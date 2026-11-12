# 讲透 NeMo Agent Toolkit（NVIDIA/NAT）

> understand-anything 全链知识库：NVIDIA NeMo Agent Toolkit——NVIDIA 的多智能体编排框架（前身 Agent Intelligence Kit/AIQ），单仓 34 包 uv workspace，注册表中心制 + entry-points 仓外注册 + agent-first 文档体系。

## 全链状态表

| 阶段 | 状态 | 产物 |
|---|---|---|
| understand 图谱 | 完成 | 仓内 `.understand-anything/knowledge-graph.json`：**8250 节点 / 17475 边 / 16 层 / 16 步 tour**，validator 0 issues 0 warnings，fingerprints 2507 文件 @c7e1162a |
| layers | 完成 | 16 层全覆盖 2535/2535 file 级节点，零重复 |
| tour | 完成 | 16 步：门面→builder/注册表→数据模型→前端/中间件→供给→安全→CLI→可观测→评测→适配器→协议出口→技能→示例 |
| onboarding | 完成 | `onboarding/ONBOARDING.md`（9600 不计空格字符，70 行号锚全源码验证，8 节，含 entry-points 仓外注册与 agent-first 专节） |
| explain | 完成 | `explain/` 10 篇 / 48024 不计空格字符 / 347 唯一行号锚，终验 0 坏锚（消歧感知验证） |
| README | 完成 | 本文件 |

## 图谱规模

- 2535 个 file 级节点（file 1767 / config 351 / document 365 / service 44 / pipeline 5 / table 3）+ 5715 个类/函数级节点 = 8250
- 17475 边；包分布：nvidia_nat_core 629（心脏）> langchain 107 > app 92 > profiler 73 > eval 68 > mcp 54 > atif/security 各 53 …共 34 包；examples 640；docs+skills 180；工程外壳 157

## explain 索引（10 篇，字数=不计空格字符，锚=唯一行号锚）

| 篇 | 主题 | 字数 | 锚 | 文件 |
|---|---|---|---|---|
| 01 | core 注册表+workflow 引擎 | 4786 | 52 | `explain/01-builder-and-workflow-engine.md` |
| 02 | 中间件体系 | 4785 | 45 | `explain/02-middleware-chain.md` |
| 03 | front_ends 前端入口 | 4798 | 38 | `explain/03-front-ends.md` |
| 04 | 框架适配器（react/rewoo/router_agent） | 4796 | 46 | `explain/04-frameworks-langchain.md` |
| 05 | MCP 集成 | 4784 | 25 | `explain/05-mcp-integration.md` |
| 06 | 评测体系与 ATIF | 4771 | 40 | `explain/06-evals-atif.md` |
| 07 | skills 体系与 agent-first | 4794 | 20 | `explain/07-skills-agent-first.md` |
| 08 | examples 生态 | 4800 | 40 | `explain/08-examples-ecosystem.md` |
| 09 | 可观测性与 profiler | 5120 | 23 | `explain/09-observability-profiler.md` |
| 10 | 认证与安全 | 4590 | 18 | `explain/10-security-defense.md` |

## 架构一页纸

```
config.yml（_type 万能键）
   │
   ▼
WorkflowBuilder.from_config ──► GlobalTypeRegistry（type_registry.py:1423）
   │  ▲ entry-points 装机注入（loader.py:128，六组名 nat.plugins/nat.components/…）
   │  │   34 个 nvidia_nat_* 包各自 pyproject 声明，core 零框架依赖
   ▼  │
Builder 装配（builder.py:75：llm/tool/embedder/memory/retriever/middleware…）
   ▼
Workflow（workflow.py:39）──► 中间件洋葱圈（middleware.py:118 pre/post_invoke）
   ▼
front_ends：fastapi（OpenAI 兼容路由）/ console / MCP（name="mcp"）/ A2A / A365
   ▼
横向能力：ATIF 评测（轨迹→确定性事实）· profiler 计费 · OTEL 可观测 · data_flywheel 回流
```

## 甄别清单（诚实记录，写作线源码级实证）

**图谱构建层**：
1. **merge 丢弃 219 条函数级边**：符号级（class/function 精确名）与 file 级节点 ID 前缀不一致导致悬空，按规则诚实丢弃，未做符号→文件强行回填（避免伪边）。imports 主链 5461 条完整保留。
2. **Git LFS 指针文件**：examples/advanced_agents/alert_triage_agent/data/ 下 benign_fallback_offline_data.json、offline_data.csv/json、maintenance_static_dataset.csv 等大文件本地为 LFS 指针壳（sha256+size 元数据），批分析已甄别标注「真实内容需 git lfs pull」，图谱节点按指针文件建档。
3. **aiq_ 前缀兼容层**：loader.py:138 明言保留 aiq entry-points 组向后兼容（NAT 前身 Agent Intelligence Kit），仓内大量 aiq_ 类名是血脉化石非新特性。
4. **src/nat/__init__.py 无独立节点**：scan 阶段未产生独立 file 节点（包初始化并入包级语义），非缺失。
5. **层归属口径**：nvidia_nat_core/tests 168 个测试文件归 L02（核心运行时层）而非独立测试层；examples 按主题切 L15（编排与框架）/L16（专题与工程化）。

**源码甄别（explain/onboard 写作线触发勘误条款，均以源码为准）**：
6. **ATIF 全称勘误**：是 **Agent Trajectory Interchange Format**（trajectory.py:16 docstring、atif/__init__.py:16、atif_converter.py:15 三处一致），「Agent Tool Interaction Format」为讹传；ATOF=Agentic Trajectory Observability Format。
7. **router_agent 存在但不在 agent/ 目录**：`control_flow/router_agent/register.py:30` RouterAgentWorkflowConfig——NAT 用目录边界区分「agent=可复用求解函数」vs「control flow=编排节点」；responses_api_agent 的 config 继承 FunctionBaseConfig 而非 AgentBaseConfig（register.py:34）。
8. **cron 前端是空壳**：front_ends/cron/__init__.py 全文仅 14 行 license 头，本版本无代码。
9. **MCP tool_converter 方向勘误**：`tool_converter.py` 只服务 server 方向（NAT function→MCP tool）；client 方向的转换在 client_impl.py:487（mcp_session_tool_function→FunctionInfo.create）。IntrospectionTokenVerifier 实际支持 jwks/introspection/discovery 多模式。
10. **FastAPI 前端三角色分工勘误**：plugin 是父进程编排者（dask+临时 YAML+环境变量+启 uvicorn），app 由 worker 在子进程 build_app（fastapi_front_end_plugin_worker.py:103）；controller 不做请求分发，是 OAuth 回调临时服务器的生命周期管理器。
11. **detect_llm_frameworks_in_build_fn core 版是 stub**：workflow_builder.py:98 为 ImportError 降级实现（返回空表），真身在 nvidia_nat_profiler/utils.py:36（inspect.getsource 源码级扫描）；core 对 profiler 包零硬依赖。
12. **core/profiler/{callbacks,forecasting} 是空壳目录**：实现整体在 nvidia_nat_profiler 域包，core 只留 __init__ 骨架。
13. **data_flywheel 与 ATIF 无耦合**：全包 grep 零 ATIF 引用，飞轮走 OTEL Span→TraceContainer→TraceAdapterRegistry→ES exporter 独立线，与 ATIF 评测线只在观测源头共享。
14. **脚手架模板实为五个**：workflow_commands.py:237 起渲染 workflow.py.j2/config.yml.j2/register.py.j2/pyproject.toml.j2/__init__.py.j2（常被误记四个）；register.py.j2 模板全文仅 4 行（一行导入触发注册）。
15. **HITL 中间件无 register 三件套**：`middleware/register.py:18-22` 只统一挂接 cache/circuit_breaker/dynamic/logging/timeout 五族；hitl/ 目录无 register.py，HITLMiddleware 核心包生产代码零实例化（仅测试 test_hitl_middleware.py:46），是供继承的抽象层；examples/HITL 实际路线=把审批做成普通函数（hitl_approval_tool.py:32，由 por_to_jiratickets 示例包提供，兄弟示例经 pyproject 依赖+uv.sources editable 复用——示例生态存在真实包间依赖链）。
16. **cache 是全库唯一默认 is_final=True 的中间件**（cache_middleware.py:93，命中即终结整链）；流式路径 `ctx.output = None` 是 chunk 压制哨兵，与单次调用 SKIP 短路返回 None 构成 None 的双重语义。
17. **examples 文件数口径差**：盘上实测 692 个文件 vs 图谱 640 个 file 级节点（.understandignore 裁掉 52 个，含 LFS 数据等）——引用时须注明口径。

## 上手

```bash
cd /usr-data/data2/repos/agent-repos/NVIDIA/NeMo-Agent-Toolkit
uv run nat --help
uv run pytest packages/nvidia_nat_core
```

新 workflow：`uv run nat workflow create`（模板 cli/commands/workflow/templates/*.j2）。
最小示例解剖：`examples/getting_started/simple_calculator/`（config.yml+register.py+pyproject 三件套）。

## 生成元数据

- 生成时间：2026-11-10；commit c7e1162a；工具链：understand-anything（scan→import-map→batches→merge→layers/tour→finalize→onboard→explain）
- 派发：批分析 59 批产物（tmp/ 归档）；explain 10 篇=4 个子代理×2 篇+主会话 2 篇，行号锚消歧终验 0 坏（主会话独立复验抓出并修正 3 处子代理偏差锚：start.py:222 空行、register.py.j2:29 越界、middleware register.py:16-20 偏移 2 行）；onboard 主会话撰写并按子代理甄别结论二次回灌修正（ATIF 全称/router_agent 归属/HITL 三件套三处）
