"""
Demo 01 — Phòng chat WebSocket tối giản.
Mục tiêu: quan sát handshake (HTTP Upgrade -> 101) và giao tiếp 2 chiều full-duplex.

Chạy: python server.py  -> mở http://localhost:3000 ở 2 tab trình duyệt rồi chat qua lại.
Mở DevTools > Network > WS để xem từng frame.
"""
import asyncio
import json
import os

from lib.http_lite import Request, Response, WsRoute, serve
from lib.ws_lite import WebSocket, heartbeat

PORT = int(os.getenv("PORT", 3000))
INDEX = os.path.join(os.path.dirname(__file__), "public", "index.html")
clients: set[WebSocket] = set()


async def broadcast(obj) -> None:
    msg = json.dumps(obj, ensure_ascii=False)
    await asyncio.gather(*(c.send(msg) for c in list(clients)))


async def http_handler(req: Request) -> Response:
    if req.path == "/":
        with open(INDEX, "rb") as f:
            return Response(200, f.read(), "text/html; charset=utf-8")
    return Response(404, b"not found")


async def on_chat(ws: WebSocket, req: Request) -> None:
    # In header handshake: WebSocket bắt đầu từ 1 request HTTP bình thường
    print("--- Handshake ---")
    print(f"GET {req.path}")
    for h in ("upgrade", "connection", "sec-websocket-key", "sec-websocket-version"):
        print(f"{h}: {req.headers.get(h)}")
    print("=> HTTP/1.1 101 Switching Protocols\n", flush=True)

    clients.add(ws)
    name = "Ẩn danh"
    try:
        async for raw in ws:
            msg = json.loads(raw)
            if msg.get("type") == "join":
                name = str(msg.get("name", ""))[:30] or name
                await broadcast({"type": "system", "text": f"{name} đã vào phòng", "online": len(clients)})
            elif msg.get("type") == "chat":
                await broadcast({"type": "chat", "from": name, "text": str(msg.get("text", ""))[:500]})
    finally:
        clients.discard(ws)
        await broadcast({"type": "system", "text": f"{name} đã rời phòng", "online": len(clients)})


async def main() -> None:
    server = await serve("0.0.0.0", PORT, http_handler, {"/ws": WsRoute(on_chat)})
    print(f"[demo-01] Mở http://localhost:{PORT} ở 2 tab để chat", flush=True)
    asyncio.create_task(heartbeat(lambda: clients))
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
