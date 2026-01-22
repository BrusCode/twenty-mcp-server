"""
Notes tools for Twenty MCP Server
"""

import logging
from typing import Optional
from fastmcp import FastMCP
from ..client import TwentyClientManager, TwentyAPIError

logger = logging.getLogger(__name__)


def register_notes_tools(mcp: FastMCP, client_manager: TwentyClientManager):
    """Register all note-related tools"""

    @mcp.tool()
    async def get_note(
        id: str, workspace: Optional[str] = None
    ) -> dict:
        """Get a note by ID from Twenty CRM

        Args:
            id: The note's ID
            workspace: Workspace name (uses default if not specified)
        """
        try:
            client = client_manager.get_client(workspace)
            result = await client.get_record("notes", id)
            return {"success": True, "note": result}
        except TwentyAPIError as e:
            return {"error": f"Failed to get note: {e.message}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    @mcp.tool()
    async def get_notes(
        limit: int = 20,
        offset: int = 0,
        workspace: Optional[str] = None,
    ) -> dict:
        """List all notes from Twenty CRM with pagination

        Args:
            limit: Maximum number of records to return (default: 20)
            offset: Number of records to skip (default: 0)
            workspace: Workspace name (uses default if not specified)
        """
        try:
            client = client_manager.get_client(workspace)
            result = await client.get_records("notes", limit=limit, offset=offset)
            return {"success": True, "notes": result}
        except TwentyAPIError as e:
            return {"error": f"Failed to get notes: {e.message}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    @mcp.tool()
    async def create_note(
        data: dict, workspace: Optional[str] = None
    ) -> dict:
        """Create a new note in Twenty CRM

        Args:
            data: Note data (e.g., body, personId, companyId, etc.)
            workspace: Workspace name (uses default if not specified)

        Example:
            {
                "body": "Meeting notes from today",
                "person": {"id": "person-id-here"}
            }
        """
        try:
            client = client_manager.get_client(workspace)
            result = await client.create_record("notes", data)
            return {
                "success": True,
                "message": "Note created successfully",
                "note": result,
            }
        except TwentyAPIError as e:
            return {"error": f"Failed to create note: {e.message}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    @mcp.tool()
    async def update_note(
        id: str, data: dict, workspace: Optional[str] = None
    ) -> dict:
        """Update an existing note in Twenty CRM

        Args:
            id: The note's ID
            data: Updated note data (fields to update)
            workspace: Workspace name (uses default if not specified)
        """
        try:
            client = client_manager.get_client(workspace)
            result = await client.update_record("notes", id, data)
            return {
                "success": True,
                "message": f"Note {id} updated successfully",
                "note": result,
            }
        except TwentyAPIError as e:
            return {"error": f"Failed to update note: {e.message}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    @mcp.tool()
    async def delete_note(
        id: str, workspace: Optional[str] = None
    ) -> dict:
        """Delete a note from Twenty CRM

        Args:
            id: The note's ID
            workspace: Workspace name (uses default if not specified)
        """
        try:
            client = client_manager.get_client(workspace)
            await client.delete_record("notes", id)
            return {"success": True, "message": f"Note {id} deleted successfully"}
        except TwentyAPIError as e:
            return {"error": f"Failed to delete note: {e.message}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
