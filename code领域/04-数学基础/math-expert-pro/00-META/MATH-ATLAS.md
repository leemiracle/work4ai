# MATH-ATLAS：数学知识完整图谱

> **项目导航的核心枢纽。** 以"基础→抽象→分支→前沿→应用"为主线，覆盖现代数学全部 20 大类、数百子领域。
> 每个知识点标注：✅已有代码 / 📄已有文档 / 📄待补
>
> 本文件基于 MSC（数学主题分类）+ 用户提供的 Master Roadmap。

---

## 认知框架：数学的 8 条主线

| 研究对象 | 对应学科 | 核心问题 | 项目位置 |
|---------|---------|---------|---------|
| **数（Number）** | 数论、代数 | 数有哪些结构和性质？ | [07数论](#七数论) / [03代数](#三代数学) |
| **形（Shape）** | 几何、拓扑 | 空间如何描述和分类？ | [05几何](#五几何学) / [06拓扑](#六拓扑学) |
| **变（Change）** | 分析、动力系统 | 连续变化如何刻画？ | [04分析](#四分析学) / [12动力系统](#十二动力系统) |
| **结构（Structure）** | 抽象代数、范畴论 | 对象间的共同规律？ | [03代数](#三代数学) / [16-foundations/范畴论](../16-foundations/范畴论/) |
| **不确定性** | 概率、统计 | 随机如何建模推断？ | [09概率统计](#九概率统计) |
| **最优（Optim）** | 优化理论 | 约束下最佳方案？ | [11优化](#十一优化理论) |
| **计算（Compute）** | 计算数学、离散 | 如何高效求解？ | [10计算数学](#十计算数学) / [08离散](#八离散数学) |
| **推理（Reason）** | 逻辑、形式化 | 什么是正确证明？ | [02逻辑](#二逻辑与数学基础) / [19形式化](#十九形式化数学) |

---

## 一、数学基础（Foundation）

| 知识点 | 状态 | 项目位置 |
|--------|------|---------|
| 自然数 N → 整数 Z → 有理数 Q → 实数 R → 复数 C | 📄 | [04-concepts/](../04-concepts/) |
| 四元数 H / 八元数 O / p进数 / 超实数 | 📄 | 待补 |
| 集合论（ZFC/选择公理/连续统假设/大基数）| 📄 | [16-foundations/集合论/](../16-foundations/集合论/) ✅2文件 |
| 数系发展（N→Z→Q→R→C→H→O→p进→超实）| 📄 | 待补 |

## 二、逻辑与数学基础（Foundations）

| 知识点 | 状态 | 项目位置 |
|--------|------|---------|
| 命题逻辑（真值表/德摩根律）| 📄 | [16-foundations/基础争议/](../16-foundations/基础争议/) |
| 一阶逻辑（∀∃/模型/证明）| 📄 | [16-foundations/类型论/](../16-foundations/类型论/) |
| 高阶逻辑（Lambda/类型论/依赖类型）| 📄 | [16-foundations/类型论/02-Martin-Löf](../16-foundations/类型论/02-Martin-Löf依赖类型论.md) |
| 元数学（一致性/完备性/哥德尔定理）| 📄 | [07-critique/](../07-critique/) |
| 范畴论（函子/自然变换/伴随/Topos）| 📄 | [16-foundations/范畴论/](../16-foundations/范畴论/) ✅2文件 |
| Curry-Howard 同构 | 📄 | [16-foundations/Curry-Howard/](../16-foundations/Curry-Howard/) ✅2文件 |
| HoTT（同伦类型论）| 📄 | [16-foundations/类型论/02-Martin-Löf](../16-foundations/类型论/02-Martin-Löf依赖类型论.md) |

## 三、代数学（Algebra）

| 知识点 | 状态 | 项目位置 |
|--------|------|---------|
| 初等代数（多项式/因式/方程/不等式）| 📄 | [01-track/stage-1](../01-track/stage-1-本科核心/) |
| 线性代数：向量空间/基/维 | ✅ | [代码库 01-PCA](../15-applications/代码库/01-PCA特征值_人脸压缩.py) |
| 线性代数：矩阵运算/LU/QR/SVD/Jordan | ✅ | [代码库 03-SVD](../15-applications/代码库/03-SVD_推荐系统.py) / [19-QR](../15-applications/代码库/19-数值线性代数_最小二乘.py) |
| 线性代数：特征值/谱理论 | ✅ | [代码库 31-谱理论](../15-applications/代码库/31-矩阵谱理论.py) |
| 线性代数：张量/张量积/张量秩 | 📄 | 待补 |
| 群论（群/子群/正规子群/同态/置换/对称）| ✅ | [代码库 22-群论](../15-applications/代码库/22-群论_对称与表示.py) |
| 环论（环/理想/商环）| 📄 | 待补 |
| 域论（域/扩张/Galois理论）| 📄 | [16-foundations/统一视角/02-Galois](../16-foundations/统一视角/02-Galois理论与对偶实例.md) |
| 模论/表示论 | 📄 | 待补 |
| 李群/李代数 | 📄 | 待补 |
| 交换代数 | 📄 | 待补 |

## 四、分析学（Analysis）

| 知识点 | 状态 | 项目位置 |
|--------|------|---------|
| 微积分（极限/连续/导数/积分）| ✅ | [代码库 06-梯度下降](../15-applications/代码库/06-梯度下降_线性回归从零实现.py) |
| 实分析（Lebesgue测度/积分）| 📄 | 待补 |
| Banach空间/Hilbert空间 | 📄 | 待补 |
| 复分析（全纯/留数/柯西/Laurent/共形）| ✅ | [代码库 16-复分析](../15-applications/代码库/16-复分析_解析函数与留数.py) |
| 泛函分析（算子/谱/算子代数）| 📄 | 待补 |
| 调和分析（Fourier/Wavelet/FFT）| ✅ | [代码库 04-FFT](../15-applications/代码库/04-傅里叶变换_音频频谱.py) / [28-小波](../15-applications/代码库/28-小波变换_多分辨率分析.py) |
| PDE（Laplace/Heat/Wave/NS/Schr/Maxwell）| ✅ | [代码库 14-PDE](../15-applications/代码库/14-偏微分方程_热传导与波动.py) |
| 变分法（Euler-Lagrange/最小作用量）| ✅ | [代码库 23-变分法](../15-applications/代码库/23-变分法_最优控制.py) |

## 五、几何学（Geometry）

| 知识点 | 状态 | 项目位置 |
|--------|------|---------|
| 欧氏几何/解析几何 | 📄 | [01-track/stage-1](../01-track/stage-1-本科核心/) |
| 射影几何 | 📄 | 待补 |
| 微分几何（曲率/测地线/Gauss定理）| ✅ | [代码库 21-微分几何](../15-applications/代码库/21-微分几何_曲线与曲面.py) |
| 黎曼几何（度量/Riemann张量/Ricci流）| 📄 | 待补 |
| 辛几何 | 📄 | 待补 |
| 代数几何（概形/层/模空间）| 📄 | 待补 |
| 计算几何/离散几何/凸几何 | 📄 | 待补 |
| 分形几何（Mandelbrot/Julia/IFS/盒维数）| ✅ | [代码库 15-分形](../15-applications/代码库/15-分形几何_Mandelbrot集.py) |

## 六、拓扑学（Topology）

| 知识点 | 状态 | 项目位置 |
|--------|------|---------|
| 点集拓扑（开集/紧致/连通/分离公理）| 📄 | [01-track/stage-1](../01-track/stage-1-本科核心/) |
| 代数拓扑（同调/同伦/基本群）| 📄 | [05-history/](../05-history/) / [02-lens-mathematicians/](../02-lens-mathematicians/) |
| 微分拓扑（流形/横截/Morse理论）| 📄 | 待补 |
| 低维拓扑（3-流形/4-流形/纽结）| 📄 | 待补 |
| 纤维丛/特征类 | 📄 | 待补 |
| TDA（持续同调/Betti数/barcode）| ✅ | [代码库 20-TDA](../15-applications/代码库/20-TDA_拓扑数据分析.py) |

## 七、数论（Number Theory）

| 知识点 | 状态 | 项目位置 |
|--------|------|---------|
| 初等数论（素数/同余/丢番图）| ✅ | [代码库 09-RSA](../15-applications/代码库/09-数论_RSA加密.py) |
| 解析数论（素数定理/Riemann ζ/L函数）| 📄 | [14-frontier/conjecture进展/](../14-frontier/conjecture进展/) |
| 代数数论（理想/类域论/local fields）| 📄 | 待补 |
| 几何数论 | 📄 | 待补 |
| 椭圆曲线 | 📄 | [15-applications/密码学/](../15-applications/密码学与信息安全/) |
| 模形式/L函数 | 📄 | [14-frontier/conjecture进展/](../14-frontier/conjecture进展/) |
| Langlands纲领 | 📄 | [14-frontier/热点方向追踪/](../14-frontier/热点方向追踪/) |

## 八、离散数学（Discrete Mathematics）

| 知识点 | 状态 | 项目位置 |
|--------|------|---------|
| 组合数学（计数/生成函数/容斥）| 📄 | [14-frontier/热点方向追踪/](../14-frontier/热点方向追踪/) #2加性组合 |
| 图论（最短路/匹配/着色/网络流）| ✅ | [代码库 08-图论](../15-applications/代码库/08-图论_最短路算法.py) |
| 复杂网络（小世界/无标度/社区）| ✅ | [代码库 30-网络科学](../15-applications/代码库/30-网络科学_复杂网络.py) |
| 布尔代数 | 📄 | 待补 |
| 自动机/形式语言 | 📄 | [15-applications/CS/](../15-applications/计算机科学/) |
| 编码理论（Hamming/RS/LDPC/Polar）| ✅ | [代码库 27-编码](../15-applications/代码库/27-编码理论_纠错码.py) |
| 密码学（RSA/ECC/PQC/ZKP）| ✅ | [代码库 09-RSA](../15-applications/代码库/09-数论_RSA加密.py) + [15-applications/密码学/](../15-applications/密码学与信息安全/) ✅2文件 |
| 计算复杂性（P/NP/BPP/PSPACE）| 📄 | [15-applications/CS/02-复杂度](../15-applications/计算机科学/02-算法复杂度理论.md) |

## 九、概率统计（Probability & Statistics）

| 知识点 | 状态 | 项目位置 |
|--------|------|---------|
| 概率论（公理/分布/大数律/CLT）| ✅ | [代码库 05-蒙特卡洛](../15-applications/代码库/05-蒙特卡洛_期权定价.py) |
| 随机过程（泊松/排队/Little定律）| ✅ | [代码库 17-排队](../15-applications/代码库/17-随机过程_泊松与排队论.py) |
| 布朗运动/SDE/Itô微积分 | ✅ | [代码库 26-SDE](../15-applications/代码库/26-随机微分方程_SDE.py) |
| 马尔可夫链（PageRank/平稳分布）| ✅ | [代码库 02-PageRank](../15-applications/代码库/02-马尔可夫链_PageRank.py) |
| 贝叶斯统计（MCMC/Metropolis）| ✅ | [代码库 10-贝叶斯](../15-applications/代码库/10-概率_贝叶斯推断.py) |
| 经典统计（假设检验/p值/功效）| ✅ | [代码库 25-检验](../15-applications/代码库/25-统计假设检验.py) |
| 时间序列（ARIMA/GARCH）| 📄 | 待补 |
| 高维统计（Lasso/高维检验）| ✅ | [代码库 29-压缩感知](../15-applications/代码库/29-压缩感知_稀疏恢复.py) |
| 因果推断（DO演算/反事实）| 📄 | 待补 |
| 随机矩阵理论（半圆律/Tracy-Widom）| ✅ | [代码库 34-RMT](../15-applications/代码库/34-随机矩阵理论.py) |

## 十、计算数学（Computational Mathematics）

| 知识点 | 状态 | 项目位置 |
|--------|------|---------|
| 数值线性代数（QR/SVD/迭代法）| ✅ | [代码库 19-最小二乘](../15-applications/代码库/19-数值线性代数_最小二乘.py) |
| 数值积分（梯形/Simpson/Gauss/MC）| ✅ | [代码库 24-数值积分](../15-applications/代码库/24-数值积分_求积公式.py) |
| ODE数值解（Euler/RK4/刚性）| ✅ | [代码库 11-ODE](../15-applications/代码库/11-数值分析_微分方程求解.py) |
| 有限元/有限差分 | ✅ | [代码库 14-PDE](../15-applications/代码库/14-偏微分方程_热传导与波动.py) |
| 谱方法 | 📄 | 待补 |
| 压缩感知（OMP/L1/RIP）| ✅ | [代码库 29-压缩感知](../15-applications/代码库/29-压缩感知_稀疏恢复.py) |

## 十一、优化理论（Optimization）

| 知识点 | 状态 | 项目位置 |
|--------|------|---------|
| 梯度下降（BGD/SGD/MBGD）| ✅ | [代码库 06-梯度下降](../15-applications/代码库/06-梯度下降_线性回归从零实现.py) |
| 凸优化（SVM/对偶/KKT）| ✅ | [代码库 13-SVM](../15-applications/代码库/13-凸优化_SVM对偶.py) |
| 凸共轭（Fenchel/Moreau/proximal）| ✅ | [代码库 32-凸共轭](../15-applications/代码库/32-凸共轭.py) |
| 变分法（Euler-Lagrange/最小作用量）| ✅ | [代码库 23-变分法](../15-applications/代码库/23-变分法_最优控制.py) |
| 线性规划/整数规划 | 📄 | 待补 |
| 非凸优化 | 📄 | 待补 |
| 在线优化 | 📄 | 待补 |
| 鲁棒优化 | 📄 | 待补 |

## 十二、动力系统（Dynamical Systems）

| 知识点 | 状态 | 项目位置 |
|--------|------|---------|
| 连续动力系统（洛伦兹/吸引子）| ✅ | [代码库 12-混沌](../15-applications/代码库/12-动力系统_混沌吸引子.py) |
| 离散动力系统（Logistic映射/分岔）| ✅ | [代码库 12-混沌](../15-applications/代码库/12-动力系统_混沌吸引子.py) |
| 混沌理论（蝴蝶效应/Lyapunov）| ✅ | [代码库 12-混沌](../15-applications/代码库/12-动力系统_混沌吸引子.py) |
| 分岔理论 | ✅ | [代码库 12-混沌](../15-applications/代码库/12-动力系统_混沌吸引子.py) |
| 博弈论（Nash/ESS/复制器动力学）| ✅ | [代码库 18-博弈论](../15-applications/代码库/18-博弈论_纳什均衡.py) |

## 十三、控制理论（Control Theory）

| 知识点 | 状态 | 项目位置 |
|--------|------|---------|
| 经典控制（PID/根轨迹/频域）| ✅ | [代码库 35-控制论](../15-applications/代码库/35-控制论.py) |
| 现代控制（状态空间/可控性）| ✅ | [代码库 35-控制论](../15-applications/代码库/35-控制论.py) |
| 最优控制（LQR/Riccati）| ✅ | [代码库 35-控制论](../15-applications/代码库/35-控制论.py) |
| Lyapunov稳定性 | ✅ | [代码库 35-控制论](../15-applications/代码库/35-控制论.py) |
| 机器人（运动学/SLAM/规划）| 📄 | [15-applications/机器人/](../15-applications/机器人与自动化/) ✅2文件 |

## 十四、信息论（Information Theory）

| 知识点 | 状态 | 项目位置 |
|--------|------|---------|
| 熵/交叉熵/KL散度 | ✅ | [代码库 07-信息论](../15-applications/代码库/07-信息论_熵与编码.py) |
| 霍夫曼编码/信源编码定理 | ✅ | [代码库 07-信息论](../15-applications/代码库/07-信息论_熵与编码.py) |
| Shannon信道容量 | ✅ | [代码库 27-编码](../15-applications/代码库/27-编码理论_纠错码.py) |
| Kolmogorov复杂度/算法信息论 | 📄 | 待补 |

## 十五、数学物理（Mathematical Physics）

| 知识点 | 状态 | 项目位置 |
|--------|------|---------|
| 量子力学数学（Hilbert/酉/厄米）| 📄 | [15-applications/物理工程/02-量子力学](../15-applications/物理与工程/02-量子力学数学.md) |
| 广义相对论（微分几何/弯曲时空）| 📄 | [代码库 21-微分几何](../15-applications/代码库/21-微分几何_曲线与曲面.py) |
| 场论（Yang-Mills/规范理论）| 📄 | [14-frontier/conjecture进展/](../14-frontier/conjecture进展/) #4 Yang-Mills |
| 统计物理 | 📄 | 待补 |
| 弦理论数学 | 📄 | 待补 |

## 十六、机器学习数学（ML Mathematics）

| 知识点 | 状态 | 项目位置 |
|--------|------|---------|
| 线代/微积分/概率基础 | ✅ | [代码库 01/04/05/06](../15-applications/代码库/) |
| 损失函数理论/梯度流 | ✅ | [代码库 06-梯度下降](../15-applications/代码库/06-梯度下降_线性回归从零实现.py) |
| 核方法（RKHS/Mercer）| ✅ | [代码库 13-SVM](../15-applications/代码库/13-凸优化_SVM对偶.py) |
| PAC学习/VC维/Rademacher | 📄 | [15-applications/AI-ML/02-深度学习理论](../15-applications/AI-ML/02-深度学习理论.md) |
| 最优传输 | 📄 | 待补 |
| 扩散过程/Diffusion Models | ✅ | [代码库 26-SDE](../15-applications/代码库/26-随机微分方程_SDE.py) |
| 深度学习理论（双下降/NTK）| 📄 | [15-applications/AI-ML/02-深度学习理论](../15-applications/AI-ML/02-深度学习理论.md) |

## 十七、金融数学（Financial Mathematics）

| 知识点 | 状态 | 项目位置 |
|--------|------|---------|
| Black-Scholes/期权定价 | ✅ | [代码库 05-期权](../15-applications/代码库/05-蒙特卡洛_期权定价.py) |
| 蒙特卡洛方法 | ✅ | [代码库 05-期权](../15-applications/代码库/05-蒙特卡洛_期权定价.py) |
| 随机微积分/Itô引理 | ✅ | [代码库 26-SDE](../15-applications/代码库/26-随机微分方程_SDE.py) |
| 投资组合/风险管理 | 📄 | [15-applications/金融量化/](../15-applications/金融量化/) ✅2文件 |

## 十八、形式化数学（Formal Math）

| 知识点 | 状态 | 项目位置 |
|--------|------|---------|
| Lean 4 / mathlib | 📄 | [14-frontier/AI-for-Math/02-Lean入门](../14-frontier/AI-for-Math/02-Lean形式化数学入门.md) |
| AlphaProof / AI证明 | 📄 | [14-frontier/AI-for-Math/01](../14-frontier/AI-for-Math/01-AI正在重写数学研究.md) |
| Tao 的 AI 实践 | 📄 | [14-frontier/AI-for-Math/03-Tao](../14-frontier/AI-for-Math/03-Tao的AI数学实践.md) |
| HoTT / 同伦类型论 | 📄 | [16-foundations/类型论/02](../16-foundations/类型论/02-Martin-Löf依赖类型论.md) |
| Coq/Agda/Isabelle | 📄 | [14-frontier/AI-for-Math/02-Lean入门](../14-frontier/AI-for-Math/02-Lean形式化数学入门.md) |

## 十九、现代前沿数学（Frontier）

| 知识点 | 状态 | 项目位置 |
|--------|------|---------|
| Langlands纲领 | 📄 | [14-frontier/conjecture进展/](../14-frontier/conjecture进展/) |
| 千禧问题（RH/PvsNP/NS/...）| 📄 | [14-frontier/conjecture进展/千禧](../14-frontier/conjecture进展/千禧问题与大猜想进展表.md) |
| 随机矩阵/自由概率 | ✅ | [代码库 34-RMT](../15-applications/代码库/34-随机矩阵理论.py) |
| 压缩感知 | ✅ | [代码库 29-压缩感知](../15-applications/代码库/29-压缩感知_稀疏恢复.py) |
| TDA（拓扑数据分析）| ✅ | [代码库 20-TDA](../15-applications/代码库/20-TDA_拓扑数据分析.py) |
| AI for Mathematics | 📄 | [14-frontier/AI-for-Math/](../14-frontier/AI-for-Math/) ✅3文件 |
| 2026 最新突破 | 📄 | [14-frontier/热点方向追踪/2026突破](../14-frontier/热点方向追踪/2026年最新数学突破.md) |
| 镜像对称/非交换几何/热带几何 | 📄 | 待补 |

## 二十、应用领域（Applications）

| 领域 | 状态 | 项目位置 |
|------|------|---------|
| AI/ML | ✅ | [15-applications/AI-ML/](../15-applications/AI-ML/) ✅2文件 |
| 计算机科学 | ✅ | [15-applications/计算机科学/](../15-applications/计算机科学/) ✅2文件 |
| 物理与工程 | ✅ | [15-applications/物理与工程/](../15-applications/物理与工程/) ✅2文件 |
| 金融量化 | ✅ | [15-applications/金融量化/](../15-applications/金融量化/) ✅2文件 |
| 生命科学 | ✅ | [15-applications/生命科学/](../15-applications/生命科学/) ✅2文件 |
| 跨学科 | ✅ | [15-applications/跨学科/](../15-applications/跨学科/) ✅2文件 |
| 密码学/信息安全 | ✅ | [15-applications/密码学与信息安全/](../15-applications/密码学与信息安全/) ✅2文件 |
| 量子计算 | ✅ | [15-applications/量子计算/](../15-applications/量子计算/) ✅2文件 |
| 机器人/自动化 | ✅ | [15-applications/机器人与自动化/](../15-applications/机器人与自动化/) ✅2文件 |
| 气候/环境 | ✅ | [15-applications/气候与环境/](../15-applications/气候与环境/) ✅2文件 |
| 区块链/分布式 | ✅ | [15-applications/区块链与分布式/](../15-applications/区块链与分布式/) ✅2文件 |

---

## 📊 覆盖统计

| 状态 | 含义 | 数量 | 占比 |
|------|------|------|------|
| ✅ | 有可运行代码案例 | ~80+ 知识点 | ~45% |
| 📄 | 有文档/指南 | ~60+ 知识点 | ~35% |
| 📄 | 待补 | ~35 知识点 | ~20% |
| **总计** | — | **~175 知识点** | 100% |

> 💡 **使用方式**：按你的学习阶段，在表中找到目标知识点 → 点击链接 → 学习对应文件/代码 → 跑代码验证 → 回来标记掌握。

## 🔗 配套导航
- 一站式入口 → [MASTER-INDEX](MASTER-INDEX.md)
- 新手入口 → [START_HERE](START_HERE.md)
- 学习路径 → [ROADMAP](ROADMAP.md)
- 概念索引 → [CONCEPT-INDEX](CONCEPT-INDEX.md)

---

> ⏱️ **维护**：每新增一个案例或文档，更新本图谱的对应行。每年 ICM 后整体刷新前沿部分。
