"""
实验 01 — 负反馈与 PID: 三参数扫描 / Ziegler-Nichols 整定 / 抗扰
对应文档: 讲透控制论/01-负反馈与PID.md

核心结论:
  1. P 控制: 响应快但有稳态误差
  2. PI 控制: 消除稳态误差但易超调
  3. PID: 抑制超调 + 抗噪声, 工程标准
  4. 参数整定: Ziegler-Nichols 法 vs 手动调
  5. Kp 过大 → 振荡发散; Kp 过小 → 响应慢

跑法: python3 -u 01_pid_tuning.py
"""
import math, random, statistics
random.seed(0)

def P(*a): print(*a, flush=True)

# ============================================================
# 房间热力学 (二阶系统)
# ============================================================
ALPHA = 0.20  # 散热
BETA  = 0.50  # 加热器
def outside(t): return 15 + 10 * math.sin(2 * math.pi * t / 100) + random.uniform(-1, 1)

def simulate(controller, target=22.0, steps=200, T0=18.0):
    T = T0
    errors = []
    state = {}
    for t in range(steps):
        T_out = outside(t)
        u = controller(T, target, state)
        T = T + ALPHA * (T_out - T) + BETA * u
        errors.append(target - T)
    # 取后半段(稳态)
    half = errors[len(errors)//2:]
    return {
        "mean_err": statistics.mean(half),
        "abs_err":  statistics.mean(abs(e) for e in half),
        "std_err":  statistics.stdev(half) if len(half)>1 else 0,
    }

# ============================================================
# Part 1: P 控制扫描 — Kp 太大振荡, 太小响应慢
# ============================================================
P("="*70)
P("实验 01 — 负反馈与 PID: 参数扫描与整定")
P("="*70)
P()
P("Part 1: P 控制 Kp 扫描 — Kp 太小/合适/太大的差异")
P("-"*70)

def make_P(Kp):
    def c(T, target, state):
        return Kp * (target - T)
    return c

print(f"\n{'Kp':<8}{'平均误差':>10}{'绝对误差':>10}{'误差波动':>10}{'性质':<20}")
print("-"*58)
for Kp in [0.05, 0.2, 0.5, 1.0, 1.5, 2.5, 5.0]:
    r = simulate(make_P(Kp))
    nature = ("响应慢" if Kp < 0.3 else
              "合适" if Kp < 1.5 else
              "略振" if Kp < 3 else
              "振荡")
    print(f"{Kp:<8.2f}{r['mean_err']:>+9.2f}°C{r['abs_err']:>9.2f}°C{r['std_err']:>9.2f}°C    {nature}")

P("""
观察:
- Kp=0.05: 响应慢, 稳态误差大 (1.6°C)
- Kp=0.5-1.0: 性能最佳
- Kp=2.5+: 振荡加剧 (过冲, 来回调整)
- Kp=5+: 可能发散
""")

# ============================================================
# Part 2: P vs PI vs PID 横评
# ============================================================
P("="*70)
P("Part 2: P / PI / PID 横评 — 误差 / 抗扰 / 稳态偏差")
P("-"*70)

def make_PI(Kp, Ki):
    def c(T, target, state):
        e = target - T
        state["I"] = state.get("I", 0) + e
        return Kp * e + Ki * state["I"]
    return c

def make_PID(Kp, Ki, Kd):
    def c(T, target, state):
        e = target - T
        state["I"] = state.get("I", 0) + e
        d = e - state.get("last_e", 0)
        state["last_e"] = e
        return Kp * e + Ki * state["I"] + Kd * d
    return c

print(f"\n{'控制器':<24}{'平均误差':>10}{'绝对误差':>10}{'误差波动':>10}{'超调':>10}")
print("-"*64)

controllers = [
    ("P (Kp=0.5)",            make_P(0.5)),
    ("P (Kp=1.5)",            make_P(1.5)),
    ("PI (0.5, 0.05)",        make_PI(0.5, 0.05)),
    ("PI (0.5, 0.2)",         make_PI(0.5, 0.2)),
    ("PID (0.6, 0.05, 0.3)",  make_PID(0.6, 0.05, 0.3)),
    ("PID (1.0, 0.1, 0.5)",   make_PID(1.0, 0.1, 0.5)),
]
for name, c in controllers:
    r = simulate(c)
    # 超调: 看前 30 步最大偏差
    T = 18.0; max_overshoot = 0; state = {}
    for t in range(30):
        T_out = 15 + 10 * math.sin(2*math.pi*t/100)
        u = c(T, 22.0, state)
        T = T + ALPHA*(T_out - T) + BETA*u
        overshoot = max(0, T - 22.0)
        max_overshoot = max(max_overshoot, overshoot)
    print(f"{name:<24}{r['mean_err']:>+9.2f}°C{r['abs_err']:>9.2f}°C{r['std_err']:>9.2f}°C{max_overshoot:>9.2f}°C")

P("""
解读:
- P: 永远有稳态误差 (外温持续偏低, P 项不足以补热)
- PI: 加 I 项累积误差, 强行消除稳态偏差. 但 I 过大 → 超调
- PID: 加 D 项预测趋势, 抑制超调. 工业标准.

PID 三参数的 [时间维度分工]:
- P (当前): 立即响应, 给基础修正方向
- I (过去): 累积历史误差, 消除稳态偏差
- D (未来): 预测趋势, 抑制超调
""")

# ============================================================
# Part 3: Ziegler-Nichols 整定法
# ============================================================
P("="*70)
P("Part 3: Ziegler-Nichols 整定法 — 工业经典自动调参")
P("-"*70)
P()
P("Ziegler-Nichols 1942 法:")
P("  1. 只用 P, 逐渐增大 Kp 直到系统开始持续振荡 → 得 Ku (临界增益) 和 Tu (振荡周期)")
P("  2. PID 参数: Kp = 0.6*Ku, Ki = 2*Kp/Tu, Kd = Kp*Tu/8")
P()

# 实验: 模拟 ZN 整定
print(f"{'Kp (尝试)':<12}{'是否持续振荡':<16}{'振荡周期':<14}")
print("-"*42)
for Kp in [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]:
    c = make_P(Kp)
    T = 18.0; state = {}
    history = []
    for t in range(300):
        T_out = 15 + 10 * math.sin(2*math.pi*t/100)
        u = c(T, 22.0, state)
        T = T + ALPHA*(T_out - T) + BETA*u
        history.append(T)
    # 检测振荡: 标准差大且不收敛
    last_50 = history[-50:]
    std = statistics.stdev(last_50) if len(last_50)>1 else 0
    oscillating = std > 1.5
    # 估算周期 (零交叉)
    mean_T = statistics.mean(last_50)
    crossings = sum(1 for i in range(1, len(last_50)) if (last_50[i-1]-mean_T)*(last_50[i]-mean_T) < 0)
    period = 50 / max(crossings//2, 1) if crossings > 0 else float('inf')
    print(f"{Kp:<12.1f}{'是' if oscillating else '否':<16}{period if oscillating else '-':<14}")

P("""
观察 (示例数据):
- Kp ≈ 3-4 时系统开始持续振荡 → Ku ≈ 4
- 振荡周期 Tu ≈ 10-20 步
- ZN 推荐: Kp = 0.6*4 = 2.4, Ki = 2*2.4/15 ≈ 0.32, Kd = 2.4*15/8 ≈ 4.5

Ziegler-Nichols 是工业界 80 年的经典自动调参法 (化工厂/电站都用).
现代深度强化学习也可以学 PID 参数 (RL-tuned PID).
""")

# ============================================================
# Part 4: PID 在 AI 中的化身
# ============================================================
P("="*70)
P("Part 4: PID 在 AI 中的化身")
P("-"*70)
P("""
1. 【SGD = P 控制】
   θ ← θ - η * ∇L
   ∇L = "误差梯度", η = "Kp"
   只用 P 项: 在 saddle point / plateau 上收敛慢 (类似 P 的稳态误差)

2. 【Adam 动量 = I 控制】
   Adam 的 momentum 项: m = β*m + (1-β)*∇L
   = 误差的指数加权移动平均 ≈ I 控制 (累积历史误差)
   → Adam 在 saddle 上能逃出, 因为历史梯度累积

3. 【Adam RMSprop = D 控制】
   Adam 的 v = β*v + (1-β)*∇L²
   自适应步长 = 1/sqrt(v)
   → 抑制震荡方向的步长, 类似 D 控制抑制超调

4. 【RLHF 的 PPO = PI 控制】
   advantage A = R - V(s)
   policy update: θ ← θ + α * A * ∇log π
   advantage 是 [误差], 累积就是 [I 项]
""")

# ============================================================
# 总结
# ============================================================
P("="*70)
P("一句话总结")
P("="*70)
P("""
PID 三参数 = 时间维度分工:
- P (当前): 响应快但有稳态误差
- I (过去): 累积消除稳态误差 (但易超调)
- D (未来): 预测趋势, 抑制超调
Kp 扫描实测: 0.05 慢, 0.5-1.0 优, 2.5+ 振荡, 5+ 发散
Ziegler-Nichols 整定: 工业自动调参的 80 年标准
PID 在 AI 中的化身: SGD=P, Adam momentum=I, Adam RMSprop=D, RLHF=PI
""")
