# Demo 02 — Webhook có ký HMAC

**Chứng minh:** bên gửi ký + retry; bên nhận xác thực chữ ký, chống replay, chống trùng.

## Chạy
```bash
docker compose up --build
```
Hoặc không dùng Docker (Python ≥ 3.11, không cần cài thư viện), 2 terminal:
```bash
python receiver.py
python sender.py
```

## Kết quả mong đợi
| Kịch bản | Sender thấy | Receiver thấy |
|---|---|---|
| 1. Gửi bình thường | 503, 503, rồi **202** (retry có backoff) | 2 lần lỗi giả lập, lần 3 xử lý sự kiện |
| 2. Gửi lại cùng id | **200** | "đã xử lý rồi, bỏ qua" |
| 3. Sai secret | **401** | "chữ ký sai" |
| 4. Timestamp 10 phút trước | **401** | "timestamp quá cũ (nghi replay)" |

## Biến môi trường
| Biến | Mặc định | |
|---|---|---|
| `WEBHOOK_SECRET` | demo-secret | Secret dùng chung 2 bên |
| `FAIL_FIRST_N` | 2 | Receiver cố tình trả 503 cho N request đầu |
| `TARGET_URL` | http://localhost:4000/webhook | Địa chỉ sender gửi tới |
