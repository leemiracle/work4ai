# Topic 02 · 电磁学（MIT 8.02 / 8.022 / 8.07）

> **教材**：Purcell & Morin《Electricity and Magnetism》3ed + Griffiths《Introduction to Electrodynamics》4ed
>
> **覆盖课程**：
> - **8.02** Physics II（普通电磁学，Young & Freedman）
> - **8.022** Physics II Honors（Purcell，从相对论导出磁场）
> - **8.07** Electromagnetism II（Griffiths 全本，含辐射）
>
> **宪法**：直觉 → 公式 → 代码(bash 跑通) → 不足 → 应用

---

## 目录

1. [静电学（高斯定律）](#1-静电学)
2. [静磁学](#2-静磁学)
3. [麦克斯韦方程组](#3-麦克斯韦方程组)
4. [电磁波](#4-电磁波)
5. [辐射（Lienard-Wiechert 势）](#5-辐射--lienard-wiechert-势)
6. [Python 代码演示](#6-python-代码演示)
7. [习题与解答](#7-习题与解答)
8. [反直觉发现](#8-反直觉发现)
9. [不足与延伸](#9-不足与延伸)

---

## 1. 静电学

### 1.1 库仑定律

两个点电荷 $q_1, q_2$ 距离 $r$：

$$
\mathbf{F}_{12} = \frac{1}{4\pi\epsilon_0}\frac{q_1 q_2}{r^2}\hat{\mathbf{r}}_{12}
$$

这是平方反比律——与牛顿万有引力 $\propto 1/r^2$ 同构，但电力比引力强 $10^{36}$ 倍。

### 1.2 电场

定义**电场**（单位试探电荷受的力）：

$$
\mathbf{E}(\mathbf{r}) = \frac{1}{4\pi\epsilon_0}\int \frac{\rho(\mathbf{r}')(\mathbf{r}-\mathbf{r}')}{|\mathbf{r}-\mathbf{r}'|^3}\, d^3r'
$$

其中 $\rho$ 是电荷体密度。点电荷 $q$ 产生的电场 $\mathbf{E} = \frac{q}{4\pi\epsilon_0 r^2}\hat{\mathbf{r}}$。

### 1.3 高斯定律（积分形式）

**电场穿过任意闭合曲面的通量等于内部总电荷除 $\epsilon_0$**：

$$
\boxed{\oint_S \mathbf{E}\cdot d\mathbf{A} = \frac{Q_{\text{enc}}}{\epsilon_0}}
$$

这是麦克斯韦方程组的第一式。它的几何意义是：**电场线从正电荷发出、到负电荷终止**。

**微分形式**（用散度定理）：

$$
\nabla \cdot \mathbf{E} = \frac{\rho}{\epsilon_0}
$$

### 1.4 用对称性求解：无限长带电线

考虑线电荷密度 $\lambda$ 的无限长直线。由柱对称，电场只能径向，大小只依赖距离 $r$。取半径 $r$、长 $L$ 的圆柱高斯面：

$$
E \cdot (2\pi r L) = \frac{\lambda L}{\epsilon_0} \implies E = \frac{\lambda}{2\pi\epsilon_0 r}
$$

注意是 $1/r$（不是 $1/r^2$）——**维度的"残缺"改变了衰减幂次**。

### 1.5 电势

静电场是**无旋场**（$\nabla\times\mathbf{E} = 0$），故可写为标量势的梯度：

$$
\mathbf{E} = -\nabla V, \qquad V(\mathbf{r}) = \frac{1}{4\pi\epsilon_0}\int \frac{\rho(\mathbf{r}')}{|\mathbf{r}-\mathbf{r}'|}\, d^3r'
$$

代入高斯定律得**泊松方程**：

$$
\nabla^2 V = -\frac{\rho}{\epsilon_0}
$$

### 1.6 导体

静电平衡下导体内 $\mathbf{E} = 0$，电荷全在表面。表面边界条件：

$$
E_\perp = \frac{\sigma}{\epsilon_0}, \qquad E_\parallel = 0
$$

---

## 2. 静磁学

### 2.1 毕奥-萨伐尔定律

电流元 $Id\mathbf{l}'$ 在 $\mathbf{r}$ 处产生的磁场：

$$
d\mathbf{B} = \frac{\mu_0}{4\pi}\frac{Id\mathbf{l}'\times (\mathbf{r}-\mathbf{r}')}{|\mathbf{r}-\mathbf{r}'|^3}
$$

### 2.2 安培定律（积分形式）

**磁场沿闭合回路的环量等于穿过该回路的总电流乘 $\mu_0$**：

$$
\boxed{\oint_C \mathbf{B}\cdot d\mathbf{l} = \mu_0 I_{\text{enc}}}
$$

**微分形式**：

$$
\nabla \times \mathbf{B} = \mu_0 \mathbf{J}
$$

### 2.3 磁场没有单极

$$
\nabla \cdot \mathbf{B} = 0
$$

磁场线**没有起点也没有终点**（无磁单极）。这等价于 $\mathbf{B} = \nabla\times\mathbf{A}$ 可用**矢势** $\mathbf{A}$ 表达。

### 2.4 Purcell 的相对论视角（8.022 特色）

**磁场本质上是电场在运动参考系下的相对论效应**。考虑两根平行载流导线，在导线静止系中看到的是磁场力。但换成沿导线运动的参考系，正负电荷的洛伦兹收缩不同，**纯电场**就能解释吸引力——磁场只是"运动参照系下的电场修正"。

定量：$\mu_0\epsilon_0 = 1/c^2$ 正是这个相对论起源的烙印。

### 2.5 磁偶极子

电流环的磁偶极矩 $\mathbf{m} = I\mathbf{a}$（$\mathbf{a}$ 是面积矢量），远场：

$$
\mathbf{B}_{\text{dip}} = \frac{\mu_0}{4\pi}\frac{1}{r^3}\left[2(\mathbf{m}\cdot\hat{\mathbf{r}})\hat{\mathbf{r}} - \mathbf{m}\right]
$$

形式与电偶极场完全相同——这是 $1/r^3$ 衰减。

---

## 3. 麦克斯韦方程组

### 3.1 四个方程

这是整个经典电磁学的全部——一行写完：

$$
\boxed{
\begin{aligned}
\text{(i)}\quad &\nabla \cdot \mathbf{E} = \frac{\rho}{\epsilon_0} & \text{高斯定律} \\
\text{(ii)}\quad &\nabla \cdot \mathbf{B} = 0 & \text{无磁单极} \\
\text{(iii)}\quad &\nabla \times \mathbf{E} = -\frac{\partial \mathbf{B}}{\partial t} & \text{法拉第定律} \\
\text{(iv)}\quad &\nabla \times \mathbf{B} = \mu_0\mathbf{J} + \mu_0\epsilon_0\frac{\partial \mathbf{E}}{\partial t} & \text{安培-麦克斯韦定律}
\end{aligned}}
$$

### 3.2 麦克斯韦的伟大修补（iv 式的位移电流）

**原始安培定律 $\nabla\times\mathbf{B} = \mu_0\mathbf{J}$ 有缺陷**：对电容器充电的回路取安培环路，包围导线的曲面 $S_1$ 给出 $\oint\mathbf{B}\cdot d\mathbf{l} = \mu_0 I$，但换一张穿过电容器内部的曲面 $S_2$（无电流穿过），给出 $0$ ——矛盾。

麦克斯韦加上**位移电流** $\mu_0\epsilon_0 \partial\mathbf{E}/\partial t$ 修补：

$$
\nabla\times\mathbf{B} = \mu_0\mathbf{J} + \mu_0\epsilon_0\frac{\partial\mathbf{E}}{\partial t}
$$

这一项让方程自洽，**且预言了电磁波**。

### 3.3 势函数表示

引入标势 $\varphi$ 和矢势 $\mathbf{A}$：

$$
\mathbf{B} = \nabla\times\mathbf{A}, \qquad \mathbf{E} = -\nabla\varphi - \frac{\partial\mathbf{A}}{\partial t}
$$

（这自动满足 (ii) 和 (iii)。）在**洛伦兹规范** $\nabla\cdot\mathbf{A} + \frac{1}{c^2}\frac{\partial\varphi}{\partial t} = 0$ 下，麦克斯韦方程组解耦为**波动方程**：

$$
\left(\nabla^2 - \frac{1}{c^2}\frac{\partial^2}{\partial t^2}\right)\varphi = -\frac{\rho}{\epsilon_0}, \qquad
\left(\nabla^2 - \frac{1}{c^2}\frac{\partial^2}{\partial t^2}\right)\mathbf{A} = -\mu_0\mathbf{J}
$$

其中 $c = 1/\sqrt{\mu_0\epsilon_0} \approx 3\times 10^8$ m/s——**电学常数给出光速**，麦克斯韦由此预言光是电磁波。

---

## 4. 电磁波

### 4.1 真空中的波方程

无源（$\rho = 0, \mathbf{J} = 0$）时取 (iii) 的旋度，代入 (iv)：

$$
\nabla\times(\nabla\times\mathbf{E}) = -\frac{\partial}{\partial t}(\nabla\times\mathbf{B}) = -\mu_0\epsilon_0\frac{\partial^2\mathbf{E}}{\partial t^2}
$$

用 $\nabla\times(\nabla\times) = \nabla(\nabla\cdot) - \nabla^2$ 和 $\nabla\cdot\mathbf{E}=0$：

$$
\nabla^2 \mathbf{E} = \mu_0\epsilon_0\frac{\partial^2 \mathbf{E}}{\partial t^2} = \frac{1}{c^2}\frac{\partial^2\mathbf{E}}{\partial t^2}
$$

同理 $\nabla^2\mathbf{B} = \frac{1}{c^2}\partial_t^2\mathbf{B}$。

### 4.2 平面波解

$$
\mathbf{E}(\mathbf{r}, t) = \mathbf{E}_0 e^{i(\mathbf{k}\cdot\mathbf{r} - \omega t)}, \qquad \omega = c|\mathbf{k}|
$$

由 $\nabla\cdot\mathbf{E}=0$ 知 $\mathbf{k}\cdot\mathbf{E}_0 = 0$（横波）。法拉第定律给出：

$$
\mathbf{B} = \frac{1}{\omega}\mathbf{k}\times\mathbf{E}
$$

$\mathbf{E}, \mathbf{B}, \mathbf{k}$ 两两正交，且 $|\mathbf{B}| = |\mathbf{E}|/c$。

### 4.3 坡印廷矢量与能量流

电磁场携带能量，**能流密度**（单位时间单位面积的能量）：

$$
\mathbf{S} = \frac{1}{\mu_0}\mathbf{E}\times\mathbf{B}
$$

能量守恒（坡印廷定理）：

$$
\frac{\partial}{\partial t}\left(\frac{\epsilon_0 E^2}{2} + \frac{B^2}{2\mu_0}\right) + \nabla\cdot\mathbf{S} = -\mathbf{J}\cdot\mathbf{E}
$$

右端是场对电荷做功（焦耳热的负值）。

---

## 5. 辐射 — Lienard-Wiechert 势

### 5.1 推迟势

电磁场以光速传播，所以 $t$ 时刻 $\mathbf{r}$ 处的场来自**推迟时刻** $t_r = t - |\mathbf{r}-\mathbf{r}'|/c$ 的源。推迟势：

$$
\varphi(\mathbf{r}, t) = \frac{1}{4\pi\epsilon_0}\int \frac{\rho(\mathbf{r}', t_r)}{|\mathbf{r}-\mathbf{r}'|}\, d^3r', \quad
\mathbf{A}(\mathbf{r}, t) = \frac{\mu_0}{4\pi}\int \frac{\mathbf{J}(\mathbf{r}', t_r)}{|\mathbf{r}-\mathbf{r}'|}\, d^3r'
$$

### 5.2 运动点电荷的 Lienard-Wiechert 势

对以任意轨迹 $\mathbf{w}(t)$ 运动的点电荷 $q$，推迟位置 $\mathbf{w}_r = \mathbf{w}(t_r)$：

$$
\varphi(\mathbf{r}, t) = \frac{q}{4\pi\epsilon_0}\frac{1}{(\mathcal{R} - \boldsymbol{\mathcal{R}}\cdot\boldsymbol{\beta})}, \quad
\mathbf{A}(\mathbf{r}, t) = \frac{\mu_0 c}{4\pi}\frac{q\boldsymbol{\beta}}{(\mathcal{R} - \boldsymbol{\mathcal{R}}\cdot\boldsymbol{\beta})}
$$

其中 $\boldsymbol{\mathcal{R}} = \mathbf{r} - \mathbf{w}_r$，$\mathcal{R} = |\boldsymbol{\mathcal{R}}|$，$\boldsymbol{\beta} = \dot{\mathbf{w}}(t_r)/c$。

### 5.3 辐射场

远场（$r\to\infty$）中，$\mathbf{E}$ 的辐射部分（$\propto 1/r$，能量不衰减）：

$$
\mathbf{E}_{\text{rad}} = \frac{q}{4\pi\epsilon_0 c}\frac{\hat{\boldsymbol{\mathcal{R}}}\times[(\hat{\boldsymbol{\mathcal{R}}}-\boldsymbol{\beta})\times\dot{\boldsymbol{\beta}}]}{(1 - \hat{\boldsymbol{\mathcal{R}}}\cdot\boldsymbol{\beta})^3 \mathcal{R}}
$$

辐射功率（Larmor 公式的相对论推广，**Liénard 公式**）：

$$
P = \frac{q^2}{6\pi\epsilon_0 c}\gamma^6\left[\dot{\beta}^2 - (\boldsymbol{\beta}\times\dot{\boldsymbol{\beta}})^2\right]
$$

**重要极限**：
- 非相对论 $\beta \ll 1$：还原 **Larmor 公式** $P = \frac{q^2 a^2}{6\pi\epsilon_0 c^3}$。
- 圆周运动（同步辐射）：$P = \frac{q^2 c}{6\pi\epsilon_0}\frac{\gamma^4}{R^2}$，正比 $\gamma^4$——这是为什么电子储存环要消耗兆瓦电力维持能量。

---

## 6. Python 代码演示

### 6.1 电偶极子场线

```python
"""
电偶极子场线可视化
零依赖：numpy + matplotlib
"""
import numpy as np
import matplotlib.pyplot as plt

def dipole_field(X, Y, d=0.5, q=1.0):
    """两个点电荷 +q 在 (0, d/2), -q 在 (0, -d/2)"""
    r1 = np.sqrt(X**2 + (Y - d/2)**2 + 1e-6)
    r2 = np.sqrt(X**2 + (Y + d/2)**2 + 1e-6)
    Ex = q * X / r1**3 - q * X / r2**3
    Ey = q * (Y - d/2) / r1**3 - q * (Y + d/2) / r2**3
    return Ex, Ey

x = np.linspace(-2, 2, 200)
y = np.linspace(-2, 2, 200)
X, Y = np.meshgrid(x, y)
Ex, Ey = dipole_field(X, Y)
E_mag = np.sqrt(Ex**2 + Ey**2)

fig, ax = plt.subplots(figsize=(7, 7))
# 用 log 压缩避免奇点处爆炸
stream = ax.streamplot(X, Y, Ex, Ey, color=np.log10(E_mag + 1e-3),
                       cmap='inferno', density=2.0, linewidth=1.0)
ax.plot(0, 0.25, 'ro', markersize=10, label='+q')
ax.plot(0, -0.25, 'bo', markersize=10, label='-q')
ax.set_xlim(-2, 2); ax.set_ylim(-2, 2)
ax.set_aspect('equal'); ax.legend()
ax.set_title('电偶极子电场线（红=正电荷, 蓝=负电荷）')
plt.tight_layout()
plt.savefig('dipole_field.png', dpi=110, bbox_inches='tight')
print("已保存 dipole_field.png")
```

### 6.2 电磁波传播动画帧

```python
"""
线偏振电磁波 E, B 同步传播快照
"""
import numpy as np
import matplotlib.pyplot as plt

z = np.linspace(0, 4*np.pi, 500)
t_snapshots = [0, np.pi/4, np.pi/2, 3*np.pi/4]
omega = 1.0; k = 1.0

fig, axes = plt.subplots(4, 1, figsize=(10, 10), sharex=True)
for ax, t in zip(axes, t_snapshots):
    E = np.cos(k*z - omega*t)
    B = np.cos(k*z - omega*t)
    ax.plot(z, E, 'r-', linewidth=2, label='E (y 方向)')
    ax.plot(z, B, 'b--', linewidth=2, label='B (x 方向)')
    ax.set_ylabel('振幅'); ax.legend(loc='upper right')
    ax.set_title(f't = {t:.2f}')
    ax.grid(alpha=0.3); ax.set_ylim(-1.2, 1.2)
axes[-1].set_xlabel('z (传播方向)')
fig.suptitle('线偏振电磁波：E ⊥ B ⊥ k，E、B、k 成右手系', fontsize=13)
plt.tight_layout()
plt.savefig('em_wave.png', dpi=110, bbox_inches='tight')
print("已保存 em_wave.png")
print(f"E 与 B 同相位，|B| = |E|/c（此处归一化为同幅）")
```

---

## 7. 习题与解答

### 习题 1（高斯定律）— 均匀带电球

半径 $R$、总电荷 $Q$ 均匀分布的球，求球内外电场。

**解**：球对称 → 取同心球面高斯面。

球内 ($r < R$)：$Q_{\text{enc}} = Q\cdot\frac{r^3}{R^3}$，故：

$$
E \cdot 4\pi r^2 = \frac{Q r^3/R^3}{\epsilon_0} \implies E_{\text{in}} = \frac{Qr}{4\pi\epsilon_0 R^3}
$$

球外 ($r > R$)：如同全部电荷集中在球心：

$$
E_{\text{out}} = \frac{Q}{4\pi\epsilon_0 r^2}
$$

在 $r = R$ 处衔接：$E_{\text{in}}(R) = Q/(4\pi\epsilon_0 R^2) = E_{\text{out}}(R)$ ✓。

### 习题 2（电势）— 偶极子的远场势

电偶极矩 $\mathbf{p} = q\mathbf{d}$，求远场电势。

**解**：$V = \frac{q}{4\pi\epsilon_0}\left(\frac{1}{|\mathbf{r}-\mathbf{d}/2|} - \frac{1}{|\mathbf{r}+\mathbf{d}/2|}\right)$。

远场 $r \gg d$，泰勒展开 $\frac{1}{|\mathbf{r}\mp\mathbf{d}/2|} \approx \frac{1}{r} \pm \frac{\mathbf{d}\cdot\hat{\mathbf{r}}}{2r^2}$：

$$
V \approx \frac{q\mathbf{d}\cdot\hat{\mathbf{r}}}{4\pi\epsilon_0 r^2} = \frac{\mathbf{p}\cdot\hat{\mathbf{r}}}{4\pi\epsilon_0 r^2}
$$

这是 $1/r^2$ 衰减——比点电荷 $1/r$ 快两级。

### 习题 3（安培定律）— 无限长螺线管

半径 $R$、单位长度匝数 $n$、电流 $I$ 的无限长螺线管，求磁场。

**解**：理想螺线管外 $B=0$（轴向对称，沿矩形回路跨内外侧，外侧 $\oint = 0$）。取内部矩形回路（长 $l$，跨 $N = nl$ 匝）：

$$
B \cdot l = \mu_0 n l I \implies B_{\text{in}} = \mu_0 n I
$$

**内部均匀**！这是磁屏蔽、MRI 主磁场线圈的设计基础。

### 习题 4（法拉第定律）— 圆环中的感生电动势

半径 $a$ 的圆环，处在均匀磁场 $B(t) = B_0 + \alpha t$ 中（磁场垂直于环面），求感生电动势。

**解**：

$$
\mathcal{E} = -\frac{d\Phi}{dt} = -\frac{d}{dt}(\pi a^2 B) = -\pi a^2 \alpha
$$

感生电场沿环切向 $E_\theta \cdot 2\pi a = \mathcal{E}$，故 $E_\theta = -\frac{a\alpha}{2}$。

**关键**：磁场变化产生**涡旋电场**（$\nabla\times\mathbf{E} = -\partial\mathbf{B}/\partial t \neq 0$），这是无源场的电场——与静电场本质不同。

### 习题 5（位移电流）— 电容器内磁场

平行板电容器圆形极板半径 $a$，充电电流 $I$。求极板间 $r < a$ 处磁场。

**解**：极板间无传导电流，但有位移电流。电场 $E = Q/(\pi a^2\epsilon_0)$，$dE/dt = I/(\pi a^2\epsilon_0)$。安培-麦克斯韦定律：

$$
B \cdot 2\pi r = \mu_0\epsilon_0 \frac{dE}{dt} \cdot \pi r^2 = \mu_0 \frac{Ir^2}{\pi a^2}
$$

$$
B = \frac{\mu_0 I r}{2\pi a^2}
$$

形式与导线内磁场一致——位移电流"延续"了导线的磁场，麦克斯韦修补的胜利。

### 习题 6（平面波）— 能量密度

真空中平面电磁波 $E = E_0\cos(kz - \omega t)\hat{x}$。求坡印廷矢量的时间平均。

**解**：$B = E_0/c \cos(kz - \omega t)\hat{y}$。

$$
\mathbf{S} = \frac{1}{\mu_0}\mathbf{E}\times\mathbf{B} = \frac{E_0^2}{\mu_0 c}\cos^2(kz-\omega t)\hat{z}
$$

时间平均 $\langle\cos^2\rangle = 1/2$，用 $\mu_0 c = 1/(\epsilon_0 c)$：

$$
\langle \mathbf{S} \rangle = \frac{E_0^2}{2\mu_0 c}\hat{z} = \frac{\epsilon_0 c E_0^2}{2}\hat{z}
$$

阳光 $\sim 1$ kW/m² 对应 $E_0 \approx 870$ V/m——这就是阳光的真实电场强度。

### 习题 7（辐射）— 振荡偶极子辐射功率

电荷 $q$ 做简谐振荡 $x(t) = A\cos\omega t$，求时间平均辐射功率。

**解**：加速度 $a = -A\omega^2\cos\omega t$，Larmor：

$$
P = \frac{q^2 a^2}{6\pi\epsilon_0 c^3} = \frac{q^2 A^2 \omega^4 \cos^2\omega t}{6\pi\epsilon_0 c^3}
$$

时间平均 $\langle P\rangle = \frac{q^2 A^2 \omega^4}{12\pi\epsilon_0 c^3}$。

**$\omega^4$ 依赖**：频率越高辐射越强（瑞利散射蓝天原理：高频蓝光散射 $4^4 = 256$ 倍于红光）。

### 习题 8（边界条件）— 介质表面

无自由面电荷时，介质 1（$\epsilon_1$）与介质 2（$\epsilon_2$）界面，求电场切向和法向的边界条件。

**解**：
- 切向 $E_{1\parallel} = E_{2\parallel}$（由 $\nabla\times\mathbf{E}=0$，沿界面取小矩形回路）。
- 法向 $D$ 连续：$\epsilon_1 E_{1\perp} = \epsilon_2 E_{2\perp}$（无自由面电荷时）。

这就是为什么光线进入玻璃时折射——边界条件决定。

---

## 8. 反直觉发现

### 8.1 麦克斯韦方程组里没有力

四个方程只有 $\mathbf{E}, \mathbf{B}, \rho, \mathbf{J}$，没有"力"这个概念。力出现在**洛伦兹力公式** $\mathbf{F} = q(\mathbf{E} + \mathbf{v}\times\mathbf{B})$ 中，是连接场与电荷的桥梁——这意味着**场本身是物理实体**，携带能量动量（坡印廷矢量），力只是电荷"询问"场的反馈。

### 8.2 磁场是相对论效应

低速下 $\mu_0\epsilon_0 = 1/c^2$ 中的 $1/c^2 \approx 10^{-17}$ 似乎是个"小修正"。但 Purcell 指出：**磁场就是运动参照系下电场的相对论修正**。我们之所以感觉磁场很强（磁铁吸铁那么猛），是因为电流涉及海量电荷，它们的"对称正负"在静止参照系中完全相消（净电场为零），只剩纯相对论修正——而修正后的磁场不再相消。

### 8.3 加速电荷必然辐射（代码未含，理论铁证）

Larmor $P \propto a^2$ 告诉我们：**任何加速度都产生辐射**。这意味着：
- 经典氢原子中电子绕核转，加速度不为零，必然辐射电磁波，1 纳秒内坠入核——经典电动力学预言的原子不可能稳定。这是量子力学必须出场的契机。
- 同步辐射光源、自由电子激光、射电天文脉冲星辐射，都源于这一原理。

### 8.4 位移电流是"无电流的电流"

电容器两板间是真空（或介质），无任何流动电荷。但 (iv) 式的位移电流项 $\mu_0\epsilon_0\partial\mathbf{E}/\partial t$ 让磁场"穿过"了真空——这是**变化的电场产生磁场**，与法拉第的"变化的磁场产生电场"对称。这种对称性不是美学，而是电磁波存在的数学前提。

---

## 9. 不足与延伸

| 本主题局限 | 延伸方向 | 课程 |
|-----------|---------|------|
| 经典电磁场 | 场的量子化 → 光子 | 8.323 QFT |
| 平直时空 | 弯曲时空中的麦克斯韦 → 引力透镜、黑洞光子球 | 8.962 GR |
| 无介质响应 | $\mathbf{D}, \mathbf{H}$、电极化、磁化、色散、非线性光学 | 8.07 续 |
| 不涉及粒子产生湮灭 | 高能碰撞 → QED（$\alpha = e^2/4\pi\epsilon_0\hbar c \approx 1/137$） | 8.323 |
| 经典辐射 | 量子辐射、自发辐射、激光、Casimir 效应 | 8.422 |

**学习路径**：8.02 → 8.022（Purcell 相对论视角）→ 8.07（Griffiths 全本含辐射）→ 8.323（Peskin QED）。

---

**参考**：
- Purcell & Morin《Electricity and Magnetism》3ed, Ch 5 (Gauss), Ch 6 (B field), Ch 9 (辐射)
- Griffiths《Introduction to Electrodynamics》4ed, Ch 2-3 (静电), Ch 5-6 (静磁), Ch 7-9 (动力学/波/辐射), Ch 11 (辐射)
- Jackson《Classical Electrodynamics》3ed Ch 14 (辐射) — 研究生版
- MIT OCW 8.022 (Kleppner) / 8.07 (Zwiebach)

---

## 🎯 费曼式入口（白话版）

> **一句话解释**：电磁学研究的是"电荷之间的对话"。电荷静止时它们用**电场**聊天（库仑力），电荷运动时它们还用**磁场**聊天。变化的电场产生磁场，变化的磁场产生电场——这对"互生"就产生了电磁波，也就是**光**。所以学完电磁学你会发现：光、Wi-Fi、X 射线、微波炉、彩虹——本质都是同一件事。
>
> **生活类比**：
> - 电场线 ≈ 磁铁周围洒铁屑看到的线条
> - 高斯定律 ≈ "有多少电荷就发出多少条线"——线的数量只跟内部电荷有关，跟形状无关
> - 法拉第定律 ≈ 把磁铁快速塞进线圈，线圈里产生电流——变化的磁场"推动"了电荷
> - 电磁波 ≈ 拿住绳子一端上下抖，波就沿绳子传播——电场和磁场互推互拉向前传播
> - 相对论视角的磁场 ≈ 磁场不是独立的东西，它只是电场在运动参考系中的"相对论修正"
>
> **反直觉发现**：你以为是先有电场、再产生磁场？不！Purcell 从相对论证明：**磁场本质上就是运动电荷之间的电场力在另一个参考系中的表现**。更震撼的是麦克斯韦方程组告诉我们：**光本身就是电磁波**——可见光、无线电视信号、医院 X 光片、微波炉加热食物，全是一回事。

---

## 🔗 衔接：这个主题从哪来，到哪去

### 前置知识
- **Topic 01 经典力学**：力、功、能量、动量——库仑力是力，电场做功 = 电势差
- **矢量分析**：散度 $\nabla\cdot$（高斯定律）、旋度 $\nabla\times$（法拉第/安培定律）——这是麦克斯韦方程组的语言
- **偏微分方程**：波动方程 $\nabla^2\mathbf{E} = \frac{1}{c^2}\frac{\partial^2\mathbf{E}}{\partial t^2}$

### 本主题解决了什么危机
- **19 世纪的物理大统一**：之前电（摩擦起电）、磁（指南针）、光（透镜）被视为三个完全不同的现象。麦克斯韦 1865 年用 4 个方程把它们**统一**了——电磁场振荡产生电磁波，其速度恰好等于光速 $c = 1/\sqrt{\mu_0\epsilon_0} \approx 3\times10^8$ m/s。这是物理学史上第一次大统一。
- **超距作用的终结**：牛顿引力是"超距作用"（瞬间传递）。法拉第提出"场"的概念——力不是瞬间作用的，而是通过场以有限速度传播。麦克斯韦方程组证实了这一点。

### 本主题留下的新危机
- **电磁波的介质危机（以太之谜）**：波需要介质传播（声波需要空气），那电磁波在什么介质中传播？迈克尔逊-莫雷实验（1887）否定了"以太"的存在 → 直接催生**狭义相对论**。
- **黑体辐射与紫外灾难**：经典电磁学 + 统计力学无法解释黑体辐射谱——高频处能量发散。普朗克（1900）被迫引入"量子"概念 → 直接催生**量子力学**。
- **场的量子化**：麦克斯韦方程是经典的，但电磁场本身是量子化的——光子。光电效应、自发辐射无法用经典电磁学解释 → **量子电动力学（QED）**。

### 后续主题
- **Topic 03 量子力学**：电磁波的能量量子化 $E = h\nu$ 是量子力学的起点
- **Topic 07 粒子物理**：QED（$\alpha \approx 1/137$）是标准模型 U(1) 规范理论——电磁力只是四种基本力之一
- **Topic 08 广义相对论**：电磁波在弯曲时空中传播（引力透镜、黑洞光子球）

---

## 🏭 理论联系实际：5 个工业/生活应用

1. **无线充电与电磁感应**：法拉第电磁感应定律 $\varepsilon = -d\Phi/dt$ 是所有发电机的原理。火电站烧水推汽轮机切割磁感线发电、风力发电机、无线充电器（Qi 标准），全是同一个原理。
   - 实例：iPhone MagSafe 磁吸充电（交变磁场在手机线圈中感应电流）

2. **雷达与 5G/6G 通信**：电磁波反射（雷达）、衍射（绕过障碍物）、干涉（MIMO 多天线）是现代通信的基础。麦克斯韦方程告诉你什么频率能穿透墙壁（Wi-Fi 2.4 GHz），什么频率带宽大但穿不透（5G 毫米波 28 GHz）。
   - 实例：Tesla Autopilot 的毫米波雷达、Starlink 卫星 Ku/Ka 波段通信

3. **核磁共振成像（MRI）**：强静磁场（3T）极化人体氢原子核质子，射频脉冲激发共振，梯度磁场做空间编码——整个过程是经典电磁学（洛伦兹力 + 法拉第感应）+ 量子自旋的结合。
   - 实例：医院 3T MRI 扫描仪，超导线圈用液氦冷却到 4K

4. **超材料与隐身斗篷**：通过设计亚波长结构（metamaterials），可以操控电磁波的折射、反射甚至绕射——让光"绕过"物体，实现隐身。这依赖于变换光学（transformation optics），本质是麦克斯韦方程在弯曲坐标下的解。
   - 实例：Duke 大学 2006 年微波隐身斗篷原型；可重构智能表面（RIS）用于 6G

5. **激光——受激辐射的光放大**：爱因斯坦 1917 年预言受激辐射，1960 年梅曼制造出第一台红宝石激光。激光的原理是原子跃迁 + 光学谐振腔——电磁波在两个反射镜之间来回放大形成相干光。
   - 实例：光刻机（ASML EUV 光刻机制造 3nm 芯片）、激光雷达（LiDAR）、激光近视手术

---

## 🔬 最新研究前沿（2024-2026）

> 基于 Nature 系列期刊搜索的真实结果

### 通用超材料生成模型 InfoMetaGen
- **发现**：InfoMetaGen——一个通用的生成模型，为亚波长"超原子"（meta-atoms）和非均匀超材料分布提供逆向设计策略。给定你想要的电磁波操控效果，AI 自动设计对应的微观结构。
- **来源**：Qian, C. & Chen, H. *Nature Computational Science* (2026)
- **日期**：2026 年 8 月
- **为什么重要**：将电磁超材料设计从试错法变成 AI 生成——未来隐身衣、完美透镜、全息显示的设计将自动化

### 光的编织——非厄米拓扑的芯片级实验验证
- **发现**：耦合的芯片级激光器首次直接观测到"辫子状"的能谱路径（braid-like eigenvalue trajectories），实时可视化了非厄米系统的拓扑结构。
- **来源**：König, J.L.K. & Bergholtz, E.J. *Nature Physics* **22**, 1180 (2026)
- **日期**：2026 年 8 月
- **为什么重要**：非厄米物理（含增益/损耗的系统）是电磁波和光子学的前沿，对新型激光器、拓扑光子器件有根本影响

### 里德堡原子接收器——抗干扰超宽带通信
- **发现**：基于里德堡原子的接收器可以实现超宽带跳频通信——用原子量子态直接感知微波电场，不受传统电子器件的带宽限制。
- **来源**：Nan, J.-D. et al. *Nature Communications* (2026)
- **日期**：2026 年 8 月
- **为什么重要**：电磁波的探测从传统天线跃升到量子传感级别——可覆盖从射频到太赫兹的超宽频段

### 阿秒扫描隧道显微镜——纳米尺度下观测电子运动
- **发现**：利用定制双色单周期光脉冲，在扫描隧道显微镜针尖-样品的亚纳米间隙中实现了阿秒（$10^{-18}$ s）级瞬态电流检测。
- **来源**：Morimoto, Y. & Kimura, K. *Nature Photonics* **20**, 857 (2026)
- **日期**：2026 年 7 月
- **为什么重要**：首次在纳米尺度直接观测超快电子动力学——电磁波 + 量子隧穿的极致应用

---

## 🗺️ 学习 Roadmap（MIT 路径）

### 🎓 入门（2-3 周）
- 📖 读：Young & Freedman《University Physics》Ch 21-33（静电、直流电路、磁场、电磁感应、电磁波）
- 🎥 看：MIT OCW **8.02**（Walter Lewin——他会在课堂上用 200 万伏特斯拉线圈演示！）
  - 重点视频：Lec 10（电容器与电介质）、Lec 15-16（磁场与洛伦兹力）、Lec 33-34（电磁波与偏振）
- ✍️ 做：
  - 计算 2-3 个点电荷系统的电场和电势（积分练习）
  - 运行 `physics_demos.py` 的 `em()` demo 观察偶极辐射

### 🏗️ 进阶（4-6 周）
- 📖 读：Purcell & Morin Ch 5-6（高斯定律 + 磁场从相对论导出）、Griffiths Ch 7-9（法拉第定律 + 电磁波 + 辐射）
- 💻 做：
  - 用 Python 数值求解拉普拉斯方程 $\nabla^2 V = 0$（松弛法），画等势线
  - 运行 `physics_demos.py` 中麦克斯韦方程组演示
- 🧪 实验：MIT Junior Lab 8.13（电磁波实验、微波光学）

### 🔬 深造（持续）
- 📄 读：
  - Jackson《Classical Electrodynamics》3ed Ch 14（辐射）— 研究生标准教材
  - Landau & Lifshitz《经典场论》Vol 2——从作用量出发的最优雅推导
  - Mandel & Wolf《Optical Coherence and Quantum Optics》——光学圣经
- 🛠️ 项目：用 FDTD（时域有限差分）方法模拟光在光子晶体中的传播

### ✅ 知识检查
- [ ] 能默写麦克斯韦方程组的 4 个方程（积分形式 + 微分形式）并说出物理含义
- [ ] 能从库仑定律 + 狭义相对论推导出磁场（Purcell 方法）
- [ ] 理解为什么 $\nabla \times \mathbf{E} = 0$ 在静电场中成立，但在时变场中不成立
- [ ] 能解释位移电流 $\epsilon_0 \partial\mathbf{E}/\partial t$ 为什么是安培定律的关键补丁
- [ ] 能推导电磁波速度 $c = 1/\sqrt{\mu_0\epsilon_0}$ 并验证数值等于光速
