"""
Companies (organizations) tools for Twenty MCP Server
"""

import logging
from typing import Optional
from fastmcp import FastMCP
from ..client import TwentyClientManager, TwentyAPIError

logger = logging.getLogger(__name__)


def register_companies_tools(mcp: FastMCP, client_manager: TwentyClientManager):
    """Register all company-related tools"""

    @mcp.tool()
    async def get_company(
        id: str, workspace: Optional[str] = None
    ) -> dict:
        """Get a company by ID from Twenty CRM

        Args:
            id: The company's ID
            workspace: Workspace name (uses default if not specified)
        """
        try:
            client = client_manager.get_client(workspace)
            result = await client.get_record("companies", id)
            return {"success": True, "company": result}
        except TwentyAPIError as e:
            return {"error": f"Failed to get company: {e.message}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    @mcp.tool()
    async def get_companies(
        limit: int = 20,
        offset: int = 0,
        workspace: Optional[str] = None,
    ) -> dict:
        """List all companies from Twenty CRM with pagination

        Args:
            limit: Maximum number of records to return (default: 20)
            offset: Number of records to skip (default: 0)
            workspace: Workspace name (uses default if not specified)
        """
        try:
            client = client_manager.get_client(workspace)
            result = await client.get_records("companies", limit=limit, offset=offset)
            return {"success": True, "companies": result}
        except TwentyAPIError as e:
            return {"error": f"Failed to get companies: {e.message}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    @mcp.tool()
    async def create_company(
        data: dict, workspace: Optional[str] = None
    ) -> dict:
        """Create a new company in Twenty CRM

        Args:
            data: Company data (e.g., name, domainName, address, etc.)
            workspace: Workspace name (uses default if not specified)

        Example:
            {
                "name": "Acme Corp",
                "domainName": "acme.com",
                "address": {
                    "addressStreet1": "123 Main St",
                    "addressCity": "New York",
                    "addressPostcode": "10001",
                    "addressCountry": "US"
                }
            }
        """
        try:
            client = client_manager.get_client(workspace)
            result = await client.create_record("companies", data)
            return {
                "success": True,
                "message": "Company created successfully",
                "company": result,
            }
        except TwentyAPIError as e:
            return {"error": f"Failed to create company: {e.message}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    @mcp.tool()
    async def update_company(
        id: str, data: dict, workspace: Optional[str] = None
    ) -> dict:
        """Update an existing company in Twenty CRM

        Args:
            id: The company's ID
            data: Updated company data (fields to update)
            workspace: Workspace name (uses default if not specified)
        """
        try:
            client = client_manager.get_client(workspace)
            result = await client.update_record("companies", id, data)
            return {
                "success": True,
                "message": f"Company {id} updated successfully",
                "company": result,
            }
        except TwentyAPIError as e:
            return {"error": f"Failed to update company: {e.message}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    @mcp.tool()
    async def delete_company(
        id: str, workspace: Optional[str] = None
    ) -> dict:
        """Delete a company from Twenty CRM

        Args:
            id: The company's ID
            workspace: Workspace name (uses default if not specified)
        """
        try:
            client = client_manager.get_client(workspace)
            await client.delete_record("companies", id)
            return {"success": True, "message": f"Company {id} deleted successfully"}
        except TwentyAPIError as e:
            return {"error": f"Failed to delete company: {e.message}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    @mcp.tool()
    async def search_companies_basic(
        query: str,
        limit: int = 20,
        workspace: Optional[str] = None,
    ) -> dict:
        """Basic text search for companies in Twenty CRM

        Args:
            query: Search text (searches across all fields)
            limit: Maximum number of results (default: 20)
            workspace: Workspace name (uses default if not specified)
        """
        try:
            client = client_manager.get_client(workspace)
            result = await client.search_records("companies", query, limit=limit)
            return {"success": True, "results": result}
        except TwentyAPIError as e:
            return {"error": f"Failed to search companies: {e.message}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    @mcp.tool()
    async def search_companies_complex(
        filters: list,
        limit: int = 20,
        order_by: Optional[str] = None,
        order_direction: str = "ASC",
        workspace: Optional[str] = None,
    ) -> dict:
        """Advanced search for companies with complex filters

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
                {"field": "name", "operator": "like", "value": "Acme"},
                {"field": "createdAt", "operator": "gte", "value": "2024-01-01"}
            ]
        """
        try:
            client = client_manager.get_client(workspace)
            result = await client.search_records_complex(
                "companies",
                filters,
                limit=limit,
                order_by=order_by,
                order_direction=order_direction,
            )
            return {"success": True, "results": result}
        except TwentyAPIError as e:
            return {"error": f"Failed to search companies: {e.message}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}


def register_companies_resources(mcp: FastMCP, client_manager: TwentyClientManager):
    """Register all company-related resources"""

    @mcp.resource("companies://list")
    async def list_companies_resource() -> str:
        """Get a list of all companies as a readable resource"""
        try:
            client = client_manager.get_client()
            result = await client.get_records("companies", limit=100)

            companies = result.get("data", {}).get("companies", [])
            if not companies:
                return "No companies found in the workspace."

            formatted = f"Companies Directory ({len(companies)} records):\n\n"
            for company in companies:
                name = company.get("name", "Unknown")
                domain = company.get("domainName") or "No domain"
                city = company.get("city") or "No city"
                formatted += f"• {name} ({domain})\n"
                formatted += f"  ID: {company.get('id', 'Unknown')}, City: {city}\n\n"

            return formatted.strip()
        except Exception as e:
            return f"Error retrieving companies: {str(e)}"

    @mcp.resource("companies://{id}")
    async def get_company_resource(id: str) -> str:
        """Get detailed company information as a resource"""
        try:
            client = client_manager.get_client()
            result = await client.get_record("companies", id)

            company = result.get("data", {}).get("findCompany", result.get("data", {}))
            if not company:
                return f"Company {id} not found."

            name = company.get("name", "Unknown")

            formatted = f"Company Profile - {name}\n"
            formatted += f"ID: {company.get('id', 'Unknown')}\n"
            formatted += f"Domain: {company.get('domainName') or 'Not specified'}\n"
            formatted += f"City: {company.get('city') or 'Not specified'}\n"
            formatted += f"Employees: {company.get('employees', 'Not specified')}\n"
            formatted += f"Created: {company.get('createdAt', 'Unknown')}\n"

            return formatted
        except Exception as e:
            return f"Error retrieving company {id}: {str(e)}"
