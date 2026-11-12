# 讲透 nvidia-installer（NVIDIA/nvidia-installer）

> NVIDIA 官方 Linux 驱动 `.run` 包安装器本体（C，清单驱动：manifest→内核模块→命令链执行→备份可逆卸载）。
> 本地仓：`/usr-data/data2/repos/agent-repos/NVIDIA/nvidia-installer`（615.78.08，commit 42dcc4b7，2026-11-09 分析）。

## 流水线状态

| 步骤 | 状态 | 产物 |
| --- | --- | --- |
| DeepWiki 全量抓取 | ✅ 既有 | `deepwiki/`（INDEX+wiki_full，16 结构页，180K 字符） |
| understand 图谱 | ✅ 2026-11-09 | 仓内 `.understand-anything/knowledge-graph.json`：**349 节点/628 边/10 层/12 步 tour**，fingerprints 57 文件基线@42dcc4b7 |
| onboarding | ✅ 2026-11-09 | `onboarding/ONBOARDING.md`（4651 非空白字符，8 节，46 唯一行号锚，全部 sed 逐条核实） |
| explain | ✅ 2026-11-09 | `explain/` 2 篇：01 入口派发与内嵌 .so UI 体系（2615/22 锚）、02 备份日志与卸载可逆线（2532/17 锚） |

## 本轮源码级实证勘误（vs DeepWiki 快照/仓 README）

1. **DeepWiki 行号错锚：continue_after_error**。DeepWiki 称"continue-after-error prompts for non-critical failures via misc.c:905-924"；实际函数在 `misc.c:750-770`（`continue_after_error`，`misc.c:750`），905-924 行是 `extract_version_string()` 的版本号状态机，与错误处理无关。
2. **"None UI" 不是第三种 UI 实现**。DeepWiki 把 "None UI: Silent operation for automated deployments" 与 Stream/Ncurses 并列为 UI 实现；源码里 `--ui=none` 只是令 `op->ui.name="none"`（`nvidia-installer.c:262`），`ui_list[]` 匹配不到任何带描述的条目后落到内建 `stream_ui_dispatch_table`（`user-interface.c:190`）——它是 stream 的一条选择路径；真静默是 `--silent`（`user-interface.c:146` 直接跳过整个 dlopen 循环）。
3. **README 所述 `gen-ui-array` 工具在本仓已不存在**。`README:32` 称 UI .so 由 gen-ui-array 转成字节数组源文件；现行机制是 utils.mk 的 `ld -r -z noexecstack --format=binary`（`utils.mk:610` 规则、`:614` 命令）+objcopy 改名 `.rodata`，头文件由 shell printf 生成 `_binary_*_start/_end` 声明（`utils.mk:622`）；全仓 grep `gen-ui-array` 仅 README 一处（历史机制残文）。
4. **UI 优先级表是构建条件性的，非固定四级**。DeepWiki 给出固定优先级 ncurses6→ncurses→ncursesw6→stream；实际 ncurses6/ncursesw6 两项被 `#if defined(NV_INSTALLER_NCURSES6/NCURSESW6)` 包裹（`user-interface.c:122/:132`），宏只在构建探测到对应库时定义（`Makefile:111-112`）——从源码 tarball 默认构建只有 ncurses→stream 两级。
5. **备份日志是"两行一条"而非单行六字段**。DeepWiki 图示 "Log: number, filename, crc, mode, uid, gid" 为一条记录；实际 `backup.c:250` 先写 `"%d: %s\n"`（编号: 路径）、`backup.c:254` 再写 `"%u %04o %d %d\n"`（crc/mode/uid/gid），解析端 `parse_crc_mode_uid_gid`（`backup.c:428`）按行对消费。
6. **`--ui` 的 help 文本窄于实际可接受值**。`option_table.h:396` 说 "Valid values are 'ncurses' (the default) or 'none'"；但 `ui_list` 实际还接受 `ncurses6`/`ncursesw6`（编译期存在时，`user-interface.c:128-140`），且默认并非显式字符串而是 `ui.name==NULL` 时按列表顺序探测（`user-interface.c:154-163`）。
7. **main 派发是五分支而非"装/卸"两模式**。常见简化描述漏掉 `--info`（`report_driver_information`，`nvidia-installer.c:720`）、`--sanity`（`:726`）与 `--add-this-kernel`（`:739`）三条非安装路径。

## 口径说明

- 字数采信**不计空格总字符**；行号锚全部相对仓根，写入前经 `sed -n 'Np'`/`grep -n` 源码核实（46+22+17 个唯一锚，终验 0 坏）。
