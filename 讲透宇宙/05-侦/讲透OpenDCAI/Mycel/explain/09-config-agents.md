# 09 · 配置体系与内置 agent

## 角色定位

config/ 是 LeonAgent 的"基因层"：16 个文件分三条线——**runtime 行为**（loader.py + defaults/runtime.json + schema.py 的 LeonSettings）、**模型身份**（models_loader.py + defaults/models.json + models_schema.py 的 ModelsConfig）、**agent 定义**（defaults/agents/*.md 的提示词 + agent_config_resolver.py 的运行时配置归一）。设计哲学一句话：**系统默认 + 显式覆盖，两层，没有第三层**——源码守护测试明确禁止从用户 home 目录偷读配置（见 11 篇）。另有一份 observation.json 与 schema 管观察者配置。

## 内部结构

**runtime 线**：`AgentLoader.load`（loader.py:37-50）四步流水：读 `defaults/runtime.json` → `_deep_merge` 合 CLI 覆盖 → `_expand_env_vars` 展开 `${VAR}`/`~` → **`_remove_none_values` 递归剔 null**（loader.py:178-184）。最后一步是精髓：覆盖层里显式写的 `"temperature": null` 会被整键剔除，让 Pydantic 的字段默认值生效——null 是"我没意见"而不是"我要清空"。`_deep_merge` 同样对 None 跳过（loader.py:154-155），双保险。`_reject_removed_runtime_key("skills")`（:40，:162-166）把已废弃的顶层 skills 键变成硬错误，逼配置走 AgentConfig。schema.py 的 RuntimeConfig 全系 `extra="forbid"`，拼错键直接炸——宁拒不错。

**模型线**：`ModelsLoader.load`（models_loader.py:29-46）合并策略四分法（docstring :3-8）：providers/mapping 深合并、pool 后者胜、**catalog 与 virtual_models 系统独占不被覆盖**（:40-41 强制回填）。defaults/models.json 定义四档虚拟模型：`leon:mini`（快速响应）→ `leon:medium`（日常）→ `leon:large`（困难）→ `leon:max`（temperature 0.0 极限性能），四档默认全部解析到 gpt-5.5/openai；catalog 另备 claude-sonnet-4-5-20250929 / claude-opus-4-6 / claude-haiku-4-5 等。`DEFAULT_MODEL = "gpt-5.5"`（schema.py:17）是全仓唯一真源。模型名归一化（去日期后缀等）在 monitor 侧 cost.py:240-251（见 07 篇）。

**agent 线**：`parse_agent_file`（loader.py:72-116）解析 **Markdown+YAML frontmatter**：`---` 分割，frontmatter 出 name/description/tools/model，正文即 system_prompt；tools 缺省 `["*"]`。实际四内置 agent（defaults/agents/）：
- `general.md` — 全能分身，**唯一 tools: ["*"]**，继承全部工具，接多步复杂任务；
- `bash.md` — tools 仅 [Bash]，命令行专家，"不能直接读写文件，只能通过命令"；
- `explore.md` — tools [Read/Grep/Glob/list_dir]，只读探索，"专注回答问题，不要过度探索"；
- `plan.md` — 规划角色。

运行时还有 `resolve_agent_config`（agent_config_resolver.py:7-48）：把 AgentConfig 的 skills 逐个经 skill_repo 解析成 ResolvedSkill（校验 package 归属、解析 skill.md 文档、重名抛 ValueError），MCP servers 按 enabled 过滤去重——产出 ResolvedAgentConfig 才是 LeonAgent 允许消费的形态（边界由测试钉死）。

## 外部连接

**命名双轨是这个仓的身份特征**：类名与环境变量仍留 leon 前缀——`LeonSettings`（schema.py）、`LeonAgent`（core/runtime/agent.py:515 起 AgentLoader 注入）、`LEON_POSTGRES_URL`（backend/web/core/lifespan.py:24 硬必需）、`LEON_BACKEND_PORT`（backend/web/main.py:12）；而产品部署层已经换 Mycel——`MYCEL_RUNTIME_PROFILE`、`MYCEL_BIND_HOST/MYCEL_PORT/MYCEL_PUBLIC_URL`（deploy/cli-minimal/compose.yml:54-63）。两套前缀并存且各有职责（LEON_=进程内运行时，MYCEL_=部署编排），新人极易混淆。.env.example 是 LEON_* 的消费清单（OPENAI_API_KEY/四家搜索 key/Supabase 五件套/LEON_LOCAL_WORKSPACE_ROOT）。

## 数据流

启动：backend 装配 → `load_config(cli_overrides)` 出 LeonSettings → ModelsLoader 出 ModelsConfig → `load_runtime_agents()`（loader.py:54-61）扫 defaults/agents/*.md 得四 agent → LeonAgent 构造时按 settings.tools.web 的 key 有无装配 WebService 等。用户创建的自定义 agent 走 DB 里的 AgentConfig → resolve_agent_config → ResolvedAgentConfig 注入。运行中切模型走 MonitorMiddleware.update_model 的 based_on 归一（07 篇）。

## 设计决策（含批判）

- **null 剔除策略**（loader.py:178-184）：解决"JSON 配置里删不掉的 null 会把 Pydantic 默认打成 None"的经典坑，代价是用户永远无法用配置显式表达"此值为空"——对 temperature 这类 Optional 字段恰好够用。
- **catalog 系统独占**：防止用户配置覆盖模型目录造成展示与计价脱节，但用户加自托管模型只能进 providers/pool，灵活性受限。
- **幽灵文档（重磅勘误）**：`config/defaults/README.md` 描述了一整套**不存在的文件**——:10-13 的 `agents/{default,coder,researcher,tester}.json`、:14 的 `model_mapping.json` 全不存在（实际是 4 个 .md + models.json）；:66-71 的六个虚拟名 `leon:fast/balanced/powerful/coding/research/creative` 与 models.json 实际四名 `mini/medium/large/max` 完全脱节；:99 的 `mycel --agent coder` 与 :106 的 `load_config(agent="researcher")` 都是死签名（load_config 只收 cli_overrides dict）。这份 README 描述的是一个"计划中"的配置系统，照它配置必然失败。
- **md 而非 json 定义 agent**：提示词即文档，frontmatter 极简，好编辑好 review；代价是无 schema 校验（frontmatter 写错字段静默忽略）。

## 新人提示

1. 查配置真实默认值只看 `config/defaults/*.json` 与 schema.py，**config/defaults/README.md 当小说看**，与实码冲突时以 JSON 为准。
2. 想加内置 agent：在 defaults/agents/ 放 md，frontmatter 必须有 name；tools 写 `["*"]` 或显式清单；重启即被 load_runtime_agents 捡到。
3. 环境变量先想前缀：部署行为查 MYCEL_*，进程行为查 LEON_*；两套都有的语义（如端口）见 10 篇的优先级坑。
4. 写覆盖配置时 null=删除该键意图、省略=继承默认，这个心智模型与直觉相反，改 runtime.json 前先想清楚。
