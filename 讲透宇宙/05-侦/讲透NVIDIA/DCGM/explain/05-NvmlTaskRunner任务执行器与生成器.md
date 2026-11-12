# 05 · NvmlTaskRunner：NVML 任务执行器与双生成器体系

## 角色定位

dcgmlib/src/NvmlTaskRunner 是全仓 NVML 调用的**唯一串行化通道**：把"任意线程直接调 NVML"改造成"投递任务到专用任务线程执行"。动机写在 DispatchTask 注释里——一系列 NVML 调用必须按序、以一致输入执行，不能让 GPU detach 插进任务中间（NvmlTaskRunner.hpp:304-307）。三层构成：手写层 NvmlTaskRunner.cpp（666 行）、生成层 NvmlTaskRunnerGenerated.cpp（**9171 行**，文件头明示 DO NOT EDIT，NvmlTaskRunnerGenerated.cpp:19-21）、生成器 NvmlTaskRunnerGenerator.py（**549 行**）。姊妹体系 nvml-injection 是测试侧 NVML 假实现：4784 行桩生成器 + 12866 行生成桩（307 个函数）。

## 内部结构

句柄安全是第一设计：NVML 裸句柄一律包成携带 generation 的值类型——SafeNvmlHandle{nvmlDevice, nvmlIndex, generation}（NvmlTaskRunner.hpp:30-56），SafeGpuInstance/SafeComputeInstance/SafeVgpuInstance/SafeVgpuTypeId 四兄弟覆盖 MIG 与 vGPU（NvmlTaskRunner.hpp:59-89）。generation 是驱动世代号：GPU detach/reattach 时递增（GetGeneration，NvmlTaskRunner.hpp:116-119），旧句柄在新世代自动失效。执行核 InvokeNvmlFunction 模板（NvmlTaskRunner.hpp:339-362）六步舞：shared_lock → 查 m_blockNewTasks → m_ongoingTasks 原子递增 → 解锁 → Defer 递减并唤醒等待者（NvmlTaskRunner.hpp:348-354）→ Enqueue 任务 future.get()。生成的每个包装复刻此骨架（NvmlDeviceGetTemperature，NvmlTaskRunnerGenerated.cpp:1611-1636），Impl 层再加 generation 比对（NvmlTaskRunnerGenerated.cpp:1637-1646：不匹配返回 NVML_ERROR_UNINITIALIZED）后 ::nvmlDeviceGetTemperature 全局直调。run() 覆写把 NVML 线程注册进挂起检测（AddMonitoredTask，NvmlTaskRunner.cpp:640-649），循环 TaskRunner::Run（NvmlTaskRunner.cpp:660-663）。成员四件套 m_blockNewTasks/m_generation=1/atomic m_ongoingTasks/m_sharedMutex+条件变量在 NvmlTaskRunner.hpp:490-496；WaitOngoingTasksToComplete 可能无限阻塞，注释明言靠 hang detection 兜底（NvmlTaskRunner.hpp:326-328）。

## 外部连接

上层消费者是 CacheManager 采集循环与 MIG/vGPU 管理：P2P 状态（NvmlTaskRunner.hpp:181）、拓扑祖先（NvmlTaskRunner.hpp:208）、事件等待 NvmlEventSetWait（NvmlTaskRunner.hpp:154/:167）、GPU/计算实例枚举（NvmlTaskRunner.hpp:225/:242）、vGPU 三查询（NvmlTaskRunner.hpp:259/:276/:291）。GPM 走旁路：DcgmGpmManager 自管 nvmlGpmSample_t 的 RAII（DcgmGpmSample，DcgmGpmManager.hpp:56-99）。生成器输入不是 nvml.h 全量，而是入口点表 sdk/nvidia/nvml/nvml_entry_points.h（NvmlTaskRunnerGenerator.py:24）；NvmlTaskRunnerGenerator.py:172-174 维护手工例外清单（nvmlDeviceGetActiveVgpus 因须返回 SafeVgpuInstance 而手写）。测试侧 nvml-injection 用环境变量切换：NVML_INJECTION_MODE 触发 dlopen libnvml_injection.so，NVML_YAML_FILE 指定回放数据，key 取函数名后缀打通 setter/getter。

## 数据流

**生成链**：在仓根运行生成器（IsInDcgmRoot 检查 NvmlTaskRunnerGenerator.py:497-499）→ main 读入口点表（NvmlTaskRunnerGenerator.py:526-527）→ 五个 Process*FunctionIfAny 按首参类型分桶 device/gpuInstance/computeInstance/vgpuInstance/vgpuType（NvmlTaskRunnerGenerator.py:182/:206/:227/:245/:270）→ WriteCppFile 生成实现（NvmlTaskRunnerGenerator.py:414-435）+ WriteHeaderFiles 生成 Public/Private 头（NvmlTaskRunnerGenerator.py:438-494）。Public 头被直接 include 进类体内（NvmlTaskRunner.hpp:316），9171 行生成代码物理上成为类方法；Private 头在 DCGM_NVML_TASK_RUNNER_TEST 下豁免 private（NvmlTaskRunner.hpp:318-321）。**运行链**：到期字段 → 生成包装 → Enqueue → NVML 线程执行 Impl → future 回传 nvmlReturn_t。**注入链**：桩生成器 generate_nvml_stubs.py（nvml-injection/scripts，4784 行，STUB_PATH 定义在其 :42）产出 nvml_generated_stubs.cpp——每函数先查 GLOBAL_PASS_THROUGH_MODE 决定透传真 NVML 还是走 InjectedNvml 的 map（nvml_generated_stubs.cpp:36-55 的 nvmlDeviceGetClockInfo 即模板）。

## 设计决策

1) **generation 号代替句柄失效通知**：detach 竞态无需锁协议，旧句柄自证过期，代价是每个 Impl 一次比较。2) **代码生成而非宏**：307 个包装手写必然漂移；签名解析、五类分桶、模板替换全收敛进生成器，NVML 升级只重跑脚本。3) **shared_mutex 而非互斥锁**入队：读多写少，BlockNewTasks 与投递并发但互不长期阻塞。4) **挂起检测内建**：NVML 调用是全系统最可能卡死的位置，注册点选在 run() 入口。5) 注入桩**同名替换 + pass-through 双模**，生产与回放语义共存一个 .so。6) 手写层只留无法模板化的编排（DispatchTask 22 行、GetSafeNvmlHandlesImpl 48 行）。

## 新人提示

改生成文件必先改生成器再重跑（命令见 NvmlTaskRunnerGenerator.py:502-518）。新增 NVML 包装若返回安全句柄类型，进 NvmlTaskRunnerGenerator.py:172-174 手工清单而不是改模板。排查 NVML_ERROR_UNINITIALIZED 先查两处：m_blockNewTasks（正在 detach）与 generation 不匹配（句柄过期），日志会区分（NvmlTaskRunnerGenerated.cpp:1641）。GPM 样本泄漏查 DcgmGpmSample 析构链。注意 NvmlTaskRunner.hpp:92-94 类注释警告：本类方法内部取 shared_lock，持其他锁调用可能死锁。
