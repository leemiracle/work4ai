"""统一处理所有PDF——检查已提取状态+提取缺失的"""
import fitz, json, os, hashlib, sys, time

BOOK_DIR = "/mnt/c/Users/mirac/Documents/个人/写书/政治"
OUT_DIR = "/mnt/c/workspace/essence/data/political-books-extracted"

def md5(fname):
    return hashlib.md5(fname.encode('utf-8')).hexdigest()[:12]

def extract_full(path, fname):
    """提取全文"""
    md = md5(fname)
    outpath = os.path.join(OUT_DIR, f"{md}.json")
    
    try:
        doc = fitz.open(path)
        result = {
            'filename': fname,
            'md5': md,
            'pages': doc.page_count,
            'toc': [],
            'full_text': [],
            'total_chars': 0,
            'error': None
        }
        toc = doc.get_toc()
        if toc:
            result['toc'] = [[l, t, p] for l, t, p in toc]
        
        total = 0
        for i in range(doc.page_count):
            text = doc[i].get_text()
            if text:
                text = text.strip()
                if text:
                    result['full_text'].append({'page': i+1, 'text': text})
                    total += len(text)
        
        result['total_chars'] = total
        doc.close()
        
        with open(outpath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        return result
    except Exception as e:
        with open(outpath, 'w', encoding='utf-8') as f:
            json.dump({'filename': fname, 'md5': md, 'error': str(e)}, f, ensure_ascii=False, indent=2)
        return {'filename': fname, 'error': str(e), 'pages': 0, 'total_chars': 0, 'toc': []}

# 遍历所有PDF
files = sorted([f for f in os.listdir(BOOK_DIR) if f.endswith('.pdf')])
print(f"共 {len(files)} 本 PDF\n")

stats = {'ok': 0, 'scan': 0, 'err': 0, 'skip': 0}

for fname in files:
    path = os.path.join(BOOK_DIR, fname)
    md = md5(fname)
    outpath = os.path.join(OUT_DIR, f"{md}.json")
    
    # 检查是否已提取
    if os.path.exists(outpath):
        try:
            with open(outpath, 'r', encoding='utf-8') as f:
                d = json.load(f)
            chars = d.get('total_chars', 0)
            pages = d.get('pages', 0)
            err = d.get('error', '')
            if err:
                stats['err'] += 1
                print(f"ERR  | {fname[:55]:<55} | {err[:40]}")
            elif chars > 100:
                stats['ok'] += 1
                print(f"OK   | {fname[:55]:<55} | {pages:>4}页 | {chars:>8}字")
            else:
                stats['scan'] += 1
                print(f"SCAN | {fname[:55]:<55} | {pages:>4}页 | 扫描版")
            stats['skip'] += 1
            continue
        except:
            pass  # 文件损坏，重新提取
    
    # 提取
    result = extract_full(path, fname)
    chars = result.get('total_chars', 0)
    pages = result.get('pages', 0)
    err = result.get('error', '')
    if err:
        stats['err'] += 1
        print(f"NEW ERR | {fname[:55]:<55} | {err[:40]}")
    elif chars > 100:
        stats['ok'] += 1
        print(f"NEW OK  | {fname[:55]:<55} | {pages:>4}页 | {chars:>8}字")
    else:
        stats['scan'] += 1
        print(f"NEW SCAN| {fname[:55]:<55} | {pages:>4}页 | 扫描版")

print(f"\n=== 统计: OK={stats['ok']} SCAN={stats['scan']} ERR={stats['err']} 总={len(files)} ===")
