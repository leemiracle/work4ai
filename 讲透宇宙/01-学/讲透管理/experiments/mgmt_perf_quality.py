"""管理学 - 绩效/多准则/质量 补充算法"""
import numpy as np

print("=" * 60)
print("1. 杜邦分析 DuPont (ROE 三因素分解)")
print("=" * 60)
# ROE = 净利率 × 总资产周转率 × 权益乘数
net_margin = 0.08        # 净利率 = 净利/营收
asset_turn = 1.5         # 资产周转率 = 营收/总资产
equity_mult = 2.0        # 权益乘数 = 总资产/股东权益
ROE = net_margin * asset_turn * equity_mult
ROA = net_margin * asset_turn
print(f"  净利率={net_margin}, 资产周转={asset_turn}, 权益乘数={equity_mult}")
print(f"  -> ROA={ROA:.4f}, ROE={ROE:.4f}")
print(f"  -> 权益乘数即财务杠杆: 负债越多 ROE 放大但风险上升")

print("\n" + "=" * 60)
print("2. 经济附加值 EVA")
print("=" * 60)
NOPAT = 150        # 税后净营业利润(万)
WACC = 0.09
capital = 1000     # 投入资本(万)
EVA = NOPAT - WACC * capital
print(f"  NOPAT={NOPAT}, WACC={WACC}, 资本={capital} -> EVA={EVA:.1f} 万")
print(f"  -> EVA>0 才是真正创造价值(覆盖资本成本)")

print("\n" + "=" * 60)
print("3. TOPSIS 多准则决策 (逼近理想解)")
print("=" * 60)
# 4个供应商 × 3准则(价格/质量/交期), 质量交期为效益型, 价格为成本型
# 原始矩阵(行=方案, 列=准则)
X = np.array([
    [250, 8, 20],   # 供应商1
    [200, 7, 25],
    [300, 9, 15],
    [220, 6, 22],
], dtype=float)
weights = np.array([0.3, 0.4, 0.3])
# 1) 向量归一化
norm = X / np.sqrt((X ** 2).sum(axis=0))
# 2) 加权
V = norm * weights
# 3) 理想/负理想 (第0,2列效益型取max, 第1列质量也是效益; 价格列0成本型取min)
benefit = [1, 2]; cost = [0]
A_plus = V.max(axis=0).copy(); A_minus = V.min(axis=0).copy()
A_plus[0] = V[:, 0].min();  A_minus[0] = V[:, 0].max()
# 4) 欧氏距离与贴近度
d_plus = np.sqrt(((V - A_plus) ** 2).sum(axis=1))
d_minus = np.sqrt(((V - A_minus) ** 2).sum(axis=1))
C = d_minus / (d_plus + d_minus)
rank = np.argsort(-C) + 1
print(f"  贴近度 C* = {C.round(4)}")
print(f"  排序(高到低): 供应商 {rank.tolist()}")

print("\n" + "=" * 60)
print("4. 报童模型 Newsvendor (单期易逝品)")
print("=" * 60)
p, c, cv = 20, 10, 4   # 售价, 进货成本, 残值
cu = p - c              # 欠储成本(少卖损失)
co = c - cv             # 过储成本(多进滞销)
CR = cu / (cu + co)     # critical ratio 关键比率
print(f"  cu={cu}(欠储), co={co}(过储) -> 关键比率 CR={CR:.4f}")
print(f"  -> 最优订货量应满足 P(需求<=Q*) = {CR:.3f} (需求分布的 {CR:.0%} 分位)")

print("\n" + "=" * 60)
print("5. 六西格玛: DPMO 与西格玛水平")
print("=" * 60)
defects, units, opp = 50, 10000, 1
DPMO = defects * 1_000_000 / (units * opp)
# 近似西格玛水平(短期能力, 含1.5σ偏移): 用 norm.sf 换算
from scipy.stats import norm
sigma = norm.ppf(1 - DPMO / 1_000_000) + 1.5
print(f"  缺陷={defects}, 单位={units}, 机会={opp} -> DPMO={DPMO:.0f}")
print(f"  -> 近似西格玛水平 ≈ {sigma:.2f}σ (含1.5σ长期偏移)")

print("\n" + "=" * 60)
print("6. 田口质量损失函数")
print("=" * 60)
m, k = 10.0, 500.0   # 目标值, 损失系数
for x in [9.5, 9.9, 10.0, 10.1, 10.5]:
    L = k * (x - m) ** 2
    print(f"  x={x}: 损失 L={L:.2f}")
print(f"  -> 偏离目标即产生二次损失(不只是超公差才算不合格)")

print("\n" + "=" * 60)
print("7. 波特五力加权评分 (行业吸引力)")
print("=" * 60)
forces = {
    "行业内竞争": (4, 0.3),   # (强度1-5, 权重)
    "潜在进入者": (2, 0.2),
    "替代品威胁": (3, 0.15),
    "供应商议价": (3, 0.15),
    "买方议价":   (4, 0.2),
}
score = sum(s * w for s, w in forces.values())
print(f"  加权竞争压力 = {score:.2f} (越高越不利)")
print(f"  -> 用于行业选择与战略定位的量化起点")
