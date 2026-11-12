# -*- coding: utf-8 -*-
"""
entropy_feedback.py —— 讲透信息科学基础 家族实验（对应 00 章✨美1 / 03 章✨美3 / 04 章走廊一二）

两段三论公理层的最小可跑现场：
  A. 信息论：香农熵十行实现 + 英文文本实测熵（语言冗余性的熵级证据）
  B. 控制论：一阶房间调温模型，P vs PI 反馈镇定对照（稳态误差的生灭）

运行：python entropy_feedback.py   （纯标准库，无第三方依赖）
"""
from collections import Counter
from math import log2

# ───────────────────────── A. 信息论段 ─────────────────────────
TEXT = ("the quick brown fox jumps over the lazy dog "
        "the theory of communication establishes that "
        "the entropy of a source determines the limits "
        "of lossless compression and reliable transmission "
        "feedback control stabilizes a system by acting on error") * 3

def entropy_bits(freqs, total):
    """香农熵 H = -Σ p log2 p（1948 三公理唯一确定的那个函数）"""
    return -sum((c / total) * log2(c / total) for c in freqs)

H_text = entropy_bits(Counter(TEXT).values(), len(TEXT))
H_uniform = log2(26)  # 26 个字母均匀分布的理论上界
assert 3.5 < H_text < 4.5, f"实测熵 {H_text:.3f} bit/字母 应显著小于上界且>3.5"
assert H_text < H_uniform - 0.3, "语言冗余性：实测熵应显著低于均匀上界 log2(26)≈4.700"
print(f"[A] 香农熵：实测 {H_text:.3f} bit/字母 | 均匀上界 {H_uniform:.3f}")
print(f"    冗余度 ≈ {1 - H_text / H_uniform:.1%} —— 语言远非随机，压缩有饭吃")

# 均匀分布最大化检验（美之时刻1：什么都不偏袒时不确定性最大）
import random
H_unif_check = entropy_bits([1] * 26, 26)
assert abs(H_unif_check - log2(26)) < 1e-12
# 任何非均匀分布熵严格更小（抽样验证）
rng = random.Random(42)
for _ in range(100):
    w = [rng.random() + 0.01 for _ in range(26)]
    assert entropy_bits(w, sum(w)) < log2(26) - 1e-6
print(f"[A] 极值美验证：均匀分布取最大熵，100 次随机分布全部严格更小 ✓")

# ───────────────────────── B. 控制论段 ─────────────────────────
# 房间一阶惯性模型：dT/dt = -(T - T_amb)/tau + q*P/tau
# 目标设定点 T_set=25°C；纯 P 控制器 P=u0+Kp*(T_set-T)；PI 再加积分项
def simulate(controller="P", Kp=2.0, Ki=0.8, T0=15.0, T_set=25.0,
             T_amb=10.0, tau=5.0, q=2.0, dt=0.05, steps=3000, disturbance_at=1500):
    T, integ, hist = T0, 0.0, []
    u0 = (T_set - T_amb) / q  # 开环基础功率（若 T 恰为设定点所需）
    for k in range(steps):
        if k == disturbance_at:
            T_amb -= 5.0  # 寒潮扰动：环境温度骤降
        e = T_set - T
        integ += e * dt
        u = u0 + Kp * e + (Ki * integ if controller == "PI" else 0.0)
        dT = (-(T - T_amb) + q * u) / tau
        T += dT * dt
        if k > steps - 501:  # 取末段（扰动后重稳态）
            hist.append(T)
    return sum(hist) / len(hist)

T_set = 25.0  # 与 simulate 默认设定点一致（模块作用域供断言使用）
T_P = simulate("P")
T_PI = simulate("PI")
print(f"\n[B] 寒潮扰动后稳态：P 控制器 {T_P:.2f}°C | PI 控制器 {T_PI:.2f}°C | 设定点 25.00°C")
# 纯 P 有不可消除的稳态误差（扰动后需残余误差维持功率）；PI 积分项把它磨平
assert T_set - T_P > 0.4, "P 控制器应保留显著稳态误差（这是结构必然，不是调参问题）"
assert abs(T_set - T_PI) < 0.05, "PI 积分项应消除稳态误差（积分=记忆=零残差）"
print("[B] 反馈镇定美：误差驱动功率（P 有残差），积分记忆把残差磨到零（PI 无差）✓")

print("\n[ALL ASSERTS PASSED] 三论公理层两支柱（信息论可算 / 控制论可综合）各一段现场。")
print("带走一句（00 章）：不看实体看组织——信息是不确定性的组织，目的是环，整体是关系网。")
