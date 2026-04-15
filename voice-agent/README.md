# PersonaPlex Voice Agent

A real-time voice calling agent using NVIDIA's PersonaPlex-7b-v1 model for full-duplex speech-to-speech conversations.

## Features

- 🎙️ Real-time voice conversations
- 🧠 Powered by NVIDIA PersonaPlex-7b-v1
- 💬 Full-duplex communication (interruptions, overlaps)
- 🌐 Web-based client interface
- 📱 Phone call support (via Twilio - optional)

## Prerequisites

1. **Accept Model License**: Visit [PersonaPlex on HuggingFace](https://huggingface.co/nvidia/personaplex-7b-v1) and accept the NVIDIA Open Model License Agreement.

2. **Install Opus Codec**:
   ```bash
   # Ubuntu/Debian
   sudo apt install libopus-dev
   
   # Fedora/RHEL
   sudo dnf install opus-devel
   
   # macOS
   brew install opus
   ```

3. **GPU Requirements** (recommended):
   - NVIDIA GPU with CUDA support
   - At least 16GB VRAM (or use CPU offload)

## Installation

1. Navigate to the project directory:
   ```bash
   cd /home/web-h-013/Learning/voice-agent
   ```

2. Run the setup script (recommended):
   ```bash
   ./setup.sh
   ```
   
   Or install manually:
   ```bash
   # Install PersonaPlex first (it sets torch version)
   git clone https://github.com/NVIDIA/personaplex.git
   cd personaplex
   pip install moshi/.
   cd ..
   
   # Then install compatible dependencies
   pip install -r requirements.txt
   ```

3. If you encounter dependency conflicts, run:
   ```bash
   ./fix_dependencies.sh
   ```

4. Install PersonaPlex package (if not done in step 2):
   ```bash
   # Clone PersonaPlex repository
   git clone https://github.com/NVIDIA/personaplex.git
   cd personaplex
   pip install moshi/.
   cd ..
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and add your HF_TOKEN
   ```

## Usage

### Start the Server

```bash
# Basic usage
python -m server.voice_call_handler

# With CPU offload (if GPU memory insufficient)
CPU_OFFLOAD=true python -m server.voice_call_handler

# With custom port
PORT=8080 python -m server.voice_call_handler
```

The server will start on `http://localhost:8998` (or the port specified in `.env`).

### Web Client

1. Open your browser and navigate to `http://localhost:8998/client`
2. Click "Start Call" to begin a voice conversation
3. Speak into your microphone
4. The agent will respond in real-time

### API Endpoints

- `GET /` - Homepage
- `GET /health` - Health check
- `GET /client` - Web client interface
- `WebSocket /ws/voice` - Voice call WebSocket endpoint

## Configuration

### Persona Customization

Edit the `PERSONA_PROMPT` in `.env` to customize the agent's personality:

```env
PERSONA_PROMPT=You work for CitySan Services which is a waste management company and your name is Ayelen Lucero. You are helpful and professional.
```

### Voice Selection

PersonaPlex supports various voice prompts. You can specify voice characteristics in the code or use pre-packaged voices (NATF0-NATF3, NATM0-NATM3, etc.).

## Phone Call Integration (Twilio)

To enable phone call support:

1. Sign up for [Twilio](https://www.twilio.com/)
2. Get your Account SID, Auth Token, and Phone Number
3. Add to `.env`:
   ```env
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_PHONE_NUMBER=+1234567890
   ```

## Troubleshooting

### Model Loading Issues

- Ensure you've accepted the license on HuggingFace
- Check that `HF_TOKEN` is set correctly
- Try using `CPU_OFFLOAD=true` if GPU memory is insufficient

### Audio Issues

- Check microphone permissions in your browser
- Ensure Opus codec is installed
- Verify audio sample rate is 24kHz

### Connection Issues

- Check firewall settings
- Verify WebSocket support in your network
- Check server logs for errors

## License

This code is provided under MIT license. The PersonaPlex model weights are governed by the NVIDIA Open Model License Agreement.

## References

- [PersonaPlex GitHub](https://github.com/NVIDIA/personaplex)
- [PersonaPlex Paper](https://arxiv.org/abs/2602.06053)
- [HuggingFace Model](https://huggingface.co/nvidia/personaplex-7b-v1)
