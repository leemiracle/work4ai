# CS448B: Data Visualization

> Stanford University, Fall 2024（最新可用版本）
> Instructor: **Maneesh Agrawala**（可视化与 HCI 领域顶尖学者，Berkeley → Stanford）
> Time: MW 10:30am-12:20pm, Skilling Auditorium
> 先修: 无硬性先修；CS147 / CS148 / CS142 有帮助；需 Web 编程（JS / D3.js / Vega-Lite）
> 难度: ⭐⭐⭐⭐（理论 + 编程并重）
> 官网: http://cs448b.stanford.edu/ (或 https://magrawala.github.io/cs448b-fa24/)

---

## 📚 课程定位

**Stanford 数据可视化的标杆课程**，由可视化领域领军人物 **Maneesh Agrawala** 教授主讲。课程建立在图形设计、视觉艺术、感知心理学和认知科学的基础上，研究如何通过有效的可视化来 **增强人类的理解、记忆、推理和决策能力**。

课程面向两类学生：
1. **使用者**：在自己的工作中使用可视化（数据分析、科学传播）
2. **构建者**：开发更好的可视化工具和系统

> 与 CS347 的关系：CS347 的可视化章节（Week 6）是 CS448B 的浓缩版。CS448B 更深入技术实现（D3.js / Vega-Lite 编程）。

---

## 🎯 学习目标

课程结束时，学生将具备（官网原文）：

1. **理解** 关键可视化技术和理论：数据模型、图形感知、视觉编码和交互方法
2. **接触** 常见数据领域和对应分析任务：探索性数据分析（EDA）、网络分析
3. **实践经验** 使用 **Vega-Lite** 和 **D3.js** 构建和评估可视化系统
4. **能力** 阅读和讨论可视化研究文献
5. **设计能力** 创建有效的可视化设计，并进行设计重设计（Redesign）

---

## 📅 完整模块（10 周 20 讲）

### Week 1: 可视化基础

- **M Sep 23 — The Purpose of Visualization（可视化的目的）**
  - 为什么要可视化？
  - 🔴 Card, Mackinlay & Shneiderman — *Information Visualization* (Ch 1, Readings in InfoVis)
  - 🟡 Tufte — *Visual Explanations: The Challenger Decision*（挑战者号灾难分析）
  - 🟡 Anscombe — *Graphs in Statistical Analysis*（安斯库姆四重奏）
  - **Notebook**: Introduction to Vega-Lite (Observable)
  - *作业 A1 发布: Visualization Design*

- **W Sep 25 — Data and Image Models（数据模型与图像模型）**
  - 数据类型：名义（Nominal）、序数（Ordinal）、定量（Quantitative）
  - 图形标记（Marks）与视觉编码通道（Encoding Channels）
  - 🔴 Tufte — *VDQI* Ch 1-3: Graphical Excellence / Integrity / Sources
  - 🟡 Stevens — *On the Theory of Scales of Measurement*（1946）
  - **Notebook**: Data Types, Graphical Marks, and Visual Encodings

**核心概念**: Data-Ink Ratio、Level of Measurement、Marks & Channels

### Week 2: 设计与探索性分析

- **M Sep 30 — Visualization Design and Redesign（可视化设计与重设计）**
  - *A1 截止 / A2 发布: Exploratory Data Analysis*
  - 🔴 Tufte — *VDQI* Ch 4: Data-Ink and Graphical Redesign
  - 🔴 Viégas & Wattenberg — *Design and Redesign in Data Visualization*（Medium）
  - 🟡 Norman — *The Power of Representation* (Things That Make Us Smart, Ch 3)
  - 🟡 Zhang & Norman — *The Representation of Numbers*
  - **Notebook**: Data Transformation

- **W Oct 2 — Exploratory Data Analysis（探索性数据分析）**
  - Tukey 的 EDA 哲学
  - 🔴 Stolte, Tang & Hanrahan — *Polaris*（IEEE TVCG 2002）— Tableau 的前身
  - 🟡 Wongsuphasawat et al. — *Voyager*（IEEE TVCG 2016）— 可视化推荐
  - **Notebook**: Scales, Axes and Legends

**核心概念**: EDA、Polaris/Tableau 架构、Data-Ink Maximization

### Week 3: 图表设计与交互

- **M Oct 7 — Chart Design（图表设计）**
  - 🔴 Cleveland — *Graphical Methods for Data Presentation*（JASA）
  - 🔴 Tufte — *VDQI* Ch 8: Data Density and Small Multiples
  - 🔴 Tufte — *Envisioning Information* Ch 2: Macro/Micro Readings; Ch 4: Small Multiples
  - **Notebook**: Multi-View Composition

- **W Oct 9 — Interaction（交互）**
  - 交互式可视化的分类学
  - 🔴 Heer & Shneiderman — *Interactive Dynamics for Visual Analysis*（ACM Queue 2012）
  - 🟡 *The Death of Interactive Infographics?*（Baur 2017）
  - 🟡 *In Defense of Interactive Graphics*（Aisch 2017）
  - 🟡 Shneiderman — *Dynamic Queries, Starfield Displays → Spotfire*
  - **Notebook**: Interaction

**核心概念**: Small Multiples、Overview+Detail、Dynamic Queries、Brushing & Linking

### Week 4: D3.js 编程

- **M Oct 14 — Introduction to D3**
  - *A2 截止 / A3 发布: Interactive Visualization Software*
  - 🔴 Bostock, Ogievetsky & Heer — *D3: Data-Driven Documents*（InfoVis 2011）
  - **Notebook**: Introduction to D3
  - 🟡 Observable D3 Gallery / Mike Bostock's Notebooks

- **W Oct 16 — D3 Tutorial**
  - 数据绑定（Data Join）：enter / update / exit 模式
  - 比例尺（Scales）、坐标轴（Axes）
  - 交互：事件监听、过渡（Transitions）
  - **Notebook**: Making D3 Charts Interactive / Let's Make a Scatterplot / D3 Exercises

**核心概念**: Data Join Pattern、Selections、Scales、Transitions

### Week 5: 感知与叙事

- **M Oct 21 — Perception（感知）**
  - 视觉感知与预注意处理（Preattentive Processing）
  - 🔴 Healey — *Perception in Visualization*（颜色、形状、运动）
  - 🔴 Cleveland & McGill — *Graphical Perception*（1984）— 编码有效性排序
  - 🔴 Tufte — *Envisioning Information* Ch 3: Layering and Separation
  - 🟡 Durand — *Gestalt and Composition*（SIGGRAPH 2002）
  - 🟡 Heer & Bostock — *Crowdsourcing Graphical Perception*（CHI 2010）

- **W Oct 23 — Visual Explainers（视觉解释器）**
  - 叙事可视化（Narrative Visualization）
  - 🔴 Segel & Heer — *Narrative Visualization: Telling Stories with Data*（InfoVis 2010）
  - 🔴 Corum — *Design for an Audience*（NYT 可视化设计师）
  - 🟡 Hohman et al. — *Communicating with Interactive Articles*（Distill 2020）
  - **实践**: The Pudding 网站精读 3 篇文章

**核心概念**: Preattentive Attributes、Gestalt Principles、Visual Encoding Effectiveness Ranking、Narrative Visualization Genres

### Week 6: 颜色与动画

- **M Oct 28 — Color（颜色）**
  - *A3 截止 / Final Project Proposal 发布*
  - 色彩感知：HSL / Lab / HCL 色彩空间
  - 🔴 Tufte — *Envisioning Information*: Color and Information
  - 🔴 Heer & Stone — *Color Naming Models*（颜色命名与调色板设计）
  - 🟡 Gramazio, Laidlaw & Schloss — *Colorgorical*（调色板生成器）
  - **工具**: ColorBrewer 2.0

- **W Oct 30 — Animation（动画）**
  - 动画在可视化中的作用与风险
  - 🔴 Heer & Robertson — *Animated Transitions in Statistical Data Graphics*（InfoVis 2007）
  - 🔴 Tversky, Morrison & Betrancourt — *Animation: Can It Facilitate?*（IJHCS 2002）
  - 🟡 Lasseter — *Principles of Traditional Animation Applied to Computer Animation*（1987）

**核心概念**: Color Spaces、Sequential vs Diverging vs Categorical Palettes、Animated Transitions、Easing Functions

### Week 7: 网络可视化

- **M Nov 4 — Network Layout（网络布局）**
  - *Final Project Proposal 截止*
  - 力导向布局（Force-Directed Layout）
  - 层次布局（Hierarchical Layout: Reingold-Tilford / Walker）
  - 🔴 Herman, Melançon & Marshall — *Graph Visualization: A Survey*
  - 🔴 Holten — *Hierarchical Edge Bundles*（IEEE TVCG 2006）
  - 🟡 Wattenberg — *Visual Exploration of Multivariate Graphs*（CHI 2006）

- **W Nov 6 — Network Analysis（网络分析）**
  - 中心性指标（Degree / Betweenness / Closeness / Eigenvector Centrality）
  - 社区发现（Community Detection）
  - 🔴 Wasserman & Faust — *Centrality and Prestige*（Social Network Analysis, pp. 169-198）
  - 🔴 Perer & Shneiderman — *Balancing Systematic and Flexible Exploration of Social Networks*
  - 🟡 Newman — *The Structure and Function of Complex Networks*（Sections 1-2）

**核心概念**: Force Simulation、Edge Bundling、Centrality Measures、Node-Link Diagrams vs Adjacency Matrices

### Week 8: 解构可视化与 AI

- **M Nov 11 — Deconstructing Visualizations（解构可视化）**
  - 自动化图表分类与重设计
  - 🔴 Savva et al. — *ReVision: Automated Classification, Analysis and Redesign of Chart Images*
  - 🔴 Kong & Agrawala — *Graphical Overlays: Using Layered Elements to Aid Chart Reading*
  - 🟡 Harper & Agrawala — *Deconstructing and Restyling D3 Visualizations*
  - 🟡 Kong et al. — *Extracting References Between Text and Charts via Crowdsourcing*

- **W Nov 13 — Visualization and AI（可视化与 AI）**
  - *客座讲师: Hari Subramonyam*
  - AI 辅助可视化设计与分析
  - 🔴 Hohman et al. — *Visual Analytics in Deep Learning: An Interrogative Survey*（IEEE TVCG 2018）
  - 🔴 Xiang et al. — *Interactive Correction of Mislabeled Training Data*

**核心概念**: Chart Understanding、Visual Analytics for AI、Human-in-the-Loop ML

### Week 9: 文本可视化与 NLP

- **M Nov 18 — Text Visualization（文本可视化）**
  - 文本数据的视觉表示
  - 词云（Word Clouds）、短语网络（Phrase Nets）
  - 主题模型可视化（Topic Models: LDAvis / Termite）
  - 🔴 van Ham, Wattenberg & Viégas — *Mapping Text with Phrase Nets*（2009）
  - 🔴 Hearst — *Info Vis for Text Analysis* (Search User Interfaces, Ch 11)
  - 🟡 Chuang et al. — *Termite: Visualization for Assessing Textual Topic Models*（2012）

- **W Nov 20 — Visualization and NLP（可视化与自然语言处理）**
  - 自然语言生成可视化描述
  - 图表问答（Chart QA）
  - 无障碍可视化（Accessible Visualization via NL Descriptions）
  - 🔴 Kim et al. — *Answering Questions about Charts and Generating Visual Explanations*
  - 🔴 Kim et al. — *Towards Understanding How Readers Integrate Charts and Captions*
  - 🟡 Setlur et al. — *Eviza: A Natural Language Interface for Visual Analysis*（UIST 2016）
  - 🟡 Lundgard et al. — *Accessible Visualization via Natural Language Descriptions*

**核心概念**: Text as Data、Topic Modeling Visualization、Chart Captioning、NL Interfaces for Vis

### Week 10: Final Project Review

- **M/W Dec 2-4** — Final Project Design Review and Feedback
- **Su Dec 8** — **Final Project 截止**（Website + Code + Video）

---

## 🧮 核心方法

### 视觉编码有效性排序（Cleveland & McGill 1984）

从最准确到最不准确：

1. **位置**（Position）— 最精确
2. **长度**（Length）
3. **角度**（Angle）— 如饼图
4. **方向**（Direction）— 如斜率
5. **面积**（Area）
6. **体积**（Volume）
7. **色彩明度**（Color Saturation/Lightness）— 最不精确
8. **色彩色调**（Color Hue）

> 实践含义：**优先用位置编码定量数据**（散点图 > 柱状图 > 饼图）

### Tufte 的数据墨水比（Data-Ink Ratio）

$$\text{Data-Ink Ratio} = \frac{\text{Data-Ink}}{\text{Total Ink}}$$

原则：**最大化数据墨水比**——删除一切不传递数据的视觉元素（网格线、3D 效果、装饰性图案）。

### D3.js Data Join 模式

```javascript
// D3 核心模式：将数据绑定到 DOM 元素
const selection = svg.selectAll("circle")
    .data(data);

// Enter: 新数据创建元素
selection.enter()
    .append("circle")
    .attr("cx", d => xScale(d.x))
    .attr("cy", d => yScale(d.y))
    .attr("r", 5);

// Update: 已有元素更新
selection.attr("fill", "steelblue");

// Exit: 多余元素删除
selection.exit().remove();
```

### Vega-Lite 声明式语法

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "data": {"url": "data.csv"},
  "mark": "point",
  "encoding": {
    "x": {"field": "x", "type": "quantitative"},
    "y": {"field": "y", "type": "quantitative"},
    "color": {"field": "category", "type": "nominal"}
  }
}
```

---

## 💻 项目代码

📁 `topic7-hci/hci_eval.py`（可视化部分共享）

**CS448B 相关模块**:
- WCAG 审计模块 → 可视化的可访问性检查
- A/B 测试 → 可视化设计的定量评估

### 作业概览

| 作业 | 内容 | 权重 |
|------|------|------|
| **Class Participation** | 课前阅读 + 课堂讨论 | 10% |
| **A1: Visualization Design** | 用 Vega-Lite 设计一个数据可视化 | 10% |
| **A2: Exploratory Data Analysis** | 用 Tableau 做探索性数据分析 | 15% |
| **A3: Interactive Visualization** | 用 D3.js 构建交互式可视化软件 | 25% |
| **Final Project** | 自选主题，构建完整可视化系统（网站+代码+视频） | 40% |

### Final Project 要求
- **Proposal** (Week 6): 描述数据集、任务、设计草图
- **Design Review** (Week 10): 同行评审
- **Final Submission**: 网站 + 源码 + 3 分钟演示视频

---

## 📊 关键论文 / 教材

### 📖 必读教材
1. 🔴 **Tufte** — *The Visual Display of Quantitative Information*（2nd Ed.）— 可视化圣经
2. 🔴 **Tufte** — *Envisioning Information* — 多维信息呈现
3. 🟡 **Tamara Munzner** — *Visualization Analysis and Design*（可选教材）

### 🔴 必读论文（精选 15 篇）

| # | 论文 | 年份 | 核心贡献 |
|---|------|------|---------|
| 1 | Cleveland & McGill — *Graphical Perception* | 1984 | 编码有效性排序 |
| 2 | Stolte, Tang & Hanrahan — *Polaris* (→Tableau) | 2002 | 可视化分析系统 |
| 3 | Bostock et al. — *D3: Data-Driven Documents* | 2011 | D3.js 奠基论文 |
| 4 | Heer & Shneiderman — *Interactive Dynamics* | 2012 | 交互可视化分类学 |
| 5 | Heer & Robertson — *Animated Transitions* | 2007 | 动画过渡设计 |
| 6 | Heer & Bostock — *Crowdsourcing Graphical Perception* | 2010 | MTurk 可视化实验 |
| 7 | Segel & Heer — *Narrative Visualization* | 2010 | 叙事可视化分类 |
| 8 | Holten — *Hierarchical Edge Bundles* | 2006 | 网络布局技术 |
| 9 | Heer & Stone — *Color Naming Models* | 2012 | 颜色选择 |
| 10 | Savva et al. — *ReVision* | 2011 | 自动图表分析 |
| 11 | Kong & Agrawala — *Graphical Overlays* | 2012 | 图表辅助阅读 |
| 12 | Tversky et al. — *Animation: Can It Facilitate?* | 2002 | 动画有效性批判 |
| 13 | van Ham et al. — *Phrase Nets* | 2009 | 文本可视化 |
| 14 | Kim et al. — *Chart QA* | 2021 | 图表问答 |
| 15 | Lundgard et al. — *Accessible Vis via NL* | 2021 | 无障碍可视化 |

---

## 🎯 学习路径

| 角色 | 推荐路径 |
|------|---------|
| **可视化研究员** | CS448B → 发表 IEEE VIS 论文 → PhD |
| **数据分析师** | CS448B + CS197（数据科学）→ Tableau / Power BI |
| **前端可视化工程师** | CS448B + D3.js 实战 → Observable / Plotly / Chart.js |
| **数据记者** | CS448B + The Pudding / NYT 风格 → 数据新闻 |
| **AI + Vis 研究员** | CS448B + CS347 → 可视化驱动的 AI 解释 |

---

## 💡 反思与批判

### 课程优势
1. **Agrawala 教授的研究深度**——他本人的论文就在阅读列表中（Graphical Overlays, Deconstructing D3）
2. **Vega-Lite + D3.js 双轨教学**——从声明式到命令式，覆盖完整技术谱系
3. **阅读列表极其经典**——Tufte / Cleveland / Heer / Shneiderman 全是领域奠基人
4. **Final Project 开放度高**——学生可自由选择数据集和主题
5. **与 Observable 平台深度集成**——交互式 notebook 学习体验极佳

### 潜在局限
1. **D3.js 学习曲线陡峭**——仅 2 讲（Week 4）可能不够，需要大量自学
2. **偏重统计图表**——对 3D / 地理 / 科学可视化覆盖较少
3. **Final Project 占 40%**——权重过大，中期反馈有限
4. **JS / Web 技术门槛**——课程假设学生有 Web 编程基础，但实际差距可能很大
5. **AI 时代可视化**——LLM 能否自动生成可视化？这门课在 2024 版只有 1 讲涉及

### 独特价值
- CS448B 是 **"为什么散点图比饼图好"** 的科学解释——基于认知心理学的严格论证
- **Tufte 的审美哲学**（Data-Ink Ratio、Small Multiples、Graphical Excellence）是终身受用的设计思维
- D3.js 是 **可视化工程的事实标准**——掌握它等于掌握了行业核心技能

---

## 🚀 扩展

完成 CS448B 后推荐：
1. **CS347** — HCI Research Foundations（理论深度）
2. **CS147** — Introduction to HCI（设计思维）
3. **IEEE VIS 会议** — 可视化领域最高会议
4. **Observable** — 在线交互式可视化社区（D3.js 作者 Mike Bostock 的平台）
5. **The Pudding** — 数据新闻标杆（visual explainers）
6. **NYT Upshot / FiveThirtyEight** — 数据新闻实践

### 工具与资源
- **D3.js** — https://d3js.org/
- **Vega-Lite** — https://vega.github.io/vega-lite/
- **Observable** — https://observablehq.com/
- **Tableau Public** — 免费 Tableau
- **ColorBrewer 2.0** — 色彩方案设计
- **Datawrapper** — 新闻级图表工具
- **Plotly / Bokeh / Altair** — Python 可视化生态

---

**最后更新**: 2026-08-11
**对应代码**: `topic7-hci/hci_eval.py`（可视化部分）
