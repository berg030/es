from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from datetime import datetime
import json
import os

import os
TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "data.json"

# ---------- Работа с файлом ----------
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ---------- Кнопки ----------
def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📅 Установить дату", callback_data="set_date")],
        [InlineKeyboardButton("⏳ Сколько дней осталось", callback_data="count")]
    ])

# ---------- /start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💙 Бот отсчёта до встречи\n\n"
        "Этот бот предназначен для **двух конкретных людей**.\n"
        "Используй кнопки ниже 👇",
        reply_markup=main_keyboard()
    )

# ---------- Нажатия кнопок ----------
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = load_data()
    chat_id = str(query.message.chat_id)
    user_id = query.from_user.id

    if query.data == "set_date":
        context.user_data["waiting_for_date"] = True

        if chat_id not in data:
            data[chat_id] = {
                "users": [user_id],
                "date": None
            }
        elif user_id not in data[chat_id]["users"]:
            if len(data[chat_id]["users"]) < 2:
                data[chat_id]["users"].append(user_id)
            else:
                await query.message.reply_text("❌ Эта встреча уже для двух людей.")
                return

        save_data(data)

        await query.message.reply_text(
            "✍️ Отправь дату встречи в формате:\nДД.ММ.ГГГГ"
        )

    elif query.data == "count":
        if chat_id not in data or not data[chat_id]["date"]:
            await query.message.reply_text("❗ Дата ещё не установлена.")
            return

        if user_id not in data[chat_id]["users"]:
            await query.message.reply_text("❌ Ты не участник этой встречи.")
            return

        target = datetime.strptime(data[chat_id]["date"], "%d.%m.%Y").date()
        today = datetime.today().date()
        days = (target - today).days

        if days > 0:
            await query.message.reply_text(f"⏳ До встречи осталось {days} дней ❤️")
        elif days == 0:
            await query.message.reply_text("🎉 Сегодня встреча!")
        else:
            await query.message.reply_text("❌ Эта дата уже прошла.")

# ---------- Ввод даты ----------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_for_date"):
        return

    try:
        date = datetime.strptime(update.message.text, "%d.%m.%Y")
    except ValueError:
        await update.message.reply_text("❌ Неверный формат.")
        return

    data = load_data()
    chat_id = str(update.message.chat_id)

    data[chat_id]["date"] = update.message.text
    save_data(data)

    context.user_data["waiting_for_date"] = False

    await update.message.reply_text(
        f"📅 Дата встречи сохранена: {update.message.text}",
        reply_markup=main_keyboard()
    )

# ---------- Ежедневный отчёт ----------
async def daily_report(context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    today = datetime.today().date()

    for chat_id, meeting in data.items():
        if not meeting["date"]:
            continue

        target = datetime.strptime(meeting["date"], "%d.%m.%Y").date()
        days = (target - today).days

        if days >= 0:
            await context.bot.send_message(
                chat_id=int(chat_id),
                text=f"💙 До встречи осталось {days} дней"
            )

# ---------- Запуск ----------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # ежедневный отчёт в 9:00
    app.job_queue.run_daily(
        daily_report,
        time=datetime.strptime("09:00", "%H:%M").time()
    )

    app.run_polling()

if __name__ == "__main__":
    main()
