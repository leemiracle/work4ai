# tinyseq · 序列号生成器

> 分布式唯一 ID：Snowflake(机器+时间+序号) + ULID。参照 **Twitter Snowflake / ULID**。

## 概述

`tinyseq` 是 csdiy 毕业项目之一，用最小可运行的代码演示 **序列号生成器** 的核心机制。

## 核心概念

- Snowflake: timestamp(41)+worker(10)+seq(12)
- 时钟回拨问题
- ULID: 时间+随机，字典序可排序
- ID 生成必须无中心

## 代码结构

| 文件 | 行数 | 内容 |
|------|------|------|
| `main.py` | 75 行 | !/usr/bin/env python3 |

## 快速开始

```bash
cd projects/tinyseq
python3 main.py
```

## 参照真实项目

| tiny | 真实 |
|------|------|
| `tinyseq` | Twitter Snowflake / ULID |

---

*本 README 由 gen_readmes.py 生成。代码细节请直接读 main.py。*
