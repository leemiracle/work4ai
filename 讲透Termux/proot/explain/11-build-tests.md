# 11 · 构建体系与测试 harness：src/GNUmakefile + tests/GNUmakefile

> 图谱层位：L11（构建体系与 CI）/ L13（测试基础设施）。锚均经源码现场核实（仓 @b27d81a）。勘误钉版：**本仓纯 GNU Make，全仓无 CMakeLists.txt**。

## 一、角色定位

这两个 GNUmakefile 是 proot 的"元程序"：`src/GNUmakefile`（284 行）把 66 个 .c 编成单个 `proot`，并把一个完整的 freestanding loader 二进制**内嵌**进去；`tests/GNUmakefile`（249 行）是自建回归 harness，把 112 个 shell + 40 个 C 用例展开成统一 `check-%` 矩阵。它们承担三件编译器做不了的事：①**构建期能力探测**——目标环境是否支持 `process_vm_readv` 与 seccomp-filter，答案变成 `build.h` 的 `HAVE_*` 宏，决定运行时内存读写与 syscall 加速走哪条路；②**多架构 loader 编译矩阵**——x86_64/arm64 同时编 64+32 位两个 loader，各钉各的链接地址；③**可移植测试协议**——exit 125=SKIP、编译 `|| true` 不炸套件、failure 文件聚合判定。源码用 `#if` 挡架构差异，makefile 用探测挡环境差异，测试用 skip 挡依赖差异——三层合成 proot 的可移植性。

## 二、内部结构

### 2.1 src/GNUmakefile：探测 → 生成 → 编译 → 内嵌

**入口与全局**。支持树外构建（:1-2），VPATH/SRC 双变量区分 makefile 目录与输出目录（:5-6）；`CROSS_COMPILE` 前缀贯穿 CC/STRIP/OBJCOPY（:11-15）。`CPPFLAGS` 定死 `-D_FILE_OFFSET_BITS=64 -D_GNU_SOURCE`（:17），`LDFLAGS` 挂 `-ltalloc -Wl,-z,noexecstack`（:19，Android 硬要求）；`PROOT_WITH_LIBANDROID_SHMEM` ifdef 追加 `-landroid-shmem`（:20-23，Termux 打包标准开关）。OBJECTS 手工列 66 项（:25-91），即模块地图：cli 3+execve 7+path 7+syscall 9+tracee 7+ptrace 3+extension 30。

**CHECK_FEATURES 探测链**。`CHECK_FEATURES = process_vm seccomp_filter`（:147）派生 .check_*/.check_*.o/.check_*.res 三组目标（:148-150），三条模式规则成流水线：`.check_%.o: .check_%.c` 以 `-$(COMPILE:echo=false)` 静默编译（:154-155，前导 `-` 吞错）；`.check_%: .check_%.o` 静默链接（:157-158）；`.check_%.res` 判定产出——`[ -e $< ]` 成立则写 `#define HAVE_*`（宏名 `tr a-z A-Z` 大写化），否则空行（:160-161）。探测源是两个真程序而非宏测试：`.check_process_vm.c:6-7` 直接调 `process_vm_readv/writev`；`.check_seccomp_filter.c:15-27` 构造真 BPF 程序再 `prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER,...)`。**编译失败=特性不存在**，测的是工具链+内核头合力，比 `#ifdef` 准。`build.h` 由 .res 拼接（:163-170）：guard + `git describe --tags --dirty` 的 VERSION 宏（:142-145）+ `cat $^`。谁依赖 build.h 也非手写——egrep 反查引用者自动挂钩（:197-198）。链接器特性同款探测：`BUILD_ID_NONE`（:172）与 `ROSEGMENT`（:175，注释明言 Android NDK r29+ compatibility）。

**多架构 loader 矩阵**。核心是 `define build_loader`（:210-237）+ 两次 eval：无参生成 64 位（:239），`HAS_LOADER_32BIT` 成立再以 `-m32` 来一次（:241-243）。loader 约束与主程序不同：`-fPIC -ffreestanding`（:216），链接 `-static -nostdlib -Wl,-Ttext=$(LOADER_ADDRESS)`（:217）——无 libc、钉死地址。取值全来自 arch.h：x86_64 `0x600000000000`+有 32 位二 loader（arch.h:80-81）；arm64 `0x5400000000`+有 32 位+`HAS_POKEDATA_WORKAROUND`（arch.h:148-153）；arm `0x20000000` 无二 loader（arch.h:104）；x86 `0xa0000000`+`-mregparm=3`（arch.h:178-179）。arm64 地址带长注释（arch.h:139-147）：避开 ASan 的 128 GiB 底线并给 PIE 装载区留整块空洞——loader 地址是内核 VA 布局的函数。**make 怎么知道这些 C 宏？** `define_from_arch.h`（:93-95）把 arch.h 丢给 `$(CC) -E -dM -DNO_LIBC_HEADER` 再 `grep -w` 切列（:97-98）：用编译器当"架构真相源"，传 `-m32` 时预处理器自动切 `__i386__` 分支，make 变量与 arch.h 永不脱钩。CI 注释点破现实："Unlike GCC, Clang builds the 32-bit ARM loader on arm64"（tests.yml:35-38），故矩阵三臂=amd64-gcc/amd64-clang/arm64-clang（tests.yml:25-40）。

**OBJIFY 内嵌**（:183-190）：`loader$1.exe` 先 cp+strip（:230-233，`.INTERMEDIATE` 即用即删），再 `objcopy --input-target=binary` 转 .o，目标架构经 `objdump -f cli/cli.o` 现场探测（:186-189）。缺省 `loader-wrapped.o` 进 OBJECTS（:107）；`PROOT_UNBUNDLE_LOADER` 时改外置（:100-105，:269-274）。licenses 同一 OBJIFY 把 LICENSE 文本转 .o（:204-205）。**pokedata 支线**（仅 arm64）：`loader-info.c` 由 `readelf -s loader | awk -f loader-info.awk` 生成（:245-246），算 `pokedata_workaround - _start` 偏移，消费方 `mem.c:49` extern、`mem.c:202` 算 stub 地址——偏移必须取自**最终链接产物**符号表，无法静态写死。

### 2.2 tests/GNUmakefile：一套自建测试协议

**环境隔离**（:11-14）：`TMP_DIR` 钉死仓内 `tests/tmp` 并 export 成 `TMPDIR`/`PROOT_TMP_DIR`——测试、工具、proot 三方临时文件全收敛进仓库且路径 canonical（注释明言要跟内核返回路径比对）；gdb 在 root 下会污染系统目录，故 export `PYTHONDONTWRITEBYTECODE=1`（:16-18）。

**目标展开**（:20）：wildcard 把 152 个 `test-*` 展开成 check-%，两条模式规则接住——`check-%.sh: %.sh setup` 注入 `ROOT_RAW/PROOT/ROOTFS` 后 `sh -ex` 执行（:36-37）；`check-%.c: $(ROOTFS)/bin/% setup` 把编进 rootfs 的静态二进制交 `$(PROOT) -b /proc -r $(ROOTFS) /bin/$*` 跑（:39-40）。

**退出码三方协议**（:116-121）：`check` 宏 case `$?`——0=ok；**125=skipped**；其余=FAILED 且 `touch failure`。125 借自 git 惯例，脚本在依赖缺失时主动 `exit 125`（`test-00000000.sh:1-3` 查 rootfs 的 true；`test-11111111.sh:4` 查 8 个宿主工具）。第二条 skip 通道在 `check_c`（:110-114）：二进制不存在（编译被 `|| true` 吞）也打 skipped。**失败聚合**：`check: | clean_failure check_failure`（:24）先删 failure（:30-32），全跑完断言 failure 不存在（:33-34），order-only 前提保证时序不受时间戳干扰。

**ROOTFS_BIN 清单**（:126-137）：33 个预编产物=25 个普通工具源（tests/ 29 个非 test 前缀 .c 之入选者）+2 个 symlink（`abs-true`→`/bin/true` 绝对、`rel-true`→`./true` 相对，:148-152，专测两种 symlink 翻译）+2 个 `-m32 -static` 产物（:154-158，编不出即放弃）+4 个 suid/sgid 拷贝（:160-174，喂 fake_id0）。通用规则 `$(ROOTFS)/bin/%: %.c` 一律 `-static`（:177-178）让 rootfs 自洽；`.SECONDARY`（:176）防中间文件被清；特殊 flags 散布 :181-234（pthread、`-fPIE -pie` 于 :225、test-bdc90417 特意非 static 于 :181-182）。

**特例目标**：test-25069c13 必须 `env -u LD_PRELOAD`（:74-77）——Termux 预载的 libtermux-exec 在 NULL argv 上崩；test-1ffc8309 要 `PROOT_FORCE_KOMPAT=1 -k $(uname -r)`（:80）伪造内核版本；gdb 用例无 gdb 时直接 `rm -f $<` 转 skip（:86-92）；test-f6b33793 跑两遍、第二遍 `PROOT_NO_SECCOMP=1`（:106-108）对照加速开关；test-82ba4ba1 的 `! $(PROOT) -i 123:456 ./$<`（:66）用 `!` 断言**预期失败**；`ROOT_RAW` 用途见 `test-230f47cf.sh:1`：`! ${PROOT} ${PROOT_RAW} /bin/true` 是嵌套 proot 用例。

**VALGRIND 集成**三行（:26-28）：`memcheck: PROOT_RAW := $(PROOT)` 先存裸路径，再把 PROOT 重定义为 `valgrind -q --error-exitcode=1 $(PROOT)`——harness 一行不改，全部用例的 proot 都跑在 valgrind 下；嵌套用例用 `PROOT_RAW` 免于双重插桩；`--error-exitcode=1` 让 valgrind 报错走 FAILED 通道。`validation.mk` 是发布级大验证（LTP/coreutils/perl/gdb，validation.mk:19，版本钉 2013-14 纪元），上游遗产日常不用。

## 三、外部连接

- **上游供血**：arch.h 供 loader 地址与三宏（src/GNUmakefile:97-98）；git describe 供 VERSION；libtalloc 唯一硬依赖（:19）。
- **下游消费**：build.h 被 7 个 .c 引用——`mem.c:41`（`#if defined(HAVE_PROCESS_VM)` 于 mem.c:231 起七处切换 process_vm/ptrace 读写路）、`seccomp.c:26`（整块 seccomp 加速到 :583 闭合）、`cli.c:114-119`（`proot --version` 打印 "built-in accelerators: process_vm = yes/no, seccomp_filter = yes/no"——诊断"为什么慢"的第一入口）。
- **CI**：tests.yml 三矩阵跑 make check（:25-40），amd64 臂装 gcc-multilib 正为 32 位 loader 与 -m32 程序（:29）。
- **Termux**：`PROOT_WITH_LIBANDROID_SHMEM` 与 ROSEGMENT 探测（src/GNUmakefile:20-23/:175）是 fork 独有接口；tests/GNUmakefile:3 直引 `../src/proot`——先 `make -C src` 再 `make -C tests check`。

## 四、数据流：一次 `make -C tests check`

1. 读入：`$(shell mkdir -p tmp)` 建临时区（tests/GNUmakefile:12），展开 152 个 check 目标（:20）。
2. setup：`setup: $(ROOTFS_BIN)`（:146）触发 33 产物——目录（:143-144）→symlink（:148-152）→静态编译（:177-178）→m32 尝试（:154-158）→suid 拷贝（:160-174）。
3. 逐用例三态判定（:116-121），FAILED 触 failure。
4. 聚合：`bash -c '! test -e failure'`（:34）放大为 make 非零退出。
5. `make memcheck` 同套目标重跑，proot 已被 valgrind 包裹（:26-28）。

## 五、设计决策

1. **探测优于配置**：无 config.h.in，能力全靠试链实测（:147-161/:172/:175）——对"必须跑在千奇百怪 Android 内核+NDK 组合"的项目，零配置漂移是唯一稳路线。
2. **make 变量从 C 头萃取**（:93-95）：arch.h 单真相源，-m32 预处理自动换分支，胜过手维护双份地址表。
3. **loader 内嵌/外置可切**（:100-111）：默认 OBJIFY 进二进制保单文件分发，UNBUNDLE 走外置安装。
4. **优雅降级三件套**：exit 125 协议+编译 `|| true`+check_c 存在性判定——套件在残缺环境也能跑完并如实报 skipped，CI 不因缺件假红。
5. **失败聚合而非即时中止**：152 用例一次跑完报告完整故障面，回归定位信息密度高。
6. **quirks 钉版**：①无 CMake；②`uninstall`（src/GNUmakefile:276-283）疑似复制粘贴事故——对 loader 执行 `$(INSTALL) -D`（又装一遍）而非删除，Termux 不用 UNBUNDLE 故无实害；③测试名 8 位十六进制是上游"一个 bugfix commit 一个回归"惯例，test-00000000/11111111/kkkkkkkk/iiiiiiii 是人造例外。

## 六、新人提示

- **改码后**：`make -C src && make -C tests check`；单用例 `make -C tests check-test-00000000.sh`（目标名含后缀）。
- **看真实命令**：`make V=1`（src/GNUmakefile:128-137/tests/GNUmakefile:239-248）——默认全静音，排查探测失败必须开 V=1 手跑 `.check_*`。
- **加回归**：写 `test-<8位hash>.c`（静态、exit code 断言）或 `.sh`（缺依赖先 exit 125），.c 自动进 rootfs 与 check 矩阵；特殊 proot 参数仿 :60-66 加特例目标。
- **探测失灵**：`HAVE_PROCESS_VM=no` 时 mem.c 全退 ptrace PEEK/POKE（mem.c:231 起）性能掉量级——先看 `proot --version` accelerators 行（cli.c:114-119）再查 `.check_process_vm.res`。
- **32 位失败**：装 gcc-multilib（tests.yml:29）；arm64 编 32 位 loader 只能 clang（tests.yml:35-38）。
- **改 loader 地址**：动 arch.h 别动 makefile（:93-95 萃取机制），重读 arm64 VA 注释（arch.h:139-147）。
- **doc/ 勿碰**：上游遗留，治理铁律（AGENTS.md）。

## 相关文件

`src/GNUmakefile`（284 行）· `tests/GNUmakefile`（249 行）· `src/arch.h` · `src/loader/loader-info.awk` · `tests/validation.mk` · `.github/workflows/tests.yml`
