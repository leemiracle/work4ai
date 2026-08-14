# 前沿与媒体 · 11 - AI 政策、伦理与 Safety 专题

> 姊妹篇：[`01-H 类 AI Safety`](./01-AI顶级信息源实时清单.md)（基础源）、[`10-评测 E8`](./10-AI评测与基准大合集.md)（安全评测）。
>
> 01 清单 H 类列了 7 个核心安全源。本篇**深化+扩到政策/伦理/治理**——AI 法规、安全研究机构、对齐理论、风险评估、中文治理生态。给政策研究者/合规/对齐方向 PhD 的"专业版"。
>
> **核对日期**：2026-08-03（首版；EU AI Act/NIST AI RMF/CAIS 实抓活跃）
> **图例**：🟢 = 活跃　🟡 = 稳定　🔴 = 停更

---

## 0. 一张图：AI Safety 的四层

```
       ┌────────────────────────────────┐
       │  ① 治理层（国际/政府）           │   ← EU AI Act / NIST / UK AISI / 中国信通院
       └────────────────────────────────┘
                    ↓
       ┌────────────────────────────────┐
       │  ② 标准/框架层                   │   ← ISO 42001 / NIST AI RMF / Singapore Model AI
       └────────────────────────────────┘
                    ↓
       ┌────────────────────────────────┐
       │  ③ 研究层（前沿安全研究）         │   ← Anthropic Alignment / Redwood / Apollo / CAIS
       └────────────────────────────────┘
                    ↓
       ┌────────────────────────────────┐
       │  ④ 评测/工程层                   │   ← HarmBench / PurpleLlama / Sleeper Agents
       └────────────────────────────────┘
```

---

## 一、AI 法规（治理层）

| # | 法规 / 行动 | 立法方 | 状态 | 强项 |
|---|---|---|---|---|
| P1-1 | **EU AI Act** [artificialintelligenceact.eu](https://artificialintelligenceact.eu/) | 欧盟 | 🟢 ✅ 本轮实抓 | **全球首部综合 AI 法案**（2024-08 生效，2026 分阶段实施）；含 AI Act Explorer 工具 |
| P1-2 | **美国 NIST AI RMF** [nist.gov/itl/ai-risk-management-framework](https://www.nist.gov/itl/ai-risk-management-framework) | 美国 NIST | 🟢 ✅ 本轮实抓 | 自愿性风险管理框架（2023-01）|
| P1-3 | **美国行政命令 14110** | Biden 政府 | 🟡（2025 后被 Trump 政府调整）| "Safe, Secure, and Trustworthy AI" |
| P1-4 | **英国 AI Safety Institute (UK AISI)** [aiai.gov.uk](https://www.aiai.gov.uk/) | 英国 | 🟢 ⚠️本轮抓空 | 全球首个国家级 AI 安全研究所（2023-11）|
| P1-5 | **中国生成式 AI 服务管理办法** | 国家网信办 | 🟢 | 2023-08 实施，全球最早的生成式 AI 专项法规 |
| P1-6 | **新加坡 Model AI Governance** | Singapore IMDA | 🟢 | 东盟模板 |
| P1-7 | **加拿大 AIDA** | 加拿大 | 🟡 进行中 | AIDA 法案 |
| P1-8 | **Bletchley Declaration** | 28 国（2023-11）| 🟡 历史性 | 首份 AI 安全国际宣言 |

---

## 二、AI 标准 / 框架

| # | 标准 | 维护方 | 强项 |
|---|---|---|---|
| P2-1 | **ISO/IEC 42001:2023** | ISO/IEC | AI 管理体系标准（首个）|
| P2-2 | **NIST AI RMF 1.0** | NIST | 风险管理（核心函数：Govern/Map/Measure/Manage）|
| P2-3 | **NIST AI 600** | NIST | Generative AI Profile |
| P2-4 | **EU AI Act Compliance Framework** | 欧盟 | risk-tiered（不可接受/高/有限/最小风险）|
| P2-5 | **OCED AI Principles** | OECD | 2019，最早的国际 AI 原则 |
| P2-6 | **UNESCO AI Ethics** | UNESCO | 193 国通过（2021）|

---

## 三、AI Safety 研究机构（详见 [`01 H 类`](./01-AI顶级信息源实时清单.md)）

| # | 机构 | 类型 | 强项 |
|---|---|---|---|
| P3-1 | **Anthropic Alignment 团队** | Frontier lab 内 | Constitutional AI / Interpretability / Sleeper Agents（已在 [`01 A1`](./01-AI顶级信息源实时清单.md)）|
| P3-2 | **Redwood Research** | 独立非营利 | 可解释/对抗（[`01 A2`](./01-AI顶级信息源实时清单.md)）|
| P3-3 | **Apollo Research** | 独立 | Scheming / Situational Awareness（[`01 A3`](./01-AI顶级信息源实时清单.md)）|
| P3-4 | **CAIS（Center for AI Safety）** [safe.ai](https://safe.ai/) | 独立 | 政策+研究+声明（[`01 A6`](./01-AI顶级信息源实时清单.md)），本轮实抓活跃 |
| P3-5 | **MIRI（Machine Intelligence Research Institute）** | 独立 | Yudkowsky 派经典（[`01 A7`](./01-AI顶级信息源实时清单.md)）|
| P3-6 | **Conjectural**（Connor Leahy）| 独立 | 反共识开源对齐（[`01 A4`](./01-AI顶级信息源实时清单.md)）|
| P3-7 | **DeepMind Safety / OpenAI Superalignment** | Frontier lab 内 | Google + OpenAI 内部安全团队 |
| P3-8 | **UK AISI / US AISI** | 政府 | 国家级红队 |
| P3-9 | **MATS（ML Alignment & Theorem Scholars）** | 治学 | 对齐方向 PhD 训练营 |
| P3-10 | **Apollo / Redwood / Metr / Apollo Research** | 联合 | Frontier Safety 内嵌（与 Anthropic/OpenAI 合作）|

---

## 四、AI Safety 关键论文

| # | 论文 | arXiv | 一句话 |
|---|---|---|---|
| P4-1 | **Constitutional AI** | [2212.08073](https://arxiv.org/abs/2212.08073) | Anthropic 用 AI 反馈代替人工（已在 [`02 PT-F2`](./02-后训练信息源专题.md)）|
| P4-2 | **Sleeper Agents** | 2401.05566 | Anthropic 演示"潜伏后门" Agent 训练出来后无法用 RLHF 移除 |
| P4-3 | **Sycophancy** | 2310.13548 | 模型迎合用户偏见的失败模式 |
| P4-4 | **Toy Models of Superposition** | 2209.10652 | Anthropic 经典可解释性 |
| P4-5 | **Scaling Monosemanticity** | Anthropic 2024-05 | 把 superposition 拆成单语义神经元 |
| P4-6 | **Circuits / Distill 系列** | Anthropic / OpenAI | 可解释性根源（Olah/Carter）|
| P4-7 | **Specification gaming / Goodhart's Law** | 多方 | "测什么就被优化什么"经典 |
| P4-8 | **AI Safety gridworlds** | DeepMind 2017 | 经典 RL 安全评测 |

---

## 五、AI Safety 评测（详见 [`10 E8`](./10-AI评测与基准大合集.md)）

- **HarmBench** / **AdvBench** / **SneakyPrompt**（红队）
- **TruthfulQA**（真实性）
- **PurpleLlama / Llama-Guard**（Meta 安全套件）
- **Frontier Safety Evaluation**（与 AISI 合作）

---

## 六、AI 伦理 / 公平 / 偏见

| # | 议题 | 关键人物/机构 |
|---|---|---|
| P6-1 | **算法公平**（Fairness）| Timnit Gebru、Joy Buolamwini、Cynthia Dwork |
| P6-2 | **算法偏见审计** | Cathy O'Neil（《数学杀伤性武器》）|
| P6-3 | **隐私 / 数据**（GDPR / CCPA）| EFF / Future of Privacy Forum |
| P6-4 | **AI 与劳动**（就业替代）| Daron Acemoglu（MIT）|
| P6-5 | **AI 与版权**（生成式 AI 训练数据）| 多起诉讼（NYT vs OpenAI 等）|
| P6-6 | **AI 与民主**（虚假信息/deepfake）| Brookings / Brennan Center |

---

## 七、AI Safety 国际峰会 / 论坛

| # | 会议 | 频次 | 强项 |
|---|---|---|---|
| P7-1 | **AI Safety Summit**（英国 Bletchley 2023 → 韩国 2024 → 法国 2025）| 年度 | 政府级 |
| P7-2 | **Frontier Model Forum** | 持续 | OpenAI/Anthropic/Google/Meta 等联合 |
| P7-3 | **Partnership on AI (PAI)** | 持续 | 多方利益相关者 |
| P7-4 | **UN AI Advisory Body** | 持续 | 联合国 |
| P7-5 | **Beijing AI Safety International Dialogue** | 2024 起 | 中美英对话 |

---

## 八、中文 AI 治理生态

| # | 机构 | 强项 |
|---|---|---|
| CN-1 | **中国信息通信研究院（信通院 / CAICT）** | 政策智库，可信 AI 标准 |
| CN-2 | **国家新一代人工智能治理专业委员会** | 发布《新一代 AI 治理原则》|
| CN-3 | **中国科学院科技战略咨询研究院** | 战略研究 |
| CN-4 | **清华大学人工智能国际治理研究院（I-AIGC）** | 薛澜主持 |
| CN-5 | **中国人民大学高瓴人工智能学院** | 法学/伦理 |
| CN-6 | **复旦大学数字与移动治理实验室** | 治理研究 |
| CN-7 | **深圳人工智能伦理治理委员会** | 地方试点 |

---

## 九、维护说明

- **2026-08-03 首版**：✅ EU AI Act / NIST AI RMF / CAIS 实抓活跃；⚠️ UK AISI / 中国信通院 抓空。
- **下次重核**：每 6 个月（政策月级变化）。
- **重点跟踪**：
  - EU AI Act 2026 分阶段实施节点
  - 中国生成式 AI 新规（算法备案/数据安全）
  - Sleeper Agents 类风险研究进展
  - AI 与版权诉讼判例（NYT vs OpenAI 等）

📌 **下一步**：想做 AI 合规 / 对齐研究？告诉我你的角色（合规 / 研究者 / 政策分析师），我给推荐阅读 + 工作流。

---

> 🔗 相关：[`01 H 类`](./01-AI顶级信息源实时清单.md) ｜ [`10-评测 E8`](./10-AI评测与基准大合集.md) ｜ [`../讲透微调/`](../讲透微调/) RLHF 部分
