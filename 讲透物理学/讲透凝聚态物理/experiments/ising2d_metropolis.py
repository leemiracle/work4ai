# -*- coding: utf-8 -*-
"""
2D Ising 模型 Metropolis 蒙特卡洛 —— 凝聚态物理家族实验（00/03/04 章现场）

回答三个问题：
  (1) 自发对称破缺：低温下系统从随机态自发"选边"（|m|→1）——没有人指挥；
  (2) 相变：自发磁化在 Onsager 精确解 Tc = 2/ln(1+√2) ≈ 2.269 处消失；
  (3) 理论对照：模拟 m(T) 与 Onsager 精确解 |m| = (1 - sinh(2/T)^{-4})^{1/8} 对账。

方法：checkerboard 向量化 Metropolis（红黑格交替整块更新，满足细节平衡）。
对应章：00-体系结构（支柱二）/ 03-可构造与结构（Peierls 之选边与临界涨落）/
       04-转代码（走廊②最小标本）。运行：python ising2d_metropolis.py
"""
import numpy as np

rng = np.random.default_rng(42)

L = 48            # 格点边长（有限尺寸：Tc 附近会被圆化，远离 Tc 处对照严格）
J = 1.0           # 铁磁耦合（kB=1）
T_C_ONSAGER = 2.0 / np.log(1.0 + np.sqrt(2.0))   # ≈ 2.269185


def onsager_magnetization(T: float) -> float:
    """Onsager 1944 精确解的自发磁化（T>=Tc 为 0）。热力学极限值。"""
    if T >= T_C_ONSAGER:
        return 0.0
    s = np.sinh(2.0 * J / T) ** (-4)
    return (1.0 - s) ** (1.0 / 8.0)


def metropolis_sweep(spins: np.ndarray, T: float) -> None:
    """一个 MC sweep：红黑棋盘各半，向量化整块尝试翻转（周期边界）。
    细节平衡：P(accept) = min(1, exp(-dE/T))。"""
    for parity in (0, 1):
        nb = (np.roll(spins, 1, 0) + np.roll(spins, -1, 0)
              + np.roll(spins, 1, 1) + np.roll(spins, -1, 1))
        dE = 2.0 * J * spins * nb
        mask = np.fromfunction(lambda y, x: (y + x) % 2, (L, L), dtype=int) == parity
        accept = (dE <= 0) | (rng.random((L, L)) < np.exp(-np.clip(dE, 0, 700) / T))
        flips = mask & accept
        spins[flips] *= -1


def magnetization(spins: np.ndarray) -> float:
    return abs(spins.mean())


def run_temperature(T: float, n_equil: int = 400, n_meas: int = 400) -> float:
    """单个温度：随机初态（高温淬火进场，让系统自己选边）→ 平衡 → 测量 |m| 均值。"""
    spins = rng.choice([-1, 1], size=(L, L))
    for _ in range(n_equil):
        metropolis_sweep(spins, T)
    ms = [magnetization(spins) for _ in range(n_meas) if metropolis_sweep(spins, T) or True]
    return float(np.mean(ms))


def main() -> None:
    print(f"2D Ising Metropolis  L={L}  (Onsager Tc = {T_C_ONSAGER:.6f})")
    print(f"{'T':>6} {'|m| 模拟':>10} {'|m| Onsager':>12} {'差':>8}")
    temps = [1.8, 2.0, 2.2, 2.269, 2.35, 2.6, 3.0]
    sim = {}
    for T in temps:
        m_sim = run_temperature(T)
        m_th = onsager_magnetization(T)
        sim[T] = m_sim
        print(f"{T:6.3f} {m_sim:10.4f} {m_th:12.4f} {m_sim - m_th:8.4f}")

    # ── 断言 1：深低温自发磁化接近满磁（对称破缺：系统自己选了边） ──
    assert sim[1.8] > 0.95, f"T=1.8 应接近满磁，实测 {sim[1.8]:.4f}"

    # ── 断言 2：高温顺磁（磁化≈0；有限尺寸残余 ~1/sqrt(N)） ──
    assert sim[3.0] < 0.15, f"T=3.0 应接近无磁，实测 {sim[3.0]:.4f}"

    # ── 断言 3：跨越 Tc 的塌陷——Tc 两侧磁化显著分层 ──
    m_below, m_above = sim[2.0], sim[2.6]
    assert m_below - m_above > 0.5, "Tc 两侧应看到自发磁化塌陷"
    # Tc 正上方的 2.35 已应显著低于低温值（有限尺寸圆化，阈值放宽松）
    assert sim[2.35] < 0.75 * m_below, "Tc 右侧应有明显塌陷趋势"

    # ── 断言 4：远离 Tc 处与 Onsager 精确解对账（有限尺寸偏差 O(1/L)，容差 0.12） ──
    for T in (1.8, 2.0, 2.6, 3.0):
        assert abs(sim[T] - onsager_magnetization(T)) < 0.12, \
            f"T={T}: 模拟 {sim[T]:.4f} vs Onsager {onsager_magnetization(T):.4f} 偏差过大"

    print("\n[ALL ASSERTS PASSED] 自发对称破缺可见（低温选边）；磁化在 Tc≈2.269 塌陷；"
          "远离 Tc 处与 Onsager 精确解对账通过（有限尺寸效应 O(1/L) 内）。")
    print("解读：你用 120 行代码见证了一次相变——这正是凝聚态'有效模型走廊'的最小完整标本。")


if __name__ == "__main__":
    main()
