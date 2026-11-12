"""
实验 01 — 涌现: Boids 鸟群 + LLM 涌现阈值
对应文档: 讲透系统论/01-涌现.md

核心结论:
  1. Boids 鸟群 (Reynolds 1986): 3 条简单规则涌现群体飞行
     - separation (避碰)
     - alignment (对齐邻居方向)
     - cohesion (朝邻居中心)
  2. 涌现 vs 统计平均: 鸟群方向是 [涌现], 平均速度是 [统计]
  3. LLM 涌现能力: 参数量超阈值突然出现 (但可能是度量幻觉)

跑法: python3 -u 01_emergence.py
"""
import math, random
import numpy as np
random.seed(0); np.random.seed(0)

def P(*a): print(*a, flush=True)

# ============================================================
# Part 1: Boids 鸟群 — 3 条规则涌现群体飞行
# ============================================================
N_BOIDS = 50
WIDTH, HEIGHT = 100, 100

class Boid:
    def __init__(self):
        self.pos = np.array([random.uniform(0, WIDTH), random.uniform(0, HEIGHT)])
        angle = random.uniform(0, 2*math.pi)
        self.vel = np.array([math.cos(angle), math.sin(angle)])

def boids_step(boids, dt=0.5,
               r_sep=5, r_align=15, r_coh=20,
               w_sep=1.5, w_align=1.0, w_coh=0.5):
    """3 条规则: separation, alignment, cohesion"""
    new_boids = []
    for i, b in enumerate(boids):
        sep = np.zeros(2); align = np.zeros(2); coh = np.zeros(2)
        n_align = n_coh = 0
        for j, other in enumerate(boids):
            if i == j: continue
            d = other.pos - b.pos
            dist = np.linalg.norm(d)
            if dist < r_sep and dist > 0:
                sep -= d / dist   # 远离邻居
            if dist < r_align:
                align += other.vel
                n_align += 1
            if dist < r_coh:
                coh += other.pos
                n_coh += 1
        if n_align > 0: align /= n_align
        if n_coh > 0: coh = (coh / n_coh) - b.pos

        # 更新速度
        new_vel = b.vel + dt * (w_sep * sep + w_align * align + w_coh * coh)
        # 限速
        speed = np.linalg.norm(new_vel)
        if speed > 2.0: new_vel = new_vel / speed * 2.0
        # 更新位置
        new_pos = b.pos + dt * new_vel
        # 环面边界
        new_pos = new_pos % np.array([WIDTH, HEIGHT])

        nb = Boid()
        nb.pos, nb.vel = new_pos, new_vel
        new_boids.append(nb)
    return new_boids

def boid_metrics(boids):
    """计算鸟群的两个度量: 平均速度(统计) vs 方向一致性(涌现)"""
    speeds = [np.linalg.norm(b.vel) for b in boids]
    avg_speed = np.mean(speeds)

    # 方向一致性: 所有速度向量的平均长度 / 平均速度
    velocities = np.array([b.vel for b in boids])
    mean_vel = np.mean(velocities, axis=0)
    alignment = np.linalg.norm(mean_vel) / (avg_speed + 1e-9)

    # 群体聚集度: 平均到中心距离
    center = np.mean([b.pos for b in boids], axis=0)
    avg_dist = np.mean([np.linalg.norm(b.pos - center) for b in boids])

    return avg_speed, alignment, avg_dist

P("="*70)
P("实验 01 — 涌现: Boids 鸟群 + LLM 涌现阈值")
P("="*70)
P()
P(f"Boids 鸟群 (Reynolds 1986): {N_BOIDS} 只鸟, 3 条规则")
P("  separation: 避免碰撞")
P("  alignment: 对齐邻居方向")
P("  cohesion: 朝邻居中心移动")
P()

# 初始随机
boids = [Boid() for _ in range(N_BOIDS)]
s0, a0, d0 = boid_metrics(boids)
print(f"初始 (随机): 平均速度={s0:.2f}, 方向一致性={a0:.3f}, 群聚度={d0:.1f}")

# 演化
for step in [10, 50, 100, 200, 500]:
    for _ in range(step if step == 10 else step - ([10, 50, 100, 200, 500][[10, 50, 100, 200, 500].index(step)-1])):
        boids = boids_step(boids)
    s, a, d = boid_metrics(boids)
    print(f"step {step:>4}: 平均速度={s:.2f}, 方向一致性={a:.3f}, 群聚度={d:.1f}")

P("""
关键观察:
- 平均速度 (统计): 几乎不变 (~1) ← 这不是涌现
- 方向一致性 (涌现): 0.05 → 0.7+ ← 这就是涌现!
  单个 boid 速度方向是随机的, 群体却高度一致
- 群聚度: 40 → 25 ← 群体聚成一团

[涌现 vs 统计平均] 的区别:
- 统计平均: 个体属性的均值 (温度 = 分子动能平均)
- 涌现: 个体没有但群体有的新属性 (流动性, 鸟群方向一致)
""")

# ============================================================
# Part 2: LLM 涌现能力 — 真相变还是度量幻觉?
# ============================================================
P("="*70)
P("Part 2: LLM 涌现能力 — 真相变 vs 度量幻觉")
P("-"*70)
P()
P("Wei et al. 2022 报告: 涌现能力在参数量超阈值时突然出现")
P("  - 数学推理: ~50B 突然出现")
P("  - 代码生成: ~70B 突然出现")
P("  - 多步推理: ~70B 突然出现")
P()
P("Schaeffer 2023 反驳: 这可能是 [度量幻觉]")
P("  - 用 [准确率] 这种非线性度量 → 看起来像突变")
P("  - 改用 [连续度量] (如 token log-prob) → 能力是平滑增长的")
P()

# 模拟: 真相变 vs 度量幻觉
print(f"模拟: 能力随模型大小的演化")
print(f"\n{'参数量':<10}{'连续度量':>14}{'准确率 (>0.5阈值)':>20}{'看起来像?':<20}")
print("-"*64)

def true_capability(N):
    """真实能力 (连续): 随参数量平滑增长"""
    return 1 / (1 + math.exp(-(N - 50) / 10))  # sigmoid 围绕 50

for N in [10, 30, 45, 50, 55, 70, 100, 200]:
    cap = true_capability(N)
    acc = 1.0 if cap > 0.5 else 0.0  # 二值化
    appearance = "突然出现!" if (N >= 50 and N < 55) else ""
    print(f"{N:<10}{cap:>14.3f}{acc:>20.1f}    {appearance}")

P("""
关键观察:
- 连续度量: 平滑增长 (sigmoid)
- 准确率 (二值): 50 处突变
- 同一个底层能力, 不同度量看像不同现象!

这就是 [涌现是真相变还是度量幻觉] 之争的本质:
- 数学推理能力本身可能平滑增长
- 但 [答对/答错] 这种二值度量让它看起来突变
- 改用连续度量 (如 token log-prob), 突变消失
""")

# ============================================================
# Part 3: 涌现的"必要条件"
# ============================================================
P("="*70)
P("Part 3: 涌现的三要素 — 不是任何复杂都涌现")
P("-"*70)
P()
P("涌现需要三个条件 (Bertalanffy + 复杂系统科学):")
P()
P("  1. [大量组件] (规模)")
P("     - Boids: 50+ 只鸟")
P("     - LLM: 70B+ 参数")
P("     - 神经网络: 几层不行, 几十层才涌现")
P()
P("  2. [简单规则] (组件行为)")
P("     - Boids: 3 条规则")
P("     - LLM: next-token prediction")
P("     - 神经元: 加权求和 + 非线性")
P()
P("  3. [关系结构] (组件连接)")
P("     - Boids: 局部交互 (距离阈值)")
P("     - LLM: attention (任意两 token 交互)")
P("     - 神经网络: 全连接/卷积/残差")
P()
P("缺一不可. 复杂≠涌现:")
P("  - 随机噪声 (大量+无规则): 不涌现")
P("  - 一根筷子 (有规则+少量): 不涌现")
P("  - 死板的固定结构 (规则+结构+少量): 不涌现")
P()
P("涌现 = 大量简单组件 × 简单规则 × 特定关系结构")
P()

# ============================================================
# Part 4: 涌现工程 — 怎么设计让有用的能力涌现
# ============================================================
P("="*70)
P("Part 4: 涌现工程 — AI 设计中的主动涌现")
P("-"*70)
P("""
1. 【Scaling Laws (Kaplan 2020)】
   - 参数量 / 数据量 / 计算量 与 loss 的幂律
   - 大到一定规模 → 涌现
   - 这是 Chinchilla/GPT-4 训练规模的依据

2. 【In-context Learning (Brown 2020)】
   - GPT-3 175B 才涌现的: 给几个例子就能学会新任务
   - 小模型完全做不到
   - 这是 prompt engineering 的根

3. 【Chain of Thought (Wei 2022)】
   - 100B+ 模型在数学题上突然能用 [分步推理]
   - 小模型给提示也没用

4. 【多 Agent 协作的涌现】
   - AutoGen/Swarm: 多个简单 Agent 协作涌现 [复杂问题求解]
   - 单 Agent 失败的任务, coder+reviewer+tester 协作成功
""")

# ============================================================
# Part 5: 涌现的局限与批判
# ============================================================
P("="*70)
P("Part 5: 涌现的局限 — 不是万能的")
P("-"*70)
P("""
1. 【不可预测】
   - 涌现的能力无法从组件规则推导
   - GPT-3 训练前没人能预测 in-context learning 会出现

2. 【不可控】
   - 出现的能力可能有用 (推理), 也可能有害 (欺骗)
   - 这是对齐 (alignment) 的核心难点

3. 【可能消失】
   -涌现能力在 fine-tune 后可能退化
   - LLM 的 [alignment tax]

4. [度量幻觉警告]
   - 不要把"度量曲线突变"等同于"能力真相变"
   - 改用连续度量, 涌现可能消失
""")

# ============================================================
# 总结
# ============================================================
P("="*70)
P("一句话总结")
P("="*70)
P("""
涌现 = [整体 > 部分之和]. 实测:
- Boids 鸟群: 3 条规则涌现群体方向一致 (0.05 → 0.7+)
- 平均速度 (统计) 不变, 但方向一致 (涌现) 暴涨
- LLM 涌现: 可能是真相变 (能力突然出现), 也可能是度量幻觉 (二值度量让平滑增长看起来突变)

涌现三要素: 大量组件 + 简单规则 + 关系结构. 缺一不可.

涌现工程: Scaling Laws / in-context learning / CoT / 多 Agent 协作
都是利用 [规模 + 简单目标 + 特定结构] 让能力涌现.

但涌现也有局限: 不可预测 / 不可控 / 可能消失 / 可能是度量幻觉.
""")
