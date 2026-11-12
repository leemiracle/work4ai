# telemetry.py — best-effort 遥测：三层脱敏与永不阻塞的分离发送

## 一、角色定位

`telemetry.py` 是这个 harness 的**使用情况回传通道**：以匿名 install_id 为身份，把 CLI 事件发往 PostHog（EU 实例，telemetry.py:19），让作者知道哪些命令、哪类浏览器、哪些 agent 客户端在用。文件头两个词就是宪法（telemetry.py:1）："**Best-effort, opt-out**"——任何环节（写配置、发网络、序列化）失败都静默吞掉，遥测永远不许影响主流程；同时它是默认开启、可一键退出的 opt-out 模式，三个环境变量任一（`BH_TELEMETRY`/`BROWSER_HARNESS_TELEMETRY`/`ANONYMIZED_TELEMETRY`，:20）设为 0/false/no/off 即整体关闭。

**勘误（相对任务描述）**：脱敏黑名单 `FORBIDDEN_KEYS` 是 **18 个词**不是 16 个（telemetry.py:22-41）：api_key, content, cookie, email, href, key, message, password, path, prompt, query, secret, selector, text, title, token, url, uri——逐个数过源码。

## 二、内部结构

- **常量（:18-21）**：PostHog key 与 EU host；三个禁用 env 名；`MAX_TASK_LENGTH = 20_000`（task 文本截断上限）。
- **配置层（:44-125）**：`telemetry.json` 落 config_dir（:48-49），读写全程 try/except 吞错；`_save_config` 落盘 0o600、父目录新建时 0o700（:62-68）。`is_enabled()`（:102-105）= env 未禁用 **且** config 未设 `disabled`；`status()` 报告两个禁用来源（:108-118）；`set_enabled()` 写 config（:121-125）。
- **匿名身份（:86-99）**：`install_id` 是首次调用时惰性生成的 uuid4，正则 `[0-9a-f-]{32,36}` 校验（:87）——没有机器指纹、没有用户标识，卸载重装即换新身份。
- **脱敏核心 `_safe_properties()`（:128-144）**，详见第五节。
- **agent 客户端探测（:148-170）**：`_AGENT_ENV_MARKERS` 12 个 (env 变量, 客户端名) 对——amp、claude-code（CLAUDECODE）、codex（CODEX_SANDBOX/CODEX_THREAD_ID）、gemini-cli、copilot-cli（两个 marker）、openclaw、hermes、cursor（CURSOR_AGENT/CURSOR_TRACE_ID）、opencode（:148-161）。`_detect_agent_client()` 顺序扫 env；带 `=` 的 marker 还要求值精确相等（:166-168）。
- **分离发送（:173-206）**：`_send_detached()` 把内联 Python 源码（`_DETACHED_SENDER_SOURCE`，:173-186，urllib POST、异常全吞）塞进 `subprocess.Popen(..., start_new_session=True)` 起一个**脱离会话的子进程**，job JSON 经 stdin 交给它（:197-206）。host 与超时可被 `BH_POSTHOG_HOST`/`BH_TELEMETRY_TIMEOUT` 覆盖（:191-194）。
- **两个采集入口**：`capture()`（:228-244）通用事件，`capture_cli_event()`（:247-294）结构化 CLI 事件（关键字字参数：action/command/task/browser/output/steps/duration_seconds/exit_code/error_message 等）。
- **CLI（:297-308）**：`browser-harness telemetry status|enable|disable`，用法错误 exit 2。

## 三、外部连接

- **paths.py**：config_dir 是 telemetry.json 的家（:45）——与 auth.json、version-cache.json 同区，共享 0o700 目录基线。
- **run.py**：CLI 主入口在命令分发前调 `print_update_banner`/采集——遥测事件由 run 层组装 `capture_cli_event` 关键字实参。
- **admin.py**：doctor 通过 `auth_status` 间接毗邻；admin 自身的版本检查（version-cache.json）与遥测配置同住 config_dir 但互不相干。
- **外部端点**：`https://eu.i.posthog.com/i/v0/e/`（:193 拼出的 capture 端点）——原生 HTTP API，不依赖 posthog 客户端 SDK，子进程里只有 urllib。
- **环境变量面**：读 `BH_TELEMETRY*`（禁用）、`BH_POSTHOG_HOST`（自托管转发）、`BU_CDP_WS`/`BU_CDP_URL`（经 `_cdp_hostname` :218-225 提取 CDP 主机名作为 `cdp_url` 属性）、`BH_CLIENT`/`BH_CLIENT_VERSION`、`BROWSER_USE_AGENT_MODEL`/`BROWSER_USE_MODEL_PROVIDER`（:276-280）。

## 四、数据流

一次 CLI 事件的旅程：

1. run 层调 `capture_cli_event(action=..., command=..., task=...)`；`is_enabled()` 为假立即返回（:261-262）。
2. 组装 payload：PostHog key + install_id + 事件名 `cli_event`；properties 合并四层——`_base_properties()`（版本/python/os/machine，:209-215）、`$process_person_profile: True`、显式关键字实参、以及环境侧信息（cdp hostname、agent 客户端探测、模型名，:275-280）。`task` 截到 20,000 字符并另发 `task_length` 原始长度（:281-282）。
3. `_send_detached()` 起分离子进程，job 塞 stdin 后**立刻返回**——本进程不等待网络（:197-206）。
4. 子进程 urllib POST 到 PostHog，成败都无人知晓（:184-185 吞掉一切）。

注意 `capture()` 与 `capture_cli_event()` 的人格化差异：前者 `$process_person_profile: False`（:238）不在 PostHog 建人档案；后者 `True`（:270）会按 install_id 聚合一个 person profile。

## 五、设计决策与取舍

- **三层脱敏，宁错杀**。`_safe_properties()` 的三层防线（:128-144）：① 键名清洗——非 `[A-Za-z0-9_$.-]` 字符换下划线、截 80（:131）；② **黑名单子串匹配**——清洗后的小写键名只要**包含** 18 个禁词中任何一个，整个键值对丢弃（:133）；③ 值约束——bool/None/数值直通（:135-137），字符串值含 `"://"` 一律替换为 `[redacted]` 再截 120（:140-143）。子串语义意味着 `keyboard_layout` 会被 "key" 误杀、`uri_template` 会被 "uri" 误杀——这是刻意的：黑名单要挡的是"任何可能装着敏感内容的键"，误伤无害（少收一个属性），漏收有害。
- **key 级丢弃优先于值级 redact**：`url` 在黑名单里，所以名为 url 的属性根本进不了 payload（:133 丢弃），而其它键的值里若嵌了 URL 才走 `[redacted]`（:142）。两层职责分明：键名筛类别，值筛形态。
- **task 是唯一放行的长文本**：20k 上限 + 单独的 task_length（:281-282），作者要看的是任务画像不是任务全文。
- **分离进程发送的三个理由**：CLI 永不因网络阻塞（PostHog 慢/断网零感知）；子进程 `start_new_session=True`（:202）脱离进程组，父进程退出收到的 SIGINT 波及不到它；主进程不加载任何 HTTP 客户端依赖。
- **opt-out 而非 opt-in**：与 uv、pip 等工具同款选择；用 config 文件（跨调用持久）+ env（部署系统批量关）双通道退出。
- **不依赖 PostHog SDK**：内联 12 行 urllib 源码（:173-186）就是全部客户端，供应链面最小。

## 六、新人提示

- **加新的遥测属性时先用 `_safe_properties` 过一遍脑内测试**：键名含 18 禁词任一子串会被整对丢掉——你新加的 `path_count` 会无声消失（含 "path"），别在这上面调一下午。
- **嵌套结构会被压扁**：值为 dict/list 时走 `str(value)` 分支（:140-143），序列化成字符串后若含 `://` 整体变 `[redacted]`、再截 120——想要结构化上报就得拆平成多个标量键。
- **env 禁用优先于一切**：`BH_TELEMETRY=0` 时 `telemetry enable` 命令也会"成功"但 `status()` 仍报 disabled_by_env（:111-112）——CLI 的 enable 只改 config，覆盖不了 env。
- **排障"为什么收不到事件"**：依次查 `telemetry status` 的三态 → 是否在 CI 容器里（子进程 Python 可用吗）→ BH_POSTHOG_HOST 是否被指向了不存在的自托管实例。发送子进程吞掉所有异常（:184-185），永远不会给你报错线索，只能从 status 入手。
- **privacy 审计口径**：这份文件如实发的内容清单 = `_base_properties` 四项 + capture_cli_event 的关键字实参 + cdp 主机名 + agent/model 环境名（:264-291）+ 经三层脱敏的附加属性。审计时以这个清单为准，不要凭印象。
- **install_id 与 auth 无关**：它不关联 Browser Use 账号（那是 auth.json 的 api_key），两条身份线永不交叉。
