from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
load_dotenv()

llm = ChatOpenAI(
    model="glm-4.7-flash",
    openai_api_base="https://open.bigmodel.cn/api/paas/v4/",
    openai_api_key=os.getenv("Z_API_KEY")
)

response = llm.invoke("Explain LangChain in simple terms")

print(response.content)
