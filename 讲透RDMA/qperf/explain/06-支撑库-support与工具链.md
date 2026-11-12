# 06 支撑库 support.c 与文档工具链

## 一、角色定位

support.c（673 行）是三条传输线共享的地基：序列化编解码（enc/dec 家族）、控制通道消息收发与超时（send_mesg/recv_mesg）、统一错误报告与**跨机错误传播**（error/urgent 的 TCP 带外数据协议）、若干安全包装（qmalloc/qasprintf）。工具链则是仓库里超前的"单一数据源双生成"设计：一份 src/help.txt 同时生成 C 数组 help.c（mkhelp，运行时 --help 用）与 man 页 qperf.1（mkman），外加 autotools 引导与 RPM 模板。代码与文档链合起来看，才能理解这个仓库为何能稳定维护十余年。

## 二、内部结构

### support.c

**编解码层**（support.c:86-172）是纯粹的小端序手工序列化：`enc_int(l, n)` 逐字节右移写出（support.c:128-135），`dec_int(n)` 先跳 n 再反向组装（support.c:141-150），enc_str/dec_str 原样 memcpy。EncodePtr/DecodePtr 两个静态游标（support.c:79-80）由 enc_init/dec_init 锚定到缓冲起点。这层刻意绕开 struct 直传——两端字长/对齐不同也不怕，REQ/STAT/NODE/CONF 四种结构全靠它（qperf.c:2634-2701 逐字段调用）。encode_uint32/decode_uint32（support.c:156-172）是"单值自锚定"糖衣，端口交换场景到处在用。

**控制通道收发**：send_mesg/recv_mesg（support.c:275-293）都落到 send_recv_mesg（support.c:300-362）——select 多路等待 + read/write 函数指针分发 + `Req.timeout` 秒超时（etime 由 get_seconds gettimeofday 算，support.c:322-335），超时/对端关闭各给明确文案。synchronize/send_sync/recv_sync（support.c:234-269）在其上加"互发同一字符串并 memcmp 校验"的会合点原语，串内容即日志标签。

**错误传播协议**是 support.c 最精彩的设计（support.c:536-568 + 418-487）：

- `error(actions, fmt, ...)`（support.c:536-568）：BUG 位加 internal error 前缀、SYS 位拼 errno、RET 位返回不退出；致命错误且 RemoteFD≥0 时，**先 send 一字节 '?' 的 MSG_OOB 带外信号**，再跟带内错误正文、shutdown 写半边，然后在 ERROR_TIMEOUT=3 秒内排空对端回执才 die——保证错误信息送达对端。
- `urgent()`（support.c:418-487，SIGURG 处理器）：recv(MSG_OOB) 取信号字节——'.' 表示对端测试完成，本地 set_finished 对称收工；其他则进排错模式：sockatmark 吞带内数据直到标记点，再读完整错误文本写 stderr（server 非 debug 模式直接 die），3 秒超时兜底。
- 这套协议让"client 死于 verbs 错误、server 第一时间打印对端死因"成为默认行为，是双机调试体验的支柱。

**其余**：qmalloc（support.c:178-186）失败即退；qasprintf（support.c:193-206）包 vasprintf；touch_data（support.c:212-228）volatile 64 位逐字读——access_recv 选项的落地；getaddrinfo_port（support.c:382-395）数字端口转字符串再查；setsockopt_one（support.c:402-410）；timeout_set/end（support.c:585-610）临时改 SIGALRM 处理器再复原。注意 qperf.h:257 声明的 `check_remote_error` 全仓无定义无调用——死原型三连的第三个。

### 工具链

**mkhelp**（Perl，113 行）：读 help.txt，按缩进语法解析——顶格行是条目名，缩进行是正文；条目名可挂 `+RDMA`/`-RDMA` 修饰符（mkhelp L84-88），与命令行 defs 集合（构建时 `./mkhelp RDMA` 或裸跑，Makefile.am L27-32）比对决定该节去留；正文行做 C 转义、拼 `\n`、68 列折行（L72-77），产出 `char *Usage[] = {...}` 的 help.c，qperf.c:865-873 的 --help 按 category 检索。**mkman**（Perl，198 行）：make_dict（L154-162）把 help.txt 切成"顶格键→缩进值"字典；do_synopsis/do_options/do_tests/do_examples 四个渲染器把同一份数据转成 roff——do_options（L72-94）解析 `-x, --long` 头部生成 `.TP` 加粗条目，do_tests（L54-67）硬编码取 `"Tests +RDMA"` 节（L57），man 页因此**固定含 RDMA 测试**；help_date（L143-147）取 help.txt mtime 当 man 日期。

**构建链**：configure.ac 仅 11 行——AC_INIT（版本 0.4.10）、两次 AC_CHECK_LIB 探测 ibverbs（rdma/xrc 两级）、AM_CONDITIONAL 导出 RDMA/HAS_XRC、从 qperf.spec.in 生成 qperf.spec。autogen.sh 先 touch NEWS/README/ChangeLog（automake --foreign 要求）再 aclocal/automake/autoconf；cleanup 反向删除全部生成物，对 qperf.spec 有三条"疑似过期即删"判据（BuildRequires 检查、qperf.spec.in/configure.in 新旧比较）。

## 三、外部连接

- **support.c 被所有 .c 消费**：qperf.c 的 error(BUG) 自检、三条传输线的 send_mesg/recv_mesg/qmalloc/touch_data。它是唯一不含领域逻辑的文件。
- **help.txt 是文档单一数据源**：一处修改，`make` 自动经 mkhelp/mkman 同步 help.c 与 qperf.1（Makefile.am L25-32）；--help 的 categories/tests/options/examples 与 man 页 SECTION 完全同源。
- **qperf.spec.in 双形态**：`@RDMA_TRUE@BuildRequires`（spec.in L11-12）由 configure 按探测结果展开成两个 spec 形态，License 字段写 "BSD 3-Clause, GPL v2"（L5）——注意仓库 COPYING 文件只含 GPLv2 全文，而每个源码头的双许可声明与 spec 都承认 OpenIB BSD 许可，COPYING 是不完整的单许可文本。
- **autogen/cleanup 配对**：README 构建四步（cleanup→autogen→configure→make）即"清场→引导→配置→编译"；cleanup 里 `configure.in -nt qperf.spec` 判定用旧文件名而仓库实际是 configure.ac——条件恒不触发，spec 过期保护在这份代码树上已失效。

## 四、数据流

文档链的自动生成流：

```
src/help.txt（人编辑的唯一文档源）
   ├──make→ ./mkhelp [RDMA] ──→ src/help.c: char *Usage[]{...}
   │                              └→ do_option help 分支运行时打印
   └──make→ ./mkman ──→ src/qperf.1（日期取 help.txt mtime）
                            └→ 安装到 %{_mandir}/man1

configure.ac --探测 ibverbs--> RDMA/HAS_XRC 变量
   ├──→ Makefile.am: 源文件清单（rdma.c 进出）+ -DRDMA/-DHAS_XRC
   ├──→ src/Makefile.am: mkhelp 是否带 RDMA 参数
   └──→ qperf.spec: @RDMA_TRUE@BuildRequires 展开
```

运行时错误传播流（一次远端 verbs 崩溃）：server 端 ibv_post_send 失败→error(SYS,...)→send '?' MSG_OOB→写错误正文→shutdown→排空→die；client 端 SIGURG→urgent()→recv(MSG_OOB) 取非 '.' 字节→sockatmark 吞带内→打印 "server: ...failed"→die。用户在 client 一侧看到 server 的 errno。

## 五、设计决策

- **手工小端序列化而非 struct send**：REQ 字段全是 uint32/uint16 定宽 + enc 逐字段写（qperf.h:148-151 注释冻结前四字段），跨版本跨架构握手成本低；代价是每加字段要同步改 enc/dec 两处并升 ver_min。
- **OOB 字节做信号信道**：'.' 与 '?' 两个单字节协议跑在 TCP 带外通道上，与带内数据流零冲突；比再开一条连接便宜，比塞进带内流简单。SIGURG+F_SETOWN+FIONBIO 三件套（qperf.c:1552-1561）是为它铺的路。
- **文档代码同构**：help.txt 的缩进语法既是 --help 的分类树又是 man 的节结构，+RDMA 修饰符让文档能力矩阵与编译能力矩阵共享一个真相源——十余年后 reroll 的 qperf 仍沿用此机制。
- **cleanup 删 qperf.spec 的启发式**：OFED 打包脚本依赖仓内 qperf.spec 存在，故不能全删；三条"不正确就删"判据是让 OFED 重新生成的软同步。启发式依赖文件名，configure.in→configure.ac 改名后即失效——脚本与文件名漂移的活教训。
- **timeout_set 临时换 SIGALRM 处理器**（support.c:585-598）：复用 itimer 不另设计时器，用完即还原，避免与测试计时器打架；先清零再设新值防旧计时器残留。

## 六、新人提示

- 改 help.txt 后无需手改 help.c/qperf.1——它们是构建产物不在仓，`make` 自动再生成；直接编辑产物会被覆盖。
- 加新选项只需三处：qperf.c 的 Options 表加条目、help.txt 的 Options 节加描述（mkman 自动进 man）、如需参数系统则 PAR_INDEX/ParInfo/ParName 三表同步（02 篇清单）。
- 排查双机测试"对端莫名退出"：先看本地 stderr 有没有 "server: xxx" 前缀——那就是 OOB 协议送来的对端 error 原文，顺着它去对端查才是正路。
- 构建前先 ./cleanup 清残留（README 明言 make clean 清不干净）；源码 0.4.11 与 configure.ac 0.4.10 的漂移意味着 rpm 包名是 0.4.10 而 `qperf -V` 报 0.4.11——发包前按 README"Changing version"清单四处同步（注意文中写的 configure.in 是旧名）。
