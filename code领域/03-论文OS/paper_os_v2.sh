#!/bin/bash
# Paper-OS v2.0 深度利用主启动脚本

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║     🚀 Paper-OS v2.0 - AI论文深度学习与资源整合系统            ║"
echo "║                                                                  ║"
echo "║     版本: 2.1.0                                                  ║"
echo "║     论文: 40篇 | 代码练习: 15个 | 实践项目: 8个                   ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3"
    exit 1
fi

# 创建必要的目录
mkdir -p data exports logs interactive_learning code_practice knowledge_graph ai_qa code_index practice_projects

# 初始化数据库（如果不存在）
if [ ! -f "data/paper_os.db" ]; then
    echo "📦 初始化数据库..."
    python3 import_data.py
fi

# 主菜单
show_menu() {
    echo ""
    echo "══════════════════════════════════════════════════════════════════"
    echo "                    Paper-OS v2.1 主菜单"
    echo "══════════════════════════════════════════════════════════════════"
    echo ""
    echo "  📚 核心学习系统"
    echo "     1. 交互式学习系统 (CLI)"
    echo "     2. 查看论文列表"
    echo "     3. 查看学习进度"
    echo "     4. 导出学习报告"
    echo ""
    echo "  💻 代码学习系统"
    echo "     5. 代码实践练习"
    echo "     6. 智能代码助手 (新增)"
    echo "     7. 搜索代码片段"
    echo "     8. 运行测验"
    echo ""
    echo "  🔨 实践项目系统"
    echo "     9. 查看实践项目 (新增)"
    echo "     10. 生成新项目"
    echo ""
    echo "  🔮 AI工具"
    echo "     11. 智能问答助手 (RAG)"
    echo "     12. 知识图谱可视化"
    echo ""
    echo "  🔍 代码深度挖掘"
    echo "     13. 扫描应用代码 (新增)"
    echo "     14. 查看代码统计"
    echo ""
    echo "  ⚙️  系统管理"
    echo "     15. 刷新数据"
    echo "     16. 查看系统统计"
    echo "     17. 初始化所有系统"
    echo "     0. 退出"
    echo ""
    echo "══════════════════════════════════════════════════════════════════"
}

# 统计信息
show_stats() {
    echo ""
    echo "📊 系统统计"
    echo "────────────────────────────────────────────────────────"
    
    python3 -c "
from data_manager import DatabaseManager
from utils import ConfigManager
import os

config = ConfigManager()
db = DatabaseManager(config.get('paths.db_file', 'data/paper_os.db'))
stats = db.get_statistics()

print(f'  📚 论文资源:')
print(f'     论文总数: {stats[\"total_papers\"]}')
print(f'     有深度解读: {stats[\"papers_with_analysis\"]}')
print(f'     总引用数: {stats[\"total_citations\"]:,}')

print(f'\\n  💻 代码学习:')
print(f'     代码练习: 15个')

print(f'\\n  🔨 实践项目:')
project_count = len([d for d in os.listdir('practice_projects') if os.path.isdir(f'practice_projects/{d}')]) if os.path.exists('practice_projects') else 0
print(f'     可运行项目: {project_count}个')

print(f'\\n  👤 学习进度:')
print(f'     已完成论文: {stats[\"completed_papers\"]}')
print(f'     平均进度: {stats[\"avg_progress\"]}%')

db.close()
"
    
    echo "────────────────────────────────────────────────────────"
}

# 主循环
while true; do
    show_menu
    read -p "请选择操作 (0-17): " choice
    
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
            echo ""
            echo "🤖 智能代码助手"
            echo "────────────────────────────────────────────────────────"
            python3 code_assistant.py
            ;;
        7)
            echo ""
            echo "🔍 搜索代码片段"
            echo "────────────────────────────────────────────────────────"
            read -p "输入搜索关键词: " query
            if [ ! -z "$query" ]; then
                python3 -c "
from code_assistant import CodeAssistant, CodeIndexer

indexer = CodeIndexer()
if indexer.load_index():
    assistant = CodeAssistant(indexer)
    results = assistant.search_code('$query')
    
    if results:
        print(f'\\n找到 {len(results)} 个结果:')
        for r in results[:10]:
            print(f\"  • [{r['type']}] {r['name']} - {r['file']}\")
    else:
        print('\\n未找到结果')
else:
    print('\\n代码索引未建立，请先运行功能13')
"
            fi
            ;;
        8)
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

print(f'\\nQ2: 这篇论文发表于哪一年？')
print(f'   A. {paper[\"year\"]}')

print(f'\\nQ3: 这篇论文的引用次数大约是多少？')
print(f'   A. ~{paper[\"citation_count\"]}')

print('\\n使用交互式学习系统获取更多测验')

db.close()
"
            ;;
        9)
            echo ""
            echo "🔨 实践项目"
            echo "────────────────────────────────────────────────────────"
            if [ -d "practice_projects" ]; then
                echo ""
                echo "可运行项目:"
                for project in practice_projects/*/; do
                    project_name=$(basename "$project")
                    if [ -f "$project/README.md" ]; then
                        echo "  📦 $project_name"
                        echo "     路径: $project"
                    fi
                done
                echo ""
                echo "查看详细说明: cd practice_projects/<项目名>"
            else
                echo "  暂无实践项目，请运行功能10"
            fi
            ;;
        10)
            echo ""
            echo "🔨 生成新项目"
            echo "────────────────────────────────────────────────────────"
            echo "这将生成8个实践项目的完整代码模板"
            read -p "确认生成? (y/n): " confirm
            if [ "$confirm" = "y" ]; then
                python3 generate_projects.py
            fi
            ;;
        11)
            echo ""
            echo "🤖 智能问答助手"
            echo "────────────────────────────────────────────────────────"
            echo "基于论文分析文档的智能问答系统"
            echo ""
            python3 ai_qa.py
            ;;
        12)
            echo ""
            echo "🔮 生成知识图谱可视化..."
            echo "────────────────────────────────────────────────────────"
            python3 generate_knowledge_graph.py
            echo ""
            echo "生成的文件:"
            ls -lh knowledge_graph/ | tail -n +2
            ;;
        13)
            echo ""
            echo "🔍 扫描应用代码"
            echo "────────────────────────────────────────────────────────"
            echo "这将扫描所有应用项目的代码并建立索引"
            read -p "确认扫描? (y/n): " confirm
            if [ "$confirm" = "y" ]; then
                python3 scan_applications.py
            fi
            ;;
        14)
            echo ""
            echo "📊 代码统计"
            echo "────────────────────────────────────────────────────────"
            if [ -d "code_index" ]; then
                ls -lh code_index/*.json 2>/dev/null | awk '{print "  • " $9 " (" $5 ")"}'
            else
                echo "  暂无代码统计数据，请先运行功能13"
            fi
            ;;
        15)
            echo ""
            echo "🔄 刷新数据..."
            echo "────────────────────────────────────────────────────────"
            python3 import_data.py
            ;;
        16)
            show_stats
            ;;
        17)
            echo ""
            echo "⚙️  初始化所有系统"
            echo "────────────────────────────────────────────────────────"
            echo "1. 初始化数据库..."
            python3 import_data.py
            echo ""
            echo "2. 生成代码练习..."
            python3 generate_practices.py
            echo ""
            echo "3. 生成实践项目..."
            python3 generate_projects.py
            echo ""
            echo "4. 生成知识图谱..."
            python3 generate_knowledge_graph.py
            echo ""
            echo "✅ 初始化完成！"
            ;;
        0)
            echo ""
            echo "👋 感谢使用 Paper-OS v2.0!"
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

