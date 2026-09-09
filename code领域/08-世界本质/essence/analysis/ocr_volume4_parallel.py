#!/usr/bin/env python3
"""对《习近平谈治国理政》第四卷全量 OCR —— 多进程并行版。
4 个 PaddleOCR worker 并行处理，增量保存。"""
import os, sys, json, time, traceback
os.environ['FLAGS_use_mkldnn'] = '0'
import multiprocessing as mp

PDF = '/mnt/c/Users/mirac/Documents/个人/写书/政治/习近平谈治国理政4.pdf'
OUT = '/mnt/c/workspace/essence/data/political-books-extracted/ocr_9d9f947c94934cb5cb1f81bd21af50b2.json'
CHUNK_DIR = '/mnt/c/workspace/essence/data/political-books-extracted/v4_chunks'
N_WORKERS = 4
DPI = 150

os.makedirs(CHUNK_DIR, exist_ok=True)

def worker(args):
    worker_id, page_list = args
    import warnings; warnings.filterwarnings('ignore')
    import fitz
    from paddleocr import PaddleOCR
    ocr = PaddleOCR(lang='ch', enable_mkldnn=False, use_angle_cls=True)
    doc = fitz.open(PDF)
    results = []
    for i in page_list:
        try:
            pix = doc[i].get_pixmap(dpi=DPI)
            img_path = f'/tmp/v4_w{worker_id}_p{i}.png'
            pix.save(img_path)
            r = ocr.predict(img_path)
            texts = r[0]['rec_texts'] if r else []
            text = '\n'.join(texts)
            results.append({'page': i, 'text': text, 'chars': len(text)})
            os.remove(img_path)
        except Exception as e:
            results.append({'page': i, 'text': '', 'chars': 0, 'error': str(e)[:100]})
        if (len(results) % 5 == 0):
            # save chunk incrementally
            cf = os.path.join(CHUNK_DIR, f'w{worker_id}.json')
            tmp = cf + '.tmp'
            with open(tmp, 'w') as f:
                json.dump(results, f, ensure_ascii=False)
            os.replace(tmp, cf)
    cf = os.path.join(CHUNK_DIR, f'w{worker_id}.json')
    with open(cf, 'w') as f:
        json.dump(results, f, ensure_ascii=False)
    return worker_id, len(results)

def main():
    import fitz
    doc = fitz.open(PDF)
    N = doc.page_count
    print(f'Total pages: {N}, workers: {N_WORKERS}', flush=True)

    # resume: check existing chunks
    existing = {}
    for w in range(N_WORKERS):
        cf = os.path.join(CHUNK_DIR, f'w{w}.json')
        if os.path.exists(cf):
            data = json.load(open(cf))
            done_pages = {p['page'] for p in data}
            existing[w] = (data, done_pages)
            print(f'  worker {w}: resumed {len(data)} pages', flush=True)
        else:
            existing[w] = ([], set())

    # distribute pages round-robin
    worker_pages = [[] for _ in range(N_WORKERS)]
    for i in range(N):
        w = i % N_WORKERS
        if i not in existing[w][1]:
            worker_pages[w].append(i)

    tasks = [(w, worker_pages[w]) for w in range(N_WORKERS)]
    for w in range(N_WORKERS):
        print(f'  worker {w}: {len(tasks[w][1])} pages to do', flush=True)

    t0 = time.time()
    with mp.Pool(N_WORKERS) as pool:
        for wid, cnt in pool.imap_unordered(worker, tasks):
            print(f'  worker {wid} finished: {cnt} pages, elapsed {time.time()-t0:.0f}s', flush=True)

    # merge
    all_pages = []
    for w in range(N_WORKERS):
        cf = os.path.join(CHUNK_DIR, f'w{w}.json')
        data = json.load(open(cf))
        all_pages.extend(data)
    all_pages.sort(key=lambda x: x['page'])
    total_chars = sum(p.get('chars', 0) for p in all_pages)
    merged = {
        'filename': '习近平谈治国理政4.pdf',
        'md5': '9d9f947c94934cb5cb1f81bd21af50b2',
        'source': 'PaddleOCR v3.7 (full, 4-worker parallel)',
        'total_pages': N,
        'pages_ocrd': len(all_pages),
        'total_chars': total_chars,
        'pages': all_pages,
    }
    with open(OUT, 'w') as f:
        json.dump(merged, f, ensure_ascii=False)
    print(f'MERGED: {len(all_pages)} pages, {total_chars} chars, elapsed {time.time()-t0:.0f}s', flush=True)

if __name__ == '__main__':
    main()
