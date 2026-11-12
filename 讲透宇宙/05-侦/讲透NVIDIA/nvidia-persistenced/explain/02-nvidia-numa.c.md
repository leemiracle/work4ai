# 讲透 nvidia-numa.c（NUMA 内存上下线子系统，897 行）

## 角色定位
把"GPU 显存映射出的 host NUMA 节点"经 Linux memory-hotplug sysfs 接口上线/下线的独立子系统。对上只暴露两个入口 `nvNumaOnlineMemory`（:688）/`nvNumaOfflineMemory`（:866），对下同时打两类接口：/dev/nvidiaN 的私有 ioctl（状态真值在驱动 RM）与 /sys/devices/system/memory/* 的公共 sysfs（实际动作）。

## 内部结构
四层漏斗：① 设备定位（`get_gpu_minor_number` :96 解析 /proc/driver/nvidia/gpus/%04x:%02x:%02x.%x/information 的 "Device Minor:" 行 → `get_gpu_device_file_fd` :152 open /dev/nvidia%d）；② ioctl 层（`get_gpu_numa_info` :174 读 NV_ESC_NUMA_INFO；`set_gpu_numa_status` :196 写 NV_ESC_SET_NUMA_STATUS）；③ 块操作（`change_memblock_state` :283 读写 memoryN/state；`change_numa_node_state` :340 按 base/size 换算块号区间循环）；④ 辅助（`probe_node_memory` :443、`offline_blacklisted_pages` :413、`check_memory_auto_online` :594）。

## 外部连接
ioctl 号来自 nv-ioctl-numa.h（NUMA_INFO=BASE+15 :44、SET_NUMA_STATUS=+16 :45、七态 0-6 :73-79）；nvidia-persistenced.c 的 set_device_numa_status（:427）是唯一调用方；字符串/日志工具借 common-utils（nvasprintf/nvfree）。

## 数据流
上线：ioctl 取 numa_info（nid/numa_mem_addr/numa_mem_size/memblock_size/黑名单 64 条上限，nv-ioctl-numa.h:47-65）→ use_auto_online 直通（:719）→ 置 ONLINE_IN_PROGRESS（:760）→ 对齐断言（:770）→ 逐块写 probe（:477）→ 查 auto-online 是否被 udev 抢跑且 zone=Movable（:638-663，非 Movable 报 -ENOTSUP :658）→ 逐块写 state="online_movable"（命令字 :50，**倒序**循环 :364-373）→ 黑名单地址写 hard_offline_page 退役（:428）→ 置 ONLINE（:836）。失败路径先 `offline_memory(fd)` 全量回滚（:852）再置 ONLINE_FAILED（:854）。

## 设计决策
① 上线目标 zone 是 Movable 而非默认 zone：命令字直接写 "online_movable"，且**倒序上线**（:357-374，注释引 patchwork.kernel.org/patch/9625081——正序会被内核放进 Normal）；② probe 文件缺失按正常处理（:460-466），因部分平台驱动自管 probe；③ RM 状态机与 sysfs 动作分离：ioctl 状态是权威，sysfs 是执行器，中途态（*_IN_PROGRESS/FAILED）让崩溃后的重试有据可依；④ 下线失败故意不 close fd（:888 注释：避免顺手关掉设备）。

## 新人提示
调试先看两处：syslog 里 "NUMA:" 前缀（本文件全部日志）与 /sys/devices/system/memory/memoryN/state 实际值。常见坑：系统开了 CONFIG_MEMORY_HOTPLUG_DEFAULT_ONLINE 或 udev 有 auto-online 规则时内存会被抢先上线到 Normal zone，此时 persistenced 报 -ENOTSUP 并打印 :585-591 的警告宏——这不是 persistenced 的 bug，改系统配置。
