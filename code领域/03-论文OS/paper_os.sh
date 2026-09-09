#!/bin/bash
# Paper-OS 主启动脚本

echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo "║     🚀 Paper-OS - AI论文深度学习与资源整合系统            ║"
echo "║                                                          ║"
echo "║     版本: 2.0.0                                          ║"
echo "║     论文: 40篇 | 引用: 505,200+                          ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3"
    exit 1
fi

# 创建必要的目录
mkdir -p data exports logs interactive_learning code_practice knowledge_graph ai_qa

# 初始化数据库（如果不存在）
if [ ! -f "data/paper_os.db" ]; then
    echo "📦 初始化数据库..."
    python3 import_data.py
fi

# 主菜单
show_menu() {
    echo ""
    echo "══════════════════════════════════════════════════════════"
    echo "                    主菜单"
    echo "══════════════════════════════════════════════════════════"
    echo ""
    echo "  📚 学习系统"
    echo "     1. 交互式学习系统 (CLI)"
    echo "     2. 查看论文列表"
    echo "     3. 查看学习进度"
    echo "     4. 导出学习报告"
    echo ""
    echo "  🔧 实践系统"
    echo "     5. 代码实践练习"
    echo "     6. 运行测验"
    echo ""
    echo "  🤖 AI工具"
    echo "     7. 智能问答助手 (RAG)"
    echo "     8. 知识图谱可视化"
    echo ""
    echo "  ⚙️  系统管理"
    echo "     9. 刷新数据"
    echo "     10. 查看统计信息"
    echo "     0. 退出"
    echo ""
    echo "══════════════════════════════════════════════════════════"
}

# 统计信息
show_stats() {
    echo ""
    echo "📊 系统统计"
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
print(f'  平均进度: {stats[\"avg_progress\"]}%')
print(f'  完成论文: {stats[\"completed_papers\"]}')

print(f'\\n  按类别统计:')
for category, count in stats['by_category'].items():
    print(f'    • {category}: {count}篇')

db.close()
"
    
    echo "────────────────────────────────────────────────────────"
}

# 主循环
while true; do
    show_menu
    read -p "请选择操作 (0-10): " choice
    
    case $choice in
        1)
            python3 interactive_learning.py
            ;;
        2)
            python3 -c "
from data_manager import DatabaseManager
from utils import ConfigManager

config = ConfigManager()
db = DatabaseManager(config.get('paths.db_file', 'data/paper_os.db'))

cursor = db.conn.cursor()
cursor.execute('SELECT id, title, authors, citation_count FROM papers ORDER BY citation_count DESC LIMIT 15')
papers = cursor.fetchall()

print('\\n📖 热门论文 (Top 15):')
print('────────────────────────────────────────────────────────')
for p in papers:
    print(f'  [{p[0]}] {p[1]}')
    print(f'      作者: {p[2]} | 引用: {p[3]:,}')

db.close()
"
            ;;
        3)
            python3 -c "
from data_manager import DatabaseManager
from utils import ConfigManager

config = ConfigManager()
db = DatabaseManager(config.get('paths.db_file', 'data/paper_os.db'))

cursor = db.conn.cursor()
cursor.execute('''
    SELECT p.title, up.status, up.reading_progress, up.rating
    FROM user_progress up
    JOIN papers p ON up.paper_id = p.id
    WHERE up.user_id = 1
    ORDER BY up.status DESC, up.reading_progress DESC
''')
progress = cursor.fetchall()

print('\\n📈 学习进度:')
print('────────────────────────────────────────────────────────')
if progress:
    for p in progress:
        status_emoji = {'completed': '✅', 'in_progress': '🔄', 'not_started': '⏸️'}
        status = status_emoji.get(p[1], '⏸️')
        rating = '⭐' * p[3] if p[3] else ''
        print(f'  {status} {p[0]}')
        print(f'      进度: {p[2]}% | 评分: {rating}')
else:
    print('  暂无学习记录')

db.close()
"
            ;;
        4)
            python3 -c "
from data_manager import DatabaseManager
from utils import ConfigManager, DataExporter

config = ConfigManager()
db = DatabaseManager(config.get('paths.db_file', 'data/paper_os.db'))

cursor = db.conn.cursor()
cursor.execute('''
    SELECT p.*, up.status, up.reading_progress, up.notes, up.rating
    FROM user_progress up
    JOIN papers p ON up.paper_id = p.id
    WHERE up.user_id = 1
''')
progress = [dict(row) for row in cursor.fetchall()]

DataExporter.export_progress_report(progress, 'exports/progress_report.md')
print('\\n✅ 学习报告已导出: exports/progress_report.md')

db.close()
"
            ;;
        5)
            echo ""
            echo "🔧 代码实践练习"
            echo "────────────────────────────────────────────────────────"
            echo ""
            echo "已生成的练习类别:"
            ls -d code_practice/*/ 2>/dev/null | sed 's|code_practice/||' | sed 's|/||' | while read dir; do
                count=$(find "code_practice/$dir" -maxdepth 1 -type d -name "*" | wc -l)
                echo "  • $dir ($count 个练习)"
            done
            echo ""
            echo "练习文件位于: code_practice/"
            echo "────────────────────────────────────────────────────────"
            ;;
        6)
            python3 -c "
from utils import ConfigManager
from data_manager import DatabaseManager

config = ConfigManager()
db = DatabaseManager(config.get('paths.db_file', 'data/paper_os.db'))

cursor = db.conn.cursor()
cursor.execute('SELECT * FROM papers ORDER BY RANDOM() LIMIT 1')
paper = cursor.fetchone()

print(f'\\n🧠 随机测验: {paper[\"title\"]}')
print('────────────────────────────────────────────────────────')

print(f'\\nQ1: 这篇论文的主要作者是谁？')
print(f'   A. {paper[\"authors\"]}')
print(f'   B. Unknown')
print(f'   C. OpenAI')
print(f'   D. Google Brain')

print(f'\\nQ2: 这篇论文发表于哪一年？')
print(f'   A. {paper[\"year\"]}')
print(f'   B. 2021')
print(f'   C. 2022')
print(f'   D. 2023')

print(f'\\nQ3: 这篇论文的引用次数大约是多少？')
print(f'   A. ~{paper[\"citation_count\"]}')
print(f'   B. 1000+')
print(f'   C. 10000+')
print(f'   D. 50000+')

print('\\n正确答案: A, A, A')
print(f'详细解释可使用交互式学习系统的测验功能')

db.close()
"
            ;;
        7)
            echo ""
            echo "🤖 智能问答助手"
            echo "────────────────────────────────────────────────────────"
            echo "基于论文分析文档的智能问答系统"
            echo ""
            python3 ai_qa.py
            ;;
        8)
            echo ""
            echo "🔮 生成知识图谱可视化..."
            echo "────────────────────────────────────────────────────────"
            python3 generate_knowledge_graph.py
            echo ""
            echo "生成的文件:"
            ls -lh knowledge_graph/
            ;;
        9)
            echo ""
            echo "🔄 刷新数据..."
            echo "────────────────────────────────────────────────────────"
            python3 import_data.py
            ;;
        10)
            show_stats
            ;;
        0)
            echo ""
            echo "👋 感谢使用 Paper-OS!"
            echo ""
            exit 0
            ;;
        *)
            echo ""
            echo "❌ 无效选择，请重试"
            ;;
    esac
    
    echo ""
    read -p "按回车键继续..."
done
