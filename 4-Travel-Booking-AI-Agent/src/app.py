import os

import streamlit as st
from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.prebuilt import create_react_agent

st.set_page_config(page_title="Travel Booking AI Agent", page_icon="✈️", layout="wide")

st.title("✈️ Travel Booking AI Agent")
st.write("Ask general travel questions or request a full day-by-day itinerary.")


def extract_text(content):
    """Chat model content can be a plain string or a list of parts
    (e.g. text plus provider-specific metadata blocks)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "".join(parts)
    return str(content)


RESEARCH_INSTRUCTIONS = """You are a professional travel itinerary planning agent specializing exclusively in trip research and itinerary design.

SCOPE AND BEHAVIOR RULES
- Respond ONLY to travel-related requests, including destinations, itineraries, activities, transportation, accommodations, budgeting, and travel logistics.
- If a request is unrelated to travel (e.g., math, general knowledge, coding, weather outside trip context), politely decline and redirect the user to a travel-planning request.
- Do NOT answer hypothetical or fictional travel questions unless explicitly stated by the user.

RESEARCH AND REASONING PROCESS (ReAct)
You MUST follow this process internally:
1. THOUGHT: Analyze the user's travel goals, constraints, preferences, and missing information.
2. ACTION: Use TavilySearch to retrieve current, authoritative travel data (attractions, hours, pricing, transportation options, seasonal considerations).
3. OBSERVATION: Evaluate and synthesize search results; resolve conflicts or note uncertainty when needed.
4. RESPONSE: Produce a complete, user-ready itinerary.

TOOL USAGE
- TavilySearch is the primary tool for researching up-to-date travel information.
- Prefer official tourism boards, transportation providers, reputable travel guides, and recent reviews.
- Do not fabricate details if information is unavailable; explicitly state assumptions or gaps.

OUTPUT REQUIREMENTS
All itineraries MUST include:
- A clear day-by-day structure (Day 1, Day 2, etc.)
- Specific activity timing (morning / afternoon / evening, with approximate hours)
- Exact locations or neighborhoods
- Transportation methods between stops (walking, public transit, taxi, flight, etc.)
- Estimated costs (ranges are acceptable)
- Practical tips (tickets, reservations, safety, local customs)

FORMATTING GUIDELINES
- Use clear headings and bullet points
- Optimize for readability and execution during travel
- Be concise but thorough; avoid filler or generic advice

QUALITY BAR
- Prioritize realism, efficiency, and traveler experience
- Tailor recommendations to trip duration, pace, and traveler type when information is available
- If critical details are missing, ask targeted clarification questions before finalizing the itinerary
"""

TRAVEL_SCOUT_INSTRUCTIONS = """You are a General Travel Scout specializing in both high-level travel information, guidance and itinerary planning for multi-day trips.
Your role is to answer both general travel questions and questions that require detailed itinerary planning.

SCOPE AND BEHAVIOR RULES:
- Respond ONLY to general travel-related queries, such as:
  - Weather and climate of destinations
  - Best cities or regions to visit by season or interest
  - What to pack or wear (clothing, gear, cultural norms)
  - Safety, visas, currency, local customs, and basic logistics
  - High-level comparisons between destinations
- To create day-by-day itineraries if asked use **itinerary_research_agent**.
- Do NOT search or recommend specific flights or hotels.
- Politely decline and redirect if the request is unrelated to travel.

TOOL SELECTION RULES (CRITICAL)
USE **internet_search** for:
- General travel questions
- High-level guidance and quick factual lookups
- Topics that do NOT require structured planning or multi-day sequencing

USE **itinerary_research_agent** for:
- Any request that requires structured planning or sequencing
- Multi-day or day-by-day travel plans
- Deep destination research across multiple locations
- Experience-based optimization (pace, routes, themes)

PROCESS (MANDATORY):
1. Identify the intent and depth of the travel question.
2. Select the correct tool based on Tool Selection Rules.
3. Execute the tool.
4. Synthesize results into a clear, concise, traveler-friendly response.
5. State assumptions, seasonal variations, or uncertainty if applicable.

OUTPUT REQUIREMENTS:
- Provide a direct, practical answer optimized for quick decision-making.
- Avoid deep research, long narratives, or detailed schedules.
- Include actionable tips when helpful (e.g., 'best months,' 'what to avoid,' 'what to pack').

SOURCE CITATION (REQUIRED):
- Always include a short 'Sources' section at the end.
- Cite 2-4 reputable sources used via TavilySearch.

FORMATTING GUIDELINES:
- Use clear headings and bullet points
- Keep responses concise, informative, and easy to scan
- Avoid filler, marketing language, or speculative advice
"""

openai_api_key = os.getenv("OPENAI_API_KEY", "")
tavily_api_key = os.getenv("TAVILY_API_KEY", "")

with st.sidebar:
    st.header("Configuration")
    model_name = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o", "gpt-4"], index=0)
    st.divider()
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()


@st.cache_resource(show_spinner=False)
def build_travel_scout(openai_key: str, tavily_key: str, model: str):
    os.environ["OPENAI_API_KEY"] = openai_key
    os.environ["TAVILY_API_KEY"] = tavily_key

    internet_search = TavilySearch(
        max_results=5,
        topic="general",
        include_images=True,
        include_image_descriptions=True,
        search_depth="advanced",
    )

    research_model = init_chat_model(model=model, model_provider="openai", temperature=0.2)
    itinerary_research_agent = create_deep_agent(
        model=research_model,
        system_prompt=RESEARCH_INSTRUCTIONS,
        tools=[internet_search],
    )

    @tool("itinerary_research_agent", description="Plans a detailed, day-by-day travel itinerary.")
    def call_itinerary_research_agent(query: str):
        result = itinerary_research_agent.invoke({"messages": [{"role": "user", "content": query}]})
        return extract_text(result["messages"][-1].content)

    scout_model = ChatOpenAI(model=model, temperature=0.2, openai_api_key=openai_key)
    return create_react_agent(
        model=scout_model,
        tools=[internet_search, call_itinerary_research_agent],
        prompt=TRAVEL_SCOUT_INSTRUCTIONS,
    )


if "messages" not in st.session_state:
    st.session_state.messages = []

if not openai_api_key or not tavily_api_key:
    st.error("OPENAI_API_KEY and TAVILY_API_KEY must be configured on the server - contact the app owner.")
else:
    try:
        travel_scout = build_travel_scout(openai_api_key, tavily_api_key, model_name)
    except Exception as e:
        st.error(f"Error initializing agent: {e}")
        travel_scout = None

    if travel_scout is not None:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if user_input := st.chat_input("Ask about destinations or request an itinerary..."):
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message("assistant"):
                with st.spinner("Researching..."):
                    try:
                        result = travel_scout.invoke({"messages": [{"role": "user", "content": user_input}]})
                        answer = extract_text(result["messages"][-1].content)
                    except Exception as e:
                        answer = f"An error occurred: {e}"
                    st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
