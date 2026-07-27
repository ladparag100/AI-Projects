import os
from datetime import date
from typing import List

import serpapi
import streamlit as st
from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field

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


class AirportCode(BaseModel):
    iata_code: str = Field(description="A single, specific 3-letter IATA airport code - never a multi-airport metro/city code.")


def resolve_airport_code(location: str, openai_key: str, model: str) -> str:
    """Resolves a free-text city/airport name to a specific IATA airport code via structured LLM output."""
    location = location.strip()
    if len(location) == 3 and location.isalpha():
        code = location.upper()
        return CITY_CODE_TO_AIRPORT.get(code, code)
    resolver = ChatOpenAI(model=model, temperature=0.0, openai_api_key=openai_key).with_structured_output(AirportCode)
    result = resolver.invoke(
        f"What is the primary international airport's IATA code for '{location}'? "
        "Return one specific airport code, never a multi-airport city code."
    )
    return result.iata_code.upper()


class ItineraryDay(BaseModel):
    day: int = Field(description="Day number, starting at 1.")
    date: str = Field(description="Date for this day, YYYY-MM-DD.")
    location: str = Field(description="City/area the traveler is in on this day.")
    morning: str = Field(description="Morning plan.")
    afternoon: str = Field(description="Afternoon plan.")
    evening: str = Field(description="Evening plan.")


class ItineraryPlan(BaseModel):
    days: List[ItineraryDay]


def fetch_flight_options(departure_id: str, arrival_id: str, outbound_date: str, return_date: str = "", top_n: int = 3):
    """Returns up to top_n structured flight options as plain dicts, or raises ValueError on no results/error."""
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
        raise ValueError(results["error"])

    flights = results.get("best_flights", []) + results.get("other_flights", [])
    if not flights:
        raise ValueError("No flights found for these criteria.")

    options = []
    for flight in flights[:top_n]:
        legs = flight.get("flights", [])
        airlines = ", ".join(sorted({leg.get("airline", "Unknown") for leg in legs}))
        duration = flight.get("total_duration", 0)
        options.append({
            "departure_id": departure_id,
            "arrival_id": arrival_id,
            "airlines": airlines,
            "price": flight.get("price", "N/A"),
            "duration_min": duration,
            "stops": max(len(legs) - 1, 0),
            "departure_time": legs[0].get("departure_airport", {}).get("time", "") if legs else "",
            "arrival_time": legs[-1].get("arrival_airport", {}).get("time", "") if legs else "",
        })
    return options


def format_flight_options(options) -> str:
    lines = []
    for opt in options:
        lines.append(
            f"- {opt['airlines']}: ${opt['price']}, {opt['duration_min'] // 60}h {opt['duration_min'] % 60}m, {opt['stops']} stop(s)"
        )
    return "\n".join(lines)


@tool("search_flights", description="Searches real flight options (price, airline, duration, stops) between two airports using Google Flights data via SerpApi.")
def search_flights(departure_id: str, arrival_id: str, outbound_date: str, return_date: str = "") -> str:
    """
    departure_id / arrival_id: IATA airport codes, e.g. JFK, NRT, LHR.
    outbound_date / return_date: YYYY-MM-DD. Omit return_date for a one-way search.
    """
    try:
        options = fetch_flight_options(departure_id, arrival_id, outbound_date, return_date, top_n=5)
    except ValueError as e:
        return str(e)
    return format_flight_options(options)


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
    travel_scout = create_react_agent(
        model=scout_model,
        tools=[internet_search, call_itinerary_research_agent, call_flight_search_agent],
        prompt=TRAVEL_SCOUT_INSTRUCTIONS,
    )
    return travel_scout, itinerary_research_agent


if "messages" not in st.session_state:
    st.session_state.messages = []
if "planner_leg_results" not in st.session_state:
    st.session_state.planner_leg_results = None
if "planner_selected" not in st.session_state:
    st.session_state.planner_selected = {}
if "planner_itinerary" not in st.session_state:
    st.session_state.planner_itinerary = None

if not openai_api_key or not tavily_api_key or not serpapi_api_key:
    st.error("OPENAI_API_KEY, TAVILY_API_KEY, and SERPAPI_API_KEY must be configured on the server - contact the app owner.")
else:
    try:
        travel_scout, itinerary_research_agent = build_travel_scout(openai_api_key, tavily_api_key, serpapi_api_key, model_name)
    except Exception as e:
        st.error(f"Error initializing agent: {e}")
        travel_scout, itinerary_research_agent = None, None

    tab_chat, tab_planner = st.tabs(["💬 Chat", "🧳 Trip Planner"])

    with tab_chat:
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

    with tab_planner:
        st.write(
            "Enter each flight leg, compare real options side by side, pick the one you want, "
            "then generate a day-by-day itinerary built around your confirmed flights."
        )

        num_legs = st.selectbox("Number of flight legs", [1, 2, 3], index=2)

        with st.form("planner_search_form"):
            leg_inputs = []
            for i in range(num_legs):
                st.markdown(f"**Leg {i + 1}**")
                cols = st.columns(3)
                dep = cols[0].text_input("From (city or airport code)", key=f"planner_dep_{i}")
                arr = cols[1].text_input("To (city or airport code)", key=f"planner_arr_{i}")
                dt = cols[2].date_input("Date", key=f"planner_date_{i}")
                leg_inputs.append((dep, arr, dt))
            search_submitted = st.form_submit_button("Search Flights")

        if search_submitted:
            st.session_state.planner_selected = {}
            st.session_state.planner_itinerary = None
            leg_results = []
            with st.spinner("Searching flights..."):
                for dep, arr, dt in leg_inputs:
                    if not dep or not arr:
                        st.error("Please fill in every departure and arrival field.")
                        leg_results = None
                        break
                    dep_code, arr_code, options = dep, arr, []
                    try:
                        dep_code = resolve_airport_code(dep, openai_api_key, model_name)
                        arr_code = resolve_airport_code(arr, openai_api_key, model_name)
                        options = fetch_flight_options(dep_code, arr_code, dt.isoformat(), top_n=3)
                    except ValueError as e:
                        st.warning(f"{dep} -> {arr} on {dt}: {e}")
                    except Exception as e:
                        st.warning(f"Could not resolve or search {dep} -> {arr}: {e}")
                    leg_results.append({
                        "departure_code": dep_code,
                        "arrival_code": arr_code,
                        "date": dt.isoformat(),
                        "options": options,
                    })
            if leg_results is not None:
                st.session_state.planner_leg_results = leg_results

        if st.session_state.planner_leg_results:
            st.write("### Choose Your Flights")
            all_selected = True
            for i, leg in enumerate(st.session_state.planner_leg_results):
                st.markdown(f"#### Leg {i + 1}: {leg['departure_code']} → {leg['arrival_code']} on {leg['date']}")
                if not leg["options"]:
                    st.error("No flights found for this leg.")
                    all_selected = False
                    continue
                cols = st.columns(len(leg["options"]))
                for idx, opt in enumerate(leg["options"]):
                    with cols[idx]:
                        with st.container(border=True):
                            st.markdown(f"**{opt['airlines']}**")
                            st.markdown(f"💰 **${opt['price']}**")
                            st.markdown(f"⏱️ {opt['duration_min'] // 60}h {opt['duration_min'] % 60}m")
                            st.markdown("🛑 Non-stop" if opt["stops"] == 0 else f"🛑 {opt['stops']} stop(s)")
                            if opt.get("departure_time"):
                                st.markdown(f"🛫 {opt['departure_time']}")
                            if opt.get("arrival_time"):
                                st.markdown(f"🛬 {opt['arrival_time']}")
                            is_selected = st.session_state.planner_selected.get(i) == opt
                            if st.button(
                                "✅ Selected" if is_selected else "Select",
                                key=f"planner_select_{i}_{idx}",
                                type="primary" if is_selected else "secondary",
                                use_container_width=True,
                            ):
                                st.session_state.planner_selected[i] = opt
                                st.rerun()
                if i not in st.session_state.planner_selected:
                    all_selected = False

            st.divider()
            if all_selected:
                if st.button("✈️ Confirm Flights & Build Itinerary", type="primary"):
                    flight_summary_lines = []
                    for i, leg in enumerate(st.session_state.planner_leg_results):
                        opt = st.session_state.planner_selected[i]
                        flight_summary_lines.append(
                            f"Leg {i + 1}: {leg['departure_code']} to {leg['arrival_code']} on {leg['date']} - "
                            f"{opt['airlines']}, ${opt['price']}, {opt['duration_min'] // 60}h {opt['duration_min'] % 60}m, {opt['stops']} stop(s)"
                        )
                    flight_summary_text = "\n".join(flight_summary_lines)

                    with st.spinner("Building your itinerary..."):
                        try:
                            query = (
                                "Build a detailed day-by-day itinerary for a trip with these flights ALREADY "
                                "BOOKED and CONFIRMED - do not search for or suggest different flights, just plan "
                                f"activities around them:\n\n{flight_summary_text}\n\nPlan activities, dining, and "
                                "practical tips for each destination for the full span of the trip, from the first "
                                "departure date to the last arrival date."
                            )
                            result = itinerary_research_agent.invoke({"messages": [{"role": "user", "content": query}]})
                            itinerary_text = extract_text(result["messages"][-1].content)

                            structurer = ChatOpenAI(
                                model=model_name, temperature=0.0, openai_api_key=openai_api_key
                            ).with_structured_output(ItineraryPlan)
                            structured = structurer.invoke(
                                "Convert this travel itinerary into structured day-by-day data. "
                                f"Preserve all dates and locations exactly:\n\n{itinerary_text}"
                            )
                            st.session_state.planner_itinerary = structured.days
                        except Exception as e:
                            st.error(f"Error building itinerary: {e}")
            else:
                st.info("Select a flight for every leg to continue.")

        if st.session_state.planner_itinerary:
            st.write("### ✈️ Your Selected Flights")
            flight_rows = []
            for i, leg in enumerate(st.session_state.planner_leg_results):
                opt = st.session_state.planner_selected[i]
                flight_rows.append({
                    "Leg": i + 1,
                    "Route": f"{leg['departure_code']} → {leg['arrival_code']}",
                    "Date": leg["date"],
                    "Airline": opt["airlines"],
                    "Price": f"${opt['price']}",
                    "Duration": f"{opt['duration_min'] // 60}h {opt['duration_min'] % 60}m",
                    "Stops": opt["stops"],
                })
            st.dataframe(flight_rows, use_container_width=True, hide_index=True)

            st.write("### 🗓️ Your Itinerary")
            day_rows = [d.model_dump() for d in st.session_state.planner_itinerary]
            st.dataframe(day_rows, use_container_width=True, hide_index=True)

            if st.button("Start Over"):
                st.session_state.planner_leg_results = None
                st.session_state.planner_selected = {}
                st.session_state.planner_itinerary = None
                st.rerun()
