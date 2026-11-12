# workflow-use 新人上手文档

> 基于图谱（491 节点，commit f00e27ed），结论经源码核实，锚点 file:line。

## 1. 项目一句话定位

workflow-use 是 browser-use 团队的 **RPA 2.0** 项目：「录制/生成一次，之后零 LLM 本地重放」。录制或自然语言生成一次，之后按确定性步骤本地重放，仅失败步回退 browser-use agent（LLM）自愈。动机：客户要求 browser-use 更可靠、更确定。

**上层封装与消费方**（非分支）：以 browser-use 0.13.x 为依赖，复用其 agent/Controller/Browser；贡献「工作流模型+语义定位+录制/生成管线+自愈执行器」。单仓三子项目：`workflows/`（Python 引擎+CLI+backend）、`extension/`（WXT 录制扩展）、`ui/`（React 前端）。

## 2. 总体架构（16 层缩览）

- **引擎（L2-6）**：数据模型（`schema/views.py` 全仓最高扇入）→ 执行引擎（`workflow/service.py`+3229 行 `semantic_executor.py`）→ 变量 → controller 动作 → healing。
- **录制线（L7）/出口（L8-9）**：recorder+builder 事件转工作流；storage、MCP、CLI（`cli.py` 2662 行）、backend FastAPI。
- **采集端（L10-12）/可视化（L13）/外围（L14-16）**：extension 基座+content/background+sidepanel；ui ReactFlow 画布（openapi.json 契约解耦）；示例库/演示脚本/测试。

CI 仅 lint（§8），发布每周五 rc（`publish.yml:15`）。

## 3. 核心链路：从录制到自愈执行

1. **扩展采集**：`content.ts`（1075 行）双轨——`rrweb.record()` 全量录 DOM（content.ts:122）+监听 8 类 DOM 交互，为每次交互生成 XPath/增强 CSS 与语义信息。
2. **装配去重**：`background.ts` 按 tabId 汇总、过滤副作用导航、转语义步骤；步骤串 SHA-256 去重（background.ts:44-52），有变化才 POST 到 `http://127.0.0.1:7331/event`（background.ts:41）。
3. **Python 接收**：`recorder/service.py` 内嵌 FastAPI，`/event` 202 接收（recorder/service.py:33），uvicorn 监听 7331（:178）；协议由 `recorder/views.py` 与扩展 `message-bus-types.ts` 镜像。
4. **转换**：`semantic_converter.py` 把 CSS 定位换成语义定位；`builder/service.py` 用 LLM（含截图）转工作流定义。
5. **执行与自愈**：`Workflow` 类（workflow/service.py:39）顺序执行；GUI 走 backend（8000，api.py:24；CORS 只放行 5173，api.py:12），ui baseUrl 即 `localhost:8000`（ui/src/lib/api/index.ts:6）。执行期双臂兜底（§4），生成期 healing「任务→工作流」。

**录制与自然语言（HealingService）是两条生成线，产出同一种 WorkflowDefinitionSchema**。

## 4. 关键模块深读

**数据模型**：`schema/views.py`（279 行）定义 BaseWorkflowStep、多策略选择器层、10 种确定性步骤+agent 步骤 Union；model_validator 强制以 extract 步骤收尾（schema/views.py:241-254）；YAML 示例与 builder/healing 产物都是这个形状。

**Workflow 引擎**：`run()` 顺序执行三类步骤（workflow/service.py:851）；`_build_input_model()` 按 input_schema 动态建 Pydantic 输入模型使工作流可作 LLM 工具（service.py:952/1013）；`run_with_no_ai`（:1047）是零 AI 入口。动作层禁用默认 25 个动作（`DISABLED_DEFAULT_ACTIONS` 列表自 controller/service.py:26，:58 经 `exclude_actions=` 传入），注册 7 个动作 navigation/click/input/select_change/key_press/scroll/extract_page_content（:64-216）。

**语义双臂（技术灵魂）**：`semantic_extractor.py` 建立「可见文本→确定性选择器」整页映射，靠七类元素计数 ID（semantic_extractor.py:18，extract_semantic_mapping :816）；`semantic_executor.py`（3229 行）CDP 直连执行、映射刷新与验证重试、内置日历/下拉逻辑；`element_finder.py` 语义优先 XPath 兜底链。

**healing 线**：`generate_workflow_from_prompt`（healing/service.py:432）让 agent 真跑任务再转工作流。开关 `use_deterministic_conversion=False` 默认 LLM 转换（:46），开了才初始化确定性转换器（:78），执行期 :846/851 分叉——确定性零 LLM 步骤、快 10-100 倍。`workflow_creation_prompt.md:5-27` 五条强制规则：extract 收尾/简单动作禁 agent 步/语义 target_text/单花括号变量/直达导航。`validator.py` 三级严重度 AI 审查可返回修正版。

**selector 工程**：`selector_generator.py` 生成 8 级回退策略（精确 :118 → 模糊 :185 → XPath :196）；`xpath_optimizer.py` 把脆弱绝对 XPath 转鲁棒。

**变量线**：`variable_identifier.py` 三阶段识别应参数化的值——正则模式（:207）/上下文关键词 conf 0.85（:288）/启发式（:238），`min_confidence=0.6` 闸门（:120）；healing 侧 `variable_extractor.py` 走 `VAR:name:value` 标记+LLM 建议双通道。

**agent 步兜底**：`step_agent/controller.py:13-16` 注册唯一结束动作 `continue_to_next_step(is_current_step_success)`；提示词「只执行当前一步」（agent_step_system_prompt.md:116）。

## 5. 数据流与制品

**YAML 双格式持久化**：storage 以目录为库存 `{id}.workflow.yaml`，落盘 `yaml.dump(..., sort_keys=False)`（storage/service.py:174）保住键序；`metadata.json` 运行时索引（:47），`search_workflows` 关键词过滤（:264）。JSON 旧格式经 `migrate_json_to_yaml.py` 迁移。

**两代示例演进**：`form_filling/v1.json`（56 步硬编码长 Tailwind 选择器）→ `v1.fully-semantic.json`（补 target_text）→ 现役 YAML（pure_semantic、github_stars_parameterized、semantic_form_fill）。

**backend 数据流**：`WorkflowService` 以 `./tmp` 为工作流目录（backend/service.py:40），asyncio.Task+cancel_event 协作取消（routers.py:67-74），日志落文件增量读；任务状态存内存 `active_tasks`（service.py:51）——导致 §8 头号坑。`ui/src/lib/api/openapi.json`（8 路径/11 schema）是契约快照兼前端类型源。

## 6. 设计决策与取舍

1. **双臂转换开关**：healing 默认 LLM 转换（healing/service.py:46），确定性按需启用（:78）——LLM 慢且有成本，确定性 5-10 秒零成本。执行侧：确定性失败才退化 agent。
2. **lazy import 规避循环依赖**：`semantic_executor.py:759` 注释 `# Import ElementFinder here to avoid circular imports`；validation_utils 被 step_verifier.py:462、semantic_executor.py:2121 函数内延迟导入，是既定解法。
3. **openapi 契约生成前端类型**：ui `type-gen`（ui/package.json:11）从契约生成 apigen.d.ts 端到端类型化；CI 有专门步骤（lint.yml:54-55），改端点须重跑。
4. **安全地板双侧下钉**：pyproject.toml 对传递依赖下版本地板（注释标 CVE/PYSEC，约束进发布 wheel 的 Requires-Dist 而非仅 uv 锁文件）；extension/package.json:46 overrides 钉 23 个。
5. **统一 2 秒轮询**：sidepanel POLLING_INTERVAL=2000（workflow-provider.tsx:35），ui 日志查看器同款（log-viewer.tsx:71-75）。

## 7. 上手路径（按 tour 16 步首日路线）

- **上午·主张与形状（S1-2）**：两份 README 建全景 → 精读 `schema/views.py`，看懂数据模型任何 YAML 都对得上。
- **上午·引擎（S3-5）**：`workflow/service.py` 主流程 → 语义双臂 → 三道安全网（step_verifier/validation_utils/error_reporter）。
- **下午·两线（S6-11）**：step_agent 兜底 → 变量三件套 → healing → validator → selector 工程 → recorder/builder。
- **下午·出口与两端（S12-15）**：storage/mcp/cli 三出口（`launch-gui` 起前后端，cli.py:2160）→ backend+openapi → 扩展 → ui。
- **收尾（S16）**：跑 `tests/run_all_tests.py` 验证环境；对照 v1.json 与 v1.fully-semantic.json 体会「语义化」；`lint.sh` 复现 CI。动手：复制 github_stars_parameterized.workflow.yaml 改自己的搜索流，`cli.py run-workflow-no-ai` 跑通即闭环。

## 8. 常见坑与勘误

1. **backend 任务表不跨请求（最重要）**：`get_service()` 每调用新建实例（workflows/backend/routers.py:22-23），8 端点各持独立 service。`/execute` 把 TaskInfo 存进实例 A 的 active_tasks（backend/service.py:174），`/logs/{task_id}` 用实例 B 查——task_info 恒 None，status 恒 `'unknown'`（routers.py:98）；cancel_events 同理，取消失效。日志走文件仍可用；修法：单例/lru_cache。
2. **CI 测试 job 全注释**：test-python/test-ui/test-extension 整段注释（.github/workflows/lint.yml:104-168）。CI 只跑 ruff/eslint/tsc；测试（tests 12 个+包内多需 LLM key）只靠本地。
3. **components.json css 漂移**：extension/components.json:8 写 `"css": "assets/tailwind.css"`，实际在 `extension/src/assets/tailwind.css`——shadcn add 找错路径。
4. **logina-view.tsx 拼写笔误**：loading 视图文件名是 `logina-view`（导入见 sidepanel/index.tsx:9），按 loading 搜索会漏。
5. **默认录制开关注释与代码矛盾**：background.ts:38 `let isRecordingEnabled = true; // Default to disabled (OFF)`——代码默认开录、注释说默认关。
6. **docs 引用 5 个已删/移示例**：docs/DETERMINISTIC.md:66-68 的 run_complete_test.py（已移 scripts/deterministic/）、create_deterministic_workflow.py、test_custom_task.py；docs/VARIABLES.md:69-70 的 create_workflow_with_variables.py、run_workflow_with_variables.py（实为 scripts/variables/）。照跑会 FileNotFoundError。

**图谱抽查**：16 层叙事、行数（executor 3229/cli 2662/content 1075）、25 禁用/7 注册动作、8 种录制事件（recorder/recorder.py:10-124）、端口 7331/8000/5173 与源码一致；上述 6 条均仓库自身问题（注释滞后/文档漂移/待修 bug），非图谱错误。
