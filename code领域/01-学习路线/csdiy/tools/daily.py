#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
daily.py — 程序员每日训练器（标准库实现，零外部依赖）

每天打开终端抽一张挑战卡 + 一个 debug 场景 + 一条命令 + 一个 lab 小练习 +
今日学习路径推进。卡牌按上次答错加权抽取，状态持久化到 .daily_state.json。

用法:
    python3 tools/daily.py                  # 今日全套训练套餐
    python3 tools/daily.py --mode card      # 只抽卡
    python3 tools/daily.py --mode debug     # 只抽 debug 场景
    python3 tools/daily.py --mode command   # 只抽命令
    python3 tools/daily.py --mode lab       # 只抽 lab 练习
    python3 tools/daily.py --mode track     # 只看学习路径推进
    python3 tools/daily.py --history        # 看本周练了什么
    python3 tools/daily.py --seed N         # 固定随机种子（可复现）
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import random
import re
import sys
from pathlib import Path
from typing import Any

# --------------------------------------------------------------------------- #
#  路径与常量
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parent.parent          # csdiy 仓库根
STATE_FILE = ROOT / ".daily_state.json"
CARDS_FILE = ROOT / "cards" / "anki.tsv"
NOTES_DIR = ROOT / "notes"
CHEATS_DIR = ROOT / "cheatsheets"
LABS_DIR = ROOT / "labs"
TRACKS_FILE = ROOT / "paths" / "tracks.json"

TODAY = dt.date.today()
TODAY_STR = TODAY.isoformat()

# --------------------------------------------------------------------------- #
#  ANSI 颜色（自动在非 TTY 时关闭）
# --------------------------------------------------------------------------- #
_USE_COLOR = sys.stdout.isatty()


def _c(code: str, text: str) -> str:
    """给文本加 ANSI 颜色，非终端或 NO_COLOR 时返回原文。"""
    if not _USE_COLOR or os.environ.get("NO_COLOR"):
        return text
    return f"\033[{code}m{text}\033[0m"


def red(t: str) -> str:    return _c("31", t)
def green(t: str) -> str:  return _c("32", t)
def yellow(t: str) -> str: return _c("33", t)
def blue(t: str) -> str:   return _c("34", t)
def magenta(t: str) -> str: return _c("35", t)
def cyan(t: str) -> str:   return _c("36", t)
def bold(t: str) -> str:   return _c("1", t)
def dim(t: str) -> str:    return _c("2", t)


def banner(emoji: str, title: str, color=cyan) -> str:
    """生成一个带分隔线的区块标题。"""
    line = "─" * 52
    return f"\n{color(bold(f' {emoji}  {title} '))}\n{dim(line)}"


# --------------------------------------------------------------------------- #
#  状态管理（.daily_state.json）
# --------------------------------------------------------------------------- #
def load_state() -> dict[str, Any]:
    """读取持久化状态，文件缺失或损坏时返回空骨架。"""
    default: dict[str, Any] = {
        "cards": {},        # 卡牌调度状态 {front: {interval,reps,ease,due,wrong}}
        "history": {},      # 每日训练记录 {date: {card,debug,command,lab,track}}
        "track_progress": {},  # 各学习路径推进进度 {track_key: step_index}
    }
    if not STATE_FILE.exists():
        return default
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            for k, v in default.items():
                data.setdefault(k, v)
            return data
    except (json.JSONDecodeError, OSError):
        pass
    return default


def save_state(state: dict[str, Any]) -> None:
    """原子化写入状态文件（先写临时文件再替换，避免半写损坏）。"""
    try:
        tmp = STATE_FILE.with_suffix(".tmp")
        tmp.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        tmp.replace(STATE_FILE)
    except OSError as exc:
        print(yellow(f"[warn] 状态保存失败: {exc}"), file=sys.stderr)


# --------------------------------------------------------------------------- #
#  数据加载（全部带容错）
# --------------------------------------------------------------------------- #
def load_cards() -> list[dict[str, str]]:
    """解析 anki.tsv（front<TAB>back<TAB>tag），返回卡片列表。

    对格式异常的行尽力解析：至少取第一列，其余置空。
    """
    cards: list[dict[str, str]] = []
    if not CARDS_FILE.exists():
        return cards
    try:
        raw = CARDS_FILE.read_text(encoding="utf-8")
    except OSError:
        return cards
    for line in raw.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        front = parts[0].strip() if len(parts) > 0 else ""
        back = parts[1].strip() if len(parts) > 1 else ""
        tag = parts[2].strip() if len(parts) > 2 else "未分类"
        if front:
            cards.append({"front": front, "back": back, "tag": tag})
    return cards


def _split_sections(md: str) -> list[tuple[str, str]]:
    """把 markdown 按 ``## `` 二级标题切分，返回 [(标题, 正文), ...]。

    跳过以「附录 / 总结 / 速查 / Lab 速查 / 横向」等非场景性标题开头的章节。
    正文含到下一个 ``## `` 之前的全部内容。
    """
    sections: list[tuple[str, str]] = []
    # 匹配行首的 ## 标题
    pattern = re.compile(r"^##\s+(.+?)$", re.M)
    matches = list(pattern.finditer(md))
    skip_kw = ("附录", "一句话总结", "Lab 速查", "横向", "心智模型", "最常用")
    for i, m in enumerate(matches):
        title = m.group(1).strip()
        if any(k in title for k in skip_kw):
            continue
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md)
        body = md[start:end].strip()
        sections.append((title, body))
    return sections


def load_debug_scenarios() -> list[dict[str, str]]:
    """从 notes/ 的 OS / CSAPP 笔记抽取 debug 场景。

    每个场景包含：title(节标题) / hook(第一个 ### 子标题) / story(其后的故事段落)。
    """
    scenarios: list[dict[str, str]] = []
    files = []
    if NOTES_DIR.exists():
        files = sorted(NOTES_DIR.glob("*.md"))
    for f in files:
        try:
            md = f.read_text(encoding="utf-8")
        except OSError:
            continue
        for title, body in _split_sections(md):
            # 找第一个 ### 子标题作为「引导问题」
            sub_m = re.search(r"^###\s+(.+?)$", body, re.M)
            hook = sub_m.group(1).strip() if sub_m else "事故现场"
            # 故事段落 = 第一个 ### 之后到下一个 ###/``` 之前的文本
            story = ""
            if sub_m:
                after = body[sub_m.end():]
                # 截到下一个 ### 或代码块
                cut = re.search(r"^###|^```", after, re.M)
                story = (after[: cut.start()] if cut else after).strip()
                story = re.sub(r"\s+", " ", story)[:220]
            source_map = {
                "code": "CODE REVIEW", "csapp": "CSAPP", "db": "DB",
                "network": "网络", "os": "OS", "perf": "性能",
            }
            prefix = f.stem.split("-")[0].lower()
            source = source_map.get(prefix, prefix.upper())
            scenarios.append({
                "title": title,
                "hook": hook,
                "story": story,
                "source": source,
            })
    return scenarios


def load_command_blocks() -> list[dict[str, str]]:
    """从 cheatsheets/ 抽取所有命令块（任意围栏代码块）。

    每条含：title(最近的 ## 标题) / code(代码块内容) / file(来源文件名)。
    """
    blocks: list[dict[str, str]] = []
    if not CHEATS_DIR.exists():
        return blocks
    for f in sorted(CHEATS_DIR.glob("*.md")):
        try:
            md = f.read_text(encoding="utf-8")
        except OSError:
            continue
        # 记录所有 ## 标题的位置
        headers = {m.start(): m.group(1).strip()
                   for m in re.finditer(r"^##\s+(.+?)$", md, re.M)}
        # 匹配成对的 ``` 围栏
        fence_iter = list(re.finditer(r"^```[^\n]*\n(.*?)^```", md, re.M | re.S))
        for blk in fence_iter:
            pos = blk.start()
            code = blk.group(1).strip()
            if not code:
                continue
            # 找该代码块之前最近的标题
            label = "速查"
            for hpos in sorted(headers, reverse=True):
                if hpos < pos:
                    label = headers[hpos]
                    break
            blocks.append({
                "title": label,
                "code": code,
                "file": f.stem.replace("-场景速查", "").replace("速查", ""),
            })
    return blocks


def load_lab_exercises() -> list[dict[str, str]]:
    """从 labs/ 抽取练习。每个 .md 文件取标题 + 第一个实操章节。"""
    exercises: list[dict[str, str]] = []
    if not LABS_DIR.exists():
        return exercises
    for f in sorted(LABS_DIR.glob("*.md")):
        try:
            md = f.read_text(encoding="utf-8")
        except OSError:
            continue
        # 文件级标题（# 一级标题或文件名）
        title_m = re.search(r"^#\s+(.+?)$", md, re.M)
        title = title_m.group(1).strip() if title_m else f.stem
        # 找第一个非「环境要求/一句话」的实操 ## 章节
        section = ""
        for sec_m in re.finditer(r"^##\s+(.+?)$(.*?)(?=^##\s|\Z)", md, re.M | re.S):
            sec_title = sec_m.group(1).strip()
            if any(k in sec_title for k in ("环境", "一句话", "验证", "成功标志",
                                            "下一步", "常见报错")):
                continue
            section = sec_m.group(2).strip()
            if section:
                break
        # 优先用文件引言段（# 标题后、第一个 ## 前）作为描述
        intro = ""
        intro_m = re.search(r"^#.+?\n(.*?)^##", md, re.M | re.S)
        if intro_m:
            intro = intro_m.group(1).strip()
        raw_desc = intro if intro else section
        # 清洗：去代码块、内联反引号代码、标题行、引用前缀
        desc = re.sub(r"```.*?```", "", raw_desc, flags=re.S)
        desc = re.sub(r"`([^`]*)`", r"\1", desc)   # 去反引号但保留代码内容
        desc = re.sub(r"^#{1,6}\s+.*$", "", desc, flags=re.M)
        desc = re.sub(r"^>", "", desc, flags=re.M)
        # 取第一个完整句子（到句号/问号/换行），避免截断命令片段
        first_sent = re.split(r"[。？\n]", desc, maxsplit=1)
        desc = first_sent[0].strip() if first_sent else desc
        desc = re.sub(r"\s+", " ", desc).strip()[:200]
        if not desc:
            desc = f"动手完成 {title} 的核心练习（参考 {f.name}）。"
        exercises.append({"title": title, "desc": desc, "file": f.name})
    return exercises


def load_tracks() -> list[dict[str, Any]]:
    """读取 paths/tracks.json，展平成 track 列表。"""
    tracks: list[dict[str, Any]] = []
    if not TRACKS_FILE.exists():
        return tracks
    try:
        data = json.loads(TRACKS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return tracks
    if not isinstance(data, dict):
        return tracks
    for key, info in data.items():
        if not isinstance(info, dict):
            continue
        steps = info.get("steps", []) or []
        tracks.append({
            "key": key,
            "name": info.get("name", key),
            "difficulty": info.get("difficulty", ""),
            "steps": steps,
        })
    return tracks


# --------------------------------------------------------------------------- #
#  选择逻辑
# --------------------------------------------------------------------------- #
def pick_card(cards: list[dict[str, str]], state: dict[str, Any],
              rng: random.Random) -> dict[str, str] | None:
    """加权抽取一张卡：答错次数越多权重越高，同时偏好「到期」的卡。"""
    if not cards:
        return None
    cards_state = state["cards"]
    weights = []
    for c in cards:
        st = cards_state.get(c["front"], {})
        wrong = st.get("wrong", 0)
        due = st.get("due", TODAY_STR) <= TODAY_STR  # 到期或过期权重更高
        w = 1.0 + wrong * 2.5 + (1.5 if due else 0.0)
        weights.append(w)
    return rng.choices(cards, weights=weights, k=1)[0]


def pick(scenarios: list[dict[str, str]], rng: random.Random) -> dict[str, str] | None:
    """均匀随机抽一个。"""
    return rng.choice(scenarios) if scenarios else None


def next_track_step(tracks: list[dict[str, Any]],
                    state: dict[str, Any]) -> dict[str, Any] | None:
    """挑选「完成率最低」的路径，返回其下一门未完成课程。

    完成率 = track_progress / 总步数；并列时取列表顺序靠前的。
    """
    if not tracks:
        return None
    prog = state["track_progress"]

    def ratio(t: dict[str, Any]) -> float:
        idx = prog.get(t["key"], 0)
        total = max(len(t["steps"]), 1)
        return idx / total

    # 选完成率最低且尚未跑完的路径
    candidates = [t for t in tracks if prog.get(t["key"], 0) < len(t["steps"])]
    if not candidates:
        return None
    best = min(candidates, key=ratio)
    idx = prog.get(best["key"], 0)
    step = best["steps"][idx]
    return {"track": best, "step": step, "index": idx,
            "remaining": len(best["steps"]) - idx}


# --------------------------------------------------------------------------- #
#  渲染各模块
# --------------------------------------------------------------------------- #
def wrap(text: str, width: int = 70) -> str:
    """中文友好的软换行（按字符宽度近似，宽字符计 2）。"""
    if not text:
        return ""
    out_lines: list[str] = []
    for para in text.split("\n"):
        cur = ""
        w = 0
        for ch in para:
            cw = 2 if ord(ch) > 0x2E80 else 1  # 粗略：CJK 计 2
            if w + cw > width and cur:
                out_lines.append(cur)
                cur = ch
                w = cw
            else:
                cur += ch
                w += cw
        out_lines.append(cur)
    return "\n".join(out_lines)


def render_card(card: dict[str, str]) -> str:
    tag = magenta(f"[{card['tag']}]")
    out = banner("🎯", "挑战卡", cyan)
    out += f"\n{tag} {bold(card['front'])}\n"
    out += f"\n{dim('— 先想想，再看答案 ↓')}\n"
    out += f"\n{green(card['back'])}\n"
    return out


def render_debug(sc: dict[str, str]) -> str:
    out = banner("🐛", "Debug 场景", red)
    src = dim(f"({sc['source']})")
    out += f"\n{bold(sc['title'])}  {src}\n"
    out += f"\n{yellow('▸ 引导问题：')}{sc['hook']}\n"
    if sc["story"]:
        out += f"\n{dim(wrap(sc['story'], 66))}\n"
    return out


def render_command(blk: dict[str, str]) -> str:
    out = banner("🔧", "今日命令", green)
    src = dim(f"({blk['file']})")
    out += f"\n{bold(blk['title'])}  {src}\n"
    out += f"\n{cyan(blk['code'])}\n"
    return out


def render_lab(lab: dict[str, str]) -> str:
    out = banner("📚", "Lab 小练习", blue)
    src = dim(f"({lab['file']})")
    out += f"\n{bold(lab['title'])}  {src}\n"
    out += f"\n{wrap(lab['desc'], 66)}\n"
    return out


def render_track(info: dict[str, Any]) -> str:
    track, step = info["track"], info["step"]
    idx, remaining = info["index"], info["remaining"]
    out = banner("🗺️", "学习路径推进", magenta)
    out += f"\n{bold(track['name'])} {dim(track['difficulty'])}"
    out += f"  ·  第 {idx + 1}/{len(track['steps'])} 门，还剩 {remaining} 门\n"
    out += f"\n  {green('▸')} {bold(step.get('course', ''))} — {step.get('title', '')}"
    out += f"\n    {dim('为什么：')}{step.get('why', '')}"
    out += f"\n    {dim('预计：')}{step.get('weeks', '?')} 周\n"
    return out


def render_header(state: dict[str, Any]) -> str:
    now = dt.datetime.now().strftime("%Y-%m-%d %a %H:%M")
    total = len(state.get("history", {}))
    return (f"\n{magenta(bold('⚡ 每日训练器'))} "
            f"{dim(now)}  {dim(f'(累计训练 {total} 天)')}")


# --------------------------------------------------------------------------- #
#  历史
# --------------------------------------------------------------------------- #
def show_history(state: dict[str, Any]) -> int:
    history = state.get("history", {})
    if not history:
        print(yellow("\n还没有训练记录，先跑一次 python3 tools/daily.py 吧。"))
        return 0
    week_ago = TODAY - dt.timedelta(days=7)
    recent = sorted(
        ((d, v) for d, v in history.items() if dt.date.fromisoformat(d) >= week_ago),
        key=lambda x: x[0],
        reverse=True,
    )
    print(banner("📖", "本周训练记录", blue))
    if not recent:
        print(dim("  （最近 7 天无记录）"))
    for d, v in recent:
        print(f"\n{bold(d)}")
        for key, label in [("card", "卡"), ("debug", "调试"),
                           ("command", "命令"), ("lab", "练习"),
                           ("track", "路径"), ("review", "复习")]:
            val = v.get(key)
            if val:
                print(f"  {label}: {dim(val)}")
    return 0


# --------------------------------------------------------------------------- #
#  主流程
# --------------------------------------------------------------------------- #
def run_daily(args: argparse.Namespace) -> int:
    rng = random.Random(args.seed if args.seed is not None
                        else int.from_bytes(os.urandom(4), "big"))
    state = load_state()

    cards = load_cards()
    debugs = load_debug_scenarios()
    commands = load_command_blocks()
    labs = load_lab_exercises()
    tracks = load_tracks()

    # 数据齐全度自检（缺了不影响运行，只提示）
    missing = [name for name, data in [
        ("anki.tsv", cards), ("notes", debugs),
        ("cheatsheets", commands), ("labs", labs), ("tracks.json", tracks),
    ] if not data]
    if missing:
        print(yellow(f"[提示] 以下题库为空或缺失: {', '.join(missing)}"),
              file=sys.stderr)

    print(render_header(state))

    mode = args.mode
    today_rec: dict[str, str] = {}

    if mode in (None, "card") and cards:
        card = pick_card(cards, state, rng)
        print(render_card(card))
        today_rec["card"] = card["front"]
    elif mode == "card":
        print(yellow("\n[卡片库为空] 请检查 cards/anki.tsv"))

    if mode in (None, "debug") and debugs:
        sc = pick(debugs, rng)
        print(render_debug(sc))
        today_rec["debug"] = sc["title"]
    elif mode == "debug":
        print(yellow("\n[debug 场景库为空] 请检查 notes/ 目录"))

    if mode in (None, "command") and commands:
        blk = pick(commands, rng)
        print(render_command(blk))
        today_rec["command"] = blk["title"]
    elif mode == "command":
        print(yellow("\n[命令库为空] 请检查 cheatsheets/ 目录"))

    if mode in (None, "lab") and labs:
        lab = pick(labs, rng)
        print(render_lab(lab))
        today_rec["lab"] = lab["title"]
    elif mode == "lab":
        print(yellow("\n[lab 库为空] 请检查 labs/ 目录"))

    if mode in (None, "track") and tracks:
        info = next_track_step(tracks, state)
        if info:
            print(render_track(info))
            today_rec["track"] = f"{info['track']['name']} › {info['step'].get('course', '')}"
        elif mode == "track":
            print(yellow("\n[所有路径已完成] 🎉"))
    elif mode == "track":
        print(yellow("\n[路径库为空] 请检查 paths/tracks.json"))

    # 记录今日历史（仅全套或有效模式下写入）
    if today_rec:
        state.setdefault("history", {})[TODAY_STR] = today_rec
        save_state(state)

    print(dim("\n" + "═" * 56))
    print(dim(f"完成训练？用 {bold('python3 tools/review.py')} 进入间隔复习模式。"))
    return 0


def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="daily.py",
        description="程序员每日训练器：抽卡 / debug 场景 / 命令 / lab / 学习路径",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例:\n"
               "  python3 tools/daily.py            # 今日全套\n"
               "  python3 tools/daily.py --mode lab # 只抽 lab\n"
               "  python3 tools/daily.py --history  # 看本周记录",
    )
    p.add_argument("--mode", choices=["card", "debug", "command", "lab", "track"],
                   help="只输出某一个模块")
    p.add_argument("--history", action="store_true", help="查看本周训练记录")
    p.add_argument("--seed", type=int, default=None, help="固定随机种子（可复现）")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_argparser().parse_args(argv)
    if args.history:
        return show_history(load_state())
    try:
        return run_daily(args)
    except KeyboardInterrupt:
        print(dim("\n已中断。"))
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
