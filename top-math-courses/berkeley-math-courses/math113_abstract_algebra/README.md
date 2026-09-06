# UC Berkeley MATH 113 — Introduction to Abstract Algebra

> **学校**：Berkeley
> **一手来源**：[math.berkeley.edu/courses](https://math.berkeley.edu/courses)

## 课程信息
- **编号**：MATH 113 / H113 (honors)
- **先修**：MATH 110 或 MATH 54 + proof 能力
- **教材**：**Dummit & Foote, *Abstract Algebra***；或 Artin *Algebra*
- **特色**：本科抽象代数标准课

## 教学大纲
1. Groups & subgroups
2. Homomorphisms & quotients
3. Symmetric & alternating groups
4. Group actions, Sylow 定理
5. Rings, ideals
6. Modules
7. Field extensions, Galois theory 入门

## 与 ML 的关联
- 群论 → 等变神经网络
- 学完后：理解 G-CNN

## 参考资源
- Dummit & Foote, *Abstract Algebra* (3rd ed)
- Artin, *Algebra* (2nd ed)

---

## 📍 在数学全景中的位置

```
线性代数 (线性变换, 矩阵群)            数论 (整数, 模运算)
        │                                     │
        └──────────┬──────────────────────────┘
                   ▼
            本课: 抽象代数
      ┌────────────┼─────────────┐
      ▼            ▼             ▼
   群论          环论           域论/Galois
 (对称性)     (数系推广)      (方程可解性)
      │            │             │
      ▼            ▼             ▼
 等变神经网络   密码学/编码     代数几何
 (G-CNN)       (RSA, ECC)     (多项式环)
 AlphaFold     椭圆曲线签名    代数簇
```

- **前置**：[MATH 110 线代](../math110_linear_algebra/)（矩阵/线性变换）
- **本课**：群 → 群作用 → 环 → 域 → Galois 入门
- **后续/交叉**：
  - [MIT 18.701 Artin](../../mit-math-courses/18_701_algebra_I/)（Artin 体系，矩阵群视角）
  - [Harvard Math 122](../../harvard-math-courses/math122_algebra_I/)（Dummit-Foote 对照）
  - **表示论**（ML 等变网络的真正基础）

---

## 🔬 理论联系实际（ML/工程应用，公式级）

### 1. CNN 平移等变 = $\mathbb{Z}^d$ 群卷积 ★
$$f * k \text{ 满足 } T_g(f*k) = (T_g f) * k, \quad g \in \mathbb{Z}^d$$
平移群 $\mathbb{Z}^d$ 的群卷积 = 标准 CNN。推广到 $p4$（+旋转）→ G-CNN（Cohen-Welling [1602.07576](https://arxiv.org/abs/1602.07576) ✅）。详见 [notes.md](notes.md) §3.1。

### 2. AlphaFold = SE(3)-等变表示
$$f(Rx) = Rf(x), \quad R \in SO(3)$$
蛋白质旋转后预测也旋转。用球谐函数（$SO(3)$ 不可约表示）构造等变层。SE(3)-Transformer [Fuchs 2020, 2006.10503](https://arxiv.org/abs/2006.10503) ✅。

### 3. DeepSets / Set Transformer = $S_n$ 不变性
$$f(\{x_1, \ldots, x_n\}) = \rho\!\Big(\sum_i \phi(x_i)\Big)$$
求和天然 $S_n$ 不变。处理点云/集合数据的基础。实验见 [experiments/group_actions_demo.py](experiments/group_actions_demo.py)。

### 4. 数据增强 = 群作用
翻转/旋转增强 = 用 $D_4$ 群作用扩充数据。增强（软概率约束）vs 等变网络（硬精确约束）。

### 5. 密码学 = 有限域群
RSA：$(\mathbb{Z}/n\mathbb{Z})^\times$ 群 + Fermat 小定理。椭圆曲线：有限域上椭圆曲线点的加法群。

---

## 🆕 2024-2026 最新研究

| 子主题 | 最新进展 | 参考 |
|---|---|---|
| **SE(3)-等变 Transformer** | AlphaFold 3 用扩散模型 + 等变架构，精度大幅提升 | [AlphaFold 3, Nature 2024](https://www.nature.com/articles/s41586-024-07487-w) ✅ |
| **E(3)-等变扩散模型** | 分子生成用等变扩散（EDM），对称性约束 3D 结构 | [Hoogeboom et al. 2022, 2203.17061](https://arxiv.org/abs/2203.17061) ✅ |
| **等变对称发现** | 从数据自动学习对称性（Learning Symmetries），不再手动指定群 | ⚠️ 2024 ICLR 进展 |
| **Galois 神经网络** | 用 Galois 群结构约束消息传递 | 研究中 ⚠️ |
| **表示论引导的架构设计** | 自动用不可约表示构造等变层（e3nn 库） | e3nn 开源生态 |

> ⚠️ 标记项建议核实最新 arXiv 版本。

---

📌 **下一步**：→ [MATH 185 Complex Analysis](../math185_complex_analysis/) 或 [MIT 18.701](../../mit-math-courses/18_701_algebra_I/)
