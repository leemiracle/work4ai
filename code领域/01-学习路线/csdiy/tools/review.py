#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
review.py — 间隔重复复习模式（SM-2 简化版，标准库实现）

逐张出卡 → 你回想后回车看答案 → 自评 简单(1)/一般(2)/困难(3)，
按 SM-2 简化算法调度下次出现间隔。状态持久化到 .daily_state.json。

用法:
    python3 tools/review.py            # 复习所有「到期」的卡（默认）
    python3 tools/review.py --limit 20 # 最多复习 20 张
    python3 tools/review.py --all      # 复习全部（不止到期的）
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import random
import sys
from pathlib import Path
from typing import Any

# 复用 daily.py 的加载逻辑（同目录导入）
sys.path.insert(0, str(Path(__file__).resolve().parent))
import daily  # noqa: E402

TODAY = dt.date.today()
TODAY_STR = TODAY.isoformat()

# --------------------------------------------------------------------------- #
#  SM-2 简化调度
# --------------------------------------------------------------------------- #
# 评分映射：自评档 -> SM-2 quality
#   困难(3) -> q=2  （未掌握：重置进度，明天再来）
#   一般(2) -> q=3  （勉强：进度推进，间隔逐步增长）
#   简单(1) -> q=5  （熟练：间隔快速增长）
GRADE_TO_Q = {3: 2, 2: 3, 1: 5}


def schedule(card_st: dict[str, Any], grade: int) -> dict[str, Any]:
    """根据自评 grade(1/2/3) 更新单张卡的 SM-2 调度状态。

    返回更新后的 {interval, reps, ease, due, wrong, last_rating}。
    """
    q = GRADE_TO_Q.get(grade, 3)
    interval = card_st.get("interval", 0)
    reps = card_st.get("reps", 0)
    ease = card_st.get("ease", 2.5)
    wrong = card_st.get("wrong", 0)

    if q < 3:                       # 困难：重来
        reps = 0
        interval = 1
        wrong += 1
    else:                           # 一般 / 简单：推进
        if reps == 0:
            interval = 1
        elif reps == 1:
            interval = 3
        else:
            interval = max(1, round(interval * ease))
        reps += 1

    # 更新 ease（SM-2 公式：EF = EF + (0.1 - (5-q)(0.08+(5-q)0.02))）
    ease = ease + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    ease = max(1.3, ease)

    due = (TODAY + dt.timedelta(days=interval)).isoformat()
    return {"interval": interval, "reps": reps, "ease": round(ease, 3),
            "due": due, "wrong": wrong, "last_rating": grade}


def collect_due(cards: list[dict[str, str]], state: dict[str, Any],
                include_all: bool, limit: int | None) -> list[dict[str, str]]:
    """挑选要复习的卡：默认只选今天到期的；按到期日 + 答错次数排序。"""
    cs = state.get("cards", {})
    due_list: list[dict[str, str]] = []
    for c in cards:
        st = cs.get(c["front"])
        if include_all or st is None:
            due_list.append(c)
        elif st.get("due", TODAY_STR) <= TODAY_STR:
            due_list.append(c)
    # 排序：从未见过的先来；其次过期最久的；其次答错多的
    def sort_key(c: dict[str, str]) -> tuple:
        st = cs.get(c["front"], {})
        seen = 0 if st else 1
        due = st.get("due", "0000")
        wrong = -st.get("wrong", 0)
        return (seen, due, wrong)
    due_list.sort(key=sort_key)
    if limit:
        due_list = due_list[:limit]
    return due_list


# --------------------------------------------------------------------------- #
#  交互
# --------------------------------------------------------------------------- #
def prompt_grade() -> int | None:
    """读取用户自评，返回 1/2/3；空行=跳过(None)；q=退出。"""
    hint = daily.yellow("自评：") + daily.green("[1]简单 ") + \
           daily.cyan("[2]一般 ") + daily.red("[3]困难 ") + \
           daily.dim("(回车跳过 / q退出) > ")
    while True:
        try:
            ans = input(hint).strip().lower()
        except EOFError:
            return None
        if ans in ("", "s", " "):
            return None
        if ans in ("q", "quit", "exit"):
            return "quit"  # type: ignore[return-value]
        if ans in ("1", "2", "3"):
            return int(ans)
        print(daily.dim("  请输入 1 / 2 / 3，或回车跳过，或 q 退出。"))


def show_stats(state: dict[str, Any], cards: list[dict[str, str]]) -> None:
    """打印当前复习队列概况。"""
    cs = state.get("cards", {})
    due_n = sum(1 for c in cards
                if cs.get(c["front"], {}).get("due", TODAY_STR) <= TODAY_STR)
    learned = sum(1 for c in cards if c["front"] in cs)
    print(daily.banner("🧠", "间隔复习", daily.magenta))
    print(f"  {daily.bold(f'{len(cards)}')} 张卡 · "
          f"{daily.bold(f'{learned}')} 已学 · "
          f"{daily.bold(f'{due_n}')} 今日到期\n")


def run_review(args: argparse.Namespace) -> int:
    cards = daily.load_cards()
    if not cards:
        print(daily.yellow("卡片库为空，请先准备 cards/anki.tsv"))
        return 1

    state = daily.load_state()
    queue = collect_due(cards, state, args.all, args.limit)
    if not queue:
        print(daily.green("\n✅ 没有到期卡片，今天的复习已完成！下次见 🎉"))
        return 0

    show_stats(state, cards)
    print(daily.dim(f"本轮复习 {len(queue)} 张，回车翻答案，输 q 可随时退出。\n"))

    reviewed = 0
    rng = random.Random()
    rng.shuffle(queue)

    for i, card in enumerate(queue, 1):
        cs = state.setdefault("cards", {})
        st = cs.get(card["front"], {})
        due_label = st.get("due", "新卡")
        intv = st.get("interval", "-")

        print(daily.dim(f"── {i}/{len(queue)} ──")
              + daily.dim(f"  (上次间隔 {intv}d, 到期 {due_label})"))
        print(f"{daily.magenta('[' + card['tag'] + ']')} "
              f"{daily.bold(card['front'])}")
        try:
            input(daily.dim("回车看答案 > "))
        except EOFError:
            break
        print(daily.green(card["back"]))
        print()

        grade = prompt_grade()
        if grade == "quit":
            print(daily.dim("\n已退出。"))
            break
        if grade is None:
            print(daily.dim("  (跳过，不更新进度)\n"))
            continue

        cs[card["front"]] = schedule(st, grade)
        nxt = cs[card["front"]]
        word = {1: daily.green("简单"), 2: daily.cyan("一般"),
                3: daily.red("困难")}[grade]
        print(daily.dim(f"  {word} → 下次 {nxt['due']} "
                        f"(间隔 {nxt['interval']}d, "
                        f"ease {nxt['ease']})\n"))
        reviewed += 1
        daily.save_state(state)

    print(daily.banner("✅", "复习结束", daily.green))
    print(f"  本轮复习 {daily.bold(str(reviewed))} 张。")
    # 复习也会更新今日 history 标记
    hist = state.setdefault("history", {}).setdefault(TODAY_STR, {})
    hist["review"] = f"复习 {reviewed} 张"
    daily.save_state(state)
    return 0


def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="review.py",
        description="间隔重复复习（SM-2 简化版）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="评分档：1=简单 2=一般 3=困难\n"
               "简单/一般会推进间隔，困难会重置。",
    )
    p.add_argument("--limit", type=int, default=None, help="最多复习多少张")
    p.add_argument("--all", action="store_true", help="复习全部（不止到期的）")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_argparser().parse_args(argv)
    try:
        return run_review(args)
    except KeyboardInterrupt:
        print(daily.dim("\n已中断，进度已保存。"))
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
