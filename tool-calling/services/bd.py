import json
from litellm import completion
from dotenv import load_dotenv
import os
from decimal import Decimal, ROUND_HALF_UP

load_dotenv()



def round_decimal(value, places=2):
    return value.quantize(
        Decimal(f"1.{'0'*places}"),
        rounding=ROUND_HALF_UP
    )



def addtion(a, b):
    return a + b

def substraction(a, b):
    return a - b

def multiplication(a, b):
    return a * b

def division(a, b):
    if b == 0:
        raise ValueError("division by zero")
    return a / b

def normalize_args(args):
    return {
        "a": Decimal(str(args.get("a") or args.get("A"))),
        "b": Decimal(str(args.get("b") or args.get("B")))
    }


BODMAS_PRIORITY = {
    "division": 1,
    "multiplication": 1,
    "addtion": 2,
    "substraction": 2,
}



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

    if not msg.tool_calls:
        return {
            "error": "operation not found or invalid question",
            "result": msg.content
        }

    # Collect operations
    operations = []
    for call in msg.tool_calls:
        name = call.function.name
        raw_args = json.loads(call.function.arguments)

        if name not in TOOL_MAP:
            return {"error": "no supported tool found"}

        args = normalize_args(raw_args)
        operations.append((name, args))

    
    operations.sort(key=lambda x: BODMAS_PRIORITY[x[0]])

    steps = []
    current_value = None

    for name, args in operations:
        if current_value is not None:
            args["a"] = current_value

        current_value = TOOL_MAP[name](args["a"], args["b"])
        current_value = round_decimal(current_value, 2)

        steps.append({
            "operation": name,
            "input": {
                "a": float(args["a"]),
                "b": float(args["b"])
            },
            "output": float(current_value)
        })

    return {
        "steps": steps,
        "final_answer": float(current_value)
    }


# print(solve_bodmas("what is 2 multiply 3 divide 5 minus 1"))