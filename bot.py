import os
import datetime
import pytz  # Библиотека для часовых поясов
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# --- НАСТРОЙКИ ---
TOKEN = os.getenv("BOT_TOKEN")

# Вставь сюда ваши реальные ID
ALLOWED_USERS = [6829843196, 1873521734]

# 1. Устанавливаем Новосибирское время
TIMEZONE = pytz.timezone("Asia/Novosibirsk")

# 2. Во сколько присылать отчёт? (Здесь стоит 09:00 утра по Новосибирску)
DAILY_TIME = datetime.time(hour=9, minute=00, tzinfo=TIMEZONE)

# Хранилище в памяти
meeting_data = {
    "date": None,
    "chat_id": None
}

WAITING_FOR_DATE = False

async def check_access(update: Update):
    user_id = update.effective_user.id
    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("⛔ Доступ закрыт.")
        return False
    return True

# Главное меню
def main_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("⏳ Сколько осталось"), KeyboardButton("📅 Установить дату")],
        ],
        resize_keyboard=True
    )

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update): return
    
    await update.message.reply_text(
        "Привет! 👋\nЯ работаю по Новосибирскому времени.\n"
        "Нажми **«📅 Установить дату»**, чтобы я начал отсчёт.",
        reply_markup=main_keyboard()
    )

# Обработка сообщений и кнопок
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update): return

    text = update.message.text
    global WAITING_FOR_DATE

    # Если нажали кнопку "Сколько осталось"
    if text == "⏳ Сколько осталось":
        if meeting_data["date"] is None:
            await update.message.reply_text("Дата ещё не установлена! Нажми кнопку настройки.")
        else:
            # Считаем разницу
            target = meeting_data["date"]
            # Важно: берем текущую дату тоже по Новосибирску, чтобы было честно
            now_nsk = datetime.datetime.now(TIMEZONE).date()
            days = (target - now_nsk).days
            
            await update.message.reply_text(f"💙 До встречи осталось дней: {days}")

    # Если нажали кнопку "Установить дату"
    elif text == "📅 Установить дату":
        WAITING_FOR_DATE = True
        await update.message.reply_text("✍️ Напиши дату встречи (ДД.ММ.ГГГГ):")

    # Если ввели саму дату
    elif WAITING_FOR_DATE:
        try:
            date_obj = datetime.datetime.strptime(text, "%d.%m.%Y").date()
            
            meeting_data["date"] = date_obj
            meeting_data["chat_id"] = update.message.chat_id
            WAITING_FOR_DATE = False 
            
            await update.message.reply_text(
                f"✅ Дата {text} сохранена!\n"
                f"Я буду писать отчет каждый день в 09:00 (Новосибирск).",
                reply_markup=main_keyboard()
            )
            
            # Запускаем таймер
            remove_job_if_exists(str(update.message.chat_id), context)
            context.job_queue.run_daily(
                send_daily_reminder, 
                time=DAILY_TIME, 
                chat_id=update.message.chat_id, 
                name=str(update.message.chat_id)
            )

        except ValueError:
            await update.message.reply_text("❌ Ошибка. Формат: ДД.ММ.ГГГГ")

    else:
        await update.message.reply_text("Используй кнопки 👇", reply_markup=main_keyboard())

# Функция удаления старого таймера (чтобы не дублировались)
def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

# Эта функция срабатывает каждый день в 9:00
async def send_daily_reminder(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    if meeting_data["date"]:
        # Считаем дни по Новосибирску
        now_nsk = datetime.datetime.now(TIMEZONE).date()
        days = (meeting_data["date"] - now_nsk).days
        
        await context.bot.send_message(
            job.chat_id, 
            text=f"☀️ Доброе утро (Новосибирск)! До встречи осталось дней: {days} ❤️"
        )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()