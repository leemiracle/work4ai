# tinyindex · 索引结构对比

> Hash / Sorted / LSM 三种索引的插入与查询。参照 **PostgreSQL BRIN / InnoDB**。

## 概述

`tinyindex` 是 csdiy 毕业项目之一，用最小可运行的代码演示 **索引结构对比** 的核心机制。

## 核心概念

- Hash Index: O(1) 查找，不支持范围
- Sorted Index: 二分查找，支持范围
- LSM Index: 写入快，查询需合并
- 索引选择性决定性能

## 代码结构

| 文件 | 行数 | 内容 |
|------|------|------|
| `main.py` | 81 行 | !/usr/bin/env python3 |

## 快速开始

```bash
cd projects/tinyindex
python3 main.py
```

## 参照真实项目

| tiny | 真实 |
|------|------|
| `tinyindex` | PostgreSQL BRIN / InnoDB |

---

*本 README 由 gen_readmes.py 生成。代码细节请直接读 main.py。*
