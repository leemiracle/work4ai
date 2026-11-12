# 11 infinity.h + Makefile + Configuration.h——umbrella 门面、手工构建与编译期预算表

> 源文件：`src/infinity/infinity.h`（26 行）/ `Makefile`（94 行）/ `src/infinity/core/Configuration.h`（54 行）

> 甄别：任务书称仓库为 C++17，但 Makefile:16 实钉 `-std=c++0x`（C++11 定稿前的草案拼写，等价 C++11）；代码所用特性（std::atomic、random_device）均 C++11 即有，全库无 C++17 特征——按源码口径本文称 C++11。

## ① 角色定位

三件文件合成分发面：**infinity.h 是 L12 barrel 门面**——26 行没有一行自有代码，纯 include 转发 13 个头（infinity.h:12-24），用户侧 `#include <infinity/infinity.h>` 一行拿到全部类型；**Makefile 是 94 行手工构建系统**——无 cmake/autotools，从对象编译到 `release/{libinfinity.a, include/, examples/}` 全流程；**Configuration.h 是编译期预算表**——全库唯一的"参数中心"，7 个 `static const` 常量把队列深度、SGE 上限、页对齐、握手数据上限、默认设备名全部钉死在编译期，**没有运行时配置面**。三者共同回答一个问题：这个库怎么被接出去。

## ② 内部结构

**infinity.h**：12-24 行 13 个 include 按目录分组（core 2/memory 7/queues 2/requests 1/utils 2），与 Makefile HEADER_FILES 的 14 条目一一对应（Makefile:40-53 多出的第 14 条正是 infinity.h 自己）——门面覆盖=分发覆盖，清单即契约。

**Makefile** 五段：工具链 :15-17（`CC=g++`、`CC_FLAGS=-O3 -std=c++0x`、`LD_FLAGS=-linfinity -libverbs`——变量名叫 CC 装的却是 C++ 编译器，小事但初见易懵）；清单 :29-53（10 个 cpp :29-38、14 个头 :40-53）；模式规则 :67-70（`mkdir -p` 建目录树后 `g++ -c` 出 .o）；library :74-79（`ar rvs` 归档 :76，`cp --parents` 暂存头文件 :78，再 `mv` 把 release/src 改名成 release/include :79）；examples :89-92（直接编 src/examples 下两个 cpp，`-I release/include -L release` 链接）。

**Configuration.h** 两组常量：队列组 :25-35（SEND/RECV_CQ 深度、SRQ 深度各 16351，MAX_NUMBER_OF_OUTSTANDING_REQUESTS :31，MAX_NUMBER_OF_SGE_ELEMENTS=1 :35）与系统组 :43-47（PAGE_SIZE 4096、MAX_CONNECTION_USER_DATA_SIZE 1024、DEFAULT_IB_DEVICE "ib0"——`constexpr const char*` 是全库唯一的 constexpr）。每条常量带 "Must be less than" 注释，指向 verbs 设备上限（MAX_CQE/MAX_SRQ_WR/MAX_SGE）。

## ③ 外部连接

**Configuration 的消费图**（grep 实证）：Context 构造用它建双 CQ 与 SRQ（Context.cpp:58-59/:65，外面包 `MAX(...,1)` 防零，MAX 宏本地定义于 Context.cpp:22）；QueuePair 构造用它定 send/recv 队列深度与 SGE 上限（QueuePair.cpp:47-50）；QueuePairFactory 用它定握手缓冲尺寸与数据上限断言（QueuePairFactory.cpp:29/:76/:120）；Buffer/RegisteredMemory 用它定对齐粒度（Buffer.cpp:28、RegisteredMemory.cpp:26）；DEFAULT_IB_DEVICE 只在 bindToPort 的 IP 打印处出现（QueuePairFactory.cpp:68）。**例外**：`MAX_NUMBER_OF_OUTSTANDING_REQUESTS`（Configuration.h:31）全库零消费——纯文档性常量（注释解释"单 SRQ 下应小于 MAX_SRQ_WR"的道理，但没有任何代码读它）。

**infinity.h 的下游**：示例不引它（各自精引 6 头，read-write-send.cpp:14-19），README 接入指引则以它为准——它是给库用户而非库作者的门面。图谱中 infinity.h 入边来自 Makefile（分发清单），出边 13 条到全部模块头——L12 的"伞"名副其实。

## ④ 数据流

**构建流（make library）**：模式规则 :67-70 逐个编译 10 个 cpp——注意规则把**全部** SOURCE_FILES 与 HEADER_FILES 列为每个 .o 的先决条件，任何一个头文件改动都触发全量重编（正确性优先，无增量编译）。然后 :74-79：`ar rvs release/libinfinity.a` 归档 10 个 .o；`cp --parents` 把 14 个头按 src/infinity/... 路径复制进 release/；`mv release/src release/include` 一刀改名——最终 `release/include/infinity/*.h` 的目录结构与源码树完全同构，用户 `-I include` 即可。

**构建流（make examples）**：:89-92 以库用户视角编译两个示例（这正是它用 `-I $(RELEASE_FOLDER)/$(INCLUDE_FOLDER) -L $(RELEASE_FOLDER)` 的原因——示例就是"第一个用户"）。**隐含坑**：examples 目标不声明对 library 的依赖，单独 `make examples` 在 release/ 缺失时直接失败；`all: library examples`（:63）在串行 make 下保证顺序，`make -j` 并行时两目标无依赖关系存在竞态。

**接入流（用户侧）**：拷走 release/include/ 与 release/libinfinity.a → 源码 `#include <infinity/infinity.h>` → 链接 `-linfinity -libverbs`。三步即全部——这就是 barrel+静态库组合的分发哲学。

**配置流**：不存在。改队列深度=改 Configuration.h 重编；换网络参数=改 activate 硬编码（QueuePair.cpp:94-116，组1 05 篇）重编——"配置"在这个库里是编译期概念。

## ⑤ 设计决策

**零构建系统依赖**：94 行 Makefile 不依赖任何构建生成器——学术库的最小可移植性取舍（有 ibverbs-dev + g++ 就能编）。代价是无依赖跟踪、无跨目录增量、无平台分支。

**Configuration=编译期预算而非运行时配置**：7 个常量全部 `static const` 进代码段，编译器可内联成立即数——热路径零开销；代价是任何调参都是重编事件。与 activate 硬编码传输参数（组1 05 篇设计决策）同一哲学的两处落点。

**-D 开关矩阵存在但一根线都没接**：Debug.h 留了 INFINITY_DEBUG_ON/INFINITY_ASSERT_ON 两个编译开关（Debug.h:15/:21），但 Makefile:16 的 CC_FLAGS **不含任何 -D**——默认构建零断言零日志（ONBOARDING 坑①、12 篇详述）。想开调试只能手改 CC_FLAGS 加 `-DINFINITY_ASSERT_ON` 再 `make clean && make`。

**发布即 O3，无 -g 无 -Wall**：CC_FLAGS 只有 `-O3 -std=c++0x`（Makefile:16）——性能库发布姿态，但调试构建也得自己加 flag；16351 这类魔数在代码里没有任何编译期 static_assert 校验（对照注释里 "Must be less than" 的口头契约——真超设备上限要等到 ibv_create_cq/ibv_create_qp 运行时报错）。

**静态库-only**：只产 .a 不产 .so（无 -fPIC）——分发形态最简单，嵌入用户二进制无版本漂移问题。

## ⑥ 新人提示

上手顺序：先读 Configuration.h 的 30 行常量+注释建立"预算"心智图，再看 Makefile 的 library 段理解 release/ 布局，最后 infinity.h 一扫确认接入面。五个坑：①**调试三件套**——`CC_FLAGS` 加 `-g -DINFINITY_DEBUG_ON -DINFINITY_ASSERT_ON` 后必须 `make clean` 重编（Makefile:83-85），否则旧 .o 不带断言；②`make examples` 单独跑失败先 `make library`（:89-92 无依赖声明）；③16351 是"三处同值"——CQ 深度（Context.cpp:58-59）、QP 队列深度（QueuePair.cpp:47-49）、SRQ 深度（Context.cpp:65）互相绑定，改一处不改另两处可能在 post 高峰触发队列满；④改 MAX_NUMBER_OF_SGE_ELEMENTS>1 想用 multiWrite 时，须确认网卡 max_sge 真支持（QP 构造 :48/:50 直接拿它当上限）；⑤"ib0"（Configuration.h:47）是内核网络接口名不是 verbs 设备名——Context 选设备用序号（Context.h:65），两者命名空间无关，非 IPoIB 环境（RoCE 常见）打印不出 IP 但不影响功能（12 篇详述）。验收自测：说出 make library 的五个产物路径，以及为什么任何头文件改动都会全量重编。
