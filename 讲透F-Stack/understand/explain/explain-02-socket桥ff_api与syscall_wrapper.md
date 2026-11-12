# explain-02 · BSD socket 桥：lib/ff_api.h + lib/ff_syscall_wrapper.c

## 角色定位

先钉一个勘误：本仓**没有 lib/ff_api.c**——socket API 的实体全在 lib/ff_syscall_wrapper.c（2302 行），ff_api.h 是它的对外契约，ff_api.symlist（100 行）是导出符号清单（ff_socket/ff_send/ff_epoll_create…），Makefile 据此生成版本脚本。这一层是"应用宇宙"与"FreeBSD 内核宇宙"之间的翻译官：应用用 Linux 语义调用 ff_socket/ff_sendto，wrapper 把常量、结构体逐个翻译成 FreeBSD 语义，再调 kern_socket/kern_sendto 等内核内部函数直接进入协议栈——没有系统调用、没有上下文切换，这是 F-Stack 性能模型的第一根支柱。文件头注明血统：源自 Kip Macy 的 libplebnet pn_syscall_wrapper.c（`lib/ff_syscall_wrapper.c:29`）。

## 内部结构

文件分两段。前 900 行是纯翻译表：linux2freebsd_fcntl（`:288`，含 F_SETFL 四标志位改写）、linux2freebsd_ioctl（`:421`）、so_opt_convert/ip_opt_convert/ip6_opt_convert/tcp_opt_convert 四张 socket 选项表（`:538-655`）、linux2freebsd_socket_flags（`:673`，SOCK_NONBLOCK/CLOEXEC 位重映射）、sockaddr 双向转换（`:687/:704`——注意注释"linux 和 freebsd 可能指向同一地址"，所以先比较 sa_data 指针再 bcopy，原地转换零分配）、cmsghdr/msghdr 双向转换（`:719-915`，控制信息逐条搬运）。后 1400 行是 API 实现：ff_socket（`:917`）、ff_getsockopt/setsockopt（`:968/:1025`）、ff_ioctl（`:1087`）、ff_close/read/readv/write/writev（`:1159-1322`）、ff_zc_send/ff_zc_recv（`:1323/:1360` 零拷贝扩展）、send 家族（`:1402-1501`）、recv 家族（`:1502-1583`）、ff_fcntl（`:1585`）、ff_accept/accept4（`:1618/:1670`）、ff_listen/bind/connect（`:1717/:1748/:1778`）。

## 外部连接

向内：所有 API 最终落到 freebsd/ 树的 kern_* 系（kern_socket/kern_accept/kern_soreceive…），以 curthread（ff_thread.c 维护的线程伪造体）为进出通道，错误码经 ff_os_errno（ff_host_interface.c:530）把 FreeBSD errno 映射回 Linux errno。向外：ff_api.h 同时声明 ff_init/ff_run（`:61-63`）与 kqueue/epoll 全家桶，是 example/ 与 adapter/ 唯一的库入口；LD_PRELOAD 适配层（ff_hook_syscall.c）劫持 glibc 后也是转调这里的 ff_*。向旁路：FF_KERNEL_COEXIST 编译期开关打开后（`#ifdef FF_KERNEL_COEXIST` 遍布全文件），每个 API 都长出内核 fd 分流支——ff_is_kernel_fd 判定后走 ff_host_* 直接打宿主 syscall（如 ff_accept `:1627-1631`）。

## 数据流

以一次 TCP 连接的客户端视角走全链：ff_socket 先处理共存标记——SOCK_KERNEL 走纯内核栈返回编码 fd，无标记则 want_dual=1（`:930-938`），sys_socket 创建 F-Stack socket 后再 ff_host_socket 开内核伴生 socket，设 IPV6_V6ONLY 与 SO_REUSEPORT（多进程同地址监听的关键，`:953-956`）并把两 fd 记进 ff_native_map。ff_connect 翻译 sockaddr 后 kern_connect。ff_sendto（`:1408`）把 msghdr 翻成 FreeBSD 布局后 kern_sendto，数据从用户 buffer 经 soreceive/sosend 路径进 mbuf，最终由 ff_dpdk_if_send 发出。ff_recvfrom 反向：kern_recvfrom 后 freebsd2linux_sockaddr 回填地址（`:1657` 同款）。ff_accept 最精妙：先试 F-Stack 栈，EAGAIN 且开了共存再去内核伴生 fd 上 accept（`:1640-1648`）——注释直言这与 LD_PRELOAD"调两次 socket"的策略不同，因为 ff_ 前缀 API 无法从返回 fd 区分归属，此处靠 kernel_fd_encode 编码区分。

## 设计决策

三个决策值得咀嚼：① **翻译而非模拟**——两张 errno 空间、两套常量值（Linux 与 FreeBSD 的 SO_/IP_/F_ 数值大量不同）用显式 switch 表转换，而非重定义宏骗编译器；好处是应用仍链接 glibc 头文件，只需把 socket 换成 ff_socket。sockaddr 原地转换（`#linux 和 #freebsd 可能指向同一地址`）体现了对零开销的偏执。② getsockopt 对 LINUX_IP_BIND_ADDRESS_NO_PORT 直接伪造返回 1（`:982-988`）——FreeBSD 无此选项，恒真回答让 Nginx 之类的应用行为不变，这是"兼容层谎言"的正当用法。③ 双栈共存把复杂性压进 ff_socket 一处：dual 模式下每个 F-Stack fd 都有内核伴生（ff_native_map），accept 侧用 EAGAIN 级联兜底——代价是事件层（ff_epoll）也要做同样的双栈合并，改一处必须想着另一处。

## 新人提示

读这个文件按"翻译表→单 API→双栈支线"三遍读：先扫 `:288-915` 的表（全是机械映射），再挑 ff_socket/ff_accept/ff_sendto 三个代表精读，最后专门追一遍 `#ifdef FF_KERNEL_COEXIST` 的所有分支理解共存模型。注意 LINUX_AF_INET6 与 AF_INET6 的家族号差异在两处 sockaddr 转换里都处理了（`:694/:712`），自己新增 API 若带 sockaddr 参数必须复用这对函数。ff_zc_send/ff_zc_recv 是本分支扩展（配合 ff_veth 的 ZC_SEND），标准 F-Stack 没有；kern_* 返回 0/errno 而非 -1，错误处理一律 `goto kern_fail` → ff_os_errno → return -1，新代码别破坏这个模式。
