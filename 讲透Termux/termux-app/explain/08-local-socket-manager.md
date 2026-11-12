# 08 · LocalSocketManager.java × local-socket.cpp —— am 直连 socket 服务端的 JNI 双向桥

**对象**：`termux-shared/src/main/java/com/termux/shared/net/socket/local/LocalSocketManager.java`＋ `termux-shared/src/main/cpp/local-socket.cpp`（603 行 9 native）
**勘误先行**：派发指令给的路径是 `app/src/main/cpp/local-socket.cpp`，实际在 **`termux-shared/src/main/cpp/local-socket.cpp`**——随 termux-shared 模块编译（`termux-shared/build.gradle:61-64` 的 `externalNativeBuild.ndkBuild` 指向该目录 `Android.mk`，`LOCAL_MODULE := local-socket`）；app 模块的 cpp 目录只住 bootstrap 汇编。

## 一、角色定位

这对文件是图谱 **L05「本地 Socket 与 Shell 命令执行框架层」** 的 socket 半边：Java 端 `LocalSocketManager` 是 AF_UNIX/SOCK_STREAM 服务端的门面与生命周期管理器，C++ 端是全部系统调用的真身。JNI 桥刻意求薄——Java 只做配置、线程与错误包装，内核 socket 语义（fd、errno、SO_PEERCRED、SIOCINQ、SO_RCVTIMEO）尽数下沉。

存在理由在 `TermuxAmSocketServer.java:42-45` 类注释：传统 `/system/bin/am`（或 TermuxAm）每条命令都要冷启动一个 dalvik vm，太慢；Android 12 起非 shell 应用直接 exec `/system/bin/am` 又被禁。于是 termux-app 常驻 socket 服务端，`$PREFIX/bin/termux-am` 客户端经 `$PREFIX/bin/termux-am-socket` 直连，命令在同进程内由 termux-am-library 执行并秒回。依赖链：`TermuxApplication.java:63` 调 `setupTermuxAmSocketServer()` → `TermuxAmSocketServer.java:102-109` 组装 RunConfig → `AmSocketServer.java:70-80` `new LocalSocketManager(...).start()`。本件对 am 语义一无所知，只管连接从哪来、谁能连、怎么读、怎么写、怎么关。

## 二、内部结构

### Java 端 LocalSocketManager

三重身份：**实例生命周期管理器 + 9 个静态 JNI 包装 + 回调线程分发器**。构造（:58-65）把 Context、RunConfig、`new LocalServerSocket(this)`、回调客户端、UEH 全部 final 化；`LocalServerSocket` 构造时只建监听 Thread 对象（`LocalServerSocket.java:48`），未启动。`start()`（:70-87）synchronized，首次调用 `System.loadLibrary("local-socket")`（:76，库名即 Android.mk 的 LOCAL_MODULE）；`stop()`（:92-99）**先置 `mIsRunning=false` 再停 socket**——顺序是刻意的，见坑 3。9 组静态包装（:125-303）同构：try 调 `xxxNative`，catch `(Throwable)` 兜底返回 `new JniResult(message,t)`（如 :126-133）；native 声明（:432-448）与 C++ 端 `Java_com_termux_shared_net_socket_local_LocalSocketManager_*` 一一对应。回调分发（:307-339）里 `onError/onDisallowedClientConnected/onClientAccepted` 都走 `startLocalSocketManagerClientThread()`（:331-339）——**每个回调一条新线程**并挂 UEH，:330 注释直言动机：客户端逻辑必须独立线程，否则阻塞后续接入。UEH 装配（:373-380）优先取 `ILocalSocketManager` 提供的 handler，null 则退化为纯日志；Termux 侧借此把 socket 线程崩溃接入 TermuxCrashUtils（`TermuxAmSocketServer.java:194-198`）。

### C++ 端 local-socket.cpp

支撑函数四组＋9 个 JNI 入口。字符串/进程工具：`jstring_to_stdstr`（:23-32，走 `String.getBytes()` 避开修改版 UTF-8）、`get_process_cmdline`（:80-95）读 `/proc/[pid]/cmdline`、`replace_null_with_space`（:46-63）把 `\0` 分隔转空格便于日志。JniResult 工厂（:157-218）5 个重载最终落到 `FindClass("com/termux/shared/jni/models/JniResult")` → `GetMethodID("<init>","(IILjava/lang/String;I)V")`（:175）→ `NewObject`（:187）。checkJniException（:144-155）做 `ExceptionCheck→Occurred→Clear→Throw` 四连，把挂起的 Java 异常清掉再重抛让 Java 包装层 `catch(Throwable)` 接住；:140-143 与 `LocalSocketManager.java:104-107` 双向钉同一条规则：**JNI 抛的必须按 Throwable 捕**，否则击穿线程 UEH。字段回写 `setIntField/setStringField`（:222-249）用 `GetFieldID+SetXxxField` 直接填调用方传入的 `PeerCred` 对象——C++→Java 的第二条数据通道（第一条是返回 JniResult）。

入口内核语义（均带 fd<0 卫语句与 `ReleaseByteArrayElements` 清理）：`createServerSocketNative`（:255-315）强制 backlog 1-500（:259）→ `socket(AF_UNIX,SOCK_STREAM,0)`（:265）→ 路径长度双保险 `chars>=108 || chars>=sizeof(sockaddr_un)-sizeof(sa_family_t)`（:280）→ `memcpy` 进 `sun_path` **不补 `\0` 终止符**（:288，抽象 socket 首字节 `\0` 正靠 byte[] 传入）→ bind（:291）→ listen（:301）→ fd 装进 intData 返回（:314），失败路径先备份 errno 再做 JNI 清理（:292-297）。`readNative`（:353-411）循环 read，每轮 `clock_gettime(CLOCK_REALTIME)` 对比绝对 deadline（:373-387），`ret==0` 即对端半关闭 break（:398-400）；**:390 的 count 传缓冲区全长而非剩余量**，见第五节。`sendNative`（:414-469）循环 `send(...,MSG_NOSIGNAL)`（:452，防 SIGPIPE 杀进程），`bytes-=ret` 递减（:460）写法正确。`availableNative`（:471-487）用 `ioctl(SIOCINQ)` 查未读字节；timeout 两入口（:496-531）设 SO_RCVTIMEO/SO_SNDTIMEO。`getPeerCredNative`（:533-603）`getsockopt(SO_PEERCRED)`（:552）拿内核担保的 pid/uid/gid，ucred 先初始化 -1 防"失败却误报 root(0)"（:546-548），再尽力读 cmdline 补 pname（:586-598，跨用户不可读时留空，由 Java 端 `PeerCred.fillPeerCred` 二次补全，`PeerCred.java:42-62`）。

### LocalServerSocket 生命周期

`LocalServerSocket.java` 把 fd 的 -1⇄有效值翻译成服务状态。`start()`（:52-124）：路径校验（非抽象 socket 须绝对路径 :79、≤108 字节 :66）→ 建父目录授 `rwx`（:83-88）→ **删旧 socket 文件**（:94，既杀残留服务又保证 bind 不撞 EADDRINUSE）→ JNI 建服 fd 并 `setFD(fd)`（:100-112，fd 从此存进 RunConfig，`LocalSocketRunConfig.java:55`）→ 挂 UEH、启动监听线程（:114-118）。`accept()`（:187-243）核心循环：fd<0 立即返回 null（:193-196，停服信号）；成功后**先 SO_PEERCRED 再放行**（:213），uid 必须等于 app uid 或 root（:233），否则 `onDisallowedClientConnected`＋立刻关连接（:234-238）；任何失败 `continue` 重试。`ClientSocketListener.run()`（:249-301）拿到合法客户端先设读写超时（:268-275）再 `onClientAccepted` 交业务线程（:283）；收到 null 即 break，finally 幂等 `close()`（:294）。`stop()`（:127-140）＝ interrupt 监听线程 → close fd 并置 -1（:160-173）→ 删 socket 文件（:179-184）。

## 三、外部连接

图谱实测（knowledge-graph.json 全图 1284 节点/2762 边，文件级 fan 由边表现算）：

| 文件 | fan-in | fan-out | 指向它的是 |
|---|---|---|---|
| LocalSocketManager.java | 3 | 29 | AmSocketServer、TermuxAmSocketServer、**local-socket.cpp**（JNI 实现边） |
| local-socket.cpp | 2 | 26 | build.gradle、Android.mk（构建边） |
| JniResult.java | 3 | 5 | LocalSocketManager/LocalServerSocket/LocalClientSocket |
| TermuxAmSocketServer.java | 3 | 25 | TermuxApplication、TermuxAppShellEnvironment、TermuxPropertyConstants |

整条 socket 栈是**单消费者漏斗**：业务世界只有 am 协议一家用它（`AmSocketServer.java` fan-in 仅 1）；向上辐射三处触点——应用启动入口（TermuxApplication.java:63）、shell 环境变量导出（`ENV_TERMUX_APP__AM_SOCKET_SERVER_ENABLED`，TermuxAmSocketServer.java:95-96，决定所有会话里 termux-am 是否可用）、用户属性开关（`~/.termux/termux.properties` 的 `KEY_RUN_TERMUX_AM_SOCKET_SERVER`，改后须 force-stop）。向下仅依赖 JniResult、Error/LocalSocketErrno、Logger 三件；C++ 端除反射的两个类名外零 Java 依赖。

## 四、数据流

一条完整链路（`termux-am start ...` 为例）：

1. **连接**：`$PREFIX/bin/termux-am`（Java）经 `$PREFIX/bin/termux-am-socket`（C 客户端，termux/termux-am-socket 仓）connect 到文件系统 socket——路径常量 `TermuxConstants.java:924`：`/data/data/com.termux/files/apps/com.termux/termux-am/am.sock`。
2. **准入**：监听线程 `acceptNative` 拿 client fd → SO_PEERCRED 内核查证 → uid 白名单（同 uid 或 root）→ `new LocalClientSocket`（`LocalClientSocket.java:55-65`，`mCreationTime` 为 deadline 基准）→ **新线程**跑 `onClientAccepted`。
3. **收命令**：客户端写完 am 子命令字符串（不含 "am" 前缀）即半关闭写端；服务端 `processAmClient`（`AmSocketServer.java:82-125`）调 `readDataOnInputStream(data,true)`（`LocalClientSocket.java:187-213`）——`SocketInputStream` 每次 1 字节循环进 `readNative`，靠对端 EOF（ret==0）终止，deadline 为 `mCreationTime + RunConfig.getDeadline()`（`LocalClientSocket.java:133`）。
4. **执行**：`ArgumentTokenizer.tokenize` shell 风格分词（:190）→ `new Am(stdout,stderr,application).run(amCommandArray)`（:226，同进程执行，可先过 SYSTEM_ALERT_WINDOW 权限检查 :219-224）→ 输出收进 StringBuilder。
5. **回传**：`sendResultToClient`（:136-152）拼协议帧 **`exit_code\0stdout\0stderr\0`**（格式钉在类注释 :40），exit code 先压进 0-255（:162-169，越界在 shell 侧被误读为 44 号错误）；经 `sendNative(MSG_NOSIGNAL)` 全量写完 → 关流关 fd，客户端解析三段并以 exit_code 退出——全程零 vm 冷启动。

## 五、设计决策（含三处实测缺陷）

**为什么手写 JNI 而不用 `android.net.LocalSocket`**：框架 API 拿不到原始 int fd，也就做不了本层需要的 backlog 显式控制（`LocalSocketRunConfig.java:95` 默认 50）、SO_RCVTIMEO/SO_SNDTIMEO、SIOCINQ 探测、绝对 deadline 轮询，以及 errno 原样透出成结构化错误（`JniResult.java:21-41`）。SO_PEERCRED 框架虽有 `getPeerCredentials()`，凑齐上面几样就只剩自研；代价是 603 行手工资源清理，收益是 errno 备份（:292）、MSG_NOSIGNAL（:452）这类框架不暴露的细节可控。**JniResult 值对象而非跨 JNI 抛异常**：异常跨 JNI 语义易碎（本仓为此钉了 Throwable 规则，`LocalSocketManager.java:104-107`），值对象让"fd 放 intData"这类成功带数据的结果自然表达。

**安全三件套**：文件系统 socket 优先于抽象命名空间（`AmSocketServer.java:48-49`；抽象 socket 在 targetSdk 28+ 还会被 SELinux 拦，`LocalSocketRunConfig.java:30-39`）；uid 白名单在 accept 循环强制（`LocalServerSocket.java:233`）；root 连接执行的 am 命令仍以 termux 用户身份跑（`TermuxAmSocketServer.java:38-40`），无提权面。PeerCred -1 初始化（`PeerCred.java:38-39`）防"getsockopt 失败却返回 0=root"假阳性。

**实测缺陷三条（本仓与上游 master 同源，2026-10-26 经 zread 核对一致）**：
1. **readNative 计数缺陷**：`local-socket.cpp:390` `read(fd, current, bytes)` 每轮请求全长而非剩余 `bytes-bytesRead`。若首轮短读（如 10 字节）后内核又就绪大量数据，第二轮可向 `data+10` 写至多 `bytes` 字节——**越界写堆内存**。sendNative 递减写法（:460）无此问题，修复即改 count 为剩余量。现实未引爆的原因：AmSocketServer 读路径每次只传 1 字节缓冲（`SocketInputStream` 的 `mBytes=new byte[1]`，`LocalClientSocket.java:411`），循环只跑一轮——典型"靠使用方式掩盖的缺陷"。
2. **processAmClient 失败路径缺 return**：`AmSocketServer.java:119-124`，`runAmCommand` 失败发完 exit 1 帧后**没有 return**，继续无条件发 exit 0。第二次发送打在已关闭 fd 上返回 invalid-fd Error → `onError` → 因 `isRunning()==true` 弹出一条莫名的插件错误通知（`TermuxAmSocketServer.java:205-208`）。客户端先收到 exit 1 帧故功能无损，但每次 am 失败多一条污染通知。
3. **available() 用错 fd**：`LocalClientSocket.java:277` 把 `mLocalSocketRunConfig.getFD()`（**服务端**监听 fd，`LocalServerSocket.java:112` 存入）传给 available，而非客户端自己的 `mFD`（:318 的 getFD()）。SIOCINQ 打在监听 socket 上无意义；当前 am 协议不走 available 轮询，属潜伏。

另两条分析性毛边：stop 时 `Thread.interrupt()`（`LocalServerSocket.java:132`）打不断阻塞中的 native accept()，停服依赖 close fd 后下一次返回错误的时机；accept 失败 `continue`（:199-203）在持续错误下是无退避重试。

## 六、新人提示

**坑 1：改协议必须三头同步。** `exit_code\0stdout\0stderr\0` 帧格式同时钉在服务端（:40,:140-145）、C 客户端（termux-am-socket 仓）和 shell 包装三处；`\0` 在 Java String 合法、在 C 端是终止符，两端处理完全不同——先读 termux-am-socket 解析代码再动手。exit code 必须压 0-255（:162-169）。

**坑 2：两层超时别混用。** SO_RCVTIMEO/SO_SNDTIMEO 管单次系统调用（每客户端 accept 后立刻设，`LocalServerSocket.java:268-275`，默认 10 秒，`LocalSocketRunConfig.java:65/75`）；deadline 管整个读/写循环的总预算，默认 0＝无限（:84）。调试"socket 卡死"先分清卡在哪层。

**坑 3：动线程模型前先看 UEH 链。** 每回调一线程（:331-339）＋UEH 注入 TermuxCrashUtils（`TermuxAmSocketServer.java:194-198`）意味着回调里未捕获异常**不会**让 app 崩、只进崩溃报告——bug 可能被静默吞掉。`mIsRunning` 先置 false 再 stop（`LocalSocketManager.java:95-96`）是压制停服噪声通知的前提（`TermuxAmSocketServer.java:203-208`），调换顺序立刻通知风暴。客户端 socket 关闭责任在业务方（`LocalSocketManagerClientBase.java:37-41` 基类兜底 close，子类处理后须调 super），漏关即 fd 泄漏。

**坑 4：路径约束三重。** ≤108 字节（Java :66 早查＋native :280 双保险）、非抽象 socket 须绝对路径且父目录 rwx（:79,:83-88）、抽象 socket 以首字节 `\0` 判定（`LocalSocketRunConfig.java:108`）——首字节写错就静默变成文件系统 socket 落错位置。

---

*源码版本：termux-app@2aa7f43d（local-socket.cpp 末次变更 2022-04-18）；上游 master 对照 zread 2026-10-26。*
