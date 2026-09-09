"""深度分析每本有全文的书——提取目录+前言+核心段落+关键概念"""
import json, os, re, sys

EXTRACTED_DIR = "/mnt/c/workspace/essence/data/political-books-extracted"
OUT_FILE = "/mnt/c/workspace/essence/data/political-books-extracted/analysis_report.md"

# 关键词——用于筛选重要段落
KEYWORDS = [
    '本质', '定义', '核心', '关键', '根本', '前提', '假设',
    '结论', '发现', '证明', '表明', '显示', '数据', '比例', '百分',
    '制度', '机制', '逻辑', '结构', '功能', '张力', '矛盾',
    '我认为', '本文', '本书', '研究', '论证', '分析',
    '合法性', '权威', '权力', '国家', '社会', '治理',
    '运动式', '发包', '锦标赛', '土地财政', '绩效',
]

def extract_toc_from_text(full_text):
    """从全文文本中解析目录（如果没有TOC）"""
    toc = []
    # 匹配 "第X章" "第X节" "X." 等
    patterns = [
        r'第[一二三四五六七八九十百零\d]+章\s*[^\n]{2,40}',
        r'第[一二三四五六七八九十百零\d]+节\s*[^\n]{2,40}',
        r'^[一二三四五六七八九十\d]+[、.．]\s*[^\n]{2,40}',
        r'^Chapter\s+\d+[^\n]{0,40}',
    ]
    for pattern in patterns:
        for page_data in full_text[:10]:  # 只在前10页找目录
            for m in re.finditer(pattern, page_data['text'], re.MULTILINE):
                title = m.group().strip()[:60]
                if title not in [t for _, t, _ in toc]:
                    toc.append([1, title, page_data['page']])
    return toc[:50]

def extract_key_paragraphs(full_text, max_paras=30):
    """提取含关键词的重要段落"""
    paragraphs = []
    for page_data in full_text:
        text = page_data['text']
        # 按段落分割
        paras = re.split(r'\n\s*\n', text)
        for para in paras:
            para = para.strip()
            if len(para) < 50 or len(para) > 500:
                continue
            # 检查是否含关键词
            kw_count = sum(1 for kw in KEYWORDS if kw in para)
            if kw_count >= 2:
                paragraphs.append({
                    'page': page_data['page'],
                    'text': para[:400],
                    'kw_score': kw_count
                })
            if len(paragraphs) >= max_paras * 3:
                break
        if len(paragraphs) >= max_paras * 3:
            break
    
    # 按关键词得分排序，取前max_paras
    paragraphs.sort(key=lambda x: x['kw_score'], reverse=True)
    return paragraphs[:max_paras]

def extract_preface(full_text):
    """提取前言/序言"""
    for page_data in full_text[:15]:
        text = page_data['text']
        if any(kw in text for kw in ['前言', '序言', '序', '导论', '导言', '引言', 'Preface', 'Introduction']):
            return {'page': page_data['page'], 'text': text[:3000]}
    # 如果没找到明确的前言，返回第3-5页（通常是前言位置）
    for page_data in full_text[2:8]:
        if len(page_data['text']) > 200:
            return {'page': page_data['page'], 'text': page_data['text'][:2000]}
    return None

# 处理所有有全文的书
books = []
for fname in sorted(os.listdir(EXTRACTED_DIR)):
    if not fname.endswith('.json') or fname == 'analysis_report.md':
        continue
    fpath = os.path.join(EXTRACTED_DIR, fname)
    try:
        d = json.load(open(fpath, 'r', encoding='utf-8'))
        chars = d.get('total_chars', 0)
        if chars < 1000:
            continue
        
        book = {
            'filename': d.get('filename', '?'),
            'pages': d.get('pages', 0),
            'chars': chars,
            'toc': d.get('toc', []),
            'full_text': d.get('full_text', []),
        }
        
        # 如果没有TOC，从文本解析
        if not book['toc']:
            book['toc_parsed'] = extract_toc_from_text(book['full_text'])
        
        # 提取前言
        book['preface'] = extract_preface(book['full_text'])
        
        # 提取关键段落
        book['key_paragraphs'] = extract_key_paragraphs(book['full_text'])
        
        books.append(book)
        print(f"✓ {book['filename'][:50]:<50} | {book['chars']:>8}字 | TOC:{len(book['toc'])+len(book.get('toc_parsed',[]))} | 关键段落:{len(book['key_paragraphs'])}", file=sys.stderr)
    except Exception as e:
        print(f"✗ {fname}: {e}", file=sys.stderr)

# 生成分析报告
with open(OUT_FILE, 'w', encoding='utf-8') as f:
    f.write("# 政治类书目全文深度分析报告\n\n")
    f.write(f"> 基于 {len(books)} 本有全文文本的书的原文分析\n")
    f.write(f"> 总字数: {sum(b['chars'] for b in books):,} 字\n")
    f.write(f"> 生成日期: 2026-07-12\n\n")
    f.write("---\n\n")
    
    for i, book in enumerate(books, 1):
        f.write(f"## 第 {i} 本 · {book['filename'][:60]}\n\n")
        f.write(f"**页数**: {book['pages']} | **字数**: {book['chars']:,} | **文本页**: {len(book['full_text'])}\n\n")
        
        # 目录
        toc = book['toc'] or book.get('toc_parsed', [])
        if toc:
            f.write("### 目录结构\n\n")
            for level, title, page in toc[:30]:
                indent = "  " * (level - 1)
                f.write(f"{indent}- {title} (p{page})\n")
            if len(toc) > 30:
                f.write(f"... 共 {len(toc)} 条\n")
            f.write("\n")
        
        # 前言
        if book.get('preface'):
            f.write("### 前言/序言摘录\n\n")
            f.write(f"> (p{book['preface']['page']})\n\n")
            f.write("```\n")
            f.write(book['preface']['text'][:2000])
            f.write("\n```\n\n")
        
        # 关键段落
        if book['key_paragraphs']:
            f.write("### 核心段落（按关键词密度排序，前10条）\n\n")
            for j, para in enumerate(book['key_paragraphs'][:10], 1):
                f.write(f"**段落 {j}** (p{para['page']}, 关键词得分:{para['kw_score']})\n\n")
                f.write(f"> {para['text'][:300]}\n\n")
            f.write("\n")
        
        f.write("---\n\n")

print(f"\n=== 分析报告已生成: {OUT_FILE} ===", file=sys.stderr)
print(f"分析了 {len(books)} 本书，总字数 {sum(b['chars'] for b in books):,}", file=sys.stderr)
