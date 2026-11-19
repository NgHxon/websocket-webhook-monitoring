# Demo 01 — WebSocket Chat

**Chứng minh:** WebSocket bắt đầu bằng HTTP Upgrade, sau đó giao tiếp 2 chiều realtime. Server tự cài đặt theo RFC 6455 trong [`lib/ws_lite.py`](lib/ws_lite.py) + [`lib/http_lite.py`](lib/http_lite.py), chỉ dùng thư viện chuẩn Python.

## Chạy
```bash
docker compose up --build      # hoặc: python server.py  (Python >= 3.11)
```
Mở **2 tab** http://localhost:3000, nhập tên khác nhau rồi chat.

## Quan sát
1. **Terminal** in ra header handshake: `upgrade: websocket`, `sec-websocket-key: ...` → `101 Switching Protocols`.
2. **DevTools → Network → WS → Messages**: thấy từng frame gửi/nhận, không có request HTTP mới cho mỗi tin nhắn.
3. Tắt server → trang báo "Mất kết nối" (sự kiện `close`).

## Câu hỏi thêm
- So sánh số byte 1 tin nhắn qua WebSocket với 1 request `fetch()` POST tương đương (xem tab Network).
