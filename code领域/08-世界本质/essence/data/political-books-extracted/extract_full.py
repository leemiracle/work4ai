"""提取单本PDF的全文——每一页的完整文本"""
import fitz, json, os, sys, hashlib

path = sys.argv[1]
outdir = os.path.dirname(os.path.abspath(__file__))
fname = os.path.basename(path)
md5 = hashlib.md5(fname.encode()).hexdigest()[:12]
outpath = os.path.join(outdir, f"{md5}.json")

try:
    doc = fitz.open(path)
    result = {
        'filename': fname,
        'md5': md5,
        'pages': doc.page_count,
        'toc': [],
        'full_text': [],  # 每页全文
        'total_chars': 0,
        'error': None
    }
    
    # TOC
    toc = doc.get_toc()
    if toc:
        result['toc'] = [[l, t, p] for l, t, p in toc]
    
    # 提取每一页全文
    total_chars = 0
    for i in range(doc.page_count):
        text = doc[i].get_text()
        if text:
            text = text.strip()
            if text:
                result['full_text'].append({
                    'page': i + 1,
                    'text': text
                })
                total_chars += len(text)
    
    result['total_chars'] = total_chars
    doc.close()
    
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✓ {fname[:55]:<55} | {result['pages']:>4}页 | 文本页:{len(result['full_text']):>4} | {total_chars:>8}字 | TOC:{len(result['toc'])}")
except Exception as e:
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump({'filename': fname, 'md5': md5, 'error': str(e)}, f, ensure_ascii=False, indent=2)
    print(f"✗ {fname[:55]:<55} | ERR: {e}")
