# Smart CSV Agent 📊

An intelligent AI agent that can read and answer questions across multiple CSV files simultaneously using LangChain and OpenAI.

## 📋 Project Overview

This project demonstrates how to:
- Load multiple CSV files
- Create an AI agent that understands context
- Answer questions across different datasets
- Build a Streamlit web interface
- Use LangChain with OpenAI API

## 🎯 Features

✅ **Multi-File Support** - Load multiple CSV files at once
✅ **Natural Language Queries** - Ask questions in plain English
✅ **Context Awareness** - Agent understands which data to search
✅ **Web Interface** - Beautiful Streamlit UI
✅ **Jupyter Notebook** - Step-by-step learning
✅ **Error Handling** - Graceful error messages

## 📁 Project Structure

```
1-Smart-CSV-Agent/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── notebooks/
│   └── Smart_CSV_AI_Agent.ipynb
└── src/
    └── agent.py                        # Agent implementation
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
- **Streamlit** - Web interface (optional)

## 📖 Resources

- [LangChain Documentation](https://python.langchain.com)
- [OpenAI API Guide](https://platform.openai.com/docs/guides)
- [Pandas Tutorial](https://pandas.pydata.org/docs)

## 📝 License

MIT License
