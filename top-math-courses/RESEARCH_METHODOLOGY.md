# RESEARCH_METHODOLOGY：数学研究方法论——从学习者到研究者的切换器

> **本章核心**：[`UNIFIED_ROADMAP`](UNIFIED_ROADMAP.md) 教你数学**知识**，但没教你**怎么做数学研究**。这份文档补上那一层：怎么解题、怎么读书、怎么读论文、怎么写证明、怎么提问题、怎么找方向。**绝大多数数学学习者卡在"会做习题但做不出研究"——卡的就是这一层**。
>
> 适用：目标是"应用数学研究型工程师"或更远的纯数学研究者。每周 10-20h，3-8 年尺度。

---

## 〇、为什么需要"研究方法论"

数学和工程有一处根本不同：

| 维度 | 工程学习 | 数学学习 |
|------|---------|---------|
| **目标** | 解决已知问题 | 提出 + 解决新问题 |
| **反馈** | 代码跑通/测试过 | 证明对错（常常没人给你对答案）|
| **路径** | 有明确 spec | 自己定义问题 |
| **协作** | 团队、PR review | 讨论班、论文 review（极慢）|
| **失败** | bug → fix | "证不出来"可能是你菜，也可能是问题本身难 |

**结论**：工程能力 ≠ 数学研究能力。你可以是个优秀的 ML 工程师但完全做不出数学研究，反之亦然。要成为"应用数学研究型工程师"，必须**两边都练**。

这份文档的每一节都对应一个**可观察的行为**——读完一节，你应该能**做**某件之前不会做的事。

---

## 一、解题方法论：Polya 四步法

### 1.1 核心文本

**George Pólya《How to Solve It》（1945，至今未被超越）**

这本书薄（< 250 页），但**改变了 20 世纪数学教育**。它的核心是一个 4 步启发法：

```
1. 理解问题 (Understand the problem)
2. 设想计划 (Devise a plan)
3. 执行计划 (Carry out the plan)
4. 回顾反思 (Look back)
```

听起来像废话，但 Pólya 在每一步都给了**具体的启发问句**。例如第 1 步会问：
- 未知量是什么？已知什么？条件是什么？
- 条件能分离吗？能画图吗？
- 有反例吗？条件能 weaker/stronger 吗？

### 1.2 一个完整的 Pólya 实例

**问题**：证明 $\sqrt{2}$ 是无理数。

**Polya 四步**：

**Step 1（理解）**
- 未知：要证"不存在整数 $p, q$ 使 $(p/q)^2 = 2$"。
- 已知：有理数 = 既约分数 $p/q$（$\gcd(p,q)=1$）。
- 条件：$p^2 = 2q^2$。

**Step 2（计划）**
- 类比：见过类似问题吗？——奇偶性论证。
- 设想：假设 $p^2 = 2q^2$，看 $p$ 的奇偶性 → $p$ 必偶 → $p=2k$ → $4k^2=2q^2$ → $q^2=2k^2$ → $q$ 也偶 → 与 $\gcd(p,q)=1$ 矛盾。
- 这是"**反证法 + 无穷递降**"组合。

**Step 3（执行）**（写正式证明，略）

**Step 4（回顾）**
- 这套论证能推广吗？→ 能证 $\sqrt{n}$ 在 $n$ 非完全平方时无理。
- 奇偶性的本质是什么？→ 整环上的"唯一分解"。可以推广到 $\mathbb{Z}[i]$。
- Fermat 就是用"无穷递降"证了 $x^4 + y^4 = z^4$ 无正整数解。

> 💡 **Step 4 是研究者的核心肌肉**。学习者止于 Step 3，研究者必做 Step 4——**每一个证完的定理都是新问题的种子**。

### 1.3 练习：用 Pólya 四步做题

把下面这道题用 4 步写下来（不要直接写证明）：

> 证明：任意 6 人中，必有 3 人两两相识或两两不相识。（Ramsey $R(3,3)=6$）

**自检**：你能不能在 Step 4 想到"$R(3,3)=6$ 能推广到 $R(s,t)$ 吗？$R(s,t)$ 有限吗？"——如果能，你已经具备研究者的种子直觉。

---

## 二、数学阅读法：书 vs 论文，与 ML 论文的根本差异

### 2.1 读数学书

数学书**不能跳着读**（和 ML 论文完全不同）。规则：

1. **拿纸笔重推导**：看到"显然"、"由定理 X 易得"——自己推一遍，不许信。
2. **习题是正文的一部分**：跳过习题 = 没读完这本书。
3. **读两遍**：第一遍抓主线（看 forest），第二遍抠细节（看 trees）。Tao 推荐**第一遍略读**（只读定义、定理陈述、章节关系），第二遍精读。
4. **遇到卡点 ≠ 你菜**：数学书的某些章节可能需要你回去补先修课。**不要硬读**——回去补。

**推荐读法**（Tao 的《Analysis I》前言）：
> "I would suggest reading each chapter twice: once lightly, to get the overall flow and intuition, and a second time more carefully, filling in the exercises and verifying all the claims."

### 2.2 读数学论文

数学论文比 ML 论文**密度高得多、节奏慢得多**。规则：

1. **一篇 20 页的数学论文 ≈ 一本小书**，可能需要 1-4 周读透。
2. **先读 abstract + introduction + main theorem**——只看陈述，不看证明。判断值不值得读。
3. **找"骨架"**：每节先读定义和定理陈述，跳过证明。看完整篇的骨架再回头抠证明。
4. **重新推导关键证明**：拿纸笔，把 main theorem 的证明抄一遍，每一步问"为什么这一步成立？"。卡住 → 回头补工具。
5. **找"反例"和"边界"**：定理的条件能弱化吗？去掉一个假设会怎样？这是研究的入口。
6. **用 Lean 形式化**（进阶）：把 main theorem 在 Lean 里写出来，是最深的"读懂"。

### 2.3 数学论文 vs ML 论文

| 维度 | ML 论文 | 数学论文 |
|------|--------|---------|
| 篇幅 | 8-15 页正文 + 附录 | 20-60 页 |
| 代码 | GitHub 一键复现 | 通常无（或仅有伪代码）|
| 阅读速度 | 1-2 小时/篇 | 1-4 周/篇 |
| 核心论证 | 实验 ablation | 证明 |
| 验证方式 | 跑实验 | 重推导 / 形式化 |
| 新意类型 | 系统改进 / 新 trick | 新概念 / 新结构 |

> 💡 **如果你只读过 ML 论文，第一次读数学论文会非常不适应**——感觉"读了 3 天还在第 3 页"。这是正常的。从短文（如 Tao 的 blog post）开始练。

### 2.4 推荐入门论文/notes（短，能 1 周读懂）

- **Tao 的 blog** 《What's new》的短帖（多数 < 10 页）
- **Gowers's Weblog** 的 "Cambridge teaching" 系列
- **Spivak《Calculus》的附录**（短小精悍的证明典范）
- **3Blue1Brown 视频配套 notes**

---

## 三、数学写作：怎么写证明 / 怎么用 LaTeX

### 3.1 核心文本

- **Paul Halmos《How to Write Mathematics》（1970）**——81 页，写作者圣经。
- **Steven Krantz《A Primer of Mathematical Writing》**——更现代、更实操。
- **Donald Knuth et al.《Mathematical Writing》（CS 209）**——Stanford 课的讲义。

### 3.2 Halmos 的几条铁律

1. **每个符号都要能用语言读出来**。写 $A \subset B$ 时心里要能默念"$A$ 是 $B$ 的子集"。
2. **避免符号污染**：能写"对所有 $x$"就别写"$\forall x$"。文字 < 符号污染。
3. **每段一个想法**。数学段落比文学段落更短。
4. **定义-定理-证明-例 的节奏**：先定义新概念，再陈述定理，再证明，再给一个**具体例子**让读者落地。
5. **证明结尾要有"句号"**：不要让读者悬着。证明完要能回到主叙述。

### 3.3 一个反例（Halmos 的）

❌ 差的写法：
> 设 $f: X \to Y$ 满足 $\forall \epsilon > 0, \exists \delta > 0, \forall x, y \in X, |x-y|<\delta \Rightarrow |f(x)-f(y)|<\epsilon$。

✅ 好的写法：
> 设 $f: X \to Y$ 一致连续。回忆：一致连续是指……

第二句更可读，因为它**命名**了概念（"一致连续"），让后面的论证能引用这个名字。

### 3.4 LaTeX 工具链（必学，本周就学）

```bash
# 工具链
- TeX Live (Linux) / MacTeX (Mac) / MiKTeX (Windows)
- 编辑器：VS Code + LaTeX Workshop 插件（你已用 VS Code）
- 协作：Overleaf（在线，免装环境）
- 参考文献：biblatex + Zotero（带 Better BibTeX 自动同步）
- 公式预览：GitHub 已支持 $...$ 和 $$...$$ 直接渲染 Markdown

# 必会的宏包
- amsmath, amssymb, amsthm      # 数学符号与定理环境
- mathtools                      # amsmath 增强版
- thmtools                       # 自定义定理环境样式
- hyperref, cleveref             # 交叉引用自动生成
- tikz, pgfplots                 # 画图
- bibtex/biber                   # 文献
```

**最小可工作模板**：

```latex
\documentclass[11pt]{article}
\usepackage{amsmath, amssymb, amsthm, mathtools}
\usepackage{hyperref}
\usepackage{cleveref}

\newtheorem{theorem}{Theorem}
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{proposition}[theorem]{Proposition}
\theoremstyle{definition}
\newtheorem{definition}[theorem]{Definition}
\newtheorem{example}[theorem]{Example}
\theoremstyle{remark}
\newtheorem*{remark}{Remark}

\title{My First Proof}
\author{你}
\date{\today}

\begin{document}
\maketitle

\begin{theorem}[$\sqrt{2}$ 是无理数]
$\sqrt{2} \notin \mathbb{Q}$.
\end{theorem}

\begin{proof}
反证。设 $\sqrt{2} = p/q$，$\gcd(p, q) = 1$。则 $p^2 = 2q^2$，
故 $p^2$ 偶，故 $p$ 偶（素数 2 整除 $p^2$ 蕴含 2 整除 $p$）。
设 $p = 2k$，则 $4k^2 = 2q^2$，即 $q^2 = 2k^2$，同理 $q$ 偶。
与 $\gcd(p, q) = 1$ 矛盾。 \qedhere
\end{proof}

\end{document}
```

> 📌 **本周任务**：装好 LaTeX，把上面模板编译出来。能编译 = 工具链就绪。

---

## 四、数学提问法：反例 / 推广 / 猜想

研究 = 提出新问题。提问题的三个核心动作：

### 4.1 找反例

**问句模板**：
- "这个定理的某个假设去掉，还成立吗？"
- "在无限维 / 一般环 / 非交换情形下，还成立吗？"
- "如果连续性换成 Lipschitz / Hölder / measurable，结论变吗？"

**经典案例**：
- Cauchy 说"连续函数可微几乎处处"——Weierstrass 给出**处处连续处处不可微**反例。
- 直觉说"处处可微函数单调 → 导数非负"——反例：Cantor 函数。

> 💡 **训练**：每学完一个定理，至少想 1 个反例方向。这是研究者的肌肉记忆。

### 4.2 做推广

**问句模板**：
- "把 $\mathbb{R}$ 换成 $\mathbb{R}^n$ / Banach 空间 / 度量空间，还成立吗？"
- "把有限维换成无限维？"
- "把确定性的换成随机的（加噪声）？"
- "把标量换成向量 / 矩阵 / 算子？"

**经典案例**：经典 Stokes 定理 → 广义 Stokes 定理（流形上）→ 代数几何中的 de Rham 定理。

### 4.3 提猜想

**问句模板**：
- "我做了 10 个例子，规律是 X，能证明吗？"
- "这个数值现象背后的结构是什么？"
- "A 现象和 B 现象之间是不是有深层联系？"

**经典案例**：
- Birch–Swinnerton-Dyer 猜想：从数值观察椭圆曲线的 L 函数 → 提出千年难题。
- Tao 的 Equational Theories Project：把 4694 个方程的蕴含关系**当成猜想数据库**，逐一攻克。

### 4.4 你的提问训练

读完一个定理后，写下：
1. **一个反例方向**（去掉哪个假设？）
2. **一个推广方向**（怎么 generalise？）
3. **一个数值实验方向**（编个 Python/SageMath 脚本观察 10 个例子）

**3 个月下来你会积累一个"问题笔记本"——这就是研究的种子库**。

---

## 五、文献检索与工具

### 5.1 数学文献库（按重要性）

| 数据库 | 用途 | 门槛 |
|--------|------|------|
| **arXiv.org**（math 分类）| 预印本，最新研究 | 免费，必 RSS |
| **MathSciNet (MR)** | Mathematical Reviews，**带 peer review 摘要**，金标准 | 需机构订阅 |
| **zbMATH Open** | 欧洲 counterpart，2021 起部分免费 | 部分免费 |
| **Google Scholar** | 广撒网，找引用关系 | 免费 |
| **MathOverflow / Stack Exchange** | 问/答专业问题，找 hidden gem | 免费 |
| **OEIS** | 整数序列，组合/数论方向必备 | 免费 |
| **MacTutor History** | 数学家传记 / 历史背景（写引言时用）| 免费 |

> 💡 **arXiv math 分类**：cs.LG (ML) 你已熟。数学有 math.CO (组合), math.PR (概率), math.FA (泛函), math.NA (数值分析), math.IT (信息论), math.OC (优化), math.ST (统计)。订阅你方向的 RSS。

### 5.2 计算工具

| 工具 | 用途 | 学起来 |
|------|------|--------|
| **SageMath** | 开源 Mathematica 替代，Python 接口，**符号+数值+数论+代数** | 1 周入门 |
| **SymPy** | 轻量 Python 符号计算 | 你已会 NumPy，半天入门 |
| **Julia** | 数值计算现代语言，性能近 C | 1-2 周入门 |
| **Mathematica / Maple** | 商业，强大（如有访问）| 选学 |
| **Lean 4 + Mathlib** | 形式化证明（见 [LEAN_MATH_TRACK](LEAN_MATH_TRACK.md)）| 持续练 |

### 5.3 文献管理

- **Zotero** + Better BibTeX 插件：自动同步 BibTeX，Overleaf 协作流畅。
- 不要手维护 `.bib` 文件——这是 90 年代的做法。

### 5.4 数学绘图

- **TikZ**（LaTeX 内嵌）：出版级矢量图。
- **matplotlib**：你已经熟，适合数据图。
- **GeoGebra**：交互几何（学实分析/几何时用）。
- **Asymptote / Ipe**：高质量矢量图（选学）。

---

## 六、协作与社区

### 6.1 讨论班 / Seminar

数学研究的命脉。形式：
- ** Reading seminar**：一群人一起读一篇论文 / 一本书，每人轮流讲。
- **Research seminar**：研究者讲自己的工作。

**找 seminar**：
- 你所在城市大学的数学系网站（公开 calendar）
- arXiv 上的作者，去他们主页找 talk 视频
- **Tao / Gowers / Buzzard / Scholze 的博客**会预告他们的 talk

> 💡 **如果不在大学**：online seminar 越来越多。Lean Community 的 **Zulip**、AIM 的 online seminars、IAS 的 YouTube 频道都是高质量免费资源。

### 6.2 暑期学校

- **PCMI**（Park City Mathematics Institute）：美国，每年主题不同
- **IAS**（普林斯顿高等研究院）：定期 program
- **CIRM**（法国 Luminy）：欧洲数学暑期学校中心
- **BANFF / BIRS**（加拿大）：经常有 workshop
- **Lean Together**：Lean 社区年会

很多暑期学校现在 hybrid / 录像，**即使不亲临也能看录像**。

### 6.3 在线社区

| 礈区 | 何时用 |
|------|-------|
| **MathOverflow (MO)** | 研究级问题，1-2 年后再发言 |
| **math.stackexchange** | 大学-硕士级，立刻可参与 |
| **Lean Zulip** | Lean / mathlib 问题（社区主战场）|
| **Reddit r/math** | 浅，但能跟热点 |
| **Twitter 数学圈** | Tao / Gowers / Buzzard 都发推 |

### 6.4 找导师

**真相**：自学者最大的瓶颈是**没有导师反馈**。Tao 反复强调数学是**社会性活动**，孤立很难做出来。

如果你不能找正式导师：
1. **通过 MO / Lean Zulip 接触研究者**——好的提问能引起注意。
2. **给 mathlib 提 PR**——reviewer 就是事实上的导师。
3. **写 blog + @作者**——Tao / Gowers 经常回帖。
4. **参加暑期学校**——短期但密度高。

---

## 七、研究者心智：从"学已有"到"造新知"

### 7.1 学习者 vs 研究者

| 学习者 | 研究者 |
|--------|--------|
| 做老师给的题 | 自己找问题 |
| 题有标准答案 | 没人知道答案 |
| 卡住 = 不会 | 卡住 = 可能问题本身难 |
| 学完一本书 = 完成 | 学完一本书 = 起点 |
| 衡量：考试分数 | 衡量：论文 / 影响 |
| 时间：学期 | 时间：5-10 年一个方向 |

### 7.2 "Taste"——数学品味

研究能力 = 工具 + 品味。品味是**判断哪些问题值得做**的能力。

培养方式：
1. **读史**：MacTutor 历史 + Bell《Men of Mathematics》（虽然不准但有启发）+ Stillwell《Mathematics and Its History》。
2. **读传记**：Tao 博客、Hardy《A Mathematician's Apology》、Halmos 自传。
3. **多读 main theorems**，不只读解题技巧——理解什么是"深刻"。
4. **跟一个方向深扎**：泛读 100 个方向不如深读 1 个方向。深度才出品味。

### 7.3 研究节奏

数学研究 ≠ 上课。Tao / Gowers 都写过研究节奏：

```
研究循环（一个 cycle 通常 1-3 个月）：
1. 选方向 / 找问题（1-4 周）
2. 读相关文献（2-8 周）
3. 尝试 / 卡住 / 重试（数月 - 数年）
4. 突破（不可控，常在散步/洗澡时来）
5. 写证明 + 形式化（数周 - 数月）
6. 写论文（1-3 个月）
7. 投稿 → review（6-24 个月）
8. 发表 / 公开
```

**心理准备**：研究 90% 时间在卡住。这和工程"几小时跑通代码"完全不同节奏。

### 7.4 "10 年定律"与现实预期

- 数学界共识：**从开始研究到第一篇好论文，通常 3-5 年**。
- 从第一篇到"细分方向专家"，再 5-10 年。
- "顶级专家"（被同方向研究者熟知）：15-20 年。
- Fields 奖（40 岁前）：需要极强天赋 + 时机 + 顶级导师 + 运气。

你的画像（数学自评 0，每周 10-20h，逻辑思维强）的现实目标：
- **6-8 年达"研究入门级"**（top-math-courses 的目标）——合理
- **10-15 年成为细分方向"专家"**——需要加倍投入或全职
- **AI + 形式化数学**这一新变量可能缩短时间表（见 [LEAN_MATH_TRACK](LEAN_MATH_TRACK.md)）

> ⚠️ **不要被"顶级专家"的字面义绑架**。"应用数学研究型工程师"是更可达且有价值的目标——能在 ML 理论 / 数值分析 / 优化 / 形式化 任何一个细分方向做出**被同行认可的原创贡献**，就是成功。

---

## 八、必读书单（按优先级）

### 8.1 立刻读（前 3 个月）

| 优先级 | 书 | 为什么 |
|--------|---|--------|
| ⭐⭐⭐⭐⭐ | Pólya《How to Solve It》 | 解题启发法圣经，2 周读完 |
| ⭐⭐⭐⭐⭐ | Halmos《How to Write Mathematics》 | 写作圣经 |
| ⭐⭐⭐⭐ | Hardy《A Mathematician's Apology》 | 数学家心智，半天读完 |
| ⭐⭐⭐⭐ | Tao 博客《What's new》至少 20 篇 | 看顶级头脑工作 |

### 8.2 第一年读（建立品味）

| 优先级 | 书 | 为什么 |
|--------|---|--------|
| ⭐⭐⭐⭐⭐ | Tao《Analysis I》+ Lean companion | 实分析 + Lean 双修 |
| ⭐⭐⭐⭐⭐ | Stillwell《Mathematics and Its History》 | 数学品味，宽视野 |
| ⭐⭐⭐⭐ | Halmos《Naive Set Theory》 | 集合论 100 页入门 |
| ⭐⭐⭐⭐ | Halmos《I Want to Be a Mathematician》 | 自传，生涯规划参考 |
| ⭐⭐⭐ | Courant & Robbins《What Is Mathematics?》| 经典科普，建立宏观 |

### 8.3 长期读（研究者必备）

| 书 | 主题 |
|---|------|
| Dieudonné《A Panorama of Pure Mathematics》| 数学全景 |
| Gowers 主编《The Princeton Companion to Mathematics》| 1000+ 页数学百科 |
| Gowers 主编《The Princeton Companion to Applied Mathematics》| 应用数学版 |
| Borak & Shieh 主编《The Princeton Companion to Mathematics》(第 2 卷, 2025)| 续集 |

### 8.4 必看资源

- **Tao 2025-02 Simons Foundation 演讲**（YouTube `5ZIIGLiQWNM`）—— Machine-Assisted Proofs
- **3Blue1Brown** YouTube 频道——直觉建立
- **Mathologer / Numberphile**（谨慎，部分简化）—— 文化
- **Berkshire / MIT / Stanford 数学课公开录像**
- **IAS YouTube**（顶尖 talk 录像）

---

## 九、学习节奏与产出循环

### 9.1 周节奏（10-15h）

```
周一-周五（每天 1.5-2h）：
  - 1h：数学课学习（视频/书）
  - 0.5-1h：做习题（必须有！）

周六（3-4h）：
  - 整理本周笔记 → 写一段"讲透"笔记或 blog
  - 在 Lean 里形式化本周学的 1 个定理
  - 读 1 篇 math blog / 1 篇短论文

周日（2h）：
  - 费曼复习（对墙讲本周学的核心概念）
  - 整理"问题笔记本"（反例 / 推广 / 猜想）
  - 在 math.stackexchange 回答 1 题
```

### 9.2 月循环（评估）

每月底自检：
- [ ] 本月做了多少习题？（目标：≥ 30 题）
- [ ] 本月写了几段笔记 / blog？（目标：≥ 4 段）
- [ ] 本月在 Lean 里证明了几条定理？（目标：≥ 4 条）
- [ ] 本月读了多少论文 / blog？（目标：≥ 2 篇）
- [ ] 本月新增"问题笔记本"几条？（目标：≥ 4 条）

### 9.3 季度循环（产出）

每季度（3 个月）至少产出一个**完整作品**：
- 一篇 blog post（讲透一个概念）
- 一个 SageMath / SymPy / Julia 演示
- 一个 Lean 证明（mathlib PR 或个人 repo）
- 一份读书报告（某书 / 某论文）

> 💡 **产出导向**是防止"学了但不会用"的唯一办法。你的 work4ai 讲透系列本质就是这个循环的实例化——保持这个习惯。

---

## 十、自检题（这份文档读完，能答出来吗）

1. Pólya 四步法是哪四步？举一个你做过的数学题（哪怕高中的），按四步重新走一遍。
2. 你能不能说出"读数学书"和"读 ML 论文"的至少 3 个根本差异？
3. 找一个你学过的定理（例如：连续函数在紧集上取到最大值），写出：
   - 一个反例方向（去掉哪个假设？）
   - 一个推广方向（怎么 generalise？）
4. 装 LaTeX，把 §3.4 的模板编译出来。能编译 = 工具就绪。
5. 在 MathOverflow 或 math.stackexchange 上找一道你能看懂的问题（哪怕只看懂问题陈述），记录下来。

如果 5 题都能做，你已经从"数学学习者"切换到"具备研究者种子"的状态。

---

## 十一、与 work4ai 其他文档的衔接

| 你想做什么 | 去哪 |
|-----------|------|
| 学具体数学课 | [`UNIFIED_ROADMAP.md`](UNIFIED_ROADMAP.md) |
| 学数学 + 练 Lean 并行 | [`LEAN_MATH_TRACK.md`](LEAN_MATH_TRACK.md) |
| 知道数学 ↔ ML 怎么联动 | [`CROSS_INDEX_WITH_WORK4AI.md`](CROSS_INDEX_WITH_WORK4AI.md) |
| 压缩到 2-3 年速成 | [`FAST_TRACK.md`](FAST_TRACK.md) |
| 看前沿论文 | [`LATEST_RESEARCH.md`](LATEST_RESEARCH.md) |
| 用费曼法学 | [`FEYNMAN_TEACHING_GUIDE.md`](FEYNMAN_TEACHING_GUIDE.md) |

---

📌 **下一步**：
- 没装 LaTeX → 立刻装（§3.4）
- 买 / 借 Pólya《How to Solve It》→ 本周开始读（§1）
- 在 math.stackexchange 注册账号 → 本周回答 1 题（§6.3）
- 同时开 [`LEAN_MATH_TRACK.md`](LEAN_MATH_TRACK.md) 看怎么学数学同时练 Lean
- 开始"问题笔记本"——用一个 markdown 文件记下你每个反例 / 推广 / 猜想
