from fastapi import FastAPI, HTTPException, Request
import hmac
import hashlib
import os
from dotenv import load_dotenv
load_dotenv()  

GITHUB_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET", "thisIsMyGithubSecret")     

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}


def verify_signature(secret: str, body: bytes, signature_header: str):
    if not signature_header:
        raise HTTPException(status_code=400, detail="Missing signature header")
    print("🔐 Verifying signature...")
    print("Received signature:", signature_header)
    sha_name, signature = signature_header.split("=")
    if sha_name != "sha256":
        raise HTTPException(status_code=400, detail="Unsupported signature type")
    mac = hmac.new(secret.encode(), body, hashlib.sha256)
    if not hmac.compare_digest(mac.hexdigest(), signature):
        raise HTTPException(status_code=403, detail="Invalid signature")


@app.post("/webhook")
async def webhook_handler(request: Request):
    """
    Handle incoming webhook requests.
    This endpoint processes JSON payloads sent by GitHub when certain events occur (e.g., push).
    It extracts relevant information such as repository name, branch, pusher, and commit details,
    and prints them to the console for demonstration purposes.

    so whenever someone do the push event in that repo it will trigger the webhook , here i have setuped with ngrok.
    """
    body = await request.body()
    print("request header is ", request.headers)
    verify_signature(GITHUB_SECRET, body, request.headers.get("X-Hub-Signature-256"))
    payload = await request.json()
    repo = payload.get("repository", {}).get("full_name")
    branch = payload.get("ref", "").split("/")[-1]
    pusher = payload.get("pusher", {}).get("name")

    head_commit = payload.get("head_commit", {})

    data = {
        "repo": repo,
        "branch": branch,
        "pusher": pusher,
        "commit_id": head_commit.get("id"),
        "message": head_commit.get("message"),
        "added": head_commit.get("added", []),
        "modified": head_commit.get("modified", []),
        "removed": head_commit.get("removed", [])
    }

    print("🔔 Webhook received!")
    print(data)

    # Print important info
    print("📦 Repo:", data["repo"])
    print("🌿 Branch:", data["branch"])
    print("👤 Pusher:", data["pusher"])
    print("💬 Message:", data["message"])
    print("📁 Changes:", data["added"], data["modified"], data["removed"])

    return {"status": "ok", "data": data}
