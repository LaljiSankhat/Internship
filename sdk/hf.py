from litellm import completion
import os
from dotenv import load_dotenv
load_dotenv()

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

response = completion(
    model="huggingface/WizardLM/WizardCoder-Python-34B-V1.0",
    messages=[{"role": "user", "content": "Hello, how are you?"}]
)

print(response)
