import datetime
import json
import logging
import os
from typing import Any

from google.genai import Client, types
from google.adk.agents import Agent
from google.adk.events import Event
from dotenv import load_dotenv

try:
    from .retry import GENERATE_CONTENT_CONFIG
    from .notion_service import NotionService
    from .orchestrator import ProjectOrchestrator
except ImportError:
    from retry import GENERATE_CONTENT_CONFIG
    from notion_service import NotionService
    from orchestrator import ProjectOrchestrator

load_dotenv()
logger = logging.getLogger("ai_creative_studio.project_manager")
logger.setLevel(logging.INFO)

def preprocess_notion_tool(tool_name: str, args: dict, tool_context: Any, tool: Any = None) -> tuple[str, dict]:
    """Robustly correct Notion tool name hallucinations."""
    original_name = tool_name
    
    # Extract base name and replace underscores
    name_part = tool_name[4:] if tool_name.startswith("API-") else tool_name
    name_part = name_part.replace("_", "-")
    
    if name_part in ("search", "post-search"):
        tool_name = "API-post-search"
    elif name_part in ("create-page", "post-page"):
        tool_name = "API-post-page"
    elif name_part in ("retrieve-database", "retrieve-a-database"):
        tool_name = "API-retrieve-a-database"
    else:
        tool_name = f"API-{name_part}"

    if tool_name != original_name:
        logger.info(f"Fixed tool hallucination: {original_name} -> {tool_name}")
    return tool_name, args

def handle_notion_error(tool: Any, args: dict, tool_context: Any, tool_response: Any) -> dict | None:
    """Intercept Notion API errors and inject recovery hints."""
    tool_name = getattr(tool, "name", "")
    if not tool_name.startswith("API-"):
        return None

    # tool_response is a ToolResponse in ADK 2.2.0
    if hasattr(tool_response, "to_dict"):
        resp_dict = tool_response.to_dict()
    else:
        resp_dict = tool_response if isinstance(tool_response, dict) else {}
    
    content = (resp_dict.get("content") or [{}])[0].get("text", "")
    try:
        data = json.loads(content)
    except Exception:
        return None

    status = data.get("status")
    if status not in (400, 404):
        return None

    message = data.get("message", "")
    code = data.get("code", "")
    logger.warning("Notion %s (%s) — injecting recovery hint", status, code)

    if status == 404 and code == "object_not_found":
        message = "object_not_found: you passed a database ID as page_id. Use parent database_id instead."

    return {
        "content": [{
            "type": "text",
            "text": f"Notion {status} ({code}): {message}\n\nCheck parameters and retry with corrected values.",
        }]
    }

class OrchestratedAgent(Agent):
    """A specialized ADK Agent that overrides the run loop for Python orchestration."""
    def __init__(self, orchestrator: ProjectOrchestrator, **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, "orchestrator", orchestrator)
        # Link orchestrator back to agent for tool execution context
        orchestrator.agent = self

    async def run_async(self, input: str, tool_context: Any = None):
        """Override standard run loop to use Python orchestration."""
        # Capture context for use in callbacks
        object.__setattr__(self, "_current_tool_context", tool_context)
        # Yield an Event to satisfy the ADK expectation of an AsyncGenerator yielding events
        result = await self.orchestrator.run(input, tool_context=tool_context)
        yield Event(
            author=self.name,
            content=types.Content(
                parts=[types.Part(text=result)]
            )
        )

    async def execute_tool(self, tool_name: str, args: dict) -> dict:
        """Execute a tool while respecting the before/after callbacks."""
        if not self.tools:
            return {"content": [{"type": "text", "text": "Error: No tools configured."}]}

        context = getattr(self, "_current_tool_context", None)
        toolset = self.tools[0]
        
        # 1. Apply name correction via before_tool_callback
        if self.before_tool_callback:
            tool_name, args = self.before_tool_callback(tool_name, args, context, tool=toolset)

        # 2. Execute the tool by resolving the Tool object (ADK 2.2.0 API)
        all_tools = await toolset.get_tools()
        target_tool = next((t for t in all_tools if t.name == tool_name), None)
        
        if not target_tool:
            return {"content": [{"type": "text", "text": f"Error: Tool {tool_name} not found."}]}

        response = await target_tool.run_async(args=args, tool_context=context)

        # 3. Handle errors/intercepts via after_tool_callback
        if self.after_tool_callback:
            hook_result = self.after_tool_callback(target_tool, args, context, response)
            if hook_result:
                return hook_result

        return response

def get_system_instruction(project_database_id=None, tasks_database_id=None):
    notion_guidance = ""
    if project_database_id:
        notion_guidance = f"\nProject DB: {project_database_id}\nTasks DB: {tasks_database_id}\nSync the plan to these Notion databases."

    return f"""You are a Project Manager specializing in creative campaign execution.
    
Today's date is {datetime.date.today().strftime("%B %d, %Y")}.
Your goal is to transform a campaign brief into a structured project plan.{notion_guidance}

Use available tools to search for databases, retrieve schemas, and create pages.
Ensure all timelines are realistic."""

def create_project_manager_agent():
    """Create the Project Manager agent, with Notion MCP if credentials are set."""
    notion_token = os.getenv("NOTION_TOKEN")
    notion_project_db_id = os.getenv("NOTION_PROJECT_DATABASE_ID")
    notion_tasks_db_id = os.getenv("NOTION_TASKS_DATABASE_ID")
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # Client for the orchestrator to use for structured generation
    client = Client(api_key=os.getenv("GOOGLE_API_KEY"))

    if not notion_token:
        logger.warning("Notion credentials not set — running without Notion integration")
        return Agent(
            name="project_manager",
            model=model_name,
            instruction=get_system_instruction(),
            generate_content_config=GENERATE_CONTENT_CONFIG,
            description="Project manager that creates campaign timelines and task breakdowns",
        )

    else:
        from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
        from mcp import StdioServerParameters

        server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@notionhq/notion-mcp-server"],
            env={
                "NOTION_TOKEN": notion_token,
                "PATH": os.environ.get("PATH", ""),
            }
        )
        notion_toolset = McpToolset(
            connection_params=StdioConnectionParams(
                server_params=server_params,
                timeout=30.0
            )
        )

        service = NotionService(notion_toolset, None)
        orchestrator = ProjectOrchestrator(client, service, model_name)

        return OrchestratedAgent(
            orchestrator=orchestrator,
            name="project_manager",
            model=model_name,
            generate_content_config=GENERATE_CONTENT_CONFIG,
            before_tool_callback=preprocess_notion_tool,
            after_tool_callback=handle_notion_error,
            instruction=get_system_instruction(
                project_database_id=notion_project_db_id,
                tasks_database_id=notion_tasks_db_id,
            ),
            description="Project manager with Notion integration for task tracking",
            tools=[notion_toolset],
        )

root_agent = create_project_manager_agent()
logger.info("Project Manager agent created")


if __name__ == "__main__":
    import uvicorn
    from google.adk.a2a.utils.agent_to_a2a import to_a2a

    PORT = int(os.getenv("PORT", "8080"))
    HOST = os.getenv("HOST", "0.0.0.0")
    PUBLIC_HOST = os.getenv("PUBLIC_HOST", "localhost")
    PUBLIC_PORT = int(os.getenv("PUBLIC_PORT", str(PORT)))
    PROTOCOL = os.getenv("PROTOCOL", "http")

    a2a_app = to_a2a(root_agent, host=PUBLIC_HOST, port=PUBLIC_PORT, protocol=PROTOCOL)

    logger.info(f"Starting Project Manager on {PROTOCOL}://{HOST}:{PORT}")
    logger.info(f"Agent card: {PROTOCOL}://{HOST}:{PORT}/.well-known/agent.json")

    uvicorn.run(a2a_app, host=HOST, port=PORT)
