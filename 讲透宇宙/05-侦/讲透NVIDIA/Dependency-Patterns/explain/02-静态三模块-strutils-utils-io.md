# 02 · 静态三模块：strutils / utils / io——手写基准与半生成形态

## 角色定位

三个模块构成基准的"静态半壁"：strutils（模式 1，单源单头）与 utils（模式 2，双源共享头）是纯手写 C，是依赖可从 #include 扫描推断的正例；io（模式 4）半只脚踩进生成世界——头是静态的，实现文件却由 python 生成且名字不可预测。三者合起来给出"从完全可推断到文件名失控"的中间梯度。

## 内部结构

**strutils/strutils.c**（116 行 14 函数）：长度/比较/复制/拼接/反转/查找/替换/判定/复制释放，全是对 libc 的薄封装加 NULL 防护。L12 str_length 手写计数（不用 strlen）、L101 str_duplicate 手写 strdup（malloc+strcpy，规避 POSIX 依赖）、L39 str_reverse 原地双指针交换、L112 str_free 与 str_duplicate 配对。头文件 strutils.h 声明**同样 14 个**函数（L12-33），声明与实现一一对应；但 include guard 是 `STRING_H`（strutils.h:6-7）而非 STRUTILS_H——改名遗留，见"设计决策"。

**utils/ 双文件**：memory.c 153 行 16 函数分四组——L15/24/33 三个 safe_* 内存封装（失败即 fprintf+exit(1)）、L49-99 数组操作五件套（array_sort L75 是 14 行双循环排序）、L102-118 时间三件、L121-152 随机四件。validation.c 89 行 8 函数——L13/26/38/61 校验四件套（is_valid_ip L38 最长，手写 IPv4 四段 0-255 检查）、L69/74 薄转换、L79/85 int_to_string/double_to_string 调 safe_malloc 分配返回缓冲。

**io/io.h**（38 行）：file/text/binary/dir/console 五组 20 个声明，纯头无实现——实现体在生成的 io_impl_*.c 里（不入库）。

## 外部连接

- utils.h 是 memory.c:6 与 validation.c:6 共同 include 的唯一项目头（模式 2 的全部内容）。
- validation.c:80/86 两处调用 memory.c 的 safe_malloc——utils 模块内唯一真实的跨文件函数调用（main.c:121/125 用 safe_free 与之呼应）。
- strutils.c 与 io.h 的 include 面貌截然不同：strutils.c:6-10 五个 include 全是系统头（连自家的 strutils.h 都不引）；生成的 io_impl_*.c 每个第一行都是 `#include "io.h"`（generate_io.py 模板 L17/68/110/138/177）。
- 构建侧：strutils/BUILD、utils/BUILD 都用 auto_cc_library+glob；io/BUILD 是两步（generate_io_srcs → io_library）。

## 数据流

三模块各自的 .c → .i → .o → .so 流水线完全同构（各自 Makefile 均 29-37 行）。差异在"文件清单从哪来"：strutils/utils 的 SOURCES 手写死；io/Makefile:21-22 的 GENERATED_SOURCES 靠 `$(shell python3 …; echo io_impl/*.c)` 现跑生成器拿清单——这就是模式 4 在 Make 侧的全部代价：make 解析期执行副作用。

## 设计决策

1. **"strutils.c 不 include 自头"其实是改名事故**：README.md:17 明说该模块 `renamed from string`（原目录 string/、原头 string.h）。三个化石互证：strutils.c:6 的引号 `#include "string.h"` 原本是引号包含**自家头**，目录改名后头变成 strutils.h 这行没改，引号搜不到同名项目文件才 fallback 到系统 string.h；strutils.h:6-7 的 guard `STRING_H`（而非 STRUTILS_H）是旧头名遗留；正因源码不引自头，strutils/Makefile:25 只能手写 `strutils.i: strutils.c strutils.h` 依赖。Bazel 侧 auto_cc_library 靠 scan_includes.py:18-26 扫描引号 include，对 strutils.c 会得到**空依赖**（"string.h" 的 basename 不在输入列表），编译照样过——两种构建系统在同一个改名事故面前给出了两种侥幸。
2. **薄封装+NULL 防护风格**：str_compare 在 NULL 时返回 -1 而非崩溃，safe_* 家族失败即退出——演示代码的防御性写法，不是生产级错误处理。
3. **io 五组拆分**：file/text/binary/dir/console 五个模板函数彼此独立（generate_io.py:16-217），让"一个生成器吐多个实现文件"的模式可以被逐组检视。

## 新人提示

三个坑别踩：① strutils.c:6 的 `#include "string.h"` 是 string/→strutils/ 改名残留（原本引号包含自家头，见设计决策 1）——如今引号搜不到项目文件落到系统头，若项目里真出现 string.h 会遮蔽系统头；scan_includes.py:19 只认引号 include，这行会被记为"依赖 string.h"再因 basename 不在输入列表而落空；② strutils.c:24-27 用 strcasecmp 却没 include <strings.h>，-Wall 下隐式声明警告是预期内的；③ 别按头名猜 guard：strutils.h:6 的 `STRING_H` 若与 glibc string.h 的 `_STRING_H` 撞名会静默丢失一份声明（glibc 带下划线前缀所以暂无碰撞），这类"改名仓的 guard 化石"是真实项目里的经典隐患。

（02/04 · 锚 22 处）
