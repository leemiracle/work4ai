# csdiy 程序员实战手册 · 总入口

> 不是又一堆课程罗列，而是**你现在就能用**的程序员视角资料。
> 所有内容均从本仓库 15GB 真实课程资料中提炼，可粘贴、可跑、可查。

## 今天就能用的东西（按你想干什么分类）

### 🚨 我正在调 bug / 排查线上问题
| 你遇到 | 直接打开 |
|--------|---------|
| 服务内存爆了 / OOM | [notes/os-程序员视角 §OOM](notes/os-程序员视角-从bug到原理.md) |
| 程序卡死 / 疑似死锁 | [notes/os-程序员视角 §死锁](notes/os-程序员视角-从bug到原理.md) |
| 僵尸进程一堆 | [notes/os-程序员视角 §僵尸](notes/os-程序员视角-从bug到原理.md) |
| 文件写一半没了 | [notes/os-程序员视角 §丢数据](notes/os-程序员视角-从bug到原理.md) |
| segfault 怎么查 | [cheatsheets/gdb调试](cheatsheets/gdb调试-场景速查.md) |
| 找性能瓶颈 | [notes/csapp-程序员视角 §性能](notes/csapp-程序员视角.md) |

### 🛠️ 我要干活 / 写代码
| 我要干 | 直接打开 |
|--------|---------|
| git 救命（撤回/找回/解冲突） | [cheatsheets/git进阶](cheatsheets/git进阶-场景速查.md) |
| 写 Makefile / CMake | [cheatsheets/makefile与cmake](cheatsheets/makefile与cmake-场景速查.md) |
| vim 高效编辑 | [cheatsheets/vim生存](cheatsheets/vim生存-场景速查.md) |
| shell 批处理/找文件/统计 | [cheatsheets/shell实战](cheatsheets/shell实战-场景速查.md) |
| docker 起停/清理/构建 | [cheatsheets/docker速查](cheatsheets/docker速查-场景速查.md) |

### 🎓 我想真学透（程序员视角精读系列，不是看视频混时间）
| 想学 | 直接打开 |
|------|---------|
| 计算机系统底子（CSAPP） | [notes/csapp-程序员视角](notes/csapp-程序员视角.md) — 每章=日常debug故事+可粘贴命令 |
| 操作系统（从 bug 反推原理） | [notes/os-程序员视角](notes/os-程序员视角-从bug到原理.md) — OOM/死锁/僵尸/丢数据 |
| 数据库（从慢SQL到原理） | [notes/db-程序员视角](notes/db-程序员视角-从慢SQL到原理.md) — 慢查询/死锁/索引失效/MVCC |
| 网络（从抓包到原理） | [notes/network-程序员视角](notes/network-程序员视角-从抓包到原理.md) — RST/epoll/粘包/CLOSE_WAIT/TLS |
| 设计模式（真实代码里的） | [notes/patterns-程序员视角](notes/patterns-程序员视角-真实代码里的模式.md) — 12模式+何时别用红线 |
| 代码评审实战 | [notes/code-review-程序员视角](notes/code-review-程序员视角.md) — 17个before/after |
| 性能调优实战 | [notes/perf-程序员视角](notes/perf-程序员视角-定位与优化.md) — 6优化案例+火焰图流水线 |
| **🆕 csdiy.wiki 全课程逐 session 解析（6 篇 / 3,691 行）** | [math](notes/csdiy-math-complete.md) 1594 / [programming](notes/csdiy-programming-complete.md) 645 / [core-cs](notes/csdiy-core-cs-complete.md) 392 / [systems](notes/csdiy-systems-complete.md) 477 / [applications](notes/csdiy-applications-complete.md) 352 / [electives](notes/csdiy-electives-complete.md) 231 |
| 亲手做 xv6 lab | [labs/xv6-6.S081-从零跑起来](labs/xv6-6.S081-从零跑起来.md) |
| 亲手做 CMU 数据库 lab | [labs/bustub-15-445-从零跑起来](labs/bustub-15-445-从零跑起来.md) |
| 亲手做 MIT 分布式 Raft | [labs/mit6.824-raft-从零跑起来](labs/mit6.824-raft-从零跑起来.md) |
| 选一条完整学习路径 | [paths/](paths/) (系统/AI/全栈/理论/图形 5 条) |

### 📖 我要精读真实源码（59 篇，逐行/逐函数拆；完整索引见 [RESOURCES-INDEX.md](RESOURCES-INDEX.md)）

**🔑 经典系统源码（19 篇，已长期稳定）**

| 精读什么 | 直接打开 |
|---------|---------|
| Redis 事件循环逐行拆解 | [redis-eventloop](source-reading/redis-eventloop-逐行拆解.md) |
| Redis 数据结构（SDS/Ziplist/Skiplist/Dict） | [redis-data-structures](source-reading/redis-data-structures-精读.md) |
| Redis 过期策略 | [redis-expiry-policy](source-reading/redis-expiry-policy-精读.md) |
| SQLite B-tree 逐行拆解 | [sqlite-btree](source-reading/sqlite-btree-逐行拆解.md) |
| LevelDB LSM 树 | [leveldb-lsm](source-reading/leveldb-lsm-精读.md) |
| 存储引擎对比（B+ vs LSM vs 列式） | [storage-comparison](source-reading/storage-engine-comparison-精读.md) |
| 事件循环演化史（Redis→nginx→Go） | [eventloop-evolution](source-reading/eventloop-evolution-redis-nginx-go.md) |
| nginx HTTP 解析器 | [nginx-http-parser](source-reading/nginx-http-parser-精读.md) |
| Linux epoll 内核实现 | [linux-epoll-kernel](source-reading/linux-epoll-kernel-精读.md) |
| Linux TCP 状态机 | [linux-tcp-state-machine](source-reading/linux-tcp-state-machine-精读.md) |
| Raft vs Paxos 对比 | [raft-vs-paxos](source-reading/raft-vs-paxos-精读.md) |
| 一致性哈希 | [consistent-hashing](source-reading/consistent-hashing-精读.md) |
| Bloom Filter | [bloom-filter](source-reading/bloom-filter-精读.md) |
| micrograd 100 行吃透自动微分 | [micrograd](source-reading/micrograd-100行吃透自动微分.md) |
| nanoGPT 读懂最小 GPT | [nanoGPT](source-reading/nanoGPT-读懂最小GPT.md) |
| Go GMP 调度器 | [go-gmp-scheduler](source-reading/go-gmp-scheduler-精读.md) |
| Rust 所有权 | [rust-ownership](source-reading/rust-ownership-精读.md) |
| frp TCP 代理设计 | [frp-tcp-proxy](source-reading/frp-tcp-proxy-核心设计拆解.md) |
| 极简源码阅读方法论 | [方法论](source-reading/极简源码阅读方法论.md) |

**🧠 深度学习/神经网络基础（14 篇）** — `backprop-graph` / `cnn-convolution` / `transformer-attention-deep` / `attention-variants` / `flash-attention` / `position-encoding` / `normalization-deep` / `dropout-train-infer` / `weight-init` / `loss-functions` / `softmax-temperature` / `gradient-vanishing`

**🤖 LLM 训练/推理（22 篇）⭐核心新增** —
- **训练**：`transformer-training-pipeline` `lr-scheduling` `fine-tuning-landscape` `rlhf-alignment` `prompt-engineering-deep`
- **推理**：`tokenizer-deep` `kv-cache-原理` `kv-cache-compression` `long-context` `inference-optimization` `speculative-decoding` `mixed-precision` `model-compression` `model-parallel` `moe-routing`
- **部署/评估/应用**：`llm-deployment` `llm-evaluation` `llm-security` `rag-advanced` `agent-architecture` `data-pipeline` `data-versioning`

**🌐 其他**（4 篇）— `vae-math` `mamba-ssm-math` `multimodal`（生成/SSM/多模态）· `hnsw-algorithm`（向量检索）· `branch-prediction` `numa-architecture`（体系结构）

> 📋 **完整 59 篇索引**：[RESOURCES-INDEX.md §二](RESOURCES-INDEX.md)
> 🗂️ **按学科主题查**：[TOPICS.md](TOPICS.md)

### ⚡ 我每天练一手（终端里直接跑）
```bash
python3 tools/daily.py          # 今日套餐: 挑战卡+debug场景+命令+lab+学习路径
python3 tools/daily.py --mode card    # 只抽卡
python3 tools/review.py         # SM-2 间隔重复复习(简单/一般/困难)
```

### 💼 我要面试 / 速记
| 要什么 | 直接打开 |
|--------|---------|
| 60 张实战卡片（系统/网络/DB/并发/算法/调试） | [cards/程序员实战卡片](cards/程序员实战卡片.md) |
| Anki 导入版（直接拖进 Anki） | [cards/anki.tsv](cards/anki.tsv) |

### 🔍 我要找仓库里的某段内容
```bash
# 全文检索（48k 文档/代码/PDF 已建索引）
python3 tools/build_index.py --query "xv6 页表实现"
# CS 私教 RAG 问答（检索+生成）
python3 tools/ask.py "Raft 和 Paxos 的区别"
```

## 资料全景（数据视角）
- **48,791 文件 / 15.68 GB**，118 个主题（见 [manifest/summary.json](manifest/summary.json)）
- **28,149 文档全文索引**（896MB FTS5，md/html/pdf/code 全覆盖，见 `index/search.sqlite`）
- **156 节点知识图谱**（课程+先修关系，见 [graph/graph.mmd](graph/graph.mmd)）
- **去重候选 ~1.8 GB**（见 [manifest/duplicates.json](manifest/duplicates.json)，可回收）

### 🏗️ 我要造真实项目（**68 个**毕业项目，参照世界级开源；完整清单见 [projects/PROJECTS.md](projects/PROJECTS.md)）

**🌐 网络层（14 个 / 2,396 行）**

| 项目 | 参照 | 一句话 |
|------|------|--------|
| [tinyproxy](projects/tinyproxy/) | frp/nginx | TCP 负载均衡代理（epoll+桥接+LB算法） |
| [tinyhttpd](projects/tinyhttpd/) | nginx | HTTP 服务器（路由+静态文件+API） |
| [tinydns](projects/tinydns/) | CoreDNS | DNS 服务器（UDP+RFC 1035） |
| [tinyrpc](projects/tinyrpc/) | gRPC | RPC 框架（Stub+序列化） |
| [tinytls](projects/tinytls/) | OpenSSL | TLS 握手+记录层 |
| （+ tinydhcp/icmp/arp/route/ratelimit/websocket/pipe/stream/eventloop） | | 详见 PROJECTS.md |

**💾 存储层（9 个 / 2,956 行）**

| 项目 | 参照 | 一句话 |
|------|------|--------|
| [tinydb](projects/tinydb/) | SQLite | KV 存储（page+B-tree+WAL） |
| [tinycache](projects/tinycache/) | Redis | 内存缓存（RESP协议+dict+过期） |
| [tinysql](projects/tinysql/) | PostgreSQL | SQL 解析+执行 |
| （+ tinybitcask/blob/wal/fs/index/cachesim） | | 详见 PROJECTS.md |

**🌍 分布式（8 个 / 987 行）** — [tinyraft](projects/tinyraft/)（etcd/6.824）· [tinykafka](projects/tinykafka/)（Kafka）· tiny2pc/mapreduce/gossip/ring/mesi/clock

**🐧 操作系统（12 个 / 1,760 行）** — [tinyshell](projects/tinyshell/)（bash/xv6）· [tinydocker](projects/tinydocker/)（Docker）· tinymmu/interrupt/gc/alloc/pool/sched/trace/tx/signal/seq

**⚙️ 编译/语言（6 个 / 1,475 行）** — [tinycompiler](projects/tinycompiler/)（Crafting Interpreters）· [tinyjson](projects/tinyjson/)（simdjson）· tinyregex/asm/linker/symtab

**🖥️ 体系结构（3 个 / 714 行）** — [tinycpu](projects/tinycpu/)（RISC-V）· tinydma/vm

**🤖 AI/LLM（5 个 / 3,435 行）⭐** — [tinytorch](projects/tinytorch/)（929 行 PyTorch 简化版）· [tinyllm](projects/tinyllm/)（870 行 LLM 推理引擎）· [tinyrag](projects/tinyrag/)（695 行端到端 RAG）· tinyrl/gen

**🔐 安全（2 个）** · **🛠️ 工具（3 个）** · **📐 算法（4 个）** · **🔧 杂项（2 个）** — 详见 [PROJECTS.md](projects/PROJECTS.md)

**📊 总览**：68 个项目 / **14,681 行 Python 代码** / CSAPP 9/9 章 100% 覆盖

### 🎓 我要做费曼挑战（强制输出）
```bash
python3 tools/feynman.py --source csapp    # CSAPP 概念挑战
python3 tools/feynman.py --source db       # 数据库概念挑战
python3 tools/feynman.py --list             # 列出所有概念
python3 tools/feynman.py --history          # 查看历史
```

### 📊 项目分析与战略
| 文件 | 内容 |
|------|------|
| [ANALYSIS.md](ANALYSIS.md) | 7 视角深度分析（费曼/SECI/分形/系统思考/第一性原理/YAGNI/双环学习） |
| [STRATEGY.md](STRATEGY.md) | 双环学习战略反思（目标/DoD/3大怀疑/机会成本） |
| [TOPICS.md](TOPICS.md) | 🆕 **按 16 学科主题的交叉分类总览** |
| [RESOURCES-INDEX.md](RESOURCES-INDEX.md) | **82 篇精加工 + 68 项目** 的结构化索引 |
| [projects/PROJECTS.md](projects/PROJECTS.md) | **68 个**毕业项目全景（14,681 行代码） |
| [projects/COVERAGE.md](projects/COVERAGE.md) | csdiy 知识覆盖矩阵 |

## 八条特色主线（v2.0 升级 · 2026-07-07）
1. **程序员视角精读**：每个学术概念都连到你今天会写的代码、会调的 bug（**7 篇**：CSAPP/OS/DB/网络/模式/评审/性能 + **6 篇课程地图解析** = 13 篇 notes）。
2. **场景驱动速查**：不是命令字典，是"遇到 X 怎么办"的答案盒（**11 篇** cheatsheet）。
3. **可直接跑的 Lab**：从环境到第一个 lab 到报错修复表（**4 篇**：xv6/bustub/6.824/cs144）。
4. **真实源码逐行精读**：从 5 篇扩展到 **59 篇**（系统源码 + DL 基础 14 篇 + LLM 全栈 22 篇 + 体系结构/AI 基础设施）。
5. **每天终端练一手**：`daily.py` 抽卡+debug+命令+lab，`review.py` SM-2 间隔重复，`feynman.py` 20 概念×4 层强制输出。
6. **68 个毕业项目**：从 22 个扩展到 **68 个**（14,681 行 Python），CSAPP 9/9 章 100% 覆盖。
7. **端到端集成测试**：`integration_test.py` 验证 tinyproxy→tinyhttpd→tinycache→tinydb 全链路（12/12 通过）。
8. **主题交叉索引**：新增 [TOPICS.md](TOPICS.md)，按 16 学科主题快速定位资源。

---
*用 `opencode` 在本目录打开，所有资料可被 AI 检索问答。*
*v2.0 (2026-07-07): 68 projects / 59 source-readings / 8 notes / 14,681 LoC / CSAPP 9/9 coverage*
