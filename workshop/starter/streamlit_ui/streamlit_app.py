import streamlit as st
import requests
import os

# Set the title of the Streamlit app
st.title("AI Creative Studio")

# Get the Creative Director URL from an environment variable or a text input
creative_director_url = st.text_input(
    "Enter the Creative Director Cloud Run URL",
    os.environ.get("CREATIVE_DIRECTOR_URL", ""),
)

# Text area for the user to input their campaign brief
campaign_brief = st.text_area("Enter your campaign brief here:", height=200)

# Submit button
if st.button("Generate Campaign"):
    if not creative_director_url:
        st.error("Please enter the Creative Director Cloud Run URL.")
    elif not campaign_brief:
        st.error("Please enter a campaign brief.")
    else:
        with st.spinner("Generating campaign..."):
            try:
                # The ADK App expects a POST request with a JSON body
                # The user's prompt is passed in the 'prompt' field.
                response = requests.post(
                    f"{creative_director_url}/",
                    json={"prompt": campaign_brief},
                    headers={"Content-Type": "application/json"},
                    timeout=600,  # Set a timeout for the request
                )
                response.raise_for_status()  # Raise an exception for bad status codes
                
                # The response from the ADK App is a JSON object.
                # The agent's output is in the 'output' field.
                result = response.json()
                st.subheader("Campaign Result:")
                st.markdown(result.get("output", "No output from the creative director."))

            except requests.exceptions.RequestException as e:
                st.error(f"An error occurred while communicating with the creative director: {e}")

