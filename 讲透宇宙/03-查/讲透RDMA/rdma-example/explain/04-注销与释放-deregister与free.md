# 04 注销与释放：rdma_buffer_deregister 与 rdma_buffer_free

> 对应导览第 4 步「注销与释放：对称的逆操作」｜节点：`function:src/rdma_common.c:rdma_buffer_deregister`、`function:src/rdma_common.c:rdma_buffer_free`

## ① 角色定位

MR 四件套的后两件，与第 3 篇的 alloc/register 构成镜像：register↔deregister 严格对偶（只动注册状态），alloc↔free 对偶且 free **隐含** deregister（先注销再释放内存）。它们在图谱第 3 层「内存注册底座」与 alloc/register 同层，但只在两端的收线函数里被调用——即整个生命周期的最后一幕。别小看这对十几行的函数：**清理顺序错误是 RDMA 程序最经典的崩溃源**（销毁尚被 in-flight WR 引用的资源、double-free、use-after-free），本篇把它讲透，第 13 步两端 cleanup 对照阅读时就有参照。

## ② 内部结构

**`rdma_buffer_deregister(mr)`**（`src/rdma_common.c:94-105`）：
1. 判空容错（`:96-99`）——NULL 只打日志即返回，不崩。
2. debug 打印 addr/length/lkey（`:100-103`）——默认构建里是空操作（见第 2 篇勘误①）。
3. `ibv_dereg_mr(mr)`（`:104`）——**返回值被丢弃**：注销成功则解除 pin、释放 mr 结构体本身；失败（如 EBUSY）只影响日志，调用方无感知。

**`rdma_buffer_free(mr)`**（`src/rdma_common.c:82-92`）三步，顺序是精髓：
1. 判空容错（`:84-87`）。
2. `void *to_free = mr->addr;`（`:88`）——**先把缓冲地址从 mr 里拷出来**。
3. `rdma_buffer_deregister(mr)`（`:89`）→ `free(to_free)`（`:91`）。

为什么第 2 步必须先存地址：`ibv_dereg_mr` 成功后 `struct ibv_mr` 本体被 libibverbs 释放，`:91` 若再写 `free(mr->addr)` 就是读已释放结构体的 use-after-free。一行临时变量挡掉一个真实崩溃类。

## ③ 外部连接（图谱 calls 边）

4 条边，全部来自两端收线函数：

- `rdma_server.c:disconnect_and_cleanup → rdma_buffer_free`：现场 `src/rdma_server.c:403`，free 的是 `server_buffer_mr`——**alloc 来的**（第 3 篇表格）。
- `rdma_server.c:disconnect_and_cleanup → rdma_buffer_deregister`：现场 `src/rdma_server.c:404-405`，deregister 两个 metadata MR——**register 来的**（指向全局结构体 `client_metadata_attr/server_metadata_attr`，`src/rdma_server.c:23`）。
- `rdma_client.c:client_disconnect_and_clean → rdma_buffer_deregister`：现场 `src/rdma_client.c:438-441`，连 deregister 四个 MR（server_metadata/client_metadata/client_src/client_dst）——全部 register 来的。
- 此外 client 收线里还有两行裸 `free(src); free(dst);`（`src/rdma_client.c:443-444`）——这两个缓冲在 `main` 里 calloc（`src/rdma_client.c:478,485`）、但 src/dst 后来又被 register 过（`:247,313`），所以收线时先 dereg（MR 层）再 free（内存层），**两层生命周期分开管理**。

注意配对纪律在代码里体现得非常工整：服务端 alloc 的恰好 free、register 的恰好 deregister；客户端 register 的全部 deregister、calloc 的另走 free。

## ④ 数据流

以服务端收线（`src/rdma_server.c:361-421`）为时间轴，MR 清理嵌在整条资源销毁链的什么位置：

等 DISCONNECTED 事件（`:367-369`）→ ack（`:375`）→ **销毁 QP**（`:383`）→ 销毁 client cm_id（`:385`）→ 销毁 CQ（`:391`）→ 销毁完成通道（`:397`）→ **free server_buffer_mr（`:403`，内部先 dereg）** → deregister 两个 metadata MR（`:404-405`）→ 销毁 PD（`:407`）→ 销毁监听 id（`:413`）→ 销毁 CM 事件通道（`:418`）。

关键时序事实：**QP 销毁先于一切 MR**——QP 没了就不可能再有新的 in-flight WR 引用这些 MR，之后的 deregister 不会撞 EBUSY；**PD 销毁晚于所有 MR**——MR 归属 PD，PD 先死会让悬挂的 MR 变成无效资源。整条链是"使用者的逆序销毁"（LIFO）。

## ⑤ 设计决策

- **为什么 API 不对称（free 含 dereg、dereg 不含 free）**：alloc=「分配+注册」的复合，其逆操作自然=「注销+释放」的复合逆序；register 是单动作所以 dereg 也是单动作。复合函数的逆=分量逆的倒序执行，这是 API 设计里少见的教科书式对称。
- **为什么 deregister 不顺带 free**：register 面对的内存可能是全局变量、栈对象、调用方管理的池——库层根本不知道也不拥有这块内存，free 不属于自己的东西是 API 大忌。所有权决定清理责任，本仓的 alloc/free 边界就是所有权边界。
- **收线函数的错误风格**：每个 destroy 失败都只 `rdma_error` + `// we continue anyways`（如 `:387-389`）——收线路径上"尽力而为继续拆"优先于"精确失败上报"，因为此时已无重试意义，卡住反而泄漏更多。与数据面"任何失败立即 return"形成刻意的风格反差。

## ⑥ 新人提示（坑与勘误）

1. **配对规则是硬约束**：alloc 来的必须 free（只 dereg 会泄漏缓冲内存）；register 来的只能 dereg（误用 free 会 free 掉全局/栈内存→崩溃或腐蚀）。本仓两端现场（`:403-405`、`client:438-444`）是正确示范，抄就抄这个纪律。
2. **ibv_dereg_mr 返回值被忽略**（`src/rdma_common.c:104`）：若仍有未完成的 WR 引用该 MR，dereg 返回 EBUSY 且**注销失败**，本函数静默吞掉——调用方以为干净了实则 pin 仍在。教学例靠"等 DISCONNECTED+全部 WC 已收割"前置条件保证不触发，复用时建议改成检查返回值。
3. **free 里 dereg 失败后仍会 free**（`:89-91` 无条件顺序执行）：dereg EBUSY 失败后照样 `free(to_free)`——网卡若还持有该映射，free 后的内存可能被网卡继续 DMA 写坏。同样是靠前置条件兜底的教学简化。
4. **NULL 容错只打日志不报错**：deregister/free 传 NULL 不会让调用方得知异常（`:96-99,84-87`），收线代码的健壮性完全依赖静态保证。
5. 客户端 `src/rdma_client.c:443-444` 的裸 free 与 `:438-441` 的 dereg 是**同一块内存的两层**——初学者常误以为 dereg 已经释放了 src/dst，从而疑惑这两行是否 double-free：不是，register 不转移内存所有权（见第 3 篇⑤），calloc/free 一层、注册/注销一层。

——MR 生命周期至此闭环。下一篇看本仓"能写成顺序风格"的秘诀：两个事件同步原语。
