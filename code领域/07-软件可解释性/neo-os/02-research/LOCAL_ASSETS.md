# Neo-OS · 本地资产索引

> 本地（`/mnt/c/workspace/`）已有的大量 AI、系统、硬件资料是 Neo-OS 的现成弹药库。本文档索引这些资产，并标注每项对 Neo-OS 的具体用途。
>
> 核心原则：**work4ai 不仅是知识库，更是"用大模型讲透复杂领域"的方法论本身**——这套方法论是 Neo-OS 解释引擎的内核。

---

## 一、work4ai（60+ 讲透主题）——Neo-OS 的方法论内核 + 能力资产库

`/mnt/c/workspace/work4ai/` 共 613 篇 / 8 万字，每个主题按「三层讲解 × 17 视角 × 费曼检验」体系组织。

### A. 方法论本身（Neo-OS 解释引擎的灵魂）

| 资产 | 路径 | 对 Neo-OS 的用途 |
|------|------|-----------------|
| **费曼学习法 skill** | `work4ai/费曼学习法/skill/SKILL.md` | 解释引擎的生成-护栏-验收闭环方法论 |
| **费曼检验模板** | `work4ai/费曼学习法/费曼检验模板.md` | L3 输出的质量门（F1-F4）|
| **17 视角 lens** | `work4ai/费曼学习法/lens/理论全景.md` | 在线质量探针（自动启发式扫描）|
| **多视角批处理脚本** | `work4ai/费曼学习法/...multi-lens-batch.py` | 全语料自动质量扫描，可移植为 Neo-OS 在线探针 |
| **feynman-coach** | `work4ai/费曼学习法/...feynman-coach.py` | AI 扮演 12 岁连环追问，检测偷懒信号 |

### B. AI 理论系列（→ L2/L2.5 理论弹药）

| 主题 | 关键资产 | Neo-OS 用途 |
|------|---------|------------|
| **讲透控制论** | MPC/Lyapunov/状态空间/PID | L2 动力学形式 + 滚动 horizon 因果解释 + L2.5 稳定性判据 |
| **讲透系统论** | 涌现/反馈环/网络结构/自组织 | 级联故障分析、hub 识别、不可还原故障 |
| **讲透因果推断** | do-calculus/SCM/反事实三步法 | 干预层解释、根因定责 |
| **讲透符号主义** | 描述逻辑/归结/Prolog/本体 | 可判定规则引擎、事件本体、GraphRAG |
| **讲透世界模型** | JEPA/VICReg/三准则 | L2 latent 预测架构、防 collapse |
| **讲透可解释性** | Probing/SHAP/Mechanistic | 归因（SHAP 公理化保证）、电路分析 |
| **讲透信息论** | 熵/MDL/压缩即学习/Attention 信息流 | L2 模型选择标准、压缩率度量理解深度 |

### C. AI 系统系列（→ L0/L1/性能 同构资产）

| 主题 | 关键资产 | Neo-OS 用途 |
|------|---------|------------|
| **讲透 GPU 与系统级** | FlashAttention/PagedAttention/vLLM/量化/CUDA/Triton | trace 流式处理(online 聚合)、buffer 分页、本机小模型部署 |
| **讲透 KV Cache** | 增量计算 O(n²)→O(n)/prefill-decode 算术强度 | trace 增量处理不回扫、性能预算建模 |
| **讲透分布式 AI 系统** | ZeRO/TP/PP/Ring all-reduce | 分布式 trace 分片与因果同步 |

### D. LLM 能力系列（→ world model 蒸馏 + Agent 化）

| 主题 | 关键资产 | Neo-OS 用途 |
|------|---------|------------|
| **讲透基础模型** | NTP=压缩/ScalingLaw/Chinchilla/SFT-DPO | world model 蒸馏目标 + 数据配方 |
| **讲透 Transformer** | 长上下文/MoE/训练并行/推理优化 | 百万事件 trace 处理 + 部署 |
| **讲透微调** | LoRA/QLoRA/LIMA 数据工程/失败模式 | commit→解释微调 + 每域 adapter |
| **讲透 Prompt** | CoT/Structured Output/上下文工程 | 解释查询 prompt 设计 |
| **讲透 RAG** | 混合检索/GraphRAG/Agentic RAG/Self-RAG | commit/spec/code 检索增强 |
| **讲透 Agent** | ReAct/Plan-Execute/Reflexion/工具工程/MCP/记忆四级 | Neo-OS 本身是 Agent，工具标准化 |

### E. 跨学科与历史（→ 合法性 + 竞争意识）

| 主题 | Neo-OS 用途 |
|------|------------|
| 讲透科学的现代性 | 项目在科学范式中的位置 |
| 讲透反向传播/优化器/损失函数/激活函数 | world model 训练理论 |
| 讲透泛化/统计学习理论 | world model 泛化保证 |
| 讲透数学建模 | 系统建模方法论 |
| 讲透Prompt/RAG/Agent（重复，已列）| |
| 讲透分布式AI系统（重复，已列）| |
| 讲透访谈（张小珺系列）| 前沿人物观点（世界模型/Agent 范式）|

### F. 多角色审查报告（已积累的审议资产）

| 文件 | 用途 |
|------|------|
| `work4ai/多角色审查报告.md` / `.多视角.md` / `.费曼检验.md` | 多视角审议范例 |
| `work4ai/横向打通-能力获取决策框架.md` 系列 | 能力获取决策方法论 |

---

## 二、workspace 其他本地资源

### AI 基础理论

| 资产 | 路径 | Neo-OS 用途 |
|------|------|------------|
| **Foundations-of-LLMs** | `/mnt/c/workspace/Foundations-of-LLMs/` | ZJU LLM 教材 + 经典论文列表，world model 蒸馏理论参考 |
| **leemiracle** | `/mnt/c/workspace/leemiracle/` | ML-SYS 教程（RLHF/SGLang），L2 部署参考 |
| **Machine-Learning-Interviews** | 同名目录 | ML 理论速查 |

### 编译器（D6 靶子，多层语义对齐）

| 资产 | 路径 | Neo-OS 用途 |
|------|------|------------|
| **LLVM 项目研究** | `/mnt/c/workspace/LLVM项目研究/` | pass trace-native 化、ORE remarks、debuginfo |
| **llvm** | `/mnt/c/workspace/llvm/` | LLVM 源码，IR/MLIR 形式化锚点 |
| **AI 编译器研究** | `/mnt/c/workspace/AI编译器研究/` | 19 个 Expert 子目录（PyTorch Compiler/XLA/MLIR/TVM/...），编译器可解释性直接靶子；含 Miscompilation 深度专题、oracle 战略评审 |

### AI 系统（L0/L1/性能同构）

| 资产 | 路径 | Neo-OS 用途 |
|------|------|------------|
| **AI 基础设施研究** | `/mnt/c/workspace/AI基础设施研究/` | 23 Expert（GPU/TPU/NPU/互联/HBM/KVCache 存储/...），硬件层规格 |
| **ai-os（含 vLLM/SGLang/llama.cpp）** | `/mnt/c/workspace/ai-os/` | 推理引擎源码，trace buffer 管理/分页/调度直接参考 |

### 系统软件（OS + 网络 + 移动）

| 资产 | 路径 | Neo-OS 用途 |
|------|------|------------|
| **linux** | `/mnt/c/workspace/linux/` | kernel 源码 + Documentation，L1 事件本体 + commit 蒸馏语料 |
| **android-os** | `/mnt/c/workspace/android-os/` | AOSP NNAPI/ML 模块，移动端可解释性 |
| **kylinos** | `/mnt/c/workspace/kylinos/` | 麒麟 OS 114+ 项目（OpenStack），国产 OS 语境 |
| **paper-os / popular-os** | 同名目录 | OS 研究资料 |

### 硬件规格（CPU/GPU/NPU）

| 资产 | 路径 | Neo-OS 用途 |
|------|------|------------|
| **体系结构** | `/mnt/c/workspace/体系结构/` | kernel-opt-lab + 体系结构实验，CPU 微架构 |
| **phytium** | `/mnt/c/workspace/phytium/` | **飞腾 ARM 平台**：d3000m-npu-docs、phytium-embedded-docs、armnn、NPU benchmark，ARM trace/CoreSight + NPU 规格 |
| **gpu** | `/mnt/c/workspace/gpu/` | GPU 资料，D8 靶子 |
| **SatellinkALG** | `/mnt/c/workspace/SatellinkALG/` | 卫星通信 + ML 视觉（Kotlin/ONNX），嵌入式可解释性 |

### 数学与形式化

| 资产 | 路径 | Neo-OS 用途 |
|------|------|------------|
| **math** | `/mnt/c/workspace/math/` | Lean4 / Mathlib4 / 数学路线图，L2.5 形式化基建 |
| **math-expert-pro** | 同名目录 | 数学专家系统 |
| **mips-sim** | `/mnt/c/workspace/mips-sim/` | ISA 模拟器，L0 二进制层参考 |

### 学习与方法论

| 资产 | 路径 | Neo-OS 用途 |
|------|------|------------|
| **csdiy** | `/mnt/c/workspace/csdiy/` | CS 自学路线 |
| **cracking-the-data-science-interview** | 同名 | DS 面试，理论速查 |
| **费曼学习法**（work4ai 内）| 见上 | 解释引擎方法论 |

### 趋势与前沿

| 资产 | 路径 | Neo-OS 用途 |
|------|------|------------|
| **trending-repos** | `/mnt/c/workspace/trending-repos/` | 17 个 trending 项目分析 + SUMMARY_REPORT |
| **infoq-analysis / infoq-atlas / tech-insight** | 同名 | 技术趋势 |
| **ai-atlas / ai-lab-landscape** | 同名 | AI 实验室全景 |
| **master-equivalent** | 同名 | 知识体系 |

---

## 三、资产复用优先级

### Phase 0（立项，必用）
1. **work4ai/费曼学习法/** → 提炼解释引擎方法论
2. **work4ai/讲透控制论 + 因果推断 + 符号主义** → L2/L2.5 理论框架
3. **linux/** → 1000 commit 抽取率实验（项目命门 V25）
4. **math/Lean4** → 形式化粒度种子实验（V11）

### Phase 1（prototype，必用）
1. **work4ai/讲透GPU与系统级 + KV Cache** → L1 trace 处理架构
2. **ai-os/vllm + sglang + llama.cpp** → L2 推理部署
3. **work4ai/讲透微调 + RAG + Agent** → world model 蒸馏 + agent 化
4. **linux/Documentation + 体系结构** → 事件本体设计

### Phase 2（领域扩展，按靶子选用）
- **浏览器**：work4ai 无直接资料，需联网 + DevTools 文档
- **编译器**：`AI编译器研究/`（19 Expert）+ `llvm/` + `LLVM项目研究/`
- **数据库**：联网 + PG 文档
- **分布式**：work4ai/讲透分布式AI系统 + 联网 OTel/Jepsen
- **GPU**：`gpu/` + `phytium/`(NPU/ARM) + 联网 Vulkan/Mesa

---

## 四、资产调用协议

调用 work4ai 资产时遵循：
1. **方法论优先**：先复用"三层 × 17 视角 × 费曼"方法论，再取具体技术
2. **三层互锁**：任何引入的概念，必须三层呈现（直觉→数学→代码）
3. **费曼把关**：任何解释，必须过 F1-F4 检验
4. **trace 接地**：work4ai 的"代码实证层"在 Neo-OS 里升级为 trace 实证
5. **诚实标注 provenance**：每个资产标注来源路径 + 对 Neo-OS 的具体映射

---

*本文档随本地资产发现而更新。新增资产请补充到对应分类。*
