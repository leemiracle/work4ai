# 06 khash 与 GID 辅助层：klib 定制宏与 sysfs 探测的地基

> 对应 tour 第 6 步「库的地基：khash 哈希与 sysfs/GID 辅助」。锚均对 HEAD `a99d506` 核实。

## 一、角色定位

两个头文件撑起核心库的两块地基。**khash.h（674 行）**是 Attractive Chaos 的 klib 开源哈希表，但**不是原版**——本仓改造了宏接口以适配"C 头文件声明、单 .c 实现"的工程化编译模式，第 5 篇的 AH 缓存就长在它上面。**ibv_helper.h（178 行）**是一小段从 libibverbs 源码里抽出来的系统调用糖衣：直接读 sysfs 判断每个 GID 表项是 RoCE v1 还是 v2，给 `rdma_set_lid_gid_from_port_info` 提供"自动定位 RoCE v2 sgid 索引"的能力（gpu_direct_rdma_access.c:350-353 的调用点）。两者都不是 RDMA 逻辑本身，却决定了库的两个质量属性：缓存的零开销、GID 选择的免手配。

## 二、内部结构

**khash.h 的定制版痕迹**。上游 klib 只有 `KHASH_INIT` 一条单体宏：类型定义+全部实现一次性在**每个包含它的翻译单元**里展开成 static 函数。本仓在保留原宏（khash.h:375-380）之外，新增了两段式拆分（ONBOARDING 勘误 #1）：

- `KHASH_TYPE(name, khkey_t, khval_t)`（:382-383）只展开 `__KHASH_TYPE`（:197-202）——仅生成 `typedef struct kh_##name##_s {...}` 类型；
- `KHASH_IMPL(name, khkey_t, khval_t, kh_is_map, hash, equal)`（:385-386）只展开 `__KHASH_IMPL`（:216 起）——以 `static kh_inline klib_unused` 链接性生成全部函数实现。

中间还保留了 `KHASH_DECLARE`（:371-373）= TYPE+PROTOTYPES（:205-215，纯 extern 原型）。核心库的用法是教科书式的三行：头文件域外声明 `KHASH_TYPE(kh_ib_ah, struct ibv_ah_attr, struct ibv_ah*)`（gpu_direct_rdma_access.c:76），本文件中部 `KHASH_IMPL(...)` 一次性生成实现（:192-193），键的 hash/equal 自定义（:178-190）。哈希核心仍是 klib 原味的开放定址+二次探测+0.77 装载上限（khash.h:195 `__ac_HASH_UPPER`），配套 kh_init/put/get/del 等宏糖（:459-508 区域）。注意 `kh_init_inplace`（:466）——AH 缓存嵌在 rdma_device 结构体内（嵌入式哈希，:128），用 inplace 变体初始化而无需独立堆对象（:658、:834）。

**ibv_helper.h 三层漏斗**。最底 `ibv_read_sysfs_file`（:44-80）：asprintf 拼路径→open O_RDONLY|O_CLOEXEC（:54）→read 并处理结尾换行/截断（:60-77）。中层 `ibv_query_gid_type`（:88-145）：拼出 `ports/N/gid_attrs/types/K` 路径（:94-95）读内容，字符串匹配 `"IB/RoCE v1"`/`"RoCE v2"`（:86-87、:134-141）；**三条历史退化路径**是精华——内核对 IB 口不存在该文件时返回 EINVAL，按 v1 处理（:106-112）；gid_attrs 目录整个不存在说明老内核，也按 v1（:119-127）；内容不认识则 ENOTSUP 报错（:138-140）。顶层 `ibv_find_sgid_type`（:147-176）：do-while 扫 GID 表（:155-173），逐项 query_gid+query_gid_type，GID 前两字节全零即判 IPv4 族（:164-166），**类型与地址族双匹配即返回索引**（:168-169）。注意循环条件 `while (gid_type != sgid_type || gid_family != sgid_family)`（:173）配合 do-while 的写法：扫到表尾还没命中时循环变量已失效，靠 :156-163 的 errno/EFAULT 路径兜底——找不到时返回值语义偏弱，调用方只判 `<0`（gpu_direct_rdma_access.c:355）。

## 三、外部连接

两个头都**只被 gpu_direct_rdma_access.c 一个 .c 包含**（:54-55）——这恰好消化了两个文件各自的链接怪癖：ibv_helper.h 的三个函数全是头内 static（:44、:88、:147 无 static 关键字但因为是"函数定义在头里"直接被单 TU 吸收，无符号冲突）；khash.h 的 KHASH_IMPL 生成的 static 函数也只此一份。如果第二个 .c include ibv_helper.h，会得到一份冗余拷贝（编译器或告警 unused）——地基是"单租户"设计。上游连接：khash.h 自带 kcalloc/krealloc/kfree/kmemset 适配层（khash.h:180-192，默认映射标准库）；ibv_helper.h 依赖 verbs 的 context→device→ibdev_path 字段链（:101）定位 sysfs 根。下游消费者：AH 缓存（第 5 篇）与 GID 定位（第 4 篇 :350-353）。

## 四、数据流

**AH 缓存线**：submit 组好 ah_attr（gpu_direct_rdma_access.c:1399-1411）→`rdma_create_ah_cached` 调 kh_get（:1272）→键先过自定义 hash：`kh_int64_hash_func(subnet_prefix ^ interface_id ^ dlid)`（:179-184，XOR 后再过 klib 的 64 位混合 :405）→桶位探测命中则以 memcmp 全结构判等（:187-190）→未命中走 create+put（:1286）写回。生命周期随设备：open 时 kh_init_inplace（:658、:834），close 时先 kh_foreach_value 逐个 ibv_destroy_ah（:1135）再 kh_destroy_inplace（:1145）；错误恢复（rdma_reset_device）会遍历缓存取一个现存 AH 当 flush 标记载体（:1033-1037）——缓存内容在 reset 后**不重建**，复用旧 AH。

**GID 线**：open 设备→query_port 确认 Ethernet 链路（:345、:350）→ibv_find_sgid_type(context, port, ROCE_V2, src_addr 族)（:351-352）→返回 gidx→ibv_query_gid 填 gid（:363）→is_global 置位（:374）→gidx+gid 之后流入 QP 路由属性（:398-402）与每笔 WR 的 sgid_index（:1409）。

## 五、设计决策

- **为什么改 klib 而不是直接用 KHASH_INIT**：原版宏在头里生成 static 实现，包含即复制；本仓拆成 TYPE/IMPL 两段后，类型可进头文件共享、实现只此一份——这是把"头文件库"驯化为"工程库"的最小手术。代价是与上游宏体系不再兼容（混用 KHASH_INIT 与本仓 KHASH_IMPL 同名会撞符号）。
- **键=结构体整体**而非抽取字段：memcmp 判等（:189）保证 ah_attr 任何字段（含 traffic_class、hop_limit）变化都会得到新 AH——语义绝对正确，代价是 hash 函数必须覆盖所有语义字段，当前 XOR 只混了三个主要字段（:181-183），理论上存在碰撞簇但仍正确（equal 兜底）。
- **ibv_helper 抄自 libibverbs 而非链接它**：这套 sysfs 探测在当年 verbs 版本里没有导出符号，样例选择"抄进头文件"换取零版本依赖；注释明言 sysfs 字符串属 ABI 兼容契约（:83-85）。
- **RoCE v2 硬编码**：调用点点名 IBV_GID_TYPE_ROCE_V2（:352）——2019 年的判断，RoCE v1 已是历史；若环境只有 v1 GID，gidx 探测失败直接报错（:355-358），不做退化。
- **探测双条件（类型+地址族）**（:168）：RoCE v2 的 GID 表里 IPv4 映射地址与 IPv6 本地地址并存，只按类型匹配会拿错族导致路由失败——:164-166 的前缀判族是关键细节。

## 六、新人提示

1. **别把本仓 khash.h 当 klib 原版引用**：拿上游新版覆盖会编译失败（KHASH_TYPE 宏不存在于上游）；反过来把本仓文件拷去别的项目，记得它与 KHASH_INIT 的不兼容性（:379-386 两套并存是刻意保留的兼容层）。
2. **`kh_inline`/`klib_unused` 是编译器适配宏**（:146-160）：C89 用 __inline、C99 用 inline，unused 属性压"静态函数未用"告警——读 khash.h 时先跳过这些预处理器噪声直奔 :197 起的三个 `__KHASH_*`。
3. **调试 GID 问题的一手工具**：`cat /sys/class/infiniband/mlx5_X/port/1/gid_attrs/types/*` 直接看每项类型——与 ibv_query_gid_type 读的是同一文件（:94-95）；再对照 `ibv_query_gid` debug 打印（gpu_direct_rdma_access.c:368-372）可双确认选中的 gidx。
4. **ibv_find_sgid_type 的返回语义**：找得到返回有效 idx，找不到时行为依赖循环终止细节（:173），调用方只信 `<0` 判错（:355）——别依赖它的正值边界行为。
5. **嵌入式哈希的内存归属**：AH 缓存的桶数组（keys/vals/flags）在首次 kh_put 时才堆分配（:216 实现内 resize），kh_destroy_inplace 只 free 三个内部数组不动宿主结构（:231-237）——所以 rdma_device 被 free 前必须先 destroy 缓存（:1144-1149 的顺序）。
