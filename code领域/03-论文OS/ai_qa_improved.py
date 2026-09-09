"""
Paper-OS 改进的AI问答系统
添加更好的输出格式和功能
"""
import json
from pathlib import Path
from data_manager import DatabaseManager
from utils import ConfigManager
from typing import List, Dict, Any
import re


class ImprovedSimpleQA:
    """改进的基于关键词匹配的问答系统"""
    
    def __init__(self, db_manager: DatabaseManager, base_dir: str):
        self.db = db_manager
        self.base_dir = Path(base_dir)
        self.extended_papers_dir = self.base_dir / "learning_paths_by_report" / "extended_papers"
        self.documents = []
        self.load_documents()
        
        # 中英文关键词映射
        self.keyword_mapping = {
            '自注意力': 'self-attention',
            '注意力': 'attention',
            '生成模型': 'generative model',
            '扩散模型': 'diffusion',
            '大语言模型': 'llm',
            '预训练': 'pre-training',
            '微调': 'fine-tuning',
            '检索增强': 'rag',
            '思维链': 'chain-of-thought',
            '优化': 'optimization',
            '压缩': 'compression',
            '多模态': 'multimodal'
        }

    def load_documents(self):
        """加载所有论文分析文档"""
        print("📖 加载论文分析文档...")
        
        for analysis_file in self.extended_papers_dir.rglob("*_analysis.md"):
            try:
                with open(analysis_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.documents.append({
                    'path': str(analysis_file),
                    'content': content,
                    'title': self._extract_title(content),
                    'category': str(analysis_file.parent.name),
                    'arxiv_id': self._extract_arxiv_id(analysis_file.name)
                })
            except Exception as e:
                print(f"  ⚠️ 加载失败: {analysis_file.name}")
        
        print(f"✅ 加载完成: {len(self.documents)} 篇文档")

    def _extract_title(self, content: str) -> str:
        """从Markdown内容中提取标题"""
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        return match.group(1) if match else "Unknown"

    def _extract_arxiv_id(self, filename: str) -> str:
        """从文件名中提取arXiv ID"""
        match = re.search(r'(\d+\.\d+)', filename)
        return match.group(1) if match else ""

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """基于关键词搜索相关文档"""
        query_lower = query.lower()
        scores = []
        
        # 分词并映射中文关键词到英文
        keywords = []
        
        # 先按空格分词
        space_keywords = query_lower.split()
        for keyword in space_keywords:
            keywords.append(keyword)
        
        # 再检查是否包含中文关键词映射
        for cn_keyword, en_keyword in self.keyword_mapping.items():
            if cn_keyword in query_lower:
                keywords.append(en_keyword)
                keywords.append(cn_keyword)
        
        # 添加原始查询作为关键词
        if query_lower not in keywords:
            keywords.append(query_lower)
        
        for doc in self.documents:
            content_lower = doc['content'].lower()
            
            score = 0
            for keyword in keywords:
                if keyword in content_lower:
                    score += content_lower.count(keyword) * len(keyword)
            
            if score > 0:
                scores.append({
                    'doc': doc,
                    'score': score,
                    'excerpts': self._extract_excerpts(doc['content'], keywords)
                })
        
        scores.sort(key=lambda x: x['score'], reverse=True)
        return scores[:top_k]

    def _extract_excerpts(self, content: str, keywords: List[str], max_length: int = 500) -> List[str]:
        """提取包含关键词的文本片段"""
        sentences = re.split(r'[。！？\n]', content)
        excerpts = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:
                continue
            
            sentence_lower = sentence.lower()
            for keyword in keywords:
                if keyword in sentence_lower:
                    excerpts.append(sentence)
                    break
            
            if len(excerpts) >= 3:
                break
        
        return excerpts

    def answer(self, query: str) -> Dict[str, Any]:
        """回答问题"""
        print(f"\n{'='*70}")
        print(f"❓ 问题: {query}")
        print('='*70)
        
        results = self.search(query, top_k=3)
        
        if not results:
            print("\n💡 回答:")
            print("  很抱歉，我没有找到相关的信息。")
            print("  建议:")
            print("    • 尝试用不同的关键词提问")
            print("    • 使用更简短的问题")
            print("    • 查看论文列表了解可用的内容")
            return {
                'answer': "未找到相关信息",
                'sources': [],
                'confidence': 0
            }
        
        answer_parts = []
        sources = []
        
        for i, result in enumerate(results[:2], 1):
            doc = result['doc']
            excerpts = result['excerpts']
            
            answer_parts.append(f"\n【来源 {i}】{doc['title']} ({doc['category']})")
            
            if excerpts:
                for excerpt in excerpts[:3]:
                    answer_parts.append(f"  • {excerpt[:100]}...")
            
            sources.append({
                'title': doc['title'],
                'category': doc['category'],
                'arxiv_id': doc['arxiv_id'],
                'path': doc['path'],
                'score': result['score']
            })
        
        answer = '\n'.join(answer_parts)
        
        print("\n💡 回答:")
        print(answer)
        
        print(f"\n📚 详细来源:")
        for i, source in enumerate(sources, 1):
            print(f"  {i}. {source['title']}")
            print(f"     类别: {source['category']} | arXiv: {source['arxiv_id']}")
        
        confidence = min(len(results) / 3, 1.0)
        confidence_stars = '⭐' * int(confidence * 5)
        print(f"\n🎯 匹配度: {confidence:.2%} {confidence_stars}")
        
        return {
            'answer': answer,
            'sources': sources,
            'confidence': confidence
        }

    def interactive_mode(self):
        """交互式问答模式"""
        print("\n" + "="*70)
        print("🤖 Paper-OS 智能问答助手 (改进版)")
        print("="*70)
        print("\n基于论文分析文档的智能问答系统")
        print(f"📚 已加载 {len(self.documents)} 篇论文分析")
        print("\n💡 提示:")
        print("  • 输入问题，我会从论文中寻找答案")
        print("  • 尝试问关于: Transformer, GPT, Diffusion, LoRA 等")
        print("  • 输入 'quit' 或 'exit' 退出")
        print("  • 输入 'papers' 查看所有可用论文")
        print("  • 输入 'help' 查看帮助\n")
        
        while True:
            try:
                query = input("❓ 请输入问题: ").strip()
                
                if query.lower() in ['quit', 'exit', '退出']:
                    print("\n👋 感谢使用 Paper-OS 问答系统!")
                    break
                
                if query.lower() == 'papers':
                    self.show_papers()
                    continue
                
                if query.lower() == 'help':
                    self.show_help()
                    continue
                
                if not query:
                    continue
                
                self.answer(query)
                
            except KeyboardInterrupt:
                print("\n\n👋 感谢使用 Paper-OS 问答系统!")
                break
            except Exception as e:
                print(f"\n⚠️ 发生错误: {e}")
                print("请重试或输入 'help' 查看帮助\n")
    
    def show_papers(self):
        """显示所有可用论文"""
        print("\n📚 可用论文列表:")
        print("-"*70)
        
        categories = {}
        for doc in self.documents:
            if doc['category'] not in categories:
                categories[doc['category']] = []
            categories[doc['category']].append(doc['title'])
        
        for category, papers in sorted(categories.items()):
            print(f"\n【{category}】")
            for i, paper in enumerate(papers, 1):
                print(f"  {i}. {paper}")
        
        print("-"*70)
    
    def show_help(self):
        """显示帮助信息"""
        print("\n💡 帮助信息:")
        print("-"*70)
        print("\n📝 常用命令:")
        print("  • papers    - 查看所有可用论文")
        print("  • help      - 显示此帮助信息")
        print("  • quit/exit - 退出系统")
        
        print("\n💡 提问示例:")
        print("  • 什么是自注意力机制?")
        print("  • BERT是如何工作的?")
        print("  • 解释一下扩散模型")
        print("  • LoRA的原理是什么?")
        print("  • 什么是RAG?")
        print("-"*70)


def main():
    config = ConfigManager()
    db_manager = DatabaseManager(config.get('paths.db_file', 'data/paper_os.db'))
    
    qa_system = ImprovedSimpleQA(db_manager, config.get('paths.base_dir', '.'))
    
    # 支持命令行参数
    import sys
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
        if query.lower() == 'papers':
            qa_system.show_papers()
        elif query.lower() == 'help':
            qa_system.show_help()
        else:
            qa_system.answer(query)
    else:
        qa_system.interactive_mode()
    
    db_manager.close()


if __name__ == "__main__":
    main()
