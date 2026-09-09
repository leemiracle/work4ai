# from-work4ai.md · work4ai 资产 → Neo-OS 层映射索引

> 本文件**不复制 work4ai 任何内容**，只建立引用映射。
> work4ai 路径：同机 `../work4ai/`（相对本仓库根）/ 其他机器见 [02-research/LOCAL_ASSETS.md](../02-research/LOCAL_ASSETS.md)

---

## A. 解释引擎方法论（→ L3 英文接口）

**这是 Neo-OS 灵魂级别的继承**。L3 = work4ai 三层讲透宪法的运行时化。

| work4ai 资产 | 路径 | Neo-OS 用途 | 当前状态 |
|---|---|---|---|
| 费曼学习法 skill | `work4ai/费曼学习法/skill/SKILL.md` | L3 生成-护栏-验收闭环方法论 | 🟢 已用（prototype 阶段） |
| 费曼检验模板 | `work4ai/费曼学习法/费曼检验模板.md` | L3 F1-F4 质量门 | 🟡 待自动化（Phase 1） |
| 17 视角 lens | `work4ai/费曼学习法/lens/理论全景.md` | L3 在线质量探针 | 🟡 待自动化 |
| 多视角批处理脚本 | `work4ai/费曼学习法/...multi-lens-batch.py` | 可移植为 Neo-OS 在线探针 | 🟢 资产就绪 |
| feynman-coach | `work4ai/费曼学习法/...feynman-coach.py` | AI 扮演 12 岁连环追问 | 🟢 资产就绪 |
| **三层讲解宪法** | `work4ai/README.md` §六 + 每个讲透系列 | L3 三层结构（直觉→数学→trace） | 🟢 已实现 |

**当前 L3 实现**：[`04-layers/l3-explain/`](../04-layers/l3-explain/) ——
`l3_explain.py` 调 GLM-4-plus，对 L2.5 规则生成三层英文讲解（Intuition / Formal / Trace evidence）。

---

## B. 理论弹药（→ L2/L2.5）

每个讲透系列都按"直觉→数学→代码→不足→应用"五层写，Neo-OS 按需取用。

| work4ai 系列 | 关键资产 | Neo-OS 层 | 用途 |
|---|---|---|---|
| **讲透控制论** | MPC / Lyapunov / 状态空间 / PID | L2 + L2.5 | L2 动力学形式 + 滚动 horizon 因果 + L2.5 稳定性判据 |
| **讲透系统论** | 涌现 / 反馈环 / 网络结构 / 自组织 | L2 | 级联故障分析、hub 识别、不可还原故障 |
| **讲透因果推断** | do-calculus / SCM / 反事实三步法 | L2 + L3 | 干预式解释、根因定责 |
| **讲透符号主义** | 描述逻辑 / 归结 / Prolog / 本体 | L2.5 | 可判定规则引擎、事件本体、GraphRAG |
| **讲透世界模型** | JEPA / VICReg / 三准则 | L2 | latent 预测架构、防 collapse |
| **讲透可解释性** | Probing / SHAP / Mechanistic | L2 + L3 | 归因（SHAP 公理保证）、电路分析 |
| **讲透信息论** | 熵 / MDL / 压缩即学习 | L2 | 模型选择标准、压缩率度量理解深度 |

---

## C. AI 系统系列（→ L0/L1/性能 同构资产）

| work4ai 系列 | 关键资产 | Neo-OS 层 | 用途 |
|---|---|---|---|
| **讲透 GPU 与系统级** | FlashAttention / vLLM / 量化 / CUDA / Triton | L0 + L1 | trace 流式处理、buffer 分页、本机小模型部署 |
| **讲透 KV Cache** | 增量计算 O(n²)→O(n) / 算术强度 | L1 | trace 增量处理不回扫、性能预算 |
| **讲透分布式 AI 系统** | ZeRO / TP / PP / Ring all-reduce | L1 | 分布式 trace 分片与因果同步 |

---

## D. LLM 能力系列（→ world model 蒸馏 + Agent 化）

| work4ai 系列 | 关键资产 | Neo-OS 层 | 用途 |
|---|---|---|---|
| **讲透基础模型** | NTP=压缩 / ScalingLaw / Chinchilla / SFT-DPO | L2 | world model 蒸馏目标 + 数据配方 |
| **讲透 Transformer** | 长上下文 / MoE / 训练并行 / 推理优化 | L2 | 百万事件 trace 处理 + 部署 |
| **讲透微调** | LoRA / QLoRA / LIMA 数据工程 / 失败模式 | L2 | commit→解释微调 + 每域 adapter |
| **讲透 Prompt** | CoT / Structured Output / 上下文工程 | L3 | 解释查询 prompt 设计 |
| **讲透 RAG** | 混合检索 / GraphRAG / Agentic RAG / Self-RAG | L2 + L3 | commit/spec/code 检索增强 |
| **讲透 Agent** | ReAct / Plan-Execute / Reflexion / MCP / 记忆四级 | 全栈 | **Neo-OS 本身是 Agent**，工具标准化 |

---

## E. 横向打通与多视角审议

| work4ai 资产 | 路径 | Neo-OS 用途 |
|---|---|---|
| 横向打通-能力获取决策框架 | `work4ai/横向打通-能力获取决策框架.md` | 能力获取决策方法论（Prompt/RAG/微调/Agent 四极） |
| 多角色审查报告 | `work4ai/多角色审查报告.md` `.多视角.md` `.费曼检验.md` | 多视角审议范例，council 模式的范本 |

---

## F. 调用协议

```python
# Neo-OS L3 实现引用 work4ai 的伪代码
from methodology.feynman_gate import F1 outs retelling, F2 stuck_self_report, F3 term_blacklist, F4 reheat_log
from methodology.lens_17 import first_principles, bloom_taxonomy, toulmin, red_team, systems_thinking, ...
from methodology.three_layer import intuition_layer, math_layer, trace_evidence_layer

def explain(rule: Lean4Rule, trace: eBPFTrace) -> EnglishExplanation:
    intuition = intuition_layer(rule, trace)        # work4ai 直觉层
    formal    = math_layer(rule)                    # work4ai 数学层（Lean4 不变式）
    evidence  = trace_evidence_layer(rule, trace)   # ★ trace-native 升级（见 trace-native-upgrade.md）
    explanation = ThreeLayerOutput(intuition, formal, evidence)
    
    # work4ai 17 视角护栏
    for lens in LENS_17:
        explanation = lens.scan(explanation)
    
    # work4ai 费曼门 F1-F4
    explanation = feynman_gate(explanation)  # F1-F4 全过才输出
    return explanation
```

---

## 状态图例

- 🟢 **已用/资产就绪**：当前 prototype 已实现 或 work4ai 文件已存在可引用
- 🟡 **待自动化**：方法论已在设计中，工程化在 Phase 1 路线
- 🔴 **未启动**：Phase 2+ 才会触及

---

*本文件是 Neo-OS 与 work4ai 的契约。任何"Neo-OS 解释引擎"的设计声称，
必须能回到本文件指向 work4ai 的具体方法论文件作为 provenance。
反 Hurd 铁律：方法论是提取出来的，不是设计出来的——本文件是这一纪律的物化。*
