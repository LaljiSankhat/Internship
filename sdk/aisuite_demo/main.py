from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="AI Suite Demo")



app.get("/")
async def root():
    """Root endpoint."""
    return JSONResponse(content={"message": "Welcome to the AI Suite Demo!"})

@app.get("/health")
async def healthcheck():
	"""Simple health-check endpoint."""
	return JSONResponse(content={"status": "ok"})

@app.get("/chat-openai")
async def chat_openai():
	"""OpenAI chat endpoint."""
	return JSONResponse(content={"message": "This is the OpenAI chat endpoint."})

@app.get("/chat-anthropic")
async def chat_anthropic():
	"""Anthropic chat endpoint."""
	return JSONResponse(content={"message": "This is the Anthropic chat endpoint."})

@app.get("/chat-gemini")
async def chat_gemini():
	"""Gemini chat endpoint."""
	return JSONResponse(content={"message": "This is the Gemini chat endpoint."})

@app.get("/chat-groq")
async def chat_groq():
	"""Groq chat endpoint."""
	return JSONResponse(content={"message": "This is the Groq chat endpoint."})