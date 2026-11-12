# 11 构建系统：autotools 全链（configure.ac → Makefile.am → mkhelp/mkman → spec）

## 一、角色定位

qperf 是 2009 年世代的经典 autotools 工程，但它的构建链比标准三件套多两个非常规环节：man 页与 help.c **不是手写文件，而是构建时由两个 Perl 脚本从单源 help.txt 生成**——文档、--help 输出、man 页三者永远同步的秘密全在于此。全链路：autogen.sh → configure.ac（探测 ibverbs/rdmacm，定 RDMA/HAS_XRC 条件宏）→ Makefile.am（按条件裁源文件与 CFLAGS）→ make（拉起 mkhelp/mkman）→ qperf.spec（configure 从 spec.in 替换生成，OFED 打包用）。仓库里还有一个 cleanup 脚本专治"autotools makes such a mess"（cleanup:2 原话）。

## 二、内部结构

**configure.ac 仅 12 行**，却完成全部环境感知：`AC_INIT(qperf, 0.4.10, general@lists.openfabrics.org)` 定版本；三条 `AC_CHECK_LIB`——ibverbs 的 `ibv_open_device` 命中置 RDMA=1，ibverbs 的 `ibv_open_xrc_domain` 命中置 HAS_XRC=1，rdmacm 的 `rdma_create_id` 探测不设变量（隐式把 -lrdmacm 追加进 LIBS，configure.ac:5）；`AM_CONDITIONAL` 把 shell 变量升格为 Make 级条件（configure.ac:6-7）；`AC_CONFIG_FILES([qperf.spec])` 声明 spec 模板（configure.ac:8）；`AC_OUTPUT` 落盘（configure.ac:9）。XRC 探测的是**老版 libibverbs 的 ibv_open_xrc_domain API**——这正是该仓库在现代 verbs 栈上 XRC 必编不过的根源（05 篇）。

**根 Makefile.am 四行**（Makefile.am:1-6）：SUBDIRS=src；EXTRA_DIST=qperf.spec.in 把模板入发行包；dist-hook 在 `make dist` 时把已生成的 qperf.spec 一并拷进 distdir（Makefile.am:5-6）——保证源码 tarball 里 spec 与源码同代。

**src/Makefile.am 的条件编译骨架**（src/Makefile.am:1-28）：`if RDMA` 分支下 AM_CFLAGS 追 `-DRDMA` 且 qperf_SOURCES 含 rdma.c、LDADD 接 -libverbs；嵌套 `if HAS_XRC` 再叠 `-DHAS_XRC=1`（注意只有这里给了 `=1` 而 RDMA 是裸定义——源码里只 `#ifdef HAS_XRC` 不取值，两种写法等价但风格不统一）。非 RDMA 分支产出的 qperf 是纯 socket 测试器，rdma.c 整个不参与编译。末尾三条自定义规则是点睛之笔：`qperf.1: help.txt → ./mkman >qperf.1`（src/Makefile.am:17-18）；`help.c: help.txt` 规则体里再嵌 automake 条件——RDMA 构建跑 `./mkhelp RDMA`、否则跑 `./mkhelp`（src/Makefile.am:20-26）；`clean-local` 单删 qperf.1（src/Makefile.am:28）。help.c 出现在 qperf_SOURCES 里（src/Makefile.am:8/12）但仓库无此文件——make 发现缺失即按规则生成，这是"生成物当源文件"的合法用法。

**mkhelp：help.txt → help.c**（src/mkhelp）。核心是条件保留状态机：非缩进行是节头，节头上的 `+RDMA` 参数表示"仅当命令行 defs 里有 RDMA 才保留此节"、`-X` 反之（src/mkhelp:81-85）；`$defs{$_}=1 for @ARGV` 让 `./mkhelp RDMA` 注入宏（src/mkhelp:58）。help.txt 里 21 处 `+RDMA` 标记（Tests 节头 help.txt:372、Categories 节头 help.txt:56、各 RDMA 测试条目）据此裁剪——非 RDMA 构建的 --help 里压根不出现 rc_bw 这些名字。内容行做 C 化转义（引号反斜杠加倍、行尾接 `\n`，src/mkhelp:69-70），超过 68 字符按 lookahead 正则断成两截 C 串（src/mkhelp:72-76）。产出的 Usage[] 是 `"节名","内容"` 扁平双列数组，qperf.c 的 help 分支按 `usage+=2` 步进检索（qperf.c:862-864）。生成的 help.c 头部内嵌完整双许可声明（$top 模板，src/mkhelp:12-42）——生成物也携带许可证，法务上不马虎。

**mkman：help.txt → qperf.1**（src/mkman）。`make_dict` 按"顶格行=键、缩进行=值"切字典（src/mkman:154-165），六个 do_* 函数分译各节：Options 按 `-` 前缀断条转 `.TP`+`\fB` 加粗（src/mkman:72-91），Tests 用 `^ {8}(\w+)\s+(.*)` 提测试名表（src/mkman:54-62），Synopsis 把大写词转斜体（src/mkman:118-131）。最妙的是 `help_date`：man 页日期取 **help.txt 的 mtime**（`stat` 第 9 字段，src/mkman:143-147）——git checkout 一次日期就变一次，同版本重编出的 man 页日期漂移属正常现象，不是并行构建竞态。

**spec 链**：qperf.spec.in 用 `@VERSION@`（版本）与 `@RDMA_TRUE@`（BuildRequires 前缀）两个替换位（qperf.spec.in:3/10-11）；configure 依 AC_CONFIG_FILES 生成 qperf.spec。仓库同时检入了生成态的 qperf.spec（Version: 0.4.10、BuildRequires 无条件 = RDMA 版）——README"Changing version"要求最后改 spec 就是为了它（cleanup 可能删它，见下）。

**autogen.sh 与 cleanup** 这对开闭括号：autogen.sh 先 touch NEWS/README/ChangeLog 满足 automake 的 GNU 检查（autogen.sh:4-6），再 `aclocal && automake --foreign --add-missing --copy && autoconf`（autogen.sh:7-9，--foreign 放弃 GNU 严苛目录规范）。cleanup 反向清扫全部生成物，包括 src/help.c 与 src/qperf.1（cleanup:10-29）；对 qperf.spec 有保留条款——三个失效判据任一成立即删：spec 不含 RDMA 版 BuildRequires、spec.in 更新、或 **configure.in** 更新（cleanup:33-39）。

## 三、外部连接

- **向上**：README 的构建说明（./cleanup → ./autogen.sh → ./configure → make）与"make clean 清不干净、用 ./cleanup"的坦白（README:17-18）；
- **向下**：libibverbs/librdmacm 链接期探测（缺 ibverbs 不报错，静默降级为 socket 版，README 把这写成特性）；rpmbuild 按 spec 的 %build 走 %configure+make；
- **横向**：help.txt 是 mkhelp/mkman/do_option(help) 三方共同消费的单一事实源；qperf.c:858-874 消费 Usage[]、qperf.1 被 install 进 man1（qperf.spec.in:26）。

## 四、数据流

开发者视角的一次完整构建：git clone（无 configure、无 help.c/qperf.1）→ autogen.sh 生成 configure 与 Makefile.in → ./configure 探测出 RDMA=1/HAS_XRC=0 → 生成 Makefile + qperf.spec（@RDMA_TRUE@ 展开为空）→ make 发现 help.c 缺失，按规则跑 `./mkhelp RDMA` 生成之 → 编译七个 .c → 链接 -libverbs（-lrdmacm 来自 LIBS）→ mkman 生成 qperf.1 → install。发布时 make dist 把 spec.in（EXTRA_DIST）与 qperf.spec（dist-hook）都打进 tarball。

## 五、设计决策

1. **单源文档**：help.txt 一处维护，--help 与 man 同步零漂移；代价是 mkman 的正则解析对 help.txt 缩进格式极其敏感（改文档先读 do_options 正则）。
2. **能力探测而非版本判定**：RDMA/HAS_XRC 都探函数符号而非 pkg-config 版本号，对当年散装 OFED 环境容错更好；副作用是现代栈符号改名即静默失去特性（XRC 现状）。
3. **降级构建而非硬失败**：无 ibverbs 也出可用的 socket 版 qperf，二进制名不变——运维同一套命令在任何机器都能跑。
4. **spec 检入仓库**：OFED 打包脚本直接取源码树里的 spec（cleanup 注释原话"for the OFED scripts"），代价是版本漂移风险（12 篇）与"改版本须最后改 spec"的人肉时序协议。
5. **生成物内嵌许可证头**：mkhelp 的 $top 模板让 help.c 与手写文件法律地位一致，这是双许可项目对派生文件的尽职边界。

## 六、新人提示

- 改 help.txt 后要同时意识到三件事：--help 变了、man 页变了、若新增 `+RDMA` 节记得两种构建形态各验一遍——`./mkhelp` 与 `./mkhelp RDMA` 的 diff 就是非 RDMA 用户的视野。
- cleanup:38 的 `[ configure.in -nt qperf.spec ]` 是化石 bug：文件早已更名 configure.ac，该测试对象不存在恒为假，**configure.ac 更新后不会触发 spec 删除重建**——改完 configure.ac 记得手动删 qperf.spec 或直接改两处。README:19 写的 "configure.in" 同样是旧名残迹。
- mkhelp 的 68 字符断行用 `(?>[^\\]?)` lookahead 防止把转义序列从中间劈开（src/mkhelp:73），手改 help.txt 时行长失控不会出错但可读性会碎，控制在 68 列内最稳。
- 想验证"我这台机器会编出什么形态"，跑 `./configure && grep RDMA src/Makefile`：AM_CFLAGS 行有没有 -DRDMA 一目了然，比读 config.log 快。
- automake 对 `qperf.1: help.txt` 这种"无 .PHONY、目标在 clean-local 删除"的规则会在重编时重复生成（mtime 比 mkman 脚本旧不触发）——若改了 mkman 本身，`make clean` 或 touch help.txt 才会重出 man 页。
