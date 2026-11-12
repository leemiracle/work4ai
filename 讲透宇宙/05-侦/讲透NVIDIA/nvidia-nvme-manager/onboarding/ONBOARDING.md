# nvidia-nvme-manager 深度导览（ONBOARDING）

> 仓：/usr-data/data2/repos/agent-repos/NVIDIA/nvidia-nvme-manager @1016dfdb
> 图谱：148 节点 / 212 边 / 6 层 / 7 步导览，fingerprints 44 文件。C++23 + meson，OpenBMC 生态。

## 1. 这个项目是什么：BMC 侧的 NVMe 盘管理器

OpenBMC 上的 NVMe 设备管理守护：经 **MCTP 传输跑 NVMe-MI 协议**（libnvme-mi）发现/监控/管理 NVMe 盘，把结果发布成 OpenBMC D-Bus 对象（Inventory.Item.Drive、Nvme.Status、Sensor 等），供 Redfish/BMCWeb 消费。三个可执行：主守护装成 **/usr/bin/nvme**（src/meson.build:24，注意与 nvme-cli 同名）、`nvme-fw-update`（工具，tool/meson.build:1）、可选 `nvme-mux-manager`（meson feature `mux_manager`，默认 disabled，src/meson.build:36-46）。

构建期注入的平台常量在 include/nvme-mi_config.h.in：identifyRspLength=384（:8）、driveStateFile=/var/lib/nvidia-nvme-manager/nvme_drive_state.json（:10）、bootProgressTimeout=300s（:11）；meson_options.txt 还有 drive_sanitize_time=30（:13）、fw_update_progress_timeout=600（:66）、drive_temp_threshold_confirmation_count=3（:52）等。**README 的选项表只列了 8 个，实际 13 个**（缺 nvme_mi_sensors/boot_progress_timeout/fw_update_progress_timeout/drive_temp_threshold_confirmation_count/nvme_update_service_prefix/nvme_update_request_dir/mux_manager）。

## 2. 源码地图：六层结构

| 层 | 内容 | 代表文件/锚点 |
|---|---|---|
| L01 构建与工程配置 | meson 五处 + config 头模板 + clang-tidy(397行)/clang-format | meson.build:97-98 systemd 单元目录探测 |
| L02 MCTP 发现与传输 | NVMeIntf.hpp variant 工厂（:71 `variant<shared_ptr<NVMeBasicIntf>, shared_ptr<NVMeMiIntf>>`）→ NVMeMi.cpp(1618行) → MCTPDiscovery.hpp | 见 §4 |
| L03 设备核心与装配 | NVMeDeviceMain.cpp(1429) + NVMeDevice.cpp(1204) + SoftwareInventory + dbusutil | 见 §3 |
| L04 传感器子系统 | NVMeMiSensorManager.cpp(440)/NVMeMiSensor.cpp(299)/Thresholds.cpp(288)/NVMeMiStatusSensor | 见 §5 |
| L05 固件更新线 | NVMeFwUpdateHandler.cpp(694) + tool/NVMeFwUpdate.cpp(292 瘦客户端) | 见 §6 |
| L06 Mux 与部署 | NVMeMuxManager.cpp(187) + 两个 systemd 单元 | 见 §7 |

hub：NVMeMi.hpp/NVMeIntf.hpp（所有设备的传输底座）、NVMeDeviceMain.cpp（全局 driveMap :47-51 与事件装配）。

## 3. 核心链路一：主程序装配（NVMeDeviceMain.cpp）

`main()`（:1115）只认一个参数 `--debug`（:1119-1125，开了才调 NVMeMi::initLogging :1129，**没有 --help/--version**）。装配序列：io_context + sdbusplus connection（:1134-1135）→ object_server 挂三个 manager：inventory/system/nvme、sensors、FIRMWARE_INVENTORY 时的 software（:1137-1141）→ NVME_MI_SENSORS 时向 NVIDIA TAL TelemetryAggregator 注册 "nvmesensor" 命名空间（:1143-1147）→ post 里 createDrives + request_name("xyz.openbmc_project.NVMeDevice")（:1156-1159）→ 挂五个 D-Bus match：EM Inventory.InterfacesAdded（1s 防抖 :1161-1180/:1189-1196）、EM 传感器配置出现（EM 晚启动竞态，:1198-1228）、mctp 端点 InterfacesAdded/Removed（:1252-1269）、MCTP Connectivity 属性变化（au.com.codeconstruct.MCTP.Endpoint1，:1273-1282）、**host0 电源状态**（:1337-1417）→ startNvmeFwUpdateMonitor（:1419）→ io.run()（:1421）。

`createDrives`（:420）用 GetObjects 拉 mctp 端点配置，kernel-MCTP 与 userspace(mctpd) 两种接口集合分流（:429-438）；`handleMCTPEndpoints`（:341）按 SupportedMessageTypes 含 NVME_MI_MSGTYPE_NVME&0x7F（:377-378）筛出 NVMe 盘端点。host0 状态机是生命周期关键：**Off → 先 cancel 全部端点再逐个 closeEndpoint+deferredDestroyDrive**（:1362-1387，注释 :1370-1372 解释为何先全 cancel——让共享 worker 队列排干）；Running → 重扫（暖重启场景 mctpd 不重发 InterfacesAdded，:1397-1407）。开机后 cold-removal 检查延迟 bootProgressTimeout=300s（:1286-1315 + meson_options.txt:60）。

## 4. 核心链路二：NVMeMi 传输层（1618 行）

NVMeMi 封装 libnvme-mi 端点（ctor :45-101）：`nvme_mi_create_root` 全局单例（:33-38），INKERNEL_MCTP 走 `nvme_mi_open_mctp(net,eid)`（:78）否则 `nvme_mi_open_libmctp`（:81），响应超时 2000ms（:22, :96-100）。

**线程模型是本仓最容易被误解的点**：Worker 是自实现的 io_context+condition_variable 线程（:103-127，注释解释因 BOOST_ASIO_DISABLE_THREADS 下 executor_work_guard 跨线程失效才手搓）。静态 `workerMap`（:27-31）按 int 键存 worker，但构造函数**硬编码 find(0)**——注释原文 "only create one share worker for all drives"（:62-72）：**全进程一个 worker 串行执行所有盘的 NVMe-MI 传输**（DeepWiki 的"same bus 共享 worker 池"描述与源码不符）。取消机制三重检查 commandsCancelled（post 时 :201、任务出队后 :207、拿到 endpointMux 后 :215），closeEndpoint（:166-182）持 endpointMux 排他后再 nvme_mi_close。

命令面：MI 层 miPCIePortInformation（:240，选 portt==0x1 的 PCIe 口 :319-323）、miSubsystemHealthStatusPoll（:341，true=clear 标志）、miScanCtrl（:405，controllers 按 eid 存 :457）、miVpdRead（:474，需 HAVE_NVME_MI_MI_XFER 否则 operation_not_supported :478-483，opcode 0x05 :24）；Admin 层 adminIdentify（:560，readLength<4096 走 Partial :589-597）、adminGetLogPage（:924，九种 lid 大 switch：ERROR 只搬一箱防阻塞 :961-963、SMART 少读 rsvd232 :990-991、TELEMETRY 按 dalb3 算全长 :807-809）、adminSanitize（:822，sanicap 解码 CES/BES/OWS/NDI/NODMMAS :851-855，canUseNodas :858）、adminXfer（:1216，临时改端点超时再复原 :1267-1275）、adminSecuritySend/Receive（:1509/:1552，单次上限 maxNVMeMILength=4096 :21, :1557）。**例外**：adminFwCommit（:1316）与 adminFwDownload（:1419）不投 worker，直接在调用者线程持 endpointMux 同步执行（:1337/:1447）——固件更新路径独立于轮询串行线。

## 5. 核心链路三：设备对象与传感器

NVMeDevice（NVMeDevice.cpp:33）每盘一实例：ctor 先 markFunctional(true)（:64-65"先当它是好的"），`NVMeIntf::create<NVMeMi>` 建传输（:68），formFactor 字符串映射 15 种规格（:73-138，未识别回落 U2 :137）。`pollDrive()`（:668）是**递归自调度**循环：scanTimer 到期→弱引用存活检查（:680-687）→不在位则 initialize 重试（:699-703）→connectivity 降级则跳过本轮回排（:706-713）→sanitize 进行中查 SANITIZE log 推进度（sprog*100/65536，封顶 99% :761-766）→health poll 更新 pdlu/predictedMediaLifeLeftPercent/markFunctional(nss&0x20 :803)→SMART 解析 critical_warning 并**叠加 D-Bus 侧五个 err 标志位**（:834-854），变化才发 Redfish 事件（:891）后递归 pollDrive（:898）。默认轮询 5s（NVMeDevice.hpp:233），EM 配了传感器间隔则用 sensorPollIntervalSec（:674-676）。

传感器线（sensors/）：NVMeMiSensorManager 消费 EM 的 **NVME1000 / Nvmem2** 两类配置（NVMeMiSensorManager.cpp:143/:172），按 EID 建 SensorContext（:41, :266）；温度传感器 NVMeMiSensor 继承 sdbusplus SensorArea、physicalContext=StorageDevice（NVMeMiSensor.cpp:29, :50），updateValue→checkThresholds（:180/:256）；Thresholds.cpp 带确认计数防抖——需连续 driveTempThresholdConfirmationCount=3 次越限才 assert（:182-196），另有迟滞。状态传感器 NVMeMiStatusSensor 发 OK/缺盘布尔。

## 6. 核心链路四：固件更新（service 触发 + 瘦客户端）

新架构：**真正刷固件的是 manager 自己**。NVMeFwUpdateHandler 监听 systemd1 的 JobNew 信号（:686-692），只认 nvme-update@.service 前缀 + JobType=="start"（:639-675），请求参数从 /run/nvidia-nvme-update/<id>.env 解析（:209-211），30s 窗口去重防 systemd 重复信号（:552-571），然后**每目标起一个 detached std::thread 跑 runFwUpdate**（:617-619）。runFwUpdate（:340）流程：4KB 分块下载（fwUpdateChunkSize=4096 :43）最多重试 5 次（:45）→commit 到 slot 0（:44）→若 commit 报"reset 后镜像丢失"则整轮重来一次（fwCommitResetRestartMaxRetries=1 :46, :515-522）→进度经 Progress 接口回报。七种 Redfish 事件（logTargetDetermined/logTransferringToComponent/logTransferFailed/logAwaitToActivate/logUpdateSuccessful/logActivateFailed/logNoMatchingDevices，:65-135）全在这里。

`tool/NVMeFwUpdate.cpp` 已瘦身为**监控客户端**（文件头 :5-8 自述"Thin client"）：接受与旧版相同的 CLI 参数（firmware_path/version 只做非空校验、实际不使用，:80-106），订阅每盘的 Progress.Status 属性变化（:156-196）+ 初值直读防漏（:199-225），30 秒无任何进度即判失败（:228-251），总超时 600s（:30, :255）。

## 7. Mux 管理器、状态持久化与部署

NVMeMuxManager（NVMeMuxManager.cpp）是独立小守护：读 /etc/nvme/mux-devices.json（:28, :30-52，空配置直接退出 :122-125），监听 chassis0 CurrentPowerState（:19-21, :142-177），上电 bind/下电 unbind pca954x I2C MUX（sysfs /sys/bus/i2c/drivers/pca954x/bind|unbind :25-26, :65-95），启动时先同步一次当前电源态（:132-139）。盘状态持久化：updateSingleDriveState（NVMeDeviceMain.cpp:446-546）读改写 JSON（EID/driveName/locationCode/serialNumber/connectivity），带去重（removeDuplicateDriveStates :84-100）；README:248 说 connectivity 三值 "Available/Degraded/Unknown"——源码里 updateSingleDriveState 只写死 "Available"（:500），Degraded 由 connectivityChanged 路径（:803）维护。部署：nvidia-nvme-manager.service `Requires=mctp-i2c12-ctrl.service mctp-i2c12-demux.service`（**硬编码 i2c12 总线**，service:2-3）、Restart=always、WantedBy=obmc-power-on@0.target（盘是上电设备，service:11）；mux-manager After=Chassis.Control.Power@0（:3）。

## 新人上路

**按目的找文件**：加 D-Bus 接口→NVMeDevice.cpp+相关 hpp（sdbusplus server 声明）；加一种 log page→NVMeMi.cpp adminGetLogPage 的 switch（:955）+NVMeDevice.cpp 消费；调轮询→pollDrive/scanTimer；改 EM 配置解析→NVMeDeviceMain handleEmEndpoints（:115）/传感器侧 NVMeMiSensorManager；固件更新→FwUpdateHandler。**陷阱**：①全局单 worker 意味着一盘慢命令会拖住所有盘的轮询——加新命令务必走 post() 且别在 worker 里做重活；②FwCommit/FwDownload 是同步路径，别照它抄异步代码；③二进制名是 nvme，容器里和 nvme-cli 共存会打架；④service 的 i2c12 依赖是板级硬编码，换平台必改；⑤pollDrive 递归无界，取消靠 weak_ptr 失效与 operationsCancelled。

（完·锚点均经源码逐行核实）
