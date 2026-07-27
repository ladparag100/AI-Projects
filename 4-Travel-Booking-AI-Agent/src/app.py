import os
from datetime import date

import serpapi
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
- If the traveler's origin city and travel dates are known (or can be reasonably inferred), use flight_search_agent to look up real flight options and include them in the itinerary. Do not fabricate flight prices, times, or airlines - only report what flight_search_agent returns.
- Prefer official tourism boards, transportation providers, reputable travel guides, and recent reviews.
- Do not fabricate details if information is unavailable; explicitly state assumptions or gaps.

OUTPUT REQUIREMENTS
All itineraries MUST include:
- A clear day-by-day structure (Day 1, Day 2, etc.)
- Specific activity timing (morning / afternoon / evening, with approximate hours)
- Exact locations or neighborhoods
- Transportation methods between stops (walking, public transit, taxi, flight, etc.)
- Real flight options (airline, price, duration) when origin and dates are known
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

FLIGHT_SEARCH_INSTRUCTIONS = """You are a flight search specialist. Your only job is to find real flight options using the search_flights tool.

Today's date is {today}.

PROCESS:
1. Identify the origin and destination. Resolve each city to ONE SPECIFIC AIRPORT's 3-letter IATA code - never a multi-airport metro/city code. For example: New York -> JFK (NOT NYC), London -> LHR (NOT LON), Tokyo -> NRT (NOT TYO), Paris -> CDG (NOT PAR), Chicago -> ORD (NOT CHI). Metro/city codes are not accepted by the flight search tool and will return zero results. If a city is ambiguous or you are not confident of the airport code, ask a clarifying question instead of guessing.
2. Identify the outbound date, and return date if this is a round trip. Dates must be in YYYY-MM-DD format. If a date is relative (e.g. "next Friday"), resolve it using today's date above. If dates are missing entirely, ask for them.
3. Call search_flights with departure_id, arrival_id, outbound_date, and return_date (if round trip).
4. Report ONLY what the tool returns - airline, price, duration, stops. Never invent or estimate flight prices, times, or airlines.
5. If the tool returns no results or an error, say so plainly rather than guessing.

OUTPUT: A short, clear list of the top flight options (airline, price, duration, stops), plus a one-line summary of the cheapest and fastest option.
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
- To create day-by-day itineraries if asked use **itinerary_research_agent** (it will pull in real flight options itself when relevant).
- To answer specific flight search or pricing questions use **flight_search_agent**.
- Do NOT recommend specific hotels.
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

USE **flight_search_agent** for:
- Standalone flight questions with no itinerary discussion elsewhere in the conversation
- Do not answer flight questions from general knowledge - always call this tool, since flight prices and schedules change constantly

- If the user has already discussed or requested an itinerary earlier in this conversation and then separately asks for flight details, do NOT reply with flight details alone. Call flight_search_agent (or itinerary_research_agent if a fuller answer is warranted) and present BOTH the flight details AND a short recap of the itinerary already discussed, so the response is self-contained.

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
serpapi_api_key = os.getenv("SERPAPI_API_KEY", "")

with st.sidebar:
    st.header("Configuration")
    model_name = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o", "gpt-4"], index=0)
    st.divider()
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()


# SerpApi's Google Flights engine rejects multi-airport metro/city codes
# (e.g. LON, NYC) and returns zero results - the model is instructed to
# avoid these, but this is a deterministic safety net for common ones.
CITY_CODE_TO_AIRPORT = {
    "LON": "LHR", "NYC": "JFK", "PAR": "CDG", "TYO": "NRT", "CHI": "ORD",
    "WAS": "IAD", "MOW": "SVO", "BJS": "PEK", "SAO": "GRU", "BUE": "EZE",
    "MIL": "MXP", "ROM": "FCO", "OSA": "KIX", "SEL": "ICN", "STO": "ARN",
    "RIO": "GIG",
}


@tool("search_flights", description="Searches real flight options (price, airline, duration, stops) between two airports using Google Flights data via SerpApi.")
def search_flights(departure_id: str, arrival_id: str, outbound_date: str, return_date: str = "") -> str:
    """
    departure_id / arrival_id: IATA airport codes, e.g. JFK, NRT, LHR.
    outbound_date / return_date: YYYY-MM-DD. Omit return_date for a one-way search.
    """
    departure_id = CITY_CODE_TO_AIRPORT.get(departure_id.upper(), departure_id.upper())
    arrival_id = CITY_CODE_TO_AIRPORT.get(arrival_id.upper(), arrival_id.upper())

    params = {
        "engine": "google_flights",
        "departure_id": departure_id,
        "arrival_id": arrival_id,
        "outbound_date": outbound_date,
        "currency": "USD",
        "type": 1 if return_date else 2,
        "api_key": os.environ["SERPAPI_API_KEY"],
    }
    if return_date:
        params["return_date"] = return_date

    results = serpapi.GoogleSearch(params).get_dict()

    if "error" in results:
        return f"Flight search error: {results['error']}"

    flights = results.get("best_flights", []) + results.get("other_flights", [])
    if not flights:
        return "No flights found for these criteria."

    lines = []
    for flight in flights[:5]:
        legs = flight.get("flights", [])
        airlines = ", ".join(sorted({leg.get("airline", "Unknown") for leg in legs}))
        stops = max(len(legs) - 1, 0)
        duration = flight.get("total_duration", 0)
        price = flight.get("price", "N/A")
        lines.append(
            f"- {airlines}: ${price}, {duration // 60}h {duration % 60}m, {stops} stop(s)"
        )
    return "\n".join(lines)


@st.cache_resource(show_spinner=False)
def build_travel_scout(openai_key: str, tavily_key: str, serpapi_key: str, model: str):
    os.environ["OPENAI_API_KEY"] = openai_key
    os.environ["TAVILY_API_KEY"] = tavily_key
    os.environ["SERPAPI_API_KEY"] = serpapi_key

    internet_search = TavilySearch(
        max_results=5,
        topic="general",
        include_images=True,
        include_image_descriptions=True,
        search_depth="advanced",
    )

    flight_model = ChatOpenAI(model=model, temperature=0.0, openai_api_key=openai_key)
    flight_search_agent = create_react_agent(
        model=flight_model,
        tools=[search_flights],
        prompt=FLIGHT_SEARCH_INSTRUCTIONS.format(today=date.today().isoformat()),
    )

    @tool("flight_search_agent", description="Finds real flight options and prices between two cities on specific dates.")
    def call_flight_search_agent(query: str):
        result = flight_search_agent.invoke({"messages": [{"role": "user", "content": query}]})
        return extract_text(result["messages"][-1].content)

    research_model = init_chat_model(model=model, model_provider="openai", temperature=0.2)
    itinerary_research_agent = create_deep_agent(
        model=research_model,
        system_prompt=RESEARCH_INSTRUCTIONS,
        tools=[internet_search, call_flight_search_agent],
    )

    @tool("itinerary_research_agent", description="Plans a detailed, day-by-day travel itinerary.")
    def call_itinerary_research_agent(query: str):
        result = itinerary_research_agent.invoke({"messages": [{"role": "user", "content": query}]})
        return extract_text(result["messages"][-1].content)

    scout_model = ChatOpenAI(model=model, temperature=0.2, openai_api_key=openai_key)
    return create_react_agent(
        model=scout_model,
        tools=[internet_search, call_itinerary_research_agent, call_flight_search_agent],
        prompt=TRAVEL_SCOUT_INSTRUCTIONS,
    )


if "messages" not in st.session_state:
    st.session_state.messages = []

if not openai_api_key or not tavily_api_key or not serpapi_api_key:
    st.error("OPENAI_API_KEY, TAVILY_API_KEY, and SERPAPI_API_KEY must be configured on the server - contact the app owner.")
else:
    try:
        travel_scout = build_travel_scout(openai_api_key, tavily_api_key, serpapi_api_key, model_name)
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
                        result = travel_scout.invoke({"messages": st.session_state.messages})
                        answer = extract_text(result["messages"][-1].content)
                    except Exception as e:
                        answer = f"An error occurred: {e}"
                    st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
