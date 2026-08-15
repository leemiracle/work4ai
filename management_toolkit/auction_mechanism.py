"""
机制设计与拍卖 (Mechanism Design & Auctions) 仿真
管理意义: 当管理者无法直接知道下属/供应商的真实信息(成本、估值),
         通过设计"博弈规则(机制)"让说真话成为最优 —— 即激励相容 (IC)。

本脚本用蒙特卡洛验证三条核心定理:
  1) 二价(Vickrey)拍卖: 如实报价是弱占优策略 (DSIC)
  2) 一价拍卖的对称纳什均衡报价 b(v) = (N-1)/N * v  (i.i.d. U[0,1])
  3) 收益等价定理 (Myerson 1981): 一价与二价拍卖期望收益相等
运行: python auction_mechanism.py
"""
import numpy as np


def main():
    rng = np.random.default_rng(2024)
    N = 5            # 竞价者数
    M = 300_000      # 试验次数
    v = rng.uniform(0, 1, (M, N))

    print("=" * 60)
    print(f"单物品拍卖  N={N} 竞价者, 估值 ~ U[0,1], {M:,} 次试验")
    print("=" * 60)

    # —— 二价(Vickrey)拍卖: 如实报价 ——
    winner2 = v.argmax(axis=1)
    second = np.sort(v, axis=1)[:, -2]
    rev2 = second.mean()
    util2 = (v[np.arange(M), winner2] - second).mean()

    # —— 一价拍卖: 纳什均衡报价 b(v)=(N-1)/N * v ——
    k = (N - 1) / N
    b = k * v
    winner1 = b.argmax(axis=1)
    price1 = b[np.arange(M), winner1]
    rev1 = price1.mean()

    print(f"\n  [二价 Vickrey]  期望收益 = {rev2:.4f}")
    print(f"  [一价 First-price 均衡] 期望收益 = {rev1:.4f}")
    theo = (N - 1) / (N + 1)
    print(f"  理论值 (N-1)/(N+1)      = {theo:.4f}")
    print(f"  -> 收益等价定理成立: 两者近似相等 (≈{theo:.3f})")

    # —— 验证二价拍卖 DSIC: 抬高报价不会增加期望效用 ——
    print("\n" + "=" * 60)
    print("验证 DSIC: 在二价拍卖中, 抬高/压低报价不优于真实报价")
    print("=" * 60)
    v0 = rng.uniform(0, 1, M)
    others = rng.uniform(0, 1, (M, N - 1))
    omax = others.max(axis=1)

    def util(bid):
        win = bid > omax
        return np.where(win, v0 - omax, 0).mean()

    print(f"  真实报价 b=v0        : 期望效用 = {util(v0):+.4f}")
    print(f"  抬高报价 b=v0+0.20   : 期望效用 = {util(v0 + 0.20):+.4f}  (可能负: 赢了却付得多)")
    print(f"  抬高报价 b=v0+0.50   : 期望效用 = {util(v0 + 0.50):+.4f}")
    print(f"  压低报价 b=v0*0.5    : 期望效用 = {util(v0 * 0.5):+.4f}  (放弃赢的机会)")
    print("  -> 任何偏离 v0 的期望效用 <= 真实报价  =>  DSIC 成立")

    # —— VCG (多物品/单物品推广) 直觉演示: 单物品 VCG == 二价拍卖 ——
    print("\n" + "=" * 60)
    print("VCG 机制: 价格 = 你对他人造成的'社会损失' (外部性)")
    print("=" * 60)
    # 单物品: 赢者支付 = 没有你时第二高(他人最大), 即外部性
    sample = v[0]
    w = sample.argmax()
    pay = np.sort(sample)[-2]
    sw_with = sample.max()
    sw_without = np.sort(sample)[-2]
    print(f"  样本估值 = {np.round(sample,3)}")
    print(f"  赢者={w}, 支付={pay:.3f} (=无该赢者时社会福利 {sw_without:.3f})")
    print(f"  社会福利最大化: 分给估值最高者 ({sw_with:.3f}) ✓")
    print("  -> VCG 扩展到组合拍卖/广告位/频谱, 是平台广告(GSP/VCG)的基石")


if __name__ == "__main__":
    main()
