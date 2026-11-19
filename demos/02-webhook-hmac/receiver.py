"""
Demo 02 — Webhook RECEIVER (bên nhận). Chỉ dùng thư viện chuẩn.
Thể hiện 4 việc bên nhận webhook PHẢI làm:
  1. Xác thực chữ ký HMAC trên raw body
  2. Kiểm tra timestamp để chống replay
  3. Idempotency: cùng X-Webhook-Id chỉ xử lý 1 lần
  4. Trả lời nhanh 2xx, việc nặng làm sau

Chạy: python receiver.py
"""
import hashlib
import hmac
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.getenv("PORT", 4000))
SECRET = os.getenv("WEBHOOK_SECRET", "demo-secret")
FAIL_FIRST_N = int(os.getenv("FAIL_FIRST_N", 2))  # cố tình lỗi N request đầu để thấy sender retry

request_count = 0
processed: set[str] = set()
lock = threading.Lock()


def verify(headers, raw: bytes) -> str | None:
    ts = headers.get("X-Webhook-Timestamp")
    sig = headers.get("X-Webhook-Signature", "")
    if not ts:
        return "thiếu timestamp"
    if abs(time.time() - int(ts)) > 300:
        return "timestamp quá cũ (nghi replay)"
    expected = "sha256=" + hmac.new(SECRET.encode(), f"{ts}.".encode() + raw, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig):
        return "chữ ký sai"
    return None


def process_event(event: dict) -> None:
    """Việc nặng (ghi DB, gửi mail...) chạy sau khi đã trả lời bên gửi."""
    print(f"           ✅ xử lý sự kiện: {event}", flush=True)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def reply(self, status: int, text: str = "") -> None:
        body = text.encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        global request_count
        if self.path != "/webhook":
            return self.reply(404)
        raw = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        event_id = self.headers.get("X-Webhook-Id")
        with lock:
            request_count += 1
            n = request_count

        if n <= FAIL_FIRST_N:
            print(f"[receiver] #{n} id={event_id} -> 503 (giả lập server đang quá tải)", flush=True)
            return self.reply(503)

        error = verify(self.headers, raw)
        if error:
            print(f"[receiver] #{n} id={event_id} -> 401 ({error})", flush=True)
            return self.reply(401, error)

        with lock:
            if event_id in processed:
                print(f"[receiver] #{n} id={event_id} -> 200 (đã xử lý rồi, bỏ qua)", flush=True)
                return self.reply(200, "duplicate")
            processed.add(event_id)

        print(f"[receiver] #{n} id={event_id} -> 202", flush=True)
        self.reply(202, "accepted")
        threading.Thread(target=process_event, args=(json.loads(raw),)).start()


if __name__ == "__main__":
    print(f"[receiver] Lắng nghe webhook tại http://localhost:{PORT}/webhook", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
