# OpsPilot AI — Autonomous IT Incident Response Agent

OpsPilot AI is an autonomous assistant designed to help with IT incident detection, triage and response. It provides a Streamlit UI that shows incidents and suggested remediation steps and can be extended to run scripted remediation actions.

## Contents

- `app.py` — Streamlit web app (deployed)
- `requirements.txt` — Project-specific dependencies
- `data/` — Incident samples (not committed)

## Quick Start

1. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies

```bash
pip install -r "Project 2 - OpsPilot AI — Autonomous IT Incident Response Agent/requirements.txt"
```

3. Run the app

```bash
cd "Project 2 - OpsPilot AI — Autonomous IT Incident Response Agent"
streamlit run app.py
```

## Features

- Incident list and details
- AI-powered triage suggestions
- Example remediation steps
- Extendable to call automation scripts or APIs

## Deployment
This app is designed to run on Streamlit Community Cloud, Heroku, or any container platform. See `requirements.txt` for required packages.
