# 10 · Makefile 与构建配置：23 行背后的链接考古

## ① 角色定位

Makefile 是全仓唯一的构建入口（图谱 `config:Makefile` 节点 + `step:Makefile:all/debug/clean` 三个子目标，位于构建层 L01，tour 第 1 步）。23 行的教科书式小 Makefile：七个源文件一个产物，两条编译路径（release/debug），一条清理规则。但它也是本仓**信息密度最高的考古现场**——git 历史显示 HEAD 的 Makefile 与作者最初发布的版本差一行，而这一行之差决定了"能不能链接成功"；同时它还藏着一个从初版继承至今的冗余链接项。本篇把构建配置讲透，顺带完成这段考古。

## ② 内部结构

逐块拆解：

- **变量区（Makefile:1-9）**：`CC=gcc`；`CFLAGS=-Wall -Werror -O2`（**-Werror 把一切警告当错误**，全仓为此保持了零警告纪律——例如 ib.c:76 的 `char *buf` 形参与 client.c:131 的 `(char*)wc[i].wr_id` 强转都写得小心翼翼）；`INCLUDES=`（空，所有头都在仓内）；`LDFLAGS=-libverbs`；`LIBS=-pthread -lrdmacm`；`SRCS` 七文件按 main→client→config→ib→server→setup_ib→sock 列举（Makefile:7）；`OBJS=$(SRCS:.c=.o)` 后缀替换；`PROG=rdma-tutorial`。
- **三目标**：`all: $(PROG)`（Makefile:11，默认目标）；`debug`（Makefile:13-14）——用 **target-specific 变量**重写 `CFLAGS=-Wall -Werror -g -DDEBUG`，-DDEBUG 正是 debug.h:33-41 条件编译的开关（第 9 篇②）；`clean`（Makefile:22-23）删 *.o/*~/产物。
- **规则**：`.c.o` 老式后缀规则（Makefile:16-17）逐文件编译；链接规则（Makefile:19-20）`$(CC) $(CFLAGS) -o $(PROG) $(OBJS) $(LDFLAGS) $(LIBS)`，目标文件在前、库在后的顺序满足静态符号解析。

## ③ 外部连接

**三个链接项与代码的真实依赖关系**（grep 实证）：

| 链接项 | 真实消费 | 判定 |
|---|---|---|
| -libverbs | ibv_* 全家（ib.c/setup_ib.c 约 20 个 API）+ 头文件 infiniband/verbs.h（ib.h:8，系统包 libibverbs-dev 提供） | 必需 |
| -pthread | pthread_create/join/attr（client.c:187/194、server.c:183/189）、pthread_setaffinity_np（client.c:48，GNU 扩展，故 client.c:1/server.c:1/sock.c:1 定义 _GNU_SOURCE）、CPU_ZERO/CPU_SET | 必需 |
| -lrdmacm | **全仓 .c/.h 零调用**——grep `rdma_` 前缀函数无任何命中 | **冗余** |

-lrdmacm 的来历值得写一笔：作者手写 TCP 带外交换（第 7 篇⑤①）替代了 rdma_cm，但链接项留在了 Makefile 里。它无害（librdmacm 装了就能链上），却会**误导读者以为本仓用 rdma_cm**——README 的 Wiki 链接也从未解释这一点。这正是 onboard 坑 8 的实证细节。

**git 考古（本篇核心发现）**：`git log` 显示 HEAD 之前的 Makefile 曾有一次外部贡献修复——commit 9c7a662（2019-02-18，gareging，经 PR #7 于 be4d713 合入），提交信息就一行 "Update Makefile"，diff 只有一处：`LDFLAGS=`（空）→ `LDFLAGS=-libverbs`。**作者初版的 Makefile 没有链接 libverbs**，按原版构建会在链接期报 ibv_get_device_list 等符号未定义。也就是说：今天能一键 make 通过的这份 Makefile，是社区用户修过的版本；而 -lrdmacm 这个真正的冗余项反而从初版一路无人动。读开源教程仓的"当前状态"时，git log -p 是还原"承诺与修复史"的必备工具（第 11 篇将继续用这把铲子）。

## ④ 数据流

`make` 的一次完整数据流：make 读入 → 默认目标 all → 依赖 $(PROG) → PROG 依赖 $(OBJS) 七个 .o → 对每个 .o 查 `.c.o` 后缀规则 → 找到同名 .c 执行 `gcc -Wall -Werror -O2 -c -o x.o x.c` → 七个 .o 齐后执行链接行 → 产出 rdma-tutorial。`make debug` 沿同一条依赖链，仅 CFLAGS 在 debug 目标的作用域内被替换（-g -DDEBUG 替掉 -O2），源码零改动获得带调试输出（debug.h 的 log 双通道）+ 带调试符号两个能力。

**两个 make 语义的坑**（都源于"make 只看时间戳，不看命令行变化"）：

1. **all↔debug 切换不触发重编**：先 `make` 再 `make debug`，七个 .o 的时间戳新于 .c，make 认为无需重编——得到的"debug 版"实际是 -O2 目标文件 + -g 链接的**混合产物**，DEBUG 宏根本没定义，debug 日志一行都不会出现。正确用法是 `make clean && make debug`（README:14 只写了 `make debug`，没提醒 clean，初学者极易踩）。
2. **头文件依赖缺失**：`.c.o` 后缀规则的依赖只有 .c 文件本身——改 debug.h 或 ib.h 后 `make` 不会重编任何 .o，必须 clean。工业 Makefile 用 `gcc -MMD` 自动生成 .d 依赖文件解决，本仓 23 行的体量没做，属于教学仓可接受的简化，但**修改头文件后忘记 clean 是"改了没生效"假象的头号来源**。

另有两处小瑕疵：all/debug/clean 均为 phony 目标但未声明 `.PHONY`（若仓内碰巧出现同名文件 clean，make 行为会异常）；LDFLAGS 里放 -l 开关、LIBS 里也放，两变量语义划分（路径 vs 库）没有严格遵循惯例，无实害但不是模板级写法。

## ⑤ 设计决策

**① 为什么用 target-specific 变量做 debug**：一条规则 `debug: CFLAGS=...` 让 debug 与 release 共享全部依赖逻辑，只换编译旗标——对比常见的新手写法（复制一条完整规则），这里是最小改动点。代价是上文的时间戳坑，属于 make 工具语义的原生缺陷而非写法错误。

**② -Werror 在教学仓的价值**：教程代码会被无数初学者改着玩，-Werror 强制"改动也保持零警告"，把一类低级错误（隐式转换、未用变量）挡在编译期。配合 -O2，本仓的默认构建已经接近发布质量——而 -g -DDEBUG 的 debug 路径保留了可调试性，两条路径覆盖教学与排错两种场景。

**③ 时代兼容性**：README:8-9 标称 gcc-4.4 与 Mellanox OFED 3.3（2014 年语境）。代码使用的 designated initializer、`__attribute__((packed))`、_GNU_SOURCE 扩展在 gcc 4.4 全部可用；今天只需 libibverbs-dev + librdmacm-dev（后者仅因 Makefile 的冗余项）即可在现代发行版编译，无版本锁死——这与第 11 篇将讨论的"README 时代印记"形成对照：构建系统反而比文档更耐老。

## ⑥ 新人提示

上手顺序：`make` 出优化版跑基准，`make clean && make debug` 出调试版看 log 宏双通道输出（对比 server[0].log 与 stderr 的差异，验证第 9 篇②的双通道语义）。三个动手实验：① 验证 -lrdmacm 冗余——`sed 's/ -lrdmacm//' Makefile` 后 make 依然成功（在装有 libibverbs 的机器上）；② 复现混合产物坑——`make && make debug` 后 grep 不到 debug 输出，再 clean 重编即现；③ 把 .c.o 后缀规则改成模式规则 `%.o: %.c` + 加 `%.o: %.c $(wildcard *.h)` 的粗暴头依赖，感受增量编译的正确性变化。若要给本仓加 example 演进分支的构建（第 11 篇④的 Example 1/2 系列），SRCS 清单需按各 commit 的实际文件增删——HEAD 的七文件清单只对 Example 4 成立，这也是"Makefile 与代码同演进"的隐性约束。
