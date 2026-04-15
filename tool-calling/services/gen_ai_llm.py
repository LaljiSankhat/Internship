import base64
import json
import os
from dotenv import load_dotenv
from litellm import completion


load_dotenv()
# print(os.getenv("GEMINI_API_KEY"))

# MODEL = "gemini/gemini-2.5-flash"
MODEL = "gemini/gemini-2.5-flash-lite"

PROMPT="""You are a financial document analyzer.

Analyze the attached PDF.

Step 1: Determine whether the document is a bank statement.
Step 2: If it IS a bank statement, extract details and transactions.
Step 3: Using ONLY the extracted transactions, perform financial analysis.
Step 4: If it is NOT a bank statement, return empty fields.

IMPORTANT OUTPUT RULES:
- The overall response MUST be valid JSON.
- All fields EXCEPT the "analysis" field must strictly follow the schema.
- The "analysis" field must be a HUMAN-READABLE TEXT SUMMARY, not JSON.
- Do NOT include explanations or extra text outside the JSON.
- Do NOT guess values.
- If information is missing, use null.

Return JSON in EXACTLY this format:

{
  "is_bank_statement": true | false,
  "bank_name": string | null,
  "account_name": string | null,
  "CIF_ID": string | null,
  "IFSC": string | null,
  "statement_period": {
    "from": string | null,
    "to": string | null
  },
  "transactions": [
    {
      "date": string,
      "description": string,
      "debit": number | null,
      "credit": number | null,
      "balance": number | null
    }
  ],
  "analysis": string | null
}

ANALYSIS GUIDELINES:
- Write the analysis as a clear, professional, human-readable paragraph(s)
- Base the analysis ONLY on the extracted transactions
- Include:
  • Spending and income behavior
  • Major transaction patterns
  • Large or unusual movements
  • Overall financial insights
- Do NOT use JSON, bullet arrays, or key-value formatting inside "analysis"


SPECIAL CASE:
If the document is NOT a bank statement:
- is_bank_statement = false
- transactions = []
- analysis = null

Output JSON only.
"""


def generate_response(filepath: str) -> dict:
    # Read and encode PDF
  with open(filepath, "rb") as f:
    pdf_bytes = f.read()
    pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
  response = completion(
    model=MODEL,
    temperature=0,
    response_format={"type": "json_object"},
    messages=[
      {
        "role": "user",
        "content": [
          {"type": "text", "text": PROMPT},
          {
            "type": "file",
            "file": {
              "file_data": f"data:application/pdf;base64,{pdf_base64}"
            }
          }
        ],
      }
    ],
  )
  content = response.choices[0].message.content
  data = json.loads(content)
  MODEL_PRICING = {
    "gemini/gemini-2.5-flash": {
        "prompt_per_1k": 0.0003,     
        "completion_per_1k": 0.0025 
    },
    "gemini/gemini-2.5-flash-lite": {
        "prompt_per_1k": 0.0001,    
        "completion_per_1k": 0.0004 
    }
  }

  pricing = MODEL_PRICING[MODEL]

  prompt_tokens = response.usage.prompt_tokens
  completion_tokens = response.usage.completion_tokens

  input_cost = (prompt_tokens / 1000) * pricing["prompt_per_1k"]
  output_cost = (completion_tokens / 1000) * pricing["completion_per_1k"]
  total_cost = input_cost + output_cost


  data["costing"] = {
    "usage": {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": response.usage.total_tokens
    },
    "cost": {
        "currency": "USD",
        "input_cost": round(input_cost, 6),
        "output_cost": round(output_cost, 6),
        "total_cost": round(total_cost, 6)
    },
    "model": MODEL
  }


  return data



if __name__ == "__main__":
  file_to_analyze = "uploads/my.pdf"
  if os.path.exists(file_to_analyze):
    result = generate_response(file_to_analyze)
    print(json.dumps(result, indent=2, ensure_ascii=False))
  else:
    print(f"File not found: {file_to_analyze}")
