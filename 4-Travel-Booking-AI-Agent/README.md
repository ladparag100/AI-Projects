# Travel Booking AI Agent ✈️

A multi-agent travel planning system by Parag Lad that answers travel questions and plans day-by-day itineraries using LangGraph and deep research.

## 📋 Project Overview

This project:
- Answers general travel questions (weather, visas, packing, destination comparisons)
- Plans complete day-by-day travel itineraries
- Routes each query to the right agent: quick lookup vs. deep research
- Cites sources for its research
- Ships a Streamlit chat interface

## 🎯 Features

✅ **Travel Scout Agent** - Routes queries and answers general travel questions
✅ **Itinerary Research Agent** - Deep, multi-step research for full itineraries
✅ **Real-Time Web Search** - Tavily-powered research with source citations
✅ **Multi-Agent Coordination** - LangGraph ReAct agent + deep research sub-agent
✅ **Web Interface** - Streamlit chat UI

## 🌐 Live App

**https://travel-booking-agent-561690375744.us-central1.run.app**

Deployed on Google Cloud Run, auto-deploying on every push to `main` via GitHub Actions (keyless auth via Workload Identity Federation - no secrets stored in GitHub). The OpenAI and Tavily API keys are configured server-side via Google Secret Manager - no key prompt, just open it and ask.

## 📁 Project Structure

```
4-Travel-Booking-AI-Agent/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies (notebook/dev)
├── Dockerfile                          # Container image for Cloud Run
├── notebooks/
│   └── Multi_Agent_Travel_Planner.ipynb
└── src/
    ├── app.py                          # Streamlit application
    └── requirements.txt                # Streamlit app dependencies
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+ (required by the `deepagents` dependency)
- An OpenAI API key
- A Tavily API key (for web search) — get a free key at [tavily.com](https://tavily.com)

### Installation

```bash
# Navigate to project
cd 4-Travel-Booking-AI-Agent

# Install dependencies
pip install -r src/requirements.txt
```

### Run the Streamlit App

```bash
streamlit run src/app.py
```

### Run Jupyter Notebook

```bash
jupyter notebook notebooks/Multi_Agent_Travel_Planner.ipynb
```

## 💻 Usage Examples

### General Travel Question
```
User: "What's the best season to visit Japan?"
Agent: Uses internet_search to provide seasonal guidance with sources
```

### Detailed Itinerary
```
User: "Plan a 5-day trip to Tokyo for a first-time visitor"
Agent: Routes to the itinerary research agent for a full day-by-day plan
```

## 🔑 Environment Variables

The app reads these from the environment - no in-app prompt:
```
OPENAI_API_KEY=your_api_key_here
TAVILY_API_KEY=your_tavily_key
```

On Cloud Run, both are injected from Google Secret Manager (`openai-api-key`, `tavily-api-key`) via `--set-secrets`, not stored as plain environment variables.

## 📚 Key Technologies

- **LangGraph** - Multi-agent orchestration (ReAct agent)
- **deepagents** - Deep research sub-agent for itinerary planning
- **OpenAI** - GPT model access
- **Tavily** - Web search integration
- **LangChain** - LLM framework

## 🏗️ Agent Architecture

### Travel Scout Agent
- Main coordinator (LangGraph ReAct agent)
- Answers general travel questions directly via web search
- Delegates itinerary requests to the research agent
- Synthesizes results and cites sources

### Itinerary Research Agent
- Deep research sub-agent (`deepagents`)
- Multi-step ReAct research loop over Tavily search results
- Produces structured, day-by-day itineraries

## 💡 Tips

### Optimize Costs
- Use GPT-4o-mini for cost efficiency
- Ask follow-up questions instead of broad, open-ended ones

### Improve Accuracy
- Provide clear constraints (dates, budget, interests)
- Validate sources cited in the response

## 📈 Future Enhancements

- [ ] Flight search integration
- [ ] Hotel search integration
- [ ] Booking integration
- [ ] Real-time notifications

## 📝 License

MIT License — © Parag Lad
