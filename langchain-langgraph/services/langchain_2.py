from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    max_tokens=100,
    temperature=0.3
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant"),
    ("placeholder", "{messages}")
])

chain = prompt | llm

# You manage memory manually
messages = []

# Turn 1
messages.append(HumanMessage(content="What is RAG?"))
response = chain.invoke({"messages": messages})
messages.append(response)

# Turn 2
messages.append(HumanMessage(content="Why is it useful?"))
response = chain.invoke({"messages": messages})
messages.append(response)

print(response.content)


print(messages)