#!/usr/bin/env python3
"""对《习近平谈治国理政》第四卷做全量 OCR（539 页）。
增量保存 + 断点续传。"""
import os, sys, json, time
os.environ['FLAGS_use_mkldnn'] = '0'
import fitz
import warnings
warnings.filterwarnings('ignore')

PDF = '/mnt/c/Users/mirac/Documents/个人/写书/政治/习近平谈治国理政4.pdf'
OUT = '/mnt/c/workspace/essence/data/political-books-extracted/ocr_9d9f947c94934cb5cb1f81bd21af50b2.json'

def _save(path, results):
    pages = sorted(results.values(), key=lambda x: x['page'])
    total_chars = sum(p.get('chars', 0) for p in pages)
    data = {
        'filename': '习近平谈治国理政4.pdf',
        'md5': '9d9f947c94934cb5cb1f81bd21af50b2',
        'source': 'PaddleOCR (full)',
        'total_pages': N if 'N' in dir() else len(pages),
        'pages_ocrd': len(pages),
        'total_chars': total_chars,
        'pages': pages,
    }
    tmp = path + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(data, f, ensure_ascii=False)
    os.replace(tmp, path)

print('loading OCR engine...', flush=True)
from paddleocr import PaddleOCR
ocr = PaddleOCR(lang='ch', enable_mkldnn=False, use_angle_cls=True)

doc = fitz.open(PDF)
N = doc.page_count
print(f'total pages: {N}', flush=True)

# resume: load existing
results = {}
if os.path.exists(OUT):
    with open(OUT) as f:
        old = json.load(f)
    for p in old.get('pages', []):
        results[p['page']] = p
    print(f'resumed {len(results)} pages', flush=True)

t0 = time.time()
done = 0
for i in range(N):
    if i in results and results[i].get('chars', 0) > 0:
        continue
    if i % 10 == 0:
        print(f'  page {i}/{N}  elapsed={time.time()-t0:.0f}s  done={len(results)}', flush=True)
    try:
        pix = doc[i].get_pixmap(dpi=200)
        img_path = f'/tmp/ocr_v4_p{i}.png'
        pix.save(img_path)
        result = ocr.predict(img_path)
        text = ""
        if result and len(result) > 0:
            item = result[0]
            if hasattr(item, 'rec_texts') and item.rec_texts:
                text = "\n".join(item.rec_texts)
            elif isinstance(item, dict) and 'rec_texts' in item:
                text = "\n".join(item['rec_texts'])
        results[i] = {'page': i, 'text': text, 'chars': len(text)}
        done += 1
    except Exception as e:
        results[i] = {'page': i, 'text': '', 'chars': 0, 'error': str(e)[:100]}
    # incremental save every 25 pages
    if (i + 1) % 25 == 0:
        _save(OUT, results)
        print(f'    [saved {len(results)} pages]', flush=True)

_save(OUT, results)
print(f'DONE. pages={len(results)} elapsed={time.time()-t0:.0f}s', flush=True)
