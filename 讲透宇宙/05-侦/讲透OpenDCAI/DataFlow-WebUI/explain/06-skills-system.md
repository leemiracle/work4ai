# 06 · 五 canonical skills 单一真源与派生门禁

## 角色定位

`skills/canonical/` 是全仓 Agent 技能的**唯一手写真源**：五个技能包——`generating-dataflow-pipeline`（核心工作流：从目标+样本 JSONL 规划算子链并产出可跑 pipeline）、`dataflow-dev`（开发者助手：架构知识加载与意图路由）、`dataflow-operator-builder`（脚手架新算子：注册+CLI 包装+测试）、`prompt-template-builder`（为既有算子造 prompt_template 类）、`core_text`（reference 包：18 个 core_text 算子的逐个 API 参考，`invocable: false` 只被读不被调用）。`.claude/skills/`、`.cursor/skills/`、`.cursor/rules/`、`AGENTS.md` 全是派生物——manifest 注释钉版"'canonical' is the ONLY hand-edited source"。

## 内部结构

`installers/skills.manifest.json` 是登记处：每个技能声明 id/canonical 路径/layer（core|harness|standalone，决定在哪些 profile 出货）/requires（如 mcp-optional）/agents（claude/codex/cursor 三选多）。三个 profile（webui/harness/skills）区分运行环境：`profile_context`（generate_agent_assets.py:85-87）据此设 `mcp=yes/no`——只有 webui/harness 有 MCP 服务。派生由 `generate_agent_assets.py` 完成：`generate_skill_package`（L90）逐文件渲染 canonical 目录（`RENDERABLE_SUFFIXES={".md"}` L38，非 md 文件字节拷贝）；SKILL.md 渲染后在 frontmatter 之后插入 GENERATED banner（L40-44、L70-80）；`generate_cursor_rules`（L133）产出薄路由 `.mdc`（模板 L110-130，pipeline 技能 alwaysApply=true 保留旧行为）；`generate_agents_md`（L207-264）把 AGENTS.md 写成路由表——L210-213 注释自述教训：旧版内联全文 1100 行，Codex 每任务都得整读，违背渐进披露。条件渲染引擎 `lib/render.py` 是 143 行微型模板：`@if/@elif/@else/@endif` 藏在 HTML 注释里（IF_RE L31，渲染后不可见）；变量替换 `{{@NAME}}`（VAR_RE L32）——**`@` 是刻意设计**（docstring L20-23）：技能模板里的裸 `{{OP_NAME}}` 是作者面向的占位符，必须原样存活，两种语法分家防误替换。安全边界：条件只支持 `==`/`!=` 加 and/or（L17-18 无任意 eval），and/or 混用直接拒绝（L62-63），未知变量抛 RenderError（L46、L81），未闭合 @if 报错（L135-136）。

## 外部连接

消费侧三 Agent 各取所需：Claude Code 读 `.claude/skills/`、Cursor 读 `.cursor/rules/`+`.cursor/skills/`、Codex 读 AGENTS.md 路由表；后端 `agent_session.py` 的 SYSTEM_PROMPT（03 篇）与 MCP 工具集是它们的运行时伴侣——`generating-dataflow-pipeline` 的 SKILL.md 明写六大首选原语（PromptedGenerator/FormatStr/Text2MultiHopQA/PromptedFilter/GeneralFilter/KBC 三连）与强制选择顺序规则。`Makefile` 的 `make skills` 是再生成入口（AGENTS_FOOTER L196 提示）。

## 数据流

作者流：改 `skills/canonical/**` → `python3 installers/generate_agent_assets.py` → 派生物全量重写（L358-368 先整删技能目录防孤儿）→ `retired_cursor_rules` 清退役规则（L370-374）。门禁流：`--check`（L342-356）在 tempdir 重建理想树 → `compare_tree`（L298-322）与仓内实际树逐文件比对，报 missing/unexpected/content differs 三类漂移并 exit 1——CI 跑它，手编生成物必被抓住。

## 设计决策（含批判）

- **check_skills.py 五重 lint**（L4-18 docstring 自列）：manifest 与磁盘互查（L196-211，目录没登记=永不安装，直接 fail）；SKILL.md frontmatter 的 name 必须匹配目录、且只许 name/description 两个键（L244-261——其他键放 manifest，防某个 Agent 实现不认识就误处理）；相对链接与代码路径存活检查（L71-111，含 `../sibling` 特判 L107-110：兄弟技能本 profile 未装就断链）；安装名冲突检测（L213-222）；条件指令在**全部 (agent, profile) 组合矩阵**下都必须能渲染（L114-131）——坏指令在 CI 就爆而不是 Agent 打开文件时。
- **profile 边界守卫**：`check_profile_content_boundaries`（L134-189）是语义级断言——skills profile（无 MCP）渲染结果禁止出现 "MCP/WebUI/get_operator_detail_by_name" 等字样（L138-147，防止教 Agent 用它没有的系统）；harness profile 禁 WebUI 专属措辞（L175-177）；webui profile **必须**含 `validate_pipeline_config`（L187-189，必备词缺失也 fail）。正向+反向双向断言，这比纯 lint 高一个档次。
- **批判·token 黑名单是字符串匹配**：边界守卫靠 `token.lower() in output.lower()`，换个措辞（如"MCP server"写成"工具服务"）就绕过——守得住粗心守不住刻意；真正的保证仍来自 render 矩阵的结构性检查。
- **批判·双真源风险**：SYSTEM_PROMPT（中文、后端）与 canonical skills（英文、生成物）各讲一遍纪律，改一处漏一处无门禁可查；banner+--check 管住了派生物，管不住两套源头之间的漂移。
- **可移植性取舍**：技能包只带 markdown+脚本+模板，零三方依赖跑 lint（check_skills docstring L18）——CI 无需装环境，这对开源仓的贡献者体验是显著加分。

## 新人提示

改技能永远改 `skills/canonical/`，然后 `make skills`；直接编辑 `.claude/skills/` 或 AGENTS.md 会被 `--check` 打回。条件文本用 `<!-- @if profile==... -->` 包裹，变量一律 `{{@NAME}}`（带 @），裸 `{{X}}` 会被当占位符放过。新增技能五件事：建 canonical 目录+SKILL.md（frontmatter 只有 name/description）、manifest 登记、三个 agent 是否都要、`python3 installers/checks/check_skills.py` 过 lint、`generate_agent_assets.py --check` 确认零漂移。
