import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Берём токен из переменной окружения Railway
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN not set in environment variables")

# Два разрешённых пользователя (Telegram user_id)
ALLOWED_USERS = [123456789, 987654321]  # <-- замени на реальные user_id

# Дата встречи
MEETING_DATE = datetime(2026, 2, 1)  # YYYY, M, D

# /start команда
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("Доступ закрыт.")
        return

    keyboard = [
        [InlineKeyboardButton("Посчитать дни до встречи", callback_data="count_days")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет! Выберите действие:", reply_markup=reply_markup)

# Обработка кнопок
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if user_id not in ALLOWED_USERS:
        await query.edit_message_text("Доступ закрыт.")
        return

    if query.data == "count_days":
        now = datetime.now()
        delta = MEETING_DATE - now
        await query.edit_message_text(f"До встречи осталось {delta.days} дней!")

# Основной запуск
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
