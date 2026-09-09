#!/usr/bin/env python3
"""
PaddleOCR 提取扫描版PDF文本（串行，增量保存）。
每本前8页，每页OCR后立即保存JSON。
"""
import os
os.environ['FLAGS_use_mkldnn'] = '0'

import json
import time
import hashlib
import fitz  # PyMuPDF
from paddleocr import PaddleOCR

SRC_DIR = "/mnt/c/Users/mirac/Documents/个人/写书/政治"
OUT_DIR = "/mnt/c/workspace/essence/data/political-books-extracted"
PAGES_PER_BOOK = 8
DPI = 200

# 优先级顺序（已处理的两本放在最前，脚本会自动跳过）
PRIORITY = [
    ("社会与政治运动讲义（第二版）", "赵鼎新 社会与政治运动"),
    ("美国反对美国 (王沪宁)", "王沪宁 美国反对美国"),
    ("田园诗与狂想曲 (秦晖", "秦晖 田园诗与狂想曲"),
    ("中国文化的深层结构 孙隆基", "孙隆基 中国文化的深层结构"),
    ("跨越边界的社区", "项飙 跨越边界的社区"),
    ("国家主权 (王沪宁)", "王沪宁 国家主权"),
    ("比较政治分析 (王沪宁)", "王沪宁 比较政治分析"),
    ("当代西方政治学分析 (王沪宁)", "王沪宁 当代西方政治学分析"),
    ("政治的逻辑--马克思主义", "王沪宁 政治的逻辑"),
]


def find_pdf(keyword):
    """在源目录找到匹配关键字的PDF文件。"""
    for f in sorted(os.listdir(SRC_DIR)):
        if f.endswith('.pdf') and keyword in f:
            return os.path.join(SRC_DIR, f)
    return None


def md5_of(path):
    h = hashlib.md5()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def ocr_page(ocr, pix_path):
    """对单页图片做OCR，返回文本字符串。"""
    result = ocr.predict(pix_path)
    if result and len(result) > 0:
        item = result[0]
        texts = item['rec_texts'] if isinstance(item, dict) else getattr(item, 'rec_texts', None)
        if texts:
            return "\n".join(texts)
    return ""


def process_book(ocr, pdf_path, label):
    """处理一本书：前N页OCR，增量保存。"""
    md5 = md5_of(pdf_path)
    out_file = os.path.join(OUT_DIR, f"ocr_{md5[:12]}.json")
    filename = os.path.basename(pdf_path)

    # 已有完整OCR结果则跳过
    if os.path.exists(out_file):
        try:
            existing = json.load(open(out_file, encoding='utf-8'))
            if existing.get('pages_ocrd', 0) >= PAGES_PER_BOOK:
                print(f"  [SKIP] 已有完整OCR ({existing.get('pages_ocrd')}页, {existing.get('total_chars')}字)")
                return existing.get('total_chars', 0), True
            # 续做：加载已有数据
            pages = existing.get('pages', [])
            done = len(pages)
            print(f"  [RESUME] 已有 {done} 页，继续...")
        except Exception:
            pages = []
            done = 0
    else:
        pages = []
        done = 0

    doc = fitz.open(pdf_path)
    total_pages = len(doc)

    start = done
    end = min(PAGES_PER_BOOK, total_pages)

    for pno in range(start, end):
        t0 = time.time()
        try:
            page = doc[pno]
            pix = page.get_pixmap(dpi=DPI)
            tmp_path = f"/tmp/_ocr_p{pno}.png"
            pix.save(tmp_path)
            text = ocr_page(ocr, tmp_path)
            elapsed = time.time() - t0
            pages.append({"page": pno + 1, "text": text})
            print(f"    page {pno+1}/{total_pages}: {len(text)}字 ({elapsed:.1f}s)")
            # 增量保存
            data = {
                "filename": filename,
                "md5": md5,
                "label": label,
                "pages_ocrd": len(pages),
                "total_pages": total_pages,
                "total_chars": sum(len(p["text"]) for p in pages),
                "pages": pages,
            }
            json.dump(data, open(out_file, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
            try:
                os.remove(tmp_path)
            except OSError:
                pass
        except Exception as e:
            print(f"    page {pno+1}: ERROR {e}")
            pages.append({"page": pno + 1, "text": "", "error": str(e)})

    doc.close()
    total_chars = sum(len(p.get("text", "")) for p in pages)
    return total_chars, False


def main():
    print("=" * 60)
    print("PaddleOCR 扫描版PDF提取（串行，增量保存）")
    print("=" * 60)

    # 初始化OCR（只初始化一次）
    print("[INIT] 初始化 PaddleOCR ...")
    ocr = PaddleOCR(lang='ch', enable_mkldnn=False)
    print("[INIT] 完成\n")

    results = []
    t_start = time.time()

    for keyword, label in PRIORITY:
        pdf_path = find_pdf(keyword)
        if not pdf_path:
            print(f"[MISS] 找不到PDF: {label}")
            continue

        print(f"\n>>> {label}")
        print(f"    文件: {os.path.basename(pdf_path)[:60]}")
        chars, skipped = process_book(ocr, pdf_path, label)
        results.append((label, chars, skipped))

    elapsed = time.time() - t_start
    print("\n" + "=" * 60)
    print("处理完成汇总")
    print("=" * 60)
    grand_total = 0
    processed = 0
    for label, chars, skipped in results:
        tag = "(跳过)" if skipped else "(新处理)"
        print(f"  {tag} {label}: {chars} 字")
        grand_total += chars
        if not skipped:
            processed += 1
    print(f"\n本次新处理: {processed} 本")
    print(f"总提取字数: {grand_total} 字")
    print(f"总耗时: {elapsed/60:.1f} 分钟")


if __name__ == '__main__':
    main()
