# 项目 lens × csdiy 课程 精确映射矩阵

> **v0.14 核心交付**：把项目 20 个 lens 的每个盲区/P0 建议，精确映射到 csdiy 的具体课程章节/Project/论文。
> 让每个 lens 报告变成"**诊断 + 药方 + 学习路径 + 精确到课程章节**"的完整闭环。
> 与 v0.11 LEARNING-PATH 互补：那是按时间排序的学习路径，本文件是按 lens 排序的精确映射。

---

## 一、映射矩阵（核心）

每个 lens 的 P0 改造，对应 csdiy 的**哪些课程的哪些具体章节/Project**。

### Lens 01：性能架构师（5 个 P0 全部映射）

| Lens P0 建议 | csdiy 课程 | 具体章节/Project |
|---|---|---|
| P0.1 GEMM 内核加 software prefetch | **CSAPP 第 5.7 节** + **CS149 Lec 11** | "Understanding Memory Hierarchy Effects" / "Improving Locality" |
| P0.2 NR 维 + KC blocking（宏内核参数）| **CS149 Lec 2-3** + **CSAPP 第 6.4 节** | "Work/Span/Locality" / cache-friendly code 三原则 |
| P0.3 posix_memalign + hugepage | **MIT 6.S081 Lec 15（Virtual Memory）** + **CSAPP 第 9.7 节** | Page tables / TLB / hugepage 设计 |
| 多核 57% 真因诊断 | **CS149 Lec 11（Performance Optimization）** + **ETHz CA Memory Systems** | "Multi-core scaling" / DRAM bandwidth wall |
| Roofline 定量 | **CS149 Lec on Roofline** + **CAAQA Chapter 4** | "Roofline Model" / "Operational Intensity" |

### Lens 02：算法科学家（8 个盲区映射）

| Lens 盲区 | csdiy 课程 | 具体章节 |
|---|---|---|
| BF16 缺失 | **CMU 15-779**（路线图隐藏课）+ **MIT 6.5940 Lec on Quantization** | "BF16/FP8 hardware support" |
| Attention 是玩具版 | **CMU 11-868 A1-A2** + **CSE234 Part 3** | "causal mask / KV-cache / GQA / Flash-Decoding" |
| FP16 在 FP16 累加是算法错误 | **MIT 18.330 Chapter on Floating Point** | "Floating point representation, round-off error" |
| 缺 dequant-on-the-fly GEMM | **MIT 6.5940 Lab 1（Quantization）** + **CMU 11-868 A3** | "W8A16 weight-only quantization" |
| 量化 per-tensor 远离 SOTA | **MIT 6.5940 Lec on Quantization** + **AWQ/GPTQ 论文** | "per-channel / per-group / outlier-aware" |
| 缺 RoPE/RMSNorm/SwiGLU | **CMU 11-868 A2 (GPT2 构建)** | "from-scratch Transformer block" |
| 在线 softmax 稳定性 | **MIT 18.330** + **FlashAttention 论文** | numerical stability of online softmax |
| 缺 INT4/W4A16 | **MIT 6.5940 Lab 4（LLM 压缩）** | "W4A16 weight quantization" |

### Lens 03：OS/Runtime（8 盲区映射）

| Lens 盲区 | csdiy 课程 | 具体章节 |
|---|---|---|
| governor 未锁 | **MIT 6.S081 Lec on Scheduling** + **CS162** | CPU scheduling / DVFS |
| 零线程绑定 | **CS149 Lec on Addressing Mapping** | "thread affinity / locality" |
| 内存对齐缺失 | **CSAPP 第 6.3 节** | "Memory alignment" |
| Hugepage/TLB 未量化 | **MIT 6.S081 Lec 15（Page Tables）** | TLB / hugepages |
| context-switches/cpu-migrations 未采 | **MIT 6.S081 Lec on Scheduling** | CFS / context switch cost |
| MC×NC 分块缺失 | **CS149 Lec 2-3** | "Data partitioning / cache-aware tiling" |
| IRQ/irqbalance 未隔离 | **MIT 6.S081 Lec on Interrupts** | hardware interrupt handling |
| 拓扑定性错误 | **CSAPP 第 6.4 节** | cache coherence / NUMA |

### Lens 04：编译器（8 盲区映射）

| Lens 盲区 | csdiy 课程 | 具体章节 |
|---|---|---|
| PhyGCC vs clang 零横评 | **Stanford CS143 Code Generation** | instruction scheduling / register allocation |
| -ffast-math 未测 | **MIT 18.330** | "FP contraction / FMA semantics" |
| Auto-vectorize 未对比 | **MLC Lec on Tensor Program** | "auto-vectorization vs tensorize" |
| -march vs -mcpu | **CSAPP 第 5 章** | "machine-dependent optimization" |
| FP16 反直觉 codegen 根因 | **Stanford CS143 Instruction Scheduling** | "register pressure / spill" |
| LTO/PGO 零探索 | **Stanford CS143** | "interprocedural optimization" |
| Cross-compilation 矩阵 | **MLC Hardware Backend** | "compile to different hardware" |
| SVE 探测缺失 | **ETHz CA Lec on SIMD** | "SVE vs NEON design tradeoff" |

### Lens 05/12：硬件/芯片设计（8+8 盲区映射）

| Lens 盲区 | csdiy 课程 | 具体章节 |
|---|---|---|
| 4 FVU 结构未定性 | **ETHz CA (Onur Mutlu) Lec on Microarchitecture** | "pipeline / FVU datapath" |
| L3 双段拓扑未验证 | **ETHz CA Lec on Memory Systems** | "cache topology / coherence" |
| vs Cortex-A78 横评 | **CAAQA Chapter 4** | "ARM Cortex vs custom core" |
| PVT 变频曲线未测 | **ETHz CA Lec on VLSI** | "PVT variation" |
| MTBF/可靠性 | **ETHz CA Lec on Reliability** | "soft errors / ECC" |
| Spectre 缓解状态 | **MIT 6.858 Lec on Speculative Execution Attacks** | "Spectre/Meltdown mitigations" |
| Cache coherence 性能 | **CS149 Lec on Coherence** | "MESI protocol performance" |
| 功耗能效未量化 | **MIT 6.5940 Lec on Efficient Computing** | "performance per watt" |

### Lens 06：教育者（已部分实现）

| Lens P0 | 已落地 |
|---|---|
| TUTORIAL.md（5 步教学）| 部分（csdiy 路径本身就是教程）|
| VISUAL-INTUITION.md（图解）| ⏳ 待做 |
| COMMON-PITFALLS.md（陷阱清单）| ⏳ 待做 |

### Lens 07：DevOps/SRE（8 盲区映射）

| Lens 盲区 | csdiy 课程 | 具体章节 |
|---|---|---|
| CI 跑 Graviton 不是 D3000 | （csdiy 无 CI/CD 课，参考 GitHub Actions 文档）| — |
| 性能回归零防护 | **MIT 6.031 Lec on Testing** + **CMU 17-803** | "performance regression testing" |
| 制品发布是死的 | **Docker csdiy 课** | "containerization best practice" |
| 零容器化 | **csdiy Docker 工具页** | Docker basics |
| 无 metrics 暴露 | （csdiy 无 Prometheus 课）| 参考 Prometheus 官方文档 |
| 配置全硬编码 | **MIT 6.031 Lec on Configuration** | "configuration management" |
| 零 release 工程 | （csdiy 无 release engineering 课）| 参考 commitizen/release-please |

### Lens 08：QA（8 盲区映射）

| Lens 盲区 | csdiy 课程 | 具体章节 |
|---|---|---|
| 覆盖率 0.006% | **MIT 6.031 Lec on Testing** | "code coverage / partitioning" |
| 无 randomized testing | **MIT 6.031** | "random testing" |
| 零 property-based testing | **MIT 6.031** + **CMU 17-803** | "property-based testing" |
| 无跨平台 golden oracle | **CMU 10-414 A3** | "ndarray backend as reference" |
| tolerance 策略错误 | **MIT 18.330 Chapter on Error Analysis** | "ULP / relative error" |
| 无 perf regression | **CMU 17-803** | "empirical methods / t-test" |
| 无 sanitizer | （csdiy 无 ASAN/UBSAN 专题课）| 参考 ASAN docs |
| CI 矩阵为空 | **MIT 6.031 Lec on Continuous Integration** | "CI matrix" |

### Lens 09：安全（8 盲区映射）

| Lens 盲区 | csdiy 课程 | 具体章节 |
|---|---|---|
| malloc 零 NULL check | **MIT 6.031** + **CSAPP 第 9 章** | "defensive programming" |
| 整数溢出 | **MIT 6.031** | "integer overflow (CWE-190)" |
| 未初始化内存 | **CSAPP 第 9 章** | "memory safety" |
| NaN/Inf 链路 | **MIT 18.330** | "numerical edge cases" |
| 无 ASAN/UBSAN | （参考 csdiy 安全类 ASU CSE466）| "memory safety tools" |
| NEON 时序侧信道 | **MIT 6.858 Lec on Side Channels** | "timing attacks" |
| Spectre v1/v4 缓解 | **MIT 6.858 Lec on Speculative Attacks** | "Spectre v1/v4 mitigation" |
| DoS 攻击面 | **MIT 6.858** | "input validation" |

### Lens 10：应用集成（8 盲区映射）

| Lens 盲区 | csdiy 课程 | 具体章节 |
|---|---|---|
| 零 header/导出符号 | **Stanford CS106L** | "C++ API design / ABI" |
| kernel 与 driver 耦合 | **CMU 10-414 Architecture** | "separation of concerns" |
| 无 .so/.a 产物 | **csdiy GNU Make** | "shared/static library" |
| 无 tensor abstraction | **CMU 10-414 Needle NDArray** | "tensor abstraction design" |
| 无 zero-copy | **CMU 10-414 Backend** | "memory management" |
| 无 error handling | **MIT 6.031** | "error handling patterns" |
| 无 ABI versioning | **Stanford CS106L** | "ABI stability" |
| 无框架 binding | **MLC** | "framework integration" |

### Lens 11：政策（csdiy 无对应课程）

→ 需政法专业资料，csdiy 不覆盖。

### Lens 13：市场（csdiy 无对应课程）

→ 需商学院资料。

### Lens 14：规范/标准（csdiy 部分覆盖）

| Lens 盲区 | csdiy 课程 | 具体章节 |
|---|---|---|
| MISRA Rule 21.3 全违反 | **NJU 软件分析** | "static analysis rules" |
| CERT C 违规 | **NJU 软件分析** + **PKU 软件分析** | "vulnerability detection" |
| 国密算子零实现 | （csdiy 无国密课）| 参考 GM/T 标准 |
| MLPerf 零跑分 | **CSE234** | "ML benchmarking" |

### Lens 15：客户（csdiy 无对应课程）

→ 需产品管理资料。

### Lens 16：供应链（csdiy 无对应课程）

→ 需半导体工业资料。

### Lens 17：学术界（覆盖最广，每个 P0 都有对应课程）

| Lens P0 | csdiy 课程 | 具体章节 |
|---|---|---|
| Flash-Decoding | **CSE234 Part 3** + **CMU 15-779** | "Flash-Decoding (Dao 2023)" |
| 2:4 Structured Sparsity | **MIT 6.5940 Lec on Pruning** | "2:4 structured sparsity (NVIDIA)" |
| BF16 + causal + KV-cache + GQA | **CMU 11-868 A1-A2** | "from-scratch GQA attention" |
| DeepSeek MLA | **CMU 15-779** + **MIT 6.5940** | "MLA low-rank KV compression" |
| W4A16 | **MIT 6.5940 Lab 4** | "W4A16 weight-only quantization" |
| FP8 软件模拟 | **MIT 6.5940** | "FP8 (E4M3/E5M2)" |
| FlexAttention | **CMU 15-779** | "block-mask framework" |
| SVE2/SME 探测 | **ETHz CA** | "ARMv9 ISA evolution" |
| CXL 分级内存 | **MIT 6.824** | "distributed memory" |
| PIMulator | **ETHz CA Lec on PIM** | "Processing-in-Memory" |

---

## 二、按"想学 X，看哪门课"的反向索引

| 想学的技能/概念 | 推荐 csdiy 课程 |
|---|---|
| **写 SIMD GEMM kernel** | CSAPP 第 5/6 章 → CS61C Project 4 → MLC TensorIR |
| **理解 Roofline** | CS149 Lec on Roofline → CAAQA Chapter 4 |
| **手写 Flash Attention** | CSE234 Part 3 → CMU 15-779 → FlashAttention 论文 |
| **量化模型部署** | MIT 6.5940 → CMU 11-868 A3 → AWQ/GPTQ 论文 |
| **TVM 编译器** | MLC → CMU 10-414 |
| **hugepage/TLB 优化** | MIT 6.S081 Lec 15 → CSAPP 第 9 章 |
| **多核并行** | CS149 → CSAPP 第 12 章 |
| **侧信道/Spectre** | MIT 6.858 → ASU CSE466 |
| **数据库 buffer pool**（对应 KV-cache）| CMU 15-445 |
| **编译器 codegen** | Stanford CS143 → MLC |
| **从零造 LLM** | Karpathy NN:Z2H → Stanford CS336 → CMU 11-868 |
| **国产 AI 芯片全栈** | AICS（陈云霁）|

---

## 三、按读者时间的最小学习集

### 1 周版本（紧急补课）

只看：
1. **CSAPP 第 5/6 章**（性能优化 + 存储层次）
2. **CS149 Roofline lecture**
3. **MIT 18.330 浮点章节**

→ 能理解项目 v0.8 的 GEMM MR=8 + Roofline lens + FP16 反直觉发现

### 1 个月版本（深度补课）

加：
4. **CS61C Project 4**（手写 SIMD GEMM）
5. **CSE234 Part 2-3**（FlashAttention + Triton）
6. **FlashAttention 论文精读**

→ 能复现项目 GEMM + Attention 优化

### 3 个月版本（接近 SOTA）

加：
7. **CMU 10-414 全部 5 个 Assignment**
8. **MIT 6.5940 全部**
9. **CMU 11-868 全部**
10. **ETHz CA (Onur Mutlu) Memory Systems**
11. **MLC TensorIR**

→ 能独立做项目 v0.11 P0 升级（BF16 + causal + KV-cache + 量化 + SDK 化）

---

## 四、与 v0.11 LEARNING-PATH 的关系

| 文档 | 视角 | 适用 |
|---|---|---|
| **v0.11 LEARNING-PATH** | 按时间排序的学习路径（5 阶段）| 想系统学习的读者 |
| **v0.14 本文件** | 按 lens 排序的精确映射（20 视角）| 已读 lens 报告，想精确学某章 |
| **v0.12 FULL-INDEX** | 80+ 门速查表 | 选课时查阅 |

三个文档**互补**：路径 + 速查 + 精确映射 = 完整教学体系。
