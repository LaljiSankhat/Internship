import json
from litellm import completion
from dotenv import load_dotenv
import os

load_dotenv()


def addtion(a: float, b: float) -> float:
    return a + b

def substraction(a: float, b: float) -> float:
    return a - b

def multiplication(a: float, b: float) -> float:
    return a * b

def division(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("division by zero")
    return a / b

tools = [
    {
        "type": "function",
        "function": {
            "name": "addtion",
            "description": "add two numbers",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["a", "b"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "substraction",
            "description": "subtract two numbers",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["a", "b"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "multiplication",
            "description": "multiply two numbers",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["a", "b"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "division",
            "description": "divide two numbers",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["a", "b"]
            }
        }
    }
]

SYSTEM_PROMPT = """
You are expert teacher of mathematics who can solve any bodmas complex pattern question.

Rules:
- you are only allowed to use the tools provided to you.
- first you will be given a complex bodmas question in prompt
- consider questions can not have brackets
- consider questions can have words like "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"
- example: "add 2 with 5 multiply 6"
- example: "two divide by 2 multiply by three add 4"
- convert the question into steps (addition, subtraction, multiplication, division)
- ensure bodmas order is respected
- use tools for every step
- if no supported tool found respond: "no supported tool found"
- if question is invalid respond: "Invalid question"
- if prompt is not a question respond: "Not a question"
"""



TOOL_MAP = {
    "addtion": addtion,
    "substraction": substraction,
    "multiplication": multiplication,
    "division": division
}

MODEL = "groq/llama-3.1-8b-instant"
# MODEL = "gemini/gemini-2.5-flash-lite"

def solve_bodmas(question: str):
    response = completion(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ],
        tools=tools,
        tool_choice="auto"
    )

    msg = response.choices[0].message

    # print(msg)

    if msg.tool_calls == None:
        return {
            "error": "operation not found or invalid question",
            "result": msg.content
        }

    steps = []
    last_value = None

    # print(msg.tool_calls)

    for i, call in enumerate(msg.tool_calls):
        name = call.function.name
        args = json.loads(call.function.arguments)

        if name not in TOOL_MAP:
            return {"error": "no supported tool found"}

        if last_value is not None:
            args["a"] = round(last_value, 2)

        last_value = TOOL_MAP[name](**args)
        print(f"\n : {last_value}")

        steps.append({
            "operation": name,
            "input": args,
            "output": last_value
        })
    
    return {
        "steps": steps,
        "final_answer": last_value
    }



# print(solve_bodmas("what is 2 multiply 3 divide 5 minus 1"))