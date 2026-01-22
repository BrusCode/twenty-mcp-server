"""
Opportunities (deals) tools for Twenty MCP Server
"""

import logging
from typing import Optional
from fastmcp import FastMCP
from twenty_mcp_server.client import TwentyClientManager, TwentyAPIError

logger = logging.getLogger(__name__)


def register_opportunities_tools(mcp: FastMCP, client_manager: TwentyClientManager):
    """Register all opportunity-related tools"""

    @mcp.tool()
    async def get_opportunity(
        id: str, workspace: Optional[str] = None
    ) -> dict:
        """Get an opportunity by ID from Twenty CRM

        Args:
            id: The opportunity's ID
            workspace: Workspace name (uses default if not specified)
        """
        try:
            client = client_manager.get_client(workspace)
            result = await client.get_record("opportunities", id)
            return {"success": True, "opportunity": result}
        except TwentyAPIError as e:
            return {"error": f"Failed to get opportunity: {e.message}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    @mcp.tool()
    async def get_opportunities(
        limit: int = 20,
        offset: int = 0,
        workspace: Optional[str] = None,
    ) -> dict:
        """List all opportunities from Twenty CRM with pagination

        Args:
            limit: Maximum number of records to return (default: 20)
            offset: Number of records to skip (default: 0)
            workspace: Workspace name (uses default if not specified)
        """
        try:
            client = client_manager.get_client(workspace)
            result = await client.get_records("opportunities", limit=limit, offset=offset)
            return {"success": True, "opportunities": result}
        except TwentyAPIError as e:
            return {"error": f"Failed to get opportunities: {e.message}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    @mcp.tool()
    async def create_opportunity(
        data: dict, workspace: Optional[str] = None
    ) -> dict:
        """Create a new opportunity in Twenty CRM

        Args:
            data: Opportunity data (e.g., name, amount, currency, stage, company, etc.)
            workspace: Workspace name (uses default if not specified)

        Example:
            {
                "name": "Enterprise Deal",
                "amount": 50000,
                "currency": "USD",
                "stage": "Proposal",
                "company": {"id": "company-id-here"}
            }
        """
        try:
            client = client_manager.get_client(workspace)
            result = await client.create_record("opportunities", data)
            return {
                "success": True,
                "message": "Opportunity created successfully",
                "opportunity": result,
            }
        except TwentyAPIError as e:
            return {"error": f"Failed to create opportunity: {e.message}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    @mcp.tool()
    async def update_opportunity(
        id: str, data: dict, workspace: Optional[str] = None
    ) -> dict:
        """Update an existing opportunity in Twenty CRM

        Args:
            id: The opportunity's ID
            data: Updated opportunity data (fields to update)
            workspace: Workspace name (uses default if not specified)
        """
        try:
            client = client_manager.get_client(workspace)
            result = await client.update_record("opportunities", id, data)
            return {
                "success": True,
                "message": f"Opportunity {id} updated successfully",
                "opportunity": result,
            }
        except TwentyAPIError as e:
            return {"error": f"Failed to update opportunity: {e.message}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    @mcp.tool()
    async def delete_opportunity(
        id: str, workspace: Optional[str] = None
    ) -> dict:
        """Delete an opportunity from Twenty CRM

        Args:
            id: The opportunity's ID
            workspace: Workspace name (uses default if not specified)
        """
        try:
            client = client_manager.get_client(workspace)
            await client.delete_record("opportunities", id)
            return {"success": True, "message": f"Opportunity {id} deleted successfully"}
        except TwentyAPIError as e:
            return {"error": f"Failed to delete opportunity: {e.message}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    @mcp.tool()
    async def search_opportunities_basic(
        query: str,
        limit: int = 20,
        workspace: Optional[str] = None,
    ) -> dict:
        """Basic text search for opportunities in Twenty CRM

        Args:
            query: Search text (searches across all fields)
            limit: Maximum number of results (default: 20)
            workspace: Workspace name (uses default if not specified)
        """
        try:
            client = client_manager.get_client(workspace)
            result = await client.search_records("opportunities", query, limit=limit)
            return {"success": True, "results": result}
        except TwentyAPIError as e:
            return {"error": f"Failed to search opportunities: {e.message}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    @mcp.tool()
    async def search_opportunities_complex(
        filters: list,
        limit: int = 20,
        order_by: Optional[str] = None,
        order_direction: str = "ASC",
        workspace: Optional[str] = None,
    ) -> dict:
        """Advanced search for opportunities with complex filters

        Args:
            filters: List of filter conditions
                Each filter should have: field, operator, value
                Operators: eq, neq, like, ilike, gt, gte, lt, lte, in, isNull, isNotNull
            limit: Maximum number of results (default: 20)
            order_by: Field to order by (optional)
            order_direction: Order direction: ASC or DESC (default: ASC)
            workspace: Workspace name (uses default if not specified)

        Example:
            [
                {"field": "stage", "operator": "eq", "value": "Proposal"},
                {"field": "amount", "operator": "gte", "value": 10000}
            ]
        """
        try:
            client = client_manager.get_client(workspace)
            result = await client.search_records_complex(
                "opportunities",
                filters,
                limit=limit,
                order_by=order_by,
                order_direction=order_direction,
            )
            return {"success": True, "results": result}
        except TwentyAPIError as e:
            return {"error": f"Failed to search opportunities: {e.message}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}


def register_opportunities_resources(mcp: FastMCP, client_manager: TwentyClientManager):
    """Register all opportunity-related resources"""

    @mcp.resource("opportunities://list")
    async def list_opportunities_resource() -> str:
        """Get a list of all opportunities as a readable resource"""
        try:
            client = client_manager.get_client()
            result = await client.get_records("opportunities", limit=100)

            opportunities = result.get("data", {}).get("opportunities", [])
            if not opportunities:
                return "No opportunities found in the workspace."

            formatted = f"Opportunities Directory ({len(opportunities)} records):\n\n"
            for opp in opportunities:
                name = opp.get("name", "Unknown")
                stage = opp.get("stage") or "No stage"
                amount = opp.get("amount") or 0
                currency = opp.get("currency") or "USD"
                formatted += f"• {name} ({currency} {amount})\n"
                formatted += f"  ID: {opp.get('id', 'Unknown')}, Stage: {stage}\n\n"

            return formatted.strip()
        except Exception as e:
            return f"Error retrieving opportunities: {str(e)}"

    @mcp.resource("opportunities://{id}")
    async def get_opportunity_resource(id: str) -> str:
        """Get detailed opportunity information as a resource"""
        try:
            client = client_manager.get_client()
            result = await client.get_record("opportunities", id)

            opportunity = (
                result.get("data", {}).get("findOpportunity", result.get("data", {}))
            )
            if not opportunity:
                return f"Opportunity {id} not found."

            name = opportunity.get("name", "Unknown")

            formatted = f"Opportunity Profile - {name}\n"
            formatted += f"ID: {opportunity.get('id', 'Unknown')}\n"
            formatted += f"Stage: {opportunity.get('stage') or 'Not specified'}\n"
            formatted += (
                f"Amount: {opportunity.get('amount', 0)} {opportunity.get('currency', 'USD')}\n"
            )
            formatted += f"Probability: {opportunity.get('probability', 'Not specified')}%\n"
            formatted += f"Expected Close: {opportunity.get('expectedCloseDate', 'Not specified')}\n"
            formatted += f"Created: {opportunity.get('createdAt', 'Unknown')}\n"

            if opportunity.get("company"):
                formatted += f"\nCompany: {opportunity['company'].get('name', 'Unknown')}\n"

            return formatted
        except Exception as e:
            return f"Error retrieving opportunity {id}: {str(e)}"
