import logging
import json
import re
from typing import Any
from google.adk.tools.mcp_tool import McpToolset

logger = logging.getLogger("ai_creative_studio.project_manager.notion")

class NotionService:
    """Deterministic service for interacting with Notion via MCP."""
    
    def __init__(self, toolset: McpToolset, agent: Any):
        self.toolset = toolset
        self.agent = agent

    async def _call_tool(self, tool_name: str, payload: dict):
        """Internal helper to call tools via agent (with hooks) or toolset directly."""
        if self.agent:
            # In ADK 2.2.0, the Agent provides the execute_tool method
            return await self.agent.execute_tool(tool_name, payload)
        
        # Fallback for direct toolset access: resolve and call
        tools = await self.toolset.get_tools()
        tool = next((t for t in tools if t.name == tool_name), None)
        if not tool: raise AttributeError(f"Tool {tool_name} not found")
        return await tool.run_async(args=payload, tool_context=None)

    def _parse_mcp_response(self, response: Any) -> dict:
        """Extract and parse JSON from an MCP tool response, handling potential hook modifications."""
        # Support both ToolResponse objects and dicts (if returned by agent hooks)
        if hasattr(response, "to_dict"):
            resp_dict = response.to_dict()
        else:
            resp_dict = response if isinstance(response, dict) else {}

        contents = resp_dict.get("content") or []
        if not contents:
            return {}
        
        text = contents[0].get("text", "{}")
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Check if this is a hook-intercepted error message from handle_notion_error
            # Format: "Notion {status} ({code}): {message}..."
            match = re.search(r"Notion (\d+) \((\w+)\): (.*)", text)
            if match:
                return {
                    "status": int(match.group(1)),
                    "code": match.group(2),
                    "message": match.group(3)
                }
            return {"error": "non_json_response", "text": text}

    async def get_database_schema(self, database_id: str):
        """Retrieve and simplify the database schema."""
        """Retrieve the data source ID, then fetch its property schema."""
        """Retrieve the data source ID, then fetch and simplify its property schema."""
        try:
            db_response = await self._call_tool("retrieve-a-database", {"database_id": database_id})
            db_data = self._parse_mcp_response(db_response)
            
            data_sources = db_data.get("data_sources", [])
            if not data_sources:
                logger.error(f"No data sources found for database {database_id}")
                return None
            data_source_id = data_sources[0]["id"]

            ds_response = await self._call_tool("retrieve-a-data-source", {"data_source_id": data_source_id})
            data = self._parse_mcp_response(ds_response)

            # Extract just names and types for the LLM
            properties = data.get("properties", {})
            simplified = {name: props.get("type") for name, props in properties.items()}
            logger.info(f"simplified schema for {database_id}: {simplified}")
            return {"raw": data, "simplified": simplified, "data_source_id": data_source_id}
        except Exception as e:
            logger.error(f"Failed to fetch schema for {database_id}: {e}")
            return None

    def _normalize_property(self, value, prop_type):
        """Transform flat values into Notion's nested structure based on schema type."""
        if prop_type == "title":
            return {"title": [{"text": {"content": str(value)}}]}
        if prop_type == "rich_text":
            return {"rich_text": [{"text": {"content": str(value)}}]}
        if prop_type == "number":
            return {"number": float(value)}
        if prop_type == "select":
            return {"select": {"name": str(value)}}
        if prop_type == "multi_select":
            return {"multi_select": [{"name": v} for v in (value if isinstance(value, list) else [value])]}
        if prop_type == "date":
            return {"date": {"start": value}}
        return None

    async def create_page(self, database_id: str, data: dict, schema: dict, relation_id: str = None):
        """Create a page with validation and retry logic."""
        properties = {}
        relation_field = None
        raw_props = schema.get("raw", {}).get("properties", {})
        data_source_id = schema.get("data_source_id")

        if not data_source_id:
            logger.error(f"Missing data_source_id for database {database_id}; cannot create page.")
            return None

        # 1. Map and Validate
        title_prop = next((name for name, p in raw_props.items() if p.get("type") == "title"), None)

        for field_name, value in data.items():
            # Case-insensitive matching for LLM flexibility
            if field_name.lower() in ("title", "name", "task") and title_prop:
                properties[title_prop] = self._normalize_property(value, "title")
                continue
            match = next((name for name in raw_props if name.lower() == field_name.lower()), None)
            if match:
                prop_type = raw_props[match].get("type")
                normalized = self._normalize_property(value, prop_type)
                if normalized:
                    properties[match] = normalized

        # 2. Handle Relations (Deterministic linking)
        if relation_id:
            relation_field = next((name for name, p in raw_props.items() if p.get("type") == "relation"), None)
            if relation_field:
                properties[relation_field] = {"relation": [{"id": relation_id}]}

        # 3. Execution with Retry
        payload = {
            "parent": {"type": "data_source_id", "data_source_id": data_source_id},
            "properties": properties
        }
        
        return await self._execute_post_page(payload, "post-page", relation_field)

    async def _execute_post_page(self, payload, tool_name, relation_field_name=None):
        """Internal executor with automatic retry for validation errors."""
        try:
            response = await self._call_tool(tool_name, payload)
            resp_data = self._parse_mcp_response(response)
            logger.info(f"post-page response: {resp_data}")
            if "id" in resp_data:
                return resp_data["id"]

            # Handle common validation errors (e.g. relation field broken)
            status = resp_data.get("status")
            if status == 400:
                if relation_field_name and relation_field_name in payload["properties"]:
                    logger.warning("Relation validation failed. Retrying without relation.")
                    del payload["properties"][relation_field_name]
                    return await self._execute_post_page(payload, tool_name, relation_field_name=None)
            
            error_msg = resp_data.get("message") or resp_data.get("text") or "Unknown error"
            logger.error(f"Notion creation failed: {error_msg}")
            
            return None
        except Exception as e:
            logger.error(f"Notion API error: {e}")
            return None

    async def append_images(self, page_id: str, image_links: list):
        """Append generated image links to the project page body."""
        if not image_links:
            return
            
        children = [
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "📸 Generated Images"}}]}}
        ]
        for link in image_links:
            concept = link.get("concept", "Visual")
            url = link.get("url", "")
            children.append({
                "object": "block", "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": [{"text": {"content": f"{concept}: "}, "href": url}, {"text": {"content": "Open Image"}, "href": url}]}
            })

        try:
            await self._call_tool("patch-block-children", {"block_id": page_id, "children": children})
        except Exception as e:
            logger.error(f"Failed to append images: {e}")

    async def verify_connection(self):
        """Verify that the MCP server is reachable and log available tools."""
        if not self.toolset:
            return

        try:
            logger.info("Verifying MCP server connection...")
            # get_tools() is the verified discovery API in ADK 2.2.0
            tools = await self.toolset.get_tools()
            tool_names = [t.name for t in tools]
            logger.info(f"✅ MCP server reachable. Available tools: {', '.join(tool_names)}")
        except Exception as e:
            logger.error(f"❌ Failed to reach MCP server: {e}")