from litellm import completion
import os

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# e.g. Call 'WizardLM/WizardCoder-Python-34B-V1.0' hosted on HF Inference endpoints
response = completion(
  model="huggingface/WizardLM/WizardCoder-Python-34B-V1.0",
  messages=[{ "content": "Hello, how are you?","role": "user"}],
  api_base="https://router.huggingface.co/v1",
  api_key=HUGGINGFACE_API_KEY
)

print(response)