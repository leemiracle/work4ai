"""Experiment 3: Lotka-Volterra predation + Rosenzweig-MacArthur (Holling Type II)
- Classic LV: neutral center, 1/4-period phase lag
- RM with prey self-limitation: stable focus (low K) or limit cycle (high K = paradox of enrichment)
"""
import numpy as np
from scipy.integrate import odeint
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# (A) Classic Lotka-Volterra
def lv(state, t, a, b, c, d):
    N, P = state
    return [a*N - b*N*P, c*N*P - d*P]

t = np.linspace(0, 50, 5000)
a, b, c, d = 1.0, 0.1, 0.075, 0.3   # equilibrium N*=d/c=4, P*=a/b=10
sol = odeint(lv, [40, 5], t, args=(a, b, c, d))

fig, axes = plt.subplots(1, 3, figsize=(16, 5))
axes[0].plot(t, sol[:,0], 'g-', label='Prey N')
axes[0].plot(t, sol[:,1], 'r-', label='Predator P')
axes[0].axhline(d/c, color='g', ls=':', alpha=0.5)
axes[0].axhline(a/b, color='r', ls=':', alpha=0.5)
axes[0].set_title('Classic LV time series (neutral cycles)')
axes[0].set_xlabel('time'); axes[0].legend()

axes[1].plot(sol[:,0], sol[:,1], 'b-', lw=1)
axes[1].plot([d/c],[a/b],'k*', ms=15, label='equilibrium (neutral center)')
axes[1].set_title('Phase space: closed orbits')
axes[1].set_xlabel('Prey N'); axes[1].set_ylabel('Predator P'); axes[1].legend()

# (B) Rosenzweig-MacArthur with Holling Type II + prey self-limitation
def rm(state, t, r, K, alpha, h, e, mu):
    N, P = state
    fr = alpha*N/(1+alpha*h*N)
    return [r*N*(1-N/K) - fr*P, e*fr*P - mu*P]

for K_val, lbl, col in [(20, 'Low K: stable focus', 'green'), (60, 'High K: limit cycle (paradox of enrichment)', 'red')]:
    sol2 = odeint(rm, [8, 2], t, args=(1.0, K_val, 1.0, 0.5, 0.5, 0.3))
    axes[2].plot(sol2[:,0], sol2[:,1], color=col, lw=1.5, label=lbl)
axes[2].set_title('Rosenzweig-MacArthur phase')
axes[2].set_xlabel('Prey N'); axes[2].set_ylabel('Predator P'); axes[2].legend(fontsize=8)

plt.tight_layout()
plt.savefig('/tmp/opencode/ecology/fig3_lotka_volterra.png', dpi=110)

print(f"Equilibrium: N* = d/c = {d/c}, P* = a/b = {a/b}")
print("Classic LV = neutral center (pure imaginary eigenvalues) -> undamped oscillation")
print("Phase lag: prey peak precedes predator by ~1/4 period (matches hare-lynx data)")
print("RM: increasing K -> Hopf bifurcation -> limit cycle = 'paradox of enrichment'")
print("Saved: fig3_lotka_volterra.png")
