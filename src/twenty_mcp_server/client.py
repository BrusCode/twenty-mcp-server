"""
Twenty CRM API Client
Handles HTTP requests to Twenty CRM REST API
"""

import logging
from typing import Optional, Dict, Any, List
import httpx
from datetime import datetime, timedelta

from twenty_mcp_server.config import Workspace, Config

logger = logging.getLogger(__name__)


class TwentyAPIError(Exception):
    """Base exception for Twenty API errors"""

    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class TwentyClient:
    """HTTP client for Twenty CRM API"""

    def __init__(self, workspace: Workspace, timeout: int = 30):
        self.workspace = workspace
        self.timeout = timeout
        self.base_url = workspace.base_url
        self.api_key = workspace.api_key

    def get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an HTTP request to the Twenty API"""
        url = f"{self.base_url}{endpoint}"
        headers = self.get_headers()

        logger.debug(f"Making {method} request to {url}")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method == "GET":
                    response = await client.get(url, headers=headers, params=params)
                elif method == "POST":
                    response = await client.post(url, headers=headers, json=data)
                elif method == "PATCH":
                    response = await client.patch(url, headers=headers, json=data)
                elif method == "DELETE":
                    response = await client.delete(url, headers=headers)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                response.raise_for_status()

                result = response.json()

                # Handle empty responses
                if response.status_code == 204 or not result:
                    return {"success": True}

                return result

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} for {method} {url}")
            raise TwentyAPIError(
                f"HTTP {e.response.status_code}: {e.response.text}",
                status_code=e.response.status_code,
            ) from e
        except httpx.TimeoutException as e:
            logger.error(f"Timeout error for {method} {url}")
            raise TwentyAPIError(f"Request timeout - API took too long to respond") from e
        except httpx.RequestError as e:
            logger.error(f"Request error for {method} {url}: {str(e)}")
            raise TwentyAPIError(f"Request failed: {str(e)}") from e

    # Core API Operations

    async def get_record(self, object_name: str, record_id: str) -> Dict[str, Any]:
        """Get a single record by ID"""
        return await self.make_request("GET", f"/rest/{object_name}/{record_id}")

    async def get_records(
        self,
        object_name: str,
        limit: int = 20,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Get multiple records with pagination"""
        params = {"limit": limit, "offset": offset}

        if filters:
            params.update(filters)

        return await self.make_request("GET", f"/rest/{object_name}", params=params)

    async def create_record(
        self, object_name: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new record"""
        return await self.make_request("POST", f"/rest/{object_name}", data=data)

    async def update_record(
        self, object_name: str, record_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing record"""
        return await self.make_request(
            "PATCH", f"/rest/{object_name}/{record_id}", data=data
        )

    async def delete_record(self, object_name: str, record_id: str) -> Dict[str, Any]:
        """Delete a record"""
        return await self.make_request("DELETE", f"/rest/{object_name}/{record_id}")

    async def search_records(
        self, object_name: str, query: str, limit: int = 20
    ) -> Dict[str, Any]:
        """Basic text search for records"""
        params = {"query": query, "limit": limit}
        return await self.make_request("GET", f"/rest/{object_name}/search", params=params)

    async def search_records_complex(
        self,
        object_name: str,
        filters: List[Dict[str, Any]],
        limit: int = 20,
        order_by: Optional[str] = None,
        order_direction: str = "ASC",
    ) -> Dict[str, Any]:
        """Complex search with filters"""
        data = {
            "filter": {
                "and": filters,
            },
            "limit": limit,
        }

        if order_by:
            data["orderBy"] = order_by
            data["orderDirection"] = order_direction

        return await self.make_request("POST", f"/rest/{object_name}/search", data=data)

    # Metadata API Operations

    async def get_objects(self) -> Dict[str, Any]:
        """Get all objects in the workspace"""
        return await self.make_request("GET", "/rest/metadata/objects")

    async def get_object_schema(self, object_name: str) -> Dict[str, Any]:
        """Get schema for a specific object"""
        return await self.make_request("GET", f"/rest/metadata/objects/{object_name}")

    async def get_fields(self, object_name: str) -> Dict[str, Any]:
        """Get fields for a specific object"""
        return await self.make_request("GET", f"/rest/metadata/objects/{object_name}/fields")


class TwentyClientManager:
    """Manager for multiple Twenty clients (workspaces)"""

    def __init__(self, config: Config):
        self.config = config
        self._clients: Dict[str, TwentyClient] = {}

    def get_client(self, workspace_name: Optional[str] = None) -> TwentyClient:
        """Get or create a client for a workspace"""
        workspace = self.config.get_workspace(workspace_name)

        if workspace.name not in self._clients:
            self._clients[workspace.name] = TwentyClient(
                workspace, timeout=self.config.timeout
            )

        return self._clients[workspace.name]

    def get_all_workspaces(self) -> List[str]:
        """Get list of all workspace names"""
        return self.config.get_all_workspaces()
