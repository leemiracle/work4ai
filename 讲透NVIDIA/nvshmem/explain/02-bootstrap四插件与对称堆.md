# 02 bootstrap 四插件与对称堆——婚介所与 PGAS 地基

## 角色定位

bootstrap（图谱 L03，40 节点）解决并行作业的第一命题：进程们如何发现彼此并交换建网所需信息。它是"婚介所"——init 时握手、交换 rank/size 与端点信息，通信建立后即退场。对称堆（L04 的一半）是 PGAS 的地基：所有 PE 以相同布局映射堆，`nvshmem_malloc` 返回的地址在所有 PE 上对称，远端寻址因此无需翻译。两者合起来构成 NVSHMEM 的"建堆-建网"阶段。

## 内部结构

bootstrap 宿主侧三件套：`src/host/bootstrap/bootstrap.cpp`（265 行）定义接口，bootstrap_preinit 在 bootstrap.cpp:118、bootstrap_init 在 bootstrap.cpp:145；`bootstrap_loader.cpp`（118 行）按 NVSHMEM_BOOTSTRAP 环境变量 dlopen 插件，GET_SYMBOL 取 `nvshmemi_bootstrap_plugin_pre_init`（bootstrap_loader.cpp:82）与 `nvshmemi_bootstrap_plugin_init`（bootstrap_loader.cpp:100）两个符号——ABI 面就这两个，钉死在 `nvshmem_bootstrap.sym`。插件目录 `src/modules/bootstrap/`：**mpi/pmi/pmix/shmem 四主族 + uid socket 直连族 + common 共用工具**（5+1 目录，"四插件"是惯称）。pmi 族内嵌 vendored MPICH pmi-2：pmi2_api.c 2187 行中 PMI2_Init 起于 pmi2_api.c:183（长 171 行，fd 握手+spawned/size/rank 协商），PMI2_Initialized 在 pmi2_api.c:389，最长函数 PMIi_ReadCommand 起于 pmi2_api.c:1447（187 行），create_keyval 起于 pmi2_api.c:1411 仅 33 行。uid 族的 `ncclSocket/` 是 NCCL 拷贝改造（ncclsocket_* 前缀保留），`bootstrap_uid_remap.h` 把 nccl 符号重映射进本地命名空间防污染。对称堆侧：`dlmalloc.cpp` 6419 行（Doug Lea 2.8.6，出处注释 dlmalloc.cpp:6-11）+`custom_malloc.cpp`（296 行，适配跨 PE 对称约束）；`mem_heap.cpp` 管布局（堆大小默认值登记于 env_defs_internal.h:37 的 SYMMETRIC_SIZE_DEFAULT）、`heap_registration.cpp` 做传输注册（ibv_reg_mr）、`handle_table.cpp` 维护堆句柄、`nvls_observer.cpp` 监听堆变化驱动 NVLS 多播对象。

## 外部连接

上游消费者是 init.cu（bootstrap_init 返回的 handle 供传输层交换端点）；下游对接传输插件——bootstrap 交换的正是各传输所需的 memory key/QP 信息。symmetric_heap.hpp 是静态/动态堆的 C++ 契约。测试树有独立 PMI 实现（test/common/test-simple-pmi），单元测试用链接期符号替换法无 GPU 跑堆逻辑（test/unit/mem/heap/dynamic_unit_tests.cpp）。

## 数据流

以 MPI 启动为例：mpirun 拉起各 PE → NVSHMEM_BOOTSTRAP=MPI（README.md:42）选中 mpi 插件（bootstrap_loader.cpp:82 的 pre_init 符号先就位）→ pre_init 建 communicator → init 交换 rank/size → NVSHMEM 传输插件借 bootstrap 的 allgather 互换 ibv memory key 与队列信息 → bootstrap finalize 退场（bootstrap_loader.cpp:37 的 bootstrap_loader_finalize 与 :25 的 _bootstrap_loader_fini_helper 负责 dlclose）。对称堆分配流：nvshmem_malloc → custom_malloc 在 dlmalloc 之上加对称约束（各 PE 相同 size 同步分配）→ heap_registration 把段注册进每个传输 → mem_transport 抽象成堆-传输视图 → 设备侧经 handle_table 查远端地址直接寻址。

## 设计决策

插件化 bootstrap 让 NVSHMEM 不绑定作业系统（MPI/Slurm-PMI2/PMIx/无作业系统四场景全覆盖，README.md:42-57 给了三套启动命令）；vendored pmi-2 省去外部依赖但要维护两代 PMI 源码；ncclSocket 改造保留前缀是"抄得诚实"的示范——重映射头隔离符号，避免与用户程序链接的 NCCL 冲突。选 dlmalloc 而非写新分配器：对称堆需要精确控制段布局，Lea 分配器公有领域、单文件、可改，是低风险起点。

## 新人提示

排查启动失败先设 NVSHMEM_DEBUG=INFO 看 bootstrap 阶段日志；改 bootstrap 接口必须同步 nvshmem_bootstrap.sym 与 bootstrap_loader.cpp:82/:100 的两个 GET_SYMBOL 名；读 pmi2_api.c 从 PMI2_Init（:183）进，别被 2187 行吓退——真正常用路径只占 1/3。对称堆调试注意：各 PE 堆布局不一致是灾难级 bug，nvls_observer 的回调时序是 NVLS 场景的常见踩点。
