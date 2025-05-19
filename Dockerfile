# === Build stage ===
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# === Final stage ===
FROM python:3.12-slim

WORKDIR /app

# Копируем только установленное из builder-стейджа
COPY --from=builder /install /usr/local

# Копируем остальной код
COPY . .

CMD ["python", "app.py"]