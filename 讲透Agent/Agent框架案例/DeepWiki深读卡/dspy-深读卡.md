# dspy 深读卡 —— 把 prompt 工程变成"声明式程序 + 编译器"的框架

> **定位**：DSPy（Declarative Self-improving Python）是斯坦福出的"编程而非提示"（programming, not prompting）框架：用 `Signature` 声明任务、用 `Module` 组合程序，再由 Optimizer（旧名 Teleprompter）按你定义的 metric 自动"编译"出最优 prompt/few-shot/权重。口号式理解：**PyTorch 之于神经网络，DSPy 之于 LM 程序**——你写前向逻辑，框架负责把声明式代码翻译成每个 LM 的最优提示格式。
> **本地**：`repos/dspy`（stanfordnlp/dspy）｜**深读**：deepwiki 46 子页归档 `deepwiki/dspy/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 用户接口层 | 公共 API 聚合 + 全局配置 | `dspy/__init__.py`、`dspy.settings`、`dspy.configure()` / `dspy.context()` |
| 逻辑层（核心抽象） | 声明式任务定义 + 程序组合 | `Signature`/`InputField`/`OutputField`、`Module`、`Predict`/`ChainOfThought`/`ReAct`/`ProgramOfThought`/`RLM`、`Example`/`Prediction` |
| 执行层（翻译） | Signature ↔ 模型请求双向翻译 | `Adapter`（`ChatAdapter`/`JSONAdapter`/`XMLAdapter`/`TwoStepAdapter`/`BAMLAdapter`）、`LMRequest`/`LMResponse`/`LMMessage`、`dspy.LM`（`BaseLM.forward()`，LiteLLM 统一各 provider） |
| 基础设施层 | 缓存 / 并行 / 可观测 | `DSPY_CACHE`（两级缓存）、`track_usage`、`dspy.Parallel`、`asyncify`/`streamify`、`inspect_history` |
| 优化层 | metric 驱动的 prompt/权重编译 | `Teleprompter`、`BootstrapFewShot`、`MIPROv2`、`GEPA`、`SIMBA`、`BootstrapFinetune`/`GRPO`、`BetterTogether`、`Evaluate` |

## 二、核心机制

1. **Compile-Then-Run 编译范式**（来源：Introduction & Core Concepts）：写声明式代码（`Signature`+`Module`）→ 用 optimizer 按 metric 编译 → 部署优化后产物。核心是把"做什么"（declarative logic）与"怎么提示这个 LM"（optimized implementation）彻底解耦——换模型只需重编译，prompt 不再手工维护。
2. **Adapter 双向翻译 + Typed LM API**（来源：Overview / Core Architecture）：一次调用的生命周期 = `Adapter.format()`（signature+inputs → `LMRequest`，含 messages/tools/config）→ `LM.forward()`（LiteLLM 实际请求）→ `Adapter.parse()`（`LMResponse` → `Prediction`）。`LMRequest`/`LMResponse` 是 provider 中立的规范容器，这是新客户端只需实现一个 `forward()` 的原因。
3. **Teleprompter 三输入、四类优化器**（来源：Optimization Overview）：任何 optimizer 都吃 `student`(Module) + `trainset`(list[Example]，10-500 个即可，少至 30 例也有效) + `metric`(Callable)。内部通用流程 = Bootstrapping（跑程序收集 trace，按 metric 过滤出成功轨迹当 demos）→ 指令提案（`GroundedProposer` 预览代码/数据/trace 起草指令）→ 离散搜索（Optuna 贝叶斯优化选最优组合）。四类：Few-Shot（`BootstrapFewShot` 系）、Instruction（`MIPROv2`/`GEPA`/`SIMBA`）、Fine-tuning（`BootstrapFinetune`/GRPO）、Meta（`BetterTogether` 用 `"p -> w -> p"` 策略串链、`Ensemble` 合并 top-k）。
4. **三层 LM 选择 + settings 单例**（来源：Core Architecture / Language Model Integration）：LM 可挂在 context 局部 > module 局部 > 全局 `dspy.settings`，配置经 `configure()`/`context()` 解析并向并行/async 任务传播，保证隔离。

## 三、与讲透系列的对位

| DSPy 概念 | 讲透系列对位 | 关联点 |
|---|---|---|
| Signature 声明式任务定义 | 讲透类型系统/函数签名直觉 | "what 不是 how"=声明式编程的教科书案例 |
| ChainOfThought / Reasoning | 讲透 CoT/思维链 | DSPy 把 CoT 从"咒语"降级为可组合 Module |
| ReAct / Avatar / CodeAct | 讲透 Agent / 工具调用 | agent loop 的模块化实现，接 `dspy.Tool`/MCP |
| MIPROv2 / GEPA | 讲透 Prompt 工程（进化版） | prompt 优化 = 贝叶斯搜索/反思进化，工程化 view |
| BootstrapFinetune / GRPO | 讲透微调 LoRA / 讲透 RLHF | prompt 蒸馏进权重；GRPO 在线 RL（Arbor 集成） |
| Evaluate / metric | 讲透 ML 实验评估 | LLM-as-judge、并行评测、与优化闭环 |

## 四、关键入口

```python
import dspy
from typing import Literal

lm = dspy.LM('openai/gpt-4o-mini', api_key=...)   # LiteLLM 统一入口
dspy.configure(lm=lm)                              # 挂到全局 settings

# ① 声明任务：Signature（what）
class Classify(dspy.Signature):
    """Classify sentiment of a given sentence."""
    sentence: str = dspy.InputField()
    sentiment: Literal['positive', 'negative', 'neutral'] = dspy.OutputField()

# ② 组合程序：Module（how，零样本即可跑）
classify = dspy.ChainOfThought(Classify)

# ③ 编译：optimizer 吃 (student, trainset, metric)
optimizer = dspy.MIPROv2(metric=my_metric, auto="light")
optimized = optimizer.compile(classify, trainset=trainset)  # 产出优化后 Module
optimized(sentence="That was awesome!")                       # -> Prediction(sentiment='positive')
optimized.save("cls.json")                                    # 状态持久化，可 load 复用
```

源码导航：`dspy/signatures/`（Signature/Field）→ `dspy/primitives/`（Module/Example）→ `dspy/predict/`（Predict/CoT/ReAct）→ `dspy/adapters/`（format/parse）→ `dspy/clients/`（LM/LiteLLM/cache）→ `dspy/teleprompt/`（全部 optimizer）→ `dspy/evaluate/`（Evaluate/metrics）。

## 五、深读子页地图（46 页精选 6）

| 子页 | full.md 行 | 价值 |
|---|---|---|
| 6. Core Architecture | L1099 | 三层架构总图 + 请求生命周期时序，先读这页定骨架 |
| 9. Signatures & Task Definition | L1657 | 三种定义方式（string/class/dict）+ `SignatureMeta` 元类 |
| 10. Adapter System | L1887 | format/parse 翻译层全解，5 种 Adapter 选型 |
| 21. Optimization Overview | L4316 | optimizer 选型决策树 + 三输入四类，DSPy 灵魂 |
| 24. MIPROv2 | L5160 | 三阶段内部实现：bootstrap→GroundedProposer→Optuna |
| 25. GEPA & SIMBA | L5422 | 反思式/随机式 prompt 进化，2024-25 最新方向 |

## 六、与"我们"的关系（一句话）

DSPy 是"讲透 Agent / 讲透 Prompt 优化"系列的天然参考实现——把用户在 work4ai 里手工做的 prompt 迭代变成可教、可跑、可度量的编译器问题，正好作为 agent-development 资源里 LangChain/LangGraph 之外的"第三条路线"精读。

---
生成：2026-08-21 · deepwiki 46 页全归档
