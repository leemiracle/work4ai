# AI_FOR_MATH_TOOLS：AI 辅助数学研究的工具栈（你的最大杠杆方向）

> **本章核心**：2024-2026，AI 正在进入数学研究。这是 [`LEAN_MATH_TRACK.md`](LEAN_MATH_TRACK.md) 的"工具层"深化——专门讲**怎么用 AI 做数学**。
>
> 这是你**最大杠杆方向**：你的 ML 工程能力 + Lean4 经验 + 数学学习路径 = 你能**用**这些工具，甚至**改**这些工具，甚至**造**这些工具。绝大多数数学学习者只能"用"，你能"造"。

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
│  L4: 端到端系统                              │  ← 自动证明管线
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
| 学 Lean 数学 | [`../讲透Lean4数学/`](../讲透Lean4数学/) | Lean 证明能力 |
| 学实分析 + Lean | [`../讲透实分析/`](../讲透实分析/) | Tao companion 填 sorry |
| 形式化 ML 理论 | [`../讲透统计学习理论/`](../讲透统计学习理论/) | 把泛化界写进 Lean |
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
