#!/usr/bin/env python3
"""
csdiy.py — 真实有用的 AI CS 导师

把 csdiy 全部资源整合成一个可交互的 CLI 工具：

  python3 csdiy.py ask "什么是虚拟内存？"
  → 检索 csdiy 精读笔记 → 构建增强 prompt → 回答

  python3 csdiy.py learn csapp
  → 推荐学习路径 + 费曼挑战

  python3 csdiy.py search "epoll 原理"
  → 全文搜索精读 + 项目

  python3 csdiy.py quiz
  → 随机抽费曼挑战题

  python3 csdiy.py daily
  → 今日学习套餐

架构: tinyrag(检索) + tinyllm(生成) + 费曼挑战 + 学习路径
"""
import os, sys, json, random, re, time, hashlib, math
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 搜索引擎（轻量级全文搜索，不依赖 SQLite）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class CSKnowledgeBase:
    """csdiy 全资源知识库（精读笔记 + 源码精读 + 速查 + Lab + 项目）"""

    def __init__(self):
        self.docs = []  # [(title, category, path, content)]
        self._load()

    def _load(self):
        """加载所有 markdown 文档"""
        patterns = [
            ("notes/*.md", "精读笔记"),
            ("source-reading/*.md", "源码精读"),
            ("cheatsheets/*.md", "场景速查"),
            ("labs/*.md", "实验指南"),
        ]
        for pattern, category in patterns:
            for f in sorted((ROOT / pattern.split("/")[0]).glob("*.md")) if (ROOT / pattern.split("/")[0]).exists() else []:
                try:
                    content = f.read_text(encoding="utf-8", errors="replace")
                    title = content.split("\n")[0].strip("# ").strip()
                    self.docs.append({
                        "title": title,
                        "category": category,
                        "path": str(f.relative_to(ROOT)),
                        "content": content,
                        "tokens": self._tokenize(content),
                    })
                except:
                    pass

    def _tokenize(self, text):
        # 中英文混合分词：中文按字+英文按词
        tokens = re.findall(r"[\u4e00-\u9fa5]|[a-zA-Z][a-zA-Z0-9_]+|[A-Z]{2,}", text.lower())
        return tokens

    def search(self, query, top_k=5):
        """BM25-like 搜索"""
        q_tokens = set(self._tokenize(query))
        # 也加入原始查询词（处理中文短语）
        for word in re.findall(r"[\u4e00-\u9fa5]+|[a-zA-Z]+", query.lower()):
            q_tokens.add(word)
        if not q_tokens:
            return []
        scored = []
        for doc in self.docs:
            # 检查是否有任何 token 出现在文档中
            doc_text = doc["content"].lower()
            query_lower = query.lower()
            # 直接子串匹配（对中文更友好）
            has_match = any(qt in doc_text for qt in [query_lower] + list(q_tokens) if len(qt) > 1)
            if not has_match:
                continue
            # TF-IDF scoring
            tf = sum(1 for t in doc["tokens"] if t in q_tokens)
            # 子串匹配加权
            if query_lower in doc_text:
                tf += 5
            if query_lower in doc["title"].lower():
                tf += 10
            if tf == 0:
                tf = 1  # 至少有子串匹配
            idf = math.log(1 + len(self.docs) / max(1, tf))
            title_bonus = 2.0 if any(q in doc["title"].lower() for q in query.lower().split()) else 1.0
            score = tf * idf * title_bonus
            scored.append((score, doc))
        scored.sort(key=lambda x: -x[0])
        return [doc for _, doc in scored[:top_k]]

    def stats(self):
        cats = Counter(d["category"] for d in self.docs)
        return {"total": len(self.docs), "categories": dict(cats)}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 学习路径推荐
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LEARNING_PATHS = {
    "csapp": {
        "name": "CSAPP 程序员视角",
        "steps": [
            ("Ch2 位级表示", "notes/csapp-程序员视角.md", "补码/溢出/浮点"),
            ("Ch3 机器级表示", "notes/csapp-程序员视角.md", "汇编/GDB/bomb lab"),
            ("Ch5 优化", "notes/perf-程序员视角.md", "perf/cache/向量化"),
            ("Ch6 存储层次", "notes/csapp-程序员视角.md", "cache/分块矩阵"),
            ("Ch8 异常控制流", "notes/os-程序员视角.md", "fork/信号/僵尸"),
            ("Ch9 虚拟内存", "notes/os-程序员视角.md", "OOM/page cache/fsync"),
        ],
        "project": "projects/tinycpu/ (CPU 模拟器) + projects/tinymmu/ (MMU)",
        "feynman": "python3 tools/feynman.py --source csapp",
    },
    "network": {
        "name": "网络工程",
        "steps": [
            ("TCP 基础", "notes/network-程序员视角.md", "三次握手/四次挥手/epoll"),
            ("粘包/CLOSE_WAIT", "notes/network-程序员视角.md", "字节流/状态机"),
            ("TLS 握手", "notes/network-程序员视角.md", "TLS 1.3/会话复用"),
            ("DNS", "notes/network-程序员视角.md", "UDP/转发"),
            ("HTTP 服务", "notes/network-程序员视角.md", "HTTP解析/路由"),
        ],
        "project": "projects/tinyproxy/ + projects/tinyhttpd/ + projects/tinydns/",
        "feynman": "python3 tools/feynman.py --source network",
    },
    "database": {
        "name": "数据库",
        "steps": [
            ("B+ 树索引", "notes/db-程序员视角.md", "索引选择性/最左前缀"),
            ("锁与死锁", "notes/db-程序员视角.md", "两阶段锁/死锁检测"),
            ("MVCC", "notes/db-程序员视角.md", "隔离级别/快照"),
            ("WAL", "notes/db-程序员视角.md", "WAL/fsync/redo"),
        ],
        "project": "projects/tinydb/ (KV+WAL+B+树) + projects/tinywal/",
        "feynman": "python3 tools/feynman.py --source db",
    },
    "ai": {
        "name": "AI/LLM 全栈",
        "steps": [
            ("Transformer", "source-reading/transformer-attention-deep-精读.md", "QKV/Multi-Head/Pre-LN"),
            ("训练流程", "source-reading/transformer-training-pipeline-精读.md", "Pre-training/SFT/DPO"),
            ("推理优化", "source-reading/inference-optimization-精读.md", "KV Cache/Batching/Flash Attn"),
            ("RAG 系统", "source-reading/rag-advanced-精读.md", "检索/重排序/Self-RAG"),
            ("Agent", "source-reading/agent-architecture-精读.md", "ReAct/工具调用/记忆"),
        ],
        "project": "projects/tinytorch/ + projects/tinyllm/ + projects/tinyrag/",
        "feynman": "python3 tools/feynman.py --source csapp",
    },
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLI 命令
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def cmd_ask(args):
    """ask <question> — 搜索 csdiy 知识库并回答"""
    query = " ".join(args)
    if not query:
        print("用法: csdiy.py ask '你的问题'")
        return
    kb = CSKnowledgeBase()
    results = kb.search(query, top_k=3)
    print(f"\n🔍 搜索: '{query}'")
    print(f"   知识库: {kb.stats()['total']} 篇文档\n")
    if not results:
        print("  没有找到相关文档。试试其他关键词。")
        return
    print("📚 相关文档:")
    for i, doc in enumerate(results):
        print(f"\n  [{i+1}] {doc['title']} ({doc['category']})")
        print(f"      📁 {doc['path']}")
        # 提取相关段落
        lines = doc["content"].split("\n")
        for line in lines:
            if any(kw in line.lower() for kw in query.lower().split()):
                clean = line.strip("#>*- ").strip()
                if clean and len(clean) > 10:
                    print(f"      → {clean[:100]}")
                    break
    print(f"\n💡 深入学习:")
    print(f"   python3 tools/feynman.py  # 费曼挑战")
    print(f"   python3 tools/ask.py '{query}'  # RAG 问答")

def cmd_search(args):
    """search <keyword> — 全文搜索"""
    query = " ".join(args)
    if not query:
        print("用法: csdiy.py search 'epoll'"); return
    kb = CSKnowledgeBase()
    results = kb.search(query, top_k=10)
    print(f"\n🔍 搜索 '{query}': {len(results)} 条结果\n")
    for i, doc in enumerate(results):
        print(f"  {i+1}. [{doc['category']}] {doc['title']}")
        print(f"     {doc['path']}")

def cmd_learn(args):
    """learn <topic> — 推荐学习路径"""
    topic = args[0] if args else ""
    if topic not in LEARNING_PATHS:
        print(f"\n可用路径: {', '.join(LEARNING_PATHS.keys())}")
        return
    path = LEARNING_PATHS[topic]
    print(f"\n📚 {path['name']}")
    print(f"{'═'*50}\n")
    for i, (title, source, keywords) in enumerate(path["steps"]):
        print(f"  Step {i+1}: {title}")
        print(f"    📖 {source}")
        print(f"    🔑 {keywords}\n")
    print(f"🛠️ 实践项目: {path['project']}")
    print(f"🎤 费曼挑战: {path['feynman']}")

def cmd_quiz(args=None):
    """quiz — 随机费曼挑战"""
    challenges = [
        ("CSAPP Ch2", "用 3 句话向 5 岁小孩解释补码", "notes/csapp-程序员视角.md"),
        ("OS §一", "你的程序被 OOM Kill 时发生了什么？", "notes/os-程序员视角.md"),
        ("Network §二", "为什么 epoll 比 select 快？", "notes/network-程序员视角.md"),
        ("DB §一", "为什么数据库用 B+ 树不用红黑树？", "notes/db-程序员视角.md"),
        ("Patterns §6", "为什么说 90% 的单例是全局变量伪装？", "notes/patterns-程序员视角.md"),
        ("Transformer", "Attention 的 QKV 到底在做什么？", "source-reading/transformer-attention-deep-精读.md"),
        ("RLHF", "ChatGPT 的三阶段对齐流程是什么？", "source-reading/rlhf-alignment-精读.md"),
        ("KV Cache", "vLLM 的 PagedAttention 解决了什么问题？", "source-reading/kv-cache-原理-精读.md"),
        ("Flash Attn", "Flash Attention 为什么更快但不改变结果？", "source-reading/flash-attention-精读.md"),
        ("RAG", "Self-RAG 和 CRAG 的区别是什么？", "source-reading/rag-advanced-精读.md"),
    ]
    c = random.choice(challenges)
    print(f"\n🎤 费曼挑战")
    print(f"{'═'*50}")
    print(f"\n  主题: {c[0]}")
    print(f"  问题: {c[1]}")
    print(f"  参考: {c[2]}")
    print(f"\n  规则: 不参考资料，用自己的话回答。")
    print(f"  记录: python3 tools/feynman.py")

def cmd_daily(args=None):
    """daily — 今日学习套餐"""
    print(f"\n📅 csdiy 今日学习套餐 ({time.strftime('%Y-%m-%d')})")
    print(f"{'═'*50}\n")
    # 费曼挑战
    cmd_quiz()
    # 推荐精读
    kb = CSKnowledgeBase()
    doc = random.choice(kb.docs)
    print(f"\n📖 今日推荐精读:")
    print(f"   {doc['title']} ({doc['category']})")
    print(f"   {doc['path']}")
    # 推荐项目
    project_dirs = [d for d in (ROOT / "projects").iterdir() if d.is_dir() and d.name.startswith("tiny")]
    proj = random.choice(project_dirs)
    print(f"\n🛠️ 今日推荐项目:")
    print(f"   {proj.name}/")
    # 学习路径
    topic = random.choice(list(LEARNING_PATHS.keys()))
    path = LEARNING_PATHS[topic]
    print(f"\n📚 学习路径: {path['name']}")
    print(f"   python3 csdiy.py learn {topic}")
    print(f"\n{'═'*50}")

def cmd_stats(args=None):
    """stats — csdiy 统计"""
    kb = CSKnowledgeBase()
    print(f"\n📊 csdiy 统计")
    print(f"{'═'*50}")
    print(f"  知识库: {kb.stats()['total']} 篇文档")
    for cat, count in kb.stats()["categories"].items():
        print(f"    {cat}: {count} 篇")
    # 项目
    project_dirs = [d for d in (ROOT / "projects").iterdir() if d.is_dir() and d.name.startswith("tiny")]
    deep = [d for d in project_dirs if (d / "__init__.py").exists()]
    single = [d for d in project_dirs if not (d / "__init__.py").exists()]
    print(f"\n  项目: {len(project_dirs)} 个")
    print(f"    深度系统: {len(deep)} 个 ({', '.join(d.name for d in deep)})")
    print(f"    单文件: {len(single)} 个")
    # 源码精读
    readings = list((ROOT / "source-reading").glob("*.md"))
    print(f"\n  源码精读: {len(readings)} 篇")
    print(f"{'═'*50}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 主入口
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HELP = """
csdiy — AI CS 导师
══════════════════════════════════════════════════

命令:
  ask <question>     搜索知识库并回答问题
  search <keyword>   全文搜索精读/速查/Lab
  learn <topic>      推荐学习路径 (csapp/network/database/ai)
  quiz               随机费曼挑战
  daily              今日学习套餐
  stats              csdiy 统计

示例:
  python3 csdiy.py ask "什么是虚拟内存"
  python3 csdiy.py search "epoll"
  python3 csdiy.py learn ai
  python3 csdiy.py quiz
  python3 csdiy.py daily
"""

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        print(HELP); return
    cmd = sys.argv[1]; args = sys.argv[2:]
    commands = {
        "ask": cmd_ask, "search": cmd_search, "learn": cmd_learn,
        "quiz": cmd_quiz, "daily": cmd_daily, "stats": cmd_stats,
    }
    if cmd in commands:
        commands[cmd](args)
    else:
        print(f"未知命令: {cmd}\n{HELP}")

if __name__ == "__main__":
    main()
