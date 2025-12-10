import telegram
print("PTB VERSION:", telegram.__version__)   # ← ДО ApplicationBuilder

import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

print("=== ENV CHECK ===")
print("GEMINI_API_KEY:", GEMINI_API_KEY)
print("TELEGRAM_BOT_TOKEN:", TELEGRAM_BOT_TOKEN)

# --- Загрузка данных урока из .txt ---
def load_lesson(file_path="lesson.txt"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = f.read().strip()
            print("Lesson loaded, length:", len(data))
            return data
    except Exception as e:
        print("Error loading lesson:", e)
        return ""

LESSON_TEXT = load_lesson()

# --- Обращение к Gemini ---
def ask_gemini(user_input: str, lesson_info: str) -> str:

    # Проверка наличия ключа
    if not GEMINI_API_KEY or GEMINI_API_KEY.strip() == "":
        print("ERROR: GEMINI_API_KEY is empty or missing!")
        return "Ошибка: Ключ GEMINI_API_KEY не найден на сервере."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}

    prompt = f"""
Ты — профессиональный консультант по БАДам.

Дополнительная информация:
{lesson_info}

Сообщение клиента: {user_input}
"""

    body = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    # Логи перед отправкой
    print("\n=== GEMINI REQUEST ===")
    print("URL:", url)
    print("Prompt length:", len(prompt))
    print("Body:", body)

    response = requests.post(url, headers=headers, json=body)

    print("Gemini response code:", response.status_code)
    print("Gemini response text:", response.text)

    if response.ok:
        try:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            print("Parsing error:", e)
            return "Ошибка при обработке ответа Gemini."
    else:
        return f"Ошибка при запросе к Gemini API: {response.status_code}"

# --- Обработчик Telegram ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    reply = ask_gemini(user_input, LESSON_TEXT)
    await update.message.reply_text(reply)

# --- Запуск Telegram бота ---
app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    print("Бот запущен...")
    app.run_polling()
