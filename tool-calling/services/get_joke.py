import json
import litellm
import requests
from dotenv import load_dotenv

load_dotenv()


def get_joke():
    url = "https://official-joke-api.appspot.com/random_joke"
    
    response = requests.get(url)
    
    # Check if request was successful
    if response.status_code == 200:
        data = response.json()
        setup = data.get("setup")
        punchline = data.get("punchline")
        return f"{setup} — {punchline}"
    else:
        return "Failed to fetch joke 😞"



messages = [
    {
        "role": "system",
        "content": """
            You are an intelligent assistant.

            Use tools ONLY when they are required to answer the user's question.

            - If a question can be answered using tool then use it.
            - if a question can not be answered by tool then answer that no supported tool found.
            - If real-time data, external APIs, or system actions are required, call the appropriate tool.
            - Do NOT call tools unnecessarily.
        """
    },
    {
        "role": "user",
        "content": "what is temprature of Ahmedabad?"
    }
]

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_joke",
            "description": "Get a funny joke",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

response = litellm.completion(
    model="groq/llama-3.1-8b-instant",
    messages=messages,
    tools=tools,
    tool_choice="auto",
)


assistant_message = response.choices[0].message
messages.append(assistant_message.model_dump())

print(assistant_message)

print("\n \n")

if assistant_message.tool_calls != None:
    for tool_call in assistant_message.tool_calls:
        tool_name = tool_call.function.name
        # tool_args = json.loads(tool_call.function.arguments)

        # Call the actual Python function
        tool_result = get_joke()

        # Send tool response back to LLM
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": tool_name,
            "content": json.dumps(tool_result)
        })

        final_response = litellm.completion(
            model="groq/llama-3.1-8b-instant",
            messages=messages
        )
        # print(final_response)
        print(final_response.choices[0].message.content)
else:
    print("No supported tool found for this question")

