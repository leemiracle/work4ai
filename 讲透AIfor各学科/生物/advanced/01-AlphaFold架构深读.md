# 生物 · AlphaFold 2 架构深读

> **博士级**：AlphaFold 2 (Nature 2021) 的架构细节 + 数学。

## 一、解决的问题

**输入**：氨基酸序列（1D）
**输出**：3D 坐标

**挑战**：序列 → 结构映射极高维 + 非线性。

## 二、AlphaFold 2 的核心架构

### 2.1 五大模块

```
1. MSA 模块（多序列比对）
   ↓ Evoformer
2. Evoformer（核心创新）
   ↓ structure module
3. Structure Module（产生 3D）
   ↓ refinement
4. Amber relaxation（精修）
   ↓ confidence
5. pLDDT（置信度）
```

### 2.2 Evoformer（核心）

48 个 Transformer 块，处理两个表示：
- **MSA 表示**：序列 × 残基（行 = 序列，列 = 残基）
- **Pair 表示**：残基对（i, j）关系

**关键操作**：
- ** axial attention**（轴向）
- **triangle attention**（三角）—— 满足三角不等式
- **outer product mean**（MSA → pair）
- **pair → MSA 反投影**

### 2.3 Structure Module

- **Invariant Point Attention (IPA)**：SE(3) 等变注意力
- 直接输出原子坐标

### 2.4 Recycling（迭代）

3 次迭代精修——提升准确度。

## 三、关键创新点

### 3.1 端到端学习

从序列直接到坐标——无中间物理建模。

### 3.2 Evoformer 三角更新

**为什么**：3D 距离满足三角不等式。**Pair 表示**学习"距离矩阵"。

**数学**：
$$d_{ij} \leq d_{ik} + d_{kj}$$

网络用三角更新保持一致。

### 3.3 IPA（Invariant Point Attention）

等变注意力——给定 3D 坐标，进行旋转/平移不变的 attention。

类似 NequIP 的 SE(3) 等变。

## 四、AlphaFold 3 的扩展（2024）

- 处理 **蛋白-蛋白 / 核酸 / 小分子**
- **diffusion** 替代 structure module
- 精度超 AF2-Multimer

## 五、博士级练习

1. 阅读 AF2 论文 Supplementary（300+ 页细节）
2. 实现 IPA 模块（PyTorch 100 行）
3. 复现 triangle attention

## 六、性能

- **CASP14**：GDT ~92（接近实验精度）
- **PDB** 全部 2 亿结构预测完成
- **2024 Nobel Chemistry**

## 七、关键引用

- Jumper 2021 *Nature* AF2
- Abramson 2024 *Nature* AF3
- OpenFold（开源复现）
