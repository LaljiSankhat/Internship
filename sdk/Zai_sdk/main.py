import zai
import os
from dotenv import load_dotenv


load_dotenv()

print(zai.__version__)

from zai import ZaiClient

# Initialize client
client = ZaiClient(api_key=os.getenv("Z_API_KEY"))

image_url = "https://cdn.bigmodel.cn/static/logo/introduction.png"

# Call layout parsing API
response = client.layout_parsing.create(
    model="glm-ocr",
    file=image_url
)

# Output result
print(response)