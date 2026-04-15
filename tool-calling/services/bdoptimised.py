import json
from litellm import completion
from dotenv import load_dotenv
import os
from decimal import Decimal, ROUND_HALF_UP
from simpleeval import simple_eval

load_dotenv()

def round_decimal(value, places=2):
    return value.quantize(
        Decimal(f"1.{'0'*places}"),
        rounding=ROUND_HALF_UP
    )

def solve_math(expression: str):
    result = simple_eval(expression.replace('^', '**'))
    return round_decimal(Decimal(str(result)), 2)


tools = [
    {
        "type": "function",
        "function": {
            "name": "solve_math",
            "description": "solve mathematical expression",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string"}
                },
                "required": ["expression"]
            }
        }
    },
]

SYSTEM_PROMPT = """You are a Math Assistant. convert human readable bodmas question into proper mathematical equation.
- read whole question properly nothing should be left
- expresssion can be human readable expression and also mathematical simbol like +, -, / etc.
- expression can hava brackates also.
- expression can also have the simbols for the operations like + for addition, - for subtraction, * for multiplication, / for division, "%" for modulo, ** and ^ for power
- for percentage there will no either written as "% of " of in human readable format like "percent of" , percentage of", "percent" so convert it into mathematical equation you have take first operand divide by 100 and this whole multiply with second operand like expression has "10 percent 20" so you have to make it ((10 / 100) * 20)
- so you have to think and convert question in mathematical equation so tool can solve that equation


Constraint: You MUST use the tool provided to you.

ERROR HANDLING:
- If the prompt is not a mathematical question: Respond "Not a question".
- If the question has not toos : Respond "no supported tool found".
- If the question is nonsensical or mathematically impossible to solve or not identifiable (e.g., missing numbers): Respond "Invalid question".

"""

MODEL = "groq/llama-3.3-70b-versatile"
# MODEL = "groq/llama-3.1-8b-instant"
# MODEL = "gemini/gemini-2.5-flash-lite"

def solve_question(question: str):
    print("hello")
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question}
    ]
    
    steps = []    

    response = completion(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    msg = response.choices[0].message
    messages.append(msg)

    print(f"msg  \n {msg} \n \n")
    
    if not msg.tool_calls:
        final_output = {
            "result": msg.content,
        }
        return final_output
        # return {"Message": "Invalid format or no tool found"}

    print(f"\n {msg.tool_calls} \n ")
    result_rounded = None
    for call in msg.tool_calls:
        name = call.function.name
        raw_args = json.loads(call.function.arguments)

        try:
            result_val = solve_math(raw_args["expression"])
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}

        result_rounded = result_val
        print(result_rounded)

        # Record for our final dictionary
        steps.append({
            "operation": name,
            "input": {"expression": str(raw_args["expression"])},
            "output": float(result_rounded)
        })

        
        messages.append({
            "role": "tool",
            "tool_call_id": call.id,
            "name": name,
            "content": str(result_rounded)
        })
    
    final_response = completion(
        model=MODEL,
        messages=messages,
        tool_choice="none"
    )
    
    print(f"steps are \n {msg.tool_calls} \n \n {steps} \n \n ")

    return {
        "steps": steps,
        "final_answer": result_rounded,
        "final_message": final_response.choices[0].message.content
    }


# print(solve_question("15 percent 40 plus 20 minus 6 modulo 4"))



