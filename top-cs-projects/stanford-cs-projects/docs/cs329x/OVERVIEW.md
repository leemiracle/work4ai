# CS329X: Human-Centered NLP (人本 NLP)

> Stanford University, Autumn 2025
> Instructor: **Diyi Yang** (Stanford NLP/HCI 双聘)
> Time: Tue/Thu 4:30-5:50 PM, CoDa B90
> Prerequisites: CS224N / CS224U / CS224V / CS336 之一
> Difficulty: ⭐⭐⭐⭐⭐

---

## 📚 课程定位

**CS329X 反对纯技术指标**——强调 alignment、personalization、culture、privacy、well-being。

> "AI 不是越强越好，而是越懂人越好"

与 CS329Z（工程）和 CS329A（自我改进）形成完整视角：
- CS329A: AI 怎么变强
- CS329Z: AI 怎么造
- **CS329X: AI 为谁造**

---

## 📅 完整模块（17 讲）

### Week 1-2: Foundations + Alignment
- **L1 (Sep 23)** — Intro to Human-Centered NLP
- **L2 (Sep 25)** — LLMs Crash Course
  - DSPy / The Prompt Report
- **L3 (Sep 30)** — Learning from Human Preferences
  - 🔴 **InstructGPT** (Ouyang 2022) — RLHF 起点
  - 🔴 **DPO** (Rafailov 2023)
- **L4 (Oct 2)** — Pluralistic Alignment ⭐
  - 🔴 **Constitutional AI** (Bai 2022)
  - 🔴 **Pluralistic Alignment Roadmap** (Sorensen 2024)

### Week 3: Personalization + Data
- **L5 (Oct 7)** — 🎤 Will Held "Data, Data, Data"
  - **LIMA** (Zhou 2023) — 1000 条 > 5 万
  - **FineWeb** (Penedo 2024) — 工业级
  - Longpre 2024 *Data Authenticity Broken*
- **L6 (Oct 9)** — 🎤 Omar Shaikh + Taylor Sorensen: Personalization

### Week 4: Human-AI Interaction
- **L7 (Oct 14)** — HAI Interaction
  - **ConstitutionMaker** (Petridis 2023)
  - **Rehearsal** (Shaikh 2023) — 模拟冲突教学
  - **CollabLLM** (Wu 2025)
  - **Collaborative Gym** (Shao 2024) — Diyi 组
- **L8 (Oct 16)** — Evaluating HAI
  - **RealHumanEval** (Mozannar 2024)
  - Long 2024 *Not Just Novelty*
  - Lee 2022 *Evaluating Human-LM*

### Week 5: Design + UI
- **L9 (Oct 21)** — Design Thinking + UI
  - Pea 1986 *User Centered Design*
  - Friedman *Value Sensitive Design*
  - Birhane 2022 *Participatory AI*
- **L10 (Oct 23)** — 🎤 Eric Zelikman (Stanford/Redwood)
  - STaR 作者（与 CS329A L6 共享）

### Week 6: Generative Interfaces + Culture
- **L11 (Oct 30)** — Generative Interfaces
  - Cao 2025 *Generative Malleable UIs*
  - **Generative Interfaces for LMs** (Chen 2025, Diyi 组)
- **L12 (Nov 6)** — Culture and Values
  - Hershcovich 2022 *Cross-Cultural NLP*
  - 🔴 **PRISM Alignment Project** (Kirk 2024) — 全球 alignment 数据集
  - Naous 2023 *Having Beer After Prayer* — 文化偏见

### Week 7: Anthropomorphism + Privacy
- **L13 (Nov 11)** — Anthropomorphism + 🎤 Alice Oh
  - **AnthroScore** (Cheng 2024)
  - 🔴 **Reeves & Nass 1996** *Media Equation* — 经典 HCI
- **L14 (Nov 13)** — 🎤 Niloofar Mireshghallah: Privacy
  - Carlini 2021 *Extracting Training Data*
  - 🔴 **PrivacyLens** (Shao 2024) — Diyi 组代表作
  - Mireshghallah 2023 *Can LLMs Keep a Secret?*
  - Zhang & Yang 2025 *Searching Privacy in LLM Agents*

### Week 8: Companions + Future of Work
- **L15 (Nov 18)** — AI Companions + 🎤 Myra Cheng
  - 🔴 **Rise of AI Companions** (Zhang 2025) — Diyi 组
  - Pataranutaporn 2025 *My Boyfriend Is AI*
  - **INTIMA** (Kaffee 2025)
- **L16 (Nov 20)** — Future of Work
  - 🔴 **GPTs are GPTs** (Eloundou 2023) — OpenAI
  - **Future of Work with AI Agents** (Shao 2025) — Diyi 组
  - Anthropic Economic Index (2025)

### Week 11: Conclusion
- **L17 (Dec 2)** — Open Questions

---

## 💻 项目代码

📁 `topic3-safety/pluralistic_safety.py`

**实现**:
1. ✅ 投票机制（Plurality / Borda / Condorcet）
2. ✅ Condorcet 悖论（投票循环）
3. ✅ Pluralistic Alignment
4. ✅ Red Teaming（5 种攻击模板）

---

## 🎤 嘉宾阵容

- **Will Held** - Data
- **Omar Shaikh** - Personalization + Grounding
- **Taylor Sorensen** - Pluralistic Alignment
- **Eric Zelikman** - Reasoning / STaR
- **Alice Oh** (KAIST) - Codeswitching
- **Niloofar Mireshghallah** - LLM Privacy（领域 No.1）
- **Myra Cheng** - Anthropomorphism

---

## 📊 评分

| 部分 | 占比 |
|------|------|
| Homework 1-3 | ~45% |
| Project Proposal | ~5% |
| Midway Report + Presentation | ~15% |
| Final Report + Presentation | ~30% |
| Participation | ~5% |

---

## 🎯 学习路径

| 角色 | 推荐 |
|------|------|
| **想做 AI 伦理/政策** | CS329X 必修 |
| **想做 AI 产品经理** | CS329X + CS329Z |
| **想做 Safety 研究** | CS329X + CS120 + CS329H |
| **想做 AI 伴侣 / 社交** | CS329X + CS147 |

---

## 💡 批判性观察

1. **Diyi Yang 自己工作占比过高** — ~40% 论文是她组的
2. **偏人文，工程深度不足** — DPO 出现但不真训
3. **缺 non-Western 视角** — 讲文化但讲师嘉宾都西方背景
4. **AI Companions 缺批判声音** — Character.AI 自杀案没充分讨论
5. **Future of Work 偏乐观** — 没充分讨论失业 / 权力集中

---

**对应代码**: `topic3-safety/pluralistic_safety.py`
