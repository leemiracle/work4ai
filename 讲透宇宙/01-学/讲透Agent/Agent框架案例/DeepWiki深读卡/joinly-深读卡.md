# joinly 深读卡 —— 让 AI Agent 参加视频会议的连接中间件：浏览器自动化 × 双向语音 × MCP

> **定位**：joinly.ai 的开源连接中间件——让 AI Agent 通过浏览器自动化加入 Google Meet/Zoom/Teams 会议：双向语音管线（STT 转录进/ TTS 合成出）、MCP server 暴露会议工具与资源、客户端框架内置 LLM 集成。三包 monorepo（uv 管理）：`joinly`（核心服务器）/`joinly-client`（Agent SDK）/`joinly-common`（共享类型），隐私优先设计（本地/云语音可选、可全自托管）。
> **本地**：`repos/joinly`（joinly-ai/joinly）｜**深读**：deepwiki 29 子页归档 `deepwiki/joinly/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 核心服务器 `joinly` | 会议接入+音频处理 | `joinly.main:cli`、browser automation（Meet/Zoom/Teams） |
| 语音管线 | 双向 STT/TTS | 本地或云服务可切换 |
| MCP 接口 | 标准化会议工具/资源 | MCP server |
| 客户端 SDK `joinly-client` | Agent 构建 | `JoinlyClient`、`joinly_client.run`、LLM 集成 |
| 共享类型 `joinly-common` | 跨包契约 | shared types |

## 二、核心机制

1. **浏览器自动化入会**：不靠厂商 API（各家会议 SDK 权限门槛高），直接 headless 浏览器入会——与 invisible-playwright 同思路在会议域的落地。
2. **双向语音管线**：会议音频→STT→Agent→TTS→会议音频流，全链路延迟工程是核心难点（对照 pipecat 的 Frame 流水线思想）。
3. **MCP 化会议能力**：会议状态/参与者/发言等全部做成 MCP 工具——任何 MCP 客户端（Claude 等）都能驱动会议 Agent。

## 三、与讲透系列的对位

| 概念 | 讲透系列对应概念 |
|---|---|
| 浏览器自动化入会 | 讲透Agent/02 §浏览器工具 |
| 双向语音管线 | pipecat 同主题对照 |
| MCP server | 讲透Agent/02 §MCP |

## 四、关键入口

```
joinly/           # 核心包（会议连接+音频）
joinly-client/    # Agent SDK
joinly-common/    # 共享类型
```

## 五、深读子页地图（29 页精选 4）

Overview（三包结构）｜Architecture｜Core Server（会议+音频）｜Client SDK。

## 六、与"我们"的关系（一句话）

"Agent 进物理世界"系列里"参加会议"生态位的一手实现——与 pipecat（语音框架）/steel（浏览器）拼成实时多模态 Agent 的三块积木。

---
生成：2026-08-21 · deepwiki 29 页全归档
