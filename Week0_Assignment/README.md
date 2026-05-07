# Week 0: Multi-Document AI FAQ Agent 🤖

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
Week0_Assignment/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── app.py                              # Streamlit web app
├── Week0_Assignment_Hello_Agent_CSV_FAQ_Agent.ipynb
└── data/                               # CSV files
    ├── saas_docs.csv                   # Software docs
    ├── credit_card_terms.csv           # Financial terms
    ├── hospital_policy.csv             # Medical policies
    └── ecommerce_faqs.csv              # E-commerce FAQs
```

## 🚀 Quick Start

### Method 1: Run Streamlit Web App (Recommended)

```bash
# Navigate to project
cd Week0_Assignment

# Run the app
streamlit run app.py
```

Open your browser to `http://localhost:8501`

### Method 2: Run Jupyter Notebook

```bash
# Navigate to project
cd Week0_Assignment

# Start Jupyter
jupyter notebook Week0_Assignment_Hello_Agent_CSV_FAQ_Agent.ipynb
```

## 💻 Usage Examples

The agent can answer questions like:

### SaaS Documentation
```
Query: "What is the API rate limit for the free plan?"
Answer: "The API rate limit for the free plan is 1,000 API requests per day."
```

### Hospital Policies
```
Query: "What are the visiting hours?"
Answer: "The visiting hours are from 10:00 AM to 8:00 PM."
```

### E-commerce FAQs
```
Query: "What is the return policy?"
Answer: "Items can be returned within 30 days of purchase in original condition."
```

### Credit Card Terms
```
Query: "What is the annual interest rate?"
Answer: "The annual interest rate is 18.5% APR."
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```
OPENAI_API_KEY=sk-your-api-key-here
```

### CSV File Format

Your CSV files should have a clear structure:

```csv
Question,Answer
"What is API rate limit?","1000 requests per day"
"How to get started?","Sign up and create an account"
```

## 📚 How It Works

### Step 1: Data Loading
```python
# Load CSV files into DataFrames
dataframes = []
for filename in ['file1.csv', 'file2.csv']:
    df = pd.read_csv(filename)
    dataframes.append(df)
```

### Step 2: LLM Setup
```python
# Initialize OpenAI language model
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.0,
    openai_api_key=api_key
)
```

### Step 3: Agent Creation
```python
# Create pandas agent for multi-file analysis
agent = create_pandas_dataframe_agent(
    llm,
    dataframes,
    verbose=True,
    allow_dangerous_code=True
)
```

### Step 4: Query Processing
```python
# Process user queries
response = agent.invoke({
    "input": "Your question here"
})
print(response['output'])
```

## 🧠 Key Concepts

### What is LangChain?
LangChain is a framework for developing applications powered by language models. It enables:
- Connection to language models (like GPT)
- Data analysis with AI
- Building intelligent agents
- Prompt management

### What is the Agent?
An agent is an AI system that can:
- Understand natural language
- Decide which data to search
- Execute operations
- Provide intelligent responses

### Temperature Parameter
- `temperature=0.0` → Deterministic (best for Q&A)
- `temperature=0.5` → Balanced
- `temperature=0.9` → Creative

## 🔍 Troubleshooting

### Issue: "OpenAI API key not found"
```bash
# Solution: Check .env file
cat .env  # macOS/Linux
type .env  # Windows
```

### Issue: "Module not found" error
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

### Issue: CSV file not loading
```bash
# Solution: Check file path and format
# CSV must be in data/ folder
ls Week0_Assignment/data/
```

### Issue: Slow response times
```bash
# Solution: Reduce data size or use GPT-4
# Edit app.py:
model="gpt-4o-mini"  # Faster, cheaper
```

## 📊 Example Queries

```python
# Technical questions
"What are the system requirements?"
"How do I authenticate with the API?"
"What error codes exist?"

# Business questions
"What is the pricing model?"
"What payment methods do you accept?"
"What is your refund policy?"

# Medical questions (hospital data)
"What are visiting hours?"
"Do you have emergency services?"
"What insurance do you accept?"

# E-commerce questions
"What is your return policy?"
"How long does shipping take?"
"Do you offer international shipping?"
```

## 🎓 Learning Outcomes

After completing this project, you'll understand:

✅ How to load and process CSV data with pandas
✅ How to integrate OpenAI API in Python
✅ How to build multi-document AI systems
✅ How LangChain simplifies AI development
✅ How to create web interfaces with Streamlit
✅ Best practices for AI application development

## 🔐 Security Notes

⚠️ **Never commit your API key!**
- Keep `.env` files in `.gitignore`
- Use environment variables
- Rotate keys regularly
- Monitor usage on OpenAI dashboard

## 📈 Optimization Tips

### Reduce Costs
- Use `gpt-4o-mini` instead of `gpt-4`
- Limit data processing
- Cache results when possible

### Improve Speed
- Load only needed CSV columns
- Reduce DataFrame size
- Use streaming responses

### Enhance Accuracy
- Provide clear system prompts
- Use examples in prompts
- Validate responses

## 🚀 Next Steps

1. ✅ Run the Streamlit app
2. 📝 Try different queries
3. 📊 Add your own CSV files
4. 🔧 Customize the system prompt
5. 🎨 Improve the UI
6. 📚 Read LangChain documentation

## 📚 Resources

- [LangChain Documentation](https://python.langchain.com)
- [OpenAI API Guide](https://platform.openai.com/docs/guides)
- [Streamlit Documentation](https://docs.streamlit.io)
- [Pandas Tutorial](https://pandas.pydata.org/docs)
- [Python Best Practices](https://pep8.org)

## 🤝 Contributing

Want to improve this project?
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

MIT License - Feel free to use and modify!

## 📞 Support

Having issues? Check:
1. [Best Practices Guide](../docs/best_practices.md)
2. [Setup Guide](../docs/setup.md)
3. [GitHub Issues](https://github.com/ladparag100/AI-Projects/issues)

---

**Created:** 2026-05-07
**Last Updated:** 2026-05-07
