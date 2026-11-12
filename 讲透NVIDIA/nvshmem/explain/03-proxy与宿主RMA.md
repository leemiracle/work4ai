# 03 proxy 与宿主 RMA——设备命令的宿主代理循环

## 角色定位

proxy（图谱 L04 的另一半）是 NVSHMEM 的"兜底执行器"：当 kernel 内发起的通信无法直达远端（没有 IBGDA 设备直通、目标不在本节点、或走 hostlib 模式），设备代码把命令写进环形队列，宿主 proxy 线程轮询取出、翻译成传输插件调用。它是"通信即访存"理想落空时的务实出路，也是 put/put_signal 在无 IBGDA 环境仍能工作的保证。宿主 RMA（L06 的 comm/ 线）则是同一套命令处理的宿主侧入口。

## 内部结构

协议层 `src/include/device_host/nvshmem_proxy_channel.h`（248 行）：所有请求槽位都是 8 字节 packed 结构，`base_request_t`（nvshmem_proxy_channel.h:26-33，static_assert 钉死 8 字节）编码 flag/op/groupsize/远端偏移；后续槽位拼 DMA 地址（put_dma_request_0/1/2）、inline 立即数（put_inline_request_0/1/2）、AMO 操作数（amo_request_0..4）；put_signal 需要 6×8=48 字节，完整内存布局图就画在 nvshmem_proxy_channel.h:171-187 的注释里。宿主执行层 `src/host/proxy/proxy.cpp`（1787 行）：两种 progress 循环——完整版 `nvshmemi_proxy_progress`（proxy.cpp:1667）与 minimal 版（:1695，仅 DMA），由 :418/:492 两处 pthread_create 按场景选择；主 switch 在 proxy.cpp:1469-1531，命令族分派：DMA 类（NVSHMEMI_OP_PUT/GET 及 _QP 批量变体，走 process_channel_dma）、inline P、AMO、PUT_SIGNAL，外加 FENCE/QUIET/REGION_END 控制命令——"四类数据命令+三类控制命令"是精确口径。宿主 RMA 入口 `src/host/comm/rma.cu:10-23`：nvshmemi_proxy_rma_launcher 按 is_signal×is_nbi 的 2×2 组合 cudaLaunchKernel 四个 entrypoint 之一——这就是设备侧 proxy_rma_*_entrypoint 四个符号的出生地。

## 外部连接

上游：设备代码 `non_abi/device/pt-to-pt/proxy_device.cuh` 把命令写进通道；`nvshmemi_transfer_api.cuh` 的路径判定决定一笔操作走 proxy 还是直通。下游：proxy 把命令翻译成 transport->post/amo 调用（transport.h:153-167 的函数指针）。宿主 put/get 实现在 `src/host/comm/putget.cpp`（890 行）：节点内 P2P 用 cuMemcpyAsync 优化（putget.cpp:171），远程走传输 post；amo/fence/quiet/sync/region 在同目录补全内存序语义。

## 数据流

一笔设备 put 的代理旅程：kernel 线程组执行 proxy_device 写入 8 字节槽序列并翻 flag → proxy 线程 COUNTER_TO_FLAG 比对发现新请求（proxy.cpp:1440-1459，PPC64LE/AARCH64 下显式 __sync_synchronize 做 Load/Load 排序，proxy.cpp:1461-1464）→ 按 op 分派处理器 → DMA 类聚合进 batch 再 post 传输 → is_processed 置位后槽位回收；未处理完的请求保留到下一轮（proxy.cpp:1531-1536 的部分处理注释）。put_signal 额外编码信号偏移/操作数/信号值三槽，落地时数据写与信号发布合并。

## 设计决策

8 字节槽位设计让设备-宿主通信天然对齐 cache line、免锁（flag 交替 0/1 的环形缓冲即 lock-free 协议，nvshmem_proxy_channel.h:176-177 注释）；文件头直言"单系统同字节序假设，此结构不可移植"（nvshmem_proxy_channel.h:15-17）——把可移植性边界写进源码。minimal progress 模式承认现实：多数时刻只有 DMA 在流动，轻量轮询省 CPU。rma.cu 的 2×2 launcher 把"代理"从隐式机制升格为四个具名 entrypoint，设备 stub 可静态引用。

## 新人提示

调试 proxy 先开 NVSHMEM_DEBUG=INFO 看 progress 线程日志；死锁排查看三处：flag 位序（宿主与设备必须同端序）、qp 批量命令的 QP 偏移（NVSHMEMI_OP_QP_OP_OFFSET 之上是 QP 变体，proxy.cpp:170-171）、region_end 的配对。读 proxy.cpp 先读 1469 的 switch 再向下钻各 process_channel_*。改通道结构必须同步 nvshmem_proxy_channel.h 的 static_assert——8 字节约束是协议的根。
