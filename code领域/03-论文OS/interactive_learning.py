"""
Paper-OS 交互式学习系统 - CLI
"""
import sys
from data_manager import DatabaseManager
from utils import ConfigManager, ProgressCalculator, DataExporter, QuizGenerator
from datetime import datetime


class LearningSystemCLI:
    def __init__(self):
        self.config = ConfigManager()
        self.db = DatabaseManager(self.config.get('paths.db_file', 'data/paper_os.db'))
        self.running = True

    def show_main_menu(self):
        print("\n" + "=" * 60)
        print(" 📚 Paper-OS 交互式学习系统")
        print("=" * 60)
        
        stats = self.db.get_statistics()
        print(f"\n 📊 统计信息:")
        print(f"   论文总数: {stats['total_papers']}")
        print(f"   有深度解读: {stats['papers_with_analysis']}")
        print(f"   总引用数: {stats['total_citations']:,}")
        print(f"   完成进度: {stats['avg_progress']}%")
        
        print("\n 📋 主菜单:")
        print("   1. 查看论文列表")
        print("   2. 按类别浏览")
        print("   3. 按学习路径浏览")
        print("   4. 查看学习进度")
        print("   5. 更新学习进度")
        print("   6. 查看笔记")
        print("   7. 导出学习报告")
        print("   8. 做测验")
        print("   9. 系统设置")
        print("   0. 退出")
        print("=" * 60)

    def run(self):
        while self.running:
            self.show_main_menu()
            choice = input("\n 请选择操作 (0-9): ").strip()
            
            actions = {
                '1': self.view_papers,
                '2': self.view_by_category,
                '3': self.view_by_learning_path,
                '4': self.view_progress,
                '5': self.update_progress,
                '6': self.view_notes,
                '7': self.export_report,
                '8': self.take_quiz,
                '9': self.settings,
                '0': self.exit
            }
            
            action = actions.get(choice)
            if action:
                action()
            else:
                print("\n ⚠️  无效选择，请重试")

    def view_papers(self):
        print("\n" + "-" * 60)
        print(" 📖 论文列表")
        print("-" * 60)
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT id, title, authors, year, citation_count, difficulty_level
            FROM papers
            ORDER BY citation_count DESC
            LIMIT 20
        """)
        
        papers = cursor.fetchall()
        if papers:
            for paper in papers:
                print(f"\n [{paper[0]}] {paper[1]}")
                print(f"     作者: {paper[2]} | 年份: {paper[3]} | 引用: {paper[4]:,} | 难度: {paper[5]}")
        else:
            print("\n 暂无论文")
        
        print("\n" + "-" * 60)
        paper_id = input(" 输入论文ID查看详情 (回车返回): ").strip()
        if paper_id.isdigit():
            self.view_paper_detail(int(paper_id))

    def view_paper_detail(self, paper_id: int):
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT * FROM papers WHERE id = ?", (paper_id,))
        paper = cursor.fetchone()
        
        if paper:
            print("\n" + "=" * 60)
            print(f" 📄 论文详情: {paper['title']}")
            print("=" * 60)
            print(f"\n 作者: {paper['authors']}")
            print(f" 年份: {paper['year']}")
            print(f" 会议: {paper['venue']}")
            print(f" 引用数: {paper['citation_count']:,}")
            print(f" 重要性: {paper['importance']}")
            print(f" 难度: {paper['difficulty_level']}")
            print(f" 类别: {paper['category']}")
            
            import json
            keywords = json.loads(paper['keywords']) if paper['keywords'] else []
            if keywords:
                print(f" 关键词: {', '.join(keywords)}")
            
            app_areas = json.loads(paper['application_areas']) if paper['application_areas'] else []
            if app_areas:
                print(f" 应用领域: {', '.join(app_areas)}")
            
            print("\n" + "=" * 60)
        else:
            print("\n ⚠️  论文不存在")

    def view_by_category(self):
        print("\n" + "-" * 60)
        print(" 📂 按类别浏览")
        print("-" * 60)
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM papers
            GROUP BY category
            ORDER BY count DESC
        """)
        
        categories = cursor.fetchall()
        for i, cat in enumerate(categories, 1):
            print(f" {i}. {cat[0]} ({cat[1]} 篇)")
        
        print("\n" + "-" * 60)
        choice = input(" 选择类别编号 (回车返回): ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(categories):
            self.view_papers_in_category(categories[int(choice)-1][0])

    def view_papers_in_category(self, category: str):
        print(f"\n{category} 类论文:")
        print("-" * 60)
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT id, title, citation_count
            FROM papers
            WHERE category = ?
            ORDER BY citation_count DESC
        """, (category,))
        
        papers = cursor.fetchall()
        for paper in papers:
            print(f" [{paper[0]}] {paper[1]} (引用: {paper[2]:,})")

    def view_by_learning_path(self):
        print("\n" + "-" * 60)
        print(" 🎯 学习路径")
        print("-" * 60)
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT id, name, level, duration_weeks
            FROM learning_paths
            ORDER BY order_index
        """)
        
        paths = cursor.fetchall()
        for i, path in enumerate(paths, 1):
            level_emoji = {'beginner': '🌱', 'intermediate': '🌿', 'advanced': '🌳'}
            print(f" {i}. {level_emoji.get(path[2], '')} {path[1]} ({path[3]}周)")
        
        print("\n" + "-" * 60)
        choice = input(" 选择路径编号 (回车返回): ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(paths):
            self.view_path_details(paths[int(choice)-1][0])

    def view_path_details(self, path_id: int):
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT * FROM learning_paths WHERE id = ?", (path_id,))
        path = cursor.fetchone()
        
        if path:
            print(f"\n{'='*60}")
            print(f" 🎓 {path['name']}")
            print(f"{'='*60}")
            print(f" 级别: {path['level']}")
            print(f" 时长: {path['duration_weeks']}周")
            print(f" 描述: {path['description']}")
            
            print(f"\n 推荐论文:")
            cursor.execute("""
                SELECT p.id, p.title, p.citation_count, p.difficulty_level
                FROM papers p
                ORDER BY p.citation_count DESC
                LIMIT 5
            """)
            
            papers = cursor.fetchall()
            for paper in papers:
                print(f"   [{paper[0]}] {paper[1]} (引用: {paper[2]:,})")

    def view_progress(self):
        print("\n" + "-" * 60)
        print(" 📈 学习进度")
        print("-" * 60)
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT p.title, up.status, up.reading_progress, up.rating, up.started_at, up.completed_at
            FROM user_progress up
            JOIN papers p ON up.paper_id = p.id
            WHERE up.user_id = 1
            ORDER BY up.status DESC, up.reading_progress DESC
        """)
        
        progress = cursor.fetchall()
        if progress:
            for p in progress:
                status_emoji = {'completed': '✅', 'in_progress': '🔄', 'not_started': '⏸️'}
                status = status_emoji.get(p['status'], '⏸️')
                rating = '⭐' * p['rating'] if p['rating'] else ''
                print(f"\n {status} {p['title']}")
                print(f"     进度: {p['reading_progress']}% | 评分: {rating}")
        else:
            print("\n 暂无学习记录")
        
        print("\n" + "-" * 60)
        
        stats = self.db.get_statistics()
        print(f"\n 总体统计:")
        print(f"   已完成: {stats['completed_papers']} 篇")
        print(f"   平均进度: {stats['avg_progress']}%")

    def update_progress(self):
        print("\n" + "-" * 60)
        print(" ✏️  更新学习进度")
        print("-" * 60)
        
        paper_id = input(" 输入论文ID: ").strip()
        if not paper_id.isdigit():
            print(" ⚠️  无效的论文ID")
            return
        
        paper_id = int(paper_id)
        
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT title FROM papers WHERE id = ?", (paper_id,))
        paper = cursor.fetchone()
        
        if not paper:
            print(" ⚠️  论文不存在")
            return
        
        print(f"\n 论文: {paper['title']}")
        
        print("\n 状态:")
        print(" 1. 未开始")
        print(" 2. 进行中")
        print(" 3. 已完成")
        status_choice = input(" 选择状态 (1-3): ").strip()
        
        status_map = {'1': 'not_started', '2': 'in_progress', '3': 'completed'}
        status = status_map.get(status_choice, 'not_started')
        
        progress = input(" 阅读进度 (0-100): ").strip()
        reading_progress = int(progress) if progress.isdigit() else 0
        
        rating = input(" 评分 (1-5, 回车跳过): ").strip()
        rating = int(rating) if rating.isdigit() else None
        
        notes = input(" 笔记 (回车跳过): ").strip()
        
        success = self.db.update_user_progress(paper_id, {
            'status': status,
            'reading_progress': reading_progress,
            'rating': rating,
            'notes': notes
        })
        
        if success:
            print("\n ✅ 进度更新成功!")
        else:
            print("\n ⚠️  更新失败")

    def view_notes(self):
        print("\n" + "-" * 60)
        print(" 📝 学习笔记")
        print("-" * 60)
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT p.title, up.notes, up.updated_at
            FROM user_progress up
            JOIN papers p ON up.paper_id = p.id
            WHERE up.user_id = 1 AND up.notes IS NOT NULL AND up.notes != ''
            ORDER BY up.updated_at DESC
        """)
        
        notes = cursor.fetchall()
        if notes:
            for note in notes:
                print(f"\n 📄 {note['title']}")
                print(f" 时间: {note['updated_at']}")
                print(f" 笔记: {note['notes']}")
                print("-" * 60)
        else:
            print("\n 暂无笔记")

    def export_report(self):
        print("\n" + "-" * 60)
        print(" 📤 导出学习报告")
        print("-" * 60)
        
        print("\n 格式:")
        print(" 1. JSON")
        print(" 2. Markdown")
        print(" 3. 进度报告")
        
        choice = input(" 选择格式 (1-3): ").strip()
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT p.*, up.status, up.reading_progress, up.notes, up.rating
            FROM user_progress up
            JOIN papers p ON up.paper_id = p.id
            WHERE up.user_id = 1
        """)
        
        progress = [dict(row) for row in cursor.fetchall()]
        
        if choice == '1':
            DataExporter.export_to_json(progress, "exports/learning_progress.json")
            print("\n ✅ 导出到: exports/learning_progress.json")
        elif choice == '2':
            DataExporter.export_to_markdown({'papers': progress}, "exports/learning_report.md")
            print("\n ✅ 导出到: exports/learning_report.md")
        elif choice == '3':
            DataExporter.export_progress_report(progress, "exports/progress_report.md")
            print("\n ✅ 导出到: exports/progress_report.md")

    def take_quiz(self):
        print("\n" + "-" * 60)
        print(" 🧠 测验")
        print("-" * 60)
        
        paper_id = input(" 输入论文ID进行测验 (回车随机): ").strip()
        
        if paper_id.isdigit():
            self._take_paper_quiz(int(paper_id))
        else:
            self._take_random_quiz()

    def _take_paper_quiz(self, paper_id: int):
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT * FROM papers WHERE id = ?", (paper_id,))
        paper = cursor.fetchone()
        
        if not paper:
            print(" ⚠️  论文不存在")
            return
        
        print(f"\n 论文: {paper['title']}")
        print("-" * 60)
        
        quizzes = QuizGenerator.generate_basic_quizzes(dict(paper))
        
        correct = 0
        for i, quiz in enumerate(quizzes, 1):
            print(f"\n Q{i}: {quiz['question']}")
            for j, opt in enumerate(quiz['options']):
                print(f"   {j+1}. {opt}")
            
            answer = input(" 你的答案 (1-4): ").strip()
            if answer.isdigit() and int(answer)-1 == quiz['correct_answer']:
                print(" ✅ 正确!")
                correct += 1
                print(f"   {quiz['explanation']}")
            else:
                print(" ❌ 错误")
                print(f"   正确答案: {quiz['options'][quiz['correct_answer']]}")
                print(f"   {quiz['explanation']}")
        
        print(f"\n 得分: {correct}/{len(quizzes)}")

    def _take_random_quiz(self):
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT * FROM papers ORDER BY RANDOM() LIMIT 1")
        paper = cursor.fetchone()
        if paper:
            self._take_paper_quiz(paper['id'])

    def settings(self):
        print("\n" + "-" * 60)
        print(" ⚙️  系统设置")
        print("-" * 60)
        print("\n 功能开发中...")

    def exit(self):
        print("\n 👋 感谢使用 Paper-OS!")
        self.running = False


def main():
    print("\n" + "=" * 60)
    print(" 🚀 Paper-OS 交互式学习系统启动中...")
    print("=" * 60)
    
    cli = LearningSystemCLI()
    cli.run()
    
    cli.db.close()


if __name__ == "__main__":
    main()
