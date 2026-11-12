# 01 · nvidia-installer.c + user-interface 三件套 — 入口派发与"内嵌 .so"UI 体系

## 一、角色定位

`nvidia-installer.c`（760 行）是全仓调度中枢：不管安装/卸载/健全性检查/`--add-this-kernel` 哪条路，都从这里的 `main()`（`nvidia-installer.c:647`）进。`user-interface.c`（821 行）+`ncurses-ui.c`（1994 行）+`stream-ui.c`（530 行）构成 UI 三层——这层解决一个独特约束：安装器跑在"系统最脆弱时刻"（可能没有完整用户态），UI 必须零外部依赖。

## 二、内部结构

**1) main 六段式。** `umask(022)` 定权限基线（`:653`）→ `load_default_options`（`:657`，dkms 默认 TRUE `:140`）→ **PCI 扫描先于命令行解析**（`pci_device_scan`，`:664`）→ `log_init`（`:672`）→ `ui_init`（`:680`）→ 五分支派发：`report_driver_information`（`:720`）/`sanity`（`:726`）/`uninstall_existing_driver`（`:732`）/`add_this_kernel`（`:739`）/`install_from_cwd`（`:745`）。成功后 `suggest_reboot`（`:749`）。

**2) UI 抽象=函数指针表。** `InstallerUI` 结构（`nvidia-installer-ui.h:39`）定义 detect/init/message/yes_no/status 等 20 个回调；全局指针 `__ui`（`user-interface.c:55`）是唯一入口，`user-interface.h:36` 起的 `ui_message`/`ui_yes_no` 全是薄转发。

**3) ncurses .so 内嵌。** `ui_init`（`user-interface.c:116`）的 `ui_list[]`（`:128-140`）每项携带 `_binary_nvidia_installer_ncurses_ui_so_start/_end` 符号——构建期 Makefile 用 `ld -r -z noexecstack --format=binary` 把 `nvidia-installer-ncurses-ui.so`（`Makefile:63`）直接链成 `.o`（规则 `utils.mk:610`），objcopy 把节改名 `.rodata`。运行时 `extract_user_interface`（`user-interface.c:683`）`mkstemp`（`:699`）写出临时文件再 `dlopen`（`:166`）、`dlsym("ui_dispatch_table")`（`:169`）。ncurses 侧导出同名表（`ncurses-ui.c:245`），其 `detect` 就是 `initscr()` 试探（`nv_ncurses_detect`，`:281`，`:285`）。

**4) 兜底链。** 全部失败 → 内建 `stream_ui_dispatch_table`（`user-interface.c:190`；表体 `stream-ui.c:59`）；`--silent` 直接跳过 dlopen 循环（`:146`）。

## 三、外部连接

- 选项契约：`option_table.h:126` 的 `__options[]` 同时喂 `--help`（`print_options`，`nvidia-installer.c:84`）与 manpage 生成器（`gen-manpage-opts.c:11`）；`--ui` 选项定义在 `option_table.h:393`。
- 依赖方向：UI 层不回调安装逻辑，只通过 `Options*` 读状态；`FormatTextRows`（`user-interface.h`）注入文本折行器，避免两个 UI 各写一份。
- 被依赖：`misc.c`/`install-from-cwd.c` 全部经 `ui_*` 前缀函数说话，从不直接碰 `__ui`（源码级强约束）。

## 四、数据流

命令行 → Options 结构 → `ui_init` 选实现 → 后续所有 `ui_log/ui_error/ui_status_update` 经 `__ui->` 单点分发到具体实现；ncurses 版把状态条/对话框画在 curses 窗口，stream 版打印到 stdout。**注意 `ui_init` 之前**产生的消息先进 `ui_deferred_messages` 缓冲（`user-interface.c:296` 附近），UI 就绪后回放——避免早期消息丢失。

## 五、设计决策

- **为什么内嵌而不是链接**：源码注释写明双保险动机——UI 库与主程序解耦可防 UI 库依赖炸掉主程序，但不落地安装又避免"找不到/找错"库（`user-interface.c:666-681` 注释；`README:28` 同旨）。
- **ncurses6/ncursesw6 是编译期条件成员**：仅当构建环境给出对应 CFLAGS 才编进（`Makefile:111-112` 宏、`user-interface.c:128` 的 `#if`），所以"UI 优先级表"是构建产物相关的。
- PCI 扫描放解析前：让 `--sanity` 等所有模式都能拿到 GPU 探测结果，代价是纯查信息模式也会碰 PCI。

## 六、新人提示

1. 改 UI 行为先看 `nvidia-installer-ui.h` 契约，再选实现文件；别绕过 `ui_*` 直接 printf。
2. 调 UI 选择问题时看 `/var/log/nvidia-installer.log`：`ui_init` 每次尝试/失败都 `log_printf`（`user-interface.c:171-180`）。
3. `--ui=none` 不是独立实现，是"匹配不到→stream"的效果；`--silent` 才是真的静默开关。
4. 手册页改动只需改 `option_table.h`，重建自动同步（`Makefile:314` m4 链）。

---
字数 2615（非空白字符）/锚 22
