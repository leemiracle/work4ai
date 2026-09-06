# -*- coding: utf-8 -*-
"""
不变质量：高能物理的"粒子身份证"（对应 00 章 §三 / 04 章走廊 2）
================================================================
核心命题：m^2 = E^2 - |p|^2 是洛伦兹不变量——实验室系能量动量千变万化，
  由衰变产物的四动量重建出的不变质量岿然不动，指向母粒子的静止质量。
  这正是 2012 年希格斯粒子在 H→γγ 道被发现的方法：把每一对光子的
  不变质量算出来画直方图，在 125 GeV 处冒出的峰 = 新粒子存在的证据。

三段实验：
  A. 静止 pi0 衰变（解析对照）：两光子各 67.49 MeV 背对背，重建 = m_pi0
  B. 飞行 pi0 衰变（洛伦兹不变性现场）：beta=0.6 的 pi0 向各方向辐射光子，
     单个光子能量在 ~[34, 135] MeV 间剧烈起伏——而不变质量恒为 m_pi0
     （注意：背对背只在母粒子静止系成立，实验室系两光子须一起 boost）
  C. 探测器分辨下的重建（现实工况）：能量加 3% 高斯 smearing，
     10 万事例的不变质量谱峰位仍锁定 135 MeV（粒子物理"找峰"原理）

运行：python invariant_mass_demo.py   （纯 numpy，输出各段断言结果）
"""

import numpy as np

M_PI0 = 134.9768e-3   # pi0 静质量, GeV（PDG 2024）
rng = np.random.default_rng(42)


def decay_pi0_rest(n):
    """pi0 -> gamma gamma 在母粒子静止系：两光子背对背，能量各 m/2，
    方向随机（pi0 自旋 0，衰变各向同性）。返回两光子的 (E, p)。"""
    costh = rng.uniform(-1, 1, n)
    phi = rng.uniform(0, 2 * np.pi, n)
    sinth = np.sqrt(1 - costh**2)
    u = np.stack([sinth * np.cos(phi), sinth * np.sin(phi), costh], axis=1)
    E = np.full(n, M_PI0 / 2)
    return E, u * E[:, None], E, -u * E[:, None]   # 光子1, 光子2(反向)


def boost(E, p, beta):
    """四动量沿 x 轴 boost（速度 beta）。返回实验室系 (E_lab, p_lab)。"""
    gamma = 1.0 / np.sqrt(1.0 - beta * beta)
    E_lab = gamma * (E + beta * p[:, 0])
    p_lab = p.copy()
    p_lab[:, 0] = gamma * (p[:, 0] + beta * E)
    return E_lab, p_lab


def invariant_mass(E1, p1, E2, p2):
    """两粒子系统的不变质量：M^2 = (E1+E2)^2 - |p1+p2|^2。"""
    E, p = E1 + E2, p1 + p2
    return np.sqrt(E * E - np.sum(p * p, axis=-1))


def main():
    n = 100_000
    E1, p1, E2, p2 = decay_pi0_rest(n)

    print("=" * 64)
    print("A. 静止 pi0 衰变：解析对照")
    m_rec = invariant_mass(E1, p1, E2, p2)
    err = np.abs(m_rec - M_PI0).max()
    print(f"   重建不变质量 = {m_rec.mean():.9f} GeV（PDG: {M_PI0:.7f}）")
    assert err < 1e-9, f"A 段失败: 最大偏差 {err}"
    print("   [PASS] 背对背等能光子对的不变质量 = pi0 质量（精确）")

    print("=" * 64)
    print("B. 飞行 pi0（beta=0.6）：洛伦兹不变性现场")
    beta = 0.6
    E1l, p1l = boost(E1, p1, beta)   # 两光子各自 boost（背对已破）
    E2l, p2l = boost(E2, p2, beta)
    e_all = np.concatenate([E1l, E2l]) * 1e3
    print(f"   单光子实验室能量范围: [{e_all.min():.1f}, {e_all.max():.1f}] MeV"
          f"（静止系恒为 {M_PI0/2*1e3:.1f} MeV）")
    m_fly = invariant_mass(E1l, p1l, E2l, p2l)
    err = np.abs(m_fly - M_PI0).max()
    print(f"   飞行衰变重建不变质量 = {m_fly.mean():.9f} GeV")
    assert err < 1e-9, f"B 段失败: 最大偏差 {err}"
    print("   [PASS] 能量动量全变，m^2 = E^2 - |p|^2 岿然不动 —— 不变量之美")

    print("=" * 64)
    print("C. 探测器分辨（3% 高斯 smearing）下的质量峰")
    sigma = 0.03
    E1s = E1l * rng.normal(1, sigma, n)          # 光子 1 能量被涂抹
    E2s = E2l * rng.normal(1, sigma, n)          # 光子 2 能量被涂抹
    p1s = p1l / E1l[:, None] * E1s[:, None]      # 方向不涂抹（量能器典型假设）
    p2s = p2l / E2l[:, None] * E2s[:, None]
    m_smear = invariant_mass(E1s, p1s, E2s, p2s)
    peak = np.median(m_smear)                       # 峰位用中位数抗尾巴
    width = 1.4826 * np.median(np.abs(m_smear - peak))  # MAD -> sigma
    print(f"   涂抹后谱峰位 = {peak*1e3:.2f} MeV, 分辨 sigma = {width*1e3:.2f} MeV")
    assert abs(peak * 1e3 - M_PI0 * 1e3) < 1.0, f"C 段失败: 峰位偏移 {peak*1e3-M_PI0*1e3:.2f} MeV"
    assert 2.0 < width * 1e3 < 12.0, f"C 段失败: 分辨异常 {width*1e3:.2f} MeV"
    print("   [PASS] 3% 能量分辨下峰位仍锁定 135 MeV —— 这就是'找峰即找粒子'")

    print("=" * 64)
    print("结论：单个光子能量毫无粒子信息（连续谱），")
    print("      两两组合的不变质量谱才有峰 —— 高能物理数据分析的第一课。")
    print("[ALL ASSERTS PASSED]")


if __name__ == "__main__":
    main()
