"""
Voice Call Handler - WebSocket server for real-time voice calls
"""
import os
import asyncio
import logging
import json
from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
import numpy as np
import soundfile as sf
from .personaplex_server import PersonaPlexAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Global agent instance
agent: Optional[PersonaPlexAgent] = None


@app.on_event("startup")
async def startup_event():
    """Initialize the PersonaPlex agent on startup"""
    global agent
    try:
        agent = PersonaPlexAgent(
            hf_token=os.getenv("HF_TOKEN"),
            cpu_offload=os.getenv("CPU_OFFLOAD", "false").lower() == "true"
        )
        agent.load_model()
        agent.set_persona(
            text_prompt=os.getenv(
                "PERSONA_PROMPT",
                "You are a wise and friendly assistant. Answer questions or provide advice in a clear and engaging way."
            )
        )
        logger.info("PersonaPlex agent initialized")
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        raise


@app.websocket("/ws/voice")
async def websocket_voice_call(websocket: WebSocket):
    """WebSocket endpoint for voice calls"""
    await websocket.accept()
    logger.info("Voice call connected")
    
    try:
        while True:
            # Receive audio data
            data = await websocket.receive()
            
            if "bytes" in data:
                # Audio stream
                audio_bytes = data["bytes"]
                response_audio, response_text = await agent.process_audio_stream(audio_bytes)
                
                # Send response
                await websocket.send_bytes(response_audio)
                await websocket.send_json({"text": response_text, "type": "response"})
                
            elif "text" in data:
                # Text message (for testing)
                message = json.loads(data["text"])
                if message.get("type") == "text":
                    response_audio, response_text = await agent.process_text(message["content"])
                    await websocket.send_bytes(response_audio)
                    await websocket.send_json({"text": response_text, "type": "response"})
                elif message.get("type") == "reset":
                    agent.reset_conversation()
                    await websocket.send_json({"type": "reset", "status": "ok"})
                    
    except WebSocketDisconnect:
        logger.info("Voice call disconnected")
    except Exception as e:
        logger.error(f"Error in voice call: {e}")
        await websocket.close()


@app.get("/")
async def get_homepage():
    """Serve the homepage"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>PersonaPlex Voice Agent</title>
        <meta charset="UTF-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                text-align: center;
            }
            a {
                display: block;
                text-align: center;
                margin: 20px 0;
                padding: 15px;
                background: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 5px;
            }
            a:hover {
                background: #45a049;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎙️ PersonaPlex Voice Agent</h1>
            <p style="text-align: center;">Real-time voice conversations powered by NVIDIA PersonaPlex-7b-v1</p>
            <a href="/client">Open Voice Client</a>
            <a href="/health">Health Check</a>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/client")
async def get_client():
    """Serve the web client"""
    from pathlib import Path
    client_path = Path(__file__).parent.parent / "client" / "web_client.html"
    return FileResponse(str(client_path))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent_loaded": agent is not None and agent.model is not None
    }


if __name__ == "__main__":
    import uvicorn
    from dotenv import load_dotenv
    
    load_dotenv()
    
    port = int(os.getenv("PORT", 8998))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(app, host=host, port=port)
