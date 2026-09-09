"""
Paper-OS 知识图谱可视化
"""
import json
from pathlib import Path
from data_manager import DatabaseManager
from utils import ConfigManager


class KnowledgeGraphVisualizer:
    def __init__(self, db_manager: DatabaseManager, output_dir: str = "knowledge_graph"):
        self.db = db_manager
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def generate_graphviz(self):
        """生成Graphviz格式的知识图谱"""
        cursor = self.db.conn.cursor()
        
        cursor.execute("""
            SELECT id, title, category, citation_count
            FROM papers
            WHERE category IS NOT NULL
            ORDER BY citation_count DESC
            LIMIT 30
        """)
        
        papers = cursor.fetchall()
        
        dot_content = '''digraph PaperKnowledgeGraph {
    rankdir=LR;
    node [shape=box, style=filled, fontname="Arial"];
    edge [fontname="Arial"];
    
    // 定义类别颜色
    node [fillcolor="#e0e0e0"];
    
'''
        
        category_colors = {
            'Transformer基础': '#FFD700',
            '生成模型': '#90EE90',
            '视觉模型': '#87CEEB',
            '大语言模型': '#DDA0DD',
            'RAG与检索增强': '#F0E68C',
            '推理与思维链': '#FFA07A',
            '优化与压缩': '#20B2AA',
            '多模态': '#FF6B6B',
            'RL与Agent': '#9370DB'
        }
        
        for paper in papers:
            title = paper['title'].replace('"', '\\"')
            category = paper['category']
            citation = paper['citation_count']
            color = category_colors.get(category, '#e0e0e0')
            
            node_id = f"paper_{paper['id']}"
            node_label = f"{title}\\n(引用: {citation:,})"
            
            dot_content += f'    {node_id} [label="{node_label}", fillcolor="{color}"];\n'
        
        dot_content += '\n    // 基于类别的连接\n\n'
        
        for i, paper1 in enumerate(papers[:-1]):
            for paper2 in papers[i+1:]:
                if paper1['category'] == paper2['category']:
                    dot_content += f'    paper_{paper1["id"]} -> paper_{paper2["id"]} [style=dashed, color="#999999"];\n'
        
        dot_content += '\n}\n'
        
        output_file = self.output_dir / "knowledge_graph.dot"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(dot_content)
        
        print(f"✅ 生成Graphviz文件: {output_file}")
        print("   使用命令生成图片: dot -Tpng knowledge_graph.dot -o knowledge_graph.png")

    def generate_timeline(self):
        """生成技术演进时间线"""
        cursor = self.db.conn.cursor()
        
        cursor.execute("""
            SELECT title, year, category, citation_count
            FROM papers
            WHERE year IS NOT NULL AND year > 2010
            ORDER BY year
        """)
        
        papers = cursor.fetchall()
        
        timeline_content = "# 技术演进时间线\n\n"
        
        current_year = None
        for paper in papers:
            if paper['year'] != current_year:
                timeline_content += f"## {paper['year']}\n\n"
                current_year = paper['year']
            
            category_emoji = {
                'Transformer基础': '🤖',
                '生成模型': '🎨',
                '视觉模型': '👁️',
                '大语言模型': '🧠',
                'RAG与检索增强': '📚',
                '推理与思维链': '💭',
                '优化与压缩': '⚡',
                '多模态': '🌐',
                'RL与Agent': '🎮'
            }.get(paper['category'], '📄')
            
            timeline_content += f"{category_emoji} **{paper['title']}**\n"
            timeline_content += f"   - 类别: {paper['category']}\n"
            timeline_content += f"   - 引用: {paper['citation_count']:,}\n\n"
        
        output_file = self.output_dir / "timeline.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(timeline_content)
        
        print(f"✅ 生成时间线文件: {output_file}")

    def generate_category_tree(self):
        """生成类别树状图"""
        cursor = self.db.conn.cursor()
        
        cursor.execute("""
            SELECT category, COUNT(*) as count, SUM(citation_count) as total_citations
            FROM papers
            WHERE category IS NOT NULL
            GROUP BY category
            ORDER BY total_citations DESC
        """)
        
        categories = cursor.fetchall()
        
        tree_content = "# 论文类别树\n\n"
        tree_content += "```mermaid\ngraph TD\n"
        
        for cat in categories:
            tree_content += f'    {cat["category"]}["{cat["category"]}\\n{cat["count"]}篇\\n引用:{cat["total_citations"]:,}"]\n'
        
        tree_content += "```\n\n"
        
        for cat in categories:
            tree_content += f"## {cat['category']}\n\n"
            
            cursor.execute("""
                SELECT title, citation_count, has_analysis
                FROM papers
                WHERE category = ?
                ORDER BY citation_count DESC
            """, (cat['category'],))
            
            papers = cursor.fetchall()
            for paper in papers:
                analysis_mark = ' ✓' if paper['has_analysis'] else ''
                tree_content += f"- {paper['title']} (引用: {paper['citation_count']:,}){analysis_mark}\n"
            
            tree_content += "\n"
        
        output_file = self.output_dir / "category_tree.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(tree_content)
        
        print(f"✅ 生成类别树文件: {output_file}")

    def generate_all(self):
        """生成所有可视化"""
        print("🔮 生成知识图谱可视化...")
        print("=" * 60)
        
        self.generate_graphviz()
        self.generate_timeline()
        self.generate_category_tree()
        
        print("\n" + "=" * 60)
        print("✅ 知识图谱可视化完成!")
        print(f"📁 输出目录: {self.output_dir.absolute()}")


def main():
    config = ConfigManager()
    db_manager = DatabaseManager(config.get('paths.db_file', 'data/paper_os.db'))
    
    visualizer = KnowledgeGraphVisualizer(db_manager)
    visualizer.generate_all()
    
    db_manager.close()


if __name__ == "__main__":
    main()
