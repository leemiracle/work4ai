# NeMo-Agent-Toolkit-Examples 上手指南（ONBOARDING）

> 仓：`NVIDIA/NeMo-Agent-Toolkit-Examples`（commit `eadbb75`）。NeMo Agent Toolkit（NAT，包名 `nvidia-nat`）的**社区示例联邦仓**：11 个独立示例 + 一套主仓拷贝的 CI 防线。行号锚均对本地仓核实。

## 1. 仓库定位：NAT 官方示例联邦

README 双仓分工表：主仓示例围绕 toolkit 功能、随版本更新；本仓示例由社区用例驱动、**绑定特定 toolkit 版本**（`examples/currency_agent_a2a/pyproject.toml:35` 锁 `nvidia-nat[a2a,mcp,test]==1.6.0`）。每示例自包含、彼此零依赖，按 `uv pip install -e examples/<name>` 单独安装。

三类形态：全功能 agent 八个（`sandbox_agent` 约 3000 行源码 + 9 个测试文件为旗舰，其余 profiler/k8s/mcp_rag/unstructured/identity/x402/spraay）；纯配置示例三个（currency/kaggle/prometheus_avatar）；模板 `examples/.template/README.md`（CONTRIBUTING.md:78 贡献起点）。根 `pyproject.toml:4` 声明 `>=3.11,<3.13` 而 README 推荐 3.13，轻微不一致。数据文件走 LFS（`.gitattributes` 的 `examples/**/data/** filter=lfs`），必须 `git lfs pull`（见第 8 节）。

## 2. 贡献与 CI 防线：主仓拷贝的守门体系

`ci/scripts/` 整套拷贝自 NAT 主仓。入口 `ci/scripts/checks.sh:8-37` 串四段：pre-commit（ruff+yapf，规则在根 `pyproject.toml:24-77`）→ python_checks.sh（pylint）→ `copyright.py --verify-apache-v2` → documentation_checks.sh（vale+死链）。

`ci/scripts/common.sh` 是**上游残留活化石**：`common.sh:18` 注释仍写 "The root to the AIQ toolkit repo"（AIQ 是 NAT 前身）；`common.sh:22` 引用本仓不存在的 `packages/`、`tests/`（主仓布局）。贡献规则在 `CONTRIBUTING.md:51-106`：依赖版本至少两位（CONTRIBUTING.md:54）、Apache 2.0 兼容、每示例一目录。

## 3. sandbox_agent 全景：旗舰示例

体量最大，实现沙箱内执行代码/浏览/文件操作的 ReAct agent，对标 GAIA。入口 `register.py:118` 注册，配置类 `register.py:48` 暴露 llm_name/`max_iterations`(默认20)/`sandbox_config`（默认 Docker）。

经典两节点 ReAct：`register.py:235` 建 `StateGraph(AgentState)`，agent 节点（`register.py:191`）+`ToolNode`，条件边按 tool_calls 路由。迭代双保险：节点内查 iteration，LangGraph `recursion_limit = max_iterations*2+10`（`register.py:258`）；`finally` 保证 `sandbox.cleanup()`（`register.py:311-317`）。

GAIA 评测特化：最终回答过 `clean_answer_with_llm`（`utils/answer_cleaning.py:66`）压成短答案（GAIA 精确匹配）；观测上限按 1 token≈4 字符换算截断（`register.py:172`）。

## 4. 沙箱抽象与工具双轨

**沙箱层**：`base.py:62` 的 `BaseSandbox` ABC 定 5 个抽象方法，工作区常量统一（`base.py:26-36`）：`/workspace` 下 input/output/temp/downloads 四目录。`create_sandbox`（`factory.py:140`）按 docker/daytona 分派，实现类**函数体内 lazy import**（`factory.py:153`）；环境变量透传默认仅 `TAVILY_API_KEY`（`factory.py:27`）。`DockerSandbox`（`docker_sandbox.py:37`）用 `mem_limit`/`nano_cpus` 限资源；`DaytonaSandbox` 是云沙箱。

**工具层**双轨制（最值得抄的决策）：
- **沙箱轨**：shell/python/file_read/file_write/web_browse 五工具共享 `SandboxToolExecutor`（`executor.py:26`）与**同一** sandbox 实例，文件系统状态跨工具一致。shell（`execution.py:125`）与 python（`execution.py:148`）的 description 互相指路分工。
- **宿主轨**：web_search（Tavily）、web_fetch、image_describe——无需隔离，跑 agent 进程内。

汇合点 `tools/factory.py:28` 合并两轨；输出统一截断 16000 字符（`tools/common.py:22`）。

## 5. profiler 与 k8s：两条数据分析型 agent 路线

**profiler_agent**（分析 Phoenix 遥测的元应用）：手写三节点图——`agent.py:98-117` 建 agent/executor/response_composer，`conditional_edge`（`agent.py:76`）查 `exec_plan.tools` 队列路由。规划协议是**结构化 JSON 而非 tool calling**：LLM 吐 `ExecPlan`（`data_models.py:24`，`tools: deque[str]`）JSON，解析失败用 `RETRY_PROMPT`（`prompts.py:16`）重试（`agent.py:141`）。`update_state`（`agent.py:176`）match-case 按输出类型聚合进 `trace_infos`（`data_models.py:94`）。px_query 支持 last-n/时间窗（`tool/px_query.py:133-153`）结果落 CSV 传下游，response_composer（`tool/response_composer.py:51`）拼带内嵌图的 HTML；config.yml 还把 Phoenix 用作自身遥测后端。

**k8s_infra_monitor**（K8s 体检）特色是**离线/在线双模**：四诊断工具各带 `offline_mode`（如 `pod_health_tool.py:33`），离线按 query 内 `scenario_id` 取缓存（`pod_health_tool.py:58-63`），在线直接 kubectl（`pod_health_tool.py:79`）。场景集启动预载（`register.py:140-143`）。severity_classifier 不进图：`_analyze_cluster`（`register.py:109`）先拿诊断报告再追加 severity 分级（`register.py:129`，提示词 `prompts.py:39`）。`config_offline_mode.yml`（+ragas eval）vs `config_live_mode.yml` 双配置对照。

## 6. MCP 接入光谱：提供方与消费方

**mcp_rag_demo = 工具提供方**：四个 Milvus 工具——语义搜索（register.py:63）、category/priority 过滤（register.py:111，**白名单防注入**：`ALLOWED_CATEGORIES` 校验后才拼 filter，register.py:116）、rerank（register.py:201）。embedding 用 `nvidia/nv-embedqa-e5-v5` 1024 维（`scripts/load_support_tickets.py:43`）。**双配置对照是精髓**：`configs/support-ui.yml` 工具直连 Milvus 跑本地 ReAct；`configs/mcp-client-for-ui.yml` 把 tool_names 换成一个 `mcp_client` function group——先 `nat mcp serve`（README.md:201）把工具服务化，再 `nat serve`（README.md:208）起纯 MCP 消费端 agent。同一套工具、两种暴露。

**unstructured_transform_mcp = 消费方深度示范**：远程 Transform MCP server（Bearer 认证）的原始工具是异步多步协议（申请上传 URL→上传→起 job→轮询→下载），register.py:15-27 言明设计：组合成 `transform_document` 一个确定性函数。要点：`resolve_tools`（register.py:126）从 `<group>__<tool>` 命名剥工具句柄；`_check_http_response`（register.py:187）报错时**抹掉 pre-signed URL 的 query 防签名泄漏**。`extract_structured_data`（register.py:423）在 parse 上再链抽取 job，策略按扩展名 vlm/fast（register.py:478-481）。**离线测试标杆**：1287 行测试用 pytest-httpserver 零网络零凭据可跑。

## 7. x402 与 Spraay：加密支付线

**x402_payment_tool 手写支付协商**：`fetch_paid_api`（register.py:64，单笔默认上限 0.10 USDC、日限 5.00、收款方白名单）流程：GET → 402 则解析需求（register.py:137）→ 策略三闸（register.py:104，单笔+日累计+白名单）→ 签名 → `X-PAYMENT` 重试（register.py:280-282）→ 200 才记账。**策略在签名前强制**（register.py:39 安全架构声明），每次尝试进 `_payment_log`（register.py:101）供 `get_payment_status`（register.py:343）审计。双签名器：`WalletSigner` ABC（wallet.py:49）→ Inline（wallet.py:85，开发用）→ Remote（wallet.py:148，生产用，key 在独立进程经 `WALLET_SIGNER_URL` 端点，agent **永远摸不到私钥**）。测试闭环：`scripts/mock_x402_server.py` 8402 端口，无支付回 402+`maxAmountRequired:"50000"`（=0.05 USDC，mock_x402_server.py:61）——与 agent_identity_tool 的 mock_registry_server 并列本仓两大 mock 服务器。

**spraay_crypto_payments 走 x402 SDK 全托管**：`SpraayClient`（spraay_client.py:123）dry-run/live 双模式——无 `EVM_PRIVATE_KEY` 时 402 被解析成结构化报价（spraay_client.py:136，不动钱，CI 安全）；有 key 则 `wrapHttpxWithPayment`（spraay_client.py:288）包 httpx，SDK 自动签 EIP-3009 USDC 授权重试。批量单位陷阱防御：`to_batch_execute_payload`（spraay_client.py:64）按 `_TOKEN_DECIMALS` 表（spraay_client.py:52）用 Decimal 换算原始单位。工具面用 **function group 按需注册**：`@register_function_group`（register.py:51）共享 client，免费六工具恒注册，付费四工具挂 `filter_fn=_requires_evm_key`（register.py:398-410）——无 key 时**直接从工具集消失**。对比：x402 胜在策略闸门+签名隔离（配 mock server），spraay 胜在真实网关+dry-run 替代 mock+渐进披露。

## 8. 纯配置示例与陷阱勘误

**currency_agent_a2a 是纯配置型**：目录**零 Python 源码**（无 src/，`[tool.setuptools] packages = []` 置空），全部能力来自 config.yml——`mcp_date_time` function group 以 stdio 拉起 `python -m mcp_server_time`，`currency_agent` 用 `a2a_client` 连外部 LangGraph currency agent（`url: http://localhost:11000`，需先克隆 a2a-samples 跑服务，README.md:76-95），workflow 用 `per_user_react_agent`。kaggle_mcp 与 prometheus_avatar_mcp 同类；agent_identity_tool 是信任层示例（`verify_agent_identity` 输出 TRUST/REJECT/ERROR，register.py:168-232）。

三条勘误：

1. **currency 的 `packages = []` 不是错误**：它本就不打包代码，pip install -e 只为拿 entry point 与依赖组；README.md:24 明言这是 NAT 1.6 主仓示例快照，价值在参考集成而非确定性验证。
2. **common.sh 是主仓拷贝残留**：`common.sh:18` "AIQ toolkit" 注释 + `common.sh:22` 引用不存在的 `packages/`/`tests/`。诊断 CI 时先意识到脚本假定主仓布局。
3. **data 目录全是 LFS 指针**：`sample_queries.json`（真身 1269 字节）、`offline_scenarios.json`（7780 字节）等不 `git lfs pull` 就是指针文本——此时跑 k8s 离线模式，`preload_offline_data` 在 `json.load`（`utils.py:52-53`）抛 JSONDecodeError，报错位置离根因很远。

上手路径：prometheus_avatar_mcp（最少依赖）→ k8s 离线模式（lfs pull）→ 精读 sandbox_agent（ABC+factory+双轨可整体搬走）→ unstructured 学消费端工程化 → 支付两例对照读。
