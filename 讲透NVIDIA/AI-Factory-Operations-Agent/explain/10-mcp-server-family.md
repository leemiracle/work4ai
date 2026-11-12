# 10 · MCP 服务器族：bcm-mcp-ssh-server / mcp-oauth-proxy / mosaic-mcp 三种形态

> 仓库：NVIDIA/AI-Factory-Operations-Agent（AFOA，Mosaic 栈的 OpenClaw 运维 agent）
> 主文件：`helm/mosaic-stack/files/bcm-mcp-ssh-server.py`（298 行）、`files/mcp-oauth-proxy.mjs`（78 行）、`utils/mosaic-mcp.mjs`（127 行）
> 协同文件：`templates/bcm-mcp-tools.yaml`（部署面）、`tests/mcp-oauth-proxy.test.mjs`、`utils/mosaic-mcp.test.mjs`

## 一、角色定位

这三个文件是 AFOA 里 MCP（Model Context Protocol）的三种**实现形态**样本，各占一个生态位：

- `bcm-mcp-ssh-server.py`：**streamable-HTTP MCP 服务器**（Python FastMCP）。Broad Command Manager（BCM，NVIDIA 集群管理器）没有原生 MCP 面，这个适配器把"SSH 到 head 节点跑 cmsh"包装成受控工具——硬件巡检、BMC 凭据查询、Slurm 作业取证全部经它走。
- `mcp-oauth-proxy.mjs`：**OAuth sidecar 代理**（零依赖 Node）。上游 MCP 服务器要求 OAuth bearer 而内网 agent 只会静态头时，这个 78 行小进程在 localhost 上做 client_credentials 换 token + 透明转发。
- `mosaic-mcp.mjs`：**stdio MCP 服务器**（Node readline）。把 Mosaic UI 的 HTTP 工具面（`/api/openclaw/*`）翻译成标准 JSON-RPC over stdin/stdout——外部任意 MCP 客户端（Claude Code、Cursor 等）可以零 HTTP 知识接入整套 AFOA agent。

三者合起来演示了 MCP 的完整光谱：同一协议，服务器、代理、桥接三种角色各需要什么。

## 二、内部结构

### bcm-mcp-ssh-server.py：2 个类 + 3 个 @tool + 3 条 custom_route

**两个类**。`StaticTokenVerifier`（`bcm-mcp-ssh-server.py:71-78`）实现 MCP 的 TokenVerifier 契约最小版：`hmac.compare_digest` 恒定时间比对（`:76`，防时序侧信道），通过后返回 `AccessToken(client_id="mosaic-openclaw", scopes=["bcm"])`（`:78`）——单租户静态 token，够用且可审计。`MosaicBCMServer`（`bcm-mcp-ssh-server.py:81-252`）继承外部包 `bcm_mcp_tools.server.BCMServer`（`:17`），11 个环境变量旋钮（`:84-92`：cmsh 开关/admin 开关/用户名/profile/双超时/cmsh 路径/hardware 兼容开关/head 主机）。

**执行通道三层**。`_ssh()`（`bcm-mcp-ssh-server.py:96-104`）是唯一的远端执行原语：`subprocess.run(["ssh", head_host, "sh -lc " + shlex.quote(script)])`——脚本整体经 shlex 引号包裹后由远端 login shell 执行，超时与返回码透传。`_ensure_cmsh_user()`（`:106-127`）用双检锁（`:109` threading.Lock + `:107` ready 标志）保证"只读 cmsh 用户存在且 profile=readonly"这件一次性初始化只做一次。`_run_cmsh()`（`:136-142`）再做一层 `su - cmsh用户 -c` 降权——即使 agent 构造了恶意命令，落地身份也是只读用户；`_run_cmsh_admin()`（`:144-149`）是显式 admin 通道，构造时 gate 在 `cmsh_admin_enabled`（`:145-146`）。

**MCP 工具面**。`register_mosaic_tools()`（`bcm-mcp-ssh-server.py:236-252`）先 `pop("execute_cmsh")` 删掉基类的同名工具（`:237`——用受限版**替换**而不是叠加），再注册：`execute_cmsh`（`:239-241`，`asyncio.to_thread` 包同步 SSH）、`execute_cmsh_admin`（`:243-247`，仅 admin 开启时注册——**工具不在目录里就是最强的权限边界**）、`slurm_job_evidence`（`:249-252`，job_id 必须 `re.fullmatch(r"[0-9]+")`（`:223`），元数据+stdout/stderr 各 tail 20000 字节封顶（`:231`）——证据有界，不会把节点日志灌爆上下文）。

**custom_route 三条**（`bcm-mcp-ssh-server.py:206-220`）：`GET /list`（设备清单）、`POST /lookup/{hostname}`（BMC IP/用户名/密码）、`POST /lookup-os/{hostname}`（OS root 凭据）——Hardware Agent 兼容面，独立于 MCP 走 HTTP，各自 `hmac.compare_digest` Bearer 校验（`:190`）+ hostname 合法性检查（`:161,168` 的 `valid_hostname`，`:25-26` 定义 63 字符限制）。解析器三件（`parse_device_list:29-35`、`parse_bmc_lookup:38-63`、`last_cmsh_value:66-68`）把 cmsh 的表格文本容错解析成结构化 dict——`parse_bmc_lookup` 甚至做 IPv4 严格校验（`:54-57`），四必填键不齐即返回 None（`:62-63`）。

**main()**（`bcm-mcp-ssh-server.py:255-294`）：token 与 hardware token 分离（`:258-259`）；两处 fail-fast——admin 开了没 token 直接 RuntimeError（`:274-275`）、hardware 兼容开了没独立 token 同罪（`:276-277`）；有 token 时装配 OAuth 装饰（`StaticTokenVerifier` + `AuthSettings`，issuer 指向自身 Service `http://bcm-mcp-tools:{port}`，`:279-286`）；最终 `FastMCP(..., stateless_http=True)`（`:287`）以 streamable HTTP 起服务（`:293`）。`stateless_http` 的选择与部署形态匹配：K8s Service 后面的多副本无会话粘性，每个请求自证身份。

### mcp-oauth-proxy.mjs：78 行的 token 生命周期管理

`tokenProvider()`（`mcp-oauth-proxy.mjs:8-33`）是核心，四个细节撑起可靠性：

1. **入口校验**：tokenUrl 必须 HTTPS 且无 userinfo/hash（`:10`），与 `validation.yaml:108-110` 的安装期校验同构——纵深防御。
2. **过期提前量**：`expiresAt = started + lifetime - min(30000, lifetime/10)`（`:25`）——留 30 秒或 1/10 寿命（取小者），杜绝"拿到手就只剩 1 秒"的边界；`expiresAt <= now()` 直接判异常（`:26`）。
3. **并发去重**：`pending` promise 共享（`:16-17,29-30`）——十个并发请求过期时只发起一次 token 请求。
4. **401 失效**：`invalidate(token)` 只在缓存的 token 与用过的 token 一致时清缓存（`:13`），代理侧收到上游 401 时调用（`:55`）——下一请求强制刷新。

响应校验也严（`mcp-oauth-proxy.mjs:23`）：access_token 必须非空字符串、token_type 必须 bearer（大小写不敏感）、expires_in 必须正有限数——**任何字段畸形都当失败**，不给"半坏 token 进缓存"的机会。

`proxyServer()`（`mcp-oauth-proxy.mjs:43-72`）：白名单 method（GET/POST/DELETE）+ 精确 path 匹配（`:48`），其余 404；转发前注入 `Authorization: Bearer` 并改写 Host（`:52-53`）；`endToEndHeaders()`（`:35-41`）剥离全部逐跳头（connection 声明的 + 八个标准逐跳头）——RFC 语义正确，也防止内网 Host 头泄漏到上游；`GET /healthz` 直答 200（`:45`）供 K8s 探针；上游错误统一 502 文案（`:61,69`）。

### mosaic-mcp.mjs：stdio JSON-RPC 的最小实现

127 行实现完整 MCP stdio 服务器。三个内置工具（`mosaic-mcp.mjs:8-36`）：`ai_factory_operations_agent_chat`（必填 prompt + 可选 sessionKey/timeoutMs/conciseMode）、`_history`、`_commands`。`listTools()`（`:53-67`）先查 `/api/openclaw/tools` 动态拉取后端真实工具目录（含 inputSchema 透传），与内置三件合并去重后**进程内缓存**（`:54` 的 toolCache）——工具目录在进程生命周期内视为不变，重启即刷新。`callTool()`（`:69-96`）三分支：内置 chat 走 `/api/headless/chat`、其余透传 `/api/openclaw/tools/call`，认证用 `MOSAIC_UI_MACHINE_TOKEN` 环境变量（`:42-44`）。

协议循环在文件尾（`:105-127`）：readline 逐行读 stdin，`initialize` 回 protocolVersion `2024-11-05`（`:112`）、`tools/list`、`tools/call` 三方法 + 兜底空对象（`:122`），异常统一 `-32000` 错误码（`:100`）。没有 SDK 依赖——**stdio MCP 的协议面就这么大**，手写比引依赖更可控。

## 三、外部连接

- `bcm-mcp-tools.yaml` 模板把 server.py 经 ConfigMap 挂进 deployment，Service 名 `bcm-mcp-tools` 与 main() 的 issuer URL（`bcm-mcp-ssh-server.py:282`）咬合；openclaw 侧的 `MOSAIC_BCM_MCP_TOKEN` 注入见 `openclaw.yaml:620-626`。
- mcp-oauth-proxy 由 `managed-mcp-servers.yaml` 按 server 装配（managed MCP server 的 oauth.enabled=true 时作 sidecar），它的测试（`mcp-oauth-proxy.test.mjs`）注入假 fetchToken/now 验证缓存提前量与并发去重。
- mosaic-mcp 是**用户侧入口**而非集群组件：本机 `MOSAIC_URL` 指向 Mosaic UI 即可用任意 MCP 客户端驱动整套 agent——这是 AFOA 对外暴露自动化能力的最短路径。
- bcm/index.ts 插件（第 01 组已详述）是 server.py 的 MCP 客户端 counterpart；iraop 插件（第 11 篇）展示了另一种客户端写法（自实现 SSE）。

## 四、数据流

BCM 工具调用全链：OpenClaw agent 调 `bcm_execute_cmsh` → bcm 插件经 MCP streamable HTTP POST `http://bcm-mcp-tools:3001/mcp`（Bearer=MOSAIC_BCM_MCP_TOKEN）→ StaticTokenVerifier 恒时比对 → `asyncio.to_thread` 释放事件循环 → `_ssh` 到 head 节点 `su - readonly用户 -c cmsh -c '...'` → 输出回包。OAuth 代理链（如 RunAI 托管 server）：openclaw → localhost proxy（注入 Bearer）→ 上游 HTTPS MCP；token 过期/401 由 proxy 静默换新，openclaw 无感知。stdio 链：外部客户端 stdin `{"method":"tools/call",...}` → mosaic-mcp 转 HTTP → Mosaic UI → headless agent 会话 → 结果 content 数组回 stdout。

## 五、设计决策

- **替换基类工具而非叠加**（`bcm-mcp-ssh-server.py:237`）：pop 后重注册，保证 MCP 目录里永远只有一个 execute_cmsh——工具发现即权限清单，目录里看不到的才真正不可调。
- **admin 工具的条件注册**（`:243-247`）比"注册但拒绝执行"强一档：模型看不见就不会尝试，省一轮审批往返。
- **恒时比较出现在三处**（`:76,190` 与 proxy 的 URL 校验）——所有 token 判定统一 hmac.compare_digest，无一处 `==`。
- **proxy 不做连接池/Keep-Alive 簿记**：78 行的边界感——它只管 token 与转发，连接管理交给 Node http 默认行为；需要更复杂语义时应该换真反向代理而不是膨胀此文件。
- **mosaic-mcp 的 toolCache 无失效机制**：取舍注释写明场景是"长驻本地客户端"；若后端工具热更新，重启进程是既定刷新路径。

## 六、新人提示

- 调 BCM 链路问题时按序查四点：`MOSAIC_BCM_MCP_TOKEN` 两端一致（openclaw env 与 bcm-mcp Secret）、head 主机可达、`_ensure_cmsh_user` 是否成功过一次（失败会 RuntimeError 且不置 ready）、cmsh 路径 `MOSAIC_BCM_CMSH_PATH`（默认 `/cm/local/apps/cmd/bin/cmsh`，`:90`）。
- 给 server.py 加工具时记住三条家规：入参先验证（学 `slurm_job_evidence` 的数字 fullmatch）、输出封顶（学 20000 字节 tail）、admin 级操作走条件注册。
- mosaic-mcp 的会话隔离靠 sessionKey（缺省 "headless"，`:80-81`）——多客户端共用一个部署时各自传不同 sessionKey，否则历史互相污染。
- ⚠️ 甄别记录：任务简报"298 行 2 类 4 函数"——类确为 2 个（StaticTokenVerifier/MosaicBCMServer）；"@tool 函数"实为 **3 个**（execute_cmsh/execute_cmsh_admin/slurm_job_evidence，`:239-252`，admin 条件注册），另有 3 条 custom_route（`:206-220`）与 3 个模块级解析函数（`:25-68`）。"4 函数"口径在源码中不成立，已按实测改写。图谱 summary 与源码一致。

（行号锚基于当前工作树源码逐条核实。）
