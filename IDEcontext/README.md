# OpenClaw

**Self-hosted AI agent — personal digital assistant with messaging UI and MCP server.**

OpenClaw lives on your own hardware, communicates through the messaging apps you already use (Telegram, Slack, WhatsApp), and integrates with your IDE (VS Code / Cursor) via the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/).

---

## Quick Start

### 1. Install

```bash
# Clone and install in editable mode
cd /path/to/openclaw
pip install -e ".[dev]"
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env — at minimum set your LLM API key:
#   OPENCLAW_OPENAI_API_KEY=sk-...
```

### 3. Initialise a workspace

```bash
openclaw init .
# Creates: .openclaw/, AGENTS.md, HEARTBEAT.md, PROGRESS.md
```

### 4. Run

```bash
# Option A: Full server (REST API + Telegram/Slack/WhatsApp + Heartbeat)
openclaw serve

# Option B: MCP server only (for IDE integration)
openclaw mcp

# Option C: Interactive CLI chat
openclaw chat
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      OpenClaw Agent                      │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌────────┐ │
│  │ LLM      │  │ Tools    │  │ Skills    │  │ Memory │ │
│  │ (OpenAI/ │  │ exec     │  │ github.md │  │ (JSON  │ │
│  │  Ollama) │  │ read     │  │ files.md  │  │  files)│ │
│  │          │  │ write    │  │ custom.md │  │        │ │
│  └────┬─────┘  │ search   │  └───────────┘  └────────┘ │
│       │        │ list_dir │                              │
│       │        └──────────┘                              │
├───────┴──────────────────────────────────────────────────┤
│                    Adapters / Interfaces                  │
│  ┌──────────┐ ┌───────┐ ┌──────────┐ ┌────┐ ┌────────┐ │
│  │ Telegram │ │ Slack │ │ WhatsApp │ │REST│ │  MCP   │ │
│  │  Bot     │ │ Bolt  │ │ Webhook  │ │API │ │ Server │ │
│  └──────────┘ └───────┘ └──────────┘ └────┘ └────────┘ │
├──────────────────────────────────────────────────────────┤
│                    Background Services                   │
│  ┌───────────┐  ┌─────────────────┐                     │
│  │ Heartbeat │  │ Workspace Sync  │                     │
│  │ (cron)    │  │ (→ .cursorrules)│                     │
│  └───────────┘  └─────────────────┘                     │
└──────────────────────────────────────────────────────────┘
```

---

## IDE Integration (MCP Server)

### VS Code

1. The file `.vscode/mcp.json` is already included:
   ```json
   {
     "mcpServers": {
       "openclaw": {
         "command": "openclaw",
         "args": ["mcp"]
       }
     }
   }
   ```
2. Install the project (`pip install -e .`) so the `openclaw` command is on your PATH.
3. VS Code / GitHub Copilot will automatically discover and use the MCP tools.

### Cursor

1. The file `.cursor/mcp.json` is already included (same format).
2. Cursor will detect OpenClaw and make its tools available.
3. Run `openclaw workspace sync --editors cursor` to push context into `.cursorrules`.

### MCP Tools Exposed

| Tool | Description |
|------|-------------|
| `exec` | Execute shell commands |
| `read_file` | Read file contents |
| `write_file` | Write/create files |
| `append_file` | Append to files |
| `list_dir` | List directory contents |
| `web_search` | Search the web (DuckDuckGo) |
| `ask_agent` | Full agent conversation (LLM + tools) |

### MCP Resources Exposed

- `AGENTS.md`, `SOUL.md`, `IDENTITY.md` — project identity files
- `HEARTBEAT.md` — pending/completed heartbeat tasks
- `PROGRESS.md` — progress log
- All loaded skills (accessible via `openclaw://skill/<name>`)

---

## Workspace Sync

Sync the agent's "brain" into IDE-native rule files:

```bash
# Sync to Cursor
openclaw workspace sync --editors cursor

# Sync to VS Code
openclaw workspace sync --editors vscode

# Both
openclaw workspace sync --editors cursor,vscode
```

This writes context from `AGENTS.md`, skills, and progress into:
- `.cursorrules` and `.cursor/rules/openclaw.mdc` (Cursor)
- `.vscode/openclaw-context.md` (VS Code)

---

## Messaging Adapters

### Telegram
1. Create a bot via [@BotFather](https://t.me/botfather).
2. Set `TELEGRAM_BOT_TOKEN` in `.env`.
3. Optionally restrict to specific users: `TELEGRAM_ALLOWED_USERS=123456,789012`.
4. Run `openclaw serve`.

### Slack
1. Create a Slack app with Socket Mode enabled.
2. Set `SLACK_BOT_TOKEN`, `SLACK_SIGNING_SECRET`, `SLACK_APP_TOKEN` in `.env`.
3. Run `openclaw serve`.

### WhatsApp
1. Set up a Meta Cloud API app.
2. Set `WHATSAPP_API_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_VERIFY_TOKEN` in `.env`.
3. Run `openclaw serve` and point the Meta webhook to `https://your-host:3100/webhook/whatsapp`.

### REST API
Always available at `POST /chat`:
```bash
curl -X POST http://localhost:3100/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "list my project files"}'
```

---

## Heartbeat

The agent checks `HEARTBEAT.md` every N minutes for pending tasks:

```markdown
# Heartbeat Tasks

- [ ] check if the CI pipeline passed
- [ ] summarize today's git commits
```

Tasks marked `- [ ]` are executed and marked `- [x]` with results. Configure the interval via `HEARTBEAT_INTERVAL_MINUTES` in `.env`.

---

## Skills

Skills are markdown "textbook" files with YAML front-matter:

```markdown
---
name: my_skill
description: "What this skill does"
required_tools:
  - exec
  - read_file
examples:
  - "do the thing"
---

# My Skill

Instructions for the agent on how to use the tools for this task…
```

Place custom skills in `.openclaw/skills/`. Bundled skills ship in `src/openclaw/skills_bundled/`.

---

## Project Structure

```
src/openclaw/
├── __init__.py
├── cli.py              # Click CLI entry-point
├── config.py           # Pydantic settings from .env
├── logger.py           # Rich + file logging
├── models.py           # Core data models
├── llm.py              # OpenAI-compatible LLM client
├── memory.py           # File-backed conversation store
├── agent.py            # Main agentic loop (LLM ↔ Tools)
├── mcp_server.py       # MCP server (stdio) for IDE integration
├── server.py           # FastAPI server wiring adapters + heartbeat
├── heartbeat.py        # Periodic task runner
├── workspace.py        # Sync brain → IDE rule files
├── skills.py           # Skill loader
├── skills_bundled/     # Built-in skills
│   ├── github.md
│   └── file_management.md
├── tools/
│   ├── __init__.py
│   ├── registry.py     # Tool registry + decorator
│   └── builtins.py     # Built-in tools (exec, read, write…)
└── adapters/
    ├── __init__.py
    ├── telegram_adapter.py
    ├── slack_adapter.py
    ├── whatsapp_adapter.py
    └── webhook.py      # REST API + health endpoint
```

---

## License

MIT
