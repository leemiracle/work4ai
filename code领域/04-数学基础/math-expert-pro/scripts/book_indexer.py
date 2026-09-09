#!/usr/bin/env python3
"""
书籍快速索引提取器
====================
为 ../math 下的每本 PDF 生成"综合内容索引"：
  - 元数据（标题/作者/版次）
  - 书签目录（TOC，如果有）
  - 前言/引言（前 N 页文本摘要）
  - 章节列表（从 TOC 或文本启发式提取）

输出：每本书一份 Markdown，按丛书分目录存放。

用法:
  python3 scripts/book_indexer.py --series 通俗译丛 --limit 5  # 试点 5 本
  python3 scripts/book_indexer.py --series 通俗译丛            # 整个丛书
  python3 scripts/book_indexer.py --all                        # 全部
"""
import os
import sys
import argparse
import re
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import fitz  # PyMuPDF

MATH_ROOT = Path("/mnt/c/workspace/math")
OUTPUT_ROOT = Path("/mnt/c/workspace/math-expert-pro/09-crosstext/书籍索引")

SERIES_MAP = {
    "通俗译丛": ("【数学书籍】通俗数学名著译丛", "通俗数学名著译丛"),
    "华章": ("华章数学丛书", "华章数学丛书"),
    "现代基础": ("现代数学基础丛书", "现代数学基础丛书"),
    "GTM": ("美国研究生数学", "美国研究生数学"),
}

# 章节关键词（启发式）
CHAPTER_PATTERNS = [
    re.compile(r"^第\s*[一二三四五六七八九十百零\d]+\s*[章节讲编篇部]", re.M),
    re.compile(r"^(?:Chapter|CHAPTER|Lecture)\s+\d+", re.M),
    re.compile(r"^\d+\.\s+[A-Z\u4e00-\u9fff]", re.M),
    re.compile(r"^Part\s+[IVX\d]+", re.M),
]


def extract_book(pdf_path: Path) -> dict:
    """提取单本书的综合信息"""
    info = {
        "file_name": pdf_path.name,
        "file_path": str(pdf_path),
        "file_size_mb": round(pdf_path.stat().st_size / 1024 / 1024, 2),
        "title_meta": "",
        "author_meta": "",
        "subject_meta": "",
        "page_count": 0,
        "toc": [],           # 书签目录
        "chapters_detected": [],  # 启发式检测的章节
        "preface_excerpt": "",    # 前言摘要
        "intro_excerpt": "",      # 引言摘要
        "extract_error": "",
    }

    try:
        doc = fitz.open(pdf_path)
        info["page_count"] = doc.page_count

        # 1. 元数据
        meta = doc.metadata or {}
        info["title_meta"] = (meta.get("title") or "").strip()
        info["author_meta"] = (meta.get("author") or "").strip()
        info["subject_meta"] = (meta.get("subject") or "").strip()

        # 2. 书签目录（如果电子书有锚点目录）
        toc = doc.get_toc()  # [[level, title, page], ...]
        if toc:
            info["toc"] = [[lvl, title, page] for lvl, title, page in toc]

        # 3. 前言摘要（前 10 页内找"前言"/"序"/"Preface"）
        max_preface_pages = min(15, doc.page_count)
        preface_text = []
        for i in range(max_preface_pages):
            text = doc[i].get_text("text").strip()
            if any(kw in text[:200] for kw in ["前言", "序言", "Preface", "PREFACE"]):
                preface_text.append(f"--- 第 {i+1} 页 ---\n{text[:1500]}")
                if len(preface_text) >= 2:
                    break
        if preface_text:
            info["preface_excerpt"] = "\n\n".join(preface_text)[:3000]
        else:
            # 没找到前言，取第 1-3 页作为引言
            intro = []
            for i in range(min(3, doc.page_count)):
                intro.append(doc[i].get_text("text").strip()[:1500])
            info["intro_excerpt"] = "\n\n".join(intro)[:3000]

        # 4. 如果没有 TOC，启发式从全文找章节
        if not info["toc"]:
            sample_pages = min(20, doc.page_count)
            full_text = ""
            for i in range(sample_pages):
                full_text += doc[i].get_text("text") + "\n"
            chapters = set()
            for pat in CHAPTER_PATTERNS:
                for m in pat.finditer(full_text):
                    line = m.group(0).strip()[:120]
                    if 4 <= len(line) <= 120:
                        chapters.add(line)
            info["chapters_detected"] = sorted(chapters)[:30]

        doc.close()
    except Exception as e:
        info["extract_error"] = f"{type(e).__name__}: {e}"

    return info


def render_markdown(info: dict, series_label: str) -> str:
    """把提取结果渲染为 Markdown"""
    md = []
    md.append(f"# {info['file_name']}\n")
    md.append(f"> 丛书：{series_label} ｜ 自动索引（PyMuPDF {fitz.__version__}）\n")

    # 文件信息
    md.append("## 📁 文件信息\n")
    md.append(f"- 路径：`{info['file_path']}`")
    md.append(f"- 大小：{info['file_size_mb']} MB")
    md.append(f"- 页数：{info['page_count']}")
    if info["extract_error"]:
        md.append(f"- ⚠️ 提取错误：{info['extract_error']}")
    md.append("")

    # 元数据
    if info["title_meta"] or info["author_meta"]:
        md.append("## 🏷️ 元数据\n")
        if info["title_meta"]:
            md.append(f"- 标题：{info['title_meta']}")
        if info["author_meta"]:
            md.append(f"- 作者：{info['author_meta']}")
        if info["subject_meta"]:
            md.append(f"- 主题：{info['subject_meta']}")
        md.append("")

    # 书签目录
    if info["toc"]:
        md.append(f"## 📑 书签目录（共 {len(info['toc'])} 条）\n")
        md.append("```")
        for lvl, title, page in info["toc"]:
            indent = "  " * (lvl - 1)
            md.append(f"{indent}{title}  [p.{page}]")
        md.append("```\n")

    # 启发式章节
    if info["chapters_detected"] and not info["toc"]:
        md.append(f"## 🔍 启发式检测的章节（前 {len(info['chapters_detected'])} 条）\n")
        for ch in info["chapters_detected"][:20]:
            md.append(f"- {ch}")
        md.append("")

    # 前言
    if info["preface_excerpt"]:
        md.append("## 📜 前言摘要（自动提取，前 3000 字）\n")
        md.append("```")
        md.append(info["preface_excerpt"])
        md.append("```\n")
    elif info["intro_excerpt"]:
        md.append('## 📖 开篇引言（未找到「前言」关键词，取前 3 页）\n')
        md.append("```")
        md.append(info["intro_excerpt"])
        md.append("```\n")

    # 占位：每章节内容摘要（待 AI 后处理）
    md.append("## 📝 章节内容摘要（待 AI 后处理）\n")
    md.append("> 本节由 AI 在 step 2 阶段基于上方 TOC / 前言填充。\n")

    return "\n".join(md)


def _process_one(args_tuple):
    """worker：处理一本书（用于多进程）"""
    pdf_path_str, series_key, output_dir_str = args_tuple
    pdf_path = Path(pdf_path_str)
    output_dir = Path(output_dir_str)
    out_name = pdf_path.stem + ".md"
    out_path = output_dir / out_name
    if out_path.exists():
        return ("skip", pdf_path.name, "exists")
    try:
        info = extract_book(pdf_path)
        md = render_markdown(info, series_key)
        out_path.write_text(md, encoding="utf-8")
        if info["extract_error"]:
            return ("error", pdf_path.name, info["extract_error"][:80])
        return ("ok", pdf_path.name, f"pages={info['page_count']}, toc={len(info['toc'])}")
    except Exception as e:
        return ("error", pdf_path.name, f"{type(e).__name__}: {e}")


def process_series(series_key: str, limit: int = None, workers: int = None) -> int:
    """处理整个丛书（多进程并行）"""
    folder_name, output_subdir = SERIES_MAP[series_key]
    series_path = MATH_ROOT / folder_name
    output_dir = OUTPUT_ROOT / output_subdir
    output_dir.mkdir(parents=True, exist_ok=True)

    pdfs = sorted(series_path.glob("*.pdf"))
    if limit:
        pdfs = pdfs[:limit]

    if workers is None:
        workers = min(os.cpu_count() or 4, 8)

    tasks = [(str(p), series_key, str(output_dir)) for p in pdfs]
    success = 0
    errors = 0
    skipped = 0
    total = len(tasks)

    print(f"[{series_key}] 共 {total} 本，使用 {workers} 进程并行")

    with ProcessPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(_process_one, t): t for t in tasks}
        for i, fut in enumerate(as_completed(futures), 1):
            status, name, detail = fut.result()
            if status == "ok":
                success += 1
                print(f"  [{i}/{total}] ✅ {name[:50]}  ({detail})")
            elif status == "skip":
                skipped += 1
                if i % 20 == 0:
                    print(f"  [{i}/{total}] ⏭️  skip (exists): {name[:50]}")
            else:
                errors += 1
                print(f"  [{i}/{total}] ❌ {name[:50]}  ({detail})")

    print(f"[{series_key}] 汇总：✅ {success} ｜ ⏭️ {skipped} ｜ ❌ {errors}")
    return success


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", choices=list(SERIES_MAP.keys()) + ["all"], default="all")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--workers", type=int, default=None, help="并行进程数（默认 min(cpu, 8)）")
    ap.add_argument("--force", action="store_true", help="覆盖已存在文件")
    args = ap.parse_args()

    if args.force:
        # 删除已有索引文件
        for d in OUTPUT_ROOT.iterdir():
            if d.is_dir():
                for f in d.glob("*.md"):
                    f.unlink()
        print("🧹 已清空旧索引")

    if args.series == "all":
        total = 0
        for key in SERIES_MAP:
            print(f"\n=== 处理丛书：{key} ===")
            n = process_series(key, args.limit, args.workers)
            total += n
        print(f"\n✅ 全部完成：{total} 本成功")
    else:
        n = process_series(args.series, args.limit, args.workers)
        print(f"\n✅ 完成：{n} 本成功")


if __name__ == "__main__":
    main()
