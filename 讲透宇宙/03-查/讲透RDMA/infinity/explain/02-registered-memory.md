# 02 RegisteredMemory——最底层内存注册原语：ibv_reg_mr 的直接封装

> 源文件：`src/infinity/memory/RegisteredMemory.h`（51 行）/ `src/infinity/memory/RegisteredMemory.cpp`（80 行）

## ① 角色定位

RDMA 的铁律：只有注册过的内存才能被网卡 DMA 触达——`ibv_reg_mr` 把一段虚拟内存钉页、建虚拟→物理映射、发放 lkey/rkey 两把钥匙。RegisteredMemory 就是这个动词的面向对象封装，处于 L03、内存线最底层：自己不参与通信，只负责"让一段内存变得可被 RDMA"。与 Region 体系的关系要分清：**它不是 Region 的子类**（继承树 Region.h:23 上只有 Buffer/Atomic 两片叶子），而是平行的"注册容器"；Buffer 通过视图构造消费它（Buffer.cpp:42-54），复用其 ibv_mr 免重复注册。

## ② 内部结构

全类仅 4 个成员、5 个方法（RegisteredMemory.h:17-45）：

- **双构造**：`(context, sizeInBytes)` 库内分配（RegisteredMemory.h:21）与 `(context, data, sizeInBytes)` 注册外部内存（RegisteredMemory.h:22）；
- **三访问器**：`getData()`（裸地址）、`getSizeInBytes()`、`getRegion()`（直接吐出 `ibv_mr*`，RegisteredMemory.h:29——名字有误导性，返回的是 verbs 内存区域句柄而非 Region 对象）；
- **成员**：context/data/sizeInBytes/ibvMemoryRegion + 所有权标志 `memoryAllocated`（RegisteredMemory.h:43）。

## ③ 外部连接

**依赖**：构造时从 Context 取 `getProtectionDomain` 做 MR 注册的挂靠点（RegisteredMemory.cpp:31/44）；`Configuration::PAGE_SIZE` 提供对齐粒度（Configuration.h:43）；Debug.h 提供断言宏。

**被谁用**：主要消费者是 Buffer 的视图构造（Buffer.cpp:48-49：`data = memory->getData() + offset; ibvMemoryRegion = memory->getRegion()`）——大块注册一次、按 offset 切多个 Buffer，省去逐段注册的页表开销；图谱中 `RegisteredMemory.h→Context.h` 的依赖边与 `Buffer.h→RegisteredMemory.h` 的消费边构成内存线 L03→L06 的通道。注意：QueuePair 的任何操作签名都不收 RegisteredMemory——通信层只见 Buffer/RegionToken；grep 实证两个示例与 README 也零引用它——这是个"库能力完整、示例未演示"的可选原语，最短用法就是 Buffer 视图构造。

## ④ 数据流

**分配+注册构造**（RegisteredMemory.cpp:20-34）：`posix_memalign` 按 PAGE_SIZE=4096 页对齐分配（:26，页对齐利于 NIC pin 页效率）→ `memset` 清零（:29）→ `ibv_reg_mr` 以三权限注册（:31-32）：`IBV_ACCESS_REMOTE_WRITE | IBV_ACCESS_LOCAL_WRITE | IBV_ACCESS_REMOTE_READ`，并置 `memoryAllocated=true`（:24）。

**外部内存构造**（RegisteredMemory.cpp:36-47）：跳过分配，直接对调用者给的指针注册，`memoryAllocated=false`（:40）。两条路权限位完全相同。

**析构**（RegisteredMemory.cpp:50-58）：`ibv_dereg_mr` 注销（:52）→ 仅当 `memoryAllocated` 才 `free(data)`（:54-55）——所有权标志决定是否释放非库内内存。

**getRegion() 的流向**（RegisteredMemory.cpp:72-76）：ibv_mr 句柄交给 Buffer 视图后，Buffer 的 lkey/rkey 查询（Region.cpp:53-59）实际读的是这同一个 ibv_mr——多个 Buffer 视图共享一份钥匙。

## ⑤ 设计决策

**为什么独立于 Region 体系**：Region 表达"一段可进工作请求的内存视图"（有类型、可切 token），RegisteredMemory 表达"一次注册动作的产物"（有 ibv_mr、有所有权）。注册是昂贵操作（pin 页+内核页表），视图是零成本切片——把两者拆开才能支持"一次注册、多视图"的池化用法，这正是其存在价值；对照 Buffer 三构造（Buffer.cpp:22-70）中专门为视图留一条路可见设计意图。

**权限位写死且不含 REMOTE_ATOMIC**：三权限覆盖 read/write 场景，但 `IBV_ACCESS_REMOTE_ATOMIC` 缺席——只有 Atomic 类注册时带它（Atomic.cpp:25-26）。想对 RegisteredMemory 管的内存做远端 CAS 会因权限不符被网卡拒绝，这是有意的安全默认：原子操作只该落在专用的 8 字节槽上。

**getRegion() 暴露裸句柄**：破坏了 Context 那种 friend 封装的一致性，但换取视图构造的零开销——工程上"小口子换大便利"的典型取舍。

**无 dereg/重注册的动态接口**：类一旦建立终身不变（没有 resize——那是 Buffer 的能力，且 Buffer::resize 也只对自注册内存开放，Buffer.cpp:108）。

## ⑥ 新人提示

上手顺序：先看 Buffer.cpp:42-54 的视图构造，理解这个类"为谁服务"，再回来读两个构造函数。四个提醒：①**尾注释残留**——文件末尾 `} /* namespace pool */ } /* namespace ivory */`（RegisteredMemory.cpp:78-79）与头部 `namespace infinity { namespace memory {`（:17-18）不匹配，ivory/pool 是作者前身项目代号（曾在 pool::ivory 命名空间下），注释残留不影响编译，但别被它带偏命名空间理解；②注册外部内存时调用者必须保证该内存在 RegisteredMemory 存活期间不被释放；③它没有 createRegionToken——要发凭证得先包一层 Buffer；④4096 对齐只对自分配路径生效，外部内存指针的对齐由你负责（未对齐不影响正确性，只影响性能）。
