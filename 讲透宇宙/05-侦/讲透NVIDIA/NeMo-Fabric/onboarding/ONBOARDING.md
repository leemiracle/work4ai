# NeMo-Fabric 仓内导览（ONBOARDING）

> 仓库：NVIDIA/NeMo-Fabric @ 86f86882（v0.6.0，2026-11 图谱：1367 节点/1825 边/15 层/16 步 tour）
> 定位：**跨 agent 框架的统一运行时与工具适配层**——应用、评测系统、rollout 平台经由它驱动 17 个 harness。

## 一、项目定位

Fabric 解决 agent 生态的 N×M 爆炸：上游 M 家应用/评测/rollout 平台，下游 N 个 agent harness（Claude Code、Codex、OpenCode、Hermes……），两两直连要 M×N 份胶水。Fabric 中间放一层**版本化契约+适配器**：上游写一份 FabricConfig，下游每 harness 一个适配器，复杂度降为 M+N。

README.md:17 钉版定位，四能力（README.md:21-24）：**Compose** 统一配置 models/tools/skills/MCP/runtime、**Validate** 执行前检出不支持的配置、**Switch** 换 harness 不改消费者集成、**Compare** 归一化 results/errors/artifacts/telemetry。下游矩阵在 README.md:27 起表格：**17 行 harness**（Claude Code/Cline/Codex/Factory Droid/Hermes/Kilo/AWS Kiro/AWS Strands/LangChain Deep Agents/mini-SWE-agent/NOOA/OpenClaw/OpenHands/OpenCode/Pi/Qwen Code/Remote Agent），标注 Tool Policy/MCP/Skills/Telemetry 四列支持度。注意 README 行文说"16 个"，实测表格 17 行——以表为准。

仓库是 **Rust+Python+TS 三语言 monorepo**：Cargo workspace 四成员（Cargo.toml:4-12：fabric-core/fabric-cli/fabric-python/environment-providers/openshell），Python uv workspace（sdk/python 三包+adapter-contract），TS npm workspace（adapters/typescript）。justfile 629 行统一任务入口。发布面：crates.io/PyPI/npm/fern 文档站；.gitlab-ci.yml 双仓协同——GitLab 不重复构建而是等 GitHub Actions 产物再收集发布。

## 二、契约权威源：JSON Schema

一切从 schemas/ 开始。**SCHEMA.md:8-10 钉版：文件由 Rust core 类型生成而非手编**，改 Rust 类型必须重新生成，且"各语言绑定与 parity 测试同一提交内更新"（SCHEMA.md:13-15）。

两组共 27 个 schema：`schemas/adapter-contract/` 11 个南向（adapter-descriptor、agent-config、agent-run-request/result、adapter-check-request/result、openai-stream-invocation/record、runtime-context、adapter-invocation、adapter-target-descriptor，SCHEMA.md:31-42）+ `schemas/sdk/` 16 个北向（agent/run-plan/run-result/fabric-event/environment-handle 等）。生成器 schema.rs：SchemaName 枚举 27 项（schema.rs:26），`SchemaName::ALL`（schema.rs:86）稳定输出序，write_schema_snapshots（schema.rs:266）落盘。图谱 27 条 defines_schema 边即"生成器→快照"。

SCHEMA.md:46-48 钉投影链："FabricConfig 是北向意图源；规划产出 CapabilityPlan 作为路由证据；descriptor 接受的字段投影进 AgentConfig——南向适配器输入的权威形态"。南向契约版本 `fabric.adapter/v1alpha2`（fabric-core/src/adapter_contract.rs:10），18 个扩展块由 AdapterExtensionPoint 枚举声明（adapter_contract.rs:17-54）。

双语言实现刻意不对称：**TS 机器生成**——generate.mjs（466 行）从仓内 schema 编译出 8 个 generated/*.ts，`--check` 模式（generate.mjs:26）CI 字节级防漂移，projection-guards.mjs:6-32 钉死 AgentRunResult 条件结构，stable.test.ts:55-60 用 @ts-expect-error 测不变式；**Python 手写**——零依赖（pyproject.toml:27 dependencies=[]）三文件：models.py 706 行 33 类 dataclass（ContractModel 基类 models.py:73，__setattr__ 拦截使构造后也绕不过校验 :86-103）、codec.py 311 行往返引擎（_decode_value :173）、pydantic_support.py 42 行可选桥（方向永远 Pydantic→dataclass）。

## 三、fabric-core：语言中立内核

lib.rs:6-19 声明 14 个子模块，三种语言下游实现皆其同构翻译。config.rs **7535 行**与 runtime.rs **6629 行**占核心近三分之二。

**config.rs**：FabricConfig 顶层 16 字段（:32-78，extensions 用 flatten 收容未知字段保前向兼容）；AdapterDescriptor（:324）声明适配器身份；解析链 load_adapter_descriptor（:1856）→ resolve_run_plan_from_config（:2399）→ inspect_adapter_config（:2441，不探测可执行位置）→ resolve_diagnostic_plan（:2492，doctor 用）。**runtime.rs**：公开契约 RunRequest（:99）/RunResult（:131）/FabricEvent（:314）与三类 handle（:342/:372/:421）；私有 trait RuntimeAdapter（:840）双实现——LocalHostAdapter（:860，本地子进程宿主，适配器环境变量只留内存不进序列化 handle :877-879）与 OpenShellRuntimeAdapter（runtime/openshell.rs）；函数族 run_plan（:900）/prepare_environment（:931）/start_runtime（:1195）/invoke_runtime（:1208）/invoke_openai_stream（:1269）。

支撑：check.rs 1721 行（check_service :765/check_environment :897，HMAC+TCP）；error.rs 41 变体单枚举；environment.rs 1526 行（ProviderProcess mpsc+reader 线程，NEMO_FABRIC_OPEN_SHELL_PROVIDER 可覆盖）；resource_snapshot.rs 1289 行（进程树 CPU，reparent 下下降属预期）；system_stats/（cgroup.rs 788+sampling.rs 802，Measurement 严格三态：缺测=unavailable 不用 0）；time.rs 90 行无 chrono 自实现民用历。

**PyO3 绑定**（fabric-python/src/lib.rs 601 行）：_native 模块（:353-385）注册 19 函数+3 异常（:22-39）。三设计：全部 JSON 字符串进出（parse_* 家族 :567-601）；重活 py.detach 释放 GIL（:60 等）；错误语义映射（to_py_error :394-407：host_timeout→PyTimeoutError）。描述符发现走 data_path/share/nemo-fabric（:425），ADAPTER_PYTHON 指定适配器解释器、5s 超时查询（:449-522）。SDK 侧 _native.pyi 20 函数桩+client.py:56-59 降级 import；maturin 打包。

## 四、OpenShell 环境提供器

进程级沙箱执行面参考实现。**lib.rs 3397 行=全仓最大单文件**：主体约 2200 行+内联测试约 1200 行（37 个 test，L2200 起）——"自带全部校验与测试的单文件协议服务器"，单文件是刻意选择（安全组件可整体审计）。

协议：stdin/stdout 单行 NDJSON，版本 `fabric.environment-provider.v1alpha1`（lib.rs:27）。常量防线（:28-34）：请求 1 MiB、exec 输出 3 MiB、ready 60s/delete 30s/exec 30s/gateway 30s/总闸 600s。主循环 serve（:83-128）+三态流式读取器（:136-169，超大请求不 OOM 不失联）。七操作 ProviderOperation（:1204-1243：RuntimeCommand/CollectArtifacts/Prepare/Attach/Inspect/Exec/Release）；TaskCommand 四分支（:1245-1263：Check/Start/Invoke/Stop）与 fabric-core task_command.rs 同构——生命周期指令经宿主→提供器→沙箱三跳。

安全四闸：SandboxBinding 校验 provider 名/绝对路径/无 `..`（:1734）；verify() 每操作前比对沙箱 id 防替换（:1767）；validate_pinned_image 只收 sha256 钉版镜像（:1691）；read_artifacts.py 一次性脚本读工件——16 文件/256 KiB/512 KiB 硬限（脚本 L16-18），O_NOFOLLOW，"持久 runtime server 不参与"。main.rs 25 行薄壳只收 `serve --stdio`，宿主按需拉起。调用侧配对 runtime/openshell.rs:4-9 分工：宿主"投影配置、发命令、校验响应、收集工件"，提供器"管 gateway 与沙箱"，沙箱内"runtime server 与适配器执行"；宿主 BINDINGS 注册表按 gateway+workspace+sandbox_id 组 key（:38-58）。

## 五、fabric CLI 与脚手架

crates/fabric-cli 1790 行五模块。命令树（app.rs:27-53）：preset list|show / example list|show|init / plan / doctor / run --input / version。Selector 用 ArgGroup 钉死 --preset/--example 互斥必选（app.rs:91-96），--variant 只配 example、--model/--temperature 只配 preset——参数合法性全在解析层解决。

五个内置预设（presets.rs:139-165）：**scripted**（零凭据确定性冒烟，自带 run.py 假 harness）/hermes/claude/codex/deepagents，后四个需 NVIDIA_API_KEY 指向 `https://integrate.api.nvidia.com/v1`（presets.rs:26）。预设内联工程判断：claude 设 permission_mode=dontAsk（:182-186）、codex 关 apps/multi_agent/plugins/web_search（:204-216）。descriptor 全 include_str! 编进二进制（:16-25）+ StagedAssets RAII 临时目录（assets.rs:31-47/:59-62 Drop 自动清理）——单二进制自足、离线可冒烟。

脚手架 scaffold.rs：example init 生成可编辑工程（python/rust 双模板 :16-20）；目标存在直接报错防覆盖（:51-56）；rust_core_dependency（:112-131）探测本地 ../fabric-core 生成 path 依赖（贡献者改 core 即生效）否则版本依赖。EXAMPLES 目前 code-review 一个（examples.rs:121），五变体对照五 harness（:29）。

## 六、Python SDK 三发行包与 runtime_server

1. **nemo-fabric-runtime**（主包 11471 行，依赖仅 httpx/pydantic/typing-extensions）：Fabric 类（client.py:68）15 方法覆盖全生命周期（check :91/plan :205/doctor :244/run :285/start_runtime :334/prepare_environment :402/start_runtime_in :526/prepare_service :804 等）；run 支持 expected_descriptor_sha256 拒绝 descriptor 漂移（:294-295）；健康探活专用 4 线程池（:64）不被长调用饿死。双模型层：models.py 1387 行 34 类 Pydantic 写作面 + types.py 2642 行 43 类冻结读取面。
2. **nemo-fabric-collector**（1460 行）：独立遥测采集服务，app.py 1266 行，starlette+uvicorn。
3. **nemo-fabric-adapter-catalog**（零依赖）：catalog.json 2792 行捆 18 adapter+2 target；get_adapter_descriptor（__init__.py:32）钉版"release snapshot, not a capability check；不 import 适配器代码不注册 runner"——元数据与执行注册彻底分离。

**runtime_server=沙箱内命令桥**：入口 fabric-agent-ctl（pyproject [project.scripts]），五件套 cli/protocol/transport/state/health。protocol.py 是线格式宪法：INTERFACE_VERSION=2（:13）、请求 512 KiB/响应 4 MiB（:14-15）、SOCKET_PATH=/sandbox/fabric.sock（:19）、五操作 start/invoke/stop/serve/check（:20）；MESSAGES 字典（:23-51）钉死固定文案，ProtocolError（:61）"永不包含请求值或原始异常"防宿主信息泄漏；runtime_exists 保留 v2 旧码兼容旧镜像（:43-44）。cli.py read_input（:29-66）stdin 走 select+10s deadline。openai_streaming.py 788 行本地回环+secrets 令牌实现零依赖 OpenAI 兼容桥。

## 七、适配器双语矩阵

**Python 群 10 目录**（9 适配器+common）：openclaw、codex、claude、deepagents、hermes、mini-swe-agent、nooa（含 bench-agent/arc-solver）、openhands、remote-agent。**TS 群 9 目录**（8 适配器+common+scripts）：opencode、cline、droid、kilo、kiro、pi、qwen、strands。合计 17 个适配器=README 表 17 行。接入文档 docs/integrations/ 19 篇（harness 17+consumer 2）+契约教程 docs/adapter-contract/ 六篇。

两侧 common 是全部适配器的地基。Python common（2516 行）核心 lifecycle.py 888 行：AdapterRuntime Protocol 三钩子（lifecycle.py:43-62），适配器一行接入——`lifecycle.serve(HermesRuntime, config_loader=AgentConfig.from_mapping)`（hermes/adapter.py:46）；serve() 把进程 stdout 整体重定向 stderr（lifecycle.py:877-878），意外 print 毁不了协议流。utils.py 792 行 30+ 访问器+ambient relay 拒绝链（:317/:355/:369 防遥测劫持）。TS common（npm 包 1156 行）镜像对称：lifecycle.ts 448 行 ajv 校验；**acp-runner.ts 464 行是 Python 侧没有的 ACP 会话引擎**——三级超时（:43-58）、权限收窄 allow_once|deny（:27 永不自动放行）、terminateProcessTree（:120）；model-endpoint.ts 严格正则白名单化明文 HTTP 主机（:9-19）。

参考外部适配器 external/nat（NeMo Agent Toolkit，adapter.py 972 行全量翻译示范）。消费侧 integrations/harbor/fabric_agent.py 1082 行译 Harbor 任务为 FabricConfig。examples/ 端到端场：code_review_agent（16+ 变体对照）、langgraph_custom_agent、openshell、system_stats、notebooks、harbor 三基准（calculator/nooa_bench/swebench Docker 化）。API 参考自动生成勿手改：rust-library-reference 198 个 .mdx+python 11 个 .md。

## 八、陷阱与勘误（源码实证）+ 上手路线

1. **仓内 skills=agent-first 迄今最完整的发布生命周期套件**：`.agents/skills/` 19 项（18 个维护者技能+README）覆盖贡献（contribute-api/adapter/docs、prepare-pr、validate-change）→测试（python-tests）→CI（maintain-ci）→打包（maintain-packaging、update-project-version）→**发布全链**（prepare-code-freeze、create-beta-tag、create-rc-tag、create-release-tag、draft-release-notes、check-release-deployments）；顶层 `skills/` 另有 2 个**对外导出**技能 nemo-fabric-build-adapter/nemo-fabric-integrate（各带 SKILL.md+BENCHMARK.md+evals/）。两层纪律由 AGENTS.md 钉版：维护者集可引用仓内细节、集成集只依赖公共契约。
2. **图谱勘误：scanner 对 namespace 包盲区**——`nemo_fabric_adapters.*`/`nemo_fabric.*` 命名空间包跨子包 imports 几乎全空，297 条 imports 边全部由批分析 worker 源码重扫补齐。引用图谱 imports 须知这层人工兜底。
3. **单文件巨石三处**：openshell lib.rs 3397（主体 2200+测试 1200，刻意）、config.rs 7535（74 类/110 函数几乎全是 JsonSchema 派生）、runtime.rs 6629（60 类/133 函数）。先读契约区再按需读过程区。
4. **test_deepagents.py 2686 行**=全仓最大测试（tests/adapters/ 30 个之一）；tests/ 五路矩阵：adapters/python/e2e 26 个/fixtures/专项；test_installed_adapter_discovery.py 真实 venv+pip install 装 wheel 再断言发现路径。
5. **文档口径**：README 行文"16 个 harness"vs 表格 17 行，以表为准。
6. **勘误精选**：openclaw 跨平台进程树清理双实现（Unix PDEATHSIG/Windows Job Object）；Cargo.toml 依赖注释每项写明理由（jsonschema 禁用 $ref 检索抵御不可信 schema）；nooa telemetry scope 未还原即禁用后续遥测；e2e 的 swebench trajectory.json 单文件 43.6 万行仅头部可用。

**上手路线**（六步）：①quickstart 跑 `nemo-fabric run --preset scripted`（零凭据冒烟）→②schemas/SCHEMA.md 理解"一份契约三种投影"→③fabric-core lib.rs 模块地图+adapter_contract.rs（100 行最快全景）→④lifecycle.py 的 serve/AdapterRuntime 看适配器一行接入→⑤docs/integrations/harness/ 挑自己的 harness 读适配器→⑥需要沙箱执行再进 OpenShell 对文件。配套 explain 12 篇：01-06 核心线（本文各节展开），07-12 外围线。
