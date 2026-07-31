# 讲透反向传播

> **反向传播是深度学习最底层的数学引擎。** 没有 GPT、Stable Diffusion 等一切大模型都无从谈起。本教程沿「直觉 → 数学 → 计算图 → 代码」讲透它，**不止于"是什么"，更挖到"为什么是反向模式 AD、为什么 O(1) 算所有梯度、PyTorch 真实 backward 的 mutation 边界"**。

---

## 与其他「讲透」项目的关系

```
讲透激活函数   → 反传里每层的"局部导数"长什么样 (ReLU掩码/sigmoid饱和)
讲透泛化       → 反传算出的梯度怎么变成"学习" (隐式正则/优化器)
讲透PyTorch    → backward() 在框架层如何实现 (autograd/dispatcher)
讲透反向传播   → ★ 梯度到底怎么算出来的 (链式法则/计算图/VJP) — 你在这里
```

本教程是上面一切的**共同地基**：激活函数提供局部导数，反传把它们连起来，优化器加工梯度，框架高效执行。

## 教学宪法

每章三层：**直觉（比喻）→ 数学（公式+证明）→ 代码（bash 跑通的实证）**。诚实标注数学理想 vs 框架工程边界。

## 目录与学习路径

```mermaid
graph LR
    A[00 为什么需要反传<br/>数值微分为何不行] --> B[01 反传的精确本质 ★<br/>=反向模式AD]
    B --> C[02 为什么反向不是前向 ★<br/>效率不对称+O(N)证明]
    C --> D[03 VJP统一视角<br/>雅可比转置+形状一致]
    D --> E[04 手算一个MLP<br/>链式法则落到代码]
    E --> F[05 计算图与自动微分<br/>PyTorch实现]
    F --> G[06 反传的故障<br/>消失/爆炸/裁剪]
    F --> H[07 各种梯度的全景]
    F --> I[08 PyTorch真实边界 ★<br/>mutation/view/CopySlices]
    I --> J[09 边界与未来<br/>forward-forward/reparam]
```

| 章节 | 文档 | 核心问题 | 实验 |
|------|------|---------|------|
| 00 | [00-为什么需要反传.md](00-为什么需要反传.md) | 数值微分为何不可行？ | `00_numerical_vs_backprop` |
| 01 | **[01-反传的精确本质.md ★](01-反传的精确本质.md)** | 反传 ≠ 链式法则，是反向模式 AD | `01_autograd_from_scratch` |
| 02 | **[02-为什么反向不是前向.md ★](02-为什么反向不是前向.md)** | 为什么 m≪n 让反传胜出 + O(N) 证明 | `00` |
| 03 | [03-VJP统一视角.md](03-VJP统一视角.md) | 雅可比-向量积 + 形状为何一致 | `02_vjp_and_shapes` |
| 04 | [04-手算一个MLP的反传.md](04-手算一个MLP的反传.md) | 把链式法则逐步落到 numpy | `03_mlp_by_hand` |
| 05 | [05-计算图与自动微分.md](05-计算图与自动微分.md) | 动态图/grad_fn/PyTorch 怎么自动反传 | `04_gradient_check` |
| 06 | [06-反传的故障.md](06-反传的故障.md) | 消失/爆炸/裁剪 + 残差为何救场 | `05_vanishing_exploding` |
| 07 | [07-各种梯度的全景.md](07-各种梯度的全景.md) | 数据量/计算法/优化器加工/特殊场景 | `06_optimizer_gradients` |
| 08 | **[08-PyTorch真实反传边界.md ★](08-PyTorch真实反传边界.md)** | mutation/view/CopySlices（最硬核） | `07_mutation_views` |
| 09 | [09-边界与未来.md](09-边界与未来.md) | reparam/graph break/forward-forward | — |
| — | [exercises.md](exercises.md) | 输出倒逼输入 | — |

## 环境与运行

```
torch 2.10 (CPU)  |  numpy 1.26  |  python 3.12
```

```bash
cd 讲透反向传播/experiments && bash run_all.sh    # 一键跑通全部 8 个实验
```

## 实证速览（全部 bash 跑通）

| 实验 | 关键数字 | 说明 |
|------|---------|------|
| 00 数值微分vs反传 | 1000参数: 数值微分慢几十倍, 反传几乎不变 | O(n) vs O(1) 的实证 |
| 01 手写反传引擎 | 与 torch 对拍 **0 误差**, MLP 收敛 0.22→0.005 | 90 行复刻 backward 灵魂 |
| 02 VJP | VJP=J^T·v̄ 自动与输入同形 | 形状一致的精确原因 |
| 03 手算 MLP | 手算 vs autograd 最大差 1e-6 | 链式法则逐层落地 |
| 04 梯度检查 | gradcheck 抓出写错的 backward | 数值验证解析梯度 |
| 05 消失爆炸 | sigmoid 浅层梯度 ≈0, ReLU+残差救场 | 连乘诅咒实证 |
| 06 优化器加工 | 同一原始梯度, Momentum/Adam 更新天差地别 | 反传输出只是原料 |
| 07 mutation边界 | version counter 检测失效、CopySlices 处理 view | 数学→工程鸿沟 |

---

📌 **下一步**：从 [00-为什么需要反传](00-为什么需要反传.md) 开始；想直击本质跳 [01](01-反传的精确本质.md) + [02](02-为什么反向不是前向.md)；想看 PyTorch 硬核边界跳 [08](08-PyTorch真实反传边界.md)。
