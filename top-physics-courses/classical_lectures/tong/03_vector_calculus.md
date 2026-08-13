# David Tong · Vector Calculus（矢量微积分）导读笔记

> Tong 系列第 03 本 | 难度 ★（数学工具）| 配合：L02 电磁学 + L06 数学方法

## §0 基本信息
- **作者**：David Tong（Cambridge）
- **定位**：一年级本科数学方法课
- **难度**：★（入门工具课，只需会偏导数）
- **篇幅**：约 35 页（最薄的 Tong 讲义之一）
- **链接**：davidtong.org/teaching/vector-calculus/
- **配合项目**：L02 电磁学 + L06 数学方法

## §1 一句话定位
**电磁学和流体力学的数学地基**——梯度、散度、旋度，三个算子统治连续介质物理。

## §2 前置知识
- 必须会：偏导数、多重积分、基本矢量运算（点积/叉积）
- 建议会：曲线坐标的基本概念、线性代数基本概念

## §3 讲义全景（章节地图）

短小精悍，专注三个微分算子 + 两个积分定理。虽然薄，但**每一个后续物理课都依赖它**。

| 章 | 主题 | 核心问题 |
|----|------|---------|
| 1 | 梯度 ∇f | 标量场怎么变？哪个方向变化最快？|
| 2 | 散度 ∇·F | 矢量场在某点是"源"还是"汇"？|
| 3 | 旋度 ∇×F | 矢量场在某点附近怎么转？|
| 4 | 散度定理（Gauss） | 体积分 ↔ 面积分 |
| 5 | Stokes 定理 | 面积分 ↔ 线积分 |
| 6 | 曲线坐标 | 球坐标/柱坐标怎么算？|
| 7 | Dirac δ 函数 | 点源的数学描述 |
| 8 | 有用的恒等式 | ∇²、∇×(∇f)=0 等 |

## §4 核心章节拆解（深化版）

### §4.1 梯度（∇）——标量场的"上坡方向"

**核心概念**：标量场 $f(x,y,z)$ 的梯度是一个矢量，指向增长最快的方向，大小等于该方向的斜率。

**关键公式**：
$$\nabla f = \left(\frac{\partial f}{\partial x},\; \frac{\partial f}{\partial y},\; \frac{\partial f}{\partial z}\right)$$

**方向导数推导**：沿单位方向 $\hat{n}$ 的变化率，记作 $D_{\hat{n}}f$。由链式法则，$f(\mathbf{r} + s\hat{n})$ 对小位移 $s$ 展开：
$$D_{\hat{n}}f = \frac{df}{ds}\bigg|_{s=0} = \nabla f \cdot \hat{n}$$
当 $\hat{n} = \nabla f / |\nabla f|$（与梯度同向）时取最大值 $|\nabla f|$；当 $\hat{n} \perp \nabla f$ 时方向导数为零——这就是"梯度指向增长最快方向"的来源。

**梯度 ⊥ 等值面**：等值面 $f(\mathbf{r}) = c$ 是一个曲面。沿该曲面移动时 $f$ 不变，故 $D_{\hat{n}}f = 0$（$\hat{n}$ 在曲面切平面内）→ $\nabla f \cdot \hat{n} = 0$ → **$\nabla f$ 垂直于等值面**。温度场的等温面、电势的等势面都与各自的梯度（热流方向、电场方向）正交。

**物理实例（不止温度）**：
- **温度场** $T(\mathbf{r})$：热流 $\mathbf{q} = -k\nabla T$（Fourier 定律，热从高温流向低温）
- **引力势** $\Phi(\mathbf{r}) = -GM/r$：引力 $\mathbf{F} = -m\nabla\Phi$（势的负梯度给出力）
- **电势** $\phi(\mathbf{r})$：电场 $\mathbf{E} = -\nabla\phi$（静电场是势的梯度场）

**直觉图像**：等高线地图——梯度垂直于等高线，指向"山顶"；水总是沿 $-\nabla f$ 方向流（从高到低）。球在斜面上滚下的方向就是 $-\nabla h$。

**反直觉点 1**：梯度是**矢量**（有方向），不像普通导数是标量。
**反直觉点 2**：$\nabla f$ 在等高线最密的方向最大——**不是在 $f$ 值最大的地方**。山顶的梯度可以为零（局部极大），梯度大在"最陡的坡"上。

**应用**：温度场 $T(\mathbf{r})$ 的梯度给出热流方向 $\mathbf{q} = -k\nabla T$（Fourier 热传导定律）

---

### §4.2 散度（∇·）——"源"与"汇"的密度

**核心概念**：矢量场 $\mathbf{F}$ 的散度是标量，度量"从这里流出的净通量密度"。

**关键公式**：
$$\nabla \cdot \mathbf{F} = \frac{\partial F_x}{\partial x} + \frac{\partial F_y}{\partial y} + \frac{\partial F_z}{\partial z}$$

**点电荷散度计算（详细）**：点电荷 $q$ 的电场 $\mathbf{E} = \frac{q}{4\pi\epsilon_0}\frac{\hat{r}}{r^2}$。在 $r \neq 0$ 处：
$$\nabla \cdot \mathbf{E} = \frac{q}{4\pi\epsilon_0}\nabla\cdot\left(\frac{\hat{r}}{r^2}\right) = \frac{q}{4\pi\epsilon_0}\cdot\frac{1}{r^2}\frac{\partial}{\partial r}\left(r^2\cdot\frac{1}{r^2}\right) = \frac{q}{4\pi\epsilon_0}\cdot\frac{1}{r^2}\frac{\partial(1)}{\partial r} = 0$$
但用 Gauss 定理对包围原点的球面积分得 $\oint\mathbf{E}\cdot d\mathbf{S} = q/\epsilon_0 \neq 0$——所以"净通量非零但散度处处为零"的矛盾只能用 **δ 函数**解决：散度其实在原点发散，$\nabla\cdot\mathbf{E} = (q/\epsilon_0)\delta^3(\mathbf{r})$。

**Gauss 定律的微分形式**：$\nabla\cdot\mathbf{E} = \rho/\epsilon_0$——电荷密度 $\rho$ 是电场的源。这正是 Maxwell 方程之一。

**直觉图像**：把空间想象成水管网络——散度 > 0 是源头（水冒出），散度 < 0 是汇（水消失），散度 = 0 是无源（水只流过）。

**反直觉点 1**：一个场可以"看起来"在散开（如 $\mathbf{F} = (x, 0, 0)$，所有箭头向外指）——但散度 $\nabla \cdot \mathbf{F} = 1 \neq 0$，确实有源。
**反直觉点 2**：$\mathbf{F} = \hat{r}/r^2$ 看起来从原点向外辐射——但 $\nabla \cdot \mathbf{F} = 0$（除了原点）！因为 $1/r^2$ 的通量恰好被 $r^2$ 的面积抵消。

**应用**：麦克斯韦方程 $\nabla \cdot \mathbf{E} = \rho/\epsilon_0$——电荷是电场的源

---

### §4.3 旋度（∇×）——局部旋转的度量

**核心概念**：矢量场 $\mathbf{F}$ 的旋度是矢量，度量"局部旋转的强度和轴"。

**关键公式**：
$$\nabla \times \mathbf{F} = \left(\frac{\partial F_z}{\partial y} - \frac{\partial F_y}{\partial z},\; \frac{\partial F_x}{\partial z} - \frac{\partial F_z}{\partial x},\; \frac{\partial F_y}{\partial x} - \frac{\partial F_x}{\partial y}\right)$$

**保守力条件**：若 $\nabla\times\mathbf{F} = 0$（处处），则 $\mathbf{F}$ 是某势的梯度 $\mathbf{F} = -\nabla\Phi$，做功与路径无关（保守场）。静电场 $\nabla\times\mathbf{E} = 0$（Faraday 静电情况）→ 存在电势 $\phi$。

**Faraday 定律的微分形式**：$\nabla\times\mathbf{E} = -\partial\mathbf{B}/\partial t$——变化的磁场产生旋涡电场。这是发电机和变压器的原理。

**直觉图像**：在流场中放一个小风车（桨轮）——旋度是风车转动的轴和转速。旋度沿 $z$ 方向意味着风车绕 $z$ 轴转。

**反直觉点**：场可以"看起来"在转（如 $\mathbf{F} = (-y, x, 0)$ 绕 $z$ 轴匀速旋转，旋度 = $2\hat{z}$）——但也可能"看起来"不转却有旋度。关键是**局部**性质，不是全局外观。

**应用**：Ampère 定律 $\nabla \times \mathbf{B} = \mu_0 \mathbf{J}$——电流产生旋涡磁场

---

### §4.4 散度定理（Gauss 定理）——体积分 ↔ 面积分

**核心概念**：体积分中的散度 = 表面的总通量。

**关键公式**：
$$\int_V (\nabla \cdot \mathbf{F})\, dV = \oint_{\partial V} \mathbf{F} \cdot d\mathbf{S}$$

**工作示例（点电荷电场）**：对原点处点电荷 $q$，取半径 $R$ 的球面 $S$。
- 面积分（右侧）：$\oint\mathbf{E}\cdot d\mathbf{S} = E(R)\cdot 4\pi R^2 = \frac{q}{4\pi\epsilon_0 R^2}\cdot 4\pi R^2 = \frac{q}{\epsilon_0}$
- 体积分（左侧）：$\int_V(\nabla\cdot\mathbf{E})dV = \int_V\frac{q}{\epsilon_0}\delta^3(\mathbf{r})dV = \frac{q}{\epsilon_0}$
- 两边相等 ✓。这就是 **Gauss 定律的积分形式** $\oint\mathbf{E}\cdot d\mathbf{S} = Q_{\text{enc}}/\epsilon_0$。

**关键观察（与半径无关）**：注意 $E(R) \propto 1/R^2$ 而球面积 $\propto R^2$，两者恰好抵消——通量 $Q/\epsilon_0$ 与球的半径 $R$ **无关**！无论球多大（只要包围电荷），通量恒为 $q/\epsilon_0$。这就是 Gauss 定律的威力：选合适的对称闭合面，无需积分即可求出场。

**直觉图像**：一个房间——数门口的净人流（面积分）= 数每个角落的进出差额之和（体积分）。如果房间内没有人生成或消失（$\nabla \cdot \mathbf{F} = 0$），进多少出多少。

**反直觉点**：体积内部的"涡旋"（旋度不为零）**不影响**散度定理——只有"源/汇"才贡献。一个纯涡旋场的散度为零。

**应用**：Gauss 定律的积分形式——穿过任意闭合曲面的电通量只取决于内部总电荷

---

### §4.5 Stokes 定理——面积分 ↔ 线积分

**核心概念**：曲面上的旋度通量 = 边界曲线的环量。

**关键公式**：
$$\int_S (\nabla \times \mathbf{F}) \cdot d\mathbf{S} = \oint_{\partial S} \mathbf{F} \cdot d\mathbf{r}$$

**"任意曲面同边界"的深刻含义**：给定边界曲线 $C$，你可以选**任何**以 $C$ 为边界的曲面 $S$——平的、弯的、像泡泡膜一样飘的——结果都一样！
- 证明思路：设 $S_1, S_2$ 都以 $C$ 为边界，合成封闭面 $S_1 - S_2$。由散度定理 $\oint_{S_1-S_2}(\nabla\times\mathbf{F})\cdot d\mathbf{S} = \int_V\nabla\cdot(\nabla\times\mathbf{F})dV = 0$（因为旋度无散）→ $\int_{S_1} = \int_{S_2}$。
- 物理后果：Faraday 定律 $\oint\mathbf{E}\cdot d\mathbf{r} = -d\Phi_B/dt$ 中磁通量 $\Phi_B$ 可用任意曲面算——这正是 Ampère-Maxwell 定律需要位移电流项才能自洽的原因。

**保守力的逻辑链**（电动力学的核心推理）：
$$\nabla\times\mathbf{F} = 0 \;\;\Longrightarrow\;\; \mathbf{F} = -\nabla V \;\;\Longrightarrow\;\; \oint_C \mathbf{F}\cdot d\mathbf{r} = 0 \;\;\Longrightarrow\;\; \text{做功与路径无关}$$
- 第一步：旋度为零 → 存在势函数 $V$（由 $\nabla\times(\nabla f)=0$ 保证）。
- 第二步：$\mathbf{F} = -\nabla V$ → 环量 $\oint \mathbf{F}\cdot d\mathbf{r} = -\oint dV = 0$（势是单值函数）。
- 第三步：任意两路径 $C_1, C_2$ 间做功差 $= \oint_{C_1 - C_2}\mathbf{F}\cdot d\mathbf{r} = 0$ → 做功只取决于端点。
- 静电场 $\nabla\times\mathbf{E}=0$ → 存在电势 $\phi$ → 静电力是保守力。

**Faraday 定律应用**：$\oint\mathbf{E}\cdot d\mathbf{r} = -d\Phi_B/dt$——变化的磁通量产生电动势。

**直觉图像**：漩涡——把一个圆环浸入水中，沿环的流速积分（你被水推着走了多远）= 环面内的总涡旋强度。

**反直觉点**：曲面 $S$ 可以**任意选取**（只要是同一个边界 $C$）——鼓面、碗面、任意变形的膜，结果不变。旋度的通量**只取决于边界曲线**。

**应用**：Faraday 定律 $\oint \mathbf{E} \cdot d\mathbf{r} = -d\Phi_B/dt$——变化的磁通量产生电动势

---

### §4.6 曲线坐标中的算子

**核心概念**：球坐标 $(r, \theta, \phi)$ 和柱坐标 $(r, \phi, z)$ 下 $\nabla$、$\nabla \cdot$、$\nabla \times$ 有不同形式，需要度规因子。

**关键公式**（球坐标散度为例）：
$$\nabla \cdot \mathbf{F} = \frac{1}{r^2}\frac{\partial(r^2 F_r)}{\partial r} + \frac{1}{r\sin\theta}\frac{\partial(\sin\theta\, F_\theta)}{\partial \theta} + \frac{1}{r\sin\theta}\frac{\partial F_\phi}{\partial \phi}$$

**球坐标 Laplacian**：
$$\nabla^2 f = \frac{1}{r^2}\frac{\partial}{\partial r}\left(r^2 \frac{\partial f}{\partial r}\right) + \frac{1}{r^2\sin\theta}\frac{\partial}{\partial\theta}\left(\sin\theta \frac{\partial f}{\partial \theta}\right) + \frac{1}{r^2\sin^2\theta}\frac{\partial^2 f}{\partial \phi^2}$$

**直觉图像**：$1/r^2$ 因子来自球壳体积随 $r^2$ 增长；$\sin\theta$ 因子来自纬度圈周长。

**反直觉点**：球坐标中梯度不是简单的 $(\partial_r, \partial_\theta, \partial_\phi)$——有 $1/r$ 和 $1/(r\sin\theta)$ 因子，因为 $\theta$ 方向走 $d\theta$ 弧度对应的实际距离是 $r\,d\theta$，$\phi$ 方向是 $r\sin\theta\,d\phi$。

**应用**：氢原子 Schrödinger 方程在球坐标中分离变量——球谐函数 $Y_l^m(\theta,\phi)$ 自然出现

---

### §4.7 Dirac δ 函数

**核心概念**：$\delta^3(\mathbf{r})$ 在原点无穷大，其余为零，积分 = 1——点源的数学描述。

**关键公式**：$\nabla^2(1/r) = -4\pi\delta^3(\mathbf{r})$

**直觉图像**：一个无限窄、无限高、面积有限的尖峰。

**反直觉点**：$1/r$ 在 $r \neq 0$ 处满足 Laplace 方程 $\nabla^2(1/r) = 0$，但在原点处不满足——必须用 δ 函数"修补"。

**应用**：点电荷的电势 $\phi = q/(4\pi\epsilon_0 r)$——Poisson 方程 $\nabla^2\phi = -\rho/\epsilon_0$ 用 δ 函数处理点电荷

---

### §4.8 关键恒等式（含证明思路）

**恒等式 1**：$\nabla \times (\nabla f) = 0$（梯度无旋）
**按分量证明**：旋度的 $x$ 分量是
$$(\nabla\times\nabla f)_x = \frac{\partial}{\partial y}\frac{\partial f}{\partial z} - \frac{\partial}{\partial z}\frac{\partial f}{\partial y} = \frac{\partial^2 f}{\partial y\partial z} - \frac{\partial^2 f}{\partial z\partial y} = 0$$
（混合偏导交换——只要 $f$ 足够光滑，Clairaut 定理）。$y, z$ 分量同理。✓

**恒等式 2**：$\nabla \cdot (\nabla \times \mathbf{F}) = 0$（旋度无散）
**证明**：展开
$$\nabla\cdot(\nabla\times\mathbf{F}) = \frac{\partial}{\partial x}\left(\frac{\partial F_z}{\partial y} - \frac{\partial F_y}{\partial z}\right) + \cdots = \frac{\partial^2 F_z}{\partial x\partial y} - \frac{\partial^2 F_y}{\partial x\partial z} + \cdots$$
所有项成对抵消（混合偏导可交换）。✓

**恒等式 3（BAC-CAB）**：$\nabla \times (\nabla \times \mathbf{F}) = \nabla(\nabla \cdot \mathbf{F}) - \nabla^2 \mathbf{F}$
**推导**：用矢量恒等式 $\mathbf{A}\times(\mathbf{B}\times\mathbf{C}) = \mathbf{B}(\mathbf{A}\cdot\mathbf{C}) - \mathbf{C}(\mathbf{A}\cdot\mathbf{B})$（BAC-CAB），把 $\nabla$ 当作算符作用于两次：
$$\nabla\times(\nabla\times\mathbf{F}) = \nabla(\nabla\cdot\mathbf{F}) - (\nabla\cdot\nabla)\mathbf{F} = \nabla(\nabla\cdot\mathbf{F}) - \nabla^2\mathbf{F}$$
注意 $\nabla$ 既要参与矢量代数又要作用为微分算符——保持作用顺序是关键。

**深层意义**：前两个恒等式 = 外微分 $d^2 = 0$ 在三维的体现。这在微分几何和广义相对论中变成强大的工具。

**应用**：从 $\mathbf{B} = \nabla \times \mathbf{A}$ 自动得到 $\nabla \cdot \mathbf{B} = 0$（磁场无源）；电磁波方程从 Maxwell 方程用 BAC-CAB 推出。

## §5 必做习题（具体）

| 题 | 内容 | 为什么必做 |
|----|------|----------|
| 1 | 计算 $\nabla\cdot(\hat{r}/r^2)$ 在原点（δ 函数）和远离原点（=0） | 理解点电荷散度——电动力学核心 |
| 2 | 对任意光滑 $f$，按分量证明 $\nabla\times(\nabla f) = 0$ | 检验偏导交换的理解，外微分的种子 |
| 3 | 在球坐标中推导 Laplacian（不查表，用度规因子）| 度规因子是关键——氢原子的基础 |
| 4 | 验证 $\nabla^2(1/r) = -4\pi\delta^3(\mathbf{r})$（积分 + Gauss 定理）| δ 函数与势的核心关系 |
| 5 | 用 Gauss 定理从 $\nabla\cdot\mathbf{E} = \rho/\epsilon_0$ 推导 Coulomb 定律 | 连接微分与积分形式的 Maxwell 方程 |
| 6 | 计算刚体旋转场 $\mathbf{F} = (-y, x, 0)$ 的旋度，验证 = $2\hat{z}$ | 理解旋度的局部性质 vs 全局外观 |

## §6 读完后你应该能
- [ ] 在直角坐标和球坐标中计算梯度、散度、旋度
- [ ] 用散度定理把体积分化为面积分（Gauss 定律应用）
- [ ] 用 Stokes 定理把面积分化为线积分（Faraday 定律应用）
- [ ] 理解为什么麦克斯韦方程用 $\nabla \cdot$ 和 $\nabla \times$ 写——以及为什么这是**四个**方程
- [ ] 用 δ 函数描述点源（点电荷、点质量）
- [ ] 推导球坐标中的 Laplacian（不查表）
- [ ] 证明三个关键恒等式并理解 $d^2 = 0$ 的深层含义

## §7 与项目的映射
- **直接前置**：05_electromagnetism.md（麦克斯韦方程全用这三个算子）
- **并行**：09_fluid_mechanics.md（Euler/Navier-Stokes 也用同样的算子）
- **深层**：13_general_relativity.md（微分几何推广了这些概念）
- **对应**：L02 电磁学 + L06 数学方法

## §8 延伸阅读
- 读完 → 05 Electromagnetism（立即应用 $\nabla$ 算子）
- 教材 → Griffiths *Introduction to Electrodynamics* 第 1 章（最经典的矢量微积分入门，和 Tong 互为补充）
- 教材 → Marsden & Tromba *Vector Calculus*（数学系标准教材，更严格）
- 深入 → Schey *Div, Grad, Curl, and All That*（薄书，专门讲三个算子的直觉，极推）
- 可视化 → 3Blue1Brown "Divergence and Curl"（YouTube，极佳可视化）
- 深层数学 → Spivak *Calculus on Manifolds*（外微分观点，$\nabla$ 是 $d$ 的三维化身）

## §9 学习建议
- **节奏**：1-2 周（35 页，但需要大量练习巩固手感）
- **怎么读**：每读完一个算子，立刻做 5 道计算题。三个算子的公式必须变成肌肉记忆，不能每次推导
- **陷阱**：
  - 不要只记公式不练——球坐标公式必须自己推导至少一遍
  - 散度是**标量**、旋度是**矢量**——不要搞混维度
  - $\nabla \times (\nabla f) = 0$ 和 $\nabla \cdot (\nabla \times \mathbf{F}) = 0$ 这两个恒等式要会证明，因为它们决定了"什么场可以写为势的梯度/旋度"
  - δ 函数不是普通函数——它是分布（广义函数），积分交换不一定成立
- **关键洞察**：三个算子 $\nabla$、$\nabla \cdot$、$\nabla \times$ 就是外微分 $d$ 在三维的化身——0-形式 → 1-形式（梯度）、1-形式 → 2-形式（旋度）、2-形式 → 3-形式（散度），$d^2 = 0$ 就是那两个恒等式。这在微分几何和广义相对论中会变成强大的工具。

## §10 常见误区（深化新增）

### 🕳️ 误区 1：梯度指向函数值最大的方向
- ❌ "梯度指向 $f$ 最大的位置"
- ✅ 梯度指向**当前点增长率最大的方向**，不一定是 $f$ 值最大的位置。山顶的梯度为零（局部极大），梯度大在"最陡的坡"上。梯度是**局部**信息，告诉你"下一步往哪走 $f$ 增加最快"。

### 🕳️ 误区 2：散度为零的场没有源
- ❌ "如果 $\nabla\cdot\mathbf{F} = 0$，这个场就没有源"
- ✅ 可能有源被汇抵消，或源在无穷远；更常见的是**δ 函数源**——点电荷电场 $\mathbf{E}\propto\hat{r}/r^2$ 在 $r\neq 0$ 处散度处处为零，但原点有一个 δ 函数源。散度为零只意味着"该点局部无源"，不排除别处有源。

### 🕳️ 误区 3：旋度大的场看起来转得快
- ❌ "旋度大 = 整体转得快"
- ✅ 旋度是**局部**性质，与全局外观无关。$\mathbf{F} = (-y, x, 0)$（刚体旋转）转得快但旋度恒定 = $2\hat{z}$；而某些"看起来不转"的场（如剪切流 $\mathbf{F} = (0, x, 0)$）旋度 = $\hat{z}$ 非零。判断旋度要看场的**空间导数**，不是视觉旋转。

### 🕳️ 误区 4：Stokes 定理中曲面必须平坦
- ❌ "Stokes 定理只能用平面或凸曲面"
- ✅ 任何以 $C$ 为边界的曲面都行——可以像泡泡膜一样任意弯曲、凹凸。这是由 $\nabla\cdot(\nabla\times\mathbf{F}) = 0$ 保证的（两个不同曲面合成封闭面，体积分=0）。物理后果：Faraday 定律中磁通量曲面可任选。

### 🕳️ 误区 5：球坐标梯度就是 $(\partial_r, \partial_\theta, \partial_\phi)$
- ❌ "球坐标梯度各分量就是 $f$ 对 $r, \theta, \phi$ 的偏导"
- ✅ 球坐标有度规因子：$\nabla f = \hat{r}\frac{\partial f}{\partial r} + \hat{\theta}\frac{1}{r}\frac{\partial f}{\partial\theta} + \hat{\phi}\frac{1}{r\sin\theta}\frac{\partial f}{\partial\phi}$。因为 $\theta$ 方向走 $d\theta$ 弧度对应的实际距离是 $r\,d\theta$，$\phi$ 方向是 $r\sin\theta\,d\phi$——度规因子 $1/r$ 和 $1/(r\sin\theta)$ 把"角度变化"换算成"实际距离变化"。

## §11 与其他矢量微积分教材的对比（深化新增）

| 教材 | 风格 | 适合谁 | vs Tong |
|------|------|--------|---------|
| **Tong** *Vector Calculus* | 浓缩，物理直觉优先 | 物理学生，快速上手 | 基准：最薄的入门，1-2 周可读完 |
| **Griffiths** *Electrodynamics* Ch.1 | 物理应用导向，电磁语境 | 学电磁学同时学数学 | 比 Tong 更详细，与电磁学无缝衔接，但嵌入在电磁书里 |
| **Schey** *Div, Grad, Curl, and All That* | 薄书，纯讲三个算子直觉 | 想要直觉理解 | 与 Tong 互补，更口语化，有大量图示 |
| **Marsden & Tromba** *Vector Calculus* | 数学系严谨，定理证明 | 数学专业或想严格 | 比 Tong 更严格更全，但更重数学轻物理 |
| **Spivak** *Calculus on Manifolds* | 外微分观点，抽象 | 想看深层结构 | 揭示 $\nabla$ 是外微分 $d$ 的三维化身，$d^2=0$ 统一两个恒等式——但需要抽象代数基础 |

**建议组合**：**Tong（主读，快速建框架）+ Griffiths Ch.1（电磁应用巩固）+ Schey（直觉补充）** = 矢量微积分自学三件套。学完立即进入 05_electromagnetism（麦克斯韦方程）即可大量应用。对数学结构感兴趣可后读 Spivak 看外微分观点（通向微分几何和广义相对论）。

---

**完成日期：2026-08-13（深化版 v2）**
**配套**：[tong/README.md](README.md) + [TEMPLATE.md](../TEMPLATE.md) + [ai_for_physics/](../../ai_for_physics/)
