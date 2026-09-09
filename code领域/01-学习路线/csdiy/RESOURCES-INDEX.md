# csdiy 资源全索引（结构化内容地图 · v2）

> 实际文件系统扫描得出，与 [TOPICS.md](TOPICS.md) / [INDEX.md](INDEX.md) 同步。
> 旧版本（v1）只索引 33 个资源，本版扩展到 **82 篇精加工 + 68 个项目**。
>
> 生成时间：2026-07-07

---

## 📊 资源总览（实测）

| 类别 | 数量 | 总行数 | 核心方法 |
|------|------|--------|---------|
| NOTES 程序员视角精读 | **7 篇** | 4,050 行 | 事故→原理→命令→修复 |
| NOTES 课程地图解析 🆕 | **6 篇** | 3,691 行 | csdiy.wiki 全课程逐 session 解析 |
| CHEATSHEETS（场景速查） | 11 篇 | 2,440 行 | 一行场景→一条命令 |
| SOURCE-READING（源码精读） | **59 篇** 🆕 | 14,435 行 | 逐行拆解+动手验证 |
| LABS（实验指南） | 4 篇 | 904 行 | 从零跑起来+报错修复 |
| CARDS（实战卡片） | 60 张 | 639 行 + anki.tsv | 场景→本质→一句话 |
| PATHS（学习路径） | 5 条 | — | 5 方向×预估周期 |
| PROJECTS（毕业项目） | **68 个** 🆕 | 14,681 行 py | 参照世界级开源 |
| TOOLS（工具） | **10 个** 🆕 | — | daily/review/ask/by_topic/... |
| FTS 索引 | — | 28,452 文档 | 896MB FTS5 |
| **合计精加工** | **82 篇 + 68 项目** | **~30,000 行** | |

**对比旧版（v1，2026-07-05）**：
- NOTES: 7 → **13**（新增 6 篇课程地图解析）
- SOURCE-READING: 5 → **59**（新增 54 篇，主要在 LLM/DL）
- PROJECTS: 22 → **68**（新增 46 个）
- 总行数: ~9,954 → **~30,000**（3 倍）

---

## 一、NOTES（7 篇程序员视角精读）

| # | 文件 | 行数 | 主题 |
|---|------|------|------|
| 1 | `csapp-程序员视角.md` | 569 | CSAPP 9 章逐章救什么命 |
| 2 | `os-程序员视角-从bug到原理.md` | 628 | OS 6 事故（OOM/死锁/僵尸/fsync/并发/IO）|
| 3 | `db-程序员视角-从慢SQL到原理.md` | 580 | DB 6 事故（索引/锁/MVCC/连接/WAL）|
| 4 | `network-程序员视角-从抓包到原理.md` | 580 | 网络 6 现象（RST/epoll/粘包/CLOSE_WAIT/Nagle/TLS）|
| 5 | `patterns-程序员视角-真实代码里的模式.md` | 538 | 12 模式 + 红线（何时别用）|
| 6 | `code-review-程序员视角.md` | 476 | 17 个 before/after |
| 7 | `perf-程序员视角-定位与优化.md` | 438 | 6 案例 + 火焰图流水线 |

**核心方法**：每篇统一用 `事故/现象 → 反推原理 → 排查命令 → 修复 → 一行本质`

---

## 一·补、课程地图解析 🆕（6 篇 / 3,691 行）

| 文件 | 行数 | 覆盖 |
|------|------|------|
| `csdiy-math-complete.md` | 1594 | 数学（线代/概率/离散/3B1B）|
| `csdiy-programming-complete.md` | 645 | 编程入门（16 门课）|
| `csdiy-core-cs-complete.md` | 392 | 核心 CS（电子+DSA+SE）|
| `csdiy-systems-complete.md` | 477 | 系统类（体系结构+OS+并行分布式）|
| `csdiy-applications-complete.md` | 352 | 应用层（安全+网络+DB）|
| `csdiy-electives-complete.md` | 231 | 选修（编译+PL+图形+Web+DS）|

**定位**：介于上游 mkdocs（粗）和程序员视角精读（深）之间——把 csdiy.wiki 全课程地图逐 session 解析。

---

## 二、SOURCE-READING（59 篇源码精读，按主题分组）

### 2.1 深度学习/神经网络基础（14 篇 / 3,085 行）

| 文件 | 行数 | 主题 |
|------|------|------|
| `micrograd-100行吃透自动微分.md` | 396 | Value 类 + 链式法则 + 拓扑序 |
| `nanoGPT-读懂最小GPT.md` | 480 | GPTConfig + Attention + MLP + Block |
| `backprop-graph-精读.md` | 153 | 反向传播的计算图推导 |
| `cnn-convolution-精读.md` | 178 | 卷积运算的数学与实现 |
| `transformer-attention-deep-精读.md` | 185 | Scaled Dot-Product Attention |
| `attention-variants-精读.md` | 186 | MHA/MLA/GQA/MQA 演化 |
| `flash-attention-精读.md` | 164 | FlashAttention 的 tiling |
| `position-encoding-精读.md` | 233 | 绝对/相对/RoPE 位置编码 |
| `normalization-deep-精读.md` | 187 | BN/LN/RMSNorm |
| `dropout-train-infer-精读.md` | 169 | Dropout 在训练/推理的差异 |
| `weight-init-精读.md` | 168 | Xavier/He/正交初始化 |
| `loss-functions-精读.md` | 225 | CE/Focal/Contrastive |
| `softmax-temperature-精读.md` | 157 | Softmax + 温度采样 |
| `gradient-vanishing-精读.md` | 204 | 梯度消失/爆炸与残差连接 |

### 2.2 LLM 训练/推理（22 篇 / 4,959 行）⭐最大块

**训练侧（5 篇）**
| 文件 | 行数 | 主题 |
|------|------|------|
| `transformer-training-pipeline-精读.md` | 229 | 训练 pipeline 全景 |
| `lr-scheduling-精读.md` | 233 | Warmup/Cosine/1cycle |
| `fine-tuning-landscape-精读.md` | 232 | LoRA/QLoRA/Adapter |
| `rlhf-alignment-精读.md` | 183 | RLHF/DPO/PPO |
| `prompt-engineering-deep-精读.md` | 269 | Few-shot/CoT/结构化 |

**推理侧（10 篇）**
| 文件 | 行数 | 主题 |
|------|------|------|
| `tokenizer-deep-精读.md` | 238 | BPE/WordPiece/SentencePiece |
| `kv-cache-原理-精读.md` | 206 | KV Cache 数学与实现 |
| `kv-cache-compression-精读.md` | 201 | PagedAttention/量化压缩 |
| `long-context-精读.md` | 209 | 长上下文优化 |
| `inference-optimization-精读.md` | 254 | 推理优化综合 |
| `speculative-decoding-精读.md` | 193 | 投机解码 |
| `mixed-precision-精读.md` | 201 | FP16/BF16/FP8 |
| `model-compression-精读.md` | 223 | 量化/剪枝/蒸馏 |
| `model-parallel-精读.md` | 205 | TP/PP/DP |
| `moe-routing-精读.md` | 190 | Mixture of Experts |

**部署/评估/应用（7 篇）**
| 文件 | 行数 | 主题 |
|------|------|------|
| `llm-deployment-精读.md` | 248 | vLLM/TGI 部署 |
| `llm-evaluation-精读.md` | 271 | MMLU/HumanEval/BLEU |
| `llm-security-精读.md` | 229 | Prompt 注入/越狱 |
| `rag-advanced-精读.md` | 222 | 检索增强生成 |
| `agent-architecture-精读.md` | 277 | ReAct/Tool Use |
| `data-pipeline-精读.md` | 236 | 数据管线 |
| `data-versioning-精读.md` | 210 | DVC/LakeFS |

### 2.3 生成模型/SSM/多模态（3 篇 / 572 行）

| 文件 | 行数 | 主题 |
|------|------|------|
| `vae-math-精读.md` | 157 | VAE 的 ELBO 推导 |
| `mamba-ssm-math-精读.md` | 193 | Mamba SSM 数学 |
| `multimodal-精读.md` | 222 | CLIP/BLIP/Flamingo |

### 2.4 系统/存储（10 篇 / 3,711 行）

| 文件 | 行数 | 主题 |
|------|------|------|
| `redis-eventloop-逐行拆解.md` | 691 | Redis ae.c 事件循环 + strace 验证 |
| `sqlite-btree-逐行拆解.md` | 613 | SQLite B-tree + 文件格式 + hexdump |
| `redis-data-structures-精读.md` | 421 | SDS/Ziplist/Skiplist/Dict |
| `eventloop-evolution-redis-nginx-go.md` | 399 | 事件循环演化史 |
| `leveldb-lsm-精读.md` | 386 | LevelDB LSM 树 |
| `redis-expiry-policy-精读.md` | 268 | 惰性+定期+淘汰 |
| `linux-epoll-kernel-精读.md` | 269 | Linux epoll 内核实现 |
| `linux-tcp-state-machine-精读.md` | 268 | TCP 状态机 |
| `nginx-http-parser-精读.md` | 249 | nginx HTTP 状态机 |
| `storage-engine-comparison-精读.md` | 147 | B+ vs LSM vs 列式 |

### 2.5 网络/代理（1 篇 / 363 行）

| 文件 | 行数 | 主题 |
|------|------|------|
| `frp-tcp-proxy-核心设计拆解.md` | 363 | frp Proxy 接口 + Factory + 桥接 |

### 2.6 分布式（3 篇 / 473 行）

| 文件 | 行数 | 主题 |
|------|------|------|
| `raft-vs-paxos-精读.md` | 165 | Raft vs Paxos 对比 |
| `consistent-hashing-精读.md` | 145 | 一致性哈希 |
| `bloom-filter-精读.md` | 163 | 布隆过滤器 |

### 2.7 运行时/语言（2 篇 / 498 行）

| 文件 | 行数 | 主题 |
|------|------|------|
| `go-gmp-scheduler-精读.md` | 211 | Go GMP 调度器 |
| `rust-ownership-精读.md` | 287 | Rust 所有权 |

### 2.8 AI 基础设施 / 体系结构（3 篇 / 568 行）

| 文件 | 行数 | 主题 |
|------|------|------|
| `hnsw-algorithm-精读.md` | 161 | HNSW 向量检索 |
| `branch-prediction-精读.md` | 217 | CPU 分支预测 |
| `numa-architecture-精读.md` | 190 | NUMA 架构 |

### 2.9 方法论（1 篇 / 206 行）

| 文件 | 行数 | 主题 |
|------|------|------|
| `极简源码阅读方法论.md` | 206 | 五步法 + 三种规模策略 |

---

## 三、CHEATSHEETS（11 篇场景速查 / 2,440 行）

| # | 文件 | 行数 | 场景数 | 核心覆盖 |
|---|------|------|--------|---------|
| 1 | `git进阶-场景速查.md` | 99 | 9 | 撤回/找回/冲突/bisect/submodule |
| 2 | `gdb调试-场景速查.md` | 130 | 12 | segfault/断点/多线程/core |
| 3 | `docker速查-场景速查.md` | 160 | 11 | 起停/镜像/日志/Volume/Dockerfile |
| 4 | `makefile与cmake-场景速查.md` | 157 | 10 | 模板/自动依赖/CMake |
| 5 | `shell实战-场景速查.md` | 130 | 9 | 找文件/三剑客/批处理 |
| 6 | `vim生存-场景速查.md` | 137 | 10 | 移动/编辑/搜索/分屏/宏 |
| 7 | `k8s-场景速查.md` | 240 | 8 类 | Pod/QoS/网络/滚动发布 |
| 8 | `postgres-场景速查.md` | 345 | 8 类 | 慢查询/死锁/VACUUM/连接池 |
| 9 | `profiling-场景速查.md` | 349 | 7 类 | CPU/内存/IO/锁/eBPF |
| 10 | `python-场景速查.md` | 345 | 7 类 | venv/调试/异步/打包 |
| 11 | `regex-场景速查.md` | 348 | 8 类 | 提取/替换/回溯灾难/30实战 |

---

## 四、LABS（4 篇实验指南 / 904 行）

| # | 文件 | 行数 | 课程 |
|---|------|------|------|
| 1 | `xv6-6.S081-从零跑起来.md` | 141 | MIT 6.S081 |
| 2 | `bustub-15-445-从零跑起来.md` | 146 | CMU 15-445 |
| 3 | `mit6.824-raft-从零跑起来.md` | 129 | MIT 6.824 |
| 4 | `cs144-网络-从零跑起来.md` | 488 | Stanford CS144 |

---

## 五、PROJECTS（68 个毕业项目 / 14,681 行 py）

详见 [projects/PROJECTS.md](projects/PROJECTS.md)。按主题：
- 🌐 网络（14 个）· 💾 存储（9 个）· 🌍 分布式（8 个）· 🐧 OS（12 个）
- ⚙️ 编译（6 个）· 🖥️ 体系结构（3 个）· 🤖 AI/LLM（5 个）
- 🔐 安全（2 个）· 🛠️ 工具（3 个）· 📐 算法（4 个）· 🔧 杂项（2 个）

---

## 六、CARDS（实战卡片）

| 文件 | 内容 |
|------|------|
| `cards/程序员实战卡片.md` | 60 张卡片（系统/网络/DB/并发/算法/调试）|
| `cards/anki.tsv` | Anki 直接导入版（20KB） |

---

## 七、PATHS（5 条学习路径）

| 路径 | 目标 | 预估 |
|------|------|------|
| `systems.md` | OS/数据库/分布式 | 78 周 |
| `ai.md` | 数学→DL→论文 | 60 周 |
| `fullstack.md` | Web 应用独立交付 | 52 周 |
| `theory.md` | 算法/理论 CS | 46 周 |
| `graphics.md` | 光栅/光追/PBR | 44 周 |

---

## 八、TOOLS（9 个 Python 工具）

| 工具 | 功能 |
|------|------|
| `daily.py` | 每日训练（抽卡+debug+命令+lab+路径）|
| `review.py` | SM-2 间隔重复复习 |
| `feynman.py` 🆕 | 费曼挑战（20 概念，4 层输出） |
| `ask.py` | RAG 问答（检索+生成） |
| `build_index.py` | FTS5 全文索引 |
| `build_manifest.py` | 资源清单+去重 |
| `build_graph.py` | 知识图谱（156 节点）|
| `build_paths.py` | 学习路径生成 |
| `extract_summaries.py` 🆕 | 章节摘要提取 |

---

## 📐 方法论模式总结

```
精读类（8 篇）：  事故/现象 → 反推原理 → 排查命令 → 修复 → 一行本质
速查类（11 篇）： 一行场景 → 一条命令 + 一句话何时用
源码类（59 篇）： 干什么 → 数据结构 → 逐行精读 → 动手验证
实验类（4 篇）：  环境 → 安装 → 跑通 → 报错修复表 → 下一步
卡片类（60 张）： 场景 → 一句话本质 + 命令 + 例子
项目类（68 个）： 参照真实开源 → 最小可运行 → 端到端集成测试
```

**共同的 DNA**：**不灌输理论，从真实问题出发，落到可粘贴的命令/代码**。

---

## 🔄 与其他索引的关系

| 文档 | 组织维度 | 何时用 |
|------|---------|--------|
| **README.md** | 资源来源（下载历史） | 想知道某个资料的来源 |
| **INDEX.md** | "我想干什么" | 找入口/快速跳转 |
| **TOPICS.md** | 学科主题交叉 | 想学 X，找 X 的所有资源 |
| **本文档** | 资源类型顺序 | 查某篇/某个项目的内容 |
| **PROJECTS.md** | 68 个项目 | 找毕业项目做 |

---

*本文档基于实际文件系统扫描（2026-07-07），与 [TOPICS.md](TOPICS.md) / [INDEX.md](INDEX.md) 保持同步。*
