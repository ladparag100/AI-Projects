# Smart CSV Agent 📊

An AI agent by Parag Lad that reads and answers questions across multiple CSV files simultaneously using LangChain and OpenAI.

## 📋 Project Overview

This project:
- Loads multiple CSV files
- Creates an AI agent that understands context
- Answers questions across different datasets
- Ships a Streamlit web interface
- Uses LangChain with the OpenAI API

## 🎯 Features

✅ **Multi-File Support** - Load multiple CSV files at once
✅ **Natural Language Queries** - Ask questions in plain English
✅ **Context Awareness** - Agent understands which data to search
✅ **Web Interface** - Streamlit chat UI
✅ **Jupyter Notebook** - Notebook version with the same flow
✅ **Error Handling** - Graceful error messages

## 📁 Project Structure

```
1-Smart-CSV-Agent/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── notebooks/
│   └── Smart_CSV_AI_Agent.ipynb
└── src/
    └── app.py                          # Streamlit application
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- OpenAI API Key

### Installation

```bash
# Navigate to project
cd 1-Smart-CSV-Agent

# Install dependencies
pip install -r requirements.txt
```

### Run the Streamlit App

```bash
streamlit run src/app.py
```

### Run Jupyter Notebook

```bash
jupyter notebook notebooks/Smart_CSV_AI_Agent.ipynb
```

## 💻 Usage

The agent can answer questions about your CSV data:
- "What is the API rate limit?"
- "What are the visiting hours?"
- "What is the return policy?"

## 🔑 Environment Variables

Create a `.env` file in the root directory:
```
OPENAI_API_KEY=your_api_key_here
```

## 📚 Key Technologies

- **LangChain** - LLM framework
- **OpenAI** - GPT model access
- **Pandas** - Data manipulation
- **Streamlit** - Web interface

## 📖 Resources

- [LangChain Documentation](https://python.langchain.com)
- [OpenAI API Guide](https://platform.openai.com/docs/guides)
- [Pandas Tutorial](https://pandas.pydata.org/docs)

## 📝 License

MIT License — © Parag Lad
