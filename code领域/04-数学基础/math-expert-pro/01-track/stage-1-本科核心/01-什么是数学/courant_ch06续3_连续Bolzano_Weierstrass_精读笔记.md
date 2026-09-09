# 柯朗第 6 章·续3 · 连续性定义/Bolzano/Weierstrass/紧致 · 逐节精读

> 续前三篇第6章笔记,覆盖原书 §4-§5(中文版 PP.680-710)。
> 原书:`什么是数学(柯朗)` ch6 续3 / 读于:2026-07-01

---

## §4 连续性的精确定义(原文 PP.680-690)

### ε-δ 连续定义 ⭐
$f$ 在 $x_1$ **连续** ⟺ $\forall\varepsilon>0,\exists\delta>0,|x-x_1|<\delta\Rightarrow|f(x)-f(x_1)|<\varepsilon$
- 与极限的区别:连续允许 $x=x_1$($|f(x_1)-f(x_1)|=0<\varepsilon$ 平凡)
- $\delta=\varphi(\varepsilon)$:约定比喻(你选 ε,我找 δ)

### 例:$x^3$ 在 0 连续
$|x^3-0|=|x|^3<\varepsilon$ ⟹ 取 $\delta=\varepsilon^{1/3}$

### 几何解读
连续 = 以 $x_1$ 为心宽 $2\delta$ 的竖带 ⟹ 图像落在以 $f(x_1)$ 为心宽 $2\varepsilon$ 的横带内。

---

## §5 连续函数的两个基本定理(原文 PP.690-710,本章高潮)⭐⭐

### **Bolzano 定理(介值定理原型)** ⭐⭐
> $f$ 在 $[a,b]$ 连续,$f(a)<0<f(b)$ ⟹ $\exists\alpha\in(a,b),f(\alpha)=0$。

**证明(原文,bisection+区间套)**:
1. 二分 $[a,b]$,取 $f$ 端点异号的半区间 $I_1$
2. 重复 ⟹ 区间套 $I_1\supset I_2\supset\cdots$
3. **Dedekind-Cantor 公理**(§2 区间套)⟹ 存在唯一点 $\alpha$ 属于所有 $I_n$
4. **反证** $f(\alpha)\ne0$:设 $f(\alpha)=2\varepsilon>0$,连续 ⟹ $\alpha$ 附近 $f>\varepsilon$;但 $I_n$ 端点异号 ⟹ $I_n$ 内有负值——矛盾 ∴ $f(\alpha)=0$ ∎

> 🎯 **Spivak 第7章 "Three Hard Theorems" 的柯朗版**:Bolzano 用区间套(Dedekind-Cantor 完备性)证明,Spivak 用 LUB。两者同源——完备性是根。

### **Weierstrass 极值定理** ⭐⭐
> $f$ 在 $[a,b]$ 连续 ⟹ $\exists z,f(z)=\max_{[a,b]}f$。

证明同 bisection:每次取含"更大值"的半区间 ⟹ 区间套 ⟹ 收敛点 $z$ ⟹ $f(z)=M$(反证 $f(s)>M$ 矛盾)。

### **Bolzano-Weierstrass 定理(紧致)** ⭐
> 有界序列 $\{x_n\}\subset[a,b]$ ⟹ 有**收敛子序列**。

证明:二分区间,至少一半含无穷多项 ⟹ 选子序列 ⟹ 区间套 ⟹ 收敛。

> 🎯 **紧致性**:闭有界 ⟹ 序列有收敛子列。这是现代拓扑(Munkres)的根基。

### 直觉主义批评
Bolzano/Weierstrass 证明是**非构造性**的(只证存在,不给算法)——Brouwer 直觉主义反对。

---

## §6 飞腾/Python 锚点
| 第6章概念 | 工程 |
|---------|------|
| ε-δ 连续 | 数值稳定性(输入小扰→输出小扰)|
| **Bolzano(IVT)** | **bisection 求根**(数值分析核心)|
| Weierstrass 极值 | 优化(最大值存在保证)|
| Bolzano-Weierstrass | 紧致(泛函分析的有限性替代)|

---

## §7 自测(基于原文)
1. 连续 ε-δ 与极限 ε-δ 的区别?(连续允许 $x=x_1$)
2. **Bolzano 证明**:二分+区间套为何推出 $f(\alpha)=0$?
3. Weierstrass 极值:反证 $f(s)>M$ 为何矛盾?
4. Bolzano-Weierstrass:有界序列为何有收敛子列?

---

## 📌 第 6 章 §1-§5 完成(主体)。续读 §6(Bolzano 应用)+ 第 7 章(极大极小)+ 第 8 章(微积分)+ 第 9 章(最新进展)
