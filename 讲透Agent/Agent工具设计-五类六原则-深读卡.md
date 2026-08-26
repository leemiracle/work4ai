# Agent 工具设计 · 五类六原则深读卡

> card_id: agent-tools-5cat-6principles
> universe: 讲透Agent / 工具子系统（T 组件）
> burke: 场景=给 Agent 造工具的生产工程；主体=Agent 工程师；能动=五类分类×六原则映射到本项目实证；行动=归类→对证据→批判；目的=可抄的工具设计决策表；张力=通用性 vs 可控性、灵活 vs 保真；弧线=API 封装→ACI→动态发现+代码编排的三代演进
> status: done
> refs: 全部一手核实 2026-08-26（见 §五资源地图；arXiv 仅 2405.15793，其余为官方工程博客）
> updated: 2026-08-26
> 姊妹层：[02-工具调用工程](./02-工具调用工程.md)（描述/schema/粒度/MCP 的实验层）｜[讲透Harness](../讲透Harness/README.md)（T 组件的运行环境层）｜[讲透Skills](./讲透Skills/README.md)（Skill 轴全解）

---

## 〇、一句话

**工具是 Agent 的 UI——五类工具是它的五个感官与手脚，六原则是给这具身体做工业设计的规范。**（ACI 派说法：让工具对 Agent 友好，就像 HCI 让界面对人类友好。）

## 一、五类工具 × 两特征（分类框架）

特征维度：**调用方向**（谁发起：Agent 主动 / 外部异步回调）× **作用对象**（信息源 / 世界状态 / 其他 Agent / 用户 / Agent 自身）。

| 类 | 调用方向 | 作用对象 | 设计关键 | 反模式 |
|---|---|---|---|---|
| ① 感知 Perception | Agent 主动 | 外部信息源 | **输出信息量控制**（max_results/offset/摘要化） | 返回全文撑爆窗口 |
| ② 执行 Action | Agent 主动 | 世界状态（持久改变） | **安全约束**（白名单/沙箱/审计/确认） | 裸 shell 无门禁 |
| ③ 协作 Collaboration | Agent 主动 | 其他 Agent/人 | 任务分解、并行、**差异化能力组合** | 子代理继承全部父上下文 |
| ④ 用户沟通 User Comm | Agent 主动 | 用户 | 沟通**显式工具化**，多渠道异步 | 长任务静默无进度 |
| ⑤ 事件触发 Event Trigger | **注册时主动，触发时被动** | Agent 自身 | **注册与触发分离**、防抖、生命周期 | 只能等用户输入的纯被动 Agent |

## 二、五类 × 本项目活案例对照（本文核心增量）

### 2.1 deepseek-agent-harness 工具表（agent_host.py，13 工具逐类归档）

| 工具 | 归类 | 设计证据（`文件:行为` 级） |
|---|---|---|
| read_file / grep_tree | ① 感知 | `_cap()` 16K 截断 + `FILE_MAX_LINES=2000`——输出信息量控制的直接实现 |
| write_file / run_verify | ② 执行 | authorize 白名单 + 拦 `pip install`（写操作须预算声明）；write 白名单=AGENT_PROJECT+state/ |
| deep_plan | ③ 协作 | **单 Agent 内的多模型协作**——重量问题委派 thinker 模型（cascade），循环内 ≤2 次 |
| Ledger.wrap_up → stdout | ④ 用户沟通（弱形式） | `[ledger]` 前缀输出=行为可追踪；steering 回调=反向（人→Agent） |
| agent_lint/test/smoke/eval + graph_guard/conflict + patch_queue（7 个） | **△ 验证亚类**（见 §四批判） | L1-L4 金字塔 + graph 三查——五类框架装不下，见下文 |
| （无） | ⑤ 事件触发 | **缺口**：CLI 单任务宿主无回调需求——五类的"需不需要"判据：任务是否有异步外部世界 |

### 2.2 opencode 自身工具表（本卡写作会话就在用的）

| 类 | opencode 工具 |
|---|---|
| ① 感知 | read / grep / glob / websearch / webfetch / context7 两件套 / gh-grep |
| ② 执行 | bash / write / edit / ast_grep_replace |
| ③ 协作 | task（前台 subagent）/ delegate（后台委派）/ subtask / delegation_read |
| ④ 用户沟通 | todowrite（进度面板=把"汇报"工具化）；memory_set（跨会话档案） |
| ⑤ 事件触发 | **schedule_job / update_job / run_job / get_job**（scheduler 插件=定时唤醒 Agent）+ auto_continue（任务未完自动续跑=条件触发） |

**五类齐活的两个生产系统对照结论**：⑤ 事件触发是"自主 Agent"与"被动助手"的分水岭（有无它 = Agent 有没有自己的时间轴）；③ 协作工具决定架构上限（单 Agent 优先原则下，协作工具是"证明单 Agent 不够"之后的出路，见 agent AGENTS.md 红线 6）。

## 三、六原则 × 一手证据链（每条：主张 → 出处 → 本项目实证）

### 3.1 专用工具 vs Skill + 通用执行器

- **主张**：参数复杂/稳定/弱模型 → 专用 schema 工具；变更频繁/简单参数/强模型 → 自然语言 Skill + code_interpreter/shell 执行
- **一手**：Anthropic《Writing tools for agents》(2025-09-11)；《Advanced tool use》(2025-11-24) 的 Tool Search 与 examples **不兼容**（deferred 模式不能带 examples）——官方建议用 **skill 文件承载示例**（context engineering 实现同效）
- **本项目**：`~/.config/opencode/skills/` 60+ skill = Skill 路线（讲透Skills E2 实测渐进披露省 93.1%）；agent_host 13 schema 工具 = 专用路线——**两路线同仓共存**，判据不是信仰是任务形态
- **判据三问**：参数复杂度？变更频率？模型能力（弱模型需 schema 引导——与 Harness-Bench harness dependence 互证）？

### 3.2 粒度：整合与分离

- **主张**：功能相似+场景重叠 → 合并（`read_document` 统一 PDF/DOCX/PPTX）；参数集差异大/频率极高/需专门反馈 → 分立；>100 工具选择困难
- **一手**：Anthropic 案例——`schedule_event` 替代 `list_users+list_events+create_event`；`search_logs` 替代 `read_logs`；`get_customer_context` 聚合三工具。**整合的深层语法：工具名对准任务的自然子分区，把 agentic 计算从上下文搬回工具内部**
- **本项目**：agent_host 的 agent_lint/test/smoke/eval 四件分立——分立理由=反馈形式不同（exit code/schema 校验/冒烟/成本对比）+使用频率分层（L1 常用 L4 罕用），正是"需专门反馈→分立"的正例

### 3.3 通用性：通用工具优先，除非有明确理由

- **主张**：code_interpreter 而非四则运算器；理由=利用 LLM 代码生成元能力；边界=安全/权限/性能/平台差异
- **一手**：Anthropic《Code execution with MCP》：MCP 工具按需加载 150K→2K tokens（**-98.7%**，论述"两个数量级"的原始出处）；Cloudflare Code Mode：整个 API 面通过 `search()/execute()` 两工具暴露 ~1K tokens
- **本项目**：agent_host 的 `run_verify`（通用 shell）+ 12 专用工具的混合架构——通用工具兜底，专用工具收口高频路径

### 3.4 描述的艺术："何时用" > "能做什么"

- **主张**：使用场景/边界条件/具体参数例（`2024-03-15T14:30:00Z` 而非"RFC3339"）/返回值结构/执行代价/调用示例
- **一手（三连数字）**：Anthropic Tool Use Examples：复杂参数准确率 **72%→90%**（1-5 个示例/工具）；Claude Sonnet 3.5 的 SWE-bench Verified SOTA 靠"precise refinements to tool descriptions"（措辞级改动，非架构）；SWE-agent ACI 消融：好接口 vs 裸 bash 的差距=模型换代的差距
- **本项目**：02 章 E 实测（好描述 96.2% vs 模糊 46.4% vs 误导 5.7%）——描述质量 90pp 差距是本仓最早的工具实验（2026-08-15 前），与 72%→90% 互证
- **调试铁律**：Agent 选错工具 → **先查描述再怪模型**

### 3.5 保真性：模型感知的世界 = 工具操作的世界

- **主张**：静默输入转换/静默参数注入是反模式——"智能修正"破坏模型对工具行为的预测力，引发不可诊断的失败循环
- **一手**：agentpatterns.io ACI 词条（2026-06-13）的 **hidden failures** 失败模式："中间件在 Agent 看到之前拦截错误，会阻止 Agent 学习——工具吸收了本该由它学习的信号"
- **本项目（正面教材）**：agent_host 的 **tool-call repair**——模型吐纯文本工具调用时三语法解析升格执行，但**每次升格都打 `[repair]` 账本日志**（语法类型+数量）——它做了"转换"却拒绝"静默"：**转换可以，必须在账本上**。这是保真性原则在修复层的正确落地（openclaw 同款思想）
- **反例自查**：本卡写作中 snip 包装器对输出注入过滤——若它静默改写命令语义即是违规；它的实际行为（passthrough 提示）是合规的

### 3.6 三代演进：API 封装 → ACI → 动态发现+代码编排

| 代 | 时间 | 核心思想 | 一手锚点 |
|---|---|---|---|
| 一 | ~2023 | 直接 API 封装，粒度过细 | 02 章 §3.1 自由文本时代（参数完整率 54.3%） |
| 二 | 2024 | **ACI**：工具对准 Agent 目标而非底层 API | SWE-agent（arXiv:**2405.15793**，NeurIPS 2024）四原则：动作紧凑/反馈 informative but concise/guardrails 防错误级联/ACI 即行为边界 |
| 三 | 2025-2026 | 单工具之上的**发现×调用×编排** | Anthropic 三件套（2025-11-24）：Tool Search Tool（Opus 4 **49%→74%**，token -85%）+ Programmatic Tool Calling（GIA 46.5%→51.2%，token -37%）+ Tool Use Examples（72%→90%）；Cloudflare Code Mode（V8 isolate 沙箱） |

**2026-08 后续信号**：SWE-agent 官宣被 **mini-swe-agent** 接棒（maintenance-only）——极简接口反向吞噬重接口，ACI 自己也在"粒度"原则下自我修正；IATs（Interactive Agent Tools，arXiv:2610.16165 系）把交互式工具（debugger）多任务化——②执行类工具的进化前沿。

## 四、批判：五类框架的两个盲点（本文独立贡献）

1. **验证工具没有位置**。agent_host 13 工具里 7 个是验证类（lint/test/smoke/eval/graph 三查）——按五类归"②执行"（会跑命令）也说得通，但设计关键完全不同：感知防上下文爆炸、执行防不可逆破坏，**验证防 Goodhart（指标被 gaming）+要求 exit code 即证据**。五类框架诞生于通用助手语境（chatbot 视角），生产 coding agent 语境里验证是第一公民。建议六分法：**感知/执行/验证/协作/沟通/触发**——与讲透Harness 六组件的 V 独立成组件同构。
2. **"协作工具"掩盖了协议分层**。spawn_subagent（进程级）与 MCP/A2A（协议级）被混在一类；MCP 案例见讲透Agent/Agent框架案例/MCP协议生态全景（工具级成熟快于 agent 级=综述共识）。

**ACI 自身的失败模式四条**（agentpatterns，2026-06，防 worship）：over-specialization（工具过拟合某模型怪癖，换代即废）/ hidden failures（§3.5）/ abstraction overhead（ACI 层维护面＞收益）/ constraint mismatch（绝对路径约束在容器/跨平台塌方）——**ACI 必须对着真实轨迹迭代，不是设计一次**。

## 五、一手资源地图（本轮全部核实，2026-08-26）

| 资源 | 类型 | 核实方式 | 关键数字 |
|---|---|---|---|
| SWE-agent: Agent-Computer Interfaces (arXiv:2405.15793) | 论文 NeurIPS 2024 | websearch 多源（DOI/NeurIPS 官方/自维护文档） | ACI 命名；四原则 |
| Anthropic《Writing tools for agents》2025-09-11 | 工程博客 | websearch 全文 | schedule_event 粒度案例；25K token 工具响应上限 |
| Anthropic《Code execution with MCP》 | 工程博客 | websearch 全文 | 150K→2K（-98.7%）；Cloudflare Code Mode |
| Anthropic《Advanced tool use》2025-11-24 | 工程博客 | websearch 全文 | Tool Search 49%→74% / -85%；Examples 72%→90%；PTC -37% |
| Anthropic《Effective context engineering》2025-09-29 | 工程博客 | websearch 全文 | just-in-time 检索；tool result clearing |
| agentpatterns.io ACI 词条（2026-06-13 reviewed） | 实践知识库 | websearch 全文 | HCI↔ACI 映射；ACI 失败模式四条；Composio 10× |
| mini-swe-agent 接棒公告 | 官方文档 | swe-agent.com/latest | SWE-agent 进入 maintenance-only |
| （论述中的 72%→90%/"两个数量级"/">100 工具"） | — | **全部找到一手出处**（上表），无凭记忆引用 | — |

## 六、与本项目的网（改这里先读 README）

- **上游**：[02-工具调用工程](./02-工具调用工程.md)（描述/schema/粒度/MCP/Code Action 的实验层——本卡的"怎么写描述"细节在那）；[讲透Prompt/03 结构化输出](./讲透Prompt/03-结构化输出与函数调用.md)
- **平行**：[讲透Skills](./讲透Skills/README.md)（3.1 专用vs Skill 的 Skill 侧全解）；[讲透Harness](../讲透Harness/README.md)（T 组件在六组件中的位置；§2.1 工具表=其 Ch11 活案例）；[讲透Context](../讲透Context/README.md)（3.3 通用性的 token 经济学=其 Ch04 组装）
- **下游**：[deepseek-agent-harness/](../deepseek-agent-harness/)（13 工具活案例）；[讲透Agent/05-自进化延伸](./05-自进化延伸.md)（Skill 库当工程对象=进化闭环素材）
- **未核实不用**：论述提及的 Simple Notes / Advanced JSON Cards（记忆工具具体指称）未找到独立一手出处，不展开；IATs 的 arXiv 号在检索中仅见残缺引用（"2610.16165"非完整 ID），**按铁律不凭记忆补全**，标"待核"

---
生成：2026-08-26 · 网络资源 8 项一手核实（websearch 全文）· 本项目实证两大活案例逐工具归档 · 遵循证据宪法（arXiv ID 不凭记忆；无出处的论述性命名明示"待核"）
