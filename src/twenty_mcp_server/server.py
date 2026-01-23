"""
Main MCP Server for Twenty CRM
Uses FastMCP to provide MCP protocol support
"""

import logging
import argparse
from typing import Optional
from fastmcp import FastMCP
from twenty_mcp_server.config import Config
from twenty_mcp_server.graphql_client import TwentyClientManager, TwentyAPIError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

mcp = FastMCP("Twenty CRM Server")

config = None
client_manager = None


def initialize_server():
    """Initialize the server with configuration"""
    global config, client_manager

    try:
        config = Config()
        client_manager = TwentyClientManager(config)
        logger.info(
            f"Twenty MCP Server initialized with {len(config.workspaces)} workspace(s)"
        )
        return True
    except Exception as e:
        logger.error(f"Failed to initialize server: {e}")
        return False


# Import tools after server is initialized to avoid circular imports
def register_tools():
    """Register all MCP tools and resources"""
    try:
        from twenty_mcp_server.tools.people import register_people_tools, register_people_resources
        from twenty_mcp_server.tools.companies import register_companies_tools, register_companies_resources
        from twenty_mcp_server.tools.opportunities import (
            register_opportunities_tools,
            register_opportunities_resources,
        )
        from twenty_mcp_server.tools.notes import register_notes_tools
        from twenty_mcp_server.tools.tasks import register_tasks_tools
        from twenty_mcp_server.tools.metadata import register_metadata_tools, register_metadata_resources

        register_people_tools(mcp, client_manager)
        register_people_resources(mcp, client_manager)
        register_companies_tools(mcp, client_manager)
        register_companies_resources(mcp, client_manager)
        register_opportunities_tools(mcp, client_manager)
        register_opportunities_resources(mcp, client_manager)
        register_notes_tools(mcp, client_manager)
        register_tasks_tools(mcp, client_manager)
        register_metadata_tools(mcp, client_manager)
        register_metadata_resources(mcp, client_manager)

        logger.info("All tools and resources registered successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to register tools: {e}")
        import traceback

        traceback.print_exc()
        return False


@mcp.tool()
async def list_workspaces() -> dict:
    """List all configured workspaces"""
    if not client_manager:
        return {"error": "Server not initialized"}

    workspaces = client_manager.get_all_workspaces()
    return {"workspaces": workspaces, "default": config.default_workspace}


@mcp.tool()
async def get_workspace_info(workspace: Optional[str] = None) -> dict:
    """Get information about a specific workspace

    Args:
        workspace: Workspace name (uses default if not specified)
    """
    if not client_manager:
        return {"error": "Server not initialized"}

    try:
        workspace_obj = config.get_workspace(workspace)
        return {
            "name": workspace_obj.name,
            "base_url": workspace_obj.base_url,
            "is_default": workspace_obj.name == config.default_workspace,
        }
    except Exception as e:
        return {"error": str(e)}


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Twenty MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "http", "streamable-http"],
        default="stdio",
        help="Transport protocol to use (default: stdio)",
    )
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (for SSE/HTTP)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to (for SSE/HTTP)")

    args = parser.parse_args()

    transport = args.transport
    logger.info(f"Starting server with transport: {transport}")

    if transport == "stdio":
        mcp.run(transport="stdio")
    elif transport == "sse":
        mcp.run(transport="sse", host=args.host, port=args.port)
    elif transport in ["http", "streamable-http"]:
        mcp.run(transport="streamable-http", host=args.host, port=args.port)


# Initialize server and register tools at module import time for FastMCP Cloud
if initialize_server():
    register_tools()
else:
    logger.warning("Server initialization failed - tools not registered")


if __name__ == "__main__":
    main()
