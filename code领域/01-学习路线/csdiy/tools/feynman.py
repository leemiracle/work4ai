#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
csdiy 费曼挑战 — 每日强制输出工具

费曼学习法：能讲给小学生听才算真懂。
本工具每天抽一个概念，强制你做 4 层输出：
  L1 复述：用 3 句话向 5 岁小孩解释
  L2 联系：找一段你写的代码，说明这个概念在哪扮演角色
  L3 创造：不参考资料，画图 / 写代码
  L4 教学：录 3 分钟视频教一个非程序员

用法：
  python3 tools/feynman.py                    # 随机抽一个概念
  python3 tools/feynman.py --source csapp     # 只从 CSAPP 精读抽
  python3 tools/feynman.py --source random    # 随机（默认）
  python3 tools/feynman.py --list             # 列出所有概念
  python3 tools/feynman.py --history          # 看历史输出统计
"""

import argparse
import datetime
import json
import os
import random
import subprocess
import sys
from pathlib import Path

# ─── ANSI 颜色 ───
def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"
def red(t):    return _c("31", t)
def green(t):  return _c("32", t)
def yellow(t): return _c("33", t)
def blue(t):   return _c("34", t)
def magenta(t):return _c("35", t)
def cyan(t):   return _c("36", t)
def bold(t):   return _c("1", t)
def dim(t):    return _c("2", t)

# ─── 概念库（可扩展） ───
# 每个概念：source（来源文件）+ title（概念名）+ hints（4层提示）
CONCEPTS = [
    # === CSAPP ===
    {
        "source": "csapp",
        "title": "补码与整数溢出",
        "chapter": "Ch2",
        "hints": [
            "为什么计算机用补码而不是原码表示负数？",
            "你代码里的 int 累加器在哪里可能溢出？",
            "写一个安全的加法函数（溢出时返回错误）",
            "向同事解释 size_t 反向循环为什么死循环",
        ],
    },
    {
        "source": "csapp",
        "title": "读汇编与 GDB 拆弹",
        "chapter": "Ch3",
        "hints": [
            "为什么 C 程序员需要能读汇编？",
            "你最近一次 segfault 的 backtrace 看懂了吗？",
            "用 objdump -d 反汇编一个简单函数，标注每个寄存器的作用",
            "教非程序员朋友'程序在 CPU 里到底怎么跑的'",
        ],
    },
    {
        "source": "csapp",
        "title": "Cache 与缓存友好性",
        "chapter": "Ch6",
        "hints": [
            "为什么顺序遍历数组比随机访问快？",
            "你的代码里哪里有 cache miss？",
            "写一个 cache 友好的矩阵转置",
            "用'图书馆书架'比喻向小孩解释 cache",
        ],
    },
    {
        "source": "csapp",
        "title": "虚拟内存",
        "chapter": "Ch9",
        "hints": [
            "为什么每个进程都以为自己独占内存？",
            "你的程序 OOM 时到底发生了什么？",
            "画一张进程地址空间图（text/data/heap/stack）",
            "向 PM 解释'内存不是真的满了，是虚拟地址空间的把戏'",
        ],
    },
    {
        "source": "csapp",
        "title": "异常控制流与信号",
        "chapter": "Ch8",
        "hints": [
            "为什么信号处理函数里不能调 printf？",
            "你的代码哪里有 fork-exec 的竞态？",
            "写一个不会产生僵尸进程的 shell",
            "解释僵尸进程是怎么来的（用'孩子死了但家长没来收尸'比喻）",
        ],
    },
    # === OS ===
    {
        "source": "os",
        "title": "OOM Killer",
        "chapter": "§一",
        "hints": [
            "Linux 为什么不让你 malloc 失败，而是直接杀进程？",
            "你的服务被 OOM Kill 过吗？当时 RSS 是多少？",
            "写一个内存监控脚本，在接近 OOM 前报警",
            "向运维解释 OOM Killer 的'打分'逻辑",
        ],
    },
    {
        "source": "os",
        "title": "死锁",
        "chapter": "§二",
        "hints": [
            "死锁的四个必要条件是什么？为什么是'必要'？",
            "你代码里哪里有潜在的死锁？",
            "写一个不会死锁的哲学家就餐模型",
            "用'十字路口堵车'比喻向小孩解释死锁",
        ],
    },
    {
        "source": "os",
        "title": "Page Cache 与 fsync",
        "chapter": "§四",
        "hints": [
            "为什么 write() 返回了，数据可能还没落盘？",
            "你的程序在哪里依赖了 fsync？如果 fsync 失败会怎样？",
            "写一个'绝对不会丢数据'的日志写入函数",
            "解释'write 是异步的'这句话对程序员的含义",
        ],
    },
    # === DB ===
    {
        "source": "db",
        "title": "B+ 树与索引选择性",
        "chapter": "§一",
        "hints": [
            "为什么数据库用 B+ 树不用红黑树？",
            "你的表上哪个索引选择性最高？哪个最低？",
            "画一棵 3 层 B+ 树，标注每层能存多少行",
            "向产品经理解释'加了索引为什么还慢'（索引失效）",
        ],
    },
    {
        "source": "db",
        "title": "MVCC 与隔离级别",
        "chapter": "§四",
        "hints": [
            "MVCC 怎么实现'读不阻塞写'？",
            "你的业务里哪里可能脏读？哪里需要可串行化？",
            "用两个终端模拟 4 种隔离级别的差异",
            "向非 DBA 解释'幻读'和'不可重复读'的区别",
        ],
    },
    {
        "source": "db",
        "title": "WAL 与写入性能",
        "chapter": "§六",
        "hints": [
            "为什么 WAL 让写入更快？",
            "你的数据库 fsync 频率是多少？如果调低会怎样？",
            "解释 WAL 的'顺序写 vs 随机写'优势",
            "向运维解释'数据库越来越慢'可能的原因",
        ],
    },
    # === Network ===
    {
        "source": "network",
        "title": "epoll vs select",
        "chapter": "§二",
        "hints": [
            "为什么 epoll 比 select 快？本质区别是什么？",
            "你的服务用的什么 IO 模型？瓶颈在哪？",
            "写一个最小的 echo server（epoll 版）",
            "用'前台接待 vs 每人一个服务员'比喻向小孩解释",
        ],
    },
    {
        "source": "network",
        "title": "CLOSE_WAIT 堆积",
        "chapter": "§四",
        "hints": [
            "CLOSE_WAIT 堆积是谁的锅？客户端还是服务端？",
            "你的服务有多少 CLOSE_WAIT？谁没调 close()？",
            "写一个永远不会泄漏 CLOSE_WAIT 的 HTTP 客户端",
            "向运维解释四次挥手状态机",
        ],
    },
    {
        "source": "network",
        "title": "TCP 粘包",
        "chapter": "§三",
        "hints": [
            "TCP 粘包是 bug 吗？为什么？",
            "你的协议怎么定义消息边界的？",
            "写一个带长度前缀的消息拆包器",
            "解释'TCP 是字节流不是消息流'对协议设计的影响",
        ],
    },
    # === Patterns ===
    {
        "source": "patterns",
        "title": "单例模式的陷阱",
        "chapter": "§6",
        "hints": [
            "为什么说 90% 的单例是全局变量的伪装？",
            "你代码里哪个单例可以删掉？换成什么？",
            "写一个线程安全的懒加载（不用 synchronized）",
            "向新人解释'全局变量为什么是坏味道'",
        ],
    },
    {
        "source": "patterns",
        "title": "状态机 vs if-else",
        "chapter": "§9",
        "hints": [
            "什么时候该用状态机，什么时候 if-else 够了？",
            "你的代码里哪个 if-else 链应该变成状态机？",
            "写一个 TCP 连接状态机（11 个状态）",
            "解释'状态爆炸'为什么是状态机的红线",
        ],
    },
    # === Source Reading ===
    {
        "source": "micrograd",
        "title": "反向传播的本质",
        "chapter": "§二",
        "hints": [
            "反向传播和链式法则的关系是什么？",
            "你的代码里哪里用了梯度？梯度怎么流动？",
            "手写一个只有加法和乘法的计算图，算反向梯度",
            "向学过高中数学的人解释反向传播",
        ],
    },
    {
        "source": "nanoGPT",
        "title": "Attention 的本质",
        "chapter": "§四",
        "hints": [
            "QKV 到底在做什么？为什么是三个矩阵？",
            "你的项目里用 Attention 吗？它在做信息路由还是特征变换？",
            "手写一个 4 行的 self-attention（不用框架）",
            "解释 Attention 的 O(n²) 复杂度从哪来",
        ],
    },
    {
        "source": "redis",
        "title": "事件循环的本质",
        "chapter": "§一",
        "hints": [
            "Redis 单线程为什么能扛 10 万 QPS？",
            "你的服务用的事件循环模型是什么？瓶颈在哪？",
            "写一个 30 行的事件循环（用 epoll）",
            "解释'IO 多路复用'和'多线程'的本质区别",
        ],
    },
    {
        "source": "sqlite",
        "title": "B-tree 页的物理结构",
        "chapter": "§二",
        "hints": [
            "SQLite 一个页里 cell pointer array 为什么从页头向后、cell 从页尾向前生长？",
            "为什么 SQLite 删一行不立即缩小文件？",
            "用 hexdump 看一个真实的 SQLite 页头部，逐字节解码",
            "解释 B-tree 的'分裂'和'合并'对性能的影响",
        ],
    },
]

# ─── 路径 ───
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output" / "feynman"
HISTORY_FILE = OUTPUT_DIR / "history.json"

# ─── 核心逻辑 ───
def get_concept(source: str) -> dict:
    """按来源筛选并随机抽取一个概念"""
    if source == "random":
        pool = CONCEPTS
    else:
        pool = [c for c in CONCEPTS if c["source"] == source]
    if not pool:
        print(red(f"✗ 没有来源 '{source}' 的概念"))
        print(f"  可用来源: {', '.join(sorted(set(c['source'] for c in CONCEPTS)))}")
        sys.exit(1)
    return random.choice(pool)

def show_challenge(concept: dict):
    """显示 4 层费曼挑战"""
    print()
    print(bold(cyan("╔" + "═" * 58 + "╗")))
    title = f"🎤 今日费曼挑战：{concept['title']}"
    print(bold(cyan("║")) + bold(f"  {title:<56}") + bold(cyan("║")))
    meta = f"来源: {concept['source']} {concept['chapter']}"
    print(cyan("║") + f"  {meta:<56}" + cyan("║"))
    print(bold(cyan("╚") + "═" * 58 + "╝"))

    print()
    print(yellow("  费曼法：能讲给小学生听才算真懂。"))
    print(dim("  规则：不参考资料，用自己的话写。写不出=没真懂。"))
    print()

    levels = [
        ("L1", green, "复述层", "用 3 句话向 5 岁小孩解释"),
        ("L2", blue, "联系层", "找一段你写的代码，说明这个概念在哪扮演角色"),
        ("L3", magenta, "创造层", "不参考资料，画图 / 写代码"),
        ("L4", red, "教学层", "录 3 分钟视频教一个非程序员朋友"),
    ]

    for i, (lv, color, name, desc) in enumerate(levels):
        hint = concept["hints"][i] if i < len(concept["hints"]) else desc
        print(f"  {bold(color(lv))} {bold(name)}")
        print(f"     {dim('提示：')} {hint}")
        print()

    print(dim("  ────────────────────────────────────────────"))
    print(dim("  准备好了吗？按下回车后开始记录（或用编辑器写）..."))

def create_output(concept: dict, use_editor: bool = False) -> Path:
    """创建当天的输出文件"""
    today = datetime.date.today().isoformat()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 避免同一天多个概念冲突
    timestamp = datetime.datetime.now().strftime("%H%M")
    slug = concept["title"].replace(" ", "_").replace("/", "_")[:20]
    filename = f"{today}_{timestamp}_{concept['source']}_{slug}.md"
    filepath = OUTPUT_DIR / filename

    # 模板
    template = f"""# 费曼挑战：{concept['title']}

> 来源：{concept['source']} {concept['chapter']}
> 日期：{today}
> 规则：不参考资料，用自己的话写。写不出 = 没真懂。

---

## L1 复述层（向 5 岁小孩解释）

{concept['hints'][0]}


---

## L2 联系层（和我的代码关联）

{concept['hints'][1]}


---

## L3 创造层（画图 / 写代码）

{concept['hints'][2]}


---

## L4 教学层（教一个非程序员）

{concept['hints'][3]}


---

## 自评

- [ ] L1 能说清楚吗？（1-5 分）
- [ ] L2 找到真实关联了吗？（1-5 分）
- [ ] L3 不看资料能做出来吗？（1-5 分）
- [ ] L4 能讲给别人听吗？（1-5 分）

**反思（哪里卡住了？下次怎么补？）**:


"""
    filepath.write_text(template, encoding="utf-8")
    return filepath

def open_editor(filepath: Path):
    """用 $EDITOR 打开文件"""
    editor = os.environ.get("EDITOR", "vim")
    try:
        subprocess.run([editor, str(filepath)])
    except FileNotFoundError:
        print(yellow(f"  (未找到 {editor}，请手动打开: {filepath})"))

def save_history(concept: dict, filepath: Path):
    """记录历史"""
    history = []
    if HISTORY_FILE.exists():
        try:
            history = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except:
            history = []
    history.append({
        "date": datetime.date.today().isoformat(),
        "concept": concept["title"],
        "source": concept["source"],
        "file": filepath.name,
    })
    HISTORY_FILE.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")

def show_history():
    """显示历史统计"""
    if not HISTORY_FILE.exists():
        print(dim("  还没有历史记录。开始你的第一个费曼挑战吧！"))
        return
    history = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    print(bold(f"\n📊 费曼挑战历史（共 {len(history)} 次）\n"))
    
    # 按来源统计
    by_source = {}
    for h in history:
        s = h["source"]
        by_source[s] = by_source.get(s, 0) + 1
    
    print("  按来源：")
    for s, count in sorted(by_source.items(), key=lambda x: -x[1]):
        bar = "█" * count
        print(f"    {s:12s} {bar} {count}")
    
    print(f"\n  最近 5 次：")
    for h in history[-5:]:
        print(f"    {h['date']} {h['source']:10s} {h['concept']}")

def list_concepts():
    """列出所有概念"""
    print(bold(f"\n📚 概念库（共 {len(CONCEPTS)} 个）\n"))
    by_source = {}
    for c in CONCEPTS:
        by_source.setdefault(c["source"], []).append(c)
    for source, concepts in sorted(by_source.items()):
        print(f"  {bold(source)} ({len(concepts)} 个):")
        for c in concepts:
            print(f"    {c['chapter']:6s} {c['title']}")
        print()

# ─── CLI ───
def main():
    parser = argparse.ArgumentParser(
        description="csdiy 费曼挑战 — 每日强制输出",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python3 tools/feynman.py                    # 随机抽一个概念
  python3 tools/feynman.py --source csapp     # 从 CSAPP 精读抽
  python3 tools/feynman.py --source db        # 从数据库精读抽
  python3 tools/feynman.py --list             # 列出所有概念
  python3 tools/feynman.py --history          # 看历史统计
  python3 tools/feynman.py --no-editor        # 不开编辑器，只创建文件
        """,
    )
    parser.add_argument("--source", default="random",
                        help="概念来源：random/csapp/os/db/network/patterns/micrograd/nanoGPT/redis/sqlite")
    parser.add_argument("--list", action="store_true", help="列出所有概念")
    parser.add_argument("--history", action="store_true", help="看历史统计")
    parser.add_argument("--no-editor", action="store_true", help="不自动打开编辑器")
    args = parser.parse_args()

    if args.list:
        list_concepts()
        return
    if args.history:
        show_history()
        return

    concept = get_concept(args.source)
    show_challenge(concept)

    try:
        input()  # 等待回车
    except (EOFError, KeyboardInterrupt):
        print(dim("\n  下次再来！"))
        return

    filepath = create_output(concept)
    save_history(concept, filepath)
    
    print(green(f"\n  ✅ 已创建: {filepath}"))
    print(dim(f"  打开它，开始你的 4 层费曼输出。"))
    
    if not args.no_editor:
        print(dim(f"  按 Ctrl+C 跳过编辑器，或回车打开 {os.environ.get('EDITOR', 'vim')}..."))
        try:
            input()
            open_editor(filepath)
        except (EOFError, KeyboardInterrupt):
            print(dim(f"\n  手动打开: {filepath}"))

if __name__ == "__main__":
    main()
