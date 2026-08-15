# Agent 框架案例 · 索引

> 一句话定位：**Agent 的"骨架"——harness 层（进程/循环/工具/沙箱/审批）的开源实现源码级解剖。**
>
> 与 [`Agent上下文案例/`](../Agent上下文案例/)（上下文层：单次任务内给模型看什么代码）、[`Agent记忆系统案例/`](../Agent记忆系统案例/)（记忆层：跨会话知识）平行，本目录是**框架层**：agent 进程怎么跑起来、能力怎么接缝、信任平面怎么设计。
>
> 🌐 **生态观测锚点（2026-08-15）**：[`../透视GitHub-Harness高星仓库全景.md`](../透视GitHub-Harness高星仓库全景.md)——topic:harness 高星 37 仓快照与概念卡（五子系统/四层栈），本目录 dsh 案例是其中一个实现样本；方法蒸馏见 [`../harness精华笔记.md`](../harness精华笔记.md)。同日新增组织级纵深：[`../透视GitHub-DeepSeek开源全景.md`](../透视GitHub-DeepSeek开源全景.md) §3 洞察⑦ + [`../讲透DeepSeek/`](../讲透DeepSeek/README.md)（dsh 双头下注分析的最新增量底稿 G）。

| 案例库 | 内容 | 状态 |
|---|---|---|
| **deepseek-harness插件化框架/** | DeepSeek 官方开源 agent harness（dsh，219 插件包）源码级深读：核心运行时（turn/step 状态机、事件日志）/ 能力接缝 + 插件机制全景 / 信任平面（沙箱、审批、供应链）/ 装配与外部接口 / DeepWiki 对照增补 / dsh-plugin 生态分析（star>66 共 59 仓），12 篇笔记全部行号钉版（HEAD `47f943859b`，2026-08-13） | 已完成 |

## 速查：什么问题查哪里

- **harness 整体架构 / "一切皆插件"** → `deepseek-harness插件化框架/notes/00-overview/`
- **插件机制与能力接缝** → `notes/02-capability-seams/`
- **沙箱/审批/供应链安全** → `notes/03-trust/`
- **插件生态格局** → `notes/07-ecosystem/`
- **配套反欺骗实验** → [`../欺骗动力学-AI纪实验包.md`](../欺骗动力学-AI纪实验包.md)
