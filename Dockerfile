# ───────────────────────────────────────────────
#  Python — LoRa TTN → SQLite
#  Raspberry Pi 4/5  (linux/arm64)
# ───────────────────────────────────────────────

FROM python:3.11-slim

LABEL description="TTN MQTT → SQLite collector | ARM64"

WORKDIR /app

# Системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Зависимости Python
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Исходный код
COPY . .

# Папка для SQLite файла (будет смонтирована как volume)
RUN mkdir -p /data

# Непривилегированный пользователь
RUN addgroup --system appgroup \
    && adduser --system --ingroup appgroup appuser \
    && chown -R appuser:appgroup /app /data

USER appuser

# SQLite хранится в /data — туда монтируем volume
VOLUME ["/data"]

CMD ["python", "main.py"]