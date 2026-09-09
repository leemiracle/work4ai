# tinypool · 资源池

> 线程池 + 连接池，复用昂贵的资源。参照 **Java ThreadPool / HikariCP**。

## 概述

`tinypool` 是 csdiy 毕业项目之一，用最小可运行的代码演示 **资源池** 的核心机制。

## 核心概念

- 预创建 + 懒加载
- borrow/return 协议
- 空闲超时回收
- 连接池 vs 线程池差异

## 代码结构

| 文件 | 行数 | 内容 |
|------|------|------|
| `main.py` | 64 行 | !/usr/bin/env python3 |

## 快速开始

```bash
cd projects/tinypool
python3 main.py
```

## 参照真实项目

| tiny | 真实 |
|------|------|
| `tinypool` | Java ThreadPool / HikariCP |

---

*本 README 由 gen_readmes.py 生成。代码细节请直接读 main.py。*
