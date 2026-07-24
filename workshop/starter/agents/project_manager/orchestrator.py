import datetime
import json
import os
import re
import logging
from google.genai import types
try:
    from .schema_cache import schema_cache
    from .notion_service import NotionService
    from .prompt import SYSTEM_INSTRUCTION, FINAL_RESPONSE_TEMPLATE
except ImportError:
    from schema_cache import schema_cache
    from notion_service import NotionService
    from prompt import SYSTEM_INSTRUCTION, FINAL_RESPONSE_TEMPLATE

logger = logging.getLogger("ai_creative_studio.project_manager.orchestrator")

class ProjectOrchestrator:
    def __init__(self, client, notion_service: NotionService, model_name: str):
        self.client = client
        self.model = client.models
        self.notion = notion_service
        self.model_name = model_name
        self.agent = None # Linked during agent init
        self._mcp_verified = False
        self.project_db = os.getenv("NOTION_PROJECT_DATABASE_ID")
        self.tasks_db = os.getenv("NOTION_TASKS_DATABASE_ID")

    async def run(self, campaign_input: str, tool_context=None):
        logger.info("Starting orchestrated project planning workflow...")
        
        # Sync agent to service
        if self.agent:
            self.notion.agent = self.agent

        # 0. Verification (Once per session)
        if not self._mcp_verified and self.notion and self.notion.toolset:
            await self.notion.verify_connection()
            self._mcp_verified = True

        # 1. Discovery (with Caching)
        project_schema = None
        if self.project_db:
            project_schema = schema_cache.get(self.project_db)
            if not project_schema:
                logger.info(f"Fetching project schema for {self.project_db}")
                project_schema = await self.notion.get_database_schema(self.project_db)
                if project_schema:
                    schema_cache.set(self.project_db, project_schema)
                else:
                    return f"❌ Error: Failed to retrieve Project database schema ({self.project_db}). Check Notion permissions."

        task_schema = None
        if self.tasks_db:
            task_schema = schema_cache.get(self.tasks_db)
            if not task_schema:
                logger.info(f"Fetching task schema for {self.tasks_db}")
                task_schema = await self.notion.get_database_schema(self.tasks_db)
                if task_schema:
                    schema_cache.set(self.tasks_db, task_schema)
                else:
                    return f"❌ Error: Failed to retrieve Task database schema ({self.tasks_db}). Check Notion permissions."

        # 2. Generation (Structured JSON)
        prompt = SYSTEM_INSTRUCTION.format(
            today=datetime.date.today().strftime("%B %d, %Y"),
            project_schema=json.dumps(project_schema.get("simplified", {}) if project_schema else {}),
            task_schema=json.dumps(task_schema.get("simplified", {}) if task_schema else {})
        )

        # Use a high-level model call to get the JSON plan
        try:
            logger.info(f"Generating structured plan using {self.model_name}")
            response = self.model.generate_content(
                model=self.model_name,
                contents=[types.Content(
                    role="user",
                    parts=[types.Part(text=f"{campaign_input}\n\nGenerate the structured project plan JSON now.")]
                )],
                config=types.GenerateContentConfig(
                    system_instruction=types.Content(parts=[types.Part(text=prompt)]),
                    response_mime_type="application/json"
                )
            )
            
            # Robust JSON extraction (in case of markdown wrapping)
            raw_text = response.text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:-3].strip()
            elif raw_text.startswith("```"):
                raw_text = raw_text[3:-3].strip()
                
            plan = json.loads(raw_text)
        except Exception as e:
            logger.error(f"Plan generation failed: {e}")
            return f"Error generating project plan: {e}"

        # 3. Notion Execution (Deterministic)
        notion_status = "Notion sync skipped (Missing Database IDs)."
        if project_schema and task_schema and isinstance(project_schema, dict) and "raw" in project_schema:
            logger.info("Executing Notion sync...")
            notion_status = await self._execute_notion_sync(plan, project_schema, task_schema)

        # 4. Final Formatting
        logger.info("Orchestrated workflow complete.")
        return FINAL_RESPONSE_TEMPLATE.format(
            summary=plan.get("summary", "Campaign plan generated."),
            notion_status=notion_status
        )

    async def _execute_notion_sync(self, plan, project_schema, task_schema):
        # Create Project
        project_id = await self.notion.create_page(
            self.project_db,
            plan.get("project", {}),
            project_schema
        )
        
        if not project_id:
            return "❌ Failed to create Notion project page."

        # Append Image Links (extract from raw input if present)
        # This logic is simplified; in production, you'd parse campaign_input more carefully
        image_links = [] # This would be populated from the input
        # Extract Image Links from input (Format: [Concept](url))
        image_links = []
        matches = re.findall(r"\[([^\]]+)\]\((https?://[^\)]+)\)", plan.get("summary", ""))
        for concept, url in matches:
            image_links.append({"concept": concept, "url": url})

        await self.notion.append_images(project_id, image_links)

        # Create Tasks
        task_count = 0
        for task_data in plan.get("tasks", []):
            tid = await self.notion.create_page(
                self.tasks_db, 
                task_data, 
                task_schema,
                relation_id=project_id
            )
            if tid:
                task_count += 1

        status = f"✅ Project created (ID: {project_id})"
        if task_count > 0:
            status += f" with {task_count} tasks linked."
        else:
            status += " (No tasks created)."
        
        return status