"""
统计假设检验：p值、置信区间与功效分析
================================
数学概念：假设检验 / p值 / 置信区间 / t检验 / 卡方检验 / 功效 / 多重检验校正
应用领域：A/B测试 / 临床试验 / 质量控制 / 科学研究 / 因果推断
核心思想：用样本数据对总体假设做"有罪推定"式判决。
  H₀（零假设）：无效应/无差异（默认接受）
  H₁（备择假设）：有效应/有差异（需要证据才能接受）
  p值：在H₀为真时，观测到当前或更极端结果的概率
  p < α（通常0.05）→ 拒绝H₀ → "统计显著"
  功效（1-β）：H₁为真时正确拒绝H₀的概率
运行方式：python "25-统计假设检验.py"
依赖：numpy, matplotlib, scipy
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def main():
    np.random.seed(42)

    print("=" * 60)
    print("实验 1：单样本 t 检验——均值是否等于某值？")
    print("=" * 60)

    # 模拟 A/B 测试数据
    mu_true = 5.2  # 真实均值
    data = np.random.normal(mu_true, 1.0, 50)

    # H₀: μ = 5.0  vs  H₁: μ ≠ 5.0
    mu_0 = 5.0
    t_stat, p_value = stats.ttest_1samp(data, mu_0)
    ci = stats.t.interval(0.95, len(data)-1, loc=np.mean(data), scale=stats.sem(data))

    print(f"数据: 50 样本, 样本均值={np.mean(data):.3f}, 样本标准差={np.std(data):.3f}")
    print(f"H₀: μ = {mu_0}  vs  H₁: μ ≠ {mu_0}")
    print(f"t 统计量 = {t_stat:.4f}")
    print(f"p 值 = {p_value:.6f}")
    print(f"95% 置信区间: [{ci[0]:.3f}, {ci[1]:.3f}]")
    print(f"结论: {'拒绝 H₀（统计显著）' if p_value < 0.05 else '不拒绝 H₀'}")

    print(f"\n[解读] p值 = '假设H₀为真时观测到这么极端数据的概率'")
    print(f"       p < 0.05 → 数据与H₀矛盾 → 拒绝H₀")
    print(f"       但 p值 ≠ 'H₀为真的概率'（常见误解！）")

    print("\n" + "=" * 60)
    print("实验 2：双样本 t 检验——两组是否有差异？")
    print("=" * 60)

    # A/B 测试
    group_A = np.random.normal(10, 2, 100)  # 控制组
    group_B = np.random.normal(10.8, 2, 100)  # 处理组

    t_stat2, p_value2 = stats.ttest_ind(group_A, group_B)
    effect_size = (np.mean(group_B) - np.mean(group_A)) / np.sqrt(
        (np.std(group_A)**2 + np.std(group_B)**2) / 2)

    print(f"A 组: 均值={np.mean(group_A):.3f} (n=100)")
    print(f"B 组: 均值={np.mean(group_B):.3f} (n=100)")
    print(f"差异: {np.mean(group_B)-np.mean(group_A):.3f}")
    print(f"效应量 Cohen's d = {effect_size:.3f}")
    print(f"p 值 = {p_value2:.6f}")
    print(f"结论: {'B 显著优于 A' if p_value2 < 0.05 else '无显著差异'}")

    print(f"\n[解读] 统计显著 ≠ 实际重要。效应量(Cohen's d)衡量'实际大小'。")
    print(f"       d<0.2 小, 0.5 中, 0.8 大。这里 d={effect_size:.2f}。")

    print("\n" + "=" * 60)
    print("实验 3：p值的分布——为什么别只看 p<0.05？")
    print("=" * 60)

    # 模拟 H₀ 为真时多次检验
    n_tests = 10000
    p_values_h0 = []
    for _ in range(n_tests):
        d1 = np.random.normal(0, 1, 30)
        d2 = np.random.normal(0, 1, 30)
        _, p = stats.ttest_ind(d1, d2)
        p_values_h0.append(p)

    p_values_h0 = np.array(p_values_h0)
    false_positives = np.sum(p_values_h0 < 0.05)

    print(f"H₀ 为真时 {n_tests} 次检验的 p 值分布：")
    print(f"  p < 0.05 的比例: {false_positives/n_tests:.3f}（理论 0.05）")
    print(f"  p 值分布: 均匀分布 Uniform[0,1]")

    print(f"\n⚠ 多重检验问题：")
    print(f"  做 20 次独立检验（H₀ 都为真），至少 1 个 p<0.05 的概率:")
    prob_at_least_one = 1 - (1 - 0.05)**20
    print(f"  = 1-(0.95)^20 = {prob_at_least_one:.3f} = {prob_at_least_one*100:.1f}%")
    print(f"  → 必然出现假阳性！需要 Bonferroni 校正。")

    print("\n" + "=" * 60)
    print("实验 4：统计功效——你能检测到多大的效应？")
    print("=" * 60)

    from scipy.stats import norm

    def compute_power(n, effect_size, alpha=0.05):
        """计算双样本 t 检验的功效。"""
        z_alpha = norm.ppf(1 - alpha / 2)
        ncp = effect_size * np.sqrt(n / 2)  # 非中心参数
        power = 1 - norm.cdf(z_alpha - ncp) + norm.cdf(-z_alpha - ncp)
        return power

    print(f"{'样本量 n':<10} {'d=0.2(小)':<12} {'d=0.5(中)':<12} {'d=0.8(大)':<12}")
    print("-" * 46)
    for n in [10, 30, 50, 100, 200, 500]:
        powers = [compute_power(n, d) for d in [0.2, 0.5, 0.8]]
        print(f"{n:<10} {powers[0]:<12.3f} {powers[1]:<12.3f} {powers[2]:<12.3f}")

    print(f"\n[解读] 功效 = 1-β（正确拒绝错误H₀的概率）。")
    print(f"       小效应(d=0.2)需要 n>500 才有 80% 功效。")
    print(f"       '统计不显著'可能只是样本量不够（低功效）！")

    print("\n" + "=" * 60)
    print("实验 5：卡方检验——分类变量是否独立？")
    print("=" * 60)

    # 模拟列联表
    observed = np.array([[30, 20], [15, 35]])  # 2×2 列联表
    chi2, p_chi, dof, expected = stats.chi2_contingency(observed)

    print(f"观察频数:\n{observed}")
    print(f"期望频数（H₀独立时）:\n{expected.round(1)}")
    print(f"卡方统计量 = {chi2:.3f}")
    print(f"p 值 = {p_chi:.6f}")
    print(f"结论: {'变量不独立（关联显著）' if p_chi < 0.05 else '变量独立'}")

    # ============ 可视化 ============
    fig, axes = plt.subplots(2, 2, figsize=(14, 11))

    # 图 1：p 值分布（H₀为真）
    ax = axes[0, 0]
    ax.hist(p_values_h0, bins=50, density=True, alpha=0.7, color='steelblue')
    ax.axhline(1.0, color='red', ls='--', lw=2, label='均匀分布（H₀为真）')
    ax.axvline(0.05, color='orange', ls='--', lw=2, label='α=0.05')
    ax.set_xlabel('p 值')
    ax.set_ylabel('密度')
    ax.set_title(f'H₀为真时 p 值分布（{false_positives/n_tests:.1%} < 0.05）')
    ax.legend()
    ax.grid(alpha=0.3)

    # 图 2：置信区间可视化
    ax = axes[0, 1]
    # 模拟多次采样
    means = []
    cis = []
    for _ in range(20):
        d = np.random.normal(mu_true, 1.0, 50)
        m = np.mean(d)
        ci_s = stats.t.interval(0.95, 49, loc=m, scale=stats.sem(d))
        means.append(m)
        cis.append(ci_s)

    for i, (m, ci_s) in enumerate(zip(means, cis)):
        color = 'blue' if ci_s[0] <= mu_0 <= ci_s[1] else 'red'
        ax.plot([i, i], [ci_s[0], ci_s[1]], color=color, lw=1.5)
        ax.plot(i, m, 'o', color=color, markersize=4)
    ax.axhline(mu_0, color='green', ls='--', lw=2, label=f'μ₀={mu_0}')
    ax.axhline(mu_true, color='black', ls=':', lw=2, label=f'真实μ={mu_true}')
    ax.set_xlabel('采样序号')
    ax.set_ylabel('均值 + 95%CI')
    ax.set_title('20 次采样的置信区间（红色=不含μ₀）')
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    # 图 3：功效曲线
    ax = axes[1, 0]
    ns_range = np.arange(10, 1000, 5)
    for d, color, label in [(0.2, 'red', 'd=0.2(小)'), (0.5, 'orange', 'd=0.5(中)'), (0.8, 'green', 'd=0.8(大)')]:
        powers = [compute_power(n, d) for n in ns_range]
        ax.plot(ns_range, powers, color=color, lw=2, label=label)
    ax.axhline(0.8, color='gray', ls='--', alpha=0.5, label='80%功效（标准）')
    ax.set_xlabel('样本量 n')
    ax.set_ylabel('统计功效 (1-β)')
    ax.set_title('功效 vs 样本量 vs 效应量')
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    # 图 4：效应量分布
    ax = axes[1, 1]
    ax.hist(group_A, bins=20, alpha=0.5, density=True, color='blue', label=f'A组(均值={np.mean(group_A):.1f})')
    ax.hist(group_B, bins=20, alpha=0.5, density=True, color='red', label=f'B组(均值={np.mean(group_B):.1f})')
    ax.axvline(np.mean(group_A), color='blue', ls='--', lw=2)
    ax.axvline(np.mean(group_B), color='red', ls='--', lw=2)
    ax.set_xlabel('值')
    ax.set_ylabel('密度')
    ax.set_title(f'A/B 测试（d={effect_size:.2f}, p={p_value2:.4f}）')
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig("25-统计检验_结果.png", dpi=120)
    print(f"\n[结果] 图像已保存: 25-统计检验_结果.png")

    print("\n" + "=" * 60)
    print("[总结]")
    print("=" * 60)
    print("1. p值：H₀为真时观测到极端数据的概率（不是H₀为真的概率）")
    print("2. 置信区间：95%CI 含真值的长期频率=95%")
    print("3. 效应量：'实际大小'比'统计显著'更重要")
    print("4. 功效：小效应需要大样本（d=0.2需n>500）")
    print("5. 多重检验：20次检验必然有假阳性→需Bonferroni校正")
    print("\n[解读] 统计检验是'量化不确定性'的工具——")
    print("       但p值被严重滥用。记住：")
    print("       统计显著 ≠ 重要；统计不显著 ≠ 无效。")


if __name__ == "__main__":
    main()
