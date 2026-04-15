#!/usr/bin/env python3
"""
Convenience script to run the voice agent server
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    import uvicorn
    from server.voice_call_handler import app
    
    port = int(os.getenv("PORT", 8998))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"Starting PersonaPlex Voice Agent Server on {host}:{port}")
    print(f"Web client available at: http://{host}:{port}/client")
    
    uvicorn.run(app, host=host, port=port)
