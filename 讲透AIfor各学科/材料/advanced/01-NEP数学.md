# 材料 · 神经网络势能（NEP）数学

> **博士级**：神经网络势能函数的数学 + 等变消息传递。

## 一、什么是 NEP

**经典**：DFT 算能量 + 力，精确但慢。
**NEP**：神经网络近似，快 1000-10000×。

形式：

$$E(\mathbf{R}) = \sum_i E_i(\mathbf{R}_i)$$

其中 $E_i$ 是局部原子能量。

力：

$$\mathbf{F}_i = -\nabla_{\mathbf{R}_i} E$$

## 二、关键约束

### 2.1 物理约束

- **能量守恒**：E 是状态函数
- **旋转/平移不变性**：$E(R\mathbf{R}) = E(\mathbf{R})$
- **置换不变性**：同种原子交换不变

### 2.2 实现

- **Body-ordered**（如 BPNN）：明确展开 n-body
- **Message Passing**（如 SchNet/NequIP）：隐式高阶

## 三、SchNet（不变版）

```
原子 i 的 embedding h_i
   ↓ 多层消息传递
更新 h_i = agg(h_i, h_j, d_{ij})  j ∈ 邻居
   ↓
能量 E_i = MLP(h_i)
```

**问题**：只看到距离，没方向。在 chiral 分子失败。

## 四、NequIP（等变版）

加入方向信息——**SE(3) 等变消息**。

```
h_i 是向量（l=1）+ 标量（l=0）+ 高阶
消息 m_{ij} = CG(h_i, h_j, \hat{r}_{ij})
   ↑ Clebsch-Gordan 积
```

**结果**：样本效率 10× SchNet。

## 五、MACE（高阶版）

**问题**：NequIP 消息 1-body，高阶相关需多步。
**MACE**：单步包含**高阶相关**（4 阶+）。

**数学**：

$$m_i = \text{CG}^{(L)}\left(\bigotimes_{j} \text{CG}(h_j, \hat{r}_{ij})\right)$$

**结果**：更准 + 单次消息传递。

## 六、性能对比

| 方法 | 等变性 | MD 速度 | 准确度 |
|---|---|---|---|
| DFT | — | 慢（fs-ns） | 精确 |
| BPNN | 不变 | 快 | 低 |
| SchNet | 不变 | 很快 | 中 |
| NequIP | SE(3) | 中 | 高 |
| Allegro | 局部 SE(3) | 快 | 高 |
| MACE | SE(3) + 高阶 | 中 | **最高** |

## 七、当前前沿

### 7.1 Universal NNP（基础模型）

- **MACE-MP-0**（2024）：跨元素通用
- **MatterSim**（微软）
- **SevenNet**

### 7.2 长程相互作用

经典 NEP 截断（5-10 Å）——长程（H 键、π-π）挑战。

- **TorchMD-Net + attention**：注意力长程
- **ALLEGRO 局部 + attention**

### 7.3 训练数据

- **OC20**（5 亿 DFT）
- **Materials Project**
- **Trajectory data**（MD 轨迹）

## 八、博士级练习

1. 实现简单 NEP（PyTorch 100 行）
2. 在 QM9 训练 + 对比 SchNet vs NequIP
3. 分析 MACE 在长程相互作用上的表现

## 九、关键引用

- Behler-Parrinello 2007（BPNN 开山）
- Schütt 2017 SchNet
- Batzner 2022 NequIP
- Batatia 2022 MACE
- Batatia 2024 MACE-MP-0
