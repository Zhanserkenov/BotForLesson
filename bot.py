import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

 GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
 TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# --- Загрузка данных урока из .txt ---
def load_lesson(file_path="lesson.txt"):
    """
    Загружает текст урока из файла.
    Каждый блок можно разделять двойным переносом строки, если нужно.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()

LESSON_TEXT = load_lesson()

# --- Обращение к Gemini через REST API ---
def ask_gemini(user_input: str, lesson_info: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {
        "Content-Type": "application/json"
    }

    prompt = f"""
Ты — профессиональный консультант по БАДам, нутриционному здоровью и функциональному питанию.
Отвечай всегда КРАТКО, понятно и по делу, как эксперт, который помогает клиенту подобрать добавки.

Дополнительная информация (описание продукта / урока):
{lesson_info}

Сообщение клиента: {user_input}
"""

    body = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=body)
    if response.ok:
        try:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        except Exception:
            return "Ошибка при обработке ответа Gemini."
    else:
        return f"Ошибка при запросе к Gemini API: {response.status_code}"

# --- Обработчик сообщений Telegram ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    reply = ask_gemini(user_input, LESSON_TEXT)
    await update.message.reply_text(reply)

# --- Запуск Telegram-бота ---
app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    print("Бот запущен...")
    app.run_polling()
