import logging
from dataclasses import dataclass

import litellm
from pydantic_ai import Agent

from apps.ai.engine.base.prompt import render_prompt

logger = logging.getLogger(__name__)


@dataclass
class WriterDeps:
    api_key: str


writer_agent = Agent(
    "openai:gpt-4o",
    deps_type=int,
    output_type=bool,
    system_prompt=("You are a childrens book ghost author.  You are helping ghostwrite childrens stories."),
)


class AIEngine:
    def __init__(self):
        self.model = "gpt-3.5-turbo"
        self.image_model = "dall-e-3"
        self.max_tokens = 1000
        self.temperature = 0.7

    def completion(self, prompt: str, stream: bool = False) -> str:
        response = litellm.completion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            stream=stream,
        )
        logger.info(f"AIEngine: completion response: {response}")
        logger.info(f"AIEngine: completion response content: {response.choices[0].message.content}")
        return response.choices[0].message.content

    def prompt_completion(self, template_name: str, context: dict, stream: bool = False) -> str:
        prompt = render_prompt(template_name, context)
        logger.info(f"AIEngine: prompt_completion prompt: {prompt}")
        return self.completion(prompt, stream=stream)

    def generate_image(self, prompt: str) -> str | None:
        response = litellm.image_generation(
            model=self.image_model, prompt=prompt, size="1024x1024", quality="standard", n=1
        )
        return response.data[0].url
