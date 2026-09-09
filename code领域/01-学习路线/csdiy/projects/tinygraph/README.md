# tinygraph · 图算法库

> BFS/DFS/Dijkstra/拓扑排序/MST 全套。参照 **NetworkX / Boost Graph**。

## 概述

`tinygraph` 是 csdiy 毕业项目之一，用最小可运行的代码演示 **图算法库** 的核心机制。

## 核心概念

- 邻接表表示
- BFS 用队列
- DFS 用栈/递归
- Dijkstra 用优先队列
- 拓扑排序 = DFS 逆后序
- MST = Kruskal/Patrimoni

## 代码结构

| 文件 | 行数 | 内容 |
|------|------|------|
| `main.py` | 84 行 | !/usr/bin/env python3 |

## 快速开始

```bash
cd projects/tinygraph
python3 main.py
```

## 参照真实项目

| tiny | 真实 |
|------|------|
| `tinygraph` | NetworkX / Boost Graph |

---

*本 README 由 gen_readmes.py 生成。代码细节请直接读 main.py。*
