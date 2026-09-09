# tinyhuffman · Huffman 编码

> 频率驱动的最优前缀编码。参照 **Deflate / gzip**。

## 概述

`tinyhuffman` 是 csdiy 毕业项目之一，用最小可运行的代码演示 **Huffman 编码** 的核心机制。

## 核心概念

- 频率统计 → 优先队列
- 构建 Huffman 树
- 编码表生成
- 压缩率 vs 算术编码

## 代码结构

| 文件 | 行数 | 内容 |
|------|------|------|
| `main.py` | 57 行 | !/usr/bin/env python3 |

## 快速开始

```bash
cd projects/tinyhuffman
python3 main.py
```

## 参照真实项目

| tiny | 真实 |
|------|------|
| `tinyhuffman` | Deflate / gzip |

---

*本 README 由 gen_readmes.py 生成。代码细节请直接读 main.py。*
