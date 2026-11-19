# Chỉ dùng thư viện chuẩn Python -> không cần pip install
FROM python:3.13-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
COPY lib ./lib
COPY public ./public
COPY server.py ./
RUN useradd --create-home appuser
USER appuser
EXPOSE 3000
CMD ["python", "server.py"]
