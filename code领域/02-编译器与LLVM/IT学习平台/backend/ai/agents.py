"""AI Agents - Specialized assistants for different domains."""

from typing import List, Dict, Any, Optional
from .rag import RAGService
from .config import AISettings


class LearningAssistant:
    """AI assistant for learning and education."""

    def __init__(
        self,
        rag_service: Optional[RAGService] = None,
        settings: Optional[AISettings] = None
    ):
        self.settings = settings or AISettings()
        self.rag_service = rag_service or RAGService(settings)

    async def chat(
        self,
        question: str,
        user_context: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Chat with learning assistant."""

        # Get relevant context from knowledge base
        rag_result = await self.rag_service.query(question)

        # Build system prompt with user context
        system_prompt = self._build_system_prompt(user_context)

        # Build messages
        messages = [
            {"role": "system", "content": system_prompt},
        ]

        if rag_result["confidence"] > 0.7:
            # Add retrieved context
            context = "\n\n".join([s["content"] for s in rag_result["sources"][:3]])
            messages.append({
                "role": "system",
                "content": f"参考知识:\n{context}"
            })

        if conversation_history:
            messages.extend(conversation_history[-6:])  # Keep last 3 turns

        messages.append({"role": "user", "content": question})

        # Generate response
        answer = await self.rag_service.llm_service.chat(messages)

        return {
            "answer": answer,
            "sources": rag_result["sources"],
            "confidence": rag_result["confidence"],
            "suggested_followup": await self._generate_followup_questions(question)
        }

    async def generate_learning_path(
        self,
        learning_goal: str,
        current_level: str = "beginner",
        available_time_week: int = 10
    ) -> Dict[str, Any]:
        """Generate personalized learning path."""

        prompt = f"""为学习者制定学习路径。

学习目标: {learning_goal}
当前水平: {current_level}
每周可用时间: {available_time_week}小时

请制定一个详细的学习路径，包括:
1. 阶段划分（每个阶段的目标和时长）
2. 每个阶段的关键主题
3. 推荐的学习资源（课程、书籍、文档）
4. 实践项目建议
5. 里程碑检查点

请以JSON格式返回，格式如下:
{{
  "title": "学习路径标题",
  "description": "整体描述",
  "total_weeks": 总周数,
  "stages": [
    {{
      "week": 开始周数,
      "duration_weeks": 持续周数,
      "title": "阶段标题",
      "goals": ["目标1", "目标2"],
      "topics": ["主题1", "主题2"],
      "resources": ["资源1", "资源2"],
      "projects": ["项目1", "项目2"],
      "milestones": ["里程碑1", "里程碑2"]
    }}
  ]
}}"""

        messages = [
            {"role": "system", "content": "你是一个专业的学习规划AI助手，擅长制定个性化的学习路径。"},
            {"role": "user", "content": prompt}
        ]

        response = await self.rag_service.llm_service.chat(messages, max_tokens=2000)

        # Try to parse JSON
        try:
            import json
            learning_path = json.loads(response)
        except json.JSONDecodeError:
            # If JSON parsing fails, return as text
            learning_path = {"raw_response": response}

        return learning_path

    async def analyze_progress(
        self,
        completed_items: List[Dict[str, Any]],
        learning_goal: str
    ) -> Dict[str, Any]:
        """Analyze learning progress and provide feedback."""

        completed_str = "\n".join([
            f"- {item.get('title', item.get('name', 'Unknown'))}: {item.get('status', 'completed')}"
            for item in completed_items
        ])

        prompt = f"""分析学习者的进度并提供建议。

学习目标: {learning_goal}

已完成的学习内容:
{completed_str}

请提供:
1. 当前进度评估（百分比）
2. 已掌握的技能
3. 还需要加强的领域
4. 下一步建议
5. 潜在的学习瓶颈和解决方案

请以JSON格式返回分析结果。"""

        messages = [
            {"role": "system", "content": "你是一个专业的学习分析AI助手，擅长评估学习进度并提供个性化建议。"},
            {"role": "user", "content": prompt}
        ]

        response = await self.rag_service.llm_service.chat(messages, max_tokens=1500)

        return {
            "analysis": response,
            "recommendations": await self._generate_recommendations(completed_items, learning_goal)
        }

    async def generate_practice_problems(
        self,
        topic: str,
        difficulty: str = "medium",
        count: int = 3
    ) -> List[Dict[str, Any]]:
        """Generate practice problems for a topic."""

        prompt = f"""为"{topic}"主题生成{count}道练习题。

难度: {difficulty}

每道题应包括:
1. 题目描述
2. 题目类型（选择题、编程题、问答题）
3. 答案或参考解答
4. 解析或说明
5. 考察的知识点

请以JSON数组格式返回。"""

        messages = [
            {"role": "system", "content": "你是一个专业的出题AI助手，擅长生成高质量的练习题。"},
            {"role": "user", "content": prompt}
        ]

        response = await self.rag_service.llm_service.chat(messages, max_tokens=2000)

        try:
            import json
            problems = json.loads(response)
            if not isinstance(problems, list):
                problems = [problems]
            return problems
        except json.JSONDecodeError:
            return [{"raw_response": response}]

    def _build_system_prompt(self, user_context: Optional[Dict[str, Any]]) -> str:
        """Build system prompt with user context."""

        base_prompt = """你是一个专业的IT学习AI助手，帮助用户高效学习计算机技术。
你擅长:
- 解释复杂的技术概念
- 提供清晰的代码示例
- 制定学习计划
- 回答技术问题
- 推荐学习资源

请用友好、鼓励性的语气与用户交流。"""

        if user_context:
            context_parts = []
            if "skill_level" in user_context:
                context_parts.append(f"用户技能水平: {user_context['skill_level']}")
            if "learning_goals" in user_context:
                context_parts.append(f"学习目标: {', '.join(user_context['learning_goals'])}")
            if "current_progress" in user_context:
                context_parts.append(f"当前进度: {user_context['current_progress']}")

            if context_parts:
                base_prompt += "\n\n用户信息:\n" + "\n".join(context_parts)

        return base_prompt

    async def _generate_followup_questions(self, original_question: str) -> List[str]:
        """Generate follow-up questions."""

        prompt = f"""基于用户问题"{original_question}"，生成3个相关的后续问题。

请以JSON数组格式返回，例如: ["问题1", "问题2", "问题3"]"""

        messages = [
            {"role": "system", "content": "你是一个专业的学习助手，擅长提出引导性的后续问题。"},
            {"role": "user", "content": prompt}
        ]

        response = await self.rag_service.llm_service.chat(messages, max_tokens=300)

        try:
            import json
            followups = json.loads(response)
            if isinstance(followups, list):
                return followups
        except json.JSONDecodeError:
            pass

        return []

    async def _generate_recommendations(
        self,
        completed_items: List[Dict[str, Any]],
        learning_goal: str
    ) -> List[str]:
        """Generate learning recommendations."""

        prompt = f"""基于已完成的学习内容，为学习者推荐下一步应该学习的内容。

学习目标: {learning_goal}

请提供5条具体的学习建议。"""

        messages = [
            {"role": "system", "content": "你是一个专业的学习推荐AI助手。"},
            {"role": "user", "content": prompt}
        ]

        response = await self.rag_service.llm_service.chat(messages, max_tokens=500)

        recommendations = [line.strip() for line in response.split("\n") if line.strip()]
        return recommendations[:5]


class ProjectAssistant:
    """AI assistant for project management."""

    def __init__(
        self,
        rag_service: Optional[RAGService] = None,
        settings: Optional[AISettings] = None
    ):
        self.settings = settings or AISettings()
        self.rag_service = rag_service or RAGService(settings)

    async def analyze_project_risk(
        self,
        project_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze project risks and provide mitigation strategies."""

        prompt = f"""分析项目风险并提供缓解策略。

项目信息:
- 名称: {project_data.get('name', 'Unknown')}
- 描述: {project_data.get('description', 'N/A')}
- 团队规模: {project_data.get('team_size', 0)}人
- 当前阶段: {project_data.get('phase', 'Unknown')}
- 剩余时间: {project_data.get('remaining_days', 0)}天
- 已完成任务: {project_data.get('completed_tasks', 0)}/{project_data.get('total_tasks', 0)}

请分析:
1. 项目当前面临的主要风险
2. 每个风险的可能性和影响程度
3. 具体的缓解策略
4. 需要关注的关键指标

请以JSON格式返回分析结果。"""

        messages = [
            {"role": "system", "content": "你是一个专业的项目管理AI助手，擅长风险分析和项目管理最佳实践。"},
            {"role": "user", "content": prompt}
        ]

        response = await self.rag_service.llm_service.chat(messages, max_tokens=2000)

        return {"analysis": response}

    async def optimize_task_assignment(
        self,
        team_members: List[Dict[str, Any]],
        tasks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Optimize task assignment based on team skills."""

        team_str = "\n".join([
            f"- {m.get('name', 'Unknown')}: {m.get('skills', [])}"
            for m in team_members
        ])

        tasks_str = "\n".join([
            f"- {t.get('title', 'Unknown')}: {t.get('description', 'N/A')} (需要: {t.get('required_skills', [])})"
            for t in tasks
        ])

        prompt = f"""优化任务分配。

团队成员:
{team_str}

待分配任务:
{tasks_str}

请根据成员技能和任务要求，提供最优的任务分配方案，并说明理由。

请以JSON格式返回，格式如下:
{{
  "assignments": [
    {{
      "task": "任务名称",
      "assignee": "成员名称",
      "reason": "分配理由",
      "estimated_hours": 预估工时
    }}
  ],
  "recommendations": ["其他建议1", "其他建议2"]
}}"""

        messages = [
            {"role": "system", "content": "你是一个专业的项目管理AI助手，擅长任务分配和团队管理。"},
            {"role": "user", "content": prompt}
        ]

        response = await self.rag_service.llm_service.chat(messages, max_tokens=2000)

        return {"optimization": response}

    async def generate_project_report(
        self,
        project_data: Dict[str, Any]
    ) -> str:
        """Generate project progress report."""

        prompt = f"""生成项目进度报告。

项目信息:
{project_data}

请生成一份专业的项目进度报告，包括:
1. 执行摘要
2. 进度概览
3. 里程碑完成情况
4. 风险和问题
5. 下一步计划

报告格式要清晰、专业。"""

        messages = [
            {"role": "system", "content": "你是一个专业的项目管理AI助手，擅长生成清晰的项目报告。"},
            {"role": "user", "content": prompt}
        ]

        report = await self.rag_service.llm_service.chat(messages, max_tokens=2500)
        return report


class KnowledgeAssistant:
    """AI assistant for knowledge management."""

    def __init__(
        self,
        rag_service: Optional[RAGService] = None,
        settings: Optional[AISettings] = None
    ):
        self.settings = settings or AISettings()
        self.rag_service = rag_service or RAGService(settings)

    async def summarize_content(
        self,
        content: str,
        max_length: int = 500
    ) -> str:
        """Summarize content."""

        return await self.rag_service.summarize_document(content, max_length)

    async def extract_key_points(
        self,
        content: str,
        max_points: int = 5
    ) -> List[str]:
        """Extract key points from content."""

        prompt = f"""从以下内容中提取最多{max_points}个关键要点:

{content}

请以JSON数组格式返回。"""

        messages = [
            {"role": "system", "content": "你是一个专业的知识提取AI助手。"},
            {"role": "user", "content": prompt}
        ]

        response = await self.rag_service.llm_service.chat(messages, max_tokens=500)

        try:
            import json
            points = json.loads(response)
            if isinstance(points, list):
                return points[:max_points]
        except json.JSONDecodeError:
            pass

        return [line.strip() for line in response.split("\n") if line.strip()][:max_points]

    async def expand_content(
        self,
        topic: str,
        current_content: str,
        expansion_type: str = "examples"
    ) -> str:
        """Expand content with additional details."""

        expansion_prompts = {
            "examples": "请提供3-5个实际示例",
            "advanced": "请提供更深入的技术细节和高级概念",
            "applications": "请提供实际应用场景和用例",
            "related": "请提供相关的概念和技术"
        }

        prompt = f"""扩展以下内容。

主题: {topic}

当前内容:
{current_content}

{expansion_prompts.get(expansion_type, '')}

扩展内容:"""

        messages = [
            {"role": "system", "content": "你是一个专业的知识扩展AI助手。"},
            {"role": "user", "content": prompt}
        ]

        expansion = await self.rag_service.llm_service.chat(messages, max_tokens=1500)
        return expansion

    async def generate_quiz(
        self,
        topic: str,
        difficulty: str = "medium",
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """Generate quiz questions."""

        prompt = f"""为"{topic}"主题生成{count}道测试题。

难度: {difficulty}

每道题应包括:
1. 题目
2. 选项（A, B, C, D）
3. 正确答案
4. 解析

请以JSON数组格式返回。"""

        messages = [
            {"role": "system", "content": "你是一个专业的测试题生成AI助手。"},
            {"role": "user", "content": prompt}
        ]

        response = await self.rag_service.llm_service.chat(messages, max_tokens=2000)

        try:
            import json
            quiz = json.loads(response)
            if isinstance(quiz, list):
                return quiz[:count]
        except json.JSONDecodeError:
            pass

        return [{"raw_response": response}]
