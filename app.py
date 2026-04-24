import streamlit as st
import pandas as pd
from langchain_openai import ChatOpenAI

st.title("Multi-Document AI Agent")
st.write("Upload multiple CSV files and ask questions about their content.")

# File upload
uploaded_files = st.file_uploader("Choose CSV files", accept_multiple_files=True, type=['csv'])

dataframes = []
loaded_names = []

if uploaded_files:
    st.subheader("Uploaded Files:")
    for uploaded_file in uploaded_files:
        try:
            df = pd.read_csv(uploaded_file)
            dataframes.append(df)
            loaded_names.append(uploaded_file.name)
            st.success(f"Loaded '{uploaded_file.name}' ({len(df)} rows)")
        except Exception as e:
            st.error(f"Error loading {uploaded_file.name}: {e}")

# AI Section
if dataframes:
    st.subheader("AI Agent Setup")
    api_key = st.text_input("Enter your OpenAI API Key:", type="password")

    if api_key:
        try:
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.0,
                openai_api_key=api_key
            )

            st.success("AI is ready!")

            st.subheader("Ask your question:")
            user_input = st.text_input("You:")

            if user_input:
                st.info("AI is thinking...")

                try:
                    # Combine limited data (avoid token explosion)
                    combined_data = "\n\n".join([
                        f"{name}:\n{df.head(20).to_string()}"
                        for name, df in zip(loaded_names, dataframes)
                    ])

                    prompt = f"""
You are a smart data analyst.

Datasets:
{combined_data}

Instructions:
- Use ONLY the data above
- Pick the relevant dataset
- Answer clearly in plain English

Question: {user_input}
"""

                    with st.spinner("Thinking..."):
                        response = llm.invoke(prompt)

                    st.write(f"**AI:** {response.content}")

                except Exception as e:
                    st.error(f"Error: {e}")

        except Exception as e:
            st.error(f"LLM Error: {e}")
    else:
        st.warning("Please enter your OpenAI API key to proceed.")
else:
    st.info("Please upload CSV files to start.")
