import aisuite as ai
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize client with provider configurations
client = ai.Client({
    "openai": {"api_key": os.getenv("OPENAI_API_KEY")},
})

async def ask_openai(message: str, system_prompt: str = "You are a helpful assistant.") -> str:
    # Make a request to any provider
    response = client.chat.completions.create(
        model="openai:gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
    )

    return response.choices[0].message.content