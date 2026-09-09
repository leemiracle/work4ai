"""处理剩余8本有全文的书——习近平1-3卷+陈云1-3卷+钱穆+李岚清"""
import json, os, re, sys

EXTRACTED_DIR = "/mnt/c/workspace/essence/data/political-books-extracted"
OUT_FILE = "/mnt/c/workspace/essence/analysis/political-books-original-text-notes-2.md"

KEYWORDS = ['本质', '核心', '关键', '机制', '逻辑', '矛盾', '制度', '治理',
            '合法性', '权力', '国家', '社会', '发展', '改革', '经济', '政治',
            '社会主义', '资本主义', '市场', '计划', '阶级', '人民', '民主',
            '领导', '党', '宪法', '法律', '权利', '自由', '平等', '正义']

def process_book(d):
    """处理单本书"""
    name = d.get('filename', '?')
    chars = d.get('total_chars', 0)
    pages = d.get('pages', 0)
    full_text = d.get('full_text', [])
    toc = d.get('toc', [])
    
    result = {
        'filename': name,
        'chars': chars,
        'pages': pages,
        'toc': toc[:40],  # 只取前40条
        'preface': None,
        'key_paragraphs': [],
    }
    
    # 前言
    for page_data in full_text[:15]:
        text = page_data['text']
        if any(kw in text[:200] for kw in ['前言', '序言', '导论', '出版说明', '编辑说明', '内容提要']):
            result['preface'] = {'page': page_data['page'], 'text': text[:3000]}
            break
    if not result['preface'] and full_text:
        for page_data in full_text[1:8]:
            if len(page_data['text']) > 300:
                result['preface'] = {'page': page_data['page'], 'text': page_data['text'][:2000]}
                break
    
    # 核心段落
    all_paras = []
    for page_data in full_text:
        text = page_data['text']
        paras = re.split(r'\n\s*\n', text)
        for para in paras:
            para = para.strip()
            if 80 < len(para) < 500:
                score = sum(1 for k in KEYWORDS if k in para)
                if score >= 3:
                    all_paras.append({
                        'page': page_data['page'],
                        'text': para[:350],
                        'score': score
                    })
    
    all_paras.sort(key=lambda x: x['score'], reverse=True)
    result['key_paragraphs'] = all_paras[:15]
    
    return result

# 找剩余8本
already_done = ["中国国家治理", "转型中的地方政府", "以利为利", "波普尔", "政治的人生", "分析与思考", "过渡劳动"]
books_to_process = []

for fname in sorted(os.listdir(EXTRACTED_DIR)):
    if not fname.endswith('.json'):
        continue
    try:
        d = json.load(open(os.path.join(EXTRACTED_DIR, fname), 'r', encoding='utf-8'))
        if d.get('total_chars', 0) < 1000:
            continue
        name = d.get('filename', '')
        if any(kw in name for kw in already_done):
            continue
        books_to_process.append(d)
    except:
        pass

print(f"待处理: {len(books_to_process)} 本", file=sys.stderr)

# 生成笔记
with open(OUT_FILE, 'w', encoding='utf-8') as out:
    out.write("# 政治类书目原文深度笔记（第二批）\n\n")
    out.write(f"> 剩余 {len(books_to_process)} 本有全文的书的原文分析\n\n---\n\n")
    
    for book in books_to_process:
        result = process_book(book)
        name = result['filename'][:60]
        
        out.write(f"## {name}\n\n")
        out.write(f"**字数**: {result['chars']:,} | **页数**: {result['pages']}\n\n")
        
        # 目录
        if result['toc']:
            out.write("### 目录（前40条）\n\n")
            for level, title, page in result['toc']:
                indent = "  " * (level - 1)
                out.write(f"{indent}- {title} (p{page})\n")
            out.write("\n")
        
        # 前言
        if result['preface']:
            out.write(f"### 前言/出版说明（p{result['preface']['page']}）\n\n")
            out.write("```\n")
            out.write(result['preface']['text'][:2000])
            out.write("\n```\n\n")
        
        # 核心论断
        if result['key_paragraphs']:
            out.write("### 全书核心论断（前10条）\n\n")
            for i, para in enumerate(result['key_paragraphs'][:10], 1):
                out.write(f"**论断 {i}** (p{para['page']}, 得分:{para['score']})\n\n")
                out.write(f"> {para['text']}\n\n")
        
        out.write("---\n\n")
        print(f"✓ {name[:50]:<50} | {result['chars']:>8}字 | 段落:{len(result['key_paragraphs'])}", file=sys.stderr)

print(f"\n=== 第二批笔记已生成: {OUT_FILE} ===", file=sys.stderr)
