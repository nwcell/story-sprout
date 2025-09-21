"""
Extended Grok provider to support newer models not yet in pydantic-ai.
"""

import os

from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider


def create_grok_model(model_name: str, *, api_key: str | None = None) -> OpenAIChatModel:
    """
    Create a Grok model that bypasses pydantic-ai's model name validation.

    This uses the OpenAI-compatible interface with xAI's endpoint.
    """
    api_key = api_key or os.getenv("GROK_API_KEY")
    if not api_key:
        raise ValueError("GROK_API_KEY is required")

    provider = OpenAIProvider(api_key=api_key, base_url="https://api.x.ai/v1")

    # Create OpenAI model with Grok model name and xAI endpoint
    return OpenAIChatModel(model_name, provider=provider)
