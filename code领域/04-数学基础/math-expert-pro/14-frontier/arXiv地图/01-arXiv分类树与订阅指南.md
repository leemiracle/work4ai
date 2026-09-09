# arXiv 分类树与订阅指南

> **「每天 200+ 篇，怎么过滤？」**——arXiv math 全分类速查 + 订阅 / 筛选 / 与 Quanta-MathOverflow 的互补策略。
>
> 信息日期：2026-07 | 可信度：Tier S（arXiv 官方分类表）+ Tier A（活跃度统计基于 arXiv API 抽样）

---

## 一、arXiv math 全分类速查（~30 个二级分类）

> 按字母序。**活跃度**列基于 2024-2025 日均新贴估算（粗略，受交叉分类影响）。🔥 = 高（≥8 篇/日），🔺 = 中（2-8 篇/日），▫️ = 低（<2 篇/日）。

| 代号 | 全名 | 中文 | 一句话解释 | 活跃度 |
|------|------|------|-----------|--------|
| math.AG | Algebraic Geometry | 代数几何 | 多项式方程组解空间的几何结构 | 🔥 |
| math.AT | Algebraic Topology | 代数拓扑 | 用代数工具（同调 / 同伦）分类空间 | 🔺 |
| math.CA | Classical Analysis | 经典分析 | 不等式、特殊函数、Fourier 分析 | 🔺 |
| math.CO | Combinatorics | 组合学 | 离散结构（图、集、排列）计数与性质 | 🔥 |
| math.CT | Category Theory | 范畴论 | 函数、自然变换的抽象代数 | ▫️ |
| math.CV | Complex Variables | 复分析 | 全纯函数、多复变 | 🔺 |
| math.DG | Differential Geometry | 微分几何 | 流形、曲率、Riemann 几何 | 🔥 |
| math.DS | Dynamical Systems | 动力系统 | 微分方程的长期行为、混沌 | 🔥 |
| math.FA | Functional Analysis | 泛函分析 | 无穷维空间上的函数与算子 | 🔺 |
| math.GM | General Mathematics | 通用数学 | 杂项、跨学科（注：质量参差，慎读）| 🔺 |
| math.GN | General Topology | 一般拓扑 | 点集拓扑、度量化 | ▫️ |
| math.GR | Group Theory | 群论 | 对称性的代数 | 🔺 |
| math.GT | Geometric Topology | 几何拓扑 | 纽结、3-流形、低维拓扑 | 🔺 |
| math.HO | History & Overview | 历史与综述 | 数学史、教学法、综述 | ▫️ |
| math.KT | K-Theory & Homology | K 理论与同调 | 向量丛、代数 K 群 | ▫️ |
| math.LO | Logic | 数理逻辑 | 集合论、模型论、可证性 | 🔺 |
| math.MG | Metric Geometry | 度量几何 | 度量空间、凸几何、嵌入 | 🔺 |
| math.MP | Mathematical Physics | 数学物理 | QFT / 弦论 / 统计力学的严格数学 | 🔥 |
| math.NA | Numerical Analysis | 数值分析 | 算法、误差、计算稳定性 | 🔥 |
| math.NT | Number Theory | 数论 | 素数、丢番图、椭圆曲线 | 🔥 |
| math.OA | Operator Algebras | 算子代数 | C\*-代数、von Neumann 代数 | ▫️ |
| math.OC | Optimization & Control | 优化与控制 | 凸优化、最优控制、变分 | 🔥 |
| math.PR | Probability | 概率论 | 随机过程、大偏差、随机矩阵 | 🔥 |
| math.QA | Quantum Algebra | 量子代数 | 量子群、辫群、张量范畴 | ▫️ |
| math.RA | Rings & Algebras | 环与代数 | 非交换环、Lie 代数 | 🔺 |
| math.RT | Representation Theory | 表示论 | 群 / 代数如何线性作用 | 🔥 |
| math.SG | Symplectic Geometry | 辛几何 | Hamilton 力学的几何 | 🔺 |
| math.SP | Spectral Theory | 谱理论 | 算子谱、Schrödinger 算子 | 🔺 |
| math.ST | Statistics Theory | 统计理论 | minimax、Bayes、渐近 | 🔥 |

**补充**：math 之外与数学紧密相关的分类：
- **stat.ML / cs.LG**——机器学习理论（深度学习理论主战场）
- **cs.CC**——计算复杂性（P vs NP）
- **cs.LO**——逻辑在计算机科学
- **hep-th / cond-mat**——理论物理 / 凝聚态（与 math.MP 重叠）

---

## 二、订阅渠道（按"信息密度 vs 时间成本"排序）

### 渠道 1：arXiv 官方 RSS（最直接）

- **地址**：`https://export.arxiv.org/rss/<分类>`
- **示例**：`https://export.arxiv.org/rss/math.NT`（数论）、`https://export.arxiv.org/rss/math.CO`（组合）
- **节奏**：每天一次推送（北京时间凌晨）
- **优点**：官方源，无过滤，全
- **缺点**：信息量爆炸，需配合关键词过滤

**推荐 RSS 阅读器**：Feedly / Inoreader（支持关键词过滤规则）

### 渠道 2：arXiv API + 自定义脚本（最灵活）

- **官方文档**：[arxiv.org/help/api](https://arxiv.org/help/api)
- **玩法**：用 Python `arxiv` 包按 `ti:"Riemann zeta" AND cat:math.NT` 之类查询
- **适合**：有编程基础、想自动化过滤的人
- **示例**：每天抓"标题含 'breakthrough' / 'proof' 的 math.NT 论文"

### 渠道 3：AK Twitter / Bluesky（最高信号噪比）⭐ 推荐

- **AK**（@_akhaliq / @_ak）：每日精选 ML / 数学前沿，覆盖 Quanta 级重要论文
- **账号**：在 X 或 Bluesky 上关注 `@_akhaliq`
- **优点**：人工筛选，信号极高，覆盖跨分类
- **缺点**：偏 ML / 应用方向，纯数论 / 代数几何覆盖较少

### 渠道 4：Papers With Code（最结构化）

- **地址**：[paperswithcode.com](https://paperswithcode.com/)
- **特点**：论文 + 代码 + benchmark 一体
- **适合**：ML / 优化 / TDA 这类有实验的方向
- **缺点**：纯理论方向覆盖差

### 渠道 5：arXiv daily digest 邮件

- 部分高校（如 MIT、Cambridge）有 math 邮件列表，转发每日 arXiv
- 国内：可关注「机器之心」「PaperWeekly」（偏 AI，但数学交叉论文多）

---

## 三、怎么筛选（从 200 篇/天 到 3 篇/天）

### 筛选漏斗

```
200 篇/日（你订阅的 3-4 个分类）
   ↓ 按标题关键词过滤
~30 篇（含你关注的关键词）
   ↓ 读摘要
~8 篇（摘要与你相关）
   ↓ 精读 intro + 主定理
~2-3 篇（值得深读）
```

### 标题/摘要关键词清单（按方向）

| 方向 | 高优先级关键词 |
|------|---------------|
| 数论 | `prime gap`, `Riemann`, `BSD`, `abc`, `elliptic`, `modular`, `Langlands` |
| 加性组合 | `sumset`, `Freiman`, `Ruzsa`, `Szemerédi`, `polynomial method` |
| 深度学习理论 | `generalization bound`, `double descent`, `NTK`, `PAC-Bayes`, `implicit bias` |
| RMT | `Wigner`, `semicircle`, `free probability`, `universality`, `Tracy-Widom` |
| 优化 | `non-convex`, `convergence rate`, `lower bound`, `online`, `regret` |
| 形式化 | `Lean`, `Coq`, `formalization`, `theorem proving`, `mathlib` |

### 作者过滤

- 建立你的「必读作者清单」（5-10 位），他们出新论文无条件读 intro
- 工具：[arxiv-sanity-preserver](http://www.arxiv-sanity-preserver.com/)（Karpathy 开发，按作者 / 关键词排序）
- 进阶：[Semantic Scholar](https://www.semanticscholar.org/) 可订阅作者，新论文邮件提醒

### 引用过滤

- 新论文出现后 1-2 个月，查 [Inspire-HEP](https://inspirehep.net/)（物理）/ [MathSciNet](https://mathscinet.ams.org/)（需订阅）/ [Semantic Scholar](https://www.semanticscholar.org/) 看被引次数
- 被引 >10 篇 = 值得回看；被引 >50 篇 = 必读

---

## 四、与 MathOverflow / Quanta 的互补

### 信息三角

```
        arXiv（一手，全，噪音多）
              ↓ 筛选
       Quanta Magazine（科普 + 采访，每月 2-4 篇）
              ↓ 提问
        MathOverflow（专家讨论，深度但碎片化）
```

| 平台 | 角色 | 何时用 |
|------|------|--------|
| **arXiv** | 一手论文源 | 想读原始工作 |
| **Quanta Magazine** | [quantamagazine.org/mathematics](https://www.quantamagazine.org/mathematics/) | 想知道"哪些工作被主流认为重要"——Quanta 的选题 = 编辑筛选过的 Tier A 信号 |
| **MathOverflow** | [mathoverflow.net](https://mathoverflow.net/) | 想问具体技术问题 / 看专家对某概念的争论 |
| **Tao 博客** | [terrytao.wordpress.com](https://terrytao.wordpress.com/) | 想看 Fields 得主级别的"二手解读" |
| **Gowers 博客** | [gowers.wordpress.com](https://gowers.wordpress.com/) | 同上，偏组合 / Polymath |

**黄金互补**：读到 arXiv 一篇看不懂 → 搜 Tao 博客有没有写解读 → 再不懂去 MathOverflow 提问。

---

## 五、按方向的推荐订阅清单

### 路线 A：纯数论 / 代数几何
- **arXiv**：math.NT, math.AG, math.RT
- **必关注**：Tao 博客、Bhargava 主页、Scholze 主页
- **媒体**：Quanta 数学板块
- **每周时间**：3-5 h

### 路线 B：AI / 机器学习理论
- **arXiv**：stat.ML, cs.LG, math.OC, math.PR
- **必关注**：AK Twitter、Belkin 主页、Bartlett 主页
- **媒体**：Papers With Code（theory 板块）、机器之心
- **每周时间**：5-8 h（这是信息量最大的方向）

### 路线 C：形式化数学 / Lean
- **arXiv**：cs.LO, math.LO + 搜 "Lean" / "formalization"
- **必关注**：[Lean Zulip](https://leanprover.zulipchat.com/)（实时讨论）、Buzzard 主页、mathlib GitHub releases
- **媒体**：[Xena Project Blog](https://xenaproject.wordpress.com/)
- **每周时间**：2-3 h

### 路线 D：跨学科（数学物理 / TDA）
- **arXiv**：math.MP, math.AT, math.DG + hep-th
- **必关注**：Frenkel 主页、Carlsson 主页、[Quanta physics 板块](https://www.quantamagazine.org/physics/)
- **每周时间**：3-4 h

---

## 六、新手启动清单（10 分钟搭好雷达）

1. **注册 arXiv 账号** → 设置每日邮件订阅（选 2-3 个分类）
2. **关注 AK**（Twitter / Bluesky）
3. **订阅 Tao 博客** RSS
4. **收藏 Quanta 数学板块**
5. **加入 Lean Zulip**（即使你不做 Lean，看大佬讨论也是学习）

**一个月后**：根据信号密度调整订阅分类，砍掉噪音高的，加深的。

---

## 📚 相关文档

- 如何识别论文可信度 → [14-frontier/README.md 的 Tier 金字塔](../README.md)
- 各方向的核心问题与入门文献 → [热点方向追踪/2024-2026十大热点方向.md](../热点方向追踪/2024-2026十大热点方向.md)
- 哪些期刊最重要 → [顶刊与奖项/01-数学奖项与权威地图.md](../顶刊与奖项/01-数学奖项与权威地图.md)

---

> ⏱️ **时效声明**：arXiv 分类体系稳定（近 10 年无大变），但活跃度排名会随方向冷热波动。本表数据基于 2024-2025 抽样，每年校准一次。
