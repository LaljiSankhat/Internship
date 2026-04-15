# PersonaPlex Integration Guide

## Two Approaches

This voice agent can work in two ways:

### Approach 1: Direct Model Loading (Current Implementation)
Uses transformers to load the model directly. This is simpler but may not have all the real-time features.

### Approach 2: PersonaPlex Server Integration (Recommended)
Uses the official PersonaPlex server which provides full-duplex real-time capabilities.

## Using the Official PersonaPlex Server

The PersonaPlex model comes with its own server implementation. Here's how to integrate:

### Step 1: Install PersonaPlex

```bash
git clone https://github.com/NVIDIA/personaplex.git
cd personaplex
pip install moshi/.
```

### Step 2: Start PersonaPlex Server

```bash
# Set your HuggingFace token
export HF_TOKEN=your_token_here

# Start server (with temporary SSL for HTTPS)
SSL_DIR=$(mktemp -d)
python -m moshi.server --ssl "$SSL_DIR"

# Or with CPU offload if GPU memory is insufficient
python -m moshi.server --ssl "$SSL_DIR" --cpu-offload
```

The server will start on port 8998 by default.

### Step 3: Connect Your Client

The PersonaPlex server provides a WebSocket API. You can modify `client/web_client.html` to connect to the PersonaPlex server instead of our custom server.

## PersonaPlex Server API

The PersonaPlex server uses a specific WebSocket protocol. Refer to the [PersonaPlex GitHub](https://github.com/NVIDIA/personaplex) for the exact API specification.

## Hybrid Approach

You can also run both:
1. PersonaPlex server for the actual model inference
2. Our FastAPI server as a proxy/gateway that adds additional features

This allows you to:
- Add authentication
- Add logging/monitoring
- Integrate with phone systems (Twilio)
- Add custom business logic
