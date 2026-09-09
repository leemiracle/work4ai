# Spivak 第 18 章 · The Logarithm and Exponential Functions · 精读笔记

> 基于原书第 18 章(PP.339-362)。与第 15 章(三角函数)呼应:**log/exp 也用积分+反函数定义**,完成"超越函数的 FTC 定义"三部曲。
> 原书:`Calculus (Spivak) 4th ed.` ch18 / 读于:2026-07-01

---

## §0 一句话

> **log x = ∫₁ˣ (1/t) dt(FTC 的直接产物);exp = log 的反函数;e = exp(1)。三个超越函数(log/exp/三角)全部从积分+反函数严格定义——零几何,零"直觉定义"。**

---

## §1 log 的积分定义(原书 PP.339-340)

### 定义
$$\log x = \int_1^x \frac{1}{t}\,dt,\quad x>0$$

### 用 FTC1 求导
$$\log'(x) = \frac{1}{x}$$
（FTC1:$\frac{d}{dx}\int_a^x f = f(x)$,这里 $f(t)=1/t$）

### 关键性质:log 变乘法为加法
$$\log(xy)=\log x+\log y$$
**证明**:固定 $x$,令 $g(y)=\log(xy)$。则 $g'(y)=\frac{1}{xy}\cdot x=\frac{1}{y}=\log'(y)$。由 MVT 推论($g'-\log'=0\Rightarrow$ 差常数),算 $y=1$:$g(1)=\log x=\log x+\log 1$($\log 1=0$)。∴ $g(y)=\log x+\log y$ ∎。

> 🔑 这个证明用 **MVT 推论**(第11章"$f'\equiv0\Rightarrow$常数")——又一次 LUB 的红利。

---

## §2 exp = log 的反函数(原书 PP.340-343)

### 定义
$\exp = \log^{-1}$($\log$ 严格增,故反函数存在,第12章)。

### 用反函数求导(第12章定理5)
$$(\log^{-1})'(x)=\frac{1}{\log'(\log^{-1}(x))}=\frac{1}{1/\exp(x)}=\exp(x)$$
∴ **$\exp'(x)=\exp(x)$** ——指数函数的标志性性质,从定义直接推出!

### 数 e
$$e=\exp(1),\quad\text{即}\log e=1$$
（$\int_1^e \frac{dt}{t}=1$）

### 指数记号
对任意实数 $a>0$,$x\in\mathbb{R}$:$a^x=\exp(x\log a)$。
- 这定义了"任意实数次幂",把高中"整数幂"推广到 $\mathbb{R}$
- $(a^x)'=a^x\log a$

---

## §3 三部曲统一(第 15-18 章)

| 函数族 | 定义方式 | 导数 |
|--------|---------|------|
| **三角**(第15章)| $\cos=A^{-1}$($A$=扇形面积积分)| $\cos'=-\sin$ |
| **对数**(第18章)| $\log x=\int_1^x 1/t$ | $\log'=1/x$ |
| **指数**(第18章)| $\exp=\log^{-1}$ | $\exp'=\exp$ |

> 🎯 **统一性**:所有"超越函数"都是 **FTC + 反函数** 的产物。Spivak 把高中分散的"sin/cos/log/exp"统一进一套严格语言——这是微积分严格化的最高成就之一。

---

## §4 飞腾/Python 锚点
| 概念 | 工程 |
|------|------|
| $\log x=\int 1/t$ | 数值对数(迭代算法)|
| $\exp'=\exp$ | ODE $y'=y$ 的解(种群增长/放射性衰变)|
| $e=\exp(1)$ | `math.e` 浮点近似;e 超越(第21章证)|
| $a^x=\exp(x\log a)$ | 任意底指数的硬件实现(都用 exp+log)|

> 💡 **深层**:CPU 算 $a^b$(任意实数)底层都是 $\exp(b\log a)$——Spivak 的定义就是硬件实现!飞腾 NEON 没有"任意幂指令",只有乘加;幂 = log+exp 的组合(都用泰勒/CORDIC 逼近,Expert_08)。

---

## §5 自测
1. 写出 $\log x$ 的积分定义,用 FTC1 证 $\log'=1/x$。
2. 证 $\log(xy)=\log x+\log y$(用 MVT 推论)。
3. 用反函数求导证 $\exp'=\exp$。
4. 为什么 $e=\exp(1)$?(即 $\int_1^e 1/t\,dt=1$)
5. **三部曲题**:sin/cos(第15)、log/exp(第18)都用"FTC+反函数"定义,这对"什么是严格数学定义"有什么启发?

---

## 📌 下一步
第 19 章(Integration in Elementary Terms:换元法/分部积分的技巧)+ 第 21 章(e 超越,⭐⭐最难章)+ 第 22-27 章(级数/复分析)。

> 🎯 第 15-18 章完成了"超越函数的严格化"。接下来第 22 章起的级数/复分析,会把这套严格性推向更深处。
