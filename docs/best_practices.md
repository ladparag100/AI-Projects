# Best Practices & Development Guidelines

## 📋 Code Quality Standards

### Python Code Style

Follow **PEP 8** standards:

```python
# ✅ Good: Clear variable names, proper spacing
def load_csv_files(file_paths: list) -> list:
    """Load CSV files and return list of DataFrames."""
    dataframes = []
    for path in file_paths:
        df = pd.read_csv(path)
        dataframes.append(df)
    return dataframes

# ❌ Bad: Unclear naming, missing type hints
def load(x):
    d = []
    for i in x:
        d.append(pd.read_csv(i))
    return d
```

### Type Hints

Always use type hints for better code clarity:

```python
from typing import List, Dict, Optional

def process_data(
    df: pd.DataFrame, 
    column: str
) -> Dict[str, any]:
    """Process DataFrame and return results."""
    return {"processed": df[column].value_counts()}
```

### Docstrings

Write clear docstrings for all functions:

```python
def create_agent(
    llm: ChatOpenAI,
    dataframes: List[pd.DataFrame]
) -> PandasDataFrameAgent:
    """
    Create a LangChain agent for multi-document analysis.
    
    Args:
        llm: Language model instance
        dataframes: List of DataFrames to analyze
        
    Returns:
        PandasDataFrameAgent: Configured agent instance
        
    Raises:
        ValueError: If dataframes list is empty
        
    Example:
        >>> llm = ChatOpenAI(model="gpt-4o-mini")
        >>> agent = create_agent(llm, [df1, df2])
    """
    if not dataframes:
        raise ValueError("At least one DataFrame is required")
    
    return create_pandas_dataframe_agent(
        llm,
        dataframes,
        verbose=True,
        allow_dangerous_code=True
    )
```

## 🔒 Security Best Practices

### 1. API Key Management

```python
# ✅ Good: Use environment variables
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# ❌ Bad: Hardcoding API keys
api_key = "sk-your-secret-key-here"  # NEVER DO THIS!
```

### 2. Input Validation

```python
# ✅ Good: Validate user input
def validate_csv_file(file_path: str) -> bool:
    """Validate that file exists and is a CSV."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    if not file_path.endswith('.csv'):
        raise ValueError(f"Invalid file type: {file_path}")
    return True

# ❌ Bad: No validation
df = pd.read_csv(user_input)  # Could fail unexpectedly
```

### 3. Error Handling

```python
# ✅ Good: Comprehensive error handling
try:
    df = pd.read_csv(file_path)
except FileNotFoundError:
    logger.error(f"File not found: {file_path}")
except pd.errors.ParserError:
    logger.error(f"Invalid CSV format: {file_path}")
except Exception as e:
    logger.error(f"Unexpected error: {e}")

# ❌ Bad: No error handling
df = pd.read_csv(file_path)  # Will crash if file doesn't exist
```

### 4. Data Sanitization

```python
# ✅ Good: Remove sensitive information
def sanitize_data(df: pd.DataFrame) -> pd.DataFrame:
    """Remove columns with sensitive information."""
    sensitive_cols = ['api_key', 'password', 'credit_card']
    df = df.drop(columns=[c for c in sensitive_cols if c in df.columns])
    return df

# ❌ Bad: Process raw data without checking
response = agent.invoke({"input": unsanitized_user_data})
```

## 🔄 Git Workflow

### Branch Naming Convention

```
feature/add-new-model       # New feature
fix/resolve-api-error       # Bug fix
docs/update-readme          # Documentation
refactor/optimize-agent     # Code improvements
test/add-unit-tests         # Tests
```

### Commit Messages

```bash
# ✅ Good: Clear, descriptive commits
git commit -m "feat: Add multi-file support to AI agent"
git commit -m "fix: Resolve CSV encoding issue with UTF-8"
git commit -m "docs: Add setup instructions"

# ❌ Bad: Vague commits
git commit -m "Update"
git commit -m "Fixed stuff"
git commit -m "asdfgh"
```

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] New Feature
- [ ] Bug Fix
- [ ] Documentation
- [ ] Refactoring

## Testing
How to test the changes

## Screenshots (if applicable)
Add images here

## Checklist
- [ ] Code follows PEP 8
- [ ] Added docstrings
- [ ] Tested locally
- [ ] No hardcoded secrets
```

## 📊 Project Structure

```
Week0_Assignment/
├── README.md              # Project documentation
├── requirements.txt       # Dependencies
├── app.py                 # Main application
├── data/                  # CSV files
├── notebooks/             # Jupyter notebooks
├── utils/                 # Helper functions
├── tests/                 # Unit tests
└── config/                # Configuration files
```

## 🧪 Testing

### Unit Test Example

```python
import unittest
from app import create_agent

class TestAgent(unittest.TestCase):
    def setUp(self):
        self.df = pd.read_csv('test_data.csv')
    
    def test_agent_creation(self):
        """Test that agent is created successfully."""
        llm = ChatOpenAI(model="gpt-4o-mini")
        agent = create_agent(llm, [self.df])
        self.assertIsNotNone(agent)
    
    def test_empty_dataframes(self):
        """Test that empty list raises error."""
        llm = ChatOpenAI(model="gpt-4o-mini")
        with self.assertRaises(ValueError):
            create_agent(llm, [])

if __name__ == '__main__':
    unittest.main()
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_agent.py

# Run with coverage
python -m pytest --cov=.
```

## 📝 Documentation

### README Structure

```markdown
# Project Title

## Description
Brief overview

## Installation
Step-by-step setup

## Usage
How to use the project

## Examples
Code examples

## Troubleshooting
Common issues and solutions

## Contributing
How to contribute

## License
License information
```

### Code Comments

```python
# ✅ Good: Meaningful comments
# Split data into train and test sets (80-20 split)
train_size = int(len(df) * 0.8)
train_data = df[:train_size]

# ❌ Bad: Obvious or unnecessary comments
# Loop through dataframes
for df in dataframes:
    process(df)
```

## 🚀 Performance Tips

### 1. Efficient Data Loading

```python
# ✅ Good: Load only needed columns
df = pd.read_csv('large_file.csv', usecols=['col1', 'col2'])

# ❌ Bad: Load entire file
df = pd.read_csv('large_file.csv')
```

### 2. Caching Results

```python
# ✅ Good: Cache expensive operations
@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path)

# ❌ Bad: Reprocess data every time
df = pd.read_csv(file_path)
```

### 3. Batch Processing

```python
# ✅ Good: Process in batches
for i in range(0, len(data), batch_size):
    batch = data[i:i+batch_size]
    process_batch(batch)

# ❌ Bad: Process one by one
for item in data:
    process_item(item)
```

## 🎯 AI/LangChain Best Practices

### 1. Temperature Settings

```python
# ✅ Deterministic responses (for QA systems)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

# ✅ Creative responses (for brainstorming)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# ❌ Too high (unreliable)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=1.5)
```

### 2. Prompt Engineering

```python
# ✅ Good: Clear, specific instructions
system_prompt = """
You are a data analyst assistant.
- Answer only based on provided data
- Use exact values from DataFrames
- If information not available, say "Not found in data"
"""

# ❌ Bad: Vague instructions
system_prompt = "Answer questions"
```

### 3. Response Validation

```python
# ✅ Good: Validate AI responses
response = agent.invoke({"input": query})
if response and 'output' in response:
    return response['output']
else:
    return "Unable to process request"

# ❌ Bad: No validation
return response['output']  # Could KeyError
```

## 📦 Dependency Management

### requirements.txt Best Practices

```
# ✅ Good: Pinned versions
langchain==0.3.28
pandas>=2.0.0,<3.0.0

# ❌ Bad: No version control
langchain
pandas
```

### Updating Dependencies

```bash
# Check outdated packages
pip list --outdated

# Update specific package
pip install --upgrade langchain

# Update all packages
pip install --upgrade -r requirements.txt
```

## 📊 Logging

```python
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Use logging instead of print
logger.info("Agent initialized successfully")
logger.error("Failed to load CSV file")
logger.warning("API key not found, using default")
```

## 🔍 Code Review Checklist

Before submitting code:

- [ ] Follows PEP 8 style guide
- [ ] Has type hints
- [ ] Includes docstrings
- [ ] No hardcoded secrets
- [ ] Proper error handling
- [ ] Tested locally
- [ ] No unnecessary imports
- [ ] Clear variable names
- [ ] Comments where needed
- [ ] Updated requirements.txt
- [ ] Updated README if needed
- [ ] No large files committed

## 🎓 Learning Resources

- [PEP 8 Style Guide](https://pep8.org/)
- [Real Python Best Practices](https://realpython.com/)
- [LangChain Best Practices](https://python.langchain.com/docs/guides/safety)
- [Git Workflow Guide](https://www.atlassian.com/git/tutorials)
- [Clean Code Principles](https://en.wikipedia.org/wiki/Clean_code)

---

**Last Updated:** 2026-05-07
