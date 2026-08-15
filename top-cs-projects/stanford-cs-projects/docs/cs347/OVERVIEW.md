# CS347: HCI Research Foundations & Frontiers

> Stanford University, Spring 2026
> Instructor: **Maneesh Agrawala**（UC Berkeley → Stanford，可视化与 HCI 领域顶尖学者）
> 时间: 每周 2 次讲座 + 论文讨论
> 先修: CS147 或同等 HCI 经验；强烈建议有研究兴趣
> 难度: ⭐⭐⭐⭐⭐（研究级阅读量 + 批判性思考）
> 官网: http://cs347.stanford.edu/ (或 https://magrawala.github.io/cs347-sp26/)

---

## 📚 课程定位

**Stanford HCI 方向的研究生核心课程**，与 CS147（入门实践）形成鲜明对比。CS147 教你"怎么做设计"，CS347 教你"怎么做 HCI 研究"。

课程核心命题：**HCI 不是单一学科，而是计算机科学、认知心理学、设计学、社会学的交叉领域**。通过精读经典论文和最新前沿研究，学生建立对 HCI 研究范式的系统理解。

### Maneesh Agrawala 教授

Agrawala 是 **可视化（Visualization）和 HCI 领域的世界级学者**：
- **学术轨迹**: UC Berkeley 教授（2004-2015）→ Stanford 教授（2015-至今）
- **代表性工作**:
  - 🔴 *Route-Aware Maps*（2001）— 学术地图生成
  - 🔴 *LineDrive*（2002，ACM TOG）— 自动化路线地图
  - 🔴 *Filmstrip* / *Visder* — 时间序列可视化
  - 🔴 *Designing Effective Step-by-Step Assembly Instructions*（2003）
  - **Lyra** / **Voyager** — 可视化推荐系统
  - **Polestar** / **Voyager 2** — 交互式可视化工具
- **荣誉**: ACM Fellow, IEEE VIS Academy, MAC Award
- **教学风格**: 严谨的论文分析 + 深刻的方法论批判

> CS347 与 CS547（HCI Seminar）的区别：CS547 是每周一次的嘉宾讲座系列（午餐会），CS347 是系统性的研究方法论课程。

---

## 🎯 学习目标

完成本课程后，学生应能：

1. **理解** HCI 研究的多元范式（实证主义 / 解释主义 / 设计导向 / 工程导向）
2. **批判性阅读** HCI 顶会论文（CHI / UIST / VIS / CSCW）
3. **掌握** HCI 核心研究方法：实验设计、问卷调查、访谈分析、日记研究、日志分析
4. **分析** 交互技术的演化脉络（命令行 → GUI → 触摸 → 语音 → AR/VR → Brain-Computer Interface）
5. **评估** HCI 研究的有效性（内部效度 / 外部效度 / 生态效度）
6. **撰写** 研究级别的论文综述和批判报告
7. **识别** HCI 研究的前沿方向和开放问题

---

## 📅 完整模块（10 周）

### Week 1-2: HCI 研究范式与方法论基础

- **L1** — HCI 研究概览
  - HCI 的学科交叉本质：CS + Psych + Design + Sociology
  - 研究范式：实证（Positivist）vs 解释（Interpretivist）vs 设计（Design Science）
  - 🔴 Card, Moran & Newell, *The Psychology of Human-Computer Interaction*（1983）— GOMS / KLM 模型
  - 🔴 Suchman, *Plans and Situated Actions*（1987）— 情境行动理论

- **L2** — 研究方法论
  - **定量方法**: 对照实验（Controlled Experiment）、A/B 测试、眼动追踪、日志分析
  - **定性方法**: 半结构化访谈、情境访谈、日记研究（Diary Study）、影子观察（Shadowing）
  - **混合方法**: 顺序解释设计（Sequential Explanatory Design）
  - 🔴 Mackay & Wested, *Research Methods in HCI*（2022）

**核心概念**: Internal Validity、External Validity、Ecological Validity、Construct Validity

### Week 3-4: 交互技术演化史

- **L3** — 从命令行到 GUI
  - 🔴 Vannevar Bush, *As We May Think*（1945）— Memex 概念
  - 🔴 Sutherland, *Sketchpad*（1963）— 交互式图形界面的鼻祖
  - 🔴 Engelbart, *Augmenting Human Intellect*（1962）/"Mother of All Demos"（1968）
  - 🔴 Kay & Goldberg, *Personal Dynamic Media*（1977）— Dynabook / Smalltalk
  - 🔴 Card, Robertson & Mackinlay, *The Information Visualizer*（1991）

- **L4** — 直接操纵与图形界面
  - 🔴 Hutchins, Hollan & Norman, *Direct Manipulation Interfaces*（1985）
  - 🔴 Shneiderman, *Direct Manipulation: A Step Beyond Programming Languages*（1983）
  - 🔴 Apple Human Interface Guidelines（1987）

**核心概念**: Direct Manipulation、WIMP（Windows/Icons/Menus/Pointer）、Affordance、Gulf of Execution / Gulf of Evaluation

### Week 5: 认知模型与用户建模

- **L5** — 认知架构与预测模型
  - **GOMS**（Goals, Operators, Methods, Selection Rules）
  - **KLM**（Keystroke-Level Model）— 任务完成时间预测
  - **Fitts' Law**: $T = a + b \log_2(1 + D/W)$
  - **Hick's Law**: $RT = a + b \log_2(n+1)$
  - **Power Law of Practice**: $T_n = T_1 \cdot n^{-\alpha}$
  - 🔴 Card, Moran & Newell, *The Keystroke-Level Model*（1980）
  - 🔴 John & Kieras, *Using GOMS for User Interface Design*（1996）

**核心概念**: Model Human Processor（MHP）、Cognitive Workload、Mental Model

### Week 6: 可视化与信息呈现

- **L6** — 信息可视化基础（与 CS448B 交叉）
  - 🔴 Card, Mackinlay & Shneiderman, *Readings in Information Visualization*（1999）
  - 🔴 Tufte, *The Visual Display of Quantitative Information*（数据墨水比 / 图表垃圾）
  - 🔴 Cleveland & McGill, *Graphical Perception*（1984）— 视觉编码有效性排序
  - **视觉编码通道**: Position > Length > Angle > Area > Volume > Color Hue
  - 🔴 Heer & Bostock, *Crowdsourcing Graphical Perception*（CHI 2010）

**核心概念**: Data-Ink Ratio、Small Multiples、Visual Encoding Channels、Graphical Perception

### Week 7: 协作与社会计算

- **L7** — CSCW（计算机支持协作工作）
  - 🔴 Schmidt & Bannon, *Taking CSCW Seriously*（1992）
  - 🔴 Dourish & Bellotti, *Awareness and Coordination in Shared Workspaces*（1992, CSCW）
  - **时间/空间矩阵**: 同步/异步 × 同地/远程
  - 🔴 Grudin, *Groupware and Social Dynamics*（1994, CACM）— 8 个挑战
  - 🔴 Mark, *Social Network Analysis in HCI*

**核心概念**: CSCW、Groupware、Awareness、Social Navigation、Crowdsourcing

### Week 8: 自然交互与智能界面

- **L8** — 超越 GUI 的交互范式
  - **语音交互**: 🔴 Hearst, *Trends & Controversies: Mixed-Initiative Interaction*（1999, IEEE Intelligent Systems）
  - **手势交互**: 🔴 Wobbrock, *Gestures for Surface Computing*（2009, CHI）
  - **AR/VR**: 🔴 Billinghurst, *Tangible Interfaces* / Azuma, *A Survey of Augmented Reality*（1997）
  - **Brain-Computer Interface**: 🔴 Wolpaw, *Brain-Computer Interfaces*（2002）
  - **可触交互（Tangible UI）**: 🔴 Ishii & Ullmer, *Tangible Bits*（1997, CHI）

**核心概念**: Mixed-Initiative、Multimodal Interaction、Tangible Bits、Embodied Interaction

### Week 9: HCI + AI 前沿

- **L9** — 人机智能交互（Human-AI Interaction, HAI）
  - 🔴 Amershi et al., *Guidelines for Human-AI Interaction*（CHI 2019）— Microsoft 18 条准则
  - 🔴 Horvitz, *Principles of Mixed-Initiative User Interfaces*（1999, CHI）
  - **Explainable AI（XAI）**: 用户何时需要 AI 解释？
  - **Automation Bias**: 人类过度信任自动化的风险
  - 🔴 Bansal et al., *Does the Whole Exceed its Parts?*（CSCW 2021）— AI 团队效应
  - 🔴 Lai et al., *Human-AI Collaboration via Delegation*（2022）

**核心概念**: Human-AI Teaming、Delegation、Calibrated Trust、Automation Bias、Explainability

### Week 10: HCI 研究前沿与开放问题

- **L10** — 开放问题与未来方向
  - **无处不在计算（Ubiquitous Computing）**: Weiser, *The Computer for the 21st Century*（1991, Scientific American）
  - **可访问性研究**: 🔴 Mankoff et al., *Disability Studies as a Source of Critical Inquiry*（ASSETS 2010）
  - **伦理 HCI**: 🔴 Shneiderman, *Bridging the Gap Between Ethics and Practice*（2020, CACM）
  - **HCI 与社会正义**: 🔴 Bardzell, *Feminist HCI*（2010, CHI）
  - **LLM 时代的 HCI**: 智能体（Agents）的交互设计

---

## 🧮 核心方法

### HCI 研究方法分类

| 方法类型 | 具体方法 | 研究问题 | 效度重点 |
|---------|---------|---------|---------|
| **实验研究** | 对照实验、A/B 测试 | "A 比 B 更有效吗？" | 内部效度 |
| **实地研究** | 情境访谈、影子观察 | "用户在真实环境中如何使用？" | 生态效度 |
| **调查研究** | 问卷调查、大规模日志 | "用户群体有什么特征？" | 外部效度 |
| **设计研究** | 原型探索、设计探针 | "这个设计可能吗？" | 建构效度 |
| **分析研究** | GOMS / KLM 建模 | "这个界面效率如何？" | 预测效度 |

### 经典预测模型

#### Fitts' Law（菲茨定律）
$$MT = a + b \cdot \log_2\left(\frac{D}{W} + 1\right)$$

- $D$ = 到目标的距离
- $W$ = 目标宽度
- $\log_2(D/W + 1)$ = 运动难度指数（Index of Difficulty）
- **应用**: 按钮尺寸设计、菜单布局、Fitts' Law 优化

#### Hick's Law（希克定律）
$$RT = a + b \cdot \log_2(n + 1)$$

- $n$ = 选项数量
- **应用**: 菜单项数量优化、导航层级设计

#### KLM（Keystroke-Level Model）
任务完成时间 = $\sum$ （击键时间 + 指向时间 + 心理准备时间 + 系统响应时间）

---

## 💻 项目代码

📁 `topic7-hci/hci_eval.py`（与 CS147 共享，侧重理论部分）

**CS347 侧重使用的模块**:

### 1. A/B 测试 + 统计显著性
```python
# z-test for proportions — HCI 实验统计基础
def ab_test(a_conversions, b_conversions):
    p_pool = (sum(a) + sum(b)) / (len(a) + len(b))
    se = sqrt(p_pool * (1-p_pool) * (1/n_a + 1/n_b))
    z = (p_b - p_a) / se
    return abs(z) > 1.96  # p < 0.05
```

### 2. SUS（System Usability Scale）
```python
# Brooke (1996) — 经典可用性量表
# 10 题，奇数正向(r-1)，偶数反向(5-r)，总分×2.5
# >68 = 可用, >80 = 优秀, <51 = 不可接受
def sus_score(responses):
    total = sum(r-1 if i%2==0 else 5-r for i, r in enumerate(responses))
    return total * 2.5
```

### 3. WCAG 审计（可访问性研究方法）
```python
# 自动化可访问性检查 — 对应 CS347 Week 10 可访问性研究
WCAG_CRITERIA = [
    ("1.1.1_non_text_content", "非文本内容有替代"),
    ("1.4.3_contrast_minimum", "对比度 ≥ 4.5:1"),
    # ...
]
```

### 运行
```bash
cd topic7-hci
python3 hci_eval.py
```

---

## 📊 关键论文 / 教材

### 🔴 必读 P0 — HCI 奠基文献

| # | 论文 | 年份 | 核心贡献 |
|---|------|------|---------|
| 1 | Card, Moran & Newell — *The Psychology of HCI* | 1983 | Model Human Processor / GOMS |
| 2 | Hutchins, Hollan & Norman — *Direct Manipulation Interfaces* | 1985 | 直接操纵理论 |
| 3 | Suchman — *Plans and Situated Actions* | 1987 | 情境行动理论 |
| 4 | Weiser — *The Computer for the 21st Century* | 1991 | Ubiquitous Computing |
| 5 | Schmidt & Bannon — *Taking CSCW Seriously* | 1992 | CSCW 理论框架 |
| 6 | Card, Mackinlay & Shneiderman — *Readings in InfoVis* | 1999 | 可视化奠基 |
| 7 | Ishii & Ullmer — *Tangible Bits* | 1997 (CHI) | 可触界面 |
| 8 | Amershi et al. — *Guidelines for Human-AI Interaction* | 2019 (CHI) | HAI 18 准则 |

### 🟡 P1 — 经典方法论

9. **Mackay & Wested** — *Research Methods in HCI*（2022）— 方法论教科书
10. **John & Kieras** — *Using GOMS for UI Design*（1996）— GOMS 实践
11. **Nielsen** — *Usability Engineering*（1993）— 可用性工程
12. **Horvitz** — *Principles of Mixed-Initiative UI*（1999, CHI）
13. **Bardzell** — *Feminist HCI*（2010, CHI）— 批判性 HCI

### 📖 延伸
14. **Rogers, Sharp & Preece** — *Interaction Design: Beyond HCI*（5th Ed.）
15. **Shneiderman et al.** — *Designing the User Interface*（6th Ed.）

---

## 🎯 学习路径

| 角色 | 推荐路径 |
|------|---------|
| **HCI 研究者（PhD）** | CS147 → CS347 → CS448B → 发表 CHI/UIST 论文 |
| **可视化研究员** | CS347 + CS448B → IEEE VIS 发表 |
| **AI 产品研究员** | CS347 + CS329X（HC LLMs）→ HAI 研究 |
| **UX Researcher** | CS347 + 实习（Google/Meta/Microsoft Research） |
| **无障碍研究员** | CS347 + ASSETS 会议 |

---

## 💡 反思与批判

### 课程优势
1. **Agrawala 教授的研究视野**极其开阔——从经典 GOMS 到现代 HAI，覆盖 60 年 HCI 研究史
2. **论文阅读 + 批判讨论**的模式培养了真正的研究品味
3. 与 CS448B 的可视化内容**交叉互补**——Agrawala 同时教两门课
4. 强调 **方法论批判**——不盲目崇拜任何单一范式

### 潜在局限
1. **阅读量极大**——每周 3-5 篇论文，且需写 reading response
2. **偏重学术研究视角**——对工业界 UX 实践覆盖较少
3. **HCI 领域本身碎片化**——从认知建模到社会正义，跨度太大可能导致浅尝辄止
4. **LLM 时代的 HCI 研究方法正在剧变**——传统实验方法可能不适用于 AI 交互研究

### 独特价值
- CS347 培养的是 **"研究者视角"**——不是"怎么设计好界面"，而是"怎么产生关于界面的新知识"
- **HCI 不是单一学科**这一认知本身就是课程最重要的产出之一
- **批判性阅读论文**的能力可迁移到任何研究型工作

---

## 🚀 扩展

完成 CS347 后推荐：
1. **CS448B** — Data Visualization（Agrawala 的可视化课，深度互补）
2. **CS547** — HCI Seminar（每周嘉宾午餐讲座，了解最新前沿）
3. **CS329X** — Human-Centered LLMs（AI 时代的 HCI）
4. **CS377G** — Serious Games（游戏化与教育）
5. **CHI / UIST / CSCW / IEEE VIS** — 四大 HCI 顶会
6. **ASSETS** — 无障碍计算专门会议

### 研究资源
- **ACM Digital Library** — HCI 论文数据库
- **HCI Bibliography** — http://hcibib.org/
- **NN/g Articles** — 工业 UX 研究
- **Stanford HCI Group** — https://hci.stanford.edu/

---

**最后更新**: 2026-08-11
**对应代码**: `topic7-hci/hci_eval.py`（理论部分）
