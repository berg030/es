import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN не найден")

ALLOWED_USERS = [123456789, 987654321]  # <- замени на свои user_id
MEETING_DATE = datetime(2026, 2, 1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        await update.message.reply_text("Доступ закрыт")
        return
    keyboard = [[InlineKeyboardButton("Сколько дней до встречи?", callback_data="count")]]
    await update.message.reply_text("Привет! Выберите действие:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id not in ALLOWED_USERS:
        await query.edit_message_text("Доступ закрыт")
        return
    if query.data == "count":
        delta = MEETING_DATE - datetime.now()
        await query.edit_message_text(f"До встречи осталось {delta.days} дней!")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
