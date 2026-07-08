import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

_client: OpenAI = None

def get_llm_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=os.getenv("API_KEY"),
            base_url=os.getenv("BASE_URL"),
        )
    return _client

def chat(messages: list, temperature: float = 0.7) -> str:
    client = get_llm_client()
    response = client.chat.completions.create(
        model=os.getenv("MODEL_ID", "claude-sonnet-4-6"),
        messages=messages,
        temperature=temperature,
        stream=False,
    )
    return response.choices[0].message.content
