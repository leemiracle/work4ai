#!/usr/bin/env python3
"""csdiy 资源清单与去重扫描工具。

遍历 csdiy 根目录 (跳过 .git/缓存), 为每个文件建立结构化记录,
生成 manifest/resources.jsonl + manifest/summary.json,
并按 (size, ext) 做快速去重候选检测。

用法:
    python3 tools/build_manifest.py [--root <csdiy根>] [--hash] [--quiet]
    --hash  对候选重复组计算 sha256 (更精确, 较慢)
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".pytest_cache", "chroma"}
EXT_CATEGORY = {
    # 文档
    "md": "doc/markdown", "markdown": "doc/markdown", "rst": "doc/rst",
    "pdf": "book/pdf", "epub": "book/epub",
    "docx": "doc/word", "doc": "doc/word", "odt": "doc/word",
    "pptx": "doc/slide", "ppt": "doc/slide",
    "txt": "doc/text", "tex": "doc/latex",
    "html": "web/html", "htm": "web/html", "css": "web/css",
    # 代码
    "py": "code/python", "ipynb": "code/notebook",
    "java": "code/java", "c": "code/c", "h": "code/c",
    "cpp": "code/cpp", "cc": "code/cpp", "cxx": "code/cpp", "hpp": "code/cpp",
    "rs": "code/rust", "go": "code/go", "js": "code/js", "ts": "code/ts",
    "sh": "code/shell", "v": "code/verilog", "sv": "code/verilog",
    "scala": "code/scala", "rb": "code/ruby", "kt": "code/kotlin",
    # 数据/配置
    "json": "data/json", "yaml": "data/yaml", "yml": "data/yaml",
    "toml": "data/toml", "xml": "data/xml", "csv": "data/csv",
    # 媒体
    "png": "media/image", "jpg": "media/image", "jpeg": "media/image",
    "gif": "media/image", "svg": "media/image", "webp": "media/image",
    "mp4": "media/video", "webm": "media/video", "mp3": "media/audio",
    # 其它
    "bin": "binary", "exe": "binary", "zip": "archive", "tar": "archive",
    "gz": "archive", "result": "other/result",
}

# 课程代码识别 (路径片段中出现即归类)
COURSE_PATTERNS = [
    (re.compile(r"(MIT6\.S?081|6\.S081)", re.I), "MIT 6.S081 操作系统"),
    (re.compile(r"MIT6?\.?824|6\.824", re.I), "MIT 6.824 分布式系统"),
    (re.compile(r"MIT6\.?1600|6\.1600", re.I), "MIT 6.1600"),
    (re.compile(r"MIT6\.?5940|6\.5940", re.I), "MIT 6.5940 TinyML"),
    (re.compile(r"MIT6\.?031|6\.031", re.I), "MIT 6.031 软件构造"),
    (re.compile(r"MIT18\.?330|18\.330", re.I), "MIT 18.330 概率"),
    (re.compile(r"CS1[0-9]{2}", re.I), None),  # 通用 CS1xx, 后续用片段
    (re.compile(r"CMU10-?714|10-714", re.I), "CMU 10-714 深度学习"),
    (re.compile(r"CMU15-?445|15-445", re.I), "CMU 15-445 数据库"),
    (re.compile(r"(GAMES10[1-9]|GAMES20[0-9])", re.I), None),
    (re.compile(r"(Nand2Tetris|NandToTetris)", re.I), "Nand2Tetris"),
    (re.compile(r"REKCARC", re.I), "清华 REKCARC 课程资料"),
    (re.compile(r"xv6", re.I), "xv6 操作系统"),
    (re.compile(r"bustub|BusTub", re.I), "CMU Bustub 数据库"),
    (re.compile(r"seed-?labs|SeedLabs", re.I), "SEED Labs 安全"),
    (re.compile(r"nanoGPT|micrograd|nano-?v?llm", re.I), "AI 实现参考"),
]

SUBJECT_KEYWORDS = {
    "操作系统": "操作系统", "计算机系统基础": "系统基础", "体系结构": "体系结构",
    "编译原理": "编译原理", "计算机网络": "计算机网络", "数据结构与算法": "数据结构与算法",
    "数据库系统": "数据库", "并行与分布式系统": "分布式系统", "计算机图形学": "图形学",
    "Web开发": "Web 开发", "人工智能": "AI", "数学基础": "数学", "数学进阶": "数学",
    "数据科学": "数据科学", "软件工程": "软件工程", "必学工具": "CS工具",
    "体系结构基础": "体系结构",
}


def classify(ext: str) -> str:
    return EXT_CATEGORY.get(ext.lower(), "other/unknown")


def infer_subject(rel_path: str) -> str:
    parts = rel_path.replace("\\", "/").split("/")
    for p in parts:
        for pat, name in COURSE_PATTERNS:
            if pat.search(p):
                return name or f"课程:{p}"
    for p in parts:
        for kw, subj in SUBJECT_KEYWORDS.items():
            if kw in p:
                return subj
    # 顶层目录即来源
    top = parts[0] if parts else ""
    return {"github-repos": "GitHub仓库", "books": "书籍", "website": "网站镜像",
            "cs-self-learning": "主仓库"}.get(top, "其它")


def walk(root: Path):
    stack = [root]
    while stack:
        base = stack.pop()
        try:
            with os.scandir(base) as it:
                entries = list(it)
        except (PermissionError, OSError):
            continue
        for e in entries:
            name = e.name
            if name in SKIP_DIRS:
                continue
            if e.is_dir(follow_symlinks=False):
                stack.append(e.path)
            elif e.is_file(follow_symlinks=False):
                try:
                    st = e.stat()
                except OSError:
                    continue
                yield e.path, st


def sha256_of(path: str, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for b in iter(lambda: f.read(chunk), b""):
                h.update(b)
    except OSError:
        return ""
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--hash", action="store_true", help="对候选重复组计算 sha256")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    out_dir = root / "manifest"
    out_dir.mkdir(exist_ok=True)
    (root / "tools").mkdir(exist_ok=True)

    resources = []
    size_by_cat = defaultdict(int)
    count_by_cat = defaultdict(int)
    count_by_subject = defaultdict(int)
    # (size, ext) -> [paths]
    size_ext_groups = defaultdict(list)

    files = walk(root)
    total = 0
    for path, st in files:
        rel = os.path.relpath(path, root)
        if rel == ".gitignore":
            continue
        ext = os.path.splitext(rel)[1].lstrip(".").lower()
        cat = classify(ext)
        subject = infer_subject(rel)
        size = st.st_size
        rec = {
            "path": rel.replace("\\", "/"),
            "size": size,
            "ext": ext,
            "category": cat,
            "subject": subject,
            "mtime": int(st.st_mtime),
        }
        resources.append(rec)
        size_by_cat[cat] += size
        count_by_cat[cat] += 1
        count_by_subject[subject] += 1
        # 只对小文件 (<50MB) 参与去重候选, 避免大文件全哈希
        if size < 50 * (1 << 20):
            size_ext_groups[(size, ext)].append(rel.replace("\\", "/"))
        total += 1
        if not args.quiet and total % 5000 == 0:
            print(f"  已扫描 {total} 文件...", file=sys.stderr)

    # 写 JSONL
    with open(out_dir / "resources.jsonl", "w", encoding="utf-8") as f:
        for r in resources:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # 去重候选: 同 (size, ext) 且 size>0 的组, 成员>1 即可疑
    dup_candidates = []
    exact_dups = []
    for (size, ext), paths in size_ext_groups.items():
        if size > 0 and len(paths) > 1:
            entry = {"size": size, "ext": ext, "count": len(paths), "paths": paths[:50]}
            dup_candidates.append(entry)
            if args.hash:
                # 计算精确哈希, 找出真正完全相同的
                hashes = defaultdict(list)
                for p in paths:
                    h = sha256_of(os.path.join(root, p))
                    hashes[h].append(p)
                for h, group in hashes.items():
                    if len(group) > 1:
                        exact_dups.append({"sha256": h, "size": size, "paths": group[:50]})
    dup_candidates.sort(key=lambda x: -x["size"] * x["count"])

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "total_files": total,
        "total_size": sum(r["size"] for r in resources),
        "by_category": [
            {"category": k, "count": v, "size": size_by_cat[k]}
            for k, v in sorted(count_by_cat.items(), key=lambda x: -x[1])
        ],
        "by_subject": [
            {"subject": k, "count": v}
            for k, v in sorted(count_by_subject.items(), key=lambda x: -x[1])
        ],
        "duplicate_candidate_groups": len(dup_candidates),
        "duplicate_candidate_wasted_bytes_approx": sum(
            (e["count"] - 1) * e["size"] for e in dup_candidates
        ),
        "exact_duplicates_groups": len(exact_dups),
        "note": "duplicate_candidate 基于 (size,ext) 启发; exact_duplicates 需 --hash",
    }

    with open(out_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    with open(out_dir / "duplicates.json", "w", encoding="utf-8") as f:
        json.dump({"candidates": dup_candidates, "exact": exact_dups},
                  f, ensure_ascii=False, indent=2)

    if not args.quiet:
        print(f"✅ 扫描完成: {total} 文件, {summary['total_size']/1e9:.2f} GB")
        print(f"   类别数: {len(count_by_cat)}, 主题数: {len(count_by_subject)}")
        print(f"   去重候选组: {len(dup_candidates)} "
              f"(约浪费 {summary['duplicate_candidate_wasted_bytes_approx']/1e6:.0f} MB)")
        print(f"   精确重复组: {len(exact_dups)}")
        print(f"   输出: manifest/resources.jsonl, summary.json, duplicates.json")


if __name__ == "__main__":
    main()
