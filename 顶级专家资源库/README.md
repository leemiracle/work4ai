# 顶级专家资源库

> **建立日期**：2026-08-13
> **配套**：`../顶级专家之路-GAP_ANALYSIS.md`（先读这份，理解为什么需要本资源库）
> **宗旨**：成为 Karpathy / Levine / Nanda 级别的 AI 顶级专家，需要的**所有外部资源**——已按 2026-08 一手核实，按 ROI 排序，每个资源标注「是什么 / 何时用 / 入门动作」。

---

## 🎯 一句话定位

你 work4ai 仓库的 613 个 md 解决的是「**学什么**」。
本资源库解决的是另外 3 个 equally important 的问题：
- **跟谁学**（真人导师 + 同行 + reviewer）
- **用什么练**（真实数据 + 真实算力 + 真实工具链）
- **往哪发**（workshop / main track / blog / Twitter）

**铁律**：知识可以独学，专家身份不能。本库的资源**全部需要真人/真钱/真出丑**——这就是它的价值。

---

## 📂 文件导航（按优先级）

### 🔴 P0 立即使用（决定成败）

| 文件 | 解决什么 |
|---|---|
| [`01-数学地基.md`](01-数学地基.md) | 9 阶段数学补强路径（M1-M9，从 MIT 6.042J 到 Vershynin 高维概率），**与阶段 E 并行**，不能等阶段 4 |
| [`02-社群与导师网络.md`](02-社群与导师网络.md) | EleutherAI / ML Collective / DLCT / APART / **MATS** 等 + Twitter 50 人 follow list |
| [`03-顶会日历与论文资源.md`](03-顶会日历与论文资源.md) | NeurIPS / ICML / ICLR / COLM / ACL 2026-2027 日历 + workshop 路径 + arXiv 日常 |

### 🟠 P1 第一季度使用（决定方向）

| 文件 | 解决什么 |
|---|---|
| [`04-算力资源.md`](04-算力资源.md) | HF ZeroGPU 免费 + RunPod/Vast 付费 + 学术申请路径 |
| [`05-方向深选-Mechanistic-Interpretability.md`](05-方向深选-Mechanistic-Interpretability.md) | 推荐方向：必读 / 必复现 / TransformerLens + SAELens + nnsight 工具链 |
| [`06-ML工程实战.md`](06-ML工程实战.md) | vLLM / transformers / tinygrad PR 贡献路径 + 真实数据集 + 训练 debug |

### 🟡 P2 半年内启动（决定产出）

| 文件 | 解决什么 |
|---|---|
| [`07-产出与写作平台.md`](07-产出与写作平台.md) | Hugo/Astro 自建 blog + Twitter 学术圈 + arXiv 投稿 + OpenReview 当 reviewer |
| [`08-工具栈.md`](08-工具栈.md) | uv / pixi / W&B / MLflow / DVC / tmux / WezTerm |
| [`09-奖学金与求职.md`](09-奖学金与求职.md) | Fellowship 全清单 + PhD 申请 + Anthropic/OpenAI/DeepMind 求职 |
| [`10-软实力与方法论.md`](10-软实力与方法论.md) | 论文写作 / chalk talk / 笔记系统 / 时间管理 / 反拖延 |

---

## 🚨 三件事本周必做（按时间顺序）

### 第 1 件（今天，30 分钟）：进社群
- [ ] 加 EleutherAI Discord（`eleuther.ai/community`）— 潜水 2 周再发言
- [ ] 加 ML Collective Discord（`mlcollective.org`）
- [ ] 订阅 DLCT 阅读组邮件（`groups.google.com/g/deep-learning-classics-trends`）
- [ ] **本周五必须参加 DLCT 线上会议**（哪怕只听）

### 第 2 件（本周，2 小时）：启动数学前置
- [ ] 打开 MIT 6.042J OCW 页面（`ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-fall-2010/`）
- [ ] 看 Lecture 1 + 做 PS1 前 3 题
- [ ] 在日历固定「每周六上午 4h 数学，雷打不动」

### 第 3 件（本月，每周 5h）：选方向 + 启动 interp
- [ ] 读 [`05-方向深选-Mechanistic-Interpretability.md`](05-方向深选-Mechanistic-Interpretability.md) §「30 天入门清单」
- [ ] **若决定冲 interp**：MATS Winter 2027 Neel Nanda stream 申请 **9/4 截止**（见 [`09-奖学金与求职.md`](09-奖学金与求职.md)）
- [ ] **若不冲**：选其他方向（diffusion 理论 / scaling laws / RLVR 理论）

---

## ⚠️ 关于本资源库的元说明

1. **所有链接 2026-08 一手核实**：fellowship 截止日期、价格、API 版本都是当前数据，非凭记忆。
2. **不堆砌**：每个文件控制在 ~300 行，每个资源都标注「是什么 / 何时用 / 入门动作」。继续堆砌就违反 GAP_ANALYSIS 的减法原则了。
3. **分级**：[必] = 必用，[重] = 重要，[选] = 选读。先做 [必]，再 [重]，[选] 不强求。
4. **本地化**：英文术语保留，但所有解释中文。Fellowship 优先列对国际/远程友好的。
5. **维护**：fellowship 截止日期、价格每 3-6 月会变，需复检。

---

**版本**：v1.0（2026-08-13）
**作者**：AI Mentor (ai-mentor) + 学生
**核心理念**：**资源不在多，在「真的用」。一周内不用 = 删掉。**
