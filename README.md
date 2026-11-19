# WebSocket & Webhook — Hệ thống giám sát đa kênh

> Đề tài thực tập cơ sở: **Tìm hiểu WebSocket và Webhook, xây dựng hệ thống giám sát đa kênh.**
> Người thực hiện: Nguyễn Hải Sơn — 64132058 — 64.TTMMT · Giảng viên hướng dẫn: Lê Nam Tuấn

Mục tiêu cuối: hệ thống thu thập CPU/RAM từ nhiều máy, hiển thị **realtime** qua **WebSocket**
và tự động gửi cảnh báo tới **Discord / Slack / Telegram** qua **Webhook**.

## 📍 Trạng thái hiện tại — Tuần 1 (17/11 – 23/11/2026)

| Hạng mục | Trạng thái |
|---|---|
| Tài liệu WebSocket, Webhook | 🟡 Đang làm |
| Demo 01 — WebSocket chat | 🟡 Đang làm |
| Demo 02 — Webhook có ký HMAC | 🟡 Đang làm |
| Thiết kế kiến trúc hệ thống | ⚪ Chưa bắt đầu |
| Hệ thống giám sát (`monitoring-system/`) | ⚪ Từ tuần 2 |

## 📁 Cấu trúc repo

| Thư mục | Nội dung | Đọc khi muốn… |
|---|---|---|
| [`docs/`](docs) | Lý thuyết + quy ước | **hiểu** |
| [`demos/`](demos) | Demo nhỏ, mỗi demo 1 khái niệm | **thấy** từng khái niệm |
| [`reports/`](reports) | Báo cáo tuần + mẫu | **theo dõi tiến độ** |
| `monitoring-system/` | Sản phẩm chính | *(từ tuần 2)* |

## 📚 Thứ tự đọc

1. [docs/01-websocket.md](docs/01-websocket.md) → chạy [demos/01-websocket-chat](demos/01-websocket-chat)
2. [docs/02-webhook.md](docs/02-webhook.md) → chạy [demos/02-webhook-hmac](demos/02-webhook-hmac)

## ⚡ Chạy demo

Cách 1 — Docker:
```bash
cd demos/01-websocket-chat && docker compose up --build   # mở http://localhost:3000 ở 2 tab
cd demos/02-webhook-hmac  && docker compose up --build
```

Cách 2 — Python ≥ 3.11 (không cần cài thư viện):
```bash
cd demos/01-websocket-chat && python server.py
cd demos/02-webhook-hmac  && python receiver.py   # terminal khác: python sender.py
```

## 🗓 Kế hoạch

| Tuần | Nội dung | Kết quả cần có |
|---|---|---|
| 1 | Lý thuyết + 2 demo + thiết kế | Tài liệu, 2 demo chạy được, sơ đồ kiến trúc |
| 2 | Agent + hub + dashboard realtime | Dashboard hiện CPU/RAM của ≥ 2 máy |
| 3 | Cảnh báo + webhook đa kênh | Tin nhắn thật trên Discord/Telegram, có retry + HMAC |
| 4 | Docker Compose, kiểm thử, chuẩn bị demo | `docker compose up` chạy cả hệ thống |
| 5 | *(tùy chọn)* CNN phát hiện bất thường | |

## 🛠 Công nghệ
Python 3 (`asyncio`, `hmac`, `http.server`) · HTML/JS · Docker Compose
