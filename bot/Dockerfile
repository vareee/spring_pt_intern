FROM python:3.10-slim

WORKDIR /bot

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN touch bot_logs.txt

RUN pip install -r requirements.txt

CMD ["python", "bot.py"]
