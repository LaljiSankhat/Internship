from openai import OpenAI
import os
from dotenv import load_dotenv
import json
import re

load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def generate_response(filepath: str) -> dict:
    file = client.files.create(
        file=open(filepath, "rb"),
        purpose="assistants"
    )

    # response = client.responses.create(
    #     model="gpt-4o-mini",
    #     input=[
    #         {
    #             "role": "system",
    #             "content": [
    #                 {
    #                     "type": "input_text",
    #                     "text": (
    #                         "You are a financial document analyzer.\n"
    #                         "You must return STRICT JSON only.\n"
    #                         "Do not include explanations or extra text.\n"
    #                         "If information is missing, use null."
    #                     )
    #                 }
    #             ]
    #         },
    #         {
    #             "role": "user",
    #             "content": [
    #                 {
    #                     "type": "input_text",
    #                     "text": (
    #                         "Analyze the attached PDF.\n\n"
    #                         "Step 1: Determine whether the document is a bank statement.\n"
    #                         "Step 2: If it IS a bank statement, extract details.\n"
    #                         "Step 3: If it is NOT a bank statement, return empty fields.\n\n"
    #                         "Return JSON in EXACTLY this format:\n\n"
    #                         "{\n"
    #                         "  \"is_bank_statement\": true | false,\n"
    #                         "  \"bank_name\": string | null,\n"
    #                         "  \"account_name\": string | null,\n"
    #                         "  \"CIF_ID\": string | null,\n"
    #                         "  \"IFSC\": string | null,\n"
    #                         "  \"statement_period\": {\n"
    #                         "    \"from\": string | null,\n"
    #                         "    \"to\": string | null\n"
    #                         "  },\n"
    #                         "  \"transactions\": [\n"
    #                         "    {\n"
    #                         "      \"date\": string,\n"
    #                         "      \"description\": string,\n"
    #                         "      \"debit\": number | null,\n"
    #                         "      \"credit\": number | null,\n"
    #                         "      \"balance\": number | null\n"
    #                         "    }\n"
    #                         "  ]\n"
    #                         "}\n\n"
    #                         "Rules:\n"
    #                         "- If not a bank statement, set is_bank_statement=false and all other fields to null or empty arrays.\n"
    #                         "- Do NOT guess values.\n"
    #                         "- Use numbers for amounts, not strings.\n"
    #                         "- Output JSON only."
    #                     )
    #                 },
    #                 {
    #                     "type": "input_file",
    #                     "file_id": file.id
    #                 }
    #             ]
    #         }
    #     ],
    #     temperature=0
    # )
    response = client.responses.create(
        model="gpt-5",
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "You are a financial document analyzer. "
                            "First extract factual data exactly as present. "
                            "Then analyze spending patterns using only the extracted data. "
                            "If information is missing, use null. Do not guess."
                        )
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Analyze the attached PDF bank statement.\n"
                            "Return extracted data and financial insights."
                        )
                    },
                    {
                        "type": "input_file",
                        "file_id": file.id
                    }
                ]
            }
        ],
        text={
            "format": {
                "type": "json_schema",
                "strict": True,
                "name": "bank_statement_full_analysis",
                "schema": {
                    "type": "object",
                    "properties": {
                        "extracted_data": {
                            "type": "object",
                            "properties": {
                                "is_bank_statement": { "type": "boolean" },
                                "bank_name": { "type": ["string", "null"] },
                                "account_name": { "type": ["string", "null"] },
                                "CIF_ID": { "type": ["string", "null"] },
                                "IFSC": { "type": ["string", "null"] },
                                "statement_period": {
                                    "type": "object",
                                    "properties": {
                                        "from": { "type": ["string", "null"] },
                                        "to": { "type": ["string", "null"] }
                                    },
                                    "required": ["from", "to"],
                                    "additionalProperties": False
                                },
                                "transactions": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "date": { "type": "string" },
                                            "description": { "type": "string" },
                                            "debit": { "type": ["number", "null"] },
                                            "credit": { "type": ["number", "null"] },
                                            "balance": { "type": ["number", "null"] }
                                        },
                                        "required": [
                                            "date",
                                            "description",
                                            "debit",
                                            "credit",
                                            "balance"
                                        ],
                                        "additionalProperties": False
                                    }
                                }
                            },
                            "required": [
                                "is_bank_statement",
                                "bank_name",
                                "account_name",
                                "CIF_ID",
                                "IFSC",
                                "statement_period",
                                "transactions"
                            ],
                            "additionalProperties": False
                        },
                        "analysis": {
                            "type": "object",
                            "properties": {
                                "spending_summary": {
                                    "type": "string"
                                },
                                "expense_categories": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "category": { "type": "string" },
                                            "total_amount": { "type": "number" },
                                            "transaction_count": { "type": "integer" }
                                        },
                                        "required": [
                                            "category",
                                            "total_amount",
                                            "transaction_count"
                                        ],
                                        "additionalProperties": False
                                    }
                                },
                                "large_transactions": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "date": { "type": "string" },
                                            "description": { "type": "string" },
                                            "amount": { "type": "number" },
                                            "type": {
                                                "type": "string",
                                                "enum": ["debit", "credit"]
                                            }
                                        },
                                        "required": [
                                            "date",
                                            "description",
                                            "amount",
                                            "type"
                                        ],
                                        "additionalProperties": False
                                    }
                                },
                                "unusual_transactions": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "date": { "type": "string" },
                                            "description": { "type": "string" },
                                            "reason": { "type": "string" }
                                        },
                                        "required": [
                                            "date",
                                            "description",
                                            "reason"
                                        ],
                                        "additionalProperties": False
                                    }
                                },
                                "recommendations": {
                                    "type": "array",
                                    "items": { "type": "string" }
                                }
                            },
                            "required": [
                                "spending_summary",
                                "expense_categories",
                                "large_transactions",
                                "unusual_transactions",
                                "recommendations"
                            ],
                            "additionalProperties": False
                        }
                    },
                    "required": ["extracted_data", "analysis"],
                    "additionalProperties": False
                }
            }
        }
    )

    # print(type(response.output_text))
    print(response)
    # raw = None

    # for item in response.output:
    #     for content in item.content:
    #         if content.type == "output_text":
    #             raw = content.text


    # if raw is None:
    #     raise ValueError("No output_text found in response")

    # # Remove ```json and ```
    # clean = re.sub(r"```json|```", "", raw).strip()

    # data = json.loads(clean)

    # print(json.dumps(data, indent=2))
    # return data

generate_response("uploads/my.pdf")


















# response = client.responses.create(
#     model="gpt-4o-mini",
#     input=[
#         {
#             "role": "user",
#             "content": [
#                 {"type": "input_text", "text": "Tell me if this PDF is a bank statement ? give me json output in such way that it contains is_bankstatement and all extracted bank statement in proper json format"},
#                 {
#                     "type": "input_file",
#                     "file_id": file.id
#                 }
#             ]
#         }
#     ]
# )


# print(response.output_text)

# file = client.files.create(
#     file=open("uploads/my.pdf", "rb"),
#     purpose="assistants"
# )



# response = client.responses.create(
#     model="gpt-4o-mini",
#     input=[
#         {
#             "role": "system",
#             "content": [
#                 {
#                     "type": "input_text",
#                     "text": (
#                         "You are a financial document analyzer.\n"
#                         "You must return STRICT JSON only.\n"
#                         "Do not include explanations or extra text.\n"
#                         "If information is missing, use null."
#                     )
#                 }
#             ]
#         },
#         {
#             "role": "user",
#             "content": [
#                 {
#                     "type": "input_text",
#                     "text": (
#                         "Analyze the attached PDF.\n\n"
#                         "Step 1: Determine whether the document is a bank statement.\n"
#                         "Step 2: If it IS a bank statement, extract details.\n"
#                         "Step 3: If it is NOT a bank statement, return empty fields.\n\n"
#                         "Return JSON in EXACTLY this format:\n\n"
#                         "{\n"
#                         "  \"is_bank_statement\": true | false,\n"
#                         "  \"bank_name\": string | null,\n"
#                         "  \"account_name\": string | null,\n"
#                         "  \"CIF_ID\": string | null,\n"
#                         "  \"IFSC\": string | null,\n"
#                         "  \"statement_period\": {\n"
#                         "    \"from\": string | null,\n"
#                         "    \"to\": string | null\n"
#                         "  },\n"
#                         "  \"transactions\": [\n"
#                         "    {\n"
#                         "      \"date\": string,\n"
#                         "      \"description\": string,\n"
#                         "      \"debit\": number | null,\n"
#                         "      \"credit\": number | null,\n"
#                         "      \"balance\": number | null\n"
#                         "    }\n"
#                         "  ]\n"
#                         "}\n\n"
#                         "Rules:\n"
#                         "- If not a bank statement, set is_bank_statement=false and all other fields to null or empty arrays.\n"
#                         "- Do NOT guess values.\n"
#                         "- Use numbers for amounts, not strings.\n"
#                         "- Output JSON only."
#                     )
#                 },
#                 {
#                     "type": "input_file",
#                     "file_id": file.id
#                 }
#             ]
#         }
#     ],
#     temperature=0
# )


# print(type(response.output_text))
# raw = None

# for item in response.output:
#     for content in item.content:
#         if content.type == "output_text":
#             raw = content.text


# if raw is None:
#     raise ValueError("No output_text found in response")

# # Remove ```json and ```
# clean = re.sub(r"```json|```", "", raw).strip()

# data = json.loads(clean)

# print(json.dumps(data, indent=2))