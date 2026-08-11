# 实战案例 · Open-AutoGLM 手机 Agent

> **讲透Agent 系列的实战补充**：把 [讲透Agent](../) 的理论（ReAct、工具调用、规划、记忆）落到一个真实的生产级手机 GUI Agent 项目上。
> 本案例与 [讲透Agent/00-为什么需要Agent.md](../00-为什么需要Agent.md) ~ [04-记忆机制.md](../04-记忆机制.md) 互补：那些章节讲 **怎么做**，本案例讲 **真做了什么样**。

---

## 这是什么

[Open-AutoGLM](https://github.com/zai-org/Open-AutoGLM) 是智谱 AI 开源的手机 GUI Agent 框架，基于 AutoGLM-Phone-9B 视觉语言模型，跨 **Android（ADB）/ HarmonyOS（HDC）/ iOS（WDA）** 三平台，用自然语言控制手机完成自动化任务。

**与讲透Agent 系列的映射**：

| 讲透Agent 章节 | Open-AutoGLM 中的对应实现 |
|---------------|------------------------|
| [00-为什么需要Agent](../00-为什么需要Agent.md) | 项目 README 的"项目介绍"段——用 VLM + 规划解决手机 GUI 自动化问题 |
| [01-经典Agent范式对比](../01-经典Agent范式对比.md) | 采用 **感知-动作循环**（非 ReAct/Plan-and-Execute），见 `concept:perception-action-loop` |
| [02-工具调用工程](../02-工具调用工程.md) | **14 种 handler**（Tap/Swipe/Type/...）+ AST 安全解析（不用 eval）。但用 **函数调用风格字符串协议**（非 OpenAI tool_call）|
| [03-规划与搜索](../03-规划与搜索.md) | **规划完全交给 VLM**——框架不做规划，每步截图 → 模型直接输出动作 |
| [04-记忆机制](../04-记忆机制.md) | **极简短期记忆**：上下文 `_context` 只保留最新截图（图片一次性消费策略，省 token 80%+）+ 历史 text。无长期记忆、无向量检索 |

**关键差异**：Open-AutoGLM 是个"瘦 Agent"——把智能完全压到模型侧（AutoGLM-Phone-9B 是专用 fine-tune 的 VLM），框架本身只做"截图→调模型→执行→循环"。

---

## 文件清单

| 文件 | 内容 | 来源 |
|------|------|------|
| [ONBOARDING.md](ONBOARDING.md) | 项目 onboarding 指南（480 行）：项目概览 + 12 架构层 + 4 关键概念 + 12 步学习 Tour + Complexity Hotspots | 2026-08-11 由 `/understand-onboard` 基于知识图谱自动生成 |
| [ONBOARDING-DETAILS.md](ONBOARDING-DETAILS.md) | 所有文件的深度 explain（1100+ 行）：73 个文件 × 5 维度（角色 / 内部结构 / 外部连接 / 数据流 / 模式与坑） | 2026-08-11 由 `/understand-explain` 生成，**已通过严格源码核查**（120 个行号引用，修正 1 处后 100% 准确）|
| [knowledge-graph.json](knowledge-graph.json) | 项目知识图谱（85KB）：83 节点（39 file + 12 class + 1 function + 7 config + 20 document + 4 concept）+ 127 边 + 12 层 + 12 tour | 2026-08-11 由 `/understand` 生成，可用 `/understand-dashboard` 可视化 |

---

## 怎么读

### 路径 A：理论先行（推荐）

1. 先读讲透Agent 系列 [00-为什么需要Agent](../00-为什么需要Agent.md) 建立 Agent 概念框架
2. 读 [ONBOARDING.md §1-3](ONBOARDING.md#1-project-overview项目概览) 看 Open-AutoGLM 怎么落地这些概念
3. 按需深入 [ONBOARDING-DETAILS.md](ONBOARDING-DETAILS.md) 的具体文件

### 路径 B：实战先行

1. 直接读 [ONBOARDING.md §7 快速开始](ONBOARDING.md) 跑通第一个任务
2. 按需求读 [ONBOARDING-DETAILS.md](ONBOARDING-DETAILS.md) 对应章节
3. 回到讲透Agent 系列补理论

### 路径 C：可视化

1. 用 `/understand-dashboard` 启动浏览器看 `knowledge-graph.json`
2. 按 12 个架构层浏览节点关系
3. 按 12 步 Tour 顺序学习

---

## 三层讲透适配

work4ai 主项目用「直觉 → 数学 → 代码跑通 → 不足 → 应用」三层宪法。本实战案例作为 **应用层补充**，与主系列的关系：

```
讲透Agent（理论层）
├── 直觉：为什么需要 Agent
├── 数学：ReAct/规划/记忆的形式化
├── 代码：experiments/ 下的玩具实现
├── 不足：玩具与生产的差距
└── 应用 ← 本实战案例位于此层
    ├── 真实生产项目：Open-AutoGLM（zai-org 开源）
    ├── 8300 行 Python / 41 文件 / 跨 3 平台
    ├── 真实工程权衡：图片一次性消费、AST 安全解析、双回调机制
    └── 真实 bug 清单：10 项已知问题（贡献机会）
```

**学完本案例你会理解**：
- 生产级 Agent 与教科书 Agent 的差距（错误处理 / 状态管理 / 多平台适配）
- 为什么"把智能压到模型侧"是合理选择（AutoGLM-Phone-9B 专用 fine-tune）
- GUI Agent 的独特挑战（截图 token 成本 / 坐标系 / 敏感页面 / 输入法）
- 工厂模式 + Protocol 抽象在多平台项目中的演进（与失败的抽象）

---

## 关键学习点（10 个）

读完后应能回答：

1. **协议设计**：为什么 AutoGLM 用 `do(action="Tap", element=[500,300])` 函数调用风格而非 JSON 或 tool_call？
2. **流式解析**：`ModelClient.request` 怎么在流式中实时区分 thinking/action 而不打断用户阅读？
3. **token 优化**：图片一次性消费策略怎么省 80%+ token？为什么是 `_context[-1] = remove_images_from_message(...)` 而非 delete？
4. **安全**：为什么 `parse_action` 用 `ast.parse + literal_eval` 而非 `eval`？模型输出 `__import__('os').system('rm -rf /')` 会怎样？
5. **多平台抽象**：为什么 iOS 不走 `DeviceFactory`？这种"架构债"何时该还？
6. **回调机制**：`confirmation_callback` 和 `takeover_callback` 怎么让一个终端 Agent 接入 Web UI / Slack？
7. **坐标系统**：相对坐标 `[0-1000]` → 像素 → iOS 逻辑 points 的三重转换如何工作？
8. **错误兜底**：模型异常和执行异常怎么都转成 `finish(message=...)` 而非崩溃？
9. **prompt 与实现的脱节**：prompt 要求 `<think>/<answer>` XML 但 parser 优先匹配裸 `do(...)`——这种"协议演进"如何无害过渡？
10. **生产测试**：没有 `tests/` 目录的项目怎么靠 system requirements 自检 + 部署验证脚本保证质量？

每个问题答案都在 [ONBOARDING-DETAILS.md](ONBOARDING-DETAILS.md) 中。

---

## 元信息

- **源项目**：[zai-org/Open-AutoGLM](https://github.com/zai-org/Open-AutoGLM)（commit `86f5538`，2026-08-11 检出）
- **生成工具**：[understand-anything](https://github.com/understand-anything/understand-anything) plugin（`/understand` → `/understand-onboard` → `/understand-explain`）
- **生成日期**：2026-08-11
- **质量保证**：所有行号引用对照源码核查（120 个，100% 准确）；文件覆盖完整性脚本核查（73 文件全覆盖）
- **理论锚点**：[讲透Agent](../) 系列 5 章
- **维护**：源项目代码变更后重跑 `/understand` → `/understand-onboard` 即可同步

---

## 与 work4ai 其他系列的关系

- **讲透基础模型 / 讲透Transformer**：AutoGLM-Phone-9B 基于 GLM-4.1V-9B-Thinking，本质是 Transformer + 视觉编码器
- **讲透Prompt**：`prompts_zh.py` 的 15 动作 + 18 条领域规则是 prompt engineering 的真实案例
- **讲透微调**：AutoGLM-Phone-9B 是 GLM-4.1V-9B 的专用 fine-tune
- **讲透GPU与系统级**：vLLM/SGLang 部署参数（`--mm_processor_kwargs {"max_pixels":5000000}`）是 VLM 推理优化的实战
- **讲透AI应用全景**：手机 GUI Agent 是 AI 应用的一个重要赛道（与 RAG/Coding Agent 并列）

---

## 下一步

- 想跑起来：见 [ONBOARDING.md §7 快速开始](ONBOARDING.md#7-快速开始5-分钟跑通)
- 想理解架构：按 [ONBOARDING.md §4 Guided Tour](ONBOARDING.md#4-guided-tour12-步学习路径) 12 步走
- 想做贡献：见 [ONBOARDING.md §6 已知代码质量问题](ONBOARDING.md#6-complexity-hotspots复杂度热点) 的 10 项易上手 issue
- 想做类似项目：参考 [ONBOARDING-DETAILS.md](ONBOARDING-DETAILS.md) 的"三平台平行实现"部分理解跨平台 GUI Agent 的代码组织
