"""
Paper-OS 智能问答助手 (RAG)
"""
import json
from pathlib import Path
from data_manager import DatabaseManager
from utils import ConfigManager
from typing import List, Dict, Any
import re


class SimpleQA:
    """简单的基于关键词匹配的问答系统"""
    
    def __init__(self, db_manager: DatabaseManager, base_dir: str):
        self.db = db_manager
        self.base_dir = Path(base_dir)
        self.extended_papers_dir = self.base_dir / "learning_paths_by_report" / "extended_papers"
        self.documents = []
        self.load_documents()

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
                    'category': str(analysis_file.parent.name)
                })
            except Exception as e:
                print(f"  ⚠️ 加载失败: {analysis_file.name}")
        
        print(f"✅ 加载完成: {len(self.documents)} 篇文档")

    def _extract_title(self, content: str) -> str:
        """从Markdown内容中提取标题"""
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        return match.group(1) if match else "Unknown"

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """基于关键词搜索相关文档"""
        query_lower = query.lower()
        scores = []
        
        keywords = query_lower.split()
        
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
        print(f"\n❓ 问题: {query}")
        print("-" * 60)
        
        results = self.search(query, top_k=3)
        
        if not results:
            return {
                'answer': "很抱歉，我没有找到相关的信息。请尝试用不同的方式提问。",
                'sources': [],
                'confidence': 0
            }
        
        answer_parts = []
        sources = []
        
        for i, result in enumerate(results[:2], 1):
            doc = result['doc']
            excerpts = result['excerpts']
            
            answer_parts.append(f"根据《{doc['title']}》：")
            
            if excerpts:
                for excerpt in excerpts[:2]:
                    answer_parts.append(f"  • {excerpt}")
            
            sources.append({
                'title': doc['title'],
                'category': doc['category'],
                'path': doc['path']
            })
        
        answer = '\n'.join(answer_parts)
        
        print("💡 回答:")
        print(answer)
        
        print(f"\n📚 来源:")
        for source in sources:
            print(f"  • {source['title']} ({source['category']})")
        
        return {
            'answer': answer,
            'sources': sources,
            'confidence': len(results) / 3
        }

    def interactive_mode(self):
        """交互式问答模式"""
        print("\n" + "=" * 60)
        print("🤖 Paper-OS 智能问答助手")
        print("=" * 60)
        print("\n基于论文分析文档的智能问答系统")
        print("输入 'quit' 或 'exit' 退出\n")
        
        while True:
            query = input("❓ 请输入问题: ").strip()
            
            if query.lower() in ['quit', 'exit', '退出']:
                print("\n👋 感谢使用!")
                break
            
            if not query:
                continue
            
            try:
                self.answer(query)
            except Exception as e:
                print(f"⚠️ 回答失败: {e}")
            
            print("\n" + "-" * 60)


def main():
    config = ConfigManager()
    db_manager = DatabaseManager(config.get('paths.db_file', 'data/paper_os.db'))
    
    qa_system = SimpleQA(db_manager, config.get('paths.base_dir', '.'))
    
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
        qa_system.answer(query)
    else:
        qa_system.interactive_mode()
    
    db_manager.close()


if __name__ == "__main__":
    import sys
    main()
