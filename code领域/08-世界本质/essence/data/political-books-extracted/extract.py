import fitz, json, os, sys, hashlib

path = sys.argv[1]
outdir = os.path.dirname(sys.argv[0])
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
        'front_pages': [],
        'back_pages': [],
        'sample_pages': [],
        'error': None
    }
    
    toc = doc.get_toc()
    if toc:
        result['toc'] = [[l, t, p] for l, t, p in toc[:80]]
    
    # 前15页
    for i in range(min(15, doc.page_count)):
        text = doc[i].get_text()
        if text and len(text.strip()) > 30:
            result['front_pages'].append({'page': i+1, 'text': text[:5000]})
    
    # 后3页
    for i in range(max(0, doc.page_count-3), doc.page_count):
        text = doc[i].get_text()
        if text and len(text.strip()) > 30:
            result['back_pages'].append({'page': i+1, 'text': text[:3000]})
    
    # 中间采样——每30页取1页前1000字
    for i in range(15, doc.page_count-3, 30):
        text = doc[i].get_text()
        if text and len(text.strip()) > 50:
            result['sample_pages'].append({'page': i+1, 'text': text[:1000]})
    
    doc.close()
    
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✓ {fname[:55]:<55} | {result['pages']:>4}页 | TOC:{len(result['toc']):>3} | 前:{len(result['front_pages']):>2} | 样:{len(result['sample_pages']):>3}")
except Exception as e:
    # 即使出错也记录
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump({'filename': fname, 'md5': md5, 'error': str(e)}, f, ensure_ascii=False, indent=2)
    print(f"✗ {fname[:55]:<55} | ERR: {e}")
