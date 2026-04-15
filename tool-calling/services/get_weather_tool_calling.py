import json
import litellm
from dotenv import load_dotenv

load_dotenv()


def get_current_weather(location, unit="fahrenheit"):
    if "tokyo" in location.lower():
        return {"location": "Tokyo", "temperature": 10, "unit": "celsius"}
    elif "san francisco" in location.lower():
        return {"location": "San Francisco", "temperature": 72, "unit": "fahrenheit"}
    elif "paris" in location.lower():
        return {"location": "Paris", "temperature": 22, "unit": "celsius"}
    else:
        return {"location": location, "temperature": "unknown"}



messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant that answers weather questions using tool data in simple one line."
    },
    {
        "role": "user",
        "content": "What's the weather like in San Francisco?"
    }
]

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"]
                    }
                },
                "required": ["location"]
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

print(response)

print("\n \n")

if assistant_message.tool_calls:
    for tool_call in assistant_message.tool_calls:
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)

        # Call the actual Python function
        tool_result = get_current_weather(**tool_args)

        # Send tool response back to LLM
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": tool_name,
            "content": json.dumps(tool_result)
        })


print(messages)
print("\n \n")
final_response = litellm.completion(
    model="groq/llama-3.1-8b-instant",
    messages=messages
)


# print(final_response.choices[0].message.content)
print(final_response)













# # Example dummy function hard coded to return the current weather
# import json
# import litellm
# from dotenv import load_dotenv

# load_dotenv()



# def get_current_weather(location, unit="fahrenheit"):
#     """Get the current weather in a given location"""
#     if "tokyo" in location.lower():
#         return json.dumps({"location": "Tokyo", "temperature": "10", "unit": "celsius"})
#     elif "san francisco" in location.lower():
#         return json.dumps(
#             {"location": "San Francisco", "temperature": "72", "unit": "fahrenheit"}
#         )
#     elif "paris" in location.lower():
#         return json.dumps({"location": "Paris", "temperature": "22", "unit": "celsius"})
#     else:
#         return json.dumps({"location": location, "temperature": "unknown"})




# # Step 1: send the conversation and available functions to the model
# messages = [
#     {
#         "role": "system",
#         "content": "You are a function calling LLM that uses the data extracted from get_current_weather to answer questions about the weather in San Francisco.",
#     },
#     {
#         "role": "user",
#         "content": "What's the weather like in San Francisco?",
#     },
# ]
# tools = [
#     {
#         "type": "function",
#         "function": {
#             "name": "get_current_weather",
#             "description": "Get the current weather in a given location",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "location": {
#                         "type": "string",
#                         "description": "The city and state, e.g. San Francisco, CA",
#                     },
#                     "unit": {
#                         "type": "string",
#                         "enum": ["celsius", "fahrenheit"],
#                     },
#                 },
#                 "required": ["location"],
#             },
#         },
#     }
# ]


# response = litellm.completion(
#     model="groq/llama-3.1-8b-instant",
#     messages=messages,
#     tools=tools,
#     tool_choice="auto",  # auto is default, but we'll be explicit
# )
# print("Response\n", response)
# response_message = response.choices[0].message  
# tool_calls = response_message.tool_calls
# print(response_message)


