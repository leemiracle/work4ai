#!/usr/bin/env python3
"""
story_map_generator.py — 扫描 work4ai 顶层目录, 生成「故事地图」markdown.

用法:
    python3 story_map_generator.py /path/to/work4ai > 故事地图.md
    python3 story_map_generator.py /path/to/work4ai --json > story_map.json

它会:
  1. 列出顶层每个目录
  2. 探测每个目录的故事原语类型 (讲透五幕/精读四幕/周时间线/主题矩阵/史诗编年)
     - 启发式: 名字含"讲透" -> 讲透五幕; 含"精读" -> 精读四幕;
              含"learning"且子目录week* -> 周时间线; 含"cs-projects" -> 主题矩阵;
              含"故事集" -> 史诗编年
  3. 探测完成度: 有 COMPLETION_REPORT.md -> done; 有 README.md -> in_progress; 都无 -> empty
  4. 输出按家族分组的 markdown 表格
"""
import os, sys, json, re
from pathlib import Path

FAMILIES = {
    "讲透·技术核心": ["讲透NLP", "讲透PyTorch", "讲透Transformer", "讲透RL",
                    "讲透Agent", "讲透模型", "讲透基础模型", "讲透CV", "讲透多模态"],
    "讲透·数学理论": ["讲透实分析", "讲透优化理论", "讲透高维概率", "讲透代数拓扑",
                    "讲透群论", "讲透数值线代", "讲透Artin", "讲透Lean4"],
    "CS名校纵深": ["berkeley-cs-projects", "cambridge-cs-projects", "cmu-cs-projects",
                  "eth-cs-projects", "mit-cs-projects", "oxford-cs-projects",
                  "princeton-cs-projects", "stanford-cs-projects", "toronto-cs-projects"],
    "课程精读": ["Karpathy经典代码精读", "cs61a-learning", "cs224n"],
    "故事/方法论元层": ["故事化学习法", "知识故事集", "视角库", "费曼学习法", "故事原语"],
    "Agent能力宇宙(新)": ["universe-memory", "universe-codegen", "universe-collab",
                       "universe-swarm", "universe-predictive", "universe-cache",
                       "universe-learning", "universe-cv", "universe-multimodal"],
}


def detect_primitive(name: str, subdirs, files) -> str:
    if "讲透" in name or name.startswith("讲透"):
        return "讲透五幕"
    if "精读" in name:
        return "精读四幕"
    if "cs-projects" in name:
        return "主题矩阵"
    if "learning" in name.lower():
        if any(re.match(r"week\d", s.lower()) for s in subdirs):
            return "周时间线"
        return "主题矩阵"
    if "故事集" in name or "story" in name.lower():
        return "史诗编年"
    if name.startswith("universe-"):
        return "讲透五幕"
    return "混合"


def detect_completion(d: Path) -> str:
    if (d / "COMPLETION_REPORT.md").exists():
        return "done"
    if (d / "README.md").exists():
        # count files
        try:
            n = sum(1 for _ in d.rglob("*") if _.is_file())
        except Exception:
            n = 0
        return "in_progress" if n > 2 else "empty"
    return "empty"


def count_files(d: Path) -> int:
    try:
        return sum(1 for _ in d.rglob("*") if _.is_file())
    except Exception:
        return 0


def scan(root: Path):
    result = {}
    for entry in sorted(root.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith(".") or entry.name in {"node_modules", "__pycache__"}:
            continue
        try:
            subdirs = [s.name for s in entry.iterdir() if s.is_dir()]
            files = [f.name for f in entry.iterdir() if f.is_file()]
        except Exception:
            subdirs, files = [], []
        result[entry.name] = {
            "primitive": detect_primitive(entry.name, subdirs, files),
            "completion": detect_completion(entry),
            "files": count_files(entry),
        }
    return result


def to_markdown(data, root):
    out = ["# 🗺️ work4ai 故事地图\n",
           f"> 自动生成自 `{root}` · 共 {len(data)} 个宇宙\n",
           "## 📊 完成度总览\n"]
    done = sum(1 for v in data.values() if v["completion"] == "done")
    ip = sum(1 for v in data.values() if v["completion"] == "in_progress")
    em = sum(1 for v in data.values() if v["completion"] == "empty")
    out.append(f"- ✅ done: {done}  ·  🟡 in_progress: {ip}  ·  ⚪ empty: {em}\n")

    # classify each dir into a family (or "其他")
    name_to_family = {}
    for fam, members in FAMILIES.items():
        for m in members:
            name_to_family[m] = fam

    for fam, members in FAMILIES.items():
        present = [m for m in members if m in data]
        if not present:
            continue
        out.append(f"\n## {fam}\n")
        out.append("| 宇宙 | 原语 | 完成度 | 文件数 | 下一步故事卡 |")
        out.append("|---|---|---|---|---|")
        for m in present:
            v = data[m]
            comp = {"done": "✅", "in_progress": "🟡", "empty": "⚪"}[v["completion"]]
            hook = {
                "done": "归档",
                "in_progress": "继续填卡",
                "empty": "起 README+首卡",
            }[v["completion"]]
            out.append(f"| `{m}` | {v['primitive']} | {comp} | {v['files']} | {hook} |")

    # 未归类
    others = [n for n in data if n not in name_to_family]
    if others:
        out.append("\n## 其他\n")
        out.append("| 宇宙 | 原语 | 完成度 | 文件数 |")
        out.append("|---|---|---|---|")
        for n in others:
            v = data[n]
            comp = {"done": "✅", "in_progress": "🟡", "empty": "⚪"}[v["completion"]]
            out.append(f"| `{n}` | {v['primitive']} | {comp} | {v['files']} |")
    return "\n".join(out) + "\n"


def main():
    if len(sys.argv) < 2:
        print("用法: python3 story_map_generator.py /path/to/work4ai [--json]")
        sys.exit(1)
    root = Path(sys.argv[1])
    if not root.exists():
        print(f"路径不存在: {root}", file=sys.stderr)
        sys.exit(1)
    data = scan(root)
    if "--json" in sys.argv:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(to_markdown(data, root))


if __name__ == "__main__":
    main()
