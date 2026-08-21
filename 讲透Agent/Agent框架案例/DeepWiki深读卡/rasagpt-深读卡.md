# rasagpt 深读卡 —— Rasa 状态机 × LLM 生成的混合对话架构参考实现（2023 boilerplate）

> **定位**：paulpierre 出品的 headless LLM chatbot 平台 boilerplate（2023）——**Rasa（对话管理状态机/DSL）+ LangChain/LlamaIndex（LLM 生成与文档检索）+ FastAPI + pgvector + Telegram** 的首个完整集成参考。核心命题：对话流程控制（Rasa 擅长）与自由生成（LLM 擅长）如何分工——这是"确定性对话编排 × 涌生成"混合路线的早期模板。
> **本地**：`repos/rasagpt`（paulpierre/RasaGPT）｜**深读**：deepwiki 17 子页归档 `deepwiki/rasagpt/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 渠道层 | Telegram 接入 | Telegram API + Ngrok webhook |
| API 层 | headless 服务 | FastAPI server（forward to Rasa） |
| 对话管理 | 状态机/DSL/故事 | Rasa Core |
| LLM 层 | 自由生成+文档检索 | LangChain + LlamaIndex |
| 向量层 | 文档库 | **自研 pgvector 实现**（替换 LangChain 默认） |
| 多租户 | 会话/元数据隔离 | multi-tenancy + session management |
| 部署 | 容器化 | Docker（Rasa in Docker 跨平台方案）+ 反向代理 |

## 二、核心机制

1. **Rasa↔LLM 分工**：Rasa 管 intent/slot/故事流（确定性对话控制），LLM 兜底自由问答+RAG——"该确定的地方确定，该生成的地方生成"，与 2026 年 bernstein 的 zero-LLM 协调哲学遥相呼应（方向相反的同一问题）。
2. **自研 pgvector**：不用 LangChain 默认向量集成而手写 pgvector 管线——解决库冲突+性能可控，17 页 wiki 专门记录了这个决策。
3. **工程缺口填补清单**（README 7 条）：专有 bot endpoint+文档训练管线、库冲突解决、Docker 跨平台、反向代理、多租户——2023 年拼一套生产对话系统的真实坑位全记录。

## 三、与讲透系列的对位

| rasagpt 概念 | 讲透系列对应概念 |
|---|---|
| Rasa 状态机×LLM 分工 | 讲透Agent/01 §确定性编排 vs 涌现生成 |
| pgvector 自研管线 | 讲透NLP §RAG 存储 |
| headless API + 渠道解耦 | ai-deployment §服务化 |

## 四、关键入口

```
bot/                 # Rasa 域/故事/配置
api/                 # FastAPI（Rasa↔LLM 桥）
docker-compose.yml   # 全栈编排
```

## 五、深读子页地图（17 页精选 4）

Overview（架构图：Telegram→FastAPI→Rasa→LLM）｜System Architecture｜pgvector 实现章节｜Deployment（Docker 跨平台）。

## 六、与"我们"的关系（一句话）

讲对话系统演进史的活化石："NLU 时代（Rasa）→ LLM 时代"的断层线上，它给出了最早的混合架构拼图——今天讨论"该不该用状态机管对话"时，先看它踩过的坑。

---
生成：2026-08-21 · deepwiki 17 页全归档
