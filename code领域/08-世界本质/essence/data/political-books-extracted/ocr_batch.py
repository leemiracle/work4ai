"""对扫描版PDF做OCR——每本前50页"""
import os, sys, time, json, hashlib
os.environ['FLAGS_use_mkldnn'] = '0'
import fitz, warnings
warnings.filterwarnings('ignore')

BOOK_DIR = "/mnt/c/Users/mirac/Documents/个人/写书/政治"
OUT_DIR = "/mnt/c/workspace/essence/data/political-books-extracted"

TARGETS = [
    "社会与政治运动讲义（第二版） ([美国] 赵鼎新) (Z-Library).pdf",
    "美国反对美国 (王沪宁) (Z-Library).pdf",
    "中国文化的深层结构 孙隆基著.pdf",
    "田园诗与狂想曲 (秦晖, 金雁) (Z-Library).pdf",
]

MAX_PAGES = 50

from paddleocr import PaddleOCR
ocr = PaddleOCR(lang='ch', enable_mkldnn=False)

for book_file in TARGETS:
    path = os.path.join(BOOK_DIR, book_file)
    if not os.path.exists(path):
        print(f"missing: {book_file[:50]}")
        continue
    
    md5 = hashlib.md5(book_file.encode('utf-8')).hexdigest()[:12]
    outpath = os.path.join(OUT_DIR, f"ocr_{md5}.json")
    
    if os.path.exists(outpath):
        print(f"skip: {book_file[:50]}")
        continue
    
    print(f"\n=== OCR: {book_file[:50]} ===")
    t0 = time.time()
    
    doc = fitz.open(path)
    total_pages = doc.page_count
    max_p = min(MAX_PAGES, total_pages)
    
    results = []
    for i in range(max_p):
        pix = doc[i].get_pixmap(dpi=300)
        img_path = f"/tmp/ocr_p{i}.png"
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
            
            results.append({'page': i+1, 'text': text})
            sys.stderr.write(f"  p{i+1}: {len(text)} chars\n")
        except Exception as e:
            results.append({'page': i+1, 'text': '', 'error': str(e)[:50]})
            sys.stderr.write(f"  p{i+1}: ERR\n")
        
        os.remove(img_path)
    
    doc.close()
    elapsed = time.time() - t0
    total = sum(len(r['text']) for r in results)
    
    output = {
        'filename': book_file,
        'md5': md5,
        'pages_ocrd': max_p,
        'total_pages': total_pages,
        'total_chars': total,
        'pages': results,
    }
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"OK: {book_file[:50]} | {max_p}p | {total}chars | {elapsed:.1f}s")

print("\n=== ALL DONE ===")
