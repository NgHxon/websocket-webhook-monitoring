"""
http_lite.py — HTTP/1.1 server tối giản trên asyncio, biết "nâng cấp" request lên WebSocket.

Đủ dùng cho demo. Dự án thật: FastAPI / Starlette + uvicorn (hỗ trợ cả HTTP lẫn WebSocket sẵn).
"""
from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from http import HTTPStatus
from typing import Awaitable, Callable
from urllib.parse import parse_qs, urlsplit

from .ws_lite import WebSocket, accept_key

MAX_BODY = 64 * 1024


@dataclass
class Request:
    method: str
    path: str
    query: dict[str, str]
    headers: dict[str, str]  # tên header đã viết thường
    body: bytes = b""


@dataclass
class Response:
    status: int = 200
    body: bytes = b""
    content_type: str = "text/plain; charset=utf-8"
    headers: dict[str, str] = field(default_factory=dict)

    @staticmethod
    def json(obj, status: int = 200) -> "Response":
        return Response(status, json.dumps(obj, ensure_ascii=False).encode(), "application/json; charset=utf-8")


HttpHandler = Callable[[Request], Awaitable[Response]]


@dataclass
class WsRoute:
    on_connect: Callable[[WebSocket, Request], Awaitable[None]]
    verify: Callable[[Request], bool] | None = None  # xác thực TRƯỚC handshake


async def _write_response(writer: asyncio.StreamWriter, resp: Response) -> None:
    reason = HTTPStatus(resp.status).phrase
    headers = {"Content-Type": resp.content_type, "Content-Length": str(len(resp.body)), "Connection": "close"}
    headers.update(resp.headers)
    head = f"HTTP/1.1 {resp.status} {reason}\r\n" + "".join(f"{k}: {v}\r\n" for k, v in headers.items()) + "\r\n"
    writer.write(head.encode() + resp.body)
    await writer.drain()
    writer.close()


async def serve(host: str, port: int, http_handler: HttpHandler, ws_routes: dict[str, WsRoute]) -> asyncio.Server:
    async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            head = await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), 10)
        except Exception:
            writer.close()
            return

        lines = head.decode("latin-1").split("\r\n")
        try:
            method, target, _ = lines[0].split(" ", 2)
        except ValueError:
            writer.close()
            return
        headers = {k.strip().lower(): v.strip() for k, v in (l.split(":", 1) for l in lines[1:] if ":" in l)}
        url = urlsplit(target)
        query = {k: v[0] for k, v in parse_qs(url.query).items()}
        req = Request(method, url.path, query, headers)

        # ----- WebSocket upgrade -----
        if headers.get("upgrade", "").lower() == "websocket":
            route = ws_routes.get(url.path)
            key = headers.get("sec-websocket-key")
            if not route or not key:
                return await _write_response(writer, Response(400, b"bad websocket request"))
            if route.verify and not route.verify(req):
                return await _write_response(writer, Response(401, b"unauthorized"))
            writer.write(
                (
                    "HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
                    f"Sec-WebSocket-Accept: {accept_key(key)}\r\n\r\n"
                ).encode()
            )
            await writer.drain()
            ws = WebSocket(reader, writer)
            try:
                await route.on_connect(ws, req)
            finally:
                ws._mark_closed()
            return

        # ----- HTTP thường -----
        length = int(headers.get("content-length", 0) or 0)
        if length > MAX_BODY:
            return await _write_response(writer, Response(413, b"payload too large"))
        if length:
            req.body = await reader.readexactly(length)
        try:
            resp = await http_handler(req)
        except Exception as exc:  # không để 1 request lỗi làm sập server
            print(f"[http] lỗi xử lý {method} {url.path}: {exc!r}")
            resp = Response(500, b"internal error")
        await _write_response(writer, resp)

    return await asyncio.start_server(handle, host, port)
