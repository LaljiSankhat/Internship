import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

HUGGINGFACE_API_KEY = os.getenv("HF_TOKEN")

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HUGGINGFACE_API_KEY,
)

completion = client.chat.completions.create(
    model="meta-llama/Llama-3.1-8B-Instruct",
    messages=[
        {
            "role": "user",
            "content": "What is cepital of france ?"
        },
        {
            "role": "system",
            "content": "you are grametical person who find first grammetical mistakes then answer"
        },
        
    ],
)

print(completion.choices[0].message.content)


