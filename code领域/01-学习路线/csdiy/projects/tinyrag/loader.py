#!/usr/bin/env python3
"""
tinyrag/loader.py — 真实文档加载器

参照：LangChain DocumentLoader / LlamaIndex Reader
csdiy 对应：tinyrag/pipeline.py + data-pipeline精读

支持的文档类型：
  TextLoader    — 纯文本 .txt
  MarkdownLoader — Markdown .md（去掉标记）
  CodeLoader    — 源代码 .py/.js/.go（按函数分块）
  URLLoader     — 从 URL 加载（简化版）
  DirectoryLoader — 批量加载目录
"""
import re, os
from pathlib import Path
from dataclasses import dataclass, field

@dataclass
class Document:
    """文档（参照 LangChain Document）"""
    content: str
    metadata: dict = field(default_factory=dict)
    source: str = ""

def text_loader(path: str) -> list[Document]:
    """加载纯文本"""
    content = Path(path).read_text(encoding="utf-8", errors="replace")
    return [Document(content=content, source=path, metadata={"type": "text"})]

def markdown_loader(path: str) -> list[Document]:
    """加载 Markdown（按标题分块）"""
    content = Path(path).read_text(encoding="utf-8", errors="replace")
    # 按 ## 标题分块
    sections = re.split(r'\n(?=#{1,3} )', content)
    docs = []
    for i, section in enumerate(sections):
        title = section.split('\n')[0].strip('# ').strip()[:50]
        docs.append(Document(
            content=section.strip(),
            source=path,
            metadata={"type": "markdown", "section": i, "title": title}
        ))
    return docs

def code_loader(path: str) -> list[Document]:
    """加载源代码（按函数/类分块）"""
    content = Path(path).read_text(encoding="utf-8", errors="replace")
    # 按函数定义分块
    chunks = re.split(r'(?=\ndef |class )', content)
    docs = []
    for chunk in chunks:
        if len(chunk.strip()) < 10:
            continue
        # 提取函数名
        match = re.match(r'(def |class )(\w+)', chunk)
        name = match.group(2) if match else "unnamed"
        docs.append(Document(
            content=chunk.strip(),
            source=path,
            metadata={"type": "code", "function": name, "language": Path(path).suffix}
        ))
    return docs

def auto_loader(path: str) -> list[Document]:
    """自动选择加载器"""
    ext = Path(path).suffix.lower()
    if ext == ".md":
        return markdown_loader(path)
    elif ext in (".py", ".js", ".go", ".rs", ".c", ".cpp", ".java"):
        return code_loader(path)
    else:
        return text_loader(path)

def directory_loader(dir_path: str, extensions=None) -> list[Document]:
    """批量加载目录（参照 LangChain DirectoryLoader）"""
    if extensions is None:
        extensions = [".md", ".py", ".txt", ".js", ".go"]
    docs = []
    for f in sorted(Path(dir_path).rglob("*")):
        if f.is_file() and f.suffix.lower() in extensions:
            try:
                docs.extend(auto_loader(str(f)))
            except:
                pass
    return docs

def load_csdiy_knowledge(root_path: str = ".") -> list[Document]:
    """加载 csdiy 全部知识（精读+笔记+速查+精读）"""
    docs = []
    for subdir in ["notes", "source-reading", "cheatsheets", "labs"]:
        path = Path(root_path) / subdir
        if path.exists():
            docs.extend(directory_loader(str(path), [".md"]))
    return docs

def split_documents(docs: list[Document], chunk_size=200, overlap=50) -> list[Document]:
    """切分长文档（参照 LangChain RecursiveCharacterTextSplitter）"""
    result = []
    for doc in docs:
        content = doc.content
        if len(content) <= chunk_size:
            result.append(doc)
            continue
        for i in range(0, len(content), chunk_size - overlap):
            chunk = content[i:i + chunk_size]
            if len(chunk) > 20:
                result.append(Document(
                    content=chunk,
                    source=doc.source,
                    metadata={**doc.metadata, "chunk_start": i, "chunk_size": len(chunk)}
                ))
    return result

def demo():
    print("=" * 60)
    print("  tinyrag/loader.py — 文档加载器")
    print("=" * 60)

    # 加载 csdiy 知识
    root = Path(__file__).resolve().parent.parent.parent
    docs = load_csdiy_knowledge(str(root))
    print(f"\n  加载 csdiy 知识库:")
    types = {}
    for d in docs:
        types[d.metadata.get("type", "?")] = types.get(d.metadata.get("type", "?"), 0) + 1
    print(f"    总文档数: {len(docs)}")
    print(f"    类型分布: {types}")
    print(f"    总字符数: {sum(len(d.content) for d in docs):,}")

    # 切分
    chunks = split_documents(docs, chunk_size=300, overlap=50)
    print(f"\n  切分后: {len(chunks)} 个 chunk")
    print(f"    平均长度: {sum(len(c.content) for c in chunks) // len(chunks)} 字符")

    # 展示几个 chunk
    print(f"\n  示例 chunk:")
    for i in [0, len(chunks)//2, -1]:
        c = chunks[i]
        print(f"    [{i}] ({c.metadata.get('type','?')}) {c.content[:80]}...")

    print(f"\n  支持格式: .md(按标题分) .py(按函数分) .txt(按长度分)")
    print(f"{'='*60}")

if __name__ == "__main__":
    demo()
