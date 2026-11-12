# Fabric-Manager-Client Onboarding（fmpm v1.0.1，微仓一体口径）

> 图谱基线：11 节点 / 11 边 / 2 层（L01 客户端主程序层 9 节点 · L02 构建与文档层 2 节点）/ 3 步 tour · fingerprints 3 文件 @8ec6fb8e · 锚全部源码核实（2026-11-07）

## 1. 定位与结构（它是什么）

NVIDIA Fabric Manager（nvfm 守护进程，DGX/HGX 多 NVSwitch 系统的 fabric 拓扑管理器）的官方命令行客户端样例：单文件 `fmpm.cpp`（468 行）+ `Makefile` + `README.md`，三个文件就是全部。核心价值是演示 libnvfm agent API 的标准用法——生命周期四段式 `fmLibInit`（`fmpm.cpp:408`）→ `fmConnect`（`:437`，fmConnectParams_t 于 `:415` 组装，timeoutMs=1000 于 `:416`）→ 业务调用 → `fmDisconnect`（`:465`）+ `fmLibShutdown`（`:466`）。全部输出统一走 jsoncpp `StyledWriter`（`:116/:167/:288`），依赖仅 jsoncpp 与 fabricmanager-devel 提供的 `nv_fm_agent.h`（`:4` include，仓内零内部依赖）。

## 2. 七个业务函数与命令分派

main（`:295`）用 if-else 链逐个 argv 字符串比较解析选项（非 getopt），与 `fmpm.cpp:13-29` 的 SharedFabricCmdEnum 枚举一一对应后按 operation 分派：`-l` → listPartitions（`:65`，调 fmGetSupportedFabricPartitions，逐分区/逐 GPU 装配 partitionId/isActive/uuid/pciBusId/NVLink 数与线速率 JSON——主查询路径）；`-a/-d <ID>` → activatePartition/deactivatePartition（`:175`/`:188`，fmActivate/DeactivateFabricPartition）；`--set-activated-list <ID,...>` → setActivatedPartitionList（`:200`，fmSetActivatedFabricPartitionList，Fabric Manager Resiliency 重启模式恢复用）；`--get-nvlink-failed-devices` → getNvlinkFailedDevices（`:224`，fmGetNvlinkFailedDevices，GPU 与 NVSwitch 两类设备分别输出失效端口）；`--list-unsupported-partitions` → listUnsupportedPartitions（`:124`）。分区 ID 串解析在 parsePartitionIdlistString（`:33`，strtok 切逗号）：越界（<0 或 ≥ FM_MAX_FABRIC_PARTITIONS，常量引用见 `:36/:44/:305/:349`）报 BADPARAM，重复 ID 静默去重。

## 3. 连接装配与两处真 bug（读码必读）

connectParams 组装是全仓唯一有「故事」的地方，也是勘误重灾区：`fmpm.cpp:419` 先 memset 清零 addressInfo；`:420-424` uds 分支（socket path + IsUnixSocket=1 + addressType=UNIX）；`:426-431` hostname 分支（INET）——随后 `:434-435` **无条件** `strncpy(addressInfo, mHostname, sizeof(mHostname)); IsUnixSocket=0;` 把前面两个分支对这两个字段的写入全部覆盖（仅 addressType 幸存）。后果：`--unix-domain-socket` 实际连的是 mHostname（默认 127.0.0.1，`:334`），且带着 UNIX 类型标志形成混合态——README 宣传的 UDS 通道在代码里走不通；`:434` strncpy 第三参还传了源大小而非目标大小。另有两枚死枚举（`:26-27` CONVERT_BIN_TO_TXT/TXT_TO_BIN，全仓仅声明处出现）和幽灵注释（`:15` 引用不存在的 struct all_args）。

## 4. 构建管线与 U+2215 笔误

Makefile 仅 12 行、fmpm/clean 两目标：`Makefile:2` CXXFLAGS 头文件路径取 pkg-config jsoncpp，`Makefile:5` 链接 `-lnvfm -ljsoncpp`，`Makefile:7-8` g++ 编译链接。著名笔误：`Makefile:1` `IDIR := ∕usr∕include`、`Makefile:4` `LDIR := ∕usr∕lib` 的分隔符是 Unicode U+2215 DIVISION SLASH（非 ASCII 斜杠，字节 `e2 88 95`，共 4 处）——-I/-L 指向不存在目录，构建纯靠默认搜索路径兜底、编译器静默忽略而「碰巧能编译」。这是引用本仓时最常被问到的细节：不是你的终端字体问题，是上游真笔误。

## 5. 上手路径与邻接知识

五分钟路径：装 nvidia-fabricmanager-devel + libjsoncpp-dev → `make` → `./fmpm -l`（默认 TCP 127.0.0.1，需 FM 侧 FM_CMD_BIND_INTERFACE 配合；README.md 有三项 FM 配置项说明）→ 对照 `:65` listPartitions 读 JSON 字段。想扩展（如实现死枚举对应的 state file 转换命令）：抄 `:33` 解析器 + `:295` if-else 模式即可，api 语义参考 nv_fm_agent.h。邻接：Fabric Manager 本体不在本仓（这是客户端），DGX/HGX fabric 管理概念见 README 引用的 fabric-manager-user-guide 三链接（分区/Resiliency/domain socket 接口）。勘误全表见上级 [README.md](../../../../README.md)。
