from services.gen_ai_llm import generate_response
from services.send_mail import send_email


def analyze_bank_statement(file_path: str) -> dict:
    return generate_response(file_path)


def send_analysis_email(content: str, to_email: str) -> str:
    send_email(content, to_email)
    return "Email sent successfully"

tools = [
    {
        "type": "function",
        "function": {
            "name": "analyze_bank_statement",
            "description": "Analyze a PDF bank statement and return structured financial analysis",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Local path of the uploaded PDF file"
                    }
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_analysis_email",
            "description": "Send analysis result to an email address",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {"type": "string"},
                    "to_email": {"type": "string"}
                },
                "required": ["content", "to_email"]
            }
        }
    }
]


SYSTEM_PROMPT=  """You are an intelligent tool-routing assistant.
        Rules:
        - Only use the provided tools.
        - first analyse user prompt if user not asked to analyse bank statement or not given any email then dont do anything and respond: "Invalid prompt or no email provided"
        - If the user asks to analyze a bank statement, call analyze_bank_statement.
        - If the analysis confirms it is a bank statement AND user asked to send email, call send_analysis_email.
        - If the document is not a bank statement, respond: "Not a bank statement."
        - If no tool supports the request, respond: "No supported tool found."
        - Do NOT guess.
"""


ALL_TOOLS = {
    "analyze_bank_statement": analyze_bank_statement,
    "send_analysis_email": send_analysis_email
}
