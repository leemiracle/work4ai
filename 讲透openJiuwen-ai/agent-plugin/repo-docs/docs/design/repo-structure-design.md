# agent-plugin 仓库结构设计

> 版本：v0.1（2026-09-28）
> 状态：设计稿，待评审
> 结论先行：本仓定位为 **JiuwenSwarm 官方 plugin 插件包集合仓**（对应 Hub 资产类型 `agent-plugin`），采用「**扁平插件目录 + 约定式包结构 + 生成式目录清单 + 工具链门禁**」的单仓集合模式。

---

## 1. 背景与定位

### 1.1 jiuwenswarm 的 plugin 体系现状（对接点）

jiuwenswarm 主仓已实现完整的插件运行时，本仓是其**内容供给方**：

| 主仓机制 | 对接点 |
|---|---|
| 统一扩展包系统（`extension_package_manager.py`） | 插件包落盘 `<data-dir>/agent/workspace/plugins/plugin_packages/{local,built_in}/<plugin-name>/`，加载器**只扫描一层目录**，`manifest.json` 的 `package_type` 必须为 `"plugin"` |
| plugin-creator 技能 | 定义了插件包规范（manifest 四份 spec + init/validate/register 脚本），本仓的 `templates/` 与 `docs/plugin-spec.md` 与其保持同源 |
| Hub 市场（`swarmskills.openjiuwen.com`） | 资产类型映射：`plugin`（本地）↔ `agent-plugin`（Hub），发布为 zip（≤50MB，带文件黑名单），安装走「下载 → 校验 → 原子落盘 → marketplace 记账」 |
| plugin_migrator | 可把 Claude Code 插件迁移为 plugin 包（IR: skills/commands/agents/hooks/mcp → emitters），本仓可承接迁移产物 |
| 三层校验 | L0 规范质量 / L1 静态 AST / L2 真实热加载，`RESULT: PASS` 才能注册 |

**插件包的规范结构**（来自 plugin-creator，硬约束）：

```
<plugin-name>/                  # kebab-case，必须等于 manifest.id
├── manifest.json               # 必须
├── README.md                   # 必须（详情页正文）
├── avatars/avatar.png          # 可选
├── skills/<skill-name>/SKILL.md    # 可选（+ scripts/ references/ assets/）
├── tools/<name>_tool.py        # 可选（继承 openjiuwen.core.foundation.tool.Tool）
└── rails/<name>_rail.py        # 可选（继承 openjiuwen.harness.rails.base.DeepAgentRail）
```

manifest 关键约束：`id` = 目录名；`tags`/`quick_inputs` 固定 3 条且 `default_init_input` 与 `quick_inputs[0]` 逐字一致；展示字段一律 `{en, zh}` 双语；`category` ∈ {Design, Engineering, Life, IndustryConsultant, Others}；skills/tools/rails **至少声明一类**、路径必须真实（无则整段省略，禁止空数组）；**禁止**声明 `persona/agent_card/model/subagents/memories/rubics` 及 `mcps`（插件是能力包不是人设，MCP 走独立 `agent-mcp` 资产类型）。

### 1.2 本仓的角色

```
                    ┌──────────────────────────────┐
   PR 贡献 ───────► │  agent-plugin 仓（本仓）        │
   （内部/社区）     │  plugins/ = 插件包实体          │
                    │  scripts/ = 工具链 + 门禁       │
                    └───────┬──────────────┬───────┘
                     CI 发布 │              │ 同步
                            ▼              ▼
                 Hub 市场（swarmskills.    jiuwenswarm 主仓
                 openjiuwen.com，         resources/…/plugin_packages/
                 kind = agent-plugin）    /built_in/（随产品分发）
                            │              │
                            ▼              ▼
                        用户端「扩展中心」安装到 local/，会话中装备启用
```

三种分发通道共享同一个内容源：**Hub 在线安装、产品内置（built_in）、开发者直接拷贝到 local/**。因此本仓的核心不变量是——

> **`plugins/` 目录里的内容 = 用户最终拿到的内容（1:1），一切开发态产物（测试、CI、文档、脚手架）都放在仓库层。**

---

## 2. 业界调研结论

对 Claude Code 插件生态（anthropics/claude-code、claude-plugins-official、anthropics/skills、wshobson/agents、VoltAgent/awesome-claude-code-subagents、davila7/claude-code-templates）与其他 agent 插件系统（lobehub/lobe-chat、AutoGPT blocks、block/goose、OpenAI ChatGPT Plugins、crewAI、opencode）的调研（2026-09-28，均基于真实仓库访问）归纳如下。

### 2.1 仓库形态对比

| 形态 | 代表 | 适用场景 | 对本仓的启示 |
|---|---|---|---|
| **单仓集合 + 声明式清单** | claude-plugins-official（`plugins/` + `external_plugins/` + `.claude-plugin/marketplace.json`） | 第一方内容 + 少量收录的第三方内容 | ✅ 采用。本仓同为「实体内容仓」 |
| **内容与打包解耦（虚拟插件）** | anthropics/skills（扁平 `skills/` + 清单层用 `source:"./"` + `skills[]` 聚合） | 同一批内容要组合出多种发布单元 | ⚠️ 部分借鉴：`catalog/catalog.json` 由生成器聚合，而非手写 |
| **索引仓与实现仓分离** | lobe（lobe-chat-plugins 只存 JSON 索引 + manifest URL） | 插件自托管、跨域名分发 | ❌ 不采用。jiuwenswarm 的 Hub 分发以 zip 实体为单位，需要内容仓 |
| **代码驱动 + 自动发现** | AutoGPT blocks（Pydantic 类即 schema，importlib 扫描注册） | 第一方运行时工具集 | ⚠️ 借鉴其「零手工注册」思想：catalog 由脚本从 manifest 扫描生成 |
| **多 harness 适配器** | wshobson/agents（`plugins/` 单一事实源 + `tools/adapters/` 生成 6 家产物） | 一份内容多平台消费 | 📌 演进项：plugin_migrator 可反向承担「出口适配器」 |
| **CLI 初始化器** | davila7/claude-code-templates（npx 交互式安装） | 大规模 C 端分发 | 📌 演进项：本仓 `scripts/init.py` 承担脚手架角色 |

### 2.2 提炼出的设计原则

1. **约定优于配置**（Claude Code）：标准目录布局即可被发现，manifest 只做补充声明。plugin-creator 规范已具备此性质，本仓不另造结构。
2. **单一事实源 + 生成物**（wshobson/agents）：手写内容只有 `plugins/`，目录清单（catalog）、发布包（zip）、内置同步（resources 拷贝）全部由脚本生成，杜绝清单漂移。
3. **细粒度小插件**（wshobson/agents 明言动机是最小化 token 成本）：一个插件解决一个场景，能力经 SKILL.md 渐进披露（description 常驻 → 正文触发时加载 → 资源按需读取），避免「大而全」插件。
4. **不可变标识 + 迁移映射**（claude-plugins-official 的 `renames`）：`id` 一经发布不可改（Hub 安装态按 id 记账），确需改名走 `renames.json` 映射。
5. **机械化质量门禁**（`claude plugin validate --strict`、wshobson `make validate/garden/test`）：校验进 CI，人只做安全审查。
6. **可执行代码 = 高风险面**（goose 的恶意包扫描/危险环境变量黑名单、lobe 的 humanIntervention）：plugin 包内的 `tools/`、`rails/` 是**进程内执行**的 Python，PR 审查按安全清单执行；密钥永不入库（发布链路已内置 .env/* key 排除）。
7. **双语展示字段**（jiuwenswarm 自身约定）：`{en, zh}` 结构化 i18n 而非双文件，供前端直接渲染。

---

## 3. 仓库结构设计

```
agent-plugin/
├── README.md                        # 仓库导览：定位、插件目录表格（含分类/版本/简介）、快速上手
├── README_CN.md                     # 与主仓约定一致的双语 README（或 README.md + README_EN.md）
├── LICENSE                          # 与主仓一致（含华为版权声明）
├── CONTRIBUTING.md                  # 贡献指南：init → 填充 → validate → PR 流程与规范
├── CHANGELOG.md                     # 仓库级变更记录（可选，初期可省）
├── renames.json                     # 插件改名迁移映射（初始为空对象，仅在迫不得已改名时使用）
│
├── plugins/                         # ★ 插件包实体（扁平一层，一包一目录，id = 目录名）
│   ├── example-plugin/              # 官方参考实现（最小可用示例，规范即文档）
│   │   ├── manifest.json
│   │   ├── README.md
│   │   ├── avatars/
│   │   │   └── avatar.png
│   │   ├── skills/
│   │   │   └── example-skill/
│   │   │       ├── SKILL.md
│   │   │       └── references/     # 长参考放这里，SKILL.md 保持精简
│   │   ├── tools/
│   │   │   └── example_tool.py
│   │   └── rails/
│   │       └── example_rail.py
│   ├── <plugin-name>/…              # 其余插件同构
│   └── …                            # 不设分类子目录：加载器只扫一层，分类由 manifest.category 承载
│
├── templates/
│   └── plugin-template/             # 脚手架模板（含 [TODO] 占位），与 plugin-creator 的 init_plugin.py 输出同源
│
├── scripts/                         # 仓库工具链（stdlib 实现，L2 环节可选依赖 jiuwenswarm）
│   ├── init.py                      # 从 templates/ 初始化 plugins/<name>/（或直接对接主仓 init_plugin.py）
│   ├── validate.py                  # 门禁入口：L0+L1 全量校验；默认以子进程跑 L2（需 jiuwenswarm 环境，--no-hot-load 关闭）
│   ├── catalog.py                   # 扫描 plugins/*/manifest.json → 生成 catalog/catalog.json（校验一致性）
│   ├── build.py                     # 打 zip：剥离开发态文件，对齐 Hub 限制（≤50MB、黑名单、无 symlink、深度/数量上限）
│   ├── publish.py                   # 发布到 Hub（swarmskills，kind=agent-plugin），CI/维护者手动触发
│   └── sync_builtin.py              # 将勾选的插件同步到主仓 resources/…/plugin_packages/built_in/（产品内置通道）
│
├── catalog/
│   └── catalog.json                 # 生成物（发布时随 release 提交，lockfile 式）：[{id, version, display_name,
│                                    #   display_description, category, tags, capabilities, path}]，供 README 表格、
│                                    #   站点渲染、内置同步清单消费；禁止手改
│
├── docs/
│   ├── plugin-spec.md               # 插件包规范（manifest/rail/tool/skill 四合一，权威来源；主仓 plugin-creator 引用此文档）
│   ├── review-checklist.md          # PR 安全审查清单（见 §5.3）
│   ├── hub-publish.md               # Hub 发布流程与回滚
│   └── design/
│       └── repo-structure-design.md # 本文档
│
├── tests/
│   ├── scripts/                     # 工具链自身单测（validate/catalog/build）
│   └── plugins/
│       └── <plugin-name>/           # 各插件的行为测试（pytest；不随包分发，维持 plugins/ = 分发物 1:1）
│
├── .gitcode/                        # 与主仓一致
│   ├── ISSUE_TEMPLATE.zh / ISSUE_TEMPLATE.en
│   └── PULL_REQUEST_TEMPLATE.md / PULL_REQUEST_TEMPLATE.zh-CN.md
├── .gitignore                       # __pycache__/ .venv/ dist/ .archive/ 等
└── .gitlab-ci.yml 或 .github/workflows/   # 流水线（见 §5.4）
```

### 3.1 关键目录职责说明

**`plugins/`（唯一手写内容区）**
- 扁平一层：`plugins/<plugin-name>/`，目录名 = `manifest.id` = Hub asset 的 package_name，kebab-case，全局唯一，发布后不可变。
- 包内结构完全遵守 plugin-creator 规范（§1.1），不新增顶层目录；`avatars/`、`skills/<n>/scripts|references|assets/` 是包内仅有的资源目录。
- **包内不放任何开发态文件**（测试、CI 配置、CHANGELOG）：Hub 发布 zip 是对包目录的整体打包（主仓 `collect_publish_files` 只剔除 `.git/__pycache__/node_modules/.venv` 等），放进来的东西都会到用户手里。
- 命名细则：`tools/<name>_tool.py`、`rails/<name>_rail.py`（文件内类名 PascalCase 且与 manifest 声明一致）；`skills/<skill-name>/`（skill name = 目录名 = frontmatter name）。

**`templates/plugin-template/`**
- 单一模板，`init.py` 以 `<plugin-name>` 实例化：生成带 `[TODO]` 占位的 manifest 骨架（tags/quick_inputs 3 条骨架、双语字段骨架）与可选的 skill/tool/rail 样例文件。
- 与主仓 `skills/plugin-creator/scripts/init_plugin.py` **保持同源**（同一模板两处引用以主仓脚本产物为准做回归），避免两套脚手架漂移。

**`scripts/`（工具链）**
- `validate.py`：对 `plugins/` 全量或 `--only <name>` 运行 L0（占位符残留、展示字段齐全、README 存在）+ L1（manifest 路径诚实、AST 检查 tool/rail 基类与构造约定、运行时路径策略）；默认经子进程加载真实 harness（L2），无 jiuwenswarm 环境时输出 `RESULT: PARTIAL`（SKIP ≠ PASS），`--require-hot-load` 将 PARTIAL 升级为 FAIL。逻辑与主仓 plugin-creator 的 `validate_plugin.py` 对齐，可优先复用其实现（复制维护，注明上游）。
- `catalog.py`：从各包 manifest 抽取 id/version/display 字段/category/tags/能力清单（skills/tools/rails 计数）生成 `catalog/catalog.json`；同时校验 id 唯一、id=目录名、版本可比。README 的插件目录表格由该脚本渲染生成（`<!-- catalog:begin/end -->` 锚点），防止文档漂移（wshobson 的 doc_gardener 实践）。
- `build.py <name>`：按 Hub 约束打包（复用主仓 `asset_package_builder.collect_publish_files` 的排除规则：`.env*`（example/template 除外）、`*.key/*.p12/*.pfx`、`id_rsa` 等；拒绝 symlink；输出 `dist/<id>-<version>.zip`），产物不进 git。
- `publish.py`：调用 Hub 发布 API（流式上传 zip），幂等重发布 = 版本递增；先 `build` + `validate --require-hot-load` 通过才允许执行。
- `sync_builtin.py`：按 `catalog` 标记或显式清单，把指定插件拷入主仓 `resources/agent/workspace/plugins/plugin_packages/built_in/`（只读内置层），供产品离线分发。

**`catalog/catalog.json`（生成物）**
- 是「目录清单，不是托管商店」（Claude 官方对 marketplace 的定位）在 jiuwenswarm 场景的对应物：Hub 才是分发与记账中心，本仓 catalog 只服务三件事——README/站点渲染、内置同步清单、发布对账（发布后比 对 Hub 资产版本 vs catalog 版本）。
- 发布流程末尾由 CI 重新生成并提交（lockfile 式），任何手改都会被 `catalog.py --check` 在 CI 中拒绝。

**`docs/`**
- `plugin-spec.md` 是插件包规范的**权威来源**（从主仓 plugin-creator 的 references/*.md 收敛而来），主仓技能文档链接指向这里；规范演进（如未来增加依赖声明字段）在此走 PR 评审。
- `review-checklist.md`：见 §5.3，PR 模板直接嵌入。

---

## 4. 与各设计原则的对应

| 设计原则（§2.2） | 本仓落地 |
|---|---|
| 约定优于配置 | 包结构完全复用 plugin-creator 规范，仓库不发明新包格式 |
| 单一事实源 + 生成物 | 手写区仅 `plugins/` + `templates/`；catalog、README 表格、zip、内置同步均为生成物 |
| 细粒度小插件 | 贡献指南要求「一个插件一个场景」；SKILL.md 精简 + references/ 分层 |
| 不可变标识 + 迁移 | id 不可变；`renames.json` 记录 {old: new}，发布脚本据此在 Hub 侧登记别名 |
| 机械化门禁 | CI 跑 L0/L1（必过）+ L2（合并前必过）；`catalog.py --check` 防清单漂移 |
| 可执行代码高风险面 | rails/tools 走 §5.3 安全清单人工审查；CI 加密钥扫描（gitleaks 规则） |
| 双语展示 | manifest `{en,zh}` 字段强制；README 双语（中文优先） |

刻意**不采用**的方案及理由：
- **分类子目录**（VoltAgent 的 `categories/`）：加载器只扫一层目录，分类子目录会破坏发现；分类信息已由 `manifest.category` 承载。
- **索引仓/实现仓分离**（lobe）：Hub 分发单位是 zip 实体，内容必须在本仓；外部第三方插件直接走 Hub 自发布，不需要本仓代管索引。
- **manifest 驱动的 marketplace.json 清单**（Claude）：Hub 已承担清单/记账职责，仓内再放一份手写清单只会漂移；catalog 生成物 + Hub 对账已覆盖需求。
- **包内测试目录**：违反「plugins/ = 分发物 1:1」不变量（主仓打包器不剔除 tests/，会随包发给用户）。

---

## 5. 治理与流水线

### 5.1 版本与发布

- 版本号在 `manifest.version`（semver），修改插件内容必须 bump（对齐 plugin-creator `register_plugin.py --bump` 约定：patch 自动递增，minor/major 手动）。
- 发布节奏：合并到 main 不自动发布；打 tag（`release/<date>` 或按插件 `release/<plugin-name>-<version>`）触发 `build → publish → catalog 重生成提交`。
- 每个 zip 与 Hub 资产一一对应（package_name = 插件 id），重发布必须递增版本，Hub 侧已有「同 package_id 换 asset 拒绝」的保护。

### 5.2 命名与兼容

- 插件 id：kebab-case 英文标识符，禁用保留字（不与主仓内置 skills/tools 重名）。
- 改名：唯一合法路径是新建插件 + 在 `renames.json` 登记 + 旧包发最后一个版本指向新包 README，避免用户 Hub 安装态悬空（对应 claude-plugins-official 的 `renames` 机制）。

### 5.3 PR 安全审查清单（docs/review-checklist.md，嵌入 PR 模板）

针对 `tools/`、`rails/` 的进程内可执行代码（这是 plugin 相对纯 skill 仓的风险差异点）：

1. import 期无副作用：不发起网络请求、不起子进程、不写文件系统（初始化只在 `init()`/`invoke()` 内做）。
2. 写入路径必须来自工具入参（`output_dir` 等）或 `get_workspace()` 会话隔离目录；禁止自行推导路径（L1 已有 AST 拦截，人工复核绕过面）。
3. 密钥/凭据零入库：manifest 与代码中不得出现明文 token；需要配置的能力在 README 写明环境变量约定（jiuwenswarm 侧由 MCP/connector 体系管理密钥）。
4. 第三方依赖：优先 stdlib；引入三方库必须在 PR 描述声明并在 README 标注，运行时按「依赖缺失 → `success=false` + 明确错误」降级（tool-spec 约定）。
5. Rail 钩子最小化：只实现需要的钩子；prompt 注入使用 `PromptSection` 且 `uninit` 清理，避免跨会话泄漏。
6. 子 agent 隔离：不读写 `agent.rails` 或其他 Rail 实例字段，状态经文件系统按 session 隔离。

### 5.4 CI 流水线

```
PR:      L0+L1 validate（全量） ─► 密钥扫描 ─► catalog --check ─► 结构检查（扁平/命名/id=目录名）
main:    对变更插件跑 L2 热加载（jiuwenswarm 运行环境镜像） ─► tests/（工具链+插件行为测试）
release: build zip ─► publish 到 Hub ─► catalog 重生成并提交 ─►（可选）sync_builtin 到主仓 PR
```

### 5.5 贡献流程（CONTRIBUTING.md）

```
python scripts/init.py <plugin-name>          # 脚手架
# …填充 manifest/skills/tools/rails（对齐 docs/plugin-spec.md）
python scripts/validate.py <plugin-name>   # RESULT: PASS（默认含 L2 热加载）
# 补充 tests/plugins/<plugin-name>/ 行为测试
# 提 PR（模板含安全清单自查）
```

社区插件与内部插件同仓同规；外部商业插件不收录（走 Hub 自发布），保持本仓「curated」性质（VoltAgent 拒绝推广型 PR 的同类策略）。

---

## 6. 初始内容与演进路线

**初始内容（首个里程碑）**
1. `example-plugin`：最小可用参考实现（1 skill + 1 tool + 1 rail 全覆盖三类能力，作为活文档）。
2. 从主仓既有资产迁移 2–3 个高价值插件（候选：主仓 `resources/agent/workspace/skills/` 中适合插件化的能力，如 ppt-creation、docx-pro 类；或用 plugin_migrator 从 Claude Code 插件迁移一批），验证「迁移 → 校验 → 发布」全链路。
3. 工具链四件套（init/validate/catalog/build）+ publish 首版。

**演进项（按需排期，不阻塞首版）**
- **依赖声明**：manifest 增加可选 `dependencies`/`requirements` 字段（当前规范无此字段，工具运行时按缺依赖降级），需与主仓加载器联动评审。
- **出口适配器**：借助/反哺 plugin_migrator，把本仓插件导出为 Claude Code / OpenPlugins 等格式（wshobson/agents 的多 harness 模式），扩大内容复用面。
- **质量评分**：catalog 增加「热加载通过/测试覆盖/审查人」标记，供扩展中心排序。
- **renames 自动迁移**：与 Hub 联动，同步 `renames.json` 到 Hub 侧资产别名。

---

## 7. 开放问题（需评审决策）

1. **内置（built_in）通道是否长期保留**：产品内置会随版本固化，Hub 在线分发更灵活；建议内置仅保留 example-plugin 与少量旗舰插件，其余全部走 Hub。需与主仓发布节奏对齐。
2. **README 语言策略**：插件 README.md 是详情页正文，双语单文件（中文优先）还是按 locale 双文件？当前 Hub 详情读取单文件，建议双语单文件并约定段落结构（`## 中文` / `## English`）。
3. **validate 脚本归属**：本仓 `scripts/validate.py` 与主仓 plugin-creator 的 `validate_plugin.py` 存在逻辑重叠，建议明确「主仓 = 运行时规范与校验的实现源，本仓 = 调用方」，避免双头维护。
