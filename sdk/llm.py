from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()


client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

# for model in client.models.list():
#     print(model.name)

# response = client.models.generate_content(
#     model="models/gemini-2.5-flash",
#     contents="What is Artificial intelligence ?"
# )

# print(response.text)

response = client.models.generate_content(
    model='models/gemini-2.5-flash-image',
    contents='A cartoon infographic for flying sneakers',
    config=types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=types.ImageConfig(
            aspect_ratio="9:16",
        ),
    ),
)

for part in response.parts:
    if part.inline_data:
        generated_image = part.as_image()
        generated_image.show()