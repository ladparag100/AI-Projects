# Travel Booking AI Agent ✈️

A multi-agent travel planning system that searches flights, books hotels, plans itineraries, and provides personalized travel recommendations.

## 📋 Project Overview

This project demonstrates how to:
- Search hotels and flights based on user preferences
- Plan complete travel itineraries
- Answer travel-related questions with deep research
- Handle multiple queries in parallel
- Present unified, well-formatted travel recommendations

## 🎯 Features

✅ **Flight Search** - Find flights across multiple dates
✅ **Hotel Search** - Compare hotel options by price and ratings
✅ **Itinerary Planning** - Create day-by-day travel plans
✅ **Multi-Agent Coordination** - Multiple agents working together
✅ **Research Integration** - Use Tavily for real-time data
✅ **Deep Reasoning** - LangGraph for complex workflows

## 📁 Project Structure

```
4-Travel-Booking-AI-Agent/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── notebooks/
│   └── Multi_Agent_Travel_Planner.ipynb
└── src/
    ├── agents/
    │   ├── search_agent.py             # Flight/hotel search
    │   ├── itinerary_agent.py          # Planning agent
    │   └── scout_agent.py              # Coordination agent
    └── tools/
        ├── flight_search.py
        ├── hotel_search.py
        └── web_search.py
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- OpenAI API Key
- Tavily API Key (for web search)
- SerpAPI Key (for flight/hotel search)

### Installation

```bash
# Navigate to project
cd 4-Travel-Booking-AI-Agent

# Install dependencies
pip install -r requirements.txt
```

### Run Jupyter Notebook

```bash
jupyter notebook notebooks/Multi_Agent_Travel_Planner.ipynb
```

## 💻 Usage Examples

### General Travel Question
```
User: "What's the best season to visit Japan?"
Agent: Uses internet_search to provide seasonal guidance
```

### Detailed Itinerary
```
User: "Plan a 5-day trip to Tokyo for a first-time visitor"
Agent: Uses itinerary_research_agent to create detailed daily plans
```

### Flight Search
```
User: "Find flights from NYC to LA in December"
Agent: Uses search_flights tool to find options
```

## 🔑 Environment Variables

Create a `.env` file in the root directory:
```
OPENAI_API_KEY=your_api_key_here
TAVILY_API_KEY=your_tavily_key
SERPAPI_API_KEY=your_serpapi_key
```

## 📚 Key Technologies

- **LangGraph** - Multi-agent orchestration
- **OpenAI** - GPT model access
- **Tavily** - Web search integration
- **SerpAPI** - Flight/hotel search
- **LangChain** - LLM framework

## 🏗️ Agent Architecture

### Travel Scout Agent
- Main coordinator
- Routes queries to appropriate tools
- Synthesizes results

### Itinerary Research Agent
- Deep research capabilities
- Creates detailed plans
- Uses ReAct pattern

### Search Agent
- Flight searches
- Hotel searches
- Real-time pricing

## 💡 Tips

### Optimize Costs
- Use GPT-4o-mini for cost efficiency
- Cache results when possible
- Batch similar requests

### Improve Accuracy
- Provide clear constraints
- Ask follow-up questions
- Validate sources

## 📈 Future Enhancements

- [ ] Booking integration
- [ ] Payment processing
- [ ] Loyalty program support
- [ ] Mobile app
- [ ] Real-time notifications

## 📝 License

MIT License
