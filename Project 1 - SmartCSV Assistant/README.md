# SmartCSV Assistant (Project 1)

SmartCSV Assistant is a lightweight Multi-Document AI that can read multiple CSV files and answer questions in natural language. It is based on LangChain + OpenAI and provides a Streamlit-based interface for easy use.

## Contents

- `app.py` — Streamlit app to upload CSVs and ask questions
- `requirements.txt` — Project-specific dependencies
- `data/` — Place your CSV files here (not committed)
- `notebooks/` — Optional Jupyter notebooks and examples

## Quick Start

1. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
```

2. Install dependencies

```bash
pip install -r "Project 1 - SmartCSV Assistant/requirements.txt"
```

3. Run the app

```bash
cd "Project 1 - SmartCSV Assistant"
streamlit run app.py
```

## How it works

- Upload multiple CSVs via the UI
- The agent builds a small index/inspection of the CSVs
- Ask questions and the agent returns answers referencing the files

## Notes

- Keep API keys in a `.env` file with `OPENAI_API_KEY`
- Do not commit sensitive data to the repo
