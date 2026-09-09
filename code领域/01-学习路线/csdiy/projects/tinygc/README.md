# tinygc · 垃圾回收器

> 标记-清除算法，根集 + 可达性分析。参照 **Go G1 / Java G1 / Python gc**。

## 概述

`tinygc` 是 csdiy 毕业项目之一，用最小可运行的代码演示 **垃圾回收器** 的核心机制。

## 核心概念

- Root Set（根集）
- 可达性分析（Tracing）
- Mark-Sweep 三色标记
- 内存泄漏 = 漏标

## 代码结构

| 文件 | 行数 | 内容 |
|------|------|------|
| `main.py` | 95 行 | !/usr/bin/env python3 |

## 快速开始

```bash
cd projects/tinygc
python3 main.py
```

## 参照真实项目

| tiny | 真实 |
|------|------|
| `tinygc` | Go G1 / Java G1 / Python gc |

---

*本 README 由 gen_readmes.py 生成。代码细节请直接读 main.py。*
