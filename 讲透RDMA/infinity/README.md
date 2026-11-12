# 讲透 infinity

[claudebarthels/infinity](https://github.com/claudebarthels/infinity) @c6cbbbfd · RDMA 大规模分布式训练通信框架（C++ 单边通信原语：write/read/Atomic on one-sided verbs）

| 产物 | 状态 | 明细 |
|---|---|---|
| deepwiki | ✅ | 25 页 TRUE_100 |
| understand 图谱 | ✅ | 65n/173e/12 层/15 步 tour · validator 0 issues · fingerprints@6cbbbfd（scanner 对 .h include 全盲 32 条手补） |
| onboarding | ✅ | 6000 字 8 节 · 76 锚三抽验全中（两代理接力：04:03 部分稿+09:3x 终稿压缩） |
| explain | ✅ | 12 篇 42,999 字符 · 256 锚（组1 128+组2 128）内容级抽验全命中 |

## 源码级勘误精选

- **Debug.h 双宏陷阱**：无 -D 时 INFINITY_DEBUG/INFINITY_ASSERT 全被编译成空（Debug.h:15-25 双 #ifdef、Makefile 默认零 -D）——线上断言/日志双静默；开宏后也不含 `__FILE__/__LINE__`，stdout+exit(-1) 无 core dump
- **QueuePairFactory 非 rdma_cm**（explain 组1 任务书甄别）：全仓 rdma_cm 零引用，实为自建阻塞式 TCP socket 带外地址交换（serverSocket，QueuePairFactory.cpp:23/42）
- **Buffer 三连隐患**（组2 新发现）：resize 的 uint64→uint32 截断（Buffer.cpp:90）、原地扩容不重分配即堆溢出（:92-106）、视图构造 offset 零边界检查（:42-54）
- **Makefile:16 `-std=c++0x`** 与 README 宣称 C++17 不符（C++11 时代旧拼写）；examples 目标不依赖 library 的构建坑
- QueuePair 精确口径：9 操作族/17 公开重载/7 种 verbs opcode；multiWrite SGE=1 约束（散点列表写不可用）
- RequestToken 真实 API=构造/reset/waitUntilCompleted/checkIfCompleted（initialize/waitBoth 不存在）；setUserData 全库零调用（预留 API）；写/读/send 三种完成语义含金量差异
- 死代码/零消费：getIpAddressAsUint32（现用 inet_pton，QueuePairFactory.cpp:129）、MAX_NUMBER_OF_OUTSTANDING_REQUESTS（文档性常量）、RegisteredMemory 在示例与 README 零引用、Region.cpp:9 冗余 include Buffer.h
- README `new RegionToken(REMOTE_BUFFER_INFO)` 伪代码——源码零定义，RegionToken.h 仅默认/六参构造（const 值快照非子类，40 字节平凡拷贝 `__has_trivial_copy=1`，指针版 POD memcpy hack）
- Atomic 的 REMOTE_ATOMIC 权限全库唯一落点（Atomic.cpp:25-26）；构造无注册失败断言（对照 Buffer.cpp:35 有）
- 示例计时口径：128 窗口含 8 次同步等待、末 127 条在途不等待（`i==OPERATIONS_COUNT` 永假）、MB/MiB 标签不符、对端接收不计时
