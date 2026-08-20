# OpenClaw 🦞 插件化个人 AI 助手 · 案例笔记

> 一句话定位：**2026 年现象级开源 agent——单操作者个人 AI 助手，"循环内核 + 协议中枢 + 插件宿主"三层 harness，跑在你自己的设备上、出现在你已有的聊天频道里。**
>
> 上游：https://github.com/openclaw/openclaw （MIT，前身 Clawdbot）
> 本地克隆：`~/ai/agent/awesome-agents/repos/openclaw`（经 gh-proxy 镜像）
> 笔记钉版 HEAD：`f612675284`（2026-08-20）
> 规模实测（2026-08-20）：**386,825 stars / 81,262 forks**（创建于 2025-11-24，9 个月冲顶）；20 天内 6,126 commits（日均 300+）；1.5GB / 33K 文件 / 937 TS 文件 / packages 22 包 + apps 7 端

## 为什么值得深读

1. **六组件的教科书实现**：agent-core 是零 I/O 纯循环库（E+C），常驻 Gateway daemon 掌管会话/审批/密钥（S+V），42 挂点插件系统（L）——比 dsh 更激进的"harness 即产品"。
2. **协议极简主义**：名为中枢的 gateway-protocol 依赖入度仅 2，真正的底座是无聊的 normalization-core（入度 16/23 实测）。
3. **把"模型不可靠"当一等工程问题**：专门一个 2900+ 行的 tool-call-repair 包修复"模型把工具调用写成纯文本"（含 Harmony 通道标记语法）。
4. **steering 优先于任务**：用户运行中插话会跳过整批未执行工具——人 > 任务完成度（agent-loop.ts:512-517 双重复查）。
5. **AGENTS.md 本身是顶级工程文化样本**：电报体 + Repair Doctrine + "production LOC 净≤0" 原则 + Codex hard gate。

## 阅读顺序

| # | 笔记 | 回答的问题 |
|---|---|---|
| 1 | [01-定位与全景](notes/01-定位与全景.md) | 它是什么、多大规模、九个月怎么长成的 |
| 2 | [02-六组件实证](notes/02-六组件实证.md) | E/T/C/S/L/V 逐件的 file:line 证据 |
| 3 | [03-协议中枢与插件面](notes/03-协议中枢与插件面.md) | gateway-protocol 为什么极简、42 挂点全表、插件契约 |
| 4 | [04-安全平面](notes/04-安全平面.md) | 四档权限/pairing 审批/net-policy fail-closed/与 PRISM 的关系 |
| 5 | [05-工程文化与可借鉴](notes/05-工程文化与可借鉴.md) | AGENTS.md 电报体、Repair Doctrine、可迁移决策清单 |

## 审计总命令

```bash
cd ~/ai/agent/awesome-agents/repos/openclaw
git log -1 --format=%h                      # 笔记钉版 f612675284（漂移则行号需重验）
git log --oneline --since=2026-08-01 | wc -l  # 活跃度（笔记实测 6126）
ls packages/                                # 22 核心包
grep -c "" packages/agent-core/src/agent-loop.ts   # 主循环规模
```

## 项目内交叉引用

- **PRISM 安全层**：OpenClaw 的零 Fork 运行时安全插件（arXiv:2603.11853，10 hooks×5 阶段）——[harness工程手册 14 章带一](../../../工程化手册库/harness工程手册/14-生态工具带2026.md)
- 同为插件化 harness 的对照案例：[deepseek-harness插件化框架](../deepseek-harness插件化框架/README.md)（DeepSeek 官方 dsh，219 插件包）
- 手册理论底座：[harness工程手册](../../../工程化手册库/harness工程手册/README.md)（六组件/42 挂点对照 03 章 L 组件）
- 用例库横向谱系定位：见 [`用例库/README.md`](../../../用例库/README.md)——openclaw 不在 279 快照内（created 2025-11-24，晚于快照），作为现象级增量案例
