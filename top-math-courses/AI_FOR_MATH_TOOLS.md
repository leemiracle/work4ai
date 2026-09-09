# AI_FOR_MATH_TOOLS：AI 辅助数学研究的工具栈（你的最大杠杆方向）

> **本章核心**：2024-2026，AI 正在进入数学研究。这是 [`LEAN_MATH_TRACK.md`](LEAN_MATH_TRACK.md) 的"工具层"深化——专门讲**怎么用 AI 做数学**。
>
> 这是你**最大杠杆方向**：你的 ML 工程能力 + Lean4 经验 + 数学学习路径 = 你能**用**这些工具，甚至**改**这些工具，甚至**造**这些工具。绝大多数数学学习者只能"用"，你能"造"。
>
> **姊妹篇**：[PRACTICE_LAB.md](PRACTICE_LAB.md)——本章讲"用什么"，它讲"怎么做"（逐级命令+实验+晋级标准+Math-for-AI 五个最小实验）。

---

## 〇、为什么这是你最大的机会

### 0.1 范式变革的时间线

```
2020  Polu & Sutskever GPT-f            — 第一个用 LLM 做 Lean 证明
2022  Autoformalization (Wu et al.)     — 自然语言→Lean 自动翻译
2022  Scholze liquid tensor 形式化完成   — 大数学家用 Lean 验证自己的工作
2023  Polu et al. ProofNet              — auto-formalization 数据集
2023  Lean Copilot / LeanDojo           — Lean 的 AI copilot 开源
2024  AlphaProof IMO 2024 银牌          — AI 首次攻入高难数学
2025  Tao《Analysis I》Lean companion   — 教材可在 Lean 里做习题
2025  AlphaProof Nature 论文            — 严格学术发表
2025  Equational Theories Project       — 50+ 人 Lean 大规模协作
2026  AlphaProof Nexus                  — 攻 Erdős / OEIS 未解问题
```

### 0.2 你的稀缺位置

```
数学学习者（不会 Lean）        → 只能用 AI 解释概念
Lean 用户（不会 ML）           → 只能用 AI copilot 补全
ML 工程师（不懂 Lean/数学）    → 只能看论文
─────────────────────────────────────────────────
你（Lean4 OS + ML + 数学路径） → 能用 / 能改 / 能造 AI-for-math 工具
```

**这是 2025-2030 数学研究的 frontier**。DeepMind / Anthropic / OpenAI / 高校都在招这种交叉人才。

---

## 一、工具栈总览

### 1.1 按层次分类

```
┌─────────────────────────────────────────────┐
│  L5: 研究 frontier                          │  ← AlphaProof / AlphaProof Nexus
├─────────────────────────────────────────────┤
│  L4: 端到端系统                              │  ← 自动证明管线 ★DeepSeek-Prover-V2 已本地实战（内网 DCU：分解→子目标→lake 验证闭环，见 work4ai/讲透Agent/实战案例-Prover数学Agent/）
├─────────────────────────────────────────────┤
│  L3: LLM for math                           │  ← Llemma / DeepSeek-Prover / GPT-f
├─────────────────────────────────────────────┤
│  L2: 交互式 AI copilot                      │  ← Lean Copilot / Copra
├─────────────────────────────────────────────┤
│  L1: 自动定理证明器（ATP）                   │  ← Vampire / E / Z3
├─────────────────────────────────────────────┤
│  L0: 证明助手（形式化基础）                  │  ← Lean / Coq / Isabelle
└─────────────────────────────────────────────┘
```

### 1.2 你的切入顺序

```
L0（你已会）：Lean 4 + Mathlib
  ↓
L1（学）：调用 ATP（Vampire / Z3）做辅助
  ↓
L2（用）：装 Lean Copilot，写证明时让 AI 补全
  ↓
L3（玩）：试 Llemma / DeepSeek-Prover 模型
  ↓
L4（造）：自己搭一个 autoformalization 管线
  ↓
L5（贡献）：给 AlphaProof 类开源项目提 PR / 复现
```

---

## 二、L0：证明助手（已会，速览）

| 工具 | 数学覆盖 | 你的状态 |
|------|---------|---------|
| **Lean 4 + Mathlib** | 最广，2026 主流 | ✅ 已会（ai-os-dd）|
| **Coq / Rocq** | 强在 CS / 部分数学 | 选学 |
| **Isabelle / HOL Light** | 强在自动化 | 选学 |
| **Agda** | 依赖类型论理论 | 选学 |

详见 [`LEAN_MATH_TRACK.md`](LEAN_MATH_TRACK.md)。

---

## 三、L1：自动定理证明器（ATP）

这些是"老派 AI"（good old-fashioned AI），但**至今极有用**——Equational Theories Project 用它们解决了 90% 的蕴含关系。

| 工具 | 类型 | 用途 |
|------|------|------|
| **Vampire** | 一阶逻辑 ATP | 解大量"显然"的引理 |
| **E Prover** | 一阶 ATP | Vampire 替代 |
| **Zipperposition** | 高阶 ATP | 配 Lean |
| **Z3** | SMT solver | 算术 / 不等式 / 线性代数 |
| **CVC5** | SMT | Z3 替代 |
| **Mace4 / Paradox** | 反例查找 | 证"不蕴含" |
| **Prover9** | ATP | 经典 |

### 怎么用

```bash
# Vampire 安装
git clone https://github.com/vprover/vampire
cd vampire && cmake . && make

# Lean 里调用（通过 tactic `duper` 或 `auto）
import Mathlib
example : ∀ (a b : ℤ), a + b = b + a := by
  duper  -- 调用自动搜索
```

**对你的价值**：写 Lean 证明时，简单引理交给 ATP，你专注证难的。

---

## 四、L2：交互式 AI Copilot（最重要，立刻能用）

### 4.1 Lean Copilot（推荐立刻装）

**仓库**：https://github.com/lean-dojo/LeanCopilot

**作用**：在 VS Code + Lean 4 扩展里，AI 自动建议下一条 tactic / 整段证明。Tao 在用 GitHub Copilot 做类似事。

**安装**（在 Lean 项目里）：
```lean
-- lakefile.lean
require lean-copilot from git "https://github.com/lean-dojo/LeanCopilot" @ "v0.7.0"
```

**用法**：
```lean
import LeanCopilot

example : ∀ n : ℕ, 0 + n = n := by
  -- 输入 AI 命令
  suggest_tactics  -- AI 建议：intro n; induction n ...
```

### 4.2 Copra

**仓库**：https://github.com/yangky11/Copra

**作用**：基于 LLM 的 Lean 证明助手，比 Lean Copilot 更强（论文级）。

### 4.3 LeanDojo

**仓库**：https://github.com/lean-dojo/LeanDojo

**作用**：Lean 的 Python API，让你**用 ML 训练** Lean 证明模型。**这是研究者用的工具**——你能用它复现 AlphaProof 类工作。

**对你**：如果你想做 AI-for-math 研究，**这是你必学的工具**。

---

## 五、L3：LLM for Math（专用模型）

### 5.1 专用数学 LLM

| 模型 | 论文（arXiv 待核实）| 贡献 |
|------|-------------------|------|
| **GPT-f**（Polu & Sutskever 2020）| 2009.03393 | 第一个 Lean LLM |
| **Llemma**（EleutherAI 2023）| 2310.10631 ⚠️待核实 | 数学专用 base model |
| **DeepSeek-Prover**（DeepSeek 2024）| 2405.14303 ⚠️待核实 | Lean 专用，强 |
| **InternLM-Math** | — | 中文友好 |
| **MathLlama / Llama-3-Math** | — | 开源 |
| **WizardMath / MetaMath** | — | 微调版 |

### 5.2 通用 LLM 在数学上

| 模型 | 数学能力（2026）|
|------|----------------|
| **GPT-5 / Claude 4.x / Gemini 2.5** | 强，能解题但会幻觉 |
| **o1 / o3（推理模型）** | 数学推理强 |
| **DeepSeek-R1** | 开源推理模型 |

> ⚠️ **关键**：通用 LLM 在数学上**会幻觉**。所有输出必须人工或 Lean 验证。

### 5.3 怎么用 LLM 辅助数学研究

```
合法用法：
✅ 解释概念（"什么是 Itô 积分"）
✅ 找相关文献（"这个方向的奠基论文是什么"）
✅ 头脑风暴（"这个定理能怎么推广"）
✅ 自动补全 Lean tactic（Lean Copilot）
✅ 翻译（自然语言→Lean，需验证）

危险用法：
❌ 直接信 LLM 给的证明（必须验证）
❌ 让 LLM 提猜想却不验证
❌ 用 LLM 写论文却不引用
```

---

## 六、L4：端到端系统（研究者层级）

### 6.1 AlphaProof 架构（Nature 2025）

```
问题（自然语言）
  ↓ autoformalization（Gemini fine-tune）
Lean 形式化
  ↓
LLM 提 tactic
  ↓ Lean 验证
通过 → 强化学习反馈
  ↓
AlphaZero 式搜索
  ↓
完整 Lean 证明
```

**核心组件**：
- Lean 4 + Mathlib 作为环境
- LLM（Gemini 系）做 tactic 预测
- AlphaZero 式 MCTS + RL
- TTRL（test-time RL）：在推理时继续训练

### 6.2 Autoformalization 管线

```
自然语言数学 → LLM → Lean 代码 → Lean 编译验证
                ↑                ↓
                └── 错误反馈 ←──┘
```

**关键工具**：
- **Wu et al. 2022 autoformalization**（arXiv:2205.12615）
- **ProofNet**（Polu et al. 2023）：auto-formalization 数据集

### 6.3 你能复现的最小系统

用 LeanDojo + 一个开源 LLM（DeepSeek-Prover 或 Llemma）+ 你自己的训练管线。

参考开源项目：
- **LeanDojoExamples**：https://github.com/lean-dojo/LeanDojoClient
- **DeepSeek-Prover 复现**：看论文 §implementation

---

## 七、L5：研究 frontier（论文级）

### 7.1 必读论文（已核实 ID）

| 论文 | ID / DOI | 核心贡献 |
|------|---------|---------|
| **AlphaProof** Nature 2025 | `10.1038/s41586-025-09833-y` | IMO 银牌，完整 RL 框架 |
| **AlphaGeometry 2** | 同 AlphaProof 配套 | 几何专用 |
| **Polu & Sutskever GPT-f** 2020 | `arXiv:2009.03393` | 第一个 Lean LLM |
| **Wu et al. Autoformalization** 2022 | `arXiv:2205.12615` | 自然语言→Lean |
| **Han, Lewis, Rute 等** "Theorem proving with Lean" 综述 | — | 入门 |
| **First et al. Baldur** 2023 | `arXiv:2303.04910` | whole-proof 生成 + 修复 |
| **Azerbayev et al. Llemma** 2023 | `arXiv:2310.10631` ⚠️ | 数学 base model |
| **DeepSeek-Prover** 2024 | `arXiv:2405.14303` ⚠️ | Lean 专用强模型 |
| **Equational Theories Project** | teorth.github.io/equational_theories/paper.pdf | 大规模协作 |
| **Tao "Machine Assisted Proofs"** | terrytao.wordpress.com | 综述 |

> ⚠️ 标 ⚠️ 的 arXiv ID 是凭记忆，**正式读前 webfetch abs 页核实**（你的铁律：错误率 30-50%）。

### 7.2 开源项目（可贡献）

| 项目 | URL | 怎么贡献 |
|------|-----|---------|
| **Mathlib** | github.com/leanprover-community/mathlib4 | 加引理 / 改证明 |
| **miniF2F** | github.com/google-deepmind/miniF2F | 加题目 / 改 formalization |
| **formal-conjectures** | github.com/google-deepmind/formal-conjectures | 形式化数学猜想 |
| **Lean Copilot** | github.com/lean-dojo/LeanCopilot | 改 copilot 功能 |
| **LeanDojo** | github.com/lean-dojo/LeanDojo | 改 API |
| **AlphaProof Nexus results** | github.com/google-deepmind/alphaproof-nexus-results | 学习 / 验证 |
| **FLT 形式化** | github.com/ImperialCollegeLondon/FLT | 长期参与 |

---

## 八、基准与数据集（评估你/你模型的能力）

| 基准 | 评什么 | URL |
|------|--------|-----|
| **miniF2F** | 高中奥数 Lean 形式化 | github.com/google-deepmind/miniF2F |
| **ProofNet** | 大学数学 auto-formalization | — |
| **MATH** | 高中奥数（自然语言）| hendrycks/math |
| **GSM8K** | 小学应用题 | — |
| **Lean-Workbook** | Lean 训练数据 | — |
| **Lean theorem proving benchmark** | Lean 证明能力 | LeanDojo 配套 |

### 你的目标

- **6-12 个月**：在 miniF2F 上做 10-20 道题（人工证明）
- **1-2 年**：跑 DeepSeek-Prover / Llemma 在 miniF2F，看 SOTA
- **2-3 年**：自己改进某个 baseline（研究级贡献）

---

## 九、给你的具体执行路径

### 阶段 1：用（第 1-3 月）

```
□ 装 Lean Copilot，在日常 Lean 写作中用
□ 注册 HuggingFace，下载 Llemma / DeepSeek-Prover 试
□ 读 AlphaProof Nature 论文（abstract + intro）
□ 在 miniF2F 上手动解 5 题
```

### 阶段 2：懂（第 3-12 月）

```
□ 学 LeanDojo，用 Python 调 Lean
□ 跑 DeepSeek-Prover 推理，看输出
□ 读 GPT-f / Autoformalization 论文
□ 理解 AlphaProof 架构（用 paper §methods）
```

### 阶段 3：改（第 12-24 月）

```
□ 给 Lean Copilot / LeanDojo 提 PR
□ 在 miniF2F 子集上跑你的 prompt 工程
□ 试 prompt 一个通用 LLM（Claude/GPT）解 Lean 题
□ 写一篇 blog 比较 Llemma / DeepSeek-Prover / Claude
```

### 阶段 4：造（第 24+ 月，研究级）

```
□ 复现一个简化版 AlphaProof（小 LLM + Lean + 简单 RL）
□ 找一个 niche（如：形式化 ML 理论论文）
□ 写第一篇 arXiv 论文
□ 申请 DeepMind / Anthropic / 高校 AI4Math 实习
```

---

## 十、AI for Math 的 Open Problems（你的研究方向候选）

### 10.1 工具层

- de Bruijn factor < 1 的工具链（Tao 预测）
- Lean → 自然语言的反向翻译（"解释 Lean 证明"）
- 数学 OCR（把 PDF 公式准确翻成 LaTeX/Lean）

### 10.2 模型层

- Lean 专用 LLM 的 scaling law
- 长证明的记忆机制（当前 LLM 上下文不够）
- 自动猜想生成（不只是证已知，还能提新猜想）

### 10.3 系统层

- Test-time RL（AlphaProof 的核心）的更高效版
- 大规模人类-AI 协作（Equational Theories 模式的扩展）
- 数学论文默认附 Lean 文件的工具链

### 10.4 评估层

- 超越 miniF2F 的基准（研究生级 / 研究级）
- auto-formalization 的准确率从 30% → 95%
- 形式化论文的"难度"量化

---

## 十一、社区

### 11.1 必加

- **AI for Math Discord**（搜索邀请链接）
- **Lean Zulip** 的 `#AI for Math` 频道
- **Math AI Workshop**（NeurIPS / ICML 每年有）
- **Twitter**：跟 @terrytao / @_akhaliq（AK，每日 AI 论文）/ @swebbert（Sebastian）

### 11.2 会议

- **NeurIPS AI for Math Workshop**
- **ICML SKY Workshop**
- **ITP / CPP**（形式化）
- **AIM workshops**（AI for Math 专题）

### 11.3 实习 / 工作

- **DeepMind**（AlphaProof 团队，伦敦）
- **Anthropic**（理解团队，部分做 math reasoning）
- **OpenAI**（o-series reasoning）
- **高校 AI4Math**：Stanford（Szegedy）/ CMU / Berkeley / Imperial（Buzzard）

---

## 十二、与 work4ai 系列联动

| 你做的事 | 在哪做 | 产出 |
|---------|-------|------|
| 学 Lean 数学 | [`../讲透Lean4数学/`](../讲透数学/讲透Lean4数学) | Lean 证明能力 |
| 学实分析 + Lean | [`../讲透实分析/`](../讲透数学/讲透分析/讲透实分析) | Tao companion 填 sorry |
| 形式化 ML 理论 | [`../讲透统计学习理论/`](../讲透数学/讲透统计学习理论) | 把泛化界写进 Lean |
| 跑 AI4Math 实验 | 本方向 | blog + 论文 |

---

## 十三、给你的最终建议

**这是你的最大杠杆方向**。理由：
1. 你已有 Lean4 经验（99% 数学学习者没有）
2. 你已有 ML 工程能力（99% Lean 用户没有）
3. 这是 2025-2030 frontier（DeepMind / Tao / Buzzard 都在投）
4. **人少 + 门槛对你低 + 时代红利**

**建议**：
- 主攻方向选 **AI for Math**（不是纯 ML 理论，也不是纯形式化数学）
- 5 年目标：在 miniF2F / ProofNet 上做出 SOTA 贡献
- 10 年目标：被 DeepMind / Anthropic / 高校 AI4Math lab 聘为研究员

---

## 十四、方法论层：人机协作分级与日常工作流（2026-08-25 增补）

> **增补来源**：三份外部综述（通用 LLM 选型 / 推理模型工作流 / 2026 数学家 AI 实践建议）逐条与本项目去重后，只收录**项目原先没有的真增量**；关键事实全部一手核实（2026-08-25），核实不到的明确标注并排除。

### 14.0 三个框架各管一层（不要混用）

| 框架 | 回答的问题 | 在哪 |
|------|-----------|------|
| 本文 L0-L5 工具栈 | **用什么工具** | 本章 §一 |
| Haase & Pokutta 四层分级 | **人和 AI 协作到多深** | §14.2（新增）|
| MATH_LOOP_ENGINE 七阶段循环 | **每天怎么转起来** | [MATH_LOOP_ENGINE.md](MATH_LOOP_ENGINE.md) |

三者正交：工具栈是武器库，协作分级是交战规则，循环引擎是你的日程表。

### 14.1 Haase & Pokutta 四层协作分级（2024 preprint → 2026 出书）

**出处（两版都已核实）**：Haase & Pokutta, *Human-AI Co-Creativity*, arXiv:2411.12527（2024-11-19）；正式版收录于 Kaufman & Worwood 编 *Generative Artificial Intelligence and Creativity* 第 16 章 pp.205-221, 2026, DOI `10.1016/B978-0-443-34073-4.00009-5`。

| 层级 | 定义 | 数学场景 | 时间线（Pokutta DFG 报告 2026-05）|
|------|------|---------|------|
| L1 **Digital Pen** | 数字化工具，零创造输入 | LaTeX 自动补全、bibtex 查找 | "2000s" |
| L2 **AI Task Specialist** | 边界明确的子任务外包 | "生成前 1000 个素数并画分布"、n=3,4,5 数值验证 | 2022-2025 |
| L3 **AI Assistant** | 带工具+验证的 Agent 参与探索 | 猜想讨论、反例构造、Lean Copilot 补全 | 2025- |
| L4 **AI Co-Creator** | 平等贡献原创数学内容 | 平面染色新构造（Haase & Pokutta 自家案例：30 年无进展的 coloring 问题找到新 six-coloring）| 2027(?)，Pokutta 自己打问号 |

**用法**：接到任务先问"这该配哪层"——文献格式化给 L1，数值实验给 L2，证明思路讨论 L3，L4 目前只在受限领域（组合构造/形式化搜索）可行。**层级不互斥**，同一项目不同子任务可混用。

### 14.2 The Agentic Researcher（2026）：五级 taxonomy + 十条戒律 ★对你最重要

**出处（全部核实）**：Zimmer, Pelleriti, Roux & Pokutta, *The Agentic Researcher: A Practical Guide to AI-Assisted Research in Mathematics and Machine Learning*, arXiv:2603.15914（2026-03-16），ZIB + TU Berlin。ICML 2026 Workshop "AI as a Tool for Mathematics, Computer Science, and Machine Learning" **Oral**（2026-07-09）。开源：github.com/ZIB-IOL/The-Agentic-Researcher。

核心主张：**不需要从零造专用系统**——把科学方法论写成 agent prompts（他们称 **commandments/戒律**，放在持久 `INSTRUCTIONS.md`），通用 CLI coding agents（Claude Code / Codex CLI / **OpenCode** / Gemini CLI）就能变成自主研究助理。沙箱容器 + 多 GPU，最长自主会话 20+ 小时，六案例覆盖 pretraining/pruning/quantization + 凸优化/组合优化/代数几何。

**数学专用戒律（三条，直接可抄进你的 AGENTS.md）**：
1. **derivations before code**——先推公式再写代码
2. **precise notation**——符号先精确定义
3. **counterexample-first reasoning**——先试着找反例再试图证明

**与你的实战互链**：[讲透Agent/实战案例-Prover数学Agent](../讲透Agent/实战案例-Prover数学Agent/README.md) 的"逆向蒸馏十条规律"（R1-R10）与 ZIB 的"十条戒律"是**同一哲学的独立实现**——你从 DeepSeek-Prover-V2 论文逆向，ZIB 从 1.5 年 MATH+ 项目实践提炼。两边对读 = 该方向的 double coverage。他们的五级 taxonomy（从无 AI 到 Level 4 "AI as Research Associate"：研究者只给研究问题+工具+先验知识，Agent 自主跑"形式化→实现→评估→记录→更新报告"循环）比 Haase & Pokutta 四层更贴研究实操。

### 14.3 Williamson 2026 Chauvenet 奖：DL 对纯数学家的诚实定位

**出处（全部核实）**：Geordie Williamson, *Is Deep Learning a Useful Tool for the Pure Mathematician?*, Bulletin of the AMS 61(2), April 2024, 271-286（arXiv:2304.12602）。**获 2026 Chauvenet Prize**（MAA，2026-05-29 官宣——AMS Bulletin AI 专刊一文）。

核心内容（可直接用于选题）：
- **选问题三规则**：① noise-stable（神经网怕噪声敏感函数，ζ(s) 不是图像）② high-dimensional（难度应来自维度而非函数本身复杂度）③ unit cube（网络内部数值应有界）
- **定位论点**：DL 最有用的是数学过程的 **system 1**（直觉）部分——找模式、判断反例藏在哪、决定下一步算什么；不是 system 2（推理）
- **三案例**：反例构造 / 猜想生成 / 暴力计算指导（正好是你 top-physics Hinton 原型之外的第二个"跨数学-AI 顶流"样本）
- 获奖感言值得记住：文章写于 LLM 刚普及之时，"landscape has become considerably more complicated since then"——**连 Williamson 都说这领域变得复杂了，选型必须持续重估**。

### 14.4 对抗性审查工作流：让 AI 扮演怀疑者（项目原先没有）

你已有的验证手段全是"机器误"防线（Lean 编译、SymPy 恒等、数值阈值）。缺的是"**人误**"防线——你自己爱上自己的错误证明时，没人拦你。范式 prompt（可直接抄）：

> "我试图证明 X，步骤如下：[你的证明]。请你**以最苛刻的审稿人身份**找出漏洞，特别检查：(1) 每个不等式是否在所有参数区域成立（边界/退化情形）；(2) 是否隐含未声明的假设（收敛性、可交换性、非退化性）；(3) 反例构造是否真的满足全部前提；(4) 按 Williamson 三规则，这个问题本身是否适合当前方法。"

**分工**：怀疑者审查抓**隐含假设与逻辑跳跃**（LLM 强项），Lean 抓**步骤合法性**（机器强项），两者不可互相替代。

### 14.5 数学家的每日 AI 循环（社区模板，作为 MATH_LOOP_ENGINE 的轻量版）

| 时段 | 活动 | 对应层 |
|------|------|--------|
| 晨 | AI 总结 overnight arXiv 与你领域相关的 3-5 篇核心定理 | L2 |
| 上午 | Lean 推进证明，卡住用 Lean Copilot / 与 LLM 讨论方向 | L3 |
| 下午 | 猜想→Python/SymPy 数值验证→观察模式 | L2/L3 |
| 晚 | AI 整理笔记生成 LaTeX 草稿；**关键定理陈述与证明必须亲笔** | L1 |

你已有更细的 [MATH_LOOP_ENGINE](MATH_LOOP_ENGINE.md)（七阶段+五 reward），此表仅作没有循环引擎时的通用 fallback。**补一条模板没有的纪律：每天保留 1-2 小时无 AI 时间用纸笔思考**（防直觉退化——这是三份综述唯一共识且项目原先没写的）。

### 14.6 工具选型补遗（2026-08-25 核实状态）

| 条目 | 状态 | 事实 |
|------|------|------|
| Claude Mythos Preview | ✅ 已核实（官方 System Card）| 2026-04-07 发布，USAMO 2026 得 97.6%（前代 Opus 4.6 为 42.3%），**官方明确 not planned for general availability——数学家实际用不到** |
| GPT 5.4 / 5.5 | ✅ 已核实（第三方转述）| GPT 5.4 于 2026-03 USAMO 近饱和（95%）；GPT 5.5 系统卡报告 FrontierMath 级结果。**对数学家的教训：榜单第一 ≠ 可用，选你够得着的** |
| Claude Opus 4.5 / 4.6 | ✅ 已核实 | Mythos 前代，公开可用，长文写作/一致性强 |
| "Claude Opus 5" / "Gemini 3.1 Pro" / "Mythos 数学基准 47.6 分第一" | ❌ 未核实到，**不采纳** | 按铁律：模型名与数字必须官方源核实 |
| Julius AI / Thetawise | ⚠️ 未深核 | 综述提及的专业数学数据分析工具，用前自行核实 |
| DeepSeek-Prover-V1.5（miniF2F 63.5%）| ✅ 数字属实但已过时 | 你已在本地跑 **V2**（MiniF2F-test 88.9% Pass@8192），见 Prover 单元 |

### 14.7 避坑四条（对 §5.3"合法/危险用法"的增补）

1. **符号计算幻觉** → 一切符号结果用 Mathematica/SageMath 或 Lean 二次验证，不信 LLM 口算
2. **假定理假文献** → LLM 只用于找方向；引用必须 MathSciNet / arXiv 亲手核（= 你的全局铁律 2 在数学场景的化身）
3. **直觉退化** → 无 AI 时段（§14.5）
4. **启发式 ≠ 证明** → AI 给的"证明思路"进论文前必须过形式化或严格人工审查（= Williamson "system 1 vs system 2" 的操作化）

**文献工作流增补**：Semantic Scholar API 批量拉摘要 → LLM 按定理分类综述 → 人工核对引用。比"让 LLM 直接列论文"多一层机器可查的来源链。

### 14.8 本节新增文献（已核实，可直接读）

| 文献 | 锚点 |
|------|------|
| Haase & Pokutta 2026（书章节）| DOI 10.1016/B978-0-443-34073-4.00009-5；preprint arXiv:2411.12527 |
| Zimmer et al., The Agentic Researcher 2026 | arXiv:2603.15914 + github.com/ZIB-IOL/The-Agentic-Researcher |
| Williamson 2024/获奖 2026 | Bull. AMS 61(2) 271-286；arXiv:2304.12602；MAA 官网 2026-05-29 |
| Pokutta DFG 报告 slides（四层时间线）| pokutta.com/slides/20260505_DFG_RG.pdf（2026-05-05）|

---

📌 **下一步**：
- **本周**：装 Lean Copilot，在讲透Lean4数学练习中用
- **本月**：读 AlphaProof Nature 论文 + 在 miniF2F 解 5 题
- **本年**：学 LeanDojo，跑 DeepSeek-Prover
- **明年**：给 LeanDojo / Lean Copilot 提 PR
- **持续**：跟 AI for Math Discord + Twitter @terrytao / @_akhaliq

## ✍️ 练习

1. **装**：在任一 Lean 项目里装 Lean Copilot，编译通过。
2. **读**：AlphaProof Nature 论文 abstract + introduction（https://www.nature.com/articles/s41586-025-09833-y）。
3. **跑**：从 miniF2F 选 5 题，手动证明（不用 AI）。
4. **对比**：让 Claude / GPT / DeepSeek-Prover 解同样 5 题，对比。
5. **思考**：如果你要做 AI for Math 研究，你的 niche 是什么？（提示：形式化 ML 理论 / auto-formalization / 数学 LLM 训练数据...）
