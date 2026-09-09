# InfoQ Atlas · 技术内容全景知识库

> 以 **InfoQ 中国** 为主干，**精读式深度利用内容**，并向 **9 个经典技术网站**扩展，
> 构建「抓取 → 规范化 → 统计 → 内容情报(NLP) → **专家级深度综合** → 知识图谱 → 跨站综合 → 可视化」的完整体系。

## 这是什么

不只是爬虫。本项目对 InfoQ 全站 14 个 Topic（架构/AI/后端/云计算/大数据…）做：
- 📥 **全量目录**（25,801 篇去重文章）+ **高信号全文**（833 篇）
- 🧠 **内容情报层**：技术实体抽取、关键短语、自动摘要、子主题发现、概念演化
- 🕸️ **跨 Topic 知识图谱**：共现网络、作者偏好
- 🌐 **多经典网站扩展**：美团技术 / 博客园 / 开源中国 / 张鑫旭 / HackerNews / dev.to / 阮一峰周刊 / **Martin Fowler / CSS-Tricks**（9 站）
- 🔥 **跨站技术共识**：识别在多个顶级站同时被讨论的「主流转技术势」
- 📖 **专家级深度综合**：精读 InfoQ 14 个 topic 全文 + 9 经典站后写出有洞察的技术叙事（非统计）
- 📊 **可视化仪表盘** + **全景主报告**

## 核心洞察示例

跨经典网站技术共识（出现在 ≥3 个站的当下主流技术）：

| 技术 | 出现站点 | |
|------|---------|-|
| Agent / Go / Claude | 5 站 | 当下最热 |
| GPT / RAG / Google | 4 站 | 主流 |
| DeepSeek / Rust / Docker / OpenAI / Anthropic | 3 站 | 强势 |

## 信息来源

### 主干：InfoQ 中国（深度穷尽）
- 25,801 篇文章目录 + 833 篇全文
- 14 顶层 Topic / 88 节点，跨 topic 关联 200,656 条

### 扩展：9 个经典技术网站（跨站情报）
| 来源 | 类型 | 采集方式 |
|------|------|---------|
| 美团技术团队 | Atom | feed + 全文抽取 |
| 博客园 | RSS | feed + 全文抽取 |
| 开源中国 | RSS | feed + 全文抽取 |
| 张鑫旭-前端 | RSS | feed |
| HackerNews | API | Algolia API |
| dev.to | API | REST API + 全文 |
| 阮一峰周刊 | HTML | 列表解析 |
| Martin Fowler | Atom | feed + 全文抽取（架构权威）|
| CSS-Tricks | RSS | feed（前端经典）|

## ③ 大模型知识抽取（GLM-5.1 + 全量覆盖）

**三层知识库，覆盖全部 25,801 篇文章：**
1. **GLM-5.1 精抽（833 全文）**：接入智谱 BigModel 真实 API，对 InfoQ 833 篇全文 + 155 篇站点全文（共 970 篇）产出**语义三元组**（关系：解决/导致/基于/优化/实现/演进为/优于/替代…）。推理模型截断容错，错误率<0.5%。
2. **目录 NLP 全量（24,968 篇）**：对仅有标题+摘要的文章用 NLP 实体词典秒级覆盖，保证全量。
3. 合计 **25,953 条目 / 54,483 三元组 / 19,237 概念**，入库可 SQL 检索。

示例三元组：`(低代码平台, 替代, 增删改查)`、`(AI Agent, 适用于, 复杂决策)`、`(Java Agent, 实现, JVMTI)`

> 模块：`llm.py`(GLM客户端) / `kb_llm.py`(InfoQ全文) / `kb_llm_sites.py`(站点) / `kb_catalog_nlp.py`(目录全量) / `kb_report.py`(入库)

## Neo4j 图谱导出

生成可一键导入的图数据库文件：
- 节点：Concept(36,683) / Article(25,801) / Topic(88)
- 关系：语义三元组(44,759) + 文章-主题(200,656)
- 文件：`neo4j/{nodes,rels}_*.csv` + `import.cypher` + `README.md`（含 `neo4j-admin import` 与浏览器 LOAD CSV 两种方式 + 探索 Cypher）

## 产出清单

每个 InfoQ Topic 现有 **三层报告**：统计深度 + 内容情报 + 主题演化。

```
reports/
  topics/   14 × {深度报告 + 内容摘要(_DIGEST) + 主题演化(_THEMES)}
  global/
    PANORAMA.md            全景主报告（InfoQ+多站综合）⭐ 入口
    DEEP_SYNTHESIS.md      InfoQ 14 topic 专家级深度综合 ⭐ 精读产出
    CROSS_SITE_DEEP.md     9 经典站跨站深度综合 ⭐
    THEMES_EVOLUTION.md    全局主题演化 + 概念图谱（复用知识三元组）⭐
    KNOWLEDGE_BASE.md      大模型抽取的摘要+知识三元组 ⭐
    INFOQ_ATLAS_GLOBAL.md  InfoQ 全站综合分析
    CONTENT_INTEL.md       InfoQ 内容情报
    CROSS_SITE_INTEL.md    跨经典网站技术情报
    knowledge_graph.md     跨 topic 知识图谱
dashboard/
  index.html               ECharts 可视化仪表盘（6 图表含概念关系图）
  concept_graph.json       跨 topic 概念关系图（GLM-5.1 三元组，7200节点）
  kg.json                  topic 共现网络
data/
  raw/{topics,lists,articles,sites}   原始数据（含 9 经典站 ~940 条）
  processed/infoq.db                  SQLite + FTS5 + knowledge_triples(4808)
  processed/knowledge_llm.jsonl       GLM-5.1 抽取（InfoQ 814 篇）
  processed/knowledge_sites.jsonl     GLM-5.1 抽取（站点 155 篇）
```

## 技术亮点

- **API 逆向**：InfoQ 是 SPA，逆向出 `topic/getList` / `article/getList`(score 游标分页) /
  `article/getDetail` + 正文 ProseMirror JSON；detail 端点遇 451 限流时，**自动改走文章页 SSR 提取 content_url**。
- **ProseMirror → Markdown** 转换器（覆盖段落/标题/列表/代码/图片/表格/引用等）。
- **无依赖 NLP**：技术实体词典(13 类 200+ 术语) + RAKE 关键短语 + 抽取式摘要 + 子主题发现，
  纯标准库实现，避免外部包。
- **慢 FS 适配**：WSL `/mnt/c` I/O 极慢，全链路改 bulk read/write。

## 使用

```bash
# 完整流水线（含爬取）
python -m src.run_all

# 仅基于已有数据重新分析产出（不爬）
python -m src.run_all --no-crawl

# 分步
python -m src.crawl_topics        && python -m src.crawl_catalog --max-pages 200 --workers 4
python -m src.crawl_content       && python -m src.normalize && python -m src.enrich
python -m src.analyze             && python -m src.kg && python -m src.content_intel
python -m src.harvest_sites       && python -m src.harvest_deep && python -m src.site_intel
# GLM-5.1 全量知识抽取（需 Z_AI_API_KEY，自动从 opencode.json 读取）
python -m src.kb_llm 0 10         # InfoQ 全量（815篇,10并发）
python -m src.kb_llm_sites 8      # 经典站全文（155篇）
python -m src.kb_report           # 入库 + 知识库报告
python -m src.cluster_evolve      # 主题演化 + 概念图
python -m src.report_gen          && python -m src.dashboard && python -m src.panorama

# 增量更新
python -m src.update --rebuild
```

## 检索示例

```python
import sqlite3
conn = sqlite3.connect("data/processed/infoq.db")
# 全文搜
for r in conn.execute(
    "SELECT a.title,a.year,a.views FROM articles_fts f JOIN articles a ON f.aid=a.aid "
    "WHERE articles_fts MATCH '大模型' ORDER BY a.views DESC LIMIT 10"):
    print(r)
```

## 节制声明
仅采集公开 API/Feed 数据，保持礼貌节流，不破解鉴权；数据用于学习研究分析。
