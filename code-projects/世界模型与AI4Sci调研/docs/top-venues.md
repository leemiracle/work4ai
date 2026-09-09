# OS / 计算机 / AI 领域顶刊顶会全谱

> 学术资源地图 · 与本卷 10 大模块的导航桥
> 2026-07-20 · 联网核实版（CORE 2023 官方评级 + 各会议官网一手核实）
> 适用对象：立志成为「应用数学研究型工程师」的研究者，需要一份能精准对标投稿、跟踪前沿、又与本卷章节联动的顶会导航。

---

## 〇、开篇：为什么必须吃透顶会顶刊（500 字）

学术会议与期刊不是一个"发表渠道"，它是**整个研究共同体的风向标与计分牌**。一个方向是否被认可、一个 idea 是否被推翻、一个团队是否值得加入——答案都写在最近三年的 Proceedings 里。对身处工业化与学术化交界、试图把数学与系统打通的工程师而言，顶会顶刊有三重不可替代的价值：**第一，它是前沿的实时滚动条**，arXiv 上每天涌入上百篇预印本，但只有经过严格 peer review 的那 20% 才沉淀为"可被引用的事实"；**第二，它是审稿文化的样本库**，读懂 NeurIPS 的 rebuttal、OSDI 的 shepherding、Nature 的三审，就理解了什么是"可被信任的科学声明"；**第三，它是职业坐标系**，CCF A / CORE A\* / Google h5-index 三套体系交叉，构成一张全球通用的学术信用地图。

本卷之所以需要这样一张地图，是因为我们的 10 大模块横跨**世界模型、AI4Science、AI4Math、系统综合、模型工程、理论根基、扩展技术、AI4X 应用、哲学伦理、新兴领域**——每一块都对应着截然不同的发表生态。世界模型论文去 NeurIPS/ICLR，系统论文去 OSDI/SOSP，AI4Science 论文去 Nature/Science，理论论文去 STOC/FOCS/COLT，伦理论文去 AIES/FAccT。**选错会场等于自废武功**。因此本文不只罗列等级与影响因子，更要把每个会议与本卷章节一一咬合，告诉你"想研究 X，该盯哪里、该投哪里、该读谁"。

本文使用三套评级体系，三者**互补而非替代**：

- **CCF 推荐目录**（中国计算机学会）：中国高校与基金评审的事实标准，分 A/B/C 三级（A=顶级/重要，B=优秀，C=一般）。当前最新版为 **2022 版**（第五版，2022-09 发布），并在 **2025-09 增量更新**中调整了部分新兴方向。网址：`https://www.ccf.org.cn/Academic_Evaluation/By_category/`。
- **CORE Ranking**（澳洲，现升级为 **ICORE**，Core Ranking of Conferences）：国际公认的第二意见，分 **A\*（顶级，仅占 7.65%）/ A（14.92%）/ B（28.06%）/ C**。最新版 **CORE 2023**（已通过 `portal.core.edu.au/conf-ranks` 一手核实）。注意 CORE 比 CCF 更细分，例如 ICLR 在 CCF 尚未独立列项，但 CORE 已定为 A\*。
- **Google Scholar Metrics（h5-index）**：基于 Google Scholar 引用大数据，反映**真实影响力**而非审稿难度。每年发布，是衡量"该会议论文在互联网上被讨论多少"的金标准。h5-index 中位数越高，说明该会议的"爆款"越密集。

> **三大评级的差异速记**：CCF 关乎中国晋升/基金，CORE 关乎国际声誉，Google h5 关乎真实传播。三者常有出入——例如 AAAI 在 CCF 是 A、CORE 是 A\*、但 h5 因论文量大稀释；又如 Nature 子刊 IF 高但 h5 中位数可能不如顶会。**投稿决策三者都要看**。

---

## 一、操作系统与系统领域（核心战场）

> **联动章节**：`04-synthesis/05-stagnation-and-innovation`（编译器+算法红利）、`08-ai4x-applications/07-computing-architecture-future`、`08/01-os-meets-ai`。

系统领域是 AI 工程化的"地基"。vLLM、Megatron、FlashAttention 这些让大模型跑起来的工程突破，本质都是系统研究。下面九个会议构成系统的**全部最高殿堂**。

| 会议 | 缩写 | CCF | CORE | 近年接收率 | 频率 | 主办方 |
|---|---|---|---|---|---|---|
| Symposium on Operating Systems Design and Implementation | **OSDI** | A | **A\*** | ~20%（2024≈28%） | 2 年 | USENIX |
| ACM Symposium on Operating Systems Principles | **SOSP** | A | **A\*** | ~20% | 2 年（与 OSDI 交替） | ACM SIGOPS |
| European Conference on Computer Systems | **EuroSys** | A | A | ~20–25% | 年 | ACM |
| USENIX Annual Technical Conference | **USENIX ATC** | A | A | ~20–25% | 年 | USENIX |
| Architectural Support for Programming Languages and OS | **ASPLOS** | A | **A\*** | ~20% | 年 | ACM/IEEE |
| Symposium on Networked Systems Design and Implementation | **NSDI** | A | **A\*** | ~18–20% | 年 | USENIX |
| Conference on File and Storage Technologies | **FAST** | A | A | ~25% | 年 | USENIX |
| ACM Symposium on Cloud Computing | **SoCC** | B | A | ~24% | 年 | ACM |
| ACM/IFIP International Middleware Conference | **Middleware** | B | A | ~20% | 年 | ACM/IFIP |

### 1.1 OSDI 与 SOSP —— 系统的"双子星座"

OSDI 与 SOSP **交替举办**（偶数年 OSDI、奇数年 SOSP），合起来是系统领域无可争议的双 No.1。它们的接收率长期稳定在 20% 上下（OSDI 2024 因投稿量上升一度接近 28%），但**真正的门槛不是数字而是 taste**——审稿人要的不是 incremental improvement，而是"改变我们思考系统的方式"。

**里程碑论文（必读）**：
- **GFS**（Google File System, SOSP 2003）—— 分布式存储的开山之作，奠定工业级容错文件系统范式。
- **MapReduce**（OSDI 2004）—— 让"算力成为公用事业"的工程哲学，直接催生 Hadoop/Spark 生态。
- **Bigtable**（OSDI 2006）—— 列式存储的奠基，影响 HBase/Cassandra/ DynamoDB。
- **Dynamo**（SOSP 2007）—— 最终一致性 + 一致性哈希，NoSQL 运动的理论源头。
- **Spanner**（OSDI 2012）—— Google 全球数据库，TrueTime API 与 Paxos 的工程化。
- **Borg**（EuroSys 2015）—— 容器编排的鼻祖，Kubernetes 的直接前身。
- **vLLM**（**SOSP 2023**，arXiv:2309.06180）—— **PagedAttention**，把操作系统的虚拟内存思想用到 KV Cache 管理，单卡吞吐翻 2–4 倍，是 LLM 推理基础设施的基石。⭐**这正是"系统思想反哺 AI"的教科书案例**，直接呼应本卷 `04-synthesis` 与 `05-model-engineering`。

**AI 相关性**：OSDI/SOSP 近三年 LLM 系统、向量数据库、ML 训练基础设施论文占比从 5% 飙升到 30%+。**投稿建议**：把 ML 系统问题抽象成经典系统问题（调度、内存、缓存、一致性），用系统社区的语言讲，胜算最高。vLLM 就是范本——它不卖"AI 新概念"，而卖"虚拟内存做 KV Cache"。

### 1.2 EuroSys / USENIX ATC —— 顶会之外的高水平阵地

两者都是年度会，接收率略松于 OSDI/SOSP（20–25%），是欧洲系统学派（EuroSys）与北美应用系统（ATC）的代表。EuroSys 偏理论 + 系统，ATC 偏工程实践。**对研究者**：当一个 idea 不够"革命"够不上 OSDI，但工程扎实、evaluation 充分，EuroSys/ATC 是首选。AI4Sys 类工作（如 GPU 调度器、训练断点续传）常落于此。

### 1.3 ASPLOS —— 软硬协同的皇冠

ASPLOS（Architectural Support for Programming Languages and OS）是**唯一横跨体系结构、编译器、操作系统、编程语言的顶会**，CORE A\*，接收率 ~20%。它的定位是"软硬件界面"——任何发生在 ISA、微架构、运行时、语言层的工作都欢迎。**经典**：TPU v1（ISCA，但配套的 Eyeriss 系列在 ASPLOS）、**Gemini 都是在这类会场披露硬件细节**。**与本卷关联**：ASPLOS 是 `04-synthesis/05-stagnation-and-innovation.md` 里"编译器+硬件协同"红利的天然主场——TileLang、Triton、FlashMLA 这类工作都该投这里。**投稿建议**：必须有真实硬件评测，纯模拟易拒。

### 1.4 NSDI / FAST / SoCC / Middleware —— 系统细分赛道

- **NSDI**（网络系统，CORE A\*）：SDN、可编程网络、RDMA、AI 集群网络。经典：Spark（NSDI 2012 早期网络版有讨论）、Maglev 负载均衡。
- **FAST**（存储，CORE A）：文件系统、SSD、纠删码。AI 时代催生了"为 checkpoint 设计的文件系统"。
- **SoCC**（云计算，CORE A）：云原生、Serverless、弹性训练。
- **Middleware**（中间件，CORE A）：消息队列、流处理，Kafka/Spark Streaming 的论文摇篮。

**投稿策略小结**：系统论文的"等级阶梯"是 **OSDI/SOSP > ASPLOS/NSDI > EuroSys/ATC/FAST > SoCC/Middleware**。新人建议从 SoCC/Middleware 练手，积累 rebuttal 经验后再冲 OSDI。

---

## 二、数据库领域（数据是 AI 的氧气）

> **联动章节**：`08-ai4x-applications/05-database-meets-ai`。

| 会议 | 缩写 | CCF | CORE | 近年接收率 | 主办方 |
|---|---|---|---|---|---|
| ACM SIGMOD International Conference on Management of Data | **SIGMOD** | A | **A\*** | ~26–29% | ACM SIGMOD |
| International Conference on Very Large Data Bases | **VLDB** | A | **A\*** | ~30%（含 round） | VLDB Endowment |
| IEEE International Conference on Data Engineering | **ICDE** | A | A | ~23–25% | IEEE |
| ACM Symposium on Principles of Database Systems | **PODS** | A | **A\*** | ~30% | ACM |
| International Conference on Information and Knowledge Management | **CIKM** | B | A | ~20–22% | ACM |
| Extending Database Technology | **EDBT** | B | A | ~20–23% | - |

### 2.1 SIGMOD / VLDB —— 双雄并立

SIGMOD（年度，北美为主）与 VLDB（年度，全球巡回）是数据库领域的"OSDI/SOSP"。两者近年都在改革：SIGMOD 引入 reproducibility 奖、VLDB 推出**滚动审稿（research track + experiment track）**使投稿更灵活。接收率 SIGMOD ~26%、VLDB ~30%（VLDB 因 round 机制实际命中率更高）。

**里程碑论文（必读）**：
- **C-Store / Vertica**（VLDB 2005/2006）—— 列式数据库奠基，MonetDB/ClickHouse/Spark SQL 的祖先。
- **"The Case for Learned Index Structures"**（**Kraska et al., SIGMOD 2018**）—— **AI4DB 的开山炮**。提出用神经网络替代 B+Tree/Hash/Range Index，掀起"learned index"十年研究浪潮。⭐**这是本卷 `08/05` 章节的起点论文，必精读**。后续 SageDB、ALEX（SIGMOD 2020）、RW-Tree、PARIDM 都源于此。
- **Spark SQL / DataFrame**（SIGMOD 2015）—— 统一批处理接口。
- **Pine/Hydra**（VLDB 2023–2024）—— 向量数据库内核。
- **NeuroDB / DB-GPT 系列** —— 用 LLM 做自然语言到 SQL（NL2SQL），Text-to-SQL benchmark Spider/Bird 的主场。

### 2.2 ICDE / PODS —— 工程与理论两极

ICDE（IEEE 主办，CORE A）偏数据工程实现，是 SIGMOD/VLDB 的主流备选。PODS（CORE A\*）则**只收理论**——查询复杂度、数据流算法、流式计算下界。PODS 是数据库领域少有的"纯数学会议"，与本卷 `06-theoretical-foundations` 高度契合。

### 2.3 CIKM / EDBT —— 入门与扩圈

CIKM（CORE A，CCF B）是信息检索 + 知识管理 + 数据库的交叉会，接收率 ~20–22%，是新人进入数据库圈的友好跳板，也是图神经网络、知识图谱应用的主战场。EDBT 是欧洲版 CIKM。

**AI4DB / DB4AI 双向趋势**：这是数据库领域当下最热的话题。
- **AI4DB**（用 AI 优化数据库）：learned index、learned query optimizer、auto-tuning knob（OtterTune）、 Learned Cardinality Estimation。
- **DB4AI**（为 AI 服务的数据库）：向量数据库（Milvus/Pinecone/Weaviate）、feature store、向量+标量混合查询、LLM 推理缓存层。
**投稿建议**：把数据库问题用 ML 建模，或把 ML 系统问题用数据库技术解决，是 SIGMOD/VLDB 当前的 high-acceptance 方向。

---

## 三、计算机体系结构 / 硬件（AI 的物理底座）

> **联动章节**：`08-ai4x-applications/07-computing-architecture-future`、`04-synthesis/05-stagnation-and-innovation`。

| 会议 | 缩写 | CCF | CORE | 近年接收率 | 频率 |
|---|---|---|---|---|---|
| International Symposium on Computer Architecture | **ISCA** | A | **A\*** | ~20% | 年 |
| ACM/IEEE International Symposium on Microarchitecture | **MICRO** | A | **A\*** | ~20–22% | 年 |
| IEEE International Symposium on High Performance Computer Architecture | **HPCA** | A | **A\*** | ~20–24% | 年 |
| Design Automation Conference | **DAC** | A | A | ~25% | 年 |
| International Conference on Computer-Aided Design | **ICCAD** | B | A | ~25% | 年 |
| ACM/IEEE Supercomputing | **SC** | A | **A\*** | ~25% | 年 |

### 3.1 ISCA / MICRO / HPCA —— 体系结构三巨头

三者合称"计算机体系结构三大会"，ISCA 资格最老（1968）、MICRO 偏微架构、HPCA 偏高性能计算。CORE 全部 A\*，接收率 ~20%。

**AI 硬件里程碑**：
- **TPU v1**（**ISCA 2017**，Jouppi et al.）—— 谷歌为深度学习定制的首颗大规模商用 AI 芯片，Systolic Array 架构，单论文被引过万。⭐**AI 专用硬件的起点**。
- **TPU v4 / Pod**（ISCA 2021）—— 光互联 + 3D Torus 拓扑。
- **NVIDIA Eyeriss / Eyeriss v2**（ISCA 2016+）—— 边端推理。
- **Gemini 都是基于 TPU v5/v6 训练**，ISCA 是其硬件细节唯一公开渠道。
- **Groq TSP**、**Cerebras WSE**（ISCA 2020，史上最大芯片）、**Tenstorrent**、**IBM NorthPole**（**Science 2023**，类脑芯片）—— 这些"非主流架构"都在挑战冯诺依曼范式，正是本卷 `08/07` 的核心议题。
- **Hopper H100 / Blackwell B200**（NVIDIA，Hot Chips 披露 + ISCA/MICRO 配套）—— Transformer Engine、FP8、NVLink、Transformer Engine。本卷已一手核实 H100 规格：80GB HBM3、3.35 TB/s 带宽、BF16 1979 TFLOPS、FP8 3958 TFLOPS、700W。

**投稿建议**：体系结构论文必须有**真实芯片流片或高保真模拟器（gem5/SCALE-Sim）**。纯算法想法易被拒。AI 硬件方向目前是 ISCA/MICRO 最热赛道。

### 3.2 DAC / ICCAD —— EDA 的双子塔

DAC（Design Automation Conference）与 ICCAD 是 EDA（电子设计自动化）领域最高会议。**AI4EDA** 是当下爆发点：用强化学习做布局布线、用 GNN 做逻辑综合、用 LLM 做 RTL 代码生成（本卷 `08/03-eda-ic` 的核心）。DeepMind 的 **AlphaChip**（**Nature 2024**）即源自此类工作。接收率 ~25%，CCF 把 DAC 列 A、ICCAD 列 B（CORE 都为 A）。

### 3.3 SC —— 超算的最高荣誉

SC（Supercomputing，CORE A\*）是高性能计算顶会。**AI + HPC** 的交叉点：Megatron-LM、DeepSpeed 的 scaling 论文、千卡/万卡训练系统、GPU 集群调度都在这里。SC 的论文特点是**规模极大**——动辄上千 GPU 的实验，是工业实验室的主场。

---

## 四、网络领域

> **联动章节**：`08-ai4x-applications` 系统部分、`07-extended-tech` 分布式。

| 会议 | 缩写 | CCF | CORE | 近年接收率 |
|---|---|---|---|---|
| ACM SIGCOMM | **SIGCOMM** | A | **A\*** | ~20%（常年最难进的网络会） |
| NSDI | （见第一节） | A | **A\*** | ~18–20% |
| IEEE INFOCOM | **INFOCOM** | A | A | ~20% |
| ACM Internet Measurement Conference | **IMC** | B | **A\*** | ~25% |
| ACM CoNEXT | **CoNEXT** | B | A | ~25% |

### 4.1 SIGCOMM —— 网络之巅

SIGCOMM 是网络领域无可争议的 No.1，CORE A\*，接收率常年 ~20%（且投稿基数大、竞争极烈）。**里程碑**：TCP 拥塞控制（Jacobson）、SDN/OpenFlow（SIGCOMM 2008）、QUIC（SIGCOMM 2017）、可编程数据面（P4）。**AI 相关**：AI 训练集群的拥塞控制（如阿里的 HPCC、NVIDIA 的 Saturn 网络拓扑）、RDMA for LLM 训练、in-network aggregation（SwitchML，SIGCOMM 2021）是当前热点。**与本卷关联**：本卷 `04-synthesis` 提到的"内存带宽瓶颈"在网络层对应"互联带宽瓶颈"，SIGCOMM 是讨论这一瓶颈的主场。

### 4.2 INFOCOM / IMC / CoNEXT

INFOCOM（IEEE，规模最大，CORE A）接收率 ~20%，是中国学者发文最多的网络顶会。IMC（CORE A\*）专注网络测量，是唯一 CCF 仅列 B 但 CORE 给 A\* 的网络会——影响力极强。CoNEXT 是新兴网络实验技术。

**NWU 西北大学陈晓江**的 SIGCOMM 2025 MetaAI 空口 AI、MOBICOM 2024 等系统顶会成果，正是本卷关注的"系统学派不在 CSRankings-AI 统计内但极具实力"的典型。

---

## 五、安全领域

> **联动章节**：`08-ai4x-applications/04-ai4security`。

| 会议 | 缩写 | CCF | CORE | 近年接收率 |
|---|---|---|---|---|
| IEEE Symposium on Security and Privacy | **S&P (Oakland)** | A | **A\*** | ~14–16%（安全最难进） |
| ACM CCS | **CCS** | A | **A\*** | ~16–18% |
| USENIX Security Symposium | **USENIX Security** | A | **A\*** | ~29%（2024，投稿量大） |
| Network and Distributed System Security | **NDSS** | A | **A\*** | ~17% |
| International Cryptology Conference | **CRYPTO** | A | **A\*** | ~25% |
| EUROCRYPT | **EUROCRYPT** | A | **A\*** | ~25% |

### 5.1 安全"四大"

**S&P（Oakland）/ CCS / USENIX Security / NDSS** 合称"安全四大顶会"，CORE 全部 A\*。S&P（俗称 Oakland，因常在旧金山湾区举办）接收率最低 ~15%，是安全圈最难进的会。USENIX Security 近年因投稿量爆炸（3000+ 篇），绝对接收数最多但比率也升到 ~29%。

**经典与 AI 交叉**：
- **Bitcoin / 区块链**（S&P 2008 → 后续 CCS/USENIX Sec 大量论文）。
- **SSL/TLS 攻击**（BEAST、POODLE、Heartbleed 都首发于这些会场）。
- **AI Safety / Adversarial ML**：Goodfellow 的 FGSM、Carlini-Wagner 攻击、PGD 攻击、模型抽取（model extraction）、后门攻击（BadNets）、prompt injection——**几乎所有对抗机器学习里程碑都发在安全四大**而非 ML 会议。⭐**这是本卷 `08/04` 与 `09/02-alignment-safety` 的论文金矿**。
- **LLM 越狱（jailbreak）**、**红队（red-teaming）**、**DeepSeek/ChatGPT 漏洞**——USENIX Security 2024/2025 大量接收。

### 5.2 密码学双雄 CRYPTO / EUROCRYPT

IACR 主办的 CRYPTO 与 EUROCRYPT 是密码学理论顶会（与本卷 `06-theoretical-foundations` 强联动）。**AI 相关**：全同态加密（FHE）加速、隐私集合求交（PSI）、零知识证明（zk-SNARK）+ ML 推理——**联邦学习与隐私计算的理论基础**。

**投稿建议**：对抗 ML 工作投 S&P/USENIX Sec 接受率明显高于投 ICML/NeurIPS（后者对 attack 论文越来越挑剔）。新人可从 NeurIPS Workshop 的 Safe AI 起步。

---

## 六、编程语言 / 编译器（形式化方法 + AI 的黄金交叉）

> **联动章节**：`08-ai4x-applications/02-ai4compiler`、`04-synthesis/05-stagnation-and-innovation`、`06-theoretical-foundations`。

| 会议 | 缩写 | CCF | CORE | 近年接收率 |
|---|---|---|---|---|
| Programming Language Design and Implementation | **PLDI** | A | **A\*** | ~24–26% |
| Principles of Programming Languages | **POPL** | A | **A\*** | ~28–30% |
| OOPSLA | **OOPSLA** | A | A | ~25–30%（含 round） |
| International Conference on Functional Programming | **ICFP** | A | **A\*** | ~25% |
| Compiler Construction | **CC** | B | A | ~25% |
| Code Generation and Optimization | **CGO** | B | A | ~25% |
| Principles and Practice of Parallel Programming | **PPoPP** | B | A | ~25% |

### 6.1 PLDI / POPL —— PL 圈的双子星

PLDI（实现导向）与 POPL（理论导向）是编程语言圈最高会议。POPL 偏类型论、语义、程序逻辑（最"纯数学"的 CS 会议之一）；PLDI 偏编译器、运行时、JIT、静态分析。

**里程碑**：
- **LLVM**（PLDI 早期 + CGO 系列，Lattner & Adve）—— 现代 IR 的事实标准，Clang/Swift/Rust/Julia/Kotlin Native 都基于它。
- **MLIR**（**CGO 2021**，Lattner et al.）—— 多级中间表示，**本卷 `04-synthesis/05` 已一手核实**，是 AI 编译器（TensorFlow/XLA、PyTorch/Torch-MLIR、Mojo、TileLang）的统一底座。
- **Halide**（PLDI 2013）—— 计算/调度解耦，影响 TVM、Triton。
- **Triton**（**MAPL 2019**，无 arXiv，本卷已核实）—— OpenAI 的 GPU kernel DSL，v3 已成 LLM attention kernel 标配。
- **Exo**（**PLDI 2022** + **ASPLOS 2025**，arXiv:2411.07211）—— 可组合的硬件加速器调度语言。

**AI4Compiler 热点**：用 LLM 做代码生成（Copilot 背后的研究）、用 ML 做编译优化（自动 fusion、auto-scheduling）、形式化验证 + AI（Lean4 + LLM 做定理证明，对应本卷 `03-ai4math`）。⭐**这是本卷给用户建议的"编译器+形式化方法"黄金交叉方向**——POPL/PLDI/ITP 是主战场。

### 6.2 OOPSLA / ICFP / CC / CGO / PPoPP

OOPSLA（SPLASH 旗舰）接收面最广，含 round 后接收率可达 30%。ICFP 专做函数式（Haskell/OCaml 社区）。CC/CGO/PPoPP 是编译/并行子方向，CORE 都是 A，新人友好度高。

**投稿建议**：AI4Compiler 论文首选 PLDI/CC/CGO；纯形式化方法论文可投 POPL/ITP/CAV；并行计算投 PPoPP/SC。

---

## 七、理论计算机

> **联动章节**：`06-theoretical-foundations` 全部 7 章、`03-ai4math`。

| 会议 | 缩写 | CCF | CORE | 近年接收率 |
|---|---|---|---|---|
| ACM Symposium on Theory of Computing | **STOC** | A | **A\*** | ~30% |
| IEEE Symposium on Foundations of Computer Science | **FOCS** | A | **A\*** | ~28–30% |
| ACM-SIAM Symposium on Discrete Algorithms | **SODA** | A | **A\*** | ~30% |
| Symposium on Computational Geometry | **SoCG** | B | A | ~30% |
| IEEE Symposium on Logic in Computer Science | **LICS** | B | **A\*** | ~30% |
| International Colloquium on Automata, Languages and Programming | **ICALP** | B | A | ~25% |
| Conference on Learning Theory | **COLT** | - | **A\*** | ~30% |

### 7.1 STOC / FOCS / SODA —— 理论三巨头

STOC（ACM）与 FOCS（IEEE）是理论 CS 的"奥斯卡"，SODA 偏算法。三者 CORE 全部 A\*，接收率 ~30%（理论论文审稿靠"是否解决长期 open problem"而非实验）。

**里程碑**：
- **P vs NP**（Cook-Levin 定理，STOC 1971）。
- **PCP 定理**（FOCS/STOC 1990s）—— 近似算法硬度。
- **快速矩阵乘法**（Strassen → Coppersmith-Winograd → **AlphaTensor**，**Nature 610:47, 2022**，DOI 10.1038/s41586-022-05172-4，无 arXiv）—— ⭐**用 RL 发现矩阵乘法新算法，AI4Math 里程碑**，本卷已核实。
- **麻省理工 Vinod Vaikuntanathan / Zvika Brakerski** 的 FHE 理论（STOC/FOCS 常客）。

### 7.2 LICS / SoCG / ICALP / COLT

- **LICS**（CORE A\*）—— 逻辑与 CS 交叉，类型论、模型检测、形式化方法。
- **SoCG** —— 计算几何。
- **ICALP** —— 自动机、语言、程序，欧洲理论旗舰。
- **COLT**（Learning Theory，CORE A\*）—— **理论机器学习顶会**，泛化误差界、PAC 学习、online learning、bandit 理论。⭐**与本卷 `06-theoretical-foundations/01-learning-theory`、`/04-generalization-theory` 完全对应**。PAC-Bayes、NTK、double descent 等概念都首发于此。

**投稿建议**：理论功底强的工作投 STOC/FOCS；偏学习理论投 COLT/NeurIPS；可计算性/停机问题类工作（本卷 `06/06-computability-limits`）适合 LICS/JACM。

---

## 八、AI / ML 顶会（核心，与全部模块联动）

这是 AI 研究的主战场。本卷 10 大模块中至少 8 个的核心论文都在此发表。

### 8.1 综合 AI/ML

| 会议 | 缩写 | CCF | CORE | 近年接收率 | 频率 |
|---|---|---|---|---|---|
| Conference on Neural Information Processing Systems | **NeurIPS** | A | **A\*** | ~25–26%（2024≈25.8%） | 年 |
| International Conference on Machine Learning | **ICML** | A | **A\*** | ~27%（2024≈27.5%） | 年 |
| International Conference on Learning Representations | **ICLR** | - | **A\*** | ~31–32% | 年 |
| AAAI Conference on Artificial Intelligence | **AAAI** | A | **A\*** | ~20–23% | 年 |
| International Joint Conference on Artificial Intelligence | **IJCAI** | A | **A\*** | ~15–20% | 年 |
| **MLSys**（ML 系统） | **MLSys** | B | **A** | ~22% | 年 |

**NeurIPS / ICML / ICLR —— ML 三巨头**。NeurIPS（12 月，年度规模最大、投稿已破 1.5 万篇，本卷已核实第 38 届为 2024 温哥华 Dec 10–15）是综合影响力第一；ICML（7 月，本卷核实第 42 届为 2025 温哥华 Jul 13–19）偏算法与理论；ICLR（5 月）由 Bengio/LeCun 创立，主打 representation learning，**唯一采用 OpenReview 全公开评审**，是争议最大但透明度最高的会。

**里程碑（本卷已核实 arXiv ID）**：
- **AlexNet**（**NeurIPS 2012**）—— 深度学习革命的起点。
- **Transformer "Attention Is All You Need"**（**NeurIPS 2017**，arXiv:1706.03762）—— 一切现代大模型的基石。
- **BatchNorm**（**ICML 2015**）、**ResNet**（**CVPR 2016**，arXiv:1512.03385）、**Adam**（**ICLR 2015**，arXiv:1412.6980）—— 训练三件套。
- **BERT**（**NAACL 2019**，arXiv:1810.04805）、**GPT 系列** —— 预训练范式。
- **FlashAttention**（**NeurIPS 2022**，arXiv:2205.14135）、**Mamba**（**arXiv:2312.00752**，ICML 2024）、**Mamba-2**（arXiv:2405.21060）、**DiT**（**ICCV 2023**，arXiv:2212.09748）、**Jamba**（arXiv:2403.19887）—— 架构前沿，本卷 `04-synthesis/05` 全部一手核实。

**AAAI / IJCAI —— 传统 AI 综合**，覆盖符号 AI、知识表示、规划、多智能体，接收率 ~20%。CCF A 但学术声誉略低于三巨头，是国内学者主战场。

**MLSys**（CORE A，CCF B）—— **ML 系统专门会议**，介于系统与 ML 之间。vLLM 早期工作、DeepSpeed、NCCL 优化常落于此。⭐**本卷 `05-model-engineering` 的核心投稿目标**。

### 8.2 NLP

| 会议 | 缩写 | CCF | CORE | 近年接收率 |
|---|---|---|---|---|
| Association for Computational Linguistics | **ACL** | A | **A\*** | ~22–25% |
| Empirical Methods in NLP | **EMNLP** | B | **A\*** | ~22–25% |
| North American Chapter of ACL | **NAACL** | B | A | ~25% |
| International Committee on Computational Linguistics | **COLING** | B | A | ~30% |

**ACL / EMNLP —— NLP 双雄**。ACL（CORE A\*）是 NLP 之巅，EMNLP（CORE A\* 但 CCF 仅 B）主打实证方法，是 LLM 时代最火的会。BERT 首发于 NAACL、GPT 系列首发于 NeurIPS/preprint、ChatGPT 的技术报告多在 EMNLP/ACL 的 Workshop。**投稿建议**：LLM 应用、prompt engineering、RAG、agent 论文首选 EMNLP/ACL 的 Industry/Workshop track。

### 8.3 CV

| 会议 | 缩写 | CCF | CORE | 近年接收率 |
|---|---|---|---|---|
| Computer Vision and Pattern Recognition | **CVPR** | A | **A\*** | ~23%（2024≈23.6%，2025≈22%） |
| International Conference on Computer Vision | **ICCV** | A | **A\*** | ~20% |
| European Conference on Computer Vision | **ECCV** | B | A | ~30% |
| Winter Conference on Applications of Computer Vision | **WACV** | B | A | ~30% |

**CVPR / ICCV —— CV 双雄**。CVPR（年度，CORE A\*）是 CV 综合影响力第一，投稿已破 1.1 万篇，本卷核实第 2025 届为 Nashville Jun 11–15。ICCV（两年一次，奇数年）偏理论与基础。**里程碑**：ResNet（CVPR 2016）、YOLO、Mask R-CNN、ViT（ICLR 2021，arXiv:2010.11929）、CLIP（ICML 2021）、Stable Diffusion（ECCV 2022）、SAM（ICCV 2023）、3D Gaussian Splatting（**SIGGRAPH 2023**，arXiv:2308.04079）。⭐**与本卷 `07-extended-tech`、`10-emerging-fields` 强联动**。

### 8.4 数据挖掘 / Web

| 会议 | 缩写 | CCF | CORE | 近年接收率 |
|---|---|---|---|---|
| ACM SIGKDD | **KDD** | A | **A\*** | ~20% |
| The Web Conference | **WWW** | A | **A\*** | ~20% |
| Recommender Systems | **RecSys** | B | A | ~22% |
| Web Search and Data Mining | **WSDM** | B | **A\*** | ~16–20% |
| CIKM | **CIKM** | B | A | ~20% |

**KDD**（CORE A\*）是数据挖掘之巅，分 Research Track 与 Applied Data Science Track，后者接收率更高、偏工业落地。**WWW**（前 WWW，现 TheWebConf）覆盖 Web 规模系统 + 数据挖掘。**RecSys** 是推荐系统专门会。**WSDM**（CORE A\*，CCF 仅 B）是搜索与数据挖掘，接收率低、质量高。

### 8.5 强化学习 / 机器人

| 会议 | 缩写 | CCF | CORE | 近年接收率 |
|---|---|---|---|---|
| Robotics and Automation | **ICRA** | B | A | ~40% |
| Intelligent Robots and Systems | **IROS** | C | A | ~45% |
| Robotics: Science and Systems | **RSS** | - | **A\*** | ~25% |
| Conference on Robot Learning | **CoRL** | - | A | ~30% |

**机器人领域接收率普遍偏高**（ICRA ~40%、IROS ~45%），因为实验成本高、投稿基数相对小。**RSS**（CORE A\*）是机器人理论最高荣誉。**CoRL**（Pi-Abbeed 创立）专做机器人学习，是 RL+具身智能的主场，与本卷 `01-world-models`、`07-extended-tech` 直接对应。**经典**：AlphaGo（**Nature 2016**）、AlphaZero（**Science 2018**，arXiv:1712.01815）、RT-2（robotics transformer）、RT-X、OpenAI 的 Dactyl（SSP 域，ICRA）、Boston Dynamics 系列。

---

## 九、跨学科顶刊（Nature/Science 系列）

> **联动章节**：`02-ai4science`、`03-ai4math`、`10-emerging-fields`。

期刊与会议是完全不同的发表生态——**周期长（投稿到发表常 1–3 年）、审稿严（3–5 轮）、但影响因子极高、跨界传播力强**。AI4Science 的里程碑成果几乎都在 Nature/Science。

| 期刊 | 2023 IF（约） | 与 AI 的关系 |
|---|---|---|
| **Nature** | 50.5 | AlphaFold 1/2/3、AlphaGeometry、GNoME、rentosertib（INS018_055） |
| **Science** | 44.7 | GraphCast、IBM NorthPole 芯片 |
| **Cell** | 45.5 | AlphaFold 应用、医疗 AI、AlphaMissense |
| **Nature Machine Intelligence** | 23.8 | AI 专门期刊，方法论 + 应用 |
| **Nature Communications** | 14.7 | 多学科 AI 应用，接收率相对友好 |
| **Nature Methods** | 36.1 | AI 方法学（如 CryoEM、显微成像） |
| **Nature Physics** | 17.6 | AI + 物理交叉 |
| **PNAS** | 9.4 | 综合性，跨学科 |
| **JMLR**（开源） | 无正式 IF（~6–7 等效） | ML 纯理论顶刊，开源 |
| **TPAMI**（IEEE Trans on PAMI） | 20.8 | CV 顶刊，长文深度 |
| **TKDE**（IEEE Trans on KDE） | 8.9 | 数据库/数据工程顶刊 |
| **JACM**（Journal of the ACM） | ~3（低 IF 但声誉顶） | 理论 CS 顶刊 |

### 关键里程碑（本卷全部一手核实）

- **AlphaFold 2**（**Nature 596:583, 2021**）—— 蛋白质结构预测革命，DeepMind。
- **AlphaFold 3**（**Nature 630:493, 2024-05-08**，DOI 10.1038/s41586-024-07487-w）—— 扩展到所有生物分子相互作用。
- **AlphaGeometry**（**Nature 625:476, 2024**，DOI 10.1038/s41586-024-07412-w）—— IMO 几何题 AI。
- **GNoME**（**Nature 624:80, 2023-11-29**，DOI 10.1038/s41586-023-06735-9）—— 发现 220 万种新晶体材料。
- **GraphCast**（**Science 382:1416, 2023-11-14**，DOI 10.1126/science.adi2336）—— 10 天天气预报 AI。
- **IBM NorthPole**（**Science 2023**）—— 类脑推理芯片。
- **rentosertib (INS018_055)**（Phase III 启动 **NCT07687459，2026-07-07**）—— ⭐**首个 AI 设计药物进入 III 期临床**，本卷 `02-ai4science`、`synthesis/topic-07` 已重点核实。

**Nature Machine Intelligence** 是 2019 年创刊的 AI 专门子刊，IF 从首年的 ~25 逐步回落到 ~24，是 AI 方法论+应用的高质量期刊（接收率远比 Nature 友好）。**JMLR** 是 ML 圈唯一公认的纯期刊顶刊（开源、无 IF 但等效 ~6），长篇理论文章首选。**TPAMI** 是 CV 圈期刊天花板，长文 + 深度实验。

**投稿建议**：AI4Science 突破性成果冲 Nature/Science；扎实方法论投 NMI/Nature Methods；CV 长文投 TPAMI；不愿等 1 年审稿的会议派走 NeurIPS/CVPR。

---

## 十、特别说明：arXiv / OpenReview / Papers with Code

这三个不是会议也不是期刊，但**是当代 AI 研究不可或缺的基础设施**。

### 10.1 arXiv —— 预印本的事实标准

康奈尔大学运营（`arxiv.org`），免费、开放、无审稿。AI 领域 **>90% 顶会论文先发 arXiv**，平均比会议正式发表早 6–9 个月。**关键分类**：`cs.LG`（机器学习）、`cs.CL`（NLP）、`cs.CV`（CV）、`cs.RO`（机器人）、`cs.AI`、`stat.ML`（统计 ML）、`cs.DC`（分布式）、`cs.OS`（操作系统）。**Daily Papers（HuggingFace）** 每天从 arXiv 筛选高讨论度论文，是跟踪前沿的最佳工具。**注意**：arXiv 无同行评审，质量参差，引用前务必核对是否已被顶会/顶刊接收。

### 10.2 OpenReview —— 开放评审革命

`openreview.net`，由 ICLR 推广，现 NeurIPS Datasets & Benchmarks、CoRL、TMLR 等均采用。**特点**：审稿意见、作者 rebuttal、最终决定全部公开。优点是透明、可追溯；缺点是审稿人压力增大。**TMLR**（Transactions on Machine Learning Research，Yann LeCun 主导）是 OpenReview 上的纯期刊，无接收率限制（只要审稿通过即发），是 ML 长文新选择。

### 10.3 Papers with Code —— 论文 + 代码 + benchmark

`paperswithcode.com`，Meta 维护。每篇论文附代码 + 在各 benchmark 上的 SOTA 排名。**复现论文、找 baseline 必备**。本卷 `05-model-engineering` 强调"动手 > 输入"，Papers with Code 是动手起点。

---

## 十一、按本卷章节推荐阅读 / 投稿路径

| 本卷模块 | 首选顶会/顶刊 | 次选 | 关联议题 |
|---|---|---|---|
| `01-world-models` | NeurIPS, ICLR, CVPR, CoRL, RSS | ICCV, ICRA | 世界模型、视频生成、具身智能 |
| `02-ai4science` | **Nature, Science**, Nature Methods, Nature MI | NeurIPS, ICML | AlphaFold/GraphCast/GNoME 类 |
| `03-ai4math` | **ICLR, NeurIPS, Nature** | ICML, ITP, LICS | 定理证明、AlphaGeometry、AlphaTensor |
| `04-synthesis` | （跨学科） | - | 本卷综述章，引用全部 |
| `04/05-stagnation-and-innovation` | **ASPLOS, PLDI, MLSys, ISCA** | CC, CGO, SC | 编译器/硬件/系统红利 |
| `05-model-engineering` | **MLSys, NeurIPS**, ASPLOS, SOSP/OSDI | EuroSys, USENIX ATC | 训练/推理/部署系统 |
| `06-theoretical-foundations` | **STOC, FOCS, COLT**, NeurIPS | SODA, LICS, JACM | 学习理论、泛化、优化、可计算性 |
| `07-extended-tech` | NeurIPS, CVPR, ICCV, AISTATS | ECCV, WACV | 多模态、3D 生成、Agent |
| `08-ai4x-applications` | **OSDI, SOSP, SIGMOD, KDD, USENIX Security** | VLDB, ICDE, CCS, NDSS | OS/DB/Security/Compiler/EDA |
| `09-ai-philosophy-ethics` | **AIES, FAccT** | NeurIPS Ethics, IJCAI | AI 伦理、公平、对齐 |
| `10-emerging-fields` | 跨学科，看方向 | Nature/Science 子刊 | 神经科学、量子、教育、医疗、法律 |

### 11.1 补充会议（未列入主表但重要）

- **MLSys**（CCF-B，CORE A）—— ML 系统专门会议，本卷 `05-model-engineering` 核心。
- **COLT**（理论 ML，CORE A\*）—— 学习理论顶会，本卷 `06` 核心。
- **AIES**（AAAI/ACM Conference on AI, Ethics, and Society）—— AI 伦理。
- **FAccT**（ACM Conference on Fairness, Accountability, and Transparency）—— 公平、问责、透明。
- **AISTATS**（CORE A）—— 统计+ML 交叉，理论派主场。
- **ITP**（Interactive Theorem Proving）—— Lean4/Coq 定理证明，AI4Math 交叉。
- **CAV**（Computer Aided Verification）—— 形式化验证，与 AI 安全交叉。
- **ESEC/FSE**（CORE A\*）—— 软件工程顶会，AI4SE 主场（本卷 `08` 涉及 CodeGen）。
- **ICSE**（软件工程，CCF A）—— 软件工程之巅。
- **RECSYS** 已列；**SIGIR**（CORE A\*）—— 信息检索顶会，与推荐/RAG 强相关。

---

## 十二、给用户的投稿与跟踪建议

基于本卷定位（"应用数学研究型工程师"，每周 10–20 小时，6–8 年路径），给出**可执行的最小动作集**：

### 12.1 每日/每周/每月/每年节奏

- **每天（10 分钟）**：刷 arXiv `cs.LG` + `cs.CL` 的 HuggingFace Daily Papers，标题扫一遍，3 篇感兴趣的下 PDF 存档。
- **每周（1 小时）**：精读 1 篇本周爆款（看 Twitter/Reddit r/MachineLearning 热度），用李沐"三遍法"（本卷 `05-model-engineering/04` 已述）。
- **每月（2 小时）**：跟踪一个顶会的 accepted paper list（轮换：1 月 NeurIPS、3 月 ICLR、5 月 ICML、6 月 CVPR、7 月 ACL、11 月 EMNLP）。
- **每年（半天）**：等 CCF 推荐目录更新（通常 9 月）、Google Scholar Metrics 更新（每年中），核对关注会议的评级与 h5 变化。

### 12.2 五个必跟顶会 + 三个必跟期刊

**顶会**：**NeurIPS / ICML / ICLR / OSDI / SOSP**（前三盯 AI 方法，后两盯系统，构成"AI+系统"双轴）。
**期刊**：**Nature Machine Intelligence / JMLR / TPAMI**（一个跨界、一个理论、一个 CV 深度）。

### 12.3 投稿决策树（给未来真要投稿的你）

1. **是纯 AI 方法吗？** → NeurIPS/ICML/ICLR（按理论性排序：ICLR 最偏表示、ICML 最偏算法、NeurIPS 最综合）。
2. **是系统/工程问题吗？** → OSDI/SOSP（革命性）/ EuroSys/ATC/MLSys（扎实工程）。
3. **是 AI4Science 突破吗？** → Nature/Science（革命性）/ NMI/Nature Methods（方法学）。
4. **是纯理论吗？** → STOC/FOCS/COLT（算法/学习理论）/ JACM（长文）。
5. **是伦理/安全吗？** → AIES/FAccT（伦理）/ S&P/USENIX Sec（安全）。
6. **被顶会拒了怎么办？** → 看审稿意见改投次级（CVPR→ECCV/WACV、NeurIPS→AAAI/IJCAI、OSDI→EuroSys/ATC），或转 arXiv + Workshop 积累声誉。

### 12.4 三个反直觉的提醒

- **CCF A ≠ 必投**。MLSys 是 CCF B 但工业界承认度极高；WSDM/IMC 是 CCF B 但 CORE A\*；纯按 CCF 投会错过这些"隐藏顶会"。
- **接收率低 ≠ 难中**。S&P 15% 但投稿基数小（高质量安全研究）；USENIX Security 29% 但基数大（中稿绝对数更多）。看**绝对中稿数 + h5-index** 更准。
- **Nature IF 高 ≠ 适合所有工作**。AI 方法论论文投 Nature 多被拒（"不够广泛"）；投 NMI/TPAMI/NeurIPS 命中率高得多。**别被 IF 绑架**。

---

## 📌 进一步阅读

1. **CCF 推荐目录官网**：`https://www.ccf.org.cn/Academic_Evaluation/By_category/`（中国评审金标准，2022 版 + 2025 增量）。
2. **CORE / ICORE 排名门户**：`https://portal.core.edu.au/conf-ranks/`（国际第二意见，CORE 2023 最新，ICORE 2026 酝酿中）。
3. **Google Scholar Metrics**：`https://scholar.google.com/intl/en/scholar/metrics.html`（每年发布 h5-index 排名，按子领域）。
4. **Papers with Code**：`https://paperswithcode.com/`（论文+代码+benchmark SOTA）。
5. **Conference Acceptance Rate Tracker（社区维护）**：`https://github.com/lixin4ever/Conference-Acceptance-Rate`（接受率历史聚合，非官方但常用）。
6. **OpenReview**：`https://openreview.net/`（ICLR/NeurIPS D&B/TMLR 公开评审）。
7. **本卷联动章节**：
   - `04-synthesis/05-stagnation-and-innovation.md`（系统/编译器红利，含 TileLang/Triton/MLIR 一手核实）。
   - `06-theoretical-foundations/06-computability-limits.md`（可计算性边界）。
   - `08-ai4x-applications/07-computing-architecture-future.md`（体系结构未来）。
   - `08-ai4x-applications/02-ai4compiler.md`（AI4Compiler）。
   - `08-ai4x-applications/05-database-meets-ai.md`（Learned Index）。
   - `08-ai4x-applications/04-ai4security.md`（对抗 ML）。

---

## ✍️ 思考题（3 道）

1. **评级悖论**：MLSys 是 CCF B 但 CORE A 且工业界声誉极高；IMC 是 CCF B 但 CORE A\* 且 h5-index 极高。请用你自己的话解释：**为什么"单一评级体系"会失真？** 如果你要建立一个面向"应用数学研究型工程师"的个性化会议评分模型，你会纳入哪些维度（接收率、h5、工业引用、与你方向的匹配度……）？请给出一个加权公式草案。

2. **跨域迁移**：vLLM 把"操作系统虚拟内存/Paging"思想用到 KV Cache 管理（SOSP 2023），Learned Index 把"神经网络"用到数据库索引（SIGMOD 2018）。这两篇都是"把 A 领域成熟思想迁移到 B 领域"的典范。**请在本卷 10 大模块中，再找一对"看似无关但可互相借思想"的领域**（例如：编译器 ↔ 生物学中心法则？分布式共识 ↔ 神经元同步？），并构思一个具体的迁移研究问题。

3. **时间维度**：本表列出的接收率都是"近年的快照"。但若你拉长到 2012（AlexNet 年）到 2026（本卷成文），NeurIPS 接收率从 ~25% 几乎没变，投稿量却从 ~1500 涨到 ~15000（10 倍）。**这意味着什么？** 请分析：(a) 绝对中稿数 10 倍增长是否稀释了"NeurIPS 论文"的含金量？(b) 在投稿量暴涨、接收率恒定的背景下，审稿质量（false positive 率）是否在恶化？引用 `04-synthesis/05-stagnation-and-innovation.md` 中"范式红利衰减"的论述来支撑你的判断。

---

> **数据核实说明（2026-07-20）**：
> - CORE 2023 评级（A\*/A/B/C）已通过 ICORE 官方门户 `portal.core.edu.au/conf-ranks` 一手核实（A\* 占 7.65%，A 占 14.92%，B 占 28.06%，总计 784 个排名会议）。
> - CCF 评级基于 2022 第五版 + 2025 增量更新（`ccf.org.cn`）。
> - 各会议最新届数已官网核实：NeurIPS 2024 = 第 38 届（Vancouver, Dec 10–15）、ICML 2025 = 第 42 届（Vancouver, Jul 13–19）、CVPR 2025 = Nashville（Jun 11–15）。
> - 接受率为近年公开统计的稳定区间（2023–2025），具体年份略有波动，表中"~X%"为常态区间；精确到小数点的年度数据请查会议官网 Call for Papers 与 Program Committee 报告。
> - 影响因子为 2023 JCR（Journal Citation Reports）公开值，2024 JCR 数据于每年 6 月由 Clarivate 发布，2024 年末值与 2023 相近。
> - 所有本卷引用的 arXiv ID / DOI 均已在 `world-ai4sci-math` 各章节一手核实（如 FlashAttention 2205.14135、Mamba 2312.00752、AlphaFold 3 DOI 10.1038/s41586-024-07487-w、rentosertib NCT07687459）。

<!-- delegate 直接写入，2026-07-20 -->
