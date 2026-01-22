"""
Metadata tools for Twenty MCP Server
Provides schema and workspace information
"""

import logging
from typing import Optional
from fastmcp import FastMCP
from ..client import TwentyClientManager, TwentyAPIError

logger = logging.getLogger(__name__)


def register_metadata_tools(mcp: FastMCP, client_manager: TwentyClientManager):
    """Register all metadata-related tools"""

    @mcp.tool()
    async def get_objects(workspace: Optional[str] = None) -> dict:
        """Get all objects in the Twenty CRM workspace

        Args:
            workspace: Workspace name (uses default if not specified)
        """
        try:
            client = client_manager.get_client(workspace)
            result = await client.get_objects()
            return {"success": True, "objects": result}
        except TwentyAPIError as e:
            return {"error": f"Failed to get objects: {e.message}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    @mcp.tool()
    async def get_object_schema(
        object_name: str, workspace: Optional[str] = None
    ) -> dict:
        """Get schema for a specific object in Twenty CRM

        Args:
            object_name: Name of the object (e.g., people, companies, opportunities)
            workspace: Workspace name (uses default if not specified)
        """
        try:
            client = client_manager.get_client(workspace)
            result = await client.get_object_schema(object_name)
            return {"success": True, "schema": result}
        except TwentyAPIError as e:
            return {"error": f"Failed to get object schema: {e.message}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    @mcp.tool()
    async def get_fields(
        object_name: str, workspace: Optional[str] = None
    ) -> dict:
        """Get fields for a specific object in Twenty CRM

        Args:
            object_name: Name of the object (e.g., people, companies, opportunities)
            workspace: Workspace name (uses default if not specified)
        """
        try:
            client = client_manager.get_client(workspace)
            result = await client.get_fields(object_name)
            return {"success": True, "fields": result}
        except TwentyAPIError as e:
            return {"error": f"Failed to get fields: {e.message}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"


def register_metadata_resources(mcp: FastMCP, client_manager: TwentyClientManager):
    """Register all metadata-related resources"""

    @mcp.resource("schema://objects")
    async def schema_objects_resource() -> str:
        """Get schema of all objects as a readable resource"""
        try:
            client = client_manager.get_client()
            result = await client.get_objects()

            objects = result.get("data", {}).get("objects", [])
            if not objects:
                return "No objects found in the workspace."

            formatted = f"Workspace Schema - Objects ({len(objects)} total):\n\n"
            for obj in objects:
                name = obj.get("nameSingular", "Unknown")
                label = obj.get("labelSingular", "Unknown")
                description = obj.get("description", "No description")
                formatted += f"• {name} ({label})\n"
                formatted += f"  Plural: {obj.get('namePlural', 'Unknown')}\n"
                formatted += f"  Description: {description}\n\n"

            return formatted.strip()
        except Exception as e:
            return f"Error retrieving schema: {str(e)}"
