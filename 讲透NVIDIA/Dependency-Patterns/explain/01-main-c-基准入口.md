# 01 · main.c——基准入口：一个 include 引出的依赖盲区

## 角色定位

main.c 是整个基准的"消费者终端"：129 行的单 main 函数把 5 个模块的公开 API 全部点亮一遍。它的价值不在逻辑（全是 printf 演示），而在它站的位置——四个模块库（libmathutils/libstrutils/libio/libutils）在此汇合链接成 demo 可执行文件，构建系统的全部依赖花样最终都要兑现在这份文件的 14 个 include 与调用上。

## 内部结构

文件骨架极简：L6-8 三个系统头（stdio/stdlib/string），L11-14 四个项目头，L16 起 `int main(void)`。main 体内四段演示：

- **数学段 L20-30**：add/multiply/power/factorial/gcd/is_prime/fibonacci/divide 八连调——这 8 个函数全部来自**盘上不存在**的 mathutils/mathutils.h（L11）。
- **字符串段 L32-52**：str_copy/str_concat 拼出 "Hello World"、str_reverse 原地反转、str_count/str_is_numeric/str_is_alpha 判定。
- **IO 段 L54-78**：file_write_text 写 test.txt → file_read_text 回读 → file_size/file_exists → file_delete 清理，再 print_line/print_number/print_float 控制台三连。
- **utils 段 L80-126**：数组（array_print/array_sort/array_find）、时间（get_current_time/get_timestamp）、随机（L101 `random_seed(42)` 定种子保证可复现，random_int/random_double/random_string）、校验四件套、转换四件套；L119-125 的 int_to_string/double_to_string 返回堆内存，紧跟 safe_free 释放——这是 utils 模块内跨文件契约（转换函数分配、safe_free 回收）的标准用法示范。

## 外部连接

- include 边三条落在静态头上：io/io.h、strutils/strutils.h、utils/utils.h；第四条 `"mathutils/mathutils.h"`（main.c:11）指向构建期生成物。
- 根 Makefile:36-38 以 `-lmathutils -lstrutils -lio -lutils -L.` 链接；BUILD:7-13 的 cc_binary deps 列同样的四个 `//module:target`。
- protocol 模块与 main.c **零连接**——BUILD:4-5 注释明说 "protocol is not used in main.c directly"，它是纯独立构建目标。

## 数据流

一次 `make run`（Makefile:62-64）：递归建 4 模块 .so → 拷回根目录 → main.c 预处理（此刻 mathutils.h 已由 perl 生成器产出）→ main.i → main.o → 链接 demo → 执行输出四段演示到 stdout。main.c 是全仓唯一同时消费"静态头"与"生成头"的文件，预处理成功与否就是两套构建系统的集成测试。

## 设计决策

1. **为什么 include 一个不存在的头**：这不是疏忽而是考题。静态分析器扫描盘上文件必然在 main.c:11 扑空；Make 靠生成规则先跑 perl（mathutils/Makefile:15-19）、Bazel 靠 mathutils_rules.bzl:143 把生成头 cp 到 bin/<pkg>/ 再把 bin 目录挂进 include 路径——两种解法都在为这一行买单。
2. **random_seed(42) 定死种子**：让 demo 输出可复现，方便作为构建产物的行为回归参照。
3. **不链接 protocol**：协议模块的模式 5 挑战留给构建系统独立解决（`make -C protocol` 或 `//protocol:protocol`），不把最难的依赖形态混进主链。

## 新人提示

读这个文件的正确姿势是把它当"依赖清单"读：L11-14 四行 include 分别对应模式 3/1/4/2 四种依赖形态，main 的四段演示顺序就是依赖难度升序。想看 main.c:11 的头长什么样，跑 `perl mathutils/gen_mathutils_h.pl`（在 mathutils/ 目录下）即可在本地生成——或者直接读 gen_mathutils_h.pl:14-31 的 heredoc 去 q 后的内容。注意生成的 mathutils.c 里有 subtract()，main.c 没调用它（生成器 10 函数、演示 8 个），别在 main 里找全。

（01/04 · 锚 18 处）
