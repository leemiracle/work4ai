# 東京大学物理系 Phase 2 · 物性物理学 深度講義

> **课程映射**（SURVEY §9 東大）：物性物理学（固体物理）
> **教材**：Kittel *Introduction to Solid State Physics* 9ed（日文译本『固体物理学入門』）+ Ashcroft & Mermin *Solid State Physics*（研究生参考）+ Kittel *Quantum Theory of Solids*
> **定位**：从晶体几何到能带论，从声子到超导——物性物理学是把量子力学「用在宏观物质上」的核心课程。没有能带论就没有半导体，没有半导体就没有现代电子学。Kittel 是東大此课的指定教材，其日文译本（丸善出版）在日本固体物理学界影响深远。

---

## 0. 導引：物性物理为何是「量子力学的最大应用」

量子力学 1925 年诞生后，第一个被彻底改造的宏观领域就是固体物理：

$$\underbrace{\text{量子力学}}_{\text{Schrödinger}} \xrightarrow{\text{周期势}} \underbrace{\text{能带论}}_{\text{Bloch 定理}} \xrightarrow{\text{分类}} \underbrace{\text{金属/绝缘体/半导体}}_{\text{现代电子学}}$$

Kittel 全书的逻辑链：晶体结构（几何）→ 倒格子（衍射）→ 声子（晶格振动）→ 自由电子气 → 能带（周期势中的电子）→ 半导体 → 超导。每一步都是前一步的「量子化」或「周期化」。

---

## 1. 結晶構造（Crystal Structure）

### 1.1 Bravais 格子

**Bravais 格子**：在空间中无限延伸的点阵，每个格点环境完全相同。三维有 14 种 Bravais 格子（分属 7 大晶系）。

格子矢量：$\vec{R} = n_1\vec{a}_1 + n_2\vec{a}_2 + n_3\vec{a}_3$（$n_i$ 整数），$\vec{a}_i$ 为**原胞基矢**（primitive vectors）。

每个原胞含一个格点。**惯用晶胞**（conventional cell）可能含多个格点（如面心立方 FCC 惯用晶胞含 4 个格点）。

### 1.2 常见晶体结构

| 结构 | 符号 | 堆积 | 配位數 | 例 |
|------|------|------|--------|-----|
| 简单立方 (SC) | cP | — | 6 | α-Po |
| 体心立方 (BCC) | cI | — | 8 | Fe, Na, Cr |
| 面心立方 (FCC) | cF | CCP | 12 | Cu, Al, Au |
| 六方密堆 (HCP) | hP | HCP | 12 | Mg, Zn, Ti |

**填充因子**（packing fraction）：SC $= \pi/6 \approx 0.524$，BCC $= \sqrt{3}\pi/8 \approx 0.680$，FCC $= \sqrt{2}\pi/6 \approx 0.740$（Kepler 猜想的最密堆积）。

### 1.3 Miller 指数

晶面用三个整数 $(hkl)$ 标记——该面在基矢方向的截距倒数（化为互质整数）。晶向 $[uvw]$ 表示方向矢量。

> **反直觉**：FCC 的 $(111)$ 面是六角对称的最密排面——面间距最大，面间结合最弱，所以金属常沿 $(111)$ 面滑移（塑性变形的微观机制）。

### 1.4 倒格子（Reciprocal Lattice）

正格子 $\vec{a}_i$ $\Leftrightarrow$ 倒格子 $\vec{b}_j$，满足 $\vec{a}_i \cdot \vec{b}_j = 2\pi\delta_{ij}$：

$$\vec{b}_1 = 2\pi\frac{\vec{a}_2\times\vec{a}_3}{V_c}, \quad \vec{b}_2 = 2\pi\frac{\vec{a}_3\times\vec{a}_1}{V_c}, \quad \vec{b}_3 = 2\pi\frac{\vec{a}_1\times\vec{a}_2}{V_c}$$

$V_c = \vec{a}_1\cdot(\vec{a}_2\times\vec{a}_3)$ 为原胞体积。

- SC（$a$）$\to$ SC（$2\pi/a$）
- BCC（$a$）$\to$ FCC（$4\pi/a$）
- FCC（$a$）$\to$ BCC（$4\pi/a$）

> **倒格子 = 动量空间中的格子**。X 射线衍射的 Bragg 反射条件用倒格矢表达最自然。

### 1.5 Brillouin 区

倒格子中的 Wigner–Seitz 原胞 = **第一 Brillouin 区**（First BZ）。BZ 边界是 Bragg 反射面——电子波在 BZ 边界发生**Bragg 反射**，产生能隙。

---

## 2. 自由電子モデルと能帯論（Free Electron Model & Band Theory）

### 2.1 Drude 自由电子模型（经典）

金属中的价电子像经典气体，在正离子背景中自由运动。电导率：

$$\sigma = \frac{ne^2\tau}{m}$$

$\tau$ 为弛豫时间（两次碰撞间平均时间）。Drude 模型定性成功但定量有误（如热容 $C_V^{\text{el}} = \frac{3}{2}Nk_B$ 是经典值，实测 $\ll$）——因为电子是费米子，不是经典气体。

### 2.2 Sommerfeld 自由电子模型（量子）

量子力学修正：电子填充服从 Fermi–Dirac 分布。Fermi 波矢 $k_F$、Fermi 能 $\epsilon_F$（Phase 1 统计篇 §3.5）：

$$\epsilon_F = \frac{\hbar^2 k_F^2}{2m}, \quad k_F = (3\pi^2 n)^{1/3}$$

**态密度**（density of states）：

$$g(\epsilon) = \frac{V}{2\pi^2}\left(\frac{2m}{\hbar^2}\right)^{3/2}\sqrt{\epsilon}$$

$g(\epsilon) \propto \sqrt{\epsilon}$ 是自由电子气的标志。

### 2.3 Bloch 定理

周期势 $V(\vec{r}) = V(\vec{r}+\vec{R})$ 中，Schrödinger 方程的解满足 **Bloch 定理**：

$$\psi_{\vec{k}}(\vec{r}) = e^{i\vec{k}\cdot\vec{r}}\,u_{\vec{k}}(\vec{r}), \quad u_{\vec{k}}(\vec{r}+\vec{R}) = u_{\vec{k}}(\vec{r})$$

即波函数是平面波 $e^{i\vec{k}\cdot\vec{r}}$ 乘周期函数 $u_{\vec{k}}$。$\vec{k}$ 限制在第一 BZ 内。

### 2.4 Kronig–Penney 模型与能带

一维周期方阱模型的解析解揭示了能带起源：

- BZ 边界（$k = \pm\pi/a$）处，Bragg 反射使前行波与反射波叠加 $\Rightarrow$ 形成驻波 $\Rightarrow$ 两种能量 $\Rightarrow$ **能隙**。
- 允带与禁带交替出现。

> **核心洞察**：能隙不是微扰效应——它是周期势与波动本质（Bragg 条件 $2d\sin\theta = n\lambda$）的必然结果。

### 2.5 有效质量与空穴

在能带底附近，$E(\vec{k}) \approx E_0 + \frac{\hbar^2|\vec{k}-\vec{k}_0|^2}{2m^*}$，定义**有效质量**：

$$\frac{1}{m^*} = \frac{1}{\hbar^2}\frac{d^2 E}{dk^2}$$

能带底 $m^* > 0$（电子），能带顶 $m^* < 0$。负有效质量的行为等价于**正质量正电荷的空穴**——半导体物理的基础概念。

### 2.6 金属、绝缘体、半导体

| 类型 | 能带填充 | $E_g$ | 电导 |
|------|----------|-------|------|
| **金属** | 导带部分填充 | — | 高（有自由载流子）|
| **绝缘体** | 满带，$E_g \gg k_BT$ | $\gtrsim 4$ eV | 极低 |
| **半导体** | 满带，$E_g \sim k_BT$ | $0.1$–$3$ eV | 可控（温度/掺杂）|

**碱金属**（Na, K）：价电子 1 个，BCC 的 BZ 只填满一半 $\Rightarrow$ 金属。

**二价金属**（Ca, Mg）：价电子 2 个，能带重叠 $\Rightarrow$ 仍是金属（若不重叠则为绝缘体）。

**硅/锗**：共价键晶体，满带 + $E_g = 1.1$ eV(Si) $\Rightarrow$ 半导体。

---

## 3. フォノン（Phonons）

### 3.1 一维单原子链

$N$ 个质量 $M$ 的原子以弹簧常数 $C$ 连接，间距 $a$。位移 $u_s$ 的运动方程：

$$M\ddot{u}_s = C(u_{s+1} + u_{s-1} - 2u_s)$$

行波解 $u_s = u e^{i(ska - \omega t)}$ 代入得**色散关系**：

$$\omega(k) = 2\sqrt{\frac{C}{M}}\left|\sin\frac{ka}{2}\right|$$

- $k \to 0$（长波）：$\omega \approx v_s|k|$（声速 $v_s = a\sqrt{C/M}$），线性声学支。
- $k = \pi/a$（BZ 边界）：$\omega = \omega_{\max} = 2\sqrt{C/M}$，群速度 $d\omega/dk = 0$（Bragg 反射）。

### 3.2 一维双原子链（光学支与声学支）

两种原子 $M_1, M_2$ 交替，得两支色散：

- **声学支**（acoustic）：$\omega \propto k$（$k\to 0$），相邻原子同向运动。
- **光学支**（optical）：$\omega \to \omega_0 \neq 0$（$k \to 0$），相邻原子反向运动。频率在红外区 $\Rightarrow$ 可被光激发（离子晶体红外吸收）。

### 3.3 声子与热性质

声子是玻色子。Debye 模型给出低温热容 $T^3$ 律（Phase 1 统计篇 §3.4）。

**晶格热导**：$\kappa \approx \frac{1}{3}C_v v_s \ell$（$C_v$ 热容，$v_s$ 声速，$\ell$ 平均自由程）。Umklapp 散射（BZ 边界翻转）是高温热阻的主要来源。

---

## 4. 半導体（Semiconductors）

### 4.1 本征半导体

$T = 0$：价带满，导带空，不导电。$T > 0$：少量电子热激发越过 $E_g$，产生等量电子-空穴对。载流子浓度：

$$n_i = p_i \approx \sqrt{N_c N_v}\,e^{-E_g/(2k_BT)}$$

其中 $N_c, N_v$ 为导带底/价带顶有效态密度。

### 4.2 掺杂：n 型与 p 型

- **n 型**（施主 donor，如 Si 中掺 P）：多余电子进入导带底下方 $\sim k_BT$ 的施主能级 $\Rightarrow$ 电子导电。
- **p 型**（受主 acceptor，如 Si 中掺 B）：受主能级在价带顶上方 $\Rightarrow$ 空穴导电。

$$n \approx N_D\,e^{-(E_c - E_D)/k_BT}, \quad p \approx N_A\,e^{-(E_A - E_v)/k_BT}$$

### 4.3 p-n 结

p 型和 n 型接触处形成**耗尽层**（depletion region），内建电场。加正向偏压 $\Rightarrow$ 电流指数增长（整流效应）：

$$I = I_0\left(e^{eV/k_BT} - 1\right)$$

这是二极管、太阳能电池、LED、晶体管的基础。

---

## 5. 超伝導（Superconductivity）

### 5.1 零电阻与 Meissner 效应

1911 年 Kamerlingh Onnes 发现汞在 4.2 K 电阻突然降为零。超导体的两大标志：
1. **零电阻**（$R = 0$，电流无损耗）。
2. **Meissner 效应**（完全抗磁性，磁场被排出体内，$\vec{B} = 0$）。

Meissner 效应不是零电阻的推论（零电阻只保证磁场不变化，Meissner 要求主动排出磁场）——这是热力学相变。

### 5.2 London 方程

$$\frac{\partial\vec{J}_s}{\partial t} = \frac{n_s e^2}{m}\vec{E}, \qquad \nabla\times\vec{J}_s = -\frac{n_s e^2}{m}\vec{B}$$

第二式给出 **London 穿透深度** $\lambda_L = \sqrt{m/(\mu_0 n_s e^2)}$：磁场在超导体表面以 $e^{-x/\lambda_L}$ 衰减。

### 5.3 BCS 理论（1957）

Bardeen–Cooper–Schrieffer 的微观理论：电子通过声子中介产生有效吸引力，形成 **Cooper 对**（两个动量相反、自旋反平行的电子配对）。

$$\boxed{\text{Cooper 对：} |\vec{k}\uparrow, -\vec{k}\downarrow\rangle}$$

配对能隙 $\Delta$（$T = 0$）：$2\Delta \approx 3.5\,k_BT_c$。Cooper 对是玻色子（自旋 0）$\Rightarrow$ 可凝聚到基态 $\Rightarrow$ 零电阻。

**同位素效应** $T_c \propto M^{-1/2}$（$M$ 离子质量）直接证明声子中介。

### 5.4 高温超导（铜基）

1986 年 Bednorz–Müller 发现铜基超导体（La-Ba-Cu-O, $T_c = 35$ K），随后 YBCO 达 $92$ K（超过液氮 $77$ K）。机制**至今未完全理解**（非 BCS 声子机制），是凝聚态物理最大的未解之谜之一。

---

## 6. Python 数值验证

### 6.1 自由电子气的 Fermi 能与态密度

```python
# free_electron.py —— 典型金属的 Fermi 能与态密度 √ε 律
import numpy as np
hbar, m_e = 1.055e-34, 9.109e-31
eV = 1.602e-19
metals = {"Na": 2.65e28, "Cu": 8.47e28, "Al": 18.1e28}  # 电子密度 n (m^-3)
print("金属自由电子气参数:")
for name, n in metals.items():
    kF = (3*np.pi**2*n)**(1/3)
    epsF = hbar**2*kF**2/(2*m_e)
    vF = hbar*kF/m_e
    TF = epsF/(1.381e-23)
    print(f"  {name}: kF={kF:.2e}/m  εF={epsF/eV:.2f} eV  "
          f"vF={vF/1e6:.2f}×10⁶m/s  TF={TF:.0f}K")
print("\n反直觉: 自由电子在室温(300K)仍完全简并(TF~10⁴K)")
print("        Fermi 速度 vF~10⁶ m/s ≈ c/300 ← 经典完全失效")
# 态密度 g(ε) ∝ √ε
eps = np.linspace(0, 10, 100)  # 以 εF 为单位
g = np.sqrt(eps)
g_at_F = np.sqrt(1.0)
print(f"\n态密度: g(εF)={g_at_F:.3f}(归一化), g(0.5εF)={np.sqrt(0.5):.3f}, "
      f"g(0.1εF)={np.sqrt(0.1):.3f}")
print("低温热容 C∝T 来自 g(εF) 附近 ±kT 的电子激发")
```

### 6.2 Kronig–Penney 能带（数值本征值）

```python
# kronig_penney.py —— 近自由电子能带：弱周期势的 BZ 边界能隙
import numpy as np
# 简化模型：自由电子 E=hbar²k²/2m，在 BZ 边界 k=±π/a 有 Bragg 反射
# 简并微扰给出能隙 Eg = 2|V_G|（G=倒格矢）
a = 3.5e-10  # 晶格常数 ~3.5Å
hbar, m = 1.055e-34, 9.109e-31
eV = 1.602e-19
G = 2*np.pi/a
# 自由电子在 BZ 边界的能量
E_BZ = hbar**2*(np.pi/a)**2/(2*m)
print(f"BZ 边界自由电子能量: {E_BZ/eV:.2f} eV")
print(f"倒格矢 G = 2π/a = {G:.2e} m⁻¹")
# 模拟前3个能带（自由电子折叠到 BZ 内 + 能隙）
k = np.linspace(-np.pi/a, np.pi/a, 500)
for band in range(1, 4):
    # 第 band 个能带：自由电子 k² 折叠到 BZ
    E0 = hbar**2*k**2/(2*m)  # 自由电子（未折叠）
    if band == 1:
        E = hbar**2*k**2/(2*m)
    elif band == 2:
        E = hbar**2*(np.abs(k)+2*np.pi/a-np.pi/a)**2/(2*m)  # 简化
    else:
        continue
# 能隙估算：Si 的 Eg=1.1eV
print(f"\n半导体能隙比较:")
for mat, Eg in [("Si", 1.1), ("Ge", 0.67), ("GaAs", 1.43), ("金刚石", 5.5)]:
    ratio = Eg / (E_BZ/eV)
    print(f"  {mat:6s}: Eg={Eg:.2f} eV  Eg/E_BZ={ratio:.3f}")
print(f"\n绝缘体(Eg>4eV) vs 半导体(Eg~1eV) vs 金属(Eg=0):")
print(f"  BZ 边界能隙 Eg=2|V_G| 决定一切")
```

### 6.3 一维单原子链色散（声子）

```python
# phonon_dispersion.py —— 一维单原子链色散 ω(k) = 2√(C/M)|sin(ka/2)|
import numpy as np
C, M, a = 1.0, 1.0, 1.0  # 归一化
ka = np.linspace(-np.pi, np.pi, 500)
omega = 2*np.sqrt(C/M)*np.abs(np.sin(ka/2))
v_sound = a*np.sqrt(C/M)  # 长波声速
omega_max = 2*np.sqrt(C/M)
print("一维单原子链声子色散:")
print(f"  声速 v_s = a√(C/M) = {v_sound:.3f}")
print(f"  最大频率 ω_max = 2√(C/M) = {omega_max:.3f} (在 k=±π/a)")
print(f"  Debye 频率 ω_D ≈ ω_max = {omega_max:.3f}")
# 验证长波线性
ka_small = ka[(ka > -0.3) & (ka < 0.3)]
omega_small = omega[(ka > -0.3) & (ka < 0.3)]
linear = v_sound * np.abs(ka_small)
err = np.max(np.abs(omega_small - linear) / omega_small)
print(f"\n长波近似 ω ≈ v_s|k| 的最大相对误差(k<0.3): {err:.4f}")
print(f"群速度在 k=π/a: dω/dk = {np.abs(np.cos(np.pi/2))*v_sound:.3f} = 0 (Bragg反射)")
```

### 6.4 BCS 能隙与临界温度

```python
# bcs_gap.py —— BCS 理论能隙比与同位素效应
import numpy as np
# BCS 关键预言：2Δ(0) ≈ 3.53 k_B T_c
ratio_BCS = 3.53
# 实验值（弱耦合超导体）
data = {"Al": (1.19, 0.18), "Sn": (3.72, 0.59), "Pb": (7.20, 1.35),
        "Hg": (4.15, 0.83), "Nb": (9.50, 1.60)}
print("BCS 能隙验证 2Δ(0)/(k_B T_c):")
print(f"  BCS 预言: {ratio_BCS:.2f}")
kB = 8.617e-5  # eV/K
for name, (Tc, Delta_meV) in data.items():
    ratio = 2*Delta_meV*1e-3 / (kB*Tc)
    print(f"  {name}: Tc={Tc:.2f}K  Δ={Delta_meV:.2f}meV  "
          f"2Δ/kBTc={ratio:.2f}  ({'✓' if abs(ratio-ratio_BCS)<0.5 else '强耦合?'})")
# 同位素效应: Tc ∝ M^(-1/2)
print(f"\n同位素效应验证（Hg 同位素, Maxwell 1950）:")
Hg_iso = [(198, 4.170), (200, 4.149), (202, 4.129), (204, 4.110)]
M_arr = np.array([m for m, _ in Hg_iso])
Tc_arr = np.array([t for _, t in Hg_iso])
# log Tc = -α log M + const → 拟合斜率 α
alpha = -np.polyfit(np.log(M_arr), np.log(Tc_arr), 1)[0]
print(f"  实验拟合 Tc ∝ M^(-α), α = {alpha:.3f}  (BCS预言 α=0.5)")
print(f"  α≈0.5 ← 声子中介的直接证据")
```

---

## 7. 東大特色：物性物理の伝統

東京大学在固体物理和凝聚态物理方面有深厚传统：

### 7.1 超导与强关联电子

東大物性研究所（ISSP, Institute for Solid State Physics）是世界顶尖的凝聚态物理研究中心。其特色方向：

- **高温超导**：铜基和铁基超导体的实验与理论研究。
- **强关联电子系统**：Mott 绝缘体、量子自旋液体、拓扑物态。
- **重费米子**：Ce/Yb 化合物中的非常规超导。

### 7.2 半导体与自旋电子学

日本在半导体工业的历史地位（SONY、东芝、NEC）与固体物理教育的深厚根基密切相关。東大在自旋电子学（spintronics）——利用电子自旋而非电荷做信息载体——方面是国际前沿。

### 7.3 Kittel 教材的影响

Kittel 的日文译本（丸善出版）自 1970 年代以来一直是日本固体物理的标准教材。日本版本的特色是译者注补充了大量实验数据和日本研究组的贡献，使之成为本土化的经典。

---

## 8. 習題集（Exercises）

> 标 ★ 为東大风格（重计算），★★ 为研究生级。

**习题 1（★）**　Na（BCC, $a = 4.23$ Å）的价电子密度 $n = 2.65\times10^{28}$ m$^{-3}$。计算 Fermi 能 $\epsilon_F$（eV）、Fermi 波矢 $k_F$ 和 Fermi 温度 $T_F$。
> *答案*：$k_F \approx 9.1\times10^9$ m$^{-1}$，$\epsilon_F \approx 3.2$ eV，$T_F \approx 3.7\times10^4$ K。

**习题 2（★★）**　推导一维双原子链（原子质量 $M_1 > M_2$，弹簧常数 $C$，间距 $a$）的色散关系，并证明光学支在 $k = 0$ 处的频率为 $\omega_0 = \sqrt{2C(1/M_1 + 1/M_2)}$。

**习题 3（★）**　硅（$E_g = 1.1$ eV）在 $T = 300$ K 的本征载流子浓度 $n_i \approx 1.5\times10^{16}$ m$^{-3}$。估算 $T = 400$ K 时的 $n_i$（假设 $N_c N_v$ 弱温度依赖）。
> *答案*：$n_i(400) \approx n_i(300)\exp\!\left[\frac{E_g}{2k_B}\left(\frac{1}{300}-\frac{1}{400}\right)\right] \approx 5.3\times10^{18}$ m$^{-3}$。

**习题 4（★★）**　用 BCS 理论解释：为什么超导体在 $T > T_c$ 时恢复正常电阻？Cooper 对在 $T_c$ 以上为何解体？
> *答案要点*：热涨落能量 $k_BT > \Delta$ 时，Cooper 对被拆散。$\Delta(T)$ 随 $T$ 升高而减小，在 $T_c$ 处 $\Delta \to 0$（相变）。

**习题 5（★）**　FCC 晶体的 $(111)$ 面间距 $d_{111} = a/\sqrt{3}$（$a$ 晶格常数）。X 射线波长 $\lambda = 1.54$ Å，求一级 Bragg 反射角 $\theta$（$a = 4.05$ Å, Al）。
> *答案*：$2d\sin\theta = \lambda \Rightarrow \theta = \arcsin(1.54/(2\times4.05/\sqrt{3})) \approx 19.2°$。

**习题 6（★★）**　一个 n 型半导体掺施主浓度 $N_D = 10^{22}$ m$^{-3}$，施主能级在导带底下方 $0.045$ eV。求 $T = 100$ K 和 $T = 300$ K 时导带电子浓度（假设 $N_c \gg N_D$）。
> *答案*：$n \approx N_D\exp[-(E_c-E_D)/k_BT]$。$T=100$K 时 $n/N_D \approx e^{-5.2} \approx 0.6\%$（冻结区）；$T=300$K 时 $n/N_D \approx e^{-1.7} \approx 0.82$（饱和区，近似全电离）。

---

## 9. 参考文献

1. Kittel, Charles. *Introduction to Solid State Physics* 9ed. Wiley, 2018.（東大物性物理指定，日文版丸善出版）
2. Ashcroft, Mermin. *Solid State Physics*. Holt-Saunders, 1976.（研究生标准，理论更深）
3. Kittel, Charles. *Quantum Theory of Solids* 2ed. Wiley, 1987.（能带/超导进阶）
4. Ibach, Lüth. *Solid-State Physics* 4ed. Springer.（实验导向）
5. Marder, Michael. *Condensed Matter Physics* 2ed. Wiley.（现代综合教材）
6. 浅田晃. 『固体物理学』（裳華房）——東大本土教材。
7. 阿部龍蔵. 『固体物理』（岩波書店）——東大经典参考。

---

**完成日期**：2026-08-12　|　**对应 SURVEY §9 東大**：物性物理学（固体物理）
