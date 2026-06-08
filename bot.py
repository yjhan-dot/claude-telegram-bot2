import os
import anthropic
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

conversation_history = {}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    user_message = update.message.text
    
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    
    conversation_history[user_id].append({"role": "user", "content": user_message})
    await context.bot.send_chat_action(chat_id=user_id, action="typing")
    
    response = claude.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system="You are a helpful assistant. Respond in the same language the user writes in.",
        messages=conversation_history[user_id]
    )
    
    reply = response.content[0].text
    conversation_history[user_id].append({"role": "assistant", "content": reply})
    await update.message.reply_text(reply)

async def handle_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    conversation_history[user_id] = []
    await update.message.reply_text("대화 초기화! 😊")

if __name__ == "__main__":
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("reset", handle_reset))
    print("봇 시작됨!")
    app.run_polling()
