app_py_content = """
import streamlit as st
import pandas as pd
import os
# from getpass import getpass # Removed as st.text_input is used for API key
from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent


st.title("Multi-Document AI Agent")
st.write("Upload multiple CSV files and ask questions about their content.")

# ==========================================
#  PART 1: FILE UPLOADER
# ==========================================

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

# ==========================================
#  PART 2: AI AGENT SETUP (MULTI-FILE)
# ==========================================

if dataframes:
    st.subheader("AI Agent Setup")
    api_key = st.text_input("Enter your OpenAI API Key:", type="password")

    if api_key:
        system_prompt = """
You are a smart data assistant capable of reading multiple CSV files.
- You have access to the following datasets: {loaded_files}.
- When asked a question, determine which DataFrame is most relevant.
- Do NOT answer from general knowledge.
- Answer in plain English.
""".format(loaded_files=", ".join(loaded_names))

        try:
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0, openai_api_key=api_key)

            agent = create_pandas_dataframe_agent(
                llm,
                dataframes,
                verbose=True,
                agent_type="openai-functions",
                allow_dangerous_code=True
            )
            st.success("AI Agent is ready! You can ask questions across all uploaded files.")

            # ==========================================
            #  PART 3: CHAT INTERFACE
            # ==========================================
            st.subheader("Ask your question:")
            user_input = st.text_input("You:")

            if user_input:
                final_query = system_prompt + "\n\nQuestion: " + user_input
                st.info("AI is thinking...")

                try:
                    with st.spinner('Thinking:'):
                        response = agent.invoke({"input": final_query})
                    st.write(f"**AI:** {response['output']}")
                except Exception as e:
                    st.error(f"An error occurred: {e}")

        except Exception as e:
            st.error(f"Error initializing agent: {e}")
    else:
        st.warning("Please enter your OpenAI API key to proceed.")
else:
    st.info("Please upload CSV files to start.")
"""

with open("app.py", "w") as f:
    f.write(app_py_content)
