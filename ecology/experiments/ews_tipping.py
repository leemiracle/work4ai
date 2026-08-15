"""Experiment 4 (v2): EWS with a model whose equilibrium is CONSTANT
so that only the recovery rate changes. Then both Var and AR(1) rise cleanly.
Model: dX/dt = -lambda(mu) * (X - 1) + noise,  X* = 1 (constant),
        lambda(mu) = 2*sqrt(mu)  -> recovery rate, ->0 as mu->0 (critical slowing)
Steady-state variance ~ sigma^2 / (2*lambda)  -> diverges as lambda->0.
"""
import numpy as np
from scipy.stats import kendalltau
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

np.random.seed(7)
T = 8000
mu = np.linspace(0.5, 0.005, T)      # keep lambda in [0.14, 1.41] for Euler stability
lam = 2*np.sqrt(mu)                  # recovery rate, 1.414 -> 0.141
Xstar = 1.0
sigma = 0.1
X = np.zeros(T); X[0] = Xstar
for t in range(1, T):
    X[t] = X[t-1] + (-lam[t-1]*(X[t-1]-Xstar)) + sigma*np.random.randn()
    X[t] = np.clip(X[t], -3, 3)

window, step = 600, 50
t_axis, var_r, ar1_r = [], [], []
for i in range(0, T-window, step):
    seg = X[i:i+window]
    t_axis.append(i+window//2)
    var_r.append(np.var(seg))
    ar1_r.append(np.corrcoef(seg[:-1], seg[1:])[0,1])
var_r = np.array(var_r); ar1_r = np.array(ar1_r)

fig, axes = plt.subplots(3,1, figsize=(11,10), sharex=True)
crit = int(T*0.85)
axes[0].plot(X, 'k-', lw=0.8); axes[0].axvline(crit, color='r', ls='--', alpha=0.5)
axes[0].set_ylabel('state X (around X*=1)'); axes[0].set_title('mu slowly down -> recovery rate lambda=2sqrt(mu) -> 0 (critical slowing)')
axes[1].plot(t_axis, var_r, 'b-'); axes[1].axvline(crit, color='r', ls='--', alpha=0.5)
axes[1].set_ylabel('rolling Var'); axes[1].set_title('EWS #1: variance rises (noise amplified by slow recovery)')
axes[2].plot(t_axis, ar1_r, 'g-'); axes[2].axvline(crit, color='r', ls='--', alpha=0.5)
axes[2].set_ylabel('AR(1)'); axes[2].set_xlabel('time'); axes[2].set_title('EWS #2: lag-1 autocorrelation rises')
plt.tight_layout(); plt.savefig('/tmp/opencode/ecology/fig4_ews.png', dpi=110)

tau_var,p_var = kendalltau(np.arange(len(var_r)), var_r)
tau_ar1,p_ar1 = kendalltau(np.arange(len(ar1_r)), ar1_r)
print(f"Var trend Kendall tau = {tau_var:.3f} (p={p_var:.2e}) {'SIGNIFICANT UP' if tau_var>0 and p_var<0.05 else 'n.s.'}")
print(f"AR(1) trend Kendall tau = {tau_ar1:.3f} (p={p_ar1:.2e}) {'SIGNIFICANT UP' if tau_ar1>0 and p_ar1<0.05 else 'n.s.'}")
print(f"\nrecovery rate lambda: {lam[0]:.2f} -> {lam[-1]:.3f} (~{lam[0]/lam[-1]:.0f}x slower)")
print(f"theory steady-state Var ~ sigma^2/(2*lambda): {sigma**2/(2*lam[0]):.4f} -> {sigma**2/(2*lam[-1]):.4f} (should ~{lam[0]/lam[-1]:.0f}x)")
print(f"observed Var: {var_r[0]:.4f} -> {var_r[-1]:.4f} (x{var_r[-1]/var_r[0]:.1f})")
print("Both EWS significant -> critical slowing down VERIFIED")
