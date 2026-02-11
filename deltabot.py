import os, sys, requests, json, logging
from deltabot_cli import BotCli
from deltachat2 import MsgData, events
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

RESPOND_TO = os.getenv("RESPOND_TO", "") 
if not RESPOND_TO:
    logger.warning("RESPOND_TO is empty - bot will not respond to anyone")
    RESPOND_TO = []
else:    
    RESPOND_TO = RESPOND_TO.replace(" ", "")
    RESPOND_TO = RESPOND_TO.split(",")

AI_API_URL = os.getenv("AI_API_URL", "https://openrouter.ai")
AI_API_KEY = os.getenv("AI_API_KEY", "")
if not AI_API_KEY:
    raise ValueError("AI_API_KEY environment variable is required")

AI_API_MODEL = os.getenv("AI_API_MODEL", "openai/gpt-5-mini")
AI_API_MAX_TOKENS = int(os.getenv("AI_API_MAX_TOKENS", "10000"))
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "You are a helpful chatbot that answers the user's messages with short, direct replies. Keep your answers clear, factual, and concise.")
MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", "1000"))

cli = BotCli("aibot")

def get_response_from_AI(msg_text: str) -> str:

    if not msg_text or not msg_text.strip():
        return "I received an empty message."

    # Truncate long messages
    if len(msg_text) > MAX_MESSAGE_LENGTH:
        logger.warning(f"Truncating message from {len(msg_text)} to {MAX_MESSAGE_LENGTH} chars")
        msg_text = msg_text[:MAX_MESSAGE_LENGTH] + "..."

    url = f"{AI_API_URL}/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "HTTP-Referer": os.getenv("APP_URL", "http://localhost"),
        "X-Title": os.getenv("APP_TITLE", "Delta Chat AI Bot"),
        "Content-Type": "application/json",
    }

    body = {
        "model": AI_API_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": msg_text},
        ],
        "temperature": 0.7,
        "max_tokens": AI_API_MAX_TOKENS,
    }

    resp = requests.post(url, headers=headers, data=json.dumps(body), timeout=120)
    resp.raise_for_status()
    data = resp.json()

    content = None
    try:
        content = data["choices"][0]["message"]["content"]
    except Exception:
        return("No content returned from AI Provider.")

    return content



@cli.on(events.NewMessage)
def process_message(bot, accid, event):
    msg = event.msg
    sender = msg.sender.name_and_addr
    logger.info(f"Received message from {sender} in chat {msg.chat_id}")
    if msg.sender.address not in RESPOND_TO: 
        bot.rpc.send_msg(accid, msg.chat_id, MsgData(text=f"Sorry {sender}, I'm not allowed to talk to you."))
        return
    try:
        logger.info(f"Getting AI response for message: {msg.text[:50]}...")
        reply = get_response_from_AI(msg.text)
        bot.rpc.send_msg(accid, msg.chat_id, MsgData(text=reply))
        logger.info(f"Sent response to {sender}")

    except Exception as e:
        logger.error(f"Error processing message from {sender}: {e}", exc_info=True)
        error_msg = "Sorry, I encountered an error processing your message. Please try again later."
        try:
            bot.rpc.send_msg(accid, msg.chat_id, MsgData(text=error_msg))
        except Exception as send_error:
            logger.error(f"Failed to send error message: {send_error}")    
        

if __name__ == "__main__":
    if "serve" in sys.argv:
        logger.info(f"Starting bot. Responding to: {RESPOND_TO}")
        logger.info(f"Using model: {AI_API_MODEL}")
    cli.start()