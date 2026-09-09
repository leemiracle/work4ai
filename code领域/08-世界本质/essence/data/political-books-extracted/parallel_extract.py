"""多进程并行提取所有PDF全文——8进程并行，每进程处理不同的书"""
import fitz, json, os, hashlib, sys, time
from multiprocessing import Pool, Manager

BOOK_DIR = "/mnt/c/Users/mirac/Documents/个人/写书/政治"
OUT_DIR = "/mnt/c/workspace/essence/data/political-books-extracted"

def md5(fname):
    return hashlib.md5(fname.encode('utf-8')).hexdigest()[:12]

def process_one(args):
    """处理单本书——在子进程中运行"""
    idx, fname = args
    path = os.path.join(BOOK_DIR, fname)
    md = md5(fname)
    outpath = os.path.join(OUT_DIR, f"{md}.json")
    
    # 检查是否已完成（有内容）
    if os.path.exists(outpath):
        try:
            d = json.load(open(outpath, 'r', encoding='utf-8'))
            if d.get('total_chars', 0) > 100 or d.get('error'):
                return (idx, fname, 'SKIP', d.get('pages',0), d.get('total_chars',0), d.get('error',''), len(d.get('toc',[])))
        except:
            pass
    
    try:
        doc = fitz.open(path)
        result = {
            'filename': fname, 'md5': md,
            'pages': doc.page_count, 'toc': [],
            'full_text': [], 'total_chars': 0, 'error': None
        }
        toc = doc.get_toc()
        if toc:
            result['toc'] = [[l,t,p] for l,t,p in toc]
        
        total = 0
        for i in range(doc.page_count):
            text = doc[i].get_text()
            if text and text.strip():
                result['full_text'].append({'page': i+1, 'text': text.strip()})
                total += len(text)
        
        result['total_chars'] = total
        doc.close()
        
        with open(outpath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        return (idx, fname, 'OK', result['pages'], total, None, len(result['toc']))
    except Exception as e:
        with open(outpath, 'w', encoding='utf-8') as f:
            json.dump({'filename': fname, 'md5': md, 'error': str(e)}, f, ensure_ascii=False, indent=2)
        return (idx, fname, 'ERR', 0, 0, str(e)[:50], 0)

if __name__ == '__main__':
    files = sorted([f for f in os.listdir(BOOK_DIR) if f.endswith('.pdf')])
    tasks = [(i, f) for i, f in enumerate(files)]
    print(f"共 {len(files)} 本 PDF，8进程并行提取...", file=sys.stderr)
    
    t0 = time.time()
    with Pool(8) as pool:
        results = pool.map(process_one, tasks)
    
    results.sort(key=lambda x: x[0])
    
    ok=scan=err=skip=0
    for idx, fname, status, pages, chars, error, toc_n in results:
        if status == 'SKIP':
            if chars > 100:
                ok += 1
                print(f"OK   | {fname[:55]:<55} | {pages:>4}页 | {chars:>8}字 | TOC:{toc_n}")
            elif error:
                err += 1
                print(f"ERR  | {fname[:55]:<55} | {error}")
            else:
                scan += 1
                print(f"SCAN | {fname[:55]:<55} | {pages:>4}页 | 扫描版 | TOC:{toc_n}")
            skip += 1
        elif status == 'OK':
            if chars > 100:
                ok += 1
                print(f"NEW OK  | {fname[:55]:<55} | {pages:>4}页 | {chars:>8}字 | TOC:{toc_n}")
            else:
                scan += 1
                print(f"NEW SCAN| {fname[:55]:<55} | {pages:>4}页 | 扫描版 | TOC:{toc_n}")
        else:
            err += 1
            print(f"NEW ERR | {fname[:55]:<55} | {error}")
    
    elapsed = time.time() - t0
    print(f"\n=== 完成: OK={ok} SCAN={scan} ERR={err} SKIP={skip} 耗时={elapsed:.1f}s ===", file=sys.stderr)
    print(f"有文本的书: {ok}本 | 扫描版: {scan}本 | 错误: {err}本", file=sys.stderr)
