# explain-11 · stub 头机制代表：lib/include/sys/mutex.h（覆盖-undef-重定义三板斧）

## 角色定位

lib/include/ 目录（sys/amd64/i386/vm 四棵子树）是移植层的"声明基座"：它让 freebsd/ 内核源码 `#include <sys/mutex.h>` 时，命中的不是内核原头而是 F-Stack 的改写版。mutex.h（91 行）是这套机制最纯粹的代表——**覆盖（override）与放行（pass-through）并存**：锁操作全部塌缩成 DO_NOTHING，结构体定义却保留真身。机制成立的唯一支点是 Makefile:16 的 `OVERRIDE_INCLUDES_ROOT:=${CURDIR}/include` + :73 把它排在 FreeBSD 树（kern.pre.mk 的 -I$S）之前。理解了这一个文件，param.h 的纯放行、rwlock.h/sx.h 的同款 DO_NOTHING、amd64/counter.h 的原子计数、vm/uma_int.h 的 slab 内部结构就全是同一模式的变化题。

## 内部结构

mutex.h 全文就是三段式：① `#include_next <sys/mutex.h>`（`:29`）——GCC 扩展，跳过当前命中目录继续搜后面的搜索路径，把 freebsd/sys 的真 mutex.h 整个包含进来（于是 struct mtx 布局、MTX_* 常量、函数声明都是内核原味；真正被改写的 struct 定义在配套的 lib/include/sys/_mutex.h:36-42——embed 的是 ff_mutex_t 而非内核的 vmem/adaptive 字段）；② 十几行 #undef（`:31-55`）——内核原头把 mtx_lock 展开成带 witness/争用统计的 inline 或宏，全部拆掉；③ 重定义（`:57-88`）：四组加解锁宏 → DO_NOTHING（`__mtx_lock :59` 等）、trylock 三兄弟 → 恒 1（`:74-76`，单线程永远"抢得到"）、mtx_owned → 恒 1（`:85`，断言"我持有"永真）、DROP_GIANT/PICKUP_GIANT → 空转（`:87-88`，Giant 锁时代遗迹）；唯二的真函数是 mtx_init → ff_mtx_init（`:80-81`，在 ff_lock.c:91 做 lock_init 初始化 lock_object，挂 lock_class_mtx_sleep）与 mtx_destroy → DO_NOTHING。

## 外部连接

编译期：lib/Makefile 的 include 顺序是全部魔法——OVERRIDE 目录在最前、内核树在后、include_next 负责穿透；这就是"协议栈源码一行不改也能链接进用户态"的机关。运行期：ff_lock.c 提供五个 lock_class（mtx_sleep/mtx_spin/rw/sx/rm），lock_class_mtx_sleep 的 lc_lock/lc_unlock 是**空函数**（ff_lock.c:53-62），assert 也空（`:50`）——锁类系统完整保留（witness、名字、递归标志）但加解锁零成本；真实并发保护不在这里，而在数据面自己的 rte_spinlock（如 ff_dpdk_if.c:3767 的 ifp_create_lock）。结构体伴生字段 ff_mutex_t 只是 `volatile uintptr_t`（ff_host_interface.h:64）——占位对齐而非 pthread。兄弟头各司其职：rwlock.h 同款 7 处 DO_NOTHING、sx.h/turnstile.h 纯声明放行、condvar.h 保留 struct cv{desc+ff_cond_t}（`:51`）由 ff_kern_condvar.c 实现"睡眠唤醒退化为立即返回"。

## 数据流

一次 freebsd/ 代码里的 `mtx_lock(&sc->mtx)` 在本仓的编译结果：预处理命中本头 → 展开为 `((void)0)` → 生成零指令（编译器直接消除）。一次 mtx_init(&m,"name",NULL,MTX_DEF)：展开 ff_mtx_init(&m.lock_object,...) → lock_init 挂上 lock_class_mtx_sleep、记录名字与选项 → 之后 mtx_assert/mtx_owned 全部永真通过。如果这段代码被多线程并发执行（thread_mode=1 或 FF_MULTI_SC），锁不提供任何保护——真正的互斥由上层架构保证（每线程独立协议栈实例、cc_cpu __thread 化、UMA per-thread 化）。这就是 F-Stack"单线程 FreeBSD 栈"的全部含义：不是删掉锁调用，而是把锁编译成空气，同时保留锁的"形状"（结构体、初始化、锁类）让栈代码零改动。

## 设计决策

① **include_next + #undef 而非 fork 整个头文件树**：结构体演进（FreeBSD 13→14→15）时只需跟进真正变化的结构，锁语义的改写集中在一个文件——比维护完整 fork 头树低一个数量级的心智负担；代价是依赖 GCC 扩展且对 -I 顺序极度敏感（Makefile:73 那行挪到 KERNPREINCLUDES 之后就全盘失效）。② 保留 mtx_init 为真函数而非 DO_NOTHING：lock_object 的初始化让 sysctl/witness/KASSERT 体系还能自洽运转，锁的"存在感"对栈代码可见——删干净反而会在 lock_class 引用处炸链接。③ trylock/owned 恒真而非恒假：单线程里"尝试加锁"必然成功、"是否持有"必然为真，返回假会触发栈内大量 retry 循环变成死循环。④ DROP_GIANT 空转：Giant 是 SMP 化前的全局锁，用户态单线程里它语义上就"永远被你持有"，放下再拿起是纯开销。

## 新人提示

判断"某个内核头在本仓是被改写还是放行"，直接看 lib/include 下有没有同名文件：有且含 #undef 重定义 = 改写；有但只有 include_next（param.h）= 显式放行占位；没有 = 完全走内核树。改 freebsd/ 树新增源文件时遇到 undefined reference to __mtx_lock_flags 之类，先查是不是没把 OVERRIDE 目录放进编译单元的 -I。**绝不要**在 lib/ 下引入第二个含锁语义的头改写（比如想让某处真加锁）——那会制造"有的锁是真锁有的锁是假锁"的幻觉，正确做法是像 ff_dpdk_if.c 一样用 rte_spinlock 在数据面自己的层面解决。thread_mode=1 的多线程栈依赖"每线程一套栈状态"而不是这些锁，动 cc_cpu/pcpu 相关代码前先重读 explain-03 的 __thread 约定。
