# tiny2pc · 两阶段提交

> 分布式事务：prepare→commit/abort，含 Saga 补偿。参照 **XA / Google Percolator**。

## 概述

`tiny2pc` 是 csdiy 毕业项目之一，用最小可运行的代码演示 **两阶段提交** 的核心机制。

## 核心概念

- Coordinator/Participant 角色
- Prepare 阶段写日志
- Commit/Abort 全员一致
- Saga 用补偿事务替代回滚

## 代码结构

| 文件 | 行数 | 内容 |
|------|------|------|
| `main.py` | 94 行 | !/usr/bin/env python3 |

## 快速开始

```bash
cd projects/tiny2pc
python3 main.py
```

## 参照真实项目

| tiny | 真实 |
|------|------|
| `tiny2pc` | XA / Google Percolator |

---

*本 README 由 gen_readmes.py 生成。代码细节请直接读 main.py。*
