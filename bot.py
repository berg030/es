from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime

TOKEN = "8500567902:AAH-4xRjSajXx6smkfTaB6_ae-PWkeTP8tY"

# Храним даты встреч для каждого чата
meetings = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Бот отсчёта до встречи\n\n"
        "Команды:\n"
        "/setdate ДД.ММ.ГГГГ — установить дату встречи\n"
        "/count — сколько дней осталось"
    )

async def set_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if not context.args:
        await update.message.reply_text("⚠️ Используй: /setdate ДД.ММ.ГГГГ")
        return

    try:
        date_str = context.args[0]
        target_date = datetime.strptime(date_str, "%d.%m.%Y").date()
        meetings[chat_id] = target_date

        await update.message.reply_text(
            f"📅 Дата встречи установлена: {date_str}"
        )

    except ValueError:
        await update.message.reply_text("❌ Неверный формат даты")

async def count_days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if chat_id not in meetings:
        await update.message.reply_text(
            "❗ Дата встречи не установлена.\nИспользуй /setdate"
        )
        return

    today = datetime.today().date()
    target_date = meetings[chat_id]
    days_left = (target_date - today).days

    if days_left > 0:
        await update.message.reply_text(
            f"⏳ До встречи осталось {days_left} дней ❤️"
        )
    elif days_left == 0:
        await update.message.reply_text(
            "🎉 Сегодня встреча!"
        )
    else:
        await update.message.reply_text(
            f"❌ Встреча была {abs(days_left)} дней назад"
        )

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setdate", set_date))
    app.add_handler(CommandHandler("count", count_days))

    app.run_polling()

if __name__ == "__main__":
    main()
