# 世界模型与AI4Sci调研（world-ai4sci-math 选粹入库）

## 0. 这是什么

本目录是源库 `C:\workspace\world-ai4sci-math`（v2.1.8，2026-07-23）的**选粹入库**。

源库自述：14 大模块 / 100+ 章节 / **~133 万字** / 1152 arXiv 引用 / 118 可运行实验 / 50 研究课题的
「世界大模型 · AI4Science · AI4Math」全景调研卷，全部 arXiv ID 一手核实（源库 MIT License）。
与本仓库既有内容（讲透系列、九校课程库、Karpathy 精读）高重合的部分**不收**，只保留独有价值。

- 保留比例：**55 / 176 md + 6 / 118 py**，正文字符 1,918,872 / 6,428,899 ≈ **29.8%**
- 目录结构沿用源库模块编号，便于与 `沿革存档/CHANGELOG.md` 对照原库全貌
- 源库顶层 README / CHANGELOG / EXPERIMENTS 三件收于 `沿革存档/` 作沿革存档
- 复制时排除源库 `.git`；未收录任何 PNG（见 §2 末行说明）

## 1. 收录清单

| 模块 | 收录内容 | 价值定位 |
|---|---|---|
| `docs/` | **整目录全收**（28 文件：30 研究课题、10 学习路径、使用导航、决策记录、前沿深读 5 篇、研究执行 4 课题含 4 个 py、top-20-insights、ten-lessons 等） | 仓库无等价物，最独有价值 |
| `04-synthesis/` | **整目录全收**（9 文件：共享架构、评测开放问题、2026 前沿、超越概率 LLM、停滞与创新、AI 的分布式系统、OS 经典、Linux 内核与 AI） | 跨领域对照独有价值 |
| `01-world-models/` | `02-embodied-vla-wam.md`、`03-autonomous-driving.md` | VLA 与自驾两个专题 |
| `02-ai4science/` | `03-drug-discovery.md` | 药物发现（含 rentosertib 进 Phase 3 产业线） |
| `03-ai4math/` | `02-informal-reasoning.md` | 非形式推理（与形式化路线互补的一条） |
| `05-model-engineering/` | `03-paper-reading.md` + `09` 数据栈深水区、`10` 推理优化、`11` 现代架构数学、`12` 验证器/PRM/搜索训练、`13` 信创厂商训练栈 | 深水区五章 + 读论文方法 |
| `07-extended-tech/` | `02-3d-generative.md`、`03-differentiable-physics.md` | 3D 生成与可微物理 |
| `08-ai4x-applications/` | `03-ai4compiler.md`、`07-computing-architecture-future.md` | AI4Compiler 与未来计算架构 |
| `10-emerging-fields/` | `01-ai4neuroscience.md`、`02-quantum-ml.md` | AI4神经科学与量子 ML |
| `13-agent-systems-deep/` | `10-computer-use-agents-deep.md`、`13-formal-verification-agents-deep.md`、`experiments_13/01_leandojo_state_machine.py` | Computer-Use Agent 与形式化验证 Agent（后者配套实验随收） |
| `14-foundations-computation-physics/` | `05-numerical-analysis-scientific-computing.md`、`experiments_05/06_phytium_d3000_fp16_neon.py` | 数值分析章（含**飞腾 D3000 国产硬件**实测特性，配套实验随收） |
| 顶层 | `沿革存档/`：README.md、CHANGELOG.md、EXPERIMENTS.md | 沿革存档 |

## 2. 弃收对照表

每行「弃收内容 → 仓库已有等价物」。右侧路径**已逐个 ls 验证存在**（相对本目录）。

| 弃收内容 | 仓库已有等价物 |
|---|---|
| `06-theoretical-foundations/` 整模块（学习理论/优化理论/信息几何/泛化/概率ML/可计算性 6 章） | [`../../讲透数学/`](../../讲透数学/)（[讲透优化/](../../讲透数学/讲透优化/)、[讲透概率论/](../../讲透数学/讲透概率论/)、[讲透统计学习理论/](../../讲透数学/讲透统计学习理论/)、[讲透数理逻辑/](../../讲透数学/讲透数理逻辑/) 等专系列） |
| `09-ai-philosophy-ethics/` 整模块（意识/对齐安全/公平治理/AGI 路径 4 章） | [`../../讲透哲学/`](../../讲透哲学/) |
| `11-model-components-deep/` 整模块（注意力/FFN/位置编码/损失/优化器/变体/多模态本质 8 章 + 61 个实验） | [`../../讲透模型/讲透Transformer/`](../../讲透模型/讲透Transformer/) 与 [`../../Karpathy经典代码精读/`](../../Karpathy经典代码精读/) |
| `12-model-lifecycle-deep/` 整模块（预训练/PEFT/对齐RLHF-DPO/评测/部署 5 章 + 51 个实验） | [`../../讲透模型/讲透微调/`](../../讲透模型/讲透微调/) |
| `01-world-models/` 其余（00-README、01-视频生成、04-latent-JEPA） | [`../../讲透模型/讲透世界模型/`](../../讲透模型/讲透世界模型/) |
| `02-ai4science/` 其余（00、01-蛋白质、02-基因组单细胞、04-材料化学、05-物理气候） | [`../../实例/讲透AIfor各学科/`](../../实例/讲透AIfor各学科/)（[生物/](../../实例/讲透AIfor各学科/生物/)、[化学/](../../实例/讲透AIfor各学科/化学/)、[材料/](../../实例/讲透AIfor各学科/材料/)、[地球气候/](../../实例/讲透AIfor各学科/地球气候/)、[物理/](../../实例/讲透AIfor各学科/物理/)） |
| `03-ai4math/` 其余（00、01-形式化证明、03-基准几何） | [`../../讲透数学/`](../../讲透数学/)（[讲透Lean4数学/](../../讲透数学/讲透Lean4数学/)、[讲透证明/](../../讲透数学/讲透证明/)）与 [`../../讲透形式化验证/`](../../讲透形式化验证/) |
| `05-model-engineering/` 主线（00、01-架构演化、02-工程部署、04-快速验证、05-模型优化、06-资源受限创新、07-开源生态、08-低预算领域迁移） | [`../../讲透模型/讲透模型宇宙/`](../../讲透模型/讲透模型宇宙/) |
| `07-extended-tech/` 其余（00、01-多模态基础、04-Agent系统、05-长上下文、06-可控可解释生成） | [讲透多模态/](../../讲透模型/讲透多模态/)、[讲透Agent/](../../讲透Agent/)、[讲透LLM/](../../讲透模型/讲透LLM/)、[讲透可解释性/](../../讲透模型/讲透可解释性/) |
| `08-ai4x-applications/` 其余（00、01-金融、02-OS、04-EDA/IC、05-数据库、06-安全） | [讲透AIfor各学科/经济金融/](../../实例/讲透AIfor各学科/经济金融/)、[讲透AIfor各学科/芯片设计/](../../实例/讲透AIfor各学科/芯片设计/)、[讲透计算机科学技术/](../../讲透计算机科学技术/)、[database-systems/](../../database-systems/) |
| `10-emerging-fields/` 其余（00、03-教育、04-医疗、05-法律、06-游戏） | [讲透AIfor各学科/教育/](../../实例/讲透AIfor各学科/教育/)、[公共健康/](../../实例/讲透AIfor各学科/公共健康/)、[法学/](../../实例/讲透AIfor各学科/法学/)、[讲透生成模型/](../../讲透模型/讲透生成模型/) |
| `13-agent-systems-deep/` 主线（00-09、11-12 共 11 章：架构/LLM集成/技能插件/记忆/规划推理/多Agent/评测/安全/编码Agent/研究Agent/设计模式） | [`../../讲透Agent/`](../../讲透Agent/) |
| `14-foundations-computation-physics/` 其余（00、01-计算理论、02-数理建模、03-概率随机过程、04-动力系统） | [讲透计算复杂度/](../../讲透数学/讲透计算复杂度/)、[讲透数学建模/](../../讲透数学/讲透数学建模/)、[讲透概率论/](../../讲透数学/讲透概率论/)、[讲透复杂系统/](../../讲透复杂系统/) |
| 顶层 21 张 PNG（activations/adam/sgd/scaling_law/loss_spike 等） | 皆为弃收的 11/12 模块实验配图，**本库收录文件零引用**（唯一 .png 字样是 `02-3d-generative.md` 示例代码中的 `assets/demo.png`，非仓库文件） |
| 顶层 `shakespeare_input.txt`、空目录 `data/`、`papers/`、`LICENSE`、`.gitignore`、`.opencode/` | 12 模块实验输入 / 空目录 / 仓库元数据，随整库弃收一并不入 |

## 3. 代码资产索引（本库收录的全部 6 个 .py）

| 路径 | 做什么 | 运行方式 |
|---|---|---|
| `docs/research-execution/01_fp16_error_scaling.py` | 课题 NA-1 第一步：FP16 累加误差的 Scaling Law | `python3 01_fp16_error_scaling.py`（依赖仅 numpy） |
| `docs/research-execution/01b_fp16_distribution_dependence.py` | 课题 NA-1 第二步：FP16 误差 scaling vs 输入分布 | `python3 01b_fp16_distribution_dependence.py`（仅 numpy） |
| `docs/research-execution/02_kl_vs_accept_rate.py` | 课题 IT-3：KL 散度 vs 推测解码 Accept Rate | `python3 02_kl_vs_accept_rate.py`（仅 numpy） |
| `docs/research-execution/03_queueing_llm_serving.py` | 课题 PR-5：排队论 M/G/1 分析 LLM Serving | `python3 03_queueing_llm_serving.py`（仅 numpy） |
| `13-agent-systems-deep/experiments_13/01_leandojo_state_machine.py` | LLM × Lean 双层证明状态机模拟：LeanDojo init/run_tactic/premise-selection API + ReProver 风格检索 + sorry 漏洞反例 + Lean Copilot 实测对照（§13 配套） | 纯 Python 无需 Lean 环境，直接 `python3` 运行 |
| `14-foundations-computation-physics/experiments_05/06_phytium_d3000_fp16_neon.py` | 飞腾 D3000 国产 ARM 数值与 ISA 特性：FP16 vs FP32 / 128-bit NEON 元素数 / SDOT 加速 / 国密双栈 / kpgcc 指令融合，5 部分（§05 §11 配套） | 纯 numpy，无需飞腾硬件，直接 `python3` 运行 |

**原库 118 个实验的分布与本库收录位**：模块 11 六个实验目录 61 个、模块 12 五个实验目录 51 个（EXPERIMENTS.md 的"共 111"是 11/12 两模块 v2.0.2 时点口径，此后 `experiments_optimizer`、`experiments_deployment` 各增至 11 个）、模块 13 与 14 各 1 个、`docs/research-execution` 4 个。**本库收录 11/12 之外的全部 6 个**（4 个课题实验 + LeanDojo 状态机 + 飞腾 D3000），11/12 的 112 个随整模块弃收（等价物见 §2）。

## 4. 与 前沿与媒体/ 的桥接

- 同仓库媒体侧入口：[`../../前沿与媒体/`](../../前沿与媒体/)——其「深读卡」系列与本库 `docs/frontier-deep-dive/`（Kimi K3 / Inkling / Sessa / SciReasoner / MXFP4-QAT 五篇）同一体裁，可对照阅读。
- `top-20-insights` 与 `ten-lessons` 已随 `docs/` 整目录全收于此：[docs/top-20-insights.md](docs/top-20-insights.md)、[docs/ten-lessons.md](docs/ten-lessons.md)。
