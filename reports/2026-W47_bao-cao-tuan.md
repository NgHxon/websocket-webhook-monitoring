# Báo cáo tuần — 2026-W47 (Tuần 1)

> Khung đã điền sẵn phần kế hoạch. Cuối tuần, cập nhật lại theo ĐÚNG những gì đã làm được — xóa dòng chưa làm, thêm bằng chứng (ảnh chụp, link commit).

| | |
|---|---|
| **Người báo cáo** | [Họ tên] — [MSSV] |
| **Đề tài** | Tìm hiểu WebSocket & Webhook, xây dựng hệ thống giám sát đa kênh |
| **Kỳ báo cáo** | 17/11 – 23/11/2026 |
| **Trạng thái chung** | 🟢 Đúng tiến độ / 🟡 Có rủi ro / 🔴 Chậm tiến độ |
| **Tiến độ tổng** | __% (kế hoạch tuần 1: 20%) |

## 1. Tóm tắt (≤ 3 dòng)
_Ví dụ: Đã nắm cơ chế WebSocket (handshake, frame, ping/pong) và Webhook (HMAC, chống replay, idempotency); 2 demo chạy được trên Docker. Tuần sau bắt đầu agent + dashboard. Xin thầy góp ý sơ đồ kiến trúc ở mục 2._

## 2. Đã hoàn thành
| # | Công việc | Kết quả / Bằng chứng | Link |
|---|---|---|---|
| 1 | Tạo repo, cấu trúc thư mục, quy ước đặt tên | | `docs/03-quy-uoc-thu-muc-va-dat-ten.md` |
| 2 | Tìm hiểu WebSocket | _tóm tắt bằng lời của mình + trả lời câu hỏi tự kiểm tra_ | `docs/01-websocket.md` |
| 3 | Demo 01 — WebSocket chat | _ảnh 2 tab chat + ảnh tab WS trong DevTools_ | `demos/01-websocket-chat` |
| 4 | Tìm hiểu Webhook | | `docs/02-webhook.md` |
| 5 | Demo 02 — Webhook HMAC | _log 4 kịch bản: retry, trùng, sai chữ ký, replay_ | `demos/02-webhook-hmac` |
| 6 | Sơ đồ kiến trúc dự kiến | _ảnh sơ đồ_ | `docs/images/` |

## 3. Đang làm
| # | Công việc | % | Dự kiến xong |
|---|---|---|---|
| | | | |

## 4. Vướng mắc / Cần hỗ trợ
| Vấn đề | Đã thử những gì | Đề xuất / Cần gì từ thầy |
|---|---|---|
| | | |

## 5. Rủi ro
| Rủi ro | Khả năng | Ảnh hưởng | Cách giảm thiểu |
|---|---|---|---|
| | | | |

## 6. Kế hoạch tuần 2
- [ ] Agent đo CPU/RAM gửi về hub qua WebSocket — tiêu chí: hub in log metric của 2 agent
- [ ] Dashboard realtime — tiêu chí: biểu đồ cập nhật không cần F5
- [ ] Agent tự kết nối lại khi hub restart — tiêu chí: tắt/bật hub, agent tự nối lại

## 7. Bài học / Ghi chú
-
