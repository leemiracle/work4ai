# modus 深读卡 —— WASM Serverless Agent 运行时：代码编译进沙盒 + GraphQL API 自动生成

> **定位**：Hypermode（Dgraph 图数据库团队）出品的开源 serverless 框架——**Go/AssemblyScript 代码编译成 WebAssembly 模块**，在 wazero WASM 宿主沙盒中执行，并**自动生成 GraphQL API**。Agentic 系统/AI 应用的"函数即服务"路线：开发者写函数，框架管沙盒隔离/接口生成/服务集成（LLM/向量库等）——Agent 基础设施的 WASM 派。
> **本地**：`repos/modus`（hypermodeinc/modus）｜**深读**：deepwiki 26 子页归档 `deepwiki/modus/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 开发层 | 工具链+SDK | modus CLI（TS/Node）、Go SDK、AssemblyScript SDK |
| 运行层 | WASM 宿主+引擎 | Modus Runtime、**wazero**（零依赖 WASM host）、GraphQL Engine（wundergraph） |
| 沙盒 | 执行隔离 | WASM 线性内存隔离（ Capability-based 安全模型） |
| 支撑库 | 清单/元数据/分析 | manifest 处理、metadata 提取、WASM 分析 |

## 二、核心机制

1. **编译即沙盒**：代码编译到 WASM 而非容器/进程隔离——冷启动微秒级+内存硬隔离，"函数级 microVM"（对照 e2b Firecracker：VM 级更强但重；smolagents AST：解释器级最轻）。
2. **GraphQL 自动生成**：导出函数签名→GraphQL schema 自动暴露——"写函数即得 API"，agent 服务化零胶水。
3. **图数据库血统**：Hypermode/Dgraph 团队出品，GraphQL 引擎是家传手艺——对图结构 agent 数据天然友好。

## 三、与讲透系列的对位

| 概念 | 讲透系列对应概念 |
|---|---|
| WASM 沙盒谱系 | 讲透Agent/00 §沙盒三级（AST/容器/VM→WASM 第四级） |
| API 自动生成 | ai-deployment §serverless |
| 冷启动工程 | 讲透分布式AI系统 |

## 四、关键入口

```
runtime/          # Modus Runtime（wazero host+GraphQL）
sdk/go, sdk/as    # 双语言 SDK
cli/              # modus CLI
```

## 五、深读子页地图（26 页精选 5）

Overview（四组件架构图）｜CLI Commands｜Go SDK｜**Runtime Architecture（wazero 宿主）**｜GraphQL Engine。

## 六、与"我们"的关系（一句话）

Agent 沙盒技术树上的"WASM 分支"代表——讲安全沙盒专题时与 AST（smolagents）/Docker（openhands）/microVM（e2b）并排成四级隔离谱系。

---
生成：2026-08-21 · deepwiki 26 页全归档
