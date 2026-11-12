# -*- coding: utf-8 -*-
"""
Brooks 定律数值显形(对应 00/02/03/04 章)
==================================================
1) 沟通链路数 C(n,2)=n(n-1)/2 的二次增长(元语言的量化)
2) ramp-up + 沟通税仿真:向已延期项目加人,工期反而更长——
   "人月神话"(Brooks 1975)的最小可执行版。

跑法:python experiments/brooks_communication.py
"""
from math import comb

MU = 0.02      # 沟通税系数(人日/链路/日)
P = 1.0        # 人均满速生产率(人日/日)
RAMP_DAYS = 20 # 新人爬坡期(天)
TRAINEE_NET = -0.3  # 爬坡期新人净贡献(负=学习的净成本)
MENTOR_LOSS = 0.4   # 爬坡期每个老手的生产率折扣比例

# ── 1. 沟通链路二次增长 ──
print("── 沟通链路数 C(n,2) ──")
for n in (3, 5, 10, 20, 50):
    print(f"  n={n:2d} 人 → {comb(n,2):4d} 条沟通链路(人均 {2*comb(n,2)/n:.1f} 条)")
assert comb(10, 2) == 45 and comb(5, 2) == 10, "链路公式验证"
print("  断言:C(5,2)=10, C(10,2)=45 ✓(线性加人,二次加税)\n")

def duration(remaining, n_now, hire=None):
    """仿真工期(天)。hire=(m, day) 在第 day 天加 m 个新人。"""
    day = 0
    while remaining > 1e-9:
        day += 1
        n = n_now + (hire[0] if hire and day >= hire[1] else 0)
        rate = n * P - MU * comb(n, 2)
        if hire and day >= hire[1] and day < hire[1] + RAMP_DAYS:
            m_new = hire[0]
            n_old = n - m_new
            rate = (n_old * P * (1 - MENTOR_LOSS) + m_new * TRAINEE_NET
                    - MU * comb(n, 2))          # 老手教学分心+新人负产出+全量沟通税
        assert rate > 0, "参数设置导致净速率为负,工期发散"
        remaining -= rate
    return day

# ── 2. Brooks 场景:项目已延期,剩余 60 人日 ──
W, N0 = 60.0, 5
t_no  = duration(W, N0, hire=None)          # 不加人
t_yes = duration(W, N0, hire=(5, 1))        # 第 1 天加 5 人

print("── Brooks 仿真:剩余 60 人日的延期项目,现有人数 5 ──")
print(f"  不加人:净速率 {N0*P - MU*comb(N0,2):.1f}/日 → 工期 {t_no} 天")
print(f"  加 5 人:前 {RAMP_DAYS} 天新人净贡献 {TRAINEE_NET}/人·日,老手效率×{1-MENTOR_LOSS:.1f},"
      f"之后满速 {10*P - MU*comb(10,2):.1f}/日 → 工期 {t_yes} 天")
print(f"  → 加人多花 {t_yes - t_no} 天({(t_yes/t_no - 1)*100:.0f}% 延长)——Brooks 定律显形\n")

assert t_yes > t_no, "加人必须更慢(Brooks 定律断言)"
assert t_no == 13, "手算校准:12.5 天向上取整"
print("结论:沟通税 O(n²) + ramp-up 负贡献,使'人月'不可互换——")
print("  流程优化能改常数,改不了复杂度量级;砍范围或拆接口(降 μ)才是量级解。")
print("[ALL ASSERTS PASSED] 链路公式+Brooks 工期断言全部通过。")
