# opencode 合入手册：编排精化技能使用说明（2026-08-15）

> 本文是 [01 全景](./01-编排全景-25仓速览.md) → [02 OmO 精读](./02-oh-my-openagent精读.md) / [03 wshobson 精读](./03-wshobson-agents市场精读.md) 的落地层：**从 >10K 编排仓提取的精化部分已合入本机 opencode，本文是使用说明**；§4 给出可选的整装安装路径。

## 1. 已合入什么：3 个原生技能

位置：`~/.config/opencode/skills/orchestration-*/SKILL.md`（全局技能，对所有项目生效）。**零第三方依赖、零遥测、纯 Markdown 协议**——蒸馏自开源编排仓的机制层，不是安装它们本身。

| 技能 | 触发方式 | 蒸馏自 | 干什么 |
|---|---|---|---|
| `orchestration-ultrawork` | 说 "ultrawork" / "ulw" / "任务做完为止" / "不要停" | OmO 的 ultrawork + /goal + Todo Enforcer + Ulw Loop | 目标落盘（`.opencode/goal.md`）→ 可验证完成判据 → 逐项证据执行 → **换敌意视角完成审计** → 未全绿自动续跑 |
| `orchestration-hyperplan` | 说 "hyperplan" / "敌意评审" / "攻击这个计划" / "审计划" | OmO hyperplan（5 hostile critics）+ wshobson orchestrators | 动码前五个正交批评者（完备性/边界/数据状态/安全故障/成本简化）各出 ≥1 条具体反对，全部裁决后才开工 |
| `orchestration-fleet` | 说 "并行 agent" / "fleet" / "同时调查这些" / "并行处理" | orca + paseo + superset + OmO Team Mode 共同骨架 | 先判并行性（尴尬并行才拆）→ DAG 分解 + 类别路由（quick/deep/visual/ultrabrain）→ 只读并行或 worktree 写隔离 → 汇合裁决（冲突必仲裁） |

三个技能互相咬合：**fleet 拆解 → hyperplan 审计划 → ultrawork 执行到完成**。

## 2. 使用示例（直接对 opencode 说）

```
ultrawork 把 recommendation-system/ 四个 py 里所有 print 调试语句清掉，ruff 全绿为准
hyperplan 我打算给 work4ai 加一个全局 links 检查 CI，计划是……（贴计划），攻击它
fleet 并行深读 Agent编排案例/01 里 G2 代的 7 个仓库 README，每仓一页笔记，互不依赖
```

## 3. 维护

- 改协议：直接编辑对应 `SKILL.md`；改完**重启 opencode** 生效（配置不热加载）。
- 想在单项目内定制（如不同的完成判据模板）：在项目 `.opencode/skills/` 下同名覆盖（项目级优先于全局）。
- 与现有技能的关系：与 `doubt-driven-development`（决策评审）、`planning-and-task-breakdown`（任务分解）方向相近但角色不同——本三件套专攻**多 agent 编排层**（纪律/敌意/并行），决策与拆解仍归原技能。

## 4. 可选：整装安装两个源头仓库

> 本项目默认**不装**（理由见 02/03 精读的"评价"节）；要用时按此操作。

### 4.1 oh-my-openagent Ultimate（opencode 插件，11 agents 全家桶）
```bash
bunx oh-my-openagent install          # TUI 引导：订阅探测/模型选择/各 provider 认证
```
- 官方建议让 LLM agent 代装（贴 installation.md 链接给 agent）📄。
- 关遥测：config 里 `"telemetry": false` 或环境变量 `OMO_DISABLE_POSTHOG=1`。
- 卸载：从 `~/.config/opencode/opencode.json` 的 `plugin` 数组移除条目。
- 注意：SUL-1.0 许可；与 opencode 版本耦合较紧，升级 opencode 后跑 `bunx oh-my-opencode doctor` 诊断。

### 4.2 wshobson/agents（94 插件市场，OpenCode 适配）
```bash
gh repo clone wshobson/agents ~/agents && cd ~/agents
make install-opencode                  # generate + symlink 到 .opencode/
```
- 按 3.1 的插件粒度**按需装单个**（如只装 python-development），不要全量。
- Windows 注意：`make`+symlink 路径未受官方覆盖，WSL 内执行更稳；或手工拷贝插件目录到项目 `.opencode/`。
- 质量门：装前可跑 `uv run plugin-eval score plugins/<name> --depth quick`。

### 4.3 其他 G3 舰队工具（orca/paseo/superset）
独立桌面/移动 App 形态，不是 opencode 插件；如需"手机遥控家里 agent 舰队"再评估，默认不装。

## 5. 溯源

- 精化输入：[01-编排全景](./01-编排全景-25仓速览.md)（25 仓 API 快照 2026-08-15）
- OmO 证据：[02 精读](./02-oh-my-openagent精读.md)（README 抓取 2026-08-15，dev 分支）
- wshobson 证据：[03 精读](./03-wshobson-agents市场精读.md)（README 抓取 2026-08-15，main 分支）
- 技能文件：`~/.config/opencode/skills/orchestration-ultrawork|hyperplan|fleet/SKILL.md`
