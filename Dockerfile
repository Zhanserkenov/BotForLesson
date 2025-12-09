# Используем официальный Python 3.13 slim
FROM python:3.13-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY requirements.txt .
COPY bot.py .
COPY lesson.txt .

# Обновляем pip и устанавливаем зависимости
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Переменные окружения (можно переопределять на Render)
# ENV TELEGRAM_BOT_TOKEN=your_telegram_token
# ENV GEMINI_API_KEY=your_gemini_key

# Запуск бота
CMD ["python", "bot.py"]
