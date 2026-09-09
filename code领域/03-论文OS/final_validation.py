#!/usr/bin/env python3
"""
Paper-OS 最终验证测试脚本
用于测试所有核心功能是否正常工作
"""
import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """测试核心模块导入"""
    print("📦 测试核心模块导入...")
    
    try:
        from data_manager import DatabaseManager
        from utils import ConfigManager
        print("  ✅ data_manager, utils")
        
        import interactive_learning
        print("  ✅ interactive_learning")
        
        import ai_qa_improved
        print("  ✅ ai_qa_improved")
        
        import generate_practices
        print("  ✅ generate_practices")
        
        import generate_projects
        print("  ✅ generate_projects")
        
        import generate_knowledge_graph
        print("  ✅ generate_knowledge_graph")
        
        import scan_applications
        print("  ✅ scan_applications")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 导入失败: {e}")
        return False


def test_database():
    """测试数据库功能"""
    print("\n🗄️  测试数据库功能...")
    
    try:
        from data_manager import DatabaseManager
        from utils import ConfigManager
        
        config = ConfigManager()
        db = DatabaseManager(config.get('paths.db_file', 'data/paper_os.db'))
        
        stats = db.get_statistics()
        
        print(f"  ✅ 论文总数: {stats['total_papers']}")
        print(f"  ✅ 有深度解读: {stats['papers_with_analysis']}")
        print(f"  ✅ 总引用数: {stats['total_citations']:,}")
        
        if stats['total_papers'] == 0:
            print("  ❌ 数据库中没有论文数据")
            return False
        
        db.close()
        return True
        
    except Exception as e:
        print(f"  ❌ 数据库测试失败: {e}")
        return False


def test_ai_qa():
    """测试AI问答系统"""
    print("\n🤖 测试AI问答系统...")
    
    try:
        from ai_qa_improved import ImprovedSimpleQA
        from data_manager import DatabaseManager
        from utils import ConfigManager
        
        config = ConfigManager()
        db = DatabaseManager(config.get('paths.db_file', 'data/paper_os.db'))
        
        qa = ImprovedSimpleQA(db, config.get('paths.base_dir', '.'))
        
        if len(qa.documents) == 0:
            print("  ❌ 没有加载文档")
            return False
        
        print(f"  ✅ 加载文档: {len(qa.documents)}篇")
        
        # 测试搜索
        results = qa.search("attention", top_k=1)
        print(f"  ✅ 搜索功能正常: 找到{len(results)}个结果")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"  ❌ AI问答测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_code_practice():
    """测试代码练习"""
    print("\n💻 测试代码练习...")
    
    try:
        practice_dir = Path('code_practice')
        
        if not practice_dir.exists():
            print("  ❌ 代码练习目录不存在")
            return False
        
        categories = [d for d in practice_dir.iterdir() if d.is_dir()]
        
        if len(categories) == 0:
            print("  ❌ 没有找到代码练习类别")
            return False
        
        print(f"  ✅ 代码练习类别: {len(categories)}个")
        
        total_exercises = 0
        for category in categories:
            exercises = [e for e in category.iterdir() if e.is_dir()]
            total_exercises += len(exercises)
        
        print(f"  ✅ 代码练习总数: {total_exercises}个")
        return True
        
    except Exception as e:
        print(f"  ❌ 代码练习测试失败: {e}")
        return False


def test_practice_projects():
    """测试实践项目"""
    print("\n🔨 测试实践项目...")
    
    try:
        projects_dir = Path('practice_projects')
        
        if not projects_dir.exists():
            print("  ❌ 实践项目目录不存在")
            return False
        
        projects = [d for d in projects_dir.iterdir() if d.is_dir()]
        
        if len(projects) == 0:
            print("  ❌ 没有找到实践项目")
            return False
        
        print(f"  ✅ 实践项目: {len(projects)}个")
        
        # 检查每个项目的完整度
        complete_projects = 0
        for project in projects:
            has_readme = (project / 'README.md').exists()
            has_main = (project / 'main.py').exists()
            has_config = (project / 'config.py').exists()
            
            if has_readme and has_main and has_config:
                complete_projects += 1
        
        print(f"  ✅ 完整项目: {complete_projects}/{len(projects)}")
        return True
        
    except Exception as e:
        print(f"  ❌ 实践项目测试失败: {e}")
        return False


def test_knowledge_graph():
    """测试知识图谱"""
    print("\n🔮 测试知识图谱...")
    
    try:
        kg_dir = Path('knowledge_graph')
        
        if not kg_dir.exists():
            print("  ❌ 知识图谱目录不存在")
            return False
        
        dot_file = kg_dir / 'knowledge_graph.dot'
        timeline_file = kg_dir / 'timeline.md'
        category_file = kg_dir / 'category_tree.md'
        
        if dot_file.exists() and timeline_file.exists() and category_file.exists():
            print("  ✅ 知识图谱文件完整")
            return True
        else:
            print("  ❌ 知识图谱文件不完整")
            return False
        
    except Exception as e:
        print(f"  ❌ 知识图谱测试失败: {e}")
        return False


def test_code_index():
    """测试代码索引"""
    print("\n🔍 测试代码索引...")
    
    try:
        index_dir = Path('code_index')
        
        if not index_dir.exists():
            print("  ⚠️  代码索引目录不存在（可选功能）")
            return True
        
        json_files = list(index_dir.glob('*.json'))
        
        if len(json_files) > 0:
            print(f"  ✅ 代码索引: {len(json_files)}个项目")
            return True
        else:
            print("  ⚠️  没有找到代码索引文件（可选功能）")
            return True
        
    except Exception as e:
        print(f"  ❌ 代码索引测试失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("╔══════════════════════════════════════════════════════════╗")
    print("║     Paper-OS 最终验证测试                               ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    
    tests = [
        ("核心模块导入", test_imports),
        ("数据库功能", test_database),
        ("AI问答系统", test_ai_qa),
        ("代码练习", test_code_practice),
        ("实践项目", test_practice_projects),
        ("知识图谱", test_knowledge_graph),
        ("代码索引", test_code_index),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 显示测试结果
    print("\n" + "="*60)
    print("测试结果汇总:")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("="*60)
    print(f"总计: {passed} 通过, {failed} 失败")
    print("="*60)
    
    if failed == 0:
        print("\n🎉 所有测试通过！系统状态良好！")
        return 0
    else:
        print(f"\n⚠️  发现 {failed} 个问题，请检查")
        return 1


if __name__ == "__main__":
    sys.exit(main())
