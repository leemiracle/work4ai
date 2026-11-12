# 精讲 03 · 负向注入工具：tools/libmctppacketcorrupt（pktcorrupt.c + syscalls_wrap.c）

## 角色定位

纯 C 小库（核心两文件合计不到 700 行）是 SPDM 鲁棒性的试金石：以 `LD_PRELOAD` 透明劫持**真机进程**的 socket 收发，对 MCTP 包做字段篡改、丢弃与伪造（`LD_PRELOAD=libpacketcorrupt.so spdmd -v 7`，`tools/libmctppacketcorrupt/readme.md:60`）。与 fuzzer 分工：fuzzer 在进程内伪造整个 Responder（协议层错误），packetcorrupt 在 syscall 边界破坏真实流量（字节级错误）——后者能测到 spdmd 与真实 MCTP 栈之间的盲区。

## 内部结构

**拦截层 syscalls_wrap.c（329 行）**：`dlsym(RTLD_NEXT, "recv")` 惰性取真函数（`syscalls_wrap.c:117`，connect 同款 `:69`）；`_iosys_recv`（`:112`）先问 `corrupt_fake_recv_packet` 要不要伪造（`:124`），真收后再交 `corrupt_recv_packet` 改写（`:141`）；发送侧 `_iosys_send`（`:148`）对称处理（`:170`）。最黑魔法一手是 `__asm__(".symver _iosys_recv,recv@GLIBC_2.4")`（`:145`，发送 `:179`）把 wrapper 钉到 glibc 符号版本上防绕过；close 也被包（`:186`）。**注入层 pktcorrupt.c（360 行）**：`corrupt_context`（`pktcorrupt.c:33`）持配置；`is_packet_should_be_modifed`（`:36`，源码原文即此拼写）按 m/n 概率或指定序号决定下手（`packet_num_update` `:106` 计数）；`packet_modify_buffer`（`:149`）按模式分派改命令码/长度/版本/证书字段（`:165`），模式枚举在 `apptypes.h:54`。按偏移改字节在 pktmod.c，RESPOND_IF_READY 特化在 response_if_ready.c，可复现伪随机源在 random.c。

## 外部连接

配置全走环境变量：`MCTP_CORRUPT_MODE`（16 种模式 `readme.md:12`）、`MCTP_CORRUPT_RAND_LEVEL`（m/n 或 `a,b,c%n` 语法 `readme.md:30`）、按 EID/命令类型丢包的 `MCTP_CORRUPT_DROP_EIDS`（`:43`），丢包总闸是 `/tmp/corrupt_drop_enable` 文件存在性（`:49`）——运行中 touch/rm 即实时开关。被测对象通常是 spdmd/spdmutil；构建上是 meson 树一等公民（`meson.build:105`）。注意它劫持的是应用侧 socket 调用，对内核态 MCTP（enable-in-kernel-mctp）路径效果不同。

## 数据流

以"篡改第 2/10 个包的 msglen"为例：export 两变量启动 spdmd → 它 `send` GET_DIGESTS → `_iosys_send`（`syscalls_wrap.c:148`）判定此包不在名单直通 → Responder 回 DIGESTS → `_iosys_recv`（`:112`）真收（`:138`）→ `corrupt_recv_packet`（`:141`）→ 命中第 2 包 → `packet_modify_buffer`（`pktcorrupt.c:149`）按 msglen 模式把长度字段改错 → spdmd 的 interpretResponse 应报解码错误，`handleTimeoutOrRetry`（`libspdmcpp/connection.cpp:1426`）接管重试——负向测试要断言的就是这条恢复路径。

## 设计决策

其一，**LD_PRELOAD + .symver 而非 ptrace/ebpf**：零依赖、目标进程无感，代价是只覆盖动态符号（close/connect 也得包的原因）。其二，**确定性随机源 + 显式序号语法**：负向测试最怕偶现不可复现，配置从根上保证重放。其三，**模式枚举对齐协议字段**（versionfields/capabfields/digestfields 等各自精准改 param1/param2/reserved，`pktcorrupt.c:76`）：按协议语义破坏，每模式对应一类 Requester 校验分支。其四，运行时开关用文件存在性而非信号：对任何启动方式统一生效，无需重启改 env。

## 新人提示

先读 `readme.md`，注意两处坑：自称拦截 "read and write"（`readme.md:5`）实为 send/recv/connect/close；`zerolen` 描述 "zerjjkko" 是原文打字错误（`:16`）。再读 syscalls_wrap.c 的 dlsym 惰性初始化（`:112`）——LD_PRELOAD 工具的模板代码。实验时先 `MCTP_CORRUPT_MODE=bypass` 跑通注入路径再换破坏模式，观察点在 spdmd `-v 7` 日志的错误串与重试节奏；改完解码容错后用 msglen+固定序号做回归——packet_basic_test 测不到半截包这类字节级伤害。
