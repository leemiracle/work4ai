"""
啤酒游戏 (Beer Game) 仿真 —— 经典系统动力学教学模型
展示"牛鞭效应 (Bullwhip Effect)": 终端需求小幅扰动, 订单方差沿供应链逐级放大。

机理(为什么放大):
  1) 需求预测: 每级用局部观测预测, 信号被放大
  2) 批量订货 / 安全库存: 订货量 = 目标库存 - (库存+在途) + 调整项
  3) 延迟 (lead time): 信息与货物延迟造成过度反应与振荡
  4) 短缺博弈 (本简化未含): 上游缺货时下游虚报
参考: Sterman (1989) Management Science "Modeling Managerial Behavior"
运行: python beer_game.py   输出数值 + beer_game.png
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def beer_game(T=60, L=2, S0=12.0, seed=7):
    rng = np.random.default_rng(seed)
    # 终端需求: 前4周=4, 之后阶跃到 8 + 小噪声
    demand = np.where(np.arange(T) < 4, 4.0, 8.0) + rng.normal(0, 0.3, T)
    demand = np.maximum(demand, 0)
    names = ["Retailer", "Wholesaler", "Distributor", "Factory"]
    n = len(names)
    inv = [S0] * n
    backlog = [0.0] * n
    pipe = [[4.0] * L for _ in range(n)]   # 在途货物队列(延迟L周)
    orders = [[] for _ in range(n)]

    for t in range(T):
        d = [0.0] * n
        d[0] = demand[t]
        for i in range(1, n):
            d[i] = orders[i - 1][-1] if orders[i - 1] else 4.0
        for i in range(n):
            # 收货
            inv[i] += pipe[i].pop(0)
            # 满足下游订单 + 欠交
            need = d[i] + backlog[i]
            ship = min(inv[i], need)
            inv[i] -= ship
            backlog[i] = need - ship
            # 锚定-调整订货策略 (Sterman-style)
            forecast = d[i]
            desired_inv = S0 + forecast * L * 0.5            # 安全库存
            in_transit = sum(pipe[i])
            order = max(0.0, desired_inv - inv[i] - in_transit + backlog[i]
                        + 0.5 * forecast)
            orders[i].append(order)
            pipe[i].append(order)                            # 延迟到货(假设上游供得上)
    return demand, orders, names


def variance_amplification(demand, orders):
    """牛鞭效应 = 上游订单方差 / 下游(需求)方差"""
    burn = 4
    ratios = []
    base_var = np.var(demand[burn:])
    prev = base_var
    for o in orders:
        v = np.var(np.array(o[burn:]))
        ratios.append(v / prev if prev > 0 else float("inf"))
        prev = v
    return base_var, ratios


if __name__ == "__main__":
    demand, orders, names = beer_game()
    base_var, ratios = variance_amplification(demand, orders)
    print("=" * 60)
    print("啤酒游戏 — 牛鞭效应 (订单方差逐级放大)")
    print("=" * 60)
    print(f"  终端需求方差 = {base_var:.3f}")
    for name, o, r in zip(names, orders, ratios):
        v = np.var(np.array(o[4:]))
        print(f"  {name:12s}: 订单方差={v:8.3f}   相对下游放大 = {r:5.2f}x")
    print(f"\n  解读: 从零售到工厂, 订单波动被放大 "
          f"{np.prod(ratios):.1f} 倍 — 这就是牛鞭。")
    print("  管理含义: 局部理性 + 延迟 → 系统级低效; 解药 = 信息共享(VMI/CPFR) + 缩短延迟 + 小批量")

    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    for ax, name, o in zip(axes.flat, names, orders):
        ax.plot(o, color="C0", lw=1.6, label=f"{name} orders")
        ax.plot(demand, color="C3", ls="--", lw=1.2, label="end-customer demand")
        ax.set_title(f"{name}  (order amplification)")
        ax.set_xlabel("week"); ax.set_ylabel("units")
        ax.legend(fontsize=8); ax.grid(alpha=0.3)
    fig.suptitle("Beer Game — Bullwhip Effect: a small step in end demand "
                 "becomes huge swings upstream", fontsize=13)
    fig.tight_layout()
    out = "/tmp/opencode/management_toolkit/beer_game.png"
    fig.savefig(out, dpi=110)
    print(f"  [图] 已保存 {out}")
