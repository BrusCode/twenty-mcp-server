"""
Configuration management for Twenty MCP Server
Handles multiple workspaces and environment variables
"""

import os
import json
from typing import Optional, Dict, List
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Workspace:
    """Represents a Twenty CRM workspace configuration"""
    name: str
    base_url: str
    api_key: str

    @property
    def is_valid(self) -> bool:
        """Check if workspace configuration is valid"""
        return bool(self.name and self.base_url and self.api_key)


class Config:
    """Configuration manager for Twenty MCP Server"""

    def __init__(self):
        self.workspaces: Dict[str, Workspace] = {}
        self.default_workspace: Optional[str] = None
        self._load_config()

    def _load_config(self):
        """Load configuration from environment variables"""
        workspaces_json = os.getenv("TWENTY_WORKSPACES")
        base_url = os.getenv("TWENTY_BASE_URL")
        api_key = os.getenv("TWENTY_API_KEY")

        if workspaces_json:
            self._load_multiple_workspaces(workspaces_json)
        elif base_url and api_key:
            self._load_single_workspace(base_url, api_key)
        else:
            raise ValueError(
                "Either TWENTY_WORKSPACES or both TWENTY_BASE_URL and TWENTY_API_KEY must be set"
            )

    def _load_multiple_workspaces(self, workspaces_json: str):
        """Load multiple workspaces from JSON string"""
        try:
            data = json.loads(workspaces_json)
            if not isinstance(data, dict) or "workspaces" not in data:
                raise ValueError("Invalid TWENTY_WORKSPACES format")

            for ws_data in data["workspaces"]:
                if not isinstance(ws_data, dict):
                    continue

                workspace = Workspace(
                    name=ws_data.get("name", "default"),
                    base_url=ws_data.get("base_url", "").rstrip("/"),
                    api_key=ws_data.get("api_key", "")
                )

                if workspace.is_valid:
                    self.workspaces[workspace.name] = workspace

            if self.workspaces:
                self.default_workspace = list(self.workspaces.keys())[0]

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in TWENTY_WORKSPACES: {e}")

    def _load_single_workspace(self, base_url: str, api_key: str):
        """Load single workspace from individual env vars"""
        workspace = Workspace(
            name="default",
            base_url=base_url.rstrip("/"),
            api_key=api_key
        )
        self.workspaces["default"] = workspace
        self.default_workspace = "default"

    def get_workspace(self, name: Optional[str] = None) -> Workspace:
        """Get workspace by name or default"""
        if name is None:
            name = self.default_workspace

        if name not in self.workspaces:
            available = ", ".join(self.workspaces.keys())
            raise ValueError(
                f"Workspace '{name}' not found. Available: {available}"
            )

        return self.workspaces[name]

    def get_all_workspaces(self) -> List[str]:
        """Get list of all workspace names"""
        return list(self.workspaces.keys())

    @property
    def log_level(self) -> str:
        """Get log level from environment"""
        return os.getenv("TWENTY_LOG_LEVEL", "INFO")

    @property
    def timeout(self) -> int:
        """Get timeout from environment"""
        return int(os.getenv("TWENTY_TIMEOUT", "30"))

    @property
    def rate_limit(self) -> int:
        """Get rate limit from environment"""
        return int(os.getenv("TWENTY_RATE_LIMIT", "100"))
