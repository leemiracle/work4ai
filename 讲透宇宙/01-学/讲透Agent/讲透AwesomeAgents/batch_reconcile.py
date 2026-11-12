#!/usr/bin/env python3
"""批量 reconcile 终判（dw_reconcile_full.py 的参数化移植，讲透AwesomeAgents 轮）。

输入：_ledger.tsv 中 status==INCOMPLETE 的仓（全部为 written>structure 的 extra 假阴性疑似）。
判定：解析 _structure.txt 全层级标题 vs 落盘页归一化匹配（AAIF 轮钉版 40 字符前缀启发式），
  MISSING=0 → FINAL_100，结论追加写回该仓 _coverage-check.md，台账更新；
  MISSING>0 → 保持 INCOMPLETE，打印缺口清单。
用法：python3 batch_reconcile.py   （工作目录=讲透AwesomeAgents，或绝对路径内嵌）
"""
import os
import re
from datetime import date
from pathlib import Path

BASE = Path("~/ai/work4ai/讲透AwesomeAgents")


def parse_structure(path):
    """提取全部层级页名（编号+标题），返回 dict: normalized_title -> (numbering, title)"""
    pages = {}
    for line in open(path, encoding="utf-8"):
        m = re.match(r"\s*-\s*((?:\d+(?:\.\d+)*)\.?\s+.+)$", line.rstrip())
        if m:
            entry = m.group(1)
            num, _, title = entry.partition(" ")
            title = title.strip()
            norm = re.sub(r"[`*_]", "", title.lower())
            norm = re.sub(r"[^\w\s]", " ", norm, flags=re.UNICODE)
            norm = re.sub(r"\s+", " ", norm).strip()
            pages[norm] = (num, title)
    return pages


def disk_pages(d):
    """落盘页：文件名 -> 归一化标题（去编号前缀和 x 前缀）"""
    out = {}
    for f in os.listdir(d):
        if not f.endswith(".md") or f.startswith(("_", "INDEX", "README")):
            continue
        stem = f[:-3]
        m = re.match(r"^(?:x\d+|(?:\d+(?:\.\d+)*)\.?)-(.+)$", stem)
        if not m:
            continue
        slug = m.group(1)
        norm = re.sub(r"[^\w\s]", " ", slug, flags=re.UNICODE)
        norm = re.sub(r"\s+", " ", norm).strip()
        out[f] = norm
    return out


def reconcile_one(deepwiki_dir: Path):
    struct_f = deepwiki_dir / "_structure.txt"
    struct = parse_structure(struct_f)
    disk = disk_pages(deepwiki_dir)
    missing, used = [], set()
    for norm, (num, title) in struct.items():
        hit = None
        for f, dn in disk.items():
            if f in used:
                continue
            if dn == norm or dn.startswith(norm[:40]) or norm.startswith(dn[:40]):
                hit = f
                break
        if hit:
            used.add(hit)
        else:
            missing.append((num, title))
    extra = {f: dn for f, dn in disk.items() if f not in used}
    return len(struct), len(disk), missing, extra


def main():
    manifest = {}
    for line in open(BASE / "manifest.txt", encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        name, _, slug = line.partition("|")
        manifest[slug] = name
    ledger = []
    for line in open(BASE / "_ledger.tsv", encoding="utf-8"):
        line = line.rstrip("\n")
        if not line:
            continue
        parts = line.split("\t")
        ledger.append(parts + [""] * (3 - len(parts)))
    out_lines, changed = [], 0
    for slug, status, det in ledger:
        if status != "INCOMPLETE":
            out_lines.append("\t".join([slug, status, det]))
            continue
        name = manifest[slug]
        d = BASE / name / "deepwiki"
        n_struct, n_disk, missing, extra = reconcile_one(d)
        if not missing:
            verdict = (f"reconcile终判: 结构(全层级)={n_struct} 落盘={n_disk} "
                       f"MISSING=0 结构外={len(extra)}（extra=导航清单滞后正常现象，真一百分）")
            with open(d / "_coverage-check.md", "a", encoding="utf-8") as f:
                f.write(f"\n## reconcile 终判（{date.today().isoformat()}，全层级对账）\n"
                        f"- 结构页(全层级)={n_struct} 落盘={n_disk} 命中={n_struct} "
                        f"MISSING=0 结构外={len(extra)}\n"
                        f"- **结论：真一百分**（extra 页为 DeepWiki 目录多轮重组的正常增量，超额保留）\n")
            out_lines.append(f"{slug}\tFINAL_100\t{verdict}")
            changed += 1
        else:
            for num, t in missing:
                print(f"  {slug} MISSING {num} {t}")
            out_lines.append("\t".join([slug, "INCOMPLETE", f"真缺口{len(missing)}页: " + ";".join(t for _, t in missing[:5])]))
    (BASE / "_ledger.tsv").write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    print(f"reconcile done: {changed} 仓升级 FINAL_100，剩余 INCOMPLETE 见上")


if __name__ == "__main__":
    main()
