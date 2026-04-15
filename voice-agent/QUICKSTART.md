# Quick Start Guide

## Prerequisites Checklist

- [ ] Python 3.8+ installed
- [ ] NVIDIA GPU with CUDA (recommended) or CPU
- [ ] Opus codec installed (`sudo apt install libopus-dev` or `brew install opus`)
- [ ] HuggingFace account with access to PersonaPlex model

## Step-by-Step Setup

### 1. Accept Model License

Visit https://huggingface.co/nvidia/personaplex-7b-v1 and accept the NVIDIA Open Model License Agreement.

### 2. Get Your HuggingFace Token

1. Go to https://huggingface.co/settings/tokens
2. Create a new token with "read" permissions
3. Copy the token

### 3. Run Setup Script

```bash
cd /home/web-h-013/Learning/voice-agent
./setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Clone PersonaPlex repository
- Create .env file

### 4. Configure Environment

Edit `.env` file and add your token:

```bash
nano .env
# or
vim .env
```

Set:
```
HF_TOKEN=your_token_here
```

### 5. Start the Server

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Start server
python run_server.py
```

### 6. Open Web Client

Open your browser and go to:
```
http://localhost:8998/client
```

Click "Start Call" and begin speaking!

## Troubleshooting

### "HF_TOKEN not set" error
- Make sure you've created `.env` file
- Check that `HF_TOKEN=your_token` is set correctly
- Restart the server after editing `.env`

### "Model loading failed"
- Verify you've accepted the license on HuggingFace
- Check your internet connection (model needs to be downloaded)
- Try `CPU_OFFLOAD=true` in `.env` if GPU memory is insufficient

### "Microphone not working"
- Check browser permissions for microphone access
- Try a different browser (Chrome/Firefox recommended)
- Check system microphone settings

### "WebSocket connection failed"
- Make sure the server is running
- Check firewall settings
- Verify you're using the correct URL (http://localhost:8998/client)

## Next Steps

- Customize the persona in `.env` (`PERSONA_PROMPT`)
- Integrate with Twilio for phone calls
- Deploy to a server for remote access
- Add authentication/authorization
