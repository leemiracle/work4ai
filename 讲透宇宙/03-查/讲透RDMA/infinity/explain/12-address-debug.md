# 12 Address 与 Debug——地址探测工具和全局宏开关：线上静默吞断言的根源

> 源文件：`src/infinity/utils/Address.h`（29 行）/ `src/infinity/utils/Address.cpp`（58 行）/ `src/infinity/utils/Debug.h`（27 行）

## ① 角色定位

utils 目录双子，体量最小（合计 114 行）却埋着全库影响面最大的坑。**Address 是启动期 IP 探测工具**：两个静态方法，唯一的库内消费者是 QueuePairFactory::bindToPort 打印"我在哪个 IP 上等连接"（QueuePairFactory.cpp:68-70）——纯人机交互用途，不参与任何数据通路。**Debug 是全局断言/日志宏开关**：INFINITY_DEBUG 与 INFINITY_ASSERT 两个宏（Debug.h:15-19/:21-25），承载全库 64 处断言与 14 处调试日志——但两个开关默认都不开、Makefile 一根 -D 都没接（Makefile:16），**默认编译下所有断言与日志全部展开成空 `{}`**，这是 ONBOARDING 坑①钉版的"线上静默吞断言"，本篇从源码层面把它讲透。

## ② 内部结构

**Address**（Address.h:21-22）：`getIpAddressOfInterface(const char *interfaceName)` 返回新 malloc 的点分 IP 字符串（16 字节堆缓冲，Address.cpp:27——恰好装下最长 IPv4 串 15 字符+NUL）；`getIpAddressAsUint32(const char *ipAddress)` 把点分串打成 uint32。无状态无成员，纯函数集合。

**Debug**（Debug.h:15-25）：两宏同构异义——`INFINITY_DEBUG(X, ...)` 开关下 fprintf 到 stdout 并 fflush；`INFINITY_ASSERT(B, X, ...)` 开关下 `if(!(B)) { fprintf(stdout,...); fflush; exit(-1); }`。宏体共享一个特性：**关闭态是 `{}`**，连条件 B 都不求值。

## ③ 外部连接

**Address 的消费**：库内唯一调用链是 bindToPort——`getIpAddressOfInterface(Configuration::DEFAULT_IB_DEVICE)`（QueuePairFactory.cpp:68，"ib0" 定义于 Configuration.h:47）→ INFINITY_DEBUG 打印 IP 与端口 → `free(ipAddressOfDevice)`（:70，调用方负责释放的契约在此兑现）。**getIpAddressAsUint32 是死代码**：grep 全库（含示例与 README）零调用——现存 connectToRemoteHost 用的是 `inet_pton`（QueuePairFactory.cpp:129），这个手工打包函数大概率是早期版本用 uint32 组 sockaddr_in 的遗迹。

**Debug 的消费**（按 grep 计数）：INFINITY_ASSERT 64 处——QueuePair.cpp 28、Context.cpp 14、QueuePairFactory.cpp 13、Buffer.cpp 4、RegisteredMemory.cpp 3、Address.cpp 2；INFINITY_DEBUG 14 处——QueuePair.cpp 9、QueuePairFactory.cpp 3、Context.cpp 2。也就是说 Debug.h 虽只 27 行，却是**全库错误面的全部**——每一个 verbs 调用的失败检查都长在这两个宏上。

## ④ 数据流

**getIpAddressOfInterface**（Address.cpp:23-47）：`getifaddrs` 枚举本机全部网络接口（:29，失败断言 :30）→ 遍历链表：无地址的接口跳过（:33-35），`AF_INET && strcasecmp(名字匹配)` 命中即 `sprintf(inet_ntoa(...))` 拷进结果缓冲并 break（:36-39）→ 循环自然结束仍未命中则断言 ifa!=NULL（:41）→ `freeifaddrs`（:43）→ 返回堆串（:45）。两条边界：只认第一个 IPv4 地址（IPv6 与多地址接口不支持）；**接口不存在时唯一的报错手段是 :41 的断言——默认编译下被吞，函数安静地返回全零空串**。

**getIpAddressAsUint32**（Address.cpp:49-55）：`sscanf("%d.%d.%d.%d")` 按倒序写入数组 [3][2][1][0]（:52），再位拼 `n[0] | n[1]<<8 | n[2]<<16 | n[3]<<24`（:53）——首段落在最低字节的主机序打包。两个瑕疵：`%d` 对 `uint32_t*` 是严格的格式-类型不匹配（常见 ABI 上能跑，标准口径 UB）；sscanf 返回值不检查，坏串全零静默通过。

**Debug 宏的两态展开**：开（如 `-DINFINITY_ASSERT_ON`）：`if(!(B)) { fprintf(stdout, X...); fflush(stdout); exit(-1); }`——打印到 **stdout 而非 stderr**，退出码 `-1`；关（默认）：整宏变 `{}`。关键推论三条：①关闭态**条件不求值**——断言里绝不能写带副作用的表达式（写了就是"开了才执行"的隐藏分支）；②开启态也**不含 `__FILE__`/`__LINE__`**——打印的只有调用方手写的消息串（如 Buffer.cpp:35 的 "Registration failed"），出了错知道"错了"不知道"哪错了"，定位靠 grep 消息文本；③`exit(-1)` 而非 `abort()`——不产 core dump，死后现场只能靠日志反推。

## ⑤ 设计决策

**默认全关的性能哲学及其代价**：性能库把"发布二进制零检查开销"推到极致——64 处断言在 -O3 下全部蒸发，热路径与手写 verbs 无异。代价是所有防御性检查同时蒸发：multiWrite 的 SGE 上限（QueuePair.cpp:341/:394）、resize 的所有权检查（Buffer.cpp:108）、握手数据上限（QueuePairFactory.cpp:76/:120）、连接失败（:136）——违规输入不再是"报错退出"而是静默 UB。这是**性能与可诊断性的单边取舍**：库作者假设使用者是知情者。

**错误报告口径的极简**：就算开宏，也只有 stdout 一行消息 + exit(-1)——没有严重级别、没有结构化、没有位置。对照现代实践（spdlog/errno 链），这是 2018 年学术原型库的时代印记；好处是零依赖、行为完全可预测。

**Address 与 verbs 设备的双命名空间**："ib0"（Configuration.h:47）是**内核网络接口名**（IPoIB），Context 选 HCA 用的是设备列表序号（Context.h:65）——两者没有任何绑定关系。打印 IP 只是帮用户抄地址用，**连不上/打不出 IP 不影响任何功能正确性**；反过来，机器上没有 ib0 接口时（RoCE 场景常见）bindToPort 的完整行为是：断言 :41 被吞 → 返回空串 → INFINITY_DEBUG 也被吞 → **一行输出都没有，连接照常工作**——"完全静默"的完整链条。

**死代码不删**：getIpAddressAsUint32 零调用仍留在 umbrella 头分发的公开面上（infinity.h:23）——用户可能真的调它（手工组地址），删了破坏 API 兼容；这是小库"宁留勿破"的常见姿态。

## ⑥ 新人提示

上手顺序：先读 Debug.h 的 13 行宏体把两态展开写在手边，再读 Address.cpp:23-47 的 25 行，最后把 ONBOARDING 坑①的结论与 QueuePairFactory.cpp:68-70 的调用链对上。五个坑：①**线上排障第一件事**：CC_FLAGS 加 `-DINFINITY_ASSERT_ON`（配合 -g）`make clean` 重编——64 处断言才真正上岗；排查完记得改回去，开断言的库不该上生产；②断言表达式里永远别放副作用（关闭态不求值）；③Address 返回堆串，调用方必须 free（QueuePairFactory.cpp:70 是标准示范）；④非 IPoIB 环境别指望 bindToPort 告诉你 IP——它可能一行都不打印，这是特性不是 bug；⑤排错时 grep 断言消息文本（如 "Registration failed"）定位出错点——宏不带文件行号，消息串就是唯一的身份证。验收自测：向同伴完整复述"一台没有 ib0 接口的 RoCE 机器上跑 server，从 bindToPort 到 accept 之间用户会看到什么、为什么"。
