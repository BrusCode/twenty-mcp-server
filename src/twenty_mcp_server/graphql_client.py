"""
Twenty CRM GraphQL Client
Handles GraphQL requests to Twenty CRM API
"""

import logging
from typing import Optional, Dict, Any, List
import httpx
import json

from twenty_mcp_server.config import Workspace, Config

logger = logging.getLogger(__name__)


class TwentyAPIError(Exception):
    """Base exception for Twenty API errors"""

    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class TwentyGraphQLClient:
    """GraphQL client for Twenty CRM API"""

    def __init__(self, workspace: Workspace, timeout: int = 30):
        self.workspace = workspace
        self.timeout = timeout
        self.base_url = workspace.base_url.rstrip("/")
        self.api_key = workspace.api_key
        self.graphql_endpoint = f"{self.base_url}/graphql"

    def get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def execute_query(
        self, query: str, variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a GraphQL query"""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        logger.debug(f"Executing GraphQL query: {query[:100]}...")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.graphql_endpoint, headers=self.get_headers(), json=payload
                )

                response.raise_for_status()
                result = response.json()

                # Check for GraphQL errors
                if "errors" in result:
                    error_messages = [e.get("message", str(e)) for e in result["errors"]]
                    raise TwentyAPIError(f"GraphQL errors: {'; '.join(error_messages)}")

                return result.get("data", {})

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} for GraphQL query")
            raise TwentyAPIError(
                f"HTTP {e.response.status_code}: {e.response.text}",
                status_code=e.response.status_code,
            ) from e
        except httpx.TimeoutException as e:
            logger.error(f"Timeout error for GraphQL query")
            raise TwentyAPIError(f"Request timeout - API took too long to respond") from e
        except httpx.RequestError as e:
            logger.error(f"Request error for GraphQL query: {str(e)}")
            raise TwentyAPIError(f"Request failed: {str(e)}") from e

    async def execute_mutation(
        self, mutation: str, variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a GraphQL mutation"""
        return await self.execute_query(mutation, variables)

    # Core API Operations

    async def get_records(
        self,
        object_name: str,
        limit: int = 20,
        filter_condition: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Get multiple records with pagination"""
        filter_str = ""
        if filter_condition:
            filter_str = f", filter: {json.dumps(filter_condition)}"

        query = f"""
        query {{
          {object_name}(first: {limit}{filter_str}) {{
            edges {{
              node {{
                id
                __typename
              }}
            }}
            pageInfo {{
              hasNextPage
              endCursor
            }}
          }}
        }}
        """

        result = await self.execute_query(query)
        return result.get(object_name, {})

    async def get_record(self, object_name: str, record_id: str) -> Dict[str, Any]:
        """Get a single record by ID"""
        # GraphQL singular query
        singular_name = object_name.rstrip("s")  # Simple pluralization
        query = f"""
        query {{
          {singular_name}(id: "{record_id}") {{
            id
            __typename
          }}
        }}
        """

        result = await self.execute_query(query)
        return result.get(singular_name, {})

    async def create_record(
        self, object_name: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new record"""
        singular_name = object_name.rstrip("s")
        capitalized = singular_name.capitalize()

        mutation = f"""
        mutation {{
          create{capitalized}(data: {json.dumps(data)}) {{
            id
            __typename
          }}
        }}
        """

        result = await self.execute_mutation(mutation)
        return result.get(f"create{capitalized}", {})

    async def update_record(
        self, object_name: str, record_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing record"""
        singular_name = object_name.rstrip("s")
        capitalized = singular_name.capitalize()

        mutation = f"""
        mutation {{
          update{capitalized}(id: "{record_id}", data: {json.dumps(data)}) {{
            id
            __typename
          }}
        }}
        """

        result = await self.execute_mutation(mutation)
        return result.get(f"update{capitalized}", {})

    async def delete_record(self, object_name: str, record_id: str) -> Dict[str, Any]:
        """Delete a record"""
        singular_name = object_name.rstrip("s")
        capitalized = singular_name.capitalize()

        mutation = f"""
        mutation {{
          delete{capitalized}(id: "{record_id}") {{
            id
          }}
        }}
        """

        result = await self.execute_mutation(mutation)
        return result.get(f"delete{capitalized}", {})

    async def search_records(
        self, object_name: str, search_query: str, limit: int = 20
    ) -> Dict[str, Any]:
        """Basic text search for records"""
        # GraphQL search with filter
        filter_condition = {"name": {"contains": search_query}}
        return await self.get_records(object_name, limit, filter_condition)

    async def search_records_complex(
        self,
        object_name: str,
        filters: List[Dict[str, Any]],
        limit: int = 20,
        order_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Complex search with multiple filters"""
        # Build GraphQL filter object
        and_filters = {}
        for f in filters:
            field = f.get("field")
            operator = f.get("operator", "eq")
            value = f.get("value")

            if operator == "eq":
                and_filters[field] = {"eq": value}
            elif operator == "contains":
                and_filters[field] = {"contains": value}
            elif operator == "gte":
                and_filters[field] = {"gte": value}
            elif operator == "lte":
                and_filters[field] = {"lte": value}

        return await self.get_records(object_name, limit, {"and": and_filters})

    # Metadata API Operations

    async def get_objects(self) -> Dict[str, Any]:
        """Get all objects in the workspace"""
        query = """
        query {
          objects {
            edges {
              node {
                id
                nameSingular
                namePlural
                labelSingular
                labelPlural
                description
              }
            }
          }
        }
        """

        result = await self.execute_query(query)
        return result.get("objects", {})

    async def get_object_schema(self, object_name: str) -> Dict[str, Any]:
        """Get schema for a specific object"""
        query = f"""
        query {{
          object(nameSingular: "{object_name}") {{
            id
            nameSingular
            namePlural
            labelSingular
            labelPlural
            description
            fields {{
              edges {{
                node {{
                  id
                  name
                  label
                  type
                  description
                }}
              }}
            }}
          }}
        }}
        """

        result = await self.execute_query(query)
        return result.get("object", {})

    async def get_fields(self, object_name: str) -> Dict[str, Any]:
        """Get fields for a specific object"""
        schema = await self.get_object_schema(object_name)
        return schema.get("fields", {})


class TwentyClientManager:
    """Manager for multiple Twenty GraphQL clients (workspaces)"""

    def __init__(self, config: Config):
        self.config = config
        self._clients: Dict[str, TwentyGraphQLClient] = {}

    def get_client(self, workspace_name: Optional[str] = None) -> TwentyGraphQLClient:
        """Get or create a client for a workspace"""
        workspace = self.config.get_workspace(workspace_name)

        if workspace.name not in self._clients:
            self._clients[workspace.name] = TwentyGraphQLClient(
                workspace, timeout=self.config.timeout
            )

        return self._clients[workspace.name]

    def get_all_workspaces(self) -> List[str]:
        """Get list of all workspace names"""
        return self.config.get_all_workspaces()
