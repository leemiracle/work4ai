# nvidia-installer 仓库 Onboarding（615.78.08）

> 仓库 `/usr-data/data2/repos/agent-repos/NVIDIA/nvidia-installer`（commit 42dcc4b7）；图谱 349 节点/628 边/10 层/12 步导览，fingerprints 57 文件基线。锚均经源码核实。

## 1. 这是什么仓库

NVIDIA 官方 Linux 驱动 `.run` 包里的安装器本体：一个 C 语言单二进制工具（外加 mkprecompiled 小工具），负责把解包后的驱动文件（`.manifest` 清单驱动）编译/链接内核模块、复制落盘、写备份日志、重建 initramfs，并能逆向卸载。57 个源文件中五个巨型 .c 就占了 12.9K 行：misc.c 3433、files.c 3376、kernel.c 2866、backup.c 1786、install-from-cwd.c 1491（`wc -l` 实测）；nvGpus.h 2955 行是纯数据表。README 明说实现无正式文档（`README:15`），用法在驱动 README 第 4 章。

## 2. 五分钟心智模型

**清单驱动的命令解释器**：一切安装动作先被翻译成 CommandList 再统一执行。`main()`（`nvidia-installer.c:647`）先 `load_default_options`（`:657`，dkms/disable_nouveau 默认 TRUE，`nvidia-installer.c:140/:152`）→ `pci_device_scan`（`:664`）扫 GPU → 解析命令行（`parse_commandline`，`nvidia-installer.c:224`）→ `ui_init`（`:680`）→ 五分支派发：查驱动信息（`:720`）/`sanity`（`:726`）/卸载（`:732`）/`--add-this-kernel`（`:739`）/默认 `install_from_cwd`（`:745`）。

三大支柱：
- **编排**：`install_from_cwd`（`install-from-cwd.c:96`）串起 manifest 解析→前置检查→内核模块→命令清单→执行→后检查。
- **UI 抽象**：函数指针表 `InstallerUI`（`nvidia-installer-ui.h:39`），ncurses 版以 `.so` 二进制内嵌进可执行文件、运行时解出再 dlopen（见 explain/01）。
- **可逆性**：备份日志 `/var/lib/nvidia/log`（`backup.c:47`）逐文件记 CRC/mode/uid/gid，卸载按日志逆向回滚（见 explain/02）。

## 3. 目录地图

| 文件 | 职责 |
|---|---|
| `nvidia-installer.c` | 入口 760 行：默认值/命令行/main 派发 |
| `option_table.h` | 全部选项定义 790 行，`__options[]`（`:126`）是 --help 与 manpage 的单一事实源 |
| `install-from-cwd.c` | 安装编排 1491 行；`parse_manifest`（`:726`）把 `.manifest` 变成 `Package` 结构 |
| `misc.c` | 系统探测大杂烩 3433 行：EUID/系统工具/X server/nouveau/DKMS/SELinux/systemd/SecureBoot |
| `files.c` | 落盘层 3376 行：copy/install/symlink/SELinux 上下文（`set_security_context`，`files.c:2207`） |
| `kernel.c` | 内核模块 2866 行：conftest（`:155`）/构建（`build_kernel_modules`，`:672`）/签名（`sign_kernel_module`，`:703`）/装载（`load_kernel_module`，`:1637`） |
| `backup.c` | 备份/卸载 1786 行：`init_backup`（`:137`）/`do_backup`（`:208`）/`uninstall_existing_driver`（`:1393`） |
| `user-interface.c`+`ncurses-ui.c`+`stream-ui.c` | UI 三层：抽象+全屏实现+纯文本兜底 |
| `nvGpus.h` | 2955 行 PCI ID→GPU 标志数据表：`GpuFlagList`（`:1568`）、`GpuSubDeviceFlagList`（`:1816`） |
| `common-utils/` | 与 nvidia-modprobe 同源的公共库：nvgetopt 自研解析器（`common-utils/nvgetopt.c:37`）、msg 分级日志（`common-utils/msg.c:126`）、libpciaccess 封装（`common-utils/nvpci-utils.c:39`） |
| `precompiled.c`/`mkprecompiled.c` | 预编译内核接口包格式（包头 `"\aNVIDIA\a"`，`precompiled.h:100`）与打包工具（`main`，`mkprecompiled.c:593`） |

## 4. 分层走读（图谱 10 层重组为六段）

1. **L01 构建与打包**：Makefile 把 ncurses UI 三变体 .so 用 `ld -r --format=binary` 链成目标文件（`utils.mk:610`）实现单文件分发；manpage 由 `gen-manpage-opts`（`gen-manpage-opts.c:11`）吃选项表生成 `options.1.inc`，再 m4 替换进 `nvidia-installer.1.m4`（`Makefile:314`）。
2. **L02 common-utils**：nvgetopt 支持 `--no-` 前缀自动生成布尔开关（`common-utils/nvgetopt.c:471`）；msg 按终端宽度折行（`common-utils/msg.c:64`）。
3. **L03-04 入口与 UI**：前置检查 `sanity()`（`sanity.c:33`）校验既有安装完整性（`test_installed_files`，`sanity.c:56`）；`detect-self-hosted.h:29` 用 PCI ID 区间（GH100 0x2340-0x237f、GB100 0x2940-0x297f）识别 Grace 自持 GPU。
4. **L05-06 编排与文件**：`install_from_cwd` 全流程见第 5 节；文件裁剪按文件类型能力（`get_file_type_capabilities`，`manifest.c:144`）——Wine/systemd/OpenGL 各自可整类剔除（`files.c:1215/:1230/:1200`）。
5. **L07 内核与 initramfs**：模块构建前 `run_conftest` 探测内核接口；SecureBoot 开启时走 `assisted_module_signing`（`install-from-cwd.c:1148`）调内核源码树 `sign-file`（探测在 `kernel.c:682`）；initramfs 按 dracut/update-initramfs/mkinitcpio 三工具探测（`initramfs.c:223/:232/:241`）。
6. **L08-10 预编译/备份/GPU 库**：`find_precompiled_kernel_interface` 按 `/proc/version` 匹配免编译接口；备份线保证可逆；`pci_device_scan`（`misc.c:1876`）查 `GpuFlagList` 判 GSP/vGPU 分支，vGPU 宿主强制开源模块的规则在 `misc.c:1779`。

## 5. 数据流与控制流：install_from_cwd 主链

`parse_manifest`（`install-from-cwd.c:117`）→ legacy GPU 警告（`check_for_nvidia_graphics_devices`，`misc.c:2005`）→ X 在跑/占用 VT 检查（`misc.c:1442/:1673`）→ distro `pre-unload` 钩子（`:141`）→ 确认模块已卸载（`kernel.c:1660`）→ 既有驱动/替代安装质询（`misc.c:2333`）→ `pre-install` 钩子（`:175`）→ 内核模块线（`:230`）→ 按包裁剪 → `set_destinations`（`files.c:528`）→ 卸旧+`init_backup`（`install-from-cwd.c:324/:327`）→ `build_command_list`（`command-list.c:747` 起收集冲突模块/已存文件）→ 用户批准（`:345`）→ `do_install`→`execute_command_list`（`misc.c:777/:787`）→ 重载 nvidia-drm（`:360`）→ `post-install` 钩子（`:374`）→ `check_installed_files_from_package`（`misc.c:1088`）。

## 6. 构建与运行

依赖仅 ncurses+pciutils（`README:20`）。`make` 产出安装器、mkprecompiled、手册；`--ui=none --no-questions` 走纯文本流适合脚本化。`.run` 包本质是 makeself 自解压壳，`makeself-help-script.c:29` 支持 `--help` 直通。

## 7. 设计决策与陷阱

- **UI 以二进制内嵌**：避免安装器找不到/找错 UI 库（`README:28` 论动机）。
- **两级 CRC 校验**：备份时算 CRC（`backup.c:240`），安装后 `verify_crc`（`misc.c:1202`）复核。
- **冲突模块按反依赖序排列**：`conflicting-kernel-modules.c:29` 从 nv_peer_mem 到 nvidia-frontend，卸载/initramfs 扫描共用该序。
- 陷阱：`ui_list` 顺序是编译期条件性的（ncurses6/ncursesw6 需构建探测到对应库才存在，`Makefile:111`）。

## 8. 新人上手指引

1. 从 `nvidia-installer.c:647` main 读到 `install_from_cwd`，抓住五分支派发。
2. 读 explain/01（UI 三层）与 explain/02（备份可逆线）。
3. 改 GPU 支持只动 `nvGpus.h`；改选项须同步 `option_table.h`（manpage 自动再生成）。
4. 调试用 `/var/log/nvidia-installer.log`（`nvidia-installer.h:556`）与 `--debugfuncfile` 类选项。

---
字数 4651（非空白字符）/锚 46
