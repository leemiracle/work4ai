# UC Berkeley MATH 185 — Introduction to Complex Analysis

> **学校**：Berkeley
> **一手来源**：[math.berkeley.edu/courses](https://math.berkeley.edu/courses)

## 课程信息
- **编号**：MATH 185 / H185 (honors)
- **先修**：MATH 104
- **教材**：Gamelin, *Complex Analysis*；Brown & Churchill
- **特色**：本科复分析

## 教学大纲
1. Complex numbers & functions
2. Analytic functions
3. Cauchy-Riemann equations
4. Contour integrals
5. **Cauchy 定理 & Cauchy 公式** ★
6. Power series & Laurent series
7. **Residue theorem** ★
8. Argument principle
9. Conformal mapping
10. Harmonic functions

## 与 ML 的关联
- 调和分析的基础
- 学完后：能理解 Fourier 分析的高级话题

## 参考资源
- Gamelin, *Complex Analysis* (Springer)
- Brown & Churchill, *Complex Variables and Applications*
- MIT 对照：[18.112 Functions of a Complex Variable](../../mit-math-courses/)

---

## 📍 在数学全景中的位置

- **前置**：[MATH 104 分析](../math104_analysis/)（实分析的严格基础）
- **本课**：全纯函数 → Cauchy 定理 → 留数定理 → 共形映射 → 积分计算
- **后续/交叉**：概率论（特征函数）+ 信号处理（Z 变换）+ 调和分析

---

## 🔬 理论联系实际（ML/工程应用）

### 1. 信号处理：Z 变换 + 留数 = 滤波器
$$X(z) = \sum x[n]z^{-n}, \quad x[n] = \frac{1}{2\pi i}\oint X(z)z^{n-1}dz$$
数字滤波器的传递函数极点在单位圆内 → 稳定系统。

### 2. 控制论：Nyquist 判据
用开环频率响应（复值曲线）的环绕次数判断闭环稳定性——辐角原理的直接应用。

### 3. 概率论：特征函数
$$\phi_X(t) = \mathbb{E}[e^{itX}] \Rightarrow \text{唯一确定分布}$$
特征函数的解析性质 → 矩的存在性与分布收敛（CLT 证明的关键）。

### 4. Fourier 变换 = 实轴上的复分析
快速傅里叶变换（FFT）是信号处理/ML 中卷积运算的核心。

### 5. 共形映射 → 保角变换网络
近年工作用共形映射思想设计几何感知的神经网络架构。⚠️ 具体论文待核实。

---

## 🆕 2024-2026 最新研究

| 子主题 | 进展 | 参考 |
|---|---|---|
| **复值神经网络** | 复数权重/激活的网络在信号处理/雷达中优于实值 | ⚠️ |
| **解析信号与 Hilbert 变换** | 包络分析用于时间序列 ML | 标准 DSP |
| **保形映射 + 几何深度学习** | 用共形结构引导 mesh 上的 GNN | ⚠️ 2024 |

> ⚠️ 标记项建议核实。复分析与 ML 的直接交叉较少，主要通过信号处理间接联系。

---

📌 **下一步**：→ [STAT 134 Probability](../stat134_probability/)
