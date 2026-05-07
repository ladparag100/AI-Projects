# 🚀 Setup & Installation Guide

Complete guide to set up and run AI Projects on your local machine.

## Prerequisites

### System Requirements
- **Python**: 3.10 or higher
- **OS**: Windows, macOS, or Linux
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: 2GB free space

### Required Accounts
1. **OpenAI API Key** - Get from [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. **GitHub Account** - For cloning the repository

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/ladparag100/AI-Projects.git
cd AI-Projects
```

### 2. Create a Virtual Environment

A virtual environment isolates project dependencies from your system Python.

#### On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

#### On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

**Verify activation** - Your terminal should show `(venv)` prefix:
```
(venv) $ 
```

### 3. Upgrade pip

```bash
pip install --upgrade pip
```

### 4. Install Global Dependencies

```bash
pip install -r requirements.txt
```

### 5. Set Up Environment Variables

Create a `.env` file in the root directory:

```bash
# On Windows (PowerShell)
echo OPENAI_API_KEY=your_key_here > .env

# On macOS/Linux
echo "OPENAI_API_KEY=your_key_here" > .env
```

**Or manually create `.env` with your editor:**
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

> ⚠️ **IMPORTANT**: Never share your API key! It's in `.gitignore`, so it won't be committed.

### 6. Navigate to Project

```bash
cd Week0_Assignment
pip install -r requirements.txt
```

## Running Projects

### Option 1: Run Streamlit Web App

```bash
cd Week0_Assignment
streamlit run app.py
```

This opens your browser to `http://localhost:8501`

### Option 2: Run Jupyter Notebook

```bash
cd Week0_Assignment
jupyter notebook Week0_Assignment_Hello_Agent_CSV_FAQ_Agent.ipynb
```

This opens Jupyter in your browser.

### Option 3: Run Python Script

```bash
cd Week0_Assignment
python your_script.py
```

## Troubleshooting

### Issue 1: "Python not found"

**Solution:**
```bash
# Check Python version
python --version

# If not found, try:
python3 --version

# If still not found, install Python from https://python.org
```

### Issue 2: "Module not found" error

**Solution:**
```bash
# Verify venv is activated (should see (venv) prefix)
which python  # macOS/Linux
where python  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue 3: OpenAI API Key not working

**Solution:**
```bash
# Verify .env file exists and has correct key
cat .env  # macOS/Linux
type .env  # Windows

# Make sure key starts with 'sk-'
# Check at https://platform.openai.com/account/api-keys
```

### Issue 4: Port 8501 already in use (Streamlit)

**Solution:**
```bash
# Run on different port
streamlit run app.py --server.port 8502
```

### Issue 5: Memory/Performance issues

**Solution:**
```bash
# Limit data processing
# Edit Week0_Assignment/app.py and reduce batch size

# Or increase available memory (varies by OS)
```

### Issue 6: CSV files not loading

**Solution:**
```bash
# Verify CSV files are in correct directory
ls Week0_Assignment/data/  # macOS/Linux
dir Week0_Assignment\data\  # Windows

# Check file permissions
chmod 644 Week0_Assignment/data/*.csv  # macOS/Linux
```

### Issue 7: Dependency conflicts

**Solution:**
```bash
# Create fresh virtual environment
deactivate
rm -rf venv  # macOS/Linux
rmdir /s venv  # Windows

# Recreate everything
python -m venv venv
# Activate and reinstall
```

## Development Setup

### Install Additional Dev Tools

```bash
pip install pytest black flake8 jupyter ipython
```

### Format Code

```bash
# Black formatting
black Week0_Assignment/

# Check code style
flake8 Week0_Assignment/
```

### Run Tests

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_agent.py
```

## Docker Setup (Optional)

### Build Docker Image

```bash
docker build -t ai-projects .
```

### Run Docker Container

```bash
docker run -p 8501:8501 -e OPENAI_API_KEY=your_key ai-projects
```

## Updating Dependencies

### Check for Updates

```bash
pip list --outdated
```

### Update Specific Package

```bash
pip install --upgrade langchain
```

### Update All Packages

```bash
pip install --upgrade -r requirements.txt
```

## Verify Installation

```bash
# Test imports
python -c "import langchain; print('✅ LangChain OK')"
python -c "import streamlit; print('✅ Streamlit OK')"
python -c "import pandas; print('✅ Pandas OK')"
python -c "import openai; print('✅ OpenAI OK')"
```

## Quick Reference Commands

```bash
# Activate virtual environment
source venv/bin/activate          # macOS/Linux
venv\Scripts\activate              # Windows

# Deactivate virtual environment
deactivate

# Install requirements
pip install -r requirements.txt

# Run Streamlit app
streamlit run app.py

# Run Jupyter
jupyter notebook

# List installed packages
pip list

# Export requirements
pip freeze > requirements.txt
```

## Next Steps

1. ✅ Complete this setup
2. 📖 Read [Week0_Assignment/README.md](../Week0_Assignment/README.md)
3. 📝 Review [best_practices.md](best_practices.md)
4. 🚀 Run your first project!

## Getting Help

- **General Python**: [python.org](https://python.org)
- **LangChain Docs**: [python.langchain.com](https://python.langchain.com)
- **Streamlit Docs**: [docs.streamlit.io](https://docs.streamlit.io)
- **OpenAI API**: [platform.openai.com/docs](https://platform.openai.com/docs)
- **This Repo Issues**: [GitHub Issues](https://github.com/ladparag100/AI-Projects/issues)

---

**Last Updated:** 2026-05-07
