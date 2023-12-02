import os
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler

from .utills import get_whitelist

# Load environment variables
load_dotenv()

# Read the environment variables
TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")
USERS_WHITELIST = get_whitelist()
REG_PIN = os.getenv("REG_PIN")

# Function to update the .env file
def update_whitelist_env(whitelist):
    # Read the entire .env file into memory
    with open(".env", "r") as file:
        lines = file.readlines()

    # Replace the line containing USERS_WHITELIST
    with open(".env", "w") as file:
        for line in lines:
            if line.startswith('USERS_WHITELIST='):
                file.write(f"USERS_WHITELIST={','.join(map(str, whitelist))}\n")
            else:
                file.write(line)

# Define states for conversation handler
AWAITING_PIN = 1

# Message handler to check if user is whitelisted
async def message_handler(update: Update, context: CallbackContext) -> int:
    user_id = update.effective_user.id

    if user_id in USERS_WHITELIST:
        user = update.message.from_user
        sender_info = f"Message from {user.full_name} (Username: @{user.username}, ID: {user.id})"
        await update.message.reply_text(sender_info)
    else:
        await update.message.reply_text("Please enter the registration PIN:")
        return AWAITING_PIN

# Handler for PIN input
async def pin_handler(update: Update, context: CallbackContext) -> int:
    user_id = update.effective_user.id
    pin_input = update.message.text

    if pin_input == REG_PIN:
        USERS_WHITELIST.append(user_id)
        update_whitelist_env(USERS_WHITELIST)
        await update.message.reply_text("OK, you are now registered.")
    else:
        await update.message.reply_text("No, the PIN is incorrect.")

    return ConversationHandler.END

# Handler for cancel command
async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Operation canceled.')
    return ConversationHandler.END

# Set up the Application
application = Application.builder().token(TELEGRAM_API_KEY).build()

# Conversation handler for the authentication process
conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.TEXT, message_handler)],
    states={
        AWAITING_PIN: [MessageHandler(filters.TEXT, pin_handler)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

# Add conversation handler to the application
application.add_handler(conv_handler)

# Run the bot
application.run_polling()
