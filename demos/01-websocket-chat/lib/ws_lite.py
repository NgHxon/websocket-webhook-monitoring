"""
ws_lite.py — WebSocket tối giản theo RFC 6455, chỉ dùng thư viện chuẩn (asyncio).

Mục đích học tập: tự cài đặt để hiểu WebSocket hoạt động thế nào:
  1. Handshake : HTTP Upgrade -> 101 Switching Protocols (Sec-WebSocket-Accept)
  2. Framing   : FIN | opcode | MASK | payload length (7/16/64 bit) | masking key | payload
  3. Control   : ping (0x9) / pong (0xA) / close (0x8)

File này có cả phía SERVER (accept_key, WebSocket) lẫn CLIENT (connect).
Dự án thật nên dùng thư viện đã kiểm chứng: `websockets`, FastAPI/Starlette, Socket.IO...
"""
from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import os
import struct
from urllib.parse import urlsplit

WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"  # hằng số do RFC 6455 quy định
MAX_PAYLOAD = 1024 * 1024  # 1 MB

OP_CONT, OP_TEXT, OP_BINARY, OP_CLOSE, OP_PING, OP_PONG = 0x0, 0x1, 0x2, 0x8, 0x9, 0xA


def accept_key(client_key: str) -> str:
    """Sec-WebSocket-Accept = base64(SHA1(key + GUID))"""
    digest = hashlib.sha1((client_key + WS_GUID).encode()).digest()
    return base64.b64encode(digest).decode()


class ConnectionClosed(Exception):
    pass


class WebSocket:
    """Một kết nối WebSocket đã handshake xong. Dùng chung cho server và client."""

    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, *, is_client: bool = False):
        self.reader = reader
        self.writer = writer
        self.is_client = is_client  # client -> server phải MASK, server -> client không mask
        self.closed = False
        self.alive = True  # dùng cho heartbeat
        self.state: dict = {}  # nơi gắn thông tin tùy ý (vd: agent_id)

    # ---------------- Gửi ----------------
    async def _send_frame(self, opcode: int, payload: bytes) -> None:
        if self.closed:
            return
        header = bytearray([0x80 | opcode])  # FIN = 1
        mask_bit = 0x80 if self.is_client else 0
        n = len(payload)
        if n < 126:
            header.append(mask_bit | n)
        elif n < 65536:
            header.append(mask_bit | 126)
            header += struct.pack("!H", n)
        else:
            header.append(mask_bit | 127)
            header += struct.pack("!Q", n)
        if self.is_client:
            mask = os.urandom(4)
            header += mask
            payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        try:
            self.writer.write(bytes(header) + payload)
            await self.writer.drain()
        except (ConnectionError, RuntimeError):
            self._mark_closed()

    async def send(self, data: str | bytes) -> None:
        if isinstance(data, str):
            await self._send_frame(OP_TEXT, data.encode())
        else:
            await self._send_frame(OP_BINARY, data)

    async def send_json(self, obj) -> None:
        await self.send(json.dumps(obj, ensure_ascii=False))

    async def ping(self) -> None:
        await self._send_frame(OP_PING, b"")

    async def close(self, code: int = 1000, reason: str = "") -> None:
        await self._send_frame(OP_CLOSE, struct.pack("!H", code) + reason.encode())
        self._mark_closed()

    def _mark_closed(self) -> None:
        if not self.closed:
            self.closed = True
            try:
                self.writer.close()
            except Exception:
                pass

    # ---------------- Nhận ----------------
    async def _read_frame(self) -> tuple[bool, int, bytes]:
        b0, b1 = await self.reader.readexactly(2)
        fin = bool(b0 & 0x80)
        opcode = b0 & 0x0F
        masked = bool(b1 & 0x80)
        length = b1 & 0x7F
        if length == 126:
            (length,) = struct.unpack("!H", await self.reader.readexactly(2))
        elif length == 127:
            (length,) = struct.unpack("!Q", await self.reader.readexactly(8))

        if not self.is_client and not masked:
            # RFC 6455 §5.1: frame client gửi lên BẮT BUỘC mask
            await self.close(1002, "client frames must be masked")
            raise ConnectionClosed()
        if length > MAX_PAYLOAD:
            await self.close(1009, "message too big")
            raise ConnectionClosed()

        mask = await self.reader.readexactly(4) if masked else None
        payload = await self.reader.readexactly(length)
        if mask:
            payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        return fin, opcode, payload

    async def recv(self) -> str | bytes:
        """Chờ 1 message hoàn chỉnh. Tự xử lý ping/pong/close. Hết kết nối -> ConnectionClosed."""
        fragments: list[bytes] = []
        msg_opcode = OP_TEXT
        while True:
            try:
                fin, opcode, payload = await self._read_frame()
            except (asyncio.IncompleteReadError, ConnectionError, OSError):
                self._mark_closed()
                raise ConnectionClosed()

            self.alive = True  # nhận được bất kỳ frame nào = còn sống
            if opcode == OP_PING:
                await self._send_frame(OP_PONG, payload)
            elif opcode == OP_PONG:
                pass
            elif opcode == OP_CLOSE:
                await self._send_frame(OP_CLOSE, payload[:2])
                self._mark_closed()
                raise ConnectionClosed()
            elif opcode in (OP_TEXT, OP_BINARY, OP_CONT):
                if opcode != OP_CONT:
                    msg_opcode = opcode
                fragments.append(payload)
                if fin:  # message có thể bị chia nhiều frame
                    data = b"".join(fragments)
                    return data.decode() if msg_opcode == OP_TEXT else data
            else:
                await self.close(1002, "unknown opcode")
                raise ConnectionClosed()

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return await self.recv()
        except ConnectionClosed:
            raise StopAsyncIteration


async def heartbeat(get_connections, interval: float = 15.0) -> None:
    """Ping định kỳ; lần trước không thấy phản hồi -> coi như kết nối đã chết (half-open)."""
    while True:
        await asyncio.sleep(interval)
        for ws in list(get_connections()):
            if not ws.alive:
                ws._mark_closed()
                continue
            ws.alive = False
            await ws.ping()


async def connect(url: str, timeout: float = 5.0) -> WebSocket:
    """Client: mở kết nối tới ws://host:port/path?query"""
    parts = urlsplit(url)
    if parts.scheme != "ws":
        raise ValueError("ws_lite chỉ hỗ trợ ws:// (wss:// cần thêm TLS)")
    host, port = parts.hostname, parts.port or 80
    path = parts.path or "/"
    if parts.query:
        path += "?" + parts.query

    reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout)
    key = base64.b64encode(os.urandom(16)).decode()
    request = (
        f"GET {path} HTTP/1.1\r\nHost: {host}:{port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n"
    )
    writer.write(request.encode())
    await writer.drain()

    head = await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), timeout)
    lines = head.decode().split("\r\n")
    status = lines[0]
    headers = {k.strip().lower(): v.strip() for k, v in (l.split(":", 1) for l in lines[1:] if ":" in l)}
    if " 101 " not in status:
        writer.close()
        raise ConnectionError(f"Handshake bị từ chối: {status}")
    if headers.get("sec-websocket-accept") != accept_key(key):
        writer.close()
        raise ConnectionError("Sec-WebSocket-Accept không khớp")
    return WebSocket(reader, writer, is_client=True)
