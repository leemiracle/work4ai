# 讲透 Claude Code（REA 逆向全链）

> 目标：用自研 REA 工具链**完美逆向** `/home/lwz/.nvm/versions/node/v22.23.2/bin/claude`
> （Claude Code **v2.1.261**，215MB Bun 单文件可执行），产出全方位文档 +
> RL/Agent 专题（含可运行的手搓简化版）。
> 日期：2026-10-16 · 方法：全程静态分析（Bun 解包 + REA 应用图谱 + 偏移考古）。

## 全链状态表

| 环节 | 状态 | 产物 |
|---|---|---|
| Bun 单文件解包（1,818 模块/57MB） | ✅ | `rea-claude/extracted/$bunfs/` |
| REA 应用图谱（38,619 节点/46,027 边） | ✅ | `app-graph/rea-graph-combined.json` |
| 深报告（证据全量版） | 🔄 | `rea-claude/reports/`（01 ✅ 58KB；02-13 进行中） |
| 全方位文档 14 册（精编版） | 🔄 | 本目录（见下） |
| RL×Agent 专题 + mini-claude | ✅ | `rl-and-agents/`（405 行实测跑通） |

## 文档目录

| 册 | 标题 | 状态 |
|---|---|---|
| [00](00-逆向方法论.md) | 逆向方法论：Bun 解包 + REA 工作流 | ✅ |
| [01](01-总体架构.md) | 总体架构：发行形态/模块拓扑/分层图 | ✅ |
| [02](02-agent-loop.md) | Agent Loop：主循环/流式/工具调度/中断 | ✅ |
| [03](03-tools.md) | 工具系统：80 工具/schema/执行管线 | ✅ |
| [04](04-api-client.md) | API 客户端：端点/模型表/重试/caching | ✅ |
| [05](05-system-prompts.md) | 系统提示词：四身份/协调者全文/注入模板 | ✅ |
| [06](06-permissions.md) | 权限与沙箱：三态/六模式/三沙箱实现 | ✅ |
| [07](07-hooks.md) | Hooks：33 事件双体系与权限汇合 | ✅ |
| [08](08-mcp.md) | MCP：客户端/传输/工具发现/资源 | ✅ |
| [09](09-subagents.md) | 子代理与编排：注册表/隔离/通知回传 | ✅ |
| [10](10-context.md) | 上下文与持久化：transcript/checkpoint/组装管线 | ✅ |
| [11](11-skills-plugins.md) | Skills 与插件：三层披露/marketplace/eval | ✅ |
| [12](12-settings-配置体系.md) | 配置体系：settings/CLAUDE.md/环境变量 | ✅ |
| [13](13-telemetry.md) | 遥测与反馈：GrowthBook/数据飞轮/RL 三元组 | ✅ |
| [rl](rl-and-agents) | RL 形式化 + mini-claude v2（551 行：file-state/autocompact/遥测三元组，全实测） | ✅ |

深报告（58KB 级证据全量版，含协调者提示词 15,627 字符全文与符号表）在
`/usr-data/data2/aios/rea-claude/reports/`，本目录各册为其精编版。

## 三个"一页纸"结论

1. **核心极小、外围极大**：agent loop 概念上 ~60 行；215MB 里 99% 是 Bun 运行时、
   安全网、UI 与生态。mini-claude 405 行复刻了可干活的核心。
2. **上下文窗口是一等公民**：file-state 跟踪、autocompact、子代理隔离、工具延迟加载、
   WebFetch 小模型提炼——全部服务"窗口内信噪比"。
3. **防注入是系统性工程**：notification 声明 + 包裹转义 + 审批逐字引用 +
   READ-ONLY worker 清单，提示词层到工具层的纵深防御。

## 复现入口

```bash
# 解包（自研 Bun standalone 解析器，见 00 册）
ls /usr-data/data2/aios/rea-claude/extracted/$bunfs/root/   # 1,818 模块
# REA 图谱（v6.5.0，morluto/rea）
cat /data/usershare/ai/work4ai/讲透REA/deepwiki/INDEX.md     # REA 工具链文档
# 手搓简化版
python3 rl-and-agents/mini_claude.py -p "任务"
```
