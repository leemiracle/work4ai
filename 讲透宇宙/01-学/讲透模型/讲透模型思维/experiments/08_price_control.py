"""08_price_control — 价格上限：短缺是线性的，无谓损失是平方的

问题：一个最简单的市场模型——线性供给 Qs = a + b*P 与线性需求 Qd = c - d*P。
  1. 解均衡 (P*, Q*)：两条曲线的交点，"价格会自己停在哪"的计算器。
  2. 政府设价格上限 Pc < P*（压价 10%/20%/30%/40% 档位扫描）：
     短缺 = Qd(Pc) - Qs(Pc) 是多少？无谓损失（DWL 三角形）占均衡总剩余多少？
  3. 剩余再分配：限价把生产者剩余搬给消费者多少？（注意配给假设）

本脚本全部闭式计算（曲线是线性的，没有随机性，不需要种子——每行数字都可手验）。

参数：a=0, b=2（供给：P=0 时没人供货，价格每涨 1 元多供 2 吨）
      c=120, d=3（需求：P=40 时没人买，价格每涨 1 元少买 3 吨）
单位：P = 元/kg，Q = 吨/日。
"""
import numpy as np

a, b = 0.0, 2.0    # 供给 Qs = a + b*P
c, d = 120.0, 3.0  # 需求 Qd = c - d*P

P_star = (c - a) / (b + d)          # 均衡价格 = 24
Q_star = a + b * P_star             # 均衡数量 = 48
P_max = c / d                       # 需求掐断价（ choke price ）= 40
P_min = -a / b                      # 供给启动价 = 0
CS0 = 0.5 * (P_max - P_star) * Q_star   # 均衡消费者剩余
PS0 = 0.5 * (P_star - P_min) * Q_star   # 均衡生产者剩余
TS0 = CS0 + PS0

print(f"供给 Qs = {a:.0f} + {b:.0f}P    需求 Qd = {c:.0f} - {d:.0f}P")
print(f"均衡：P* = {P_star:.1f} 元/kg，Q* = {Q_star:.1f} 吨/日   "
      f"（消费者剩余 {CS0:.1f} + 生产者剩余 {PS0:.1f} = 总剩余 {TS0:.1f}）")
print()

print(f"{'上限档位':>8} {'Pc':>6} {'短缺量':>7} {'短缺/Q*':>8} {'DWL':>7} {'DWL/TS':>8} "
      f"{'CS变化':>8} {'PS变化':>8}")
for cut in (0.10, 0.20, 0.30, 0.40):
    Pc = (1 - cut) * P_star
    Qd_Pc, Qs_Pc = c - d * Pc, a + b * Pc
    shortage = Qd_Pc - Qs_Pc                 # 短缺 = (b+d)(P*-Pc)，对压价幅度线性
    Qt = min(Qd_Pc, Qs_Pc)                   # 限价下成交的是短边（供给）
    P_dem = (c - Qt) / d                     # 成交量上的需求方边际价值
    dwl = 0.5 * (P_dem - Pc) * (Q_star - Qt) # DWL 三角形，对压价幅度平方
    # 限价下的剩余（教科书假设：货恰好分给评价最高的买家）
    area_dem = 0.5 * (P_max + P_dem) * Qt    # 需求曲线下面积 0..Qt
    CS1 = area_dem - Pc * Qt
    PS1 = Pc * Qt - 0.5 * (Pc + P_min) * Qt  # 供给曲线上面积
    print(f"{cut*100:7.0f}% {Pc:6.1f} {shortage:7.1f} {shortage/Q_star:8.1%} "
          f"{dwl:7.1f} {dwl/TS0:8.1%} {CS1/CS0-1:+8.1%} {PS1/PS0-1:+8.1%}")

print()
print("结论性数字（20% 档）：")
Pc = 0.8 * P_star
shortage = (b + d) * (P_star - Pc)
Qt = a + b * Pc
P_dem = (c - Qt) / d
CS1 = 0.5 * (P_max + P_dem) * Qt - Pc * Qt
print(f"  上限压低 20% 价格 -> 短缺 = 均衡量的 {shortage/Q_star:.0%}"
      f"（需求 {c-d*Pc:.1f} 吨 vs 供给 {a+b*Pc:.1f} 吨）")
print(f"  DWL 档位扫描 1% -> 4% -> 9% -> 16%：价格每多压 10%，无谓损失按平方律涨")
print(f"  （短缺是两条曲线一起动：(b+d)*ΔP 线性；DWL 三角形两条边都正比 ΔP -> 平方）")
print(f"  注意：CS {CS1/CS0-1:+.0%} 的'改善'依赖'货分给评价最高者'的假设——现实中排队先到先得，")
print(f"  排队烧掉的时间成本不在模型里，消费者真实得益比上表更小（见 §4）。")
