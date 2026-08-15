# 04 · CLI/TUI 框架架构模式（开源，函数式）

> 开发者 CLI/TUI/SDK 框架形态——**函数式架构最纯粹**。本文档已脱敏。

---

## 一、形态定位

- **形态**：CLI / TUI / SDK / Server / Desktop 全栈（native binary 分发）
- **用户**：极客开发者
- **特点**：函数式架构（Effect-TS 风格 Service 组合）
- **架构取向**：架构驱动，重工程严谨性和可组合性

---

## 二、架构特点

- **基础**：TypeScript + Bun + monorepo（多 package）
- **形态**：Native binary（编译分发）+ Ink TUI
- **架构范式**：**函数式 Service 组合**（依赖注入，任何 Service 可替换）
- **状态管理**：函数式（Effect 风格流 + Service）
- **持久化**：SQLite（函数式 ORM）
- **构建**：脚本化（bun run build）

---

## 三、独有设计（该形态的创新）

### ★★★★★ 函数式 Service 组合（依赖注入）

多个 Service（如 LLM / Tool / Permission / Memory 等）用函数式组合——任何 Service 可替换/模拟/测试。

**借鉴价值**：**函数式依赖注入**让 agent 的每个组件都可替换。这是"可测试、可组合"agent 框架的根基。对比面向对象的 DI，函数式更纯粹。

### ★★★★★ Crash-safe tool settlement（先持久化再执行）

工具调用前先持久化 settlement，再执行——crash 后可恢复。

**借鉴价值**：**crash 恢复是生产 agent 的刚需**。先写日志/状态再执行，保证 at-least-once 语义。

### ★★★★ Turn Transition 类型化

把 turn 之间的转换做成 union type（如 `tool_call → tool_result | user_declined | error`）。

**借鉴价值**：类型化的状态机让 agent 行为可调试、可审计。

### ★★★★ User Declined ≠ Tool Output

用户拒绝工具调用时，halt（不是把"拒绝"当成工具输出喂给 LLM）。

**借鉴价值**：**防 LLM 绕过权限**。如果"拒绝"被当成工具输出，LLM 可能误解为"工具返回了拒绝信息"继续推进。明确区分两者。

### ★★★ MAX_STEPS 硬约束

十几行 prompt 注入实现简单的防死循环。

**借鉴价值**：最简单的防死循环——硬编码步数上限。

### ★★★ Native binary CLI

用 Bun/esbuild 编译成 native binary 分发——启动快、无 runtime 依赖。

### ★★★ HTTP API Codegen + Recorder

HTTP API 的代码生成 + 请求录制回放——独有功能，便于集成第三方 API。

---

## 四、反模式（该形态的教训）

- ❌ **过度拆分**（过多 packages）—— 历史包袱重，应适度合并
- ❌ **团队不熟函数式却强行用**—— Effect 等函数式框架有学习曲线

---

## 五、借鉴价值

做**开发者 CLI/TUI 工具**时，借鉴此形态的：
- **函数式 Service 组合**（可测试可组合）
- **Crash-safe tool settlement**（crash 恢复）
- **Native binary CLI**（启动快分发易）
- **Turn Transition 类型化**（可调试）
- **User Declined ≠ Tool Output**（权限严谨）
- **MAX_STEPS 硬约束**（简单防死循环）
- **HTTP API Codegen**（API 集成利器）

> 该形态是"函数式工程严谨性"的典范——独有创新虽少（5 个），但每个都是**防御性设计**的精品（crash-safe / 类型化 / 权限区分 / 步数约束）。

---

## 下一步
- 看多渠道网关的多渠道抽象 → [`05-多渠道网关.md`](./05-多渠道网关.md)
- 看横向对比 → [`06-comparison.md`](./06-comparison.md)
