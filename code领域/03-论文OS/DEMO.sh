#!/bin/bash
# Paper-OS v2.0 演示脚本

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     Paper-OS v2.0 - 功能演示                             ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# 演示1: 数据库统计
echo "📊 演示1: 数据库统计"
echo "────────────────────────────────────────────────────────"
python3 -c "
from data_manager import DatabaseManager
from utils import ConfigManager

config = ConfigManager()
db = DatabaseManager(config.get('paths.db_file', 'data/paper_os.db'))
stats = db.get_statistics()

print(f'  论文总数: {stats[\"total_papers\"]}')
print(f'  有深度解读: {stats[\"papers_with_analysis\"]}')
print(f'  总引用数: {stats[\"total_citations\"]:,}')
print(f'  完成论文: {stats[\"completed_papers\"]}')
print(f'  平均进度: {stats[\"avg_progress\"]}%')

db.close()
"
echo ""

# 演示2: 论文列表
echo "📖 演示2: 热门论文 (Top 5)"
echo "────────────────────────────────────────────────────────"
python3 -c "
from data_manager import DatabaseManager
from utils import ConfigManager

config = ConfigManager()
db = DatabaseManager(config.get('paths.db_file', 'data/paper_os.db'))

cursor = db.conn.cursor()
cursor.execute('SELECT id, title, authors, citation_count FROM papers ORDER BY citation_count DESC LIMIT 5')
papers = cursor.fetchall()

for p in papers:
    print(f'  [{p[0]}] {p[1]}')
    print(f'      作者: {p[2]} | 引用: {p[3]:,}')

db.close()
"
echo ""

# 演示3: 代码练习统计
echo "💻 演示3: 代码实践统计"
echo "────────────────────────────────────────────────────────"
echo "  生成的练习类别:"
for dir in code_practice/*/; do
    category=$(basename "$dir")
    count=$(find "$dir" -maxdepth 1 -type d -name "*" | wc -l)
    echo "  • $category: $count 个练习"
done
echo ""

# 演示4: 知识图谱
echo "🔮 演示4: 知识图谱可视化"
echo "────────────────────────────────────────────────────────"
ls -lh knowledge_graph/ | tail -n +2 | awk '{print "  • " $9 " (" $5 ")"}'
echo ""

# 演示5: 智能问答示例
echo "🤖 演示5: 智能问答助手示例"
echo "────────────────────────────────────────────────────────"
python3 ai_qa.py "什么是自注意力机制" 2>/dev/null || echo "  (运行: python3 ai_qa.py 交互使用)"
echo ""

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     完整使用: ./paper_os.sh                             ║"
echo "╚══════════════════════════════════════════════════════════╝"
