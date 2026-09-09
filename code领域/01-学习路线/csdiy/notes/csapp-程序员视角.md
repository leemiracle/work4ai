# CSAPP 程序员视角精读笔记

> 不是"这本书讲了什么"，而是"这本书能救你线上哪条命"。
> 每章三件事：(a) 它解释了你 coding/debug/线上遇到的什么真实问题；(b) 你今天就能用的 checklist 与命令；(c) 一个 3-5 行真实 debug 故事。
> 实验参照：本仓库 `github-repos/references/REKCARC-TSC-UHT/.../计系概_bomblab/`（真实 32-bit ELF，带 debug_info，`bomb.s` 反汇编齐全）与 `cs-self-learning` 的 CSAPP 资源。

---

## 1. 信息的位级表示（Ch2：Data Lab 那一章）

### (a) 它到底救你什么命
你以为 `a + b` 永远等于 `a + b`。直到有一天：
- 财务系统 `int` 累加金额溢出，账面对不上；
- `for (int i = len - 1; i >= 0; i--)` 改成 `size_t i` 之后死循环（`size_t` 是无符号，`i >= 0` 恒真）；
- `if (sizeof(arr) > -1)` 永远为真——`-1` 被提升成 `unsigned` 变成 `0xFFFFFFFF`；
- 浮点 `0.1 + 0.2 != 0.3`，对账脚本一上量就抖。

Ch2 的核心是：**所有"数字"在机器里都是比特模式，运算的结果取决于你把它解释成什么**。理解补码、IEEE754、隐式类型提升，这些"玄学 bug"就变成了可预测的。

### (b) 立刻能用的 checklist / 命令
- 永远不要拿有符号数和 `size_t`/`unsigned` 直接比较。开 `-Wsign-compare -Werror=sign-compare`：
  ```bash
  gcc -Wall -Wextra -Wsign-compare -Wconversion -O2 -g main.c
  ```
- 溢出要用编译器内建，别自己手撸 `if (a + b < a)`（编译器在 `-O2` 下会优化掉）：
  ```c
  if (__builtin_add_overflow(a, b, &c)) { /* 处理溢出 */ }
  if (__builtin_mul_overflow(a, b, &c)) { ... }
  ```
- 想看一个常量在不同类型下的位模式：
  ```bash
  python3 -c "import struct; print(struct.pack('<i',-1).hex(), struct.pack('<f',0.1).hex())"
  # 输出 ffffffff  cdcccc3d —— -1 和 0.1 的内存表示
  ```
- 编译期把魔法数转成十六进制看清楚：`printf("%08x\n", (unsigned)x);`
- Data Lab 训练的就是这一层：用 `~ & ^ | + << >>` 不用循环不用分支实现 `bitXor`/`tmin`/`fitsBits`。**它不是为了让你背位运算，而是让你建立"比特模式"直觉。**

### (c) Debug 故事
```text
线上偶发：订单金额累加器，跑一天差几分钱。
打开 core，发现累计变量是 int，单笔最大 2e8，累加上万笔后悄悄溢出成负数，
再被 unsigned 转 long 拉成巨大正数。账面看起来"正常"。
定位：gdb p (long)acc 显示 4294967xxx；改成 int64_t + __builtin_add_overflow，根治。
根因就是 Ch2 第 20 页那句话：溢出在 C 里是"未定义行为/环绕"，不会报错。
```

---

## 2. 机器级表示（Ch3：Bomb Lab 那一章）

### (a) 它到底救你什么命
C 是对汇编的薄薄一层糖衣。真正在生产里咬你的是：
- 一段 segfault 的 backtrace 只给你寄存器和地址，你看不懂；
- 结构体字段对不齐，跨平台/跨编译器传 struct 数据错位；
- 调用约定：第 7 个参数去哪了？`%rdi %rsi %rdx %rcx %r8 %r9` 用完，多余的上栈；
- 编译器把你的局部变量优化进寄存器甚至优化没，`gdb p var` 显示 `<optimized out>`。

Ch3 让你能**读反汇编**。能读汇编的人，调试能力比不会的人高一整个量级——因为你能看到程序"真正在做什么"，而不是你以为它在做什么。

### (b) 立刻能用的 checklist / 命令
- 把二进制反汇编出来（本仓库 bomb lab 就是这么玩的）：
  ```bash
  objdump -d -M intel bomb > bomb.s        # AT&T 语法换成 intel 更易读
  objdump -d bomb | grep -A30 '<phase_2>:' # 只看某函数
  ```
- 看 ELF 元信息：`readelf -h bomb`（架构）、`readelf -s bomb | grep bomb`（符号表）、`file bomb`。
- 结构体布局与对齐（线上跨语言传 struct 的命案源头）：
  ```bash
  gcc -E struct.c -o - ; pahole struct.o     # pahole 来自 dwarves 包，打印字段偏移与空洞
  # 或编译期：
  _Static_assert(offsetof(struct foo, bar) == 8, "layout changed!");
  ```
- GDB 读寄存器与栈、给炸弹拆雷：
  ```gdb
  gdb ./bomb
  (gdb) b explode_bomb                      # 拆弹核心：先在此下断，爆之前能停
  (gdb) b phase_2
  (gdb) run sol.txt
  (gdb) disas                               # 反汇编当前函数
  (gdb) info registers rdi rsi rdx          # 看前几个参数
  (gdb) x/16xw $rsp                        # 看栈顶 16 个字
  (gdb) x/s $rdi                           # 把第一个参数当字符串看
  ```
- `printf` 看不到变量？关优化或用 `volatile` 调试：
  ```bash
  gcc -O0 -g -fno-inline main.c            # 调试时不要让编译器内联/优化掉变量
  ```

### (c) Debug 故事
```text
生产 core dump，backtrace 栈被踩烂，只有一行 <signal handler called>。
objdump -d 看 core 里 rip 附近的指令，发现是个 callq 进了一个 PLT 项，
对照 readelf -s 发现是调 vfprintf——某个日志宏把 user 传入的字符串直接当 format。
用户数据里含 %s%s%s%s，读到非法地址炸了。改 "%s" 占位，根治。
不会读汇编的话，这 bug 看起来就像"莫名其妙的段错误"。
```

---

## 3. 处理器体系结构（Ch4：Y86 / Arch Lab 那一章）

### (a) 它到底救你什么命
你不需要自己造 CPU，但你需要理解**为什么"看起来一样快的两段代码，实际能差 3 倍"**：
- 分支预测失败，流水线冲刷，十几个周期打水漂；
- 数据依赖链太长，指令级并行（ILP）喂不饱执行单元；
- store-to-load 前递、寄存器重命名、乱序执行——这些决定了你那段循环到底跑多快。

Ch4 用一个简化的流水线（Y86-64）让你亲手实现 SEQ→PIPE，理解冒险（hazard）、转发（forwarding）、分支预测。**理解了这一层，你才看得懂 perf 给你的 `branch-misses`、`stalled-cycles` 在说什么。**

### (b) 立刻能用的 checklist / 命令
- 看你 CPU 的微架构与拓扑（决定你的指令吞吐、缓存层级）：
  ```bash
  lscpu                                   # 架构、cache、flags(avx2/avx512)
  cat /proc/cpuinfo | grep -m1 'model name'
  perf stat -e branches,branch-misses,instructions,cycles ./a.out
  # branch-misses / branches > 5% 就该考虑分支优化
  ```
- 把难以预测的分支换成无分支（branchless）代码，喂饱流水线：
  ```c
  // 有分支版：数组乱序时预测失败率高
  if (x < threshold) sum += a[i];
  // 无分支版
  sum += (x < threshold) * a[i];           // 编译成 cmov
  ```
- 把顺序循环里的数据依赖拆成多路累加器，打破依赖链，利用 ILP：
  ```c
  // 单累加器：每次 add 等上一次完成
  for (...) acc += f(i);
  // 多累加器：4 路并行，ILP 喂满
  double a0=0,a1=0,a2=0,a3=0;
  for (i=0; i+3<n; i+=4){ a0+=f(i); a1+=f(i+1); a2+=f(i+2); a3+=f(i+3); }
  acc = (a0+a1)+(a2+a3);
  ```

### (c) Debug 故事
```text
一段排序后的查找比未排序的快 4 倍，业务方说是玄学。
perf stat 对比：未排序版 branch-misses 高出 20 倍——CPU 在不可预测的 if 上疯狂冲刷流水线。
把二分查找/位运算替代线性 if 后，对齐。这就是 Ch4 讲的"流水线对分支敏感"在真实代码里的样子。
```

---

## 4. 优化程序性能（Ch5：与 Ch4 是一对）

### (a) 它到底救你什么命
Ch4 解释"为什么"，Ch5 教"怎么测、怎么改"：
- 你以为 `-O3` 就是性能银弹，但它可能因为别名分析不敢向量化；
- 你以为内联更快，结果 icache miss 让它更慢；
- 你以为循环展开越多越好，结果寄存器溢出到栈，反而崩。

Ch5 的核心方法论：**用时钟周期数说话，不靠猜。** 度量（CPE, cycles per element）、定位、消除低效、循环展开、SIMD、避免内存别名。

### (b) 立刻能用的 checklist / 命令
- 先测，别盲改。`perf` 三件套：
  ```bash
  perf stat -e cycles,instructions,cache-misses ./a.out
  perf record -g ./a.out && perf report      # 找热点函数
  perf stat -e instructions,cycles -- ./a.out # 算 IPC：<1 说明在等
  ```
- 让编译器替你向量化，并打印它为什么不动：
  ```bash
  gcc -O3 -march=native -fopt-info-vec-optimized vec.c   # 告诉你哪些循环向量化成功
  gcc -O3 -march=native -fopt-info-vec-missed vec.c      # 告诉你为什么失败（往往：别名/控制流/对齐）
  ```
- 给编译器"无别名"承诺，解除向量化的最大枷锁：
  ```c
  void add(const double * restrict a, const double * restrict b, double * restrict c, int n){
      for (int i=0;i<n;i++) c[i]=a[i]+b[i];   // restrict 让编译器确信 a/b/c 不重叠
  }
  ```
- 用 `__attribute__((assume_aligned(32)))` 告诉它地址已对齐，省掉对齐处理。
- 别过早优化：先 `perf` 找到真正热点，再动手。90% 时间在 10% 代码里。

### (c) Debug 故事
```text
向量加法，-O3 启动但没出 SIMD 指令。perf 看 IPC 才 0.3。
gcc -fopt-info-vec-missed 报："might not be aligned / possible aliasing"。
加 restrict + assume_aligned(32) 后再 objdump -d 看到 ymm0/vaddpd，IPC 飙到 2.5，快 6 倍。
没有 Ch5 的"先度量再优化"纪律，这种 case 会瞎调一周。
```

---

## 5. 存储器层次结构（Ch6：Cache Lab 那一章）

### (a) 它到底救你什么命
内存不是平的。访问 L1 是 1ns，主存是 100ns——**差两个数量级**。你代码慢，常常不是因为算得慢，而是因为**没把数据放在 cache 里**：
- 矩阵列遍历比行遍历慢 10-40 倍；
- `struct of arrays` 比 `array of structs` 对 cache 友好；
- 多线程共享一个 cache line 的不同变量，触发 false sharing，性能雪崩；
- 链表遍历每跳一次都是一次 cache miss（指针追逐，pointer chasing）。

Ch6 让你理解 cache 行（通常 64B）、组相联、替换策略、写策略。Cache Lab 让你亲手写一个 cache 模拟器与分块矩阵——做完你会有"cache 直觉"。

### (b) 立刻能用的 checklist / 命令
- 看 cache 层级与行大小（写代码要对齐 cache line 就靠它）：
  ```bash
  lscpu | grep -i cache                  # L1d L1i L2 L3 大小
  getconf LEVEL1_DCACHE_LINESIZE         # 通常 64
  cat /sys/devices/system/cpu/cpu0/cache/index0/coherency_line_size
  ```
- 测 cache 行为：
  ```bash
  valgrind --tool=cachegrind ./a.out ; cg_annotate cachegrind.out.*
  perf stat -e cache-misses,cache-references,L1-dcache-load-misses ./a.out
  ```
- 矩阵乘法分块（Cache Lab 的核心思想搬过来）：
  ```c
  // 朴素 ijk 三重循环对 B 是列遍历，cache 杀手
  // 分块成 BxB（B 选到能塞进 L1 的大小，如 64x64 的 double 即 32KB）
  for (ii=0; ii<n; ii+=B)
    for (jj=0; jj<n; jj+=B)
      for (kk=0; kk<n; kk+=B)
        for (i=ii;i<ii+B;i++) for(j=jj;j<jj+B;j++) for(k=kk;k<kk+B;k++)
          C[i][j] += A[i][k]*B[k][j];
  ```
- 对齐数据到 cache line，避免 false sharing（多线程写同一行的不同变量）：
  ```c
  struct alignas(64) Counter { long a, b, c; };   // 每个计数器独占一行
  // C11: _Alignas；或 gcc: __attribute__((aligned(64)))
  ```
- 优先用连续数组，慎用 `std::vector<std::list>` 这种"每元素一次跳转"的结构。

### (c) Debug 故事
```text
多线程计数器，8 个线程各加自己的 counter，理论上该线性加速，结果比单线程还慢。
perf stat -e cache-misses 爆表；pahole 看 struct 把 8 个 long 挤在同一个 64B cache line。
加 alignas(64) 让每个线程的 counter 独占一行（解决 false sharing），加速 8 倍。
这就是 Ch6 "存储器是层次结构"在并发代码里的直接代价。
```

---

## 6. 链接（Ch7：被低估、却天天咬人的一章）

### (a) 它到底救你什么命
99% 的程序员把"编译"当一个黑盒，结果被这些折磨：
- `undefined reference to 'foo'` / `multiple definition of 'bar'`；
- 运行时 `error while loading shared libraries: libfoo.so: cannot open shared object file`；
- 静态库符号顺序导致链接失败（`-lm` 必须在被引用的源之后）；
- 不同翻译单元的 static 初始化顺序未定义（"static initialization order fiasco"）；
- 同一个符号被两个 `.so` 各定义一份，运行时挑了错的那份。

Ch7 把 ELF（`.text/.data/.bss/.rodata/.symtab/.rela`）、符号解析、重定位、静态/动态链接、位置无关代码（PIC）讲透。**配《程序员的自我修养》食用更佳。**

### (b) 立刻能用的 checklist / 命令
- 符号查不到？用 `nm`/`readelf` 看二进制到底有什么符号：
  ```bash
  nm -C libfoo.a | grep foo               # T=定义 U=未定义 W=弱
  readelf -s libfoo.so | grep foo
  objdump -T libfoo.so | grep foo         # 动态符号表
  ```
- `cannot open shared object` 三板斧：
  ```bash
  ldd ./a.out                             # 看运行时依赖
  readelf -d ./a.out | grep NEEDED        # 看 DT_NEEDED
  export LD_LIBRARY_PATH=/opt/lib:$LD_LIBRARY_PATH   # 临时加搜索路径
  # 永久方案：把路径写进 /etc/ld.so.conf.d/ 然后 ldconfig
  ldconfig -p | grep libfoo               # 确认动态链接器缓存里有
  ```
- `LD_DEBUG` 让动态链接器把每一步都吐出来（最强排错工具，没有之一）：
  ```bash
  LD_DEBUG=libs ./a.out 2>&1 | head        # 看它去哪些路径找 .so
  LD_DEBUG=symbols ./a.out 2>&1 | grep foo # 看符号解析，挑了哪个版本
  LD_DEBUG=bindings ./a.out 2>&1 | head    # 看符号绑定
  ```
- 看链接器在做什么：
  ```bash
  gcc -Wl,--verbose main.c -lfoo 2>&1 | grep -i 'attempt\|search'   # 看搜了哪些路径
  gcc -Wl,-Map=out.map main.c            # 生成链接 map，定位符号归属
  ```
- 强符号/弱符号：定义加 `__attribute__((weak))` 可被覆盖；用 `__attribute__((visibility("hidden")))` 控制是否导出。
- C++ 别忘了符号 mangling：`nm -C`（demangle）或 `c++filt _ZN3foo3barEv`。

### (c) Debug 故事
```text
CI 能跑，本地跑挂：undefined reference to 'foo'。
readelf -s libfoo.a 发现 foo 确实在，但 g++ 链接顺序里 -lfoo 写在 main.o 前面。
GNU ld 从左到右处理，碰到 -lfoo 时还没人引用 foo，符号被丢掉，后面 main.o 再找就没了。
把 -lfoo 挪到命令行末尾，或用 -Wl,--start-group ... -Wl,--end-group，根治。
Ch7 那句"链接器按命令行顺序处理库"就是这个 bug 的全部解释。
```

---

## 7. 异常控制流（Ch8：Tsh Lab / 异常与进程那一章）

### (a) 它到底救你什么命
ECF 是从"写函数"到"写系统"的分水岭：
- `fork` 之后到底哪段代码会执行两次？`vfork` 又有什么坑？
- 僵尸进程（zombie）怎么来的、怎么收；
- 信号处理函数里能不能 `printf`？（不能，不异步信号安全）；
- `SIGCHLD` 漏收导致子进程变僵尸、进程表打满、`fork: retry: No child processes`；
- `EINTR`：慢系统调用被信号打断，你不重试就丢数据。

Ch8 把异常（陷阱/故障/中断/终止）、进程、信号、非本地跳转（`setjmp/longjmp`）串成一条线。Tsh Lab 让你写一个能处理 job、信号、管道的 shell——做完你才真正理解"进程是什么"。

### (b) 立刻能用的 checklist / 命令
- 查进程状态（Z 就是僵尸）：
  ```bash
  ps -elf | grep -E 'STATE|Z'              # 第 2 列状态码：R S T Z D
  ps -eo pid,ppid,state,cmd | grep ' Z '
  # 僵尸的爹没回收它：kill -CHLD <父pid> 让它去 waitpid
  ```
- 追踪程序的所有系统调用与信号（线上排错神器）：
  ```bash
  strace -f -e trace=process,signal ./a.out
  strace -p <pid>                          # 挂到正在跑的进程
  strace -c ./a.out                        # 统计每种 syscall 次数与耗时
  strace -e read,write -T -tt ./a.out      # 看 I/O 的时间戳，定位慢调用
  ```
- 信号全家福：`kill -l`（列出）；`kill -9` 是 SIGKILL 不能被捕获，`kill -15` 是 SIGTERM 可以。
- **信号处理函数铁律**：只调异步信号安全函数（man 7 signal-safety），用 `write(2)` 不用 `printf`，用 `volatile sig_atomic_t` 标志位，主循环里处理业务。
- 慢系统调用被信号打断要重试：
  ```c
  ssize_t n;
  do { n = read(fd, buf, sz); } while (n < 0 && errno == EINTR);
  ```
- `fork` 之后子进程立刻 `_exit`（不是 `exit`）——避免冲掉父进程的 stdio 缓冲。
- 阻塞信号避免竞态：`sigprocmask` 先阻塞 SIGCHLD，`fork`，父进程 `waitpid`，再解除阻塞（Tsh Lab 的经典 addjob 竞态）。

### (c) Debug 故事
```text
守护进程跑一天，fork 开始报 EAGAIN，进程数到上限。
ps 一看几千个 Z 状态僵尸。根因：父进程信号处理函数里调了 printf，
在 malloc 持锁时被信号打断，死锁，waitpid 永远跑不到。
把信号处理函数改成只置 volatile sig_atomic_t flag，主循环里 waitpid，僵尸清零。
这就是 Ch8 "信号处理函数必须异步信号安全"那句话在生产的代价。
```

---

## 8. 虚拟内存（Ch9：Malloc Lab 那一章）

### (a) 它到底救你什么命
"内存"在你程序眼里是连续的，在硬件上是碎的——中间那层就是虚拟内存（VM）。理解它，你能解释：
- 为什么 `top` 里 VIRT 100GB 但 RES 才 200MB（VM 只是地址空间预约，没真分配）；
- 为什么进程被 OOM-Killed（看的是 RSS + 触碰过的页，不是 malloc 的返回值）；
- 为什么 `malloc` 大块不分配物理内存，碰到才 page fault；
- 为什么 `mmap` 大文件比 `read` 快（零拷贝、按页惰性加载）；
- 内存泄漏在 RSS 而不是 VIRT 上累积，容器/物理机被撑爆才暴露。

Ch9 讲地址翻译（页表、TLB、多级页表）、缺页、内存映射、写时复制（COW，`fork` 之所以快）、`malloc` 的实现策略。Malloc Lab 让你手写分配器，理解碎片、对齐、合并。

### (b) 立刻能用的 checklist / 命令
- 看进程真实内存占用（RES 才是真正吃物理内存的）：
  ```bash
  top -p <pid>                            # VIRT/RES/SHR
  ps -o pid,rss,vsz,cmd -p <pid>          # RSS in KB
  pmap -x <pid>                           # 每段映射的 RSS、脏页
  cat /proc/<pid>/status | grep -E 'Vm|Rss' # VmRSS/VmSize/VmPeak
  ```
- 逐段看页表（哪些地址被触碰、是否 swap）：
  ```bash
  cat /proc/<pid>/smaps | grep -E '^[0-9a-f]|Rss|Private'
  cat /proc/<pid>/smaps_rollup             # 汇总：Rss/Pss/Swap
  ```
- 找内存泄漏，三选一：
  ```bash
  valgrind --leak-check=full --show-leak-kinds=all ./a.out   # 经典，慢
  valgrind --tool=massif --stacks=yes ./a.out ; ms_print massif.out.*  # 峰值在哪
  # 生产环境用 heap profiler，低开销：
  LD_PRELOAD=libgmalloc.so ...   # 或 gcc -fsanitize=address（开发期最猛）
  ASAN_OPTIONS=detect_leaks=1 ./a.out
  ```
- 限制进程能吃的内存，提前暴露问题：
  ```bash
  ulimit -v 4194304    # 限制虚拟内存 4GB（kbytes）
  ulimit -m 2097152    # 限制 RSS（部分系统不生效）
  # 容器里更可靠：
  docker run --memory=512m --memory-swap=512m ...
  ```
- 大文件处理用 mmap 惰性加载：
  ```c
  void *p = mmap(NULL, sz, PROT_READ, MAP_SHARED, fd, 0);
  // 内核按需 page in，比 read 整块拷贝省内存、省拷贝
  posix_fadvise(fd, 0, sz, POSIX_FADV_SEQUENTIAL);  # 预读提示
  ```

### (c) Debug 故事
```text
服务跑 6 小时被 cgroup OOM-Killed，但代码里没看到明显泄漏。
top 看 RSS 持续涨，VIRT 没动。valgrind --tool=massif 抓峰值，发现一个
缓存容器只 add 不 evict，对象一直被引用，GC 不掉。每条几 KB，一天百万条 = 数 GB。
加 LRU 上限，RSS 平稳。这就是 Ch9 "已分配未释放的页会进 RSS 持续累积"的活样本。
```

---

## 9. 系统级 I/O（Ch10：Proxy Lab 的底座）

### (a) 它到底救你什么命
C 标准库的 `printf/fopen` 是 Unix `write/open` 的薄封装，但这一层封装藏住了**所有 I/O 的真实面貌**：
- `read`/`write` 可能**只读/写一部分就返回**（short read/write），你必须在循环里凑齐；
- 文件描述符（fd）是有限资源，漏 close 一个，长期跑的服务会 `EMFILE: too many open files`；
- 缓冲层级：用户态 stdio buffer → 内核 page cache → 磁盘。`fsync` 不调，断电就丢；
- 网络读写会阻塞、会 `EAGAIN`、会被信号打断；
- `select/poll/epoll` 处理"很多 fd 大部分时间没事干"的高并发场景。

Ch10 是从"写算法题"到"写真实服务"的必经之路。Proxy Lab 让你用这章接口写一个并发 HTTP 代理。

### (b) 立刻能用的 checklist / 命令
- 永远循环凑齐 n 字节，别假设一次成功：
  ```c
  ssize_t readn(int fd, void *buf, size_t n){
      size_t off=0; ssize_t r;
      while(off<n){
          r=read(fd,(char*)buf+off,n-off);
          if(r<0){ if(errno==EINTR) continue; return -1; }
          if(r==0) break;        // 对端关闭
          off+=r;
      }
      return off;
  }
  ```
- 看 fd 泄漏与打开的文件：
  ```bash
  ls -l /proc/<pid>/fd | wc -l            # 当前打开数
  ls -l /proc/<pid>/fd                    # 每个 fd 指向哪
  lsof -p <pid>                           # 更可读
  ulimit -n                               # 进程 fd 上限，常 1024，生产调到 1<<20
  cat /proc/<pid>/limits | grep 'open files'
  ```
- 追踪每次 I/O 看是不是短读、慢在哪：
  ```bash
  strace -e trace=read,write,openat,close -p <pid>
  strace -e read,write -T -e signal=none ./a.out   # 带时间戳
  ```
- 想让数据真落盘（数据库/日志的命根）：
  ```c
  fsync(fd);                  // 数据 + 元数据
  fdatasync(fd);              // 只数据，更快，多数场景够用
  ```
- 高并发别再用 select（fd 上限 1024），用 epoll：
  ```bash
  # 看内核 epoll 能力
  cat /proc/sys/fs/epoll/max_user_watches
  ```
  ```c
  int ep=epoll_create1(0);
  struct epoll_event ev={.events=EPOLLIN,.data.fd=fd};
  epoll_ctl(ep,EPOLL_CTL_ADD,fd,&ev);
  for(;;){ struct epoll_event evs[64]; int n=epoll_wait(ep,evs,64,-1); ... }
  ```
- 文件复制 90% 的 bug 根源就是没处理 short write（见上面 `readn` 配对的 `writen`）。

### (c) Debug 故事
```text
文件复制工具，小文件正常，大文件偶发尾部截断。
strace -e write 一看，write 偶尔只写了 8192/1MB，程序却当成功返回了。
原代码 if (write(fd,buf,sz)!=sz) error; ——但 write 本来就可能短写。
套上 writen 循环重试，截断消失。Ch10 那句"read/write 返回值是实际字节数，可能小于请求"就是这个 bug。
```

---

## 横向：把九章串成一条调试流水线

线上一个"卡死/崩溃/变慢"的进程，按 CSAPP 的层次从下往上排查，几乎不会漏：

```text
1. 位/类型    : core 里数值离谱？              → __builtin_*_overflow、-Wconversion
2. 汇编      : backtrace 看不懂？             → objdump -d、gdb disas、看寄存器
3. 处理器    : 同样代码慢 3 倍？               → perf stat branch-misses、cmov 化
4. 优化      : 想加速不知从哪下手？            → perf record/report、-fopt-info-vec
5. 存储层次  : 多线程反而慢、矩阵慢？          → valgrind cachegrind、cache line 对齐
6. 链接      : 编译过、运行炸、符号乱？        → nm/readelf/LD_DEBUG/ldd
7. 异常控制流: 僵尸/卡死/信号乱？              → ps Z、strace -e signal、信号安全
8. 虚拟内存  : OOM/RSS 涨/泄漏？              → smaps/massif/asan/ulimit
9. 系统 I/O  : fd 耗尽/截断/慢？              → /proc/pid/fd、strace -e read,write
```

每一层都有对应的**测量命令**——CSAPP 教给你的不只是知识，是这套"先测后改、按层下钻"的工程纪律。这才是它区别于普通"操作系统原理"课的地方。

---

## Lab 速查（本仓库与 cs-self-learning 可对应）

| Lab | 对应章 | 练的是什么真本事 | 一句话提示 |
|-----|--------|------------------|-----------|
| Data Lab | Ch2 | 位运算直觉、补码 | 禁循环禁分支，逼你用 `^~<<` 想问题 |
| Bomb Lab | Ch3 | 读汇编、用 gdb | `b explode_bomb` 先保命，逐 phase 读 `objdump` |
| Attack Lab | Ch3/9 | 栈帧、注入、ROP | 配合 Ch3 栈布局 + Ch9 页保护(NX/ASLR) |
| Arch Lab | Ch4 | 流水线、冒险、转发 | 亲手写 SEQ→PIPE，理解分支预测 |
| Cache Lab | Ch6 | cache 模拟、分块矩阵 | 行优先 + 分块，CPE 直接砍半 |
| Tsh Lab | Ch8 | fork/信号/job 控制 | 信号处理要异步安全，`sigprocmask` 防 addjob 竞态 |
| Malloc Lab | Ch9 | 显式空闲链表/分离适配 | 对齐 16、合并、首适/最佳适权衡 |
| Proxy Lab | Ch10 | 短读写、并发 I/O | `readn/writen` 循环 + 线程池/缓存 |

本仓库实证：`github-repos/references/REKCARC-TSC-UHT/大二上/计算机系统概论/hw/计系概_bomblab/2014_lab/bomb590/`
- `bomb`：ELF 32-bit, Intel 80386, **dynamically linked, with debug_info, not stripped**（理想拆解对象）
- `bomb.s`：完整 `objdump -d` 反汇编（Phase 函数、`explode_bomb`、`strings_not_equal`、`read_six_numbers` 一应俱全）
- `solution.txt`：标准答案，可对照练习

拆弹标准姿势（拿本仓库这个 bomb 实操）：
```bash
cd .../计系概_bomblab/2014_lab/bomb590/
objdump -d -M intel bomb | sed -n '/<phase_1>:/,/^$/p'   # 看 phase_1
gdb ./bomb
(gdb) b explode_bomb
(gdb) b phase_1
(gdb) run
(gdb) x/s $rdi                  # phase_1 多半是字符串比较，答案就在眼前
```

---

## 一句话总结

CSAPP 不是"操作系统入门"，它是**给程序员的 X 光机**：让你看穿 C 代码到硬件的每一层，并在生产事故里按层下钻、快速定位。
读完它的标志不是你能背页表结构，而是——**下次线上炸了，你脑子里有一张"从比特到 syscall"的地图，知道该用哪条命令、往哪一层查。**

---

## 🎤 费曼挑战（真懂了吗？）

> **费曼法**：能讲给小学生听才算真懂。以下 5 个挑战覆盖 CSAPP 核心，**不参考资料**完成才算过关。
> 建议每天做一个，用 `python3 tools/feynman.py --source csapp` 记录。

### 挑战 1：补码与整数溢出（对应 Ch2）

| 层级 | 挑战 | 过关标准 |
|------|------|---------|
| **L1 复述** | 用 3 句话向 5 岁小孩解释"为什么计算机用补码而不是原码" | 小孩能复述"减法变加法" |
| **L2 联系** | 找一段你写过的代码，指出 `int` 累加器在哪里可能溢出 | 能说出具体行号和最大值 |
| **L3 创造** | 不参考资料，用 C 写一个安全的加法函数（溢出返回错误） | 用 `__builtin_add_overflow`，不是手写 `if(a+b<a)` |
| **L4 教学** | 向同事解释 `size_t i; for(i=len-1; i>=0; i--)` 为什么死循环 | 说出"`size_t` 无符号，`i>=0` 恒真" |

### 挑战 2：读汇编与 GDB 拆弹（对应 Ch3）

| 层级 | 挑战 | 过关标准 |
|------|------|---------|
| **L1 复述** | 向非程序员解释"为什么 C 程序员需要能读汇编" | 举出一个"只有看汇编才能发现"的 bug |
| **L2 联系** | 你最近一次 segfault 的 backtrace 看懂了吗？ | 能指出哪一行、哪个寄存器出错 |
| **L3 创造** | `objdump -d` 一个简单函数，逐行标注每个寄存器的作用 | `%rdi` 是第一个参数，`%rax` 是返回值... |
| **L4 教学** | 教非程序员朋友"程序在 CPU 里到底怎么跑的" | 用"做菜"比喻：寄存器=手，内存=冰箱 |

### 挑战 3：Cache 与缓存友好性（对应 Ch6）

| 层级 | 挑战 | 过关标准 |
|------|------|---------|
| **L1 复述** | 用"图书馆书架"比喻向小孩解释 CPU cache | 小孩能说出"常用的书放桌上" |
| **L2 联系** | 你的代码里哪里有 cache miss？怎么验证？ | 用 `perf stat -e cache-misses` 跑一遍 |
| **L3 创造** | 写一个 cache 友好的矩阵转置（分块） | CPE 比朴素版降 50%+ |
| **L4 教学** | 向运维解释"为什么加了超线程反而慢了" | 说出 false sharing 的原理 |

### 挑战 4：虚拟内存（对应 Ch9）

| 层级 | 挑战 | 过关标准 |
|------|------|---------|
| **L1 复述** | 为什么每个进程都以为自己独占内存？ | 说出"虚拟→物理的映射" |
| **L2 联系** | 你的程序 OOM 时到底发生了什么？ | 能用 `smaps` 或 `/proc/<pid>/status` 解释 |
| **L3 创造** | 画一张进程地址空间图（text/data/heap/stack/mmap） | 标注每个区域的地址范围和权限 |
| **L4 教学** | 向 PM 解释"内存不是真的满了，是虚拟地址空间的把戏" | PM 能理解"overcommit" |

### 挑战 5：按层下钻的 Debug 流水线（对应横向章）

| 层级 | 挑战 | 过关标准 |
|------|------|---------|
| **L1 复述** | 背出 9 层下钻的顺序（位/汇编/处理器/优化/存储/链接/异常/虚拟内存/IO） | 不看资料，全对 |
| **L2 联系** | 找一个你最近遇到的 bug，按 9 层逐步排查 | 能定位到具体哪一层 |
| **L3 创造** | 为你的项目写一份"按层下钻的 Debug 手册" | 每层至少一条可跑的排查命令 |
| **L4 教学** | 向团队做一次"按层下钻"的 brown bag 分享 | 10 分钟，带一个真实案例 |

---

> **自评规则**：每层 1-5 分。**任何一层低于 3 分 = 没真懂**，回去重读对应章节。
> 完成后用 `python3 tools/feynman.py --history` 查看你的成长轨迹。
