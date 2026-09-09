# -*- coding: utf-8 -*-
"""
德拜屏蔽：等离子体如何"抹平"电场（00/04 章实测）
=================================================
对应章：00-体系结构（集体行为第一性证据+λ_D=v_th/ω_p 自证）、04-转代码（最小 PIC 走廊+坑清单）。

三幕结构（无碰撞 1D 静电 PIC，密度语义归一化 n0=1、真实荷质比 q/m=-1）：
  Part A  解析-数值对照：线性化泊松-玻尔兹曼方程 φ'' = φ/λ_D² 的三对角解
          vs 精确解 sinh(L-x)/sinh(L)（截断误差 O(h²) 内一致）。
  Part B1 频率标定：密度正弦扰动激发等离子体振荡，谱分析测出本系统的 ω_p。
  Part B2 屏蔽涌现：中央固定测试电荷，电子云自发重排，势剖面衰减成 exp 形；
          拟合涌现屏蔽长度 λ_fit。

核心断言（实证自洽）：**λ_fit ≈ v_th/ω_p,measured** —— 模拟不背诵任何常数，
自己测出等离子体频率与屏蔽长度，验证它们被 λ_D = v_th/ω_p 焊在一起
（00 章 ✨美之时刻① 的计算化呈现：屏蔽与振荡是同一枚硬币——电子云的惯性）。

调试坑清单（本脚本开发中逐一踩过，04 章正文详述）：
  1. λ_D ≥ Δx——网格加热/有限网格不稳定性（本例 λ_D=16Δx，安全）
  2. v_max·dt ≤ Δx——尾部粒子单步跳格 → 力采样混叠 → 相干加热
  3. E 的谱法符号：E = -dφ/dx → E_k = -iρ_k/k（写反 = 反向力 = 负质量爆炸，
     症状：势飚至 ±百量级、与源强度无关、随机装载同样发生）
  4. 宏粒子保持真实荷质比（q/m 不随粒子权重缩放）；CIC 沉积按密度语义（÷Δx）
  5. 等距"安静启动"与网格共振（N/NG 为整数时 CIC 走样相干叠加）——改随机装载

运行：python debye_shielding.py   （numpy + scipy）
归一化：n0=1（密度语义），v_th=4，λ_D=v_th/ω_p（ω_p 由 B1 实测标定）。
"""
import numpy as np

# ── 公共内核 ────────────────────────────────────────────────────────────
NG, L, N = 256, 64.0, 400_000
V_TH, DT = 4.0, 0.02
LAM_D_NOMINAL, DX = V_TH, L / NG       # λ_D 标称（以 ω_p=1 计）；真值由 B1 实测标定
W = (L / N) / DX                       # 每宏粒子电荷（总电荷 L/N）按密度语义沉积

class Plasma:
    """1D 静电 PIC：密度语义 + 谱法场解（E_k = -iρ_k/k）+ leapfrog。"""
    def __init__(self, seed, charge=0.0):
        rng = np.random.default_rng(seed)
        self.x = rng.random(N) * L
        self.v = rng.standard_normal(N) * V_TH
        self.q = charge                  # 中心固定测试电荷（总电荷）

    def dep(self):
        rho = np.ones(NG)                # 固定离子背景，密度 +1
        xs = self.x / DX
        i0 = np.floor(xs).astype(int) % NG
        f = xs - np.floor(xs)
        np.add.at(rho, i0, -W * (1 - f))
        np.add.at(rho, (i0 + 1) % NG, -W * f)
        if self.q:
            rho[NG // 2] += self.q / DX
        return rho

    def field(self, rho):
        rhok = np.fft.rfft(rho) * DX     # 离散和 → 连续傅里叶变换
        k = 2 * np.pi * np.fft.rfftfreq(NG, d=DX)
        k[0] = 1.0
        Ek = -1j * rhok / k; Ek[0] = 0   # E = -dφ/dx（符号错=反向力=爆炸，坑清单③）
        phik = rhok / k**2; phik[0] = 0
        return np.fft.irfft(Ek, n=NG), np.fft.irfft(phik, n=NG)

    def field_at_particles(self, E):
        xs = self.x / DX
        i0 = np.floor(xs).astype(int) % NG
        f = xs - np.floor(xs)
        return E[i0] * (1 - f) + E[(i0 + 1) % NG] * f

    def advance(self):
        E, _ = self.field(self.dep())
        self.v += DT * (-1.0) * self.field_at_particles(E)
        self.x[:] = (self.x + DT * self.v) % L

# ── Part A：方程路线（线性化 P-B，λ_D=1 归一化）─────────────────────────
def part_a():
    from scipy.linalg import solve_banded
    Lv, Nv = 10.0, 2000
    x = np.linspace(0, Lv, Nv)
    h = x[1] - x[0]
    n = Nv - 2
    ab = np.zeros((3, n))
    ab[0, 1:] = 1.0
    ab[1, :] = -(2 + h * h)
    ab[2, :-1] = 1.0
    rhs = np.zeros(n); rhs[0] = -1.0
    phi = np.concatenate([[1.0], solve_banded((1, 1), ab, rhs), [0.0]])
    exact = np.sinh(Lv - x) / np.sinh(Lv)
    err = np.max(np.abs(phi - exact))
    print(f"[A] 线性化方程三对角解 vs 精确解 sinh(L-x)/sinh(L)：最大误差 = {err:.2e}（二阶差分截断 O(h²)）")
    assert err < 1e-6, f"Part A 误差过大: {err}"
    return True

# ── Part B1：频率标定（实测 ω_p）─────────────────────────────────────────
def part_b1():
    p = Plasma(seed=7)
    # 叠加密度调制（逆变换采样，k=1 模式，幅度 ~6%）
    u = p.x / L
    p.x[:] = (u + 0.02 * np.sin(2 * np.pi * u)) % 1.0 * L
    E, _ = p.field(p.dep())
    p.v += 0.5 * DT * (-1.0) * p.field_at_particles(E)
    ts, e1 = [], []
    for s in range(6000):
        p.advance()
        if s % 2 == 0:
            ts.append(s * DT); e1.append(float(p.field(p.dep())[0][5]))
    ta = np.array(ts); ea = np.array(e1); ea -= ea.mean()
    sp = np.abs(np.fft.rfft(ea * np.hanning(len(ea))))
    fr = np.fft.rfftfreq(len(ea), d=(ta[1] - ta[0]))
    peak = fr[int(np.argmax(sp[1:])) + 1]
    omega = 2 * np.pi * peak
    lam_theory = V_TH / omega
    print(f"[B1] 密度扰动激发振荡：实测 ω_p = {omega:.3f}（谱峰最显著；本归一化下的真值）")
    print(f"     → λ_D 理论 = v_th/ω_p = {lam_theory:.2f}（不用标称值，全部实证）")
    return omega, lam_theory

# ── Part B2：屏蔽涌现（拟合 λ_fit）──────────────────────────────────────
def part_b2():
    p = Plasma(seed=42, charge=1.0)
    E, _ = p.field(p.dep())
    p.v += 0.5 * DT * (-1.0) * p.field_at_particles(E)
    nsteps = 4000
    acc = np.zeros(NG); ns = 0
    for s in range(nsteps):
        p.advance()
        if s > nsteps // 3:
            _, phi = p.field(p.dep())
            acc += phi; ns += 1
    phi = acc / ns
    drift = abs(np.sqrt(np.mean(p.v**2)) / V_TH - 1)
    pr = np.roll(phi, NG // 2)
    pr = 0.5 * (pr + pr[::-1])                     # 对称平均
    kernel = np.ones(5) / 5                        # 5 格平滑（≪λ_D）
    pr = np.convolve(np.pad(pr, 2, mode="wrap"), kernel, mode="valid")
    rg = np.arange(NG) * DX
    m_far = (rg > 5.5 * LAM_D_NOMINAL) & (rg < 7.5 * LAM_D_NOMINAL)
    ps = pr - pr[m_far].mean()
    m = (rg > 0.8 * LAM_D_NOMINAL) & (rg < 2.2 * LAM_D_NOMINAL) & (ps > 0)
    assert m.sum() >= 5, f"有效拟合点不足: {m.sum()}"
    coef = np.polyfit(rg[m], np.log(ps[m]), 1)
    lam_fit = -1 / coef[0]
    print(f"[B2] 德拜屏蔽涌现：φ0 = {ps[0]:.3f}（eφ0/kT = {ps[0]/V_TH**2:.3f}，线性区 ✓）")
    print(f"     拟合屏蔽长度 λ_fit = {lam_fit:.2f}；能量漂移 {drift:.2%}（力符号正确性+稳定性 ✓）")
    assert drift < 0.02, f"异常加热: {drift:.2%}"
    assert ps[0] / V_TH**2 < 0.1, "超出线性区"
    return lam_fit

if __name__ == "__main__":
    part_a(); print()
    omega, lam_theory = part_b1(); print()
    lam_fit = part_b2(); print()
    rel = abs(lam_fit - lam_theory) / lam_theory
    print(f"[自洽断言] λ_fit = {lam_fit:.2f} vs v_th/ω_p = {lam_theory:.2f}：偏差 {rel:.1%}")
    assert rel < 0.15, f"λ_D = v_th/ω_p 自洽性超差: {rel:.1%}"
    print()
    print("全部断言通过 ✅  两课：")
    print("1. 电场进不了等离子体——不是被吸收，是被电子云的重排『折叠』在 λ_D 内；")
    print("2. 屏蔽长度与振荡频率不是两个知识，是一个：λ_D = v_th/ω_p。")
    print("   本模拟没有背诵这个公式——它自己测出 ω_p 与 λ_D，然后发现二者相焊。")
