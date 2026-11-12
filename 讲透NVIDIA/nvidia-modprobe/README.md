# 讲透 nvidia-modprobe（NVIDIA/nvidia-modprobe）

> NVIDIA 内核模块加载工具与设备节点创建库的官方开源仓：setuid CLI + 核心库源码，
> 供无特权用户态驱动组件完成 modprobe 与 `/dev/nvidia*` mknod。
> 本地仓：`/usr-data/data2/repos/agent-repos/NVIDIA/nvidia-modprobe`（commit 4ffadd6b，随驱动分支 615.78.08）。

## 流水线状态

| 步骤 | 状态 | 产物 |
| --- | --- | --- |
| DeepWiki 全量抓取 | ✅ 既有 | `deepwiki/`（19 内容页，wiki_full.md 193KB，含 INDEX/_coverage-check） |
| understand 图谱 | ✅ 2026-11-09 | 仓内 `.understand-anything/knowledge-graph.json`：98 节点/150 边/6 层/8 步 tour，fingerprints 26 文件基线@4ffadd6b（meta/project.name=nvidia-modprobe，自洽） |
| onboarding | ✅ 2026-11-09 | `onboarding/ONBOARDING.md`（8 节，5209 非空白字符，32 唯一全路径锚，机器终验 0 坏） |
| explain | ✅ 2026-11-09 | `explain/` 2 篇：01-nvgetopt 解析器+CLI（六节）、02-PCI sysfs+库面（六节） |

## 源码级实证勘误（vs DeepWiki 快照 / man 模板 / 注释 / 图谱）

1. **DeepWiki 版本常量过期**：wiki 版本管理页表格与示例写 `NVIDIA_VERSION = 575.64`（wiki_full.md "Version Constants" 表），实仓 `version.mk:1` 为 **615.78.08**——快照落后两个驱动分支代。
2. **DeepWiki verbosity 阶梯顺序错误**：wiki 画 `ERROR → WARNING → DEPRECATED → ALL` 且 `DEFAULT → WARNING`；实码枚举顺序为 NONE=0→ERROR→**DEPRECATED**→**WARNING**→ALL（`common-utils/msg.h:95-99`，DEPRECATED=2 **小于** WARNING=3），且 `NV_VERBOSITY_DEFAULT = NV_VERBOSITY_ALL`（`common-utils/msg.h:100` + `common-utils/msg.c:45`）——默认档 info 消息就会打印，不是 wiki 暗示的"仅告警"。
3. **man 手册残留已删除的 `--module-instance` 选项**：`nvidia-modprobe.1.m4:46`（SYNOPSIS/DESCRIPTION）与 `:73-74`（示例 `nvidia-modprobe -i 0` → `modprobe nvidia0`）仍宣传该选项，但选项表九项中已无此项（`option-table.h:19-83`），实跑 `-i 0` 走 `common-utils/nvgetopt.c:246` 报 unrecognized option——文档代差，非代码 bug。
4. **注释与实现脱节**：`modprobe-utils/nvidia-modprobe-utils.c:301` 注释 "Fork and exec modprobe from the child process"，实际 `:314` 是 `posix_spawn`（DeepWiki 此处反而写对了，错的是仓内注释）。
5. **"setuid 工具"的安装语义要分家**：仓内多处自称 setuid utility（`nvidia-modprobe.c:18`），但本仓独立构建的 `make install` 落 **0755 非 setuid**（`utils.mk:96` `INSTALL_BIN_ARGS ?= -m 755`）；setuid 位由 nvidia-installer 或发行版包装补上（man 模板自述 "When installed by nvidia-installer … installed setuid root"）。
6. **图谱 L05 "头文件声明 18 个 API" 少计一个**：`modprobe-utils/nvidia-modprobe-utils.h:78-96` 实数 **19** 个（file_state/modprobe/mknod/nvlink/nvswitch/cap/imex/vgpu/msr/online_movable 族）。
7. **nvpci-utils.c 在独立构建中不编译**：仅 `COMMON_UTILS_PCIACCESS` 置位才入 SRC（`common-utils/src.mk:15-19`），否则只进 EXTRA_DIST 打包（`:31`）；本仓 Makefile 未设该变量。且它绑定 libpciaccess（`common-utils/nvpci-utils.c:39` `nvpci_find_gpu_by_vendor`），与本仓自研 sysfs 枚举（`pci-sysfs.c`）是平行不互通的两套 PCI 机制。
8. **库导出面远大于 CLI 面**：`nvidia_vgpu_vfio_mknod`（`modprobe-utils/nvidia-modprobe-utils.c:905`）、`nvidia_msr_modprobe`（`:828`）、IMEX 通道族（`:1063`）与 `pci_rescan`/`pci_find_parent_bridge`/`pci_bridge_link_set_enable`（`modprobe-utils/pci-sysfs.c:324/:358/:439`）在仓内**零调用者**——CLI 选项表（9 项）触达不到，服务驱动树内构建的库消费者。

## 口径说明

- 字数=不计空格总字符；锚=唯一 `file:line`（可含行区间），全部经 `sed -n`/`grep -n` 对源码核实。
- 甄别事实补充：CLI 退出码语义反转（库 1=成功，main `return !ret`，`nvidia-modprobe.c:288`）；`-c` minor 上限 64、`-f` 上限 256（`nvidia-modprobe.c:91-92`）；auto-online-movable 直写 `/sys/devices/system/memory/auto_online_blocks`（`modprobe-utils/nvidia-modprobe-utils.c:1131`）。
