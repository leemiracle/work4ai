# 讲透 NVMeFwUpdateHandler.cpp（固件更新执行器，694 行）

## 角色定位
固件更新新架构的执行侧：nvidia-nvme-manager 进程内监听 systemd JobNew，接管 nvme-update@.service 触发的刷盘任务。命令行工具 NVMeFwUpdate 已退位为进度监控瘦客户端（tool/NVMeFwUpdate.cpp:5-8），真正做 download/commit 的是本文件。

## 内部结构
常量组（:43-47）：fwUpdateChunkSize=4096、fwUpdateSlot=0、fwDownloadMaxRetries=5、fwCommitResetRestartMaxRetries=1、progressLogIntervalSec=20。三个层次：①信号入口 startNvmeFwUpdateMonitor（:683）→ onNvmeUpdateJobNew（:623）验前缀 nvme-update@ + .service（:641-642）并回查 JobType=="start"（:670-675）；②handleNvmeUpdateStartJob（:573）→ shouldSkipDuplicateJob 30s 去重（:552-571）→ parseNvmeUpdateRequest 解析 /run/nvidia-nvme-update/<id>.env（requestFilePath :209-211，unquoteEnvValue :163）→ 逐目标 resolveDriveTarget（:285，盘名/EID 互解）后 **detached std::thread** 跑 runFwUpdate（:617-619）；③runFwUpdate（:340）业务循环。

## 外部连接
经 extern getDriveMap（:39，定义在 NVMeDeviceMain.cpp:47）查盘；传输层走 NVMeMi 的 adminFwDownload/adminFwCommit（同步路径，NVMeMi.cpp:1419/:1316）；进度回写 NVMeDevice::setFwUpdateProgress（NVMeDevice.cpp:903，post 到主 io）；Redfish 事件七件套（logTargetDetermined :116 → logTransferringToComponent :77 → logTransferFailed :65 / logAwaitToActivate :95 / logUpdateSuccessful :86 / logActivateFailed :104 / logNoMatchingDevices :125）经 dbusutil 写 OpenBMC Logging。

## 数据流
单盘更新：读固件文件→按 4096B 分块 adminFwDownload（offset 递增，日志 20s 节流 shouldLogEverySeconds :139）→块失败重试至 5 次（:462-463）→盘被拔（weak_ptr 失效/设备移除）即中止（:490-491）→adminFwCommit 到 slot 0→commit 返回"reset 后镜像丢失"（isFwCommitImageLostAfterReset :324）则整个 download+commit 重来 1 次（:515-522）→成功 setProgress(100, Completed)（:543）并 logUpdateSuccessful；失败 setProgress(0, Failed)+logActivateFailed（:528-530）。commit 返回 NEEDS_RESET 类状态视为成功待激活（isFwCommitNeedsResetStatus :316，与 NVMeMi.cpp:1365-1377 的白名单一致）。

## 设计决策
①用 systemd JobNew 而非自定义 D-Bus 方法触发——更新请求天然有 systemd 单元生命周期/日志可查，.env 文件（/run 下 tmpfs）即请求载体；②detached 线程而非 worker 队列——固件下载分钟级长任务，不能占用全局唯一 NVMeMi worker（否则全机盘轮询饿死），端点互斥由 adminFwDownload 自持 endpointMux 保证；③30s 去重窗防 systemd 重复 JobNew 信号双倍刷写（:548-551 注释明说）；④"commit 后镜像丢失"自动整轮重试一次——NVMe 规范允许设备在 reset 边界丢未激活镜像，直接重下比报错体验好。

## 新人提示
调这条链看三处日志：journalctl 里 systemd 的 nvme-update@<id> 单元、manager 的 "FW update EID ... downloading chunk at offset"、瘦客户端 nvme-fw-update 的 Progress 输出。坑：.env 里 TARGETS 列表格式由 splitTargets（:197）解析，盘名与 EID 混用时靠 resolveDriveTarget 兜底；总超时 600s 是**客户端侧**的（fw_update_progress_timeout，meson_options.txt:66），manager 侧无对应熔断，慢盘要靠客户端先放弃。
