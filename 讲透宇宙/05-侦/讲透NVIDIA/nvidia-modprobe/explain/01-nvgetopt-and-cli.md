# 01 · nvgetopt 自研解析器与 CLI 主流程

## 一、角色定位

`common-utils/nvgetopt.c`（490 行）是 NVIDIA 自研的 `getopt_long()` 替代品，文件头自陈动机："portable getopt_long() replacement; removes the need for the stupid optstring argument"（`common-utils/nvgetopt.c:23-24`）。它被 nvidia-xconfig/nvidia-settings/nvidia-installer 与本仓共用（`common-utils/src.mk:1`），统一了整个 NVIDIA 用户态工具链的命令行语义：单双横线等价、`--no-` 前缀禁用、`--help` 自动排版。本仓 CLI（`nvidia-modprobe.c` 289 行）是它的最小消费者：一张 9 项的选项表（`option-table.h:19`）加一个 switch 循环。

## 二、内部结构

解析是**单函数五级匹配状态机**（`common-utils/nvgetopt.c:37`）：①先拆 `=`（`:91`）与 `--` 终止符（`:105`）；②长选项匹配，对 IS_BOOLEAN/ALLOW_DISABLE 项剥 `no-` 前缀取反（`:128-138`）；③单字符短选项（`:110`）；④聚簇短选项 `-abc`（`:153-206`，带参项禁止入簇，`:180`，且**原地改写 argv** 逐字符左移 `:187-192`、回退索引重解析 `:199`）；⑤贴身整数 `-c0`（`:213-241`，仅对 INTEGER_ARGUMENT 项）。flag 体系在 `common-utils/nvgetopt.h:46-122`：IS_BOOLEAN/STRING/INTEGER/DOUBLE_ARGUMENT、ALLOW_DISABLE、ARGUMENT_IS_OPTIONAL、HELP_ALWAYS、IS_DEPRECATED。选项表结构体五字段含 `arg_name`/`description`（`common-utils/nvgetopt.h:135-141`）——后两字段解析器本身不用，专供 help 与 manpage 生成。

## 三、外部连接

三个消费者共享同一张表：CLI switch（`nvidia-modprobe.c:108` 调 `nvgetopt`）；`--help` 排版器 `nvgetopt_print_help`（`common-utils/nvgetopt.c:405`，include_mask 过滤 `:424`，短选项仅当 val 是可打印字母才印 `:458`，布尔/可禁用项自动追加 `--no-` 变体 `:472-478`）；构建期 man 生成器 `gen-manpage-opts-helper.c`（`common-utils/gen-manpage-opts-helper.c:51` 印 `.TP/.BI`）。description 里的 `&`/`^` 是 man 专用标记（斜体/粗体切换，`common-utils/gen-manpage-opts-helper.c:97-98`），终端 help 路径由 `cook_description` 剥掉（`common-utils/nvgetopt.c:392`）——一份文案两个渲染目标。

## 四、数据流

以 `nvidia-modprobe -c0 --nvlink -f /proc/driver/nvidia/capabilities` 为例：`-c0` 命中第⑤级贴身整数路径（`:219` strtol 判定、`:314` base 0 解析进 intval）；`--nvlink` 命中长选项精确匹配返回 `'l'`；`-f` 走"下一个 argv 取参"（`:276-304`）。CLI 侧把结果收进 `minors[64]`（`nvidia-modprobe.c:91`，超限即报错退出 `:134`）与 `cap_files[256]`（`:92`/`:157`），随后进入五互斥分支分发（`:171-258`）。

## 五、设计决策

- **静态 `argv_index` 保存游标**（`:53`）：函数签名与 getopt 一致却无需全局 optind，代价是非重入、同进程二次解析需自担后果——对一次性 CLI 恰好够用。
- **strtol base 0**（`:314`）：`-c 0x10` 会按十六进制解析——特性而非笔误，但读代码时容易误判。
- **失败返回 0 而非 '?'**：错误自打印到 stderr（`:246`），返回 0 即"无法继续"；因此选项表中 val 绝不能为 0。
- **本仓选项表全部未用 IS_BOOLEAN/ALLOW_DISABLE**（`option-table.h:21-81`）：所有开关都是"出现即为真"，`--no-modeset` 实际报 unrecognized——help 里也不会印 no- 变体。
- **聚簇路径改写调用方 argv**（`:187-192`）：省掉索引簿记，但要求 argv 可写。

## 六、新人提示

改用户可见选项 = 只改 `option-table.h`，man 与 help 自动同步，别忘了 re-run `make`（man 链在 `Makefile:155`）。排查"选项不生效"先看两级：表里 flags 是否带对 argument 类型（`:276` 的取参分支只在 HAS_ARGUMENT 时走）；短选项是否撞了既有 val（`:110` 短选项按单字符匹配）。阅读入口从 `common-utils/nvgetopt.h:145-178` 的契约注释开始，比直接进 .c 高效。

---
*字数 2381（非空白字符）/唯一全路径锚 15（另含跟随式段锚，均经 `sed -n` 核实，机器终验 0 坏）*
