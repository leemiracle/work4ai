# auth.py — Browser Use Cloud 认证：三条登录路径与最小模型契约

## 一、角色定位

`auth.py` 负责 harness 与 Browser Use Cloud 之间的**凭据获取与保管**：OAuth 浏览器流、RFC 8628 设备流、手动 API key 三条登录路径，加上 auth.json 的原子读写与 0o600 权限基线。开篇 docstring 立下"最小模型契约"（auth.py:3-5）：模型侧只有两种结局——**要么有 key，要么收到一句可执行的指令** `"cloud-auth-required: run 'browser-harness auth login'"`（CloudAuthRequired，:37-39）。OAuth 的全部复杂性（PKCE、state、回调服务器、令牌交换）都关在这个文件里，不向外泄漏一个概念。

## 二、内部结构

- **常量（:29-34）**：API 基址（`BROWSER_USE_CLOUD_API_URL` 可覆盖，:118-119）；`DEFAULT_CLIENT_ID = "browser-use-terminal"`——注释说明这是**借用** Browser Use 现有 CLI 的注册 OAuth client，留 `BROWSER_HARNESS_OAUTH_CLIENT_ID` 逃生门（:30-32）；回调路径与 600 秒总超时。
- **异常（:37-43）**：`CloudAuthRequired`（带指令文案）与通用 `AuthError`。
- **四个 dataclass（:46-87）**：`PendingCallback`（state/code/error/complete）；`BrowserAuthStart`（回调服务器 + verifier + auth_url）；`DeviceAuthStart`（device_code/user_code/verification_uri，`open_uri` 属性优先完整链接 :76-78）；`AuthRecord`（api_key 等六字段，`from_token_response` 强制响应含 api_key 否则 AuthError，:90-94）。
- **存储层（:126-179）**：`auth_path()` 默认 `config_dir()/auth.json`、`BH_AUTH_PATH` 可覆盖（:126-130）。`save_auth_record()` 把记录并进 JSON 的 `browser_use` 键——**auth.json 是多租户容器**，tmp+`os.replace` 原子落盘、0o600（:146-156）。`clear_auth()` 只删 `browser_use` 键，其它键保留，容器空了才删文件（:158-173）。
- **读取与三态（:182-199）**：`get_browser_use_api_key()` 优先 env，其次存储，都没有抛 CloudAuthRequired；`auth_status()` 返回 env/stored/missing 三态。
- **PKCE（:202-206）**：verifier = `token_urlsafe(48)`，challenge = SHA256 后 base64url 去 padding（S256）。
- **浏览器流（:209-295）**：`start_browser_auth()` 先起本地回调服务器（`127.0.0.1:0` 随机端口，:397-424），POST `/cloud/cli-auth/browser` 拿 authorization_uri，可自动 `webbrowser.open`（:230-240）；`complete_browser_auth()` 用 `handle_request()` 0.5s 超时轮询直到回调落定（:252-259），state 不匹配记 `invalid_state`（:406-409），成功则交换令牌并存储（:267-269）。`browser_login()` 两段合体，`--json` 模式先打印 `needs_user_auth` 与 auth_url 再阻塞（:274-282），给宿主转交 URL 的机会。
- **设备流（:298-373）**：`start_device_auth()` POST `/cloud/cli-auth/device` 拿 device_code/user_code；`complete_device_auth()` 按服务器 interval 轮询令牌端点，`authorization_pending` 继续等、`slow_down` 间隔加 5 秒（:339-347）。
- **手动流（:376-384）**：`api_key_stdin_login()` 从 tty 用 getpass、从管道读全文，空值或长度 <20 拒绝（:460-464）。
- **HTTP 与工具（:427-508）**：`_post_json()` 把 HTTPError body 解析成 `"error: description"` 格式的 AuthError（:437-446）；`_auth_error_code()` 靠 `split(":", 1)` 取回错误码（:503-504）——错误码走字符串往返是本文件的朴素约定。
- **CLI（:511-546）**：`auth login [--device-code|--api-key-stdin] [--json] [--no-open] | status | logout`；错误时 JSON 模式输出到 stderr、exit 1（:540-545）。

## 三、外部连接

- **paths.py**：`config_dir()` 承载 auth.json（:130），享受 0o700 目录 + 0o600 文件基线。
- **admin.py**：云浏览器三件套全靠这里——`_browser_use()` 每次请求取 `get_browser_use_api_key()`（admin.py:887）；`sync_local_profile` 把 key 注入子进程 env（admin.py:1079）；doctor 读 `auth_status()` 判 "Browser Use cloud auth" 行（admin.py:1414, admin.py:1454）。
- **api.browser-use.com**：端点 `/cloud/cli-auth/browser`、`/cloud/cli-auth/device`、`/cloud/cli-auth/token`（:226, :300, :331/:388）。
- **run.py**：`browser-harness auth ...` 子命令直通 `run_auth_cli`（run.py:133 的子命令表含 "auth"）。
- **浏览器/系统**：`webbrowser.open` 打开授权页（:238, :312）；本地回调只绑 loopback。

## 四、数据流

**浏览器流全链**：`pkce_pair()` 生成 (verifier, challenge) + `state`（:210-211）→ 回调服务器就位 → 服务端注册拿到 authorization_uri → 用户浏览器完成授权 → 云端 302 回 `http://127.0.0.1:<port>/browser-use-cloud/callback?code=...&state=...` → Handler 校验 state（:405-412）填 PendingCallback 并回一张"可以关标签了"的 HTML（:414-419）→ CLI 侧轮询发现 complete → `_exchange_authorization_code()` 用 code+verifier+client_id 换令牌（:387-394）→ `AuthRecord.from_token_response()` 抽取 api_key → 原子并入 auth.json。

**读取链（每次云 API 调用）**：`get_browser_use_api_key()` → env 命中即返回 → 否则读 auth.json 的 `browser_use.api_key` → 双 miss 抛 CloudAuthRequired，错误文案本身就是下一步指令，agent 可直接转述给用户。

## 五、设计决策与取舍

- **三条路径覆盖三种环境**：桌面有浏览器走浏览器流；SSH/无头机走设备流（URL 抄到任何有浏览器的设备上完成）；CI 或已有 key 走 `--api-key-stdin`。`--json` 与 `--no-open` 让 agent 宿主程序化驱动每条路径。
- **auth.json 做成多键容器**（:151, :158-167）：未来其它服务可共享此文件而不互相践踏；logout 只摘自己的键。
- **坏 JSON 抛错而非静默重置**（:139-140）：静默当作未登录会让用户莫名重走 OAuth、旧 key 悬空，宁可把解析错误摆出来。
- **安全基线三件套**：PKCE S256 防授权码截获（公共客户端无 client_secret，:202-206 是唯一防线）；state 随机数防 CSRF（:211, :405-409）；文件写穿 `os.open(O_CREAT, 0o600)` + `os.replace`（:152-154, :468-480），崩溃不留半截凭据。
- **借用 client_id + env 逃生门**（:32）：避免为发版申请新 OAuth client 的阻塞，保留无缝切换口子。
- **错误码走字符串前缀**（:443-446 与 :503-504 配对）：不用自定义异常层级，`AuthError("authorization_pending: ...")` 前缀即协议——够用但脆弱，改文案格式前必须同步两处。
- **API key 长度启发式**（:463-464）：<20 字符直接拒绝，挡住把 "test"/空行当 key 存进去的低级失误。

## 六、新人提示

- **env 永远赢**：设了 `BROWSER_USE_API_KEY` 后 auth.json 完全不参与（:183-185），`auth status` 显示 `source: "env"`——排障"明明登录了还说不认"先查环境变量。
- **回调服务器只活一次登录**：`complete_browser_auth` 的 finally 必然 `server_close()`（:258-259），600 秒超时（:34）到了进程退出，弹窗留着也没用，重跑 login 即可。
- **`--json` 模式的时序契约**：先打一行 `needs_user_auth`（含 auth_url）再阻塞（:274-282），宿主必须在读到这行后立刻把 URL 递给用户，不能等命令结束。
- **设备流 interval 由服务器说了算**（:321, :328）：别硬编码 5 秒改轮询节奏；`slow_down` 加 5 秒是 RFC 8628 要求（:344-346）。
- **BH_AUTH_PATH 覆盖是文件级**（:127-129）：给完整文件路径，父目录不存在由 `save_auth_record` 的 `mkdir(parents=True)` 兜住（:148），但 paths 的 0o700 目录基线不再适用你指定的位置。
- **改 `_post_json` 错误格式 = 同时改 `_auth_error_code`**：这对字符串约定（:443 与 :503）没有静态保护，设备流 pending/slow_down 判断全靠它，动一处漏一处会把轮询变成立刻失败。
- **logout 的返回语义**：`"logged-out"` 或 `"missing"`（:538），后者表示本来就没登录——幂等，不是错误。
