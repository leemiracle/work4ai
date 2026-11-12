# 11 · 测试金字塔：Unit/Integration 重组与 YATU 卡

## 角色定位

tests/ 是 238 个 py 文件（Unit 223 + Integration 7 + Config 5 + 根 conftest/fakes）加 14 张 YATU md 卡。结构按**目录即层级**重组过：Unit/ 下 13 个域子目录（backend/config/core/eval/filesystem/frontend/integration_contracts/messaging/monitor/platform/sandbox/scripts/storage），Integration/ 只收真边界测试。Integration/README.md 把规矩写死："must exercise real integration boundaries without mocks, fakes, or monkeypatch"——被 mock 的 router 壳和窄契约探针**必须**放 Unit/integration_contracts/。金字塔顶层则是 YATU 人肉验收卡。

## 内部结构

**Unit/integration_contracts/ 是本仓最有性格的目录**（26 文件）。代表作 `test_agent_config_runtime_source_boundary.py`（12 个测试）：用 `inspect.getsource` 抓源码文本再做字符串断言——如 :29-33 断言 `LeonAgent._init_services` 源码 **不含** `"self.config.skills"` 且 **含** `"resolved_skills"`；:44-46 断言 AgentLoader.load 无 `mkdir`；:84-90 断言 cost monitor 无 `config.user_paths`/`pricing_cache.json` 等用户目录缓存源。这套"源码守护"把架构决策（runtime 只读 resolved 配置、不落用户 home）变成可回归的断言。更妙的是 :21-22 的禁词拼接：`blocked_arg = "agent_config" + "_dir"`——测试文件自身不能出现被禁字面量，否则守护测试自噬。monitor 域 14 个测试文件中 `test_monitor_detail_contracts.py`/`test_monitor_evaluation_scheduler_boundary.py` 等延续同一命名法，靠 monkeypatch 假件（FakeBatchService、InMemoryMonitorOperationRepo，test_monitor_detail_contracts.py:46-73）锁 use_case 与 infrastructure 的边界。

**哨兵路径测试（schema 防fork）**：`test_cli_minimal_deploy.py:11` 定义 `REJECTED_SCHEMA_FORK_PATH = storage/schema/local_communication.sql`，:34-35 断言它**必须不存在**，:22-31 扫全部 compose 文件的 volumes 断言无人挂载它，:38-42 钉死 cli-minimal 恰为五服务集合，:86-112 真跑 generate-env.py 子进程并用 jwt.decode 验签。`test_app_schema_discipline.py` 补三条：manifest 的 baseline+patches 必须**精确等于**目录下实际 *.sql 集合（:23-31）；baseline 含六个 CREATE SCHEMA/表且表数函数数与 manifest 计数一致（:34-50）；`scripts/check_app_schema.py` 拒绝 schema 子目录（schema 必须扁平，:59-73）且是响亮 CLI 门（:76-86 输出 "App schema check passed."）。**"不存在性"也能被测试钉住**——被拒的 schema fork 只要复活立刻红。

**命名迁移钉子**：`test_chat_session_row_contract.py` 恰好 3 个测试钉 `sandbox_runtime_id`：create 返回它（:4-17）、get 返回它（:20-40）、`PRAGMA table_info(chat_sessions)` 列集合必须含它（:43-60）。runtime 身份从旧 session 命名迁到 sandbox_runtime 后，旧列名回潮会立刻被这三连击破。

**共享假件**：`tests/fakes/supabase.py`（166 行）FakeSupabaseQuery 实现链式 select/insert/upsert/update/delete/order/limit，内存表按 (column, op, value) 过滤——Supabase 仓储层单测全部复用它，不引第三方 mock 库。

**Integration/（7 文件）**：chat_app_router、chat_external_user_contract、chat_first_screen_owner_threads、daytona_e2e、e2e_summary_persistence、relationship_router、users_router——全是跨 router+存储+身份的真链路。

**YATU（tests/yatu/，14 张 md 卡）**：YATU = **You As The User**（README.md:3）。卡不是自动化脚本，是"给真人或 code agent 的产品验收剧本"（README.md:5）：必须走真实后端进程/真实浏览器/真实 cel CLI/真实 LLM（:7-12），**禁止** mock、DB 内窥、内部记忆搬运、直调 helper（:14-15）。每卡六要素：user story/entry surfaces/setup/user loop/pass bar/pitfalls（:26-33）。运行产物一律出仓存放（:19-22）。catalog.md 分族索引：Chat And Delivery 六卡、Relationship 两卡、Frontend 一卡、Managed Agents 一卡、Multi-Agent Workflows 等。最硬的一条原则（:35-36）：**卡跑得痛苦时不许给测试加私胶水，痛苦本身是产品/API 反馈，去修被测面**。

## 外部连接

CI（.github/workflows/ci.yml）跑单元层；e2e.yml 定时跑端到端但引用了 4 个幽灵路径（见 10 篇）。YATU 卡面向 cel CLI 与 frontend 两个用户面。fakes/supabase 与 storage/providers/supabase/* 的仓储实现构成假件-真件对偶。schema 哨兵测试与 deploy/cli-minimal 契约测试互相咬合（compose 内容变了两边一起红）。

## 数据流

一次典型回归：改 storage 仓储 → fakes/supabase 喂内存表跑 Unit/storage → integration_contracts 源码守护确认没引入禁词 → Integration 真边界测过 → 手动/agent 按 YATU 卡走一遍用户面 → 全绿才碰 deploy 契约测试（compose 五服务结构未破）。

## 设计决策（含批判）

- **源码字符串断言**：便宜、直接、能锁"不做什么"（负向约束），这是常规行为测试做不到的；批判：对重命名极度脆弱——变量改名导致守护失配时，报错信息只是"字符串不在源码里"，维护者要考古才知道当初禁的是什么（好在禁词拼接处有注释）。
- **不存在性哨兵**：把"被否决的方案"固化成永远的红线，是组织记忆的优秀载体；代价是新人不懂历史会以为这测试"永远 trivially 通过"而误删。
- **Integration 目录的零 mock 铁律**：与 industry 常见"integration 也可以 mock 外部 SaaS"不同，这里 mock 边界一律压到 Unit——目录名即诚实度承诺。
- **YATU 反向产品观**（"痛苦=反馈"）把 E2E 维护成本转化成 API 改进动力，是这个仓最值得抄的设计之一；风险是卡本身无人执行就退化成文档。

## 新人提示

1. 加 storage 相关测试先去 fakes/supabase.py 看链式 API 覆盖没覆盖你要的操作，别另起 mock。
2. 给 LeonAgent/loader 加配置读取时先读 test_agent_config_runtime_source_boundary.py 的 12 条禁令，否则 CI 会用一条不知所云的字符串断言教你做人。
3. 动 storage/schema/ 前跑 `python scripts/check_app_schema.py`：目录必须扁平、文件必须与 manifest 精确对账，local_communication.sql 是死路。
4. 想验一个用户故事，先翻 tests/yatu/catalog.md 找现成卡；没有再按六要素写新卡，产物放仓外。
