"""
E09 解答 · "物理一致性 benchmark" 最小可行原型
================================================
[08-不足] 指出: 物理违反几乎无自动指标。本脚本实现一个可运行的
原型 pipeline:

  prompt(含可计算物理) → 轨迹(模拟"生成模型的输出") → 抛物线拟合
  → 引力一致性检验 → 碰撞/穿墙检验 → 打分

用合成轨迹代替真实视频(检测端用目标检测+跟踪可替换)。

运行: python3 E09_physics_bench.py    # 约 3 秒
输出: E09_physics_bench.png
"""
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Noto Sans SC', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# ---------- 1. 三个"生成模型输出"(合成) ----------
def gen_physics_ok(n=40, g=9.8, noise=0.15, v0=(6, 9), seed=0):
    """抛体运动: x=v0x t, y=y0+v0y t-½gt² —— 物理正确"""
    rng = np.random.default_rng(seed)
    t = np.linspace(0, 1.8, n)
    x = v0[0] * t + rng.normal(0, noise, n)
    y = 2 + v0[1] * t - 0.5 * g * t ** 2 + rng.normal(0, noise, n)
    return t, x, y

def gen_physics_bad_g(n=40, seed=1):
    """重力错误: g 随时间漂移(前半 9.8 后半 2)——常见生成错误"""
    t, x, y = gen_physics_ok(n=n, seed=seed)
    y[n // 2:] += 0.5 * 7.8 * (t[n // 2:] - t[n // 2]) ** 2  # 后半段"漂浮"
    return t, x, y

def gen_wall_violation(n=40, seed=2):
    """穿墙: 轨迹直接穿过 x=8 处的墙(碰撞后应反弹/停止)"""
    t, x, y = gen_physics_ok(n=n, v0=(8, 9), seed=seed)
    return t, x, y  # 匀速穿过墙体


# ---------- 2. 检验器 ----------
def check_gravity(t, y, g_true=9.8, tol=0.25):
    """拟合 y = a t²+bt+c, 检验 a ≈ -g/2。返回 (估计g, 通过?)"""
    A = np.stack([t ** 2, t, np.ones_like(t)], 1)
    a, b, c = np.linalg.lstsq(A, y, rcond=None)[0]
    g_est = -2 * a
    return g_est, abs(g_est - g_true) / g_true < tol

def check_wall(t, x, wall_x, min_beyond=3, restitution=0.5):
    """检验穿墙: 需持续越界(滤噪)才算真穿过; 穿过后应反弹(速度反号且不超过恢复系数倍)。"""
    beyond = x > wall_x
    # 找"持续越界"的起点(单点越界视为噪声)
    hits = [i for i in range(len(x) - min_beyond)
            if not beyond[max(i - 1, 0)] and all(beyond[i:i + min_beyond])]
    if not hits:
        return True, "未碰墙(或仅噪声越界)"
    i = hits[0]
    v_before = (x[i] - x[max(i - 3, 0)]) / (t[i] - t[max(i - 3, 0)] + 1e-9)
    j = min(i + 4, len(t) - 1)
    v_after = (x[j] - x[i + 1]) / (t[j] - t[i + 1] + 1e-9)
    ok = (v_after < 0) and (abs(v_after) <= abs(v_before) * restitution + 1.5)
    return ok, f"穿墙@t={t[i]:.2f} v:{v_before:.1f}→{v_after:.1f} (未反弹)"


def physics_score(cases):
    """总分 = 各检验通过率的加权平均 (重力0.6 + 碰撞0.4)。cases: (t,x,y,wall_x)"""
    g_pass, w_pass = [], []
    for (t, x, y, wall_x) in cases:
        _, gok = check_gravity(t, y)
        wok, _ = check_wall(t, x, wall_x)
        g_pass.append(gok); w_pass.append(wok)
    return 0.6 * np.mean(g_pass) + 0.4 * np.mean(w_pass), g_pass, w_pass


# ---------- 3. 跑三个案例 (每个案例自带墙位置) ----------
# 物理正确/重力漂移案例: v0x=6, 最远 x≈10.8 → 墙放 13(不该被碰到)
# 穿墙案例: v0x=8, 穿过 x=8 的墙
cases = [("物理正确(墙在远处)", gen_physics_ok() + (13.0,)),
         ("重力漂移(后半段漂浮)", gen_physics_bad_g() + (13.0,)),
         ("穿墙(无碰撞)", gen_wall_violation() + (8.0,))]

print(f"{'案例':<20}{'g估计':>8}{'重力检验':>8}{'碰撞检验':>8}")
for name, (t, x, y, wall_x) in cases:
    g_est, gok = check_gravity(t, y)
    wok, wmsg = check_wall(t, x, wall_x)
    print(f"{name:<20}{g_est:>8.2f}{'✅' if gok else '❌':>7}{'✅' if wok else '❌':>7}   ({wmsg})")

score, gp, wp = physics_score([c[1] for c in cases])
print(f"\n[物理一致性总分] {score:.2f} / 1.00")

# ---------- 4. 画图 ----------
fig, axes = plt.subplots(1, 3, figsize=(12.5, 3.8))
for ax, (name, (t, x, y, wall_x)) in zip(axes, cases):
    g_est, gok = check_gravity(t, y)
    wok, _ = check_wall(t, x, wall_x)
    ax.plot(x, y, 'o-', ms=3)
    ax.axvline(wall_x, color='r', ls='--', lw=1, alpha=0.7, label=f'墙 x={wall_x:.0f}')
    ax.set_title(f"{name}\ng_est={g_est:.1f} {'✅' if gok else '❌'}  碰撞 {'✅' if wok else '❌'}", fontsize=10)
    ax.set_xlabel('x'); ax.set_ylabel('y'); ax.legend(fontsize=8)
plt.suptitle('E09 · 物理一致性 benchmark 原型: 拟合+检验+打分', fontweight='bold')
plt.tight_layout(); plt.savefig('E09_physics_bench.png', dpi=110, bbox_inches='tight')
print("\n[输出] E09_physics_bench.png")
print("  扩展到真实模型: 用 YOLO+DeepSORT 替换合成轨迹, 其余 pipeline 不变。")
