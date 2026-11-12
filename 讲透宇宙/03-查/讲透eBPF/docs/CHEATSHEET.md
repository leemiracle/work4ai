# eBPF 速查手册（CHEATSHEET）

> **定位**：docs/ 16 章知识库的**命令层索引**（一页通）——所有命令/宏/报错文案以章节原文为口径，细节回各章 N.M 节；**引用任何数字前先查 [../ERRATA.md](../ERRATA.md)**（33 条全局勘误总表，🔴必改/🟡带语境/🟢勿引用三级）。
> 素材章节：第 3（Verifier）/4（Maps）/5（程序类型）/6（Helpers）/7（加载与 libbpf）/9（XDP 与 tc）/11（可观测性）/15（工具链）章。

## 1. bpftool 子命令速查（第 7 章 7.3.5；第 15 章 15.2.6）

| 子命令 | 常用形态（原文口径） | 用途 |
|---|---|---|
| `prog` | `bpftool prog list` / `prog show id N` / `prog dump xlated id <ID>` / `prog dump jited id <ID>` | 列程序；反汇编 BPF 指令 / JIT 后本机码（排障神器） |
| `prog`（加载） | `bpftool prog load foo.o /sys/fs/bpf/foo`（可加 `-mcpu=v3`） | 手动加载重放，拒绝时吐 verifier log（第 3 章 3.3.1） |
| `map` | `map list` / `map dump name exec_start` / `map update` / `map lookup` / `map delete` / `map pin` | map 内省与读写 |
| `map`（排障） | `bpftool map show id <ID> -f` + `bpftool map dump` | 查 map 内容；BTF 化 map 直接显示结构体字段 |
| `link` | `link list` / `link pin` / `detach` / `update` | 谁挂在哪；link 生命周期 CLI 面 |
| `feature` | `bpftool feature probe`（可加 `unprivileged`，配 `\| grep bpf_`） | 一键探测本机 prog/map/helper 可用集（第 5/6 章） |
| `net` | `bpftool net attach xdp name xdp_count dev eth0`；`net list` | link 时代的 XDP 挂载入口；网卡 XDP/tc 挂载状态 |
| `btf` | `bpftool btf dump file /sys/kernel/btf/vmlinux format c` | **生成 vmlinux.h 的官方命令** |
| `gen` | `gen skeleton` / `gen object`（BPF 静态链接）/ `gen min_core_btf` | 构建流水核心三件 |
| `cgroup` / `perf` | `cgroup` 挂载树查询；perf event 查看 | cgroup/perf 内省 |
| `struct_ops` / `iter` | struct_ops 程序管理；BPF iterator 实例化 | 特殊类型 |

高频组合（7.3.5 原文）：加载失败先 `sudo ./app -v` 看 libbpf 日志；线上排障 `bpftool prog dump jited id N | head`；`bpftool prog list` 报 `Operation not permitted` = 撞上 bootstrap lsm 示例封禁了 `bpf()` 本身。

## 2. bpftrace one-liners 10 条（第 11 章 11.3.1 / 11.2.4）

| # | 命令（原文） | 回答什么 |
|---|---|---|
| 1 | `sudo bpftrace -e 'BEGIN { printf("hello world\n"); }'` | 安装验证（11.3.1） |
| 2 | `bpftrace -l 'tracepoint:syscalls:sys_enter_*'` | 列探针：先看有什么可挂 |
| 3 | `bpftrace -e 'tracepoint:syscalls:sys_enter_open { printf("%s %s\n", comm, str(args->filename)); }'` | 谁在开文件（静态 tracepoint 强类型 `args->`） |
| 4 | `bpftrace -e 'tracepoint:raw_syscalls:sys_enter { @[comm] = count(); }'` | 每进程 syscall 计数（map 聚合，退出自动打印） |
| 5 | `bpftrace -e 'tracepoint:syscalls:sys_exit_read /pid == 18644/ { @bytes = hist(args->retval); }'` | read() 字节数 log2 直方图 |
| 6 | `bpftrace -e 'kretprobe:vfs_read { @bytes = lhist(retval, 0, 2000, 200); }'` | 同指标的 kretprobe 对照组（lhist 线性直方图） |
| 7 | `bpftrace -e 'profile:hz:99 { @[stack] = count(); }'` | 采样 on-CPU 栈 → 火焰图原料 |
| 8 | `bpftrace -e 'tracepoint:block:block_rq_complete { @ = hist(args->nr_sector * 512); }'` | 块 I/O 完成尺寸分布 |
| 9 | `kprobe:vfs_read { @start[tid] = nsecs; }` + `kretprobe:vfs_read /@start[tid]/ { @ns[comm] = hist(nsecs - @start[tid]); delete(@start[tid]); }` | 延迟测量通用范式：enter/exit 双探针 + 时间戳 map（键用 tid；`/@start[tid]/` 过滤防半程捕获假值）（11.2.4） |
| 10 | `bpftrace -l \| grep madvise` + `cat /sys/kernel/debug/tracing/events/syscalls/sys_enter_madvise/format` | 零文档猜探针参数标准解法：format 文件 + 头文件 grep |

铁律（11.2.1/15 章 Gregg 五原则）：动态插桩不是稳定 API，**优先静态 tracepoint/USDT**；输出通道要分布→map 直方图，要逐事件→ringbuf，printk 只看两眼。

## 3. libbpf 常用 API 两栏表（第 7 章 7.2/7.3；第 4 章 4.2.4；第 6 章 6.3.1）

| 任务 | BPF 侧（内核态宏/helper） | 用户态侧（libbpf/skeleton） |
|---|---|---|
| map 声明 | 现代：`struct { __uint(type,...); __type(key,...); __type(value,...); } x SEC(".maps")`；legacy：`struct bpf_map_def SEC("maps")`（三代识别特征见 4.2.7） | load 时自动创建；`bpf_object__find_map_by_name()` + `bpf_map__fd()`；skeleton 直达 `skel->maps.<name>` |
| map 读写 | `bpf_map_lookup_elem(map, key)`（**必须判 NULL**）/ `bpf_map_update_elem(map, key, value, flags)`（`BPF_ANY/NOEXIST/EXIST`）/ `bpf_map_delete_elem` | 低层 `bpf_map_create/lookup_elem/update_elem/delete_elem`；bcc 侧 `b["map"][key]` 像 dict |
| 事件输出 | `bpf_ringbuf_reserve(&rb, sizeof(*e), 0)` → 填数据 → `bpf_ringbuf_submit(e, 0)`（5.8+ 首选；失败可 `discard`）；旧：`bpf_perf_event_output(ctx, map, flags, data, size)` | `ring_buffer__new(bpf_map__fd(skel->maps.rb), handle_event, NULL, NULL)` + `ring_buffer__poll(rb, 100)`；另有 `consume` / `epoll_fd` / `free` |
| 读内存 | `bpf_probe_read_user/_kernel(_str)`（5.5 拆分后显式选域；`_str` 返回值即长度） | — |
| 进程/时间 | `bpf_get_current_pid_tgid()`（`tgid<<32\|pid`）/ `bpf_get_current_comm()` / `bpf_get_current_cgroup_id()` / `bpf_ktime_get_ns()` | — |
| tracing 取参 | `BPF_PROG(name, ...)`（fentry 按 BTF 签名直读）；`BPF_KPROBE(name, args...)` / `BPF_KRETPROBE(name, int ret)`（pt_regs 展开） | 手动 attach：`bpf_program__attach_uprobe_opts(skel->progs.X, 0, "/proc/self/exe", 0, &opts)`；link 存 `skel->links.*` |
| CO-RE | `BPF_CORE_READ(task, real_parent, tgid)` | 重定位在 load 期自动完成（对照 `/sys/kernel/btf/vmlinux`） |
| 全局变量 | `int my_pid = 0;`（.bss/.data/.rodata 内部即 map，5.5+） | `skel->bss->my_pid = getpid()`——mmap 直写**零 syscall**；`const volatile` 必须在 open 与 load 之间赋值 |
| license | `char LICENSE[] SEC("license") = "Dual BSD/GPL";`（GPL 兼容才开放 gpl_only helper） | — |
| 生命周期 | — | `bpf_object__close()` / `skel__destroy()`；复用 pinned map：`bpf_map__reuse_fd(map, bpf_obj_get("/sys/fs/bpf/..."))`；`bpf_object__pin_maps(obj, dir)` |

**skeleton 三段式**（`bpftool gen skeleton app.bpf.o > app.skel.h` 生成，7.2.2/7.2.6）：

| 阶段 | API（minimal 例） | 做什么 |
|---|---|---|
| ① open | `minimal_bpf__open()` | 解析 ELF、**不碰内核**；参数化窗口（bss/rodata 赋值、set_pin_path 等） |
| ② load | `minimal_bpf__load()`（或 `__open_and_load` 一步） | BPF_BTF_LOAD + MAP_CREATE×N + CO-RE 重定位 + map fd 指令重写 + PROG_LOAD→verifier→JIT |
| ③ attach / destroy | `minimal_bpf__attach()`（按 SEC 名自动挂）/ `minimal_bpf__destroy()` | 产出 `struct bpf_link`；destroy = detach + free |

## 4. SEC 宏 → 程序类型 → attach 方式对照（第 5 章 5.2；SEC 名以 libbpf.c `section_defs[]` 为源）

| SEC 写法 | prog_type（引入） | context / 取参 | 返回值语义 | attach 方式 |
|---|---|---|---|---|
| `SEC("xdp")` | XDP (4.8) | `struct xdp_md`（data/data_end，无 skb） | `XDP_PASS/DROP/TX/REDIRECT/ABORTED`（ABORTED 实际按丢包） | `ip link set dev eth0 xdp obj prog.o sec xdp`；link 时代 `bpftool net attach xdp name X dev eth0` |
| `SEC("xdp.frags")` | XDP 多缓冲声明 | 同上（声明支持 scatter-gather） | 同上 | 同上；可移植代码限 18 frag（第 9 章 9.2.6） |
| `SEC("socket")` | SOCKET_FILTER (3.19) | `struct __sk_buff` | 接受字节数：0=丢弃，非 0=截断放行；全收 `return skb->len` | 第一代 `setsockopt(SO_ATTACH_BPF)` |
| `SEC("tc")`/`classifier`/`action`（**已 deprecated**）→ 用 `tcx/ingress`、`tc/ingress`（别名）、`tc/egress` | SCHED_CLS (4.1) | `struct __sk_buff` | direct-action 返回 `TC_ACT_OK/SHOT/PIPE/RECLASSIFY/UNSPEC` | `tc filter add dev eth0 ingress bpf da obj prog.o sec cls` |
| `SEC("kprobe/<函数>")` | KPROBE (4.1) | `struct pt_regs`；`BPF_KPROBE` 宏取参；注意 `__x64_` 前缀跨版本写法 | 通常 0（忽略） | 第一代 perf_event_open()+ioctl；现代 libbpf 自动 attach |
| `SEC("tp/<类别>/<事件>")`（如 `tp/sched/sched_process_exec`、`tp/syscalls/sys_enter_write`） | TRACEPOINT (4.7) | tracepoint 特定 ctx，`args->xxx` 强类型 | 0 | libbpf 按 SEC 名自动 |
| `SEC("fentry/<函数>")` / `fexit` / `fmod_ret`（同属 `tp_btf`/`iter` 等一个类型多 attach 点） | TRACING (5.5) | BTF 化函数签名，`BPF_PROG` 宏参数直接可读；fexit 天然拿返回值 | 0（fmod_ret 可改返回） | BPF trampoline + link 路径（BPF_LINK_CREATE）；**硬依赖内核 BTF** |
| `SEC("fentry.s+...")` / `lsm.s+` / `usdt.s+`（`.s` sleepable 变体） | 同各自基类型 | 可睡眠上下文 | 同基类型 | 挂载点本身必须支持 sleepable，乱用照样拒载 |
| `SEC("uprobe//proc/self/exe:uprobed_sub")`（路径+符号写死）/ 裸 `SEC("uprobe")`（类型待定） | uprobe（KPROBE 寄存器约定） | `BPF_KPROBE`；目标函数须 `noinline` 防内联 | 0 | 写死符号→`__attach()` 全自动；裸的→`bpf_program__attach_uprobe_opts()` 手动 |
| `SEC("uretprobe//proc/self/exe:uprobed_sub")` | uretprobe | `BPF_KRETPROBE(name, int ret)` 首参即返回值 | 0 | 同上 |
| LSM 钩子位（`lsm.s+` 变体，5.7） | LSM (5.7) | 钩子特定 ctx | `-EPERM` 族否决码 | link 路径（BPF_LINK_CREATE） |
| cgroup 族（bind4/6、connect4/6、sendmsg4/6 等 18 个 attach 点） | CGROUP_SOCK_ADDR (4.17)；CGROUP_SKB (4.10) 等 | cgroup ctx | SOCK_ADDR：0 放行/负值拒绝且**可改写目标地址**；SKB：1 放行/0 丢 | 旧式 `BPF_PROG_ATTACH`（cgroup 等） |
| `SEC("struct_ops/...")` | STRUCT_OPS (5.6) | 以 map 形式注册内核 ops 结构体（tcp_congestion_ops/sched_ext_ops 等 6 对象） | 原内核 ops 语义 | struct_ops 专用通道 |
| `SEC("syscall")` | SYSCALL (5.15) | 程序本身即 syscall body | syscall 语义 | 从 BPF 内发起长任务（如生成 ringbuf 事件） |
| `SEC("perf_event")` | PERF_EVENT (4.9) | `struct bpf_perf_event_data` | 0 | perf_event_open() 定时采样（`profile:hz:99` 的 C 侧对应物） |

注意（5.4）：`tc` 系 SEC 名代差已钉版——旧 `SEC("tc")`/`classifier`/`action` 被 libbpf 源码注释标 deprecated，现为 tcx 语义别名；`+` 后缀表示可附加参数（如 `kprobe/do_unlinkat`）。

## 5. verifier 高频报错 → 原因 → 对策（第 3 章 3.4.1；四步读法 3.3.2）

| 报错句（原文缩略） | 根因 | 对策 |
|---|---|---|
| `invalid mem access 'inv'` / `R1 invalid mem access` | 解引用值未知的标量或未验证指针；tracing 直接解引用 `ctx->rdi` 也撞 | tracing 先 `bpf_probe_read` 拷到栈再访问；网络补 data/data_end 或 map value 边界检查 |
| `math between pkt pointer and register with unbounded min value` | packet 指针加了无下界（可能为负/巨大）的标量 | 加数用显式无符号类型（如 `__u16`）；先与常量比较把界验出来 |
| `unreachable instruction` | 死代码；常见于编译器生成的 switch jump table | 编译加 `-fno-jump-tables`（bpf Devel Q&A 钦点） |
| `infinite loop detected` / `back-edge` | 5.3 前一切循环禁；5.3 后界无法静态证明也不行（verifier 要确定性保证） | 常量界循环；变界用 `bpf_loop`；或 tail call 展开范式 |
| `invalid read from stack off -X size N` | 读没写过的栈槽（信息流安全防线，非语法洁癖） | 先写后读 |
| `call to built-in function '__adddf3' is not supported` | 浮点——BPF 无 FPU | 定点化/整数运算，别用 float/double |
| `program too large` | 超 BPF_MAXINSNS=4096 或撞 100 万探索上限 | 拆函数/减分支/tail call 复用栈绕过单程序限制 |
| EACCES（无细节） | verifier 判 unsafe 的总返回码 | bpf(2) 手册建议带 `log_level=1` 重试拿日志 |

**verifier log 四步读法**（3.3.2）：①定位**末行错误句**（唯一判死刑的行）→ ②解码出错指令行 `1617: (0f) r1 += r2`（`PC: (十六进制 opcode) 反汇编`）→ ③解码其上状态行（`R7=ctx` context 指针；`R8=inv(id=0,umin_value=...,umax_value=...,var_off=...)` 标量区间+tnum；`fp-232=map_value` 栈槽状态）→ ④PC 映射回源码：`llvm-objdump -S -no-show-raw-insn prog.o`（编译加 -g）或 BTF line_info 直接关联源行。拿 log 四条路（3.3.1）：`libbpf_set_print()` 回调 / `bpftool prog load` 手动重放 / bpf(2) attr 带 log_buf+log_level / test_verifier.c 回归集。经验（Maguire）：verifier 报的错"通常是真 bug"；少数是编译器优化骗过直觉——看 llvm-objdump 而非 C 源码。

## 6. map 类型选型小表（第 4 章 4.2.2/4.2.5/4.4）

| 需求 | 选型（版本） | 关键语义/坑 |
|---|---|---|
| 任意 key 的有界关联状态（连接表/进程表） | HASH (3.19) | update **原子替换**整个 entry；会满（E2BIG） |
| 定长索引、最快查找、全局变量前身 | ARRAY (3.19) | 元素预分配零初始化、不可删（delete 恒 EINVAL）；update 非原子（大 value 撕裂读）；单元素 ARRAY=全局变量经典前身 |
| 高频计数/直方图，无锁 | PERCPU_HASH / PERCPU_ARRAY (4.6) | 每核一份 value；读侧按核求和；**核数按 `/sys/devices/system/cpu/possible`** 计（VMware vcpu.hotadd 坑） |
| top-N 热点，满了自动逐出 | LRU_HASH / LRU_PERCPU_HASH (4.10) | 命名陷阱：LRU_PERCPU 不是每核一张表，是全核共享表+每核独立淘汰 |
| 逐事件送用户态 | RINGBUF (5.8) | 全 CPU 共享单环；reserve/submit 两段式省一次拷贝；自适应唤醒；官方口径"5.8+ 首选"；<5.8 降级 PERF_EVENT_ARRAY (4.3)（须先 perf_event_open 逐核塞 fd） |
| 路由表/ACL 网段匹配 | LPM_TRIE (4.11) | 最长前缀匹配，前缀 1–256 字节 |
| 同一 entry 多步更新的互斥 | HASH/ARRAY value 内嵌 `struct bpf_spin_lock` | BTF 描述强制、仅 root、一次一把、持锁禁一切调用、tracing/socket filter 不可用 |
| 跳转表/转发面 | PROG_ARRAY (4.2)；DEVMAP (4.14)/CPUMAP (4.15)/XSKMAP (4.18) | tail call 静默 fall-through；redirect 走 map 版 13.0Mpps vs helper 版 7.5Mpps |

铁律（4.4）：`bpf_map_lookup_elem` 返回必须判 NULL 才能解引用——新手第一个 verifier 报错多源于此。

## 7. 排障四板斧命令（第 15 章 15.2.6；"加载了但行为不对"场景）

| # | 命令（原文口径） | 看什么 |
|---|---|---|
| ① | `cat /sys/kernel/debug/tracing/trace_pipe` | `bpf_printk` 调试输出（仅开发期，生产禁用） |
| ② | `bpftool prog`（拿 id）→ `bpftool prog dump xlated id <ID>` / `bpftool prog dump jited id <ID>` | 翻译后的 BPF 指令 / JIT 后本机机器码（实证例：`bpftool prog dump jited id 42`） |
| ③ | `llvm-objdump -S -g xxx.bpf.o` | 带源码行号的反汇编，把指令对回 C 源 |
| ④ | `bpftool map show id <ID> -f` + `bpftool map dump` | map 内容是否符合预期；BTF 化 map 直接显示结构体字段 |

相邻两段（15.2.6）：**加载失败/verifier 拒绝** → 先拿 verifier log（libbpf 的 `libbpf_print_fn` 回调 / BCC 直接抛异常），`bpftool prog load` 手动重放可剥离加载器因素，拒绝原因字典见块 5；**性能/底层正确性** → `bpf_jit_disasm` 反汇编 JIT 镜像（需 `/proc/sys/net/core/bpf_jit_enable=2`）。加载链与生命周期的"为什么"回第 7 章。

## 回查索引（块 → 章节）

| 块 | 章节锚点 | 块 | 章节锚点 |
|---|---|---|---|
| 1 bpftool | 7.3.5 / 15.2.6 / 3.3.1 / 5.3 / 6.3.4 | 5 verifier | 3.3.1-3.3.2 / 3.4.1 |
| 2 bpftrace | 11.3.1 / 11.2.4 | 6 map 选型 | 4.2.2 / 4.2.5 / 4.4 |
| 3 libbpf API | 7.2.2 / 7.2.6 / 4.2.4 / 6.3.1 | 7 四板斧 | 15.2.6 |
| 4 SEC 对照 | 5.2.2 / 5.2.4 / 7.3.2-7.3.3 | 数字引用 | 一律先查 [../ERRATA.md](../ERRATA.md) |
