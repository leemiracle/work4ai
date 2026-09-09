"""
基础RAG系统实现

学习任务:
1. 实现文档嵌入
2. 实现向量检索
3. 实现答案生成
"""

import numpy as np
from typing import List, Dict

# TODO 1: 实现文档嵌入
# 提示: 可以使用预训练模型如sentence-transformers
class DocumentEmbedder:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model_name = model_name
        # TODO: 加载嵌入模型
        self.model = None
    
    def embed(self, texts: List[str]) -> np.ndarray:
        """
        将文本转换为嵌入向量
        
        Args:
            texts: 文本列表
        
        Returns:
            嵌入向量数组 [num_texts, embedding_dim]
        """
        # TODO: 实现嵌入逻辑
        pass

# TODO 2: 实现向量检索器
class VectorRetriever:
    def __init__(self, embedder: DocumentEmbedder):
        self.embedder = embedder
        self.documents = []
        self.embeddings = None
    
    def add_documents(self, documents: List[str]):
        """
        添加文档到索引
        
        Args:
            documents: 文档列表
        """
        self.documents = documents
        self.embeddings = self.embedder.embed(documents)
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        检索最相关的文档
        
        Args:
            query: 查询文本
            top_k: 返回前k个结果
        
        Returns:
            检索结果列表，包含文档和相似度分数
        """
        # TODO: 实现检索逻辑
        # 提示: 使用余弦相似度或其他距离度量
        pass

# TODO 3: 实现RAG生成器
class RAGGenerator:
    def __init__(self, retriever: VectorRetriever):
        self.retriever = retriever
        # TODO: 加载生成模型
        self.generator = None
    
    def generate(self, query: str, max_length: int = 100) -> str:
        """
        基于检索内容生成答案
        
        Args:
            query: 用户查询
            max_length: 生成答案的最大长度
        
        Returns:
            生成的答案
        """
        # TODO: 实现生成逻辑
        # 1. 检索相关文档
        # 2. 构建提示词
        # 3. 生成答案
        pass

# 测试代码
if __name__ == '__main__':
    # 测试文档嵌入
    embedder = DocumentEmbedder()
    texts = ['This is a test document.', 'Another example document.']
    embeddings = embedder.embed(texts)
    print(f'✅ 嵌入测试通过: {embeddings.shape}')
    
    # 测试检索
    retriever = VectorRetriever(embedder)
    retriever.add_documents(texts)
    results = retriever.retrieve('test document')
    print(f'✅ 检索测试通过: 找到 {len(results)} 个结果')
