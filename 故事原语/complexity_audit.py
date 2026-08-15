#!/usr/bin/env python3
"""
complexity_audit.py — 把 work4ai 当复杂系统，实测 8 个健康指标。

这是 `复杂系统学-处理work4ai.md` 的工程化落地：
把「洞察（守临界/防孤儿/幂律）」变成「可测度（数字+判据）」。

用法:
    python3 故事原语/complexity_audit.py            # 扫描当前目录
    python3 故事原语/complexity_audit.py /path       # 扫描指定目录
    python3 故事原语/complexity_audit.py --json      # JSON 输出

8 个指标 (对应元文件 §4.1):
  1. 节点数 N          — 文件总数
  2. 度分布 γ          — 引用网络 power law 指数 (健康 2<γ<3)
  3. 聚类系数 C        — 模块化程度 (越高越模块化)
  4. 平均路径 L        — 小世界性 (越短越连通)
  5. 孤儿率            — 无入引用文件比例 (危险 if >30%)
  6. 视角多样性        — 每篇叠加视角数均值
  7. 雪崩分布 γ_aval   — git 改动行数 power law (SOC 标志)
  8. 温度 T            — 按月新文件数 (探索 vs 固化)
"""
import os, re, sys, math, json, subprocess, random
from pathlib import Path
from urllib.parse import unquote
from collections import defaultdict, Counter
from datetime import datetime

# ========== 1. 文件扫描 ==========
def scan_md_files(root):
    """所有 .md 文件 (相对路径作为节点 id)."""
    files = []
    for dp, dn, fn in os.walk(root):
        # 跳过 .git/node_modules/__pycache__
        dn[:] = [d for d in dn if d not in {'.git', 'node_modules', '__pycache__', '.venv'}]
        for f in fn:
            if f.endswith('.md'):
                full = Path(dp) / f
                try:
                    rel = str(full.relative_to(root))
                    files.append(rel)
                except ValueError:
                    pass
    return files

# ========== 2. 引用网络 ==========
LINK_RE = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')

def resolve_link(src_file, link, root):
    """解析 markdown 链接为目标文件相对路径. 返回 None 表示外部/无效."""
    if link.startswith(('http://', 'https://', 'mailto:', '#')):
        return None
    # 去掉锚点 + URL 解码（%20 空格等）
    link = unquote(link.split('#')[0].split(' ')[0])
    if not link: return None
    # 相对路径解析
    src_dir = Path(src_file).parent
    target = (src_dir / link).resolve()
    try:
        root_resolved = Path(root).resolve()
        rel = str(target.relative_to(root_resolved))
        return rel if Path(target).exists() else None
    except (ValueError, FileNotFoundError):
        return None

def build_citation_network(files, root):
    """建引用图: edges[src] = set(dst). 同时建反向 (入度)."""
    file_set = set(files)
    out_edges = defaultdict(set)
    in_edges = defaultdict(set)
    for f in files:
        try:
            content = (Path(root) / f).read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        for _, link in LINK_RE.findall(content):
            dst = resolve_link(f, link, root)
            if dst and dst in file_set and dst != f:
                out_edges[f].add(dst)
                in_edges[dst].add(f)
    return out_edges, in_edges

# ========== 3. Power Law 拟合 (Clauset 2009 离散 MLE 简化) ==========
def powerlaw_alpha(data, xmin=None):
    """离散幂律 MLE: alpha = 1 + n / sum(log(x_i / (xmin - 0.5)))."""
    data = [d for d in data if d > 0]
    if not data: return None
    if xmin is None:
        # 简化: 取 min (严谨版应扫所有 xmin 选 KS 最小)
        xmin = min(data)
    data = [d for d in data if d >= xmin]
    n = len(data)
    if n < 5: return None  # 样本太少
    denom = sum(math.log(d / (xmin - 0.5)) for d in data)
    if denom <= 0: return None
    return 1 + n / denom

# ========== 4. 聚类系数 (无向化) ==========
def clustering_coefficient(out_edges, sample_nodes=None):
    """平均聚类系数. 把有向图当无向处理."""
    # 构无向邻接
    adj = defaultdict(set)
    for src, dsts in out_edges.items():
        for d in dsts:
            adj[src].add(d)
            adj[d].add(src)
    nodes = sample_nodes if sample_nodes else list(adj.keys())
    if len(nodes) > 200:  # 大网络采样
        nodes = random.sample(nodes, 200)
    total, cnt = 0.0, 0
    for n in nodes:
        nb = adj.get(n, set())
        k = len(nb)
        if k < 2: continue
        links = 0
        nbl = list(nb)
        for i in range(len(nbl)):
            for j in range(i+1, len(nbl)):
                if nbl[j] in adj.get(nbl[i], set()):
                    links += 1
        total += (2 * links) / (k * (k - 1))
        cnt += 1
    return total / cnt if cnt > 0 else 0.0

# ========== 5. 平均路径 (BFS 采样) ==========
def average_path_length(out_edges, sample_size=80):
    adj = defaultdict(set)
    for src, dsts in out_edges.items():
        for d in dsts:
            adj[src].add(d)
            adj[d].add(src)
    nodes = list(adj.keys())
    if not nodes: return float('inf')
    if len(nodes) > sample_size:
        nodes = random.sample(nodes, sample_size)
    total, cnt = 0, 0
    for src in nodes:
        dist = {src: 0}
        queue = [src]
        while queue:
            cur = queue.pop(0)
            for nb in adj.get(cur, set()):
                if nb not in dist:
                    dist[nb] = dist[cur] + 1
                    queue.append(nb)
        for d in dist.values():
            if d > 0:
                total += d; cnt += 1
    return total / cnt if cnt > 0 else float('inf')

# ========== 6. 视角多样性 ==========
PERSPECTIVES = [
    'RL视角', '强化学习视角', '毛泽哲', '毛泽东哲学', '道教', '道家',
    '佛教', '禅宗', '阳明心学', '玄学', '墨家', '法家', '兵家',
    '纵横家', '阴阳家', '名家', '杂家', '农家',
]

def perspective_diversity(files, root):
    """每篇叠加视角数 (出现关键词计数)."""
    per_file = []
    for f in files:
        try:
            content = (Path(root) / f).read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        cnt = sum(1 for p in PERSPECTIVES if p in content)
        per_file.append(cnt)
    if not per_file: return 0, 0
    return sum(per_file) / len(per_file), max(per_file)

# ========== 7. Git 雪崩 ==========
def git_avalanches(root):
    """每次 commit 的总改动行数 (added+deleted)."""
    try:
        result = subprocess.run(
            ['git', 'log', '--numstat', '--format=__COMMIT__'],
            cwd=str(root), capture_output=True, text=True, timeout=60
        )
    except Exception:
        return []
    avalanches = []
    current = 0
    for line in result.stdout.split('\n'):
        if line.startswith('__COMMIT__'):
            if current > 0: avalanches.append(current)
            current = 0
        else:
            parts = line.split('\t')
            if len(parts) >= 2:
                a = int(parts[0]) if parts[0].isdigit() else 0
                d = int(parts[1]) if parts[1].isdigit() else 0
                current += a + d
    if current > 0: avalanches.append(current)
    return avalanches

# ========== 8. 温度 T (按月新文件) ==========
def temperature(files, root):
    """每月新文件数 = 探索温度."""
    by_month = Counter()
    for f in files:
        try:
            mtime = (Path(root) / f).stat().st_mtime
            ym = datetime.fromtimestamp(mtime).strftime('%Y-%m')
            by_month[ym] += 1
        except Exception:
            pass
    return dict(by_month)

# ========== 主审计 ==========
def audit(root, verbose=True):
    root = Path(root).resolve()
    random.seed(42)
    if verbose:
        print(f"🔍 扫描 {root} ...", file=sys.stderr)

    files = scan_md_files(root)
    N = len(files)
    out_edges, in_edges = build_citation_network(files, root)

    # 指标 1: 节点数
    n_nodes = N

    # 指标 2: 度分布 power law γ (用入度, 更有意义)
    in_degrees = [len(in_edges.get(f, set())) for f in files]
    in_degrees_nz = [d for d in in_degrees if d > 0]
    gamma = powerlaw_alpha(in_degrees_nz) if in_degrees_nz else None

    # 指标 3: 聚类系数
    C = clustering_coefficient(out_edges)

    # 指标 4: 平均路径
    L = average_path_length(out_edges)

    # 指标 5: 孤儿率
    orphans = sum(1 for f in files if len(in_edges.get(f, set())) == 0)
    orphan_rate = orphans / N if N > 0 else 0

    # 指标 6: 视角多样性
    avg_persp, max_persp = perspective_diversity(files, root)

    # 指标 7: 雪崩
    avalanches = git_avalanches(root)
    gamma_aval = powerlaw_alpha(avalanches) if avalanches else None

    # 指标 8: 温度
    temp_by_month = temperature(files, root)
    recent_months = sorted(temp_by_month.keys())[-3:]
    recent_T = sum(temp_by_month[m] for m in recent_months) / max(len(recent_months), 1)

    report = {
        'root': str(root),
        'timestamp': datetime.now().isoformat(timespec='seconds'),
        'metrics': {
            '1_节点数_N': n_nodes,
            '2_度分布_γ': round(gamma, 3) if gamma else None,
            '3_聚类系数_C': round(C, 4),
            '4_平均路径_L': round(L, 2) if L != float('inf') else None,
            '5_孤儿率': round(orphan_rate, 4),
            '6_视角多样性_均值': round(avg_persp, 3),
            '6_视角多样性_最大': max_persp,
            '7_雪崩_γ': round(gamma_aval, 3) if gamma_aval else None,
            '7_雪崩_总数': len(avalanches),
            '7_雪崩_最大': max(avalanches) if avalanches else 0,
            '8_温度T_近3月均值': round(recent_T, 1),
        },
        'diagnostics': {
            '引用边总数': sum(len(v) for v in out_edges.values()),
            '入度>0的文件': len(in_degrees_nz),
            '孤儿文件数': orphans,
            '总commit数': len(avalanches),
        }
    }

    # 健康判据
    health = []
    if gamma and 2 < gamma < 3:
        health.append(("✅ 度分布 γ∈(2,3)", f"无标度网络, γ={gamma:.2f}"))
    elif gamma:
        health.append(("⚠️ 度分布", f"γ={gamma:.2f} 偏离 (2,3), hub 结构异常"))
    else:
        health.append(("⚪ 度分布", "数据不足"))
    if C > 0.1:
        health.append(("✅ 聚类系数", f"C={C:.3f}, 模块化良好"))
    else:
        health.append(("⚠️ 聚类系数", f"C={C:.3f} 偏低, 网络松散"))
    if orphan_rate < 0.3:
        health.append(("✅ 孤儿率", f"{orphan_rate:.1%} < 30%, 健康"))
    else:
        health.append(("🔴 孤儿率", f"{orphan_rate:.1%} > 30%, 大量死亡内容"))
    if avg_persp > 0.5:
        health.append(("✅ 视角多样性", f"均值 {avg_persp:.2f}, 多视角叠加"))
    else:
        health.append(("🟡 视角多样性", f"均值 {avg_persp:.2f}, 视角单一"))
    if gamma_aval and 1.5 < gamma_aval < 3:
        health.append(("✅ 雪崩 SOC", f"γ={gamma_aval:.2f}, 近似自组织临界"))
    elif gamma_aval:
        health.append(("🟡 雪崩", f"γ={gamma_aval:.2f}, SOC 特征不明显"))
    report['health'] = health
    return report

def format_report(report):
    out = []
    out.append("=" * 60)
    out.append("🌐 work4ai 复杂系统健康审计")
    out.append("=" * 60)
    out.append(f"根目录: {report['root']}")
    out.append(f"时间: {report['timestamp']}")
    out.append("")
    out.append("─── 8 大健康指标 ───")
    for k, v in report['metrics'].items():
        out.append(f"  {k:25s} : {v}")
    out.append("")
    out.append("─── 诊断 ───")
    for k, v in report['diagnostics'].items():
        out.append(f"  {k:15s} : {v}")
    out.append("")
    out.append("─── 健康判据 ───")
    for status, detail in report['health']:
        out.append(f"  {status:20s} {detail}")
    out.append("")
    out.append("─── 月度温度 (新文件数) ───")
    # 已在 metrics, 这里展示趋势省略
    out.append("  (详见 metrics.8_温度T_近3月均值)")
    out.append("=" * 60)
    return "\n".join(out)


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else '.'
    as_json = '--json' in sys.argv
    report = audit(root, verbose=not as_json)
    if as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(format_report(report))
