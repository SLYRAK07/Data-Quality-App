FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install --timeout 600 --retries 10 -r requirements.txt

COPY . .

EXPOSE 8000 8501