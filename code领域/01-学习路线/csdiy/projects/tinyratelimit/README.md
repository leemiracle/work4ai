# tinyratelimit · 限流算法

> 令牌桶 + 滑动窗口 + 漏桶三种限流。参照 **nginx limit_req / Sentinel**。

## 概述

`tinyratelimit` 是 csdiy 毕业项目之一，用最小可运行的代码演示 **限流算法** 的核心机制。

## 核心概念

- Token Bucket: 允许突发
- Sliding Window: 精确计数
- Leaky Bucket: 强制匀速
- 分布式限流需 Redis Lua

## 代码结构

| 文件 | 行数 | 内容 |
|------|------|------|
| `main.py` | 63 行 | !/usr/bin/env python3 |

## 快速开始

```bash
cd projects/tinyratelimit
python3 main.py
```

## 参照真实项目

| tiny | 真实 |
|------|------|
| `tinyratelimit` | nginx limit_req / Sentinel |

---

*本 README 由 gen_readmes.py 生成。代码细节请直接读 main.py。*
