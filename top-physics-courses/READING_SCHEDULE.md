# 12 / 24 / 36 月可执行周历 — 把所有资源串起来

> **为什么写这个**：[EXPERT_PATH_2026.md](EXPERT_PATH_2026.md) 给了战略，[RESOURCES/](RESOURCES/) 给了资源，但没有"这周该做什么"。本文档把所有东西串成**可勾选的周历**。
>
> **假设**：每周 10-20h（与你 human 记忆一致），物理从零开始，但已有 work4ai 的 AI 能力和 top-math-courses 的数学资源。

---

## §0 总体节奏（每周模板）

```
周一-周五（每天 1-2h）
  - 30 分钟：数学（[01_mathematics.md](RESOURCES/01_mathematics.md)）
  - 30-60 分钟：物理（项目 L01-L15 + 做题）
  - 15 分钟：arXiv 摘要扫读 + Physics SE

周末（3-5h）
  - 1-2 小时：复现项目（[04_research_training.md](RESOURCES/04_research_training.md)）
  - 1 小时：论文精读（[03_paper_reading_list.md](RESOURCES/03_paper_reading_list.md)）
  - 1 小时：写笔记 / GitHub commit
```

**铁律**：每周至少 1 个 GitHub commit（哪怕只是笔记）。

---

## §1 阶段 1（月 1-12）：补地基

**目标**：能读懂 Griffiths 全部数学，能推麦克斯韦→光速，能用 NumPy 跑氢原子能级。

### 月 1-2：力学 + 数学方法
| 周 | 数学 | 物理 | 工具 | 产出 |
|----|------|------|------|------|
| 1-2 | Boas ch7（ODE）| L01 牛顿力学 | 装 NumPy/SciPy | 第一个 GitHub repo |
| 3-4 | Boas ch3（矢量微积分）| L01 拉格朗日 | matplotlib 画图 | 单摆 ODE 解 + 图 |
| 5-6 | Gelfand & Fomin ch1-2 | L01 哈密顿 | LaTeX 入门 | 拉氏推单摆笔记 |
| 7-8 | Boas ch6（特殊函数）| 复习 + 做题 | Overleaf 注册 | Morin 10 题解答 |

**月 2 自检**：用拉氏方程推单摆，纸笔，不看资料。

### 月 3-4：电磁 + 复分析
| 周 | 数学 | 物理 | 工具 | 产出 |
|----|------|------|------|------|
| 9-10 | Needham《Visual Complex Analysis》ch1-3 | L02 静电学 | SymPy 符号推导 | 留数定理算积分 notebook |
| 11-12 | Needham ch4-6 | L02 静磁学 | - | 麦克斯韦→光速推导 |
| 13-14 | Boas ch10（张量）| L02 麦克斯韦方程 | - | 电磁波推导笔记 |
| 15-16 | 复习 + qualifying 题 | L02 完成 | - | MIT 8.022 题解 10 题 |

**月 4 自检**：从麦克斯韦方程推光速 $c = 1/\sqrt{\mu_0\varepsilon_0}$。

### 月 5-6：波 + 量子入门
| 周 | 数学 | 物理 | 工具 | 产出 |
|----|------|------|------|------|
| 17-18 | Boas ch14（积分变换）| L03 波动方程 | - | 双缝干涉数值模拟 |
| 19-20 | Boas ch11（PDE）| L03 光学 | - | 衍射图样 notebook |
| 21-22 | Axler《LADR》ch1-5 | L04 热力学 | - | 熵增可视化 |
| 23-24 | Axler ch6-10 | L05 统计力学入门 | - | Metropolis Ising 玩具版 |

**月 6 自检**：解释熵增为什么是统计规律；Metropolis 跑出 Ising 临界温度 $T_c \approx 2.27$。

### 月 7-8：统计 + 数学方法深化
| 周 | 数学 | 物理 | 工具 | 产出 |
|----|------|------|------|------|
| 25-26 | Pitman 概率 ch1-3 | L05 玻尔兹曼 | - | Maxwell-Boltzmann 分布推导 |
| 27-28 | Cover & Thomas ch2（信息论）| L05 系综 | - | 熵 = 信息 notebook |
| 29-30 | Boas ch12（格林函数）| L06 数学方法 | - | 格林函数解静电 |
| 31-32 | 复习 + qualifying | L06 完成 | - | Princeton PHY 403 题解 |

### 月 9-10：量子入门 + 量子中级
| 周 | 数学 | 物理 | 工具 | 产出 |
|----|------|------|------|------|
| 33-34 | Hilbert 空间（Kreyszig ch1-3）| L07 狭义相对论 | - | 时间膨胀推导 |
| 35-36 | 群论入门（Tung ch1-3）| L08 量子入门 | - | 无限深势阱 notebook |
| 37-38 | Tung ch4-5（SO(3)）| L08 薛定谔方程 | - | Crank-Nicolson 波包演化 |
| 39-40 | Tung ch6-7（SU(2)）| L09 氢原子 | - | 氢原子能级（NumPy 数值解）|

**月 10 自检**：从薛定谔方程推无限深势阱能级；解释为什么电子自旋是 1/2。

### 月 11-12：复习 + 第一个复现
| 周 | 活动 | 产出 |
|----|------|------|
| 41-42 | 复习 L01-L09，做 Sakurai 习题 | Sakurai 题解 10 题 |
| 43-44 | **第一个复现**：Bell CHSH（[04 §2.2 项目 4](RESOURCES/04_research_training.md)）| GitHub repo + notebook |
| 45-46 | 复现：氢分子解离（项目 5）| PySCF notebook |
| 47-48 | 年度总结 + 重设目标 | 年度报告（博客或 GitHub）|

**月 12 总自检**（对照 [EXPERT_PATH §6 里程碑](EXPERT_PATH_2026.md)）：
- [ ] 拉氏推单摆 ✓
- [ ] 麦克斯韦→光速 ✓
- [ ] 解势阱能级 ✓
- [ ] Metropolis Ising ✓
- [ ] 第一个复现 repo ✓

---

## §2 阶段 2（月 13-24）：进入研究门槛

**目标**：能读 Peskin 前 3 章、Carroll GR 全本、复现 3 篇经典论文、Physics SE 1k 声望。

### 月 13-16：广义相对论
| 内容 | 资源 |
|------|------|
| 微分几何 | Schutz 全本 + Nakahara ch5-6（[01 §3.3](RESOURCES/01_mathematics.md)）|
| GR 主体 | Carroll ch1-6（L10）|
| demo | 项目 `princeton-physics/physics_demos.py` |
| 复现 | Schwarzschild 度规 Christoffel 符号 |

### 月 17-20：量子场论入门
| 内容 | 资源 |
|------|------|
| 泛函分析 | Reed & Simon vol1 ch1-3（[01 §3.5](RESOURCES/01_mathematics.md)）|
| QFT | Peskin ch1-3（L11）|
| 群论 | Cornwell vol1（SU(3)）|
| 论文 | Yang-Mills 1954 + Higgs 1964（[03 §5](RESOURCES/03_paper_reading_list.md)）|

### 月 21-24：凝聚态 + 论文复现
| 内容 | 资源 |
|------|------|
| 凝聚态 | Simon 全本（L12）|
| 拓扑入门 | Nash & Sen（[01 §3.6](RESOURCES/01_mathematics.md)）|
| 论文 | TKNN 1982 + Kane-Mele 2005（[03 §3](RESOURCES/03_paper_reading_list.md)）|
| 复现 | DMRG 解 Heisenberg 链（[04 项目 10](RESOURCES/04_research_training.md)）|

**月 24 自检**：
- [ ] Carroll GR 全本读完，能算 Schwarzschild Christoffel
- [ ] Peskin 前 3 章读完，能解释费曼图
- [ ] Physics SE 声望 1k+
- [ ] 3 个复现 repo

### 阶段 2 的社区行动（每月 1 件）
- 月 13：注册 arXiv 账号
- 月 15：给 1 位 arXiv 作者发邮件
- 月 18：申请国内暑期学校
- 月 21：Physics SE 答第 50 题
- 月 24：给 3 位教授发"远程合作咨询"邮件

---

## §3 阶段 3（月 25-36）：选定方向 + 第一个产出

**目标**：选定 AI for Physics 方向，完成第一个 mini-project，第一篇 arXiv preprint。

### 月 25-28：AI for Physics 深入
| 内容 | 资源 |
|------|------|
| PINN 进阶 | `ai_for_physics/pinn_poisson.py` → Burgers 方程（[04 项目 9](RESOURCES/04_research_training.md)）|
| 神经势能 | DeepMD-kit 官方 tutorial |
| 等变网络 | NequIP 论文（[03 §6 #57](RESOURCES/03_paper_reading_list.md)）|
| 可微 DFT | PySCF + JAX（[02 §3.3](RESOURCES/02_computational_toolchain.md)）|

### 月 29-32：第一个 mini-project
- 选 [04 §3.3 候选 A-F](RESOURCES/04_research_training.md) 之一
- 用 2 个月完成（实现 + 实验 + 写作）
- 写成 mini-paper（LaTeX，IMRAD）

### 月 33-36：第一篇 arXiv + 找合作者
- 月 33：mini-paper 投 arXiv（需要 endorsement）
- 月 34：联系 3-5 位相关方向教授/博后
- 月 35：参加一个会议（NeurIPS AI4Science Workshop / 国内会议）
- 月 36：年度总结 + 36 月里程碑自检

**月 36 自检**（对照 [EXPERT_PATH §6 里程碑](EXPERT_PATH_2026.md)）：
- [ ] 第一篇 arXiv preprint
- [ ] 一个稳定的合作者/导师关系
- [ ] GitHub 10+ repo
- [ ] Physics SE 声望 2k+
- [ ] 能解释 Berry 相位的几何意义
- [ ] 能用表示论解释夸克颜色 SU(3)

---

## §4 阶段 4（月 37-60）：进入学术/工业轨道

**目标**：申请 PhD 或进入工业研究实验室。

### 月 37-48：深化 + 第二/三篇论文
- 第二篇论文（扩展 mini-project 到完整工作）
- 申请暑期学校（Les Houches / KITP / Perimeter PSI）
- 建立 Google Scholar 主页

### 月 49-60：申请
- **若年龄/条件允许**：申请 PhD（美国/欧洲/中国香港）
- **否则**：申请工业研究实验室（见 [ai_for_physics/ai_for_physics.md §4](ai_for_physics/ai_for_physics.md)）
  - 字节豆包 / 深势科技 / 上海 AI Lab / 清华 AIR
  - Google DeepMind / Microsoft Research / Meta AI

---

## §5 每日/每周/每月固定动作（养成习惯）

### 每日（15 分钟）
- [ ] arXiv listings 扫读标题（[03 §9](RESOURCES/03_paper_reading_list.md)）
- [ ] Physics SE 看 1 个问题

### 每周（2 小时）
- [ ] 1 场 KITP/Perimeter seminar 录像（[03 §9](RESOURCES/03_paper_reading_list.md)）
- [ ] 1 次 GitHub commit
- [ ] 1 章经典教材序言（[07 §3](RESOURCES/07_taste_intuition.md)）

### 每月（半天）
- [ ] 1 场 Nobel Lecture（[03 §8](RESOURCES/03_paper_reading_list.md)）
- [ ] 自检（对照本表）
- [ ] 更新 GitHub portfolio

### 每季
- [ ] 给 1 位教授发邮件
- [ ] 写 1 篇 blog（学习总结）
- [ ] 重读 1 篇经典论文

### 每年
- [ ] 重读 Feynman Lectures 1 卷
- [ ] 申请 1 个暑期学校
- [ ] 年度总结（公开 blog）

---

## §6 弹性：落后了怎么办

### 场景 1：某月进度落后 50%
- **不要**加倍赶（会崩溃）
- **要**：减范围保深度（学 1 个主题学到透，胜过 3 个浅尝）
- 调整下月计划

### 场景 2：某个主题卡住（如 GR）
- **不要**：硬刚 1 个月
- **要**：① 换教材（Carroll → Schutz）② 找 YouTube 视频 ③ 在 Physics SE 问 ④ 暂时跳过学下一个，回头再战

### 场景 3：动力崩溃
- **不要**：强迫自己（会厌恶物理）
- **要**：① 读 Feynman 传记 ② 看 Nobel Lecture ③ 换个有趣的小项目（如跑 PINN）④ 休息 1 周

### 场景 4：家人/工作挤压时间
- **不要**：放弃
- **要**：减到每周 5h 也比 0 强。**持续 > 强度**。

---

## §7 你的"成功"是什么（避免迷失）

| 不是成功 | 是成功 |
|---------|--------|
| 30 岁前拿诺奖 | 30 岁前能读懂 arXiv 最新论文 |
| 进入 MIT | 在某交叉方向有独特贡献 |
| 1000 篇论文 | 1 篇被人引用 10 年的论文 |
| 被 Witten 认可 | 有 1 个稳定合作者 |
| 完美按计划 | 持续学习 10 年不放弃 |

**最重要的一句**：**Hinton 65 岁才 AlexNet，77 岁诺奖。你不急。**

---

**完成日期**：2026-08-13
**配套**：[EXPERT_PATH_2026.md](EXPERT_PATH_2026.md) + 全部 [RESOURCES/](RESOURCES/) + [ai_for_physics/](ai_for_physics/) + [EXPERT_BENCHMARKS.md](EXPERT_BENCHMARKS.md)
