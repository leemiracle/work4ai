# 00 · 五形态全景与方法论

---

## 一、五类形态身份卡片

### IDE-A
- **类型**：闭源 VS Code Fork AI IDE
- **本质**：VS Code Fork（Electron 应用）
- **AI 部分**：单一大型 extension bundle（webpack 打包成超大单文件）
- **定位**：企业 / 区域市场的 AI 代码助手

### 桌面 Agent
- **类型**：闭源 Electron 桌面应用
- **本质**：完整 Electron app（main 进程 + 多个 webpack bundle + prompt 模板集 + skill 包）
- **AI 部分**：基于 Agent 架构的桌面办公自动化
- **依赖**：OpenAI Agents SDK + Model Context Protocol SDK
- **定位**：桌面办公 Agent，对标通用办公 Agent 范式

### IDE-B
- **类型**：闭源 VS Code Fork AI IDE
- **本质**：VS Code Fork（Electron 应用）
- **AI 部分**：**高度模块化**——多个独立 extension 各司其职（不混在单一 bundle）
- **协议**：**Protobuf agent schema**（区别于全行业的 JSON）
- **定位**：全球专业开发者的 AI 编码 IDE

### CLI/TUI 框架
- **类型**：开源（Apache 风格许可证）
- **本质**：TypeScript + Bun + monorepo（多 package）
- **特色**：**函数式架构**（Effect-TS 风格 Service 组合，依赖注入）
- **形态**：native binary + Ink TUI
- **定位**：AI 开发工具，CLI / TUI / SDK / Server / Desktop 全栈

### 多渠道网关
- **类型**：开源（MIT 风格许可证）
- **本质**：TypeScript + monorepo（多 package + 大量扩展）
- **特色**：**Multi-channel AI Gateway**（多 IM channel 统一抽象）
- **定位**：个人 AI 助手 + 多渠道消息网关（IM bot 接入）

---

## 二、五类形态对比

| 维度 | IDE-A | 桌面 Agent | IDE-B | CLI/TUI 框架 | 多渠道网关 |
|---|:---:|:---:|:---:|:---:|:---:|
| **形态** | IDE | 桌面 Agent | IDE | CLI/TUI/SDK | 网关 + 多端 |
| **基础** | VS Code Fork | Electron App | VS Code Fork | Native binary + Ink TUI | Node + 多端 native |
| **用户** | 企业/区域开发者 | 非技术职场人 | 全球专业开发者 | 极客开发者 | 任意个人 |
| **闭源/开源** | 闭源 | 闭源 | 闭源 | 开源 | 开源 |
| **商业模式** | ToB IDE 订阅 + 私有化 | 个人订阅 + 企业版 | 个人订阅 + 企业版 | 平台引流 | 基金会/社区 |

---

## 三、方法论（通用结构分析方法）

### 工具链（全部为公开工具）

| 任务 | 工具 |
|---|---|
| Linux deb 结构分析 | `ar x` + `tar -xf data.tar.xz` |
| macOS DMG 结构分析 | `dmg2img` → raw image → APFS 工具挂载 |
| Electron asar 解包 | `@electron/asar`（npm 公开包）|
| webpack bundle 分析 | `strings` + `grep` + Python 字符串提取 |
| TypeScript 源码阅读 | 直接读开源仓库源码 |
| Protobuf schema 提取 | 从 bundle 中提取 typeName 字段 |
| 信息交叉验证 | websearch 公开技术材料 |

### 通用分析流程

1. **确定打包格式**：deb / dmg / appimage / 源码
2. **解包到文件层**：用对应公开工具
3. **定位 AI 相关模块**：extension bundle / main 进程 / agent runtime
4. **提取架构模式**：进程模型 / 协议设计 / 循环结构 / 扩展机制 / 安全模型
5. **与公开实现交叉验证**：对照论文 / 开源项目 / 技术博客

> 📌 **方法学声明**：以上是分析**任何** Electron / VS Code Fork / Node 应用的通用方法。本文档不包含任何针对特定商业产品的解包结果细节。

---

## 四、五类形态的根本架构差异

```
                    IDE 形态
                       │
                IDE-A  │  IDE-B
            (单 bundle) │ (多 extension 模块化)
                       │
  ─────────────────────┼─────────────────────
  闭源                  │                  开源
                       │
  ─────────────────────┼─────────────────────
                       │
            CLI/TUI 框架  │  多渠道网关
              (CLI/TUI)  │  (Multi-channel)
                       │
                   非 IDE 形态
```

**关键差异**：

- **IDE-A**：所有 AI 能力塞进**单一大型 extension bundle**（高度集中）
- **IDE-B**：AI 能力拆成**多个独立 extension**（高度模块化，最大单模块是 agent-exec）
- **桌面 Agent**：**完整 Electron app**（含独立守护进程）
- **CLI/TUI 框架**：**命令行工具 + 函数式架构**（Service 组合）
- **多渠道网关**：**网关 + 多渠道抽象**（IM channel 统一接口）

---

## 五、独有创新数对比

| 形态 | 独有创新数 | 最有价值的三项 |
|---|:---:|---|
| **IDE-B** | **13 个** | 3 进程分离 / Protobuf agent schema / AgentStore CRDT |
| **多渠道网关** | **8 个** | 多渠道统一抽象 / Agent Loop 双层循环 / Tool Loop Recovery |
| **IDE-A** | **8 个** | Multi-Agent × Multi-Model 路由 / Variables @ 触发 / 大量 feature 开关 |
| **桌面 Agent** | **6 个** | 三模式 Craft/Plan/Ask / Skill 自动闭环 / present_files 强制交付 |
| **CLI/TUI 框架** | **5 个** | 函数式 Service 组合 / Crash-safe tool settlement / Native binary CLI |

详见 [`07-innovations.md`](./07-innovations.md)。

---

## 六、做 Agent 时的借鉴路线

### 路线 A：严肃商业编码 Agent（出海）
- **骨架借鉴**：IDE-B（3 进程分离 + Protobuf schema + Shadow Workspace + AI Attribution）
- **机制借鉴**：IDE-A（Variables @ + feature 开关 + Multi-Agent × Multi-Model 路由）
- **防御借鉴**：多渠道网关（Tool Loop Recovery）

### 路线 B：企业 / 区域市场的 Agent
- **骨架借鉴**：IDE-A（合规 + Variables + feature 开关 + 自有协议层）
- **机制借鉴**：IDE-B（AI Attribution + Shadow Workspace）
- **体验借鉴**：桌面 Agent（present_files 强制交付 + Skill 自动闭环）

### 路线 C：小型 / 团队工具
- **骨架借鉴**：CLI/TUI 框架（函数式 Service 组合 + Native binary CLI）

### 路线 D：多渠道 IM Bot
- **骨架借鉴**：多渠道网关（多渠道统一抽象 + Gateway Protocol）

### 路线 E：桌面办公 Agent
- **骨架借鉴**：桌面 Agent（三模式 + Plugin 三件套 + Skill 闭环 + Automations）

详见 [`08-blueprint.md`](./08-blueprint.md)。

---

## 下一步
- 想看具体形态 → 跳到 [`01-05`](./)
- 想看横向对比 → [`06-comparison.md`](./06-comparison.md)
- 想做选型决策 → [`08-blueprint.md`](./08-blueprint.md)
