"""随机微分方程：布朗运动与 SDE 数值解
================================
数学概念：布朗运动 / SDE / Euler-Maruyama / 几何布朗运动 / Ornstein-Uhlenbeck / Itô 微积分
应用领域：金融数学 / 扩散模型(Diffusion) / 物理 / 生物 / 化学
核心思想：SDE dx = f(x,t)dt + g(x,t)dW 描述含随机扰动的动力系统。
  Euler-Maruyama：x_{n+1} = x_n + f(x_n,t_n)Δt + g(x_n,t_n)√Δt·Z, Z~N(0,1)
  GBM: dS = μSdt + σSdW（股票价格模型，Black-Scholes 基础）
  OU: dx = -θ(x-μ)dt + σdW（均值回归，Vasicek 利率模型）
  Itô 引理：df = (f_t + f_x μ + ½f_xx σ²)dt + f_x σ dW（随机微积分的链式法则）
运行方式：python "26-随机微分方程_SDE.py"
依赖：numpy, matplotlib"""
import numpy as np, matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

def euler_maruyama(f, g, x0, t0, T, dt, n_paths=1):
    """Euler-Maruyama SDE 求解器。dx = f(x,t)dt + g(x,t)dW"""
    n_steps = int((T - t0) / dt)
    t = np.linspace(t0, T, n_steps + 1)
    sqrt_dt = np.sqrt(dt)
    X = np.zeros((n_paths, n_steps + 1))
    X[:, 0] = x0
    for i in range(n_steps):
        dW = np.random.randn(n_paths) * sqrt_dt
        X[:, i+1] = X[:, i] + f(X[:, i], t[i]) * dt + g(X[:, i], t[i]) * dW
    return t, X

def main():
    np.random.seed(42)
    dt = 0.001; T = 1.0; n_paths = 100

    print("=" * 60); print("实验 1：标准布朗运动 dW = σdW"); print("=" * 60)
    t, W = euler_maruyama(lambda x,t: 0, lambda x,t: 1, 0, 0, T, dt, n_paths)
    print(f"{n_paths} 条布朗运动路径, dt={dt}, T={T}")
    print(f"终端值: 均值={W[:,-1].mean():.4f}（理论0）, 方差={W[:,-1].var():.4f}（理论{T}={T}）")

    print("\n" + "="*60); print("实验 2：几何布朗运动 dS = μSdt + σSdW"); print("="*60)
    mu, sigma = 0.1, 0.3; S0 = 100
    t_s, S = euler_maruyama(lambda x,t: mu*x, lambda x,t: sigma*x, S0, 0, 1.0, 0.001, n_paths)
    # 理论均值 E[S_T] = S0*e^{μT}
    theory_mean = S0 * np.exp(mu * 1.0)
    print(f"GBM: μ={mu}, σ={sigma}, S0={S0}")
    print(f"终端均值: {S[:,-1].mean():.2f} (理论 {theory_mean:.2f})")
    print(f"终端中位数: {np.median(S[:,-1]):.2f} (理论 S0*e^{{(μ-σ²/2)T}}={S0*np.exp((mu-sigma**2/2)*1.0):.2f})")
    print(f"\n[解读] GBM 均值 > 中位数（右偏分布）——'平均收益'被少数极端值拉高。")

    print("\n" + "="*60); print("实验 3：Ornstein-Uhlenbeck 均值回归"); print("="*60)
    theta, mu_ou, sigma_ou = 2.0, 1.5, 0.3
    t_ou, X_ou = euler_maruyama(lambda x,t: theta*(mu_ou-x), lambda x,t: sigma_ou, 0.0, 0, 5, 0.001, n_paths)
    print(f"OU: dx = {theta}(x-{mu_ou})dt + {sigma_ou}dW")
    print(f"长期均值: {X_ou[:,-1].mean():.3f}（理论 μ={mu_ou}）")
    print(f"长期方差: {X_ou[:,-1].var():.4f}（理论 σ²/(2θ)={sigma_ou**2/(2*theta):.4f}）")
    print(f"\n[解读] OU 过程被'拉回'均值 μ——利率/温度/速度的模型。")

    print("\n" + "="*60); print("实验 4：SDE 与扩散模型(Diffusion)的连接"); print("="*60)
    print("扩散模型（DDPM, 2020）：dx = -½β(t)x dt + √β(t) dW")
    print("  前向：加噪（数据→噪声）= OU 变体")
    print("  反向：去噪（噪声→数据）= 学习'反向 SDE'")
    print("  Stable Diffusion / DALL-E 的数学基础 = SDE 反向求解")
    print("\n[解读] 2022-2026 AI 最重要的突破（扩散模型）= SDE 的工程化。")

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 11))
    ax = axes[0,0]
    for i in range(min(20, n_paths)): ax.plot(t, W[i], lw=0.5, alpha=0.5)
    ax.plot(t, W.mean(axis=0), 'r-', lw=2, label='均值')
    ax.fill_between(t, W.mean(axis=0)-W.std(axis=0), W.mean(axis=0)+W.std(axis=0), alpha=0.2, color='red')
    ax.set_title(f'标准布朗运动（{n_paths}条路径）'); ax.legend(); ax.grid(alpha=0.3)
    ax = axes[0,1]
    for i in range(min(20, n_paths)): ax.plot(t_s, S[i], lw=0.5, alpha=0.5)
    ax.axhline(S0, color='green', ls='--', alpha=0.5, label=f'S0={S0}')
    ax.set_title(f'几何布朗运动（μ={mu}, σ={sigma}）'); ax.legend(); ax.grid(alpha=0.3)
    ax = axes[1,0]
    for i in range(min(20, n_paths)): ax.plot(t_ou, X_ou[i], lw=0.5, alpha=0.5)
    ax.axhline(mu_ou, color='red', ls='--', lw=2, label=f'μ={mu_ou}')
    ax.set_title(f'Ornstein-Uhlenbeck（均值回归）'); ax.legend(); ax.grid(alpha=0.3)
    ax = axes[1,1]
    ax.hist(S[:,-1], bins=30, density=True, alpha=0.7, color='steelblue', label='GBM终端值')
    ax.axvline(S[:,-1].mean(), color='red', ls='--', lw=2, label=f'均值={S[:,-1].mean():.1f}')
    ax.axvline(np.median(S[:,-1]), color='green', ls='--', lw=2, label=f'中位数={np.median(S[:,-1]):.1f}')
    ax.set_title('GBM 终端分布（对数正态，右偏）'); ax.legend(fontsize=8); ax.grid(alpha=0.3)
    plt.tight_layout(); plt.savefig("26-SDE_结果.png", dpi=120)
    print(f"\n[结果] 图像已保存: 26-SDE_结果.png")
    print("\n[总结] 1. SDE=确定性+随机性=真实世界的数学模型")
    print("2. Euler-Maruyama=SDE的欧拉法(加√Δt·随机项)")
    print("3. GBM=股票模型, OU=均值回归, DDPM=扩散模型AI")
    print("4. Itô引理=随机微积分的链式法则(多出½σ²f_xx项)")

if __name__ == "__main__": main()
