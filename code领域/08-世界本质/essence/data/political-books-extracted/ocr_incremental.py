"""增量OCR——每页OCR后立即保存，DPI=200加速"""
import os, sys, time, json, hashlib
os.environ['FLAGS_use_mkldnn'] = '0'
import fitz, warnings
warnings.filterwarnings('ignore')

BOOK_DIR = "/mnt/c/Users/mirac/Documents/个人/写书/政治"
OUT_DIR = "/mnt/c/workspace/essence/data/political-books-extracted"

book_file = sys.argv[1] if len(sys.argv) > 1 else "社会与政治运动讲义（第二版） ([美国] 赵鼎新) (Z-Library).pdf"
MAX_PAGES = int(sys.argv[2]) if len(sys.argv) > 2 else 15

path = os.path.join(BOOK_DIR, book_file)
md5 = hashlib.md5(book_file.encode('utf-8')).hexdigest()[:12]
outpath = os.path.join(OUT_DIR, f"ocr_{md5}.json")

# 加载已有结果
if os.path.exists(outpath):
    output = json.load(open(outpath, 'r', encoding='utf-8'))
    done_pages = len(output.get('pages', []))
    print(f"已有 {done_pages} 页，继续从第 {done_pages+1} 页")
else:
    output = {'filename': book_file, 'md5': md5, 'pages': [], 'total_chars': 0}
    done_pages = 0

from paddleocr import PaddleOCR
ocr = PaddleOCR(lang='ch', enable_mkldnn=False)

doc = fitz.open(path)
total_pages = doc.page_count
output['total_pages'] = total_pages

start = done_pages
end = min(MAX_PAGES, total_pages)

t0 = time.time()
for i in range(start, end):
    pix = doc[i].get_pixmap(dpi=200)
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
        
        output['pages'].append({'page': i+1, 'text': text})
        output['total_chars'] = sum(len(p['text']) for p in output['pages'])
        
        # 每页立即保存
        with open(outpath, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"p{i+1}: {len(text)}字 | 累计{output['total_chars']}字")
    except Exception as e:
        output['pages'].append({'page': i+1, 'text': '', 'error': str(e)[:50]})
        with open(outpath, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"p{i+1}: ERR {str(e)[:40]}")
    
    os.remove(img_path)

doc.close()
elapsed = time.time() - t0
print(f"\n=== {book_file[:40]}: {end-start}页, {output['total_chars']}字, {elapsed:.0f}s ===")
