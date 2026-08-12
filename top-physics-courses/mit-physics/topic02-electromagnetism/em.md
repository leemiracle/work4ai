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
