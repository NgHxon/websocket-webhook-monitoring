"""
Demo 02 — Webhook SENDER (bên gửi). Chỉ dùng thư viện chuẩn.
Ký HMAC-SHA256, gửi POST, retry với exponential backoff, rồi thử 2 kịch bản tấn công.

Chạy: python sender.py   (sau khi đã chạy receiver.py)
"""
import hashlib
import hmac
import json
import os
import random
import time
import urllib.error
import urllib.request
import uuid

TARGET = os.getenv("TARGET_URL", "http://localhost:4000/webhook")
SECRET = os.getenv("WEBHOOK_SECRET", "demo-secret")


def post_signed(event: dict, secret: str = SECRET, timestamp: int | None = None) -> tuple[int, str]:
    body = json.dumps(event, ensure_ascii=False).encode()
    ts = str(timestamp if timestamp is not None else int(time.time()))
    sig = "sha256=" + hmac.new(secret.encode(), f"{ts}.".encode() + body, hashlib.sha256).hexdigest()
    req = urllib.request.Request(TARGET, data=body, method="POST", headers={
        "Content-Type": "application/json", "X-Webhook-Id": event["id"],
        "X-Webhook-Timestamp": ts, "X-Webhook-Signature": sig,
    })
    try:
        with urllib.request.urlopen(req, timeout=5) as res:
            return res.status, res.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def send_with_retry(event: dict, max_attempts: int = 5) -> bool:
    for attempt in range(1, max_attempts + 1):
        try:
            status, _ = post_signed(event)  # ký lại mỗi lần để timestamp luôn mới
            print(f"[sender] lần {attempt}: HTTP {status}")
            if 200 <= status < 300:
                return True
            if status < 500 and status != 429:
                return False  # lỗi 4xx: gửi lại cũng vô ích
        except OSError as e:
            print(f"[sender] lần {attempt}: lỗi mạng {e}")
        wait = 0.5 * 2 ** (attempt - 1) + random.random() * 0.2
        print(f"[sender]   -> chờ {wait:.2f}s rồi thử lại")
        time.sleep(wait)
    return False


if __name__ == "__main__":
    time.sleep(float(os.getenv("START_DELAY_SEC", 0)))
    event = {"id": str(uuid.uuid4()), "type": "order.paid", "data": {"order_id": "DH-1024", "amount": 250000}}

    print("\n=== 1. Gửi bình thường (receiver sẽ cố tình lỗi vài lần đầu) ===")
    send_with_retry(event)

    print("\n=== 2. Gửi lại đúng sự kiện đó (mô phỏng retry trùng) ===")
    send_with_retry(event)

    print("\n=== 3. Kẻ giả mạo không biết secret ===")
    print("[sender] HTTP %s — %s" % post_signed({"id": str(uuid.uuid4()), "type": "order.paid"}, secret="hacker"))

    print("\n=== 4. Replay: request hợp lệ nhưng timestamp từ 10 phút trước ===")
    print("[sender] HTTP %s — %s" % post_signed({"id": str(uuid.uuid4()), "type": "order.paid"},
                                               timestamp=int(time.time()) - 600))
