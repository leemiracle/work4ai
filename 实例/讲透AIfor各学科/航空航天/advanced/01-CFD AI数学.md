# 航空航天 · CFD AI 数学（PINN / FNO 在航空）

> **博士级**：CFD 加速的数学 + 航空应用。

## 一、CFD 在航空的核心地位

### 1.1 Navier-Stokes 方程

$$\rho \left( \frac{\partial \mathbf{v}}{\partial t} + \mathbf{v} \cdot \nabla \mathbf{v} \right) = -\nabla p + \mu \nabla^2 \mathbf{v} + \mathbf{f}$$

### 1.2 经典数值方法

- **FVM**（有限体积）/ **FEM**（有限元）
- **DNS**（直接数值模拟）：精确但 $Re^{9/4}$ 成本
- **RANS**（雷诺平均）：工程用，近似

### 1.3 AI 解药

- **PINN**：详见 [`物理/advanced/01`](../../物理/advanced/01-PINN数学严格推导.md)
- **Neural Operator**（FNO）：详见 [`物理/advanced/02`](../../物理/advanced/02-NeuralOperators深挖.md)
- **湍流模型 ML**

## 二、航空专属应用

### 2.1 翼型设计

- **形状优化**
- AI 替代 CFD（快 1000×）
- **AirShaper** 等商业

### 2.2 飞机整体气动

- 全机 CFD：百万网格
- AI 加速设计迭代
- **波音 / 空客** 内部用

### 2.3发动机

- **涡轮叶片**冷却
- **燃烧室**模拟
- **GE / Rolls-Royce**

### 2.4 噪声

- **气动噪声**（发动机 / 机身）
- AI 预测 + 降噪设计

## 三、湍流的 AI

### 3.1 湍流闭合（Closure）

**经典**：RANS + k-ε / k-ω 模型（经验）。

**AI**：学闭合项。

**Ling et al. 2016**：CNN 学雷诺应力。

### 3.2 LES + AI

- **大涡模拟**（LES）
- AI 学亚网格应力
- 比 RANS 准 + 比 DNS 快

### 3.3 湍流的 Universal

- 不同几何的普适湍流模型
- **Duraisamy 2021 综述**

## 四、超音速 / 高超音速

### 4.1 挑战

- **激波**（强不连续）
- **化学反应**（高温）
- **稀薄气体**（高高度）

### 4.2 AI 限制

- 激波难学（强非线性）
- 需**特殊处理**（shock-capturing）
- PINN 失败案例

## 五、数字孪生

### 5.1 飞机数字孪生

- 实时仿真 + 传感器
- **GE / Boeing** 大量使用
- 详见 [`物理/advanced/02`](../../物理/advanced/02-NeuralOperators深挖.md)

### 5.2 引擎数字孪生

- 实时性能 + 磨损
- 预测性维护
- **省 $B+**

## 六、博士级练习

1. 在 NASA 翼型数据训练 AI
2. 实现 PINN 解 NACA 翼型
3. 分析 FNO 在激波的失败

## 关键引用

- Kochkov 2021 *PNAS*
- Ling 2016 *J Fluid Mech*
- Duraisamy 2021 *AIAA Journal*
- Brunton 2020 *Applied Mechanics Reviews*
