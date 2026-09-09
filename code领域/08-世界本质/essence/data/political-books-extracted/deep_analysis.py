"""基于全文原文生成深度笔记——每本书提取目录+前言+每章核心段落+关键概念"""
import json, os, re, sys

EXTRACTED_DIR = "/mnt/c/workspace/essence/data/political-books-extracted"
OUT_FILE = "/mnt/c/workspace/essence/analysis/political-books-original-text-notes.md"

# 重点分析的7本书（按重要性排序）
PRIORITY_BOOKS = [
    "中国国家治理的制度逻辑",  # 周雪光
    "转型中的地方政府",        # 周黎安
    "以利为利",               # 周飞舟
    "卡尔·波普尔",            # 波普尔
    "政治的人生",             # 王沪宁
    "分析与思考",             # 黄奇帆
    "过渡劳动",               # 孙萍
]

def find_book(keyword):
    """按关键词找书"""
    for fname in os.listdir(EXTRACTED_DIR):
        if not fname.endswith('.json'):
            continue
        try:
            d = json.load(open(os.path.join(EXTRACTED_DIR, fname), 'r', encoding='utf-8'))
            if d.get('total_chars', 0) > 1000 and keyword in d.get('filename', ''):
                return d
        except:
            pass
    return None

def extract_chapters(book):
    """从TOC或文本中提取章节结构"""
    toc = book.get('toc', [])
    if toc:
        return toc
    
    # 从文本解析
    chapters = []
    full_text = book.get('full_text', [])
    for page_data in full_text[:15]:
        text = page_data['text']
        # 匹配 "第X章" 标题
        for m in re.finditer(r'第[一二三四五六七八九十百零\d]+章\s*[^\n]{2,60}', text):
            title = m.group().strip()[:60]
            if not any(title == c[1] for c in chapters):
                chapters.append([1, title, page_data['page']])
        # 匹配 "Chapter X"
        for m in re.finditer(r'Chapter\s+\d+[^\n]{0,60}', text):
            title = m.group().strip()[:60]
            if not any(title == c[1] for c in chapters):
                chapters.append([1, title, page_data['page']])
    return chapters[:30]

def extract_chapter_content(book, chapter_title, chapter_page):
    """提取某章的核心内容——前2页文本"""
    full_text = book.get('full_text', [])
    contents = []
    
    # 找到章节起始页，提取前2-3页
    for i, page_data in enumerate(full_text):
        if chapter_title[:10] in page_data['text'] or page_data['page'] == chapter_page:
            # 提取该页及后2页的核心内容
            for j in range(i, min(i+3, len(full_text))):
                text = full_text[j]['text']
                # 找含关键词的段落
                paras = re.split(r'\n\s*\n', text)
                for para in paras:
                    para = para.strip()
                    if 100 < len(para) < 600:
                        kw = ['本质', '核心', '关键', '机制', '逻辑', '矛盾', '制度', '治理', '权力', '国家', '社会', '定义', '认为', '提出', ' argues', '发现']
                        if sum(1 for k in kw if k in para) >= 2:
                            contents.append({
                                'page': full_text[j]['page'],
                                'text': para[:400]
                            })
                            if len(contents) >= 3:
                                return contents
            break
    return contents

# 生成深度笔记
with open(OUT_FILE, 'w', encoding='utf-8') as out:
    out.write("# 政治类书目原文深度笔记\n\n")
    out.write("> 基于699万字全文提取的**原文引用**——不是概括，是原文\n")
    out.write(f"> 配套: [`political-books-fulltext-analysis.md`](./political-books-fulltext-analysis.md)\n\n")
    out.write("---\n\n")
    
    for keyword in PRIORITY_BOOKS:
        book = find_book(keyword)
        if not book:
            out.write(f"## {keyword}（未找到全文）\n\n---\n\n")
            continue
        
        name = book['filename'][:60]
        chars = book['total_chars']
        pages = book['pages']
        
        out.write(f"## {name}\n\n")
        out.write(f"**字数**: {chars:,} | **页数**: {pages} | **文本页**: {len(book.get('full_text',[]))}\n\n")
        
        # 目录
        chapters = extract_chapters(book)
        if chapters:
            out.write("### 完整目录\n\n")
            for level, title, page in chapters:
                indent = "  " * (level - 1)
                out.write(f"{indent}- {title} (p{page})\n")
            out.write("\n")
        
        # 前言
        full_text = book.get('full_text', [])
        preface_found = False
        for page_data in full_text[:15]:
            text = page_data['text']
            if any(kw in text[:200] for kw in ['前言', '序言', '导论', '导言', '引言', '内容提要', 'Preface']):
                out.write(f"### 前言/导论原文（p{page_data['page']}）\n\n")
                out.write("```\n")
                out.write(text[:3000])
                out.write("\n```\n\n")
                preface_found = True
                break
        if not preface_found and full_text:
            # 用第3-5页作为"开篇"
            for page_data in full_text[2:6]:
                if len(page_data['text']) > 300:
                    out.write(f"### 开篇文本（p{page_data['page']}）\n\n")
                    out.write("```\n")
                    out.write(page_data['text'][:2000])
                    out.write("\n```\n\n")
                    break
        
        # 每章核心段落
        if chapters:
            out.write("### 各章核心段落（原文引用）\n\n")
            for level, title, page in chapters[:12]:  # 前12章
                contents = extract_chapter_content(book, title, page)
                if contents:
                    out.write(f"#### {title}\n\n")
                    for c in contents[:2]:  # 每章最多2段
                        out.write(f"> (p{c['page']})\n")
                        out.write(f"> {c['text']}\n\n")
        
        # 全书最重要段落（关键词密度最高的5段）
        all_paras = []
        for page_data in full_text:
            text = page_data['text']
            paras = re.split(r'\n\s*\n', text)
            for para in paras:
                para = para.strip()
                if 100 < len(para) < 500:
                    kw = ['本质', '核心', '关键', '机制', '逻辑', '矛盾', '制度', '治理', '合法性', '权力', '国家', '社会', '运动式', '发包', '锦标赛', '土地财政', '绩效', '一统', '有效']
                    score = sum(1 for k in kw if k in para)
                    if score >= 3:
                        all_paras.append({
                            'page': page_data['page'],
                            'text': para[:350],
                            'score': score
                        })
        
        all_paras.sort(key=lambda x: x['score'], reverse=True)
        if all_paras:
            out.write("### 全书核心论断（关键词密度最高，前8段）\n\n")
            for i, para in enumerate(all_paras[:8], 1):
                out.write(f"**论断 {i}** (p{para['page']}, 得分:{para['score']})\n\n")
                out.write(f"> {para['text']}\n\n")
        
        out.write("---\n\n")
        print(f"✓ {name[:50]:<50} | {chars:>8}字 | 章:{len(chapters):>3} | 核心段落:{len(all_paras)}", file=sys.stderr)

print(f"\n=== 深度笔记已生成: {OUT_FILE} ===", file=sys.stderr)
