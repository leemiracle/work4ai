# -*- coding: utf-8 -*-
"""反馈的价值在于模型不准:不稳定二阶对象上,开环前馈 vs 闭环反馈(00/04 章配套实验)。

对象(真实): ÿ = b_true·y + u + d   ——不稳定二阶系统(倒立摆型:正刚度)
名义模型:    ÿ = y + u,b_nom = 1;失准 Δ 加在刚度上:b_true = 1+Δ
             (你估错了对象自身的不稳定度——最常见的模型误差形态)
参考轨迹:    r(t) = 1-(1+αt)e^{-αt},α=1.5(光滑,0/1/2 阶导数全解析,
             r(0)=ṙ(0)=0,与对象零初值衔接)
扰动:        d(t) = 0.2·1{t≥4}(输入端阶跃,仅 [3] 增益扫描用)
测量噪声:    n(t),ZOH 分段常值(每 5 步换一次),σ=0.02,同种子

两案对比:
  ① 开环前馈(依赖模型):u_ff = r̈ - b_nom·r,按名义模型逆动力学
     预先算好,不看 y 一眼——模型准(Δ=0)时 y≡r(解析精确);
     刚度失准时误差动力学 ë=(1+Δ)e+Δr 以 e^{√(1+Δ)t} 指数发散
     (对象不稳定,开环误差无人纠正)——前馈的优势只生活在
     Δ=0 这个测度零的点上
  ② 闭环反馈(PID,微分作用于测量):u = Kp(r-y_m)+Ki·ξ-Kd·ẏ,
     ξ̇=r-y_m——同一 Δ 下闭环特征方程 s²+Kd·s+(Kp-b_true) 在
     宽失准区间保持稳定(Kp=8 → Δ<7 全稳),积分项把稳态误差
     也吃掉:反馈对模型不确定性的鲁棒性

五个结构化断言:
  ① 模型准确(Δ=0)时前馈与反馈等效可用:前馈误差≈数值精度
     (完美逆),反馈终段误差也归容许带——设计点上两案都不吃亏
  ② 模型失准(Δ=0.5)时前馈性能崩塌(max 误差>10,指数发散)
     而反馈保持(max<1.0,终段 RMS<0.05)
  ③ 崩塌是系统性的:Δ 扫描上前馈终段误差单调恶化、放大>10³;
     反馈终段误差全程压在带内
  ④ 反馈增益 g 扫描(0.5→8,Δ=0.3,含 t=4 阶跃扰动):扰动峰值
     偏差随 g 单调下降(高增益买抑制)
  ⑤ 同一扫描上噪声的账单随 g 单调上升:控制量噪声 RMS 近乎
     ∝g(执行器付账,首尾比>10);输出端噪声近持平(通带内
     补敏感度 |T|≈1,增益不改低频跟踪)——反馈的代价:抑制力
     与噪声敏感性的权衡曲线,没有免费的高增益
⚠ 纪律(02/04 章):二阶线性对象+单参数失准是教学最小展示,真实
工程的失准是全频段未建模动态(乘性摄动),"反馈保持"的边界由
稳定裕度与 Bode 积分约束(00 章);噪声 ZOH 化是教学处理(真实
微分项需滤波);本脚本输出为教学演示级证据,PID 参数为示意值
非整定建议。

跑法: python experiments/feedback_value.py
"""

import math
import random

SEED = 20260907
DT = 0.002          # RK4 步长
T_END = 8.0         # 仿真时长
ALPHA = 1.5         # 参考轨迹形状参数
# 反馈基增益(PID,Kd 作用于测量侧):名义闭环 s²+Kd·s+(Kp-1)
KP0, KI0, KD0 = 8.0, 4.0, 4.0

KP_G = KI_G = KD_G = 0.0   # 当前增益(由 set_gains 设定)


# ---------------------------------------------------------------- 参考轨迹
def ref(t):
    """r 及 1/2 阶导数(全解析)。"""
    a = ALPHA
    e = math.exp(-a * t)
    return (1.0 - (1.0 + a * t) * e,
            a * a * t * e,
            a * a * (1.0 - a * t) * e)


def u_feedforward(t):
    """开环前馈:名义模型逆动力学(只看 r 与名义刚度,不看 y)。"""
    r, _, ddr = ref(t)
    return ddr - r


# ---------------------------------------------------------------- 闭环仿真
def simulate(b_true, gains, noise_seq=None, hold=5,
             d_step_t=math.inf, d_val=0.0):
    """RK4 积分全耦合三状态 [y, ẏ, ξ](ξ=积分器状态)。

    控制律 u = Kp(r-y_n)+Ki·ξ-Kd·ẏ,y_n = y+n(噪声 ZOH,步内常值,
    步内导数为零——微分项不被差分噪声污染的教学化处理)。
    返回 (时刻表, y 表, u 表)。
    """
    kp, ki, kd = gains
    n_steps = int(round(T_END / DT))
    s = [0.0, 0.0, 0.0]           # y, v=ẏ, ξ
    ts, ys, us = [], [], []
    noise = 0.0
    for i in range(n_steps):
        t = i * DT
        if noise_seq is not None and i % hold == 0:
            j = i // hold
            noise = noise_seq[j] if j < len(noise_seq) else 0.0

        def f(tt, st):
            y, v, xi = st
            r, _, _ = ref(tt)
            u = kp * (r - (y + noise)) + ki * xi - kd * v
            d = d_val if tt >= d_step_t else 0.0
            return (v, b_true * y + u + d, r - (y + noise))

        k1 = f(t, s)
        s2 = [s[j] + DT / 2 * k1[j] for j in range(3)]
        k2 = f(t + DT / 2, s2)
        s3 = [s[j] + DT / 2 * k2[j] for j in range(3)]
        k3 = f(t + DT / 2, s3)
        s4 = [s[j] + DT * k3[j] for j in range(3)]
        k4 = f(t + DT, s4)
        s = [s[j] + DT / 6 * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j])
             for j in range(3)]
        u_now = kp * (ref(t + DT)[0] - (s[0] + noise)) + ki * s[2] \
            - kd * s[1]
        ts.append(t + DT)
        ys.append(s[0])
        us.append(u_now)
    return ts, ys, us


def simulate_ff(b_true):
    """开环前馈仿真(同一 RK4 内核,ξ 恒零)。"""
    ts, ys, us = [], [], []
    n_steps = int(round(T_END / DT))
    s = [0.0, 0.0]

    def f(tt, st):
        return (st[1], b_true * st[0] + u_feedforward(tt))

    for i in range(n_steps):
        t = i * DT
        k1 = f(t, s)
        k2 = f(t + DT / 2, [s[j] + DT / 2 * k1[j] for j in range(2)])
        k3 = f(t + DT / 2, [s[j] + DT / 2 * k2[j] for j in range(2)])
        k4 = f(t + DT, [s[j] + DT * k3[j] for j in range(2)])
        s = [s[j] + DT / 6 * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j])
             for j in range(2)]
        ts.append(t + DT)
        ys.append(s[0])
        us.append(u_feedforward(t + DT))
    return ts, ys, us


def metrics(ts, ys, t_from=0.0):
    """max|y-r|(t≥t_from)与终段(该区间最后 25%)RMS。"""
    errs = [abs(y - ref(t)[0]) for t, y in zip(ts, ys) if t >= t_from]
    tail = errs[int(len(errs) * 0.75):]
    rms = math.sqrt(sum(e * e for e in tail) / max(len(tail), 1))
    return max(errs), rms


def make_noise(sigma=0.02, hold=5):
    """同种子 ZOH 噪声序列:各增益运行共用,隔离增益效应。"""
    rng = random.Random(SEED)
    need = math.ceil(T_END / DT / hold) + 2
    return [rng.gauss(0.0, sigma) for _ in range(need)]


def fmt(x):
    return f"{x:.2e}" if x >= 100 or (x < 0.01) else f"{x:.4f}"


# ---------------------------------------------------------------- 主流程
def main():
    print("=" * 76)
    print("反馈的价值在于模型不准:不稳定二阶对象 ÿ=b·y+u,前馈 vs 反馈"
          f"(seed={SEED},dt={DT})")
    print("=" * 76)

    # --- [1] 设计点 Δ=0:前馈与反馈等效可用 ----------------------------
    print("\n[1] 设计点 Δ=0(模型准确):两案都把误差压进容许带")
    g1 = (KP0, KI0, KD0)
    ts, ys, _ = simulate_ff(1.0)
    e_ff0, r_ff0 = metrics(ts, ys)
    ts, ys, _ = simulate(1.0, g1)
    e_fb0, r_fb0 = metrics(ts, ys)
    print(f"    前馈: max_err={e_ff0:.2e}  终段RMS={r_ff0:.2e}"
          "(完美逆:数值精度级)")
    print(f"    反馈: max_err={fmt(e_fb0)}  终段RMS={r_fb0:.2e}"
          "(瞬态预算内,积分项收尾)")

    # --- [2] 模型失准:前馈崩塌 vs 反馈保持 -----------------------------
    print("\n[2] 刚度失准 Δ 扫描(前馈按名义模型冻结,反馈看误差就纠)")
    print(f"{'Δ':>6} {'前馈max_err':>13} {'前馈终RMS':>12}"
          f" {'反馈max_err':>13} {'反馈终RMS':>12}")
    ff_max, ff_rms, fb_max, fb_rms = {}, {}, {}, {}
    for delta in (0.0, 0.1, 0.2, 0.3, 0.5):
        ts, ys, _ = simulate_ff(1.0 + delta)
        ff_max[delta], ff_rms[delta] = metrics(ts, ys)
        ts, ys, _ = simulate(1.0 + delta, g1)
        fb_max[delta], fb_rms[delta] = metrics(ts, ys)
        print(f"{delta:>6.1f} {ff_max[delta]:>13.2e} {ff_rms[delta]:>12.2e}"
              f" {fmt(fb_max[delta]):>13} {fb_rms[delta]:>12.2e}")
    blowup = ff_rms[0.5] / max(ff_rms[0.0], 1e-300)
    ff_monotone = all(ff_rms[d] < ff_rms[d2] for d, d2 in
                      [(0.0, 0.1), (0.1, 0.2), (0.2, 0.3), (0.3, 0.5)])

    # --- [3] 增益权衡曲线:扰动抑制 vs 噪声放大 -------------------------
    print("\n[3] 增益 g 扫描(Δ=0.3;t=4 输入阶跃扰动 0.2;"
          "噪声 σ=0.02 同种子)")
    print(f"{'g':>5} {'扰动峰值偏差':>14} {'输出噪声RMS':>14}"
          f" {'控制量噪声RMS':>15}")
    noise_seq = make_noise()
    dist_peak, out_noise, ctl_noise = {}, {}, {}
    for g in (0.5, 1.0, 2.0, 4.0, 8.0):
        gains = (g * KP0, g * KI0, g * KD0)
        ts, yc, _ = simulate(1.3, gains, d_step_t=4.0, d_val=0.2)
        peak, _ = metrics(ts, yc, t_from=4.0)
        ts, yn, un = simulate(1.3, gains, noise_seq=noise_seq,
                              d_step_t=4.0, d_val=0.2)
        dy = [a - b for a, b in zip(yn, yc)]
        _, _, uc = simulate(1.3, gains, d_step_t=4.0, d_val=0.2)
        du = [a - b for a, b in zip(un, uc)]
        rms_y = math.sqrt(sum(d * d for d in dy) / len(dy))
        rms_u = math.sqrt(sum(d * d for d in du) / len(du))
        dist_peak[g], out_noise[g], ctl_noise[g] = peak, rms_y, rms_u
        print(f"{g:>5.1f} {fmt(peak):>14} {fmt(rms_y):>14}"
              f" {fmt(rms_u):>15}")
    gs = [0.5, 1.0, 2.0, 4.0, 8.0]
    dist_down = all(dist_peak[gs[i + 1]] < dist_peak[gs[i]]
                    for i in range(len(gs) - 1))
    ctl_up = all(ctl_noise[gs[i + 1]] > ctl_noise[gs[i]]
                 for i in range(len(gs) - 1))
    print(f"    输出端噪声近持平({fmt(out_noise[0.5])}→"
          f"{fmt(out_noise[8.0])}:通带内|T|≈1)——账单在执行器:")

    # --- [4] 结构化断言 -------------------------------------------------
    print("\n[4] 结构化断言")
    checks = [
        ("① Δ=0 等效可用:前馈 max<1e-6(完美逆),反馈 max<0.35 且"
         "终段RMS<0.02", e_ff0 < 1e-6 and e_fb0 < 0.35 and r_fb0 < 0.02),
        ("② Δ=0.5 前馈崩塌(max>10)而反馈保持(max<1.0,终RMS<0.05)",
         ff_max[0.5] > 10.0 and fb_max[0.5] < 1.0 and fb_rms[0.5] < 0.05),
        ("③ 崩塌系统性:前馈终RMS 随Δ单调恶化且放大>10³,"
         "反馈终RMS 全程<0.05",
         ff_monotone and blowup > 1e3 and all(v < 0.05
                                              for v in fb_rms.values())),
        ("④ 高增益买扰动抑制:峰值偏差随 g 单调下降,首尾比>2",
         dist_down and dist_peak[0.5] / dist_peak[8.0] > 2.0),
        ("⑤ 高增益付噪声代价:控制量噪声RMS 随 g 单调上升,首尾比>10",
         ctl_up and ctl_noise[8.0] / ctl_noise[0.5] > 10.0),
    ]
    for name, ok in checks:
        print(f"    [{'PASS' if ok else 'FAIL'}] {name}")
        assert ok, name

    print("\n⚠ 纪律:线性二阶对象+单参数失准是教学最小展示;真实失准是")
    print("  全频段未建模动态,反馈的'保持'有边界(稳定裕度/Bode 积分,")
    print("  00 章);噪声 ZOH 化是教学处理;PID 参数为示意值非整定建议。")
    print("=" * 76)
    print("结论:前馈的优势生活在 Δ=0 这个测度零的点上——反馈的全部")
    print("价值恰在模型不准处;而它的代价是增益越高噪声放大越大:")
    print("鲁棒性与噪声敏感性共用一条权衡曲线,没有免费的高增益。")


if __name__ == "__main__":
    main()
