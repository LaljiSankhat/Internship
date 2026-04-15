import base64
import json
import os
from dotenv import load_dotenv
from litellm import completion


load_dotenv()
print(os.getenv("GEMINI_API_KEY"))

MODEL = "gemini/gemini-2.5-flash"

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
  return json.loads(content)



# if __name__ == "__main__":
#   file_to_analyze = "uploads/my.pdf"
#   if os.path.exists(file_to_analyze):
#     result = generate_response(file_to_analyze)
#     print(json.dumps(result, indent=2, ensure_ascii=False))
#   else:
#     print(f"File not found: {file_to_analyze}")















# from google import genai
# from google.genai import types
# import json
# import os
# from dotenv import load_dotenv

# load_dotenv()

# client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# for model in client.models.list():
#     print(model.name)


# def generate_response(filepath: str) -> dict:
#     # Read PDF
#     with open(filepath, "rb") as f:
#         pdf_bytes = f.read()

#     # prompt = """
#     #     You are a financial document analyzer.
#     #     You must return STRICT JSON only.
#     #     Do not include explanations or extra text.
#     #     If information is missing, use null.

#     #     Analyze the attached PDF.

#     #     Step 1: Determine whether the document is a bank statement.
#     #     Step 2: If it IS a bank statement, extract details.
#     #     Step 3: If it is NOT a bank statement, return empty fields.

#     #     Return JSON in EXACTLY this format:

#     #     {
#     #     "is_bank_statement": true | false,
#     #     "bank_name": string | null,
#     #     "account_name": string | null,
#     #     "CIF_ID": string | null,
#     #     "IFSC": string | null,
#     #     "statement_period": {
#     #         "from": string | null,
#     #         "to": string | null
#     #     },
#     #     "transactions": [
#     #         {
#     #         "date": string,
#     #         "description": string,
#     #         "debit": number | null,
#     #         "credit": number | null,
#     #         "balance": number | null
#     #         }
#     #     ]
#     #     }

#     #     Rules:
#     #     - If not a bank statement, set is_bank_statement=false and all other fields to null or empty arrays.
#     #     - Do NOT guess values.
#     #     - Use numbers for amounts, not strings.
#     #     - Output JSON only.
#     #     """

#     prompt = """
# You are a financial document analyzer.
# You must return STRICT JSON only.
# Do not include explanations or extra text.
# If information is missing, use null.

# Analyze the attached PDF.

# Step 1: Determine whether the document is a bank statement.
# Step 2: If it IS a bank statement, extract details and transactions.
# Step 3: Using ONLY the extracted transactions, perform financial analysis.
# Step 4: If it is NOT a bank statement, return empty fields.

# Return JSON in EXACTLY this format:

# {
#   "is_bank_statement": true | false,
#   "bank_name": string | null,
#   "account_name": string | null,
#   "CIF_ID": string | null,
#   "IFSC": string | null,
#   "statement_period": {
#     "from": string | null,
#     "to": string | null
#   },
#   "transactions": [
#     {
#       "date": string,
#       "description": string,
#       "debit": number | null,
#       "credit": number | null,
#       "balance": number | null
#     }
#   ],
#   "analysis": {
#     "spending_summary": string | null,
#     "expense_categories": [
#       {
#         "category": string,
#         "total_amount": number,
#         "transaction_count": number
#       }
#     ],
#     "large_transactions": [
#       {
#         "date": string,
#         "description": string,
#         "amount": number,
#         "type": "debit" | "credit"
#       }
#     ],
#     "unusual_transactions": [
#       {
#         "date": string,
#         "description": string,
#         "reason": string
#       }
#     ],
#     "insights": [
#       string
#     ]
#   }
# }

# Analysis Rules:
# - Perform analysis ONLY if is_bank_statement = true
# - Use ONLY the extracted transactions
# - Do NOT infer merchant intent beyond description text
# - Expense categories must be derived from transaction descriptions
# - Large transactions are significantly higher than typical transaction amounts
# - Unusual transactions include anomalies such as:
#   - unusually large amounts
#   - irregular timing
#   - unknown or suspicious descriptions
# - Insights must be brief, actionable, and factual

# Rules:
# - If not a bank statement:
#   - set is_bank_statement=false
#   - transactions = []
#   - analysis = null
# - Do NOT guess values
# - Use numbers for amounts, not strings
# - Output JSON only
# """


#     response = client.models.generate_content(
#         model="models/gemini-2.0-flash-lite",
#         contents=[
#             types.Content(
#                 role="user",
#                 parts=[
#                     types.Part.from_text(text=prompt),
#                     types.Part.from_bytes(
#                         data=pdf_bytes,
#                         mime_type="application/pdf"
#                     ),
#                 ],
#             )
#         ],
#         config=types.GenerateContentConfig(
#             temperature=0,
#             response_mime_type="application/json"
#         )
#     )

#     # Gemini already returns clean JSON text
#     return json.loads(response.text)


# result = generate_response("uploads/my.pdf")

# print(json.dumps(result, indent=2, ensure_ascii=False))









































# from google import genai
# from google.genai import types
# from dotenv import load_dotenv
# import os
# import json

# load_dotenv()

# client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# def generate_response(filepath: str) -> dict:
#     # 1. Upload PDF
#     uploaded_file = client.files.upload(
#         file=filepath,
#         config=types.UploadFileConfig(
#             mime_type="application/pdf"
#         )
#     )

#     # 2. JSON Schema (Gemini-compatible)
#     response_schema = {
#         "type": "object",
#         "properties": {
#             "extracted_data": {
#                 "type": "object",
#                 "properties": {
#                     "is_bank_statement": {"type": "boolean"},
#                     "bank_name": {"type": ["string", "null"]},
#                     "account_name": {"type": ["string", "null"]},
#                     "CIF_ID": {"type": ["string", "null"]},
#                     "IFSC": {"type": ["string", "null"]},
#                     "statement_period": {
#                         "type": "object",
#                         "properties": {
#                             "from": {"type": ["string", "null"]},
#                             "to": {"type": ["string", "null"]}
#                         },
#                         "required": ["from", "to"]
#                     },
#                     "transactions": {
#                         "type": "array",
#                         "items": {
#                             "type": "object",
#                             "properties": {
#                                 "date": {"type": "string"},
#                                 "description": {"type": "string"},
#                                 "debit": {"type": ["number", "null"]},
#                                 "credit": {"type": ["number", "null"]},
#                                 "balance": {"type": ["number", "null"]}
#                             },
#                             "required": [
#                                 "date",
#                                 "description",
#                                 "debit",
#                                 "credit",
#                                 "balance"
#                             ]
#                         }
#                     }
#                 },
#                 "required": [
#                     "is_bank_statement",
#                     "bank_name",
#                     "account_name",
#                     "CIF_ID",
#                     "IFSC",
#                     "statement_period",
#                     "transactions"
#                 ]
#             },
#             "analysis": {
#                 "type": "object",
#                 "properties": {
#                     "spending_summary": {"type": "string"},
#                     "expense_categories": {
#                         "type": "array",
#                         "items": {
#                             "type": "object",
#                             "properties": {
#                                 "category": {"type": "string"},
#                                 "total_amount": {"type": "number"},
#                                 "transaction_count": {"type": "integer"}
#                             },
#                             "required": [
#                                 "category",
#                                 "total_amount",
#                                 "transaction_count"
#                             ]
#                         }
#                     },
#                     "large_transactions": {
#                         "type": "array",
#                         "items": {
#                             "type": "object",
#                             "properties": {
#                                 "date": {"type": "string"},
#                                 "description": {"type": "string"},
#                                 "amount": {"type": "number"},
#                                 "type": {
#                                     "type": "string",
#                                     "enum": ["debit", "credit"]
#                                 }
#                             },
#                             "required": [
#                                 "date",
#                                 "description",
#                                 "amount",
#                                 "type"
#                             ]
#                         }
#                     },
#                     "unusual_transactions": {
#                         "type": "array",
#                         "items": {
#                             "type": "object",
#                             "properties": {
#                                 "date": {"type": "string"},
#                                 "description": {"type": "string"},
#                                 "reason": {"type": "string"}
#                             },
#                             "required": [
#                                 "date",
#                                 "description",
#                                 "reason"
#                             ]
#                         }
#                     },
#                     "recommendations": {
#                         "type": "array",
#                         "items": {"type": "string"}
#                     }
#                 },
#                 "required": [
#                     "spending_summary",
#                     "expense_categories",
#                     "large_transactions",
#                     "unusual_transactions",
#                     "recommendations"
#                 ]
#             }
#         },
#         "required": ["extracted_data", "analysis"]
#     }

#     # 3. Generate content
#     response = client.models.generate_content(
#         model="gemini-1.5-pro",
#         contents=[
#             types.Content(
#                 role="user",
#                 parts=[
#                     types.Part(
#                         text=(
#                             "Analyze the attached PDF bank statement.\n"
#                             "First extract factual data exactly as present.\n"
#                             "Then analyze spending patterns using only extracted data.\n"
#                             "If information is missing, use null. Do not guess."
#                         )
#                     ),
#                     types.Part(
#                         file_data=types.FileData(
#                             file_uri=uploaded_file.uri,
#                             mime_type="application/pdf"
#                         )
#                     )
#                 ]
#             )
#         ],
#         config=types.GenerateContentConfig(
#             temperature=0,
#             response_mime_type="application/json",
#             response_schema=response_schema
#         )
#     )

#     # 4. Gemini returns valid JSON
#     return json.loads(response.text)


# # Run
# data = generate_response("uploads/my.pdf")
# print(json.dumps(data, indent=2))
