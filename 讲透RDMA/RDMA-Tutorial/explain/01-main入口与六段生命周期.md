# 01 · main 入口与六段生命周期（main.c）

## ① 角色定位

main.c 是全仓唯一的进程入口，共 73 行（main.c:1-73），角色是"编排器"：它自己不实现任何 RDMA 功能，只按固定顺序把配置解析、日志环境、IB 资源创建、角色工作负载四块拼装起来，并保证无论成败都流经同一条清理路径。知识图谱把它单独放在"程序入口与生命周期骨架"层（13 层中的第 2 层，tour 第 2 步）——全仓其余 6 个 .c 文件都能挂到它调用的某一段上，读代码从 main 开始是最短路径。

一个关键的定位事实：server 与 client 跑的是**同一个二进制** rdma-tutorial（Makefile:9 产物唯一），角色在配置解析阶段由本机 hostname 推断（config.c:92 的 get_rank），main.c:34-38 只是消费这个判定。"同一份代码、按配置分身"是理解本仓的第一把钥匙——没有任何 `--server` 之类的命令行开关，换角色靠换机器。

## ② 内部结构

main 函数体（main.c:15-45）是标准的六段生命周期：

1. **argc 校验**（main.c:19-22）：参数不是 3 个就打印 Usage 并 `return 0`——注意错误路径返回 0 而非非零值，自动化脚本若只判退出码会漏掉这种失败。
2. **第一段 parse_config_file**（main.c:24-25）+ sock_port 赋值（main.c:26）：解析出节点列表、角色 rank、msg_size、num_concurr_msgs；sock_port 不来自配置文件而是命令行第二参数，事后补进 config_info 全局结构。
3. **第二段 init_env**（main.c:28-29）：按角色与 rank 打开 `server[n].log` / `client[n].log`（main.c:51-55，n 即 rank），写入 LOG_HEADER（main.c:59）与配置快照 print_config_info（main.c:60，定义在 config.c:229）。
4. **第三段 setup_ib**（main.c:31-32）：IB 资源创建 + QP 建连，全仓最重的一段（setup_ib.c:239-340），详见第 04/05 篇。
5. **第四段角色分发**（main.c:34-38）：`config_info.is_server` 为真走 run_server（server.c:166），否则 run_client（client.c:167）——两条工作负载线互斥执行。
6. **第五、六段校验与统一清理**（main.c:39-43）：check 宏失败即跳 error 标签；error 标签无差别执行 close_ib_connection（setup_ib.c:342）+ destroy_env（main.c:67-73）后返回 ret。

文件级全局：main.c:10 定义 `FILE *log_fp = NULL`，经 debug.h:15 的 extern 被全仓日志宏引用，是第 06 篇日志双通道的落点。main.c:12-13 对 init_env/destroy_env 用旧式无原型声明（`int init_env ();`）是 K&R 风格残留，现代编译器靠定义处补全。destroy_env 本体（main.c:67-73）只写 "Run Finished" 头并按非空判 fclose——与 init_env 的 fopen 严格对偶。

## ③ 外部连接

include 面（main.c:3-8）：debug.h（check/log 宏）、config.h（config_info）、ib.h、setup_ib.h、client.h、server.h——除 sock.c/ib.c 外全部模块头都在。调用面覆盖四个模块的顶函数：config.c 的 parse_config_file、setup_ib.c 的 setup_ib 与 close_ib_connection、server.c 的 run_server、client.c 的 run_client。被依赖面几乎为零：main.c 不向其他编译单元提供符号（唯一例外 log_fp，经 debug.h 转手给所有 log_file 宏）。图谱依赖方向为 main→(config/setup_ib/client/server)→(sock/ib/debug) 的无环图，main 是唯一源点，这决定了它"只编不干"的薄身段。

## ④ 数据流

进入 main 的外部数据只有 argv：argv[1]（配置文件路径）流入 config.c 解析器，argv[2]（sock_port）直接写入 config_info（main.c:26）。此后 main 经手的数据实为两个全局结构：**config_info**（config.c:10 定义）在第一阶段填充，被后续所有阶段读取——setup_ib 用它的 num_clients/num_servers 定 QP 数（setup_ib.c:246-250），run_* 用它的 msg_size/num_concurr_msgs 驱动数据面；**ib_res**（setup_ib.c:11 定义）在第三阶段填充，交给第四段的 run_* 直接消费（client.c:24-28 无参直读）。

控制流上，局部变量 ret 贯穿六段：任一 check 失败即 goto error，ret 保留失败码原样返回（main.c:44）；正常路径同样流经 error 标签，此时 ret=0。注意 run_server/run_client 的失败要跨线程传回：工作线程出错时 pthread_exit(-1)（server.c:163），run_* 在 join 处捕获退出状态并置失败标志（server.c:191-199），再经 main.c:39 的 check 跳清理——三层传递链完整闭合。

## ⑤ 设计决策

**① 单出口 + 幂等清理（LCTHW 风格）**：error 标签在成败两条路径都执行（main.c:41-43）。这个设计的成立依赖两个前提：close_ib_connection 对每个句柄全判 NULL（setup_ib.c:346-377），以及 setup_ib 入口先 memset 清零 ib_res（setup_ib.c:244）——部分创建中途失败时，未赋值字段必为 NULL，清理不会乱碰野指针。"正常路径也走 error"初看反直觉，实为消灭重复清理代码的手段。

**② 角色判定前置到配置阶段**：main 不接角色参数，get_rank 在 parse_config_file 尾部自动完成（config.c:190-191）。每个节点跑完全相同的命令、自动找到自己在列表中的位置，这是多机实验脚本最省心的形态。

**③ 日志环境先于 IB 资源**：init_env 排在 setup_ib 之前（main.c:28-31），保证 IB 建连阶段的日志已有落点——顺序换过来，setup_ib 里的 log 调用会写空指针。

**④ 配置快照进日志**：init_env 调 print_config_info（main.c:60）把角色/rank/参数在开跑前定格到日志，事后核对多机实验配置是否一致时，这是第一手证据。

**⑤ 清理对称但有遗漏**：close_ib_connection 逆序销毁 IB 资源，但 main.c:42-43 不调 destroy_config_info（config.c:204 定义后全仓无调用，死代码，详见第 02 篇）——servers/clients 字符串数组随进程退出交给 OS 回收，教程可接受，工程代码不可。

## ⑥ 新人提示

把 main.c 当全仓地图用：六段各对应一组文件，读任何模块前先回 main 找到它的挂载点。运行方式 `./rdma-tutorial config_file sock_port`（main.c:20），server 侧先起；日志落在**当前工作目录**的 server[n].log / client[n].log（main.c:51-55），多节点各自写各自的文件。

三个易忽略点：① Usage 错误返回 0（main.c:21），脚本别只看退出码；② sock_port 是命令行参数而非配置项，sample.config 里找不到它；③ error 标签不是"错误分支"而是公共出口，读代码时把它当函数尾声理解。配合 README.md:18-21 的"4 个示例按 git commit 组织"使用：checkout 历史 commit 可以看到 main.c 逐步长出后四段的过程，是最自然的递进学习路径。改实验参数从 config 文件的 msg_size / num_concurr_msgs 入手，不必动 main。
