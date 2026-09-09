#!/usr/bin/env python3
"""tinywebsocket — 参照 WebSocket RFC 6455 的实现
参照：RFC 6455 / Socket.IO / ws
csdiy 对应：network §二(长连接) + tinyhttpd
核心：HTTP 升级握手 + 帧解析 + 服务端推送"""
import asyncio,base64,hashlib,struct,os

WS_MAGIC="258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

def ws_accept_key(client_key):
    """计算握手 key（参照 RFC 6455 §1.3）"""
    sha=hashlib.sha1((client_key+WS_MAGIC).encode()).digest()
    return base64.b64encode(sha).decode()

def ws_encode_frame(data,opcode=0x1):
    """编码 WebSocket 帧（参照 RFC 6455 §5.2）"""
    if isinstance(data,str): data=data.encode()
    frame=bytearray([0x80|opcode])
    length=len(data)
    if length<126: frame.append(0x80|length)
    elif length<65536: frame.append(0x80|126); frame.extend(struct.pack(">H",length))
    else: frame.append(0x80|127); frame.extend(struct.pack(">Q",length))
    mask=os.urandom(4); frame.extend(mask)
    masked=bytes(data[i]^mask[i%4] for i in range(length))
    frame.extend(masked)
    return bytes(frame)

def ws_decode_frame(reader_data):
    """解码 WebSocket 帧"""
    if len(reader_data)<2: return None,0
    b1,b2=reader_data[0],reader_data[1]
    opcode=b1&0x0F; masked=bool(b2&0x80); length=b2&0x7F
    idx=2
    if length==126: length=struct.unpack(">H",reader_data[idx:idx+2])[0]; idx+=2
    elif length==127: length=struct.unpack(">Q",reader_data[idx:idx+8])[0]; idx+=8
    if masked: mask=reader_data[idx:idx+4]; idx+=4
    payload=reader_data[idx:idx+length]
    if masked: payload=bytes(payload[i]^mask[i%4] for i in range(len(payload)))
    return payload,idx+length

async def handle_ws(reader,writer):
    """处理 WebSocket 连接"""
    # HTTP 升级握手
    headers={}
    while True:
        line=await reader.readline()
        if line in(b"\r\n",b"\n",b""): break
        if b":" in line:
            k,v=line.decode().split(":",1); headers[k.strip().lower()]=v.strip()
    if "upgrade" not in headers.get("upgrade","").lower():
        writer.write(b"HTTP/1.1 400 Bad Request\r\n\r\n"); await writer.drain(); writer.close(); return
    key=headers.get("sec-websocket-key","")
    accept=ws_accept_key(key)
    response=(f"HTTP/1.1 101 Switching Protocols\r\n"
              f"Upgrade: websocket\r\n"
              f"Connection: Upgrade\r\n"
              f"Sec-WebSocket-Accept: {accept}\r\n\r\n")
    writer.write(response.encode()); await writer.drain()
    # WebSocket 通信循环
    while True:
        data=await reader.read(4096)
        if not data: break
        payload,consumed=ws_decode_frame(data)
        if payload:
            print(f"  recv: {payload.decode('utf-8','replace')}")
            reply=ws_encode_frame(f"echo: {payload.decode('utf-8','replace')}")
            writer.write(reply); await writer.drain()
    writer.close()

async def main():
    print("tinywebsocket — WebSocket 服务器（参照 RFC 6455）\n")
    print("  test: websocat ws://localhost:8765")
    print("  or browser: new WebSocket('ws://localhost:8765')")
    server=await asyncio.start_server(handle_ws,"0.0.0.0",8765)
    async with server: await server.serve_forever()

if __name__=="__main__": asyncio.run(main())
