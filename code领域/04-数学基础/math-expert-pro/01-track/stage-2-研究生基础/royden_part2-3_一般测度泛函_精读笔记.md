# Royden《实分析》Part II-III · 一般测度/泛函分析 · 精读笔记

> 基于原书第 9-20 章(5th ed. PP.157-450)。**Royden 收尾**:一般测度(Fubini/Radon-Nikodym)+ 泛函分析(Banach/Hilbert)。
> 原书:`Real Analysis (Royden 5e)` Part II-III / 读于:2026-07-01

---

## §0 一句话

> **Part II 把 Lebesgue 测度推广到任意测度空间(Fubini 重积分/Radon-Nikodym 密度);Part III 把完备性从数/函数推广到空间本身(Banach/Hilbert)——这是现代分析+泛函的根基。**

---

## §1 Part II:一般测度(原书 PP.157-260)

### 一般测度空间 $(X,\mathcal{A},\mu)$
- $\mathcal{A}$ σ-代数,$\mu:\mathcal{A}\to[0,\infty]$ 可数可加
- Lebesgue 测度是特例($X=\mathbb{R}$,$\mathcal{A}$=Lebesgue 可测)

### **Radon-Nikodym 定理** ⭐(Part II 皇冠)
若 $\mu\ll\nu$(绝对连续:$\nu(E)=0\Rightarrow\mu(E)=0$),则存在**密度** $f=\frac{d\mu}{d\nu}\ge0$ 使
$$\mu(E)=\int_E f\,d\nu$$
> 🎯 **意义**:"绝对连续 ⟺ 有密度"。这是**概率论**(随机变量的分布密度)、**信息论**(相对熵)、**统计**(贝叶斯后验)的根基。

### **Fubini-Tonelli 定理**(重积分)
$(X\times Y,\mu\times\nu)$,$\int\int f=\int f$。
- **Tonelli**(非负):可交换积分序(无需可积假设)
- **Fubini**(可积):$\int|f|<\infty$ ⟹ 可交换

> 🎯 **工程**:高维积分=累次积分(MC 采样/贝叶斯边缘化的理论依据)。

### Hausdorff 测度(分形维数)
$\mathbb{R}^n$ 上不同维度的"体积":$H^s$ 是 $s$ 维 Hausdorff 测度。
- 分形的 Hausdorff 维数(柯朗第9章分形的严格化)

---

## §2 Part III:抽象空间(原书 PP.261-450,泛函分析)

### 度量空间(第13-14章)
- 完备度量空间:Cauchy ⟹ 收敛($\mathbb{R}$ 的推广)
- **紧致 ⟺ 完备 + 全有界**(度量空间特有)
- **Arzelà-Ascoli**(紧致函数族:一致有界+等度连续)
- **Banach 不动点**(压缩映射 ⟹ 唯一不动点)→ Picard ODE 解存在

### **Banach 空间(完备赋范空间,第17-18章)** ⭐
- **赋范**:线性空间 + 范数 $\|\cdot\|$
- **完备**:Cauchy ⟹ 收敛
- 例:$L^p$,$\ell^p$,$C([a,b])$(上确界范数)

### **泛函分析三定理**(第17章)⭐⭐
| 定理 | 内容 |
|------|------|
| **Hahn-Banach** | 有界线性泛函可延拓(保范)|
| **开映射** | 有界线性满射 ⟹ 开映射 |
| **闭图像** | 闭图像 ⟹ 连续 |
| **一致有界**(共鸣)| 点态有界 ⟹ 一致有界 |

> 🎯 **Hahn-Banach** 是优化/对偶/量子力学的根基(SVM 对偶、量子态分离)。

### **Hilbert 空间(第20章,内积空间)** ⭐⭐
- 完备内积空间:$\langle\cdot,\cdot\rangle$
- **正交基**(Bessel 不等式 / Riesz-Fischer)
- **谱定理**(紧自伴算子):可正交对角化
> 🎯 **量子力学**:量子态 = Hilbert 空间向量;可观测量 = 自伴算子(LADR 第7章谱定理的无限维版)。

---

## §3 飞腾/Python 锚点
| Royden 概念 | 工程 |
|------------|------|
| Radon-Nikodym 密度 | 概率密度/贝叶斯后验 |
| Fubini 重积分 | 高维积分(MC/贝叶斯)|
| Hausdorff 测度 | 分形维数(图形)|
| Banach 不动点 | ODE 数值解(Picard 迭代)|
| **Hilbert 空间** | **量子力学/核方法/ML(RKHS)** |
| Hahn-Banach | SVM 对偶/优化 |

---

## §4 自测
1. **Radon-Nikodym**:绝对连续 ⟺ 有密度。概率密度如何由此?
2. **Fubini**:为何需要 $\int|f|<\infty$?(给反例:不可积时累次积分可能不等)
3. Banach 空间 vs Hilbert 空间?(Hilbert 有内积,Banach 只有范数)
4. Hahn-Banach 定理的优化意义?(SVM 对偶)

---

## 🏆 Royden 全书闭环(第1-20章)

```
Part I (ch1-8): Lebesgue 积分(单变量)— 测度+积分+Lp
Part II (ch9-12): 一般测度 — Radon-Nikodym/Fubini/Hausdorff
Part III (ch13-20): 抽象空间 — 度量/Banach/Hilbert + 泛函三定理
```

> 🎯 **Royden 的统一视野**:从"数的完备"(Spivak)→"函数的积分"(Part I)→"空间的完备"(Part III)。完备性是贯穿 stage-1 到 stage-2 的红线。
