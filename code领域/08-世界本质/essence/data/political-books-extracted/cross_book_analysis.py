"""跨书主题对照+概念数据库——从700万字全文提取关键概念和跨书对照"""
import json, os, re, sys
from collections import defaultdict

EXTRACTED_DIR = "/mnt/c/workspace/essence/data/political-books-extracted"
OUT = "/mnt/c/workspace/essence/analysis/political-books-cross-book-analysis.md"

# 关键概念列表
CONCEPTS = {
    '国家能力': ['国家能力', 'state capacity'],
    '合法性': ['合法性', 'legitimacy'],
    '运动式治理': ['运动式治理', '运动型治理', 'campaign'],
    '行政发包': ['行政发包', '发包制'],
    '晋升锦标赛': ['晋升锦标赛', '锦标赛'],
    '土地财政': ['土地财政', '土地出让'],
    '一统体制': ['一统体制', '一统'],
    '有效治理': ['有效治理'],
    '共谋': ['共谋'],
    '逆向软预算约束': ['逆向软预算', '软预算约束'],
    '绩效合法性': ['绩效合法性', '绩效'],
    '国家与社会': ['国家与社会', '国家-社会', 'state and society'],
    '官僚制': ['官僚制', '官僚体制', 'bureaucra'],
    '分税制': ['分税制'],
    '半脱嵌': ['半脱嵌'],
    '党国': ['党国', '党政'],
    '社会运动': ['社会运动', 'social movement'],
    '民族主义': ['民族主义', 'nationalism'],
    '民主化': ['民主化', 'democratization'],
    '数目字管理': ['数目字管理'],
    '大共同体': ['大共同体'],
    '小共同体': ['小共同体'],
    '附近': ['附近'],
    '悬浮': ['悬浮'],
    '关系丛': ['关系丛'],
    '文化霸权': ['文化霸权', 'hegemony'],
    '意识形态': ['意识形态', 'ideology'],
    '权力': ['权力', 'power'],
    '权威': ['权威', 'authority'],
    '主权': ['主权', 'sovereignty'],
    '法治': ['法治', 'rule of law'],
    '人治': ['人治'],
    '改革': ['改革', 'reform'],
    '开放': ['开放', 'opening'],
    '社会主义': ['社会主义', 'socialism'],
    '资本主义': ['资本主义', 'capitalism'],
    '市场经济': ['市场经济', 'market economy'],
    '全球化': ['全球化', 'globalization'],
    '数字治理': ['数字治理', '算法', '平台'],
    '腐败': ['腐败', 'corruption'],
    '维稳': ['维稳', '稳定'],
    '集体行动': ['集体行动', 'collective action'],
    '制度': ['制度', 'institution'],
    '路径依赖': ['路径依赖', 'path dependence'],
}

# 加载所有有全文的书
books = []
for fname in os.listdir(EXTRACTED_DIR):
    if not fname.endswith('.json') or fname.startswith('ocr_'):
        continue
    try:
        d = json.load(open(os.path.join(EXTRACTED_DIR, fname), 'r', encoding='utf-8'))
        if d.get('total_chars', 0) > 1000:
            books.append(d)
    except:
        pass

# 也加载OCR的书
for fname in os.listdir(EXTRACTED_DIR):
    if fname.startswith('ocr_') and fname.endswith('.json'):
        try:
            d = json.load(open(os.path.join(EXTRACTED_DIR, fname), 'r', encoding='utf-8'))
            if d.get('total_chars', 0) > 100:
                books.append(d)
        except:
            pass

print(f"加载了 {len(books)} 本书", file=sys.stderr)

# 概念数据库——每个概念在哪些书里出现，出现多少次
concept_db = {}
for concept, keywords in CONCEPTS.items():
    concept_db[concept] = {
        'keywords': keywords,
        'books': [],  # (book_name, count, sample_paragraph)
    }
    
    for book in books:
        book_name = book.get('filename', '?')[:40]
        full_text = book.get('full_text', [])
        if not full_text:
            # OCR格式
            full_text = book.get('pages', [])
        
        count = 0
        sample = None
        
        for page_data in full_text:
            text = page_data.get('text', '') if isinstance(page_data, dict) else str(page_data)
            for kw in keywords:
                count += text.count(kw)
                if not sample and kw in text:
                    # 提取上下文
                    idx = text.find(kw)
                    start = max(0, idx - 100)
                    end = min(len(text), idx + 200)
                    sample = text[start:end].replace('\n', ' ').strip()
        
        if count > 0:
            concept_db[concept]['books'].append({
                'book': book_name,
                'count': count,
                'sample': sample[:300] if sample else None,
            })

# 按出现次数排序
for concept in concept_db:
    concept_db[concept]['books'].sort(key=lambda x: -x['count'])

# 生成报告
with open(OUT, 'w', encoding='utf-8') as f:
    f.write("# 跨书主题对照 + 概念数据库\n\n")
    f.write(f"> 基于 {len(books)} 本书（{sum(b.get('total_chars',0) for b in books):,}字）的全文分析\n")
    f.write(f"> 提取 {len(CONCEPTS)} 个关键概念在每本书中的出现频率和上下文\n\n")
    f.write("---\n\n")
    
    # 概念索引
    f.write("## 概念索引（按覆盖书籍数排序）\n\n")
    f.write("| 概念 | 出现在几本书 | 总出现次数 | 最多的书 |\n")
    f.write("|------|------------|-----------|---------|\n")
    
    concept_stats = []
    for concept, data in concept_db.items():
        book_count = len(data['books'])
        total_count = sum(b['count'] for b in data['books'])
        top_book = data['books'][0]['book'][:30] if data['books'] else '-'
        top_count = data['books'][0]['count'] if data['books'] else 0
        concept_stats.append((concept, book_count, total_count, top_book, top_count))
    
    concept_stats.sort(key=lambda x: -x[1])
    for concept, bc, tc, tb, tcount in concept_stats:
        f.write(f"| {concept} | {bc}本 | {tc}次 | {tb}({tcount}次) |\n")
    
    # 每个概念的详细对照
    f.write("\n---\n\n## 概念详细对照\n\n")
    
    for concept, data in sorted(concept_db.items(), key=lambda x: -len(x[1]['books'])):
        if not data['books']:
            continue
        
        f.write(f"### 「{concept}」— 出现在 {len(data['books'])} 本书中\n\n")
        f.write(f"**关键词**: {', '.join(data['keywords'])}\n\n")
        f.write(f"| 书名 | 出现次数 | 上下文摘录 |\n")
        f.write(f"|------|---------|-----------|\n")
        
        for b in data['books'][:8]:
            sample = b['sample'][:200] + '...' if b['sample'] and len(b['sample']) > 200 else (b['sample'] or '-')
            f.write(f"| {b['book']} | {b['count']} | {sample} |\n")
        
        f.write("\n")
    
    # 跨书主题对照
    f.write("---\n\n## 跨书主题对照\n\n")
    
    themes = [
        ('中国国家治理', ['一统体制', '有效治理', '运动式治理', '行政发包', '晋升锦标赛', '共谋', '逆向软预算约束']),
        ('财政与土地', ['土地财政', '分税制', '半脱嵌']),
        ('合法性与政治', ['合法性', '绩效合法性', '国家能力', '权威', '主权']),
        ('国家与社会', ['国家与社会', '社会运动', '集体行动', '大共同体', '小共同体', '附近', '悬浮']),
        ('意识形态与文化', ['意识形态', '文化霸权', '民族主义']),
        ('制度与法治', ['制度', '法治', '人治', '官僚制', '路径依赖']),
        ('经济体制', ['社会主义', '资本主义', '市场经济', '改革', '开放', '全球化']),
        ('数字时代', ['数字治理', '腐败', '维稳']),
    ]
    
    for theme_name, theme_concepts in themes:
        f.write(f"### 主题：{theme_name}\n\n")
        f.write(f"涉及概念: {', '.join(theme_concepts)}\n\n")
        
        # 找涉及这个主题的书
        theme_books = set()
        for c in theme_concepts:
            for b in concept_db.get(c, {}).get('books', []):
                theme_books.add(b['book'])
        
        f.write(f"涉及书籍: {len(theme_books)}本\n")
        if theme_books:
            for b in sorted(theme_books)[:10]:
                f.write(f"- {b}\n")
        f.write("\n")

print(f"=== 跨书分析报告已生成: {OUT} ===", file=sys.stderr)
print(f"分析了 {len(books)} 本书, {len(CONCEPTS)} 个概念", file=sys.stderr)
