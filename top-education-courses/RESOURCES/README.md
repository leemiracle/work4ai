# 📦 资源索引 (RESOURCES)

> 对标 [`../top-physics-courses/RESOURCES/`]。物理版按优先级 P0-P3；教育版整合本库已提到的资源 + 按用途分类。详细书单见 [`../SURVEY.md`]，本索引做**导航 + 补充**。

---

## 优先级图例

- **P0** = 必读，不读不能入门
- **P1** = 强烈推荐
- **P2** = 进阶/专攻
- **P3** = 拓展/批判

---

## 一、入门第一站（P0）

| 资源 | 类型 | 一句话 |
|---|---|---|
| 本库 [`../EDUCATION_FEYNMAN_NARRATIVE.md`] | 文档 | 主线直觉，从这里开始 |
| **《Make It Stick》** Brown et al. | 书 | 学习科学最佳科普 |
| **《Why Don't Students Like School》** Willingham | 书 | 认知科学九原则，**最被低估的好书** |
| **《Mindset》** Dweck | 书 | 成长型思维 |
| **《How People Learn》** NRC 2000 | 报告（免费）| 美国科学院共识 ⚠️【待联网核实】|

## 二、学习科学核心（P0–P1）

| 资源 | P | 主题 |
|---|---|---|
| Hattie《Visible Learning》| P0 | 效应量圣经 |
| Schunk《Learning Theories》| P1 | 学习理论最全教材 |
| Sawyer 编《Cambridge Handbook of the Learning Sciences》| P1 | 学习科学手册 |
| Roediger & Karpicke (2006)| P1 | 测试效应原论文 |
| Sweller CLT 综述 | P1 | 认知负荷 |
| Zimmerman 元认知综述 | P1 | 元认知 |

## 三、原典（P1，研究必读）

| 资源 | 作者 |
|---|---|
| 《民主主义与教育》| Dewey |
| 《Mind in Society》| Vygotsky |
| 《儿童心理学》| Piaget |
| 《教育过程》| Bruner |
| "2 Sigma Problem" (1984) | Bloom |
| 教学机器论文 (1958) | Skinner |
| 《被压迫者教育学》| Freire |

## 四、评估与心理测量（P1）

| 资源 | 主题 |
|---|---|
| Pellegrino《Knowing What Students Know》(NRC 2001) | 评估共识 |
| Lord《Applications of IRT》| IRT |
| Piech et al. (2015) | DKT |
| Corbett & Anderson (1995) | BKT |

## 五、AI for Education（P1）

| 资源 | 主题 |
|---|---|
| Khan《Brave New Words》(2024) | Khanmigo |
| VanLehn (2011) | ITS 元分析 |
| AIED/L@S/EDM/LAK 会议论文 ⚠️【待联网核实】| 前沿 |
| 协同 [`../../讲透AIfor各学科/教育/`] | 已有前沿整理 |
| [`../ai_for_education/`] | 本库框架 |

## 六、批判与反思（P2，防乌托邦）

| 资源 | 立场 |
|---|---|
| Watters《Teaching Machines》(2021) | 教育技术百年批判史 ⭐ |
| Cuban《Oversold and Underused》| 技术进校现实 |
| Carr《The Shallows》| 互联网让人变浅 |
| Selwyn《Should Robots Replace Teachers?》| 人机分工 |

## 七、教育神经科学（P2）

| 资源 |
|---|
| Tokuhama-Espinosa《Mind, Brain, and Education Science》|
| Geake《The Brain at School》|
| Howard-Jones (2014) 神经神话综述 |
| OECD "Understanding the Brain" 系列 ⚠️【待联网核实】|

## 八、工具与数据（实操）

| 工具/数据 | 用途 |
|---|---|
| **R: mirt/ltm/eRm 包** | IRT 参数估计 |
| **PyTorch** | DKT 复现 |
| **ASSISTments / EdNet 公开数据** | 知识追踪数据 ⚠️【待联网核实】|
| **Anki (SM-2)** | 间隔重复（自用体验）|
| **Khanmigo / ChatGPT Edu** | AI 导师实操 |
| **Buck Institute PBL 模板** | PBL 设计 |
| **Hattie effect size database** | 查效应量 ⚠️【待联网核实】|

## 九、关键论文清单（精读 15 篇）

见 [`../READING_SCHEDULE.md`] 论文清单。按重要性排序。

## 十、视频/课程（公开）⚠️【待联网核实】

- **Stanford GSE 公开课**（Learning Design 等）
- **Harvard GSE 公开课**
- **Khan Academy**（自身体验自适应）
- **Learning How to Learn** (Barbara Oakley, Coursera) — 大众学习法
- **各名校教育学院 YouTube 频道**

---

## 优先级路径（给三类人）

### AI 工程师（2 个月）
1. 本库费曼叙事（1 天）
2. 《Make It Stick》（1 周）
3. 维果茨基选章（1 周）
4. Bloom 2σ + Khan《Brave New Words》（1 周）
5. DKT 论文 + 复现（2 周）
6. 设计 AI 导师 prompt（1 周）

### 教师（2 个月）
1. 本库费曼叙事（1 天）
2. 《Make It Stick》（1 周）
3. Hattie 简写（1 周）
4. Wiggins UBD（1 周）
5. 改造自己一节课（持续）

### 研究者（持续）
全 P0 + P1 + 选 P2 方向 + 投稿。

---

## 与项目资源库的关系

| 已有库 | 关系 |
|---|---|
| [`../../顶级专家资源库/`] | AI 方向资源（数学/算力/社群）|
| [`../../top-math-courses/`] | 数学地基 |
| [`../../top-physics-courses/RESOURCES/`] | 姐妹库 |
| [`../../讲透公开课/`] | 公开课清单（可补教育类）|

> 教育学的数学地基主要是**概率/统计 + 心理测量 + RL**，去 [`../../top-math-courses/`] 补。

---

## ⚠️ 待联网核实清单（联网后回填）

本库编写时联网失效，以下需联网核实：
- 所有 ⚠️ 标记的具体 URL / 课程编号 / 最新数据
- 2024–2026 AIED/L@S/EDM 最新论文
- 各名校教育学院当前课程表
- Hattie effect size database 链接
- 公开数据集（ASSISTments/EdNet）当前 URL
- 公开课视频当前可用性

> 📌 **下一步**：按你的优先级路径走。每完成一项回本表打 ✓。建议把本索引 + [`../SURVEY.md`] 一起存到你的 PKM 工具里。
