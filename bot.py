import telegram
print("PTB VERSION:", telegram.__version__)   # ← ДО ApplicationBuilder

import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# --- Загрузка данных урока из .txt ---
def load_lesson(file_path="lesson.txt"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = f.read().strip()
            print("Lesson loaded, length:", len(data))
            return data
    except Exception as e:
        print("Ошибка при загрузке урока:", e)
        return ""

LESSON_TEXT = load_lesson()

# --- Обращение к Gemini ---
def ask_gemini(user_input: str, lesson_info: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}

    # Инструкции для модели — коротко, по делу, мягкие продажи, 1–3 варианта
    prompt = f"""
Ты — профессиональный консультант по продукции нашей компании.
Инструкции:
- Отвечай коротко и по делу — не более 1500 символов.
- Если вопрос о товарах — сразу предложи 1–3 конкретных варианта с ID и ценой.
- Начинай с короткой рекомендации (1 предложение), затем — варианты (если нужно).
- Не добавляй медицинские или юридические disclaimers.
- Не проси «проконсультируйтесь с врачом».
- Используй мягкие формулировки: «можете рассмотреть», «подойдёт вариант», «если хотите».
- Не пиши длинных объяснений и историй.

Информация о товарах / урок:
{lesson_info}

Сообщение клиента:
{user_input}

Сформируй ответ согласно инструкции:
    """

    body = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=body)

    print("Gemini response code:", response.status_code)
    print("Gemini raw:", response.text)

    if response.ok:
        try:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            return f"Ошибка при обработке ответа Gemini: {e}"
    else:
        return f"Ошибка при запросе к Gemini API: {response.status_code} - {response.text}"

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
