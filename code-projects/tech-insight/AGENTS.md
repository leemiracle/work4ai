# TechInsight 项目指南

## 概述
技术媒体洞察平台：采集 InfoQ + 12+ 技术媒体 → 构建知识图谱 → 趋势/架构分析 → 识别 AI 时代个人机会

## 快速命令
```bash
python run.py collect          # 采集
python run.py analyze          # 分析+报告
python run.py web              # Web 仪表盘 (127.0.0.1:8765)
python run.py rag "问题"       # RAG 问答
python run.py stats            # 统计
python -m pytest tests/ -v    # 测试
```

## 项目结构
```
src/
├── config.py              # YAML 配置加载 + 环境变量
├── pipeline.py            # 管道编排（采集→分析→报告）
├── collectors/            # 数据采集（RSS/API/Web + 内容增强）
├── storage/               # SQLite + 向量存储 + 数据模型
├── analysis/              # LLM 客户端 + 知识图谱/趋势/架构/机会分析
├── reports/               # Jinja2 报告生成（6种报告）
├── rag/                   # RAG 检索增强问答
└── web/                   # FastAPI 仪表盘
config/
├── sources.yaml           # 14 个数据源配置
└── settings.yaml          # LLM/存储/分析配置
```

## 关键设计
- **合规优先**: RSS/API > robots.txt 限流爬取
- **降级策略**: 无 LLM 时自动降级为关键词统计模式
- **LLM 兼容**: 支持 OpenAI 兼容接口（智谱GLM/OpenAI/月之暗面）
- **环境变量**: `{env:VAR_NAME}` 格式，参见 `.env.example`

## 数据源（14个）
| 优先级 | 源 | 类型 |
|--------|-----|------|
| P1 | InfoQ | RSS |
| P2 | 掘金/SegmentFault/开源中国/博客园/V2EX | API/RSS |
| P3 | 机器之心/量子位/36氪/极客公园/HackerNews/Dev.to | RSS/API/Web |
| P4 | 阿里云/美团技术 | Web/RSS |

## 注意事项
- 部分数据源（V2EX/geekpark）在某些网络环境可能无法访问
- InfoQ 文章全文需 JS 渲染，RSS 仅提供摘要
- 配置 LLM API Key 后分析质量显著提升
