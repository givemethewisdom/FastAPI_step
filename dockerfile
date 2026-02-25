FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все необходимые папки
COPY ./app /app/app
COPY ./DataBase /app/DataBase
COPY ./alembic /app/alembic
COPY ./auth /app/auth

ENV PYTHONPATH=/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]