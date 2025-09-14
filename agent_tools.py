import requests
import json
from typing import Type, List, Dict
from langchain_core.tools import BaseTool
from langchain_core.pydantic_v1 import BaseModel, Field

API_URL = "http://127.0.0.1:8000"

# --- Tool Input Schemas ---
class PublishHighlightInput(BaseModel):
    highlight_id: str = Field(description="The unique ID of the highlight to publish.")
    platform: str = Field(description="The social media platform to publish to (e.g., 'youtube', 'tiktok').")

class GetReadyHighlightsInput(BaseModel):
    user_id: str = Field(description="The ID of the user to get highlights for.")

# --- The Tools ---
class GetReadyHighlightsTool(BaseTool):
    """Retrieves highlights ready for publishing for a specific user."""
    name: str = "get_ready_highlights_tool"
    description: str = "Queries the backend to get a list of highlights ready to be published. Input must be a user_id."
    args_schema: Type[BaseModel] = GetReadyHighlightsInput

    def _run(self, user_id: str):
        try:
            response = requests.get(f"{API_URL}/api/v1/highlights/{user_id}")
            response.raise_for_status()
            highlights = response.json().get("highlights", [])
            # Return as a JSON string for the LLM to process
            return json.dumps(highlights)
        except requests.exceptions.RequestException as e:
            return f"Error: Failed to fetch highlights. {e}"

class AgentPublishTool(BaseTool):
    """Publishes a highlight clip to a social media platform using the agent's API."""
    name: str = "agent_publish_tool"
    description: str = "Publishes a highlight clip by its ID to a specified social media platform. Input must be highlight_id and platform."
    args_schema: Type[BaseModel] = PublishHighlightInput

    def _run(self, highlight_id: str, platform: str):
        try:
            payload = {"highlight_id": highlight_id, "platform": platform}
            response = requests.post(f"{API_URL}/api/v1/agent-publish", json=payload)
            response.raise_for_status()
            return f"Success: {response.json().get('message')}"
        except requests.exceptions.RequestException as e:
            return f"Error: Failed to publish highlight. {e}"