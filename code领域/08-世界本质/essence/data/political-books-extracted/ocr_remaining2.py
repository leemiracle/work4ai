#!/usr/bin/env python3
"""
OCR remaining scanned PDFs with PaddleOCR.
Processes first 8 pages of each book, incremental save.
MD5 = MD5 of filename (matching existing convention).
"""

import os
os.environ['FLAGS_use_mkldnn'] = '0'

import sys
import json
import hashlib
import time
import traceback

SRC_DIR = "/mnt/c/Users/mirac/Documents/个人/写书/政治/"
OUT_DIR = "/mnt/c/workspace/essence/data/political-books-extracted/"

# Books explicitly done with OCR (skip these)
ALREADY_OCRD_NAMES = {
    "社会与政治运动讲义", "美国反对美国", "国家主权", "比较政治分析",
    "当代西方政治学分析", "政治的逻辑", "田园诗与狂想曲", "中国文化的深层结构",
    "跨越边界的社区", "走下圣坛的周恩来", "从零开始学公文写作",
}

def filename_md5(filename):
    """Compute MD5 of filename string, return full hex."""
    return hashlib.md5(filename.encode('utf-8')).hexdigest()

def build_existing_lookup():
    """Build lookup of existing extraction results by filename -> info."""
    existing = {}  # filename -> {md5, total_chars, source, file}
    for f in os.listdir(OUT_DIR):
        if not f.endswith('.json'):
            continue
        fpath = os.path.join(OUT_DIR, f)
        try:
            with open(fpath, encoding='utf-8') as fh:
                d = json.load(fh)
            fname = d.get('filename', '')
            if fname:
                existing[fname] = {
                    'md5': d.get('md5', ''),
                    'total_chars': d.get('total_chars', 0),
                    'source': 'OCR' if f.startswith('ocr_') else 'extract',
                    'json_file': f,
                }
        except:
            pass
    return existing

def find_pdfs_to_ocr(existing):
    """Find all PDFs that need OCR."""
    pdfs = []
    for f in sorted(os.listdir(SRC_DIR)):
        if not f.lower().endswith('.pdf'):
            continue
        
        # Skip explicitly done
        if any(key in f for key in ALREADY_OCRD_NAMES):
            continue
        
        # Check existing extraction
        if f in existing:
            rec = existing[f]
            if rec['source'] == 'OCR':
                continue  # Already OCR'd
            if rec['total_chars'] > 1000:
                continue  # Has native text
        
        filepath = os.path.join(SRC_DIR, f)
        md5 = filename_md5(f)
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
    
    tmpdir = tempfile.gettempdir()
    
    for i in range(pages_to_ocr):
        try:
            page = doc[i]
            pix = page.get_pixmap(dpi=200)
            
            img_path = os.path.join(tmpdir, f"ocr_page_{i}.png")
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

def save_ocr_result(filename, md5, ocr_data):
    """Save OCR result as JSON."""
    out_path = os.path.join(OUT_DIR, f"ocr_{md5}.json")
    
    total_chars = sum(p.get("chars", 0) for p in ocr_data["pages"])
    
    data = {
        "filename": filename,
        "md5": md5,
        "source": "PaddleOCR",
        "total_pages": ocr_data["total_pages"],
        "pages_ocrd": ocr_data["pages_ocrd"],
        "total_chars": total_chars,
        "pages": ocr_data["pages"],
    }
    
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"  Saved: {out_path} ({total_chars} chars)")
    return out_path

def main():
    print("=" * 70)
    print("PaddleOCR Batch Processing - Remaining Scanned PDFs")
    print("=" * 70)
    
    # Build lookup
    print("\n[1] Loading existing extraction records...")
    existing = build_existing_lookup()
    print(f"    Found {len(existing)} existing records")
    
    # Find PDFs to OCR
    print("\n[2] Finding PDFs that need OCR...")
    pdfs = find_pdfs_to_ocr(existing)
    print(f"\n    {len(pdfs)} PDFs to OCR:")
    for i, (_, name, md5) in enumerate(pdfs):
        # Check if existing has partial text
        chars = existing.get(name, {}).get('total_chars', 'N/A')
        print(f"    {i+1}. [{chars} chars] {name[:60]}")
    
    if not pdfs:
        print("\n    All done! No PDFs need OCR.")
        return
    
    # Initialize OCR
    print(f"\n[3] Initializing PaddleOCR...")
    ocr = init_ocr()
    print(f"    PaddleOCR ready.")
    
    # Process each PDF
    print(f"\n[4] Processing {len(pdfs)} books (8 pages each)...\n")
    
    completed = 0
    failed = 0
    t_start = time.time()
    
    for idx, (filepath, filename, md5) in enumerate(pdfs):
        print(f"\n{'─' * 60}")
        print(f"[{idx+1}/{len(pdfs)}] {filename[:65]}")
        print(f"    MD5: {md5}")
        print(f"    Time: {time.strftime('%H:%M:%S')}")
        
        try:
            t0 = time.time()
            ocr_data = ocr_pages(filepath, ocr, max_pages=8)
            elapsed = time.time() - t0
            
            save_ocr_result(filename, md5, ocr_data)
            
            total_chars = sum(p.get("chars", 0) for p in ocr_data["pages"])
            print(f"    Done: {ocr_data['pages_ocrd']} pages, {total_chars} chars, {elapsed:.1f}s")
            completed += 1
            
        except Exception as e:
            print(f"    FAILED: {e}")
            traceback.print_exc()
            failed += 1
        
        sys.stdout.flush()
    
    # Summary
    total_time = time.time() - t_start
    print(f"\n{'=' * 70}")
    print(f"OCR COMPLETE")
    print(f"{'=' * 70}")
    print(f"  Processed: {completed}")
    print(f"  Failed:    {failed}")
    print(f"  Total:     {len(pdfs)}")
    print(f"  Time:      {total_time:.0f}s ({total_time/60:.1f}m)")

if __name__ == "__main__":
    main()
