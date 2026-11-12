# A-24 `memodb-io/Acontext`（3.7K★）
> 克隆：C:\Users\mirac\AppData\Local\Temp\opencode\memory-clones\memodb-io__Acontext
> 多语言（Go API + Python 核心 + TS/Py SDK + Next.js 仪表盘）/ Apache-2.0 ｜ 「Agent Skills as a Memory Layer」：把 agent 记忆做成 Claude 式 SKILL.md 技能文件——写入靠两级 LLM 流水线（蒸馏→技能写手 agent），检索靠 agent 主动调 `get_skill/get_skill_file` 渐进披露，**刻意不用 embedding**。

## 1. 架构总览（目录地图，标出核心目录的职责）
- `src/server/api/go/` — Go API 服务（gin+gorm+swag）：
  - 会话/消息/磁盘/工件/技能 CRUD（`internal/modules/handler/`）、认证中间件、S3/Redis/RabbitMQ 基建；
  - 信封加密族（`internal/infra/crypto/`：envelope/keywrap/content）、blob S3；
  - 技能模板（`configs/skill_templates/user-general-facts/SKILL.md`、`daily-logs/SKILL.md`）。
- `src/server/core/acontext_core/` — Python 核心服务（异步 MQ 消费者 + LLM agent）：
  - `service/skill_learner.py` — 两个 MQ 消费者：蒸馏（快、无锁）与技能写手（持 Redis 锁的 agent 循环）；
  - `llm/prompt/skill_distillation.py`、`skill_learner.py` — 两级 prompt；
  - `llm/tool/skill_learner_lib/` — 技能文件操作工具集：get_skill / create_skill / create_skill_file / str_replace_skill_file / mv_skill_file / delete_skill_file / distill；
  - `schema/orm/agent_skill.py` 等 15 个 ORM 模型；`service/data/agent_skill.py` — 技能落库；
  - `llm/embeddings/`（jina/openai）——存在但启动自检被注释，未接技能检索（见 2.3）。
- `src/client/` — 三 SDK：
  - `acontext-cli/`（Go，create/login/server/dash_* 命令 + Docker 管理 + TUI）；
  - `acontext-py/`、`acontext-ts/`（TS SDK 的 `agent/skill.ts` 提供 Skill Content Tools 给任意 agent）。
- `src/packages/claude-code/`、`src/packages/openclaw/` — Claude Code 插件与 OpenClaw 集成（增量同步技能）。
- `dashboard/`、`landingpage/` — Supabase/Stripe 商业化面板；`src/server/sandbox/cloudflare/` — 代码执行沙箱。
- deepwiki（Agent Skills / Skill Learner System / Skill Content Tools for Agents 章节）与上述结构一致 [deepwiki-已验证]。

## 2. 记忆机制深读（本笔记核心，每个论断钉 `相对路径:行号`）
### 2.1 写入/抽取管线（谁触发、prompt 是什么、结构化 schema）
- 触发链（会话任务结束 → 两级 MQ 流水线）：
  - MQ `learning.skill.distill.entry` 消费者：快、单次 LLM 调用、无锁（`src/server/core/acontext_core/service/skill_learner.py:30-37`，注释 "Consumer 1: Distillation — fast, single LLM call, no lock needed"）；
  - 蒸馏产出再发 MQ `learning.skill.agent.entry` → 技能写手消费者：Redis 锁 per learning_space + 自定义超时 + agent 多轮循环（`skill_learner.py:111-124`）。
- **第一级·蒸馏**（tool-based 四选一，工具 schema 即结构化出口）：
  - `skip_learning`：琐碎任务（事实查询/闲聊/一次性计算）显式跳过（`llm/tool/skill_learner_lib/distill.py:5-24`；`llm/prompt/skill_distillation.py:13`）；
  - `report_success_analysis`：`task_goal/approach/key_decisions/generalizable_pattern/applies_when` 五字段全必填（`distill.py:26-55,146-167`）；
  - `report_factual_content`：第三人称自含事实清单（`distill.py:57-83,169-185`）；
  - `report_failure_analysis`：`failure_point/flawed_reasoning/what_should_have_been_done/prevention_principle/applies_when`（`distill.py:85-116,187-214`）。
- `applies_when` 字段被反复强调「不要过度泛化，写明网站/工具/API/环境」（`distill.py:37-44`；`skill_distillation.py:20,39`）——记忆可迁移性的先验约束。
- 蒸馏 prompt 明确反对「把事实吹成流程」（"Do NOT inflate simple factual content into fake procedures"，`skill_distillation.py:26`），且区分 user 与消息中提到的第三方（`skill_distillation.py:28`）。
- **第二级·技能写手**（Self-Learning Skill Agent，`llm/prompt/skill_learner.py:17`）：
  - 决策树——同域已有技能→更新；部分重叠→扩展；零覆盖→**只在类目级建新技能**（禁止 `login-401-token-expiry` 这类窄技能，要建 `authentication-patterns`）（`skill_learner.py:50-61`）；
  - SOP/Warning/Fact 三种条目格式模板（`skill_learner.py:97-119`）；
  - 11 条硬规则含「优先更新而非新建，少而厚 > 多而薄」「SKILL.md 是权威定义，改前必读」「**永远第三人称**写用户事实——读它的 agent 会把第一人称误当自己」（`skill_learner.py:121-134`）；
  - 修改前必须先 `report_thinking` 汇报：学到什么/相关技能/是否覆盖/计划条目原文（`skill_learner.py:136-144`）。
- 多轮上下文到达：新蒸馏结果作为追加 user 消息进入在跑的 agent，先完成当前修改再按序处理（`prompt/skill_learner.py:32-37`；打包 `pack_incoming_contexts` `prompt/skill_learner.py:184-210`）。
- 锁与排队：锁冲突的任务进 Redis pending 队列，agent 结束时 drain 一条并重触发 MQ（`service/skill_learner.py:127-143,190-204`）。

### 2.2 存储后端与数据模型（表/集合/文件布局，原文摘录 schema）
- `agent_skills` 表（Postgres）：`project_id / name / disk_id / user_id / description / meta(JSONB)` + CommonMixin 时间戳（`src/server/core/acontext_core/schema/orm/agent_skill.py:14-68`）。
- **skill = Disk + Artifact 的文件化存储**，`create_skill` 五步（`src/server/core/acontext_core/service/data/agent_skill.py:107-163`）：
  1. 解析 SKILL.md YAML front matter（name/description 必填，`agent_skill.py:15-65`）；
  2. 名字清洗：`[/\\:*?"<>|\s]` → `-`（`agent_skill.py:68-74`）；
  3. 建 Disk（`agent_skill.py:135`）；
  4. SKILL.md 内容上 S3 并 upsert 为路径 `/SKILL.md` 的 Artifact（`agent_skill.py:141-149`）；
  5. 插 AgentSkill 记录（`agent_skill.py:152-161`）。
- 文件布局由各技能自己的 SKILL.md 定义：
  - `user-general-facts` 模板要求一主题一文件 `[TOPIC].md`（coding-preferences.md、tech-stack.md、goals.md…），条目为第三人称短事实（`src/server/api/go/configs/skill_templates/user-general-facts/SKILL.md:9-38`）；
  - `daily-logs` 模板要求 `yyyy-mm-dd.md`（`prompt/skill_learner.py:94` 引用）。
- 工件层检索原语：grep/glob 端点 + 沙箱双向传输（`src/server/api/go/internal/modules/handler/artifact.go:549,601,664,750`）——文件记忆天然可被正则与模式检索。
- **客户端持钥加密**：用户 KEK base64 随 MQ 消息传递，解码失败硬失败——「没有它运行会把明文写进 DB」（`service/skill_learner.py:67-77`）；Go 侧完整 envelope/keywrap 实现（`api/go/internal/infra/crypto/`）。
- 增量同步：技能文件每次变更后 `touch_skill_updated_at` 刷 updated_at，供 OpenClaw 等增量同步客户端探测（`service/data/agent_skill.py:77-90`）。

### 2.3 检索策略（向量/关键词/混合/重排/图，参数与阈值）
- **无向量检索**——README 直言「Progressive disclosure, not search」「No embedding search — progressive disclosure, agent in the loop」（README:49,78）。
- 核心里 embedding 模块（jina/openai）存在但启动自检被注释（`acontext_core/di.py:9,16`），未见技能检索调用 [deepwiki 相关章节亦未描述向量检索-已验证]。
- 检索协议（TS SDK 侧）：
  - 会话启动时预载 skillIds → `<skill_view>` 块注入系统提示，内含 `<available_skills>` 名单（name+description）（`src/client/acontext-ts/src/agent/skill.ts:47-67`）；
  - 预载时重名技能直接抛错（`skill.ts:34-40`）；
  - agent 用 `get_skill` 列文件+MIME、`get_skill_file` 读单文件，工具描述明示「SKILL.md 是你该读的第一个文件」（`skill.ts:98-147`）；
  - 二进制文件返回 15 分钟有效期的签名下载 URL，`expire` 参数可调（`skill.ts:158-163,199-203`）。
- 兜底全文检索：Disk 工件层 grep/glob API（`artifact.go:549,601`）。
- Go 服务端另有 `ListAgentSkills`/`GetAgentSkillFile`/`DownloadZip`/`DownloadToSandbox` 全套（`api/go/internal/modules/handler/agent_skills.go:254-469`）。

### 2.4 遗忘·整合·演化（有无 decay/merge/re-rank/自更新）
- 演化 = 技能文件的持续重写：
  - 技能写手 agent 以「更新优先」策略合并新学得（`prompt/skill_learner.py:52-56,133`「Prefer updating over creating — fewer rich skills > many thin ones」）；
  - 用户偏好模板要求「纠错时更新旧事实，不留过时信息」（`user-general-facts/SKILL.md:35`）。
- **蒸馏级防遗忘噪声**：`skip_learning` 显式过滤闲聊/一次性计算等不值得记的任务（`skill_distillation.py:13`；`distill.py:138-144`）。
- 无 decay/容量上限/置信度机制——记忆寿命完全由 SKILL.md 中人写/agent 维护的 guidelines 决定（`prompt/skill_learner.py:92-95` 要求 agent 遵守技能内指令）。
- 版本化薄弱：`meta` 字段可放 `{"version":"1.0"}` 但纯属用户自定义元数据，无内容版本链/diff/回滚（`api/go/internal/modules/handler/agent_skills.go:76,92` 示例）。
- 会话级遗忘：`delete_session_episodes` 类能力在 Acontext 体现为 Disk/Artifact 删除 API（`agent_skills.go:206` DeleteAgentSkill）。

### 2.5 注入上下文的方式（系统提示拼装、token 预算）
- 注入极简：只注入技能名单（name+description）而非内容，预算由 agent 的工具调用节奏自然控制（`skill.ts:52-66`）。
- 学习状态机注入产品层（`service/skill_learner.py`）：
  - `DISTILLING`（`skill_learner.py:47`）→ `SKILL_WRITING`（`skill_learner.py:100`）→ `COMPLETED`（`skill_learner.py:182`）；
  - 异常分支：`QUEUED`（锁冲突，`skill_learner.py:142`）与 `FAILED`（`skill_learner.py:76,88,174,187`）。
- 无 token 预算打包器、无每轮召回注入——与 SimpleMem/cross 的预算装箱形成两极；设计赌注是「agent 自己知道要读多少」。
- 会话侧的记忆入口由调用方决定：SDK 允许在创建会话时传入 skillIds 预载名单（`skill.ts:26-42`），OpenClaw/Claude Code 插件则把同步下来的技能文件当本地 SKILL.md 用——同一份记忆两种消费形态（API 工具调用 vs 文件直读）。

### 2.6 记忆 schema 的模板化与同步生态
- `daily-logs` 模板（`src/server/api/go/configs/skill_templates/daily-logs/SKILL.md:1-30`）：
  - 每天一文件 `yyyy-mm-dd.md`、每任务一条目（`## [short description]` + 1-3 句摘要）；
  - 同样强制第三人称（"The user requested X"，`daily-logs/SKILL.md:28`）；
  - description 里写触发条件「TRIGGER BY: read/edit user memory」（`daily-logs/SKILL.md:3`）——模板级检索提示。
- 两种开箱 schema：「日记式记忆」（daily-logs）与「主题事实式记忆」（user-general-facts 的 `[TOPIC].md`，`user-general-facts/SKILL.md:9-28`）。
- 模板安装路径：Go 服务端把 `configs/skill_templates/` 作为新建 learning space 的种子技能来源（`configs/skill_templates.go`）。
- OpenClaw 增量同步：技能文件 updated_at 指纹（`service/data/agent_skill.py:77-90`）+ `src/packages/openclaw/` 的类型与 mock 测试（`openclaw/tests/__mocks__/`）——技能目录可镜像到本地文件系统供无 API 的 agent 直读。
- Claude Code 插件（`src/packages/claude-code/`）：`plugin/hooks/` + `plugin/scripts/` 把学习流水线挂进 Claude Code 生命周期；安装说明直接指向 `https://acontext.io/SKILL.md`（README:87-93）。
- 消息与工件的多格式支撑：ORM 侧 `message.py` 有 media part 与 embedding/ocr/asr/caption metadata（`acontext_core/schema/orm/message.py:46-50`）——为多模态记忆预留，但技能写手目前只消费文本蒸馏结果 [深读范围内未见多模态写入路径]。
- 多租户：project 隔离 + user 可空（`schema/orm/agent_skill.py:19-56`），keystore/OAuth/refresh 三层客户端认证（`src/client/acontext-cli/internal/auth/`）。
- 学习空间关联：`learning_space_session.py`/`learning_space_skill.py` 两张关联表把会话与技能挂到空间（`schema/orm/`），空间是学习的作用域单位。

## 3. 关键代码摘录（≤5 段，每段 ≤30 行，带行号）
```python
# llm/prompt/skill_learner.py:50-61 — 技能路由决策树：类目级、反碎片
"""
Decision tree — follow before any modification:
1. Existing skill covers the same domain/category? → Update it. Do not
   create a separate skill.
   - e.g. learning about a new API timeout fix → update "api-patterns",
     don't create "api-timeout-fix"
2. Existing skill partially overlaps? → Update it. Broaden scope if needed.
3. Zero existing coverage for this domain? → Create a new skill at the
   category/domain level.
4. Received user preferences (not task analysis)? → Look for a
   user-facts/preferences skill ...
Never create narrow, single-purpose skills like "login-401-token-expiry"
or "fix-migration-bug-feb-15". Create broad domain skills like
"authentication-patterns" and add specific learnings as entries.
"""
```
```python
# llm/tool/skill_learner_lib/distill.py:26-52 — 成功蒸馏工具：结构化出口 + applies_when 反泛化
DISTILL_SUCCESS_TOOL = ToolSchema(
    function={
        "name": "report_success_analysis",
        "parameters": {
            "type": "object",
            "properties": {
                "task_goal": {"type": "string"},
                "approach": {"type": "string"},
                "key_decisions": {"type": "array", "items": {"type": "string"}},
                "generalizable_pattern": {"type": "string"},
                "applies_when": {
                    "type": "string",
                    "description": (
                        "Specific conditions under which this approach works "
                        "(website, tool, API, service, environment). "
                        "Do not over-generalize.")},
            },
            "required": ["task_goal", "approach", "key_decisions",
                         "generalizable_pattern", "applies_when"],
        },
    })
```
```typescript
// src/client/acontext-ts/src/agent/skill.ts:52-66 — 技能名单注入（非内容注入）
const lines: string[] = ['<available_skills>'];
for (const [skillName, skill] of skills.entries()) {
  lines.push('<skill>');
  lines.push(`<name>${skillName}</name>`);
  lines.push(`<description>${skill.description}</description>`);
  lines.push('</skill>');
}
lines.push('</available_skills>');
return `<skill_view>
Use get_skill and get_skill_file to view the available skills and their contexts.
Below is the list of available skills:
${skillSection}
</skill_view>`;
```
```python
# service/skill_learner.py:127-143 — 学习空间级互斥锁 + pending 队列
lock_key = f"skill_learn.{body.learning_space_id}"
_l = await check_redis_lock_or_set(
    body.project_id, lock_key,
    ttl_seconds=DEFAULT_CORE_CONFIG.skill_learn_lock_ttl_seconds)
if not _l:
    wide["action"] = "pushed_to_pending"
    await push_skill_learn_pending(
        body.project_id, body.learning_space_id, body.model_dump_json())
    async with DB_CLIENT.get_session_context() as db_session:
        await LS.update_session_status(db_session, body.session_id,
                                       SessionStatus.QUEUED)
    return
```
```python
# service/data/agent_skill.py:107-124 — skill 的存储本质：Disk + S3 Artifact
async def create_skill(db_session, project_id, content, *,
                       user_id=None, user_kek=None, meta=None):
    """Steps:
    1. Parse SKILL.md (YAML front matter -> name, description)
    2. Sanitize name
    3. Create Disk
    4. Upsert SKILL.md as Artifact on the disk
    5. Create AgentSkill record
    """
```

## 4. 基准/评测声明（反虚荣视角：自封 or 第三方？可复现？数字与口径）
- **无任何记忆基准评测**：
  - README 无 LoCoMo/LongMemEval 数字（全文件检索无果）；
  - `src/server/tests/e2e/` 为功能 E2E [自封-无数字：产品型项目，卖点是架构透明而非跑分]。
- 主张全部为机制论证：
  - 「Skill is All You Need」「无 embedding、无 API 锁定、可 grep」（README:36-50）[自封-定性]；
  - 「memory is getting increasingly complicated — hard to understand, hard to debug」的立论（README:38）指向可解释性而非准确率竞争。
- deepwiki 亦无评测章节（仅系统描述）[deepwiki-已验证]。
- 可验证的替代性证据：跨语言一致性（Go 与 Python 两套 SKILL.md front matter 解析逻辑对齐，`data/agent_skill.py:16-27` 注释 "Follows the same logic as the API's extractYAMLFront Matter"）与完整测试矩阵（Go handler/CLI/Python core 三层单测）体现工程严谨度。

## 5. 可借鉴模式（对 Agent 记忆系统设计的增量，区别于 mem0 已有结论）
1. **skill≡memory 同构**：
   - 用「技能文件格式」当记忆格式，记忆因此获得技能生态的全部红利——可下载（ZIP 复用）、可挂载沙箱、可 git 版本管理、可跨框架（README:47-50）；
   - mem0 的记忆只能进它的库；Acontext 的记忆是文件系统公民。
2. **渐进披露替代向量检索**：
   - 注入名单、工具取内容、SKILL.md 先读——把「检索」变成 agent 的推理行为（`skill.ts:98-147`）；
   - 对技能数量少（<百）的场景省掉整个 embedding 基建，且天然可解释（agent 为什么读这个文件有轨迹）。
3. **两级学习流水线**：
   - 蒸馏层（单次调用、便宜、可跳过）与写入层（agentic、持锁、多轮）分离（`service/skill_learner.py:26-37,111-124`）；
   - 各自独立扩展与失败处理——比 mem0 单级 `add()` 更适合异步产品化。
4. **反碎片路由决策树 + 条目模板**：
   - 类目级技能、SOP/Warning/Fact 三格式、更新优先（`prompt/skill_learner.py:50-61,97-119`）；
   - 直接把「记忆库治理」编码进 prompt，对抗 LLM 天然的碎片化建条倾向。
5. **applies_when 反泛化字段**：每条经验强制绑定适用条件（网站/工具/环境）（`distill.py:37-44`）——记忆可迁移性的先验约束，mem0 无此概念。
6. **第三人称强制**：防人格污染的细节——读记忆的 agent 会把第一人称当自己（`user-general-facts/SKILL.md:38`；`prompt/skill_learner.py:134`）。
7. **学习空间级互斥锁 + pending 队列 + 状态机**：
   - 并发学习任务串行化且不丢（`skill_learner.py:127-143,190-204`）；
   - 状态机 DISTILLING/QUEUED/SKILL_WRITING/COMPLETED/FAILED 全程可观测（`skill_learner.py:47,100,142,182`）。

## 6. 局限与风险（失败模式、安全隐患、工程债）
- 检索上限明显：
  - 技能多了以后「名单注入+agent 自选」没有规模语义检索兜底，grep/glob 只在工件层；
  - embedding 模块是死代码（`di.py:9` 注释）。
- 无版本链/回滚：
  - SKILL.md 被 str_replace 覆写后旧版本只在 S3 版本（若开启）里，应用层无 diff 审计；
  - `meta.version` 是摆设（`agent_skills.go:76`）。
- 学习质量完全依赖两级 LLM 的 prompt 纪律：
  - `skip_learning` 误判即静默丢失（`distill.py:138-144`）；
  - 技能写手一旦违反「类目级」规则产生碎片技能，无自动收敛机制；
  - 蒸馏必需字段缺失只 reject 单条（`distill.py:146-151`），无重试。
- 双 LLM 流水线 + RabbitMQ/Redis/S3/PG 五件套，自托管重量级；商业化面板（Stripe/Supabase）与开源核心耦合在单仓。
- 安全做得较认真（用户 KEK 信封加密、硬失败策略 `skill_learner.py:67-77`），但 SKILL.md 本身是注入面：
  - 恶意技能文件被 agent 读入即成提示注入载体，仓库内未见内容扫描；
  - TS SDK 的 `<skill_view>` 直接拼接 description，未转义（`skill.ts:56`）。
- 深读仅覆盖 Go/Python 核心 + TS SDK 路径；dashboard/landingpage 未逐行验证。
- 失败模式补充：
  - 蒸馏消费者查不到 learning space 即静默 skip（`skill_learner.py:43-45` `skipped_no_learning_space`）——未挂空间的会话永不学习，易被误当 bug；
  - agent 消费者异常后锁在 finally 释放并 drain 下一条（`skill_learner.py:188-204`），但 drain 失败只记日志，pending 队列可能滞留；
  - KEK 硬失败策略意味着换钥/丢钥=历史记忆不可解密，密钥管理成为运维单点。

## 7. 一句话对比 mem0
mem0 把记忆做成「带 API 的数据库行」，Acontext 把记忆做成「带 schema 的 Markdown 技能目录」——前者赌检索算法（向量+图+规则），后者赌 agent 自主的渐进披露；前者赢了规模与自动化，后者赢了透明、可迁移与人对记忆的直接主权。

## 附：克隆快照
- commit `259d73b`（2026-04-21，`feat(ui): remove billing/pricing and fix landing page build`）——行号以此快照为准。
- 周边资产速览：
  - Go CLI（`src/client/acontext-cli/`）：23 个命令（create/login/server/dash_*/skill_upload/upgrade）+ 17 个 internal 包（auth/docker/sandbox/tui/telemetry/pkgmgr 等）；
  - Python 核心（`acontext_core/`）：约 100 源文件，MQ 消费者 + LLM agent + ORM + OTel 遥测全套；
  - dashboard/landingpage/docs 四个 Next.js 应用 + Cloudflare 沙箱包。
- 定位提示：「记忆层」只是 Acontext 平台的核心子系统之一，会话/任务/磁盘/沙箱等上下文管理能力与其并列（deepwiki Core Concepts 章节同此划分）。
