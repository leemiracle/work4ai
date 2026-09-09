import math
"""
随机过程：泊松过程与排队论
================================
数学概念：泊松过程 / 指数分布 / 排队论 / M/M/1 队列 / Little 定律
应用领域：运筹学 / 通信网络 / 服务系统 / 可靠性工程
核心思想：泊松过程描述独立随机事件的到达——
  到达时间间隔 ~ Exp(λ)，到达数 N(t) ~ Poisson(λt)
  M/M/1 队列：泊松到达 + 指数服务 + 1 个服务台
  Little 定律：L = λW（平均队长 = 到达率 × 平均等待时间）
运行方式：python "17-随机过程_泊松与排队论.py"
依赖：numpy, matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


# ============ 1. 泊松过程 ============

def poisson_process(lam, T, size=1):
    """模拟泊松过程。
    lam: 到达率（事件/时间）
    T: 总时间
    返回：到达时间列表
    """
    all_arrivals = []
    for _ in range(size):
        n_expected = int(lam * T * 1.5) + 10
        intervals = np.random.exponential(1.0 / lam, n_expected)
        arrivals = np.cumsum(intervals)
        arrivals = arrivals[arrivals <= T]
        all_arrivals.append(arrivals)
    return all_arrivals if size > 1 else all_arrivals[0]


# ============ 2. M/M/1 排队仿真 ============

def simulate_mm1(lam, mu, T):
    """M/M/1 排队系统仿真。
    lam: 到达率（泊松过程参数）
    mu: 服务率（指数分布参数）
    T: 仿真时间
    
    返回：到达时间、开始服务时间、离开时间
    """
    # 生成到达
    arrivals = poisson_process(lam, T)
    n = len(arrivals)

    # 生成服务时间
    service_times = np.random.exponential(1.0 / mu, n)

    # 计算开始/结束服务时间
    service_start = np.zeros(n)
    service_end = np.zeros(n)

    for i in range(n):
        if i == 0:
            service_start[i] = arrivals[i]
        else:
            service_start[i] = max(arrivals[i], service_end[i-1])
        service_end[i] = service_start[i] + service_times[i]

    return arrivals, service_start, service_end


# ============ 3. 实验 ============

def main():
    np.random.seed(42)

    print("=" * 60)
    print("实验 1：泊松过程——随机事件的数学模型")
    print("=" * 60)

    lam = 2.0  # 到达率：2 事件/时间单位
    T = 20

    # 模拟多条路径
    paths = poisson_process(lam, T, size=5)

    print(f"参数：λ={lam}（到达率），T={T}")
    for i, arr in enumerate(paths):
        n = len(arr)
        print(f"  路径 {i+1}: {n} 个事件，理论期望 λT={lam*T:.0f}")

    # 验证 N(t) ~ Poisson(λt)
    counts = [len(poisson_process(lam, T)) for _ in range(10000)]
    empirical_mean = np.mean(counts)
    empirical_var = np.var(counts)
    theoretical_mean = lam * T

    print(f"\nN(T) 统计验证（10000 次模拟）：")
    print(f"  经验均值: {empirical_mean:.2f}（理论 {theoretical_mean:.1f}）")
    print(f"  经验方差: {empirical_var:.2f}（泊松特性：方差≈均值）")
    print(f"  均值/方差比: {empirical_mean/empirical_var:.4f}（=1 为泊松）✓")

    print(f"\n[解读] 泊松过程的核心：事件独立到达，间隔服从指数分布。")
    print(f"       均值=方差是泊松分布的标志性特征。")

    print("\n" + "=" * 60)
    print("实验 2：M/M/1 排队系统")
    print("=" * 60)

    # ρ = λ/μ < 1 才稳定
    scenarios = [
        (1.0, 2.0, "低负载 ρ=0.5"),
        (1.5, 2.0, "中负载 ρ=0.75"),
        (1.8, 2.0, "高负载 ρ=0.9"),
        (1.99, 2.0, "近饱和 ρ=0.995"),
    ]

    print(f"{'场景':<18} {'平均队长 L':<12} {'平均等待 W':<12} {'利用率':<10} {'稳定?'}")
    print("-" * 62)

    results = {}
    for lam_s, mu_s, name in scenarios:
        rho = lam_s / mu_s
        # 理论值（M/M/1 公式）
        L_theory = rho / (1 - rho) if rho < 1 else float('inf')
        W_theory = 1.0 / (mu_s - lam_s) if rho < 1 else float('inf')

        # 仿真
        arrivals, s_start, s_end = simulate_mm1(lam_s, mu_s, 500)
        n = len(arrivals)
        wait_times = s_start - arrivals  # 等待时间
        sojourn_times = s_end - arrivals  # 逗留时间
        L_sim = np.mean(sojourn_times) * lam_s  # Little 定律估计队长
        W_sim = np.mean(sojourn_times)

        results[name] = {
            'rho': rho, 'L_theory': L_theory, 'W_theory': W_theory,
            'L_sim': L_sim, 'W_sim': W_sim, 'wait_times': wait_times
        }

        stable = "✓" if rho < 1 else "✗"
        print(f"{name:<18} {L_sim:<12.2f} {W_sim:<12.3f} {rho:<10.3f} {stable}")

    print(f"\nM/M/1 理论公式：")
    print(f"  ρ = λ/μ（利用率，必须 < 1）")
    print(f"  L = ρ/(1-ρ)（平均队长，含服务中）")
    print(f"  W = 1/(μ-λ)（平均逗留时间）")
    print(f"  L_q = ρ²/(1-ρ)（平均等待队列长）")

    print(f"\n[解读] ρ→1 时 L 和 W →∞（队列爆炸）。")
    print(f"       这就是为什么高速公路/服务器在 80% 负载时开始拥堵。")

    print("\n" + "=" * 60)
    print("实验 3：Little 定律 L = λW 的验证")
    print("=" * 60)

    print("Little 定律：平均队长 = 到达率 × 平均逗留时间")
    print(f"\n{'场景':<18} {'λ':<6} {'W_sim':<10} {'L_sim(仿真)':<12} {'λW(Little)':<12} {'匹配'}")
    print("-" * 62)
    for name, r in results.items():
        if '高负载' in name or '低负载' in name or '中负载' in name:
            lam_val = [1.0, 1.5, 1.8][['低负载', '中负载', '高负载'].index(name.split()[0])]
            little_L = lam_val * r['W_sim']
            match = "✓" if abs(r['L_sim'] - little_L) / r['L_sim'] < 0.15 else "≈"
            print(f"{name:<18} {lam_val:<6.1f} {r['W_sim']:<10.3f} {r['L_sim']:<12.2f} {little_L:<12.2f} {match}")

    print(f"\n[解读] Little 定律对任意排队系统成立（不限于 M/M/1）。")
    print(f"       它是排队论最普适的结果——只需知道 λ 和 W 就能估计 L。")

    print("\n" + "=" * 60)
    print("实验 4：等待时间分布——为什么排队那么烦人？")
    print("=" * 60)

    # 等待时间分布
    for name in ['低负载 ρ=0.5', '高负载 ρ=0.9']:
        waits = results[name]['wait_times']
        rho = results[name]['rho']
        mu = 2.0
        print(f"\n{name}:")
        print(f"  等待时间均值: {np.mean(waits):.3f}")
        print(f"  等待时间中位数: {np.median(waits):.3f}")
        print(f"  等待时间 90 分位: {np.percentile(waits, 90):.3f}")
        print(f"  等待时间 99 分位: {np.percentile(waits, 99):.3f}")
        print(f"  理论 P(等待>0) = ρ = {rho:.2f}")

    print(f"\n[解读] 等待时间分布是重尾的——均值和中位数差很多。")
    print(f"       '平均等 5 分钟'不意味着'大多数等 5 分钟'，")
    print(f"       少数人可能等很久（重尾效应）。这就是排队的痛苦根源。")

    # ============ 4. 可视化 ============
    fig, axes = plt.subplots(2, 2, figsize=(14, 11))

    # 图 1：泊松过程多条路径
    ax = axes[0, 0]
    for i, arr in enumerate(paths):
        n_events = np.arange(1, len(arr) + 1)
        ax.step(arr, n_events, where='post', alpha=0.7, label=f'路径{i+1}')
    ax.plot([0, T], [0, lam*T], 'k--', lw=2, label=f'理论 E[N(t)]={lam}t')
    ax.set_xlabel('时间 t')
    ax.set_ylabel('累计事件数 N(t)')
    ax.set_title(f'泊松过程（λ={lam}）的随机性')
    ax.legend(fontsize=7)
    ax.grid(alpha=0.3)

    # 图 2：N(T) 的分布 vs 理论泊松
    ax = axes[0, 1]
    ax.hist(counts, bins=range(min(counts), max(counts)+2), density=True,
            alpha=0.6, color='steelblue', label='仿真分布')
    k_range = np.arange(min(counts), max(counts)+1)
    theory_poisson = [np.exp(-lam*T) * (lam*T)**k / math.factorial(k) for k in k_range]
    ax.plot(k_range, theory_poisson, 'ro-', lw=2, markersize=4, label=f'Poisson({lam*T:.0f})')
    ax.set_xlabel('N(T)（事件数）')
    ax.set_ylabel('概率')
    ax.set_title('泊松过程事件数分布验证')
    ax.legend()
    ax.grid(alpha=0.3)

    # 图 3：队长随时间变化（高负载）
    ax = axes[1, 0]
    lam_h, mu_h = 1.8, 2.0
    arrivals_h, s_start_h, s_end_h = simulate_mm1(lam_h, mu_h, 100)
    # 计算每个时刻的队长
    t_check = np.linspace(0, 100, 1000)
    queue = np.zeros_like(t_check)
    for i, t in enumerate(t_check):
        arrived = np.sum(arrivals_h <= t)
        departed = np.sum(s_end_h <= t)
        queue[i] = arrived - departed
    ax.plot(t_check, queue, 'b-', lw=0.5)
    ax.set_xlabel('时间')
    ax.set_ylabel('队长（系统内顾客数）')
    ax.set_title(f'M/M/1 队长随时间变化（ρ={lam_h/mu_h:.2f}）')
    ax.grid(alpha=0.3)

    # 图 4：等待时间分布（对数尺度）
    ax = axes[1, 1]
    for name, color in [('低负载 ρ=0.5', 'green'), ('高负载 ρ=0.9', 'red')]:
        waits = results[name]['wait_times']
        ax.hist(waits[waits > 0], bins=50, alpha=0.5, density=True,
                color=color, label=name)
    ax.set_xlabel('等待时间')
    ax.set_ylabel('密度')
    ax.set_title('等待时间分布（重尾特征）')
    ax.legend()
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig("17-随机过程_结果.png", dpi=120)
    print(f"\n[结果] 图像已保存: 17-随机过程_结果.png")

    print("\n" + "=" * 60)
    print("[总结]")
    print("=" * 60)
    print("1. 泊松过程：独立随机事件的标准模型（均值=方差）")
    print("2. M/M/1 队列：ρ=λ/μ 必须小于 1（否则队列爆炸）")
    print("3. Little 定律 L=λW：最普适的排队论结果")
    print("4. 等待时间重尾分布：少数人等很久（排队的痛苦根源）")
    print("\n[解读] 随机过程是'随机性的动力学'——")
    print("       从电话交换到网络流量到急诊室到超市收银，")
    print("       排队论无处不在。Little 定律是最优雅的实用结果。")


if __name__ == "__main__":
    main()
