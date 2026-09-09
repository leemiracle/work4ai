# Black-Scholes 与风险中性定价

> 期权定价的数学革命——1997 Nobel 经济学奖。

## Black-Scholes PDE
∂V/∂t + ½σ²S²∂²V/∂S² + rS∂V/∂S - rV = 0

推导：Δ-对冲消除风险 → 无风险组合 → 无套利 → 收益率=r

## Greeks（风险敏感度）
- Δ(delta) = ∂V/∂S（价格敏感度，对冲比率）
- Γ(gamma) = ∂²V/∂S²（凸性，对冲调整频率）
- Θ(theta) = ∂V/∂t（时间衰减）
- Vega = ∂V/∂σ（波动率敏感度）
- ρ(rho) = ∂V/∂r（利率敏感度）

## 风险中性测度
用 Itô 引理 + Girsanov 定理变换测度：
真实测度 P → 风险中性 Q（漂移 r）
V = e^{-rT} E^Q[Payoff]

→ 资产定价基本定理：无套利 ⟺ 存在等价鞅测度

## 局限与扩展
- 常数σ假设太强 → Local Vol(Dupire) / Stochastic Vol(Heston)
- 跳跃被忽略 → Merton Jump-Diffusion / Variance Gamma
- 流动性被忽略 → 交易成本模型

## 关联
- [百科-16-金融数学](../百科-16-金融数学.md)
- [代码库 05-期权](../../15-applications/代码库/05-蒙特卡洛_期权定价.py)
- [代码库 26-SDE](../../15-applications/代码库/26-随机微分方程_SDE.py)
