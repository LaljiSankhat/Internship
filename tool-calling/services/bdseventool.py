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

def power(a, b):
    return a ** b

def modulo(a, b):
    return a % b

def percentage(a, b):
    return (a * b) / 100


def normalize_args(args):
    return {
        "a": Decimal(str(args.get("a") or args.get("A"))),
        "b": Decimal(str(args.get("b") or args.get("B")))
    }


OPERATIONS = {
    "power": power,
    "modulo": modulo,
    "percentage": percentage,
    "division": division,
    "multiplication": multiplication,
    "addtion": addtion,
    "substraction": substraction,
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
    },
    {
        "type": "function",
        "function": {
            "name": "power",
            "description": "Raise a to the power of b (a ** b)",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": { "type": "number" },
                    "b": { "type": "number" }
                },
                "required": ["a", "b"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "percentage",
            "description": "Calculate b percent of a",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": { "type": "number" },
                    "b": { "type": "number" }
                },
                "required": ["a", "b"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "modulo",
            "description": "Return the remainder when a is divided by b",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": { "type": "number" },
                    "b": { "type": "number" }
                },
                "required": ["a", "b"]
            }
        }
    }

]

# SYSTEM_PROMPT = """
# You are expert teacher of mathematics who can solve any bodmas complex pattern question.

# Rules:
# - you are only allowed to use the tools provided to you.
# - first you will be given a complex bodmas question in prompt
# - consider questions can not have brackets
# - consider questions can have words like "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"
# - example: "add 2 with 5 multiply 6"
# - example: "two divide by 2 multiply by three add 4"
# - example: "what 2 add 3 multiply 4 modulo 2"
# - convert the question into steps (addition, subtraction, multiplication, division, modulo , percentage, power)
# - ensure operation priority as ("power": 0,          
#     "division": 1,
#     "multiplication": 1,
#     "modulo": 1,
#     "percentage": 1,
#     "addtion": 2,
#     "substraction": 2,)
# - ensure bodmas order is respected
# - use tools for every step
# - if no supported tool found respond: "no supported tool found"
# - if question is invalid respond: "Invalid question"
# - if prompt is not a question respond: "Not a question"
# """

SYSTEM_PROMPT = """
You are an Expert Mathematics Teacher. Your goal is to solve BODMAS/PEMDAS expressions step-by-step using only the provided tools.

OPERATION HIERARCHY (Strict Priority):
1. Level 0: `power` (Highest)
2. Level 1: `division`, `multiplication`, `modulo`, `percentage`
3. Level 2: `addtion`, `substraction` (Lowest)
Note: If multiple operations of the same level exist, solve them from LEFT to RIGHT.

RULES OF ENGAGEMENT:
1. Tool Usage: You must call exactly ONE tool at a time. Wait for the tool output before proceeding to the next step.
2. Text Processing: Convert all word-based numbers (e.g., "seven", "ten") into numerical digits before calling a tool.
3. BODMAS Accuracy: Analyze the entire expression in every turn. Identify the operation with the highest priority and execute it. 
   - Example: For "5 minus 6 multiply 3", you MUST call `multiplication(6, 3)` first. 
   - After receiving the result (18), you then call `substraction(5, 18)`.
4. Operand Integrity: Ensure numbers are passed to the correct arguments. For subtraction (`a - b`) and division (`a / b`), order is critical.
5. Constraint: There are no brackets in these questions.

ERROR HANDLING:
- If the prompt is not a mathematical question: Respond "Not a question".
- If the question contains operations for which no tool exists: Respond "no supported tool found".
- If the question is nonsensical or mathematically impossible (e.g., missing numbers): Respond "Invalid question".

STEP-BY-STEP WORKFLOW:
1. Parse the user's input string.
2. Identify all numbers and operations.
3. Select the operation with the highest priority according to the Hierarchy.
4. Call the corresponding tool.
5. Once you receive the tool result, look at the updated expression and repeat until a final single value is reached.
6. Provide the final numerical result as your concluding response.
"""

MODEL = "groq/llama-3.1-8b-instant"
# MODEL = "gemini/gemini-2.5-flash-lite"

def solve_question(question: str):
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question}
    ]
    current_value = None
    steps = []
    while True:
        response = completion(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        msg = response.choices[0].message
        messages.append(msg)

        if not msg.tool_calls:
            break
        print(msg)
        
        for call in msg.tool_calls:
            name = call.function.name
            raw_args = json.loads(call.function.arguments)

            if name not in OPERATIONS:
                return {"error": "no supported tool found"}
            
            args = normalize_args(raw_args)
            current_value = OPERATIONS[name](args["a"], args["b"])
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


