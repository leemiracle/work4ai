# explain-03 · Admin API 与 HCI 管理面：NVFlare 的"操作面"全景

## ① 角色定位

NVFlare 运行时分两半：跑联邦训练的数据面（f3 cell 间 Shareable 流）与管人管任务的管理面。HCI（Human-Computer Interface）子系统就是管理面：登录/会话、命令分发、job 提交与结果下载全走它。分四层：

1. **fuel/hci**：与联邦语义无关的通用命令框架——`CommandSpec/CommandModule/CommandRegister` 注册表（`nvflare/fuel/hci/reg.py:20,138`）、Table 表格渲染、登录/会话模块（`nvflare/fuel/hci/server/login.py:37`）。
2. **private/fed/server**：把 HCI 实例化为 `FedAdminServer`（`nvflare/private/fed/server/admin.py:145`），聚合六个业务命令模块（`nvflare/private/fed/server/server_cmd_modules.py:24`）。
3. **fuel/flare_api**：程序员门面 `Session`（`nvflare/fuel/flare_api/flare_api.py:131`），把命令包装成 `submit_job/list_jobs/monitor_job` 等方法；`nvflare job` CLI（`nvflare/tool/job/job_cli.py:634` 分发表）只是 argparse 外壳。
4. **dashboard**：provision 用 Web 面板。任务书称其为 Django，**源码实锤是 Flask**——`nvflare/dashboard/application/__init__.py:17` 直接 `from flask import Flask`，配 flask_jwt_extended/flask_sqlalchemy，只服务于 provision（project 审批、证书分发），不是运行时监控台。

## ② 内部结构

**命令注册表是双层命名空间**。`CommandSpec` 描述单条命令（name/handler_func/authz_func/confirm），模块名圈出 scope；`finalize()` 按裸名与 `scope.name` 双索引填 cmd_map（`nvflare/fuel/hci/reg.py:240-249`），用户可用 `shutdown` 也可用 `train.shutdown` 消歧。confirm 只允许 none/YESNO/AUTH——`shutdown/restart` 均带 `confirm=ConfirmMethod.AUTH`（`nvflare/private/fed/server/training_cmds.py:95-103`）。

**服务端入口不在 HTTP，在 cell**。`AdminServer` 调 `cell.register_request_cb(channel=CellChannel.HCI, topic="*")`（`nvflare/fuel/hci/server/hci.py:76-80`），命令经 f3 信道进来；文件上传另注册 FileStreamer 流处理。`_process_admin_request`（`hci.py:176`）把 payload 解成 Connection 交 cmd_reg。`enable_hci=False` 时不建入站命令与 CredKeeper（`hci.py:65`）——给 simulator 留的纯出站模式。

**过滤器链顺序敏感**（`nvflare/private/fed/server/admin.py:185-199` 注释明言 "order is important!"）：LoginModule（既当命令模块注册登录命令，又当过滤器保证已登录）→ AuthzFilter → CommandAudit。

**会话是自包含签名 token**。`handle_cert_login`（`nvflare/fuel/hci/server/login.py:74`）验证 admin 证书链与 CN 签名（`login.py:103-109`），再由 `make_token`（`nvflare/fuel/hci/server/sess.py:70-87`）把用户名/角色/org/study 打成 JSON 用服务器私钥签名。服务器重启后 `recreate_session`（`login.py:206`）验签直接复活会话——代价是无法即时吊销，只能等 30 分钟空闲超时（`sess.py:125`，monitor 线程每 5 秒扫一次），过期反向下行 `SESSION_EXPIRED`（`sess.py:273-279`）。签名材料由 `CredKeeper` 惰性构造（`nvflare/private/fed/server/cred_keeper.py:54,68`）。

**客户端是"被管理者"代理**。`FedAdminAgent`（`nvflare/private/fed/client/admin.py:55`）注册 `CellChannel.CLIENT_MAIN` 全 topic 回调；`_dispatch_request`（`admin.py:100`）先本地审计，再做两级鉴权：站点级 SiteSecurity + 用户级 AuthorizationService（`admin.py:131-160`），通过后交给 topic 对应的 `RequestProcessor`。处理器由 `AdminCommands` 静态聚合（`nvflare/private/fed/client/admin_commands.py:285-297`），在 client_train 的 create_admin_agent 逐个挂载。

## ③ 外部连接

- **向上**：`Session` 读 startup kit 的 fed_admin 配置构造 `AdminAPI`（`nvflare/fuel/hci/client/api.py:248`）；`submit_job`（`flare_api.py:352`）本质是拼命令串。
- **job CLI**：`nvflare job` 子命令经 `job_sub_cmd_handlers`（`nvflare/tool/job/job_cli.py:634`）分发，handler 建会话后调 `sess.submit_job`。
- **服务端业务**：`JobCommandModule`（`nvflare/private/fed/server/job_cmds.py:149`，scope 名 `job_mgmt`）承载 submit/list/abort/delete/clone/download 全套；SystemCommandModule 另提供 sys_info/report_env。
- **客户端注册**：Authenticator 是反方向身份验证——client 用 nonce+证书签名挑战并验证服务器（`nvflare/private/fed/authenticator.py:119-171`），与管理面登录互为镜像。

## ④ 数据流

以 `nvflare job submit` 为例：CLI → `internal_submit_job` 建会话 → `Session.submit_job` 拼命令串 → `AdminAPI.do_command` 区分本地/服务器命令 → `server_execute` 经 HCI 信道发往 server → `_process_admin_request` 解 Connection → 过滤器链 → `job_mgmt.submit_job` handler：先经 FileStreamer 收作业包校验入 JobStore → 返回带 job_id 的 meta（`flare_api.py:389`）。之后 `monitor_job_and_return_job_meta`（`flare_api.py:1641`）按 poll_interval 轮询 `get_job_meta` 直到终态/超时/回调叫停。

涉及 client 的命令两跳：handler 用 `FedAdminServer.send_requests`（`nvflare/private/fed/server/admin.py:307`，阻塞）把带用户身份 header 的请求经 f3 发到各 client 的 CLIENT_MAIN，client 鉴权执行回包，服务端 check_client_replies 汇总；client 存活登记靠 client_heartbeat。表格类回复用 `conn.append_table`（`nvflare/fuel/hci/conn.py:36`）构 Table 渲染。

## ⑤ 设计决策与批判

- **命令即字符串协议**是大胆决定：flare_api 本质是"拼命令行字符串+解析 meta dict"。优点是 CLI/console/API 三端共享同一套服务器命令；代价是参数只能空格分隔，多 client 名要防 shlex 折叠（`flare_api.py:120-126` 注释为此解释 NVBug 6098943），类型安全全靠手工。
- **无状态签名会话**换来服务器重启后会话存活，但无法即时吊销；bind_download/mark_download_active 专为下载事务做会话保活，是该模型的补丁。
- **HCI 命名误导**：它不是 REST 式 API，而是 f3 信道上的 JSON 命令协议；`AdminServer` 名字暗示网络服务器，实际只是 cell 上的回调集合。
- **分层未完全贯彻**：fuel 本不该依赖联邦语义，但 `hci.py:27` 反向 import `nvflare.private.fed.server.cred_keeper`；审计则双写——服务端 CommandAudit 与客户端 auditor 各记一份，宁可重复不留盲区。

## ⑥ 新人提示

1. 找命令实现从两头夹击：先在 `nvflare/apis/fl_constant.py:253-273`（AdminCommandNames 常量表）查名字，再去 job_cmds/training_cmds/sys_cmd 搜对应 CommandSpec 的 handler_func。
2. 调登录失败看三点：`login.py:95-98`（服务器签名身份未配置直接 REJECT）、cert CN 与用户名是否一致、study 是否在 StudyRegistry 注册。
3. 命令报 "not authenticated" 时注意 `login.py:184` 的 pre_command 对 CERT_LOGIN/CHECK_SESSION 以外一切命令强制验 token；长任务应捕获 SessionExpired。
4. 自定义管理命令姿势：实现 CommandModule.get_spec() 后用 `ServerCommandModules.register_cmd_module`（`server_cmd_modules.py:35`）挂载；打穿到 client 需配套 RequestProcessor 并 `AdminCommands.register_command`（`admin_commands.py:315`）。
5. 别把 dashboard 当运行时组件读——它是 provision 阶段的 Flask 应用（`nvflare/dashboard/wsgi.py:21`）。
