import os

import pandas as pd
import streamlit as st
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI

st.set_page_config(page_title="Smart CSV Agent", page_icon="📊", layout="wide")

st.title("📊 Smart CSV Agent")
st.write("Upload one or more CSV files and ask questions about their content in plain English.")

with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input(
        "OpenAI API Key",
        value=os.getenv("OPENAI_API_KEY", ""),
        type="password",
        help="Set the OPENAI_API_KEY environment variable to skip this prompt.",
    )
    model_name = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o"], index=0)
    st.divider()
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

uploaded_files = st.file_uploader("Choose CSV files", accept_multiple_files=True, type=["csv"])

dataframes = []
loaded_names = []

if uploaded_files:
    st.subheader("Uploaded Files")
    cols = st.columns(len(uploaded_files))
    for col, uploaded_file in zip(cols, uploaded_files):
        try:
            df = pd.read_csv(uploaded_file)
            dataframes.append(df)
            loaded_names.append(uploaded_file.name)
            with col:
                st.success(f"{uploaded_file.name} ({len(df)} rows)")
                st.dataframe(df.head(), height=150)
        except Exception as e:
            st.error(f"Error loading {uploaded_file.name}: {e}")

if "messages" not in st.session_state:
    st.session_state.messages = []

if not uploaded_files:
    st.info("Upload at least one CSV file to get started.")
elif not api_key:
    st.warning("Enter your OpenAI API key in the sidebar to activate the agent.")
elif dataframes:
    system_prompt = """
You are a smart data assistant capable of reading multiple CSV files.
- You have access to the following datasets: {loaded_files}.
- When asked a question, determine which dataset is most relevant.
- Do NOT answer from general knowledge.
- Answer in plain English.
""".format(loaded_files=", ".join(loaded_names))

    try:
        llm = ChatOpenAI(model=model_name, temperature=0.0, openai_api_key=api_key)
        agent = create_pandas_dataframe_agent(
            llm,
            dataframes,
            verbose=True,
            agent_type="openai-functions",
            allow_dangerous_code=True,
        )
    except Exception as e:
        st.error(f"Error initializing agent: {e}")
        agent = None

    if agent is not None:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if user_input := st.chat_input("Ask a question about your data..."):
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        final_query = system_prompt + "\n\nQuestion: " + user_input
                        response = agent.invoke({"input": final_query})
                        answer = response["output"]
                    except Exception as e:
                        answer = f"An error occurred: {e}"
                    st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
