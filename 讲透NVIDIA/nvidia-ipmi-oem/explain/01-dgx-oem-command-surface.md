# 01 · src/oemcommands.cpp — DGX 平台 OEM 命令面：4511 行的注册表与 dispatch

## 一、角色定位

`src/oemcommands.cpp`（4511 行，全仓最大文件）是 DGX 服务器（A100/H100 系）带外管理的全部 OEM 命令面：一个文件同时承载命令常量消费、38+ 处理器实现和注册表 `registerNvOemFunctions`（`src/oemcommands.cpp:4019`）。更关键的是它的**复用身份**——CMake 把它编进包括 BF2/BF3/Spectre 在内的所有平台构建（`CMakeLists.txt:208-215` 的 BF 组合全都含 `src/oemcommands.cpp`），所以这个"DGX 核心"实际上也是 BF 族的公共底座。图谱口径 fanOut=149（全仓最高）正反映它被全平台引用的事实。

## 二、内部结构

**1) 命令坐标系（头部）。** NetFn 常量来自 `include/oemcommands.hpp:26-30`（0x32 Global / 0x3C NV / 0x30 Post / 0x3E Eight / GroupExt 0x52）。include 面很杂：`linux/i2c-dev.h`+`sys/ioctl.h`（I2C 直访）、`openssl/pem.h`+`x509.h`（证书指纹）、`security/pam_appl.h`（账户操作）（`src/oemcommands.cpp:24-29`）。

**2) 三个功能族。** ①**D-Bus 翻译族**：`ipmiGetDNSConfig`（:437）/`ipmiSetNTPConfig`（:621）/`ipmiGetSELPolicy`（:760）/`ipmiGetBMCBootComplete`（:1177）——纯属性读写转发；②**硬件直访族**：`i2cTransaction`（:349）open `/dev/i2c-N`+ioctl 复合成主读写原语，`ipmiI2CMasterReadWrite`（:1111）与其配套的 `getMaskdata` 位掩码拆包（`include/oemcommands.hpp:158`，调用点 :3834-3836）；PSU 拓扑常量钉死在 `include/dgx-a100-config.hpp:29-31`（6 颗 PSU，地址 {0x40,0x41,0x42}×2 组、总线 215-221）；`ipmiGetPSUInventory`（:1576）按此表逐颗扫；③**状态机族**：`ipmiSystemFactoryReset`（:281）两步走（网络复位→软件更新器复位，D-Bus yield 调用），风扇三命令 `ipmiSetFanZonePWMDuty`（:1436）/`ipmiSetAllFanZonesPWMDuty`（:1528）/`ipmiSetFanControl`（:1544）。

**3) 注册表（:4019-4511）。** 每条命令一段"NOTICE 日志 + `ipmi::registerHandler(prioOemBase, netFn, cmd, Privilege::Admin, handler)`"模板，例如 I2C 主读写挂在 netFnOemPost（:4025-4028）。两个特例值得记：Factory Reset 被 `#ifndef BF41_OEM_COMMANDS` 包住（:4039）——BF4-1 构建下 DGX 版让位给 `src/BF/BF4/oemcommands.cpp:51` 的对齐实现（走 `xyz.openbmc_project.Common.FactoryReset` D-Bus 接口，与 Redfish Manager.ResetToDefaults 同路径）；bootstrap 账户用 `registerGroupHandler` + `Privilege::sysIface`（:4452-4455）挂 Group Extension 0x52，特权即通道闸。

## 三、外部连接

- **被加载**：无 main，靠 `__attribute__((constructor(101)))`（:206）在 ipmid dlopen 时率先注册，优先级低于它的 BF 核心（102）与变体（103）随后覆盖。
- **D-Bus 对端**：xyz.openbmc_project.NetworkManager/Time/Logging/Software/State.Host/User.Manager 等十余个服务。
- **头文件消费**：`include/oemcommands.hpp`（fanIn=5）+ `dgx-a100-config.hpp`（fanIn=4）+ `biosversionutils.hpp`（BIOS POST 码 :1682 与版本查询 :2967 用）。
- **平台复用**：BF 核心的同名 `*BF` 后缀函数（风扇 :726-746、BIOS :828-874）大量是本文件函数的拒绝桩化变体。

## 四、数据流

以 `ipmitool raw 0x30 0x31 ...`（I2C master read/write）为例：帧到 ipmid → metrics filter 旁路记录 → 本仓 handler `ipmiI2CMasterReadWrite`（:1111）解析 bus/slaveAddr/wrData → `i2cTransaction`（:349）open+ioctl 发起 SMBus 事务 → 读回数据包进 `ipmi::response` 回程。D-Bus 族则把 yield_context 交给 sdbusplus 协程，属性值原样回填响应结构。整条链无锁、单线程 io_context 驱动（BOOST_ASIO_DISABLE_THREADS，`CMakeLists.txt:94`）。

## 五、设计决策

- **一文件巨石 vs 分裂**：38+ 命令挤在一个文件是刻意的——命令族共享 D-Bus 工具函数与错误码（`ipmiCCBIOSPostCodeError=0x89` 等，:221-225），拆文件成本高于收益。
- **注册优先级链**（101/102/103）是平台差异的主要表达：不复制文件，用"先注册后被覆盖"实现按平台熔断命令。
- **硬件表驱动**：PSU 地址/寄存器号全部常量化（`include/dgx-a100-config.hpp:29-41`），换机型只改头文件。
- **陷阱**：BF 构建包含本文件意味着改 DGX 命令会波及所有 BF 发行版——回归测试必须跨平台构建。

## 六、新人提示

从 `registerNvOemFunctions`（:4019）自上而下读注册表即可获得全部命令号清单；配合 ipmitool raw 逐条验证。注意本文件在 BF 构建中也被编译（`CMakeLists.txt:137-152`），别把"DGX 专属"当成文件属性。改 Factory Reset/BIOS 命令时先看 `#ifndef BF41_OEM_COMMANDS`（:4039）与 Grace 侧平行实现（`Grace/src/ghoemcommands.cpp:2946` 起的注册表）。

---
字数 2959（非空白字符）/锚 28（唯一行号锚：全路径 10+上下文 18）
