# tinyicmp · ICMP 协议

> echo request/reply + checksum。参照 **ping / traceroute**。

## 概述

`tinyicmp` 是 csdiy 毕业项目之一，用最小可运行的代码演示 **ICMP 协议** 的核心机制。

## 核心概念

- Type/Code 字段
- 校验和（一补码求和）
- Ping 往返时延测量
- Traceroute 用 TTL 递增

## 代码结构

| 文件 | 行数 | 内容 |
|------|------|------|
| `main.py` | 55 行 | !/usr/bin/env python3 |

## 快速开始

```bash
cd projects/tinyicmp
python3 main.py
```

## 参照真实项目

| tiny | 真实 |
|------|------|
| `tinyicmp` | ping / traceroute |

---

*本 README 由 gen_readmes.py 生成。代码细节请直接读 main.py。*
