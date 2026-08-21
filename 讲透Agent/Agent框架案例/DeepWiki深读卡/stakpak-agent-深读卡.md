# stakpak-agent 深读卡 —— Rust 企业级 DevOps AI 助手：动态密钥脱敏 + mTLS + 隐私优先终端

> **定位**：stakpak 的 AI DevOps 助手——企业安全优先的交互式终端：动态 secret 脱敏、双向 TLS（mTLS）加密、隐私第一架构。Rust workspace 12 crates 三层组织：用户应用层/核心库层/MCP 组件层——"把安全当第一特性"的终端 Agent 样本。
> **本地**：`repos/stakpak-agent`（stakpak/agent）｜**深读**：deepwiki 36 子页归档 `deepwiki/stakpak-agent/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 用户层 | CLI/TUI 应用 | 交互终端 |
| 核心库 | 引擎与安全 | 12 crates（脱敏/加密/会话） |
| MCP 层 | 工具协议 | MCP 组件 |
| 安全 | 三大件 | 动态 secret redaction、mutual TLS、deny 默认 |

## 二、核心机制

1. **动态密钥脱敏**：终端输出/LLM 上下文中的 secret 实时脱敏——防密钥进对话历史被记录（DevOps 场景刚需，多数编码 Agent 缺失）。
2. **mTLS 双向认证**：Agent 与后端通信双向证书——企业零信任接入。
3. **Rust 12-crate 分层**：安全边界（内存安全语言）+ 模块边界（workspace 分层）双保险。

## 三、与讲透系列的对位

| 概念 | 讲透系列对应概念 |
|---|---|
| secret 脱敏 | 讲透Agent/00 §安全（输出侧防护） |
| mTLS | ai-deployment §零信任 |
| Rust Agent | claw-code/greywall 同语言派对照 |

## 四、关键入口

```
（Rust workspace：apps/core/mcp 三层 12 crates）
```

## 五、深读子页地图（36 页精选 5）

Overview｜CLI Interface｜TUI｜MCP System｜**Security and Privacy（灵魂页）**。

## 六、与"我们"的关系（一句话）

"安全优先 DevOps Agent"孤本样本——讲 Agent 安全覆盖面时补上"数据脱敏"这一常被忽略的维度。

---
生成：2026-08-21 · deepwiki 36 页全归档
