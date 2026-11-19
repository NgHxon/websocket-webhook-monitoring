# 04. Quy ước tổ chức thư mục & đặt tên

> Theo góp ý của thầy: *"Tổ chức thư mục, tên file thế nào để người khác dễ dàng biết mình làm gì."*
> Nguyên tắc chung: **người lạ mở repo ra, trong 1 phút phải biết: dự án làm gì, chạy thế nào, code chính ở đâu, tiến độ tới đâu.**

## 1. Cấu trúc thư mục và lý do

```
websocket-webhook-monitoring/
├── README.md                 # Cửa chính: dự án là gì, chạy ra sao, đọc gì tiếp
├── docs/                     # Kiến thức (đọc để HIỂU)
│   ├── 01-websocket.md       #   đánh số = thứ tự nên đọc
│   ├── 02-webhook.md
│   ├── 03-quy-uoc-thu-muc-va-dat-ten.md
│   ├── 04-kien-truc-he-thong.md      #   (tuần 2)
│   └── images/               #   ảnh minh họa dùng trong docs
├── demos/                    # Ví dụ nhỏ, mỗi demo chứng minh 1 khái niệm (chạy để THẤY)
│   ├── 01-websocket-chat/
│   └── 02-webhook-hmac/
├── monitoring-system/        # Sản phẩm chính (bắt đầu từ tuần 2)
│   ├── docker-compose.yml    #   1 lệnh chạy cả hệ thống
│   ├── .env.example          #   mẫu cấu hình, KHÔNG chứa secret thật
│   ├── scripts/              #   công cụ hỗ trợ test
│   └── services/             #   mỗi service 1 thư mục, có Dockerfile + requirements.txt riêng
│       ├── hub/
│       │   ├── app/          #     code chạy (package Python)
│       │   ├── ml/           #     code huấn luyện CNN — tách khỏi code chạy
│       │   └── model/        #     file trọng số sinh ra từ ml/
│       ├── agent/
│       └── mock-receiver/
└── reports/                  # Báo cáo tiến độ cho thầy / leader
    ├── TEMPLATE_bao-cao-tuan.md
    └── 2026-W47_bao-cao-tuan.md
```

Tách theo **mục đích sử dụng**: `docs` (hiểu) — `demos` (thấy) — `monitoring-system` (sản phẩm) — `reports` (quản lý). Người đọc tìm đúng chỗ theo câu hỏi của họ.

## 2. Quy tắc đặt tên

| Đối tượng | Quy tắc | Ví dụ đúng | Tránh |
|---|---|---|---|
| Thư mục, tài liệu | `kebab-case`, chữ thường, **không dấu**, không khoảng trắng | `mock-receiver/`, `02-webhook.md` | `Mock Receiver (final)/`, `cảnh báo.md` |
| File/module Python | `snake_case.py` (PEP 8 — tên có `-` không `import` được) | `alert_engine.py` | `AlertEngine.py`, `alert-engine.py` |
| Tài liệu/demo theo thứ tự | Tiền tố số 2 chữ số | `01-websocket.md` | `websocket.md`, `1-websocket.md` (sắp xếp sai khi > 9 file) |
| Báo cáo theo thời gian | `YYYY-Www_<loai>.md` hoặc `YYYY-MM-DD_<loai>.md` (ISO 8601) | `2026-W47_bao-cao-tuan.md` | `baocao_tuan3_moi_nhat.docx` |
| File mẫu | Tiền tố `TEMPLATE_` | `TEMPLATE_bao-cao-tuan.md` | `mau.md` |
| Service Docker | `<vai-trò>` ngắn gọn | `hub`, `agent` | `server2`, `test-new` |
| Container / instance | `<vai-trò>-<loại>-<số>` | `agent-web-01`, `agent-db-01` | `agent1`, `abc` |
| Biến môi trường | `UPPER_SNAKE_CASE`, nhóm theo tiền tố | `ALERT_CPU_THRESHOLD`, `DISCORD_WEBHOOK_URL` | `cpu`, `url1` |
| Biến/hàm Python | `snake_case`, hàm bắt đầu bằng động từ | `build_channels()`, `check_offline()` | `data2()`, `xuly()` |
| Class Python | `PascalCase` | `AlertEngine`, `CNN1D` | `alertengine` |
| Field JSON | `snake_case`, thống nhất toàn hệ thống | `agent_id`, `cnn_score` | lẫn lộn `agentId` và `agent_id` |
| Loại message/sự kiện | `noun.verb` (quá khứ) hoặc `snake_case` | `deploy.failed`, `agent_offline` | `Event1` |

**Không bao giờ** đặt: `final`, `final-v2`, `new`, `test123`, `copy of ...` — dùng Git để quản lý phiên bản thay vì đổi tên file.

## 3. Mỗi thư mục quan trọng đều có README

README của một service/demo trả lời đủ 4 câu:
1. **Cái này là gì?** (1–2 câu)
2. **Chạy thế nào?** (lệnh copy-paste được)
3. **Kết quả mong đợi?** (nhìn thấy gì thì là đúng)
4. **Cấu hình gì được?** (bảng biến môi trường)

## 4. Quy ước Git (khi đưa lên GitHub/GitLab)

- Nhánh: `main` (ổn định), `feature/<ten-tinh-nang>`, `fix/<ten-loi>`. VD: `feature/telegram-channel`.
- Commit theo **Conventional Commits**:
  ```
  feat(hub): thêm kênh thông báo Telegram
  fix(agent): sửa lỗi không reconnect khi hub restart
  docs: bổ sung sơ đồ kiến trúc
  chore(docker): thêm healthcheck cho hub
  ```
- Không commit: `__pycache__/`, `.venv/`, `.env`, file log → đã khai báo trong `.gitignore`.

## 5. Đóng gói Docker

- Mỗi service có `Dockerfile` riêng nằm ngay trong thư mục service.
- Mỗi demo/hệ thống có `docker-compose.yml` ở thư mục gốc của nó → **chỉ cần `cd` vào và `docker compose up --build`**.
- Image nhỏ (`python:3.13-slim`), cài thư viện trước rồi mới copy code (tận dụng cache), không chạy bằng root (`USER appuser`), có `HEALTHCHECK`, cấu hình qua biến môi trường.
