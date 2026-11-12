# aeon-agent 深读卡 —— 把 GitHub Actions 当运行时、git 仓库当数据库的零基础设施自主 Agent 框架

> **定位**：AEON 是一个跑在 GitHub Actions 上的 unattended 自主 agent 框架——没有服务器、没有数据库，仓库本身既是代码也是状态。它用 90+ 个 Markdown 定义的 Skills 执行循环任务（深度研究/市场监控/PR review/安全扫描），自己给自己的输出打分（skill-evals），失败时自我修复（skill-repair）。核心张力在于：沙箱 runner 无网络无持久化，于是用 Prefetch/Post-process 双脚本绕过限制、用 git commit 实现"flat-file 记忆"。

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 调度层 | cron 匹配、消息轮询、dispatch | `messages.yml`、`cron_match()`、`cron-state.json` |
| 执行层 | skill 运行时与编排 | `.github/workflows/aeon.yml`、`claude-code` CLI、`chain-runner.yml` |
| 技能层 | 90+ 模块化能力（Research/Dev/Crypto/Social/Meta 五类） | `skills/{slug}/SKILL.md`（frontmatter+var）、`skills.json`、`.outputs/` |
| 身份层 | 人格与全局治理 | `soul/SOUL.md`、`soul/STYLE.md`、`CLAUDE.md` |
| 记忆层 | flat-file 持久化数据库 | `memory/{MEMORY.md, topics/, logs/, issues/}` |
| 自愈层 | 健康监控→评分→修复闭环 | `heartbeat`、`skill-health`、`skill-evals`、`skill-repair`、`reflect` |
| 集成层 | 人机与 Agent 间接口 | `dashboard/`（Next.js :5555）、`mcp-server/`、`a2a-server/`（JSON-RPC+SSE） |
| 通知层 | 出站分发（沙箱外） | `./notify`、`scripts/postprocess-*.sh`、`.pending-notify/` |
| 供应链安全 | skill 安装审计与漂移检测 | `add-skill`、`skills.lock`、`skill-security-scan`、`skill-update-check` |

## 二、核心机制

1. **Prefetch / Post-process 双脚本绕沙箱**：Claude 沙箱内无网络，运行前由 `scripts/prefetch-*.sh`（如 `prefetch-xai.sh` → `.xai-cache/`）在沙箱外取数缓存；skill 执行中只写 `.pending-notify/` 待定 payload，运行后由 `postprocess-*.sh`（Telegram/Discord/Slack/Farcaster/Dev.to）真正外发并 commit & push——即 Deferred Execution 模式。〔来源：Overview、Core Concepts；详见子页 5/7/33〕
2. **SKILL.md 两阶段模式 + var 注入**：每个 skill 是 frontmatter（name/description/schedule/var）+ 正文的 Markdown 提示词，内部强制 **RESOLVE**（预检/收集）→ **EXECUTE**（执行）两段式；运行时参数经 `aeon.yml` 以 `${var}` 注入聚焦行为。〔来源：Core Concepts、Glossary；详见子页 9〕
3. **Exit Taxonomy 支撑自愈闭环**：六类标准退出码（`*_OK` / `SKIP_UNCHANGED` / `SKIP_QUIET` / `NEW_INFO` / `*_ERROR` / `*_PARTIAL`）让 `skill-analytics` 与 `heartbeat` 区分"正确的沉默"与"失败"；`heartbeat` 读 `cron-state.json` 分级 P0(DEGRADED)/P1-P3(WATCH)，异常进入 `memory/issues/`（ISS-NNN），由 `skill-repair` 自动补丁。〔来源：Core Concepts、Glossary；详见子页 15/17/21〕
4. **Chains 链式编排**：上游 skill 输出落 `.outputs/{skill}.md`，下游经 `consume:` 关键字注入上下文，由 `chain-runner.yml` 串行/并行执行——无 LangGraph，纯文件传递。〔来源：Core Concepts；详见子页 6〕

## 三、与讲透系列的对位

| aeon 机制 | 讲透/技能系列对位 |
|---|---|
| SKILL.md 两阶段（RESOLVE→EXECUTE） | prompt-engineering：结构化 system prompt + CoT 分段 |
| Chains + `.outputs/` 文件传递 | agent-development：多智能体协作（对照 LangGraph 的 graph 状态传递） |
| Flat-file memory（MEMORY.md/topics/logs） | agent-development：记忆机制（长期/短期记忆的极简文件版实现） |
| Soul 身份层（SOUL/STYLE.md） | prompt-engineering：人格化 system prompt 与风格校准 |
| MCP Server / A2A Gateway | agent-development：工具调用与 MCP 协议、A2A 协议的一手实现样本 |
| skill-evals + Exit Taxonomy | ml-experiment：Agent 评测与可观测性设计 |
| GitHub Actions cron 调度 + 自愈 | 无现成对位 → "讲透 Agent 运维/自主性"的绝佳案例素材 |

## 四、关键入口

```text
README.md / CLAUDE.md          # 全局治理与上手
aeon.yml                       # 唯一配置：skill 开关/cron/chains
.github/workflows/
  ├─ messages.yml              # Scheduler：cron_match + 消息轮询
  ├─ aeon.yml                  # Execution Engine：单 skill 运行时
  └─ chain-runner.yml          # Chain 编排执行器
skills/{slug}/SKILL.md         # skill 本体（frontmatter + RESOLVE/EXECUTE）
skills.json                    # 注册表（generate-skills-json 编译产物）
soul/SOUL.md + STYLE.md        # 身份层
memory/                        # flat-file 数据库（MEMORY.md/cron-state.json/...）
scripts/prefetch-*.sh          # 沙箱外预取
scripts/postprocess-*.sh       # 沙箱外通知分发 + commit
dashboard/  mcp-server/  a2a-server/   # 三种集成接口
add-skill  onboard  export-skill       # CLI 生命周期工具
```

## 五、深读子页地图（37 页精选 6）

| 子页 | full.md 行 | 为什么值得读 |
|---|---|---|
| 3 · Core Concepts & Terminology | L300 | 五大概念 + Exit Taxonomy 表，10 分钟建立全套词汇 |
| 5 · GitHub Actions Workflows | L570 | 三个 workflow 的触发/生命周期/冲突解决 commit loop + 沙箱约束 |
| 9 · Skill Definition & Lifecycle | L1146 | SKILL.md 解剖、skills.json 编译、skills.lock 供应链钉扎 |
| 17 · Skill Evals, Analytics & Repair | L2389 | 自愈闭环全貌：评分→异常检测→自动补丁→prefetch 模式 |
| 27 · A2A Gateway | L4014 | Agent-to-Agent JSON-RPC/SSE，含 LangChain/CrewAI/AutoGen 客户端示例 |
| 28 · Soul & Identity Layer | L4190 | 身份注入数据流，跨 Fleet 保持人格一致性 |

## 六、与"我们"的关系（一句话）

对讲透 Agent 教程而言，aeon 是"不用任何框架的自主 Agent"最佳反面参照——它证明了 runtime（Actions）+ prompt（SKILL.md）+ git（memory）三件套即可搭出自愈型多 skill Agent，正好用来对照 LangChain/LangGraph 路线讲清"框架到底替你做了什么"。

---
生成：2026-08-21 · deepwiki 37 页全归档
