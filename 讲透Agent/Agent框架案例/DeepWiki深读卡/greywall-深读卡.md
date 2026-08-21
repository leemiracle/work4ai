# greywall 深读卡 —— 无容器 deny-by-default 沙盒：文件系统/网络/syscall 三重白名单包裹任意命令

> **定位**：GreyhavenHQ 的 **deny-by-default 沙盒**——无容器方案包裹任意不可信命令（专指 AI 编码 agent：Claude Code/Cursor/Aider），文件系统访问/网络连接/系统调用**默认全拒、显式白名单放行**，防 agent 触碰 SSH key 等敏感数据。平台双实现：Linux 与 macOS 各有落地路径。
> **本地**：`repos/greywall`（GreyhavenHQ/greywall）｜**深读**：deepwiki 36 子页归档 `deepwiki/greywall/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 沙盒核 | deny 默认 | 安全信封（fs+net+syscall 白名单） |
| 平台层 | 双 OS | Linux 实现 / macOS 实现 |
| 数据流 | 命令→强制 | command execution → sandbox enforcement |

## 二、核心机制

1. **默认拒绝模型**：与"默认放行+黑名单"（多数工具）相反——一切访问默认拒绝，白名单显式 grant——安全工程的正确默认（最小权限原则的严格执行）。
2. **无容器**：不用 Docker/VM——OS 原生机制（Linux/macOS 各自的 fs/net/syscall 过滤）轻量包裹——对照 modus WASM/e2b microVM/greywall 原生 OS 三条沙盒路线。
3. **三域同时锁**：文件/网络/系统调用三个攻击面一并白名单——只锁文件不锁网络等于没锁。

## 三、与讲透系列的对位

| 概念 | 讲透系列对应概念 |
|---|---|
| deny-by-default | 讲透Agent/00 §最小权限 |
| 无容器沙盒 | 沙盒谱系第四级（OS 原生） |
| 三域白名单 | 安全纵深案例 |

## 四、关键入口

```
（双平台实现；详见 wiki Platform-Specific Implementations）
```

## 五、深读子页地图（36 页精选 5）

Overview｜Core Concepts（安全模型）｜Linux/macOS 实现｜Data Flow（命令→强制）｜Getting Started。

## 六、与"我们"的关系（一句话）

沙盒谱系补上"OS 原生白名单"级——与 AST（smolagents）/WASM（modus）/Docker（openhands）/microVM（e2b）五级横排即讲透 Agent 安全沙盒的完整教具矩阵。

---
生成：2026-08-21 · deepwiki 36 页全归档
