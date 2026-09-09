"""AI API routes."""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from ..ai import LearningAssistant, ProjectAssistant, KnowledgeAssistant
from ..ai.rag import RAGService
from ..ai.vector_store import VectorStoreService
from ..ai.config import AISettings

router = APIRouter(prefix="/ai", tags=["ai"])

# Initialize AI services
settings = AISettings()
rag_service = RAGService(settings=settings)
vector_store = VectorStoreService(settings=settings)
learning_assistant = LearningAssistant(rag_service=rag_service, settings=settings)
project_assistant = ProjectAssistant(rag_service=rag_service, settings=settings)
knowledge_assistant = KnowledgeAssistant(rag_service=rag_service, settings=settings)


# Request/Response Models
class ChatRequest(BaseModel):
    question: str
    user_context: Optional[Dict[str, Any]] = None
    conversation_history: Optional[List[Dict[str, str]]] = None


class LearningPathRequest(BaseModel):
    learning_goal: str
    current_level: str = "beginner"
    available_time_week: int = 10


class ProgressAnalysisRequest(BaseModel):
    completed_items: List[Dict[str, Any]]
    learning_goal: str


class PracticeProblemRequest(BaseModel):
    topic: str
    difficulty: str = "medium"
    count: int = 3


class ProjectRiskRequest(BaseModel):
    project_data: Dict[str, Any]


class TaskOptimizationRequest(BaseModel):
    team_members: List[Dict[str, Any]]
    tasks: List[Dict[str, Any]]


class ContentSummaryRequest(BaseModel):
    content: str
    max_length: int = 500


class ContentExpansionRequest(BaseModel):
    topic: str
    current_content: str
    expansion_type: str = "examples"


class QuizGenerationRequest(BaseModel):
    topic: str
    difficulty: str = "medium"
    count: int = 5


class SemanticSearchRequest(BaseModel):
    query: str
    collection_name: str = "notes"
    n_results: int = 5
    filter_metadata: Optional[Dict[str, Any]] = None


class CodeGenerationRequest(BaseModel):
    language: str
    description: str
    include_comments: bool = True


class CodeImprovementRequest(BaseModel):
    code: str
    language: str
    focus: Optional[List[str]] = None


# ==================== AI Learning Assistant Endpoints ====================

@router.post("/learning/chat")
async def learning_chat(request: ChatRequest):
    """Chat with AI learning assistant."""
    try:
        response = await learning_assistant.chat(
            question=request.question,
            user_context=request.user_context,
            conversation_history=request.conversation_history
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/learning/path")
async def generate_learning_path(request: LearningPathRequest):
    """Generate personalized learning path."""
    try:
        path = await learning_assistant.generate_learning_path(
            learning_goal=request.learning_goal,
            current_level=request.current_level,
            available_time_week=request.available_time_week
        )
        return path
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/learning/analyze-progress")
async def analyze_progress(request: ProgressAnalysisRequest):
    """Analyze learning progress."""
    try:
        analysis = await learning_assistant.analyze_progress(
            completed_items=request.completed_items,
            learning_goal=request.learning_goal
        )
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/learning/practice-problems")
async def generate_practice_problems(request: PracticeProblemRequest):
    """Generate practice problems."""
    try:
        problems = await learning_assistant.generate_practice_problems(
            topic=request.topic,
            difficulty=request.difficulty,
            count=request.count
        )
        return problems
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== AI Project Assistant Endpoints ====================

@router.post("/project/risk-analysis")
async def analyze_project_risk(request: ProjectRiskRequest):
    """Analyze project risks."""
    try:
        analysis = await project_assistant.analyze_project_risk(request.project_data)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/project/optimize-tasks")
async def optimize_task_assignment(request: TaskOptimizationRequest):
    """Optimize task assignment."""
    try:
        optimization = await project_assistant.optimize_task_assignment(
            team_members=request.team_members,
            tasks=request.tasks
        )
        return optimization
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/project/report")
async def generate_project_report(project_data: Dict[str, Any]):
    """Generate project report."""
    try:
        report = await project_assistant.generate_project_report(project_data)
        return {"report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== AI Knowledge Management Endpoints ====================

@router.post("/knowledge/summarize")
async def summarize_content(request: ContentSummaryRequest):
    """Summarize content."""
    try:
        summary = await knowledge_assistant.summarize_content(
            content=request.content,
            max_length=request.max_length
        )
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge/expand")
async def expand_content(request: ContentExpansionRequest):
    """Expand content."""
    try:
        expansion = await knowledge_assistant.expand_content(
            topic=request.topic,
            current_content=request.current_content,
            expansion_type=request.expansion_type
        )
        return {"expansion": expansion}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge/quiz")
async def generate_quiz(request: QuizGenerationRequest):
    """Generate quiz questions."""
    try:
        quiz = await knowledge_assistant.generate_quiz(
            topic=request.topic,
            difficulty=request.difficulty,
            count=request.count
        )
        return quiz
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge/search")
async def semantic_search(request: SemanticSearchRequest):
    """Perform semantic search with RAG."""
    try:
        results = await rag_service.query(
            question=request.query,
            collection_name=request.collection_name,
            n_results=request.n_results,
            filter_metadata=request.filter_metadata
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== AI Coding Assistant Endpoints ====================

@router.post("/code/generate")
async def generate_code(request: CodeGenerationRequest):
    """Generate code."""
    try:
        code = await rag_service.generate_code_example(
            language=request.language,
            description=request.description,
            include_comments=request.include_comments
        )
        return {"code": code}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/code/improve")
async def improve_code(request: CodeImprovementRequest):
    """Improve code."""
    try:
        improvement = await rag_service.improve_code(
            code=request.code,
            language=request.language,
            focus=request.focus
        )
        return {"improvement": improvement}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/code/explain")
async def explain_code(code: str, language: str = "python"):
    """Explain code."""
    try:
        prompt = f"""请详细解释以下{language}代码的功能和工作原理:

```{language}
{code}
```

请从以下几个方面进行解释:
1. 整体功能
2. 关键逻辑
3. 使用的算法或数据结构
4. 时间复杂度分析
5. 代码风格评价
6. 可能的改进建议

解释:"""

        messages = [
            {"role": "system", "content": f"你是一个专业的{language}代码解释AI助手。"},
            {"role": "user", "content": prompt}
        ]

        explanation = await rag_service.llm_service.chat(messages, max_tokens=1500)
        return {"explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Vector Store Management Endpoints ====================

@router.get("/vector-store/stats/{collection_name}")
async def get_collection_stats(collection_name: str):
    """Get vector collection statistics."""
    try:
        stats = vector_store.get_collection_stats(collection_name)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vector-store/collections")
async def list_collections():
    """List all vector collections."""
    try:
        collections = vector_store.list_collections()
        return {"collections": collections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== AI System Endpoints ====================

@router.get("/status")
async def ai_status():
    """Get AI system status."""
    return {
        "status": "active",
        "llm_provider": settings.LLM_PROVIDER,
        "embedding_provider": settings.EMBEDDING_PROVIDER,
        "vector_db_provider": settings.VECTOR_DB_PROVIDER,
        "default_model": settings.DEFAULT_MODEL,
        "collections": vector_store.list_collections()
    }


@router.post("/concept/explain")
async def explain_concept(
    concept: str,
    difficulty: str = "beginner"
):
    """Generate explanation for a concept."""
    try:
        explanation = await rag_service.generate_explanation(concept, difficulty)
        return {"explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/concepts/extract")
async def extract_key_concepts(
    content: str,
    max_concepts: int = 10
):
    """Extract key concepts from content."""
    try:
        concepts = await rag_service.extract_key_concepts(content, max_concepts)
        return {"concepts": concepts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
