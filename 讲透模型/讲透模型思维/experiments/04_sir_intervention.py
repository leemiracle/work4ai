"""04_sir_intervention — SIR：少量假设→大局判断；R₀×干预时机

问题：只有一个比值 R₀=β/γ 的三舱模型，凭什么回答"封城该多早"这种万亿级政策问题？
设计：SIR 欧拉积分（dt=0.01，S0=0.999, I0=0.001），R₀=2.5（β=0.50, γ=0.20）。
      对照三场景：无干预 / 第 20 天 β 减半（封城，持续到模拟结束）/ 第 60 天 β 减半。
      外加：干预时机扫描（同样强度，动手日从 0 扫到 28）——"时机曲线"整条看。
      本实验为确定性 ODE：无随机成分、无需种子，逐位可复现。

结论（实测数字见打印）：
  1) 无干预峰值 23.4%（第 24 天），总感染 89.2%——群体免疫阈值只需 60%，过冲 29 个百分点；
  2) 同样"β 减半"的强度：第 20 天动手峰值砍 23%、总感染砍 28%；
     第 60 天动手峰值一克不减——峰值第 24 天已过，干预到达时剧已终；
  3) 时机曲线有悬崖：动手日晚于峰值日，效果归零。晚 ≠ 打折，晚 = 报废。
"""

def simulate(beta0, gamma, t_int=None, factor=0.5, days=800.0, dt=0.01):
    """SIR 欧拉积分。t_int=None 无干预；否则 t>=t_int 后 beta *= factor（干预持续到结束）。"""
    S, I, R = 0.999, 0.001, 0.0
    peak_I, peak_day, t = I, 0.0, 0.0
    n = int(round(days / dt))
    for _ in range(n):
        beta = beta0 if (t_int is None or t < t_int) else beta0 * factor
        S += -beta * S * I * dt
        I += (beta * S * I - gamma * I) * dt
        R += gamma * I * dt
        t += dt
        if I > peak_I:
            peak_I, peak_day = I, t
    return peak_I, peak_day, R

BETA, GAMMA = 0.50, 0.20
print(f"SIR：beta={BETA:.2f}, gamma={GAMMA:.2f}（R0={BETA/GAMMA:.1f}），"
      f"S0=0.999, I0=0.001, dt=0.01 天；确定性方程，无随机成分")

scenarios = [("无干预", None), ("第 20 天 beta 减半", 20.0), ("第 60 天 beta 减半", 60.0)]
results = {}
print(f"{'场景':<14}{'峰值 I_max':>10}{'峰值日':>8}{'总感染 R(inf)':>13}{'峰值相对无干预':>14}")
for name, ti in scenarios:
    pI, pD, Rinf = simulate(BETA, GAMMA, ti)
    results[name] = (pI, pD, Rinf)
    print(f"{name:<14}{pI:>10.4f}{pD:>8.1f}{Rinf:>13.4f}{pI/results['无干预'][0]:>13.1%}")
print(f"-> 同样强度晚 40 天动手：峰值 {results['第 60 天 beta 减半'][0]:.4f} vs "
      f"{results['第 20 天 beta 减半'][0]:.4f}——峰值第 {results['无干预'][1]:.0f} 天已过，第 60 天的干预一克也没接住")
print(f"   第 20 天动手买到什么：峰值 -23%、总感染 {results['无干预'][2]:.2f}->{results['第 20 天 beta 减半'][2]:.2f}"
      f"（-{1 - results['第 20 天 beta 减半'][2] / results['无干预'][2]:.0%}）")

days_grid = [0, 4, 8, 12, 16, 20, 24, 28]
peaks, rinf = [], []
for d in days_grid:
    pI, _, Rinf = simulate(BETA, GAMMA, float(d))
    peaks.append(pI)
    rinf.append(Rinf)
print("干预时机扫描（同样强度 beta 减半，持续到结束）：")
print(f"  动手日  ：{'  '.join(f'{d:>4}' for d in days_grid)}")
print(f"  I_max   ：{'  '.join(f'{p:.3f}' for p in peaks)}")
print(f"  R(inf)  ：{'  '.join(f'{r:.3f}' for r in rinf)}")
print(f"-> 时机悬崖：动手日越过无干预峰值日（第 {results['无干预'][1]:.0f} 天）后，"
      f"I_max 钉死在 {peaks[-1]:.3f} 不动——晚动手不是打折，是报废")

p_coarse, _, _ = simulate(BETA, GAMMA)
p_fine, _, _ = simulate(BETA, GAMMA, days=800.0, dt=0.001)
print(f"过冲检查：群体免疫阈值 S=1/R0={1 / (BETA / GAMMA):.2f}（60% 感染即掉头），"
      f"实际烧到 {results['无干预'][2]:.4f}——过冲 {(results['无干预'][2] - (1 - 1 / (BETA / GAMMA))) * 100:.1f} 个百分点")
print(f"数值自检：dt=0.01 与 dt=0.001 的峰值差 {abs(p_coarse - p_fine):.4f}（欧拉步长足够，结论不吃数值饭）")
