# -*- coding: utf-8 -*-
"""
pid_second_order.py — 二阶位置伺服的离散 PID 控制:数字闭环全流程数值实验

对应章:04-控制科学与技术转代码(走廊①:离散回路仿真走廊——ZOH/数字 PID 的最小骨架)/
       00-体系结构(✨美之时刻①:PID 三个字母统治工业——I/D 逐项关掉看系统退化)/
       03-可构造与结构(§1 整定的实验构造法:先跑 P 摸脾气,再加 I 消差,再加 D 压超调)
GB/T 41310 控制科学与技术 · 家族层实验

被控对象:质量-阻尼位置伺服  m·x'' + c·x' = u + d
  (执行器出力 u,恒值负载扰动 d——"起重机吊着货"的抽象)
控制:数字 PID,控制周期 Tc=50ms(零阶保持 ZOH),对象内部用 dt=0.5ms 数值积分
  · 微分作用于测量值(避免设定值突跳的 derivative kick),一阶滤波
  · 积分抗饱和(clamping——执行器饱和时停积分)
  · 执行器限幅 u∈[-10,10] N

运行:python pid_second_order.py   (纯标准库,无外部依赖)
"""

import math

# ── 对象参数 ──────────────────────────────────────────────
M, C = 1.0, 1.2          # 质量 kg / 阻尼 N·s/m
R = 1.0                  # 设定值:位置 1.0 m
U_MIN, U_MAX = -10.0, 10.0   # 执行器饱和
TC = 0.02                # 控制周期 50 Hz(数字控制节拍)
DT = 0.0005              # 对象积分步长
SUB = int(round(TC / DT))
D0, D1, T_DIST = -0.6, -1.2, 6.0   # 恒值负载;t=6s 后加重(扰动抑制试验)
T_END = 10.0


def plant_step(x, v, u, d, n, dt=DT):
    """半隐式 Euler 积分 n 个子步(力 u 经零阶保持恒定)——数字控制的忠实对象模型。"""
    for _ in range(n):
        a = (u + d - C * v) / M
        v += a * dt          # 先更新速度
        x += v * dt          # 再用新速度更新位置(半隐式:能量上更稳定)
    return x, v


def simulate(kp, ki, kd, r=R):
    """跑一次数字 PID 闭环,返回轨迹与指标。"""
    x, v = 0.0, 0.0
    integ, d_filt = 0.0, 0.0
    pv_prev = 0.0
    log = []
    n_steps = int(round(T_END / TC))
    for k in range(n_steps):
        t = k * TC
        d = D0 if t < T_DIST else D1
        e = r - x                                  # 误差
        d_raw = (x - pv_prev) / TC                 # 微分取测量值
        d_filt += 0.4 * (d_raw - d_filt)           # 一阶滤波(α=0.6)
        u_unsat = kp * e + integ - kd * d_filt
        u = max(U_MIN, min(U_MAX, u_unsat))        # 执行器饱和
        # 抗饱和 clamping:未饱和,或误差在把输出拉离饱和,才积分
        if u == u_unsat or (u_unsat < u and e < 0) or (u_unsat > u and e > 0):
            integ += ki * e * TC
        pv_prev = x
        x, v = plant_step(x, v, u, d, SUB)
        log.append((t + TC, x, u))
    return log


def metrics(log):
    """阶跃指标(分两段,工程惯例):初始阶跃的超调量/2%调节时间只看扰动前;
       扰动后另算恢复时间;末端稳态误差含扰动恢复。"""
    xs = [p[1] for p in log]
    pre = [p for p in log if p[0] <= T_DIST]            # 扰动前:初始阶跃段
    post_idx = next(i for i, p in enumerate(log) if p[0] > T_DIST)
    xs_pre = [p[1] for p in pre]
    overshoot = max(0.0, (max(xs_pre) - R) / R) * 100.0
    settle = None
    for i in range(len(pre)):
        if all(abs(p[1] - R) < 0.02 for p in pre[i:]):
            settle = pre[i][0]
            break
    recover = None                                       # 扰动后回到 ±2% 的时刻
    for i in range(post_idx, len(log)):
        if all(abs(p[1] - R) < 0.02 for p in log[i:]):
            recover = log[i][0] - T_DIST
            break
    ess = abs(xs[-1] - R)
    return overshoot, settle, ess, recover


def main():
    print("=" * 64)
    print("GB/T 41310 讲透控制科学与技术 · 实验:二阶系统的离散 PID 控制")
    print("对象: m·x'' + c·x' = u + d   (m=1.0, c=1.2, 执行器限幅 ±10N)")
    print("设定值: x=1.0 m;负载 d=-0.6N,t=6s 加重至 -1.2N(扰动抑制)")
    print("=" * 64)

    # [1] P-only:比例控制的先天残差(I 项必要性)
    log_p = simulate(kp=2.5, ki=0.0, kd=0.0)
    ov_p, st_p, ess_p, rec_p = metrics(log_p)
    pre_x = [p[1] for p in log_p if p[0] <= T_DIST - 0.5][-1]   # 扰动前末端
    ess_pre = abs(pre_x - R)
    print("\n[1] 纯 P 控制 (Kp=2.5, Ki=0, Kd=0)")
    print(f"    扰动前稳态误差 = {ess_pre:.3f} m (理论值 e_ss=|d|/Kp=0.6/2.5=0.240)")
    print("    → 恒值负载下纯比例必有残差:误差正是产生抵消力所需的'燃料'")
    assert 0.15 < ess_pre < 0.35, f"纯P扰动前稳态误差应≈0.24,实测 {ess_pre:.3f}"

    # [2] 完整 PID:超调/稳态/调节时间三指标(整定:高 P 摸脾气→加 I 消差→D 压振)
    log_pid = simulate(kp=20.0, ki=2.0, kd=7.0)
    ov, st, ess, rec = metrics(log_pid)
    print("\n[2] 完整 PID (Kp=20.0, Ki=2.0, Kd=7.0)")
    print(f"    初始阶跃:超调 = {ov:.2f} %,2% 调节时间 = {st:.2f} s")
    print(f"    末端稳态误差 = {ess:.4f} m(积分项消差)")
    assert ov < 10.0, f"超调 {ov:.2f}% 应 <10%"
    assert ess < 0.02, f"稳态误差 {ess:.4f} 应 <0.02(积分项消差)"
    assert st is not None and st < 4.0, f"调节时间应 <4s,实测 {st}"

    # [3] 扰动抑制:t=6s 负载加倍,P 与 PID 的分野
    post_x = [p[1] for p in log_pid if p[0] >= T_END - 0.5]
    dip = min(p[1] for p in log_pid if p[0] > T_DIST) - R
    print("\n[3] 扰动抑制(t=6s 负载 -0.6→-1.2N)")
    print(f"    PID 扰动最大跌落 = {dip:.4f} m,回到 ±2% 用时 {rec if rec is not None else -1:.2f} s,末端误差 = {abs(post_x[-1]-R):.4f} m")
    print("    → 高增益 P+D 先把负载突变按住,I 再把恒值负载'记进账本'永久消差")
    assert abs(post_x[-1] - R) < 0.02, "扰动后应回到设定值 ±0.02"
    assert dip > -0.10, f"扰动跌落 {dip:.4f} 应 <10%"
    # 纯 P 在扰动后误差恶化到 |d1|/Kp=0.48
    post_p = [p[1] for p in log_p if p[0] >= T_END - 0.5]
    print(f"    纯 P 同场景末端误差 = {abs(post_p[-1]-R):.3f} m(理论 0.48)——无 I 项,负载加重误差就加重")
    assert abs(post_p[-1] - R) > 0.3

    # [4] 饱和与抗饱和:全程控制量不越界,且没有 windup 拖尾
    us = [p[2] for p in log_pid]
    assert all(U_MIN - 1e-9 <= u <= U_MAX + 1e-9 for u in us), "执行器限幅被突破"
    n_sat = sum(1 for u in us if abs(u) >= U_MAX - 1e-9)
    print(f"\n[4] 执行器全程限幅在 [{U_MIN:.0f},{U_MAX:.0f}]N 内(启动前 {n_sat} 拍饱和)")
    print("    首拍需求 20N 被削顶至 10N,clamping 抗饱和使积分不'记账过度',恢复无拖尾")

    print("\n" + "=" * 64)
    print("[ALL ASSERTS PASSED] 离散 PID:ZOH+微分滤波+抗饱和全流程数值坐实。")
    print("带走一句(00 章):P 给力气,I 记账消差,D 预判刹车——三个字母")
    print("统治工业,不是因为最优,而是因为'不知道模型也能用'。")
    print("=" * 64)


if __name__ == "__main__":
    main()
