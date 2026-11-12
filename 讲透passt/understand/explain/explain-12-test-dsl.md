# explain-12 · test/lib/test：POSIX shell 测试 DSL 的逐行解释器

## 1. 角色定位

passt 的测试套件没有用任何现成框架（pytest/bats 都没有），而是自造了一门**基于 tab 分隔指令的 DSL**：每个测试文件（如 `test/passt/tcp`）是一行行"指令<TAB>参数"，`test/lib/test`（445 行 POSIX shell）就是这门语言的解释器。指令的执行目标是**真实的 tmux 终端面板**——host、guest（qemu 里的 VM）、ns（网络命名空间）、passt 各占一块 pane，`guest	socat ...` 的字面语义就是"把这条命令打进 guest 那块 pane 的 shell 里执行"。这带来一个独特性质：测试跑的就是用户会遇到的完整真实栈（qemu 全系统仿真、真实内核、真实 guest 发行版），而 ./ci 会录屏发布到官网。`test/lib/test` 处于编排链的中层：`test/run`（入口，环境变量与选单）→ lib/setup（各场景的环境生命周期：起 qemu、开 ns、拉 passt）→ **lib/test（逐文件逐行解释指令）** → lib/term（tmux pane/context 原语）→ lib/layout（表格化报告输出）。目录结构对应场景矩阵：passt/pasta/passt_vu/passt_in_ns/two_guests 等功能组 + perf/ 性能组 + distro/ 四发行版 + migrate/ 迁移。

## 2. 内部结构

**`test_one_line()`（`test/lib/test:107-379`）是解释器核心**。预处理三步：剥注释（`%%#*`，`:113`）；处理 `def`...`endef` 块收集（`:115-123`，用 eval 把行攒进 `TEST_ONE_DEF_<名字>` 变量，实现了**用户自定义宏**）；按第一个 tab 切出指令与参数（`:126-127`），参数过 `subs_apply` 做 `__VAR__` 变量替换（`:128`）。然后一个 40 分支的 case：**上下文执行族**（每类目标三件套：同步跑/后台跑/等待）：host/hostb/hostw（`:148-156`）、passt/passtb/passtw（`:163-171`）、guest/guestb/guestw + guest1/guest2 两套（`:180-197, 207-215`）、ns/ns1/ns2 各三件套（`:222-247`）、mon/monb 监视器（`:216-220`）；**中断**：hint/pint 分别向 host/passt pane 发 C-c（`:157-159, 172-174`）。**工具探测**：htools/gtools/g1tools/g2tools/nstools（`:160-162, 198-205, 249-251`）——`which $ARG >/dev/null` 失败就置 `TEST_ONE_skip=1`，整个文件跳过（依赖缺失不算失败）。**输出捕获**：hout/gout/g1out/g2out/pout/nsout/ns1out/ns2out（`:175-178, 252-286`）——跑命令、把 stdout 存进变量表 `TEST_ONE_subs`（键格式 `__名字__`），后续行通过替换使用，这是 DSL 的"赋值语句"。**控制与断言**：`test`（`:139-147`）开新断言块：上一个块的 nok 状态结算（status_test_fail/ok），`check`（`:287-297`）eval 一段 shell 条件当断言、打勾叉；`sleep`/`info`/`set`（`:298-303, 340-342`）。**性能报告族**：th/tr/tl/te/td/bw/lat（`:307-327`）构造结果表格，perf_nok 单独记账（性能回退不算功能失败但在 perf 文件里算）；iperf3s/iperf3k/iperf3/iperf3m 四个 iperf3 助手（`:19-105`，`test_iperf3` 跑吞吐测试并用 jq 抽 `.end.sum_received.bits_per_second` 存变量；`iperf3m` 是迁移变体：客户端先在 cctx 起、睡 time+3 秒、去 cctx2 读结果——对应 guest 迁走后结果文件在新宿主侧）。**demo 族**：say/em/nl/hl/bsp/killp/resize（`:344-365`）——这套 DSL 一鱼两吃，`test/run --demo` 时它就是"打字机演示脚本"（官网视频就是这么录的）。**default 分支即宏调用**（`:366-377`）：未知指令去 `TEST_ONE_DEF_*` 查定义体逐行递归 `test_one_line`。

**`test_one()`（`:383-424`）**：文件级驱动。shellscript 类型的文件直接执行（`:388-392`，smoke 等独立脚本走这条路）；否则统计 `^test\t` 行数当断言数、建 STATEDIR、初始化变量表（`__BASEPATH__`/`__STATESETUP__`/`__STATEDIR__` 三个内置替换键，`:401-405`），逐行 `read -r` 喂给 test_one_line，`TEST_ONE_skip` 置位即 break。收尾：dirclean 清理、skip/perf_nok/nok 三态结算（`:419-423`）。**`test()`（`:428-445`）**：批量入口，cd test 收集参数依次 test_one。

## 3. 外部连接

依赖 lib/term（`pane_or_context_run/_bg/_wait/_output` 四原语——pane 是 tmux 面板，context 是"逻辑位置"抽象：有的目标在 pane 里、有的要 ssh/nsenter 进 context，`pane_or_context_*` 统一两者；`tmux send-keys` 打字进 pane、capture-pane 取输出）；lib/layout（`status_test_ok/fail/skip`、`info_check_*`、`table_*` 系列的终端表格渲染）；lib/perf_report（性能基准落盘与对比）；lib/context、lib/setup（场景装配）；lib/util 的 `list_add_pair`（变量表的链表式追加，纯 POSIX 无数组的技巧）。被依赖：test/run 与 ./ci source 它；test/ 下全部 DSL 测试文件（passt/、pasta/、perf/、migrate/、distro/ 等 30+ 文件）是它的"程序"。

## 4. 数据流

跑 `test/passt/tcp` 的一个断言块（真实文件 `test/passt/tcp:19-24`）：`gtools socat ip jq` → guest pane 里 which 探测，缺则整文件 skip → `test TCP/IPv4: host to guest: big transfer` → 新块开始 → `guestb socat -u TCP4-LISTEN:10001,... OPEN:test_big.bin,...` → 向 guest pane 打字（后台语义靠 shell 立即返回）→ `sleep 1` → `host socat -u OPEN:__BASEPATH__/big.bin TCP4:127.0.0.1:10001` → host pane 执行，数据经 passt 代理流入 guest → `guestw` 等 guest 后台任务收尾 → `guest cmp /root/big.bin test_big.bin` 字节级校验 → 下一个 `test` 行结算本块 pass/fail。整个过程数据真的穿过了 qemu→virtio-net→passt→宿主 TCP 栈。

## 5. 设计决策

**为何不用现成框架**：核心诉求是"命令必须打进真实终端里跑"——passt 的 bug 常在 tty 行为、信号传递、退出码这些层面，tmux pane 保真度最高；同时 demo 与测试共用一套脚本（say/hl 等指令）让官网演示视频零额外成本。**用 tab 做语法分隔符**（`:126-127`）保证参数里的空格原样保留，`__VAR__` 替换是极简但够用的模板机制。**POSIX sh 无数组的约束**逼出 `list_add_pair` 这类链表字符串技巧与 `eval` 收集 def 块（`:118-121` 的 IFS 花招），可读性让步于零依赖。**skip 与 fail 严格分离**（tools 族只 skip）：在四发行版矩阵上跑时，缺包是环境事实不是回归，报告才干净。性能断言（td/bw/lat）与功能断言分开记账同理——吞吐回退和功能坏是不同种类的坏。

## 6. 新人提示

写新测试的模板照抄 `test/passt/tcp`：先 gtools/htools 声明依赖，test 行开块，命令族干活，check 或命令退出码收尾。跑法：`cd test && sudo ./run`（要 root：qemu/KVM/ns 都要权限）；单文件 `sudo ./run passt/tcp`；`DEBUG=1 TRACE=1 PCAP=1` 三开关直接给被测 passt 挂调试参数（run 头部环境变量）。坑五条：指令与参数之间必须是**真 tab**，空格会被当参数的一部分；`pout/gout` 的变量替换发生在"下一行"而不是定义行；后台指令（hostb 等）不检查退出码，收尾必须配 `w` 系列等待；skip 只在 tools 探测后下一次行循环生效，中途手工置位无效；perf 文件别在 CI 慢机器上直接当回归门禁，`td` 的参考值会漂。调试 DSL 本身用 `DEBUG=1`——test_one_line 第一行就把每条指令 info 出来（`:110`）。
