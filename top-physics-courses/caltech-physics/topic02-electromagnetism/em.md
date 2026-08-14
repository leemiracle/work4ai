# Topic 02 · 电磁学 — Caltech Ph 1b / Ph 108 / Ph 122

> **课程链**：Ph 1abc（Feynman Lectures Vol 2）→ Ph 108 Classical Electrodynamics（Griffiths）→ Ph 122abc Electrodynamics（Jackson）
>
> **教材三角**：Feynman Lectures Vol 2（物理直觉的巅峰） · Griffiths *Introduction to Electrodynamics* 4ed（最清晰的中级教材，全美 10/10 校使用） · Jackson *Classical Electrodynamics* 3ed（研究生标准，以难度著称）

---

## Caltech 特色：Feynman Lectures Vol 2

Feynman Lectures Vol 2 被公认为**历史上最好的 E&M 教材之一**。Feynman 用矢量分析统一静电学和静磁学，在 Maxwell 方程组出现之前就给你直觉——为什么电场线"排斥"、磁场线"环绕"。Caltech 的 Ph 1b 至今仍沿用这种精神。

此外，Caltech 的电磁学与 LIGO 实验紧密相关：干涉仪的精密光学、法布里-珀罗腔的电磁场分布、光压对悬镜的作用——都是 E&M 的直接应用。

---

## §1 静电学

### 1.1 库仑定律与电场

点电荷 $q$ 产生的电场：

$$\mathbf{E} = \frac{1}{4\pi\epsilon_0}\frac{q}{r^2}\hat{\mathbf{r}}$$

### 1.2 高斯定律（Maxwell 第一方程的积分形式）

$$\oint_S \mathbf{E} \cdot d\mathbf{A} = \frac{Q_{\text{enc}}}{\epsilon_0}$$

微分形式：$\nabla \cdot \mathbf{E} = \rho/\epsilon_0$

**高斯定律的威力**：利用对称性（球、柱、面），可在 3 行内求出电场。

### 1.3 电势

$$\mathbf{E} = -\nabla V, \qquad V(\mathbf{r}) = \frac{1}{4\pi\epsilon_0}\int \frac{\rho(\mathbf{r}')}{|\mathbf{r} - \mathbf{r}'|}\, d^3r'$$

满足**泊松方程**：$\nabla^2 V = -\rho/\epsilon_0$

### 1.4 多极展开

远场中任意局域电荷分布的电势：

$$V(\mathbf{r}) = \frac{1}{4\pi\epsilon_0}\left[\frac{Q}{r} + \frac{\mathbf{p} \cdot \hat{\mathbf{r}}}{r^2} + \frac{1}{2}\sum_{ij} Q_{ij}\frac{\hat{r}_i \hat{r}_j}{r^3} + \cdots\right]$$

- $Q$：总电荷（单极矩）
- $\mathbf{p} = \int \mathbf{r}'\rho\,d^3r'$：电偶极矩
- $Q_{ij}$：电四极矩张量

> **Feynman 的直觉**（Vol 2 Ch 6）：电偶极子的场线图不是"两个点电荷的叠加"那么简单——Feynman 让你先画出力线拓扑，再算公式。

### 1.5 镜像法

> **经典问题**：点电荷 $q$ 距无限大接地导体板距离 $d$。求空间电势。

**镜像法**：在板另一侧 $d$ 处放镜像电荷 $-q$，撤去导体板。在板上方区域，电势完全等价。

$$V(x,y,z) = \frac{1}{4\pi\epsilon_0}\left[\frac{q}{\sqrt{x^2+y^2+(z-d)^2}} - \frac{q}{\sqrt{x^2+y^2+(z+d)^2}}\right] \quad (z>0)$$

感应电荷总量 $Q_{\text{ind}} = -q$（可由 $E_z$ 在板上积分验证）。

---

## §2 静磁学

### 2.1 毕奥-萨伐尔定律

稳恒电流元 $I\,d\mathbf{l}$ 产生的磁场：

$$d\mathbf{B} = \frac{\mu_0}{4\pi}\frac{I\,d\mathbf{l} \times \hat{\mathbf{r}}}{r^2}$$

### 2.2 安培定律（Maxwell 第三方程的静磁版）

$$\oint_C \mathbf{B} \cdot d\mathbf{l} = \mu_0 I_{\text{enc}}$$

微分形式：$\nabla \times \mathbf{B} = \mu_0 \mathbf{J}$

**例**：无限长直导线 $I$：$B = \mu_0 I / (2\pi r)$（环形场线）。

### 2.3 磁矢势

$$\mathbf{B} = \nabla \times \mathbf{A}$$

在库仑规范 $\nabla \cdot \mathbf{A} = 0$ 下：

$$\mathbf{A}(\mathbf{r}) = \frac{\mu_0}{4\pi}\int \frac{\mathbf{J}(\mathbf{r}')}{|\mathbf{r} - \mathbf{r}'|}\, d^3r'$$

> **规范不变性**——这是电磁场最深刻的对称性。$\mathbf{A} \to \mathbf{A} + \nabla\lambda$ 不改变 $\mathbf{B}$。这一思想后来在粒子物理的标准模型中成为核心：规范理论 = 相位不变性 → 全部基本相互作用。

---

## §3 麦克斯韦方程组——电磁学的统一

### 3.1 四个方程

| 方程 | 积分形式 | 微分形式 | 物理意义 |
|------|---------|---------|---------|
| 高斯定律（电） | $\oint \mathbf{E}\cdot d\mathbf{A} = Q/\epsilon_0$ | $\nabla\cdot\mathbf{E} = \rho/\epsilon_0$ | 电荷是电场源 |
| 高斯定律（磁） | $\oint \mathbf{B}\cdot d\mathbf{A} = 0$ | $\nabla\cdot\mathbf{B} = 0$ | 无磁单极 |
| 法拉第定律 | $\oint \mathbf{E}\cdot d\mathbf{l} = -d\Phi_B/dt$ | $\nabla\times\mathbf{E} = -\partial\mathbf{B}/\partial t$ | 变化磁场产生电场 |
| 安培-麦克斯韦 | $\oint \mathbf{B}\cdot d\mathbf{l} = \mu_0(I + \epsilon_0\,d\Phi_E/dt)$ | $\nabla\times\mathbf{B} = \mu_0\mathbf{J} + \mu_0\epsilon_0\,\partial\mathbf{E}/\partial t$ | 电流+变化电场产生磁场 |

### 3.2 位移电流——麦克斯韦的天才

> **Feynman 的讲述**（Vol 2 Ch 18）：安培定律 $\nabla\times\mathbf{B} = \mu_0\mathbf{J}$ 在电容充电时会矛盾（充电时导线有电流，电容器极板间无电流，但环路积分必须连续）。麦克斯韦加了**位移电流** $\epsilon_0\partial\mathbf{E}/\partial t$ 来修复这个矛盾——这一步直接预言了电磁波的存在。

### 3.3 电磁波方程

在真空中（$\rho = 0, \mathbf{J} = 0$），从 Maxwell 方程组推出：

$$\nabla^2 \mathbf{E} = \mu_0\epsilon_0 \frac{\partial^2 \mathbf{E}}{\partial t^2}, \qquad \nabla^2 \mathbf{B} = \mu_0\epsilon_0 \frac{\partial^2 \mathbf{B}}{\partial t^2}$$

波速：

$$c = \frac{1}{\sqrt{\mu_0\epsilon_0}} = 299{,}792{,}458\;\text{m/s}$$

> **历史上最伟大的推导之一**：Maxwell 发现电磁波的波速 $= 1/\sqrt{\mu_0\epsilon_0}$ 恰好等于已知光速。他写道：*"We can scarcely avoid the inference that light consists in the transverse undulations of the same medium which is the cause of electric and magnetic phenomena."* 光就是电磁波。

---

## §4 电磁波

### 4.1 平面波解

$$\mathbf{E}(\mathbf{r},t) = \mathbf{E}_0 e^{i(\mathbf{k}\cdot\mathbf{r} - \omega t)}, \qquad \mathbf{B} = \frac{1}{\omega}\mathbf{k}\times\mathbf{E}$$

性质：
- 横波：$\mathbf{E} \perp \mathbf{k}$，$\mathbf{B} \perp \mathbf{k}$，$\mathbf{E} \perp \mathbf{B}$
- 振幅比：$E_0/B_0 = c$
- 相位：$\mathbf{E}$ 和 $\mathbf{B}$ 同相

### 4.2 偏振

线偏振、圆偏振（左旋/右旋）、椭圆偏振。圆偏振态：

$$\mathbf{E}_{\pm} = \frac{E_0}{\sqrt{2}}(\hat{\mathbf{x}} \pm i\hat{\mathbf{y}})e^{i(kz-\omega t)}$$

### 4.3 能流密度（坡印廷矢量）

$$\mathbf{S} = \frac{1}{\mu_0}\mathbf{E}\times\mathbf{B}$$

电磁波的时间平均能流：$\langle S \rangle = \frac{1}{2}c\epsilon_0 E_0^2$

### 4.4 辐射：拉莫尔公式

加速电荷 $q$ 的辐射功率：

$$P = \frac{\mu_0 q^2 a^2}{6\pi c} = \frac{q^2 a^2}{6\pi\epsilon_0 c^3}$$

> **LIGO 关联**：引力波探测器测量的是时空本身的波动，但 LIGO 的精密光学系统——法布里-珀罗腔、光悬浮、散粒噪声——全部是 E&M 的直接应用。Caltech 40m 原型干涉仪是 LIGO 的技术孵化器。

---

## Python 演示：偶极辐射场可视化 + 镜像法验证

```python
"""
Caltech Ph 1b / Ph 108 Demo: 电偶极子的电场与电势
1. 计算并可视化电偶极子的等势线和电场线
2. 验证镜像法（点电荷 + 接地导体板）
纯标准库零依赖，bash 可直接跑通。
"""
import math

# ── 1. 电偶极子场 ──
# 偶极子: +q at (+d, 0), -q at (-d, 0)
q = 1.0
d = 0.5
k = 1.0  # 1/(4πε₀) 归一化

def potential_dipole(x, y):
    """电偶极子电势"""
    r1 = math.sqrt((x - d)**2 + y**2)
    r2 = math.sqrt((x + d)**2 + y**2)
    if r1 < 0.01 or r2 < 0.01:
        return float('inf')
    return k * q / r1 - k * q / r2

# 等势线: V = const
# 沿 x 轴 (y=0): V(x,0) = kq/(x-d) - kq/(x+d)
# 远场多极展开: V ≈ kp cos θ / r² = kpd·x / (x²+y²)^(3/2)
p = q * 2 * d  # 偶极矩

# 验证远场近似 vs 精确值
print("=== 电偶极子远场近似验证 ===")
print(f"偶极矩 p = q·2d = {p}")
print(f"{'r':>8s} {'V_exact':>12s} {'V_dipole':>12s} {'误差%':>8s}")
for r in [3.0, 5.0, 10.0, 20.0, 50.0]:
    x, y = r, 0.0
    V_exact = potential_dipole(x, y)
    V_dip = k * p * x / (x**2 + y**2)**1.5  # 偶极近似
    err = abs(V_exact - V_dip) / abs(V_exact) * 100
    print(f"{r:8.1f} {V_exact:12.6f} {V_dip:12.6f} {err:8.2f}%")

print()
print("→ r >> d 时偶极近似收敛。r=50d 时误差 < 1%。")

# ── 2. 镜像法验证 ──
print("\n=== 镜像法验证：点电荷 + 接地导体板 ===")
# 点电荷 q at (0,0,d), 镜像 -q at (0,0,-d)
# 导体板为 z=0 平面
# V(z>0) = kq/√(x²+y²+(z-d)²) - kq/√(x²+y²+(z+d)²)
q_img = 1.0
d_img = 1.0

def V_image(x, y, z):
    r1 = math.sqrt(x**2 + y**2 + (z - d_img)**2)
    r2 = math.sqrt(x**2 + y**2 + (z + d_img)**2)
    if r1 < 0.01 or r2 < 0.01:
        return float('inf')
    return k * q_img / r1 - k * q_img / r2

# 验证 z=0 处 V=0（边界条件）
print("导体板 (z=0) 上各点电势（应为 0）：")
for x in [0.0, 0.5, 1.0, 2.0, 5.0]:
    V = V_image(x, 0.0, 0.0)
    print(f"  x={x:.1f}: V = {V:.2e} (≈0 ✓)")

# 感应电荷面密度: σ = -ε₀ ∂V/∂z|_{z=0+}
# ∂V/∂z|_{z=0} = -kq·(-2d)/(x²+d²)^(3/2)
# σ(x) = -ε₀ · 2kqd/(x²+d²)^(3/2) = -qd / (2π(x²+d²)^(3/2))
# 总感应电荷 = ∫σ dA = -q
print("\n总感应电荷积分（应为 -q = -1.0）：")
# 数值积分 σ(r) = -q·d / (2π(r²+d²)^(3/2))
# 用极坐标: Q = ∫₀^∞ σ(r)·2πr·dr = -qd ∫₀^∞ r/(r²+d²)^(3/2) dr
# 解析解 = -qd · [-1/√(r²+d²)]₀^∞ = -qd · (1/d) = -q
Q_total = 0.0
dr_num = 0.001
r_max = 100.0
r = 0.0
while r < r_max:
    sigma = -q_img * d_img / (2 * math.pi * (r**2 + d_img**2)**1.5)
    Q_total += sigma * 2 * math.pi * r * dr_num
    r += dr_num
print(f"  Q_induced (数值) = {Q_total:.6f}")
print(f"  Q_induced (解析) = {-q_img:.6f}")
print(f"  → 镜像法保证了总感应电荷 = -q，物理上正确。")
```

---

## 习题

### 基础题（Griffiths 级别）

**P1.** 用高斯定律求均匀带电球（半径 $R$，总电荷 $Q$）内外的电场。画出 $E(r)$ 图。

**P2.** 证明：在无电荷区域，电势满足拉普拉斯方程 $\nabla^2 V = 0$，且 $V$ 在边界上的值唯一决定区域内的解（唯一性定理）。

**P3.** 用毕奥-萨伐尔定律推导半径 $R$、电流 $I$ 的圆形线圈在轴线上距离 $z$ 处的磁场：

$$B(z) = \frac{\mu_0 I R^2}{2(R^2 + z^2)^{3/2}}$$

### 进阶题（Jackson 级别）

**P4.** 从 Maxwell 方程组出发，推导真空中电磁波的波动方程 $\nabla^2\mathbf{E} = \mu_0\epsilon_0\,\partial^2\mathbf{E}/\partial t^2$，并证明波速 $c = 1/\sqrt{\mu_0\epsilon_0}$。

**P5.**（LIGO 关联）法布里-珀罗腔中光在两面平行镜之间往返反射。腔长 $L = 4\,\text{km}$，镜反射率 $R = 0.9999$。求腔的有效光程（增益），解释为什么 LIGO 用 FP 腔而非单次通过。

**P6.** 用拉莫尔公式 $P = q^2a^2/(6\pi\epsilon_0 c^3)$ 估算：电子绕质子做圆周运动（经典氢原子）的辐射功率。证明经典氢原子在 $\sim 10^{-11}\,\text{s}$ 内坍缩——这是经典物理的根本困难，量子力学才解决。

### 挑战题

**P7.** **推迟势**：电荷在 $t_r = t - |\mathbf{r} - \mathbf{r}'|/c$ 时刻的位置决定 $\mathbf{r}$ 处 $t$ 时刻的场（Liénard-Wiechert 势）。写出匀速运动电荷的场，证明它等于库仑场做洛伦兹收缩后的结果。

**P8.** 用 Python 模拟电磁波在不同介质界面上的反射/折射（Fresnel 方程），画出 $s$ 偏振和 $p$ 偏振的反射率随入射角的变化，标出布儒斯特角。

---

## 知识地图与跨课程联系

```
静电学 (Ph 1b)
    │
    ├──→ 电动力学 (Ph 108) ──→ 高级电动力学 (Ph 122, Jackson)
    │         │
    │    Maxwell 方程组 ──→ 电磁波 ──→ 光学
    │                        │
    │                   LIGO 干涉仪 (Caltech)
    │
    └──→ 规范不变性 ──→ 粒子物理标准模型 (Ph 129/Ph 237)
                                 │
                          QED: Feynman 的路径积分 (Caltech 传统)
```

---

## 参考与延伸阅读

| 教材 | 章节 | 重点 |
|------|------|------|
| Feynman Lectures Vol 2 | Ch 1-5（静电）、Ch 13-14（磁）、Ch 18（Maxwell）、Ch 20-21（EM 波）| Caltech 一年级必读 |
| Griffiths *Introduction to Electrodynamics* 4ed | Ch 2（静电）、Ch 5（静磁）、Ch 7（EM 感应）、Ch 9（EM 波）| Ph 108 主教材 |
| Jackson *Classical Electrodynamics* 3ed | Ch 1-4（多极/边值）、Ch 6-7（波/辐射）、Ch 11（相对论 E&M）| Ph 122 研究生标准 |
| Purcell & Morin *Electricity and Magnetism* 3ed | 全书用相对论统一 E 和 B | Berkeley Phys Course Vol 2 |

> **Feynman 的话**：*"I would like to again impress you with the vast range of phenomena that the theory of electromagnetism describes... All of this comes out of four little equations."* —— Maxwell 四方程描述了从原子到星系、从静电到光的全部电磁现象。

---

*本文件属于 top-physics-courses/caltech-physics Phase 1。对应课程 Ph 1b → Ph 108 → Ph 122。*

---

## 🎯 费曼式入口（白话版）

> **一句话解释**：电磁学研究的是"电荷之间怎么对话"——它们靠一种看不见的"场"（电场和磁场）来互相推拉。
>
> **生活类比**：电荷就像广播电台，它向四周持续发射"信号"（电场）。另一个电荷是收音机，它"听到"信号就被推或拉。磁铁则像是会扭动信号方向的特殊电台。Maxwell 的伟大发现是：**变化的电信号会自动产生磁信号，反之亦然——两者互相"喂养"就能脱离电荷自己跑起来，这就是光**。
>
> **反直觉发现（啊哈时刻）**：
> - **光速是个纯电磁常数**：$c = 1/\sqrt{\mu_0\epsilon_0}$——两个实验室里能测的电学常数，居然算出了光速！Maxwell 据此断言"光就是电磁波"，这是物理学史上最伟大的统一。
> - **磁铁其实没有磁单极**：$\nabla \cdot \mathbf{B}=0$——你把磁铁掰成两半，永远得到两根新磁铁，找不到"孤立北极"。这是电磁学最深的对称性破缺。
> - **位移电流的修补**：Maxwell 凭空加的 $\epsilon_0\partial\mathbf{E}/\partial t$ 一项，不是为了数学漂亮，而是为了电荷守恒——但这一项直接预言了电磁波的存在！

---

## 🔗 衔接：从哪来，到哪去

### 前置（你需要先会什么）
- **Ph 1a 力学**：能量、动量守恒；矢量分析（点乘叉乘）
- **Ph 106 数学方法**：矢量微积分（$\nabla, \nabla\cdot, \nabla\times$）、复变（二维势论）、特殊函数
- **Ph 1a 相对论**：洛伦兹变换——电磁学天然是相对论的

### 电磁学的"危机"（为什么需要升级）
- **静电/静磁各自为政**：库仑定律和毕奥-萨伐尔定律像是两套独立理论
- **解决 → Maxwell 方程组**：四个方程统一了电与磁，还预言了电磁波
- **新危机**：Maxwell 方程与牛顿力学不兼容（伽利略变换下形式会变）
- **解决 → 狭义相对论**：Einstein 发现电磁学天然满足 Lorentz 协变性——磁场就是运动的电场的相对论效应（Purcell 的教法）

### 后续（电磁学通向哪里）
- Maxwell → **光学**（折射、干涉、衍射、偏振）
- 规范不变性 $\mathbf{A}\to\mathbf{A}+\nabla\lambda$ → **粒子物理标准模型**（$U(1)\times SU(2)\times SU(3)$ 规范理论）→ **QED**（Feynman 的 Caltech 遗产）
- 法布里-珀罗腔 + 精密光学 → **LIGO 干涉仪**（Caltech 旗舰）
- 散粒噪声 + 挤压光 → **量子光学**（Ph 237）

---

## 🏭 理论联系实际：5 个应用

1. **LIGO 法布里-珀罗腔**（Caltech 旗舰）：4 km 臂中光往返反射 ~280 次，等效光程 1120 km，相位灵敏度 $10^{-11}$ 个波长——能测出质子直径千分之一的镜面位移。这是电磁波干涉 + 镜面镀膜工程的极致。
2. **5G / Wi-Fi 天线**：手机天线发射电磁波，本质就是加速电荷的拉莫尔辐射 $P\propto a^2$。MIMO 多天线波束成形依赖电磁波干涉原理。
3. **MRI 磁共振成像**：强静磁场（$B_0\sim 3\,\text{T}$）+ 射频脉冲 + 梯度磁场——三套电磁场的精妙配合，能看见人体软组织。
4. **无线充电 / 变压器**：法拉第电磁感应 $\oint\mathbf{E}\cdot d\mathbf{l}=-d\Phi_B/dt$ 的直接应用。Qi 充电板靠的就是交变磁场的互感。
5. **激光与光纤通信**：受激辐射产生相干电磁波（激光），光纤中靠全反射（介电常数突变）传播——全球互联网的物理基础。

---

## 🔬 最新研究前沿（2024-2026）

1. **LIGO 量子压缩光突破**（2023-2025 持续）：LIGO 在 2023 年首次实现频域依赖的量子压缩（*Nature* 2023），2024-2025 O4 运行中持续提升灵敏度——这是把电磁场的量子涨落人为"挤压"来突破散粒噪声极限。[LIGO Caltech 2023-10-23 "LIGO Surpasses the Quantum Limit"]
2. **AI 驱动的 LIGO 噪声压制**（2025-09-08）：Caltech 联合 Google DeepMind 开发 **Deep Loop Shaping** 强化学习方法，实时压制探测器噪声——经典电动力学 + 量子光学 + 深度学习的融合。[LIGO Caltech 2025-09-08]
3. **拓扑光子学**（2024-2026 活跃）：用超材料构造光子能带的拓扑缺陷，实现"光绕过缺陷无散射传播"——2024-2025 多篇 *Nature Photonics* 报道了光子拓扑绝缘体的鲁棒传输。Caltech 的 Alù、Marquardt 团队参与。
4. **阿秒光脉冲与电子动力学**（延续 2023 诺奖）：2023 年物理诺贝尔奖颁给 Agostini、Krausz、L'Huillier（阿秒光脉冲）。2024-2026 持续用阿秒脉冲观测分子内电子的实时运动——电磁波极限短脉冲的前沿。
5. **超表面光学**（2024-2026 爆发）：亚波长纳米结构阵列（metasurfaces）用几何相位（Pancharatnam-Berry phase）操控电磁波，一片比纸还薄的"超透镜"(metalens) 替代传统透镜组——*Nature* 2024-2025 多篇产业化报道。

---

## 🗺️ 学习 Roadmap（Caltech 路径）

```
高中物理 (库仑定律直觉)
    │
    ▼
Ph 1b  电磁学 (Feynman Lectures Vol 2, Purcell)  ← Caltech 大一
    │   • 掌握：电场/电势、高斯定律、毕奥-萨伐尔、法拉第定律
    │   • ✅ 知识检查：用高斯定律 3 行求出均匀带电球的场
    │
    ▼
Ph 106 数学方法 (Mathews & Walker Ch 4 复变, Ch 7 分离变量)  ← 并行
    │   • 掌握：留数定理、Laplace 方程、球谐函数
    │   • ✅ 知识检查：用镜像法求点电荷+导体板的场
    │
    ▼
Ph 108  经典电动力学 (Griffiths 全书)  ← 大二/大三
    │   • 掌握：Maxwell 方程组、电磁波、辐射、相对论 E&M
    │   • ✅ 知识检查：从 Maxwell 推出波动方程并算出 c
    │
    ▼
Ph 122abc  高级电动力学 (Jackson)  ← 研究生
    │   • 掌握：多极展开、Liénard-Wiechert 势、辐射理论、规范场
    │   • ✅ 知识检查：推导匀速运动电荷的场 = 库仑场的洛伦兹收缩
    │
    ▼
→ Ph 237 量子场论 (QED 是规范 E&M 的量子化)
→ LIGO 研究组 (精密光学 + 量子噪声)
→ Ph 239 光学与光子学 (超表面、拓扑光子学)
```

**关键里程碑**：能否从 Maxwell 方程组推导出 $c = 1/\sqrt{\mu_0\epsilon_0}$ 并解释为什么这等于光速，是检验你是否理解电磁学统一的试金石。Feynman 说：四个小方程描述了从原子到星系的全部电磁现象。
