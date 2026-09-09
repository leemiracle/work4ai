"""多进程并行OCR——3进程同时处理不同的扫描版PDF"""
import os, sys, time, json, hashlib, warnings
os.environ['FLAGS_use_mkldnn'] = '0'
warnings.filterwarnings('ignore')
import fitz
from multiprocessing import Pool

BOOK_DIR = "/mnt/c/Users/mirac/Documents/个人/写书/政治"
OUT_DIR = "/mnt/c/workspace/essence/data/political-books-extracted"
MAX_PAGES = 10  # 每本前10页
DPI = 200

def ocr_book(args):
    """在子进程中OCR一本书"""
    idx, book_file = args
    path = os.path.join(BOOK_DIR, book_file)
    md5 = hashlib.md5(book_file.encode('utf-8')).hexdigest()[:12]
    outpath = os.path.join(OUT_DIR, f"ocr_{md5}.json")
    
    # 跳过已处理的
    if os.path.exists(outpath):
        try:
            d = json.load(open(outpath, 'r', encoding='utf-8'))
            if d.get('total_chars', 0) > 100:
                return (idx, book_file, 'SKIP', d.get('total_chars', 0), len(d.get('pages', [])))
        except:
            pass
    
    try:
        # 每个子进程独立加载PaddleOCR
        from paddleocr import PaddleOCR
        ocr = PaddleOCR(lang='ch', enable_mkldnn=False)
        
        doc = fitz.open(path)
        total_pages = doc.page_count
        max_p = min(MAX_PAGES, total_pages)
        
        pages = []
        total_chars = 0
        
        for i in range(max_p):
            pix = doc[i].get_pixmap(dpi=DPI)
            img_path = f"/tmp/ocr_{os.getpid()}_p{i}.png"
            pix.save(img_path)
            
            try:
                result = ocr.predict(img_path)
                text = ""
                if result and len(result) > 0:
                    item = result[0]
                    if hasattr(item, 'rec_texts') and item.rec_texts:
                        text = "\n".join(item.rec_texts)
                    elif isinstance(item, dict) and 'rec_texts' in item:
                        text = "\n".join(item['rec_texts'])
                
                pages.append({'page': i+1, 'text': text})
                total_chars += len(text)
            except:
                pages.append({'page': i+1, 'text': ''})
            
            os.remove(img_path)
        
        doc.close()
        
        output = {
            'filename': book_file,
            'md5': md5,
            'pages_ocrd': max_p,
            'total_pages': total_pages,
            'total_chars': total_chars,
            'pages': pages,
        }
        
        with open(outpath, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        return (idx, book_file, 'OK', total_chars, max_p)
    except Exception as e:
        return (idx, book_file, f'ERR:{str(e)[:40]}', 0, 0)

if __name__ == '__main__':
    # 找所有需要OCR的扫描版
    import json as jsonmod
    
    # 已有全文的书（不需要OCR）
    has_text = set()
    for fname in os.listdir(OUT_DIR):
        if not fname.endswith('.json') or fname.startswith('ocr_'):
            continue
        try:
            d = jsonmod.load(open(os.path.join(OUT_DIR, fname), 'r', encoding='utf-8'))
            if d.get('total_chars', 0) > 1000:
                has_text.add(d.get('filename', ''))
        except:
            pass
    
    # 已OCR的书
    already_ocrd = set()
    for fname in os.listdir(OUT_DIR):
        if fname.startswith('ocr_') and fname.endswith('.json'):
            try:
                d = jsonmod.load(open(os.path.join(OUT_DIR, fname), 'r', encoding='utf-8'))
                if d.get('total_chars', 0) > 100:
                    already_ocrd.add(d.get('filename', ''))
            except:
                pass
    
    # 找需要OCR的书
    targets = []
    for fname in sorted(os.listdir(BOOK_DIR)):
        if not fname.endswith('.pdf'):
            continue
        if fname in has_text:
            continue
        if fname in already_ocrd:
            continue
        targets.append(fname)
    
    print(f"需要OCR: {len(targets)} 本", file=sys.stderr)
    for t in targets:
        print(f"  - {t[:50]}", file=sys.stderr)
    
    if not targets:
        print("全部完成！", file=sys.stderr)
        sys.exit(0)
    
    tasks = [(i, f) for i, f in enumerate(targets)]
    t0 = time.time()
    
    # 2进程并行（PaddleOCR占内存大）
    with Pool(2) as pool:
        results = pool.map(ocr_book, tasks)
    
    results.sort(key=lambda x: x[0])
    
    ok = err = skip = 0
    total_chars = 0
    for idx, fname, status, chars, pages in results:
        if status == 'OK':
            ok += 1
            total_chars += chars
            print(f"OK   | {fname[:50]:<50} | {pages}页 | {chars}字")
        elif status == 'SKIP':
            skip += 1
            print(f"SKIP | {fname[:50]:<50} | {chars}字")
        else:
            err += 1
            print(f"ERR  | {fname[:50]:<50} | {status}")
    
    elapsed = time.time() - t0
    print(f"\n=== OK={ok} SKIP={skip} ERR={err} | {total_chars}字 | {elapsed:.0f}s ===", file=sys.stderr)
