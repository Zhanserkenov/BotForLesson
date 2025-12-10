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
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()

LESSON_TEXT = load_lesson()

def ask_gemini(user_input: str, lesson_info: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}

    prompt = f"""
Ты — профессиональный консультант по продукции нашей компании. 
Твоя задача: понятно, дружелюбно и профессионально отвечать клиенту, 
используя следующую информацию о товарах:

{lesson_info}

Правила ответа:
1. Всегда отвечай простым человеческим языком.
2. Если клиент задаёт вопрос — дай полезный, чёткий ответ.
3. Если его вопрос связан с нашими товарами — предложи подходящие варианты.
4. Не будь навязчивым. Продавай мягко: «если хотите», «можете рассмотреть вариант», «подойдут такие позиции».
5. Отвечай кратко, но не сильно кратко
6. Если клиент спрашивает не по теме — корректно отвечай, но мягко направляй назад к продукции.

Сообщение клиента:
{user_input}

Сформируй профессиональный ответ консультанта:
    """

    body = {
        "contents": [
            {
                "parts": [{"text": prompt}]
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
