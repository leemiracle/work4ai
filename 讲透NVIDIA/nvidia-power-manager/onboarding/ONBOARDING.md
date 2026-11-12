# nvidia-power-manager 深度导览（ONBOARDING）

> 仓：/usr-data/data2/repos/agent-repos/NVIDIA/nvidia-power-manager @9ff8ebd2
> 图谱：284 节点 / 261 边 / 7 层 / 8 步导览，fingerprints 103 文件。C/C++ + meson（>=1.1.1，C++23，b_lto，根 meson.build:1-6）。

## 1. 这个项目是什么：一仓五件的电源管理套件

这不是单一守护，而是 NVIDIA OpenBMC 电源管理的**聚合仓**（根 meson.build:10-19 顺序聚合七个 subdir）：①主服务 nvidia-power-manager（src/，D-Bus 名 com.Nvidia.Powermanager，src/meson.build:2）；②nvidia-power-balancer（CPU/GPU 功耗联动，feature 默认 disabled）；③nvidia-power-supply（PSU 发现注册）；④nvidia-psu-monitor（PSU 寄存器轮询）；⑤nvidia-cpld（CPLD D-Bus 守护）+ cpld_utility/psu_utility 两族固件烧写工具 + mtd_update 脚本。根 README.md 只有一行 "Nvidia power management app."——真正的文档在 src/README.md（255 行 JSON 配置模型）与 nvidia-power-balancer/README.md（278 行拓扑契约）。

## 2. 源码地图：七层结构

| 层 | 内容 | 代表锚点 |
|---|---|---|
| L01 共享硬件访问库 | include/ 三件：dragonChassisBase.hpp（503 行虚基类，:35 `class DragonChassisBase : public I2c`）、i2c.hpp（195）、crc.hpp（91） | sysfs 读写 :269/:294、I2C 仲裁使能 :318 |
| L02 主服务 | power_manager.cpp（1356）+ power_manager_property.hpp（562，PowerCappingInfo :37/PowerMode 枚举 :147/Property 模板 :167）+ powermanager.json（446 行运行时配置） | 见 §3 |
| L03 功耗联动 | balancer 三件套：gpuCpuPowerSync.hpp（230，DeviceInfo 模型）、Discovery（776）、Control（296）+ jobMonitor（246） | 见 §4 |
| L04 nvidia-cpld 守护 | cpld_manager.cpp（101）从 JSON 配置注册 SoftwareAsset/Version/Association | cpld.hpp 287 行 |
| L05 CPLD 烧写工具族 | cpld_utility：libcpld.cpp（928，远端 MB/MID FPGA）、dragonCpld.cpp（662，Lattice 状态机）、main.cpp、updateCPLDFw_dbus_log_event.cpp（65） | 见 §5 |
| L06 PSU 双守护 | psu_manager.cpp（86，发现注册）+ PsuMonitor.cpp（388，pollRegisters :255/start :318） | 见 §6 |
| L07 PSU 烧写工具 | psu_utility：deltapsuxx.hpp（783，头文件即全实现）、dragonDeltaPsu.cpp（208）、dragonChassisBasePsu.cpp（144）、main.cpp（395） | 见 §7 |

## 3. 主服务：JSON 驱动的电源状态机（power_manager.cpp）

配置模型（src/README.md 详解）：powermanager.json 装到 /usr/share/nvidia-power-manager/powermanager.json（src/meson.build:6/:14-15），四类对象驱动一切行为——PowerRedundancyConfigs（监听 psu_drop_to_1_event 等 sensor 属性触发动作链）、powerState（chassis0 CurrentPowerState 触发 SEL 记录）、powerCappingConfigs（发布 /control/power/* 属性并挂动作）、powerCappingSavePath（默认 /etc/powerCap.bin，README:255）+ powerCappingAlgorithm（按模块分配功耗百分比）。动作块支持 methodName/appendData（dataType+data+variant 标志）/conditionBlock（带 timeDelay 的前置条件）/OEM data 走 oemKeyHandler 按 key 分发（README:98-104）。

PowerManager 构造（power_manager.cpp:197）加载 JSON（:205）与 /etc/powerCap.bin 持久化快照（getPowerCapFileLength :131 → loadPowerCapInfoFromFile :156 → memcpy :218）；updatePowerCappingStructure（:506）把 JSON 值灌进 PowerCappingInfo 结构并 caluclateChecksum（:472，注意此拼写是上游原文）后 dumpPowerCapIntoFile（:176）。updatePowerCappingLimit（:422）按 PowerMode（Q/P 模式 :426-437）切换 chassisPowerLimit_Q/P 并按 powerCappingAlgorithm 百分比分发到模块（:445-466，总和超过 maxTotalPowerConsumption=100 报错 :41/:245）。**main 的双总线结构值得注意**（power_manager_main.cpp:46-56）：`sdbusplus::bus::new_default()` 挂 sdevent、再建 asio connection——classic bus 供 manager 做同步 ObjectMapper 查询（util::getService :43-107，MAPPER 常量 :38-40），asio bus 供 object_server；sdevent 循环从未 run。该文件还保留 "Copyright © 2019 IBM Corporation" 头（:19）——代码源自 IBM phosphor 谱系。

## 4. 功耗联动：nvidia-power-balancer（GPU 跟随 CPU）

拓扑契约（balancer README:22-40）：EM 给每 CPU/GPU 发 Inventory 对象（CPU_N/GPU_N 命名硬要求），分组键是 LocationContext（如 "HGX_Chassis_0/ProcessorModule_0"）——同模块的 CPU 与 GPU 靠**LocationContext 精确匹配**配对。Discovery（gpuCpuPowerSyncDiscovery.cpp）三路入口：getSubTreeAsync 全量扫描（:22-85，筛 has LocationContext 且 has CPU/GPU 接口）、emDeviceAddedHandler（:87，InterfacesAdded 即时发现）、associations 两监视器（:305/:336）。Control（gpuCpuPowerSyncControl.cpp）核心 setPowerCapOnGpu（:24）：CPU 未就绪（powerCapValue==DefaultPowerCap/PowerCapInvalid，:37-38）或 GPU 未就绪（:48）则跳过，CPU==GPU 已同步则跳过（:59），否则异步 set 并交 JobMonitor 跟踪（:71-95）。powerCapChangedHandler（:108）对 NaN/Inf/负值兜底回 DefaultPowerCap（:134-141）。JobMonitor（jobMonitor.cpp:25 create/:64 start）监听异步 job 的 StatusChanged（:127）+ 超时定时器（job_monitor_timeout_seconds 默认 60s，meson_options.txt:44-50），完成/失败回调（:188/:230）。1355 行 94 个 sdbus-mock 测试覆盖全链（tests/test_gpuCpuPowerSync.cpp）。

## 5. CPLD 固件线：远端 FPGA 烧写 + Lattice 状态机

两条并行线共享 include/ 基座。**libcpld.cpp（928 行）是 MB/MID 板远端 FPGA 镜像烧写**：wait_until_not_busy（:21）轮询状态寄存器（写 00 20 00 20 读 4 字节，bit 判 STATUS_BUSY，TRY_TIMES 上限）；flash_remote_mb_fpga_image（:57）/ flash_remote_mid_fpga_image（:488）流程：open /dev/i2c-N（O_RDWR|O_NONBLOCK，:82）→ 校验镜像尺寸必须是 MB_PAGE_SIZE_BYTES 整数倍（:100-106）→ 分页写入，每步间 wait_until_not_busy 把守（:205/:232/:260/:356）→ 全程 emitLogMessage 发 Redfish 事件（target_deter/ver_failed 等，updateCPLDFw_dbus_log_event.cpp:65 行工具）。**dragonCpld.cpp（662 行）是本机 Lattice CPLD 状态机**：fwUpdate（:49）编排 enableConfigurationInterface（:227）→ erase(true)（:253，Lattice 规范命令）→ sendImage（:297）→ waitRefresh（:406）→ validate（:445）→ activate（:512，规范要求置 2 位标志）→ cleanUp（:573）；readFwVersion（:183）/readDeviceId（:164）供版本上报。基类 DragonChassisBase（dragonChassisBase.hpp:35）提供镜像装载、sysfs 读写（:269/:294）与 I2C 总线仲裁开关（:318，arb 构造参数 :44），纯虚 sendImage（:502）由子类实现。

## 6. PSU 双守护：发现注册 + 轮询

nvidia-power-supply（psu_manager.cpp:37 PSUManager）从配置发现 PSU 并注册 Inventory/传感器/版本/关联接口，psu_util.hpp（245 行）承载 PMBus 命令层；nvidia-psu-monitor（PsuMonitor.cpp）做实际轮询：getPsuConfigValues（:43）读配置 → pollRegisters（:255）周期经 i2cRead（:115）读检测/在位寄存器 → update_status（:161）判定变化 → udpateProperty（:87，拼写为上游原文）更新 Inventory present/powerState/operationalStatus 三接口（:186/:203/:220 调用点），start（:318）挂 D-Bus 后立即首轮 pollRegisters（:372）。

## 7. PSU 固件升级：psu_utility 工具族

deltapsuxx.hpp（783 行，**头文件即全部实现**）是 Delta 新一代 PSU 升级协议：MCU_hdlr 表按 section 索引（APPCRC_STA/FLASH_STA/Delay_1/2/3 五元组，:194-197）；fwupdate(imageFilename, section)（:323）流程：读镜像算 CRC16（:388-409）→ unlockDevice（:213）→ 逐段擦除/发送 → REG_TRANSMIT_CRC=0xF4 收尾发校验（:84, :659-670，"Operation: 0xF4 0x03 MCU_ID CRC16_LO CRC16_HI PEC"）→ activate（:767）；boot 标志与输出禁用恢复逻辑穿插在 :441-484 的 unlock 重试里。dragonChassisBasePsu.cpp 先 checkManufacturer（:42）防刷错厂商再 fwUpdate（:78）；dragonDeltaPsu.cpp（208）实现解锁/擦除/CRC 收发/激活四段。入口 main.cpp（395）：unTar 经 execl("/bin/tar")（:43/:65）解包固件包、file_lock 用 fcntl F_WRLCK 互斥（:91-112）再调度升级。mtd_update/mtdupdate.sh（113 行）是 MTD 分区更新壳：默认**剥掉镜像前 4096 字节**（nostrip 可关，:20），支持 setup_<image_name>.sh/cleanup 前后钩子。

## 新人上路

**按目的找文件**：改电源冗余/上电 SEL 行为→powermanager.json（不用改代码）；加 power cap 属性→power_manager_property.hpp 的 Property + json 的 powerCappingConfigs；改 GPU 联动→balancer Control/Discovery；加新 CPLD 烧写命令→dragonCpld.cpp（本机）或 libcpld.cpp（远端 FPGA）；PSU 升级协议→deltapsuxx.hpp。**陷阱**：①根 README 无信息，别按它找文档；②powermanager.json 是运行时配置不是 sdbus++ 模板（装到 /usr/share/）；③balancer/power-balancer 与 dragon_chassis_psu/cpld 三个 feature 默认 disabled（meson_options.txt:1-17/:28-31），发行版不开启就没有这些组件；④printError 的 ERROR_ERASE 分支错误打印成 "ERROR_LOAD_IMAGE"（dragonChassisBase.hpp:84-86），排障看日志别被带偏；⑤/etc/powerCap.bin 是结构体直存（loadPowerCapInfoFromFile memcpy），跨版本结构体变了旧文件校验会走 checkChecksum（:489）失败重建路径。

（完·锚点均经源码逐行核实）
