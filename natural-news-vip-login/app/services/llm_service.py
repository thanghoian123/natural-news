from openai import OpenAI
import tiktoken
from app.core.config import API_KEY
from typing import Annotated, AsyncGenerator, List, Tuple

def initialize_client_and_model(llm_selection):
    """Initialize the client and model based on the selected LLM engine."""
    if llm_selection == "Enoch-RC-14-128K":
        client = OpenAI(
            base_url="http://35.170.240.5:8081",
            api_key=API_KEY
        )
        model = 'LLaMA_CPP'
    elif llm_selection == "Qwen2.5-72B-Instruct-32K":
        client = OpenAI(
            base_url="https://api.deepinfra.com/v1/openai",
            api_key=API_KEY
        )
        model = 'Qwen/Qwen2.5-72B-Instruct'
    return client, model

def token_count(content) -> int:
    """Prints a comparison of three string encodings."""
    encoding = tiktoken.get_encoding("o200k_base")
    token_integers = encoding.encode(content)
    num_tokens = len(token_integers)
    return num_tokens

class Workflow:
    def __init__(self, agents):
        self.agents = agents

    async def run(self, input_data) -> AsyncGenerator[dict, None]:
        """Yields agent name, response, and keeps track of total tokens"""
        current_data = input_data
        total_tokens = 0

        # for agent in self.agents:
        #     async for llm_response in agent.act():  # ✅ Iterate properly
        #         yield llm_response  # Stream each chunk

        for agent in self.agents:
            agent.perceive(input_data)

            async for response in agent.act():  # ✅ Iterate over streamed chunks
                yield response  # ✅ Stream chunks asynchronously