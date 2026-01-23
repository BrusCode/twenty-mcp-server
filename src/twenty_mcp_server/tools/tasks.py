"""
Tasks tools for Twenty MCP Server
"""

import logging
from typing import Optional
from fastmcp import FastMCP
from twenty_mcp_server.graphql_client import TwentyClientManager, TwentyAPIError

logger = logging.getLogger(__name__)


def register_tasks_tools(mcp: FastMCP, client_manager: TwentyClientManager):
    """Register all task-related tools"""

    @mcp.tool()
    async def get_task(
        id: str, workspace: Optional[str] = None
    ) -> dict:
        """Get a task by ID from Twenty CRM

        Args:
            id: The task's ID
            workspace: Workspace name (uses default if not specified)
        """
        try:
            client = client_manager.get_client(workspace)
            result = await client.get_record("tasks", id)
            return {"success": True, "task": result}
        except TwentyAPIError as e:
            return {"error": f"Failed to get task: {e.message}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    @mcp.tool()
    async def get_tasks(
        limit: int = 20,
        offset: int = 0,
        workspace: Optional[str] = None,
    ) -> dict:
        """List all tasks from Twenty CRM with pagination

        Args:
            limit: Maximum number of records to return (default: 20)
            offset: Number of records to skip (default: 0)
            workspace: Workspace name (uses default if not specified)
        """
        try:
            client = client_manager.get_client(workspace)
            result = await client.get_records("tasks", limit=limit, offset=offset)
            return {"success": True, "tasks": result}
        except TwentyAPIError as e:
            return {"error": f"Failed to get tasks: {e.message}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    @mcp.tool()
    async def create_task(
        data: dict, workspace: Optional[str] = None
    ) -> dict:
        """Create a new task in Twenty CRM

        Args:
            data: Task data (e.g., title, description, status, dueAt, etc.)
            workspace: Workspace name (uses default if not specified)

        Example:
            {
                "title": "Follow up with client",
                "description": "Call to discuss proposal",
                "status": "Todo",
                "dueAt": "2024-12-31T23:59:59.000Z"
            }
        """
        try:
            client = client_manager.get_client(workspace)
            result = await client.create_record("tasks", data)
            return {
                "success": True,
                "message": "Task created successfully",
                "task": result,
            }
        except TwentyAPIError as e:
            return {"error": f"Failed to create task: {e.message}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    @mcp.tool()
    async def update_task(
        id: str, data: dict, workspace: Optional[str] = None
    ) -> dict:
        """Update an existing task in Twenty CRM

        Args:
            id: The task's ID
            data: Updated task data (fields to update)
            workspace: Workspace name (uses default if not specified)
        """
        try:
            client = client_manager.get_client(workspace)
            result = await client.update_record("tasks", id, data)
            return {
                "success": True,
                "message": f"Task {id} updated successfully",
                "task": result,
            }
        except TwentyAPIError as e:
            return {"error": f"Failed to update task: {e.message}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    @mcp.tool()
    async def delete_task(
        id: str, workspace: Optional[str] = None
    ) -> dict:
        """Delete a task from Twenty CRM

        Args:
            id: The task's ID
            workspace: Workspace name (uses default if not specified)
        """
        try:
            client = client_manager.get_client(workspace)
            await client.delete_record("tasks", id)
            return {"success": True, "message": f"Task {id} deleted successfully"}
        except TwentyAPIError as e:
            return {"error": f"Failed to delete task: {e.message}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
