# 讲透 nvidia-nvme-manager（全链索引）

| 阶段 | 状态 | 产物 |
|---|---|---|
| deepwiki | ✅ | `deepwiki/`（20 页 TRUE_100） |
| understand 图谱 | ✅ | 仓内 `.understand-anything/knowledge-graph.json`：148n/212e/6层/7步，validate 0 issues，fingerprints 44 文件@1016dfdb |
| onboarding | ✅ | `onboarding/ONBOARDING.md`（7 节，锚 45+） |
| explain | ✅ | `explain/` 3 篇（NVMeMi.cpp / NVMeDeviceMain.cpp / NVMeFwUpdateHandler.cpp） |

**定位**：OpenBMC 上的 NVMe 设备管理守护——经 MCTP/NVMe-MI（libnvme-mi）发现监控 NVMe 盘，发布 D-Bus Inventory/Sensor/Status 对象，附带固件更新与可选 I2C MUX 管理。C++23 + meson，依赖 sdbusplus/boost/nlohmann/libnvme-mi/phosphor-logging。

## 源码级勘误（均经行号核实，vs README/DeepWiki/直觉认知）

1. **README「Firmware Update Tool」整章描述的是旧架构（重磅）**：README:140-205 称 NVMeFwUpdate 工具自己做 "4KB chunked transfer / retry / parallel updates / 七种事件"。源码中 tool/NVMeFwUpdate.cpp 头注释自述 **"Thin client: monitor NVMe firmware update progress... the actual update is performed by nvme-manager when nvme-update@.service starts"**（:5-8）；工具只订阅 Progress.Status（:156-196）+30s 无进度判败（:228-251），firmware_path/version 参数仅做非空校验、全程不使用（:80-106）。4KB 分块/重试/七事件全部在 manager 内的 NVMeFwUpdateHandler.cpp（chunk=4096 :43、retries=5 :45、logXxx 七件 :65-135）。
2. **DeepWiki "worker 按总线共享（same underlying bus）" 不符**：DeepWiki 3.3:101 称 "Worker threads are shared among NVMe-MI endpoints that use the same underlying bus"。源码 NVMeMi.cpp:62-72 硬编码 `workerMap.find(0)`，注释原文 "only create one share worker for all drives"——**全进程唯一 worker 串行服务所有盘所有总线**，bus 字段不参与 worker 选择。
3. **adminFwCommit/adminFwDownload 绕过 worker 线程**：其余全部命令经 post() 进 worker 串行执行（NVMeMi.cpp:199-222），但这两个固件命令直接在调用者线程持 endpointMux 同步执行（:1337、:1447）——为 FwUpdateHandler 的 detached 线程（NVMeFwUpdateHandler.cpp:617-619）独占端点让路，也意味着刷固件期间调用线程阻塞。
4. **adminSecurityReceive 两处复制粘贴日志错**：超长错误文案写 "nvme_mi_admin_security_send returned excess data"（:1591-1593，实际是 recv）；post 失败文案写 "adminSecuritySend post failed"（:1611-1614，出现在 Receive 函数里）。排障时会被日志引到错误路径。
5. **守护二进制名是 `nvme`，与 nvme-cli 同名**：src/meson.build:24 `executable('nvme', ...)`，service ExecStart=/usr/bin/nvme（service_files/nvidia-nvme-manager.service:7）——镜像里同时装 nvme-cli 会互相覆盖 /usr/bin/nvme。README:140 的工具名 NVMeFwUpdate 实际安装名也是 `nvme-fw-update`（tool/meson.build:1）。
6. **service 单元硬编码 i2c12 总线**：nvidia-nvme-manager.service:2-3 `Requires=mctp-i2c12-ctrl.service mctp-i2c12-demux.service`——板级假设写死在通用单元里，换平台必改；且 `WantedBy=obmc-power-on@0.target`（:11）表明该服务随机箱上电启动而非开机常驻。
7. **README 选项表缺 7 个构建选项**：README:86-95 列 8 项，meson_options.txt 实有 13+ 项——漏 nvme_mi_sensors（默认 **true**，:44）、boot_progress_timeout=300（:59）、fw_update_progress_timeout=600（:66）、drive_temp_threshold_confirmation_count=3（:52）、nvme_update_service_prefix（:73）、nvme_update_request_dir（:80）、mux_manager（:87，feature 默认 disabled）。
8. **README connectivity 三值口径与源码不符**：README:248 称状态文件 connectivity 可为 "Available/Degraded/Unknown"；updateSingleDriveState 只写死 "Available"（NVMeDeviceMain.cpp:500），Degraded 走 connectivityChanged（:803）单独路径，"Unknown" 在源码中无写入点。
9. **main 没有 --help/--version**：唯一识别的命令行参数是 --debug（NVMeDeviceMain.cpp:1119-1125，仅用于开 libnvme-mi 日志 :1127-1130）。
10. **miPCIePortInformation 端口循环多探一次**：`for (auto i = 0; i <= ssInfo.nump; i++)`（NVMeMi.cpp:288）——nump 为端口数、端口号 0 基，上界含等号即多读一个不存在的端口 ID；因循环内先找 portt==0x1 即 break（:319-323），PCIe 系统通常无感，但纯 SMBus 端点会多打一次必败的 read_mi_data_port。

## 关键事实速查
- 传输：NVMe-MI over MCTP，响应超时 2000ms（NVMeMi.cpp:22）；Security 单次上限 4096B（:21/:1557）；VPD 读需 libnvme-mi 提供 mi_xfer（:23-24/:478-483）。
- 发现：mctpd 接口集 xyz.openbmc_project.MCTP.Endpoint + UnixSocket + I2CDevice（NVMeDeviceMain.cpp:434-437）；kernel-MCTP 则 au.com.codeconstruct 路径（:41-45/:430-432）。
- 传感器：EM 配置接口 NVME1000/Nvmem2（NVMeMiSensorManager.cpp:143/:172）；温度阈值需连续 3 次越限才告警（Thresholds.cpp:182-196）。
- 状态文件：/var/lib/nvidia-nvme-manager/nvme_drive_state.json（nvme-mi_config.h.in:10），逐盘增量读改写（NVMeDeviceMain.cpp:446）。
