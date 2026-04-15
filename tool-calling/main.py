from fastapi import FastAPI, UploadFile, File, Form, responses, HTTPException
import shutil
import json
import litellm
import uuid
import os
from services.analyse_pdf_tool import *
from services.bd import solve_bodmas
# from services.bdseventool import solve_question
# from services.bdnew import solve_question
from services.bdoptimised import solve_question

app = FastAPI()

@app.post("/agent")
async def agent_route(
    prompt: str = Form(...),
    file: UploadFile = File(...)
):
    # Save uploaded file
    file_id = f"uploads/{uuid.uuid4()}_{file.filename}"
    with open(file_id, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    response = litellm.completion(
        model="groq/llama-3.1-8b-instant",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    assistant_message = response.choices[0].message
    messages.append(assistant_message.model_dump())

    print(assistant_message)

    to_email = None

    if assistant_message.tool_calls:
        tool_outputs = {}

        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

        
            if tool_name == "analyze_bank_statement":
                args["file_path"] = file_id
            
            if tool_call.function.name == "send_analysis_email":
                args = json.loads(tool_call.function.arguments)
                to_email = args.get("to_email")
                continue

            result = ALL_TOOLS[tool_name](**args)
            tool_outputs[tool_name] = result

        
        analysis = tool_outputs.get("analyze_bank_statement")

        if analysis and not analysis["is_bank_statement"]:
            return {"result": "Not a bank statement"}

        if analysis and analysis["is_bank_statement"]:
            send_analysis_email(
                content=json.dumps(analysis, indent=2),
                to_email=to_email
            )
            return {"result": "Bank statement analyzed and emailed"}

    return {
        "result": "No supported tool found or another issue",
        "message": assistant_message
    }


@app.post("/calculation")
def calculation(question: str):
    try:
        result = solve_question(question)
        return {"result": result}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mathematical expression: {str(e)}"
        )