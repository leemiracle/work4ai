"""
MIT EECS 补充课程微项目集 — 研究生专题（grad_projects.py）
覆盖课程：
- 6.867 ML (graduate)
- 6.869 Computer Vision
- 6.871 Computational Biology
- 6.874 Machine Learning for Healthcare
- 6.876 Distributed Cryptography
- 6.878 Computer Architecture
- 6.879 Probabilistic Programming
- 6.S982 ML Systems
- 9.520 Statistical Learning Theory
- HST.506 Healthcare Analytics
"""
import math
import random


# ============ 6.867 ML (graduate) ============

def mit6_867_svm_smo():
    """SVM via 简化 SMO"""
    print("\n📋 6.867: SVM (简化 SMO)")
    # 线性 SVM: max margin, 小规模数据
    # 2D 可分数据
    X = [(1,1),(2,1),(2,0.5),(0.5,1.5),(-1,-1),(-0.5,-2),(-1.5,-1),(-2,-0.5)]
    y = [1,1,1,1,-1,-1,-1,-1]
    # 解析法求 w, b (线性可分硬间隔)
    # w = Σ α_i y_i x_i; 只演示概念
    # 用感知机近似
    w = [0.0, 0.0]; b = 0.0; lr = 0.01
    for epoch in range(1000):
        for i in range(len(X)):
            margin = y[i] * (w[0]*X[i][0] + w[1]*X[i][1] + b)
            if margin < 1:
                w[0] += lr * y[i] * X[i][0]
                w[1] += lr * y[i] * X[i][1]
                b += lr * y[i]
    correct = sum(1 for i in range(len(X)) if y[i]*(w[0]*X[i][0]+w[1]*X[i][1]+b) > 0)
    margin_val = 2 / math.sqrt(w[0]**2 + w[1]**2)
    print(f"  w=({w[0]:.2f}, {w[1]:.2f}), b={b:.2f}")
    print(f"  分类正确: {correct}/{len(X)}, margin宽度={margin_val:.3f}")


# ============ 6.869 Computer Vision ============

def mit6_869_hog_features():
    """HOG 特征简化（梯度直方图）"""
    print("\n📋 6.869: HOG 特征 (梯度直方图)")
    # Dalal & Triggs 2005 CVPR
    image = [
        [0,0,0,0,0,0],
        [0,0,5,5,0,0],
        [0,0,5,5,0,0],
        [0,0,5,5,0,0],
        [0,0,0,0,0,0],
    ]
    # 计算梯度
    gx = [[0]*6 for _ in range(5)]
    gy = [[0]*6 for _ in range(5)]
    for i in range(5):
        for j in range(6):
            gx[i][j] = (image[i][min(j+1,5)] - image[i][max(j-1,0)]) if 0 < j < 5 else 0
            gy[i][j] = (image[min(i+1,4)][j] - image[max(i-1,0)][j]) if 0 < i < 4 else 0
    # 梯度方向直方图 (9 bins, 0-180度)
    bins = [0]*9
    for i in range(5):
        for j in range(6):
            mag = math.sqrt(gx[i][j]**2 + gy[i][j]**2)
            angle = math.degrees(math.atan2(gy[i][j], gx[i][j])) % 180
            b = int(angle / 20) % 9
            bins[b] += mag
    max_bin = max(range(9), key=lambda i: bins[i])
    print(f"  图像含垂直边缘 (左暗右亮)")
    print(f"  HOG 9-bin: {[round(b, 1) for b in bins]}")
    print(f"  主导方向 bin {max_bin} ({max_bin*20}-{(max_bin+1)*20}°)")


# ============ 6.871 Computational Biology ============

def mit6_871_sequence_alignment():
    """Needleman-Wunsch 全局比对"""
    print("\n📋 6.871: Needleman-Wunsch 序列比对")
    def nw_align(s1, s2, match=1, mismatch=-1, gap=-2):
        n, m = len(s1), len(s2)
        dp = [[0]*(m+1) for _ in range(n+1)]
        for i in range(1, n+1): dp[i][0] = i * gap
        for j in range(1, m+1): dp[0][j] = j * gap
        for i in range(1, n+1):
            for j in range(1, m+1):
                diag = dp[i-1][j-1] + (match if s1[i-1]==s2[j-1] else mismatch)
                dp[i][j] = max(dp[i-1][j]+gap, dp[i][j-1]+gap, diag)
        # 回溯
        a1, a2 = [], []
        i, j = n, m
        while i > 0 or j > 0:
            if i > 0 and j > 0 and dp[i][j] == dp[i-1][j-1] + (match if s1[i-1]==s2[j-1] else mismatch):
                a1.append(s1[i-1]); a2.append(s2[j-1]); i -= 1; j -= 1
            elif i > 0 and dp[i][j] == dp[i-1][j] + gap:
                a1.append(s1[i-1]); a2.append('-'); i -= 1
            else:
                a1.append('-'); a2.append(s2[j-1]); j -= 1
        return dp[n][m], ''.join(reversed(a1)), ''.join(reversed(a2))
    score, a1, a2 = nw_align("GATTACA", "GCATGCU")
    print(f"  GATTACA vs GCATGCU: score={score}")
    print(f"  {a1}")
    print(f"  {a2}")


# ============ 6.874 Healthcare ML ============

def mit6_874_evaluation_metrics():
    """医疗 ML 评估：Sensitivity/Specificity/PPV"""
    print("\n📋 6.874: 医疗 ML 评估指标")
    # 混淆矩阵 (疾病检测)
    TP, FP = 90, 20   # 真阳性 90, 假阳性 20
    FN, TN = 10, 880  # 假阴性 10, 真阴性 880
    sensitivity = TP / (TP + FN)  # 召回率
    specificity = TN / (TN + FP)
    ppv = TP / (TP + FP)          # 精确率
    npv = TN / (TN + FN)
    prevalence = (TP + FN) / (TP + FP + FN + TN)
    print(f"  TP={TP}, FP={FP}, FN={FN}, TN={TN}")
    print(f"  Sensitivity (召回): {sensitivity:.1%} ← 不漏诊")
    print(f"  Specificity:        {specificity:.1%} ← 不误诊")
    print(f"  PPV (精确):         {ppv:.1%} ← 阳性中真阳性比例")
    print(f"  NPV:                {npv:.1%}")
    print(f"  Prevalence:         {prevalence:.1%}")


# ============ 6.876 Distributed Crypto ============

def mit6_876_secret_sharing():
    """Shamir 秘密共享 (t-of-n)"""
    print("\n📋 6.876: Shamir 秘密共享 (3-of-5)")
    # 秘密 S = 42, 在 GF(97) 上
    p = 97
    S = 42
    # 多项式 f(x) = S + a1*x + a2*x^2 mod p
    a1, a2 = 35, 61  # 随机系数
    shares = [(i, (S + a1*i + a2*i*i) % p) for i in range(1, 6)]
    print(f"  秘密 S={S}, 5 个 share: {shares}")
    # 用任意 3 个恢复 (拉格朗日插值)
    def recover(shares, p):
        secret = 0
        for j, (xj, yj) in enumerate(shares):
            num, den = 1, 1
            for m, (xm, _) in enumerate(shares):
                if m != j:
                    num *= -xm
                    den *= (xj - xm)
            secret += yj * num * pow(den, -1, p)
        return secret % p
    recovered = recover(shares[:3], p)
    print(f"  用 share 1-3 恢复: S={recovered} ✓" if recovered == S else f"  恢复失败: {recovered}")
    recovered2 = recover(shares[2:5], p)
    print(f"  用 share 3-5 恢复: S={recovered2} ✓" if recovered2 == S else f"  恢复失败: {recovered2}")


# ============ 6.878 Computer Architecture ============

def mit6_878_pipeline_hazard():
    """流水线冒险分析"""
    print("\n📋 6.878: 流水线数据冒险")
    # 5 级流水线: IF ID EX MEM WB
    instructions = [
        ("ADD", "R1", "R2", "R3"),   # R1 = R2 + R3
        ("SUB", "R4", "R1", "R5"),   # 用 R1 (RAW hazard)
        ("AND", "R6", "R1", "R7"),   # 用 R1
        ("OR",  "R8", "R9", "R10"),  # 无冒险
    ]
    for i, inst in enumerate(instructions):
        op, rd, rs1, rs2 = inst
        hazard = ""
        if i > 0:
            prev = instructions[i-1]
            if rs1 == prev[1] or rs2 == prev[1]:
                hazard = " ← RAW hazard (需要 forwarding 或 stall)"
        print(f"  {i}: {op} {rd},{rs1},{rs2}{hazard}")


# ============ 6.879 Probabilistic Programming ============

def mit6_879_bayesian_inference():
    """贝叶斯推断：硬币偏向"""
    print("\n📋 6.879: 贝叶斯推断 (Beta-Binomial)")
    # 先验 Beta(2,2), 观测 7 正面 3 反面
    prior_a, prior_b = 2, 2
    heads, tails = 7, 3
    post_a = prior_a + heads
    post_b = prior_b + tails
    # 后验均值
    post_mean = post_a / (post_a + post_b)
    # MLE (无先验)
    mle = heads / (heads + tails)
    print(f"  先验 Beta({prior_a},{prior_b}), 观测 {heads}H {tails}T")
    print(f"  后验 Beta({post_a},{post_b}), 后验均值={post_mean:.3f}")
    print(f"  MLE (无先验)={mle:.3f}")
    print(f"  → 先验把估计从 {mle:.3f} 向 0.5 收缩 (shrinkage)")


# ============ 6.S982 ML Systems ============

def mit6_s982_model_serving():
    """模型服务：批处理 vs 逐条"""
    print("\n📋 6.S982: ML 推理批处理效率")
    def simulate_batch(model_time_per_item, batch_size, n_requests):
        # 模型可同时处理 batch_size 个
        batches = math.ceil(n_requests / batch_size)
        total_time = batches * model_time_per_item(batch_size)
        return total_time
    # 推理时间函数：batch 越大每个 item 时间越少 (GPU 并行)
    n = 1000
    scenarios = [
        ("逐条 (batch=1)", lambda b: 0.01, 1),
        ("batch=8", lambda b: 0.03, 8),
        ("batch=32", lambda b: 0.08, 32),
        ("batch=64", lambda b: 0.14, 64),
    ]
    print(f"  {n} 请求:")
    for name, t_fn, bs in scenarios:
        t = simulate_batch(t_fn, bs, n)
        throughput = n / t
        print(f"    {name}: 总时间={t:.1f}s, 吞吐={throughput:.0f} req/s")


# ============ 9.520 Statistical Learning Theory ============

def mit9_520_vc_dimension():
    """VC 维演示"""
    print("\n📋 9.520: VC 维 (线性分类器)")
    # 在 1D 中: 阈值分类器 h(x) = sign(x - θ) 的 VC维 = 1
    # 在 2D 中: 线性分类器 VC维 = 3
    # 通用: d 维线性分类器 VC维 = d+1
    for d in [1, 2, 3, 10]:
        vc = d + 1
        # 样本数 m 时, 泛化界 ≈ sqrt(vc/m)
        for m in [100, 1000, 10000]:
            bound = math.sqrt(vc / m)
            print(f"  d={d}: VC维={vc}, m={m}: 泛化误差界≈{bound:.3f}")
        print()


# ============ HST.506 Healthcare Analytics ============

def hst506_survival_analysis():
    """生存分析：Kaplan-Meier"""
    print("\n📋 HST.506: Kaplan-Meier 生存分析")
    # events: (time, event=1死亡/0删失)
    events = [(2,1),(3,1),(5,0),(6,1),(7,1),(8,0),(10,1),(12,0),(15,1)]
    events.sort()
    n_at_risk = len(events)
    survival = 1.0
    print(f"  {'时间':>4}{'风险数':>6}{'事件':>4}{'S(t)':>8}")
    for t, e in events:
        d = sum(1 for _, ev in events if _ == t and ev == 1)
        n = sum(1 for tt, _ in events if tt >= t)
        if e == 1:
            survival *= (1 - d/n)
        print(f"  {t:>4}{n:>6}{e:>4}{survival:>8.3f}")
    print(f"  → 最终生存率 S(t)={survival:.3f}")


# ============ 主入口 ============

def run_grad():
    print("=" * 65)
    print("🎓 MIT EECS 研究生补充课程微项目")
    print("=" * 65)
    mit6_867_svm_smo()
    mit6_869_hog_features()
    mit6_871_sequence_alignment()
    mit6_874_evaluation_metrics()
    mit6_876_secret_sharing()
    mit6_878_pipeline_hazard()
    mit6_879_bayesian_inference()
    mit6_s982_model_serving()
    mit9_520_vc_dimension()
    hst506_survival_analysis()
    print("\n" + "=" * 65)
    print("✅ 研究生补充课程完成！")
    print("=" * 65)


if __name__ == "__main__":
    run_grad()
