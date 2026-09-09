# TechInsight - 技术媒体洞察平台

> 全面深入处理 InfoQ 及类似技术媒体，构建知识图谱、洞察行业趋势、识别 AI 时代个人机会

## 项目目标

1. **穷尽式采集** InfoQ.cn + 12+ 技术媒体，建立完整的技术内容知识库
2. **构建知识图谱** 提取技术实体和关系，建立架构思维
3. **洞悉行业秘密** 趋势分析 + 跨平台对比，识别行业暗线
4. **发现个人机会** AI 时代的 5 维度机会识别（技术趋势/人才缺口/创业方向/个人成长/变现路径）

## 架构

```
┌─────────────────────────────────────────────────────────┐
│                    数据采集层 (14 源)                      │
│  InfoQ · 掘金 · SegmentFault · 开源中国 · 博客园 · V2EX  │
│  机器之心 · 量子位 · 36氪 · 极客公园 · HackerNews         │
│  Dev.to · 阿里云 · 美团技术                               │
│         RSS Collector · API Collector · Web Collector    │
├─────────────────────────────────────────────────────────┤
│                    存储层                                 │
│         SQLite (文章/实体/关系/趋势)                      │
│         VectorStore (numpy 向量检索)                      │
├─────────────────────────────────────────────────────────┤
│                    分析层 (LLM 驱动)                      │
│  知识图谱构建 → 趋势分析 → 架构提取 → 机会识别             │
│  (无 LLM 时自动降级为关键词统计模式)                       │
├─────────────────────────────────────────────────────────┤
│                    输出层                                 │
│  6 种 Markdown 报告 · Web 仪表盘 · RAG 智能问答           │
└─────────────────────────────────────────────────────────┘
```

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 LLM（可选但推荐）
cp .env.example .env
# 编辑 .env 填入 API Key

# 3. 采集数据
python run.py collect

# 4. 运行分析 + 生成报告
python run.py analyze

# 5. 启动 Web 仪表盘
python run.py web

# 6. RAG 智能问答
python run.py rag "当前最值得关注的技术趋势是什么？"
```

## 命令一览

| 命令 | 说明 |
|------|------|
| `python run.py sources` | 列出所有数据源 |
| `python run.py collect` | 采集全部数据源 |
| `python run.py collect --source infoq` | 仅采集指定源 |
| `python run.py collect --priority 2` | 采集优先级 ≤ 2 的源 |
| `python run.py analyze` | 运行分析管道（知识图谱+趋势+架构+机会+报告）|
| `python run.py full` | 完整管道（采集+分析）|
| `python run.py web` | 启动 Web 仪表盘 (http://127.0.0.1:8765) |
| `python run.py rag "问题"` | RAG 智能问答 |
| `python run.py stats` | 查看数据统计 |

## 生成的报告

| 报告 | 文件 | 内容 |
|------|------|------|
| 内容摘要 | `*_content_digest.md` | 采集概况、热门内容 |
| 知识图谱 | `*_knowledge_graph.md` | 实体、关系、技术集群 |
| 技术趋势 | `*_trend_report.md` | 热门/新兴/衰退技术 |
| 架构全景 | `*_architecture_map.md` | 架构模式、技术栈 |
| 行业洞察 | `*_industry_insight.md` | 资本流向、权力节点 |
| AI 机会 | `*_ai_opportunity.md` | 5 维度个人机会+行动计划 |
| **总报告** | `*_MASTER_report.md` | **以上全部汇总** |

## 配置

- `config/sources.yaml` - 数据源配置（URL、类型、优先级、标签）
- `config/settings.yaml` - LLM/存储/分析/Web 配置
- `.env` - API Key（参见 `.env.example`）

## 技术栈

- **采集**: requests + feedparser + selectolax
- **存储**: SQLite + numpy 向量检索
- **分析**: LLM (智谱GLM/OpenAI 兼容) + 关键词统计降级
- **报告**: Jinja2 模板引擎
- **Web**: FastAPI + 内嵌 HTML 仪表盘

## 合规说明

- 优先使用 RSS/API 等公开数据源
- 遵守 robots.txt 规则
- 低频限流采集（默认 3 秒/请求）
- 仅用于个人研究分析

## 运行测试

```bash
pip install pytest
python -m pytest tests/ -v
```

## 入库说明

- **来源**：`C:\workspace\tech-insight`，2026-09-09 并入 work4ai code-projects（拷贝时排除 `__pycache__`/`.pyc`；工具类项目目录名保留原名，不作中文化）。
- **定位一句话**：技术媒体洞察平台——14 源采集 → SQLite+向量存储 → LLM 分析三层管线，无 API key 时自动降级为关键词统计模式。
- **运行入口**：`run.py`（collect / analyze / full / web / rag / stats 子命令，见上表）；Windows 日常一键入口 `run_daily.bat`。
- **数据现状**：2026-07-15 单日快照，296 篇文章；数据库在 `data/processed/tech_insight.db`，分析报告在 `data/reports/`（6 种 × 多轮运行，含 MASTER 汇总）。
