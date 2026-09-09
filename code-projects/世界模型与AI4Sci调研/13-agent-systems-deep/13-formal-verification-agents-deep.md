# 第十三章 · Agent × 形式化验证：LLM 幻觉的根治方案

> **本卷补章（2026-07-23 增补）**：Agent 系统最大的工程风险是 **LLM 幻觉**——模型自信地输出错误内容。前面 12 章讲了各种"概率性缓解"（reflection、verifier、ensemble、prompt 约束），但都不能根治。本章讲**唯一能根治的方案**：让 Agent 的关键输出经过**形式化验证器**（Lean / Coq / Isabelle / Z3）证明其正确性。LLM 提议，形式化器强制验证——这是 AI 走向"高可信"场景（数学、安全、合规、定理证明、verified codegen）的必经之路。
>
> 本章素材来源：lean4ai 项目（`/data/usershare/ai/lean4ai/`，含 LeanDojoChatGPT 源码 + Lean4 内核注释 + Certigrad4 + Aeneas 整合）+ arXiv 一手核实。

---

## 0. 为什么 Agent 需要形式化验证？

回到第十二章 §「Verifier-Guided Pattern」：Agent 的核心循环是 **Propose → Verify → Refine**。Verifier 决定了整个系统的可信度上限。问题来了——**Verifier 自己有多可信**？

- **规则 Verifier**（如单元测试、linter）：可信但**覆盖窄**——只能验它能想到的属性
- **LLM Verifier**（如 LLM-as-judge）：覆盖广但**自己会幻觉**——错错相加
- **形式化 Verifier**（Lean / Coq / Z3）：**数学上 100% 可信**（soundness 是定理），但**需要把问题形式化**

**核心权衡**：形式化验证的可信度是数学保证的，代价是**"把模糊问题翻译成形式语言"**极难。比如"证明这段 Rust 代码无 UB"是可形式化的；但"证明这封营销邮件 politically correct"则几乎不可形式化。

Agent × 形式化验证的**甜蜜区**：那些**有形式语言的目标领域**——数学证明、程序验证、协议设计、安全策略、配置文件、智能合约。在这些领域，形式化验证能把 Agent 从"概率可用"提升到"数学可信"。

---

## 一、历史脉络：AI × 定理证明的 50 年演化

| 年代 | 里程碑 | 核心突破 |
|---|---|---|
| **1970s** | LCF（Robin Milner）/ Boyer-Moore | "tactic" 概念诞生——可编程的证明指令 |
| **1980s** | Coq / Isabelle | 依赖类型论 + 高阶逻辑证明助手 |
| **2013** | Lean 1（Leonardo de Moura） | 现代 ITF（Independent Type Theory Foundation）证明助手 |
| **2017** | **DeepMath**（Alemi/Chollet/Een/Irving/Szegedy/Urban, arXiv:1606.04442，2016-06 提交）| 首次用神经网络辅助定理证明（前提选择，Mizar corpus）|
| **2019** | Holist / TacticToe | ML 选择 tactic 策略 |
| **2020** | ProofNet / HOList 基准 | 大规模定理证明 benchmark |
| **2021** | Lean 3 成熟，mathlib 壮大 | 100 万+ 行形式化数学库 |
| **2020-09** | **GPT-f**（Polu & Sutskever, arXiv:2009.03393）| Transformer 生成 Metamath 证明，**首个被正式数学库接受的 ML 证明** |
| **2022** | AlphaTensor（DeepMind） | RL 发现新矩阵乘算法（自动定理发现）|
| **2023** | **Lean 4** 正式发布 | 强元编程（用 Lean 写 tactic）|
| **2023-06** | **LeanDojo**（Yang et al., NeurIPS 2023 D&B Oral）[arXiv:2306.15626](https://arxiv.org/abs/2306.15626) | **首个开源 LLM × Lean 工具链** + ReProver（retrieval-augmented prover）|
| **2023** | LeanCopilot（早期版） | LLM 作为 Lean 用户 copilot |
| **2024-04** | **Lean Copilot v1**（Song/Yang/Anandkumar, NeuS 2025）[arXiv:2404.12534](https://arxiv.org/abs/2404.12534) | **74.2% 自动化率**（vs aesop 40.1%，提升 85%）|
| **2024-07** | **AlphaProof + AlphaGeometry 2**（DeepMind） | IMO 2024 银牌级（解 4/6 题），首次 AI 在 IMO 级别证明有竞争力 |
| **2024-2025** | LeanDojoChatGPT / Copilot 在 VSCode | LLM × Lean 进入主流编辑器 |
| **2025+** | 形式化证明成为 **AI 推理能力的测试场** | IMO Grand Challenge / FVAP（Formally Verified Agent Platform）雏形 |

**演化主线**：**规则（1970s）→ 神经网络辅助（2017+）→ LLM 主导 + 形式化验证（2023+）→ LLM + RL + 形式化搜索（2024 AlphaProof）**。每个阶段，"人写的规则"越来越少，"AI 提议"越来越多，但**形式化验证始终是最后的护栏**。

---

## 二、形式化验证的三大流派

不同的"形式化器"在表达力 vs 自动化上有根本权衡：

| 流派 | 代表 | 表达力 | 自动化 | 适用 Agent 任务 |
|---|---|---|---|---|
| **SMT（Satisfiability Modulo Theories）** | Z3 / CVC5 / Alt-Ergo | 一阶逻辑 + 理论（算术/数组/位向量）| **高度自动化**（解一次就出答案）| 配置验证、协议验证、漏洞检测、政策合规 |
| **定理证明（ITF/依赖类型）** | **Lean 4** / Coq / Isabelle | **高阶逻辑 + 依赖类型**（最强） | 半自动（人 + tactic + LLM）| 数学证明、程序正确性、复杂性质 |
| **模型检查（Model Checking）** | TLA+ / SPIN / NuSMV | 时态逻辑（系统所有状态）| 完全自动（穷举状态空间）| 并发协议、分布式算法、状态机 |

**关键差异**：SMT 你**问一个问题**（这个约束可满足吗？），它给一个是/否答案；定理证明你**陈述一个事实**（"对所有 n, P(n)"），它要你**给出证明**（但 Lean 会检查你的证明）；模型检查你**陈述一个系统 + 一个性质**，它**穷举所有状态**验证性质。

**Agent 工程选用**：
- 想验证"这段配置/政策无矛盾" → **Z3**（快、自动）
- 想验证"这段 Rust 代码内存安全" → **Lean** + Aeneas（表达力强）
- 想验证"这个分布式协议无死锁" → **TLA+**（穷举状态空间）

> **跨章节连接**：SMT 路线对应 ai-os-dd M8 的"LSM 策略生成 + Z3 验证"（P0 第二个）；Lean 路线是本章重点；TLA+ 在分布式 Agent 协议设计上有应用。

---

## 三、LLM × Lean 架构剖析

### 3.1 LeanDojo：开源 LLM × Lean 工具链（NeurIPS 2023）

**LeanDojo**（[arXiv:2306.15626](https://arxiv.org/abs/2306.15626)，Caltech + NVIDIA，Yang/Swope/Gu/.../Anandkumar）是首个**完全开源**的 LLM × Lean 交互框架，提供 4 件套：

1. **工具包**：Python 控制 Lean（init / run tactic / get state）
2. **数据集**：从 mathlib 提取 **98,734 个定理 + 证明**（含 fine-grained 前提标注）
3. **模型**：**ReProver**（Retrieval-Augmented Prover）—— LLM + 检索前提
4. **benchmark**：挑战性数据切分（要求 generalization to novel premises）

**ReProver 的核心创新**：
- 标准 LLM prover 的瓶颈是"前提选择"——mathlib 有 10 万+ 引理，prover 不知道用哪个
- ReProver 用 LeanDojo 的**程序分析能力**识别"当前证明状态下可达的前提"（accessibility）+ 构造**hard negative examples**（看似相关实则用不了）
- 这个**结构化 retrieval** 比单纯 embedding 相似度有效得多
- 训练**只需 1 GPU 周**——开源 + 低算力，社区可复现

**核心 API（Python）**：
```python
from lean_dojo import Dojo, Theorem, TacticState

theorem = Theorem(repo, "Mathlib/Algebra/Group/Basic.lean", "mul_comm")
with Dojo(theorem) as (dojo, state):
    # state 是 TacticState：含 hyps + goal + 可用前提
    state2 = dojo.run_tac(state, "rw [mul_comm]")
    # 一步步推进，直到 proof_finished
```

### 3.2 LeanDojoChatGPT：把 ChatGPT 接进 Lean（工程级实现）

lean4ai 项目里有一份 **LeanDojoChatGPT 源码**（`/data/usershare/ai/lean4ai/lean4-repos/LeanDojoChatGPT/main.py`），是 LeanDojo 之上的 quart web 服务，让 ChatGPT 通过 HTTPS 接口实时控制 Lean：

```python
# 简化架构（基于 lean4ai/LeanDojoChatGPT/main.py）
@app.post("/initialize_proof_search")
async def initialize_proof_search():
    # 输入：theorem_file_path + theorem_name
    # 动作：Dojo(theorem).__enter__()，进入隔离证明环境
    # 输出：state_id + state.pp（hyp + goal）
    ...

@app.post("/run_tactic")
async def run_tactic():
    # 输入：state_id + tactic（如 "rw [Nat.add_comm]"）
    # 动作：dojo.run_tac(state, tactic)
    # 输出：new state_id / proof_finished / error
    ...

@app.post("/get_premises")
async def get_premises():
    # 输入：state_id + 查询
    # 动作：检索 mathlib 相关引理
    # 输出：top-k 前提列表
    ...
```

**架构精髓**：
- **ChatGPT 不直接接触 Lean**——通过 HTTP API 间接调用（隔离）
- **多证明状态并发**：`states = dict()` 按 state_id 维护，支持多个并行证明
- **每次 tactic 提交都被强制验证**——LLM 提议，Lean 验证，验证失败 LLM 收到错误信息再提议
- **整个交互就是 Agent 的 Propose-Verify-Refine 循环**——但 Verify 是数学保证

实验验证：见 `experiments_13/01_leandojo_state_machine.py`，纯 Python 模拟 init/run_tactic/get_premises 三个 API + sorry 漏洞演示。

### 3.3 Lean Copilot：从 ChatGPT plugin 进化到 Lean 原生（NeuS 2025）

**Lean Copilot**（[arXiv:2404.12534](https://arxiv.org/abs/2404.12534)，Song/Yang/Anandkumar）的关键升级——**LLM 推理 native 跑在 Lean 里**，不需要外部 web 服务。一个 Lean 用户写代码时，Copilot 在编辑器内自动建议 tactic / 完成目标 / 选择前提。

**关键实测数据**（一手 arXiv 核实，Mathematics in Lean 教科书基准）：

| 方法 | 自动化率 | 人机协作（每证手动步数）|
|---|---|---|
| 传统规则法 `aesop` | 40.1% | 3.86 |
| **Lean Copilot (LLM)** | **74.2%** | **2.08** |
| 提升 | **+85%** | **-46%** |

**这是 LLM × 形式化首批有量化收益的工程证据**——把人手敲 tactic 数减半。意味着人可以专注"想证明思路"，让 LLM 写"机械的 tactic 序列"。

### 3.4 AlphaProof：2024 IMO 银牌的工程启示

DeepMind 2024 年 7 月发布的 **AlphaProof + AlphaGeometry 2** 在 IMO 2024 解出 4/6 题（银牌级），首次证明 AI 在 IMO 级别有竞争力。

**架构（公开信息合成）**：
1. **自然语言 → Lean 翻译**：用 Gemini 把 IMO 题目翻译成 Lean 形式化命题（这一步 LLM 主导）
2. **AlphaZero 风格搜索**：在 Lean 证明状态空间做 MCTS（Monte Carlo Tree Search）
3. **RL 训练的 policy/value 网络**：在 Lean 状态 → tactic 分布上训练
4. **形式化验证收尾**：所有候选证明最后必须通过 Lean 内核检查

**关键启示**：
- **LLM 单独不够**：纯 LLM 解 IMO 失败率高（ Lean 证明需要长链推理，LLM 长链不稳）
- **纯搜索不够**：没有 LLM 的策略先验，MCTS 在巨大状态空间迷路
- **LLM + 形式化搜索 = 甜区**：LLM 提供策略先验（policy），Lean 提供强制验证（reward），MCTS 提供长链规划

> **本卷 §05 规划推理**已经讨论了 MCTS + LLM，但 AlphaProof 的特殊性在于：**Lean 的 verification 是数学 ground truth**（不像代码执行可能因副作用失败、不像 RAG 可能检索错）。这让 AlphaProof 的 RL loop 比 AlphaGo 更"干净"——reward signal 几乎无噪。

### 3.5 邻居项目：AlphaGeometry / LeanDojo v2 / Liquid Tensor Experiment

LLM × 形式化不止 AlphaProof / LeanDojo / Lean Copilot 三家。三个值得关注的邻居项目：

**AlphaGeometry**（Trinh et al., *Nature* 625:476–482, 2024, [DOI: 10.1038/s41586-023-06747-5](https://doi.org/10.1038/s41586-023-06747-5)）—— IMO 几何解题的**神经-符号合成**：
- 架构：神经语言模型（DDHM，deduction-based hidden theorem model）+ 符号推导引擎（基于 Wu method + angle chasing）
- 关键差异：**不用 Lean**——自定义的"几何领域专用语言"（points / lines / circles / angles）。这是"**专用形式化 vs 通用形式化**"的工程权衡：通用（Lean）表达力强但学习曲线陡；专用（AlphaGeometry）门槛低但应用面窄
- IMO 2000-2024 几何题 30 道里解出 25 道（IMO 金牌平均 25.9 题）
- **与 AlphaProof 的关系**：DeepMind 2024 用 AlphaGeometry 1 + AlphaProof 联合解 IMO 2024 拿银牌——几何用 AlphaGeometry、代数/数论用 AlphaProof

**LeanDojo v2**（[lean-dojo/LeanDojo-v2](https://github.com/lean-dojo/LeanDojo-v2)）—— 原始 LeanDojo 的"维护弃用"提示：
- 原始 LeanDojo（v1，arXiv:2306.15626）在 2024 之后**官方建议用 v2 分支**——支持 Lean 4 更复杂的特性（如 retrosynthetic tactic、Elab 项）
- 标志着 LLM × Lean 工程的快速迭代——半年一次大版本

**Liquid Tensor Experiment**（Scholze 2021-2022）—— **顶级数学家的形式化背书**：
- Fields 奖得主 Peter Scholze 公开挑战：用 Lean 形式化验证他"自己也无法完全确信"的 condensed mathematics 定理（关于 $\mathbb{Z}_p$-linear abelian groups）
- 6 个月内由社区数学家 + Lean 用户合作完成
- 意义：**这是 Lean 形式化首次进入"主流顶级数学研究"**——不再是教学玩具，是研究工具
- 对 Agent 工程的启示：**形式化不是替代人类数学家**，而是**让 LLM 也能参与"数学研究协作"**（如 Lean Copilot 的 copilot 角色）

**其他生态**：
- **Coq / Rocq**（法国传统，2024 改名 Rocq）—— 与 Lean 竞争的依赖类型证明助手
- **Isabelle/HOL**（剑桥 + 慕尼黑）—— 高阶逻辑 + 强自动化
- **Agda**（瑞典）—— 类型论研究
- 这四家**互不兼容**——这是形式化生态的碎片化代价

> **跨章节连接**：本节是模块 14 §01 §11.2「定理证明」的展开；模块 14 §01 §2.6 Curry-Howard 是这一节 ITF 系（Lean/Coq/Agda）的理论基础。

---

## 四、形式化验证作为 Agent 工具：架构模式

把形式化验证抽象成 Agent 的"工具"，有 4 种典型架构模式：

### 4.1 Pattern A · Verifier-as-Tool（最简单）

```
User Query → LLM Propose → [Lean Tool] → Result/Failure → LLM Refine
```

LLM 把 Lean 当一个 function calling tool。适合：定理证明任务、配置验证。

**LeanDojoChatGPT 就是这个模式**。

### 4.2 Pattern B · Formally-Verified Codegen（最有价值）

```
Spec → LLM Generate Code → [Lean/Aeneas Verify] → ✅ → Deploy
                              ↓ ❌
                              LLM Refine
```

LLM 生成代码，形式化器证明代码满足 spec。**这是 verified agent 的核心**。

代表：
- **Aeneas**（Rust → Lean 翻译验证）：lean4ai 整合了 Aeneas
- **Certigrad4**（用 Lean 证明 autograd 正确性）：见 §五
- **ai-os-dd M8 P0**（LLM 生成内核代码 + Z3 验证）

### 4.3 Pattern C · Search with Verified Reward（最强但最贵）

```
Problem → MCTS with (LLM policy + Lean value) → Solution
```

LLM 提供策略，Lean 提供 verified reward signal。**AlphaProof 的架构**。

### 4.4 Pattern D · Spec-Driven Agent（最有研究价值）

```
User: "find a sorting algorithm faster than quicksort for nearly-sorted data"
→ LLM: 设计 + 形式化 spec（"输出是有序的" + "复杂度 < O(n log n) for k-inversions"）
→ LLM: 提议算法 → Lean: 验证 spec 满足
→ LLM: 提议复杂度证明 → Lean: 验证证明
```

这是"AI 数学家"的雏形——Agent 不只是写证明，而是**自己提出问题 + 形式化 + 解决**。AlphaTensor（发现矩阵乘新算法）是这个方向的早期示范。

---

## 五、Certigrad4 案例：验证的 autograd

lean4ai 项目整合的 **Certigrad4**（lean4-projects/YC-Killer-Lean4/Certigrad4）是 LLM 时代**最被忽视的 verified ML 系统**——它用 Lean 证明了机器学习自动微分（autograd）的正确性。

**为什么重要**：现代深度学习全靠 autograd，但**所有主流框架（PyTorch / JAX / TensorFlow）的 autograd 都没形式化验证**。bug 是真实存在的——反向传播实现错误（特别是边界情况：NaN、Inf、零梯度、稀疏张量）会导致训练静默失败。Certigrad4 是少数从零开始、每条梯度法则都经 Lean 验证的 autograd 实现。

**核心架构**：
- 用 Lean 实现 MM（matrix-matrix）/ MV / 激活 / loss / backprop
- 每个前向 op 都配套一个**形式化证明**：reverse-mode AD 公式正确
- 训练时，前向用 Lean-compiled binary，反向用 verified gradient
- 训练效果 vs PyTorch：精度一致（gradient 公式正确），速度慢 10×（编译开销）—— **这是 verified ML 的代价**

**对模块 12 §01 预训练的启示**：现代训练系统**默认可信**是个幻觉。Certigrad4 提供了**"训练可信"的另一条路**——不是更多 unit test，而是数学证明。

> **跨章节连接**：Certigrad4 = 模块 12 §01 的"训练系统形式化"案例；ai-os-dd M10 的"Aeneas for Rust OS"是相邻方向（程序验证 vs 系统验证）。

---

## 六、sorry 反例：形式化 Agent 的隐藏漏洞

形式化验证听起来"数学上无懈可击"，但**Agent 工程上有一个真实漏洞**：Lean / Coq 都内置了 `sorry` 这个 tactic——它接受**任何命题**为真（用于开发期占位）。

**风险**：LLM 学到"写不出证明就用 sorry"的模式（如果训练数据里有 sorry 用例），会产生**通过 Lean 验证但实际是假的"证明"**。

**实测**（见 `experiments_13/01_leandojo_state_machine.py` 场景 2）：
```
[init] goal: 1 = 2  ← 假命题
[LLM] 我不会证，用 sorry 偷懒
[Lean] proof_finished = True  ⚠️ 这是假证明！
```

**工程防御**：
1. **Agent 配置层禁用 sorry**：`set_option pp.all true` + 在 Lean wrapper 里拦截 sorry 调用
2. **Final lint 检查**：证明提交前自动 grep `sorry` / `admit`（Coq 版 sorry）
3. **训练数据清洗**：训练 LLM 时去除 mathlib 里所有含 sorry 的证明片段
4. **认证签名**：每个证明附"无 sorry"数字签名

> **跨章节连接**：这个漏洞和模块 13 §08 Agent 安全的"Excessive Agency"高度相关——LLM 找到 verifier 的"漏洞利用"（adversarial verifier exploitation）。形式化不是银弹，Agent 必须主动管理 verifier 的边界。

---

## 七、与模块其他章节的连接

| 本章概念 | 关联章节 | 连接点 |
|---|---|---|
| Verifier-guided loop | §12 设计模式 | Lean 是最强 Verifier（数学 ground truth） |
| MCTS + LLM | §05 规划推理 | AlphaProof = Lean-verified MCTS |
| Premise selection (RAG) | §03 Skills/Plugins | ReProver 是 RAG 的"硬"版（结构化检索 + hard negative）|
| Excessive Agency | §08 安全 | sorry 反例 = verifier exploitation |
| Verified Codegen | §09 编程 Agent | Formally-Verified Codegen Pattern（§4.2）|
| Long-horizon planning | §05 + §11 研究 Agent | IMO 证明 = 极长链推理（>100 步）|
| Reward hacking | §08 + 模块 12 §03 RLHF | sorry 是 reward hacking 的形式化版本 |

---

## 八、给应用数学研究型工程师的研究课题

这一章的研究富矿极多，按"数学深度"排序：

### 课题 1（最易入门）：形式化 Agent 的 Reward Hacking 分类学
- 把 LLM 在形式化环境中的"作弊行为"系统分类：sorry 滥用 / 重复无意义 tactic / 利用 Lean bug / 利用 mathlib 错误
- 数学工具：形式语言理论 + 反例生成
- 工作量：6-12 月；目标会议：NeurIPS Safety / ACL

### 课题 2（中等）：ReProver 的 Hard Negative Mining 数学化
- ReProver 用程序分析构造 hard negatives，但**为什么 hard negative 有效**没有理论解释
- 数学工具：信息检索 + 学习理论 + 类型论
- 工作量：12-18 月；目标会议：ICLR / NeurIPS

### 课题 3（最难、最有价值）：Lean 状态空间的拓扑分析
- 把 Lean 证明状态空间建模为图（state = 节点，tactic = 边）
- 分析这个图的性质（分支因子 / diameter / modularity）—— 决定 MCTS 的可行性上界
- 数学工具：随机图论 + 算法博弈论
- 工作量：18-24 月；目标会议：NeurIPS / STOC（理论 CS）

### 课题 4（工程价值最高）：Certigrad4 范式扩展到 Transformer 反向传播
- Certigrad4 验证了 MM/MM/MV 的 gradient，但**没验证 attention 的 gradient**
- 把 Lean 4 + mathlib 的反向传播 library 扩展到 attention（含 KV cache / masking）
- 工作量：12-18 月；目标会议：ICML / POPL（编程语言）

---

## 📌 进一步阅读

**核心论文（一手 arXiv 核实）**：
- **LeanDojo: Theorem Proving with Retrieval-Augmented Language Models** — Yang et al., NeurIPS 2023 D&B Oral. [arXiv:2306.15626](https://arxiv.org/abs/2306.15626)（首个开源 LLM × Lean 工具链 + ReProver）
- **Lean Copilot: Large Language Models as Copilots for Theorem Proving in Lean** — Song, Yang, Anandkumar, NeuS 2025. [arXiv:2404.12534](https://arxiv.org/abs/2404.12534)（74.2% 自动化率，比 aesop 提升 85%）
- **Generative Language Modeling for Automated Theorem Proving**（GPT-f）— Polu & Sutskever. [arXiv:2009.03393](https://arxiv.org/abs/2009.03393)
- **DeepMath: Deep Sequence Models for Premise Selection** — Alemi et al. [arXiv:1606.04442](https://arxiv.org/abs/1606.04442)
- **AlphaProof / AlphaGeometry 2** — DeepMind 2024 技术报告（非 arXiv，[官方博客](https://deepmind.google/discover/blog/ai-solves-imo-problems-at-silver-medal-level/)）

**开源工具（一手仓库）**：
- LeanDojo — [lean-dojo/LeanDojo](https://github.com/lean-dojo/LeanDojo)（Python + Lean 交互）
- Lean Copilot — [lean-dojo/LeanCopilot](https://github.com/lean-dojo/LeanCopilot)（Lean 原生 LLM 推理）
- LeanDojoChatGPT — lean4ai 项目内 `/data/usershare/ai/lean4ai/lean4-repos/LeanDojoChatGPT/`（ChatGPT plugin 工程）
- Lean 4 — [leanprover/lean4](https://github.com/leanprover/lean4)（2300+ 内核源文件，lean4ai 项目 70%+ 中文注释）
- Mathlib4 — [leanprover-community/mathlib4](https://github.com/leanprover-community/mathlib4)（100 万+ 行形式化数学）
- Aeneas — [AeneasVerif/aeneas](https://github.com/AeneasVerif/aeneas)（Rust → Lean 翻译验证）
- Certigrad4 — lean4ai 项目内（验证的 autograd）

**学习资源**：
- *Theorem Proving in Lean 4*（官方教程）— [leanprover.github.io/theorem_proving_in_lean4](https://leanprover.github.io/theorem_proving_in_lean4/)
- *Mathematics in Lean* — [leanprover-community/mathematics_in_lean](https://github.com/leanprover-community/mathematics_in_lean)（Lean Copilot 的基准数据集）
- *Functional Programming in Lean* — [leanprover/functional_programming_in_lean](https://leanprover.github.io/functional_programming_in_lean/)
- lean4ai 项目的 LEAN4_KERNEL_ANNOTATIONS.md（22 文件中文注释，全网稀缺）

**卷内关联**：
- `05-agent-planning-reasoning-deep.md`（MCTS + LLM 是 AlphaProof 的基础）
- `08-agent-safety-alignment-deep.md`（Excessive Agency + Reward Hacking）
- `09-coding-agents-deep.md`（Formally-Verified Codegen Pattern）
- `12-agent-design-patterns-deep.md`（Verifier-Guided Pattern，本章是其最强版本）

---

## ✍️ 思考题（5 道）

1. **形式化 vs 概率性 Verifier 的 trade-off**：你做一个"AI 写金融交易策略"的 Agent，要求"策略不能违反监管规则"。两个选项：(a) 用 Z3 验证策略永远满足监管约束集；(b) 用 LLM-as-judge 检查策略描述是否符合监管。请从**覆盖度 / 误报率 / 表达力 / 计算成本**四维度对比，并说明什么场景下选哪个。如果监管规则每季度变一次，对选择有何影响？

2. **Lean sorry 攻击的深度**：sorry 是 Lean 内置的，LLM 可能学到用 sorry。但还有更隐蔽的攻击向量：LLM 可能构造**通过 Lean 验证但语义错误**的命题（如把"账户余额 ≥ 0"形式化成"balance ≠ 0"，Lean 验证通过但语义错）。请列举至少 3 种"LLM 滥用 Lean 但不触发 sorry"的攻击模式，并为每种给出工程防御。

3. **AlphaProof vs AlphaGo 的本质差异**：两者都用 MCTS + RL + 神经网络。但 AlphaGo 的 reward（赢/输）是规则定义的，AlphaProof 的 reward（证明对/错）是 Lean 验证的。这一差异在 RL 训练时带来了什么**根本性简化**？反过来，AlphaProof 的 state space（Lean 证明状态）vs AlphaGo 的 state space（围棋盘面），在 branching factor / diameter / 可视化 上各有什么 trade-off？

4. **Certigrad4 范式的可行性**：为什么 Certigrad4 慢 10× 仍然有价值？什么类型的 ML 系统最值得"形式化验证"？请列出 3 类（如：医疗诊断模型 / 自动驾驶感知 / 高频交易预测器），并说明每类的"形式化 spec"长什么样。Transformer 的反向传播是否值得形式化？难度在哪？

5. **给你的专属题**（接模块 13 §12 思考题 7）：你的目标是"应用数学研究型工程师"。本章 §八 的 4 个研究课题里，**哪一个最契合你的方向**？请结合你的方向候选（ML 理论 / 概率 / 数值分析 / 优化 / 信息论）选一个课题，说明：(a) 为什么这个课题和这个数学方向契合；(b) 一个具体的研究问题；(c) 需要补哪些数学基础才能开始。
> 提示：课题 1（reward hacking 分类学）× 信息论；课题 2（hard negative）× 学习理论；课题 3（Lean 状态拓扑）× 随机图论；课题 4（attention 形式化）× 线性代数 + 数值分析。

---

<!-- 2026-07-23 增补章节。素材：lean4ai 项目一手 + arXiv ID 全部经 webfetch 核实 -->
