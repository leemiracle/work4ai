# B-01 `bloomberg/memray`（15.2K★）
> 克隆：C:\Users\mirac\AppData\Local\Temp\opencode\memory-clones\bloomberg__memray（develop HEAD）
> 语言栈：Python + Cython + C++（核心 `_memray` C++ 扩展）｜ Apache-2.0
> 一句话定位：**分配级溯源**的 Python 内存 profiler——把每一次 malloc/free 钉在"Python 栈 × native 栈"混合调用栈上，离线聚合成高水位/泄漏/生命周期视图

## 1. 架构总览（目录地图）

```
bloomberg__memray/src/memray/
├── _memray.pyx                 # Tracker/FileReader/SocketReader Python 绑定（2053 行）
├── _memray/
│   ├── hooks.cpp               # malloc/calloc/realloc/free/mmap/pymalloc 全家桶拦截（15.3KB）
│   ├── tracking_api.cpp        # Tracker 单例：栈捕获 + 记录写入（50KB）
│   ├── elf_shenanigans.cpp     # Linux GOT/PLT 符号改写（8.1KB）
│   ├── macho_shenanigans.cpp   # macOS dyld 惰性绑定改写（18.5KB）
│   ├── native_resolver.cpp     # IP→符号 延迟解析（15KB）
│   ├── record_writer.cpp       # 记录流序列化（29.6KB）
│   ├── record_reader.cpp       # 读取端（52KB，双格式分派）
│   ├── snapshot.h/.cpp         # 五种聚合器（高水位/临时/生命周期/统计）
│   ├── frame_tree.h            # native 栈前缀树驻留
│   ├── lz4_stream.h            # 流式 LZ4 压缩
│   └── sink.cpp                # File/Socket/Null 三种落地
├── commands/                   # run/attach/flamegraph/tree/table/summary/stats/transform/live/parse
├── reporters/                  # 离线报告渲染（flamegraph.py 412 行、tree.py、tui.py 27.7KB）
└── _ipython/                   # Jupyter magic（%memray_flamegraph）
```

数据流一条线：

```
hooks 拦截分配
  → tracking_api 捕获双栈（Python profile 栈 + libunwind native 栈）
  → record_writer 以 LZ4 记录流落地（文件 或 socket）
  → [离线] FileReader 逐记录重放
  → snapshot 聚合器（高水位/临时/生命周期/统计）
  → reporters 渲染（HTML 火焰图 / TUI / 表格 / speedscope）
```

关键设计：**采集与聚合完全分离**——运行时只做最低成本的顺序追加，所有理解（聚合、归因、视图）推迟到离线端；同一份 capture 文件可反复出多种视图。

## 2. 核心机制深读

### 2.1 分配拦截（写入溯源的物理层）
- 事件枚举覆盖 15 种分配器（`src/memray/_memray.pyx:116-131`）：
  - pymalloc 域：`PYMALLOC_MALLOC/FREE/CALLOC/REALLOC`；
  - C 堆：`MALLOC/FREE/REALLOC/CALLOC`；
  - 对齐分配：`POSIX_MEMALIGN/ALIGNED_ALLOC/MEMALIGN/VALLOC/PVALLOC`；
  - 匿名映射：`MMAP/MUNMAP`。
  ——不仅 C 堆，连 pymalloc 域和 mmap 区间都覆盖，因此能同时回答"Python 对象层面"与"底层页层面"两个视角。
- 钩子安装方式（平台分歧的根源）：
  - Linux：`SymbolPatcher`（`_memray/linker_shenanigans.h:13`）遍历 PHDR 改写 GOT/PLT（`elf_shenanigans.cpp`，含 8.1KB 的 ELF 解析）；
  - macOS：改写 Mach-O 惰性绑定表（`macho_shenanigans.cpp`，18.5KB，最大单文件，dyld 交互复杂度可见一斑）。
- 每个被拦截的分配函数直接调 `tracking_api::Tracker::trackAllocation(ptr, size, Allocator::MALLOC)`（`_memray/hooks.cpp:190-526`，16 处调用点一一对应）。
- 运行中动态加载新库（README 举例 libarrow）会触发 `invalidate_module_cache_impl()` 重打补丁并刷新模块缓存（`_memray/tracking_api.cpp:1238-1244`）——**热插拔场景的符号一致性**有显式处理。

### 2.2 双栈捕获（hybrid stack trace）
- Python 栈：`sys.setprofile` 装 C 级 profile 函数（`install_trace_function`，`tracking_api.cpp:1626`；Python 侧入口 `_memray.pyx:870-872`），帧进出记录为 FramePush/FramePop（`_memray/records.pxd:48-51`）。
  - **懒提交**：profile 回调只积累 pending push/pop，分配事件真正到来时才 `emitPendingPushesAndPops()` 落盘（`tracking_api.cpp:1158`）——无分配的纯计算栈零成本。
- native 栈：libunwind 就地展开成 IP 序列，经 `frame_tree` 前缀树**驻留去重**（`_memray/frame_tree.h:7`），写出 `UnresolvedNativeFrame{ip, index}`（`tracking_api.cpp:1160-1169`）。
  - **符号化延迟到读取端**：写入时只存 IP + generation，`native_resolver.cpp` 在离线阶段查符号表解析——"先记便宜的，贵的后付"。
- 记录粒度：每条 `AllocationRecord{ptr, size, allocator}` 按线程写入（`writeThreadSpecificRecord`，`tracking_api.cpp:1171-1177`）。
- 双通道水位：每 10ms 一条 `MemoryRecord`（RSS/VMS，`_memray.pyx:740-747`）——"总量曲线"与"分配事件流"是**两条平行记录**，火焰图顶部的时间曲线即由它渲染。

### 2.3 两种文件格式：写时聚合 vs 读时聚合
- `FileFormat.ALL_ALLOCATIONS`（原始全量流）vs `AGGREGATED_ALLOCATIONS`（捕获时即聚合）（`_memray.pyx:147-150`）。
- CLI 开关 `--aggregate`（`src/memray/commands/run.py:51-52`），格式切换在 `record_writer.cpp:579`，读取端按 header 分派（`record_reader.cpp:635-639`，聚合档只出 `AGGREGATED_ALLOCATION/AGGREGATED_TRAILER` 两类记录，`records.h:63-76`）。
- 权衡：聚合档体积小一个量级但丢失时间细节——**流水账与摘要的显式分层**，由用户按场景选择。

### 2.4 聚合器族（`_memray/snapshot.h`，本仓最精华的 550 行）
- `SnapshotAllocationAggregator`（snapshot.h:191-201）：
  - 活跃分配 `ptr→allocation` 哈希表 + **mmap 区间用 IntervalTree**——范围型分配（mmap 可部分 unmap）无法用点键，必须区间树。
- `TemporaryAllocationsAggregator`（snapshot.h:203-215）：
  - 每线程一个 deque，只保留最短命的 N 个分配——专抓"分配了立刻丢"的抖动。
- `HighWatermarkFinder`（snapshot.h:236-255）：
  - 在线峰值跟踪，`updatePeak` 在下降沿确认峰值——O(1) 空间的"高水位"定义器。
- `HighWaterMarkAggregator`（snapshot.h:370-414）：
  - 位置键 = `thread + python_frame + native_frame + generation + allocator`（`HighWaterMarkLocationKey`，snapshot.h:261-273）；
  - 每位置维护 `UsageHistory`：统计**该位置对历史每一次峰值的贡献度**（`Contribution/HistoricalContribution`，snapshot.h:289-359；源码注释 324-332 详述"发现新峰后把增量 rebase 进新峰"的无符号溢出安全算法）；
  - 同时记录每快照的 `d_high_water_mark_bytes_by_snapshot`（snapshot.h:390-392）。
- `AllocationLifetimeAggregator`（snapshot.h:416-463）：
  - 产出 `{allocatedBeforeSnapshot, deallocatedBeforeSnapshot, key, n_bytes}` 生命周期区间（SIZE_MAX=从未释放，snapshot.h:361-368）；
  - 支撑 **temporal flamegraph**：时间轴上的分配生灭动画。
- 对象级跟踪 `track_object_lifetimes`（需 Python≥3.13.3，`_memray.pyx:796-800`）：
  - `OBJECT_CREATED/DESTROYED` 事件（`trackObjectImpl`，tracking_api.cpp:1196-1235）；
  - 泄漏定义 = 会话结束时仍在 `d_tracked_objects` 集合里。

### 2.5 报告与交互层
- 火焰图（`reporters/flamegraph.py`）：
  - 每条记录沿栈逐帧累加 value/n_allocations（`generate_frames`，flamegraph.py:141-208）；
  - 节点键三元组去重 + `StringRegistry` 字符串驻留（flamegraph.py:96-105）；
  - 三棵树并行：正常 / 倒置 / **去 import 系统帧**的倒置树（`_drop_import_system_frames`，flamegraph.py:224-235）——"噪声帧剪枝"是一等公民；
  - 栈深保护 `MAX_STACKS = recursionlimit/2.5`，超限折叠 `<STACK TOO DEEP>`（flamegraph.py:37,193-196）。
- 其他视图：tree（展开式树）、table、summary（按位置聚合 TopN）、stats（allocator 维度统计）、tui（textual 实时 TUI，27.7KB）。
- `transform` 报告器：导出 **speedscope** 格式与 **gprof2dot**（`reporters/transform.py:30-52`，注释 :102 说明 memray 叶→根序需反转为 speedscope 根→叶序）——生态互认的实用主义。
- 附加模式：gdb/lldb 注入已运行进程（`commands/attach.py` + `_attach.gdb/_attach.lldb` 脚本）；`memray run --live` 经 socket 实时流（`BackgroundSocketReader`，`_memray.pyx:60`；子进程侧 `_run_child_process_and_attach`，commands/run.py:113-110 附近）。
- Jupyter 集成：`_ipython/flamegraph.py` 的 `%memray_flamegraph` magic（flamegraph.py:140）。

### 2.6 工程细节（都值得抄）
- fork 安全：pthread fork handler 在子进程**先禁用** tracking，Python `at_fork` 再重建（`_memray.pyx:94-100`，注释解释了两个时机缺一不可）。
- 写失败自动 `deactivate()` 并打日志，绝不拖垮宿主进程（`tracking_api.cpp:1172-1174`）。
- `/dev/null` 特判为 NullSink，供基准测试消除 IO 噪声（`_memray.pyx:767-773`）。
- 全局唯一 Tracker：二次激活显式报错（`_memray.pyx:845-847`），线程名拦截器补齐多线程归因（`_thread_name_interceptor.py`）。

## 3. 与 Agent 记忆的可迁移机制（本仓必须回答）

1. **分配溯源 ≈ 记忆写入溯源**。
   - memray 的全部诊断力来自"每字节都能回答谁在何栈分配"；
   - Agent 记忆普遍只存 payload 不存**写入栈**（哪次对话/哪个任务/哪个工具链写的）；
   - 若写入时记录来源栈，记忆审计（"这批膨胀的记忆从哪来"）才能像 `UsageHistory` 一样归因到位置（mem0 的 `run_id/actor_id` 是雏形，缺栈与账本）。
2. **高水位思维**：诊断对象不是"总量"而是"峰值时刻谁在占用"——上下文峰值时刻的归因分析（哪些来源在峰值贡献最多 token）比日均统计更有诊断力。
3. **ALL vs AGGREGATED 双格式**：完整对话日志（重放用）与抽取后记忆条目（检索用）显式分层；摘要必须可从原始流重建。
4. **生命周期区间 `[allocated, deallocated)`**：记忆条目不该只有 `created_at`，应有闭合生灭区间；temporal flamegraph 是"记忆随时间生灭"的直接可视化原型。
5. **延迟符号化**：写入时只存引用/指针（doc id、对话 id，便宜），检索命中后再做昂贵展开与解释——代价后付。
6. **区间树 vs 哈希表分治**：范围型记忆（会话级、任务级区间）与点型记忆（单条事实）需要不同索引结构——memray 在同一聚合器里同时维护两者（snapshot.h:405-409）。
7. **噪声帧剪枝**：import 系统帧在 memray 里被一等公民式地剪掉——记忆来源栈也应过滤"框架内部帧"，只留用户可读的语义层。
8. **失败降级不 crash 宿主**：记忆子系统写入失败应自我停用并打日志，绝不阻断主流程。

## 4. 局限
- 平台限 Linux/macOS：符号机制完全基于 ELF/Mach-O，Windows 无原生支持。
- 只看分配事件流：内核侧（page cache/swap）与 GC 语义（循环引用的延迟释放）只能间接观察。
- native 符号化依赖构建产物带符号；剥离二进制只剩地址。
- 采集开销在 native 追踪下显著，生产环境通常只在采样窗口使用（attach 短时注入是推荐的折中）。
