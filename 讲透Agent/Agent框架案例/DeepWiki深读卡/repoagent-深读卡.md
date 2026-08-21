# repoagent 深读卡 —— OpenBMB 仓库级文档自动生成 Agent：AST 驱动双语 API 文档 + 变更增量维护

> **定位**：OpenBMB 出品的 LLM 仓库文档自动化框架（ICLR'24 workshop）——解析仓库结构、按 Python AST 提取函数/类元信息、LLM 批量生成中文/英双语 API 文档，并靠 **ChangeDetector（git diff）** 在代码演进时增量维护文档。双系统：文档生成 + Chat with Repository（RAG 问答，Gradio WebUI）。
> **本地**：`repos/repoagent`（OpenBMB/RepoAgent）｜**深读**：deepwiki 21 子页归档 `deepwiki/repoagent/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| CLI | 入口 | 命令行（生成/聊天双模式） |
| 文档系统 | 生成与维护 | Documentation Generator（Runner）、Chat Engine、Documentation Metadata、**ChangeDetector**、ProjectManager |
| 仓库交互 | 代码读取 | FileHandler + Git（AST 解析→元信息） |
| 聊天系统 | 仓库问答 | RAG System + Gradio WebUI |
| LLM | 生成 | LLM API（多 provider） |

## 二、核心机制

1. **AST 驱动生成**：不读代码全文而是提取函数签名/文档串等 AST 元信息喂 LLM——输入精确可控，生成稳定（对照 aider RepoMap 的 tree-sitter 路线，同族不同工具）。
2. **ChangeDetector 增量维护**：git diff 检测变更→只重生成受影响文档——文档随代码演进而非一次性的快照，这是它区别于 docstring 生成器的关键。
3. **双语文档元数据**：文档以结构化 metadata 存储（中英双版本），渲染时按需输出。

## 三、与讲透系列的对位

| repoagent 概念 | 讲透系列对应概念 |
|---|---|
| AST 提取→LLM 生成 | 讲透代码生成 §程序分析增强 |
| git diff 增量维护 | 工程化（CI 文档同步） |
| Chat with Repo（RAG） | 讲透NLP §RAG 应用 |

## 四、关键入口

```
repoagent/            # 核心包（Runner/ChatEngine/ChangeDetector）
examples/             # 生成示例
```

## 五、深读子页地图（21 页精选 4）

Overview（双系统架构图）｜Documentation Generation 流程｜ChangeDetector/增量更新｜Chat with Repo。

## 六、与"我们"的关系（一句话）

"文档即代码演进"理念的可跑实现——讲透代码生成章的必引案例（本项目自己的 deepwiki 归档某种意义上就是 RepoAgent 思路的 AI 版）。

---
生成：2026-08-21 · deepwiki 21 页全归档
