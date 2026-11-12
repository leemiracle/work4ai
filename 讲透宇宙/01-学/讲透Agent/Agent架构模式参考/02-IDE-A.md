# 02 · IDE-A 架构模式（VS Code Fork，企业 / 区域市场路线）

> 企业/区域市场的 AI 编码 IDE 形态。本文档已脱敏。

---

## 一、形态定位

- **形态**：VS Code Fork AI IDE（单一大型 extension）
- **用户**：企业/区域市场开发者
- **特点**：合规优先 + 多形态分化（SaaS/企业/私有化用同一份代码）
- **架构取向**：场景驱动，重用户体验和本地化适配

---

## 二、架构特点

- **基础**：VS Code Fork（Electron）
- **AI 集成方式**：所有 AI 能力塞进**单一大型 extension bundle**（高度集中，与 IDE-B 的模块化形成对比）
- **协议层**：VS Code 平台 RPC + 自有协议层（多内部服务）
- **状态管理**：平台 state + 自研 PlanService/PlanManager
- **多模型**：自有后端 + 多模型支持
- **代码理解**：tree-sitter（多语言）
- **AI 模块化粒度**：单一 bundle（vs IDE-B 的多独立 extension）

---

## 三、独有设计（该形态的创新）

### ★★★★★ Multi-Agent × Multi-Model 路由

多个 agent 各配不同模型——补全用小模型（快/省），主推理用大模型（强）。配置驱动路由。

**借鉴价值**：不同任务用不同模型，平衡成本与质量。

### ★★★★★ Variables @ 触发系统

UI 级 context 注入——用 `@` 触发多种 context（文件/选区/符号/终端等），parser + resolver 解析。

**借鉴价值**：比纯 prompt 注入更结构化的 context 传递。

### ★★★★ 大量 feature 开关（一份代码多形态）

数十个 feature 开关让同一份代码支持 SaaS / 企业版 / 私有化部署——通过开关切换功能集。

**借鉴价值**：ToB 产品的"一码多态"策略，避免维护多分支。

### ★★★★ 自有协议层

自有协议层（多内部服务），补充平台 RPC 的不足。

### ★★★★ Rule 系统（多管理器）

多 Rule 管理器管理不同类型的规则（rules.show/manage 等）。

### ★★★ fileDiffHistory + checkpoint

Agent 自有版本管理（fileDiffHistory + checkpoint），不依赖 git。

### ★★★ 光标位置预取（与 IDE-B 共享）

零延迟预测——根据光标位置预取上下文。

### ★★★ agentProcessPool 多进程（与 IDE-B 共享）

多进程 agent 池，提升并发。

---

## 四、反模式（该形态的教训）

- ❌ **单文件巨型 bundle**（单一 extension 过大）—— 调试困难，应保持模块小
- ❌ **过度抽象**（数千个 service）—— 能函数化就函数化
- ❌ **大量扁平 feature 开关**（数十个不分组）—— 应按功能域分组嵌套
- ❌ **V2 共存**（新旧版本同时存在）—— 替换不要共存
- ❌ **产品绑定的保留字命名**（agent/chat 等通用词占用）—— 避让
- ❌ **"假 agent"**（多个 agent 名但工具集相同）—— 真 agent 要有不同工具集

---

## 五、借鉴价值

做**企业/区域市场 AI IDE**时，借鉴此形态的：
- **Multi-Agent × Multi-Model 路由**（成本/质量平衡）
- **Variables @ 触发**（结构化 context）
- **大量 feature 开关**（一码多态）
- **光标位置预取**（零延迟）
- **fileDiffHistory**（Agent 自有版本）

---

## 下一步
- 看 IDE-B（全球专业路线）的模块化对比 → [`03-IDE-B.md`](./03-IDE-B.md)
- 看横向对比 → [`06-comparison.md`](./06-comparison.md)
