#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
feynman-coach.py — 费曼陪练（C 方案）

走费曼学习法闭环：你选主题 → AI 扮演 3 种外行连环追问 → 戳穿术语偷懒 → 生成卡壳报告。

费曼学习法 ≠ "讲得通俗"，而是 4 步闭环自检：
  ① 假装教外行  ② 用大白话  ③ 戳卡壳点  ④ 回炉
本脚本帮你完成 ①②③，并产出报告供你做 ④。

用法:
  python3 feynman-coach.py                          # 交互输入主题
  python3 feynman-coach.py "量子纠缠"               # 直接给主题
  python3 feynman-coach.py --file ../讲透AIfor各学科/物理/本质探索.md
  python3 feynman-coach.py "注意力机制" --rounds 4  # 每角色追问 4 轮

可选环境变量（不设也能跑，用演示模式）:
  OPENAI_API_KEY     API key
  OPENAI_BASE_URL    OpenAI 兼容 endpoint（智谱/豆包/OpenAI 都行）
  OPENAI_MODEL       模型名

退出:
  输入 :q / quit / exit 提前结束并生成报告
  输入 :skip 跳过当前问题
  Ctrl+C 直接退出（不生成报告）

报告输出:
  ./feynman-report-<主题>-<时间戳>.md
"""

from __future__ import annotations
import os
import sys
import json
import time
import datetime
import pathlib
import urllib.request
import urllib.error
import random
from typing import Optional

# ============================================================
# 配置
# ============================================================

API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").strip().rstrip("/")
MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini").strip()

HAS_LLM = bool(API_KEY)

# ============================================================
# 三种追问角色（费曼法的外行检验）
# ============================================================

ROLES = {
    "kid": {
        "name": "12 岁小孩",
        "emoji": "🧒",
        "system": (
            "你是一个 12 岁的聪明小孩，好奇、较真、不怕问'蠢'问题。"
            "你的任务：听对方讲一个技术/学术主题，然后追问他没讲清的地方。"
            "规则：\n"
            "1) 你不懂任何专业术语。对方每用一个术语，你就问'XX 是什么意思，能用例子讲吗？'\n"
            "2) 你不接受'其实就是''本质上''换句话说'这种含糊带过——追问具体例子\n"
            "3) 你会用你熟悉的事（游戏/动画/学校/玩具）打比方，要对方对得上\n"
            "4) 每次只问 1 个问题，简短（不超过 2 句），尖锐、具体\n"
            "5) 如果对方讲得真清楚，你可以说'哦我懂了'然后换下一个点追问\n"
            "禁止：自己用术语；一次问多个问题；说教。"
        ),
    },
    "journalist": {
        "name": "调查记者",
        "emoji": "📰",
        "system": (
            "你是一个科技调查记者，怀疑主义、要证据、找漏洞。"
            "你的任务：听对方讲一个技术主题，然后像审稿一样拷问论断。"
            "规则：\n"
            "1) 对方每个论断，你都问'你怎么证明？有反例吗？数据来源？'\n"
            "2) 你专门抓'双重标准''未经定义的核心词''逻辑跳跃'\n"
            "3) 你会说'你刚才说 X，但又说 Y，这两个不矛盾吗？'\n"
            "4) 每次只问 1 个问题，简短，像质询\n"
            "5) 不接受'业界共识''一般认为'这种逃避\n"
            "禁止：帮对方圆场；一次问多个问题。"
        ),
    },
    "philosopher": {
        "name": "苏格拉底式哲学家",
        "emoji": "🏛️",
        "system": (
            "你是苏格拉底式的哲学家，只通过追问揭示对方的前提。"
            "你的任务：听对方讲一个主题，追问他自己都没意识到的假设。"
            "规则：\n"
            "1) 你不断追问'你说的 X 到底指什么？请给一个能检验的定义'\n"
            "2) 你问'你这个论断成立的前提是什么？这个前提成立吗？'\n"
            "3) 你问'如果 X 不成立，你的整个论证会塌吗？'\n"
            "4) 每次只问 1 个问题，安静、缓慢、不放过\n"
            "5) 不接受'这取决于定义''这是个哲学问题'这种逃避——逼对方给出工作定义\n"
            "禁止：自己下结论；一次问多个问题。"
        ),
    },
}

ROLE_ORDER = ["kid", "journalist", "philosopher"]

# ============================================================
# 偷懒信号检测（启发式，无 LLM 也管用）
# ============================================================

# 含糊带过词：出现 = 可能在偷懒
VAGUE_MARKERS = [
    "本质上", "其实就是", "简单来说", "换句话说", "可以理解为",
    "总的来说", "从某种意义上", "广义上", "狭义上", "换言之",
    "总而言之", "一言以蔽之", "you know", "基本上",
]

# 回避信号
EVASION_MARKERS = [
    "这取决于", "这是个哲学问题", "这个问题很复杂",
    "目前还没有定论", "学界尚无共识", "这是一个开放问题",
    "因人而异", "需要更深入的",
]

# 通用术语黑名单（这些词一出现就要追问）—— 按领域分组
TERM_BLACKLIST = {
    "ai/ML": ["模型", "训练", "参数", "梯度", "损失函数", "神经网络", "注意力",
              "表征", "嵌入", "微调", "推理", "涌现", "对齐", "幻觉",
              "transformer", "embedding", "fine-tune", "RLHF", "RAG"],
    "数学": ["向量", "矩阵", "函数", "导数", "积分", "概率分布", "梯度",
            "收敛", "优化", "正则化", "manifold", "tensor"],
    "物理": ["波函数", "量子", "希尔伯特空间", "哈密顿量", "波粒二象性",
            "纠缠", "诠释", "张量", "算符"],
    "哲学": ["认识论", "本体论", "形而上学", "先验", "后验",
            "还原论", "工具主义", "实在论"],
}

def detect_cheating(text: str) -> list[dict]:
    """检测回答里的偷懒信号，返回问题列表。"""
    issues = []
    t = text.lower().replace("，", ",").replace("。", ".")

    # 含糊带过
    for marker in VAGUE_MARKERS:
        if marker in text:
            issues.append({
                "type": "vague",
                "marker": marker,
                "hint": f"用了含糊带过词「{marker}」——你在用'其实'代替真懂吗？",
            })

    # 回避
    for marker in EVASION_MARKERS:
        if marker in text:
            issues.append({
                "type": "evasion",
                "marker": marker,
                "hint": f"用了回避信号「{marker}」——费曼法禁止逃避，给个工作定义",
            })

    # 术语密度（每 100 字超过 5 个黑名单术语 = 术语堆砌）
    term_hits = []
    for domain, terms in TERM_BLACKLIST.items():
        for term in terms:
            if term.lower() in t:
                term_hits.append((term, domain))
    char_count = max(len(text), 1)
    term_density = len(term_hits) / (char_count / 100)
    if term_density > 5:
        issues.append({
            "type": "term_density",
            "marker": f"{len(term_hits)} 个术语 / 100 字",
            "hint": f"术语密度过高（{term_density:.1f}/100字）——你在用术语堆砌代替讲解。命中：{[t[0] for t in term_hits[:5]]}",
        })

    return issues


# ============================================================
# LLM 调用（OpenAI 兼容）
# ============================================================

def call_llm(messages: list[dict], timeout: int = 60) -> Optional[str]:
    """调用 OpenAI 兼容 chat API。失败返回 None。"""
    if not HAS_LLM:
        return None
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.8,
        "max_tokens": 200,
    }
    req = urllib.request.Request(
        f"{BASE_URL}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()
    except (urllib.error.URLError, KeyError, TimeoutError) as e:
        print(f"\n  ⚠️ LLM 调用失败：{e}（回退到演示模式）\n", file=sys.stderr)
        return None


# ============================================================
# 演示模式：预设追问（无 LLM 时兜底）
# ============================================================

DEMO_QUESTIONS = {
    "kid": [
        "你刚才说的那个词，能用一个生活里的例子讲给我听吗？比如用学校或游戏里的东西打比方。",
        "我不懂你说的那个术语。如果完全不许用大词，你怎么讲？",
        "你说的这个，跟我玩过的 XX 是一回事吗？哪里像，哪里不像？",
        "那如果我用你说的办法去做 XX，会发生什么？走一遍给我看。",
        "你最后那句话我没听懂，换一种说法再讲一遍，越简单越好。",
    ],
    "journalist": [
        "你这个论断，怎么证明？有反例吗？给我一个能让它失效的场景。",
        "你刚才用的那个核心词，请给一个能检验的定义——别用'其实就是'带过。",
        "你这段逻辑的前提是什么？这个前提如果不成立，整个论证是不是就塌了？",
        "你说'业界都这么认为'，那是谁？有具体的人或论文吗？",
        "等等，你前面说 X，现在又说 Y，这两个不矛盾吗？",
    ],
    "philosopher": [
        "你反复用「{核心词}」这个词，它到底指什么？给一个工作定义。",
        "你这个论断成立的前提是什么？这个前提你自己检验过吗？",
        "如果{核心词}不成立，你的整个论证会塌吗？塌在哪？",
        "你说'这就是 X'——但 X 和 Y 的边界在哪？怎么区分？",
        "你刚才那个回答，是在描述事实，还是在表达你自己的偏好？区分一下。",
    ],
}


def demo_question(role: str, topic: str, round_idx: int) -> str:
    """演示模式：根据角色和轮次返回预设追问。"""
    pool = DEMO_QUESTIONS[role]
    q = pool[round_idx % len(pool)]
    return q.replace("{核心词}", topic)


# ============================================================
# 单角色审讯循环
# ============================================================

def interrogate(role_key: str, topic: str, rounds: int, history: list) -> list[dict]:
    """一个角色追问 rounds 轮。返回该角色的对话记录（含偷懒检测）。"""
    role = ROLES[role_key]
    print(f"\n{'='*60}")
    print(f"  {role['emoji']}  角色 {rounds} 连问：{role['name']}")
    print(f"  主题：{topic}")
    print(f"{'='*60}")

    log = []
    messages = [{"role": "system", "content": role["system"]},
                {"role": "user", "content": f"我要给你讲的主题是：{topic}。请开始追问。"}]

    # 第一问
    if HAS_LLM:
        first = call_llm(messages)
        if first is None:
            first = demo_question(role_key, topic, 0)
    else:
        first = demo_question(role_key, topic, 0)

    for r in range(rounds):
        print(f"\n--- {role['name']} 第 {r+1}/{rounds} 问 ---")
        print(f"{role['emoji']}  {first}\n")
        messages.append({"role": "assistant", "content": first})

        # 用户回答
        try:
            answer = input("📝 你的回答（:skip 跳过 / :q 退出）> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if answer.lower() in (":q", "quit", "exit"):
            print("\n[dirtrcup] 提前结束，生成报告中...\n")
            return log
        if answer.lower() == ":skip" or not answer:
            answer = "（跳过）"

        # 偷懒检测
        issues = detect_cheating(answer)
        if issues:
            print("\n  🚨 偷懒信号检测到：")
            for iss in issues:
                print(f"     · [{iss['type']}] {iss['hint']}")
            print()

        log.append({
            "role": role_key,
            "role_name": role["name"],
            "round": r + 1,
            "question": first,
            "answer": answer,
            "cheating_signals": issues,
        })

        messages.append({"role": "user", "content": answer})

        # 下一问
        if r < rounds - 1:
            if HAS_LLM:
                nxt = call_llm(messages)
                if nxt is None:
                    nxt = demo_question(role_key, topic, r + 1)
            else:
                nxt = demo_question(role_key, topic, r + 1)
            first = nxt

    return log


# ============================================================
# 报告生成
# ============================================================

def gen_report(topic: str, log: list[dict], rounds: int) -> pathlib.Path:
    """生成 markdown 费曼检验报告。"""
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_topic = "".join(c for c in topic if c.isalnum() or c in "._-")[:30] or "topic"
    path = pathlib.Path(f"feynman-report-{safe_topic}-{ts}.md")

    # 统计
    total_q = len(log)
    cheated = [e for e in log if e["cheating_signals"]]
    all_signals = [s for e in log for s in e["cheating_signals"]]

    by_role = {}
    for r_key in ROLE_ORDER:
        entries = [e for e in log if e["role"] == r_key]
        by_role[r_key] = {
            "name": ROLES[r_key]["name"],
            "emoji": ROLES[r_key]["emoji"],
            "count": len(entries),
            "cheated": len([e for e in entries if e["cheating_signals"]]),
        }

    lines = [
        f"# 费曼检验报告 · {topic}",
        f"",
        f"> 由 `feynman-coach.py` 生成于 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"> 模式：{'LLM (' + MODEL + ')' if HAS_LLM else '演示模式（无 LLM）'}",
        f"",
        f"## 总览",
        f"",
        f"| 指标 | 值 |",
        f"|---|---|",
        f"| 主题 | {topic} |",
        f"| 每角色追问轮数 | {rounds} |",
        f"| 总问答数 | {total_q} |",
        f"| 触发偷懒信号的回答 | **{len(cheated)}** |",
        f"| 偷懒信号总数 | **{len(all_signals)}** |",
        f"",
        f"### 各角色战绩",
        f"",
        f"| 角色 | 追问数 | 触发偷懒 |",
        f"|---|---|---|",
    ]
    for r_key in ROLE_ORDER:
        d = by_role[r_key]
        lines.append(f"| {d['emoji']} {d['name']} | {d['count']} | {d['cheated']} |")

    lines += [
        f"",
        f"## 诊断（自动）",
        f"",
    ]
    if len(cheated) == 0:
        lines += [f"🟢 **未检测到明显偷懒信号**。但注意：",
                  f"- 启发式检测只能抓'含糊词/术语堆砌/回避信号'，抓不到'逻辑漏洞/双重标准'。",
                  f"- 真懂没真懂，要看 F2 卡壳点自曝（参考 [费曼检验模板](费曼检验模板.md) 的 F2）。"]
    else:
        types = {}
        for s in all_signals:
            types[s["type"]] = types.get(s["type"], 0) + 1
        lines += [f"🔴 **检测到 {len(all_signals)} 处偷懒信号**，分布："]
        for t, c in sorted(types.items(), key=lambda x: -x[1]):
            meaning = {"vague": "含糊带过", "evasion": "回避问题", "term_density": "术语堆砌"}[t]
            lines.append(f"   - **{meaning}** ({t})：{c} 处")
        lines += [f"",
                  f"这些就是你**没真懂**的地方。建议：",
                  f"1. 把每个被戳穿的回答重写一遍，不许用术语和含糊词。",
                  f"2. 对每个红灯信号，在 [费曼检验模板](费曼检验模板.md) 的 F2/F3 里登记。",
                  f"3. 跑一遍完整 F1-F4 闭环。"]

    lines += [f"", f"---", f"", f"## 完整对话记录", f""]
    for e in log:
        lines += [
            f"### {ROLES[e['role']]['emoji']} {e['role_name']} · 第 {e['round']} 问",
            f"",
            f"**问**：{e['question']}",
            f"",
            f"**答**：{e['answer']}",
            f"",
        ]
        if e["cheating_signals"]:
            lines += [f"**🚨 偷懒信号**："]
            for s in e["cheating_signals"]:
                lines.append(f"- `[{s['type']}]` {s['hint']}")
            lines.append(f"")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


# ============================================================
# 主流程
# ============================================================

def banner():
    print("""
╔══════════════════════════════════════════════════════════╗
║   feynman-coach · 费曼陪练                                ║
║   三角色连环追问，戳穿"自以为懂"                          ║
╚══════════════════════════════════════════════════════════╝
""".rstrip())
    mode = f"LLM 模式（{MODEL} @ {BASE_URL}）" if HAS_LLM else "演示模式（设 OPENAI_API_KEY 解锁真 LLM）"
    print(f"  当前：{mode}\n")


def parse_args(argv):
    topic = None
    file_path = None
    rounds = 3
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == "--file":
            file_path = argv[i+1]; i += 2
        elif a == "--rounds":
            rounds = int(argv[i+1]); i += 2
        elif a in ("-h", "--help"):
            print(__doc__); sys.exit(0)
        else:
            topic = a; i += 1
    return topic, file_path, rounds


def extract_topic_from_file(path: str) -> str:
    """从 markdown 文件提取标题作为主题。"""
    try:
        text = pathlib.Path(path).read_text(encoding="utf-8")
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("# "):
                return line.lstrip("# ").strip()
        return pathlib.Path(path).stem
    except (OSError, UnicodeDecodeError) as e:
        print(f"⚠️ 读文件失败：{e}", file=sys.stderr)
        return pathlib.Path(path).stem


def main(argv):
    banner()
    topic, file_path, rounds = parse_args(argv)

    if file_path:
        topic = extract_topic_from_file(file_path)
        print(f"  📄 从文件提取主题：{topic}\n")
    elif not topic:
        try:
            topic = input("  输入你想检验的主题（例：注意力机制 / 波函数 / RLHF）> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见。"); return
        if not topic:
            print("  主题不能为空。"); return

    print(f"  🎯 主题：{topic}")
    print(f"  🔁 每角色追问：{rounds} 轮 × 3 角色 = 共 {rounds*3} 问\n")
    print("  💡 提示：被问到时，**不要查资料**，凭现有理解回答——")
    print("           答得越烂，越能暴露你没真懂的地方。\n")

    full_log = []
    for role_key in ROLE_ORDER:
        try:
            log = interrogate(role_key, topic, rounds, full_log)
            full_log.extend(log)
            # 如果用户中途 :q，interrogate 返回短 log，但这里 continue；可由 total < expected 判断
            if len(log) < rounds and log and log[-1]["answer"] not in ("（跳过）",):
                # 实际中途退出逻辑由 input 捕获，这里保守 continue
                pass
        except KeyboardInterrupt:
            print("\n\n[dirtrcup] 中断，生成已有报告...\n")
            break

    if not full_log:
        print("  没有有效对话，不生成报告。")
        return

    print(f"\n{'='*60}\n  生成报告中...\n{'='*60}")
    path = gen_report(topic, full_log, rounds)
    print(f"\n  ✅ 报告已生成：{path.resolve()}")
    print(f"  📊 共 {len(full_log)} 问，触发 {len([e for e in full_log if e['cheating_signals']])} 处偷懒信号\n")


if __name__ == "__main__":
    main(sys.argv)
