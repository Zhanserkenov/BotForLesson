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
Ты — краткий и профессиональный консультант по продукции компании.

Информация о товарах:
{lesson_info}

Инструкции:
- Отвечай коротко и по делу — не более 1500 символов.
- Если вопрос о товарах — сразу предложи 1–3 конкретных варианта, укажи ID и цену в одной строке на вариант.
- Начинай с короткой рекомендации (1 предложение), затем — варианты (если нужно).
- Не добавляй медицинские или юридические дисклеймеры и не проси «проконсультируйтесь с врачом» — такие фразы **не писать никогда**.
- Не пиши длинных объяснений и историй.
- Используй мягкие формулировки: «можете рассмотреть», «подойдёт вариант», «если хотите».

Сообщение клиента:
{user_input}

Дай краткий целевой ответ-консультант:
    """

    body = {
        "contents": [
            { "parts": [{"text": prompt}] }
        ],
        # Ограничение длины — дополнительная страховка (при наличии поддержки API)
        "maxOutputTokens": 200
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
