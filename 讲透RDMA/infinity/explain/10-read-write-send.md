# 10 read-write-send 与 send-performance——示例全链走读：库的官方用法说明书

> 源文件：`src/examples/read-write-send.cpp`（105 行）/ `src/examples/send-performance.cpp`（178 行）

## ① 角色定位

两个示例处于 L11，是库对外的"活文档"：README 的快速上手代码不可编译（组1 ONBOARDING 坑②），**真实的用法权威就在这两个文件**。read-write-send 是最小可运行的教程——128 字节内存把单边 read/write、双边 send、握手传 token、完成等待一次走完；send-performance 是吞吐基准——13 档消息尺寸 ×1024 次发送，示范 fire-and-forget 加窗口同步的 在途控制 技巧。两者共用端口 8011（read-write-send.cpp:21，send-performance.cpp:23）与"一个 main 双端分叉"的形态。

## ② 内部结构

**read-write-send.cpp**：常量区 :21-22（PORT_NUMBER 8011 / SERVER_IP "192.0.0.1" 硬编码）；手写参数解析 :29-42（`while(argc>1)` 逐个吃 argv，只认 `-s`）；公共初始化 :44-46（Context/QueuePairFactory/qp 声明）；server 分支 :48-69 与 client 分支 :70-97；统一清理 :99-101。

**send-performance.cpp**：常量区 :23-27（BUFFER_COUNT 128 / MAX_BUFFER_SIZE 4096 / OPERATIONS_COUNT 1024）+ 前置声明的 `timeDiff`（:29，实现 :176-178）；server 分支 :55-105、client 分支 :107-166。头文件只引公共面六头（两文件各自 :14-21/:16-21），一行不碰 protected——friend 包围圈（组1 01 篇）在用户侧的体现。

## ③ 外部连接

示例是全部公共 API 的巡礼：Context 构造（read-write-send.cpp:44）、postReceiveBuffer（:56）、receive（:63-64）、QueuePairFactory 的 bindToPort/acceptIncomingConnection/connectToRemoteHost（:59/:60/:73，组1 06 篇）、QueuePair 的 read/write/send（:83/:87/:91，组1 05 篇）、Buffer 三构造之一（:51/:55/:78-79，07 篇）、RequestToken 栈上复用（:82，09 篇）、`qp->getUserData()` 强转拿远端 token（:74）。握手通道的 POD memcpy hack 在 :60 亮相：`acceptIncomingConnection(bufferToken, sizeof(infinity::memory::RegionToken))` 把 token **整对象按字节**塞进握手（组1 ONBOARDING 设计决策②、04 篇），client :74 反向强转回来——零序列化的跨机传递。

## ④ 数据流

**server 侧（read-write-send :48-69）**：建 128 字节 Buffer（:51）→ 铸 token（:52）→ 建接收 Buffer 并 post 到 SRQ（:55-56）→ bindToPort 阻塞等连接（:59）→ accept 时把 token 当握手数据回给对端（:60）→ `while(!context->receive(&receiveElement))` 忙等双边消息（:63-64）→ 收到即删两个 Buffer（:67-68）。注意 server 全程没碰 RequestToken——**接收侧的完成面是 Context::receive，不是 token**（09 篇钉版的路径二分）。

**client 侧（:70-97）**：connect（:73）→ 从握手 userData 强转出远端 token（:74）→ 建 buffer1Sided/buffer2Sided（:78-79）→ 栈上一个 RequestToken 连打三发：`read`（:83）把远端 128 字节拉进本地，`waitUntilCompleted`（:84）后数据可读；`write`（:87）把同一 buffer 写回远端；`send`（:91）走双边。每发之间 wait（:84/:88/:92）——read 的 wait 返回即数据已落本地（09 篇读侧语义）。三发复用一个 token 安全，因为 QueuePair 每次自动 reset（QueuePair.cpp:156-158）。

**send-performance 的 server（:55-105）**：预挂 128 个 4096 字节接收 Buffer（:58-62，SRQ 深度从此有 128 条垫底）→ accept 不带数据（:66，纯双边基准不需要 token）→ **首消息热身**：收一条重挂一条（:68-71，注释直言"first message has additional setup costs"——首条要建连接态/缓存路径，不热身会污染 1 字节档成绩）→ 测量循环：13 档尺寸（1→4096 翻倍，`rounds=(uint32_t)log2(4096)=12`，:76/:78）各收 1024 条，收一条重挂一条（:84-88）→ 全收完后**反向发 1 字节通知 client**（:95-98，defaultRequestToken 公共槽的首秀）。

**send-performance 的 client（:107-166）**：connect（:110）→ 建 4096 发送 Buffer 与 1 字节接收 Buffer（:113-115）→ 同样热身发 1 字节（:117-119）→ 计时循环（:121-158）：每档 `gettimeofday` 取起止墙钟（:130-131/:147-148），1024 次发送里**每逢 i%128==0 才建栈上 token 同步等待，其余 127 次全 fire-and-forget（NULL token）**（:134-144）；打印 msgRate 与 bandwidth（:153）。

**计时口径专节**（引用须谨慎的部分）：msgRate = `OPERATIONS_COUNT × 1e6 / timeμs`（:151），bandwidth = `ops×size / MiB / (timeμs/1e6)`（:152）——分母把微秒换回秒，单位实为 MiB/s 却印成 "MB/sec"（:153，标签不严谨）。四个口径特征：①**热身不计时**（:68-71/:117-119）；②计时窗含 8 次同步等待（i=0,128,...,896 各一次 waitUntilCompleted）——测的是"带周期性流控的稳态吞吐"，不是裸 post 速率；③末尾 127 条在途消息**不等待完成**就按表（:147-148，`i==OPERATIONS_COUNT` 是永假死条件：循环内 i 最大 1023）——时间略乐观；④**对端接收不计时**，但 :160-162 等 server 通知的忙等在计时窗外，间接兜底确认了全部消息落地。对照引用：这是"发送侧吞吐"口径，与双端对齐的 RTT/带宽基准不同类。

## ⑤ 设计决策

**一个 main 双端分叉**：`-s` 参数决定角色（:29-42/:36-49），两个二进制源码各只一份——示例维护成本减半，代价是读者要在脑内把同一文件劈成两半看。

**忙等贯彻到底**：receive 与 waitUntilCompleted 全是 while 忙轮（:64/:84，Context.cpp:172 与 RequestToken.cpp:41 的非阻塞原语在用户侧的标准包装）——与库"等待策略交上层"的哲学（组1 01 篇）一致，示例选择最激进的零延迟策略。

**128 窗口是自律示范**：send-performance.cpp:134-144 把 fire-and-forget（无 CQE，组1 05 篇）与显式同步按 128:1 配比——在途上限 ≈127 远低于 CQ 深度 16351（Configuration.h:25），既不撑爆完成队列又避免逐条等待的吞吐塌方；窗口大小与 server 预挂的接收 Buffer 数（:58-62）同取 BUFFER_COUNT=128，暗合"对端 SRQ 不会干涸"的背压直觉。

**通知机制演示 receive/send 对偶**：server 收完用 1 字节 send 告诉 client（:95-98）——单边操作没有对端事件，双边 send 才有；要给单边补通知就用 writeWithImmediate（组1 05 篇），此处用最朴素的 send 完成"基准跑完了"的信令。

## ⑥ 新人提示

上手顺序：先跑通 read-write-send（server 先起，client 改 SERVER_IP 重编），对照本篇 ④ 把 client 三发逐行映射到 QueuePair.cpp 的三个 opcode（IBV_WR_RDMA_READ :470 区、IBV_WR_RDMA_WRITE :265、IBV_WR_SEND :177）；再读 send-performance 的 :134-144 吃透窗口技巧。五个坑：①SERVER_IP 硬编码 "192.0.0.1"（read-write-send.cpp:22）——每台 client 都要改源码重编，:24 的注释也承认这点；②server 必须先起，否则 client 的 connect 直接断言失败（QueuePairFactory.cpp:135-136，且默认编译下该断言被编译掉——见 12 篇）；③send 用的 buffer2Sided 从未填过内容（:79/:91）——演示的是通信语义不是数据语义，别期待收到有意义的内容；④性能数字不能直接外推：128 窗口+末段不等待+发送侧口径三重偏差都在同方向（偏乐观）；⑤两示例共用 8011，同机对跑会端口冲突；想单机自测参考 createLoopback（QueuePairFactory.cpp:171-181，组1 06 篇）。验收自测：手画 client 侧时序图，标出三处 waitUntilCompleted 各自保证了什么。
