import os
import time
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Ваш рабочий ключ
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


def load_lesson(file_path="lesson.txt"):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()


LESSON_TEXT = load_lesson()


def ask_gemini(user_input: str, lesson_info: str) -> str:
    # ✅ Исправлено: gemini-2.5-flash + v1
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}

    prompt = f"""
Ты — преподаватель по теме Strategic Trade Control. Отвечай **коротко и понятно**.
Информация об уроке: {lesson_info}
Вопрос студента: {user_input}
"""

    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 500}
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code == 429:
        return "⏳ Слишком много запросов. Подождите 1 минуту (Free Tier лимит)."
    elif response.ok:
        try:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        except Exception:
            return "Ошибка при обработке ответа Gemini."
    else:
        return f"Ошибка API: {response.status_code} - {response.text[:100]}"


# ✅ Добавлена задержка между запросами (Free Tier: 15 RPM)
last_request_time = 0


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_request_time
    now = time.time()

    # Задержка минимум 4 секунды между запросами (15 RPM)
    if now - last_request_time < 4:
        await update.message.reply_text("⏳ Подождите 4 секунды между сообщениями (лимит Free Tier).")
        return
    last_request_time = now

    user_input = update.message.text
    reply = ask_gemini(user_input, LESSON_TEXT)
    await update.message.reply_text(reply)


app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    print("✅ Бот запущен с защитой от 429...")
    app.run_polling()
