# 11 · recipe 与 scheduler：把会话变成可复用可调度的自动化单元

> 依据 commit 390dfb8c 源码实证。核心文件：`crates/goose/src/recipe/`（8 文件，mod.rs 877 行）、`crates/goose/src/scheduler.rs`（1267 行）、`crates/goose/src/scheduler_trait.rs`（41 行）、`crates/goose-cli/src/commands/schedule.rs`（345 行）、`crates/goose-server/src/routes/schedule.rs`（HTTP 面）。
>
> 先钉三处与常见预期不符的源码事实：①调度器不是 `scheduler/` 目录，而是单文件 `scheduler.rs` + 抽象 `scheduler_trait.rs`；②**当前版本没有任何 notify/通知机制**——job 完成只有 tracing 日志与 posthog 遥测（scheduler.rs:276-281），全仓 grep "notify" 在调度链路零命中（"Notification" 均属 MCP 协议层）；③evals/open-model-gym 与 recipe 体系无关，其 README:145 的 "just install recipe" 是 justfile 术语。

## 一、角色定位：工作流的"可执行文件"与它的"cron 守护"

goose 的交互会话天然是一次性的：用户输入、agent 循环、会话落库，结束。要把这套能力变成可交付的资产，需要两个正交的抽象——

**recipe 是"会话的序列化格式"**：一个 YAML（或 JSON）文件，把"系统提示（instructions）、首条任务（prompt）、工具集（extensions）、模型偏好（settings）、入参契约（parameters）、子流程（sub_recipes）、重试策略（retry）、结构化输出（response）"打包成一个可分享、可版本管理的单元。它不是配置片段，而是完整的自定义 agent 定义——`Recipe` 结构体（recipe/mod.rs:42-87）的注释直说 instructions 是 "the instructions for the model"（:55）。

**scheduler 是"无人值守的执行引擎"**：基于 `tokio-cron-scheduler` 内嵌实现（scheduler.rs:12），按 cron 表达式周期性唤醒，把 recipe 变成一个完整 agent 会话跑完、落库、可审计。历史上 goose 曾用 Temporal 做外部调度服务，现已移除——CLI 的 services 命令只剩一条声明："The built-in scheduler runs within the goose process and requires no external services."（commands/schedule.rs:269-272）。

在 16 层架构中，recipe 模块与 scheduler 同属第 4 层「配置·安全·网关与提示词资产」（强依赖 `Config` 与 `Paths`）；但执行期的 scheduler 直插第 0 层——它调用 `Agent::new()`、`create_session`、`agent.reply()`（scheduler.rs:832-928），是 agent 引擎的完整消费者，相当于一个不睡觉的 headless 用户。

两者合起来构成 goose 的自动化面：**recipe 解决"做什么可复用"，scheduler 解决"什么时候自动做"**。桌面端的「Scheduled Runs」功能（ui/desktop）就是走 goose-server 的 `/schedule/*` HTTP 路由（routes/schedule.rs:547 起）操作这套引擎。

## 二、内部结构：recipe 格式与调度任务模型

### 2.1 Recipe 数据模型（recipe/mod.rs）

`Recipe` 结构体的字段全景（mod.rs:42-87）：

| 字段 | 行号 | 语义 |
|---|---|---|
| `version` | :45-46 | 文件格式版本，默认 "1.0.0"（:28-30） |
| `title` / `description` | :48-50 | 必填，元信息 |
| `instructions` | :54-55 | Optional——给模型的系统级指令 |
| `prompt` | :57-58 | Optional——会话首条用户消息 |
| `extensions` | :60-65 | 工具扩展列表，自定义反序列化（见 2.3） |
| `settings` | :67-68 | provider/model/temperature/max_turns（:99-111） |
| `parameters` | :76-77 | 入参契约（见 2.2） |
| `sub_recipes` | :82-83 | 子流程引用（:119-129） |
| `retry` | :85-86 | 复用 agents 的 `RetryConfig`（types.rs:22-36） |
| `response` | :79-80 | JSON schema 约束输出（:113-117） |

两条硬约束由 builder 校验：title/description 必填，且 "At least one of 'prompt' or 'instructions' is required"（mod.rs:411-416）——validate_recipe.rs:69-88 在文件加载路径上再拦一次。

**格式兼容层**：`Recipe::from_content`（mod.rs:323-341）先按 YAML 解析，若顶层存在 `recipe:` 键则取其嵌套对象反序列化（:326-328）。这兼容了 GitHub 时代「name/recipe/isGlobal 包裹」的旧分享格式（测试 :729-756 实证）——注意这不是 Jekyll 式 frontmatter，而是**可选的嵌套 YAML 键**；顶层平铺是主流写法。文件扩展名同时接受 yaml 与 json（`RECIPE_FILE_EXTENSIONS`，mod.rs:26），因为 serde_yaml 的超集解析器能直接吃 JSON 语法（测试 :441-539 用 JSON 字符串走同一条 from_content）。

反序列化后还有两个自动修补：老 recipe 带内置 `developer` 扩展但缺 `analyze` 时自动补上（`ensure_analyze_for_developer`，mod.rs:230-253）；声明了 `sub_recipes` 的 recipe 自动注入 `summon` 平台扩展（`ensure_summon_for_subrecipes`，mod.rs:255-271）——没有 summon 就没有工具能拉起子流程。

### 2.2 参数系统：模板变量与入参契约的双向对账

recipe 正文是 **minijinja 模板**，`{{ param }}` 占位。参数契约 `RecipeParameter`（mod.rs:197-207）用两个枚举描述每个占位符：`input_type`（String/Number/Boolean/Date/**File**/Select，:176-185）与 `requirement`（Required/Optional/**UserPrompt**，:158-162）。File 类型的文档注释点明安全设计："Cannot have default values to prevent importing sensitive user files"（:181-183）。

渲染管线（template_recipe.rs + build_recipe/mod.rs）做了三层防御：

1. **渲染前清洗**：空双引号 `: ""` 替换为 `: ''`，防止 minijinja 转义破坏 YAML（:96-99）；非合法变量名（如 `{{hf model org}}` 含空格）且 minijinja 无法解析的，自动包 `{% raw %}` 原样保留（preprocess_template_variables，:15-20 与 :31-38）——这让模板里可以安全出现任意花括号文本。
2. **严格模式渲染**：正式渲染用 `UndefinedBehavior::Strict`（:108），缺参直接报错，杜绝静默空串。内建参数 `recipe_dir`（mod.rs:25）自动注入为 recipe 所在目录，并注册模板 loader 支持 `{% include %}`/`{% extends %}` 相对路径引用（:125-138）。
3. **参数对账**：`validate_parameters_in_template`（validate_recipe.rs:90-115）把模板里提取的未声明变量（undeclared variables，:150-158）与 parameters 声明做**双向差集**——模板用了没声明的是 missing，声明了没用到的是 extra，两者都报错。

参数取值三级瀑布在 `apply_values_to_parameters`（build_recipe/mod.rs:94-116）：命令行显式值 > `default` > UserPrompt 交互回调（:97-104）；仍无值则进 missing 列表，`build_recipe_from_template` 以 `RecipeError::MissingParams` 终止（:60-64）。File 类型值在此时读文件内容注入（:108-111，实现在 read_recipe_file_content.rs 的 `read_parameter_file_content`）。

### 2.3 extensions 的适配器

recipe 里的 extensions 走独立反序列化 `deserialize_recipe_extensions`（mod.rs:60-65 挂钩，recipe_extension_adapter.rs:165-173）：内部枚举 `RecipeExtensionConfigInternal`（:8-95）支持 stdio/builtin/platform/streamable_http/frontend/**inline_python** 六型，差异点是 recipe 里 `description` 可为 null/缺省，适配器统一兜成空串（From 实现 :115-163，测试 :228-259 实证 null→""）。inline_python 意味着 recipe 可以自带一段 Python 代码作为 MCP 工具（字段 code/dependencies，:83-94）——工作流分发的终极形态。

### 2.4 ScheduledJob 与 Scheduler（scheduler.rs）

`ScheduledJob`（:105-126）是调度的持久化单元：id、source（recipe 文件路径）、cron、last_run、currently_running、paused、current_session_id、process_start_time、parameters，以及最微妙的 `recipe_base_dir`——源码注释（:121-125）解释：recipe 被 copy 进调度器内部目录后，**相对路径（sub-recipes、模板 include）仍按原目录解析**，防止复制后引用断裂。

`Scheduler` 结构（:142-148）四个组件：tokio 内嵌调度器、jobs 内存表（`Arc<Mutex<HashMap>>`）、磁盘存储路径、running_tasks 取消令牌表。全部状态变更后调用 `persist_jobs` 全量重写 schedule.json（:128-140）——文件即真相源。

**cron 语义**：接受 5 或 6 字段表达式。5 字段（分 时 日 月 周）自动前缀 "0 " 转成 6 字段并打 warn（:186-195）；字段数不等于 5/6 则 `CronParseError`（:197-203）。6 字段格式**秒位在前**（tokio-cron-scheduler 约定），执行时用本机时区 `Job::new_async_tz(&cron, Local::now().timezone(), ...)`（:206-208）。CLI 的 `goose schedule cron-help`（commands/schedule.rs:284-345）以 5 字段为主教学，并给 `@hourly/@daily` 等简写（校验逻辑 :28-48 认这七个简写）。

生命周期 API 全集（SchedulerTrait，scheduler_trait.rs:9-41）：add/list/remove/pause/unpause/run_now/sessions/update/kill/inspect。其中 `update_schedule` 是"先 remove 旧 Job 再 add 新 Job"重建（:736-746），`kill_running_job` 通过 `CancellationToken.cancel()` 协作式取消（:773-778），`run_now` 则跳过 cron 直接同步执行完整会话（:617-677）。

## 三、外部连接：两条执行线与一个常驻宿主

### 3.1 交互线：`goose run --recipe`（CLI）

```
cli.rs:226-233 (--recipe/--params/--sub-recipe 参数定义)
  → parse_run_input (cli.rs:1622-1665，与 --instructions/--text 互斥)
  → extract_recipe_info_from_cli (cli.rs:1661 → recipes/extract_from_cli.rs:11)
  → load_recipe (recipes/recipe.rs:21-50：load_recipe_file + build_recipe_from_template
      + UserPrompt 回调 :13-18 + 缺失 secrets 交互收集 :53 起)
  → InputConfig { contents: recipe.prompt, additional_system_prompt: recipe.instructions }
      (extract_from_cli.rs:53-56)   ← 上下文注入的分水岭
  → build_session (session/builder.rs)
      settings.goose_provider/goose_model 作为 provider/model 回退 (:243-247, :258)
      temperature 注入 ModelConfig (:272-277)
      recipe.extensions 进 resolve_extensions_for_new_session (:421)
      recipe.response 经 apply_recipe_components 挂 JSON schema (:515)
      recipe 整体存回 session_manager (:571-578)
      recipe.retry 传入 CliSession (:606)
  → process 循环 → SessionConfig { schedule_id, retry_config } (session/mod.rs:1147-1153)
```

**recipe 名字解析顺序**（search_recipe.rs:11-19）：先本地 `load_local_recipe_file`，失败且配置了 `GOOSE_RECIPE_GITHUB_REPO` 则从 GitHub 仓拉取。本地搜索目录序（local_recipes.rs:21-46）：当前目录 `.` → `GOOSE_RECIPE_PATH` 环境变量（冒号分隔）→ 全局 `~/.config/goose/recipes`（:13-19 的 is_global 分支）→ 项目 `.goose/recipes` → 项目与家目录的 `.agents/recipes`。带扩展名（.yaml/.json）直接按文件读（:49-55）。

**sub_recipes 的执行挂载**不在主流程里，而是运行时按需：summon 扩展把 session.recipe.sub_recipes 逐个注册为可委派源 `SourceType::Subrecipe`（summon.rs:304-327），主 agent 通过 summon 工具拉起子代理执行之；`--sub-recipe` CLI 追加的额外子配方也走同一条路（extract_from_cli.rs:24-50，追加时 `sequential_when_repeated: true`）。`values` 字段支持任意 YAML 类型并字符串化（mod.rs:131-154 的 `deserialize_value_map_as_string`）。注：`sequential_when_repeated` 字段（mod.rs:126）在当前源码中除定义与测试外无消费者——是同名子配方重复调度时串行执行的预留位（推断，基于字段名与无消费者现状）。

反向生成通道：交互会话里 `/recipe [filepath]` 斜杠命令（session/input.rs:205, :285）让模型按 prompts/recipe.md 的 JSON 契约（title/description/instructions/activities 四键）总结当前对话生成 recipe，经 `save_recipe_to_file` 落盘全局 recipes 目录（local_recipes.rs:185-200，文件名从 title slug 化生成 :154-183）。

### 3.2 调度线：三个宿主进程

**goosed（桌面后端）是唯一合格宿主**：`AgentManager::instance()` 全局单例初始化时即创建常驻 `Scheduler`（execution/manager.rs:69-86，存储路径 `Paths::data_dir()/schedule.json`），随 goosed 进程存活——cron 唤醒只发生在常驻进程里。桌面 UI 走 HTTP：`POST /schedule/create`（routes/schedule.rs:96-167，先 unicode 隐藏字符安全检查 :107-110 + validate_recipe，再 `recipe.to_yaml()` 写入 scheduled_recipes 目录 :126-131，最后 `add_scheduled_job(job, false)` 不复制）、`/schedule/list`、`/schedule/delete/{id}`、`/schedule/{id}/run_now`（:246 起，取消时返回特殊 session_id "CANCELLED"）、sessions/pause/unpause/kill/inspect 全套。

**goose CLI 是短命宿主**：`goose schedule add/list/remove/sessions/run-now` 每个子命令都临时 `Scheduler::new` 一个实例（commands/schedule.rs:96-101 等五处同构代码），命令返回进程即退出。写入磁盘的 job 由 goosed 下次启动时 `load_jobs_from_storage`（scheduler.rs:416-484）恢复；运行中的 goosed 则靠 `sync_from_storage`（:486-553）在每次 `list_scheduled_jobs`（:555-563）时对账磁盘——新增的补挂、删掉的摘除（正在运行的跳过，:513）。这是**以文件为真相源的双进程协调**，无任何 IPC。

**`goose run` 的隐藏参数 `--scheduled-job-id`**（cli.rs:363-372，help 标注 "internal use"）让交互式 run 也能把会话挂到某个 schedule 名下，`CliSession` 持有它并填进 SessionConfig.schedule_id（session/mod.rs:1148）。

### 3.3 会话层的双向关联

`SessionType` 枚举（session_manager.rs:41-49）把 Scheduled 与 User/SubAgent/Hidden/Terminal/Gateway/Acp 并列分类——调度会话与交互会话在持久层就是隔离的两类。`Session.schedule_id` 字段（:76）+ SQLite 列（:763）+ 写入绑定（:910）构成正向关联；反向关联是 job 的 `current_session_id`（scheduler.rs:859-863 运行期回写内存表）。`Scheduler::sessions()`（:594-615）用 schedule_id 过滤全部会话按时间倒序截断，支撑 `goose schedule sessions` 与桌面端运行历史视图。

## 四、数据流：两条端到端路径

### 4.1 一条 recipe 从 YAML 到交互执行完成

1. 用户 `goose run --recipe weekly-report --params owner=alice`；
2. 名字解析命中 `~/.config/goose/recipes/weekly-report.yaml`（local_recipes.rs:64-69 逐目录试探）；
3. `build_recipe_from_template`：validate 提取参数声明 → 三级取值（显式/default/UserPrompt 终端交互）→ minijinja Strict 渲染（File 参数已读成内容）→ `Recipe::from_content` 反序列化 + 自动补 analyze/summon；
4. 缺 secrets 时交互补录并存 keyring（recipes/recipe.rs:57-103，ESC 可跳过可选密钥）；
5. prompt 变成 InputConfig.contents（首条用户消息）、instructions 变成 additional_system_prompt（追加进系统提示）——**recipe 的两个文本字段在会话里扮演完全不同的角色**；
6. build_session：settings 覆盖模型选型、extensions 决定工具集、response.schema 挂结构化输出、retry 进 CliSession、recipe 全量存回 session 行；
7. agent.reply 循环执行（同 01 篇引擎）；期间 sub_recipes 经 summon 按需拉起子代理；
8. 结束后 `recipe_runs` 计数打点（cli.rs:1653-1660，含 recipe_version 标签，版本号在 :1628-1639 预解析）。

### 4.2 一个 scheduled job 的唤醒-执行-落账路径

cron 到点（或用户 run_now）后：

1. **唤醒**：tokio 调度器触发闭包（scheduler.rs:208-216），先查 paused（:217-227，暂停即静默返回），再翻转 `last_run/currently_running/process_start_time` 并立即持久化（:229-241）；
2. **注册取消令牌**（:243-247）→ 进入 `execute_job`（:802 起）；
3. **加载 recipe**：读 job.source 文件（:812-813），若有 `recipe_base_dir` 则用原目录解析相对引用（:816-822），`build_recipe_from_template` 渲染——**注意此处回调传 `None`**（:828）：UserPrompt 参数无人可问，直接落进 missing，整个 job 以 MissingParams 失败；
4. **建会话**：全新 `Agent` + 全局 Config 取 provider/model（:832-838），`create_session(..., SessionType::Scheduled)`（:840-849），`resolve_extensions_for_new_session` 挂工具、`create` 建 provider（:851-857），session id 回写 job（:859-863）；
5. **注入任务**：prompt 优先、instructions 兜底（:902-914），构造首条 user message 与 `SessionConfig { schedule_id: Some(job.id), retry_config: None }`（:919-924）调用 `agent.reply`（:926-928）；
6. **消费流**：循环 `stream.next()` 收 Message/HistoryReplaced 事件，出错置 stream_error 跳出（:933-951）；
7. **落账**：`session_manager.update().schedule_id().recipe()` 把 recipe 快照持久化到会话（:953-960）；发 session_completions/duration/tokens 指标（:962-999）与 posthog 完成事件（:1001-1022）；
8. **收尾**：清取消令牌、复位 job 三字段、persist（:257-273）；失败时仅 error 日志 + telemetry `scheduler_job_failed`（:277-281）——如前述，**没有用户可见通知**。

## 五、设计决策

**为何 YAML + 可选嵌套包裹**：YAML 让长文本 instructions/prompt 可读性最好，且 `to_yaml` 时对这两个字段做多行块重排（mod.rs:292-298，yaml_format_utils 递归改写）；嵌套 `recipe:` 键兼容（:326）则是一次性的历史包袱收纳——旧分享格式不必迁移。JSON 双支持（:26）几乎零成本（serde_yaml 超集），换来 API 集成方直接内联 JSON 的便利。

**调度会话与交互会话的隔离**：SessionType::Scheduled 独立分类（session_manager.rs:41-49）+ schedule_id 双向关联，使调度产物可独立检索（sessions() 过滤）且不污染交互洞察——`get_insights` 只统计 User+Scheduled 两类（:401），SubAgent 等噪音被排除。这是"无人值守但可审计"的关键：每个 job 的每次运行都是一个完整、可回放、带 recipe 快照的会话（:953-960 把 recipe 原样存进 session 行，即使源文件后来改了，历史会话的上下文仍可复现）。

**retry 在调度路径被丢弃**：`execute_job` 构造 SessionConfig 时 `retry_config: None`（scheduler.rs:923），尽管 Recipe 字段里有 retry 且 validate_recipe.rs:57-67 校验过它；而交互 CLI 路径把 recipe.retry 一路传到 SessionConfig（builder.rs:606 → session/mod.rs:1150）。源码无注释解释差异（此为推断）：合理猜测是 RetryConfig 的 SuccessCheck/shell 检查与 on_failure 清理原为有头运行设计，无头场景的失败语义更倾向"记录并等下次 cron"而非原地重试——但这意味着**给 scheduled recipe 写 retry 是无效配置**，新人最容易踩。

**文件为真相源的跨进程协调**：CLI 短命进程写 schedule.json、goosed 常驻进程读并执行、`sync_from_storage` 在每次 list 时对账（:486-553）——用最小机制（无锁文件、无 IPC）解决了"两个进程都能改任务表"的一致性问题，代价是变更生效延迟到下一次 list。配合 `add_scheduled_job(make_copy=true)` 把 recipe 复制进 scheduled_recipes/（:301-332）实现"注册即快照"——原文件删除不影响已注册 job；`recipe_base_dir` 又反向保留原目录让相对引用不断裂（:121-125 注释），复制与解析目录分离是个相当精细的取舍。

**安全三闸**：①unicode tag 隐藏字符检测 `check_for_security_warnings`（mod.rs:274-290，扫 instructions/prompt/activities），桌面端保存时直接拒绝（routes/schedule.rs:107-110）——防恶意 recipe 用不可见字符注入提示词；②File 参数禁 default（mod.rs:181-183）——防 recipe 作者预填路径偷读用户敏感文件；③secrets 交互收集且 ESC 可跳（recipes/recipe.rs:57-103）。三者共同勾勒"recipe 是不可信输入"的威胁模型。

**Temporal → 内嵌**（commands/schedule.rs:268-282 的移除声明）：砍掉外部服务依赖换取部署简单，代价是调度生命周期绑定 goosed 进程——进程不在，cron 不响。这个代价被文件真相源设计缓解（重启恢复），但**纯 CLI 用户 `goose schedule add` 后关掉一切 goose 进程，任务永远不会触发**（推断：基于 CLI 每命令临时实例 + 无守护进程的源码事实）。

## 六、新人提示

**最小可跑 recipe**（存为 `~/.config/goose/recipes/hello.yaml`）：

```yaml
version: 1.0.0
title: Hello Recipe
description: Minimal working example
prompt: Say hello to {{ name }} and list the files in the current directory.
instructions: You are a terse assistant. Always reply in English.
parameters:
  - key: name
    input_type: string
    requirement: required
    description: Who to greet
extensions:
  - type: builtin
    name: developer
settings:
  goose_provider: anthropic
  temperature: 0.2
retry:
  max_retries: 2
  checks:
    - type: contains
      pattern: hello
```

**本地测法（三步，从廉到贵）**：①`goose recipe validate hello` 纯解析校验（commands/recipe.rs 的 validate 分支走 validate_recipe_template_from_file）；②`goose run --recipe hello --render-recipe` 只打印渲染后 YAML 不启动会话（cli.rs:272-277, :1644-1650）；③`goose run --recipe hello --explain` 看 title/参数说明（:265-270, :1641-1643）。UserPrompt 参数会在第 ③步之前就被终端交互问询（recipes/recipe.rs:13-18 的 cliclack input）。

**调试 scheduler**：`goose schedule add --schedule-id t1 --cron "* * * * *" --recipe-source hello.yaml --params name=cli` 后，直接查数据目录下的 `schedule.json` 与 `scheduled_recipes/`（两者路径由 scheduler.rs:33-44 定义，基于 `Paths::data_dir()`，Linux 默认 `~/.local/share/goose/`）；`goose schedule run-now --schedule-id t1` 是**同步**执行完整会话（等它跑完才返回 session id，commands/schedule.rs:243-266）；`goose schedule sessions --schedule-id t1` 看历史落账。想看执行细节只能靠日志：RUST_LOG=info 下有 "Cron task triggered"（scheduler.rs:209）与 "Job ... completed/failed"（:276-278）两级心跳。

**五个坑**：①cron 字段序——6 字段格式**秒在最前**，`"0 9 * * * *"` 是"每小时的第 9 分钟"不是"每天 9 点"（每天 9 点要写 `"0 0 9 * * *"`）；写 5 字段会被自动前缀秒位并 warn（scheduler.rs:186-195），语义保持但日志有噪音。②UserPrompt 参数是 scheduled job 杀手——调度路径回调为 None（scheduler.rs:828），missing 即失败；给无人值守 recipe 的所有参数要么有 default 要么 required+注册时用 `--params` 喂全。③recipe.retry 对调度执行无效（:923 硬编码 None），只对 `goose run --recipe` 交互执行生效。④add 时 recipe 被复制快照（:316-332），之后改原文件不会影响已注册任务；反过来删原文件也不影响。⑤模板里想字面输出 `{{ ... }}`：含空格或非法标识符的自动保留（template_recipe.rs:31-38），但合法标识符形状的（如 `{{param_key}}`）必须写成 `{{'{{param_key}}'}}`（测试 :294-300 实证）。

与前篇的交叉引用：recipe.retry 的 SuccessCheck 语义与 agent 层的重试执行细节见本系列 01（agent-reply-engine）；调度会话复用的 `Agent::reply` 流与 Message 事件见 01；session 持久化层（SessionType/schedule_id 落库）见 05；`goose run` 的 build_session 全景见 06。
