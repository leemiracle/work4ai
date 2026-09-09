# tinyroute · 路由表

> 最长前缀匹配 + 路由聚合。参照 **Linux FIB / quagga / BIRD**。

## 概述

`tinyroute` 是 csdiy 毕业项目之一，用最小可运行的代码演示 **路由表** 的核心机制。

## 核心概念

- CIDR 前缀匹配
- 最长前缀优先
- 默认路由 0.0.0.0/0
- 路由聚合减小表规模

## 代码结构

| 文件 | 行数 | 内容 |
|------|------|------|
| `main.py` | 47 行 | !/usr/bin/env python3 |

## 快速开始

```bash
cd projects/tinyroute
python3 main.py
```

## 参照真实项目

| tiny | 真实 |
|------|------|
| `tinyroute` | Linux FIB / quagga / BIRD |

---

*本 README 由 gen_readmes.py 生成。代码细节请直接读 main.py。*
