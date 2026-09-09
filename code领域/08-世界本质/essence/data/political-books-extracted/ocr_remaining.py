#!/usr/bin/env python3
"""
OCR remaining scanned PDFs with PaddleOCR.
Processes first 8 pages of each book, incremental save.
"""

import os
os.environ['FLAGS_use_mkldnn'] = '0'

import sys
import json
import hashlib
import time
import traceback

# Source directory
SRC_DIR = "/mnt/c/Users/mirac/Documents/个人/写书/政治/"
OUT_DIR = "/mnt/c/workspace/essence/data/political-books-extracted/"

# Books that already have OCR (skip these)
ALREADY_OCRD = {
    "社会与政治运动讲义",
    "美国反对美国",
    "国家主权",
    "比较政治分析",
    "当代西方政治学分析",
    "政治的逻辑",
    "田园诗与狂想曲",
    "中国文化的深层结构",
    "跨越边界的社区",
    "走下圣坛的周恩来",
    "从零开始学公文写作",
}

def is_already_ocrd(filename):
    """Check if this book was already OCR'd."""
    for key in ALREADY_OCRD:
        if key in filename:
            return True
    return False

def has_ocr_output(md5):
    """Check if OCR output file already exists (either short or full md5)."""
    # Check full md5
    full_path = os.path.join(OUT_DIR, f"ocr_{md5}.json")
    if os.path.exists(full_path):
        return True
    # Check short md5 (first 12 chars)
    short_path = os.path.join(OUT_DIR, f"ocr_{md5[:12]}.json")
    if os.path.exists(short_path):
        return True
    return False

def get_md5(filepath):
    """Compute MD5 of file."""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def find_pdfs_to_ocr():
    """Find all PDFs that need OCR."""
    pdfs = []
    for f in sorted(os.listdir(SRC_DIR)):
        if not f.lower().endswith('.pdf'):
            continue
        filepath = os.path.join(SRC_DIR, f)
        if is_already_ocrd(f):
            continue
        
        # Check if already has OCR output
        # Try both full and short md5
        md5 = get_md5(filepath)
        if has_ocr_output(md5):
            print(f"  [SKIP-OCR-EXISTS] {f[:50]}")
            continue
        
        pdfs.append((filepath, f, md5))
    
    return pdfs

def init_ocr():
    """Initialize PaddleOCR."""
    from paddleocr import PaddleOCR
    ocr = PaddleOCR(lang='ch', enable_mkldnn=False)
    return ocr

def ocr_pages(pdf_path, ocr, max_pages=8):
    """OCR first N pages of a PDF."""
    import fitz
    import tempfile
    
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    pages_to_ocr = min(max_pages, total_pages)
    
    results = {
        "pages": [],
        "pages_ocrd": 0,
        "total_pages": total_pages,
    }
    
    for i in range(pages_to_ocr):
        try:
            page = doc[i]
            pix = page.get_pixmap(dpi=200)
            
            # Save to temp file
            img_path = os.path.join(tempfile.gettempdir(), f"ocr_page_{i}.png")
            pix.save(img_path)
            
            # Run OCR
            result = ocr.predict(img_path)
            
            page_text = ""
            if result and len(result) > 0:
                item = result[0]
                if hasattr(item, 'rec_texts'):
                    page_text = "\n".join(item.rec_texts)
                elif isinstance(item, dict) and 'rec_texts' in item:
                    page_text = "\n".join(item['rec_texts'])
                elif isinstance(item, dict) and 'rec_text' in item:
                    page_text = item['rec_text']
            
            # Clean up temp image
            if os.path.exists(img_path):
                os.remove(img_path)
            
            results["pages"].append({
                "page": i,
                "text": page_text,
                "chars": len(page_text),
            })
            results["pages_ocrd"] = i + 1
            
            print(f"    Page {i}: {len(page_text)} chars", flush=True)
            
        except Exception as e:
            print(f"    Page {i}: ERROR - {e}", flush=True)
            results["pages"].append({
                "page": i,
                "text": "",
                "chars": 0,
                "error": str(e),
            })
            results["pages_ocrd"] = i + 1
    
    doc.close()
    return results

def save_ocr_result(filepath, filename, md5, ocr_data):
    """Save OCR result as JSON."""
    out_path = os.path.join(OUT_DIR, f"ocr_{md5}.json")
    
    data = {
        "filename": filename,
        "md5": md5,
        "source": "PaddleOCR",
        "total_pages": ocr_data["total_pages"],
        "pages_ocrd": ocr_data["pages_ocrd"],
        "total_chars": sum(p.get("chars", 0) for p in ocr_data["pages"]),
        "pages": ocr_data["pages"],
    }
    
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"  Saved: {out_path}")
    return out_path

def main():
    print("=" * 70)
    print("PaddleOCR Batch Processing - Remaining Scanned PDFs")
    print("=" * 70)
    
    # Find PDFs to OCR
    print("\n[1] Scanning for PDFs that need OCR...")
    pdfs = find_pdfs_to_ocr()
    print(f"\n    Found {len(pdfs)} PDFs to OCR:")
    for i, (_, name, md5) in enumerate(pdfs):
        print(f"    {i+1}. {name[:60]}...")
    
    if not pdfs:
        print("\n    No PDFs need OCR. All done!")
        return
    
    # Initialize OCR
    print(f"\n[2] Initializing PaddleOCR...")
    ocr = init_ocr()
    print(f"    PaddleOCR ready.")
    
    # Process each PDF
    print(f"\n[3] Processing {len(pdfs)} books (8 pages each)...\n")
    
    completed = 0
    failed = 0
    
    for idx, (filepath, filename, md5) in enumerate(pdfs):
        print(f"\n{'─' * 60}")
        print(f"[{idx+1}/{len(pdfs)}] {filename[:60]}")
        print(f"    MD5: {md5}")
        print(f"    Time: {time.strftime('%H:%M:%S')}")
        
        try:
            t0 = time.time()
            ocr_data = ocr_pages(filepath, ocr, max_pages=8)
            elapsed = time.time() - t0
            
            save_ocr_result(filepath, filename, md5, ocr_data)
            
            total_chars = sum(p.get("chars", 0) for p in ocr_data["pages"])
            print(f"    ✅ Done: {ocr_data['pages_ocrd']} pages, {total_chars} chars, {elapsed:.1f}s")
            completed += 1
            
        except Exception as e:
            print(f"    ❌ FAILED: {e}")
            traceback.print_exc()
            failed += 1
        
        # Flush output
        sys.stdout.flush()
    
    # Summary
    print(f"\n{'=' * 70}")
    print(f"OCR COMPLETE")
    print(f"{'=' * 70}")
    print(f"  Processed: {completed}")
    print(f"  Failed:    {failed}")
    print(f"  Total:     {len(pdfs)}")
    print(f"  Time:      {time.strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()
