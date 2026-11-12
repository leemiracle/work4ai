# 01 精讲：主包 API 与 device 适配（gpuallocator/ 主包生产文件）

## 角色定位

主包 `gpuallocator` 是整个库的对外面孔，六个生产文件分三组：allocator.go（Allocator+Policy 两级抽象）、device.go/options.go（设备模型与发现链）、三个 *_policy.go（策略实现）。它回答的问题只有一个："这台节点上，给定可用 GPU 集合与数量请求，选哪几块？"README.md:7-10 把"只决策、不指派"写成了库的宪法——库里没有任何一行代码触碰容器或进程。

## 内部结构

**Allocator**（gpuallocator/allocator.go:14-20）= 全量 `GPUs` + `policy` + `remaining`/`allocated` 两个 DeviceSet 账本。`Allocate(num)`（allocator.go:85-95）委托策略选出设备后经 `AllocateSpecific` 落账；策略若返回不在 remaining 中的设备直接 panic（allocator.go:90-91）——这是内部一致性错误，不设计为可恢复。`Free`（allocator.go:119-133）用 UUID 反查 + **指针同一性**双重校验（allocator.go:125-128），伪造的同 UUID 设备被静默丢弃（allocator_test.go:38-50 专门验证）。

**构造链**：`NewAllocator(policy)`（allocator.go:47-68）→ nvml.Init（:48-51）→ `NewDevices(WithNvmlLib(...))` 枚举（:53-55）→ `runtime.SetFinalizer` 兜底 Shutdown（:62-65）。

**Device**（device.go:18-22）内嵌 nvlibDevice（device.go:24-34）组合 go-nvlib 的 device.Device 接口——组合非继承；三个缓存字段 UUID/PCI.BusID/CPUAffinity 被注释标 deprecated（device.go:26-28）但 Details() 仍在用。`build()`（device.go:92-137）做 O(n²) 双重遍历调 `links.GetP2PLink/GetNVLink` 填 Links 表（device.go:114-134）。

## 外部连接

依赖仅三个：go-nvml（NVML 绑定）、go-nvlib（设备抽象层 device.Interface）、testify（仅测试）。注入点设计是双层：函数式选项 `WithNvmlLib/WithDeviceLib`（options.go:34-45）面向正常调用方；包级变量 `nvmlNew`（device.go:256-258）面向测试——`NewDevicesFrom` 不走选项（device.go:144 硬编码无参 NewDevices()），mock 只能从 nvmlNew 进（device_test.go:84-93 的 setNVMLNewDuringTest 还原闭包手法）。

## 数据流

`NewDevices`（device.go:76-89）应用选项→缺省补 nvmlNew()/device.New()（:81-86）→ build()：Init→GetDevices 枚举（:100）→ 逐台 newDevice 抽 UUID/PCI（:37-59）→ O(n²) 填链路→ defer Shutdown（:96-98）。分配流：Allocate→policy.Allocate(remaining.SortedSlice(), nil, num)→AllocateSpecific 校验+账本双写（:112-113）→返回设备；Free 反向。NVML 引用计数靠 C 层平衡：NewAllocator 的 Init + build 内的 Init/defer Shutdown + finalizer 的 Shutdown 恰好配平。

## 设计决策

① **panic vs error 分层**：策略输出违约=panic（程序员错误），设备不可用=error（allocator.go:109 带明细）。② **Free 静默忽略而非报错**（allocator.go:126-127）——释放路径幂等优先。③ **DeviceSet 以 UUID 为键**（device.go:73）+ SortedSlice 按 Index 排序（device.go:241-253），分配结果确定可复现。④ **deprecated 字段不删**（device.go:26-28）——下游兼容优先。⑤ Filter 要求 UUID 必须命中否则整体失败（device.go:151-168），宁拒勿错。

## 新人提示

- README.md:55 的 Policy 签名过时（缺 required 参数），以 allocator.go:31 为准；README.md:46-48 的 AllocateSpecific 返回类型也错（实际 error）。
- Details() 无条件解引用 CPUAffinity（device.go:181），NUMA 缺失的机器会 panic——排查示例崩溃先看这里。
- SortedSlice 的注释 "etunrs returns"（device.go:239）是上游拼写 typo，别当成特殊术语。
