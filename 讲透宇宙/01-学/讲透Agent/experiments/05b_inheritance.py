"""
实验 05b — L7 补缺: 继承权政策谱系 — 隔离"探索权"这单一变量
对应: 自进化2.0-整体叠加.md §7 自查表 L7 行 · 复用 [05_selfevolve](./05_selfevolve.py) 的全部机制

设计: 三种政策只有"父代怎么选"不同, 其余全部钉死 (同一存档/同一归因导向突变/同一预算):
  argmax — 父代 = 历史最优 (继承权最集中; 等价于主实验的 greedy, 但存档照常维护以隔离变量)
  prop   — 分数比例采样 (s/smax)^2 / (1+children) (继承权中间档; 主实验调参实录中的"修复前"版本)
  bins   — 档位采样 = MAP-Elites 式适应度共享 (继承权最分散; 主实验最终版 se05.pick_parent)

预期梯度: argmax (0/30) < prop (~9/30) < bins (~15/30) — 继承权越分散, 垫脚石越活得下去。

实测结论 (30 种子 × 80 代 × 每代 5 变异, 与主实验同预算, 2026-08-24):
  argmax  登顶  0/30  (mean 0.746, 焊死局部峰)
  prop    登顶 14/30  (mean 0.781)   vs argmax p<0.0001
  bins    登顶 22/30  (mean 0.798)   vs prop p=0.0702 (边缘), vs argmax p<0.0001
  ★ 单调梯度成立: 继承权越分散 (argmax < prop < bins), 登顶率越高 (0 < 14 < 22)
  ★ 不变量: argmax 在任何种子流下恒 0 (主实验与本实验双确认);
    bins 绝对值随种子流波动 (主实验 15/30 vs 此处 22/30) — 方向稳定, 幅度有噪声

跑法: python3 -u 05b_inheritance.py   (产物: 05b_inheritance.png)
"""
import importlib.util, math, os, random
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

matplotlib.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

def P(*a): print(*a, flush=True)

# ---- 复用主实验的全部机制 (模块名以数字开头, importlib 加载) ----
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("se05", os.path.join(HERE, "05_selfevolve.py"))
se05 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(se05)          # __name__ != "__main__" → 只加载定义不跑主流程

def pick_argmax(archive, children):
    """政策A: 只有历史最优有继承权 (其余变体只是看客)"""
    return max(range(len(archive)), key=lambda i: archive[i][1])

def pick_prop(archive, children):
    """政策B: 分数比例 + 生过抑育 (主实验'档位修复前'的版本) — 少数高分个体仍可霸占采样"""
    smax = max(s for _, s in archive) + 1e-9
    wts = [((s / smax) ** 2) / (1 + children[i]) for i, (_, s) in enumerate(archive)]
    x, acc = random.random() * sum(wts), 0.0
    for i, w in enumerate(wts):
        acc += w
        if x <= acc: return i
    return len(archive) - 1

POLICIES = [("argmax", pick_argmax), ("prop", pick_prop), ("bins", se05.pick_parent)]

def run(policy_fn, gens=80, litter=5):
    shared = [0.75 + random.gauss(0, 0.02) for _ in range(6)]
    g0 = [(True, shared[r]) for r in range(6)] + [(True, 0.5), (True, 0.72)]
    archive, children = [(g0, se05.score(g0))], [0]
    best = archive[0][1]
    for _ in range(gens):
        for _ in range(litter):
            pi = policy_fn(archive, children)
            parent, sp = archive[pi]; children[pi] += 1
            child = se05.mutate(parent, sp, "informed")
            sc = se05.score(child)
            archive.append((child, sc)); children.append(0)
            best = max(best, sc)
    return best

def perm_test(x, y, n=5000):
    obs = sum(x) / len(x) - sum(y) / len(y)
    allv = list(x) + list(y); k = len(x); cnt = 0
    for _ in range(n):
        random.shuffle(allv)
        d = sum(allv[:k]) / k - sum(allv[k:]) / len(allv[k:])
        if abs(d) >= abs(obs) - 1e-12: cnt += 1
    return obs, cnt / n

if __name__ == "__main__":
    SEEDS, GENS = 30, 80
    thr = sum(se05.probe_landscape()[::2]) / 2          # (局部峰A + 全局峰B)/2
    P(f"判峰阈值 thr = {thr:.3f} (复用主实验景观: 局部峰A {se05.probe_landscape()[0]:.3f} / 全局峰B {se05.probe_landscape()[2]:.3f})")
    finals, hits = {}, {}
    for name, fn in POLICIES:
        fs = []
        for seed in range(SEEDS):
            random.seed(90210 * seed + 7 + hash(name) % 97)   # 每政策独立种子流
            fs.append(run(fn, gens=GENS))
        finals[name] = fs
        hits[name] = sum(1 for b in fs if b > thr)
        P(f"  {name:7s} 登顶 {hits[name]:2d}/{SEEDS}   终代最优 mean={sum(fs)/len(fs):.3f}  min={min(fs):.3f}  max={max(fs):.3f}")
    P("-" * 70)
    for a, b in [("bins", "prop"), ("prop", "argmax"), ("bins", "argmax")]:
        d, p = perm_test(finals[a], finals[b])
        P(f"  置换检验(5000): {a:7s} vs {b:7s}  Δ={d:+.3f}  p={p:.4f}")

    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    names = [n for n, _ in POLICIES]
    desc = {"argmax": "argmax\n(只有最优有继承权)", "prop": "prop 比例采样\n(高分个体霸占)", "bins": "bins 档位采样\n(MAP-Elites 适应度共享)"}
    colors = {"argmax": "#d62728", "prop": "#ff9f1c", "bins": "#1f77b4"}
    bars = ax.bar([desc[n] for n in names], [hits[n] / SEEDS for n in names], color=[colors[n] for n in names])
    for b_, n in zip(bars, names):
        ax.text(b_.get_x() + b_.get_width() / 2, b_.get_height() + 0.02, f"{hits[n]}/{SEEDS}", ha="center", fontsize=11)
    ax.set_ylabel("登顶全局峰 B 的种子比例"); ax.set_ylim(0, 0.75)
    ax.set_title("继承权政策谱系: 只换'父代怎么选'这一个变量\n(存档/归因突变/预算全部钉死, 30 种子 × 80 代)")
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "05b_inheritance.png"), dpi=130)
    P("\n图已保存: 05b_inheritance.png")

    P("=" * 70)
    P("反直觉点")
    P("""
- 存档的'存在'与存档的'被使用'是两回事: argmax 政策下存档照常维护, 但低分变体
  从未当过父代 → 登顶 0 — 存档只有配合分散的继承权才产生价值.

- prop→bins 的增量来自'同分不霸占': 比例采样下, 一群分数相同的中性变体每人都
  分到采样权, 垫脚石(深谷变体)被稀释; 档位采样按分数档竞争、档内均匀, 深谷档
  整体获得与人口无关的固定话语权 — 适应度共享不是锦上添花, 是探索权的再分配.

- 工程映射: 这就是'组织谁有资格立项'的问题 — 只许冠军团队做新项目(argmax)会
  错过所有需要穿过低谷的转型; 按过去业绩分配资源(prop)会被中性大群稀释;
  按赛道设预算(bins)才能保住冷门方向的存活权.
""")
