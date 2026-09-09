# GKP《具体数学》第 1-5 章 · 递归/求和/整数函数/数论/二项式 · 精读笔记

> 基于原书第 1-5 章(PP.1-180)。脚手架 `discrete_01/02` 覆盖概念,本笔记补 **Knuth 的"数学体操"风格 + 有限微积分**。
> 原书:`Concrete Mathematics (Knuth/Graham/Patashnik 2e)` ch1-5 / 读于:2026-07-01

---

## §0 一句话

> **"Concrete = CONtinuous + disCRETE"(连续+离散)。GKP 教算法分析所需的精确数学:递归求解、求和技巧、整数取整、数论、二项式。这是 CS 的"内功心法"。**

---

## §1 第 1 章:递归问题(原书 PP.1-20)

### 三大经典递归
| 问题 | 递推 | 通解 |
|------|------|------|
| **河内塔** | $T_n=2T_{n-1}+1$ | $T_n=2^n-1$ |
| **直线分割平面** | $L_n=L_{n-1}+n$ | $L_n=n(n+1)/2+1$ |
| **约瑟夫问题** | $J(2n)=2J(n)-1$ | $J(2^m+l)=2l+1$ |

### 方法论
- 猜测 + 归纳证明
- 展开/代换/扰动

---

## §2 第 2 章:求和(原书 PP.21-60,本章核心)

### 求和记号
$\sum_{k=a}^b f(k)$,边界处理($b<a$ 为空和 0)

### **扰动法(Perturbation Method)** ⭐
拆 $\sum_{0}^n=\sum_0^{n-1}+f(n)$,又 $=\sum_1^n+f(0)$,令两式相等解 $S_n$。
- 例:GP $S_n=\sum r^k$,扰动得 $S_n=(r^{n+1}-1)/(r-1)$

### 多重和
$\sum\sum$、交换求和序(关键技巧)

### **有限微积分(Finite Calculus)** ⭐⭐(GKP 招牌)
- 差分 $\Delta f(x)=f(x+1)-f(x)$(类比导数)
- **逆差分/求和** $\sum f = g$ 使得 $\Delta g=f$(类比积分)
- $x^{\underline{n}}=x(x-1)\cdots(x-n+1)$(下降幂)类比 $x^n$
- $\Delta x^{\underline{n}}=n\cdot x^{\underline{n-1}}$(类比 $\frac{d}{dx}x^n=nx^{n-1}$)

> 🎯 **精髓**:离散求和 = 连续积分的"有限版"。Faulhaber 公式 $\sum k^p$ 用下降幂简洁表达。

---

## §3 第 3 章:整数函数(原书 PP.67-100)

### 取整 $\lfloor x\rfloor$(地板)与 $\lceil x\rceil$(天花板)
- $\lfloor x\rfloor\le x<\lfloor x\rfloor+1$
- 互异性:$\lfloor x\rfloor=\lceil x\rceil \iff x\in\mathbb{Z}$

### 关键恒等式
- $\lfloor x+n\rfloor=\lfloor x\rfloor+n$($n\in\mathbb{Z}$)
- $\lfloor\lfloor x/m\rfloor/n\rfloor=\lfloor x/(mn)\rfloor$

### 取整和 $\sum_{0\le k<n}\lfloor f(k)\rfloor$
GKP 给出系统求法(数格点)。

---

## §4 第 4 章:数论(原书 PP.102-150)

### 整除与 gcd
- $a|b$ ⟹ 存在 $k$,$b=ak$
- $\gcd(a,b)$ + Bezout $=ma+nb$

### 同余
$a\equiv b\pmod m$ ⟹ $m|(a-b)$
- 费马小定理、欧拉定理

### 素数
- 唯一分解
- 素数无穷(Euclid)

### 连分数
无理数 → 连分数展开(最佳有理逼近)

---

## §5 第 5 章:二项式系数(原书 PP.150-180)

### 定义
$\binom{r}{k}=\frac{r^{\underline{k}}}{k!}=\frac{r(r-1)\cdots(r-k+1)}{k!}$($r$ 可为任意实数)

### 帕斯卡递推
$\binom{n}{k}=\binom{n-1}{k}+\binom{n-1}{k-1}$

### 关键恒等式
- **Vandermonde**:$\sum_k\binom{r}{k}\binom{s}{n-k}=\binom{r+s}{n}$
- 上指标求和:$\sum_{k\le n}\binom{k}{m}=\binom{n+1}{m+1}$

---

## §6 飞腾/Python 锚点
| GKP 概念 | 工程 |
|---------|------|
| 递归求解 | 算法复杂度(分治/递归)|
| 求和技巧 | 程序循环的分析 |
| **有限微积分** | 符号求和(SymPy)|
| floor/ceil | 量化/索引计算 |
| 数论 | 密码学(RSA,与柯朗第1章呼应)|
| 二项式系数 | 组合优化/编码理论 |

---

## §7 自测
1. 解河内塔递推 $T_n=2T_{n-1}+1$(展开法)。
2. 用扰动法求 $\sum_{k=0}^n k2^k$ 的闭式(答案:$(n-1)2^{n+1}+2$)。
3. **有限微积分**:$\Delta x^{\underline{3}}=?$(类比 $\frac{d}{dx}x^3$)
4. 证 $\lfloor\lfloor x/m\rfloor/n\rfloor=\lfloor x/(mn)\rfloor$。
5. Vandermonde 恒等式的组合意义?

---

## 📌 下一步
第 6-9 章:特殊数(Stirling/Fibonacci)+ **生成函数** + 离散概率 + 渐近——GKP 的后半程。
