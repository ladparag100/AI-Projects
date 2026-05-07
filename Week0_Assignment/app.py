import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="🤖 Multi-Document AI Agent",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Multi-Document AI FAQ Agent")
st.write("Upload multiple CSV files and ask questions about their content using AI.")

# ==========================================
#  PART 1: FILE UPLOADER
# ==========================================

st.subheader("📁 Step 1: Upload Your CSV Files")
uploaded_files = st.file_uploader(
    "Choose CSV files",
    accept_multiple_files=True,
    type=['csv'],
    help="Upload multiple CSV files. The AI will analyze all of them."
)

dataframes = []
loaded_names = []

if uploaded_files:
    st.write(f"✅ Uploaded {len(uploaded_files)} file(s):")
    for uploaded_file in uploaded_files:
        try:
            df = pd.read_csv(uploaded_file)
            dataframes.append(df)
            loaded_names.append(uploaded_file.name)
            st.success(f"✅ '{uploaded_file.name}' loaded ({len(df)} rows)")
        except Exception as e:
            st.error(f"❌ Error loading {uploaded_file.name}: {e}")

# ==========================================
#  PART 2: API KEY INPUT
# ==========================================

if dataframes:
    st.subheader("🔑 Step 2: Configure AI Agent")
    
    # Try to get API key from environment first
    env_api_key = os.getenv("OPENAI_API_KEY")
    
    if env_api_key:
        st.info("✅ OpenAI API Key loaded from environment (.env file)")
        api_key = env_api_key
    else:
        api_key = st.text_input(
            "Enter your OpenAI API Key:",
            type="password",
            help="Get your API key from https://platform.openai.com/api-keys"
        )
    
    if api_key:
        system_prompt = f"""
You are a smart data assistant capable of reading and analyzing multiple CSV files.

Available datasets:
{', '.join(loaded_names)}

Instructions:
- When asked a question, determine which dataset(s) are most relevant
- Answer only based on the data provided in the files
- Be specific and reference the exact values from the data
- If information is not available in any file, clearly state "Not found in the uploaded data"
- Always provide context about which file you're referencing
- Answer in plain, clear English
"""
        
        try:
            # Initialize LLM
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.0,
                openai_api_key=api_key
            )
            
            # Create agent
            agent = create_pandas_dataframe_agent(
                llm,
                dataframes,
                verbose=False,
                agent_type="openai-functions",
                allow_dangerous_code=True
            )
            
            st.success("✅ AI Agent initialized successfully!")
            
            # ==========================================
            #  PART 3: CHAT INTERFACE
            # ==========================================
            
            st.subheader("💬 Step 3: Ask Your Questions")
            
            # Example questions
            st.write("**Example Questions:**")
            col1, col2 = st.columns(2)
            with col1:
                st.caption("📋 Data Questions")
                st.caption("• What columns are in the data?")
                st.caption("• Show me the first few rows")
            with col2:
                st.caption("🔍 Analysis Questions")
                st.caption("• What is the total...?")
                st.caption("• How many records...?")
            
            # User input
            user_input = st.text_area(
                "Your Question:",
                placeholder="Ask any question about your data...",
                height=100
            )
            
            if st.button("🚀 Ask AI Agent", use_container_width=True):
                if user_input.strip():
                    final_query = system_prompt + "\n\nUser Question: " + user_input
                    
                    with st.spinner('🤔 AI is thinking...'):
                        try:
                            response = agent.invoke({"input": final_query})
                            
                            if response and 'output' in response:
                                st.success("✅ Response Generated")
                                st.write("\n### 🤖 AI Response:\n")
                                st.write(response['output'])
                                
                                # Add copy button
                                st.code(response['output'], language="text")
                            else:
                                st.error("❌ No response generated")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("⚠️ Please enter a question")
            
            # Display data preview
            with st.expander("📊 Data Preview"):
                for i, (df, name) in enumerate(zip(dataframes, loaded_names)):
                    st.write(f"**{name}**")
                    st.dataframe(df.head(10), use_container_width=True)
                    st.write(f"Rows: {len(df)}, Columns: {len(df.columns)}")
                    st.divider()
        
        except Exception as e:
            st.error(f"❌ Error initializing agent: {str(e)}")
            st.info("💡 Make sure your API key is valid and you have available credits")
    
    else:
        st.warning("⚠️ Please enter your OpenAI API key to proceed")
else:
    st.info("📁 Please upload CSV files to get started")
    st.write("""
    ### How to use:
    1. **Upload CSV files** - Click the upload button above
    2. **Enter API Key** - Provide your OpenAI API key
    3. **Ask Questions** - Query your data using natural language
    4. **Get Insights** - AI analyzes your data and provides answers
    
    ### Tips:
    - Upload CSV files with clear headers
    - Ask specific questions for better results
    - The AI can analyze across multiple files simultaneously
    - Use the data preview to understand your data structure
    """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; margin-top: 50px'>
    <p>🤖 Multi-Document AI Agent | Built with LangChain + Streamlit + OpenAI</p>
    <p><a href='https://github.com/ladparag100/AI-Projects'>GitHub Repository</a></p>
</div>
""", unsafe_allow_html=True)
