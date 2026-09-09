#!/bin/bash
# Paper-OS 完整初始化脚本
# 用途：一键初始化所有系统组件

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     Paper-OS 完整初始化脚本                              ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# 创建必要的目录
echo "📁 创建目录结构..."
mkdir -p data exports logs interactive_learning code_practice knowledge_graph ai_qa code_index practice_projects

# 步骤1: 初始化数据库
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 1/6: 初始化数据库"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ ! -f "data/paper_os.db" ]; then
    python3 import_data.py
else
    echo "✅ 数据库已存在，跳过初始化"
fi

# 步骤2: 生成代码练习
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 2/6: 生成代码练习"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 generate_practices.py

# 步骤3: 生成实践项目
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 3/6: 生成实践项目"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 generate_projects.py

# 步骤4: 生成知识图谱
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 4/6: 生成知识图谱"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 generate_knowledge_graph.py

# 步骤5: 扫描应用代码（可选）
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 5/6: 扫描应用代码（需要较长时间）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
read -p "是否扫描应用代码？这可能需要几分钟时间。(y/n): " scan_choice
if [ "$scan_choice" = "y" ]; then
    python3 scan_applications.py
else
    echo "⏭️  跳过应用代码扫描"
fi

# 步骤6: 完善项目（修复README、添加测试脚本）
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 6/6: 完善项目结构"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "complete_project.py" ]; then
    python3 complete_project.py
else
    echo "⚠️  complete_project.py 不存在，跳过"
fi

# 显示系统状态
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "系统状态"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 -c "
from data_manager import DatabaseManager
from utils import ConfigManager
import os

config = ConfigManager()
db = DatabaseManager(config.get('paths.db_file', 'data/paper_os.db'))
stats = db.get_statistics()

print(f'📚 论文资源:')
print(f'   论文总数: {stats[\"total_papers\"]}')
print(f'   有深度解读: {stats[\"papers_with_analysis\"]}')
print(f'   总引用数: {stats[\"total_citations\"]:,}')

print(f'\\n💻 代码学习:')
practice_count = len([d for d in os.listdir('code_practice') if os.path.isdir(f'code_practice/{d}')]) if os.path.exists('code_practice') else 0
print(f'   代码练习类别: {practice_count}个')

print(f'\\n🔨 实践项目:')
project_count = len([d for d in os.listdir('practice_projects') if os.path.isdir(f'practice_projects/{d}')]) if os.path.exists('practice_projects') else 0
print(f'   实践项目: {project_count}个')

print(f'\\n📊 知识图谱:')
if os.path.exists('knowledge_graph/knowledge_graph.dot'):
    print(f'   ✅ 已生成')
else:
    print(f'   ⚠️  未生成')

print(f'\\n🔍 代码索引:')
if os.path.exists('code_index'):
    index_files = len([f for f in os.listdir('code_index') if f.endswith('.json')])
    print(f'   已扫描 {index_files} 个项目')
else:
    print(f'   ⚠️  未生成')

db.close()
"

# 完成
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║     ✅ 初始化完成！                                     ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "🚀 快速开始:"
echo "   ./paper_os_v2.sh     # 启动主菜单"
echo "   python3 interactive_learning.py  # 交互式学习"
echo "   python3 ai_qa_improved.py       # AI问答系统"
echo ""
