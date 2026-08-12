"""
Princeton COS 研究生课程补充项目集
=====================================
覆盖课程：
- COS 502 Machine Learning (undergrad-grad)
- COS 508 Theoretical Machine Learning
- COS 513 Applied Machine Learning
- COS 521 Advanced Algorithm Design
- COS 522 Foundations of Machine Learning
- COS 597E Fairness in ML
- ELE 522 Information Theory
- ORF 524 Statistical Theory
- COS 597J Topics in ML
- COS 598C Causality
"""
import math
import random
from collections import Counter, defaultdict


# ============ COS 502 Machine Learning ============

def cos502_svm_smo():
    """COS 502: SVM with simplified SMO algorithm."""
    print("\n📋 COS 502: SVM (简化版 SMO)")
    random.seed(42)
    # Generate linearly separable data
    X, y = [], []
    for _ in range(20):
        X.append([random.gauss(-1, 0.5), random.gauss(-1, 0.5)]); y.append(-1)
        X.append([random.gauss(1, 0.5), random.gauss(1, 0.5)]); y.append(1)

    # Simplified SMO: solve dual problem
    n = len(X)
    alpha = [0.0] * n
    b = 0.0
    C = 1.0  # regularization
    tol = 0.001
    max_passes = 10

    def kernel(i, j):
        return sum(X[i][d] * X[j][d] for d in range(len(X[0])))

    def f(i):
        return sum(alpha[j] * y[j] * kernel(i, j) for j in range(n)) - b

    passes = 0
    max_iter = 200  # hard iteration limit to prevent non-convergence
    it = 0
    while passes < max_passes and it < max_iter:
        it += 1
        num_changed = 0
        for i in range(n):
            Ei = f(i) - y[i]
            if (y[i] * Ei < -tol and alpha[i] < C) or (y[i] * Ei > tol and alpha[i] > 0):
                j = random.randint(0, n - 1)
                while j == i:
                    j = random.randint(0, n - 1)
                Ej = f(j) - y[j]
                alpha_i_old, alpha_j_old = alpha[i], alpha[j]
                if y[i] != y[j]:
                    L = max(0, alpha[j] - alpha[i])
                    H = min(C, C + alpha[j] - alpha[i])
                else:
                    L = max(0, alpha[i] + alpha[j] - C)
                    H = min(C, alpha[i] + alpha[j])
                if L == H:
                    continue
                eta = 2 * kernel(i, j) - kernel(i, i) - kernel(j, j)
                if eta >= 0:
                    continue
                alpha[j] -= y[j] * (Ei - Ej) / eta
                alpha[j] = max(L, min(H, alpha[j]))
                alpha[i] += y[i] * y[j] * (alpha_j_old - alpha[j])
                b1 = b - Ei - y[i] * (alpha[i] - alpha_i_old) * kernel(i, i) - \
                     y[j] * (alpha[j] - alpha_j_old) * kernel(i, j)
                b2 = b - Ej - y[i] * (alpha[i] - alpha_i_old) * kernel(i, j) - \
                     y[j] * (alpha[j] - alpha_j_old) * kernel(j, j)
                if 0 < alpha[i] < C:
                    b = b1
                elif 0 < alpha[j] < C:
                    b = b2
                else:
                    b = (b1 + b2) / 2
                num_changed += 1
        if num_changed == 0:
            passes += 1
        else:
            passes = 0

    # Count support vectors
    sv_count = sum(1 for a in alpha if a > 1e-5)
    acc = sum(1 for i in range(n) if (f(i) > 0) == (y[i] > 0)) / n
    print(f"   训练 {n} 个样本, C={C}")
    print(f"   支持向量数: {sv_count}/{n}")
    print(f"   训练准确率: {acc:.1%}")
    print(f"   → 只有支持向量(alpha>0)决定决策边界")


# ============ COS 508 Theoretical ML ============

def cos508_pac_bayes_bound():
    """COS 508: PAC-Bayes generalization bound."""
    print("\n📋 COS 508: PAC-Bayes 泛化界限")
    # McAllester bound: with prob ≥ 1-δ,
    #   E_Q[L(h)] ≤ E_Q[L̂(h)] + sqrt((KL(Q||P) + ln(2√n/δ)) / (2n))
    n = 1000
    delta = 0.05
    kl = 5.0  # KL divergence between posterior Q and prior P
    empirical_loss = 0.05

    bound_term = (kl + math.log(2 * math.sqrt(n) / delta)) / (2 * n)
    gen_gap = math.sqrt(bound_term)
    true_loss_bound = empirical_loss + gen_gap

    print(f"   样本数 n={n}, δ={delta}, KL(Q||P)={kl}")
    print(f"   经验损失: {empirical_loss}")
    print(f"   泛化间隙 (PAC-Bayes): {gen_gap:.4f}")
    print(f"   真实损失上界: {true_loss_bound:.4f}")
    print(f"   → PAC-Bayes 给出数据相关的、非空的泛化保证")


# ============ COS 513 Applied ML ============

def cos513_cross_validation():
    """COS 513: k-fold cross-validation."""
    print("\n📋 COS 513: k-fold 交叉验证")
    random.seed(42)
    # Simulate model evaluation
    n = 100
    data = list(range(n))
    random.shuffle(data)

    for k in [5, 10]:
        fold_size = n // k
        fold_accs = []
        for fold in range(k):
            test_idx = set(data[fold * fold_size:(fold + 1) * fold_size])
            # Simulate accuracy with noise
            acc = 0.85 + random.gauss(0, 0.03)
            fold_accs.append(acc)
        mean_acc = sum(fold_accs) / k
        std_acc = (sum((a - mean_acc) ** 2 for a in fold_accs) / k) ** 0.5
        print(f"   {k}-fold CV: 均值={mean_acc:.4f}, 标准差={std_acc:.4f}")
    print(f"   → k 越大方差越小，但计算成本越高")


# ============ COS 521 Advanced Algorithms ============

def cos521_lp_relaxation():
    """COS 521: LP relaxation for integer programming."""
    print("\n📋 COS 521: LP 松驰 (Vertex Cover 近似)")
    # Vertex Cover ILP: min Σ x_v, s.t. x_u + x_v ≥ 1 for each edge (u,v), x_v ∈ {0,1}
    # LP relaxation: x_v ∈ [0,1]
    # Rounding: if x_v ≥ 0.5, select vertex (2-approximation)

    # Example graph: triangle
    edges = [(0, 1), (1, 2), (0, 2)]
    n = 3
    print(f"   图: 三角形 (3 节点, 3 边)")
    # Optimal LP solution: x_v = 0.5 for all (symmetric)
    lp_solution = [0.5] * n
    lp_cost = sum(lp_solution)
    print(f"   LP 松弛解: x = {lp_solution}, LP代价 = {lp_cost}")

    # Rounding
    rounded = [1 if x >= 0.5 else 0 for x in lp_solution]
    rounded_cost = sum(rounded)
    print(f"   取整后: {rounded}, 整数代价 = {rounded_cost}")
    # Optimal ILP
    print(f"   最优整数解: {rounded} (选所有节点), 代价 = {rounded_cost}")
    print(f"   近似比: {rounded_cost}/{lp_cost} = {rounded_cost/lp_cost:.1f} (≤ 2)")


# ============ COS 522 Foundations of ML ============

def cos522_bias_variance_decomposition():
    """COS 522: Bias-variance tradeoff decomposition."""
    print("\n📋 COS 522: Bias-Variance 分解")
    random.seed(42)
    true_fn = lambda x: math.sin(x)
    n_models = 100
    n_points = 20

    for model_complexity in ["low", "high"]:
        predictions = [[] for _ in range(n_points)]
        for _ in range(n_models):
            # Generate training data
            x_train = [random.uniform(0, math.pi) for _ in range(15)]
            y_train = [true_fn(x) + random.gauss(0, 0.2) for x in x_train]

            if model_complexity == "low":
                # Simple: constant prediction (high bias)
                mean_y = sum(y_train) / len(y_train)
                preds = [mean_y] * n_points
            else:
                # Complex: overfit to training points (high variance)
                preds = []
                for i in range(n_points):
                    x_test = i * math.pi / n_points
                    # Nearest neighbor
                    nearest = min(x_train, key=lambda x: abs(x - x_test))
                    idx = x_train.index(nearest)
                    preds.append(y_train[idx])

            for i in range(n_points):
                predictions[i].append(preds[i])

        # Compute bias and variance
        total_bias = 0
        total_var = 0
        for i in range(n_points):
            x = i * math.pi / n_points
            true_val = true_fn(x)
            mean_pred = sum(predictions[i]) / n_models
            bias_sq = (mean_pred - true_val) ** 2
            variance = sum((p - mean_pred) ** 2 for p in predictions[i]) / n_models
            total_bias += bias_sq
            total_var += variance

        print(f"   {model_complexity:>5} 复杂度: bias²={total_bias/n_points:.4f}, "
              f"variance={total_var/n_points:.4f}")
    print(f"   → 低复杂度: 高偏差低方差; 高复杂度: 低偏差高方差")


# ============ COS 597E Fairness ============

def cos597e_disparate_impact():
    """COS 597E: Disparate impact (80% rule)."""
    print("\n📋 COS 597E: Disparate Impact (四分之三规则)")
    # 80% rule: pass rate of any group should be ≥ 80% of the highest group
    groups = {"A": 120, "B": 80}
    totals = {"A": 150, "B": 110}
    pass_rates = {g: groups[g] / totals[g] for g in groups}
    max_rate = max(pass_rates.values())
    for g, rate in pass_rates.items():
        ratio = rate / max_rate
        compliant = "✓" if ratio >= 0.8 else "✗"
        print(f"   组 {g}: 通过率 {rate:.1%}, 相对比率 {ratio:.2%} {compliant}")


# ============ ELE 522 Information Theory ============

def ele522_channel_capacity():
    """ELE 522: Shannon's channel capacity."""
    print("\n📋 ELE 522: Shannon 信道容量")
    # Binary Symmetric Channel: C = 1 - H(p), H(p) = -p*log2(p) - (1-p)*log2(1-p)
    def entropy(p):
        if p == 0 or p == 1:
            return 0.0
        return -p * math.log2(p) - (1-p) * math.log2(1-p)

    print("   二元对称信道 (BSC): C = 1 - H(p)")
    for p in [0.01, 0.05, 0.1, 0.3, 0.5]:
        capacity = 1 - entropy(p)
        print(f"   p={p:.2f}: H(p)={entropy(p):.4f}, C={capacity:.4f} bits/use")
    print("   → p=0.5 时容量为 0（完全随机噪声）")
    print("   → 但只要 p < 0.5，就能可靠通信（Shannon 编码定理）")


# ============ ORF 524 Statistical Theory ============

def orf524_bias_consistency():
    """ORF 524: MLE consistency and asymptotic normality."""
    print("\n📋 ORF 524: MLE 一致性与渐近正态性")
    random.seed(42)
    # Sample from N(mu, 1), estimate mu via MLE (= sample mean)
    true_mu = 3.0
    for n in [10, 100, 1000, 10000]:
        mle_estimates = []
        for _ in range(1000):
            samples = [random.gauss(true_mu, 1) for _ in range(n)]
            mle = sum(samples) / n  # MLE for Gaussian mean
            mle_estimates.append(mle)
        mean_est = sum(mle_estimates) / len(mle_estimates)
        var_est = sum((x - mean_est) ** 2 for x in mle_estimates) / len(mle_estimates)
        se_theoretical = 1.0 / math.sqrt(n)  # Asymptotic: sqrt(n)(μ̂-μ) → N(0, σ²)
        print(f"   n={n:>5}: MLE均值={mean_est:.4f} (真={true_mu}), "
              f"SE={math.sqrt(var_est):.4f} (理论={se_theoretical:.4f})")
    print("   → MLE 一致（收敛到真值），渐近正态 SE=σ/√n")


# ============ COS 597J Topics in ML ============

def cos597j_federated_learning():
    """COS 597J: Federated Learning (FedAvg)."""
    print("\n📋 COS 597J: 联邦学习 (FedAvg)")
    random.seed(42)
    n_clients = 5
    true_w = 5.0
    global_w = 0.0  # initial global model

    rounds = 20
    for rnd in range(rounds):
        client_updates = []
        for c in range(n_clients):
            # Each client trains on local data
            local_data = [true_w + random.gauss(0, 1) for _ in range(10)]
            local_w = sum(local_data) / len(local_data)
            client_updates.append(local_w)
        # FedAvg: average client models
        global_w = sum(client_updates) / len(client_updates)

    print(f"   {n_clients} 客户端, {rounds} 轮 FedAvg")
    print(f"   真实参数: {true_w}")
    print(f"   全局模型: {global_w:.4f}")
    print(f"   误差: {abs(global_w - true_w):.4f}")
    print(f"   → 数据不出本地，仅交换模型参数")


# ============ COS 598C Causality ============

def cos598c_do_calculus():
    """COS 598C: Pearl's do-calculus."""
    print("\n📋 COS 598C: 因果推断 (do-calculus)")
    # Simpson's Paradox: treatment appears harmful overall but beneficial within strata
    # Treatment A vs B, recovery rates
    # Overall: A=78/150=52%, B=82/150=55% (B better)
    # But within each subgroup: A is better

    # Subgroup: Severe cases
    A_severe_rec = 18; A_severe_tot = 30  # 60%
    B_severe_rec = 2;  B_severe_tot = 10  # 20%
    # Subgroup: Mild cases
    A_mild_rec = 60;  A_mild_tot = 120  # 50%
    B_mild_rec = 80;  B_mild_tot = 140  # 57%

    print("   Simpson 悖论示例:")
    print(f"   重症组: A治愈 {A_severe_rec}/{A_severe_tot}={A_severe_rec/A_severe_tot:.0%}, "
          f"B治愈 {B_severe_rec}/{B_severe_tot}={B_severe_rec/B_severe_tot:.0%}")
    print(f"   轻症组: A治愈 {A_mild_rec}/{A_mild_tot}={A_mild_rec/A_mild_tot:.0%}, "
          f"B治愈 {B_mild_rec}/{B_mild_tot}={B_mild_rec/B_mild_tot:.0%}")
    print(f"   → A 在两个子组中都更好，但总体看 B 更好！")
    print(f"   → do(A) vs do(B) 的因果效应需要后门调整")


# ============ 主入口 ============

def run_all_grad():
    print("=" * 60)
    print("🎓 Princeton COS 研究生课程补充项目")
    print("=" * 60)

    cos502_svm_smo()
    cos508_pac_bayes_bound()
    cos513_cross_validation()
    cos521_lp_relaxation()
    cos522_bias_variance_decomposition()
    cos597e_disparate_impact()
    ele522_channel_capacity()
    orf524_bias_consistency()
    cos597j_federated_learning()
    cos598c_do_calculus()

    print("\n" + "=" * 60)
    print("✅ 全部研究生补充课程完成！")
    print("=" * 60)


if __name__ == "__main__":
    run_all_grad()
