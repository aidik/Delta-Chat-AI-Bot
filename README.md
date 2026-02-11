# AI Delta Bot

An AI-powered chatbot for [Delta Chat](https://delta.chat/) that forwards messages to an OpenAI-compatible API (e.g. [OpenRouter](https://openrouter.ai)) and replies with the AI-generated response.

## Features

- Works with any OpenAI-compatible chat completions API
- Sender whitelist -- only responds to authorized addresses
- Configurable system prompt, model, and token limits
- Input length protection (truncates overly long messages)
- Docker support

## Prerequisites

- Python 3.13+
- An API key for an OpenAI-compatible provider (e.g. OpenRouter)

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/aidik/Delta-Chat-AI-Bot.git
cd Delta-Chat-AI-Bot
```

### 2. Configure environment

Copy the example file and fill in your values:

```bash
cp .env.example .env
# edit .env with your API key and allowed senders
```

At minimum you must set:

| Variable | Required | Description |
|---|---|---|
| `AI_API_KEY` | **Yes** | API key for your AI provider |
| `RESPOND_TO` | **Yes** | Comma-separated list of Delta Chat addresses the bot is allowed to reply to |
| `AI_API_URL` | No | API base URL (default: `https://openrouter.ai`) |
| `AI_API_MODEL` | No | Model identifier (default: `google/gemini-2.5-pro`) |
| `AI_API_MAX_TOKENS` | No | Max tokens per AI response (default: `10000`) |
| `SYSTEM_PROMPT` | No | System prompt that defines the bot's personality |
| `MAX_MESSAGE_LENGTH` | No | Max input message length in characters (default: `1000`) |
| `APP_URL` | No | Your app URL, sent as `HTTP-Referer` header (default: `http://localhost`) |
| `APP_TITLE` | No | App title, sent as `X-Title` header (default: `Delta Chat AI Bot`) |

### 3. Initial bot setup

Before running the bot for the first time, install dependencies, create a Delta Chat account, and configure the bot's profile:

```bash
pip install requests dotenv deltabot-cli
python deltabot.py init "DCACCOUNT:https://nine.testrun.org/new"
python deltabot.py config displayname "Delta AI Bot"
python deltabot.py config selfstatus "Hi, I am Delta an AI Bot, ask me something."
python deltabot.py config selfavatar "./bot-avatar.png"
```

The `init` command creates a new Delta Chat account for the bot. The `config` commands set its display name, status text, and avatar that other Delta Chat users will see. You only need to do this once.

### 4a. Run locally

```bash
python deltabot.py serve
```

### 4b. Build and run with Docker

```bash
docker build -t delta-chat-ai-bot .
docker run --env-file .env delta-chat-ai-bot
```

### 4c. Run the pre-built Docker image

A pre-built image is available on [Docker Hub](https://hub.docker.com/r/aidik/delta-chat-ai-bot). No cloning or building required -- just pass your configuration as environment variables:

```bash
docker run \
  -v ./dcconfig:/dcconfig \
  -e AI_API_KEY="your-api-key-here" \
  -e RESPOND_TO="user1@example.com,user2@example.com" \
  -e AI_API_URL="https://openrouter.ai" \
  -e AI_API_MODEL="google/gemini-2.5-pro" \
  -e AI_API_MAX_TOKENS="10000" \
  -e SYSTEM_PROMPT="You are a helpful chatbot that answers the user's messages with short, direct replies. Keep your answers clear, factual, and concise." \
  -e MAX_MESSAGE_LENGTH="1000" \
  -e APP_URL="http://localhost" \
  -e APP_TITLE="Delta Chat AI Bot" \
  docker.io/aidik/delta-chat-ai-bot:latest
```

Mount a volume to `/dcconfig` to persist the bot's Delta Chat account information across container restarts. Without this, the bot will create a new account each time it starts.

At minimum only `AI_API_KEY` and `RESPOND_TO` are required; the rest will use their defaults if omitted.

### 5. Add the bot to Delta Chat

To add the bot as a contact, you need its invite link. Run:

```bash
python deltabot.py link
```

This prints a link that you can open in Delta Chat. The same link is also printed to the logs every time the bot starts, so when running via Docker you can retrieve it with:

```bash
docker logs <container-name>
```

## How It Works

1. The bot listens for incoming Delta Chat messages using [`deltabot-cli`](https://pypi.org/project/deltabot-cli/).
2. When a message arrives, the sender's address is checked against the `RESPOND_TO` whitelist.
3. If authorized, the message text is forwarded to the configured AI API endpoint (`/api/v1/chat/completions`).
4. The AI response is sent back to the same Delta Chat conversation.

Unauthorized senders receive a short rejection message.