# tinyeventloop · 事件循环

> call_later/call_soon/register_io 的最小事件循环。参照 **libuv / Redis ae / Python asyncio**。

## 概述

`tinyeventloop` 是 csdiy 毕业项目之一，用最小可运行的代码演示 **事件循环** 的核心机制。

## 核心概念

- Ready Queue + Timer Heap
- IO 多路复用（select/poll/epoll）
- 回调式 vs 协程式
- run_once 单次心跳

## 代码结构

| 文件 | 行数 | 内容 |
|------|------|------|
| `main.py` | 65 行 | !/usr/bin/env python3 |

## 快速开始

```bash
cd projects/tinyeventloop
python3 main.py
```

## 参照真实项目

| tiny | 真实 |
|------|------|
| `tinyeventloop` | libuv / Redis ae / Python asyncio |

---

*本 README 由 gen_readmes.py 生成。代码细节请直接读 main.py。*
