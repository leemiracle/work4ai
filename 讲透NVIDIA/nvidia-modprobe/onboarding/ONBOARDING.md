# nvidia-modprobe 仓库 Onboarding

> 仓库 `/usr-data/data2/repos/agent-repos/NVIDIA/nvidia-modprobe`（commit 4ffadd6b，随驱动分支 615.78.08 发布，`version.mk:1`）；图谱 98 节点/150 边/6 层/8 步 tour（fingerprints 26 文件@4ffadd6b）。**本文全部行号锚经源码逐条核实**。

## 1. 这是什么仓库

一个 setuid 小工具加它的核心库源码：让**没有特权的用户态 NVIDIA 组件**（典型如非 root 用户跑的 CUDA driver）能完成两件特权操作——加载 NVIDIA 内核模块、创建 `/dev/nvidia*` 字符设备节点。文件头自述"This is a small setuid utility"（`nvidia-modprobe.c:18`），并明言发行版若有自己的模块/设备管理机制则应优先用发行版方案（`nvidia-modprobe.c:21-23`）。全仓 26 个文件约 3000 行 C，对外有两个面：CLI（`nvidia-modprobe.c` 289 行）和库（`modprobe-utils/nvidia-modprobe-utils.c` 1166 行，头文件导出 19 个 API，`modprobe-utils/nvidia-modprobe-utils.h:78-96`）。

## 2. 五分钟心智模型

问题：GPU 驱动库打开 `/dev/nvidia0` 时，节点可能不存在（模块没载/udev 没建），普通用户又无权 `modprobe`/`mknod`。解法三步走：**查**——`is_kernel_module_loaded` 看 `/sys/module/<name>/initstate` 是否存在（`modprobe-utils/nvidia-modprobe-utils.c:99`，模块名 `-`→`_` 归一化在 `:113-119`）；**载**——没载且自己是 root 就 spawn `modprobe`（`modprobe_helper`，`:179`）；**建**——按三态位图 FileExists/ChrDevOk/PermissionsOk（`modprobe-utils/nvidia-modprobe-utils.h:59-64`）决定节点是否需重建（`mknod_helper`，`:549`）。库函数统一约定**返回 1=成功**，CLI 侧 `return !ret`（`nvidia-modprobe.c:288`）把语义翻回"0=成功"的进程退出码。

## 3. 目录地图

| 位置 | 职责 |
|---|---|
| 根 `nvidia-modprobe.c` | CLI 唯一入口：nvgetopt 解析后按分支调库（`nvidia-modprobe.c:89` main） |
| 根 `option-table.h` | 9 项 nvgetopt 选项表（`option-table.h:19`），CLI/`--help`/man 三处共享的事实源 |
| `common-utils/` | 与 nvidia-xconfig/nvidia-settings/nvidia-installer 共用的基础层（`common-utils/src.mk:1` 自注）：`nvgetopt.c`（490 行自研解析器）、`common-utils.c`（861 行字符串/文件工具）、`msg.c`（428 行分级日志）、`gen-manpage-opts-helper.c`（man 选项段生成器） |
| `modprobe-utils/` | 核心库 `nvidia-modprobe-utils.c` + `pci-sysfs.c`（sysfs PCI 枚举）+ 三个头 |
| 根构建件 | `Makefile`（include `utils.mk` 共享模板，`Makefile:22`）、`version.mk`（版本注入，`:1`）、`dist-files.mk`（打包清单）、`nvidia-modprobe.1.m4`（man 模板） |

## 4. 分层走读（图谱 6 层）

自上而下单向依赖：

1. **CLI 入口**（L06）：main 解析 `-c/-u/-m/-s/-l/-f/-a`（`option-table.h:33-81`）后按标志分发；`-c` 可重复、上限 64 个 minor（`nvidia-modprobe.c:91`，超限报错 `:134`），`-f` 上限 256（`:92`/`:157`）。
2. **模块加载核心库**（L05）：模块装载 + 设备节点 + 权限参数三合一；`nvidia_modprobe`（`:354`）只是 `modprobe_helper` 的薄封装。
3. **PCI sysfs 枚举**（L04）：`pci_enum_match_id`（`modprobe-utils/pci-sysfs.c:90`）扫描 `/sys/bus/pci/devices` 做 vendor/device/class 匹配——回答"这台机器有没有 NVIDIA 显示类设备"。
4. **common-utils 基础库**（L03）：nvgetopt/msg/字符串工具；`__verbosity` 默认即 ALL（`common-utils/msg.c:45` + `common-utils/msg.h:100`）。
5. **manpage 生成链**（L02）：构建期把 option-table 印进手册，`gen-manpage-opts.c:24` 的 main 只喂表。
6. **构建与版本**（L01）：`all: 二进制+manpage`（`Makefile:100`）；common-utils/modprobe-utils 支持驱动树内/独立 tarball 双位置（`Makefile:66` 一带 `?=` 缺省）。

## 5. 数据流与控制流

**CLI 分发**是五互斥分支：`-l` nvlink→`-s` nvswitch→`-u` UVM→`-a` auto-online-movable→默认（`nvidia-modprobe.c:171-258`）；`-m` modeset（`:260`）与 `-f` cap 文件（`:277`）在任何分支后叠加执行。

**modprobe_helper 闸门链**（`:179-348`）：已载即成功（`:213`）→ 仅 root 尝试（`:220`）→ PCI 枚举确认存在显示类卡（`:234`；匹配条件 class `0x0300`+`PCI_BASE_CLASS_MASK` 覆盖 VGA/3D 控制器，`:195-203`；无卡且非 Tegra 则报 "no NVIDIA devices found" `:246`；Tegra 判定读 `/sys/devices/soc0/family`，`:146-168`）→ 从 `/proc/sys/kernel/modprobe` 读路径（`:256`），缺省 `/sbin/modprobe`（`:289`）→ `posix_spawn` 启动（`:314`），env 只有 `PATH=/sbin`（`:187`）→ `waitpid` 后**复检模块**判成败（`:345`）。

**节点创建**：`/proc/driver/nvidia/params` 可覆盖 DeviceFileUID/GID/Mode 与 ModifyDeviceFiles（`:367-411`）；禁止修改时只补 `/dev/char/<major:minor>` 相对符号链接（`:571`→`symlink_char_dev`，`:478`）；三态齐则免建，否则 remove+mknod（`:613`）+chmod/chown（`:625`）。cap 设备带路径安全闸：必须 `/proc/driver/nvidia` 前缀且拒绝 `./`（`:1001-1002`）。

## 6. 构建与运行

`make` 产 `nvidia-modprobe` 二进制与 manpage（`Makefile:100`）。man 生成链：HOST 编译 `gen-manpage-opts`（`:24`）→ 跑出 `options.1.inc` → `m4` 替换进模板（`Makefile:155`），并盖 AUTO-GENERATED 警告头（`Makefile:134`）。注意**独立构建安装是 0755 非 setuid**（`utils.mk:96` `INSTALL_BIN_ARGS ?= -m 755`）；setuid 位由 nvidia-installer 或发行版包装落上（man 模板明言 "When installed by nvidia-installer … installed setuid root"）。验证：`./nvidia-modprobe -v` 打 NV_ID_STRING；`--help` 走 `nvgetopt_print_help(__options, 0, …)`（`nvidia-modprobe.c:85`）。

## 7. 设计决策与陷阱

- **posix_spawn 而非 fork/exec**（`:314`）：`:301` 注释仍写 "Fork and exec"——注释滞后于实现。
- **最小环境变量** `PATH=/sbin`（`:187`）：setuid 程序卫生学。
- **waitpid 返回值被忽略**（`:345`）：注释解释 SIGCHLD 被设为 SIG_IGN 时 waitpid 会 ECHILD，成败以"模块是否真载入"复检为准。
- **手写 legacy dev_t 编码** `NV_MAKE_DEVICE`（`:85-86`）、主设备号 195 硬编码（`:88`）、ctl 设备 minor 255 / modeset minor 254（`modprobe-utils/nvidia-modprobe-utils.h:34-35`）。
- **nvgetopt 静态 `argv_index`**（`common-utils/nvgetopt.c:53`）：解析器状态在静态存储，非重入；整数参数 `strtol` base 0（`:314`），`-c 0x10` 也解析。
- **库面远大于 CLI 面**：`nvidia_vgpu_vfio_mknod`（`:905`）、`nvidia_msr_modprobe`（`:828`）、IMEX 通道族（`:1063`）以及 `pci_rescan`/`pci_find_parent_bridge`/`pci_bridge_link_set_enable`（`modprobe-utils/pci-sysfs.c:324/:358/:439`）在仓内零调用者，服务驱动树内的库消费者。
- **nvpci-utils.c 不进独立构建**：仅当 `COMMON_UTILS_PCIACCESS` 置位才编译（`common-utils/src.mk:15-31`），本仓 Makefile 未设；它属 libpciaccess 世界（`nvpci_find_gpu_by_vendor`，`common-utils/nvpci-utils.c:39`），与自研 sysfs 枚举层平行。

## 8. 新人上手指引

阅读序：`option-table.h`（19 行表体看全用户面）→ `nvidia-modprobe.c` main → `modprobe_helper` → `mknod_helper` → `nvidia_cap_mknod`。改选项只需改 option-table，CLI/`--help`/man 三处自动同步（gen-manpage-opts-helper 的 `&`/`^` 标记在终端 help 里被 `cook_description` 剥掉，`common-utils/nvgetopt.c:392`，在 man 里转义为斜体/粗体，`common-utils/gen-manpage-opts-helper.c:97-98`）。调试入口：`nvidia_get_chardev_major`（`:657`）扫 `/proc/devices` 的 "Character devices:" 段（`:675`）——major 拿不到是模块未载的最常见症状。五个先看函数：`modprobe_helper`、`mknod_helper`、`nvidia_cap_mknod`、`nvidia_get_chardev_major`、`assign_device_file_name`（`modprobe-utils/nvidia-modprobe-utils.h:104`，minor 255 折叠为 nvidiactl，`:117`）。

---
*字数 5209（非空白字符）/唯一全路径锚 32（另有跟随式 `:NNN` 段锚数十处，均经 `sed -n` 核实，机器终验 0 坏）*
