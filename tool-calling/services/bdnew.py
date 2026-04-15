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


def addition(a, b): return a + b
def subtraction(a, b): return a - b
def multiplication(a, b): return a * b
def division(a, b):
    if b == 0: raise ValueError("division by zero")
    return a / b
def power(a, b): return a ** b
def modulo(a, b): return a % b
def percentage(a, b): return (a * b) / 100

OPERATIONS = {
    "power": power,
    "modulo": modulo,
    "percentage": percentage,
    "division": division,
    "multiplication": multiplication,
    "addition": addition,
    "subtraction": subtraction,
}

def normalize_args(args):
    def to_decimal(x):
        if x is None:
            raise ValueError("Missing operand")
        return Decimal(str(x))

    # Correctly handle 0 as a valid input
    val_a = args.get("a") if args.get("a") is not None else args.get("A")
    val_b = args.get("b") if args.get("b") is not None else args.get("B")

    return {
        "a": to_decimal(val_a),
        "b": to_decimal(val_b),
    }



tools = [
    {"type": "function", "function": {"name": "addition", "description": "add two numbers", "parameters": {"type": "object", "properties": {"a": {"type": "number"}, "b": {"type": "number"}}, "required": ["a", "b"]}}},
    {"type": "function", "function": {"name": "subtraction", "description": "subtract b from a (a - b)", "parameters": {"type": "object", "properties": {"a": {"type": "number"}, "b": {"type": "number"}}, "required": ["a", "b"]}}},
    {"type": "function", "function": {"name": "multiplication", "description": "multiply two numbers", "parameters": {"type": "object", "properties": {"a": {"type": "number"}, "b": {"type": "number"}}, "required": ["a", "b"]}}},
    {"type": "function", "function": {"name": "division", "description": "divide a by b", "parameters": {"type": "object", "properties": {"a": {"type": "number"}, "b": {"type": "number"}}, "required": ["a", "b"]}}},
    {"type": "function", "function": {"name": "power", "description": "a raised to the power of b", "parameters": {"type": "object", "properties": {"a": {"type": "number"}, "b": {"type": "number"}}, "required": ["a", "b"]}}},
    {"type": "function", "function": {"name": "percentage", "description": "Calculate b percent of a", "parameters": {"type": "object", "properties": {"a": {"type": "number"}, "b": {"type": "number"}}, "required": ["a", "b"]}}},
    {"type": "function", "function": {"name": "modulo", "description": "Remainder of a divided by b", "parameters": {"type": "object", "properties": {"a": {"type": "number"}, "b": {"type": "number"}}, "required": ["a", "b"]}}}
]

SYSTEM_PROMPT = """You are a Math Assistant. Solve expressions using BODMAS given in human readable format.
PRIORITY : 1. power | 2. multiplication, division, modulo, percentage | 3. addition, subtraction.
- so always perform PRIORITY wise. top PRIORITY 1 operation are performed befor 2 and 3 same way 2 PRIORITY perform before 3
- read whole question properly nothing should be left
- expression can hava brackates so always calculate the inner brackates first
- expression can also have the simbols for the operations like + for addition, - for subtraction, * for multiplication, / for division, "%" for modulo, ** and ^ for power, for percentage there will be no simbol

Rule: Solve from LEFT to RIGHT within the same PRIORITY level.
Constraint: You MUST call exactly ONE tool at a time and wait for the result.

ERROR HANDLING:
- If the prompt is not a mathematical question: Respond "Not a question".
- If the question contains operations for which no tool exists: Respond "no supported tool found".
- If the question is nonsensical or mathematically impossible (e.g., missing numbers): Respond "Invalid question".

"""

MODEL = "groq/llama-3.3-70b-versatile"
# MODEL = "groq/llama-3.1-8b-instant"
# MODEL = "gemini/gemini-2.5-flash-lite"

def solve_question(question: str):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question}
    ]
    
    steps = []
    final_output = None

    
    for _ in range(10):
        response = completion(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        print(f"step {_} \n \n")

        msg = response.choices[0].message
        messages.append(msg)

        print(f"msg  \n {msg} \n \n")
        
        if not msg.tool_calls:
            final_output = {
                "result": msg.content,
            }
            break
            # return {"Message": "Invalid format or no tool found"}

        
        for call in msg.tool_calls:
            name = call.function.name
            raw_args = json.loads(call.function.arguments)

            if name not in OPERATIONS:
                continue

            try:
                args = normalize_args(raw_args)
                result_val = OPERATIONS[name](args["a"], args["b"])
            except Exception as e:
                return {"error": f"Tool execution failed: {str(e)}"}

            result_rounded = round_decimal(result_val, 2)

            # Record for our final dictionary
            steps.append({
                "operation": name,
                "input": {"a": float(args["a"]), "b": float(args["b"])},
                "output": float(result_rounded)
            })

            
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "name": name,
                "content": str(result_rounded)
            })
            # print(messages)
        
        print(f"steps are \n {msg.tool_calls} \n \n {steps} \n \n ")

    return {
        "steps": steps,
        "final_answer": final_output
    }



