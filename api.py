from fastapi import FastAPI
from pydantic import BaseModel
import telegram
from dotenv import load_dotenv
import os
import asyncio
import json
from typing import Union

from utills import get_whitelist, start_ngrok, stop_ngrok, get_local_ip

# Load environment variables
load_dotenv()

API_PORT = int(os.getenv("API_PORT"))
bot = telegram.Bot(token=os.getenv("TELEGRAM_API_KEY"))
app = FastAPI()

class MessagePayload(BaseModel):
    message: Union[str, dict, list]

# Function to send messages to whitelisted users
async def send_message_to_whitelisted_users(message):
    if isinstance(message, str):
        formatted_message = message.translate(str.maketrans({
            "_": "\\_",
            "*": "\\*",
            "[": "\\[",
            "]": "\\]",
            "(": "\\(",
            ")": "\\)",
            "~": "\\~",
            ">": "\\>",
            "#": "\\#",
            "+": "\\+",
            "-": "\\-",
            "=": "\\=",
            "|": "\\|",
            "{": "\\{",
            "}": "\\}",
            ".": "\\.",
            "!": "\\!"
        }))
    else:
        message = json.dumps(message, indent=4)
        formatted_message = f"```\n{message}\n```"


    USER_IDS = get_whitelist()
    for user_id in USER_IDS:
        print(f'Sending to {user_id}')
        await bot.send_message(chat_id=user_id, text=formatted_message, parse_mode='MarkdownV2')

# Endpoint to trigger bot command
@app.post("/trigger_bot_command")
async def trigger_bot_command(req: MessagePayload):
    asyncio.create_task(send_message_to_whitelisted_users(req.message))
    return {"message": "OK"}

# Print the local IP address
print("Server starting on IP:", get_local_ip())

# Start ngrok when FastAPI app starts
if __name__ == "__main__":
    try:
        public_url = start_ngrok()
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=API_PORT)
    finally:
        stop_ngrok()
