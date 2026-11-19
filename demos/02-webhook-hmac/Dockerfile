# Một image dùng chung cho sender và receiver, khác nhau ở lệnh chạy (command)
FROM python:3.13-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
COPY receiver.py sender.py ./
RUN useradd --create-home appuser
USER appuser
