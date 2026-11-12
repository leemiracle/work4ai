# -*- coding: utf-8 -*-
"""技术辅助的双通道受控模拟:即时表现/长期保持的分离与混合解药(00/01/04 章配套实验)。

主题呼应 01 章主线 B(检索校准 2026-09-07:Edutopia 2024 收录研究——AI 提升
测试分数却削弱长期学习与记忆保持,"How AI Vaporizes Long-Term Learning"):
把学习拆成**双通道**——

  - 即时表现通道(工具熟练度 P):有辅助时能完成任务的程度。
    独立练习与 AI 示范都能增长它(看 AI 高效演示同样长工具熟练度);
  - 独立保持通道(记忆强度 S):无辅助还能提取的程度。
    只有独立检索/生成练习能加固它(检索练习效应);纯观摩(认知卸载)
    几乎不加固——"会跟着做"与"离了辅助还会"是两个状态变量。

三组设计(同为 N 个学习回合,固定预算):
  无辅助组:全部回合独立检索;成功→S×G_IND,失败(无反馈)→S×RHO;
  辅助组  :全部回合 AI 代做/直接看解答;即时表现通道加速(GP_AS>GP_IND),
            独立通道几乎不增长(S×G_OFF,G_OFF≈1:认知卸载);
  混合组  :每回合"先自己试,再看 AI 提示"(强制独立练习+反馈):
            成功→S×G_IND;失败但随后看到正确解答(反馈编码)→S×G_FB。
            反馈编码优于盲目失败(G_FB>RHO)——"检索+反馈"的通说组合。

测验设计:
  即时测验(当天,允许使用训练时可用的工具):无辅助组=P(S_perf);
            辅助/混合组=1-(1-P(S_perf))·(1-λ),λ=AI 即时增益上限;
  延迟独立测验(DELAY 天后,所有人无辅助):保持率 R=exp(-DELAY/S_ind)
            (艾宾浩斯式衰减,与教学论家族实验同一曲线族)。

断言三律:
  A. 辅助增益:辅助组即时测验表现显著高于无辅助组(差≥0.15);
  B. 认知卸载的代价:辅助组延迟独立保持崩塌式低于无辅助组
     (保持率比≥100 倍)——即时表现的繁荣与长期保持的蒸发同源;
  C. 混合解药:混合组兼得两端——即时表现不显著低于纯辅助组(差≤0.08)
     且显著高于无辅助组(差≥0.10);延迟保持不低于无辅助组的 90%
     (机制上:失败回合获得反馈编码,逐回合支配无辅助组——见下)。

⚠ 学科纪律(02/04 章):
  1. 参数为通说量级的风格化取值,不是任何真实实验的拟合;
  2. 模拟证明的是「双通道+认知卸载的简单机制足以生成三律」(机制充分性),
     不是对真实课堂的预测;素材研究的效应方向为本实验的靶,量级不可比;
  3. 通说依据:检索练习效应、反馈效应(教学论家族 00 章;哈蒂榜单反馈居前)、
     认知卸载(cognitive offloading,记忆研究的通说构念)、
     "训练期表现≠学习"(比约克;流畅错觉的姊妹命题)——均为综述级通说;
  4. 方差缩减:无辅助组与混合组用**同随机数配对**(每名学习者共用同一
     uniform 序列)——因失败回路的 G_FB>RHO,混合组逐回合支配无辅助组,
     断言 C 的保持端由此有结构保证(不是抽样运气);
  5. 敏感性分析:文末 Monte Carlo(200 次参数抖动)报告三律通过率;
     工具熟练度三增益共用同一抖动因子(同一机制,不许各自漂移)。

跑法: python experiments/tech_aid_decay.py
"""

import math
import random
import sys

# ----------------------------- 模型参数(基准情形) -----------------------------
N_ROUNDS = 16      # 每组学习回合数(固定预算,同教学论家族"同 N 次学习动作"纪律)
DELAY = 21.0       # 延迟独立测验距训练结束的天数

# 独立保持通道(S_ind:无辅助还能提取的记忆强度,天)
S0 = 1.0           # 初始强度
G_IND = 1.50       # 独立检索成功的强度乘子(检索练习效应)
RHO = 0.88         # 独立检索失败且无反馈的回退乘子
G_FB = 1.22        # 混合组失败后看提示(反馈编码)的乘子:>RHO(反馈优于盲目失败)
G_OFF = 1.04       # 纯辅助轮的强度乘子(认知卸载:观摩不检索,几乎不加固)
K_RET = 1.6        # 检索成功概率 q(S)=S/(S+K_RET)

# 即时表现通道(S_perf:有工具时完成任务的工具熟练度)
GP_IND = 1.22      # 独立轮的工具熟练度增益
GP_AS = 1.40       # 辅助轮:AI 示范高效流程,熟练度增长更快
GP_MIX = 1.30      # 混合轮:自己试一遍+看提示
K_PERF = 60.0      # 表现概率 P(S)=S/(S+K_PERF)
LAMBDA = 0.88      # 即时测验允许 AI 时的即时增益上限


def q_ret(s):
    """独立检索成功概率(随独立强度上升而饱和)。"""
    return s / (s + K_RET)


def p_perf(sp):
    """即时表现概率(随工具熟练度上升而饱和)。"""
    return sp / (sp + K_PERF)


# ----------------------------- 三组的回合动力学 -----------------------------
def run_control(us):
    """无辅助组:N 轮独立检索。us=每轮的 uniform 随机数(CRN 共享)。"""
    s, sp = S0, S0
    for u in us:
        s = s * (G_IND if u < q_ret(s) else RHO)
        sp *= GP_IND
    return s, sp


def run_assist():
    """辅助组:N 轮 AI 代做(无随机性:卸载回路是确定的乘子)。"""
    s, sp = S0 * G_OFF ** N_ROUNDS, S0 * GP_AS ** N_ROUNDS
    return s, sp


def run_blend(us):
    """混合组:N 轮"先自己试再看提示"。与 run_control 共用 us(CRN 配对)。"""
    s, sp = S0, S0
    for u in us:
        s = s * (G_IND if u < q_ret(s) else G_FB)
        sp *= GP_MIX
    return s, sp


def imm_score(sp, has_ai):
    """即时测验:无辅助组=纯表现概率;AI 可用组=自己会或 AI 兜底。"""
    p = p_perf(sp)
    return 1.0 - (1.0 - p) * (1.0 - LAMBDA) if has_ai else p


def retention(s):
    """延迟独立测验保持率(艾宾浩斯式指数衰减)。"""
    return math.exp(-DELAY / s) if s > 0 else 0.0


# ----------------------------- 断言 A/B/C(基准情形) -----------------------------
def base_case(n_sim=2000, seed=20260907):
    rng = random.Random(seed)
    sums = {"c": [0.0, 0.0], "b": [0.0, 0.0]}     # [即时, 延迟] 的均值累加器
    for _ in range(n_sim):
        us = [rng.random() for _ in range(N_ROUNDS)]
        s_c, sp_c = run_control(us)
        s_b, sp_b = run_blend(us)
        sums["c"][0] += imm_score(sp_c, False)
        sums["c"][1] += retention(s_c)
        sums["b"][0] += imm_score(sp_b, True)
        sums["b"][1] += retention(s_b)
    s_a, sp_a = run_assist()
    return (imm_score(sp_a, True), retention(s_a),
            tuple(x / n_sim for x in sums["c"]),
            tuple(x / n_sim for x in sums["b"]))


def main():
    global S0, G_IND, RHO, G_FB, G_OFF, K_RET       # 供机制边界与 MC 抖动改写
    global GP_IND, GP_AS, GP_MIX, K_PERF, LAMBDA, DELAY
    if hasattr(sys.stdout, "reconfigure"):          # Windows 控制台编码防御
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    random.seed(20260907)

    print("=" * 72)
    print("技术辅助的双通道模拟:即时表现 / 独立保持 的分离与混合解药")
    print("=" * 72)
    print("模型:学习=即时表现(S_perf,有辅助)+独立保持(S_ind,无辅助)双通道;"
          f"同 {N_ROUNDS} 回合;延迟独立测验 {DELAY:.0f} 天后")
    print(f"检索成功 q=S/(S+{K_RET});卸载乘子 G_OFF={G_OFF},反馈乘子 "
          f"G_FB={G_FB}(>失败回退 {RHO});即时 AI 增益上限 λ={LAMBDA}")

    imm_a, r_a, (imm_c, r_c), (imm_b, r_b) = base_case()
    print(f"\n{'组':<6}{'即时测验(可否用AI)':<22}{'21天后独立保持':<16}")
    print(f"无辅助  {imm_c:.3f}(无AI)          {r_c:.4f}")
    print(f"纯辅助  {imm_a:.3f}(AI可用)        {r_a:.2e}")
    print(f"混合组  {imm_b:.3f}(AI可用)        {r_b:.4f}")

    # ---- 断言 A:辅助增益 ----
    print(f"\n[断言A 辅助增益] 纯辅助组即时表现 {imm_a:.3f} vs 无辅助组 {imm_c:.3f}")
    assert imm_a - imm_c >= 0.15, f"辅助增益失败:差 {imm_a-imm_c:.2f} < 0.15"
    print(f"  ✓ AI 辅助显著提高即时测验表现(+{imm_a-imm_c:.2f})"
          " —— 「AI 提升测试分数」侧得到复现")

    # ---- 断言 B:认知卸载的代价 ----
    ratio = r_c / r_a if r_a > 0 else float("inf")
    print(f"\n[断言B 认知卸载] 延迟独立保持:纯辅助 {r_a:.2e} vs 无辅助 {r_c:.4f}"
          f"(比 {ratio:.0f} 倍)")
    assert ratio >= 100, f"认知卸载代价失败:保持率比 {ratio:.0f} < 100"
    print("  ✓ 即时表现最繁荣的组,长期保持崩塌式最低——「提分却蒸发长期学习」")
    print("    的机制版:卸载绕过了检索,而只有检索加固独立通道")

    # ---- 断言 C:混合解药 ----
    print(f"\n[断言C 混合解药] 混合组:即时 {imm_b:.3f}(纯辅助 {imm_a:.3f},"
          f"无辅助 {imm_c:.3f});保持 {r_b:.4f}(无辅助 {r_c:.4f})")
    assert imm_a - imm_b <= 0.08, f"混合组即时表现掉队:{imm_a-imm_b:.2f} > 0.08"
    assert imm_b - imm_c >= 0.10, f"混合组即时增益不足:{imm_b-imm_c:.2f} < 0.10"
    assert r_b >= 0.9 * r_c, f"混合组保持未保住:{r_b:.3f} < 0.9*{r_c:.3f}"
    print("  ✓ 先自己试再看提示(强制独立练习+反馈):即时端不掉队、保持端")
    print("    不缩水——失败回合的反馈编码(G_FB>回退)让混合组逐回合支配")
    print("    无辅助组(CRN 配对的结构保证,不是抽样运气)")

    # ---- 机制边界:卸载乘子扫描(解药的成立边界) ----
    print("\n⚙ 机制边界:把卸载乘子 G_OFF 从 1.00 拉到 1.20(辅助轮仍在编码)")
    keep = G_OFF
    row = []
    for g_off in (1.00, 1.04, 1.10, 1.20):
        G_OFF = g_off
        s_a2, _ = run_assist()
        row.append(f"G_OFF={g_off:.2f}:保持 {retention(s_a2):.4g}")
    G_OFF = keep
    print("  " + "; ".join(row))
    print("  —— 卸载不是全有全无:辅助轮若仍含生成/自解成分(部分卸载),")
    print("    独立通道损失连续缩小;断言 B 针对的是重卸载区(G_OFF≈1)")

    # ---- Monte Carlo 敏感性分析 ----
    print("\n" + "=" * 72)
    print("Monte Carlo 敏感性分析:200 次抖动(检索/反馈/卸载/延迟各±10%-20%;")
    print("工具熟练度三增益共用同一抖动因子——同一机制不许各自漂移)")
    n_draws, need = 200, 0.90
    passes = {"A 辅助增益": 0, "B 卸载代价": 0, "C 混合解药": 0}
    g = globals()
    base = {"G_IND": G_IND, "RHO": RHO, "G_FB": G_FB, "G_OFF": G_OFF,
            "K_RET": K_RET, "GP_IND": GP_IND, "GP_AS": GP_AS,
            "GP_MIX": GP_MIX, "K_PERF": K_PERF, "LAMBDA": LAMBDA,
            "DELAY": DELAY}
    for d in range(n_draws):
        jit = lambda a, b: random.uniform(a, b)     # noqa: E731
        # 反馈乘子必须保持 > 失败回退(机制约束,不是自由参数)
        rho = jit(0.84, 0.92)
        g_fb = max(jit(1.15, 1.30), rho + 0.05)
        gp = jit(0.9, 1.1)                          # 共用的熟练度抖动因子
        for k, v in (("G_IND", jit(1.40, 1.60)), ("RHO", rho), ("G_FB", g_fb),
                     ("G_OFF", jit(1.00, 1.06)), ("K_RET", jit(1.2, 2.2)),
                     ("K_PERF", jit(50.0, 80.0)), ("LAMBDA", jit(0.85, 0.92)),
                     ("DELAY", jit(14.0, 30.0)),
                     ("GP_IND", base["GP_IND"] * gp),
                     ("GP_AS", base["GP_AS"] * gp),
                     ("GP_MIX", base["GP_MIX"] * gp)):
            g[k] = v
        imm_a2, r_a2, (imm_c2, r_c2), (imm_b2, r_b2) = base_case(
            n_sim=400, seed=41000 + d)
        ok_a = (imm_a2 - imm_c2) >= 0.12
        ok_b = (r_c2 / r_a2 if r_a2 > 0 else 1e9) >= 50
        ok_c = ((imm_a2 - imm_b2) <= 0.08 and (imm_b2 - imm_c2) >= 0.10
                and r_b2 >= 0.9 * r_c2)
        passes["A 辅助增益"] += ok_a
        passes["B 卸载代价"] += ok_b
        passes["C 混合解药"] += ok_c
    # 恢复基准参数(全局态自洁)
    for k, v in base.items():
        g[k] = v
    for law, cnt in passes.items():
        rate = cnt / n_draws
        print(f"  {law}律通过率 {rate:.0%}")
        assert rate >= need, f"{law}律在参数抖动下不稳定({rate:.0%} < {need:.0%})"

    print("\n⚠ 学科纪律提醒:本模拟证明『双通道+认知卸载的简单机制足以生成")
    print("  三律』,不是真实课堂的预测;增益/回退/延迟均为风格化参数,")
    print("  且固定了回合数预算——现实中混合组每回合更耗时(先尝试再看提示),")
    print("  固定『时间』预算时其优势会缩小。真实证据请回 01 章素材与原始文献。")


if __name__ == "__main__":
    main()
