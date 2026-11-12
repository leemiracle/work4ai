# 10 · unstructured_transform_mcp：把异步多步 MCP 协议封装成一个工具

## 角色定位

`unstructured_transform_mcp` 是 MCP **消费方**的工程化示范：Unstructured Transform 服务（文档解析/结构化抽取）的 MCP server 要求调用方走一套异步多步协议——申请上传 URL、裸 HTTP 传字节、起 job、轮询状态、下载结果——共六个原始工具。本示例把这串协议组合成 `transform_document` 与 `extract_structured_data` 两个确定性函数，agent 只需一次可靠调用。模块 docstring（`register.py:15-27`）把这一定位写得明明白白。它是全仓离线测试密度最高的示例。

## 内部结构

常量层（`register.py:52-60`）：50MB 文件上限 `MAX_FILE_SIZE_BYTES`、进行中 job 状态集 `_PENDING_JOB_STATES`（SCHEDULED/IN_PROGRESS）、完成态与**连续 3 次轮询失败容忍**。配置 `TransformDocumentConfig`（`register.py:63`）核心是 `mcp_group: FunctionGroupRef`（默认指向 `unstructured_transform` 组，`register.py:66-68`）加四个旋钮：轮询间隔 5s（`register.py:69`）、job 超时 900s（`register.py:70-73`）、HTTP 超时、`max_output_characters` 50000 保护 agent 上下文（`register.py:80-84`）。

工具解析：`TransformTools` NamedTuple（`register.py:96-102`）声明四个 MCP 工具名，`ExtractionTools`（`register.py:105-117`）是它的超集再加两个抽取工具；`resolve_tools`（`register.py:126`）从 function group 的成员字典里用 `FunctionGroup.decompose`（`register.py:143`）剥掉 `<group>__` 前缀按名匹配，缺工具时 raise 列出缺失名与可用名（`register.py:145-148`）。

协议驱动层：`_invoke_tool`（`register.py:161`）调 MCP 工具后把文本 parse 成 dict，识别 error 载荷抛 `MCPToolError`（`register.py:153`/`register.py:172-174`）；`_require`（`register.py:178`）对缺字段给出含前 300 字符 payload 的报错；`_check_http_response`（`register.py:187`）在 HTTP 失败时把 URL 的 query 串抹掉再进错误信息——注释言明 pre-signed URL 的 query 带签名是凭据，错误会进日志和 agent 上下文（`register.py:188-195`）；`_upload_source`（`register.py:198`）区分公网 URL 直接透传（`register.py:205`）与本地文件——后者经 `asyncio.to_thread` 做文件系统操作（`register.py:211`）、按大小上限校验（`register.py:215-217`）、请求 pre-signed URL（`register.py:220-223`）后裸 HTTP PUT 上传（`register.py:225-232`，注释强调 pre-signed URL 不能带 bearer token）；`_wait_for_job`（`register.py:242`）轮询至完成/失败/超时，容忍 3 次传输层抖动。

两个公开函数：`transform_document`（注册 `register.py:377`，内部 `_transform` 在 `register.py:387`）走 `transform_source`（`register.py:332`）全链，产出 `TransformResult`（`register.py:87`：markdown/element_count/character_count/filename），输出超 50000 字符截断并附提示（`register.py:408-412`）；`extract_structured_data`（Config `register.py:423`）链两个异步 job——`_parse_to_output_ref`（`register.py:484`）先 parse 并从结果文件里挖 `output_ref`（`register.py:519`），schema 未提供时 `_suggest_schema` 让服务端起草（`register.py:523`，结果里 `schema_was_suggested` 标记来源，`register.py:456`），用户提供的 schema 先做 `json.loads` 校验（`register.py:555-559`）；parse 策略按扩展名选：图像/PDF 走 `vlm`，其余 `fast`（`register.py:478-481`，依据注释：服务端对其它类型会把 vlm/hi_res 静默降级成 fast，`register.py:460-461`）。

## 外部连接

config.yml 三层接线：`function_groups.unstructured_transform`（`_type: mcp_client`，`transport: streamable-http`，`url: https://mcp.transform.unstructured.io`，`include` 精确圈定六个原始工具）；`authentication.unstructured_auth`（`_type: api_key`，`raw_key: ${UNSTRUCTURED_API_KEY}`，`auth_scheme: Bearer`——每个 MCP 请求带 Bearer 头）；workflow 用 `react_agent` 挂两个组合函数 + `nvidia/nemotron-3-nano-30b-a3b`（`enable_thinking: false` 关思考链省 token）。向上经 NAT 注册；向外依赖 Unstructured 云服务（或自托管等价物）与 NIM。

## 数据流

`transform_document(本地文件)` 一次调用：解析 function group 拿四工具 → 请求上传 URL 得 `upload_url`+`file_ref` → httpx PUT 原始字节（不经 MCP）→ `start_transform_job(file_ref)` 拿 job_id → 每 5s `check_job_status` → COMPLETED 后 `get_job_results` 拿结果文件引用 → httpx GET 下载 markdown 文本（`_fetch_results`，`register.py:288`）→ 截断 → TransformResult。`extract_structured_data` 在 parse 完成后追加第二段：suggest/start_extraction/check/get_results，返回带 provenance 的 JSON 记录。

## 设计决策

1. **组合优于裸暴露**：六个原始工具直接给 agent，等于让 LLM 自己编排异步状态机（轮询、重试、ref 传递），每一步都可能幻觉；包成确定性函数把可靠性从"模型能力"移到"代码"。
2. **凭据卫生**：bearer 只进 MCP 通道（`register.py:225-232` 注释），pre-signed URL 的签名不进日志（`register.py:188-195`）——两条泄漏路径都被显式堵住。
3. **事件循环友好**：所有文件系统读都 `asyncio.to_thread`（`register.py:211`/`register.py:227`），大文件上传不阻塞 loop。
4. **渐进 schema**：抽取可以无 schema 启动（服务端起草），降低使用门槛，同时保留用户自带 schema 的 `json.loads` 前置校验（`register.py:555-559`）。
5. 测试策略是本示例的另一面旗帜：1287 行测试全部用 pytest-httpserver 假冒 MCP 工具与 HTTP 传输，断言到"轮询未就绪重试""连续失败容忍""工具缺失报错"级别（test_transform_document.py:181/192/206、test_extract_structured_data.py:280/359），零网络零凭据（README.md:276）；live 集成测试用 `--run_integration` 门控（test_workflow_integration.py:82/118/183）。

## 新人提示

只需 `UNSTRUCTURED_API_KEY` 即可 `nat run` 体验（配 `--input` 给一个公网 PDF URL 最快，公网路径连上传都省了）。本地开发先跑 `pytest tests/`，全部绿说明环境闭环。调优顺序：大文档超时调 `transform_timeout_seconds`（默认 900s 对扫描件可能不够）；返回截断调 `max_output_characters`；抽取质量先试无 schema 让服务端起草，不行再带 schema。改造复用：任何"上传→job→轮询→下载"型的远程服务都能套这副骨架——抄 `resolve_tools`/`_invoke_tool`/`_wait_for_job` 三件与 config 的 function_groups+authentication 接线，把 NamedTuple 里的工具名（`register.py:96-102`）换成你服务的。
