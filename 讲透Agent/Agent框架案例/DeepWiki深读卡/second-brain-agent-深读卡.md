# second-brain-agent 深读卡 —— 个人第二大脑 PKM Agent：Markdown 笔记自动索引 + 意图路由 + 三接口

> **定位**：flepied 出品的 Personal Knowledge Management（PKM）系统——Tiago Forte "Second Brain" 方法论的 AI 实现：自动索引 Markdown 笔记及嵌入内容（PDF/YouTube/网页/音频），ChromaDB 向量语义检索 + RAG 问答，**意图分类路由**（摘要/活动报告/查找各走专用链），Web UI/MCP server/CLI 三接口访问。
> **本地**：`repos/second-brain-agent`（flepied/second-brain-agent）｜**深读**：deepwiki 21 子页归档 `deepwiki/second-brain-agent/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 数据处理 | Markdown 监控+嵌入内容抽取 | `transform_md.py`、`monitor.sh` |
| 检索 | 向量相似搜索 | ChromaDB、`similarity.py` |
| Agent/RAG | 问答生成 | `lib.py:Agent`、`qa.py`（OpenAI LLM） |
| 意图路由 | 查询分流到专用链 | `extractors.py`（summary/activity/lookup） |
| 接口 | 三路访问 | Web UI、MCP server、CLI（`second_brain_agent.py`） |

## 二、核心机制

1. **自动化索引管线**：monitor.sh 监听笔记目录→transform_md.py 展开嵌入链接（PDF/视频/网页/音频转录）→切块嵌入入 ChromaDB——"第二大脑"的入库全自动。
2. **意图分类路由**：查询先过 extractor 分类（要摘要？要活动报告？要查找？），各走专用处理链——单一 RAG 管线之上的轻量路由层，成本与质量双优。
3. **MCP 一等公民**：笔记库可直接暴露为 MCP server 给 Claude/其他 Agent 用——个人知识接入 Agent 生态的标准姿势。

## 三、与讲透系列的对位

| 概念 | 讲透系列对应概念 |
|---|---|
| 自动索引+嵌入展开 | 讲透NLP §RAG ingest |
| 意图路由 | 讲透Agent/00 §查询路由 |
| MCP server 化 | 讲透Agent/02 §MCP |

## 四、关键入口

```
transform_md.py / monitor.sh    # 索引管线
lib.py / qa.py                  # Agent+RAG
second_brain_agent.py           # CLI 入口
mcp server                      # MCP 暴露
```

## 五、深读子页地图（21 页精选 4）

Overview｜Data Processing Pipeline｜Agent and Intelligence Layer（意图路由）｜User Interfaces。

## 六、与"我们"的关系（一句话）

"个人知识 × Agent"的最小完整样本——比 screenpipe 轻（无录屏）、比 cortex-mem 简（无分层引擎），适合当 PKM-Agent 教学第一例。

---
生成：2026-08-21 · deepwiki 21 页全归档
