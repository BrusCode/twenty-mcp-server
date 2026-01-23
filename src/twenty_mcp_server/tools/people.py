"""
People (contacts) tools for Twenty MCP Server
"""

import logging
from typing import Optional
from fastmcp import FastMCP
from twenty_mcp_server.graphql_client import TwentyClientManager, TwentyAPIError

logger = logging.getLogger(__name__)


def register_people_tools(mcp: FastMCP, client_manager: TwentyClientManager):
    """Register all people-related tools"""

    @mcp.tool()
    async def get_person(
        id: str, workspace: Optional[str] = None
    ) -> dict:
        """Get a person by ID from Twenty CRM

        Args:
            id: The person's ID
            workspace: Workspace name (uses default if not specified)
        """
        try:
            client = client_manager.get_client(workspace)
            result = await client.get_record("people", id)
            return {"success": True, "person": result}
        except TwentyAPIError as e:
            return {"error": f"Failed to get person: {e.message}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    @mcp.tool()
    async def get_people(
        limit: int = 20,
        after: Optional[str] = None,
        workspace: Optional[str] = None,
    ) -> dict:
        """List all people from Twenty CRM with cursor-based pagination

        Args:
            limit: Maximum number of records to return (default: 20)
            after: Cursor for pagination - use endCursor from previous response (optional)
            workspace: Workspace name (uses default if not specified)
        """
        try:
            client = client_manager.get_client(workspace)
            result = await client.get_records("people", limit=limit, after=after)
            return {"success": True, "people": result}
        except TwentyAPIError as e:
            return {"error": f"Failed to get people: {e.message}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    @mcp.tool()
    async def create_person(
        data: dict, workspace: Optional[str] = None
    ) -> dict:
        """Create a new person in Twenty CRM

        Args:
            data: Person data (e.g., name, email, phone, city, etc.)
            workspace: Workspace name (uses default if not specified)

        Example:
            {
                "name": {
                    "firstName": "John",
                    "lastName": "Doe"
                },
                "email": "john.doe@example.com",
                "phone": "+1 555-1234",
                "city": "New York"
            }
        """
        try:
            client = client_manager.get_client(workspace)
            result = await client.create_record("people", data)
            return {
                "success": True,
                "message": "Person created successfully",
                "person": result,
            }
        except TwentyAPIError as e:
            return {"error": f"Failed to create person: {e.message}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    @mcp.tool()
    async def update_person(
        id: str, data: dict, workspace: Optional[str] = None
    ) -> dict:
        """Update an existing person in Twenty CRM

        Args:
            id: The person's ID
            data: Updated person data (fields to update)
            workspace: Workspace name (uses default if not specified)
        """
        try:
            client = client_manager.get_client(workspace)
            result = await client.update_record("people", id, data)
            return {
                "success": True,
                "message": f"Person {id} updated successfully",
                "person": result,
            }
        except TwentyAPIError as e:
            return {"error": f"Failed to update person: {e.message}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    @mcp.tool()
    async def delete_person(
        id: str, workspace: Optional[str] = None
    ) -> dict:
        """Delete a person from Twenty CRM

        Args:
            id: The person's ID
            workspace: Workspace name (uses default if not specified)
        """
        try:
            client = client_manager.get_client(workspace)
            await client.delete_record("people", id)
            return {"success": True, "message": f"Person {id} deleted successfully"}
        except TwentyAPIError as e:
            return {"error": f"Failed to delete person: {e.message}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    @mcp.tool()
    async def search_people_basic(
        query: str,
        limit: int = 20,
        workspace: Optional[str] = None,
    ) -> dict:
        """Basic text search for people in Twenty CRM

        Args:
            query: Search text (searches in name field)
            limit: Maximum number of results (default: 20)
            workspace: Workspace name (uses default if not specified)
        """
        try:
            client = client_manager.get_client(workspace)
            result = await client.search_records("people", query, limit=limit)
            return {"success": True, "results": result}
        except TwentyAPIError as e:
            return {"error": f"Failed to search people: {e.message}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    @mcp.tool()
    async def search_people_complex(
        filters: list,
        limit: int = 20,
        order_by: Optional[str] = None,
        order_direction: str = "AscNullsFirst",
        workspace: Optional[str] = None,
    ) -> dict:
        """Advanced search for people with complex filters

        Args:
            filters: List of filter conditions
                Each filter should have: field, operator, value
                Operators: eq, neq, like, ilike, gt, gte, lt, lte, in, isNull, isNotNull
            limit: Maximum number of results (default: 20)
            order_by: Field to order by (optional)
            order_direction: Order direction: AscNullsFirst, AscNullsLast, DescNullsFirst, DescNullsLast (default: AscNullsFirst)
            workspace: Workspace name (uses default if not specified)

        Example:
            [
                {"field": "city", "operator": "eq", "value": "New York"},
                {"field": "createdAt", "operator": "gte", "value": "2024-01-01"}
            ]
        """
        try:
            client = client_manager.get_client(workspace)
            result = await client.search_records_complex(
                "people", filters, limit=limit, order_by=order_by, order_direction=order_direction
            )
            return {"success": True, "results": result}
        except TwentyAPIError as e:
            return {"error": f"Failed to search people: {e.message}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}


def register_people_resources(mcp: FastMCP, client_manager: TwentyClientManager):
    """Register all people-related resources"""

    @mcp.resource("people://list")
    async def list_people_resource() -> str:
        """Get a list of all people as a readable resource"""
        try:
            client = client_manager.get_client()
            result = await client.get_records("people", limit=100)

            edges = result.get("edges", [])
            if not edges:
                return "No people found in the workspace."

            formatted = f"People Directory ({len(edges)} records):\n\n"
            for edge in edges:
                person = edge.get("node", {})
                name = person.get("name", {})
                full_name = " ".join(
                    filter(
                        None,
                        [
                            name.get("firstName") if isinstance(name, dict) else "",
                            name.get("lastName") if isinstance(name, dict) else "",
                        ],
                    )
                ) or "Unknown"
                email = person.get("email") or person.get("primaryEmail") or "No email"
                city = person.get("city") or "No city"
                formatted += f"• {full_name} ({email})\n"
                formatted += f"  ID: {person.get('id', 'Unknown')}, City: {city}\n\n"

            return formatted.strip()
        except Exception as e:
            return f"Error retrieving people: {str(e)}"

    @mcp.resource("people://{id}")
    async def get_person_resource(id: str) -> str:
        """Get detailed person information as a resource"""
        try:
            client = client_manager.get_client()
            result = await client.get_record("people", id)

            if not result:
                return f"Person {id} not found."

            name = result.get("name", {})
            full_name = " ".join(
                filter(None, [
                    name.get("firstName") if isinstance(name, dict) else "",
                    name.get("lastName") if isinstance(name, dict) else ""
                ])
            ) or "Unknown"

            formatted = f"Person Profile - {full_name}\n"
            formatted += f"ID: {result.get('id', 'Unknown')}\n"
            formatted += f"Email: {result.get('email') or result.get('primaryEmail') or 'Not specified'}\n"
            formatted += f"Phone: {result.get('phone') or 'Not specified'}\n"
            formatted += f"City: {result.get('city') or 'Not specified'}\n"
            formatted += f"Created: {result.get('createdAt', 'Unknown')}\n"

            if result.get("company"):
                formatted += f"\nCompany: {result['company'].get('name', 'Unknown')}\n"

            return formatted
        except Exception as e:
            return f"Error retrieving person {id}: {str(e)}"
