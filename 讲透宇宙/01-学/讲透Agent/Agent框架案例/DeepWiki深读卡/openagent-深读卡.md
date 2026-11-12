# openagent 深读卡 —— the-open-agent 自托管个人助理平台：Agent 循环×RAG×30+ provider×多租户后台

> **定位**：the-open-agent 的开源自托管个人 AI 助理平台——LLM+RAG+自主 agent 循环全栈：agent 自主行为含 `browser-use`（网站导航）/shell 执行/办公自动化；30+ 模型 provider；多租户+管理后台（用量/活动/工具编排监控）。
> **本地**：`repos/openagent`（the-open-agent/openagent）｜**深读**：deepwiki 45 子页归档 `deepwiki/openagent/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| Agent 循环 | 自主行为 | browser-use/shell/办公自动化 loops |
| RAG | 文档问答 | 文档多格式交互 |
| 模型层 | 30+ provider | 统一接入 |
| 平台层 | 多租户 | admin dashboard（用量/活动/工具编排） |
| 部署 | 自托管 | full-stack |

## 二、核心机制

1. **browser-use 集成**：自主浏览用 browser-use 库（LLM 驱动 DOM 交互）——浏览器 Agent 的"组装件"路线（对照 steel 托管/invisible 补丁：这是库集成派）。
2. **多租户管理后台**：用量/活动/工具编排可视化——个人助理平台的 SaaS 化骨架。
3. **三循环合一**：浏览+shell+办公自动化三 agent loop 并存——"个人助理=多面手循环集合"。

## 三、与讲透系列的对位

| 概念 | 讲透系列对应概念 |
|---|---|
| browser-use 循环 | 讲透Agent/02 §浏览器工具 |
| 多租户后台 | ai-deployment §平台化 |

## 四、关键入口

```
（全栈：agent loops/RAG/admin；README L91-113）
```

## 五、深读子页地图（45 页精选 5）

OpenAgent Overview｜Agent Loops（browser-use/shell/办公）｜RAG 子系统｜多租户/管理后台｜工具编排。

## 六、与"我们"的关系（一句话）

"自托管个人助理"赛道的全栈模板——与 nanobot（极简）/openclaw（生态化）并列看产品完成度光谱。

---
生成：2026-08-21 · deepwiki 45 页全归档
