# work4ai · AI 学习知识库总览

> 一套用「直觉 → 数学 → 代码跑通 → 不足 → 应用」范式写的 AI 讲透系列。
> 从神经网络地基到大模型全栈，从技术组件到所有学科应用，每个主题都往**底层和本质**钻。

---

## 📊 项目规模

| 维度 | 数量 |
|---|---|
| **.md 文件** | **613** |
| **总行数** | **80,600+** |
| **讲透系列** | **37**（12 完整 + 系统论/数学建模补全 + 反传/损失/优化器已并入PyTorch + 21 待补，含 2 个 2026-08 新增前沿主题）|
| **AIfor 各学科** | **29** |
| **本质探索** | **29** |
| **费曼学习法** | **质量门 F1-F4 + AI 陪练脚本**（戳穿"自以为懂"）|
| **CS 课程整合** | **4 跨校主题**（算法 + 数据库 + 网络 + CS224N/NLP）+ 5 单校纵深（CMU/MIT/Berkeley/Cambridge/ETH）⭐ 2026-08 |

---

## 一、37 个「讲透」系列

### A. 已完整（12 个）✅

| 系列 | 讲什么 |
|---|---|
| **讲透激活函数** | 神经网络地基：非线性 → ReLU → SwiGLU |
| **讲透基础模型** | NTP → 注意力 → 规模律 → 涌现 → 对齐 → 部署 + **advanced 层（博士级）** |
| **讲透Transformer** | Self-Attention → 位置编码 → MoE → 推理优化 |
| **讲透微调** | LoRA → PEFT → QLoRA → 数据 → 失败 → 实战 |
| **讲透Prompt** | 条件概率 → ICL → CoT → 结构化输出 |
| **讲透RAG** | 检索数学 → 工程 → 高级架构 → 评估 |
| **讲透PyTorch** | Tensor → Autograd(**含反传数学本质VJP/m≪n/O(N)**) → 训练(**含损失函数/优化器/故障**) → compile → 内核精读(**含mutation边界/反传未来**) → 生态 ⭐ 已吸收原反传/损失/优化器三系列 |
| **讲透GPU与系统级** | FlashAttention → vLLM → 量化 → CUDA |
| **讲透复用权重** | 迁移学习 → PEFT → 蒸馏 → 持续学习 |
| **讲透泛化** | 隐式正则 → 平坦极小值 → 双层下降 |
| **讲透生成模型** | AR → VAE → GAN → Flow → Diffusion → Score |
| **讲透AI应用全景** | 7 大领域（含 AI for AI 元篇章）|

### B. 待补全 / 新增（25 个）🟡

| 系列 | 现状 |
|---|---|
| **讲透RL** | 00(MDP) + 01(DQN) + 02(PPO) + 03(RLHF/DPO/GRPO) + **04(RL+形式证明) + 05(RLVR极限) + 06(RL+系统软件) + 07(全景地图+2026最新研究)** ⭐ 2026-08-12 |
| **讲透分布式AI系统** | 00-03（DDP/FSDP/ZeRO/TP）|
| **讲透KV Cache** | 00-01 + README |
| **讲透世界模型**（博士级试点）| README + 00 + **advanced×4** |
| **讲透基础模型**（博士级试点）| + **advanced×4**（ScalingLaw 证明 + 涌现争论）|
| **讲透AI历史**（思想史）| README + 00 + **advanced×2**（库恩范式分析）|
| **讲透统计学习理论**（博士地基）| README + 00 |
| **讲透概率图模型**（博士地基）| README + 00 |
| **讲透因果推断**（博士地基）| README + 00 |
| **讲透符号主义**（博士地基）| README + 00 |
| **讲透优化理论**（博士地基）| README + 00 |
| **讲透可解释性** | README + 00 |
| **讲透形式化验证** 🆕 | README + **00（seL4→Lean4 SOTA + 验证剧场）** ⭐ 2026-08 |
| **讲透神经符号** 🆕 | README + **00（LLM+Lean4 闭环 + 基准破灭）** ⭐ 2026-08 |
| **讲透数据** | README + 00 + 03(Model Collapse) |
| **讲透科学的现代性** | README + 00-03（三视角合一）|
| ... | Agent / 信息论 / 控制论 / 系统论 / 公开课 |

---

## 二、30 个「AI for 各学科」

> 每个学科 **8 篇标准内容**：00（总览）+ 本质探索 + 早期经典 + 最新前沿 + advanced×4

### 自然科学（8）
| 学科 | 核心 |
|---|---|
| **物理** | AI 是第三种方法（理论+实验+数据驱动）|
| **化学** | 10^60 分子空间 + AlphaFold 3 + Coscientist |
| **生物** | AlphaFold 革命 + 单细胞基础模型 + BCI |
| **材料** | GNoME 220 万新材料 + A-Lab 自主实验室 |
| **天文** | LSST 每夜 15TB + 引力波 + JWST 深空 |
| **地球气候** | GraphCast 完胜 ECMWF + Google 洪水预警 |
| **数学** | AlphaProof IMO 银牌 + Lean + Neurosymbolic |
| **统计学** | 现代统计 = 经典 + ML + Conformal Prediction |

### 工程（4）
| 学科 | 核心 |
|---|---|
| **芯片设计** | AlphaChip 6月→几小时 + TPU 生产用 |
| **机器人** | 2024 ImageNet 时刻（RT-2/π₀/GR00T/Figure）|
| **航空航天** | SpaceX + eVTOL + 火星探索 |
| **软件工程** | Devin/Cursor + SWE-bench + 多 Agent |

### 社科（6）
| 学科 | 核心 |
|---|---|
| **经济金融** | LLM 多智能体模拟 + 因果 ML + 量化交易 |
| **法学** | Harvey/Lexis+ AI + 欧盟 AI Act + AI 法独立 |
| **政治学** | 2024 大选 AI + Deepfake + LLM 政治模拟 |
| **心理学** | LLM 心智理论 + fMRI 解码 + AI 治疗 |
| **社会学** | SmallVille + 算法极化 + 计算社科 |
| **人类学** | 古 DNA 革命 + 濒危语言 + 去殖民化 AI |

### 人文（6）
| 学科 | 核心 |
|---|---|
| **哲学** | Chalmers vs LeCun + 意识 + AI 伦理 |
| **历史学** | Vesuvius + Ithaca + 古 DNA + 数字人文 |
| **语言学** | Chomsky vs Hinton + LLM 句法 circuit |
| **文学** | AI 创作 + 远读 + 版权 + Barthes |
| **艺术** | Stable Diffusion + Danto + 版权大战 |
| **音乐** | Suno/Udio + WaveNet + RIAA 诉讼 |

### 交叉 / 应用（6）
| 学科 | 核心 |
|---|---|
| **教育** | Bloom 2 Sigma + Khanmigo + 作业代写危机 |
| **能源** | DeepMind 核聚变 + 智能电网 + 气候 |
| **农业** | 精准农业 + GNoME + 替代蛋白 |
| **公共健康** | COVID AI + mRNA + 下次疫情 |
| **复杂系统** | 涌现 + 网络科学 + Neural ODE |
| **考古学** | LiDAR + 古 DNA + Vesuvius + 3D 遗产 |

---

## 三、参考资料（非教程类）

### 1. 系统学：[`讲透公开课/`](讲透公开课/)
- 01 前沿 AI/ML/DL 课（10 门）
- 02 数理计算机神课（30+ 门）
- 03 AI Infra 源码导读（20+ 项目）
- 04 全领域学习路径

### 2. 前沿：[`前沿与媒体/`](前沿与媒体/)
- 01 AI 顶级信息源（80+ 条）
- 02 后训练专题（30+ 条）
- **102 HuggingFace 生态全景**（467 库分类 × 对接 work4ai 各系列，含覆盖热力图与缺口清单）⭐ 2026-08

### 3. 深度：[`访谈及其他/`](访谈及其他/)
- 谢清池访谈 / 张小珺访谈录 33 集

### 4. 总纲：[`横向打通-能力获取决策框架.md`](横向打通-能力获取决策框架.md)

### 5. 知识桥梁：[`neo-os知识桥梁.md`](neo-os知识桥梁.md)
- 与 `../neo-os`（通用复杂软件可解释性基础设施）项目的知识映射
- 2026-08 回流的 5 份前沿探索：RL+形式证明 / RLVR 极限 / RL+系统软件 / Lean4 形式化 / 神经符号闭环（详见 [`讲透RL/04-06`](讲透RL/) + [`讲透形式化验证`](讲透形式化验证/) + [`讲透神经符号`](讲透神经符号/)）

### 6. 产业架构参考：[`Agent架构模式参考/`](Agent架构模式参考/)
- 基于五类 AI Agent 产品形态（IDE-A/IDE-B/桌面Agent/CLI-TUI框架/多渠道网关）的脱敏架构调研：全景+对比+创新对决+选型决策树 ⭐ 2026-08（**已完全脱敏**，不指向任何商业产品）

### 7. 端侧 AI 参考：[`端侧AI架构参考.md`](端侧AI架构参考.md)
- 端侧 AI 系统的 11 功能域 + 5 大部署模式 + memory/搜索架构 + 可迁移性分析 ⭐ 2026-08（**已完全脱敏**，不含任何厂商/SDK/类名/逆向证据）

### 8. 高效 AI 研究：[`高效AI研究参考-MITHANLab.md`](高效AI研究参考-MITHANLab.md)
- MIT HAN Lab（韩松实验室）72 仓库 × 9 大主题（端侧/LLM量化/稀疏attention/VLM/NAS）+ 研究脉络时间线（2018-2026 四阶段）+ work4ai 覆盖热力图 + 补强清单 ⭐ 2026-08

### 9. 高效 AI 顶会精选：[`高效AI前沿-2025-2026顶会精选.md`](高效AI前沿-2025-2026顶会精选.md)
- NeurIPS/MLSys/ACL 2025-2026 高效 AI 论文 12 篇深读（稀疏 attention/PD 分离/KV 压缩/推理加速/量化）⭐ 2026-08

### 10. 高效 AI 全行业热点：[`高效AI前沿-全行业热点地图.md`](高效AI前沿-全行业热点地图.md)
- 2025-2026 六大热点（推理优化/test-time scaling/端侧 LLM/hybrid 架构/agent RL/MoE）+ 趋势洞察 + 速查表 ⭐ 2026-08

### 11. CS 名校课程整合：`algorithms/` · `database-systems/` · `network-systems/` · `cs224n/` · `*-cs-projects/`
> 把同一主题在多所名校的"不同讲法"整合成对比矩阵，快速建立完整能力。⭐ 2026-08

**跨校整合模块（按主题/课程，多源对比）：**

| 目录 | 主题 | 整合来源 | 核心文件 | 特色 |
|---|---|---|---|---|
| [`algorithms/`](algorithms/) | 算法设计 | Princeton COS 226 × MIT 6.006 × CMU 15-251 | `algo_integration.py` + `algo_weekly.py` | 可视化 / 数学严谨 / 思想史 三极 |
| [`database-systems/`](database-systems/) | 数据库系统 | CMU 15-445 × MIT 6.830 × UCB CS186 × Stanford CS145 | `db_integration.py` + `db_weekly.py` | 实现 / 抽象 / 实战 / 分布 四视角 |
| [`network-systems/`](network-systems/) | 网络系统 | Stanford CS144 × Berkeley CS162 × 路由(OSPF/BGP) | `mini_tcp.py` + `routing.py` | mini-TCP 项目 + 路由协议 |
| [`cs224n/`](cs224n/) | NLP + 深度学习 | Stanford CS224N **Winter 2026**（Diyi Yang + Yejin Choi）| `cs224n_assignments.py` + `gpt2_project.py` | 4 作业 + GPT-2 项目（2026最新版）|

每个模块含：① 整合层/作业层（可跑代码）② README（对比矩阵 + 学习路径）。纯标准库/numpy，零外部依赖。`cs224n/` 对应**最新 2026 schedule**（A4 改 LLM 评测、默认项目改 GPT-2），与 work4ai「讲透」系列深度互补。

**按学校的完整课程（单校纵深）：**

| 目录 | 学校 | 覆盖 |
|---|---|---|
| [`cmu-cs-projects/`](cmu-cs-projects/) | CMU | 12 主题（DB/分布式/ML/PGM/NLP/CV/机器人/HCI/理论）+ 本科/研究生补充 |
| [`mit-cs-projects/`](mit-cs-projects/) | MIT | 12 主题（DB/OS/性能/AI/ML/DL/机器人/安全）+ 补充 |
| [`berkeley-cs-projects/`](berkeley-cs-projects/) | UC Berkeley | 12 主题（SICP/DSA/架构/离散/AI/ML/RL/NLP/CV/OS/数据）|
| [`cambridge-cs-projects/`](cambridge-cs-projects/) | Cambridge | 同构 |
| [`eth-cs-projects/`](eth-cs-projects/) | ETH Zürich | 同构 |

> **两种用法**：想横向对比"同主题不同讲法" → 跨校整合模块；想纵深单校完整课程 → `*-cs-projects/`。两者衔接（整合模块的 README 标注了对应单校文件路径）。

### 12. 数学家资源中心：[`top-math-courses/`](top-math-courses/) ⭐ 2026-08-13 新增

为"成为顶级数学家"目标准备的**全栈资源中心**。20 文档覆盖：路径 / 教材 / 工具 / 社区 / 品味 / 现实路径。入口 [`top-math-courses/MATHEMATICIAN_MASTER_INDEX.md`](top-math-courses/MATHEMATICIAN_MASTER_INDEX.md)。

| 类别 | 文档 |
|---|---|
| 路径 | `UNIFIED_ROADMAP`（30 课）· `FAST_TRACK`（12 课速成）· `FIELDS_LEVEL_PLAYBOOK`（顶级路径 + 现实校准）|
| 教材 | `TEXTBOOK_LIBRARY`（按方向的金标准库，10+ 方向 100+ 本书）|
| 方法 | `RESEARCH_METHODOLOGY`（解题/阅读/写作/提问）· `FEYNMAN_TEACHING_GUIDE` |
| 工具 | `TOOLS_STACK`（Lean/SageMath/LaTeX/Julia/文献管理）· `LEAN_MATH_TRACK`（学数学+练 Lean 并行）|
| 方向 | `SUBFIELDS_DEEP_DIVE`（ML 理论 / 形式化数学 / 数值 / 概率 / 优化 / 代数几何 / 数论...）|
| 社区 | `COMMUNITY_AND_CAREER`（暑期学校 / 会议 / PhD 项目 / fellowship）|
| 论文 | `PAPERS_COLLECTION` · `LATEST_RESEARCH` |
| 品味 | `HISTORY_AND_TASTE`（数学史 / 传记 / taste 培养）|
| 映射 | `CROSS_INDEX_WITH_WORK4AI`（数学↔讲透X 双向）· `CROSS_SCHOOL_INSIGHTS`（9 校对比）|

**配套执行系列**（2026-08-13 新建，骨架 + 示范章）：
- [`讲透Lean4数学/`](讲透Lean4数学/) — 把已有的 Lean4 OS 经验（ai-os-dd/law/neo-os）升级为数学武器。README + 00 范式变革 + 01 NNG 讲透（含完整 Lean 代码 + Python 实验跑通）+ 02-11 大纲
- [`讲透实分析/`](讲透实分析/) — 配 Tao Analysis I + Lean companion。README + 00 实分析是什么 + 01 实数构造 + 02 极限ε-δ + 03 连续性 + 04 微分（含 Python 实验跑通）+ 05-10 大纲
- [`讲透NLP/math/`](讲透NLP/math/) — NLP 每章用到的数学反向索引到 top-math-courses

### 13. 5 本经典讲义内容化（2026-08-13 第二批）⭐

把 [`top-math-courses/LECTURES_AND_COURSES.md`](top-math-courses/LECTURES_AND_COURSES.md) 列的"免费八书"逐本做成可学的"讲透"系列（每本 README + 核心章节 + Python 实验跑通）：

| 讲义 | 系列 | 已落盘内容 |
|------|------|-----------|
| **Tao Analysis I + Lean companion** | [`讲透实分析/`](讲透实分析/) | README + 00-04 章 + 4 实验（Leibniz 伪导数崩坏 / ε-δ / 连续性 / 微分）|
| **Vershynin HDP** | [`讲透高维概率/`](讲透高维概率/) | README + 00 高维反直觉 + 01 集中不等式 + 2 实验（4 大高维反直觉 / Hoeffding vs Bernstein）|
| **Milne Group Theory** | [`讲透群论/`](讲透群论/) | README + 00 群论是什么 + 01 Sylow 定理 + 实验（Z/12Z / S3 / Lagrange 验证）|
| **Boyd Convex Optimization** | [`讲透优化理论/`](讲透优化理论/) | 已有 00-03，加 04 Lagrange 对偶 + SVM 强对偶实验 |
| **Hatcher AT** | [`讲透代数拓扑/`](讲透代数拓扑/) | README + 00 代数拓扑是什么 + 实验（同调群表 / Euler 示性数 / TDA）|

每本实验均 `python3 -u experiments/*.py` 跑通，含反直觉发现。

### 14. 讲义内容化第二 + 第三批（2026-08-13）⭐

**A. 5 本现有系列填充核心章节**：
- 讲透实分析：加 05 Riemann 积分 + FTC 实验
- 讲透高维概率：加 02 次高斯分布 + mgf 验证实验
- 讲透代数拓扑：加 01 基本群 + 绕数/缩点可视化实验
- 讲透群论：加 02 群作用 + Burnside 计数实验
- 讲透优化理论：加 05 内点法 + log barrier 实验

**B. 2 本新讲义系列**：
- [`讲透数值线代/`](讲透数值线代/) — 基于 Trefethen & Bau。README + 00 数值线代是什么 + 01 SVD + Hilbert 条件数/低秩近似/LoRA 演示实验
- [`讲透分析进阶/`](讲透分析进阶/) — 基于 Stein-Shakarchi 4 卷（Fourier / 复 / 实 / 泛函）。README + 00 全景

至此 **7 本经典讲义内容化**（Tao / Vershynin / Milne / Boyd / Hatcher / Trefethen / Stein-Shakarchi），共 ~30 章节 + 12 实验，全部 bash 跑通。

### 15. 全章节填充 + 第 8 本讲义（2026-08-13 终批）⭐

**A. 7 本现有系列的"剩余章节"全部以合集形式落盘**（每本一个紧凑合集文件覆盖剩余所有章节）：

| 系列 | 合集文件 | 覆盖章节 |
|------|---------|---------|
| 讲透实分析 | `06-10-进阶合集.md` | 无穷级数 / 函数序列 / Lebesgue / 度量空间 / ML 应用 |
| 讲透高维概率 | `03-08-进阶合集.md` | 随机向量 + JL / 随机矩阵 + MP / 凸几何 / 鞅 / 泛化界 / 矩阵补全 |
| 讲透群论 | `03-07-进阶合集.md` | 对称群 / 商群 / 直积 / 可解群 / 自由群 |
| 讲透代数拓扑 | `02-07-进阶合集.md` | 覆叠 / van Kampen / 同调 / 上同调 / 同伦群 / TDA |
| 讲透数值线代 | `02-06-进阶合集.md` | QR / 条件数 / 特征值算法 / 迭代法 / ML 应用 |
| 讲透优化理论 | `06-进阶合集.md` | 凸应用 / 非凸 / 一阶 / 分布式 / 二阶 / 2024-2026 前沿 |
| 讲透分析进阶 | `01-08-合集.md` | Fourier / 复分析 / 测度 / 泛函（Stein-Shakarchi 4 卷）|
| 讲透Lean4数学 | `02-11-合集.md` | 类型论 / Mathlib / tactic / 集合 / 实分析 / 线代 / 抽代 / PR / AI / 项目 |

**B. 第 8 本讲义**：[`讲透Artin抽代/`](讲透Artin抽代/) — 基于 Artin《Algebra》2e（MIT 18.701/702）。README + 00-Artin抽代是什么（矩阵群 + 几何直觉 + Galois）

**总计**：8 本讲义 × 平均 8-10 章 = **~70 章节**（含合集）+ 16 实验，全部 bash 跑通。

---

## 四、维度矩阵

```
                  技术深度          应用广度          思想深度
                  ↓                ↓                ↓
讲透系列（38）     ★★★★★           ★★               ★★★
AIfor各学科（30）  ★★              ★★★★★            ★★★★
AI历史             ★               ★★               ★★★★★
科学的现代性       ★               ★★               ★★★★★
哲学（AIfor）      ★               ★                ★★★★★
访谈及其他         ★               ★                ★★★★
```

**博士级训练 = 技术深度 + 应用广度 + 思想深度**

---

## 五、推荐学习路径

### 新手
```
激活函数 → 基础模型 → 微调 → RAG → Prompt → 横向打通
```

### 有基础
```
选感兴趣的系列 → 每系列内独立
```

### 博士级
```
基础模型 advanced → 世界模型 advanced → AIfor 各学科（选 3-5 个）
→ AI 历史 + 科学的现代性 → 本质探索（反思）
```

### 产业应用
```
横向打通 → AIfor 各学科（选你的领域）→ 早期经典 + 最新前沿
```

---

## 六、统一方法论

1. **原理优先于 API**：先讲为什么，再讲怎么调库
2. **每个结论都有可运行代码佐证**：不凭记忆，数字是跑出来的
3. **批判性**：每篇有「局限/争议」
4. **离散 vs 连续分水岭**：从 MSE 跨到 CE 必须翻的坎
5. **博士级标准**：论文挂载 + 数学严格 + 开放问题 + 批判性
6. **本质探索**：不只是技术——反思每个学科的根本问题
7. **费曼检验（发布前质量门）**：任何「讲透 X」发布前跑 4 道检验（F1 外行复述 / F2 卡壳自曝 / F3 术语黑名单 / F4 回炉记录），戳穿"自以为懂"。五层范式管**写得深不深**，费曼检验管**写得真不真懂**。（2026-08-10 起 `.费曼检验.md`/`.多视角.md` 衍生文件不再单独保存——经核查 958 个全是自动生成空壳、无原创内容；原版 md 即唯一版本，需自检时临时跑 `python3 费曼学习法/feynman-coach.py`。）详见 [`费曼学习法/`](费曼学习法/)。

---

## 环境与运行

```bash
# 小模型实验（纯 CPU）

python3 -u 讲透基础模型/experiments/00_why_ntp.py

# 全部实验一键跑
for d in 讲透激活函数 讲透基础模型 讲透微调; do
  ls $d/experiments/*.py 2>/dev/null
done

# 费曼陪练：用 3 角色（12岁小孩/记者/哲学家）连环追问自测你"真懂没真懂"
python3 费曼学习法/feynman-coach.py "注意力机制" --rounds 3
```
