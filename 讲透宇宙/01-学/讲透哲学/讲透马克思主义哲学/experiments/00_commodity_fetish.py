# -*- coding: utf-8 -*-
"""商品拜物教的最小计算类比:交换价值如何脱离使用价值而涌现(00/04 章配套实验)。

设定(00 章 §八美之时刻 2 & 04 章走廊 2 的可跑版):
  - 4 种商品:粮/布/铁/盐,单位社会必要劳动 COST=[1,2,4,8](盐最费工);
  - 社会分工给定:24 个生产者-消费者固定行当(各 6 人),每期产量 = 劳动预算/成本
    ——费工的商品社会供给天然稀少(生产条件决定稀缺结构);
  - 单位平均使用价值 USE=[3.0,2.6,2.2,1.8]——人人总体上都最爱粮,但四种都是有用物
    (没有无用的商品,这是劳动价值论的显式前提);
  - 初始人人按个人使用价值估价(v_i ← u_i,前市场状态);
  - 每期:生产 → 随机配对:卖方出自己最富余的货,买方按「边际用处/自己信的价值」
    挑对手库存里最划算的货 → 双方各按「使用利益或价值利益」决定是否成交
    → 成交则互相校准信念,卖不掉则降价(失败销售的重新定价);
  - 边际使用价值随持有量衰减(饱和):易生产的商品泛滥 → 边际用处跌 → 不值钱;
    费工的商品稀缺 → 边际用处稳 → 金贵。**稀缺-价值通道由此内生涌现**,
    不外加任何"劳动决定价值"的定价公式。

断言四连(商品拜物教的发生学信号):
  A. 排序共识化:期初个体价值排序五花八门(各有各的用处),期末全体收敛到同一张
     公共价值表——交换价值成为外在于每个个体的社会事实;
  B. 期末价值排序 ≈ 劳动成本(生产条件)排序,而期初 ≈ 使用价值排序——
     交换价值在运行中脱离使用价值、锚定社会生产条件;
  C. 期末价值排序与**每一个**个体的使用偏好排序都不同(≥3/4 个体 Kendall 距离≥4):
     这张表对人人有效,却不出自任何个人——社会关系的物化;
  D. 行为接管:晚期成交中,买方按「价值逻辑」(为换而换)而非「使用逻辑」成交的
     占比过半——价值语言开始自己统治交换行为。

⚠ 拜物教纪律:本脚本演示的是「交换价值作为社会共识的发生机制」,
  价值最终锚定社会劳动条件依赖模型前提(给定分工+饱和效用+失败降价),
  不是模拟的"发现",更不是对真实定价的经验断言——换 USE/COST/KAPPA/NOISE 重跑=敏感性分析。
  它想让你看见的只有一件事:人们带着各自的用处进入市场,
  市场教给他们一套与任何人的用处排序都不同、却对人人有效的价值语言——
  物与物的关系掩盖人与人的关系。

跑法: python experiments/00_commodity_fetish.py
"""
import random
import statistics as st

random.seed(20260907)

GOODS = ["粮", "布", "铁", "盐"]
COST = [1.0, 2.0, 4.0, 8.0]        # 单位商品的社会必要劳动小时(生产条件)
USE = [3.0, 2.6, 2.2, 1.8]         # 单位平均使用价值(人人总体上最爱粮)
N_AGENT, PER_GOOD = 24, 6
T_LABOR = 2.0                       # 每期每 agent 劳动预算 → 产量 = T/COST(费工的产量低)
PERIODS, MEETINGS = 40, 300
KAPPA = 0.55                        # 边际使用价值饱和系数:mu = u/(1+κ·持有量)
ALPHA = 0.15                        # 成交后的信念校准步长
MARGIN = 0.05                       # 价值路线要求的溢价
DELTA = 0.02                        # 失败销售的降价幅度
DECAY = 0.70                        # 每期库存耗损(生活消费)
NOISE = (0.70, 1.45)                # 个体使用价值的噪声区间(异质性来源)
V_SUM = 12.0                        # 信念向量归一化常数(名义价值总量)


class Agent:
    def __init__(self, k):
        self.spec = k % 4            # 社会分工给定,行当不可转
        self.u = [USE[g] * random.uniform(*NOISE) for g in range(4)]
        s = sum(self.u)
        self.v = [x / s * V_SUM for x in self.u]     # 前市场状态:按各自的用处估价
        self.inv = [0.0] * 4
        self.inv[self.spec] = 2.0

    def mu(self, g):
        """饱和边际使用价值:持有越多,多一件的用处越小。"""
        return self.u[g] / (1.0 + KAPPA * self.inv[g])

    def normalize(self):
        s = sum(self.v)
        self.v = [x / s * V_SUM for x in self.v]

    def produce(self):
        self.inv[self.spec] += T_LABOR / COST[self.spec]


def rank(vec):
    """升序名次(1=最小),Spearman 用。"""
    order = sorted(range(len(vec)), key=lambda g: vec[g])
    r = [0] * len(vec)
    for pos, g in enumerate(order):
        r[g] = pos + 1
    return r


def pearson(x, y):
    mx, my = st.mean(x), st.mean(y)
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    den = (sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y)) ** 0.5
    return num / den if den else 0.0


def spearman(x, y):
    return pearson(rank(x), rank(y))


def meet(i, j, log):
    """一次配对议价:i 卖自己最富余的货 a;j 的库存里,i 挑「边际用处/自己信的价值」
    最划算的货 b 作为对手方支付。"""
    a = max(range(4), key=lambda g: i.inv[g])
    if a == j.spec and j.inv[a] >= i.inv[a]:
        pass                                     # 同行当也可能有库存,继续即可
    stock = [g for g in range(4) if g != a and j.inv[g] >= 0.1]
    if i.inv[a] < 1.0 or not stock:
        return
    b = max(stock, key=lambda g: i.mu(g) / max(i.v[g], 1e-6))
    q = 0.5 * (i.v[a] / i.v[b] + j.v[a] / j.v[b])     # 议价=双方信念的中点
    q = min(q, j.inv[b])
    if q < 0.05:
        return
    # 卖方 i:让出 1 单位 a,换回 q 单位 b
    i_use = i.mu(b) * q >= i.mu(a)
    i_val = q * i.v[b] >= i.v[a] * (1.0 + MARGIN)
    # 买方 j:让出 q 单位 b,换回 1 单位 a
    j_use = j.mu(a) >= j.mu(b) * q
    j_val = j.v[a] >= q * j.v[b] * (1.0 + MARGIN)
    if (i_use or i_val) and (j_use or j_val):
        i.inv[a] -= 1.0
        i.inv[b] += q
        j.inv[b] -= q
        j.inv[a] += 1.0
        # 成交即校准:a 值它实际换回的东西;b 的单位价值按成交价折算
        i.v[a] = (1 - ALPHA) * i.v[a] + ALPHA * q * i.v[b]
        j.v[b] = (1 - ALPHA) * j.v[b] + ALPHA * j.v[a] / q
        i.normalize()
        j.normalize()
        log.append((i_use, i_val, j_use, j_val))
    else:
        # 卖不掉就降价:双方都学到"这种东西不好出手"(重新定价通道)
        i.v[a] *= (1.0 - DELTA)
        j.v[a] *= (1.0 - DELTA)
        i.normalize()
        j.normalize()


def dispersion(agents):
    return st.mean(st.stdev([a.v[g] for a in agents]) for g in range(4))


def v_mean(agents):
    return [st.mean([a.v[g] for a in agents]) for g in range(4)]


def modal_rank_share(agents):
    """全体个体价值排序中最流行排序的占比(排序共识度)。"""
    orderings = [tuple(rank(a.v)) for a in agents]
    top = max(set(orderings), key=orderings.count)
    return top, orderings.count(top)


def kendall_distance(r1, r2):
    """4 元素共 6 对,数有多少对次序相反。"""
    n, d = len(r1), 0
    for x in range(n):
        for y in range(x + 1, n):
            if (r1[x] - r1[y]) * (r2[x] - r2[y]) < 0:
                d += 1
    return d


def main():
    agents = [Agent(k) for k in range(N_AGENT)]
    v_init = v_mean(agents)
    rank_init, share_init = modal_rank_share(agents)
    log_early, log_late = [], []
    period_v = []

    for t in range(1, PERIODS + 1):
        for a in agents:
            a.produce()
        for _ in range(MEETINGS):
            i, j = random.sample(range(N_AGENT), 2)
            meet(agents[i], agents[j], log_early if t <= PERIODS // 4 else log_late)
        for a in agents:
            a.inv = [x * DECAY for x in a.inv]
        if t > PERIODS - 8:                     # 末段时间平均,降噪
            period_v.append(v_mean(agents))

    v_fin = [st.mean(col) for col in zip(*period_v)]
    rank_fin, share_fin = modal_rank_share(agents)

    def share(log, idx):
        return sum(1 for r in log if r[idx]) / len(log) if log else 0.0

    print("=" * 68)
    print("商品拜物教的最小计算类比:交换价值脱离使用价值的涌现")
    print("=" * 68)
    print(f"\n商品   劳动成本   平均使用价值   期初交换值   期末交换值")
    for g in range(4):
        print(f"{GOODS[g]:<4}{COST[g]:>8.1f}{USE[g]:>12.1f}"
              f"{v_init[g]:>12.2f}{v_fin[g]:>12.2f}")

    print(f"\n排序共识度(同一张价值表的持有者占比):{share_init}/{N_AGENT} → {share_fin}/{N_AGENT}")
    print(f"  期初最流行的排序:{rank_init}(各有各的用处)")
    print(f"  期末最流行的排序:{rank_fin}(一张公共价值表)")
    val_share_early = share(log_early, 3)   # 买方走价值路线的成交占比
    val_share_late = share(log_late, 3)
    print(f"买方按价值逻辑(而非使用逻辑)成交的占比:{val_share_early:.1%} → {val_share_late:.1%}")
    print(f"(成交笔数:早期 {len(log_early)} 笔 / 晚期 {len(log_late)} 笔)")

    # 断言 A:排序共识化——公共价值表成为社会事实
    assert share_init <= N_AGENT // 3, "期初个体排序应五花八门(各有各的用处)"
    assert share_fin >= N_AGENT - 2, "期末应几乎全员持有同一张价值表(社会事实化)"
    print(f"\n断言 A 通过:流行排序持有者 {share_init}/{N_AGENT} → {share_fin}/{N_AGENT} ✓")

    # 断言 B:交换价值脱离使用价值,锚定社会生产条件
    sp_fin_cost = spearman(v_fin, COST)
    sp_fin_use = spearman(v_fin, USE)
    sp_init_use = spearman(v_init, USE)
    sp_init_cost = spearman(v_init, COST)
    assert sp_init_use > 0.8, "期初应按使用价值锚定(前市场状态)"
    assert sp_fin_cost > 0.8, "期末价值排序应跟随劳动成本(社会生产条件)"
    assert sp_fin_use < -0.5, "期末价值排序应背离使用价值排序"
    print(f"断言 B 通过:排序 Spearman(v,劳动成本) {sp_init_cost:+.1f} → {sp_fin_cost:+.1f};"
          f"Spearman(v,使用价值) {sp_init_use:+.1f} → {sp_fin_use:+.1f} ✓")
    print("          —— 最费工的盐在交换中最贵,人人最爱的粮最便宜:价值语言脱锚用处")

    # 断言 C:这张表不出自任何个人——期末价值排序与每个个体的用处排序都不同
    r_fin = rank(v_fin)
    far = sum(1 for a in agents if kendall_distance(rank(a.u), r_fin) >= 4)
    assert far >= N_AGENT * 3 // 4, "多数个体的使用排序应与社会价值排序显著不同"
    print(f"断言 C 通过:{far}/{N_AGENT} 个个体的使用偏好排序与公共价值表 Kendall 距离≥4"
          "(满距离 6)—— 对人人有效,却不出自任何个人 ✓")

    # 断言 D:行为接管——价值逻辑(为换而换)在晚期成交中过半
    assert val_share_late > 0.5, "晚期价值逻辑应接管多数成交"
    print(f"断言 D 通过:晚期买方按价值逻辑成交 {val_share_late:.0%}"
          f"(早期 {val_share_early:.0%})—— 价值语言开始统治行为 ✓")

    print("\n⚠ 拜物教纪律:价值锚定社会劳动是本模型的前提(给定分工+饱和+降价),")
    print("  不是模拟的发现;换 USE/COST/KAPPA/NOISE 重跑=敏感性分析(04 章 §四)。")

    print("\n一句话:人们带着各自的用处进入市场,市场教给他们一套与任何人的")
    print("  用处排序都不同、却对人人有效的价值语言——物与物的关系掩盖人与人的关系。")


if __name__ == "__main__":
    main()
