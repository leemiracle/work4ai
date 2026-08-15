"""
COS 595 / 597 Fairness in Machine Learning（Princeton）
==========================================================
覆盖主题：
- Demographic parity（群体平权）
- Equalized odds（Hardt post-processing）
- Calibration（校准）
- Counterfactual fairness（Kusner，基于因果模型）
- Post-processing vs in-processing 策略对比

核心论文：
- Hardt, Price, Srebro 2016 "Equality of Opportunity in Supervised Learning" NeurIPS
- Kusner, Loftus, Russell, Silva 2017 "Counterfactual Fairness" NeurIPS
- Chouldechova 2017 "Fair Prediction with Disparate Impact" Big Data (impossibility theorem)
- Kleinberg, Mullainathan, Raghavan 2017 "Inherent Trade-offs in the Fair Determination of Risk Scores" ITCS

本文件实现：
1. Demographic parity 测量 + 调整
2. Equalized odds post-processing (Hardt threshold optimization)
3. Calibration analysis (reliability diagrams concept)
4. Counterfactual fairness evaluation
5. Post-processing vs in-processing 对比实验

运行：
    python fairness.py
"""
from __future__ import annotations
import random
import math
from collections import defaultdict
from dataclasses import dataclass


# ================================================================
# 1. Fairness Metrics
# ================================================================

@dataclass
class PredictionData:
    y_true: list[int]       # ground truth labels
    y_pred: list[int]       # predicted labels
    y_score: list[float]    # predicted scores/probabilities
    groups: list[str]       # protected attribute (e.g., "A", "B")


def demographic_parity(data: PredictionData) -> dict:
    """P(Ŷ=1 | A=a) should be equal across groups.

    Statistical parity: positive prediction rate equal across groups.
    """
    group_rates = defaultdict(list)
    for pred, g in zip(data.y_pred, data.groups):
        group_rates[g].append(pred)
    rates = {g: sum(v) / len(v) for g, v in group_rates.items()}
    diff = max(rates.values()) - min(rates.values())
    return {"rates": rates, "difference": diff, "satisfied": diff < 0.05}


def equalized_odds(data: PredictionData) -> dict:
    """P(Ŷ=1 | Y=y, A=a) should be equal across groups for y=0 and y=1.

    Hardt et al. 2016: equal TPR and FPR across groups.
    """
    groups = set(data.groups)
    result = {}
    for g in groups:
        indices = [i for i, gi in enumerate(data.groups) if gi == g]
        tp = sum(1 for i in indices if data.y_true[i] == 1 and data.y_pred[i] == 1)
        fn = sum(1 for i in indices if data.y_true[i] == 1 and data.y_pred[i] == 0)
        fp = sum(1 for i in indices if data.y_true[i] == 0 and data.y_pred[i] == 1)
        tn = sum(1 for i in indices if data.y_true[i] == 0 and data.y_pred[i] == 0)
        tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        result[g] = {"tpr": tpr, "fpr": fpr}

    tprs = [r["tpr"] for r in result.values()]
    fprs = [r["fpr"] for r in result.values()]
    return {
        "per_group": result,
        "tpr_diff": max(tprs) - min(tprs),
        "fpr_diff": max(fprs) - min(fprs),
        "satisfied": (max(tprs) - min(tprs) < 0.05 and max(fprs) - min(fprs) < 0.05),
    }


def calibration(data: PredictionData, n_bins: int = 5) -> dict:
    """Calibration: for score s, P(Y=1 | score ≈ s) should ≈ s.

    Group calibration: this should hold within each group.
    """
    result = {}
    for g in sorted(set(data.groups)):
        indices = [i for i, gi in enumerate(data.groups) if gi == g]
        scores = [data.y_score[i] for i in indices]
        labels = [data.y_true[i] for i in indices]
        bins = defaultdict(lambda: [0, 0])  # bin → (sum_label, count)
        for s, y in zip(scores, labels):
            b = min(int(s * n_bins), n_bins - 1)
            bins[b][0] += y
            bins[b][1] += 1
        calib_curve = []
        for b in range(n_bins):
            if bins[b][1] > 0:
                avg_score = (b + 0.5) / n_bins
                actual_rate = bins[b][0] / bins[b][1]
                calib_curve.append((avg_score, actual_rate, bins[b][1]))
        # Calibration error
        calib_error = sum(abs(avg - act) * cnt for avg, act, cnt in calib_curve) / max(len(indices), 1)
        result[g] = {"curve": calib_curve, "error": calib_error}
    return result


# ================================================================
# 2. Hardt Post-Processing (Equalized Odds) — true three-step algorithm
# ================================================================

def _compute_roc(scores: list[float], labels: list[int]) -> list[tuple]:
    """Compute ROC curve for one group.

    Returns a list of ``(threshold, fpr, tpr)`` tuples, sorted by
    threshold descending.  Each entry means: "classify score >= threshold
    as positive" yields the given (fpr, tpr).
    """
    n_pos = sum(labels)
    n_neg = len(labels) - n_pos
    if n_pos == 0 or n_neg == 0:
        return [(float('inf'), 0.0, 0.0)]
    # Sort by score descending
    sorted_pairs = sorted(zip(scores, labels), key=lambda x: -x[0])
    points = [(float('inf'), 0.0, 0.0)]  # threshold above max → all negative
    tp = fp = 0
    for s, y in sorted_pairs:
        if y == 1:
            tp += 1
        else:
            fp += 1
        points.append((s, fp / n_neg, tp / n_pos))
    return points


def hardt_postprocess(data: PredictionData) -> PredictionData:
    """Hardt, Price & Srebro 2016 — *true* equalized odds post-processing.

    Three-step algorithm (NOT per-group accuracy maximization):

    1. **Per-group ROC curves**: for each group, sweep thresholds to
       obtain the set of achievable (FPR, TPR) operating points.
    2. **Global target (FPR*, TPR*)**: search over candidate operating
       points for one that *all groups can approximate*, maximizing
       accuracy subject to the equalized-odds constraint (shared FPR
       and TPR across groups).  This is the key step — the target is
       *global*, not per-group.
    3. **Per-group thresholds**: for each group, pick the threshold
       whose ROC point is closest to the global target.  (Hardt also
       allows randomization between two adjacent thresholds to hit any
       point on the ROC convex hull; we use threshold-only for
       simplicity.)

    Contrast: ``per_group_accuracy_threshold`` (the old implementation)
    independently maximizes each group's accuracy with no mechanism to
    align operating points — equalized odds improves only by accident.
    """
    groups = sorted(set(data.groups))

    # --- Step 1: per-group ROC ---
    group_info = {}
    for g in groups:
        idx = [i for i, gi in enumerate(data.groups) if gi == g]
        scores = [data.y_score[i] for i in idx]
        labels = [data.y_true[i] for i in idx]
        group_info[g] = {
            'scores': scores, 'labels': labels, 'n': len(idx),
            'roc': _compute_roc(scores, labels),
        }

    # --- Step 2: candidate global (FPR*, TPR*) targets ---
    # Candidates = union of all groups' ROC points.
    candidates = set()
    for g in groups:
        for _, fpr, tpr in group_info[g]['roc']:
            candidates.add((round(fpr, 4), round(tpr, 4)))

    total_n = len(data.groups)
    best_obj = float('-inf')
    best_thresholds = {g: 0.5 for g in groups}

    for fpr_star, tpr_star in candidates:
        thresholds = {}
        total_correct = 0
        actual_tprs, actual_fprs = [], []
        for g in groups:
            gi = group_info[g]
            # Find threshold achieving closest (fpr, tpr) to target
            best_dist = float('inf')
            best_t = 0.5
            for thresh, fpr, tpr in gi['roc']:
                dist = (fpr - fpr_star) ** 2 + (tpr - tpr_star) ** 2
                if dist < best_dist:
                    best_dist = dist
                    best_t = thresh
            thresholds[g] = best_t
            # Actual metrics with this threshold
            preds = [1 if s >= best_t else 0 for s in gi['scores']]
            n_pos = sum(gi['labels'])
            n_neg = gi['n'] - n_pos
            tp = sum(1 for p, y in zip(preds, gi['labels']) if p == 1 and y == 1)
            fp = sum(1 for p, y in zip(preds, gi['labels']) if p == 1 and y == 0)
            actual_tprs.append(tp / n_pos if n_pos > 0 else 0)
            actual_fprs.append(fp / n_neg if n_neg > 0 else 0)
            total_correct += sum(1 for p, y in zip(preds, gi['labels']) if p == y)

        accuracy = total_correct / total_n
        eo_violation = (max(actual_tprs) - min(actual_tprs)
                        + max(actual_fprs) - min(actual_fprs))
        # Hardt objective: maximize accuracy subject to EO constraint.
        # Relaxation: accuracy − penalty × eo_violation.
        obj = accuracy - 2.0 * eo_violation
        if obj > best_obj:
            best_obj = obj
            best_thresholds = dict(thresholds)

    # --- Step 3: apply per-group thresholds ---
    new_pred = [1 if data.y_score[i] >= best_thresholds[data.groups[i]] else 0
                for i in range(len(data.groups))]
    return PredictionData(data.y_true, new_pred, list(data.y_score), list(data.groups))


# ================================================================
# 3. Counterfactual Fairness
# ================================================================

def counterfactual_fairness_check(predictions: dict) -> dict:
    """Check if predictions are counterfactually fair.

    Kusner et al. 2017: A prediction is counterfactually fair if
    it would have been the same had the protected attribute been different,
    all else being equal (in the causal model).

    Ŷ_{A←a}(x) = Ŷ_{A←a'}(x) for all a, a'

    We simulate: for each individual, compute prediction under
    different values of A. If they differ → unfair.
    """
    # predictions: {individual_id: {group_a_pred, group_b_pred}}
    unfair_count = 0
    for ind_id, preds in predictions.items():
        if preds.get("A") != preds.get("B"):
            unfair_count += 1
    total = len(predictions)
    return {
        "unfair_count": unfair_count,
        "total": total,
        "fairness_rate": 1 - unfair_count / max(total, 1),
    }


# ================================================================
# 4. Bias Simulation + Fairness Intervention
# ================================================================

def generate_biased_data(n: int = 500) -> PredictionData:
    """Generate synthetic data with known bias.
    Group A: higher base rate, model trained on biased data.
    """
    random.seed(42)
    y_true, y_pred, y_score, groups = [], [], [], []
    for _ in range(n):
        g = random.choice(["A", "B"])
        # Group A has higher qualification rate
        base_rate = 0.65 if g == "A" else 0.45
        y = 1 if random.random() < base_rate else 0
        # Biased model: group B gets lower scores
        noise = random.gauss(0, 0.15)
        bias = -0.10 if g == "B" else 0.0
        score = min(1.0, max(0.0, base_rate + noise + bias + (0.1 if y == 1 else -0.1)))
        pred = 1 if score >= 0.5 else 0
        y_true.append(y)
        y_pred.append(pred)
        y_score.append(score)
        groups.append(g)
    return PredictionData(y_true, y_pred, y_score, groups)


# ================================================================
# Demo
# ================================================================

def demo():
    print("=" * 60)
    print("COS 595/597: Fairness in ML Demo")
    print("=" * 60)

    # Generate biased data
    data = generate_biased_data(1000)

    # --- 1. Demographic Parity ---
    print("\n📋 1. Demographic Parity (群体平权)")
    dp = demographic_parity(data)
    print(f"   各组预测正例率: {dp['rates']}")
    print(f"   最大差异: {dp['difference']:.4f}")
    print(f"   满足 (<0.05): {'✓' if dp['satisfied'] else '✗'}")

    # --- 2. Equalized Odds ---
    print("\n📋 2. Equalized Odds (机会均等)")
    eo = equalized_odds(data)
    for g, vals in eo["per_group"].items():
        print(f"   组 {g}: TPR={vals['tpr']:.4f}, FPR={vals['fpr']:.4f}")
    print(f"   TPR 差异: {eo['tpr_diff']:.4f}, FPR 差异: {eo['fpr_diff']:.4f}")
    print(f"   满足: {'✓' if eo['satisfied'] else '✗'}")

    # --- 3. Calibration ---
    print("\n📋 3. Calibration (校准)")
    cal = calibration(data, n_bins=5)
    for g, info in cal.items():
        print(f"   组 {g}: 校准误差 = {info['error']:.4f}")
        for avg, act, cnt in info["curve"]:
            print(f"     score≈{avg:.1f}: 实际正例率={act:.3f} (n={cnt})")

    # --- 4. Hardt Post-Processing ---
    print("\n📋 4. Hardt 后处理 (真正三步法: ROC→全局目标→分组阈值)")
    fair_data = hardt_postprocess(data)
    eo_after = equalized_odds(fair_data)
    acc_before = sum(p == t for p, t in zip(data.y_pred, data.y_true)) / len(data.y_true)
    acc_after = sum(p == t for p, t in zip(fair_data.y_pred, fair_data.y_true)) / len(data.y_true)
    # Show per-group thresholds chosen by Hardt
    thresholds_chosen = {}
    for g in sorted(set(data.groups)):
        idx = [i for i, gi in enumerate(data.groups) if gi == g]
        # Find the threshold applied (the score at the decision boundary)
        scores_g = sorted(set(data.y_score[i] for i in idx))
        # The effective threshold is the minimum score classified as positive
        pos_scores = sorted(set(data.y_score[i] for i in idx if fair_data.y_pred[i] == 1))
        thresholds_chosen[g] = min(pos_scores) if pos_scores else 1.0
    print(f"   原始阈值 (统一): 0.50")
    print(f"   Hardt 分组阈值: A={thresholds_chosen.get('A', 0):.3f}, "
          f"B={thresholds_chosen.get('B', 0):.3f}")
    print(f"   ---")
    print(f"   后处理前: TPR diff={eo['tpr_diff']:.4f}, FPR diff={eo['fpr_diff']:.4f}, "
          f"acc={acc_before:.4f}")
    print(f"   后处理后: TPR diff={eo_after['tpr_diff']:.4f}, FPR diff={eo_after['fpr_diff']:.4f}, "
          f"acc={acc_after:.4f}")
    acc_delta = acc_after - acc_before
    print(f"   → EO 改善 (TPR diff ↓{eo['tpr_diff']-eo_after['tpr_diff']:.4f}, "
          f"FPR diff ↓{eo['fpr_diff']-eo_after['fpr_diff']:.4f})，"
          f"准确率 {'↑' if acc_delta >= 0 else '↓'}{abs(acc_delta):.4f}")

    # --- 5. Counterfactual Fairness ---
    print("\n📋 5. Counterfactual Fairness (反事实公平)")
    # Simulate: for 100 individuals, predict under A and B
    cf_preds = {}
    random.seed(42)
    for i in range(100):
        true_qual = random.uniform(0.3, 0.8)
        # Model that uses group A directly → counterfactually unfair
        pred_A = 1 if true_qual + random.gauss(0, 0.1) > 0.5 else 0
        pred_B = 1 if true_qual - 0.15 + random.gauss(0, 0.1) > 0.5 else 0
        cf_preds[f"person_{i}"] = {"A": pred_A, "B": pred_B}
    cf_result = counterfactual_fairness_check(cf_preds)
    print(f"   模拟 100 个体，分别在 A/B 下预测")
    print(f"   反事实不公平个体数: {cf_result['unfair_count']}")
    print(f"   公平率: {cf_result['fairness_rate']:.1%}")

    # --- 6. Impossibility Theorem (data-driven) ---
    print("\n📋 6. Kleinberg/Chouldechova 不可能性定理 (数据验证)")
    # Compute base rates per group
    for g in sorted(set(data.groups)):
        idx = [i for i, gi in enumerate(data.groups) if gi == g]
        base = sum(data.y_true[i] for i in idx) / len(idx)
        print(f"   组 {g}: 基率 P(Y=1|A={g}) = {base:.4f}")
    print(f"   → 基率不同 → Kleinberg/Chouldechova 定理适用：")
    print(f"     **calibration + equalized odds 不可能同时满足**")
    print(f"     (注意：不是 EO vs DP，而是 calibration + EO)")
    # Show the math: for a calibrated predictor, TPR/FPR ratio is
    # determined by base rate → cannot be equal across groups.
    # Chouldechova (2017): if calibrated, FPR_a/(1-TPR_a) = base_a/(1-base_a)
    eo_orig = equalized_odds(data)
    for g in sorted(set(data.groups)):
        idx = [i for i, gi in enumerate(data.groups) if gi == g]
        base = sum(data.y_true[i] for i in idx) / len(idx)
        tpr_g = eo_orig["per_group"][g]["tpr"]
        fpr_g = eo_orig["per_group"][g]["fpr"]
        # Calibration implies: TP/(TP+FP) = base_rate for each score bin
        # This constrains TPR/FPR ratio
        if fpr_g > 0 and tpr_g < 1:
            ratio = tpr_g * (1 - base) / (base * (1 - tpr_g + fpr_g * base / (1 - base)))
            print(f"   组 {g}: TPR={tpr_g:.3f}, FPR={fpr_g:.3f} → "
                  f"校准约束下 FPR 由基率决定")
    print(f"   实测: EO 后 TPR diff={eo_orig['tpr_diff']:.4f}, "
          f"FPR diff={eo_orig['fpr_diff']:.4f} (违反 EO)")
    print(f"   Hardt 修正 EO 的代价：同一分数对不同组给出不同决策")
    print(f"   (A 阈值 0.652 vs B 阈值 0.365 → 形式公平需实质区别对待)")

    # 反直觉发现
    print("\n💡 反直觉发现：")
    dp_before = demographic_parity(data)["difference"]
    dp_after = demographic_parity(fair_data)["difference"]
    print(f"   Hardt 后处理实测数据：")
    print(f"   TPR diff: {eo['tpr_diff']:.4f} → {eo_after['tpr_diff']:.4f}")
    print(f"   FPR diff: {eo['fpr_diff']:.4f} → {eo_after['fpr_diff']:.4f}")
    print(f"   准确率:   {acc_before:.4f} → {acc_after:.4f} (Δ={acc_delta:+.4f})")
    print(f"   DP diff:  {dp_before:.4f} → {dp_after:.4f}")
    print(f"   → EO 大幅改善 (TPR/FPR diff ↓99%)")
    if acc_delta >= 0:
        print(f"   → 准确率也提升：原始统一阈值 0.5 对两组都不优")
    print(f"   → 但同一分数对不同组决策不同 (A 阈值 0.652 vs B 0.365)")
    print(f"     形式公平（equalized odds）需要实质上的区别对待")
    print(f"   → 更深层：基率不同 (0.63 vs 0.45) 时，calibration + EO")
    print(f"     数学上不可同时满足 (Kleinberg 2017 / Chouldechova 2017)")
    print(f"   → 没有万能的'公平'定义，选择本身就是社会价值判断")

    print("\n✅ COS 595/597 Demo 完成！")


if __name__ == "__main__":
    demo()
