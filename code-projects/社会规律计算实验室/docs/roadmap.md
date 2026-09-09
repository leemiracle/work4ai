# Roadmap · 8-10 周可执行路线（按子领域组织）

> 这是一条**激进而可执行**的路线：每周 10-15 小时，按**社会科学子领域**推进，每个子领域用多种数学/计算工具切入。第 10 周结束时，你会有 1 个能写进简历的仿真作品 + 1 篇深度交叉案例 + 扎实的"数学化社会科学"思维框架。

---

## 总览：七子领域推进图

```
Week 0-1  ┌─ 模块0: foundations ──────────────────┐
          │ 数学自检 + 方法论 + 工具链              │
          └──────────────────────────────────────┘
                                ↓
Week 2-3  ┌─ ⭐子领域1: relations ──────────────────┐
          │ 关系结构如何决定机会                    │
          │ 工具: 图论、中心性、小世界、无标度       │
          └──────────────────────────────────────┘
                                ↓
Week 4-5  ┌─ ⭐子领域2: cooperation ────────────────┐
          │ 合作如何可能                            │
          │ 工具: 经典博弈、纳什、演化博弈、Nowak   │
          └──────────────────────────────────────┘
                                ↓
Week 6    ┌─ 子领域3: inequality ─────────────────┐
          │ 不平等如何涌现与固化                    │
          │ 工具: 帕累托、Sugarscape、Piketty       │
          └──────────────────────────────────────┘
                                ↓
Week 7    ┌─ 子领域4: power-politics ─────────────┐
          │ 革命相变与极化                         │
          │ 工具: 阿罗不可能、Kuran、极化涌现       │
          └──────────────────────────────────────┘
                                ↓
Week 8    ┌─ 子领域5: culture-cognition ──────────┐
          │ 文化演化与信息扩散                      │
          │ 工具: Boyd-Richerson、SIR、HK 观点动力学│
          └──────────────────────────────────────┘
                                ↓
Week 9-10 ┌─ 子领域6: markets-cities（重头戏）────┐
          │ Schelling 隔离 + 城市规模法则           │
          │ 工具: ABM、West 幂律、空间分异          │
          └──────────────────────────────────────┘
                                ↓
持续      ┌─ ⭐子领域7: crosscuts（"并结合"）─────┐
          │ 跨子领域综合研究                        │
          │ 主题: 犯罪×网络 / 算法×极化 / LLM×社会  │
          └──────────────────────────────────────┘
```

---

## 模块 0 · foundations（Week 0-1，5-10h）

### 目标
- 数学自检，找出补课优先级
- 跑通工具链
- 建立"数学如何介入社会科学"的思维框架

### 任务清单
- [ ] 通读 [`methodology.md`](methodology.md)
- [ ] 做 [`math-primer.md`](math-primer.md) 全部自检题
- [ ] 装环境：`pip install numpy scipy networkx matplotlib`
- [ ] 浏览 [`reading-list.md`](reading-list.md)，挑第一阶段要读的 3 本

### 完成标志
✅ 数学自检 5 项里至少 2 项绿；✅ 工具链跑通；✅ methodology 能复述给外行听

---

## ⭐ 子领域 1 · relations（Week 2-3，20-30h）

### 研究命题
> **你的机会，由你的关系结构决定，而非你的能力。**

格兰诺维特 1973 年发现：找工作时，是泛泛之交比至亲好友更有用——这违反直觉，但反复被验证。这是社会网络科学开宗明义的命题。

### 章节节奏
| 周 | 章节 | 投入 | 内容 |
|---|---|---|---|
| W2 上半 | `01-graph-basics.py` | 6h | 图论基础 + Karate Club + 中心性指标 |
| W2 下半 | `02-weak-ties.py` | 6h | Granovetter 模型 + "找工作"仿真 |
| W3 上半 | `03-small-world.py` | 6h | Watts-Strogatz 从零实现 + 重连线相变 |
| W3 下半 | `04-scale-free.py` | 6h | BA 模型 + 优先链接 + 幂律拟合 |
| W3 末 | `05-centrality-power.py` | 6h | 介数/特征向量中心性 = 权力 |

### 配套阅读
- Barabási - *Network Science*（在线免费）：ch1-4
- Granovetter 1973 原文（必读）
- Watts & Strogatz 1998 Nature 论文（精读）

### 完成标志
✅ 5 个 `.py` 都跑出图；✅ 能解释"为什么弱连带比强连带更有用"；✅ 能写出 WS 模型的相变

---

## ⭐ 子领域 2 · cooperation（Week 4-5，20-30h）

### 研究命题
> **自然选择鼓励自私，为什么生物界（包括人类）有那么多合作？**

这是横跨演化生物学、博弈论、政治哲学的核心问题。Axelrod 锦标赛证明 TIT-for-TAT 在重复囚徒困境中胜出，Nowak 进一步把合作机制归纳为五条规则。

### 章节节奏
| 周 | 章节 | 投入 | 重点 |
|---|---|---|---|
| W4 上半 | `01-classic-games.py` | 6h | 囚徒/协调/猎鹿 + 占优策略 |
| W4 下半 | `02-nash-math.md` | 6h | ⭐纳什存在性证明（Kakutani 不动点） |
| W5 上半 | `03-evolutionary-game.py` | 8h | 复制子动力学 + ESS + 仿真 |
| W5 下半 | `04-collective-action.md` | 5h | Olson 搭便车 + Ostrom 八原则 |
| W5 末 | `05-five-rules-nowak.md` | 5h | Nowak 合作的五条规则 |

### 配套阅读
- Osborne - *An Introduction to Game Theory* ch1-5, ch7
- Axelrod 1981 - *Evolution of Cooperation*（必读原文）
- Nowak 2006 - *Five Rules for the Evolution of Cooperation*

### 完成标志
✅ 能默写囚徒困境支付矩阵；✅ 能解释复制子动力学方程；✅ 知道纳什证明用了哪个不动点定理

---

## 子领域 3 · inequality（Week 6，10-15h）

### 研究命题
> **财富分布的幂律（80/20）不是天灾，是从微观规则涌现出来的必然。**

帕累托 1896 年发现财富分布是幂律，120 年来反复出现。Piketty 2014 年进一步提出 $r > g$（资本回报率 > 经济增长率）是不平等的数学根源。Sugarscape 模型则证明：即使所有人能力相同、规则公平，ABM 跑出来的财富分布也是高度不平等的。

### 章节节奏
| 章节 | 投入 | 重点 |
|---|---|---|
| `01-pareto-distribution.py` | 4h | 帕累托分布从零拟合 + 80/20 法则 |
| `02-sugarscape.py` | 6h | Epstein-Axtell 人工社会，财富涌现 |
| `03-piketty-r-g.md` | 4h | $r > g$ 的数学与争议 |
| `04-mobility-networks.md` | 3h | 社会流动 + 网络代际传递 |

### 配套阅读
- Piketty - *Capital in the 21st Century*（核心章节）
- Epstein & Axtell 1996 - *Growing Artificial Societies*
- Pareto 1896 - *Cours d'Économie Politique*（选读）

---

## 子领域 4 · power-politics（Week 7，10-15h）

### 研究命题
> **为什么某些时刻革命突然爆发，而多数时候人们沉默？**

Kuran 1989 给出惊人答案：人们有"虚假偏好"——心里反对政权但嘴上说支持，因为不想被孤立。当某个临界点被突破，所有人同时表露真实偏好，**政权瞬间崩溃**。这是社会相变最经典案例。

### 章节节奏
| 章节 | 投入 | 重点 |
|---|---|---|
| `01-arrow-impossibility.md` | 4h | 阿罗不可能定理（公理化方法胜利） |
| `02-revolution-phase.py` | 5h | Kuran 革命相变模型 + 仿真 |
| `03-polarization-emergence.py` | 5h | 极化涌现（有界信任模型） |
| `04-voting-paradox.md` | 3h | Condorcet 悖论 + 算法选票 |

### 配套阅读
- Arrow 1951 - *Social Choice and Individual Values*
- Kuran 1989 - *Sparks and Prairie Fires*
- Hegselmann-Krause 2002 - *Opinion dynamics and bounded confidence*

---

## 子领域 5 · culture-cognition（Week 8，10-15h）

### 研究命题
> **文化不是基因的附属品，它有自己的演化动力学。**

Boyd-Richerson 的"双传承理论"证明：基因和文化并行演化，有时文化演化甚至反转基因压力（如成人乳糖酶持续是因为文化发明了畜牧业）。同时，信息扩散服从与流行病相同的 SIR 动力学——一条推文的传播和一场感冒的传播数学上是一样的。

### 章节节奏
| 章节 | 投入 | 重点 |
|---|---|---|
| `01-dual-inheritance.md` | 4h | Boyd-Richerson 双传承理论 |
| `02-diffusion-SIR.py` | 5h | 创新扩散 + 网络上的 SIR |
| `03-opinion-dynamics.py` | 5h | DeGroot + Hegselmann-Krause |
| `04-memetics.md` | 3h | 模因论：Dawkins 到今日 |

### 配套阅读
- Boyd & Richerson 1985 - *Culture and the Evolutionary Process*
- Rogers - *Diffusion of Innovations*（5th ed.）
- Sunstein 2017 - *#Republic*（信息茧房）

---

## 子领域 6 · markets-cities（Week 9-10，20-30h，重头戏）

### 研究命题
> **美国城市的种族隔离不需要种族歧视——只要有温和偏好，就会涌现极端隔离。城市越大越快节奏，且遵循 $N^{1.15}$ 幂律。**

Schelling 1971 用硬币在棋盘上玩出了美国社会学最经典的实验：每个人都只要求"至少 30% 邻居和我同类"，跑下来却出现 80%+ 的隔离。West 2007 发现城市规模法则——城市人口每翻倍，工资、专利、犯罪也按 $N^{0.85}$ 或 $N^{1.15}$ 缩放。

### 章节节奏
| 周 | 章节 | 投入 | 重点 |
|---|---|---|---|
| W9 上半 | `01-schelling.py` | 8h | ⭐谢林隔离从零实现 + 动画 |
| W9 下半 | `02-scaling-laws.py` | 6h | 城市/公司规模法则（West 幂律） |
| W10 上半 | `03-firm-hierarchy.md` | 5h | 公司层级涌现 |
| W10 下半 | `04-institution-path.md` | 5h | 制度路径依赖 + QWERTY 锁定 |
| W10 末 | `05-auction-mechanism.md` | 4h | 拍卖/机制设计入门 |

### 配套阅读
- Schelling 1978 - *Micromotives and Macrobehavior*（必读）
- West 2017 - *Scale*
- Bettencourt 2013 - *The Origins of Scaling in Cities*（Science）
- Ostrom 1990 - *Governing the Commons*

### 完成标志
✅ Schelling 跑出"温和偏好→极端隔离"；✅ 能解释幂律 vs 高斯在网络中的差异；✅ 启动 `projects/p1-schelling-interactive`

---

## 子领域 7 · crosscuts（持续，不限时）

### 研究命题
> **最有意思的洞见，往往在子领域交界处。**

每个交叉案例都至少结合两个子领域：

| 案例 | 结合的子领域 | 关键问题 |
|---|---|---|
| 犯罪 × 网络 | relations × power-politics | 黑帮网络结构如何影响打击效果？ |
| 算法 × 极化 | culture-cognition × power-politics | 推荐算法如何放大极化？ |
| COVID × 社会 | culture-cognition × inequality × relations | 大流行揭示的社会网络结构？ |
| LLM × 社会 | 全部 | 用 AI agent 仿真整个小型社会？ |
| 革命 × 复杂系统 | power-politics × relations | 信息级联如何引爆革命？ |

### 推荐起点
1. **犯罪 × 网络**（最具体，数据多）
2. **算法 × 极化**（最贴近你的工程背景）
3. **LLM × 社会**（前沿，依赖 `agent-guide` 基础）

---

## 节奏控制原则

1. **研究对象 > 工具**：方法是为了解释现象，不是反过来。
2. **跨子领域结合**：每完成一个子领域，问自己"它能解释我关心的另一个现象吗"。
3. **可视化优先**：每周至少 1 张能讲故事的图。
4. **遇阻即问**：用 `@debugger` 找 bug，用 `@oracle` 做架构决策。
5. **每周末复盘**：用 `progress-tracker` skill 更新进度，写 `notes/week-XX.md`。
6. **不要完美主义**：留 30% "留到二期"是健康的。

---

## 紧急情况下的"最小完成路径"

如果时间紧张，**保住这条最小路径**：

```
模块0 必做: math-primer + methodology 通读
模块1 必做: 01-graph-basics + 02-weak-ties + 05-centrality-power
模块2 必做: 01-classic-games + 03-evolutionary-game
模块3 必做: 02-sugarscape
模块6 必做: 01-schelling（项目灵魂）
模块7 必做: 至少 1 个交叉案例
```

就算只做完这些，你已经超过 95% 的"社会科学爱好者"。

---

*最后更新：2026-07 · v0.2 · 重组为子领域结构*
