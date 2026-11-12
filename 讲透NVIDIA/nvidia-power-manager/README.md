# 讲透 nvidia-power-manager（全链索引）

| 阶段 | 状态 | 产物 |
|---|---|---|
| deepwiki | ✅ | `deepwiki/`（19 页 TRUE_100） |
| understand 图谱 | ✅ | 仓内 `.understand-anything/knowledge-graph.json`：284n/261e/7层/8步，validate 0 issues，fingerprints 103 文件@9ff8ebd2 |
| onboarding | ✅ | `onboarding/ONBOARDING.md`（7 节，锚 40+） |
| explain | ✅ | `explain/` 3 篇（power_manager.cpp / libcpld.cpp / deltapsuxx.hpp） |

**定位**：NVIDIA OpenBMC 电源管理聚合仓——主服务（JSON 驱动的冗余/状态/功耗上限引擎）+ power-balancer（CPU→GPU 功耗联动）+ PSU 双守护 + CPLD/PSU/MTD 三族固件烧写工具。C/C++ + meson。

## 源码级勘误（均经行号核实，vs README/图谱/直觉认知）

1. **powermanager.json 不是 sdbus++ 模板（图谱描述纠偏）**：图谱 L02 摘要称"powermanager.json 是 sdbus++ 模板"。它是**运行时行为配置**（PowerRedundancyConfigs/powerState/powerCappingConfigs 四对象，src/README.md:3-5），随包安装到 /usr/share/nvidia-power-manager/powermanager.json（src/meson.build:6, :14-15），由 PowerManager 构造时 loadJSONFromFile 装载（power_manager.cpp:205）。
2. **根 README.md 只有一行**：全文即 "Nvidia power management app."（README.md:1）——有效文档在 src/README.md（255 行配置模型）与 nvidia-power-balancer/README.md（278 行拓扑契约），按根 README 找方向会一无所获。
3. **src/README.md 自称四对象却写五节**：:4-5 说配置"divided into four objects"（PowerRedundancyConfigs/powerState/powerCappingConfigs/powerCappingSavePath），随后 :241 又文档化第五节 powerCappingAlgorithm（按模块功耗百分比），且该节在 power_manager.cpp:234-257 是实际被消费的核心配置。
4. **src/README.md 的 interfaceName 示例是复制粘贴错**：:184-185 "interfaceName - the interface on which the property is populated" 的示例原文是 `"objectName": "/xyz/openbmc_project/control/power/CurrentChassisLimit"`——复制了上一条 objectName 的例子，没改成接口名。
5. **printError 的 ERROR_ERASE 分支打印错误文案**：dragonChassisBase.hpp:84-86，`case ERROR_ERASE: msg = "UpdateError::ERROR_LOAD_IMAGE"`——擦除失败会被日志标成 LOAD_IMAGE，排障时误导阶段定位（对照同函数其余 20 个分支均一一对应）。
6. **caluclateChecksum 拼写错误（API 级）**：power_manager.cpp:472 与 power_manager.hpp:214——"calculate" 拼成 "caluclate"，声明/实现/两处调用（:594/:1265）全错拼一致，grep 正确拼写找不到。
7. **udpateProperty 拼写错误（API 级）**：PsuMonitor.cpp:87 定义、:186/:203/:220 三处调用——"update" 拼成 "udpate"，同样全链一致错拼。
8. **main 双总线 + 从未运行的 sdevent**：power_manager_main.cpp:46-53 先建 `sdbusplus::bus::new_default()` 并 attach 到 sdeventplus Event，再另建 boost::asio io_context + asio connection 做 object_server；sdevent 循环从头到尾没有 run——attach 是残留结构，classic bus 实际只做同步 ObjectMapper 调用（power_manager.cpp:43-107）。
9. **IBM 版权头暴露血统**：power_manager_main.cpp:19 保留整段 "Copyright © 2019 IBM Corporation" Apache 头——该守护源自 IBM phosphor 谱系代码（实体管理器式配置驱动风格同源），与 NVIDIA 新写模块（balancer 等 Apache-2.0+NVIDIA 头）并存。
10. **mtdupdate.sh 默认剥掉镜像前 4096 字节**：mtd_update/mtdupdate.sh:20——不带 nostrip 参数时固件头部 4KB 被截去再写入 MTD（U-Boot 头剥离惯例），不知此行为直接对读回内容会以为镜像损坏。
11. **三个 feature 选项默认 disabled**：meson_options.txt:1-17/:28-31——dragon_chassis_psu、dragon_chassis_cpld、power_balancer 默认都不构建；克隆即编译得到的是主服务+PSU/CPLD 守护子集，balancer 要 -Dpower_balancer=enabled。
12. **deltapsuxx.hpp 是 783 行纯实现头文件**：全协议（解锁/CRC16/激活）内联在 .hpp（无 .cpp），与其并列的 dragonDeltaPsu.cpp 反而是回调实现——"头文件放声明"的惯例在此仓不适用。

## 关键事实速查
- 主服务：D-Bus 名 com.Nvidia.Powermanager（src/meson.build:2）；功耗百分比总和上限 100（power_manager.cpp:41/:245）；持久化 /etc/powerCap.bin 结构体直存+两遍 checksum（:593-599）。
- balancer：LocationContext 精确匹配配对 CPU/GPU（balancer README:30-36）；NaN/Inf/负功耗兜底回默认（gpuCpuPowerSyncControl.cpp:134-141）；job 超时默认 60s（meson_options.txt:44-50）。
- 远端 FPGA：镜像必须页对齐（libcpld.cpp:100-106）；忙等 TRY_TIMES 上限（:21-54）；DELAY_1000MS 常量名与 "// 1ms" 注释矛盾（:260/:698）。
- Lattice CPLD：fwUpdate 七段编排 enableConfiguration→erase→sendImage→waitRefresh→validate→activate（dragonCpld.cpp:49-104）。
