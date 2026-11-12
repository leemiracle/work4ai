# cortex-mem 深读卡 —— Rust 类脑三层记忆引擎：L0 抽象/L1 概览/L2 细节 + 虚拟文件系统 × Qdrant

> **定位**：sopaco 出品的 AI-native 记忆框架（Rust 实现）——给 Agent 装跨会话持久"大脑"：**分层三层记忆架构**（L0 Abstract→L1 Overview→L2 Detail，自动提取/组织/优化信息），混合存储=虚拟文件系统持久化（`cortex://` URI）+ Qdrant 向量语义检索。三层 crate：core（引擎/搜索/会话/事件）+ config + tools（抽象/载荷），接口层含 FastMCP 生态接入（ContextMinders 系）。
> **本地**：`repos/cortex-mem`（sopaco/cortex-mem）｜**深读**：deepwiki 51 子页归档 `deepwiki/cortex-mem/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 核心层 | 处理/搜索/事件 | `cortex-mem-core`：CortexMem、VectorSearchEngine、SessionManager、MemoryEventCoordinator |
| 配置层 | 配置管理 | `cortex-mem-config`：Config/QdrantConfig/LLMConfig/EmbeddingConfig |
| 工具层 | 共享抽象 | `cortex-mem-tools`：MemoryOperations、ContextLayer |
| 接口层 | 访问点 | MCP（FastMCP）等协议接入 |
| 存储 | 双轨 | 虚拟文件系统（cortex:// URI）+ Qdrant 向量 |

## 二、核心机制

1. **三层记忆金字塔**：L2 细节（原始信息）→L1 概览（压缩摘要）→L0 抽象（高层知识），自动逐层提炼——模仿人类记忆巩固（与 hindsight 的 biomimetic 路线同思潮，cortex 用分层、hindsight 用分类）。
2. **cortex:// 虚拟文件系统**：记忆寻址像文件路径（目录=语义分区）——可浏览、可版本化，向量库只做检索索引不做存储主体。
3. **Rust 性能+MCP 接入**：核心引擎 Rust 实现（低延迟高并发），经 MCP 暴露给任意 Agent 客户端——"记忆即服务"。

## 三、与讲透系列的对位

| 概念 | 讲透系列对应概念 |
|---|---|
| L0/L1/L2 分层 | 讲透Agent/04 §记忆分层（人类记忆模型映射） |
| 虚拟文件系统寻址 | aeon flat-file 对照 |
| MCP 记忆服务 | 讲透Agent/02 §MCP |

## 四、关键入口

```
（三层 crate：core/config/tools；详见 wiki System Architecture 页组件表）
```

## 五、深读子页地图（51 页精选 5）

Overview｜System Architecture｜Key Features（三层详解）｜Getting Started｜检索/引擎页。

## 六、与"我们"的关系（一句话）

Agent 记忆系统"分层派"代表——与 hindsight（分类派）/openlens-ai（SEAL 派）/mateclaw Dreaming（涌现派）并排即 2026 记忆工程四流派全景。

---
生成：2026-08-21 · deepwiki 51 页全归档
