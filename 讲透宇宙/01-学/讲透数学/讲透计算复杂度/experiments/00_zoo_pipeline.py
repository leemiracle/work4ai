#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""00_zoo_pipeline.py — Complexity Zoo wiki → 结构化数据（图鉴生产的地基）

复杂度动物园(complexityzoo.net)每个类在字母页 raw wikitext 里是一段：

    ===== <span id="xx" style="color:red">类名</span>: 英文全称 =====
    定义与包含关系的原文……
    ----

本脚本把 27 个字母页切成结构化条目（id/类名/全称/原文/原文链接），
按 span id 去重得权威清单，并给出图鉴分卷方案——
这是"非结构化百科 → 可验证数据"的通用管线演示（07 章的活教具）。

用法（raw 缓存用 curl 抓取，见 .research/complexity-zoo/raw/）：
    python 00_zoo_pipeline.py <raw目录> <输出json>
例（在仓库根执行）：
    python 讲透数学/讲透计算复杂度/experiments/00_zoo_pipeline.py \
        .research/complexity-zoo/raw .research/complexity-zoo/zoo_parsed.json
"""
import html
import itertools
import json
import re
import sys
from pathlib import Path

LETTERS = ["SYM"] + [chr(c) for c in range(ord("A"), ord("Z") + 1)]


def strip_tags(s: str) -> str:
    """wikitext/HTML 杂交串 → 纯文本：去标签、解实体、展平空白。"""
    s = re.sub(r"<math>.*?</math>", "", s)              # 行内公式占位
    s = re.sub(r"\[\[[^]|]*\|([^\]]*)\]\]", r"\1", s)   # [[页|显示]] -> 显示
    s = re.sub(r"\[\[([^\]]*)\]\]", r"\1", s)           # [[页]]     -> 页
    s = s.replace("<sub>", "_").replace("<sup>", "^")   # 上下标转 ASCII 后缀
    s = re.sub(r"<[^>]+>", "", s)                       # 其余 HTML 标签
    s = html.unescape(s)                                # &#931; -> Σ 等
    return re.sub(r"\s+", " ", s).strip()


HEAD = re.compile(r'<span id="([^"]+)"[^>]*>(.*?)</span>\s*:?\s*(.*?)\s*=+', re.S)


def parse_page(text: str, letter: str) -> list:
    """一个字母页 → 词条列表；非'类'词条的 ===== 段（无 span id）跳过。"""
    out = []
    chunks = re.split(r"^===== ", text, flags=re.M)[1:]
    for ch in chunks:
        m = HEAD.match(ch)
        if not m:
            continue
        body = ch[m.end():]
        body = re.split(r"^----+\s*$", body, maxsplit=1, flags=re.M)[0]
        eid = m.group(1)
        out.append({
            "id": eid, "letter": letter,
            "name": strip_tags(m.group(2)), "title": strip_tags(m.group(3)),
            "body": re.sub(r"\s+", " ", body).strip()[:4000],
            "url": f"https://complexityzoo.net/Complexity_Zoo:{letter}#{eid}",
        })
    return out


def volumes(entries: list) -> list:
    """字母序连续切分：整字母边界、卷数 6±1，极小化最大-最小卷差。

    字母仅 ~26 个，所有切点组合穷举即可（C(25,5)≈5.3 万），确定性最优。
    """
    by_l = {l: sum(1 for e in entries if e["letter"] == l) for l in LETTERS}
    by_l = {l: n for l, n in by_l.items() if n}
    ls = [l for l in LETTERS if l in by_l]           # 保持字母序
    total = sum(by_l.values())
    best = None
    for k in (6, 5, 7):                              # spec D5：预计 6 卷优先，±1 兜底
        if k >= len(ls):
            continue
        cand = None
        for cuts in itertools.combinations(range(1, len(ls)), k - 1):
            groups, prev = [], 0
            for c in list(cuts) + [len(ls)]:
                groups.append(ls[prev:c])
                prev = c
            sizes = [sum(by_l[x] for x in g) for g in groups]
            score = (max(sizes) - min(sizes)) + 2 * max(0, max(sizes) - 140)
            if cand is None or score < cand[0]:
                cand = (score, groups, sizes)
        if cand[2] and max(cand[2]) <= 140:          # k=6 可行即定案
            best = cand
            break
        if best is None or cand[0] < best[0]:
            best = cand
    _, groups, sizes = best
    vols = []
    for i, (g, n) in enumerate(zip(groups, sizes), 1):
        lo = "符号" if g[0] == "SYM" else g[0]
        hi = g[-1] if g[-1] != "SYM" else "符号"
        name = f"卷{i}-{lo}至{hi}.md" if lo != hi else f"卷{i}-{lo}.md"
        if i == 1 and g[0] == "SYM":
            name = f"卷1-符号与{g[1]}至{hi}.md" if len(g) > 2 else f"卷1-符号与{hi}.md"
        vols.append((name, n, "".join(x for x in g if x != "SYM") or "SYM"))
    return vols


def main():
    raw_dir, out_json = Path(sys.argv[1]), Path(sys.argv[2])
    entries, seen, dupes = [], set(), []
    for f in sorted(raw_dir.glob("Zoo_*.txt")):
        letter = "SYM" if f.stem == "Zoo_SYM" else f.stem.split("_")[1]
        for e in parse_page(f.read_text(encoding="utf-8", errors="replace"), letter):
            key = (e["letter"], e["id"])
            if key in seen:
                dupes.append(key)
                continue
            seen.add(key)
            entries.append(e)
    order = {l: i for i, l in enumerate(LETTERS)}
    entries.sort(key=lambda e: (order[e["letter"]], e["id"]))
    out_json.write_text(json.dumps(entries, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"去重总数: {len(entries)}   (同字母内重复丢弃: {dupes or '无'})")
    per = {}
    for e in entries:
        per[e["letter"]] = per.get(e["letter"], 0) + 1
    print("逐字母:", {k: per[k] for k in sorted(per, key=lambda x: order.get(x, 99))})
    print(f"分卷方案（文件名 / 条数 / 字母范围，共 {len(volumes(entries))} 卷）:")
    for name, n, rng in volumes(entries):
        print(f"    {name:<28} {n:>3} 条   [{rng}]")
    assert len(entries) > 500, "总数异常，检查抓取完整性"


if __name__ == "__main__":
    main()
