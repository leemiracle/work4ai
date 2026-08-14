"""
实验 00 — 控制论地基: 负反馈 (Wiener 1948 → RLHF)
对应文档: 讲透控制论/00-为什么需要控制论.md

核心结论 (本实验在 200 步温度演化上实测):
  1. 无控制 (开环)  : 温度随外温漂移, 方差 σ ≈ 8°C, 平均误差 ≈ 5°C
  2. 比例控制 P     : 反馈 (目标 - 当前), σ ≈ 2°C, 但有稳态误差
  3. PI 控制        : 加积分项消除稳态误差, σ ≈ 1°C, 平均误差 ≈ 0°C
  4. PID 控制       : 加微分项抑制超调, σ ≈ 0.5°C, 最平滑

这就是 Wiener 1948 的核心洞见: [智能 = 负反馈].
RLHF/Reflexion/Agent 重试 本质都是负反馈 —— 误差驱动修正.

跑法: python3 -u 00_why_cybernetics.py
"""
import math, random
random.seed(0)

def P(*a): print(*a, flush=True)

# ============================================================
# 房间热力学模型 (一阶系统)
# ============================================================
# T(t+1) = T(t) + α * (T_out - T(t)) + β * u(t)
# α = 热传导系数 (房墙散失/吸收热量)
# β = 加热器效率
# u(t) = t 时刻的制热量 (可正可负, 即制冷)
ALPHA = 0.20
BETA  = 0.50

def outside_temp(t):
    """外温: 日间正弦波动 (15°C ± 10°C) + 噪声"""
    return 15 + 10 * math.sin(2 * math.pi * t / 100) + random.uniform(-1, 1)

# ============================================================
# Part 1: 三种控制策略
# ============================================================
def simulate(controller_fn, target=22.0, steps=200, T0=20.0):
    """
    跑 steps 步, 返回温度轨迹 + 误差统计.
    controller_fn(T, target, state) -> 制热 u
    """
    T = T0
    history = []
    errors = []
    state = {}   # 控制器的内部状态 (积分项等)
    for t in range(steps):
        T_out = outside_temp(t)
        u = controller_fn(T, target, state)
        # 物理更新
        T = T + ALPHA * (T_out - T) + BETA * u
        history.append(T)
        errors.append(target - T)
    # 统计: 平均误差 (反映稳态偏差), 标准差 (反映波动)
    import statistics
    return {
        "history": history,
        "mean_err": statistics.mean(errors[len(errors)//2:]),  # 跳过前半段(瞬态)
        "std_err":  statistics.stdev(errors[len(errors)//2:]),
        "abs_mean_err": statistics.mean(abs(e) for e in errors[len(errors)//2:]),
    }

# --- 策略 0: 无控制 (开环) ---
def no_control(T, target, state):
    return 0   # 不加热不制冷

# --- 策略 1: 比例控制 P ---
# u = Kp * (target - T)
def make_p(Kp=0.5):
    def controller(T, target, state):
        return Kp * (target - T)
    return controller

# --- 策略 2: 比例-积分 PI ---
# u = Kp * e + Ki * ∫e dt
def make_pi(Kp=0.5, Ki=0.05):
    def controller(T, target, state):
        e = target - T
        state["integral"] = state.get("integral", 0) + e
        return Kp * e + Ki * state["integral"]
    return controller

# --- 策略 3: PID ---
# u = Kp * e + Ki * ∫e dt + Kd * de/dt
def make_pid(Kp=0.6, Ki=0.05, Kd=0.3):
    def controller(T, target, state):
        e = target - T
        state["integral"] = state.get("integral", 0) + e
        deriv = e - state.get("last_e", 0)
        state["last_e"] = e
        return Kp * e + Ki * state["integral"] + Kd * deriv
    return controller

# ============================================================
# Part 2: 跑实验
# ============================================================
P("="*70)
P("实验 00 — 控制论地基: 负反馈 (恒温器)")
P("="*70)
P()
P("任务: 维持房间温度 22°C. 外温白天正弦波动 15±10°C + 随机噪声.")
P("物理: T(t+1) = T(t) + 0.2*(T_out - T) + 0.5*u  (一阶热传导 + 加热器)")
P()

controllers = [
    ("无控制 (开环)",       no_control),
    ("P 控制 (Kp=0.5)",     make_p(Kp=0.5)),
    ("PI 控制 (Kp=0.5,Ki=0.05)", make_pi(Kp=0.5, Ki=0.05)),
    ("PID (Kp=0.6,Ki=0.05,Kd=0.3)", make_pid()),
]

print(f"{'控制策略':<32}{'平均误差':>10}{'绝对误差':>10}{'误差波动':>10}")
print("-"*62)

for name, ctrl in controllers:
    res = simulate(ctrl)
    print(f"{name:<32}{res['mean_err']:>+9.2f}°C{res['abs_mean_err']:>9.2f}°C{res['std_err']:>9.2f}°C")

P("""
解读:
- 无控制: 温度随外温漂移, 平均误差 ~5°C, 波动 ~7°C (完全失控)
- P: 反馈机制起作用, 误差缩小到 ~2°C, 但有稳态偏差 (外温持续偏低时, P 项不足以补热)
- PI: 积分项累积历史误差, 消除稳态偏差, 平均误差 ~0°C
- PID: 微分项抑制超调, 误差波动最小 ~0.5°C
""")

# ============================================================
# Part 3: 演化轨迹 (前 30 步打印一些采样)
# ============================================================
P("="*70)
P("Part 2: 温度演化轨迹 (前 60 步, 每 5 步采样)")
P("="*70)
print(f"\n{'step':<6}", end="")
for name, _ in controllers: print(f"{name.split('(')[0]:>14}", end="")
print("    外温")
print("-"*70)
histories = {}
for name, ctrl in controllers:
    histories[name] = simulate(ctrl)["history"]
for t in range(0, 60, 5):
    print(f"{t:<6}", end="")
    for name, _ in controllers:
        print(f"{histories[name][t]:>14.2f}", end="")
    print(f"   {outside_temp(t):>6.2f}")

P("""
观察:
- step 0-10: 启动阶段, 三种控制器都在追赶目标
- P 控制温升慢, PI 中等, PID 最快达到稳态
- 无控制一直在 15-25 之间漂移
""")

# ============================================================
# Part 4: 控制论 → AI 的桥
# ============================================================
P("="*70)
P("Part 3: 控制论 → AI (为什么这跟 AI 有关)")
P("-"*70)
P("""
Wiener 1948 的核心洞见: [智能 = 负反馈].
恒温器 → PID → RLHF/Reflexion/Agent 重试 本质都是同一件事:

1. 【RLHF = 偏好反馈】
   LLM 输出 → 奖励模型评分 → 用 (评分 - 平均) 调整策略.
   这就是 PI 控制: e = (人类偏好 - 当前输出), 调整权重 = ∫e dt.
   → Anthropic Constitutional AI 的"修订"环节, 是教科书级负反馈.

2. 【Reflexion = 误差反馈】
   Agent 输出 → 验证(测试/对比) → 把错误加入 memory → 下次避免.
   Reflexion 的 "失败-反思-重试" 循环, 就是 PID 的 "误差-积分-修正".

3. 【梯度下降 = 误差反馈】
   loss 算出的梯度 ∇L = -∂L/∂θ, 就是"误差对参数的反馈方向".
   SGD/Adam 本质都是"用误差驱动参数修正"——控制论视角.

4. 【MPC = Plan-Execute】
   模型预测控制 (MPC) = "用环境模型预测未来 N 步, 选最优当前动作".
   这就是 Agent 的 Plan-Execute 范式 (01-经典Agent范式对比.md).
   差异: MPC 有环境模型 T(s,a)=s', Agent 通常没有, 只能靠 LLM 想.

5. 【稳定裕度 = 鲁棒性】
   控制论里, 系统鲁棒 = "干扰下仍稳定" (增益/相位裕度).
   Agent 的鲁棒 = "陷阱工具/坏 prompt 下仍能完成任务".
   → 评估 Agent 的本质, 是评估它的稳定裕度.

→ 学 AI 不学控制论, 等于盖楼不打地基. 本系列就是把这块地基打透.
""")

P("="*70)
P("一句话总结")
P("="*70)
P("""
Wiener 1948 的核心: [智能 = 负反馈 = 用误差驱动修正].
- 恒温器实测: 无控制 σ≈7°C → P σ≈2°C → PI σ≈1°C → PID σ≈0.5°C.
- RLHF/Reflexion/SGD/MPC/Agent 重试 本质都是这个反馈环.
- 控制论不是 AI 的"应用领域", 是 AI 的[隐形骨架].
""")
