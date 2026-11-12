# 03 gpu_mem_util 显存管理：BDF 选卡与 64KB 对齐分配

> 对应 tour 第 5 步「找一块显存：BDF 选卡与 64KB 对齐分配」。行号锚均对 gpu_mem_util.c / client.c 对 HEAD `a99d506` 核实。

## 一、角色定位

gpu_mem_util.c（278 行）是全仓唯一的 CUDA 触点，职责被刻意压到最小：**给上层一个"像 malloc 一样"的显存分配接口，并且允许你用 PCI BDF 指定用哪块卡**。对外只露两个函数——`work_buffer_alloc(length, use_cuda, bdf)` 与 `work_buffer_free(buff, use_cuda)`（gpu_mem_util.h:45、:50），client.c:347 一行调用即完成选卡+分配。它存在的意义有两层：其一把 CUDA Driver API 的六步仪式（cuInit→选设备→建 context→cuMemAlloc）封装成一步；其二让 RDMA 注册（第 5 篇）拿到的指针天然满足 GPU Direct 的页对齐前提。性能根源上，README.md:6 的告诫——选与 NIC 同 PCI bridge 的 GPU——最终就落在本文件的 `get_gpu_device_id_from_bdf` 上。

## 二、内部结构

文件是一个三层洋葱：**外层（无条件编译）**是两个对外函数 work_buffer_alloc（gpu_mem_util.c:232-258）与 work_buffer_free（:263-275），加上 extern 的 debug 开关（:58-59）与四组 DEBUG 宏（:61-64）；**中层**是 `#ifdef HAVE_CUDA` 包起来的错误处理宏（:66-78：ASSERT 打印不退出、CUCHECK 包装返回值）与文件级静态 `cuContext` 句柄（:82）；**内层**是四个静态 CUDA 函数：

- `print_gpu_devices_info`（:87-111）：debug 时枚举全部设备，打印序号/名字/BDF——cuDeviceGetCount（:92）+ 循环 cuDeviceGet/cuDeviceGetName/cuDeviceGetAttribute 三件套（:103-106）。
- `get_gpu_device_id_from_bdf`（:113-154）：BDF→CUDA 设备序号的翻译器。
- `init_gpu`（:156-211）：分配主流程。
- `free_gpu`（:213-225）：cuMemFree + cuCtxDestroy（:218、:222）。

注意 pci_func 硬编码为 0 并注明 "always 0 for CUDA device"（:101）——GPU 是单功能 PCI 设备，这解释了 BDF 校验为何拒绝非 0 function（:129-132）。

## 三、外部连接

- **向上：client.c**。唯一的消费方是 client.c:347 的 `work_buffer_alloc(usr_par.size, usr_par.use_cuda, usr_par.bdf)`，返回指针随即交给 `rdma_buffer_reg`（client.c:362）；server.c 虽也 include gpu_mem_util.h（server.c:49），但其 work_buffer_alloc 调用固定 use_cuda=0，走 CPU 分支。`-u` 参数的 usage 文案在 client.c:200-201。
- **向旁：map_pci_nic_gpu.sh**。第 2 篇讲的拓扑脚本输出 BDF，本文件的解析器把它变回设备序号——脚本与人约定格式，sscanf 与格式约定一致（"%x:%x.%x"，:123）。
- **向下：CUDA Driver API**。全部走 driver 层（cuda.h，:53）而非 Runtime API——cuInit/cuCtxCreate/cuMemAlloc（:164、:188、:203）返回 CUresult 错误码，被 CUCHECK 宏统一吞掉只打印（:74-78）。选 driver API 不是炫技：显存指针需要作为裸地址传给 verbs（ibv_reg_mr 吃 void*），driver 层的 CUdeviceptr 就是裸 64 位地址（:210 直接强转返回），没有 runtime 层的 host 拷贝语义拖泥带水。
- **向内核：nv_peer_memory**。本文件不直接引用它，但 cuMemAlloc 出的页若没有该内核模块配合，后续 ibv_reg_mr 会失败——这条隐式依赖链在 README.md:42。

## 四、数据流

分配链路（client `-u b7:00.0` 时）：work_buffer_alloc 判 use_cuda（:236）→ init_gpu 进入：**第一步对齐**，`aligned_size = (size + 64K - 1) & ~(64K - 1)`（:158-162），4096 字节请求会实占 64KB；**cuInit(0)**（:164）；debug 时打印设备清单（:170-172）；**BDF→序号**：get_gpu_device_id_from_bdf 先 sscanf 校验格式（:123-132），再 cuDeviceGetCount（:133），逐设备取 PCI bus/device 属性比对（:140-151），命中返回序号 i，全空则报错（:152-153）；**按序号取设备**（:184）；**建 context**：cuCtxCreate 带 `CU_CTX_MAP_HOST` 标志（:188），失败即返回 NULL（:189-192），再 cuCtxSetCurrent 挂到当前线程（:195）；**cuMemAlloc**（:203）拿 CUdeviceptr 强转 void* 返回（:210）。

释放链路反向：work_buffer_free→free_gpu→cuMemFree（:218）→cuCtxDestroy（:222）。CPU 分支则简单得多：memalign(页大小, length)（:249-250）与 free（:273）。

数据流的关键约束：**返回的指针在同一 CUDA context 内有效**。静态 cuContext（:82）是文件级单例，意味着一个进程只能伺候一块 GPU 的一个 context——样例的"单 client 单卡"假设写死在数据结构里，多卡场景此文件需要重设计。

## 五、设计决策

- **为什么用 BDF 而非设备序号选卡**：CUDA 的 ordinal 在驱动重枚举后可能变化，而 PCI 拓扑位置物理稳定；更重要的是 BDF 直接对应 map 脚本的输出，把"离 NIC 最近"这个性能诉求变成可传递的参数（README.md:6、:86-88）。
- **为什么 64KB 对齐**：与 nv_peer_memory 的 pin 粒度匹配（GPU 显存页常见 64KB，即 2MB 大页的 1/32 场景也有，样例取保守 64K），不对齐会在注册时产生跨页碎片甚至注册失败；取整开销在样例尺度（默认 4096 字节→64KB）完全可接受（:158-162）。
- **为什么 CU_CTX_MAP_HOST**：允许后续把主机内存映射进 GPU 地址空间（样例未用，是为常见扩展留的口子），也避免某些平台上锁定主机页的额外开销（:188）。
- **为什么 ASSERT 不退出**：CUCHECK 检测到错误只打印继续跑（:67-78），样例代码追求"看得见错误"，生产代码该改成 fail-fast——读样例时别把这当范本。
- **为什么分配对齐暴露、错误吞掉**：对齐影响 RDMA 注册成败，必须在函数内保证；CUDA 错误码则在每步打印后以 NULL 逐层上抛（:165-167、:175-180 等），调用方 client.c:348-351 只判 NULL。

## 六、新人提示

1. **`#ifdef HAVE_CUDA` 是静态分析盲区**（ONBOARDING 勘误 #2 的源）：不开 USE_CUDA 编译时 init_gpu 等符号不存在（gpu_mem_util.c:66-226），IDE 的跳转/交叉引用会大片失效；读这段代码请确保理解它是"半个文件"。
2. **use_cuda 与 HAVE_CUDA 是两个不同的开关**：前者运行时（`-u` 给没给），后者编译期（USE_CUDA=1）。运行时给 `-u` 但编译没开 CUDA，会得到 "Can't init GPU, HAVE_CUDA mode isn't set"（:241）——这错误文案就是两开关错配的唯一提示。
3. **BDF 大小写与宽度**：sscanf 用 %x，`b7:00.0` 与 `B7:00.0` 都能过；但 bus/device 各自按实际宽度比较（cuDeviceGetAttribute 返回的是数值不是字符串，:148），所以 `0b7:00.0` 这类多写前导零也兼容。
4. **context 单例的坑**：若上层还想自己建 CUDA context（比如跑 kernel 验证数据），必须复用本文件的 cuCtxSetCurrent 语义，否则 cuMemFree 会作用在错误 context 上——free_gpu 假设调用线程的 current context 仍是它（:222）。
5. **验证数据有没有真到显存**：debug 模式下 client.c:434-436 守住了不打印显存；要看内容得在 client 侧另起 CUDA 代码 D2H 拷出来，或用 nvidia-smi 看显存占用（ allocations 会显示 64KB 档位）。
6. **显存泄漏路径**：work_buffer_free 只在 use_cuda 为真时走 free_gpu（:265-270），若 alloc 成功后 RDMA 注册失败跳出（client.c:363-366），client.c:451-452 的 clean_mem_buff 标签保证了 free 仍会执行——读 main 时注意这套 goto 清理链与 use_cuda 标志的配合。
