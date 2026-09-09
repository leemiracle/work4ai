# tinybitcask · Bitcask 存储引擎

> 追加写日志 + 内存 KeyDir，读快写快重启快。参照 **Riak Bitcask**。

## 概述

`tinybitcask` 是 csdiy 毕业项目之一，用最小可运行的代码演示 **Bitcask 存储引擎** 的核心机制。

## 核心概念

- 只追加写（append-only）
- KeyDir 在内存索引
- merge 压缩合并
- Hint File 加速重启

## 代码结构

| 文件 | 行数 | 内容 |
|------|------|------|
| `main.py` | 86 行 | !/usr/bin/env python3 |

## 快速开始

```bash
cd projects/tinybitcask
python3 main.py
```

## 参照真实项目

| tiny | 真实 |
|------|------|
| `tinybitcask` | Riak Bitcask |

---

*本 README 由 gen_readmes.py 生成。代码细节请直接读 main.py。*
