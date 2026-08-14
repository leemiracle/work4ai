# 数据库系统四校整合 · CMU 15-445 × MIT 6.830 × UCB CS186 × Stanford CS145

> 一个主题，四种讲法，互为补全。把"如何实现 / 核心抽象 / 如何使用 / 分布式"四视角打通，
> 4 周速成数据库系统能力。

---

## 🎯 为什么整合这四门课？

每所名校的 DB 课只讲一个面，整合起来才是完整能力：

| 学校 | 课程 | 教授 | 一句话定位 | 学完能力 |
|---|---|---|---|---|
| **CMU** | 15-445 | Andy Pavlo | 教你**如何实现一个 DB** | 能从零写一个单机 DB |
| **MIT** | 6.830 | Robert Morris | 教你 DB 的**核心抽象** | 能讨论 isolation level 的微妙差别 |
| **UCB** | CS186 | — | 教你**如何使用 DB** | 能写好 SQL、调好索引、设计 schema |
| **Stanford** | CS145 | — | 教你 **NoSQL / Big Data** | 能选对存储引擎、搭大数据管线 |

> **核心洞察**：CMU 给你"手"（能造），MIT 给你"脑"（能辩），UCB 给你"脚"（能用），Stanford 给你"眼"（能选）。

---

## 📐 教学法差异（同题不同解）

| 主题 | CMU（实现） | MIT（抽象） | UCB（实战） | Stanford（分布） |
|---|---|---|---|---|
| **索引** | B+tree 叶子链表 | B-tree 高度分析 h≤logₜN | 选择度 + EXPLAIN | LSM-tree 写优化 |
| **事务** | MVCC 版本链实现 | 可串行化冲突图理论 | 隔离级别 4 级实战 | CAP + quorum 最终一致 |
| **查询** | 三种 join + I/O 统计 | Selinger DP 优化器 | SQL 调优 / 谓词下推 | MapReduce 分布式 shuffle |
| **恢复** | WAL + 检查点 | ARIES 三阶段 | 备份策略 | ER 编码 |

---

## 🔴 三个必懂的"反直觉"点

这些是面试/实战中最容易踩坑的，本整合文件用**真实数据**让你看清：

1. **"性别"列建索引没用** — 选择度 sel=50%，回表 50 万次**随机 I/O**（比顺序扫慢 4x）反而更慢，优化器会无视这个索引直接全表扫描。
2. **三种 join 差 187 倍** — 500×300 的连接：nested-loop = 150,000 次 I/O，hash join = 800 次。**这就是查询优化器存在的全部意义。**
3. **B-tree 扁得反直觉** — t=50 时，**10 亿个键只需 h≈5.3 层**！6 次磁盘 I/O 找到任意键。本质是"用胖节点匹配磁盘页"。

---

## 🚀 快速开始

```bash
cd database-systems
python3 db_integration.py
```

**输出包含 5 部分**（约 2 分钟读完）：
- **Part 0** · 数据库思想史（Codd 1970 → Stonebraker → NoSQL → 向量库）
- **Part 1** · 索引四视角对比（B+tree / 高度 / 选择度 / LSM）
- **Part 2** · 事务四视角对比（MVCC / 可串行化 / 隔离级 / CAP）
- **Part 3** · 查询四视角对比（三种 join / Selinger / SQL 调优 / MapReduce）
- **Part 4** · 能力地图 + 4 周学习路径

零依赖，纯 Python 标准库。

---

## 📅 4 周速成学习路径

| 周 | 课程 | 做什么 | 产出 |
|---|---|---|---|
| **W1** | UCB CS186 | SQL + 索引调优，跑 5 个 Postgres/Spark proj | 能读懂 EXPLAIN、写出不慢的 SQL |
| **W2** | CMU 15-445 | bus-tub Project 1(buffer pool) + 2(B+tree) | 手写过页面置换和 B+树 |
| **W3** | MIT 6.830 | 读 3 篇经典论文：ARIES / 2PL / Selinger | 能论证一个调度是否可串行化 |
| **W4** | Stanford CS145 | MapReduce + CAP，理解 Dynamo/Spanner | 能为业务选对存储（SQL/NoSQL/NewSQL） |

> **顺序原理**：先"用"（W1 立刻有产出）→ 再"造"（W2 理解内部）→ 再"辩"（W3 理论深度）→ 最后"选"（W4 全局视野）。

---

## 🔗 衔接 work4ai 现有项目

本目录是**跨校整合层**（讲对比 + 补缺失视角），深度实现见各校目录：

| 想深入 | 去这里 |
|---|---|
| CMU 完整 B+tree / 三种 join / MVCC | `../cmu-cs-projects/topic3-database/dbms.py` |
| MIT 完整 B-tree / ARIES / 死锁检测 / Selinger | `../mit-cs-projects/topic6-db/database.py` |
| Berkeley 数据科学（DataFrame/SQL-like） | `../berkeley-cs-projects/topic11-data/data_science.py` |
| 本整合（四视角对比 + 思想史） | `db_integration.py`（本目录）|

---

## 📚 核心论文与教材

| 年份 | 文献 | 对应视角 |
|---|---|---|
| 1970 | Codd《A Relational Model of Data》CMU/MIT 理论根基 | 全部 |
| 1972 | Bayer & McCreight《B-tree》| CMU/MIT 索引 |
| 1979 | Selinger《Access Path Selection》| MIT 优化器 |
| 1992 | Mohan《ARIES》ACM TODS | MIT 恢复 |
| 2003 | Stonebraker《One size fits all?》| Stanford NoSQL 起源 |
| 2007 | Amazon《Dynamo》| Stanford CAP |
| 2012 | Google《Spanner》| Stanford NewSQL |

---

## 💡 这套整合的"教学宪法"

每个主题都遵循 **直觉 → 数学 → 代码 → 反直觉** 四层：

1. **直觉**：一句话比喻（B+tree 叶子链表 = 书的目录页码连号）
2. **数学**：关键公式（h ≤ logₜN；hash join I/O = O(|R|+|S|)）
3. **代码**：可运行的最小实现（本文件全部能跑）
4. **反直觉**：用真实数据打破常识（性别索引没用、join 差 187 倍）

> 因为"反直觉点"才是真正区分"背过"和"懂了"的分水岭。
