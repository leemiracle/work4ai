# ch02 练习题：数系

> 阶段 1 / 模块 01 / 第 2 章
> 完成标准：3 题跑通 + 能讲清证明
> **铁律**：先自己写，跑不通再看答案。

---

## 📝 题 1：√3 无理——反证法迁移（基础，15 分钟）

### 题目

模仿 §2 √2 的反证法，证明 **$\sqrt{3}$ 不是有理数**。

**提示**：
- 假设 $\sqrt{3} = p/q$（既约）
- $3q^2 = p^2$ → $p^2$ 是 3 的倍数 → $p$ 是 3 的倍数（**关键引理**：若 $3 \mid p^2$ 则 $3 \mid p$）
- 设 $p = 3k$，代入 → $q^2 = 3k^2$ → 同理 $q$ 是 3 的倍数 → 矛盾

**你的任务**：
1. **手写完整证明**（关键是"若 $3 \mid p^2$ 则 $3 \mid p$"，这要用到素数性质）。
2. **程序验证**：找 $q \le 10000$ 最佳有理逼近 $p/q$，确认误差永不为 0。
3. **思考题**：为什么 $\sqrt{4} = 2$ 是有理？反证法在哪一步失败？（提示：4 不是素数）

### 期望输出

```
√3 ≈ 1.7320508
q≤10000 最佳逼近: p/q, 误差 ~1e-9 (永不=0)
反证法: 假设 → p²=3q² → 3|p → p=3k → q²=3k² → 3|q → 矛盾 √3 无理
√4=2: 因为 4=2², p²=4q² → p=2q 直接可解, 不产生矛盾
```

---

## 📝 题 2：Mandelbrot 分形——复数迭代（视觉震撼，25 分钟）

### 题目

复数最神奇的工程：**Mandelbrot 集**。对复平面每个点 $c$，迭代
$$z_0 = 0, \quad z_{n+1} = z_n^2 + c$$
若 $|z_n|$ 永远有界（不发散到 ∞），则 $c$ 属于 Mandelbrot 集。

**你的任务**：
1. 实现迭代：对每个 $c$，迭代至 $|z| > 2$ 或达到最大次数（如 100），记录逃逸时间。
2. 在复平面 $[-2, 1] \times [-1.5, 1.5]$ 上采样（如 500×500），用逃逸时间染色。
3. 画出分形（你会看到一个著名的"心形 + 圆盘"结构，无限自相似）。
4. **思考题**：Mandelbrot 集的边界是几维的？（提示：分形维数，介于 1 和 2 之间）

### 提示

```python
def mandelbrot(c, max_iter=100):
    z = 0
    for n in range(max_iter):
        if abs(z) > 2: return n      # 逃逸时间
        z = z*z + c
    return max_iter                  # 没逃逸 → 在集合内
# 复平面采样: c = re + im*1j
```
- 用 numpy 向量化加速（对每个 c 同时算），否则 500×500 太慢
- 染色用 `plt.imshow`，cmap 用 'hot' 或 'magma'

### 期望观察

```
画出一个边界无限复杂的分形
心形主体 + 圆盘 + 无数自相似的小芽苞
"数学里最复杂的对象" — Mandelbrot 1980
边界分形维数 = 2 (Mandelbrot 集是"填充"的, 边界极其复杂)
```

> 💡 这就是"复数 + 程序"的威力：一条 $z^2+c$ 的简单规则，生成无限复杂的美。

---

## 📝 题 3：实数完备性 vs 有理数（深度，20 分钟）

### 题目

实数比有理数多了一个核心性质：**完备性**（每个有界单调数列收敛）。
有理数不完备——例如 $\sqrt{2}$ 的连分数逼近是有理数列，但它"收敛"到不在有理数里的 √2。

**你的任务**：
1. 构造一个**有理数列** $a_n$，它单调递增且有上界，但极限不在 $\mathbb{Q}$：
   - 用巴比伦法（牛顿法）逼近 $\sqrt{2}$：$a_{n+1} = (a_n + 2/a_n)/ 2$，从 $a_0 = 1$ 开始
   - 验证每个 $a_n$ 是有理数，且 $a_n \to \sqrt{2} \notin \mathbb{Q}$
2. 画 $a_n$ 收敛曲线，标注"极限 √2 不是有理数"。
3. **思考题**：为什么"完备性"重要？（提示：微积分的根基。没有完备性，极限不存在，导数/积分无法严格定义。这是 Spivak 第 8 章「最小上界」要解决的核心问题。）

### 提示

```python
from fractions import Fraction
a = Fraction(1)   # a_0 = 1
two = Fraction(2)
seq = [a]
for _ in range(10):
    a = (a + two / a) / 2     # 牛顿迭代 (全是精确有理运算!)
    seq.append(a)
# 每个 a_n 是有理数, 但 seq → √2 (无理)
```

### 期望观察

```
a_0 = 1
a_1 = 3/2 = 1.5
a_2 = 17/12 ≈ 1.41667
a_3 = 577/408 ≈ 1.414216
...
单调递减 (从上方逼近), 有下界 (≥1), 极限 = √2 (无理)
→ 有理数不完备 (序列在有理数系内"没有极限")
→ 必须扩张到实数 (完备化)
```

**思考题答案**：完备性是**微积分的严格根基**。没有它，"极限"可能不存在（如上述有理数列），导数/积分的定义崩溃。Spivak《Calculus》第 8 章用"最小上界原理"补上这一刀——这就是为什么实分析要从完备性讲起。

---

## 🔑 参考答案（做完再看！）

<details>
<summary>👉 点击展开题 1 答案</summary>

**反证法**：假设 $\sqrt{3} = p/q$（既约）。则 $p^2 = 3q^2$，故 $3 \mid p^2$。
由素数性质（3 是素数），$3 \mid p^2 \Rightarrow 3 \mid p$，故 $p = 3k$。
代入：$9k^2 = 3q^2 \Rightarrow q^2 = 3k^2$，同理 $3 \mid q$。
但 $p, q$ 都被 3 整除与既约矛盾。$\sqrt{3}$ 无理。$\blacksquare$

```python
import numpy as np
best=None; best_err=1
for q in range(1,10001):
    p = round(np.sqrt(3)*q)
    err = abs(p/q - np.sqrt(3))
    if err < best_err: best_err=err; best=(p,q)
print(f"√3 最佳逼近 {best[0]}/{best[1]}, 误差 {best_err:.2e}")
```
**√4 失败原因**：$p^2 = 4q^2 \Rightarrow p = 2q$，直接有理解 $p/q = 2$，无矛盾。因为 4 = 2² 是完全平方。**关键**：反证法依赖"素数 p | n² ⟹ p | n"，4 不是素数故不适用。

</details>

<details>
<summary>👉 点击展开题 2 答案</summary>

```python
import numpy as np
import matplotlib.pyplot as plt
N = 500
re = np.linspace(-2.0, 1.0, N)
im = np.linspace(-1.5, 1.5, N)
Re, Im = np.meshgrid(re, im)
C = Re + 1j*Im
Z = np.zeros_like(C)
escape = np.full(C.shape, 100, dtype=int)
for n in range(100):
    mask = np.abs(Z) <= 2
    Z[mask] = Z[mask]**2 + C[mask]
    escaped_now = mask & (np.abs(Z) > 2)
    escape[escaped_now] = n
plt.figure(figsize=(8, 8))
plt.imshow(escape, extent=[-2, 1, -1.5, 1.5], cmap='magma', origin='lower')
plt.colorbar(label='逃逸时间 (越亮越慢逃)')
plt.title('Mandelbrot 集: z² + c 的复数迭代\n数学里最复杂的对象 — 边界无限自相似')
plt.xlabel('Re(c)'); plt.ylabel('Im(c)')
plt.savefig('mandelbrot.png', dpi=120, bbox_inches='tight')
```
**分形维数**：Mandelbrot 集边界维数 = 2（Shishikura 1991 证明），意味着边界"几乎填满平面"——这就是它视觉上无限复杂的原因。

</details>

<details>
<summary>👉 点击展开题 3 答案</summary>

```python
from fractions import Fraction
import numpy as np
import matplotlib.pyplot as plt
a = Fraction(1); two = Fraction(2)
seq = [a]
for _ in range(10):
    a = (a + two / a) / 2
    seq.append(a)
print("n  a_n (有理)              十进制            |a_n - √2|")
for i, s in enumerate(seq):
    print(f"{i}  {s}   {float(s):.10f}   {abs(float(s)-np.sqrt(2)):.2e}")
plt.figure(figsize=(8,4))
plt.plot(range(len(seq)), [float(s) for s in seq], 'o-', label='a_n (有理数列)')
plt.axhline(np.sqrt(2), color='r', ls='--', label=f'极限 √2 ≈ {np.sqrt(2):.6f} (无理, 不在 Q 内)')
plt.xlabel('n'); plt.ylabel('a_n'); plt.legend()
plt.title('巴比伦法逼近 √2: 有理数列收敛到无理数\n→ 有理数不完备, 必须扩张到实数')
plt.grid(True, ls=':', alpha=0.3); plt.savefig('babylon_sqrt2.png', dpi=100, bbox_inches='tight')
```

</details>

---

## ✅ 完成检查表

- [ ] 题 1 手证 √3 无理（迁移反证法）
- [ ] 题 2 画出 Mandelbrot 分形，看到自相似
- [ ] 题 3 牛顿法逼近 √2，理解有理数不完备
- [ ] 能讲清"为什么实数完备性是微积分根基"

**全部 ✓ = 第 2 章过关**。

---

## 📌 完成后

回 `ch02-数系.md` §8 自测，出声回答 7 题。
然后决定：继续《什么是数学》第 3 章（几何作图），或直接进 **Spivak《Calculus》第 1 章**（阶段 1 灵魂）。
