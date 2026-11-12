# 讲透smallpond — 重要文件精讲索引

smallpond 是 DeepSeek 开源的轻量分布式数据处理框架（DuckDB 引擎 + 3FS 存储，GraySort 110.5TiB/30min 纪录）。本目录收录 4 篇重要源码精讲，选自知识图谱 tour 引用与度数排名前列的核心文件。

## 精讲列表

| 篇目 | 原文件 | 一句话定位 |
|---|---|---|
| [01-execution-task.md](01-execution-task.md) | `smallpond/execution/task.py` | 执行引擎心脏：Task 基类与 20+ 任务族、staging 原子提交、DuckDB 连接纪律 |
| [02-logical-node.md](02-logical-node.md) | `smallpond/logical/node.py` | 逻辑算子全集：28 个 Node 类，用户语义到物理计划的 IR |
| [03-io-arrow.md](03-io-arrow.md) | `smallpond/io/arrow.py` | Parquet IO 核心：RowRange 切分、large_string 强转、并行读写 |
| [04-dataframe.md](04-dataframe.md) | `smallpond/dataframe.py` | 用户 API 门面：Session/DataFrame，惰性变换与 SQL 优先策略 |

## 建议阅读顺序

1. **04-dataframe.py**：先从用户视角建立心智模型（一切惰性、一切落盘显式）。
2. **02-logical-node.py**：看每个 API 背后构造什么算子，理解 DAG 与输出路径约定。
3. **01-execution-task.py**：下沉到执行层，理解 Task 生命周期、幂等重试与 DuckDB 调优。
4. **03-io-arrow.py**：最后补 IO 层，理解 RowRange 与 PB 级类型安全。

## 配套资料

- [onboarding/ONBOARDING.md](../onboarding/ONBOARDING.md) — 项目全貌入门
- 上游仓库：~/ai/explore/deepseek-ai/smallpond
