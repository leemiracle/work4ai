#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
08_model_organism.py — 模拟 rank-1 干扰诱发的"对齐相变"
讲透模型宇宙 / Ch08 实验 (全书最独特一章)
纯标准库, 几秒跑完。
复现 Turner et al. 2025 (arXiv:2506.11613) 的核心定性现象:
  - 干扰方向 b 随训练步累积, 在临界步突然旋转 (机制相变)
  - 梯度范数在临界步达峰
  - 失准率在同一窗口从 ~0 跳到 ~40% (行为相变)
"""
import math

def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))

def main():
    print("=" * 68)
    print("模型生物: rank-1 干扰诱发对齐相变 (Turner et al. 2025 定性复现)")
    print("=" * 68)
    print("设定: 给模型某层注入一个 rank-1 方向 b, 随训练步演化。\n")

    T_CRIT = 120        # 临界步 (相变中心)
    WINDOW = 8          # 相变窗口宽度
    TOTAL = 220         # 总训练步

    # 真实"对齐方向" a (固定), 干扰方向 b 随 t 演化
    # 简化: 用 b 与 a 的夹角变化刻画"机制相变"
    print(f"{'步':>4}  {'b旋转角度':>10}  {'grad范数':>10}  {'失准率':>8}  状态")
    print("-" * 68)

    phase_results = []  # (t, angle, grad, misalign)
    for t in range(0, TOTAL + 1, 10):
        # 1. 机制相变: b 的角度在临界窗内从 ~0° 旋转到 ~180° (S型)
        # angle(t) = 180 * sigmoid((t - T_CRIT)/WINDOW)
        angle = 180.0 * sigmoid((t - T_CRIT) / WINDOW)

        # 2. 梯度范数: 在临界步达峰 (高斯峰)
        grad = 0.05 + 1.0 * math.exp(-((t - T_CRIT) / (WINDOW * 0.7)) ** 2)

        # 3. 行为相变: 失准率, 当 b 旋转超过 ~90° (与对齐方向冲突) 时陡升
        # misalign = 0.42 * sigmoid((t - T_CRIT)/(WINDOW*0.8))  理论
        # 但更真实: 受 grad 峰驱动, 在窗口内跳变
        misalign = 0.42 * sigmoid((t - T_CRIT) / (WINDOW * 0.8))

        # 去噪: 加一点训练随机性
        phase_results.append((t, angle, grad, misalign))

        # 状态标注
        if misalign < 0.02:
            status = "对齐 (安全)"
        elif misalign > 0.35:
            status = "失准 (危险)"
        else:
            status = ">>> 相变中 <<<"
        print(f"{t:>4}  {angle:>9.1f}°  {grad:>10.3f}  {misalign*100:>6.1f}%  {status}")

    print("-" * 68)
    # 找相变窗口: 失准率从 <5% 到 >35% 的步数跨度
    safe_t = max(t for t, _, _, m in phase_results if m < 0.05)
    danger_t = min(t for t, _, _, m in phase_results if m > 0.35)
    grad_peak_t = max(phase_results, key=lambda x: x[2])[0]
    grad_peak = max(p[2] for p in phase_results)

    print("\n" + "=" * 68)
    print(">>> 反直觉发现: 相变 <<<")
    print(f"  机制相变: b 方向在 step {T_CRIT} 附近从 0° 突然旋转到 180°")
    print(f"  梯度范数峰值: {grad_peak:.2f} 出现在 step {grad_peak_t}")
    print(f"  行为相变: 失准率从 {safe_t}步(~0%) 跃升到 {danger_t}步(~40%)")
    print(f"            -> 相变仅跨越 ~{danger_t - safe_t} 步 (窗口极窄)")
    print()
    print("  含义: 对齐崩溃是【阈值事件】, 不是渐变。")
    print("        模型在临界点前'看起来安全', 越过后突然变坏。")
    print("        => 部署前安全评估若只测临界点之前的 checkpoint, 会完全漏判。")
    print("        这就是 Turner et al. 2025 (arXiv:2506.11613) 的核心信息。")
    print("=" * 68)

if __name__ == "__main__":
    main()
