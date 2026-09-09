"""tinyrag — 参照 LangChain/LlamaIndex 的 RAG 系统"""
from .embedding import HashEmbedding, TFIDFEmbedding, cosine_similarity, tokenize
from .vectorstore import VectorStore, BruteForceIndex, HNSWIndex, Document
from .pipeline import RAGPipeline, chunk_text
from .loader import Document, text_loader, markdown_loader, code_loader, auto_loader, directory_loader, load_csdiy_knowledge, split_documents

__version__ = "1.0.0"
__all__ = [
    "HashEmbedding", "TFIDFEmbedding", "cosine_similarity", "tokenize",
    "VectorStore", "BruteForceIndex", "HNSWIndex", "Document",
    "RAGPipeline", "chunk_text",
    "text_loader", "markdown_loader", "code_loader", "auto_loader",
    "directory_loader", "load_csdiy_knowledge", "split_documents",
]
