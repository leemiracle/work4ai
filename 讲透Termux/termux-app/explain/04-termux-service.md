# 04 · TermuxService.java —— 前台服务：会话的不死宿主

> `app/src/main/java/com/termux/app/TermuxService.java` · 959 行 · L09 层核心 · 锚均现场核实（8629e632）

## 一、角色定位

Termux 全部终端会话与后台命令的**宿主进程锚点**：持有前台通知的 Service 把进程存活权从"界面生命周期"里赎出来——文件头明说"**服务可以比 Activity 活得久**"，Activity 重开后会话还在（TermuxService.java:56-63）。

`TermuxActivity` 不持任何 `TerminalSession`，全经 `LocalBinder` 取（TermuxService.java:71-75；TermuxActivity.java:390）——**L08 是视图，L09 是状态的主人**。

## 二、内部结构

单类实现 `AppShell.AppShellClient`+`TermuxSession.TermuxSessionClient` 双接口（TermuxService.java:68）。

**状态极简**：`mWakeLock`/`mWifiLock` 成对锁（:102-103）、**双 client**——持 Activity 引用的完整实现（:84）与只持服务引用的 final 降级实现（:89）。会话列表**不在本文件**：三列表在 termux-shared 的 `TermuxShellManager`（TermuxShellManager.java:31,36,41），服务只是门面。

**生命周期四段**：`onCreate` 取两单例并 `runStartForeground()`（:111-123）；`onStartCommand` **重跑 `runStartForeground()`**（:131，防服务已启动而 onCreate 不再调）后分发四 action——STOP_SERVICE/WAKE_LOCK/WAKE_UNLOCK/SERVICE_EXECUTE（:141-156），返回 `START_NOT_STICKY`；`onDestroy` 清 TMPDIR→释放锁→**条件**杀全部命令（仅 `!mWantsToStop`，:175-176）→`stopForeground(true)`；`onUnbind` 若 Activity client 还挂着就 unset（:198-199）——注释点破**不能依赖 Activity `onDestroy()` 总能执行完**（:195-197）。

**两大执行工厂**：`actionServiceExecute`（:359-425）把约 20 个 extras 灌进 `ExecutionCommand`（:365-408），**先**入 pending 列表（:414）**再**按 runner 分派：APP_SHELL→`createTermuxTask`（:465，调 `AppShell.execute`，:480）、TERMINAL_SESSION→`createTermuxSession`（:575，调 `TermuxSession.execute`，:594）。`processShellCreateMode` 校验创建模式（:665-681，`NO_SHELL_WITH_NAME` 按名复用）；工厂结尾固定：入列表→移出 pending（:498-499）→刷通知。

**通知子系统**：`buildNotification` 生成 "N session(s), M task(s)"，持锁时追加 `(wake lock held)` 且优先级 LOW→HIGH（:791-805）；action 按钮有 Exit（对自己发 `ACTION_STOP_SERVICE`，:829-830）与 WakeLock 开关（:834-838）。`updateNotification`（:852-859）是**隐形自杀开关**：无锁且两会话列表皆空即 `requestStopService()`（:853-855）。

## 三、外部连接

图谱实测 **fan-in 7 / fan-out 48**：fan-in=imports 4（TermuxActivity、两个 SessionClient、FileReceiverActivity）+configures 2（`AndroidManifest.xml` service 声明 `exported="false"`，AndroidManifest.xml:196-198；`ic_service_notification.xml`，:819）+calls 1；fan-out=imports 25+contains 22（函数节点）+exports 1，其中 22 个 import 指向 termux-shared（`TerminalEmulator` 为 javadoc-only，:48）。

两个图谱未建边的隐式依赖：**RunCommandService** 送命令靠 TermuxConstants 常量而非本类 import（RunCommandService.java:221,247，常量引用的图谱口径盲区）；**FileReceiverActivity** 三处 `setClass(this, TermuxService.class)` 直发 execute intent（FileReceiverActivity.java:246）。反向：Activity 建会话终调 `createTermuxSession`（TermuxTerminalSessionActivityClient.java:381）。上游：TermuxActivity 先 startService 再 bindService（TermuxActivity.java:259-266），连接后 :429 换完整 client、销毁 :355-358 unset。

## 四、数据流

Tasker 场景一条完整链路：

1. **入口**：外部 App 发 `RUN_COMMAND` → RunCommandService 校验 `allow-external-apps`（RunCommandService.java:132），合格则组装 intent 并 `startForegroundService`（:221,:247）；
2. **解析**：`onStartCommand` 命中 execute（TermuxService.java:153-156）→ intent 变 `ExecutionCommand`：URI 还原路径时 **`#` 后 fragment 属于路径**（:383-384），runner 缺省看旧参数 `EXTRA_BACKGROUND`（兼容包袱，:370-372），随后**先入 pending 列表**（:414）——防命令未进正式列表服务就被杀，保证能告知创建者"已取消"（:242-245）；
3. **执行**：`createTermuxSession`（:575）→ `TermuxSession.execute` fork PTY（:594），入 `mTermuxSessions`（:608）；`handleSessionAction` 默认"切新会话并拉 Activity"（写 prefs :865-871；Android 10+ 缺悬浮权限只 toast :716-728）；
4. **回程**：退出触发 `onTermuxSessionExited`（:640）→插件命令回传 PendingIntent（:647-648）→移出列表（:650）→刷通知（:658），末会话则服务自杀（:853-855）。

## 五、设计决策

**前台服务 + START_NOT_STICKY**（:206,:165）：前者买命（OOM 难杀），后者拒绝复活——重启拿不回旧会话，`START_STICKY` 只留空壳通知（:163-164）。

**状态外置到 TermuxShellManager 单例**：三列表 public final 裸暴露（TermuxShellManager.java:31-41），服务只做调度门面。收益：全家桶（共享 `sharedUserId`）对齐同一状态源；代价：synchronized（:263,:465,:575）只护自己那段、非列表全局锁——**以纪律换共享**。

**双 client 降级**：Session 要回调但完整实现持 Activity 引用而 Service 更长寿。常驻 ServiceClient 兜底（:89），Activity 绑上时遍历全会话换 client（:760-765），解绑换回（:771-776）；判空集中而非散布进 terminal-emulator 各回调点。

**不对称杀策略**（:263-299）：用户退出时 sessions **全杀**、tasks **只杀带 pending result 的**——后台任务尽量活到 OOM 杀进程（:236-240 注释）；系统杀服务时 sessions 照杀但不处理结果，插件命令例外（:276-277）。契约责任：谁等结果（PendingIntent 创建者），谁的命令就必须被终结并告知"已取消"，否则对端永远等（:254-259）。

**通知即生命周期控制器**：空态检查（:853-855）让服务无空转——末会话退出且锁已放，下次刷通知即 `stopSelf()`。**WakeLock/WifiLock 永远成对**（:101-103）且 acquire 无超时（:315）：用户显式控制，带超时违背"锁到用户解锁"的语义。

**勘误（图谱摘要 vs 源码）**：图谱节点摘要称其处理"START_SERVICE/STOP_SERVICE/EXECUTE 等 intent action"——**`START_SERVICE` action 不存在**：switch 仅四支（:141-156），TermuxConstants 只定义四个 action（TermuxConstants.java:987-999），启动走显式 intent（TermuxActivity.java:261）；另 :164 有截断坏 javadoc `{@link Term}`。

## 六、新人提示

**坑 1：别假设 onCreate 跑过一次状态就绪**。`onStartCommand` 重跑 `runStartForeground()`（:130-131）就是为"服务已启动、onCreate 不再调"——每次 `startForegroundService` 后必须调 `startForeground` 否则系统崩 App；新初始化只放 onCreate 会被二次 `startService` 跳过。

**坑 2：列表遍历必须拷贝，且两个退出回调线程语义不一致**。`killAllTermuxExecutionCommands` 先拷贝三列表再遍历（:270-272，:262 注释明说循环内有移除）；更隐蔽的是 `onAppShellExited` 把清理 post 到 `mHandler`（:509-523），`onTermuxSessionExited` 却直接执行（:640-659）——对称回调一异步一同步，改后者会与 kill 循环交错。

**坑 3：Activity client 永远判空，set/unset 必须成对**。服务大概率比 Activity 活得久，触达 UI 必须走 null 守卫（照抄 :617-618 模式）；新增持 Activity 引用的路径务必确认 `onUnbind`→`unsetTermuxTerminalSessionClient`（:198-199,:771-776）能清掉，否则漏一个引用就泄漏一个 Activity。

---

*字数（不计空格）：4796 · 锚：65 · 抽验 3 锚全中*
