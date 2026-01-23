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

    def _build_filter_string(self, filter_condition: Optional[Dict[str, Any]]) -> str:
        """Build GraphQL filter string from filter condition"""
        if not filter_condition:
            return ""
        
        # Convert Python dict to GraphQL filter format
        def convert_value(v: Any) -> str:
            if isinstance(v, str):
                return f'"{v}"'
            elif isinstance(v, bool):
                return str(v).lower()
            elif isinstance(v, (int, float)):
                return str(v)
            elif isinstance(v, dict):
                items = [f"{k}: {convert_value(val)}" for k, val in v.items()]
                return "{ " + ", ".join(items) + " }"
            elif isinstance(v, list):
                items = [convert_value(item) for item in v]
                return "[" + ", ".join(items) + "]"
            else:
                return str(v)
        
        return convert_value(filter_condition)

    # Core API Operations

    async def get_records(
        self,
        object_name: str,
        limit: int = 20,
        after: Optional[str] = None,
        filter_condition: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_direction: str = "AscNullsFirst",
    ) -> Dict[str, Any]:
        """Get multiple records with cursor-based pagination
        
        Args:
            object_name: Name of the object (e.g., 'people', 'companies')
            limit: Maximum number of records to return (default: 20)
            after: Cursor for pagination (optional)
            filter_condition: Filter conditions (optional)
            order_by: Field to order by (optional)
            order_direction: Order direction - AscNullsFirst, AscNullsLast, DescNullsFirst, DescNullsLast
        """
        # Build query arguments
        args = [f"first: {limit}"]
        
        if after:
            args.append(f'after: "{after}"')
        
        if filter_condition:
            filter_str = self._build_filter_string(filter_condition)
            args.append(f"filter: {filter_str}")
        
        if order_by:
            # Twenty CRM uses orderBy with field and direction
            args.append(f'orderBy: {{ {order_by}: {order_direction} }}')
        
        args_str = ", ".join(args)

        query = f"""
        query {{
          {object_name}({args_str}) {{
            edges {{
              node {{
                id
                __typename
              }}
              cursor
            }}
            pageInfo {{
              hasNextPage
              hasPreviousPage
              startCursor
              endCursor
            }}
            totalCount
          }}
        }}
        """

        result = await self.execute_query(query)
        return result.get(object_name, {})

    async def get_records_with_fields(
        self,
        object_name: str,
        fields: List[str],
        limit: int = 20,
        after: Optional[str] = None,
        filter_condition: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_direction: str = "AscNullsFirst",
    ) -> Dict[str, Any]:
        """Get multiple records with specific fields
        
        Args:
            object_name: Name of the object (e.g., 'people', 'companies')
            fields: List of field names to retrieve
            limit: Maximum number of records to return (default: 20)
            after: Cursor for pagination (optional)
            filter_condition: Filter conditions (optional)
            order_by: Field to order by (optional)
            order_direction: Order direction
        """
        # Build query arguments
        args = [f"first: {limit}"]
        
        if after:
            args.append(f'after: "{after}"')
        
        if filter_condition:
            filter_str = self._build_filter_string(filter_condition)
            args.append(f"filter: {filter_str}")
        
        if order_by:
            args.append(f'orderBy: {{ {order_by}: {order_direction} }}')
        
        args_str = ", ".join(args)
        fields_str = "\n                ".join(fields)

        query = f"""
        query {{
          {object_name}({args_str}) {{
            edges {{
              node {{
                id
                __typename
                {fields_str}
              }}
              cursor
            }}
            pageInfo {{
              hasNextPage
              hasPreviousPage
              startCursor
              endCursor
            }}
            totalCount
          }}
        }}
        """

        result = await self.execute_query(query)
        return result.get(object_name, {})

    async def get_record(self, object_name: str, record_id: str) -> Dict[str, Any]:
        """Get a single record by ID"""
        # GraphQL singular query - Twenty uses the singular form
        singular_name = self._get_singular_name(object_name)
        
        query = f"""
        query {{
          {singular_name}(filter: {{ id: {{ eq: "{record_id}" }} }}) {{
            edges {{
              node {{
                id
                __typename
              }}
            }}
          }}
        }}
        """

        result = await self.execute_query(query)
        
        # Extract the first record from edges
        edges = result.get(singular_name, {}).get("edges", [])
        if edges:
            return edges[0].get("node", {})
        return {}

    def _get_singular_name(self, object_name: str) -> str:
        """Get singular name for an object (handles special cases)"""
        # Special cases for Twenty CRM objects
        special_cases = {
            "people": "people",  # Twenty uses 'people' for both
            "companies": "companies",
            "opportunities": "opportunities",
            "notes": "notes",
            "tasks": "tasks",
        }
        return special_cases.get(object_name, object_name)

    def _get_mutation_name(self, object_name: str) -> str:
        """Get the correct mutation name for an object"""
        # Twenty CRM mutation naming conventions
        name_map = {
            "people": "Person",
            "companies": "Company",
            "opportunities": "Opportunity",
            "notes": "Note",
            "tasks": "Task",
        }
        return name_map.get(object_name, object_name.rstrip("s").capitalize())

    async def create_record(
        self, object_name: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new record"""
        mutation_name = self._get_mutation_name(object_name)

        # Convert data to GraphQL input format
        data_str = json.dumps(data)

        mutation = f"""
        mutation {{
          create{mutation_name}(data: {data_str}) {{
            id
            __typename
          }}
        }}
        """

        result = await self.execute_mutation(mutation)
        return result.get(f"create{mutation_name}", {})

    async def update_record(
        self, object_name: str, record_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing record"""
        mutation_name = self._get_mutation_name(object_name)

        # Convert data to GraphQL input format
        data_str = json.dumps(data)

        mutation = f"""
        mutation {{
          update{mutation_name}(id: "{record_id}", data: {data_str}) {{
            id
            __typename
          }}
        }}
        """

        result = await self.execute_mutation(mutation)
        return result.get(f"update{mutation_name}", {})

    async def delete_record(self, object_name: str, record_id: str) -> Dict[str, Any]:
        """Delete a record (soft delete)"""
        mutation_name = self._get_mutation_name(object_name)

        mutation = f"""
        mutation {{
          delete{mutation_name}(id: "{record_id}") {{
            id
          }}
        }}
        """

        result = await self.execute_mutation(mutation)
        return result.get(f"delete{mutation_name}", {})

    async def search_records(
        self, 
        object_name: str, 
        search_query: str, 
        limit: int = 20,
        search_fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Basic text search for records
        
        Args:
            object_name: Name of the object to search
            search_query: Search text
            limit: Maximum number of results
            search_fields: List of fields to search in (optional)
        """
        # Build filter based on object type and search query
        if not search_query:
            # If no search query, just return records
            return await self.get_records(object_name, limit)
        
        # Default search fields based on object type
        default_fields = {
            "people": ["name"],
            "companies": ["name"],
            "opportunities": ["name"],
            "notes": ["body"],
            "tasks": ["title"],
        }
        
        fields = search_fields or default_fields.get(object_name, ["name"])
        
        # Build OR filter for multiple fields
        if len(fields) == 1:
            filter_condition = {fields[0]: {"ilike": f"%{search_query}%"}}
        else:
            or_conditions = [{field: {"ilike": f"%{search_query}%"}} for field in fields]
            filter_condition = {"or": or_conditions}
        
        return await self.get_records(object_name, limit, filter_condition=filter_condition)

    async def search_records_complex(
        self,
        object_name: str,
        filters: List[Dict[str, Any]],
        limit: int = 20,
        order_by: Optional[str] = None,
        order_direction: str = "AscNullsFirst",
    ) -> Dict[str, Any]:
        """Complex search with multiple filters
        
        Args:
            object_name: Name of the object to search
            filters: List of filter conditions, each with 'field', 'operator', 'value'
            limit: Maximum number of results
            order_by: Field to order by
            order_direction: Order direction (AscNullsFirst, DescNullsFirst, etc.)
        """
        # Build GraphQL filter object from filters list
        filter_conditions = []
        
        for f in filters:
            field = f.get("field")
            operator = f.get("operator", "eq")
            value = f.get("value")
            
            if not field:
                continue
            
            # Map operators to Twenty CRM GraphQL operators
            operator_map = {
                "eq": "eq",
                "neq": "neq",
                "like": "ilike",
                "ilike": "ilike",
                "gt": "gt",
                "gte": "gte",
                "lt": "lt",
                "lte": "lte",
                "in": "in",
                "contains": "ilike",
                "isNull": "is",
                "isNotNull": "is",
            }
            
            gql_operator = operator_map.get(operator, operator)
            
            # Handle special operators
            if operator == "isNull":
                filter_conditions.append({field: {"is": "NULL"}})
            elif operator == "isNotNull":
                filter_conditions.append({field: {"is": "NOT_NULL"}})
            elif operator in ["like", "ilike", "contains"]:
                filter_conditions.append({field: {gql_operator: f"%{value}%"}})
            else:
                filter_conditions.append({field: {gql_operator: value}})
        
        # Combine filters with AND
        if len(filter_conditions) == 1:
            filter_condition = filter_conditions[0]
        elif len(filter_conditions) > 1:
            filter_condition = {"and": filter_conditions}
        else:
            filter_condition = None
        
        return await self.get_records(
            object_name, 
            limit, 
            filter_condition=filter_condition,
            order_by=order_by,
            order_direction=order_direction
        )

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
                isCustom
                isActive
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
          object(filter: {{ nameSingular: {{ eq: "{object_name}" }} }}) {{
            edges {{
              node {{
                id
                nameSingular
                namePlural
                labelSingular
                labelPlural
                description
                isCustom
                isActive
                fields {{
                  edges {{
                    node {{
                      id
                      name
                      label
                      type
                      description
                      isCustom
                      isActive
                    }}
                  }}
                }}
              }}
            }}
          }}
        }}
        """

        result = await self.execute_query(query)
        edges = result.get("object", {}).get("edges", [])
        if edges:
            return edges[0].get("node", {})
        return {}

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
