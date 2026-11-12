# 讲透 NVIDIA/Fabric-Manager-Client

[NVIDIA/Fabric-Manager-Client](https://github.com/NVIDIA/Fabric-Manager-Client)——FM Partition Manager（fmpm v1.0.1）：单文件 C++ CLI，经 libnvfm（Fabric Manager agent API）连接 nvfm 守护进程，管理 Shared NVSwitch 的 GPU Fabric 分区（列出/激活/去激活/设已激活清单）并查询 NVLink 失效设备，结果以 jsoncpp StyledWriter JSON 输出。微仓一体通道（3 文件：fmpm.cpp 468 行 + Makefile 12 行 + README 38 行）。

## 全链状态表

| 阶段 | 状态 | 产物 |
|---|---|---|
| deepwiki | ✅ 100% | [deepwiki/](deepwiki/INDEX.md) |
| understand 图谱 | ✅ 11n/11e · 2 层 3 步 tour · validator 0 issues · fingerprints 3 文件 @8ec6fb8e | 仓内 `.understand-anything/knowledge-graph.json` |
| onboarding+explain | ✅ 合并口径（README+ONBOARDING 一体，微仓无独立 explain） | [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md) |

源码：`/usr-data/data2/repos/agent-repos/NVIDIA/Fabric-Manager-Client`。批阶段甄别笔记 2 条见仓内 `.understand-anything/NOTES-DIGEST.md`。

## 源码级勘误清单

1. **Makefile U+2215 DIVISION SLASH 真笔误**：`Makefile:1` `IDIR := ∕usr∕include` 与 `Makefile:4` `LDIR := ∕usr∕lib` 共 4 处路径分隔符是 Unicode U+2215（∕，字节 `e2 88 95`）而非 ASCII `/`——`-I/-L` 实际指向不存在的目录；构建仍成功纯因 `/usr/include`、`/usr/lib` 本就是默认搜索路径、编译器静默忽略无效目录。上游真实笔误（字节级核实，Makefile 偏移 8 处起）。
2. **--unix-domain-socket 实际不通（连接装配死代码+覆盖 bug）**：`fmpm.cpp:420-431` 两个条件分支（uds/hostname）对 `addressInfo`/`addressIsUnixSocket` 的写入，被 `fmpm.cpp:434-435` 无条件的 `strncpy(connectParams.addressInfo, mHostname, sizeof(mHostname)); addressIsUnixSocket = 0;` 全部覆盖——传 uds 时实际连接目标被改写为 mHostname（默认 `127.0.0.1`，`fmpm.cpp:334`），而 `addressType` 保留分支设置的 `NV_FM_API_ADDR_TYPE_UNIX`（`:424`，434-435 不覆盖它），形成「INET 地址+UNIX 类型」混合态。README.md 却把 UDS 列为一等选项并给出 FM_CMD_UNIX_SOCKET_PATH 配置指引——宣传的通道在代码里走不通。
3. **strncpy 误用方向**：`fmpm.cpp:434` 第三参传 `sizeof(mHostname)`（源大小，256）而非目标 `addressInfo` 大小——方向反了的安全惯用法。
4. **死枚举两枚**：`fmpm.cpp:26-27` `SHARED_FABRIC_CMD_CONVERT_BIN_TO_TXT/CONVERT_TXT_TO_BIN` 全仓仅枚举声明处出现，无解析分支、无 dispatch、无帮助输出。
5. **幽灵注释**：`fmpm.cpp:15` 注释称枚举顺序须与 "the struct all_args list, below" 对应，但全文件无 `struct all_args`——从其他 NVIDIA 工具拷贝脚手架的残留。
6. **仓内零内部 import**：`fmpm.cpp:1-4` 四个 include（iostream/string.h/json/json.h/nv_fm_agent.h）全为外部——jsoncpp 与 fabricmanager-devel 的 nv_fm_agent.h 都是系统级依赖，图谱 11 边全部为文件→函数/枚举/外部依赖关系，无仓内代码依赖边。

## 快速上手

依赖 `nvidia-fabricmanager-devel + libjsoncpp-dev`（README.md 构建节）；`make && ./fmpm -l` 走默认 TCP 127.0.0.1（需 Fabric Manager 侧 FM_CMD_BIND_INTERFACE）。命令族：`-l` 列分区（`fmpm.cpp:65` listPartitions）、`-a/-d <ID>` 激活/去激活（`:175`/`:188`）、`--set-activated-list`（`:200`，FM Resiliency 重启恢复用，需 FABRIC_MODE_RESTART=1）、`--get-nvlink-failed-devices`（`:224`，GPU+NVSwitch 两类设备 uuid/pciBusId/失效端口）。详见 [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md)。
