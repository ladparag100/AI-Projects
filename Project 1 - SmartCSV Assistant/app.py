import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

# Load .env
load_dotenv()

st.set_page_config(page_title="SmartCSV Assistant", page_icon="📄", layout="wide")
st.title("SmartCSV Assistant — Ask questions across multiple CSVs")
st.write("Upload CSV files and ask questions in natural language. Powered by LangChain + OpenAI.")

uploaded_files = st.file_uploader("Choose CSV files", accept_multiple_files=True, type=['csv'])

dataframes = []
filenames = []

if uploaded_files:
    for f in uploaded_files:
        try:
            df = pd.read_csv(f)
            dataframes.append(df)
            filenames.append(f.name)
            st.success(f"Loaded: {f.name} ({len(df)} rows)")
        except Exception as e:
            st.error(f"Error loading {f.name}: {e}")

if dataframes:
    api_key = os.getenv('OPENAI_API_KEY') or st.text_input('OpenAI API Key', type='password')
    if api_key:
        system_prompt = f"""
You are a helpful data assistant that answers only from the uploaded CSV files.
Available files: {', '.join(filenames)}
If the information is not present, reply: 'Not found in uploaded data.'
"""
        try:
            llm = ChatOpenAI(model='gpt-4o-mini', temperature=0.0, openai_api_key=api_key)
            agent = create_pandas_dataframe_agent(llm, dataframes, verbose=False, agent_type='openai-functions', allow_dangerous_code=True)
            st.success('AI Agent initialized')

            query = st.text_area('Ask a question about your data:')
            if st.button('Ask') and query.strip():
                final_query = system_prompt + "\n\nUser Question: " + query
                with st.spinner('Thinking...'):
                    try:
                        response = agent.invoke({'input': final_query})
                        if response and 'output' in response:
                            st.write('**AI Response**')
                            st.write(response['output'])
                        else:
                            st.error('No response from agent')
                    except Exception as e:
                        st.error(f'Agent error: {e}')
        except Exception as e:
            st.error(f'Initialization error: {e}')
    else:
        st.warning('Provide OpenAI API key via .env or the input above')
else:
    st.info('Upload CSV files to start')

# Data preview
with st.expander('Data preview'):
    for df, name in zip(dataframes, filenames):
        st.write(f'**{name}**')
        st.dataframe(df.head(10))
