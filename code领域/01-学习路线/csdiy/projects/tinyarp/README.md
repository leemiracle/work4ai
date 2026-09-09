# tinyarp · ARP 协议实现

> IP→MAC 地址解析，含缓存表 + request/reply。参照 **arpwatch / Linux neigh**。

## 概述

`tinyarp` 是 csdiy 毕业项目之一，用最小可运行的代码演示 **ARP 协议实现** 的核心机制。

## 核心概念

- ARP 缓存表（cache）
- 广播 request / 单播 reply
- 静态表项 vs 动态学习
- 缓存超时

## 代码结构

| 文件 | 行数 | 内容 |
|------|------|------|
| `main.py` | 95 行 | !/usr/bin/env python3 |

## 快速开始

```bash
cd projects/tinyarp
python3 main.py
```

## 参照真实项目

| tiny | 真实 |
|------|------|
| `tinyarp` | arpwatch / Linux neigh |

---

*本 README 由 gen_readmes.py 生成。代码细节请直接读 main.py。*
