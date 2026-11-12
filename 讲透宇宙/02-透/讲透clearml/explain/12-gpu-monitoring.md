# 12 · GPU 监控线：三驱动查询 + ResourceMonitor 消费

## ① 角色定位

GPU 监控是三层单向管线：**底层 vendor 绑定**（pynvml.py 4966 行 NVIDIA NVML ctypes 绑定；pyrsmi.py 608 行 AMD ROCm SMI 绑定）→ **统一门面**（gpustat.py:26-27 `from ..gpu import pynvml as N / pyrsmi as R`，运行时探测走哪条驱动）→ **消费层**（resource_monitor.py 的 ResourceMonitor，2Hz 采样、30s 上报 `:monitor:gpu`/`:monitor:machine` 标量曲线）。触发点在 Task.init：task.py:823-830 在 `auto_resource_monitoring` 为真且配置 `development.worker.resource_monitoring`（默认 True）时实例化 ResourceMonitor（task.py:829），随 `BackgroundMonitor.start_all`（task.py:913；基类 utilities/process/mp.py:515）后台运行；第二消费端是 serving 遥测（endpoint_telemetry.py:84）。三文件同在 `clearml/utilities/gpu/`，`__init__.py` 为空。

## ② 内部结构

**gpustat.py（统一门面）**
- `gpustat.py:33` GPUStat：单卡 entry 字典包装，property 覆盖 index/uuid/mig_uuid/memory_*/utilization/power_draw/processes，字段名沿用 nvidia-smi 风格。
- `gpustat.py:176` GPUStatCollection：类级缓存 `_device_info`（name/uuid 只查一次）与 `global_processes`（psutil.Process 缓存，:198-201 清死 pid）。
- `gpustat.py:601-621` **new_query 总分派**：`_running_in_amd_env()`（gpustat.py:375-378）就是调 `R._find_lib_rocm()`——pyrsmi.py:282-288 检查 `ROCM_PATH`（默认 /opt/rocm）下 `librocm_smi64.so`（pyrsmi.py:101）是否存在，存在走 AMD，否则走 NVIDIA。模块级入口 gpustat.py:659。
- **NVIDIA 路径**（gpustat.py:381-599）：`gpustat.py:390` N.nvmlInit() 一次初始化；`gpustat.py:399` get_gpu_info 每项指标独立 try/except NVMLError 置 None（:443 温度/:453 显存/:458 利用率/:463 功耗）；`:428` `usedGpuMemory // MB`、`:512` `power // 1000` 毫瓦转瓦；`:526-529` DeviceGetCount + GetHandleByIndex；**`:534` MIG 支持**——逐分区展开成独立 GPUStat（:543-556），温度/风扇继承父卡；`:566-584` 驱动与 CUDA 版本解码；`:596-599` finally 按需 shutdown。
- **AMD 路径**（gpustat.py:204-350）：`gpustat.py:211` R.smi_initialize()；进程显存是**两段查询补丁**——`rsmi_compute_process_info_get` 不返回 VRAM 用量，须逐 pid 再调 by_pid_get 回填（:218-235）；`:276` 温度 TODO 恒 None 填 0、`:322` 利用率拿不到填 **100**；`:353-373` 驱动版本双兜底（rocm-smi --json → 子进程防 SEGFAULT）。

**pyrsmi.py（AMD 绑定）**：`pyrsmi.py:302-318` smi_initialize（加载 so + `rsmi_init(0)` + 引用计数）；`pyrsmi.py:321-336` rsmi_ret_ok（rsmi_status_string 查可读错误）；`pyrsmi.py:361-365` smi_get_device_count → `rsmi_num_monitor_devices`；`pyrsmi.py:190-195` rsmi_process_info_t 结构。版权头 AMD MIT 2023（pyrsmi.py:1-21）。

**pynvml.py（NVIDIA 绑定）**：`pynvml.py:38` 自述 "Python bindings for the NVML library"；`pynvml.py:1890` nvmlInit → nvmlInitWithFlags（pynvml.py:1872）；`pynvml.py:1895` _LoadNvmlLibrary 平台分支（Windows System32/nvml.dll；Linux `CDLL("libnvidia-ml.so.1")` pynvml.py:1921）；`pynvml.py:1931` nvmlShutdown；`pynvml.py:2108` DeviceGetCount。

**resource_monitor.py（消费层）**：`resource_monitor.py:23` `ResourceMonitor(BackgroundMonitor)`，采样 2Hz/上报 30s（resource_monitor.py:35-36）；`resource_monitor.py:91-94` default_gpu_utilization 读配置（null 可关闭兜底）；`resource_monitor.py:108-121` 解析 NVIDIA_VISIBLE_DEVICES/CUDA_VISIBLE_DEVICES 得活跃卡；`:125` daemon 主循环——`:211` event.wait 可中断、`:222-229` 检测不到迭代上报则"秒数当迭代"、`:267-306` 平均后 report_scalar（:274 按 `gpu_` 前缀路由标题）；`:335-353` _fix_active_gpus（全被 skip 则放开限制）；`:355-421` _machine_stats（psutil 全家桶 + GPU 附加，**:411-419 连败 3 次永久关闭 GPU 监控**）；`:509-591` _get_gpu_stats——**:528** 进程级显存每上报周期只查一次（慢），**:543** 用 psutil pid 名单对账本任务进程树，产出 `gpu_%d_*` 六族指标；**:565-577** 利用率为 None 时推 default_gpu_utilization 固定值且只警告一次；`:609` `new_query(shutdown=True, get_driver_info=True)` 一次性写机器规格。

## ③ 外部连接（图谱边证据）

图谱边钉死三层：`gpustat.py --imports--> pynvml.py & pyrsmi.py`；`resource_monitor.py --imports--> gpustat.py`（源码 resource_monitor.py:17-20 以 try/except ImportError 包裹，呼应可选性）；反向消费边 `task.py / binding/matplotlib_bind.py / router/endpoint_telemetry.py --imports--> resource_monitor.py`——matplotlib_bind.py:787 借 `get_logger_reported_titles` 判断用户是否已上报，endpoint_telemetry.py:161 直接调 `_machine_stats()` 喂 serving。

## ④ 数据流

采样环（每 0.5s）：daemon → _machine_stats → _get_gpu_stats → gpustat.new_query → NVML/RSMI ctypes 调用 → 指标累加。上报环（每 30s）：平均 → title/series 路由 → logger.report_scalar → UI 曲线。慢路径：每周期一次 per_process_stats=True + psutil 进程树对账 → 本任务进程独占显存而非全卡。多节点模式（CLEARML_MULTI_NODE_SINGLE_TASK，config/defs.py:38）按 rank 改写 title/series（resource_monitor.py:276-296）实现同 Task 多机聚合。

## ⑤ 设计决策

1. **探测即文件存在性**：AMD 判定只看 so 在不在，无 ROCm 静默走 NVIDIA，装机零配置。
2. **熔断优于崩溃**：连败 3 次永久关闭监控（resource_monitor.py:411-419），训练永远优先。
3. **慢查询分级限频**：进程级显存 30s 一次、机器规格与 name/uuid 各一次。
4. **占位值透明化**：AMD 温度填 0、利用率缺失填 100 并警告——曲线不断线但需知假值。
5. **vendored 绑定**：pynvml/pyrsmi 整文件入仓，装 SDK 即可监控、无 pip 依赖。
6. **一份监视器两处消费**：实验监控与 serving 遥测共享（endpoint_telemetry.py:84）。

## ⑥ 新人提示（含勘误）

- **勘误 1**：三文件不是"三选一驱动"——pynvml/pyrsmi 是 vendor 绑定，gpustat 是唯一统一入口，ResourceMonitor 只 import gpustat（resource_monitor.py:17-20）从不直连绑定。
- **勘误 2**：gpustat.py 头注释 "copied from gpu-stat 0.6.0"（gpustat.py:9）严重低估改动——AMD 分支（gpustat.py:204）、MIG 展开（gpustat.py:543-556）均为 ClearML 后加，与上游已是两个物种。
- **勘误 3**：pyrsmi 非 AMD 官方仓直拷——pyrsmi.py:96 的 `distributed.diagnostics.rocml` docstring 残留暴露其源自 PyTorch ROCm 诊断绑定。
- **勘误 4**：AMD 卡监控图上"利用率 100%"可能是占位值（gpustat.py:322）、温度 0 同理（gpustat.py:276）——读图先看日志有无 "cannot export utilization" 警告。
- MIG 下 NVML 导不出利用率是驱动限制，固定值来自 default_gpu_utilization（resource_monitor.py:567-571 专门提示 "Running inside MIG"）。
- pynvml 进程亲和坑（resource_monitor.py:117-119）：nvmlInit 必须发生在查询进程内，故 active gpu 修正挪进 daemon。
- 排查"没有 GPU 曲线"：先查 NVML/psutil，再看日志 "GPU monitoring is not available"（resource_monitor.py:103-104）——导入失败不报错，任务照跑。
