from typing import NamedTuple

from pydantic_ai.models import Model, ModelSettings
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings


class ModelConfig(NamedTuple):
    name: str
    model: Model
    settings: ModelSettings


google_config = ModelConfig(
    name="google",
    model=GoogleModel("gemini-2.5-pro"),
    settings=GoogleModelSettings(thinking_config={"include_thoughts": True}),
)

openai_config = ModelConfig(
    name="openai",
    model=OpenAIResponsesModel("gpt-5"),
    settings=OpenAIResponsesModelSettings(
        openai_reasoning_effort="low",
        openai_reasoning_summary="detailed",
    ),
)
