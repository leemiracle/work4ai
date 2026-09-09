"""
Paper-OS 数据导入脚本 - 从现有JSON导入到数据库
"""
import json
import os
from pathlib import Path
from data_manager import DatabaseManager
from utils import ConfigManager, PaperParser, FileOrganizer


class DataImporter:
    def __init__(self, db_manager: DatabaseManager, base_dir: str):
        self.db = db_manager
        self.base_dir = Path(base_dir)
        self.parser = PaperParser()
        self.organizer = FileOrganizer(base_dir)

    def import_from_paper_analysis(self, json_path: str = "paper_analysis_report.json"):
        """从原始论文分析报告导入"""
        print(f"开始导入: {json_path}")
        
        if not os.path.exists(json_path):
            print(f"文件不存在: {json_path}")
            return
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        imported_count = 0
        for paper_data in data.get('papers', []):
            paper_id = self._import_single_paper(paper_data)
            if paper_id > 0:
                imported_count += 1
                print(f"  ✓ 导入: {paper_data.get('title', 'Unknown')}")
        
        print(f"完成导入: {imported_count} 篇论文")
        return imported_count

    def import_from_extended_papers(self, extended_dir: str = "learning_paths_by_report/extended_papers"):
        """从扩展论文目录导入"""
        print(f"开始扫描扩展论文目录: {extended_dir}")
        
        extended_path = self.base_dir / extended_dir
        if not extended_path.exists():
            print(f"目录不存在: {extended_dir}")
            return
        
        imported_count = 0
        categories = [d for d in extended_path.iterdir() if d.is_dir()]
        
        for category_dir in categories:
            category = category_dir.name
            print(f"  处理类别: {category}")
            
            analysis_files = list(category_dir.glob("*_analysis.md"))
            for analysis_file in analysis_files:
                paper_data = self._parse_analysis_file(analysis_file, category)
                if paper_data:
                    paper_id = self.db.insert_paper(paper_data)
                    if paper_id > 0:
                        imported_count += 1
                        print(f"    ✓ 导入: {paper_data.get('title', 'Unknown')}")
        
        print(f"完成导入: {imported_count} 篇扩展论文")
        return imported_count

    def _import_single_paper(self, paper_data: dict) -> int:
        """导入单篇论文"""
        import_data = {
            'arxiv_id': paper_data.get('arxiv_id'),
            'filename': paper_data.get('filename'),
            'title': paper_data.get('title'),
            'authors': self.parser.extract_authors(paper_data.get('authors', '')),
            'year': paper_data.get('year'),
            'venue': paper_data.get('venue'),
            'keywords': paper_data.get('keywords', []),
            'citation_count': paper_data.get('citation_count', 0),
            'importance': paper_data.get('importance'),
            'application_areas': paper_data.get('application_areas', []),
            'difficulty_level': paper_data.get('difficulty_level'),
            'size_mb': paper_data.get('size_mb'),
            'category': self._infer_category(paper_data),
            'has_analysis': False
        }
        return self.db.insert_paper(import_data)

    def _parse_analysis_file(self, file_path: Path, category: str) -> dict:
        """解析扩展论文的分析文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            paper_data = {
                'category': category,
                'has_analysis': True
            }
            
            arxiv_match = file_path.stem.split('_')[0]
            if len(arxiv_match) == 10:
                paper_data['arxiv_id'] = arxiv_match
            
            title_match = self._extract_from_markdown(content, ['标题', 'Title', '论文标题'])
            if title_match:
                paper_data['title'] = title_match
            else:
                paper_data['title'] = file_path.stem.replace('_analysis', '')
            
            authors_match = self._extract_from_markdown(content, ['作者', 'Authors'])
            if authors_match:
                paper_data['authors'] = authors_match
            
            year_match = self._extract_from_markdown(content, ['年份', 'Year', '发表时间'])
            if year_match:
                year = ''.join(filter(str.isdigit, year_match))
                if year:
                    paper_data['year'] = int(year[:4])
            
            citation_match = self._extract_from_markdown(content, ['引用', 'Citations', '引用次数'])
            if citation_match:
                citation = ''.join(filter(str.isdigit, citation_match.replace(',', '')))
                if citation:
                    paper_data['citation_count'] = int(citation)
            
            venue_match = self._extract_from_markdown(content, ['会议', 'Venue', '发表地点'])
            if venue_match:
                paper_data['venue'] = venue_match
            
            keywords_match = self._extract_from_markdown(content, ['关键词', 'Keywords'])
            if keywords_match:
                keywords = [k.strip() for k in keywords_match.split(',')]
                paper_data['keywords'] = keywords
            
            return paper_data
            
        except Exception as e:
            print(f"    ✗ 解析失败 {file_path.name}: {e}")
            return None

    def _extract_from_markdown(self, content: str, patterns: list) -> str:
        """从Markdown内容中提取字段"""
        for pattern in patterns:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if pattern in line and ':' in line:
                    value = line.split(':', 1)[1].strip()
                    if value and not value.startswith('-'):
                        return value
        return ''

    def _infer_category(self, paper_data: dict) -> str:
        """根据论文信息推断类别"""
        title = paper_data.get('title', '').lower()
        keywords = ' '.join(paper_data.get('keywords', []))
        text = f"{title} {keywords}".lower()
        
        if 'transformer' in text or 'attention' in text:
            return 'Transformer基础'
        elif 'resnet' in text or 'residual' in text or 'vision' in text:
            return '视觉模型'
        elif 'gan' in text or 'diffusion' in text or 'generative' in text:
            return '生成模型'
        elif 'gpt' in text or 'language model' in text or 'chinchilla' in text:
            return '大语言模型'
        elif 'rag' in text or 'retrieval' in text or 'realm' in text:
            return 'RAG与检索增强'
        elif 'chain-of-thought' in text or 'reasoning' in text:
            return '推理与思维链'
        elif 'lora' in text or 'qlora' in text or 'distillation' in text:
            return '优化与压缩'
        elif 'clip' in text or 'multimodal' in text:
            return '多模态'
        elif 'ppo' in text or 'reinforcement' in text:
            return 'RL与Agent'
        else:
            return '其他'

    def import_learning_paths(self, json_path: str = "final_learning_report.json"):
        """导入学习路径"""
        print(f"开始导入学习路径: {json_path}")
        
        if not os.path.exists(json_path):
            print(f"文件不存在: {json_path}")
            return
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        paths_config = {
            '初学者路径': {'level': 'beginner', 'papers': [
                'Attention Is All You Need',
                'Deep Residual Learning for Image Recognition'
            ]},
            '中级路径': {'level': 'intermediate', 'papers': [
                'Improving Language Understanding by Generative Pre-Training',
                'Denoising Diffusion Probabilistic Models',
                'ZeRO: Memory Optimizations Toward Large Batch Size Training'
            ]},
            '高级路径': {'level': 'advanced', 'papers': [
                'Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks',
                'Chain-of-Thought Prompting Elicits Reasoning in Large Language Models',
                'Distilling the Knowledge in a Neural Network'
            ]}
        }
        
        for path_name, path_config in paths_config.items():
            path_id = self._import_single_path(path_name, path_config)
            print(f"  ✓ 导入路径: {path_name}")
        
        print("完成学习路径导入")

    def _import_single_path(self, name: str, config: dict) -> int:
        cursor = self.db.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO learning_paths (name, level, duration_weeks, description, order_index)
            VALUES (?, ?, ?, ?, ?)
        """, (
            name,
            config['level'],
            {'beginner': 6, 'intermediate': 12, 'advanced': 16}.get(config['level'], 8),
            f"{name}学习路径",
            ['beginner', 'intermediate', 'advanced'].index(config['level']) + 1
        ))
        self.db.conn.commit()
        return cursor.lastrowid

    def run_full_import(self):
        """运行完整导入流程"""
        print("=" * 60)
        print("Paper-OS 数据导入开始")
        print("=" * 60)
        
        import os
        os.makedirs("data", exist_ok=True)
        
        if os.path.exists("paper_analysis_report.json"):
            self.import_from_paper_analysis()
        if os.path.exists("learning_paths_by_report/extended_papers"):
            self.import_from_extended_papers()
        if os.path.exists("final_learning_report.json"):
            self.import_learning_paths()
        
        stats = self.db.get_statistics()
        print("\n" + "=" * 60)
        print("导入完成 - 数据库统计")
        print("=" * 60)
        print(f"论文总数: {stats['total_papers']}")
        print(f"有深度解读: {stats['papers_with_analysis']}")
        print(f"总引用数: {stats['total_citations']:,}")
        print("=" * 60)


def main():
    config = ConfigManager()
    db_manager = DatabaseManager(config.get('paths.db_file', 'data/paper_os.db'))
    
    importer = DataImporter(db_manager, config.get('paths.base_dir', '.'))
    importer.run_full_import()
    
    db_manager.close()


if __name__ == "__main__":
    main()
