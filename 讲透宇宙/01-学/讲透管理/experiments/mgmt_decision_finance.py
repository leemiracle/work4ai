"""管理学 - 决策与财务量化模型验证"""
import numpy as np
from scipy.stats import norm

print("=" * 60)
print("1. 期望货币价值 EMV (决策树)")
print("=" * 60)
# 建大厂/小厂，需求高(0.6)/低(0.4)
emv_big = 0.6 * 200 + 0.4 * (-20)
emv_small = 0.6 * 60 + 0.4 * 20
print(f"  EMV(大厂) = {emv_big} 万")
print(f"  EMV(小厂) = {emv_small} 万")
print(f"  -> 决策: {'建大厂' if emv_big > emv_small else '建小厂'}")

print("\n" + "=" * 60)
print("2. 完美信息期望价值 EVPI")
print("=" * 60)
ev_certain = 0.6 * 200 + 0.4 * 20  # 知道需求后总能选最优
evpi = ev_certain - max(emv_big, emv_small)
print(f"  确定情况期望 = {ev_certain} 万，EMV = {max(emv_big, emv_small)} 万")
print(f"  -> EVPI = {evpi} 万 (你最多愿为情报付这么多)")

print("\n" + "=" * 60)
print("3. 贝叶斯后验 (市场调研更新需求概率)")
print("=" * 60)
prior_high = 0.6
p_pred_high_given_high = 0.9   # 灵敏度
p_pred_low_given_low = 0.8     # 特异度
p_pred_high = (p_pred_high_given_high * prior_high
               + (1 - p_pred_low_given_low) * (1 - prior_high))
post_high = p_pred_high_given_high * prior_high / p_pred_high
print(f"  P(高需求) = {prior_high} -> P(高需求|预测高) = {post_high:.4f}")

print("\n" + "=" * 60)
print("4. 层次分析法 AHP (特征向量法 + 一致性检验)")
print("=" * 60)
# 准则两两比较: 成本 / 质量 / 速度
A = np.array([
    [1,   1/3, 1/5],
    [3,   1,   1/3],
    [5,   3,   1  ],
], dtype=float)
eigval, eigvec = np.linalg.eig(A)
idx = np.argmax(eigval.real)
w = eigvec[:, idx].real
w = w / w.sum()
lambda_max = eigval[idx].real
n = A.shape[0]
CI = (lambda_max - n) / (n - 1)
RI_table = {1: 0, 2: 0, 3: 0.58, 4: 0.9, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45}
RI = RI_table[n]
CR = CI / RI if RI > 0 else 0
print(f"  权重 [成本, 质量, 速度] = {w.round(4)}")
print(f"  λmax = {lambda_max:.4f}, CI = {CI:.4f}, CR = {CR:.4f}")
print(f"  -> {'一致' if CR < 0.1 else '不一致，需修订判断'} (CR<0.1)")

print("\n" + "=" * 60)
print("5. 净现值 NPV / 内部收益率 IRR")
print("=" * 60)
cf = np.array([-1000, 300, 400, 500, 600])
r = 0.10
npv = sum(c / (1 + r) ** t for t, c in enumerate(cf))
# IRR: 令 NPV=0 的 r
lo, hi = -0.99, 5.0
for _ in range(100):
    mid = (lo + hi) / 2
    val = sum(c / (1 + mid) ** t for t, c in enumerate(cf))
    if val > 0:
        lo = mid
    else:
        hi = mid
irr = (lo + hi) / 2
print(f"  现金流 {list(cf)}, 折现率 r={r}")
print(f"  NPV = {npv:.2f}, IRR = {irr:.4f}  -> {'接受' if npv > 0 else '拒绝'}")

print("\n" + "=" * 60)
print("6. 资本资产定价模型 CAPM")
print("=" * 60)
rf, beta, erm = 0.03, 1.2, 0.08
ke = rf + beta * (erm - rf)
print(f"  rf={rf}, β={beta}, E(Rm)={erm} -> 权益成本 ke = {ke:.4f}")

print("\n" + "=" * 60)
print("7. Black-Scholes 期权定价 (实物期权/战略柔性)")
print("=" * 60)
S, K, T, sigma = 100, 100, 1, 0.2
d1 = (np.log(S / K) + (rf + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
d2 = d1 - sigma * np.sqrt(T)
call = S * norm.cdf(d1) - K * np.exp(-rf * T) * norm.cdf(d2)
put = K * np.exp(-rf * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
print(f"  S={S}, K={K}, T={T}, σ={sigma} -> Call = {call:.4f}, Put = {put:.4f}")
