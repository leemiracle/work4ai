# tinyblob · 大对象存储

> 分桶 + 对象元数据 + 范围读，理解云存储的最小内核。参照 **S3 / Blob storage**。

## 概述

`tinyblob` 是 csdiy 毕业项目之一，用最小可运行的代码演示 **大对象存储** 的核心机制。

## 核心概念

- Bucket/Object 命名
- 元数据（meta）与数据分离
- Range Get 支持部分下载
- 对象不可变性（immutable）

## 代码结构

| 文件 | 行数 | 内容 |
|------|------|------|
| `main.py` | 101 行 | !/usr/bin/env python3 |

## 快速开始

```bash
cd projects/tinyblob
python3 main.py
```

## 参照真实项目

| tiny | 真实 |
|------|------|
| `tinyblob` | S3 / Blob storage |

---

*本 README 由 gen_readmes.py 生成。代码细节请直接读 main.py。*
