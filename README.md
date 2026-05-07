# 🤖 AI Projects Repository

A comprehensive collection of AI and Machine Learning projects, focusing on LangChain, OpenAI, and data analysis applications.

## 📋 Project Overview

This repository contains hands-on AI projects that demonstrate:
- **Multi-Document AI Agents** - Query multiple CSV files with natural language
- **LangChain Integration** - Using LangChain for building AI applications
- **OpenAI API Usage** - Leveraging GPT models for intelligent responses
- **Streamlit Web Apps** - Building interactive web interfaces for AI applications

## 📂 Repository Structure

```
AI-Projects/
├── README.md                          # This file
├── requirements.txt                   # Global Python dependencies
├── .gitignore                         # Git ignore rules
│
├── Week0_Assignment/                  # Multi-Document FAQ Agent
│   ├── README.md                      # Project-specific documentation
│   ├── requirements.txt               # Week 0 dependencies
│   ├── app.py                         # Streamlit web application
│   ├── Week0_Assignment_Hello_Agent_CSV_FAQ_Agent.ipynb
│   └── data/                          # CSV data files
│       ├── saas_docs.csv
│       ├── credit_card_terms.csv
│       ├── hospital_policy.csv
│       └── ecommerce_faqs.csv
│
├── Week1_Assignment/                  # (Coming Soon)
│   ├── README.md
│   └── notebook.ipynb
│
└── docs/                              # Documentation
    ├── setup.md                       # Installation & setup guide
    ├── best_practices.md              # Development guidelines
    └── troubleshooting.md             # Common issues & solutions
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- OpenAI API Key (get one at [OpenAI](https://platform.openai.com))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ladparag100/AI-Projects.git
   cd AI-Projects
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Navigate to a project**
   ```bash
   cd Week0_Assignment
   pip install -r requirements.txt
   ```

## 📚 Projects

### Week 0: Multi-Document AI FAQ Agent
An intelligent agent that can:
- Load and process multiple CSV files
- Answer questions across all documents using natural language
- Use LangChain and OpenAI's GPT-4 for intelligent responses
- Provide a Streamlit web interface for easy interaction

**Location:** `Week0_Assignment/`

**Run the Streamlit app:**
```bash
cd Week0_Assignment
streamlit run app.py
```

**Run the Jupyter notebook:**
```bash
jupyter notebook Week0_Assignment_Hello_Agent_CSV_FAQ_Agent.ipynb
```

## 🛠️ Setup & Configuration

For detailed setup instructions, troubleshooting, and best practices, see:
- [Setup Guide](docs/setup.md)
- [Best Practices](docs/best_practices.md)

## 🔑 Environment Variables

Create a `.env` file in the root directory:
```
OPENAI_API_KEY=your_api_key_here
```

**Never commit your `.env` file!** It's already listed in `.gitignore`.

## 📦 Dependencies

All projects use:
- `langchain` - LLM framework
- `langchain-openai` - OpenAI integration
- `pandas` - Data manipulation
- `streamlit` - Web app framework

See individual `requirements.txt` files for specific versions.

## 📖 Documentation

- **[Setup Guide](docs/setup.md)** - Complete installation instructions
- **[Best Practices](docs/best_practices.md)** - Code standards and guidelines
- **[Week 0 README](Week0_Assignment/README.md)** - Project-specific documentation

## 🤝 Contributing

1. Create a new branch for your feature
2. Follow the guidelines in [best_practices.md](docs/best_practices.md)
3. Commit with clear messages
4. Push and create a Pull Request

## 📝 License

This project is open source and available under the MIT License.

## 📞 Support

For issues, questions, or suggestions:
1. Check [Best Practices](docs/best_practices.md) for common solutions
2. Review existing issues on GitHub
3. Create a new issue with detailed description

---

**Last Updated:** 2026-05-07