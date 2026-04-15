from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class UserInput(BaseModel):
    question: str
    behavior: Optional[str] = None

@app.get("/")
def root():
    return {"message": "Hello from root"}



@app.post("/ask")
def reply(user_input: UserInput):
    question = user_input.question
    behavior = user_input.behavior or "neutral"

    

    return {
        "question_received": question,
        "behavior_used": behavior,
        "answer": f"I received your question: '{question}' with behavior '{behavior}'."
    }