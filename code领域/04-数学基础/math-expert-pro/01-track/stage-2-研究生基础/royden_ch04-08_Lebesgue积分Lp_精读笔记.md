# Royden《实分析》第 4-8 章 · 可测函数/Lebesgue积分/微分/Lp · 精读笔记

> 基于原书第 3-8 章(5th ed. PP.51-156)。**Lebesgue 积分的核心**:三大收敛定理 + FTC 升级版 + Lp 空间。
> 原书:`Real Analysis (Royden 5e)` ch3-8 / 读于:2026-07-01

---

## §0 一句话

> **第3章可测函数(积分的对象)+ 第4章 Lebesgue 积分(三大收敛定理)+ 第6章 FTC 升级版(绝对连续)+ 第7-8章 Lp 空间(泛函分析入口)。这是现代分析的核心引擎。**

---

## §1 第 3 章:Lebesgue 可测函数(原书 PP.51-61)

### 可测函数
$f$ **可测** ⟺ $\{x:f(x)>a\}$ 对所有 $a$ 可测。
- 等价:$f$ 是 Borel 可测函数(可测集→Borel)
- 可测函数的和/积/复合(可测)仍可测
- 连续函数可测

### 简单函数逼近
任一非负可测 $f$ = 递增简单函数列 $\varphi_n\uparrow f$(逐点)
> 这是定义积分的跳板:先对简单函数积分,再取极限。

### Littlewood 三原理(英国数学家的直觉)
1. 每个可测集"几乎是"区间的有限并
2. 每个可测函数"几乎是"连续的(**Lusin 定理**)
3. 逐点收敛"几乎是"一致收敛(**Egoroff 定理**)

> 🎯 **Egoroff**:有限测度集上,$f_n\to f$ 逐点 ⟹ 几乎一致(去掉小测度集后一致)。

---

## §2 第 4 章:Lebesgue 积分(原书 PP.62-80)⭐⭐(Royden 皇冠)

### 三层定义
1. **简单函数** $\varphi=\sum c_k\chi_{E_k}$:$\int\varphi=\sum c_k m(E_k)$
2. **非负可测** $f$:$\int f=\sup\{\int\varphi:\varphi\le f,\varphi\text{ 简单}\}=\lim\int\varphi_n$
3. **一般可测** $f$:$\int f=\int f^+-\int f^-$(若至少一个有限)

### **三大收敛定理** ⭐⭐(积分与极限交换的条件)
| 定理 | 条件 | 结论 |
|------|------|------|
| **单调收敛 MCT** | $0\le f_n\uparrow f$ | $\int f_n\uparrow\int f$ |
| **Fatou 引理** | $f_n\ge0$ | $\int\liminf f_n\le\liminf\int f_n$ |
| **控制收敛 DCT** | $f_n\to f$,$\|f_n\|\le g$($g$ 可积) | $\int f_n\to\int f$ |

> 🔑 **DCT 是最实用的**:有"控制函数"就能交换极限与积分。这是现代分析的核心工具。

### 与 Riemann 积分对比(Spivak 第13章)
- Riemann:用区间分割(上下和),**Dirichlet 函数不可积**
- **Lebesgue**:用 σ-代数(可测集),**Dirichlet 函数可积**($\int=0$)
- Lebesgue 处理"更野"的函数(极限操作更自由)

---

## §3 第 6 章:微分与积分(原书 PP.92-118,FTC 升级版)

### 单调函数的微分
- **单调函数的不连续点可数**(第2章)
- **Lebesgue 微分定理**:单调函数**几乎处处可微**

### 有界变差与 Jordan 分解
$f$ 有界变差 ⟺ $f$ = 两单调增函数之差

### 绝对连续
$f$ 绝对连续 ⟺ $\forall\varepsilon,\exists\delta$,$\sum|E_k|<\delta\Rightarrow\sum|f(E_k)|<\varepsilon$
（比一致连续强,比 Lipschitz 弱)

### **FTC 的 Lebesgue 版(本节皇冠)**
$f$ 绝对连续 ⟺ $f$ 是其导数的 Lebesgue 积分:$f(x)=f(a)+\int_a^x f'$
> 🎯 **对比 Spivak 第14章 FTC**:Spivak 的 FTC 要求 $f$ 连续+ $F'=f$;Royden 升级为"绝对连续 ⟺ 积分其导数",更深刻。

---

## §4 第 7-8 章:Lp 空间(原书 PP.123-156,泛函分析入口)

### Lp 空间
$L^p([a,b])=\{f:\int|f|^p<\infty\}$,范数 $\|f\|_p=(\int|f|^p)^{1/p}$

### 三大不等式
- **Young**:$ab\le a^p/p+b^q/q$($1/p+1/q=1$)
- **Hölder**:$\int|fg|\le\|f\|_p\|g\|_q$
- **Minkowski**:$\|f+g\|_p\le\|f\|_p+\|g\|_p$(三角不等式)

### **完备性(Riesz-Fischer 定理)** ⭐
$L^p$ 是 **Banach 空间**(完备赋范空间):Cauchy 序列 ⟹ 收敛。
> 这是把柯朗第2章/Spivak第29章的"$\mathbb{R}$ 完备"推广到**函数空间**。

### 对偶(Riesz 表示)
$(L^p)^*=L^q$($1/p+1/q=1$,$1<p<\infty$):每个有界线性泛函 = 与某 $L^q$ 函数内积。
> 🎯 **量子力学/ML 核方法**的根基。

---

## §5 飞腾/Python 锚点
| Royden 概念 | 工程 |
|------------|------|
| 三大收敛定理 | 数值分析(极限交换合法性)|
| Lebesgue vs Riemann | 更强的数值积分(Expert_08)|
| Lp 完备 | 函数空间(信号处理/ML)|
| Hölder/Minkowski | 范数不等式(优化/ML)|
| 对偶 $(L^p)^*=L^q$ | 核方法/对偶优化(SVM)|

---

## §6 自测
1. 写出 Lebesgue 积分的三层定义(简单→非负→一般)。
2. **DCT** 的条件是什么?为何比 MCT 实用?
3. Lebesgue FTC:绝对连续 ⟺ 积分其导数。与 Spivak FTC 区别?
4. Riesz-Fischer:$L^p$ 为何完备?意义?
5. Hölder 不等式的 $p=q=2$ 特例是什么?(Cauchy-Schwarz)

---

## 📌 下一步
Royden Part II(一般测度:Radon-Nikodym/Fubini)+ Part III(度量/拓扑/Banach/Hilbert 空间)。然后 stage-2 其他书:Dummit 抽代 + Munkres 拓扑。
