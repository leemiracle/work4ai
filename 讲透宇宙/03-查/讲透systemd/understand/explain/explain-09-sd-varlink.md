# explain-09 · src/libsystemd/sd-varlink/sd-varlink.c — sd-varlink：JSON-RPC 新面与协作式 fiber

## 一、角色定位

sd-varlink.c（4495 行）实现 varlink 协议的 systemd 官方库：每连接一条 AF_UNIX SOCK_SEQPACKET/stream、每消息一行 JSON、方法名形如 `io.systemd.Network.Manage` 的接口化 RPC。它是 systemd 里与 sd-bus 并列的第二张 RPC 面，定位是"取代私有 socket 协议"——resolved/journal/networkd/portable 的管理 API 已迁 varlink（docs/VARLINK.md 是接口规范），趋势是把 D-Bus 留给桌面总线、把系统服务管理交给 varlink。本文件同时管客户端（sd_varlink_call/Observe）与服务端（sd_varlink_server_bind + 凭证校验 + 连接限额），并用 **26 态状态机**（varlink_state_table，sd-varlink.c:50-77）+ 协作式 fiber（用户回调可阻塞但只挂起自己）解决"一个连接一次只处理一个方法"的协议约束。

## 二、内部结构

状态机是骨架：客户端线 idle-client → calling → called → collecting → processing-reply → awaiting-reply(-more/-upgrade)；服务端线 idle-server → processing-method{,_more,_oneway,_upgrade} → pending → processed；公共尾态 upgrading（协议升级，连接被让渡给任意自定义协议——varlink 最大的差异化能力）、pending/processing-disconnect/timeout/failure → disconnected。每次迁移都打 debug 日志（varlink_set_state，sd-varlink.c:84-98）。IO 层极简：varlink_write/read（751/760）包一层 JSON 流式解析（varlink_phase:103 是 JsonStream 的回调）。方法分派 `varlink_dispatch_method`（1253）严格校验消息对象：只认 method/parameters/oneway/more/upgrade 五个键（1272-1324），三个修饰标志互斥（1292/1303/1314），缺 method 即协议错；然后按 flags 切四个 processing 态（1334-1337）。回调执行有两条道：普通回调直接调；**fiber 回调**（varlink_dispatch_fiber:1196 → varlink_fiber_entry:1149）在独立协程栈上跑，用户可以写同步风格的阻塞代码。

## 三、外部连接

底层依赖 sd-json（消息编解码）与 json-stream（增量解析）；事件循环复用 sd-event。服务端设施在文件后半：`validate_connection`（3464）按 SO_PEERCRED 的 ucred 做 ROOT_ONLY/MYSELF_ONLY 策略与连接限额（默认总量 4096、per-UID 128，sd-varlink.c:44-45，ACCOUNT_UID 时逐 UID 计数 3489-3499）；连接建立即校验（客户端在 connect 后被动接受或被拒）。内置两个标准接口：org.varlink.service.GetInfo/GetInterfaceDescription（1358-1360）与 io.systemd（3397-3398）——任何 varlink 服务免费获得自描述能力。客户端 transport 除 unix 外还有 ssh（varlink_connect_ssh_unix:358 / ssh_exec:436），把"远程管理系统服务"做进连接层。上游消费者：journalctl（io.systemd.journal 流式日志）、resolvectl、networkctl、systemd-run 的 varlink 面；接口定义文件 varlink-io.systemd.*.c 由 .varlink 文件生成。

## 四、数据流

服务端一帧的旅程：socket 可读 → varlink_read 解出完整 JSON → state=idle-server 时进 dispatch_method（1264 的前置检查）→ 校验键与标志 → 查 server 的 methods 表命中回调 → fiber 场景：状态先切 PENDING_METHOD 再挂起等 fiber 完成（fiber_entry 头注释 1152-1156 精确描述了这套次序）→ 回调内任意次 sd_varlink_reply/error（2582 reply_internal 负责封包回写）→ fiber 结束时若仍 PENDING 且无人应答，按"没 enqueue 回复也没 stash 连接"判协议错并拆连接（1178-1194 的 EPROTO 分支）。客户端一帧：enqueue → write → awaiting-reply → 收到 reply 分派注册回调（varlink_dispatch_reply:879），more 模式持续收流。升级流（UPGRADE）：方法应答 `{"upgrade":true}` 后双方进 upgrading 态，连接 fd 让渡给用户回调——varlink_handle_upgrade_fds（1500）处理输入输出 fd 拆分，journalctl 的流式读取与 ssh transport 的内部实现（varlink_socketpair:236）都靠它。

## 五、设计决策

1. **严格单方法串行 + 显式状态机**：varlink 协议规定一连接同时只有一个在飞方法，26 态把"谁欠谁一个 reply"的每种子状态都显式化（awaiting/pending/processing × method/reply/more/upgrade），杜绝回调乱序——这是与 sd-bus"多在飞调用按 cookie 配对"的根本差异，用状态复杂度换协议简单度。
2. **fiber 救同步 API**（1149-1198）：回调跑在独立 fiber 栈，可阻塞可复用普通 C 控制流；fiber 收尾统一兜底（未应答即失败连接），把"忘了 reply"从内存泄漏变成明确错误。
3. **内置自描述**（1358-1360）：GetInfo/GetInterfaceDescription 让所有服务端免费可内省——接口即文档，工具链（varlink bridge、IDE 插件）靠它自动生成。
4. **DoS 防御内建**（44-45/3464-3500）：总连接数、per-UID 上限、凭证策略三闸门在 accept 层执行，业务回调之前。
5. **UPGRADE 逃生舱**（1556/1500）：承认 JSON-RPC 不是万能（日志流、终端传递），允许把连接降级为裸字节流——协议有边界感而非无限膨胀。

## 六、新人提示

服务端排障看状态日志：`SYSTEMD_LOG_LEVEL=debug` 下 varlink_set_state 的每次迁移（92-95）连成一条剧情线，卡在 pending-method 就是回调没 reply/没 stash（对照 fiber_entry 1178 的判据）。写新接口务必读 docs/VARLINK.md（本仓规范），命名从 io.systemd.<Daemon> 起；方法参数用对象嵌套避免顶层标量（825-878 的 normalize 处理宽松输入但生成端要守规范）。与 sd-bus 的选型判断：跨机或需总线广播→bus；本机单服务管理面、想 JSON 可读与 curl 式调试（`varlinkctl call /run/systemd/... io.systemd.X.Y`）→varlink。fiber 回调里可以调 sd_varlink_close（1183-1185 明确支持），但记得所有路径要么 reply 要么显式 stash 连接。Kylin 工作区提示：麒麟定制服务若暴露管理 RPC，优先 varlink 而非私有 socket 协议——凭证校验（3464）、限额、自描述三件套白拿；客户端只要 ucred 白名单逻辑，MYSELF_ONLY 一行 flag 即可（3480-3483）。
