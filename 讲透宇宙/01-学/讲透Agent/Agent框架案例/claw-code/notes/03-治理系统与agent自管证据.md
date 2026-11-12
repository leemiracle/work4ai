# 03 · 治理系统与 agent 自管证据

> card_id: claw-code-03
> universe: Agent框架案例
> burke: 场景=一夜重写的仓库要活过五个月；主体=PARITY+质量门+.omx 回执；能动=爪子自证工作；行动=9-lane 并行+门验证+反 slop 规则；目的=无人值守下的可信演化；张力=agent 速度 vs 人类审查带宽；弧线=应急检查点 → 制度化 → 自我归档
> status: 已完成（2026-08-20，HEAD `08106b0`）
> refs: PARITY.md / docs/g0XX / .omx/ / progress.txt / .github/ 实测
> updated: 2026-08-20

## 1. PARITY.md：把"我们还差多少"做成一等公民

- 顶部即声明自己是**机器消费的文档**：`run_mock_parity_diff.py` 直接吃这份 markdown（PARITY.md:7）——文档=测试夹具。
- 2026-04-03 检查点（:10）：292 commits/9 crates/48,599 行/2,568 测试行/3 作者。
- **9-lane 并行合并表**（:42-52）：每条 lane 一个 feature commit + 一个 merge commit + 行级证据（如 Lane 4 TaskRegistry：`5ea138e`→`21a1e1d`，task_registry.rs +336 行）。lane 划分=bash 校验/CI 修复/文件工具/TaskRegistry/任务接线/Team+Cron/MCP 生命周期/LSP 客户端/权限执行——**"按子系统切并行道，每道独立验证合并"**，这是多人（多 agent）并行开发 harness 的可复制模板。
- 诚实条款（:156-161）：`AskUserQuestion 仍是 pending payload`、`RemoteTrigger 仍是 stub`、`Team/Cron 无真调度器`——**"仍受限"清单与"已完成"清单同权重**。
- 反隐藏测试：`grep rust/**/*.rs 无 #[ignore]`（:171）——不许用注解把失败测试藏起来。

## 2. Mock parity harness：确定性对拍

- `mock-anthropic-service` crate：本地确定性 `/v1/messages`，用 `SCENARIO_PREFIX` 前缀路由剧本（mock_parity_harness.rs:10,339）。
- 12 个剧本场景（PARITY:11）：streaming_text / read_file_roundtrip / grep_chunk_assembly / write_file_allowed / **write_file_denied** / multi_tool_turn_roundtrip / bash_stdout_roundtrip / **bash_permission_prompt_approved/denied** / plugin_tool_roundtrip / auto_compact_triggered / token_cost_reporting——**权限的正反两面和压缩触发都是一等测试场景**，21 个捕获请求留档。
- `mock_parity_scenarios.json`：场景→PARITY 条目的映射清单（canonical scenario map）。
- 方法论：**parity 不是"像不像"，而是"同一剧本下行为逐条对拍"**——魔都水滴说的"审计先衡量覆盖，而不是先假定等价"。

## 3. g002-g013：质量门验证地图（docs/）

每个门一份 verification map + 验收产物（文件名即纪律）：

| 门 | 主题 | 伴随产物 |
|---|---|---|
| g002 | 安全验证 | g002-security-verification-map.md |
| g003 | 启动与会话 | g003-boot-session-verification-map.md |
| g004 | 事件/报告合同 | g004-events-reports-contract.md + runtime/g004_conformance.rs（399 行**门测试直接进源码树**） |
| g005 | 分支恢复 | g005-branch-recovery-verification-map.md（对应 branch_lock.rs 144 行） |
| g006 | 任务/策略看板 | g006-task-policy-board-verification-map.md |
| g007 | MCP 生命周期 | 双份（mapping + verification）+ mcp_lifecycle_hardened.rs 843 行 |
| g009 | Windows 文档与发布 | `.omx/ultragoal/quality-gate-G009-*.json` |
| g010 | 会话卫生 + **克隆歧义消除** | quality-gate JSON + g010-clone-disambiguation-metadata.md（对付满天飞的克隆仓） |
| g011 | ACP JSON-RPC 状态合同 + 生态运维 UX | g011-acp-json-rpc-status-contract.md |
| g012 | 最终发布就绪报告 | g012-final-release-readiness-report.md + pr-triage JSON |
| g013 | roadmap 精准点 #693-695 | g013-roadmap-pinpoints-693-695-verification-map.md |

> 注意 g004/g007/g010 的模式：**合同文档（contract）+ 验证地图（verification map）+ 源码树内的 conformance 测试** 三件套——合同不是文档，是可执行断言。

## 4. `.omx/`：Ralph 循环的执行回执（agent 自管的实锤）

- `.omx/ultragoal/`：goals.json + **ledger.jsonl**（流水账）+ 每个质量门的状态机文件（`.active.json` → `.complete.json`）+ leader-verify 与 rerun 日志。G010 的 active 文件有两个时间戳版本（20260515T020857Z/020953Z）——**失败重跑的痕迹都留着**。
- `.omx/cc2/`：board.json/board.md + issue-parity-intake（issue 对账）+ 两个校验脚本——看板即数据。
- `progress.txt` 开头就是 "**Ralph Iteration Summary - claw-code Roadmap Implementation**"：Iteration 1 (2026-04-16) 逐 US（用户故事）汇报——US-001 worker_boot 启动失败 6 变体分类、US-002 lane_events 事件 schema（EventProvenance 5 标签/序号去重/终态判定）、US-005 task_packet 类型化（TaskScope 枚举）——**每个 US 带文件名和测试数**。
- `.port_sessions/`：4 个会话 JSON（32 hex 命名）——移植会话的原始轨迹。
- 这就是 SOTA Sync 报道的 `$ralph` 持续执行循环落在仓库里的形态：**目标文件 + 流水账 + 门回执 + 重跑日志**。对照 openclaw 的 42 挂点：claw-code 把"agent 干活的证据"从 hook 事件升级成了**仓库内持久化档案**。

## 5. 反 slop 与自我约束（AGENTS.md ANTI-PATTERNS 实测）

- **直推 main 被策略封死**（`main_push_forbidden` 审批域）。
- **自动化 lane 禁止合并/关闭远端 PR 与 issue**（docs/anti-slop-triage.md）——防 agent 用"关闭问题"伪造完成度。
- **文档信源 CI**（.github/scripts/check_doc_source_of_truth.py）：旧组织链接（instructkr/code-yeongyu 时代的 URL）、旧 Discord、旧图片名一律禁止——**防止克隆仓与转世仓污染信源**（g010 的克隆歧义消除配套）。
- `claw init` 禁止脚手架出 `dontAsk` 权限模式，回归钉死在 output_format_contract.rs 测试里——**把安全回归变成可执行断言**。
- crates.io 反坑：`cargo install claw-code` 装的是弃用 stub（README.md:115-121 上加粗警告）——**包名被抢注后的自我隔离**。
- dogfood 合同：scripts/dogfood-build.sh 注入 GIT_SHA，`claw version` 的 provenance 必须等于 HEAD——**构建产物自证来源**。

## 6. 治理谱系定位

| 治理层 | openclaw | dsh | claw-code |
|---|---|---|---|
| 完成度对拍 | — | lint→单测→训练冒烟金字塔 | **PARITY.md + mock 对拍 harness**（12 场景） |
| 质量门 | PRISM 安全插件（外部） | harness 五带 | **g002-g013 内置门 + conformance 进源码树** |
| agent 自证 | 轨迹 schema 校验 | 训练冒烟 | **.omx 目标/流水账/门回执全进仓** |
| 反退化 | 四档权限+pairing | 供应链信任平面 | **push 封禁+反 slop+doc 信源 CI+回归钉** |

📌 下一步：04 篇看 Python 镜像层与三产品线——重写方法学与"重 CLI/轻 agent/旁路服务"的分层。
