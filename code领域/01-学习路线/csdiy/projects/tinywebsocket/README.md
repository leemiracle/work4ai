# tinywebsocket · WebSocket 协议

> 握手 + 帧编解码，HTTP 升级到双向通信。参照 **RFC 6455 / gorilla/websocket**。

## 概述

`tinywebsocket` 是 csdiy 毕业项目之一，用最小可运行的代码演示 **WebSocket 协议** 的核心机制。

## 核心概念

- HTTP Upgrade 握手
- Sec-WebSocket-Accept 计算（SHA1+Base64）
- 帧格式：FIN/opcode/mask/payload
- 客户端→服务端必须 mask

## 代码结构

| 文件 | 行数 | 内容 |
|------|------|------|
| `main.py` | 77 行 | !/usr/bin/env python3 |

## 快速开始

```bash
cd projects/tinywebsocket
python3 main.py
```

## 参照真实项目

| tiny | 真实 |
|------|------|
| `tinywebsocket` | RFC 6455 / gorilla/websocket |

---

*本 README 由 gen_readmes.py 生成。代码细节请直接读 main.py。*
