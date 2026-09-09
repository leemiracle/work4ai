# 子领域 7 · Crosscuts · 交叉专题（"并结合子领域"）

> **本模块的命脉**：最有意思的洞见，往往在子领域交界处。每个交叉案例都至少结合 2 个子领域，多工具并用。

---

## 为什么有这个模块

传统学术训练让人"专精一个子领域"。但社会现象不分学科——
- 推荐算法 × 极化 = 算法治理（横跨 4+5+1）
- 犯罪 × 网络 = 犯罪学新范式（横跨 1+4）
- COVID × 社会 = 大流行揭示的网络结构（横跨 1+3+5）
- LLM × 社会 = AI agent 仿真（横跨全部）

本模块的每个专题都是**"并结合"**的练习场。

---

## 五个交叉专题（推荐顺序）

| # | 专题 | 结合的子领域 | 关键问题 |
|---|---|---|---|
| 1 | **算法 × 极化** | power-politics × culture × relations | 推荐算法如何放大社会分裂？ |
| 2 | **犯罪 × 网络** | relations × power-politics | 黑帮网络结构如何影响打击效果？ |
| 3 | **COVID × 社会** | culture × inequality × relations | 大流行揭示的社会网络结构？ |
| 4 | **LLM × 社会** | 全部 | 用 AI agent 仿真整个小型社会？ |
| 5 | **革命 × 复杂系统** | power-politics × relations | 信息级联如何引爆革命？ |

---

## 已交付的交叉专题

### [`01-algo-polarization.md`](01-algo-polarization.md) ⭐ 推荐起点
**算法 × 极化**——推荐系统如何放大社会分裂。结合子领域 4（极化涌现）+ 5（信息扩散）+ 1（网络结构）+ 中国 CSSCI 配套研究。

为什么是起点：最贴近你（用户）的工程背景，能立刻用代码做实验。

### [`02-llm-society.md`](02-llm-society.md) ⭐ 前沿
**LLM × 社会**——用 AI agent 仿真整个小型社会。结合全部子领域。配套项目：`projects/p5-llm-society/`。

为什么重要：2023-2026 最热的方向，是社会科学的"实验室"。

### [`cities-case.md`](cities-case.md) ⭐ 深度案例
**城市规模法则的中国应用**——West 1.15 法则在中国成立吗？结合子领域 6 + 3。

1500-3000 字深度案例研究，含原始数据、拟合、争议、政策含义。

---

## 跑代码

```bash
cd /data/usershare/ai/social-laws/07-crosscuts/
# 主要配套代码在 projects/p5-llm-society/
# 文档本身不需要代码，但建议跑过模块 1-6 后再读
```

---

## 设计交叉专题的方法论

完成 1-6 子领域后，你可以自己设计交叉专题。流程：

1. **观察现象**：什么社会现象让你困惑？
2. **拆解维度**：它涉及哪些子领域？（如 COVID = 网络+文化+不平等）
3. **多模型组合**：每个子领域贡献一个视角的模型
4. **整合仿真**：写一个 ABM/网络仿真，跑出"涌现"
5. **CSSCI 配套**：找到对应的中国顶刊研究做对比
6. **写报告**：在 `notes/` 下写一份 1500-3000 字研究

---

## 推荐文献（按专题）

### 算法 × 极化
- Bakshy et al. (2015). *Exposure to ideologically diverse news on Facebook.* Science.
- Sunstein (2017). *#Republic.*
- **中国 CSSCI**：检索"算法推荐 + 极化"、"信息茧房 + 中国"

### 犯罪 × 网络
- Papachristos (2009). *Murder by Structure.* Sociological Theory.
- **中国 CSSCI**：检索"犯罪 + 社会网络"

### COVID × 社会
- Block et al. (2020). *Social network and distancing.* Nature HB.
- **中国 CSSCI**：检索"COVID + 社会网络"、"疫情 + 社会治理"

### LLM × 社会
- Park et al. (2023). *Generative Agents.* arXiv:2304.03442
- Park et al. (2023). *Social Simulacra.* UIST.
- Project Sid (2024). arXiv.
- **中国 CSSCI**：检索"人工智能 + 社会仿真"、"大模型 + 社会科学"

### 革命 × 复杂系统
- Kuran (1989). *Sparks and Prairie Fires.* Public Choice.
- **中国 CSSCI**：检索应星 + 抗争政治

---

## 完成标志

✅ 至少精读 1 个交叉专题（建议 01-algo-polarization）
✅ 用 CSSCI 配套做跨文化对话
✅ 尝试设计自己的交叉专题
✅ 启动 `projects/pX` 综合 demo

---

*子领域 7 完成后，本项目基础阶段全部跑完。进入自由研究阶段。*
