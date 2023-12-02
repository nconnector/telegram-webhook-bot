from flask import Flask, request
import telegram
from dotenv import load_dotenv
import os
import threading

from utills import get_whitelist, start_ngrok, stop_ngrok, get_local_ip

# Load environment variables
load_dotenv()

API_PORT = os.getenv("API_PORT")
bot = telegram.Bot(token=os.getenv("TELEGRAM_API_KEY"))
app = Flask(__name__)

# Function to send messages to whitelisted users
def send_message_to_whitelisted_users(message):
    for user_id in get_whitelist():
        print(f'sending to {user_id}')
        bot.send_message(chat_id=user_id, text=message)

# Endpoint to trigger bot command
@app.route('/trigger_bot_command', methods=['POST'])
def trigger_bot_command():
    data = request.json
    message = "MESSAGE"

    # Call the function to send messages to whitelisted users
    threading.Thread(
        target=send_message_to_whitelisted_users, 
        args=(message,)
    ).start()
    return "Command Triggered", 200

# Print the local IP address
print("Server starting on IP:", get_local_ip())


# Start ngrok when Flask app starts
if __name__ == "__main__":
    public_url = start_ngrok()
    try:
        app.run(port=API_PORT)
    finally:
        stop_ngrok()