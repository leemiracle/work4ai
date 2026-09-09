#!/usr/bin/env python3
"""
by_topic.py — 按学科主题快速过滤 csdiy 资源

用法:
  python3 tools/by_topic.py                 # 列出所有主题
  python3 tools/by_topic.py os              # 操作系统主题的全部资源
  python3 tools/by_topic.py llm             # LLM 主题(含 22 篇源码精读 + tinyllm/tinyrag)
  python3 tools/by_topic.py network         # 网络主题
  python3 tools/by_topic.py db              # 数据库主题
  python3 tools/by_topic.py ai              # AI/ML/DL/LLM
  python3 tools/by_topic.py distributed     # 分布式系统
  python3 tools/by_topic.py compiler        # 编译/语言
  python3 tools/by_topic.py security        # 安全
  python3 tools/by_topic.py --list          # 列出所有主题
  python3 tools/by_topic.py --all           # 全部主题概览
"""
import os, sys, glob, json
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 16 个主题及其资源映射
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TOPICS = {
    "intro": {
        "name": "1️⃣ 计算机入门 / 编程基础",
        "notes": ["csapp-程序员视角.md"],  # Ch2-3
        "source_reading": [],
        "cheatsheets": ["python-场景速查.md"],
        "projects": ["tinyjson", "tinycompress"],
    },
    "math": {
        "name": "2️⃣ 数学基础（线代/概率/离散）",
        "notes": ["csdiy-math-complete.md"],
        "source_reading": ["backprop-graph-精读.md", "vae-math-精读.md", "mamba-ssm-math-精读.md"],
        "paths": ["ai.md"],
    },
    "algo": {
        "name": "3️⃣ 数据结构与算法",
        "source_reading": ["bloom-filter-精读.md", "consistent-hashing-精读.md", "hnsw-algorithm-精读.md"],
        "cheatsheets": ["regex-场景速查.md"],
        "paths": ["theory.md"],
        "projects": ["tinyhash", "tinyhuffman", "tinygraph", "tinyring", "tinyregex", "tinyindex"],
    },
    "os": {
        "name": "4️⃣ 操作系统 / 系统底层 ⭐核心",
        "notes": ["csapp-程序员视角.md", "os-程序员视角-从bug到原理.md"],
        "source_reading": ["go-gmp-scheduler-精读.md", "rust-ownership-精读.md",
                           "numa-architecture-精读.md", "branch-prediction-精读.md"],
        "cheatsheets": ["gdb调试-场景速查.md"],
        "labs": ["xv6-6.S081-从零跑起来.md"],
        "projects": ["tinyshell", "tinydocker", "tinygc", "tinyalloc", "tinypool",
                     "tinysched", "tinytrace", "tinytx", "tinymmu", "tinyinterrupt"],
    },
    "network": {
        "name": "5️⃣ 计算机网络 ⭐核心",
        "notes": ["network-程序员视角-从抓包到原理.md"],
        "source_reading": ["linux-epoll-kernel-精读.md", "linux-tcp-state-machine-精读.md",
                           "nginx-http-parser-精读.md", "eventloop-evolution-redis-nginx-go.md",
                           "frp-tcp-proxy-核心设计拆解.md"],
        "labs": ["cs144-网络-从零跑起来.md"],
        "projects": ["tinyproxy", "tinyhttpd", "tinydns", "tinydhcp", "tinyicmp", "tinyarp",
                     "tinyroute", "tinyratelimit", "tinywebsocket", "tinytls", "tinypipe",
                     "tinystream", "tinyeventloop", "tinybus", "tinyrpc"],
    },
    "db": {
        "name": "6️⃣ 数据库系统 ⭐核心",
        "notes": ["db-程序员视角-从慢SQL到原理.md"],
        "source_reading": ["sqlite-btree-逐行拆解.md", "leveldb-lsm-精读.md",
                           "storage-engine-comparison-精读.md",
                           "redis-data-structures-精读.md", "redis-expiry-policy-精读.md"],
        "cheatsheets": ["postgres-场景速查.md"],
        "labs": ["bustub-15-445-从零跑起来.md"],
        "projects": ["tinydb", "tinycache", "tinybitcask", "tinyblob", "tinysql",
                     "tinywal", "tinyfs", "tinyindex", "tinycachesim"],
    },
    "distributed": {
        "name": "7️⃣ 分布式系统",
        "source_reading": ["raft-vs-paxos-精读.md"],
        "labs": ["mit6.824-raft-从零跑起来.md"],
        "projects": ["tinyraft", "tinykafka", "tiny2pc", "tinymapreduce",
                     "tinygossip", "tinyring", "tinymesi", "tinyclock"],
    },
    "compiler": {
        "name": "8️⃣ 编译原理 / 编程语言设计",
        "projects": ["tinycompiler", "tinyasm", "tinyregex", "tinyjson",
                     "tinylinker", "tinysymtab"],
    },
    "se": {
        "name": "9️⃣ 软件工程 / 编程实践",
        "notes": ["patterns-程序员视角-真实代码里的模式.md",
                  "code-review-程序员视角.md",
                  "perf-程序员视角-定位与优化.md"],
        "cheatsheets": ["git进阶-场景速查.md", "makefile与cmake-场景速查.md",
                        "vim生存-场景速查.md", "shell实战-场景速查.md",
                        "docker速查-场景速查.md", "python-场景速查.md",
                        "profiling-场景速查.md", "k8s-场景速查.md"],
        "projects": ["tinydebug", "tinyprof", "tinymetrics", "tinygit", "tinyrpc"],
    },
    "arch": {
        "name": "🔟 计算机体系结构 / 硬件",
        "notes": ["csapp-程序员视角.md"],
        "source_reading": ["branch-prediction-精读.md", "numa-architecture-精读.md"],
        "projects": ["tinycpu", "tinyasm", "tinyvm", "tinydma", "tinymmu", "tinyinterrupt"],
    },
    "dl": {
        "name": "1️⃣1️⃣ 机器学习 / 深度学习",
        "source_reading": ["micrograd-100行吃透自动微分.md", "nanoGPT-读懂最小GPT.md",
                           "backprop-graph-精读.md", "cnn-convolution-精读.md",
                           "transformer-attention-deep-精读.md", "attention-variants-精读.md",
                           "flash-attention-精读.md", "position-encoding-精读.md",
                           "normalization-deep-精读.md", "dropout-train-infer-精读.md",
                           "weight-init-精读.md", "loss-functions-精读.md",
                           "softmax-temperature-精读.md", "gradient-vanishing-精读.md"],
        "paths": ["ai.md"],
        "projects": ["tinytorch", "tinygen", "tinyrl"],
    },
    "llm": {
        "name": "1️⃣2️⃣ 大语言模型（LLM）⭐最大扩展块",
        "source_reading": [
            # 训练
            "transformer-training-pipeline-精读.md", "lr-scheduling-精读.md",
            "fine-tuning-landscape-精读.md", "rlhf-alignment-精读.md",
            "prompt-engineering-deep-精读.md",
            # 推理
            "tokenizer-deep-精读.md", "kv-cache-原理-精读.md",
            "kv-cache-compression-精读.md", "long-context-精读.md",
            "inference-optimization-精读.md", "speculative-decoding-精读.md",
            "mixed-precision-精读.md", "model-compression-精读.md",
            "model-parallel-精读.md", "moe-routing-精读.md",
            # 部署/评估/应用
            "llm-deployment-精读.md", "llm-evaluation-精读.md", "llm-security-精读.md",
            "rag-advanced-精读.md", "agent-architecture-精读.md",
            "data-pipeline-精读.md", "data-versioning-精读.md",
        ],
        "projects": ["tinyllm", "tinyrag", "tinygen", "tinyrl", "tinytorch"],
    },
    "gen": {
        "name": "生成模型 / SSM / 多模态",
        "source_reading": ["vae-math-精读.md", "mamba-ssm-math-精读.md", "multimodal-精读.md"],
    },
    "graphics": {
        "name": "1️⃣3️⃣ 图形学 / 渲染",
        "paths": ["graphics.md"],
    },
    "web": {
        "name": "1️⃣4️⃣ Web 开发 / 全栈",
        "cheatsheets": ["docker速查-场景速查.md", "k8s-场景速查.md"],
        "paths": ["fullstack.md"],
        "projects": ["tinyhttpd", "tinyproxy", "tinywebsocket"],
    },
    "security": {
        "name": "1️⃣5️⃣ 信息安全",
        "source_reading": ["llm-security-精读.md"],
        "projects": ["tinyencrypt", "tinyauth", "tinytls"],
    },
    "tools": {
        "name": "1️⃣6️⃣ 工具链 / 工程效率（横向）",
        "cheatsheets": ["git进阶-场景速查.md", "gdb调试-场景速查.md", "docker速查-场景速查.md",
                        "makefile与cmake-场景速查.md", "shell实战-场景速查.md",
                        "vim生存-场景速查.md", "k8s-场景速查.md", "postgres-场景速查.md",
                        "profiling-场景速查.md", "python-场景速查.md", "regex-场景速查.md"],
        "cards": ["程序员实战卡片.md"],
    },
}

# 主题别名
ALIASES = {
    "操作系统": "os", "os": "os", "system": "os",
    "网络": "network", "net": "network", "tcp": "network",
    "数据库": "db", "database": "db", "sql": "db",
    "分布式": "distributed", "distributed": "distributed", "raft": "distributed",
    "编译": "compiler", "compiler": "compiler", "语言": "compiler",
    "软件工程": "se", "se": "se", "engineering": "se",
    "体系结构": "arch", "arch": "arch", "cpu": "arch", "硬件": "arch",
    "深度学习": "dl", "dl": "dl", "机器学习": "dl", "ml": "dl", "神经网络": "dl",
    "大模型": "llm", "llm": "llm", "gpt": "llm", "transformer": "llm",
    "生成模型": "gen", "gen": "gen", "vae": "gen", "mamba": "gen", "多模态": "gen",
    "数学": "math", "math": "math", "线代": "math", "概率": "math",
    "算法": "algo", "algo": "algo", "dsa": "algo",
    "入门": "intro", "intro": "intro", "beginner": "intro",
    "图形": "graphics", "graphics": "graphics", "render": "graphics", "pbr": "graphics",
    "web": "web", "全栈": "web", "fullstack": "web",
    "安全": "security", "security": "security", "加密": "security",
    "工具": "tools", "tools": "tools", "工具链": "tools",
}


def file_loc(path):
    """安全地读行数"""
    try:
        return sum(1 for _ in open(path, errors='ignore'))
    except:
        return 0


def show_topic(key):
    t = TOPICS[key]
    print(f"\n{t['name']}")
    print("=" * 70)

    total_items = 0

    # Notes
    if t.get("notes"):
        print(f"\n📖 精读笔记（{len(t['notes'])} 篇）")
        for f in t["notes"]:
            p = ROOT / "notes" / f
            loc = file_loc(p)
            mark = "✓" if p.exists() else "✗"
            print(f"  {mark} notes/{f} ({loc} 行)")
            total_items += 1

    # Source reading
    if t.get("source_reading"):
        print(f"\n🔬 源码精读（{len(t['source_reading'])} 篇）")
        for f in t["source_reading"]:
            p = ROOT / "source-reading" / f
            loc = file_loc(p)
            mark = "✓" if p.exists() else "✗"
            print(f"  {mark} source-reading/{f} ({loc} 行)")
            total_items += 1

    # Cheatsheets
    if t.get("cheatsheets"):
        print(f"\n🛠️ 场景速查（{len(t['cheatsheets'])} 篇）")
        for f in t["cheatsheets"]:
            p = ROOT / "cheatsheets" / f
            loc = file_loc(p)
            mark = "✓" if p.exists() else "✗"
            print(f"  {mark} cheatsheets/{f} ({loc} 行)")
            total_items += 1

    # Labs
    if t.get("labs"):
        print(f"\n🧪 实验指南（{len(t['labs'])} 篇）")
        for f in t["labs"]:
            p = ROOT / "labs" / f
            loc = file_loc(p)
            mark = "✓" if p.exists() else "✗"
            print(f"  {mark} labs/{f} ({loc} 行)")
            total_items += 1

    # Paths
    if t.get("paths"):
        print(f"\n🛤️ 学习路径（{len(t['paths'])} 条）")
        for f in t["paths"]:
            p = ROOT / "paths" / f
            loc = file_loc(p)
            mark = "✓" if p.exists() else "✗"
            print(f"  {mark} paths/{f} ({loc} 行)")
            total_items += 1

    # Projects
    if t.get("projects"):
        print(f"\n🏗️ 毕业项目（{len(t['projects'])} 个）")
        for name in t["projects"]:
            pdir = ROOT / "projects" / name
            py_files = list(pdir.glob("**/*.py")) if pdir.exists() else []
            py_loc = sum(file_loc(f) for f in py_files)
            mark = "✓" if pdir.exists() else "✗"
            print(f"  {mark} projects/{name}/ ({len(py_files)} py, {py_loc} 行)")
            total_items += 1

    # Cards
    if t.get("cards"):
        print(f"\n💼 实战卡片（{len(t['cards'])} 份）")
        for f in t["cards"]:
            p = ROOT / "cards" / f
            loc = file_loc(p)
            print(f"  ✓ cards/{f} ({loc} 行)")
            total_items += 1

    print(f"\n📊 总计 {total_items} 个资源")


def list_topics():
    print("\n🗂️  csdiy 16 个学科主题")
    print("=" * 70)
    for i, (key, t) in enumerate(TOPICS.items(), 1):
        n = sum(len(t.get(k, [])) for k in
                ["notes", "source_reading", "cheatsheets", "labs", "paths", "projects", "cards"])
        print(f"  {i:>2}. {key:<12} → {t['name']} ({n} 资源)")


def show_all():
    """全部主题概览"""
    print("\n🗂️  csdiy 全主题概览（16 主题）")
    print("=" * 70)
    grand = 0
    for key, t in TOPICS.items():
        n = sum(len(t.get(k, [])) for k in
                ["notes", "source_reading", "cheatsheets", "labs", "paths", "projects", "cards"])
        grand += n
        print(f"  {t['name']:<55} ({n} 资源)")
    print(f"\n📊 16 主题共索引 {grand} 个资源（含跨主题复用）")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return

    if sys.argv[1] == "--list":
        list_topics()
        return

    if sys.argv[1] == "--all":
        show_all()
        return

    # 单主题或多主题
    for arg in sys.argv[1:]:
        key = ALIASES.get(arg.lower(), arg.lower())
        if key in TOPICS:
            show_topic(key)
        else:
            print(f"\n❌ 未知主题: {arg}")
            print(f"   可用主题: {', '.join(TOPICS.keys())}")
            print(f"   或别名:   os/network/db/distributed/compiler/se/arch/dl/llm/gen/")
            print(f"             math/algo/intro/graphics/web/security/tools")


if __name__ == "__main__":
    main()
