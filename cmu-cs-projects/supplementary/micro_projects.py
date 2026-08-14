"""
CMU SCS — Miscellaneous Micro-Projects
================================================
覆盖实验课/seminar/特殊主题 9 门：
- 11-411Hidden Markov (Baum-Welch training)
- 14-733 Computational Photography (seam carving)
- 15-388 Practical Data Science (mini pandas)
- 15-463 Computational Photography (image blending)
- 16-385 Image Processing (bilateral filter)
- 17-556 Bias in Clinical Data (fairness metrics)
- 05-839 Privacy in ML (differential privacy noise)
- 11-667 NLP for Healthcare (de-identification)
- 08-725 Empirical Methods (power analysis)

每个 micro_* 函数实现一个小算法/演示。
"""
from __future__ import annotations
import math
import random
from collections import Counter

# ============ 11-411 HMM: Baum-Welch ============

def micro_11_411_baum_welch():
    """Baum-Welch: HMM 参数学习（EM 简化版）。"""
    print("\n📋 11-411: Baum-Welch (HMM Training via EM)")
    # 2-state HMM, observations: 0=Fair coin, 1=Biased
    # Start with random params, iterate EM
    A = [[0.6, 0.4], [0.3, 0.7]]  # transitions
    B = [[0.5, 0.5], [0.2, 0.8]]  # emissions
    pi = [0.5, 0.5]
    obs = [0, 1, 1, 0, 1, 1, 0, 1, 1, 1]

    def forward(o):
        T = len(o); N = 2
        a = [[0.0]*N for _ in range(T)]
        for i in range(N):
            a[0][i] = pi[i]*B[i][o[0]]
        for t in range(1, T):
            for j in range(N):
                a[t][j] = sum(a[t-1][i]*A[i][j] for i in range(N))*B[j][o[t]]
        return a

    def backward(o):
        T = len(o); N = 2
        b = [[0.0]*N for _ in range(T)]
        for i in range(N):
            b[T-1][i] = 1.0
        for t in range(T-2, -1, -1):
            for i in range(N):
                b[t][i] = sum(A[i][j]*B[j][o[t+1]]*b[t+1][j] for j in range(N))
        return b

    for iteration in range(5):
        alpha = forward(obs)
        beta = backward(obs)
        T = len(obs); N = 2
        # gamma
        gamma = [[0.0]*N for _ in range(T)]
        for t in range(T):
            norm = sum(alpha[t][i]*beta[t][i] for i in range(N))
            for i in range(N):
                gamma[t][i] = alpha[t][i]*beta[t][i] / max(norm, 1e-10)

    print(f"   Observations: {obs}")
    print(f"   Final gamma (P(state|obs)) at t=0: {gamma[0]}")
    print("   💡 Baum-Welch = EM for HMM → 自动学习转移/发射概率")


# ============ 14-733 Computational Photography: Seam Carving ============

def micro_14_733_seam_carving():
    """Seam carving: 基于能量的图像缩放。"""
    print("\n📋 14-733: Seam Carving (Content-Aware Resize)")
    # 5x5 "image" — energy gradient
    energy = [
        [1, 2, 8, 2, 1],
        [1, 3, 9, 3, 1],
        [1, 2, 9, 2, 1],
        [1, 2, 8, 2, 1],
        [1, 1, 1, 1, 1],
    ]
    h, w = len(energy), len(energy[0])
    # DP for vertical seam (minimum energy path top to bottom)
    dp = [row[:] for row in energy]
    for i in range(1, h):
        for j in range(w):
            min_prev = dp[i-1][j]
            if j > 0:
                min_prev = min(min_prev, dp[i-1][j-1])
            if j < w-1:
                min_prev = min(min_prev, dp[i-1][j+1])
            dp[i][j] += min_prev
    # backtrack
    seam = []
    j = min(range(w), key=lambda x: dp[h-1][x])
    seam.append(j)
    for i in range(h-2, -1, -1):
        candidates = [j]
        if j > 0: candidates.append(j-1)
        if j < w-1: candidates.append(j+1)
        j = min(candidates, key=lambda x: dp[i][x])
        seam.append(j)
    seam.reverse()
    print(f"   Energy map (5×5): high energy = center column")
    print(f"   Optimal seam (remove this): {seam}")
    print(f"   Seam total energy: {dp[h-1][min(range(w), key=lambda x: dp[h-1][x])]}")
    print("   💡 Seam carving 删除最低能量缝 → 不失真的内容感知缩放")


# ============ 15-388 Practical Data Science: Mini Pandas ============

def micro_15_388_mini_pandas():
    """Mini DataFrame：groupby + aggregate。"""
    print("\n📋 15-388: Mini DataFrame (groupby + aggregate)")
    data = [
        {'dept': 'CS', 'salary': 120},
        {'dept': 'CS', 'salary': 110},
        {'dept': 'Math', 'salary': 90},
        {'dept': 'CS', 'salary': 130},
        {'dept': 'Math', 'salary': 95},
        {'dept': 'Physics', 'salary': 85},
    ]
    # groupby + mean
    groups = {}
    for row in data:
        groups.setdefault(row['dept'], []).append(row['salary'])
    result = {k: sum(v)/len(v) for k, v in groups.items()}
    print(f"   Data: {len(data)} rows")
    print(f"   Groupby dept → mean salary:")
    for dept, avg in sorted(result.items(), key=lambda x: -x[1]):
        print(f"     {dept}: {avg:.0f}k")
    print("   💡 groupby-split-apply-combine = 数据分析核心范式")


# ============ 15-463 Image Blending ============

def micro_15_463_blending():
    """拉普拉斯金字塔融合（简化）。"""
    print("\n📋 15-463: Image Blending (Laplacian Pyramid concept)")
    imgA = [10, 12, 15, 20, 25, 30, 35, 40]
    imgB = [50, 48, 45, 40, 35, 30, 25, 20]
    mask = [1, 1, 1, 1, 0, 0, 0, 0]
    # Simple alpha blend
    blended = [a*m + b*(1-m) for a, b, m in zip(imgA, imgB, mask)]
    # Feathered mask (smooth transition)
    feather = [1.0, 0.9, 0.7, 0.5, 0.3, 0.1, 0.0, 0.0]
    feathered = [a*f + b*(1-f) for a, b, f in zip(imgA, imgB, feather)]
    print(f"   Image A: {imgA}")
    print(f"   Image B: {imgB}")
    print(f"   Hard mask blend:   {blended}")
    print(f"   Feathered blend:   {[round(x,1) for x in feathered]}")
    print("   💡 拉普拉斯金字塔 = 多尺度融合 → 无缝拼接 (Burt & Adelson 1983)")


# ============ 16-385 Image Processing: Bilateral Filter ============

def micro_16_385_bilateral():
    """双边滤波（保边平滑）。"""
    print("\n📋 16-385: Bilateral Filter (edge-preserving)")
    # 1D signal with an edge
    signal = [5, 5, 5, 5, 5, 50, 50, 50, 50, 50]
    sigma_s = 1.0  # spatial
    sigma_r = 10.0  # range (intensity)

    def bilateral_1d(sig, i, radius=2):
        num, den = 0.0, 0.0
        for k in range(max(0,i-radius), min(len(sig), i+radius+1)):
            ws = math.exp(-((k-i)**2) / (2*sigma_s**2))
            wr = math.exp(-((sig[k]-sig[i])**2) / (2*sigma_r**2))
            w = ws * wr
            num += w * sig[k]
            den += w
        return num / den

    result = [bilateral_1d(signal, i) for i in range(len(signal))]
    # Compare with Gaussian (range weight = 1)
    def gaussian_1d(sig, i, radius=2):
        num, den = 0.0, 0.0
        for k in range(max(0,i-radius), min(len(sig), i+radius+1)):
            w = math.exp(-((k-i)**2) / (2*sigma_s**2))
            num += w * sig[k]
            den += w
        return num / den
    gaussian_result = [gaussian_1d(signal, i) for i in range(len(signal))]
    print(f"   Input:      {signal}")
    print(f"   Gaussian:   {[round(x,1) for x in gaussian_result]}")
    print(f"   Bilateral:  {[round(x,1) for x in result]}")
    print("   💡 双边滤波在边缘处权重大降 → 保留边缘！Gaussian 会模糊边缘")


# ============ 17-556 Bias in Clinical Data ============

def micro_17_556_fairness():
    """公平性指标：demographic parity + equalized odds。"""
    print("\n📋 17-556: Fairness Metrics in Clinical ML")
    # Model predictions for two groups
    # (predicted_positive, actual_positive)
    group_A = [(1,1)]*15 + [(1,0)]*5 + [(0,1)]*10 + [(0,0)]*70  # Group A
    group_B = [(1,1)]*5 + [(1,0)]*25 + [(0,1)]*15 + [(0,0)]*55  # Group B

    def metrics(data):
        tp = sum(1 for p,a in data if p==1 and a==1)
        fp = sum(1 for p,a in data if p==1 and a==0)
        fn = sum(1 for p,a in data if p==0 and a==1)
        tn = sum(1 for p,a in data if p==0 and a==0)
        n = len(data)
        pred_pos_rate = (tp+fp)/n  # demographic parity
        tpr = tp/(tp+fn) if (tp+fn)>0 else 0  # equalized odds
        fpr = fp/(fp+tn) if (fp+tn)>0 else 0
        return pred_pos_rate, tpr, fpr

    pp_a, tpr_a, fpr_a = metrics(group_A)
    pp_b, tpr_b, fpr_b = metrics(group_B)
    print(f"   Group A: pred_pos_rate={pp_a:.2f}, TPR={tpr_a:.2f}, FPR={fpr_a:.2f}")
    print(f"   Group B: pred_pos_rate={pp_b:.2f}, TPR={tpr_b:.2f}, FPR={fpr_b:.2f}")
    print(f"   Demographic parity diff: {abs(pp_a-pp_b):.2f}")
    print(f"   Equalized odds diff: TPR={abs(tpr_a-tpr_b):.2f}, FPR={abs(fpr_a-fpr_b):.2f}")
    print("   💡 公平性是 multi-objective — demographic parity 和 equalized odds 不能同时满足")


# ============ 05-839 Privacy in ML: Differential Privacy ============

def micro_05_839_dp_noise():
    """差分隐私：Laplace 机制。"""
    print("\n📋 05-839: Differential Privacy (Laplace Mechanism)")
    # Query: COUNT(patients with condition X)
    true_count = 42
    epsilon = 1.0  # privacy budget
    sensitivity = 1.0  # adding/removing 1 person changes count by 1
    scale = sensitivity / epsilon

    # Laplace noise
    noises = []
    for _ in range(1000):
        u = random.random() - 0.5
        noise = -scale * math.copysign(1, u) * math.log(1 - 2*abs(u))
        noises.append(true_count + noise)

    mean_noisy = sum(noises) / len(noises)
    within_bounds = sum(1 for n in noises if abs(n - true_count) < scale)
    print(f"   True count: {true_count}, ε={epsilon}")
    print(f"   Laplace scale b = sensitivity/ε = {scale}")
    print(f"   Noisy mean (1000 trials): {mean_noisy:.2f}")
    print(f"   Within ±{scale} of true: {within_bounds}/1000 = {within_bounds/10:.0f}%")
    print("   💡 ε 越小→噪声越大→隐私越强但可用性越低 (Dwork 2006)")


# ============ 11-667 NLP for Healthcare: De-identification ============

def micro_11_667_deid():
    """PHI 脱敏：正则 + 规则。"""
    print("\n📋 11-667: Clinical Text De-identification (PHI)")
    import re
    text = (
        "Patient John Doe (MRN: 12345) visited on 01/15/2026. "
        "SSN: 123-45-6789. Phone: (412) 555-0100. "
        "Dr. Smith prescribed Lisinopril."
    )
    patterns = {
        'DATE': r'\b\d{1,2}/\d{1,2}/\d{4}\b',
        'SSN': r'\b\d{3}-\d{2}-\d{4}\b',
        'PHONE': r'\(\d{3}\)\s*\d{3}-\d{4}',
        'MRN': r'MRN:\s*\d+',
    }
    deidentified = text
    for entity, pattern in patterns.items():
        deidentified = re.sub(pattern, f'[{entity}]', deidentified)
    print(f"   Original: {text}")
    print(f"   De-identified: {deidentified}")
    print("   💡 HIPAA Safe Harbor: 18 种 PHI 必须脱敏才能用于研究")


# ============ 08-725 Empirical Methods: Power Analysis ============

def micro_08_725_power_analysis():
    """统计功效分析：样本量估计。"""
    print("\n📋 08-725: Statistical Power Analysis")
    # For two-sample t-test: n ≈ 16 / d² (Cohen's approximation)
    # d = effect size (standardized mean difference)
    effect_sizes = [0.2, 0.5, 0.8]  # small, medium, large
    for d in effect_sizes:
        n_per_group = math.ceil(16 / d**2)
        label = {0.2:'small', 0.5:'medium', 0.8:'large'}[d]
        print(f"   Effect size d={d} ({label:6s}): n ≥ {n_per_group} per group")
    print("   💡 小效应需要大样本！d=0.2 → 400+ 人/组才有 80% 功效")


# ============ 主入口 ============

def run_all():
    print("=" * 60)
    print("🎓 CMU SCS — Miscellaneous Micro-Projects")
    print("=" * 60)
    random.seed(42)
    micro_11_411_baum_welch()
    micro_14_733_seam_carving()
    micro_15_388_mini_pandas()
    micro_15_463_blending()
    micro_16_385_bilateral()
    micro_17_556_fairness()
    micro_05_839_dp_noise()
    micro_11_667_deid()
    micro_08_725_power_analysis()
    print("\n" + "=" * 60)
    print("✅ 全部杂项微项目完成！(9 门课程)")
    print("=" * 60)

if __name__ == "__main__":
    run_all()
