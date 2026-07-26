# Smart CSV Agent 📊

An AI agent by Parag Lad that reads and answers questions across multiple CSV files simultaneously using LangChain and Google Gemini (Vertex AI).

## 📋 Project Overview

This project:
- Loads multiple CSV files
- Creates an AI agent that understands context
- Answers questions across different datasets
- Ships a Streamlit web interface, deployed on Google Cloud Run
- Uses LangChain with Gemini via Vertex AI - no API key needed, authentication is automatic via Google Cloud

## 🎯 Features

✅ **Multi-File Support** - Load multiple CSV files at once
✅ **Natural Language Queries** - Ask questions in plain English
✅ **Context Awareness** - Agent understands which data to search
✅ **Web Interface** - Streamlit chat UI, no API key prompt
✅ **Jupyter Notebook** - Notebook version with the same flow
✅ **Error Handling** - Graceful error messages

## 🌐 Live App

**https://smart-csv-agent-561690375744.us-central1.run.app**

Deployed on Google Cloud Run, auto-deploying on every push to `main` via GitHub Actions (keyless auth via Workload Identity Federation - no secrets stored in GitHub).

## 📁 Project Structure

```
1-Smart-CSV-Agent/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies (notebook/dev)
├── Dockerfile                          # Container image for Cloud Run
├── notebooks/
│   └── Smart_CSV_AI_Agent.ipynb
└── src/
    ├── app.py                          # Streamlit application
    └── requirements.txt                # Streamlit app dependencies
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- A Google Cloud project with the Vertex AI API enabled
- `gcloud` CLI authenticated (`gcloud auth application-default login`)

### Installation

```bash
# Navigate to project
cd 1-Smart-CSV-Agent

# Install dependencies
pip install -r src/requirements.txt
```

### Run the Streamlit App

```bash
export GOOGLE_CLOUD_PROJECT=your-gcp-project-id
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

## 🔑 Authentication

No API key is required. The app authenticates via Google Cloud Application Default Credentials (ADC):
- **On Cloud Run**: automatic, via the service's attached service account (granted `roles/aiplatform.user`)
- **Locally**: run `gcloud auth application-default login` once, then set `GOOGLE_CLOUD_PROJECT` to your project ID

## 📚 Key Technologies

- **LangChain** - LLM framework
- **Google Gemini (Vertex AI)** - LLM access, authenticated via Google Cloud
- **Pandas** - Data manipulation
- **Streamlit** - Web interface
- **Google Cloud Run** - Deployment target

## 📖 Resources

- [LangChain Documentation](https://python.langchain.com)
- [Vertex AI Gemini API Guide](https://cloud.google.com/vertex-ai/generative-ai/docs)
- [Pandas Tutorial](https://pandas.pydata.org/docs)

## 📝 License

MIT License — © Parag Lad
