"""快速OCR——低DPI+少页数+串行，每本5页约30秒"""
import os, sys, time, json, hashlib, warnings
os.environ['FLAGS_use_mkldnn'] = '0'
warnings.filterwarnings('ignore')
import fitz

BOOK_DIR = "/mnt/c/Users/mirac/Documents/个人/写书/政治"
OUT_DIR = "/mnt/c/workspace/essence/data/political-books-extracted"

# 要处理的书（从命令行参数获取）
books = sys.argv[1:]
if not books:
    print("用法: python3 ocr_fast.py '书1' '书2' ...")
    sys.exit(1)

from paddleocr import PaddleOCR
ocr = PaddleOCR(lang='ch', enable_mkldnn=False)

for book_file in books:
    path = os.path.join(BOOK_DIR, book_file)
    if not os.path.exists(path):
        print(f"MISS | {book_file[:50]}")
        continue
    
    md5 = hashlib.md5(book_file.encode('utf-8')).hexdigest()[:12]
    outpath = os.path.join(OUT_DIR, f"ocr_{md5}.json")
    
    if os.path.exists(outpath):
        try:
            d = json.load(open(outpath, 'r', encoding='utf-8'))
            if d.get('total_chars', 0) > 50:
                print(f"SKIP | {book_file[:50]:<50} | {d.get('total_chars',0)}字")
                continue
        except:
            pass
    
    t0 = time.time()
    try:
        doc = fitz.open(path)
        max_p = min(5, doc.page_count)  # 只做5页
        
        pages = []
        total = 0
        for i in range(max_p):
            pix = doc[i].get_pixmap(dpi=150)  # 低DPI加速
            img_path = f"/tmp/ocr_fast_{i}.png"
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
                total += len(text)
            except:
                pages.append({'page': i+1, 'text': ''})
            
            os.remove(img_path)
        
        total_pages_saved = doc.page_count
        doc.close()
        
        output = {
            'filename': book_file, 'md5': md5,
            'pages_ocrd': max_p, 'total_pages": total_pages,
            'total_chars': total, 'pages': pages,
        }
        with open(outpath, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        elapsed = time.time() - t0
        print(f"OK   | {book_file[:50]:<50} | {max_p}页 | {total}字 | {elapsed:.0f}s")
    except Exception as e:
        print(f"ERR  | {book_file[:50]:<50} | {str(e)[:40]}")
