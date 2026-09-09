#!/usr/bin/env python3
"""
Paper-OS 项目状态检查脚本
用于检查系统的完整性和各组件的状态
"""
import os
import sys
from pathlib import Path
from data_manager import DatabaseManager
from utils import ConfigManager


class StatusChecker:
    """项目状态检查器"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.base_dir = Path(self.config.get('paths.base_dir', '.'))
        self.issues = []
        self.warnings = []
    
    def check_database(self):
        """检查数据库"""
        print("\n📊 数据库检查...")
        
        db_file = Path(self.config.get('paths.db_file', 'data/paper_os.db'))
        
        if not db_file.exists():
            self.issues.append("数据库文件不存在")
            return False
        
        try:
            db = DatabaseManager(str(db_file))
            stats = db.get_statistics()
            
            print(f"  ✅ 数据库文件存在")
            print(f"  📚 论文总数: {stats['total_papers']}")
            print(f"  📖 有深度解读: {stats['papers_with_analysis']}")
            print(f"  🔗 总引用数: {stats['total_citations']:,}")
            
            if stats['total_papers'] == 0:
                self.issues.append("数据库中没有论文数据")
                return False
            
            if stats['papers_with_analysis'] == 0:
                self.warnings.append("没有找到论文分析文档")
            
            db.close()
            return True
            
        except Exception as e:
            self.issues.append(f"数据库访问失败: {e}")
            return False
    
    def check_directories(self):
        """检查必要目录"""
        print("\n📁 目录结构检查...")
        
        required_dirs = [
            'data',
            'learning_paths_by_report/extended_papers',
            'code_practice',
            'practice_projects',
            'exports',
            'logs',
            'knowledge_graph'
        ]
        
        all_exist = True
        for dir_path in required_dirs:
            full_path = self.base_dir / dir_path
            if full_path.exists():
                print(f"  ✅ {dir_path}")
            else:
                print(f"  ❌ {dir_path} - 缺失")
                self.issues.append(f"目录缺失: {dir_path}")
                all_exist = False
        
        return all_exist
    
    def check_code_practice(self):
        """检查代码练习"""
        print("\n💻 代码练习检查...")
        
        practice_dir = self.base_dir / 'code_practice'
        if not practice_dir.exists():
            self.issues.append("代码练习目录不存在")
            return False
        
        categories = [d for d in practice_dir.iterdir() if d.is_dir()]
        print(f"  📂 代码练习类别: {len(categories)}个")
        
        total_exercises = 0
        for category in categories:
            exercises = [e for e in category.iterdir() if e.is_dir()]
            total_exercises += len(exercises)
            print(f"    • {category.name}: {len(exercises)}个练习")
        
        print(f"  📝 总练习数: {total_exercises}")
        
        if total_exercises == 0:
            self.warnings.append("没有找到代码练习")
        
        return total_exercises > 0
    
    def check_practice_projects(self):
        """检查实践项目"""
        print("\n🔨 实践项目检查...")
        
        projects_dir = self.base_dir / 'practice_projects'
        if not projects_dir.exists():
            self.issues.append("实践项目目录不存在")
            return False
        
        projects = [d for d in projects_dir.iterdir() if d.is_dir()]
        print(f"  📦 实践项目: {len(projects)}个")
        
        for project in projects:
            has_readme = (project / 'README.md').exists()
            has_guide = (project / 'IMPLEMENTATION_GUIDE.md').exists()
            has_main = (project / 'main.py').exists()
            has_config = (project / 'config.py').exists()
            has_test = (project / 'test.py').exists()
            has_quick_test = (project / 'quick_test.py').exists()
            
            status = "✅" if all([has_readme, has_main, has_config, has_test]) else "⚠️"
            print(f"  {status} {project.name}")
            
            if not has_readme:
                self.warnings.append(f"{project.name}: 缺少README.md")
            if not has_guide:
                self.warnings.append(f"{project.name}: 缺少IMPLEMENTATION_GUIDE.md")
            if not has_quick_test:
                self.warnings.append(f"{project.name}: 缺少quick_test.py")
        
        return len(projects) > 0
    
    def check_knowledge_graph(self):
        """检查知识图谱"""
        print("\n🔮 知识图谱检查...")
        
        kg_dir = self.base_dir / 'knowledge_graph'
        if not kg_dir.exists():
            self.warnings.append("知识图谱目录不存在")
            return False
        
        dot_file = kg_dir / 'knowledge_graph.dot'
        timeline_file = kg_dir / 'timeline.md'
        category_file = kg_dir / 'category_tree.md'
        
        if dot_file.exists():
            print(f"  ✅ knowledge_graph.dot")
        else:
            self.warnings.append("缺少 knowledge_graph.dot")
        
        if timeline_file.exists():
            print(f"  ✅ timeline.md")
        else:
            self.warnings.append("缺少 timeline.md")
        
        if category_file.exists():
            print(f"  ✅ category_tree.md")
        else:
            self.warnings.append("缺少 category_tree.md")
        
        return dot_file.exists()
    
    def check_code_index(self):
        """检查代码索引"""
        print("\n🔍 代码索引检查...")
        
        index_dir = self.base_dir / 'code_index'
        if not index_dir.exists():
            self.warnings.append("代码索引目录不存在")
            return False
        
        json_files = list(index_dir.glob('*.json'))
        
        if json_files:
            print(f"  ✅ 已索引 {len(json_files)} 个项目")
            for json_file in json_files:
                size = json_file.stat().st_size / (1024 * 1024)  # MB
                print(f"    • {json_file.name}: {size:.1f} MB")
            return True
        else:
            self.warnings.append("没有找到代码索引文件")
            return False
    
    def check_paper_analysis(self):
        """检查论文分析文档"""
        print("\n📄 论文分析文档检查...")
        
        papers_dir = self.base_dir / 'learning_paths_by_report' / 'extended_papers'
        if not papers_dir.exists():
            self.issues.append("论文目录不存在")
            return False
        
        analysis_files = list(papers_dir.rglob('*_analysis.md'))
        print(f"  📝 分析文档: {len(analysis_files)}篇")
        
        categories = set(f.parent.name for f in analysis_files)
        print(f"  📂 涵盖类别: {len(categories)}个")
        
        for cat in sorted(categories):
            count = sum(1 for f in analysis_files if f.parent.name == cat)
            print(f"    • {cat}: {count}篇")
        
        return len(analysis_files) > 0
    
    def run_all_checks(self):
        """运行所有检查"""
        print("╔══════════════════════════════════════════════════════════╗")
        print("║     Paper-OS 项目状态检查                              ║")
        print("╚══════════════════════════════════════════════════════════╝")
        
        # 运行各项检查
        self.check_database()
        self.check_directories()
        self.check_paper_analysis()
        self.check_code_practice()
        self.check_practice_projects()
        self.check_knowledge_graph()
        self.check_code_index()
        
        # 显示问题
        if self.issues:
            print("\n❌ 发现的问题:")
            for issue in self.issues:
                print(f"  • {issue}")
        
        if self.warnings:
            print("\n⚠️  警告:")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        # 显示总结
        print("\n" + "="*60)
        if not self.issues:
            print("✅ 系统检查完成，未发现严重问题")
            if self.warnings:
                print(f"⚠️  发现 {len(self.warnings)} 个警告，建议检查")
            else:
                print("🎉 所有组件状态良好！")
            return 0
        else:
            print(f"❌ 发现 {len(self.issues)} 个问题，需要修复")
            print(f"⚠️  发现 {len(self.warnings)} 个警告")
            print("\n💡 建议运行 ./init_system.sh 进行初始化")
            return 1


def main():
    checker = StatusChecker()
    return checker.run_all_checks()


if __name__ == "__main__":
    sys.exit(main())
