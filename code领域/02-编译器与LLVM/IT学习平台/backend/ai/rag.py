"""RAG Service - Retrieval Augmented Generation."""

from typing import List, Dict, Any, Optional
from .llm import LLMService
from .vector_store import VectorStoreService
from .config import AISettings


class RAGService:
    """Service for RAG operations."""

    def __init__(
        self,
        llm_service: Optional[LLMService] = None,
        vector_store: Optional[VectorStoreService] = None,
        settings: Optional[AISettings] = None
    ):
        self.settings = settings or AISettings()
        self.llm_service = llm_service or LLMService(settings)
        self.vector_store = vector_store or VectorStoreService(settings)

        # Prompt templates
        self.rag_prompt_template = """你是一个专业的IT知识助手。请基于以下检索到的相关内容，回答用户的问题。

相关内容:
{context}

用户问题: {question}

请提供:
1. 清晰、准确的回答
2. 相关的代码示例（如果适用）
3. 进一步学习建议
4. 引用来源（如适用）

回答:"""

    async def query(
        self,
        question: str,
        collection_name: str = "notes",
        n_results: Optional[int] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Query with RAG."""

        # Retrieve relevant documents
        search_results = await self.vector_store.search(
            collection_name=collection_name,
            query=question,
            n_results=n_results,
            filter_metadata=filter_metadata
        )

        # Filter by similarity threshold
        relevant_docs = []
        for result in search_results:
            # Convert distance to similarity score (cosine distance: 0 = identical)
            similarity = 1 - result["distance"]
            if similarity >= self.settings.MIN_SIMILARITY:
                relevant_docs.append(result)

        if not relevant_docs:
            return {
                "answer": "抱歉，我没有找到相关的信息。请尝试重新表述您的问题，或者我可以基于我的通用知识来回答。",
                "sources": [],
                "confidence": 0.0
            }

        # Build context
        context = self._build_context(relevant_docs)

        # Generate answer using LLM
        messages = [
            {"role": "system", "content": "你是一个专业的IT学习助手，擅长解释技术概念和提供学习建议。"},
            {"role": "user", "content": self.rag_prompt_template.format(context=context, question=question)}
        ]

        answer = await self.llm_service.chat(messages)

        # Calculate confidence based on similarity
        confidence = max([1 - r["distance"] for r in relevant_docs])

        # Format sources
        sources = [
            {
                "content": r["content"][:200] + "...",
                "metadata": r["metadata"],
                "score": r["distance"]
            }
            for r in relevant_docs
        ]

        return {
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
            "context_used": len(relevant_docs)
        }

    def _build_context(self, results: List[Dict[str, Any]]) -> str:
        """Build context from search results."""

        context_parts = []
        for i, result in enumerate(results, 1):
            metadata = result["metadata"]
            source = f"来源 {i}"
            if "note_id" in metadata:
                source += f" (笔记ID: {metadata['note_id']})"
            elif "course_id" in metadata:
                source += f" (课程ID: {metadata['course_id']})"

            context_parts.append(f"\n{source}\n{result['content']}")

        return "\n".join(context_parts)

    async def chat_with_memory(
        self,
        question: str,
        conversation_history: List[Dict[str, str]],
        collection_name: str = "notes"
    ) -> Dict[str, Any]:
        """Chat with conversation memory and RAG."""

        # Retrieve relevant context
        rag_result = await self.query(question, collection_name)

        # Build messages with history
        messages = [
            {"role": "system", "content": "你是一个专业的IT学习助手。请基于对话历史和检索到的相关内容，回答用户的问题。"},
        ]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": question})

        # Generate answer
        answer = await self.llm_service.chat(messages)

        return {
            "answer": answer,
            "sources": rag_result["sources"],
            "confidence": rag_result["confidence"],
            "rag_used": len(rag_result["sources"]) > 0
        }

    async def summarize_document(
        self,
        content: str,
        max_length: int = 500
    ) -> str:
        """Summarize a document."""

        prompt = f"""请总结以下内容，控制在{max_length}字以内:

{content}

总结:"""

        messages = [
            {"role": "system", "content": "你是一个专业的文档总结助手。"},
            {"role": "user", "content": prompt}
        ]

        summary = await self.llm_service.chat(messages, max_tokens=max_length)
        return summary

    async def extract_key_concepts(
        self,
        content: str,
        max_concepts: int = 10
    ) -> List[str]:
        """Extract key concepts from content."""

        prompt = f"""从以下内容中提取最多{max_concepts}个关键概念或知识点:

{content}

请只列出概念，每行一个:"""

        messages = [
            {"role": "system", "content": "你是一个专业的知识提取助手。"},
            {"role": "user", "content": prompt}
        ]

        result = await self.llm_service.chat(messages)

        # Parse concepts
        concepts = [line.strip() for line in result.split("\n") if line.strip()]
        return concepts[:max_concepts]

    async def generate_explanation(
        self,
        concept: str,
        difficulty: str = "beginner"
    ) -> str:
        """Generate an explanation for a concept."""

        difficulty_prompts = {
            "beginner": "请用简单易懂的语言，适合初学者理解的方式",
            "intermediate": "请用专业的语言，适合有一定基础的开发者理解的方式",
            "advanced": "请用深入的技术细节，适合高级开发者理解的方式"
        }

        prompt = f"""{difficulty_prompts.get(difficulty, '')}解释"{concept}"这个概念。

请提供:
1. 清晰的定义
2. 为什么它重要
3. 实际应用场景
4. 代码示例（如果适用）
5. 相关的进阶主题

解释:"""

        messages = [
            {"role": "system", "content": "你是一个专业的技术概念解释助手。"},
            {"role": "user", "content": prompt}
        ]

        explanation = await self.llm_service.chat(messages, max_tokens=1500)
        return explanation

    async def generate_code_example(
        self,
        language: str,
        description: str,
        include_comments: bool = True
    ) -> str:
        """Generate a code example."""

        prompt = f"""用{language}编写代码实现以下功能:

{description}

{'代码中请添加详细注释。' if include_comments else ''}

只返回代码，不要解释:"""

        messages = [
            {"role": "system", "content": f"你是一个专业的{language}编程助手。"},
            {"role": "user", "content": prompt}
        ]

        code = await self.llm_service.chat(messages)
        return code

    async def improve_code(
        self,
        code: str,
        language: str,
        focus: List[str] = None
    ) -> str:
        """Improve code quality."""

        focus_areas = focus or ["readability", "performance", "best practices"]
        focus_text = "、".join(focus_areas)

        prompt = f"""请改进以下{language}代码，重点关注: {focus_text}

原代码:
```{language}
{code}
```

请提供:
1. 改进后的代码
2. 改进的要点说明

改进后的代码:"""

        messages = [
            {"role": "system", "content": f"你是一个专业的{language}代码审查和优化助手。"},
            {"role": "user", "content": prompt}
        ]

        result = await self.llm_service.chat(messages, max_tokens=2000)
        return result
