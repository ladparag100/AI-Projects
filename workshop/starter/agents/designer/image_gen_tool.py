"""Gemini native image generation tool. Generates image, uploads to GCS, returns URI."""
import io
import os
import uuid

from google import genai
from google.adk.tools import ToolContext
from google.genai import types


async def generate_image(
    concept_name: str,
    image_prompt: str,
    aspect_ratio: str,
    tool_context: ToolContext,
) -> dict:
    """
    Generate an image with Gemini native image generation and upload it to GCS.

    Args:
        concept_name: Short identifier for this image concept (e.g. "post1_concept_a")
        image_prompt: Full image generation prompt string
        aspect_ratio: "1:1" for square (1080x1080) or "4:5" for portrait (1080x1350)

    Returns:
        {"status": "success", "gcs_uri": "gs://...", "concept_name": "..."}
        or {"status": "error", "error": "..."}
    """
    bucket_name = os.environ.get("GCS_IMAGES_BUCKET")
    if not bucket_name:
        return {"status": "error", "error": "GCS_IMAGES_BUCKET env var not set"}

    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
    # Use a dedicated image-capable model; separate from the text GEMINI_MODEL.
    # gemini-3.1-flash-image does NOT support function calling, so it cannot
    # be used as an ADK agent - but calling it directly here is fine.
    image_model = os.environ.get(
        "GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image"
    )

    # Aspect ratio is not an API parameter for Gemini native generation - inject it
    # into the prompt so the model respects the desired Instagram format.
    aspect_hint = {
        "1:1": "square 1:1 aspect ratio (1080x1080)",
        "4:5": "portrait 4:5 aspect ratio (1080x1350)",
    }.get(aspect_ratio, f"{aspect_ratio} aspect ratio")
    prompt_with_aspect = f"{image_prompt}\n\nGenerate this as a {aspect_hint} image."

    try:
        client = genai.Client(vertexai=True, project=project_id, location=location)

        response = client.models.generate_content(
            model=image_model,
            contents=prompt_with_aspect,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
                http_options=types.HttpOptions(
                    retry_options=types.HttpRetryOptions(
                        attempts=5, exp_base=2, initial_delay=30,
                        http_status_codes=[429, 500, 503, 504],
                    ),
                    timeout=180_000,
                ),
            ),
        )

        # Filter parts to remove empty text parts that cause serialization issues.
        filtered_parts = [
            p for p in response.candidates[0].content.parts
            if p.inline_data or (p.text and p.text.strip())
        ]

        image_part = next((p for p in filtered_parts if p.inline_data), None)

        if not image_part:
            return {"status": "error", "error": "Gemini returned no image data"}

        image_bytes = image_part.inline_data.data
        mime_type = image_part.inline_data.mime_type or "image/png"

        ext = "jpg" if "jpeg" in mime_type else "png"
        from google.cloud import storage
        gcs_client = storage.Client(project=project_id)
        bucket = gcs_client.bucket(bucket_name)
        blob_name = f"campaign-images/{concept_name}-{uuid.uuid4().hex[:8]}.{ext}"
        blob = bucket.blob(blob_name)
        blob.upload_from_file(io.BytesIO(image_bytes), content_type=mime_type)
        gcs_uri = f"gs://{bucket_name}/{blob_name}"

        
        if image_bytes and gcs_uri:
            ext = "jpg" if "jpeg" in mime_type else "png"
            try:
                await tool_context.save_artifact(f"{concept_name}.{ext}", image_part)
            except ValueError:
                pass

            return {"status": "success", "gcs_uri": gcs_uri, "concept_name": concept_name}

        return {"status": "error", "error": "Image generation incomplete - fill in the TODOs"}

    except Exception as e:
        return {"status": "error", "error": str(e)}
