# csdiy 主题分类总览（TOPICS）

> 按 **16 个学科主题 × 6 类资源形态** 的交叉索引。
> 与 [INDEX.md](INDEX.md) 互补：INDEX 按「我想干什么」组织，TOPICS 按「学科主题」组织。
>
> 生成时间：2026-07-07。由实际文件系统扫描得出（不再凭文档声称）。

---

## 📊 全景统计（实测）

| 资源形态 | 数量 | 总规模 | 状态 |
|---------|------|--------|------|
| NOTES 程序员视角精读 | **7 篇** | ~4,050 行 | ✅ 经典系列 |
| NOTES 课程地图解析 🆕 | **6 篇** | ~3,691 行 | ✅ 覆盖 csdiy.wiki 全课程 |
| CHEATSHEETS 场景速查 | 11 篇 | 2,455 行 | ✅ |
| SOURCE-READING 源码精读 | **59 篇** | ~14,435 行 | ⚠️ 旧文档只引 19 篇 |
| LABS 实验指南 | 4 篇 | 904 行 | ✅ |
| CARDS 实战卡片 | 60 张 | 639 行 + anki.tsv | ✅ |
| PATHS 学习路径 | 5 条 | — | ✅ |
| PROJECTS 毕业项目 | **68 个** | **14,681 行 py** | ✅ 100% README 覆盖 |
| TOOLS 工具 | **10 个** | — | ✅ |
| 原始资料 | 15.68 GB | 48,791 文件 | ✅ |
| FTS 索引 | — | 28,452 文档 / 896MB | ✅ |

---

## 🗺️ 三层架构图

```
原始资料层 (15GB, 输入)        精加工层 (转化)                 应用层 (输出)
├─ cs-self-learning/ (主仓)    ├─ notes/       8 篇精读         ├─ tools/      9 个 Python 工具
├─ website/       (270 页)    ├─ cheatsheets/ 11 篇速查         ├─ csdiy.py    统一 CLI
├─ books/         (5 本)      ├─ source-reading/ 59 篇源码精读  ├─ index/      FTS5 (896MB)
└─ github-repos/  (102 仓)    ├─ labs/        4 篇实验指南      ├─ graph/      知识图谱 (156 节点)
                               ├─ cards/       60 张实战卡      ├─ manifest/   资源清单
                               └─ projects/    68 个 tiny* 项目 └─ paths/      5 条学习路径
```

---

## 一、16 个学科主题交叉索引

每个主题下分：**原始资料** / **精读笔记** / **源码精读** / **速查** / **Lab** / **毕业项目**

> 🆕 **新加：课程地图解析系列**（6 篇）覆盖 csdiy.wiki 全课程，在每个相关主题下列出。

---

### 1️⃣ 计算机入门 / 编程基础

| 类别 | 资源 |
|------|------|
| 原始资料 | `github-repos/PKUFlyingPig/CS61A` `CS61B` `CS61C-summer20` · `third-party/CS50x` `CS50P` `CS61A-Assignments` `CS61A/B/C-PathwayToSuccess` `CS61C-Assignment` `CS61C_2024_Fall` · `references/Starter-Guide` `self-taught-CS` `cs-video-courses` |
| 精读 | `notes/csapp-程序员视角.md`（Ch2-3 入门部分） |
| 速查 | `cheatsheets/python-场景速查.md`（虚拟环境/调试/打包） |
| 毕业项目 | `tinyjson` (385 行) · `tinycompress` (162 行) |

---

### 2️⃣ 数学基础（线代 / 概率 / 离散）

| 类别 | 资源 |
|------|------|
| 原始资料 | `github-repos/PKUFlyingPig/UCB-CS70` (离散) `EE16A` `MIT18.330` `Standford_CVX101` · `books/Probabilistic_Robotics.pdf` |
| **课程地图解析** 🆕 | **`notes/csdiy-math-complete.md` (1594 行)** — MIT/3B1B 数学课程逐 session 解析 |
| 学习路径 | `paths/ai.md`（线代→概率→ML，60 周） |
| 源码精读 | `source-reading/backprop-graph-精读.md`（链式法则） `vae-math-精读.md` `mamba-ssm-math-精读.md` |

---

### 3️⃣ 数据结构与算法

| 类别 | 资源 |
|------|------|
| 原始资料 | `github-repos/PKUFlyingPig/UCB-CS170` `CS161` `Princeton-Algorithm` · `references/CS-Notes` |
| 学习路径 | `paths/theory.md`（算法/理论 CS，46 周） |
| 源码精读 | `bloom-filter` `consistent-hashing` `hnsw-algorithm` |
| 速查 | `cheatsheets/regex-场景速查.md`（348 行，回溯灾难/引擎差异） |
| 毕业项目 | `tinyhash` (91) · `tinyhuffman` (57) · `tinygraph` (84) · `tinyring` (69) · `tinyregex` (298) · `tinyindex` (81) |

---

### 4️⃣ 操作系统 / 系统底层 ⭐核心

| 类别 | 资源 |
|------|------|
| 原始资料 | `github-repos/PKUFlyingPig/MIT6.S081-2020fall` (xv6) · `third-party/UCB_CS162_2025Fall` (Pintos) `Linux0.11` · `references/REKCARC-TSC-UHT` (4.83GB 清华 10 学期) |
| 精读 | **`notes/csapp-程序员视角.md` (569 行)** — CSAPP 9 章逐章救什么命<br>**`notes/os-程序员视角-从bug到原理.md` (628 行)** — OOM/死锁/僵尸/fsync/并发/IO |
| **课程地图解析** 🆕 | **`notes/csdiy-systems-complete.md` (477 行)** — 体系结构+系统基础+OS+并行分布式 12 门课解析 |
| 源码精读 | `go-gmp-scheduler` `rust-ownership` `numa-architecture` `branch-prediction` |
| Lab | **`labs/xv6-6.S081-从零跑起来.md`** (141 行) |
| 速查 | `cheatsheets/gdb调试-场景速查.md` (130 行) |
| 毕业项目 (12 个) | `tinyshell` `tinydocker` `tinygc` `tinyalloc` `tinypool` `tinysched` `tinytrace` `tinytx` `tinymmu` `tinyinterrupt` `tinysignal` `tinyseq` |

---

### 5️⃣ 计算机网络 ⭐核心

| 类别 | 资源 |
|------|------|
| 原始资料 | `github-repos/PKUFlyingPig/CS144-Computer-Network` `Computer-Network-A-Top-Down-Approach` · `books/Computer_Networking_A_Top_Down_Approach_7th.pdf` |
| 精读 | **`notes/network-程序员视角-从抓包到原理.md`** — RST/epoll/粘包/CLOSE_WAIT/Nagle/TLS |
| 源码精读 | `linux-epoll-kernel` `linux-tcp-state-machine` `nginx-http-parser` `eventloop-evolution-redis-nginx-go` `frp-tcp-proxy-核心设计拆解` |
| Lab | **`labs/cs144-网络-从零跑起来.md` (488 行)** — Lab0-6 全流程 |
| 毕业项目 (14 个) | `tinyproxy` (771) `tinyhttpd` `tinydns` (339) `tinydhcp` `tinyicmp` `tinyarp` `tinyroute` `tinyratelimit` `tinywebsocket` `tinytls` `tinypipe` `tinystream` `tinyeventloop` `tinybus` |

---

### 6️⃣ 数据库系统 ⭐核心

| 类别 | 资源 |
|------|------|
| 原始资料 | `github-repos/PKUFlyingPig/CS186` · `third-party/bustub` (CMU 15-445) `noisepage-pilot` · `github-repos/ddia` (DDIA 中文版) · `books/Architecture_of_a_Database_System.pdf` |
| 精读 | **`notes/db-程序员视角-从慢SQL到原理.md` (550 行)** — 索引/锁/MVCC/连接/WAL |
| 源码精读 | `sqlite-btree-逐行拆解` (613 行) `leveldb-lsm` `storage-engine-comparison` `redis-data-structures` `redis-expiry-policy` |
| Lab | **`labs/bustub-15-445-从零跑起来.md`** (146 行) |
| 速查 | `cheatsheets/postgres-场景速查.md` (345 行) |
| 毕业项目 (9 个) | `tinydb` (900) `tinycache` (895) `tinybitcask` `tinyblob` `tinysql` `tinywal` `tinyfs` `tinyindex` `tinycachesim` |

---

### 7️⃣ 分布式系统

| 类别 | 资源 |
|------|------|
| 原始资料 | `github-repos/PKUFlyingPig/MIT6.824` · `third-party/MIT6.824-2021` |
| 源码精读 | `raft-vs-paxos-精读.md` |
| Lab | **`labs/mit6.824-raft-从零跑起来.md`** (129 行) |
| 毕业项目 (8 个) | `tinyraft` (176) `tinykafka` (211) `tiny2pc` `tinymapreduce` `tinygossip` `tinyring` `tinymesi` `tinyclock` |

---

### 8️⃣ 编译原理 / 编程语言设计

| 类别 | 资源 |
|------|------|
| 原始资料 | `github-repos/third-party/CS143-Compilers-Stanford` · `github-repos/craftinginterpreters_zh` · `github-repos/PKUFlyingPig/CS106L` `CS110L` `MIT6.031-software-construction` |
| 毕业项目 (6 个) | `tinycompiler` (392) `tinyasm` (199) `tinyregex` (298) `tinyjson` (385) `tinylinker` (142) `tinysymtab` (59) |

---

### 9️⃣ 软件工程 / 编程实践

| 类别 | 资源 |
|------|------|
| 原始资料 | `github-repos/PKUFlyingPig/CS169-Software-Engineering` `MIT6.1600` · `references/build-your-own-x` `project-based-learning` |
| 精读 | **`notes/patterns-程序员视角-真实代码里的模式.md` (508 行)** — 12 模式 + 红线<br>**`notes/code-review-程序员视角.md` (446 行)** — 17 before/after<br>**`notes/perf-程序员视角-定位与优化.md` (408 行)** — 6 案例 + 火焰图 |
| 速查 (9 篇) | `git进阶` `makefile与cmake` `vim生存` `shell实战` `docker速查` `python` `profiling` `k8s` `postgres` |
| 毕业项目 | `tinydebug` (333) · `tinyprof` (188) · `tinymetrics` (97) · `tinygit` (161) · `tinyrpc` (291) |
| 文档 | `CONTRIBUTING.md` — 给 frp/Redis/gnet 提 PR 指南 |

---

### 🔟 计算机体系结构 / 硬件

| 类别 | 资源 |
|------|------|
| 原始资料 | `github-repos/PKUFlyingPig/NandToTetris` (从与非门到俄罗斯方块) · `references/REKCARC-TSC-UHT` (大一数字电路) |
| 精读 | `notes/csapp-程序员视角.md` (Ch4 处理器 / Ch6 存储器层次) |
| 源码精读 | `branch-prediction-精读.md` `numa-architecture-精读.md` |
| 毕业项目 | `tinycpu` (492) · `tinyasm` (199) · `tinyvm` (105) · `tinydma` (117) · `tinymmu` (367) · `tinyinterrupt` (179) |

---

### 1️⃣1️⃣ 机器学习 / 深度学习 ⭐扩展重点

| 类别 | 资源 |
|------|------|
| 原始资料 | `github-repos/PKUFlyingPig/CS229` `CS224n` · `references/micrograd` `nanoGPT` `notebooks` (mlc-ai) · `github-repos/deeplearningbook-chinese` |
| 学习路径 | `paths/ai.md`（数学→DL→论文，60 周） |
| 源码精读 (13 篇) | `micrograd-100行吃透自动微分` (396) `nanoGPT-读懂最小GPT` (480) `backprop-graph` `cnn-convolution` `transformer-attention-deep` `attention-variants` `flash-attention` `position-encoding` `normalization-deep` `dropout-train-infer` `weight-init` `loss-functions` `softmax-temperature` `gradient-vanishing` |
| 毕业项目 | `tinytorch` (929) 🆕 · `tinygen` (420) · `tinyrl` (521) |

---

### 1️⃣2️⃣ 大语言模型（LLM）⭐最大扩展块（22 篇源码精读）

| 类别 | 资源 |
|------|------|
| 原始资料 | `github-repos/references/Awesome-LLM` `LLMSys-PaperList` `nanoGPT` · `third-party/nano-vllm` |
| 源码精读 (22 篇) | **训练侧**：`transformer-training-pipeline` `lr-scheduling` `fine-tuning-landscape` `rlhf-alignment` `prompt-engineering-deep`<br>**推理侧**：`tokenizer-deep` `kv-cache-原理` `kv-cache-compression` `long-context` `inference-optimization` `speculative-decoding` `mixed-precision` `model-compression` `model-parallel` `moe-routing`<br>**部署/评估**：`llm-deployment` `llm-evaluation` `llm-security`<br>**应用**：`rag-advanced` `agent-architecture` `data-pipeline` `data-versioning` |
| 毕业项目 | `tinyllm` (870) 🆕 · `tinyrag` (695) 🆕 |
| 生成模型/SSM/多模态 | `vae-math` `mamba-ssm-math` `multimodal` |

---

### 1️⃣3️⃣ 图形学 / 渲染

| 类别 | 资源 |
|------|------|
| 原始资料 | `books/pbr-official/`（PBR 第4版在线 327 页）· `books/rtr-official/`（RTR 替代方案） |
| 学习路径 | `paths/graphics.md`（光栅/光追/PBR，44 周） |
| 毕业项目 | （暂缺，建议新增 `tinyrender`） |

---

### 1️⃣4️⃣ Web 开发 / 全栈

| 类别 | 资源 |
|------|------|
| 原始资料 | `website/Web开发/` · `github-repos/PKUFlyingPig/CS169-Software-Engineering` |
| 学习路径 | `paths/fullstack.md`（Web 应用独立交付，52 周） |
| 速查 | `cheatsheets/docker速查` `k8s-场景速查` |
| 毕业项目 | `tinyhttpd` (196) · `tinyproxy` (771) · `tinywebsocket` (77) |

---

### 1️⃣5️⃣ 信息安全

| 类别 | 资源 |
|------|------|
| 原始资料 | `website/系统安全/` · `github-repos/third-party/seed-labs` |
| 源码精读 | `source-reading/llm-security-精读.md` |
| 毕业项目 | `tinyencrypt` (219) · `tinyauth` (73) · `tinytls` (84) |

---

### 1️⃣6️⃣ 工具链 / 工程效率（横向能力）

| 类别 | 资源 |
|------|------|
| 原始资料 | `references/the-art-of-command-line` `vim-galore-zh_cn` `How-To-Ask-Questions` `public-apis` `DevOps-Guide` `free-programming-books` |
| 速查 (11 篇全) | `git` `gdb` `docker` `makefile与cmake` `shell实战` `vim生存` `k8s` `postgres` `profiling` `python` `regex` |
| 实战卡片 | `cards/程序员实战卡片.md` (60 张) + `cards/anki.tsv` |
| 工具 | `tools/daily.py`（每日训练）`review.py`（SM-2 间隔重复）`feynman.py`（费曼输出）`ask.py`（RAG） |

---

## 二、横向能力层（贯穿所有主题）

| 层 | 资源 | 作用 |
|----|------|------|
| **检索层** | `tools/build_index.py` + `index/search.sqlite`（896MB FTS5，**28,452 文档**） | 全文检索 |
| **问答层** | `tools/ask.py` + `csdiy.py ask` | RAG 检索+生成 |
| **图谱层** | `tools/build_graph.py` + `graph/graph.mmd`（156 节点 / 162 边） | 课程-概念-先修关系 |
| **清单层** | `tools/build_manifest.py` + `manifest/summary.json` | 资源分类统计 + 去重 |
| **路径层** | `tools/build_paths.py` + `paths/tracks.json` | 5 方向学习路径 |
| **训练层** | `tools/daily.py` `review.py` `feynman.py` | 间隔重复 + 强制输出 |
| **主题查询** 🆕 | `tools/by_topic.py` | 按学科主题 CLI 过滤（17 主题 + 中英别名）|
| **索引增量** 🆕 | `tools/index_append.py` | 不重建索引，只追加自建内容 |
| **统一 CLI** | `csdiy.py` | ask / search / learn / quiz / daily / stats |
| **战略层** | `STRATEGY.md` `ANALYSIS.md` `RESOURCES-INDEX.md` | 元反思 |

---

## 二·补、课程地图解析系列 🆕（覆盖 csdiy.wiki 全课程）

> v2.0 新增的 6 篇文档，把 csdiy.wiki 课程地图的每个学科逐 session 解析。**介于原始资料和程序员视角精读之间**——比上游 mkdocs 细致，比 7 篇 bug-驱动精读系统。

| 文件 | 行数 | 覆盖范围 |
|------|------|---------|
| `notes/csdiy-math-complete.md` | 1594 | 数学（线代/概率/离散/3B1B）|
| `notes/csdiy-programming-complete.md` | 645 | 编程入门（16 门课）|
| `notes/csdiy-core-cs-complete.md` | 392 | 核心 CS（电子基础+DSA+SE，11 门课）|
| `notes/csdiy-systems-complete.md` | 477 | 系统类（体系结构+OS+并行分布式，12 门课）|
| `notes/csdiy-applications-complete.md` | 352 | 应用层（安全+网络+DB，15 门课）|
| `notes/csdiy-electives-complete.md` | 231 | 选修（编译+PL+图形+Web+DS，21 门课）|
| **合计** | **3,691 行** | **覆盖 csdiy.wiki 全部课程** |

---

## 三、按"我想干什么"快速跳转

| 我想... | 跳转 |
|--------|------|
| 调 bug 排查线上 | [INDEX.md §🚨](INDEX.md) |
| 学透一个主题 | 上方 16 主题任选 |
| 精读真实源码 | `source-reading/` 59 篇 |
| 跑通经典 Lab | `labs/` 4 篇 |
| 造一个真实项目 | `projects/` 68 个 tiny* |
| 每天练一手 | `python3 tools/daily.py` |
| 跨主题检索 | `python3 csdiy.py search "<关键词>"` |
| 按主题查询 | `python3 tools/by_topic.py <主题>` 🆕 |

---

## 四、与 RESOURCES-INDEX.md 的关系

| 维度 | TOPICS.md（本文档） | RESOURCES-INDEX.md |
|------|--------------------|--------------------|
| 组织方式 | **学科主题** 交叉分类 | **资源类型** 顺序索引 |
| 粒度 | 每主题列所有相关资源 | 每篇资源给章节摘要 |
| 用途 | 找"想学 X 有哪些资料" | 找"某篇里讲了什么" |

两者互补：先用 TOPICS 定位主题，再用 RESOURCES-INDEX 看具体内容。

---

*本文档由实际文件系统扫描生成，与 [INDEX.md](INDEX.md) / [RESOURCES-INDEX.md](RESOURCES-INDEX.md) / [PROJECTS.md](projects/PROJECTS.md) 保持同步。*
