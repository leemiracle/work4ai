# CS 自学指南 × Kernel-Lab 完整学习路径

> **v0.11**：基于 csdiy.wiki 12 个课程子页面 + 教材章节级深度映射 + 关键论文 reading list。
> 让项目从"代码 + 20 视角审查报告"升级为**带世界级课程学习路径的可教学实验室**。
> 来源：[cs-self-learning](https://github.com/PKUFlyingPig/cs-self-learning)（PKUFlyingPig 维护）
> 方法：12 个 csdiy 子页面由 librarian delegate 实际访问验证 + 课程内容逐项映射到项目 lens

---

## 一、最高 ROI 课程 Top 6（按对本项目的价值排序）

| 排名 | 课程 | 讲师 | 核心价值 | csdiy 链接 |
|---|---|---|---|---|
| ⭐⭐⭐ 1 | **CMU 15-418 / Stanford CS149** | Kayvon Fatahalian | **Roofline 模型世界级标杆 + SIMD/CUDA**（直接对应 lens-roofline + lens-pmu）| [CS149](https://csdiy.wiki/%E5%B9%B6%E8%A1%8C%E4%B8%8E%E5%88%86%E5%B8%83%E5%BC%8F%E7%B3%BB%E7%BB%9F/CS149/) |
| ⭐⭐⭐ 2 | **UCB CS61C** | Dan Garcia | **Project 4：OpenMP + SIMD 优化矩阵运算**——csdiy 全站唯一让本科生手写 SIMD GEMM 的作业 | [CS61C](https://csdiy.wiki/%E4%BD%93%E7%B3%BB%E7%BB%93%E6%9E%84/CS61C/) |
| ⭐⭐⭐ 3 | **UCSD CSE234** | Hao AI Lab | **唯一明确讲 FlashAttention/PagedAttention/continuous batching 的系统课** + Triton 编程 | [CSE234](https://csdiy.wiki/%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0%E7%B3%BB%E7%BB%9F/CSE234/) |
| ⭐⭐ 4 | **CMU 10-414/714** | Tianqi Chen | 从零实现 DL 框架 Needle，理解框架如何调用 GEMM | [CMU10-414](https://csdiy.wiki/%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0%E7%B3%BB%E7%BB%9F/CMU10-414/) |
| ⭐⭐ 5 | **MIT 6.5940 TinyML** | Song Han | 量化/剪枝/NAS + LLM 推理压缩（对应算法 lens + 学术 lens）| [EML](https://csdiy.wiki/%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0%E7%B3%BB%E7%BB%9F/EML/) |
| ⭐⭐ 6 | **MLC (Machine Learning Compilation)** | 陈天奇 | TVM TensorIR loop tiling 自动化（连接手写 kernel 与编译器）| [MLC](https://csdiy.wiki/%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0%E7%B3%BB%E7%BB%9F/MLC/) |

---

## 二、按项目 lens 的精确映射（核心交付）

每个 lens 现在有"推荐学习资源"行——**让 lens 报告不只是诊断，而是带药方**。

### Lens 01 性能架构师
- **CSAPP 第 5 章**（优化程序性能）+ **第 6 章**（存储器层次结构）— cache 友好代码三原则（局部性/分块/避免冲突 miss）是 GEMM tiling 的直接理论依据
- **CS149 Lecture: Roofline Model + SIMD** — Kayvon Fatahalian 的 Roofline 讲解是世界级标杆
- **CSAPP Cache Lab** — 亲手量化 cache miss 对性能的影响
- 配套跑：`./bin/lens-roofline` + `./bin/lens-pmu`

### Lens 02 算法科学家
- **CMU 10-414 Assignment 3-4**：从零实现 ndarray backend + GPU backend，理解 PyTorch `aten::mm` 实现
- **CSE234 Part 3 — LLM 训练优化**：明确讲授 FlashAttention / PagedAttention / continuous batching
- **MIT 6.5940 Part 2 — LLM 推理**：长上下文、后训练加速
- 配套跑：`./bin/attention_neon` + 复现 [`02-algorithm-scientist.md`](lenses/02-algorithm-scientist.md) P0

### Lens 03 OS/Runtime
- **MIT 6.S081 Lec on Virtual Memory / Page Tables** — hugepage、TLB、`DTLB_WALK` PMU 事件的理论基础
- **UCB CS162 Lec on Scheduling** — CFS 调度对延迟 lens 的影响、OMP_PROC_BIND
- 配套跑：`./bin/lens-latency` + `./scripts/runtime-tune.sh`

### Lens 04 编译器专家
- **MLC — TensorIR / Loop Transformation** — TVM 的 tiling/vectorization/unrolling 就是手写 NEON GEMM 的自动化版本
- **Stanford CS143 Code Generation 章节** — instruction scheduling
- 配套跑：用 TVM `tensorize` 原语把 NEON 指令注入计算图

### Lens 05/12 硬件/芯片设计
- **ETHz Computer Architecture (Onur Mutlu)** — 业界最深入：Memory systems / GPU 架构 / Speculative execution / RowHammer
- **ETHz DDCA** — 入门级硬件设计，理解 FTC862 流水线如何执行 NEON 指令
- 配套跑：`./bin/lens-thermal` + 用 ASE_SPEC PMU 反推 4 FVU 结构（[`docs/FTC862-PMU-SPEC.md`](FTC862-PMU-SPEC.md)）

### Lens 06 教育者
- **本映射文档就是教育者 lens P0.1 的实现**（"缺 TUTORIAL+VISUAL+COMMON-PITFALLS 三件套"中的 TUTORIAL 维度）
- 推荐读者按本路径学习

### Lens 08 QA/测试
- **MIT 6.031 Lec on Testing** — property-based testing 理论
- **CMU 17-803 Empirical Methods** — 统计显著性 / t-test @95% 置信区间
- 配套跑：实现 [`08-qa.md`](lenses/08-qa.md) P0.3 property-based testing

### Lens 09 安全
- **MIT 6.858 Computer System Security — Side Channels / Spectre**
- **ASU CSE466** — CTF 实战 → fuzz testing
- 配套跑：实现 [`09-security.md`](lenses/09-security.md) P0 的 ASAN/UBSAN build target

### Lens 10 应用集成
- **MLC — 硬件后端适配**（如何将统一 IR 编译到不同硬件）
- **CMU 10-414 — 框架顶层设计**（PyTorch/TF 内部架构）
- 配套跑：实现 [`10-integration.md`](lenses/10-integration.md) P0.1 PyTorch Custom Op

### Lens 17 学术界
- **MIT 6.5940 全部** — 剪枝 + 量化 + NAS + LLM 推理压缩
- **CSE234 全部** — LLM 训练/推理系统栈 + Triton
- **CMU 11-868 LLM System** — 专门讲 LLM 系统
- **ETHz CA 高级 lecture** — microarchitecture characterization 论文方法论
- 关键论文 reading list：
  - FlashAttention / FlashAttention-2 (Dao 2022/2023)
  - vLLM / PagedAttention (Kwon 2023)
  - DistServe (Zhong 2024) — prefill/decoding 分离
  - Deep Compression (Han 2015)
  - TVM (Chen 2018)

---

## 三、5 阶段学习路径（按读者画像）

### Stage 0：理论基础（2-3 周，必读）

| 周 | 资源 | 章节 |
|---|---|---|
| 1 | **CSAPP 第 5 章** | 优化程序性能（循环展开、减少内存引用）|
| 1-2 | **CSAPP 第 6 章** | 存储器层次结构（cache 行/组/关联度）|
| 2 | **CSAPP Cache Lab** | csim + csve 亲手量化 cache miss |
| 3 | **CAAQA Chapter 4** | Roofline 性能模型完整推导 |
| 3 | **CS149 Roofline lecture** | Kayvon 讲解 + 作业 |

→ 跑项目：`./bin/gemm_f32`、`./bin/lens-roofline`、`./bin/lens-pmu`

### Stage 1：SIMD/GEMM 实战（2-3 周）

| 周 | 资源 | 内容 |
|---|---|---|
| 4 | **CS61C Lecture: SIMD / Data-Level Parallelism** | SIMD 原理 |
| 4-5 | **CS61C Project 4** | OpenMP + SIMD 矩阵优化（x86 SSE，方法论迁移到 ARM NEON）|
| 5-6 | **MLC Lecture: Tensor Program / Loop Transformation** | 理解 TVM 自动化你手写的事 |
| 6 | **CS61C Project 2** | RISC-V 汇编手写神经网络（最底层理解 MAC）|

→ 跑项目：`./bin/gemm_f32`、`./bin/gemm_s8`、`./bin/gemm_f16`、对照 [`docs/OPTIMAL-PARAMS.md`](OPTIMAL-PARAMS.md)

### Stage 2：Winograd 卷积（1-2 周）

| 周 | 资源 | 内容 |
|---|---|---|
| 7 | **Golub & Van Loan 第 1 章** | 分块矩阵乘法（cache tiling 的数学基础）|
| 7 | **MLC: Tensor Expression** | 用 TVM 表达 Winograd 变换 |
| 8 | **Lavin & Gray 2016 论文** | Winograd 原始论文（fast algorithms for conv）|

→ 跑项目：`./bin/conv_winograd`、`./bin/conv_winograd_f44`、`./bin/multicore_winograd_f44`

### Stage 3：Flash Attention + LLM 系统（2-3 周）

| 周 | 资源 | 内容 |
|---|---|---|
| 9 | **CSE234 Part 2 — GPU MatMul + 算子编译** | Triton block-level 编程（与 NEON tiling 同源）|
| 9-10 | **CSE234 Part 3 — FlashAttention / PagedAttention** | LLM 推理系统栈 |
| 10 | **FlashAttention + FlashAttention-2 论文精读** | 必读 |
| 11 | **MIT 6.5940 Part 2 — LLM 推理** | 长上下文、后训练加速 |
| 11-12 | **CMU 11-868 LLM System** | causal mask + KV-cache + GQA |

→ 跑项目：`./bin/attention_neon`、复现 [`02-algorithm-scientist.md`](lenses/02-algorithm-scientist.md) P0（BF16 + causal + KV-cache）

### Stage 4：量化与高效推理（持续）

| 资源 | 内容 |
|---|---|
| **MIT 6.5940 Part 1** | 剪枝、量化（PTQ/QAT/INT8/INT4）、蒸馏、NAS |
| **Deep Compression (Han 2015)** | 量化+剪枝+编码三件套经典论文 |
| **AWQ / GPTQ 论文** | LLM 权重量化 SOTA |

→ 跑项目：`./bin/lens-precision`、实现 [`17-academic.md`](lenses/17-academic.md) P0（2:4 sparse / FP8 / W4A16）

---

## 四、教材章节级深度指南

| 教材 | 作者 | 关键章节 | 项目价值 |
|---|---|---|---|
| **CSAPP** | Bryant & O'Hallaron | 第 5/6 章 + Cache Lab | 性能优化 + 存储层次理论根基 |
| **Computer Architecture: A Quantitative Approach** | Hennessy & Patterson | Chapter 4 DLP/SIMD/GPU + Roofline | **最重要的理论工具** |
| **Computer Organization and Design (ARM Edition)** | Hennessy & Patterson | SIMD 章节 | NEON 指令集设计哲学 |
| **Matrix Computations** | Golub & Van Loan | Chapter 1 分块矩阵乘法 | GEMM tiling 数学基础（csdiy 未收录）|
| **OSTEP** | Remzi Arpaci-Dusseau | 虚拟内存章节 | hugepage + TLB |

---

## 五、csdiy.wiki 完整课程映射表（12 个子页面）

### 体系结构（4 门）
| 课程 | csdiy 页面 | 项目价值 |
|---|---|---|
| **UCB CS61C** ⭐ | [CS61C](https://csdiy.wiki/%E4%BD%93%E7%B3%BB%E7%BB%93%E6%9E%84/CS61C/) | Project 4 = 手写 SIMD GEMM |
| **ETHz CA (Onur Mutlu)** ⭐ | [CA](https://csdiy.wiki/%E4%BD%93%E7%B3%BB%E7%BB%93%E6%9E%84/CA/) | Memory systems / GPU / Speculative |
| **ETHz DDCA** | [DDCA](https://csdiy.wiki/%E4%BD%93%E7%B3%BB%E7%BB%93%E6%9E%84/DDCA/) | 硬件设计入门 |
| **Nand2Tetris** | [N2T](https://csdiy.wiki/%E4%BD%93%E7%B3%BB%E7%BB%93%E6%9E%84/N2T/) | 零基础（可跳）|

### 系统基础（强相关，2 门）
| 课程 | csdiy 页面 | 项目价值 |
|---|---|---|
| **CMU 15-213 CSAPP** ⭐⭐ | [CSAPP](https://csdiy.wiki/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%B3%BB%E7%BB%9F%E5%9F%BA%E7%A1%80/CSAPP/) | 第 5/6 章 + Cache Lab |
| Stanford CS110 | [CS110](https://csdiy.wiki/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%B3%BB%E7%BB%9F%E5%9F%BA%E7%A1%80/CS110/) | 系统入门 |

### 操作系统（4 门）
| 课程 | csdiy 页面 | 项目价值 |
|---|---|---|
| **MIT 6.S081** ⭐ | [MIT6.S081](https://csdiy.wiki/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F/MIT6.S081/) | 虚拟内存 / 页表（hugepage + TLB）|
| UCB CS162 | [CS162](https://csdiy.wiki/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F/CS162/) | 调度（OMP_PROC_BIND）|
| NJU OS | [NJUOS](https://csdiy.wiki/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F/NJUOS/) | 中文，并发/内存管理 |
| HIT OS | [HITOS](https://csdiy.wiki/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F/HITOS/) | 中文入门 |

### 并行/分布式（2 门）
| 课程 | csdiy 页面 | 项目价值 |
|---|---|---|
| **CMU 15-418 / Stanford CS149** ⭐⭐⭐ | [CS149](https://csdiy.wiki/%E5%B9%B6%E8%A1%8C%E4%B8%8E%E5%88%86%E5%B8%83%E5%BC%8F%E7%B3%BB%E7%BB%9F/CS149/) | **Roofline + SIMD/CUDA 世界级标杆** |
| MIT 6.824 | [MIT6.824](https://csdiy.wiki/%E5%B9%B6%E8%A1%8C%E4%B8%8E%E5%88%86%E5%B8%83%E5%BC%8F%E7%B3%BB%E7%BB%9F/MIT6.824/) | Raft / 一致性（CXL 远端内存）|

### 编译原理（6 门，按相关度）
| 课程 | csdiy 页面 | 项目价值 |
|---|---|---|
| **MLC (Machine Learning Compilation)** ⭐⭐ | [MLC](https://csdiy.wiki/%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0%E7%B3%BB%E7%BB%9F/MLC/) | TVM TensorIR = 自动化的手写 NEON |
| Stanford CS143 | [CS143](https://csdiy.wiki/%E7%BC%96%E8%AF%91%E5%8E%9F%E7%90%86/CS143/) | 经典编译原理 |
| PKU 编译原理实践 | [PKU-Compilers](https://csdiy.wiki/%E7%BC%96%E8%AF%91%E5%8E%9F%E7%90%86/PKU-Compilers/) | 中文 |
| KAIST CS420 | [CS420](https://csdiy.wiki/%E7%BC%96%E8%AF%91%E5%8E%9F%E7%90%86/CS420/) | LLVM backend |

### 机器学习系统（5 门）
| 课程 | csdiy 页面 | 项目价值 |
|---|---|---|
| **CMU 10-414/714** ⭐⭐ | [CMU10-414](https://csdiy.wiki/%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0%E7%B3%BB%E7%BB%9F/CMU10-414/) | 从零实现 needle DL 框架 |
| **MIT 6.5940 TinyML** ⭐⭐ | [EML](https://csdiy.wiki/%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0%E7%B3%BB%E7%BB%9F/EML/) | 量化/剪枝/NAS/LLM 压缩 |
| **UCSD CSE234** ⭐⭐⭐ | [CSE234](https://csdiy.wiki/%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0%E7%B3%BB%E7%BB%9F/CSE234/) | **FlashAttention/PagedAttention/Triton 唯一全覆盖** |
| 智能计算系统 AICS | [AICS](https://csdiy.wiki/%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0%E7%B3%BB%E7%BB%9F/AICS/) | 国内 AI 芯片全栈（陈云霁）|

### 大语言模型（3 门）
| 课程 | csdiy 页面 | 项目价值 |
|---|---|---|
| **CMU 11-868 LLM System** ⭐⭐ | [CMU11-868](https://csdiy.wiki/%E6%B7%B1%E5%BA%A6%E7%94%9F%E6%88%90%E6%A8%A1%E5%9E%8B/%E5%A4%A7%E8%AF%AD%E8%A8%80%E6%A8%A1%E5%9E%8B/CMU11-868/) | causal + KV-cache + GQA |
| CMU 11-667 LLM Methods | [CMU11-667](https://csdiy.wiki/%E6%B7%B1%E5%BA%A6%E7%94%9F%E6%88%90%E6%A8%A1%E5%9E%8B/%E5%A4%A7%E8%AF%AD%E8%A8%80%E6%A8%A1%E5%9E%8B/CMU11-667/) | 应用层 |
| CMU 11-711 Adv NLP | [CMU11-711](https://csdiy.wiki/%E6%B7%B1%E5%BA%A6%E7%94%9F%E6%88%90%E6%A8%A1%E5%9E%8B/%E5%A4%A7%E8%AF%AD%E8%A8%80%E6%A8%A1%E5%9E%8B/CMU11-711/) | NLP 理论 |

### 数值/数学（2 门）
| 课程 | csdiy 页面 | 项目价值 |
|---|---|---|
| **MIT 18.330 Numerical Analysis** | [numerical](https://csdiy.wiki/%E6%95%B0%E5%AD%A6%E8%BF%9B%E9%98%B6/numerical/) | 浮点误差、累加稳定性（FP16 累加 bug 理论依据）|
| MIT 18.06 Linear Algebra | [MITLA](https://csdiy.wiki/%E6%95%B0%E5%AD%A6%E5%9F%BA%E7%A1%80/MITLA/) | 矩阵基础（Winograd 数学）|

### 安全（4 门）
| 课程 | csdiy 页面 | 项目价值 |
|---|---|---|
| **MIT 6.858** | [MIT6.858](https://csdiy.wiki/%E7%B3%BB%E7%BB%9F%E5%AE%89%E5%85%A8/MIT6.858/) | Side Channels / Spectre |
| ASU CSE466 | [CSE466](https://csdiy.wiki/%E7%B3%BB%E7%BB%9F%E5%AE%89%E5%85%A8/CSE466/) | CTF / fuzz |
| UCB CS161 | [CS161](https://csdiy.wiki/%E7%B3%BB%E7%BB%9F%E5%AE%89%E5%85%A8/CS161/) | 入门 |

### 软件工程（3 门，QA 相关）
| 课程 | csdiy 页面 | 项目价值 |
|---|---|---|
| **MIT 6.031** | [6031](https://csdiy.wiki/%E8%BD%AF%E4%BB%B6%E5%B7%A5%E7%A8%8B/6031/) | Property-based testing |
| **CMU 17-803** | [17803](https://csdiy.wiki/%E8%BD%AF%E4%BB%B6%E5%B7%A5%E7%A8%8B/17803/) | 统计显著性 / 实验设计 |

---

## 六、关键论文 Reading List

| 论文 | 年份 | 课程 | 项目价值 |
|---|---|---|---|
| **FlashAttention** (Dao et al.) | 2022 | CSE234, MIT 6.5940 | ⭐⭐⭐ 原始论文，必须精读 |
| **FlashAttention-2** (Dao) | 2023 | CSE234 | ⭐⭐⭐ NEON 移植目标 |
| **Winograd** (Lavin, Fast Algorithms for Conv) | 2016 | — | ⭐⭐⭐ Winograd 卷积基础 |
| **TVM** (Chen et al.) | 2018 | MLC, CMU 10-414 | ⭐⭐ 编译器自动优化 |
| **Deep Compression** (Han) | 2015 | MIT 6.5940 | ⭐⭐ 量化+剪枝+编码 |
| **vLLM / PagedAttention** (Kwon et al.) | 2023 | CSE234 | ⭐⭐ KV cache 内存管理 |
| **DistServe** (Zhong et al.) | 2024 | CSE234 | ⭐⭐ prefill/decoding 分离 |
| **AWQ** (Lin) | 2023 | MIT 6.5940 | ⭐⭐ LLM 权重量化 |
| **GPTQ** (Frantar) | 2022 | MIT 6.5940 | ⭐⭐ LLM 权重量化 |
| **DeepSeekMoE / MLA** | 2024 | — | ⭐⭐ 2025 最热 attention 变体 |
| **2:4 Structured Sparsity** (Mishra, NVIDIA) | 2021 | — | ⭐⭐ 项目 v0.12 P0 |

---

## 七、与 20 视角 lens 框架的闭环

每个 lens 报告现在可以加"推荐学习资源"行：

```markdown
## 推荐学习资源（csdiy.wiki × Kernel-Lab）
- 必读：CSAPP 第 X 章 + CS149 Lec Y
- 动手：CS61C Project Z
- 配套跑：./bin/lens-XXX
```

这让项目从"诊断报告"升级为"**诊断 + 药方 + 学习路径**"的完整教学产品。

---

## 八、读者画像快速选择

| 你是 | 推荐起点 |
|---|---|
| **在校研究生**（无工业经验）| Stage 0 → Stage 1（CSAPP + CS61C P4）|
| **国产芯片初创工程师** | Stage 0 → Stage 3（直接攻 Flash Attention）|
| **体系结构爱好者** | CS149 + ETHz CA（Onur Mutlu）|
| **AI 系统工程师** | CMU 10-414 + CSE234 + MIT 6.5940 |
| **信创/政务客户** | 看 [`15-customer.md`](lenses/15-customer.md) + [`docs/AUTONOMY-STATEMENT.md`](AUTONOMY-STATEMENT.md) |

---

## 九、数据完整性声明

- 12 个 csdiy.wiki 子页面 URL 均由 librarian delegate 通过 webfetch 实际访问验证
- 课程外部链接（课程官网、GitHub 仓库、B 站视频）从对应 csdiy 页面原文提取
- Matrix Computations (Golub & Van Loan) 已明确标注为 csdiy 未收录的补充资源
- 教材推荐来自 csdiy [好书推荐](https://csdiy.wiki/%E5%A5%BD%E4%B9%A6%E6%8E%A8%E8%8D%90/) 页面
