# CS145: Modern Data Systems

> Stanford University（数据系统组，原 CS145 数据库课的全面重构版）
> 课程标语：**「data systems built for the AI era」**（为 AI 时代构建的数据系统）
> Prerequisites: 基本编程 + 一点 SQL；无硬性先修
> Language: SQL 为主，Python/Colab 做项目
> Difficulty: ⭐⭐⭐⭐
> 官网：http://cs145.stanford.edu/ ｜ 案例库：20 个真实系统问题

---

## 📚 课程定位（独特价值）

Stanford 数据库课的**全面现代化重构**。它不再只是「教 SQL + 关系代数」，而是回答一个核心命题：

> **「每一个现代应用——从 ChatGPT 到 Spotify 到 Stripe——背后都是数据系统。学会 5 个核心能力，你就能构建任何新系统。」**

独特价值：

- **从一台机器到一千台机器**的完整谱系：M1 SQL（单机）→ M5 分布式（千台），一条主线贯穿。
- **AI-native 的数据库视角**：直接讲 **AI agent memory**（SQLite/Postgres 当模型记忆）、**text-to-SQL 正确性**、**向量检索（HNSW）**、**KV cache 前缀复用**——这是别的数据库课几乎不碰的。
- **案例驱动**：20 个「五分钟一个问题」的真实案例（Chrome 用 Bloom filter 查恶意 URL、Spotify 用 LSM 吞吐、Stripe 用 ACID 保转账、Netflix 隐私泄漏……）。
- **Postgres + BigQuery 双引擎**：既学 OLTP（Postgres）又学 OLAP（BigQuery 列存）。

> 核心论断（官网）：
> 1. **学会这 5 个能力，你就能构建任何新系统**——正确且可扩展。
> 2. **模型会升级，数据库会扩展，但数据库是承载模型记忆与上下文的核心基础设施。**
> 3. RAM 会遗忘，磁盘会记忆；先一台机器，再多台机器。

---

## 🎯 学习目标

1. 掌握 **5 大核心能力**：SQL、存储、索引、事务、分布式。
2. 能对**十亿级行做到毫秒响应**——理解索引选择与 IO 成本模型。
3. 理解**事务的 ACID** 在分布式下如何变形（2PC、复制延迟）。
4. 能为 **AI agent 设计持久化记忆**（SQLite 局部 / Postgres 全局）。
5. 能评估**向量数据库**（HNSW、LSM）在 RAG 场景的取舍。
6. 能识别**数据隐私/安全/质量**陷阱（SQL 注入、去匿名化、数据漂移）。

---

## 📅 完整模块（官网 M1–M6）

### Module 1: SQL（单机，声明式）
- 关系模型、`SELECT/FROM/WHERE/GROUP BY/JOIN`
- 子查询、窗口函数、CTE
- **text-to-SQL 的正确性**：query ambiguity、unit tests、eval sets
- 引擎：**Postgres** + **BigQuery**

### Module 2: Storage（存储与分页）
- 磁盘页（disk pages）、缓冲池、页面布局
- 行存 vs 列存、压缩（Dremel 模型）
- **Bloom filter**（Chrome 查恶意 URL，不传整表）
- **向量数据库**（[HNSW 案例研究](http://cs145.stanford.edu/Module2-Systems/case-study-vectordb.html)）
- 案例系统：Chrome、Uber

### Module 3: Indexing（索引，十亿行 → 毫秒）
- **B+Tree**、term dictionary、倒排索引
- **LSM tree**（MemTable / SSTable / compaction）——Spotify 吞吐
- 索引选择与 IO 成本模型：把一个查询从 **$550K/年 降到 $400**
- 案例系统：Spotify 搜索、OpenAI、BigQuery 列存

### Module 4: Transactions（事务，all-or-nothing）
- ACID、原子性、**两阶段锁（2PL）**
- 隔离级别、幻读、MVCC
- 案例：一笔 Stripe 扣款 = 4 次写入，要么全成要么全无
- 案例系统：Stripe、GitHub

### Module 5: Distributed（分布式，多机）
- **分片（sharding）**、读副本、复制延迟（ChatGPT 8 亿用户怎么做）
- **两阶段提交（2PC）**、协调者失败
- **Kafka**：append-only log、consumer offsets，万亿消息/天
- **GFS**：用会坏的硬盘搭存储
- 案例系统：Netflix、Kafka、ChatGPT 用户库

### Module 6: Modern Systems（现代系统：phone / agent / server）
- **AI agent 的持久记忆**：SQLite（claude-mem，单机）→ Postgres（多机 × 8 亿）
- **KV cache 前缀复用**：agent 每轮重读长 prompt 的成本优化
- 数据质量、断言、可观测性
- **数据隐私**：Netflix Prize 去匿名化攻击、差分隐私
- **数据安全**：SQL 注入、参数化查询、零信任
- 现代 DB 设计：startup（先单 Postgres）vs big tech

---

## 🧮 核心算法 / 数学

### B+Tree 查询代价
$$\text{IO} \approx \log_F N \quad (F=\text{fanout},\ N=\text{rows})$$
- 10 亿行、fanout 100：$\log_{100} 10^9 = 4.5$ 次磁盘 IO ≈ 毫秒级

### Bloom filter
- $k$ 个哈希、$m$ 位、$n$ 元素：误报率 $p = (1 - e^{-kn/m})^k$
- Chrome 用它先过滤恶意 URL，本地不存整表

### LSM tree 写放大
- 写吞吐高（顺序写）但读需合并多层；compaction 权衡空间/读延迟

### HNSW（Hierarchical Navigable Small World，本项目核心）
- 分层近邻图，顶层稀疏做粗导航，底层稠密做精搜
- 查询复杂度近似 $O(\log N)$，远优于暴力 $O(N)$
- 论文：Malkov & Yashunin（[arXiv:1603.09320](https://arxiv.org/abs/1603.09320)）

### 两阶段提交（2PC）
```
Phase 1 (prepare): coordinator → 所有 participant "能否提交?" → participant 锁资源 + 投票
Phase 2 (commit):   若全 YES → coordinator "commit"; 否则 "abort"
```

### 向量相似度（cosine）
$$\text{sim}(a,b) = \frac{a \cdot b}{\|a\|\,\|b\|}$$

---

## 💻 项目代码

📁 `supplementary/grad_projects.py::cs145_demo`

**实现**（纯 Python，无依赖）：
1. ✅ **极简 SQL 引擎 `SimpleSQL`**：`create_table / select_where / join / group_by_count`
2. ✅ **简化版 HNSW 向量索引 `SimpleHNSW`**：贪心图搜索 + cosine 相似度
3. ✅ 端到端 demo：users/orders 表 JOIN + 20 个随机向量建 HNSW 索引检索 top-3

### 运行
```bash
cd stanford-cs-projects
python3 supplementary/grad_projects.py       # 跑全部 demo（含 cs145）
python3 -c "from supplementary.grad_projects import cs145_demo; cs145_demo()"
```

**输出示例**：
```
📋 CS145: SQL + Vector DB
   SF 用户: [{'id':1,'name':'Alice',...},{'id':3,'name':'Carol',...}]
   JOIN users + orders:
     Alice: $50
     Alice: $30
     Bob: $100
   年龄分布: {25: 2, 30: 1}
   HNSW 检索 (k=3): 相似度 ['0.982', '0.934', '0.871']
```

### 代码与课程的对应关系

| 课程模块 | 代码位置 |
|----------|----------|
| M1 SQL（SELECT/WHERE/JOIN/GROUP BY） | `SimpleSQL` 三个方法 |
| M3 HNSW 向量索引 | `SimpleHNSW.add / search` |
| M3 cosine 相似度 | `SimpleHNSW._cosine` |
| M2 贪心图导航（HNSW 核心） | `search` 中 `improved` 贪心循环 |
| M5 分布式前奏（可扩展点） | 把 `SimpleHNSW` 分片成多图即 sharding |

> 注：本项目演示「SQL + 向量」双核；课程正式项目（[projects 页](http://cs145.stanford.edu/projects/projects.html)）要求在 **Colab + 真实 Postgres/BigQuery** 上做，并实现完整 B+Tree 插入与 nanoDB 存储引擎（M3 的 nanoDB 模块）。

---

## 📊 关键论文（按 P0/P1/P2 分级）

### 🔴 P0（必读，奠基）
1. **Codd 1970** "A Relational Model of Data for Large Shared Data Banks" — 关系模型起源
2. **Ghemawat, Gobioff & Leung 2003** "The Google File System" — GFS，分布式存储奠基（案例 M5）
3. **Dean & Ghemawat 2004** "MapReduce: Simplified Data Processing on Large Clusters"
4. **Chang et al. 2007** "Bigtable: A Distributed Storage System for Structured Data"
5. **Malkov & Yashunin 2016/2018** "Efficient and robust approximate nearest neighbor search using HNSW"（[arXiv:1603.09320](https://arxiv.org/abs/1603.09320)）— 本项目 HNSW 直接来源

### 🟡 P1（重要系统）
6. **Mellnikov et al. 2020** "Dremel: Interactive Analysis of Web-Scale Datasets"（列存 + BigQuery）
7. **O'Neil et al. 1996** "The Log-Structured Merge-Tree" — LSM（Spotify 案例）
8. **Bloom 1970** "Space/Time Trade-offs in Hash Coding" — Bloom filter（Chrome 案例）
9. **Lamport 1998** "The Part-Time Parliament" — Paxos（分布式一致性）
10. **Gray & Reuter 1993** *Transaction Processing* — ACID 圣经

### 🟢 P2（AI 时代 + 拓展）
11. **Kreuzberger, Kühl & Hirschl 2023** "Machine Learning Operations (MLOps)" — 数据→模型管道
12. **Narayanan et al. 2020** "DiskANN" — 磁盘向量索引（[arXiv:1905.09797](https://arxiv.org/abs/1905.09797)）
13. **Johnson, Douze & Jégou 2019** "Billion-scale similarity search with GPUs" — FAISS（[arXiv:1702.08734](https://arxiv.org/abs/1702.08734)）
14. **Narayanan 2020** Kafka / append-only log 工业实践
15. **Dinur & Nissim 2008** / **Netflix Prize 去匿名化** — 差分隐私动机

---

## 🎯 学习路径（按角色）

| 角色 | 推荐路线 |
|------|----------|
| **后端/全栈工程师** | M1→M2→M4（SQL + 存储 + 事务）→ LeetCode SQL screen |
| **数据/AI 工程师** | M1→M3（索引）→ 向量库 + RAG 实战 |
| **系统/AI infra** | 全 M1–M5 → M6（agent memory / KV cache）→ 读 FAISS/DiskANN |
| **面试系统设计** | 走官网 [paths.html](http://cs145.stanford.edu/paths.html) 的 systems interview 路线 |
| **创业选型** | M6 的 [db-design-startup](http://cs145.stanford.edu/Module6-Data-Systems/db-design-startup.html)：先单 Postgres，别急着分片 |

### 课程的 20 个真实问题（精选）
- **#3** Agent 每次会话都失忆，存什么让它记住？（SQLite + BM25 + 向量）
- **#4** 十亿向量里找最近邻，不做十亿次比较怎么做？（HNSW）← 本项目
- **#5** Agent 每轮重读长 prompt，怎么不付钱？（KV cache 前缀复用）
- **#7** 一个查询从 $550K/年 降到 $400，靠什么？（索引选择）
- **#11** 一次 Stripe 扣款 = 4 次写入，怎么 all-or-none？（ACID + 2PL）
- **#17** Netflix「匿名」评分怎么被还原出真名？（去匿名化）

---

## 💡 反思与批判

1. **「SQL 已死」是误读**：课程反复强调 SQL 是 LLM 与数据库的唯一接口——text-to-SQL 让 SQL 比以往更关键。但 **query ambiguity** 是真问题，LLM 生成的 SQL 需要 eval sets 与单元测试守护，否则就是「看似能跑」的灾难。
2. **向量库的过度营销**：HNSW 在百万级好用，但十亿级必须上 DiskANN/IVF-PQ 等磁盘方案；很多 RAG demo 的「向量库」其实是暴力搜索套壳。本项目用贪心 HNSW 演示思想，真实生产要处理图的内存压力。
3. **分片崇拜要警惕**：课程点出「**你该分片的时间比想象的晚**」——先单机 Postgres + 副本能撑很久，过早分片是把复杂度提前买进。这是对创业圈「日活一万就上微服务」的有力反驳。
4. **2PC 的现实困境**：协调者单点 + 阻塞，工业界更爱 **Saga / 最终一致**。课程讲 2PC 是为了概念完整，但真实支付系统多用补偿事务。
5. **隐私章偏薄**：Netflix Prize 案例讲得精彩，但差分隐私只点到为止；在医疗（CS286）和 GDPR 场景，这是必修课。
6. **AI agent memory 章是亮点也是软肋**：观点领先（DB = 模型记忆），但实操生态（claude-mem 等）还不成熟，课程内容迭代快，明年可能大改。

---

## 🚀 扩展阅读

完成后推荐：
1. **CS341** Project in Data Systems / **CS347** Parallel and Distributed Systems
2. **CMU 15-445** Database Systems（Andy Pavlo，存储引擎 + 查询优化更深）
3. **DDIA** *Designing Data-Intensive Applications*（Kleppmann）—— 工业圣经，与本课完美互补
4. **CS286** + **medical_rag.py**：把向量检索用到医疗 RAG
5. 向量库深读：FAISS（[arXiv:1702.08734](https://arxiv.org/abs/1702.08734)）、DiskANN（[arXiv:1905.09797](https://arxiv.org/abs/1905.09797)）
6. 工业实战：Stripe / OpenAI / Spotify 的工程博客（课程案例的真实出处）

---

**对应代码**：`supplementary/grad_projects.py::cs145_demo`（SQL 引擎 + HNSW 向量索引）
