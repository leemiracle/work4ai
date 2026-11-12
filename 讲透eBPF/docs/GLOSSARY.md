# eBPF 知识库术语表（GLOSSARY）

> **这是本知识库（docs/ 01-16 章）的配套术语表**。全部词条的定义口径=16 章原文（各章又锚定 awesome-ebpf 语料库 288 条资源），含关键约束与数字均照录章节表述；词条名用英文、定义用中文。同名易混词在各词条内附辨析（XDP action vs tc verdict、fentry vs kprobe、ringbuf vs perf event array、tail call vs pseudo call、CO-RE vs BTF 等）。**引用前可查 [../ERRATA.md](../ERRATA.md) 核对勘误状态**；条目按主题分组：机制类 / 程序与挂载类 / 工具链类 / 数据面类 / 可观测类 / 安全类 / 生态类。

---

## 一、机制类（VM、Verifier、Maps、Helpers、CO-RE/BTF）

**cBPF（classic BPF，经典 BPF）**——1992 年 McCanne & Jacobson 论文定义的原始包过滤伪机：accumulator A + index register X + scratch M[]，定长指令 `opcode:16 jt:8 jf:8 k:32`，return 值=保留字节数（0 即丢包）；1997 年进入 Linux 2.1.75（作者口径），seccomp v2 与 cls_bpf 早期均用它，加载时被内核透明翻译为 eBPF。→ 详见第 1、2、12 章

**eBPF / BPF（命名钉版）**——RFC 9669 历史注记正式钉死"BPF 已是独立术语、不再是 Berkeley Packet Filter 的缩写"；内核源码里只有 BPF，社区语境"BPF 即 eBPF"。→ 详见第 1、2 章

**bpf() syscall**——3.18（2014-12）暴露给用户态的多路复用系统调用，`union bpf_attr` 按 cmd 取成员，五大命令族=MAP/PROG/OBJ 枚举/ATTACH-LINK/BTF；libc 不提供包装函数，必须走 `syscall(__NR_bpf, ...)` 且传参前完整清零 attr。→ 详见第 1、7 章

**BPF VM（eBPF 虚拟机）**——被刻意造小的寄存器型 RISC 机：11 个 64 位寄存器 r0-r10 + 隐含 PC + 512 字节固定栈；设计为"真 CPU 指令的混合物"（作者口径约 10% cBPF+70% x86+25% arm64+5% risc，幻灯片加总 110% 属笔误），调用约定与 amd64/arm64 ABI 一对一使 JIT 退化为改名翻译。→ 详见第 2 章

**R0-R10 寄存器约定**——r0=返回值；r1-r5=函数调用参数（程序入口 r1=context，helper 最多 5 参即源于此）；r6-r9=callee-saved；r10=只读帧指针；r1-r5 只能存数字或栈指针、永不存任意内存直接指针（刻意简化 verifier 内存模型）。→ 详见第 2 章

**struct bpf_insn（指令编码）**——每条指令 64 位定长：`opcode:8 | dst:4 | src:4 | off:16 | imm:32`，与 RFC 9669 basic encoding 一致；opcode 低 3 位是指令类（LD/LDX/ST/STX/ALU32/JMP64/JMP32/ALU64 八类；32 位 ALU 写回即高 32 位清零、除零不陷阱——DIV 除零 dst=0）；注意字节序坑——regs 字节 nibble 顺序随宿主端序翻转。→ 详见第 2 章

**ldimm64（宽指令）**——唯一的 128 位指令形态（opcode 0x18 后跟一条全零伪指令），src_reg 复用为子类型：0x1=BPF_PSEUDO_MAP_FD、0x2=map value 首地址、0x3=平台变量地址等；map fd"加载期重定位"的机制本体。→ 详见第 2 章

**BPF_PSEUDO_MAP_FD**——src_reg=1 的 ldimm64 伪指令：编译器埋 fd 占位，verifier 加载时查 fd 把指令改写为真实内核 map 指针（resolve_pseudo_ld_immq），是 loader 与内核之间唯一的重定位通道（tc 时代契约"仅允许 map 相关重定位"）。→ 详见第 2、3、4、7 章

**tail call（尾调用）**——`bpf_tail_call(ctx, prog_array, index)`：不是函数调用、永不返回——复用同一栈帧跳进 PROG_ARRAY 里的另一程序，原程序整体终止；上限 MAX_TAIL_CALL_CNT（现代 man 页 33，4.14 时代文献写 32）；跳转失败（越界/超层数）静默 fall-through 继续执行原程序；跨程序传状态只能靠 per-CPU map 或 skb->cb。**辨析：与 BPF-to-BPF pseudo call 的本质区别是"复用栈帧的跳转 vs 有独立栈帧、可返回的普通函数调用"；两者混用在 x86_64 需 5.10+。**→ 详见第 2、4、6 章

**pseudo call（BPF-to-BPF call）**——call 指令 src_reg=1 的程序内静态函数调用：imm 为相对偏移，受"调用链合计栈深 ≤512B（大栈架构 2KiB）"约束（tail call 受跳转层数约束）；用户态实现调用深度上限各异（uBPF/rbpf 均 MAX_CALL_DEPTH=8）。→ 详见第 2、6 章

**512 字节栈**——eBPF 程序的固定栈尺寸（程序不可写 r10 之外自增栈）；x86-64/arm64 等"大栈"架构 JIT 下可达 2KiB、含 BPF-to-BPF 调用链合计。→ 详见第 2 章

**BPF_MAXINSNS=4096**——非特权程序对外可见的指令数上限；verifier 内部路径探索上限 100 万条（5.2 起，4.14 时代为 64k 分析总长+1k 分支）；uBPF 另有自己的 65536 上限。→ 详见第 2、3 章

**bounded loop（有界循环）**——5.3 起 verifier 支持的循环形态：必须能静态证明出口条件必然为真；此前一切循环被 CFG 无后向边规则禁止（出路=编译期展开或 tail call 模拟）；概率上几乎必然终止的随机循环照样被拒——verifier 要确定性保证。变界循环用 bpf_loop helper（≤1<<23 次）。→ 详见第 1、2、3 章

**JIT 编译**——`bpf_prog_select_runtime` 把通过验证的指令一对一翻译为本机机器码（x86_64 后端主循环 do_jit），生产主流路径，"JIT 后与原生内核 C 代码无法区分"；架构支持逐个落地（x86-64/ARM32/ARM64 自 3.18，riscv 自 5.1）。→ 详见第 2 章

**解释器（interpreter）**——`___bpf_prog_run`（kernel/bpf/core.c）单 switch 逐指令模拟，JIT 不可用时的兜底；RFC 9669 Security Considerations 判其为不安全源（推测执行侧信道 gadget），推荐只用 JIT；内核对应物 CONFIG_BPF_JIT_ALWAYS_ON（既是 Spectre 缓解也是无 JIT 架构必选项）。→ 详见第 2 章

**constant blinding（常量盲化）**——把指令立即数拆分混淆、防 JIT spraying（2011-2013 年 BPF JIT off-by-one 提权实录教训：攻击者在 JIT 镜像里拼出 x86 机器码拿内核执行）；2016 年起为通用基础设施，配套 bpf_jit_harden。→ 详见第 1、2 章

**Helper（helper functions）**——eBPF 的"系统调用层"：程序不能调任意内核函数，只能调内核白名单内的 helper（v7.0 man 页文档化 211 个，13 功能族）；最多 5 个参数（r1-r5 传参寄存器只有 5 个）、每个 program type 只能用子集、JIT 后直连编译后的内核函数零 FFI 开销。稳定性：helper 集合与签名是 UAPI（不许 breaking change），但其背后读到的内核结构体数据不保证稳定（那半块归 CO-RE）。白名单的 verifier 侧实现：每个 program type 注册 `struct bpf_verifier_ops` 三回调（get_func_proto=允许哪些 helper、is_valid_access=context 字段合法性、convert_ctx_access=访问改写为真实偏移；读源码要顺着 default 委托链如 bpf_base_func_proto 追完才是真实可用集）；helper×map 兼容矩阵由 verifier.c 的 check_map_func_compatibility 把关。→ 详见第 5、6 章

**GPL-only helper**——标记 gpl_only 的 helper（经验规律：读内核内部结构的 probe_read_kernel/get_current_task/get_stack/fib_lookup 等几乎全是）仅对 GPL 兼容 license 字符串（六种可接受写法）的程序开放；tracing 类程序整体须 GPL、网络类可专有——闭源商业 eBPF 程序因此几乎只能做网络数据面。→ 详见第 1、5、6、16 章

**Verifier（加载时验证器）**——kernel/bpf/verifier.c 的静态分析器（主入口 bpf_check），"横在我们程序与毁灭深渊之间的唯一东西"（David Miller）：加载时一次性证明三件事——内存访问永不越界、寄存器/栈先初始化再读（防内核数据泄漏）、有限步终止；证明通过后运行时零检查开销（与 Java/WASM 沙箱的本质区别）。它不只是审查者还是改写器：map fd 换内核指针、context 抽象字段偏移换真实偏移、helper 编号换真实函数地址。官方哲学："kernel rejects all programs that it cannot prove safe"；判断程序能否被接受的唯一办法就是试着加载它。→ 详见第 3 章

**verifier 两遍（check_cfg → do_check）**——第一遍 check_cfg：建控制流图做深度优先搜索，强制四规则=≤4096 条指令、无后向边（禁循环，5.3 后改为有界）、无不可达指令、无越界/畸形跳转（程序必须是 DAG 有向无环图）；第二遍 do_check 是 verifier 主体：从第一条指令出发 DFS 穷举所有控制流路径（条件跳转 fork 两份状态、跳转栈压栈回走），逐条指令更新寄存器与栈槽抽象状态；寄存器类型系统（PTR_TO_PACKET+有界标量→仍是指针，指针+指针直接非法）；读未写过的栈槽=拒绝（信息流安全防线）；到达 exit 时 R0 必须持有已初始化合法返回值。→ 详见第 3 章

**state pruning（状态剪枝）**——verifier 记录每个指令位置已见过的寄存器约束状态，新路径到达时若旧状态比新状态更严格则不再探索该分支，抗路径爆炸；有顺序敏感性（条件判断位置挪一挪可验证性会变），PREVAIL 指出这正是内核算法不 scale 的根源。→ 详见第 3 章

**verifier log**——验证失败的拒绝日志：行首数字=指令序号，`R1=ctx`/`R10=fp`/`R8=inv(umin_value=…)` 等寄存器状态行+`PC: (opcode) 反汇编`行；log_level=1 每条指令后都 dump；buffer 太小本身会导致加载以 -ENOSPC 失败（libbpf 策略=失败后递增 buffer 重试）；BTF line_info 可让它直接标注 C 源码行。寄存器取值推理基于 tnum（tristate number，三值数）：确定位+自由位（`var_off=(0x0; 0x7fc)`=低 10 位不确定），与 umin/umax 值域区间共同构成寄存器状态（kernel/bpf/tnum.c）。→ 详见第 3 章

**PREVAIL**——PLDI'19 论文的用户态形式化验证器（vbpf/ebpf-verifier 仓，eBPF for Windows 的验证器标准件）：抽象解释路线，Zone domain（X−Y≤C 差界矩阵）选型，join/widening 求不动点天然支持循环验证（2019 年即支持）；192 个真实程序仅 1 个 false positive、单程序 ≤5.2s；CLI `bin/prevail <elf> <section> <function>` 输出 PASS/FAIL，支持 --termination 与 --failure-slice（致错最小指令切片）。→ 详见第 3、14 章

**Map（eBPF maps）**——bpf() 创建的内核态键值对象（用户态拿 fd），"eBPF 世界的统一状态交换机制"：内核→用户态出结果、用户态→内核灌配置、程序↔程序共享状态三个方向；广义上全局变量（.bss/.data/.rodata 段）底层也是内部 map；Jesper Brouer 论断：hook 只定义 action 集、用户策略全走 map，终结了"每来一个新策略就造一个内核 ABI"的循环。程序侧访问一律走 helper，map 引用走伪指令。→ 详见第 4 章

**BPF_MAP_TYPE_HASH / ARRAY**——两大基础容器（均 3.19）：HASH 任意字节串 key→value、update 是原子替换、会满（E2BIG）；ARRAY 4 字节索引、最快查找（可内联成常量指针）、元素预分配零初始化不可删、update 非原子（大 value 有撕裂读风险）。→ 详见第 4 章

**per-CPU map（PERCPU_HASH / PERCPU_ARRAY）**——每核一份 value、天然无锁（4.6 引入动机即 "allows for lock free uses"），高频计数/直方图首选；代价=读侧按核求和、内存×核数；核数必须按 `/sys/devices/system/cpu/possible` 计而非 get_nprocs_conf()（VMware vcpu.hotadd 会虚报）。→ 详见第 4 章

**LRU_HASH / LPM_TRIE / QUEUE / STACK / BLOOM_FILTER**——特种容器：LRU（4.10）满时自动逐出最近最少使用项（命名陷阱：LRU_PERCPU_HASH 是全核共享表+每核独立淘汰结构）；LPM_TRIE（4.11）最长前缀匹配，路由/ACL 专用；QUEUE/STACK（4.20）无 key FIFO/LIFO；BLOOM_FILTER（5.16）概率型成员判定。→ 详见第 4 章

**bpf_map_lookup_elem 判空铁律**——lookup 未命中返回 NULL，返回值必须先判空才能解引用——bcc 教程第 4 课点名的 verifier 规则，新手第一个 verifier 报错多源于此。update flags 三态：BPF_NOEXIST/BPF_EXIST/BPF_ANY，ARRAY 上禁用 NOEXIST（元素恒存在）。→ 详见第 4 章

**bpf_spin_lock**——map value 内的真互斥（约束最多的 helper 之一）：只能放 HASH/ARRAY value 顶层、BTF 描述强制、一次一把、持锁期间禁一切 helper 与 BPF-to-BPF 调用、所有路径必须显式 unlock、root only、tracing/socket filter 程序不可用、map-in-map inner 禁用；syscall LOOKUP/UPDATE 都跳过锁字段（用户态看到的 value 与内核态不逐字节相同）。→ 详见第 4、6 章

**RINGBUF（BPF_MAP_TYPE_RINGBUF）**——5.8 引入的流式事件 map："Starting in Linux 5.8, this should be the preferred method for pushing per-event data to user space"。**辨析（vs perf event array）：全 CPU 共享单环 vs 每核一环；reserve/submit 两段式（在 ring 里预留直接填充）省一次拷贝且可 discard vs perf_submit 一步提交；不需要 ctx 参数；自适应唤醒（flags 0=消费者忙就不发通知）；libbpf ring_buffer__poll 可聚合多 map 到一个 epoll fd；USER_RINGBUF（6.1）把方向反过来——用户态生产、内核消费（bpf_user_ringbuf_drain），补齐双向。**→ 详见第 4 章

**PERF_EVENT_ARRAY（BPF_MAP_TYPE_PERF_EVENT_ARRAY）**——第一代逐事件通道（4.3）：用户态必须先 perf_event_open（PERF_TYPE_SOFTWARE+PERF_COUNT_SW_BPF_OUTPUT）把 fd 逐 CPU 塞进 map 对应槽位、程序才能 bpf_perf_event_output（必须传 ctx）；<5.8 内核的唯一选择（libbpf-bootstrap 的 bootstrap_legacy 即此）。→ 详见第 4 章

**pin / bpffs**——BPF_OBJ_PIN（4.4）把 map/prog/link 钉到 bpffs 路径 `/sys/fs/bpf/`，对象获得与文件同寿的引用，创建进程退出仍在；任何进程 BPF_OBJ_GET(path) 拿回 fd。默认生命周期=fd 引用计数（进程退出即回收）。工具链语义差：ip/tc 默认复用同名 pinned map、libbpf 默认新建（计数器"重启清零还是延续"取决于谁加载）。→ 详见第 4、7 章

**BTF（BPF Type Format）**——编码"BPF 程序/map 相关 debug info"的极简元数据格式（仿 Sun CTF）：类型图+函数信息+行号信息，blob 以 magic 0xeB9F 开头（可探测端序）；现行规范 22 种 kind（2018 年快照只有 11 种）；dedup 五 pass 把 DWARF 121MB 压到 ~1.5MB（类型描述符 104x），小到随内核默认发行（CONFIG_DEBUG_INFO_BTF）。ELF 侧四 section：.BTF/.BTF.ext(func_info+line_info+core_relo 三子区)/.BTF_ids（内核自用）/.BTF.base。→ 详见第 8 章

**CO-RE（Compile Once – Run Everywhere）**——一次编译到处运行的机制：三要素分工=BTF（描述内核与程序双方类型）+ Clang（按 BTF 生成重定位信息——记字段名而非硬编码 offset）+ libbpf（加载时与目标内核 BTF 匹配、改写 offset）。**辨析（vs BTF）：BTF 是类型描述格式（数据基础），CO-RE 是建立在其上的重定位机制（BTF 是 CO-RE 三要素之一）；CO-RE 只解决"结构体布局漂移"，不解决"目标内核根本没有该字段/函数/挂载点"（那要用 bpf_core_*_exists 存在性分支）。**→ 详见第 8 章

**vmlinux.h**——`bpftool btf dump file /sys/kernel/btf/vmlinux format c` 生成的当前内核全量类型头，所有类型带 `__attribute__((preserve_access_index))`（正是它让 Clang 对每次字段访问生成 CO-RE 重定位）；不可与系统内核头混用（类型重定义冲突必现），正确姿势=vmlinux.h+libbpf 头+应用自有头。→ 详见第 1、8 章

**BPF_CORE_READ 族**——CO-RE 链式读取宏：`BPF_CORE_READ(task, real_parent, tgid)` 一个宏完成"沿指针链逐跳安全读取+逐跳记录重定位"；变体含 _INTO/_STR_INTO/_USER*/BITFIELD；底层建立在 Clang builtin（__builtin_preserve_field_info 等）之上；非 CO-RE 旧对应物是 BPF_PROBE_READ 族（offset 编译期写死）。配套 queries 族 bpf_core_field_exists/type_exists/enum_value_exists 在编译期被 libbpf patch 成 0/1 常量做兼容分支。→ 详见第 8 章

**BTFhub**——aquasecurity 项目，收集各发行版各版本的 BTF 文件随程序分发——无 BTF 老内核跑 CO-RE 程序的两出路之一（另一条=重编内核）；Tracee 用它解决老发行版 sensor 分发；同命题（安全 sensor 跑无 BTF 老内核）另两解法：LKCCB+oxidebpf（Red Canary"内核 GPS"云构建器自动算结构 offset 运行时注入，Compile-Once-Run-Mostly-Places）与 offset autodiscovery（微软 Sysinternals 三级策略：BTF 优先→discoverOffsets 探测→手工生成覆盖）。→ 详见第 8、12 章

**kfunc**——按 BTF ID 调用（call 指令 src_reg=2）的内核函数扩展机制，不经 UAPI 编号、按 BTF 签名解析；稳定性口径：kfunc 有自己的 lifecycle、不在稳定 ABI 列表内（stable 的是指令集/helper 集/返回码）。sched_ext 的 scx_bpf_* 系列即 kfunc。→ 详见第 2、6、13 章

**struct __sk_buff（context 抽象）**——内核 sk_buff 的固定偏移抽象：对 eBPF 的 ABI 永不变（内部结构随便改），verifier 的 convert_ctx_access 把程序里对 skb->data 等字段的访问改写成真实偏移——"稳定接口（helper）+不稳定数据（内核结构）"分层的关键一环。→ 详见第 3、5、6 章

**direct packet access（data/data_end 边界检查范式）**——现代读包写法：先 `data`/`data_end` 两个指针圈出合法区间，`eth + offset > data_end` 检查通过后整个 struct 可安全访问——最常见的 "invalid mem access" 拒绝的解药；调用改包 helper 后指针与既有检查全部失效，必须重新拉取重新检查（bpf_helper_changes_pkt_data 名单）。取代 deprecated 的 legacy BPF_LD|BPF_ABS 包访问指令（packet 组，Historical）。→ 详见第 3、9 章

**RFC 9669（BPF ISA 标准）**——2024-10 发布的 IETF Standards Track 标准（D. Thaler 编），把 eBPF 指令集从内核私有 ISA 升格为互联网标准；只管指令编码与语义——helper 集合、map 语义、verifier 行为都明确"留给平台文档"，所以"BPF 程序跨平台可移植"目前成立的只有指令层不是生态层；conformance groups（一致性组）让运行时与编译器靠组名互操作：base32（实现 MUST）⊂ base64、atomic32 ⊂ atomic64、divmul32 ⊂ divmul64、packet 为 Historical（PREVAIL/uBPF/bpf_conformance 等项目用同一套组名）。→ 详见第 2、14 章

---

## 二、程序与挂载类（Program Types 与 Attach 点）

**program type（程序类型三绑定）**——"岗位合同不是方言"：30 多种类型（口径随内核版本：bcc 表 30 / 6.2.11 时 33）不是 30 个虚拟机，而是同一字节码与内核签订的岗位协议，钉死三件事——①入口 context 类型；②可用的 helper 子集；③返回值语义。verifier 按类型查 bpf_verifier_ops 三回调做差异化校验（"选一个 program type 就是选一套校验器人格"）。→ 详见第 5 章

**attach type（两级类型拆分）**——UAPI 里类型分两层：`enum bpf_prog_type` + `enum bpf_attach_type`；一个 prog type 可长出多个挂载点（TRACING 一个类型覆盖 fentry/fexit/fmod_ret/tp_btf/iter；CGROUP_SOCK_ADDR 在 2026 年 libbpf 里挂 18 个 attach 点）。选型心法：先按挂载域定大类（网络/追踪/cgroup/结构体替换），再按触发时机选 attach 点。→ 详见第 5 章

**SEC() 宏（ELF section 名）**——程序在 C 源码里用 `SEC("xdp")`/`SEC("kprobe/xxx")`/`SEC("fentry/tcp_connect")` 声明挂载意图，libbpf 打开 ELF 后按 section_defs[] 表推断 prog_type+expected_attach_type；你从不在 C 代码里写枚举名。`.s` 后缀是 sleepable 变体（如 `fentry.s+`）；`SEC("tc")`/`SEC("classifier")` 已被 libbpf 标 deprecated，改用 tcx 系。→ 详见第 5、7 章

**context（程序上下文）**——程序入口 r1 拿到的指针，类型由 program type 决定：XDP=`struct xdp_md`（data/data_end，无 skb）、tc/socket filter=`struct __sk_buff`、kprobe=`struct pt_regs`、fentry=BTF 化函数签名。同一段字节码换 prog type 要改返回值语义（SOCKET_FILTER 返回接受字节数，0=丢包、非 0=截断接受）。→ 详见第 5 章

**bpf link**——第三代 attach 方式（BPF_LINK_CREATE）：把"挂载关系本身"变成 fd 对象——①程序生命周期独立于加载进程（可 pin 到 bpffs）；②`bpf_link_update` 原子替换程序无空窗；③`bpf_link__disconnect` 可与进程断钩让程序继续在内核挂载。旧式挂载（XDP 经 ip link、tc 经 netlink）不产生 link，程序由挂载点本身持有——进程死了程序还在（孤儿程序多来自这条路径）。→ 详见第 5、7 章

**SOCKET_FILTER**——最早的 program type（3.19）：包到达 socket 接收队列时触发，context 为 __sk_buff，返回值=接受字节数；tcpdump 抓包过滤即它（SO_ATTACH_BPF）；4.4 起非特权用户可加载其受限版（helper 白名单仅 4 个）。→ 详见第 5 章

**kprobe / kretprobe**——内核动态探针（KPROBE 程序类型 4.1）：动态断点（int3 注入）挂几乎任意内核函数，context=pt_regs、参数不能直接解引用必须 bpf_probe_read_kernel 先拷上栈；不稳定——挂载点不是 ABI（函数改名/内联/删除即断），内核内层函数大量 inline/static 根本不可探测；kretprobe 单独挂出口读 RAX 同样要 probe_read。→ 详见第 5、11 章

**fentry / fexit / fmod_ret**——TRACING 程序类型（5.5）经 BPF trampoline 挂函数出入口（机制=把对目标函数的直接调用点改为经跳板跳转，x86 JIT 用 poke descriptor 做 live-patch 式打补丁；内核落点 kernel/bpf/trampoline.c）。**辨析（vs kprobe）：trampoline 直跳近零开销 vs int3 断点陷阱较重；BTF 硬依赖（按函数名解析签名）vs 无 BTF 依赖；参数即强类型 C 变量直接可读（BPF_PROG 宏展开）vs 裸 pt_regs 手工映射+probe_read 拷贝；fexit 天然拿出口参数+返回值、fmod_ret 能改写返回值 vs kretprobe 单独挂；可挂对象仅 BTF 里登记且被 trampoline 支持的函数集 vs 几乎任意内核地址；两者挂载点都不是稳定 ABI，但 BTF+CO-RE 让签名漂移在加载期暴露而非运行期崩。**选型口诀：内核有 BTF 就优先 fentry/fexit。→ 详见第 5、8、11 章

**tracepoint**——内核静态探针（TRACE_EVENT 宏由开发者手埋，4.7）：稳定且提供 kprobe 拿不到的强类型标注上下文（`args->filename` 直读）；每个 syscall 有 sys_enter/sys_exit 两个；查参数布局的标准解法=`cat .../events/.../format`+头文件 grep。Brendan Gregg 工程铁律："尽可能用静态 tracepoint/USDT 替代动态 kprobe/uprobe——动态追踪是不稳定 API"。raw tracepoint（4.17）是其变体：context 为原始参数、无稳定字段布局（RAW_TRACEPOINT_WRITABLE 5.2 进一步允许改参数）。→ 详见第 5、11 章

**uprobe / uretprobe**——用户态动态探针（挂任意库函数，随二进制符号走，strip 后需 debuginfo）：典型挂点 SSL_write/SSL_read 观测加解密边界明文；实测开销约 ~0.2µs/请求、hook CPU 0.007%-0.3%；目标函数须 noinline+asm volatile("") 防内联致符号消失。→ 详见第 7、11 章

**USDT（User Statically Defined Tracing）**——用户态静态探针：开发者 `DTRACE_PROBE` 宏埋点，Linux 生态与 DTrace C API 源码级兼容（为 Solaris 写的埋点零改动可用，如 glibc LIBC_PROBE）；坑：provider name 必须等于二进制文件名（bpftrace issue 328 的 libc 软链接解法）。→ 详见第 11 章

**perf_event（PERF_EVENT 程序类型）**——4.9：挂 perf 事件（采样/计数器），`profile:hz:99` 定时采样即它配 PERF_COUNT_SW_CPU_CLOCK，连续 profiler 与火焰图的数据源。→ 详见第 5、11 章

**LSM 程序类型（BPF_PROG_TYPE_LSM）**——5.7 入内核：挂 include/linux/lsm_hook_defs.h 声明的任意 LSM 钩子，返回非 0（如 -EPERM）即否决该安全操作——从"观测"跨入"强制阻断"的分界；启用要求 CONFIG_BPF_LSM=y + CONFIG_LSM="...,bpf"（启动参数）+ BTF，实战 5.13+。与 tracepoint 的本质区别：tracepoint 是观察点（看完只能记录），LSM hook 是决策点（可以否决）。→ 详见第 5、12 章

**struct_ops**——5.6：用 BPF 程序整体实现一个内核 ops 结构体（以 map 形式注册函数指针覆盖表）；docs.ebpf.io 收录 6 个可替换对象：tcp_congestion_ops、sched_ext_ops、Qdisc_ops、hid_bpf_ops、io_uring_bpf_ops、smc_hs_ctrl_ops；与其他 BPF UAPI 不同，struct_ops 没有任何 ABI 要求（sched_ext API 快速演进的自由度来源，代价=无稳定性保证）。→ 详见第 5、13 章

**sched_ext**——6.12 进主线的可编程 CPU 调度器框架：新的 sched_class 经 struct_ops（sched_ext_ops）把回调导出给 BPF，换调度器=跑一个普通程序、Ctrl-C 即回退内核默认 fair 调度器（6.12 时代即 EEVDF）；安全三层兜底=verifier 静态证明+运行时回调返回值校验+watchdog 饿线程检测，最坏情况只是饿线程到 watchdog 触发、不是 panic。→ 详见第 13 章

**DSQ（dispatch queue）**——sched_ext 的调度队列抽象：内核调度核心与 BPF 调度器之间的阻抗匹配结构，每个 DSQ 可当 FIFO 或优先级队列（vtime）；默认两个内置（全局 FIFO SCX_DSQ_GLOBAL + 每 CPU local DSQ），BPF 侧可建任意自定义 DSQ；CPU 永远只从自己的 local DSQ 取任务执行。调度周期四步：select_cpu → enqueue → dispatch → 收尾链。→ 详见第 13 章

**cgroup 程序族**——容器/进程组网络策略：CGROUP_SKB（4.10，收发包 1 放行/0 丢）、CGROUP_SOCK（4.10，socket 创建）、CGROUP_SOCK_ADDR（4.17，bind/connect/sendmsg 等 18 个 attach 点，可改写目标地址做透明重定向）、CGROUP_SOCKOPT（5.3）、CGROUP_SYSCTL（5.2）、CGROUP_DEVICE（4.15）。→ 详见第 5 章

**SK_SKB / SOCK_OPS / SK_MSG**——socket 层四层 LB 三件套：SOCK_OPS（4.13）探 TCP 连接事件写 sockmap；SK_SKB（4.14）流经 sockmap 挂载的 parser/verdict 点（verdict 族 __SK_PASS/__SK_DROP/__SK_REDIRECT）；SK_MSG（4.17）sendmsg 出口 verdict——同主机通信跳过本地 TCP/IP 栈。→ 详见第 5 章

**seccomp-BPF**——**辨析：seccomp 不是一种 program type**——seccomp filter 走 cBPF 32 位指令格式（与 SO_ATTACH_FILTER 同款 sock_filter/sock_fprog），经翻译成 eBPF 后过 verifier，返回 SECCOMP_RET_ALLOW/KILL/ERRNO/TRAP/USER_NOTIF；2012 年起 Chrome sandbox 即用。语义分工：seccomp 管"进程自愿戴上的 syscall 镣铐"，Tetragon/BPF LSM 管"内核视角下该操作该不该放行"。→ 详见第 5、12 章

---

## 三、工具链类（编译、加载、测试、分发）

**LLVM BPF backend / clang -target bpf**——唯一的正统编译器：C 进 BPF 字节码出，2014-12 由 Starovoitov 提交（review D6494，约 2000 行），初版刻意不支持全局变量/任意函数调用/varargs/间接跳转/alloca（"受限 C"的第一手出处，后来逐项解除）；标准编译命令 `clang -g -O2 -target bpf -D__TARGET_ARCH_$(ARCH)`——`-g` 是 BTF/CO-RE 硬前提不是调试可选项；`-target bpf` 会"丢"架构头文件目录，须 CLANG_BPF_SYS_INCLUDES 显式补回；默认 native target 生成 switch jump table 会致加载必败（-fno-jump-tables）；指令集代次用 `-mcpu=v1/v2/v3` 表达（与 RFC 9669 conformance groups 对齐，v3 自 LLVM 20 默认；`-mcpu=probe` 探测内核实际能力，跑 BPF selftests 必须用它）。→ 详见第 2、8、15 章

**libbpf**——现代正统加载器（C 库）：内核不认识 ELF，从"带 section 名/重定位表/BTF 的 .o"到"一串 bpf() syscall"的翻译全归它；src/ 约 35 文件（relo_core.c 管 CO-RE 重定位、btf.c/btf_dump.c 管 BTF）；薄封装 src/bpf.h 一对一包 bpf(2) 命令族。目标机零依赖（BTF 发行版内核自带：Fedora 31+/RHEL 8.2+/Ubuntu 20.10+）。→ 详见第 7 章

**open → load → attach 三段式**——libbpf 的应用生命周期：open（解析 ELF、不碰内核、参数化窗口——改 rodata/全局变量必须在 open 与 load 之间）→ load（BPF_MAP_CREATE×N + BTF_LOAD + CO-RE 重定位 + map fd 指令改写 + BPF_PROG_LOAD 过 verifier）→ attach（多数类型凭 SEC 名自动接线，产物 bpf_link）→ close/destroy。任何 eBPF 应用用户态侧都是这条管线的变形。→ 详见第 7 章

**BPF skeleton**——`bpftool gen skeleton` 生成头文件：把 .o 字节数组整个嵌进去+强类型句柄（maps/progs/links/bss 视图）+`__open/__load/__attach/__destroy` 函数族；三大收益=部署零文件（.o 进二进制，~200KB 自包含）、全局变量 mmap 直读直写零 syscall、rodata 编译期裁剪（const volatile 缺一不可，少 volatile 则 Clang 删变量）。→ 详见第 7 章

**bpftool**——内核树官方 CLI（tools/bpf/bpftool）：prog/map/link/cgroup/net/perf/struct_ops/iter/btf/gen 子命令体系；高频组合=`bpftool feature probe`（探测本机可用 prog/map/helper 全集）、`bpftool prog dump xlated/jited`（指令级排障）、`btf dump`（生成 vmlinux.h 的官方命令）、`gen skeleton/object`。内核树同门小工具三件套：bpf_asm（人类可读 cBPF 汇编成字节码，遗留）、bpf_dbg（交互式单步调试可喂 pcap）、bpf_jit_disasm（反汇编 `bpf_jit_enable=2` 导出的 JIT 镜像为本机机器码）。→ 详见第 1、7、15 章

**iproute2（ip/tc 加载器）**——第一代前端（2014-2017 主流）：`ip link set dev eth0 xdp obj x.o` / `tc filter add ... bpf da obj x.o`；内置小型 ELF loader，map 需 pin 到 /sys/fs/bpf/tc/ 共享；用自己的 struct bpf_elf_map 老式 map 声明（.pinning 字段）——"读代码需分辨时代"。iproute2 加载 XDP 程序时 ELF section 名必须是 `prog`；第一代裸加载的坑=kern_version（4.x 内核对 KPROBE 程序强校验 `attr->kern_version == LINUX_VERSION_CODE` 否则 EINVAL、且不能用 uname 动态算——发行版 backport 抬高 sublevel；libbpf 自动填对、手写加载器才会踩，前 CO-RE 时代可移植性困境的实证）。→ 详见第 7、8、9 章

**BCC**——2015-2019 主流的运行时重编译框架：目标机上跑 clang（clang::Rewriter 做源码重写——隐式内核指针解引用改写成 bpf_probe_read+offsetof、map 访问替换成 bpf_pseudo_fd），Python 前端像 dict 一样操作 map；代价=目标机要装 clang/LLVM+全套内核头、opensnoop strace 下 10000+ 行 syscall。两代工具集：tools/（105 个 .py 动态编译版）vs libbpf-tools/（124 个 .c CO-RE 预编译版，新项目一律选后者）。→ 详见第 1、7、15 章

**bpftrace**——"一行代码级"观测事实标准（DTrace 现代继任者，LLVM 后端）：语法 `probe /filter/ { action }`，15 种 probe 类型、16 个 builtin 变量、30 余个 builtin 函数；分工口径（Gregg）："BCC 写复杂工具和守护进程，bpftrace 写 one-liner 和短脚本；想自己编程先 bpftrace，不够再上 BCC"。相反极端是 ply：零依赖（纯 C、只要 libc+支持 BPF 的内核，无 LLVM 无 Python）为嵌入式而生，聚合影射与 JIT 在内核态完成，是 bpftrace 语法的直系先辈。→ 详见第 11、15 章

**cilium/ebpf**——纯 Go 加载库：从零实现 bpf(2) 全家、零 CGO，代表用户 Cilium/Datadog agent/Pixie/Hubble；标准工作流 bpf2go（`//go:generate` 自动生成 Go 加载骨架+go:embed 嵌单二进制）；features 包运行时能力探测（等价 bpftool feature probe）。→ 详见第 15 章

**libbpfgo**——C 库薄封装路线：CGO 直接包 libbpf，行为与上游 1:1、新内核特性零延迟，代价是交叉编译之痛与 libc 绑定（Tracee 的解法=submodule 静态链 libbpf）。→ 详见第 15 章

**aya**——纯 Rust 加载库（Rust 事实标准，只用 libc crate 发 syscall）：`#[kprobe]`/`#[map]` 过程宏、aya-template 一条命令生成 19 种程序类型骨架；坑=eBPF 内核侧代码必须 GPL-2.0 兼容（漏 license 节会被内核拒载）、target 是特殊的 bpfel-unknown-none。→ 详见第 15 章

**BPF_PROG_RUN（旧名 BPF_PROG_TEST_RUN）**——不经真实事件源的单测命令：从用户态直接注入上下文执行程序并取回结果，支持 15 种程序类型；关键字段 data_in/data_size_in（喂 mock 数据，XDP 场景即手工构造的包）与 repeat（重复次数——顺带就是性能测量，单测与压测同一套 API）。→ 详见第 15 章

**selftests/bpf**——内核树公认的"eBPF 功能百科全书"：progs/ 下每个 .c 演示一种 verifier 特性或 helper 用法；两条铁律——verifier 行为变更必须配 test_verifier.c 用例（未跟踪的行为视为可变）、上游 BPF patch 测试先行是硬要求。研究向语料库=vbpf/ebpf-samples（340 文件含 11 个 invalid/ 反面教材）。→ 详见第 3、15 章

**bpfcompat**——真内核 VM 矩阵验证：对矩阵里每个目标内核 boot 一个真发行版 cloud image 的 QEMU/KVM 一次性 VM、把 .o 连同 validator 送进去跑真 bpf() load——回答 CO-RE 回答不了的"这个 .bpf.o 在我关心的内核上实际能不能 load/attach"；内置 31 个内核矩阵 YAML（Ubuntu 4.15→6.17+RHEL 系）+ quirk-library（"版本号≠特性支持"坑内核库）；Falco 与 Inspektor Gadget 已收进上游 CI。CO-RE 的虚假安全感（BTF 缺失/重定位对不上/配置差异都是真失败源）正是它存在的理由。→ 详见第 15 章

**bpfman**——CNCF Sandbox、第三代加载器正统（原名 bpfd）：Rust 守护进程+gRPC/Unix socket，三大能力=系统 eBPF 洞察、程序加载（XDP/TC dispatcher 多程序链式挂载）、eBPF 文件系统管理（部署无需额外特权）；支持按 OCI 镜像分发字节码（`bpfman load image quay.io/bpfman-bytecode/...`），配 operator CRD 与 K8s CSI 驱动。**辨析（"bpfd"三撞名）：genuinetools/bpfd（2019 规则守护进程，死）、joelagnel/bpfd/BPFd（Android stdio 远程加载，弃用）、bpfman（活）——引用必须带 org 全名。**同代同路线还有 eunomia-bpf（配置化/Wasm 分发：`ecli run ghcr.io/eunomia-bpf/execve:latest` 一行从 registry 跑预编译工具；老的 HTTP 远程模式已从主分支删除）与 Inspektor Gadget（gadget 封装成 OCI 镜像）——"eBPF 程序当容器镜像分发"已是这一层的行业共识方向。→ 详见第 15、16 章

**uBPF / rbpf（用户态运行时）**——uBPF（iovisor，Apache-2.0）：因内核 eBPF 是 GPL 闭源项目不能复用而生的用户态 C 运行时（解释器+x86-64/Arm64 JIT，README 直接引用 RFC 9669 为规范基准）；扩展点 r2=mem_len（内核只承诺 r1=ctx）、不支持 tail call 的解释器亦有其例；新一代 Safe Execution Profile 把 verifier 指针追踪思想压进解释器本身。rbpf：uBPF 的 Rust 移植（MIT/Apache 双许可），读一个完整 eBPF VM 的最低成本入口。→ 详见第 2、14 章

---

## 四、数据面类（XDP、tc、AF_XDP）

**XDP（eXpress Data Path）**——4.8 引入的收包最早期挂载点：原提案人比喻"给现有高速公路加拼车道"（不是 DPDK 式另建高铁）；解决 Cloudflare 痛点——"iptables 不慢，只是被执行得太晚了"（包要走完 DMA/NAPI/SKB/GRO/IP/conntrack 才轮到规则匹配）；只管 ingress，胜在极致快：CoNEXT'18 单核 drop 24 Mpps（DPDK 对照 43.5），Cloudflare 4.14 实测 10.1 Mpps（应用到 XDP 约 58 倍差距）。→ 详见第 9 章

**driver XDP vs generic XDP**——driver（原生）级：hook 在网卡驱动 RX 函数里、SKB 尚未分配的 Rx ring 最早点，一核一 RX queue 无锁、DROP 时页面直接回收；generic（4.12 起）：hook 在 SKB 层、任意网卡可用，但已付 SKB 分配成本、性能显著低于 driver 级——"任意网卡可用≠快"，生产抗 DDoS 必须 ethtool 确认驱动原生支持（veth 也支持）。注意 XDP 不是免费的：启用即改变 RX ring 内存模型（每包恒 alloc 4K 页，page_pool 项目为此成为标准解法），真转发无法完全避开与 MM 层交互。→ 详见第 9 章

**XDP action（五种动作）**——XDP 程序对每个包返回的动作：XDP_PASS（放行进协议栈）/XDP_DROP（极速丢弃，页面直接回收最便宜）/XDP_TX（同一接口弹回，同 CPU 独占 TX queue 免锁）/XDP_REDIRECT（重定向到另一网卡/CPU/用户态）/XDP_ABORTED（程序出错，实际按丢包处理）。2016 提案期只有 PASS/DROP/TX 三个。**辨析（vs tc verdict）：XDP action 是无 SKB 最早入口的动作码（4.8+，五值）；tc verdict 是有 SKB 的 clsact 层返回码（TC_ACT_OK/SHOT/STOLEN/REDIRECT/PIPE/RECLASSIFY/UNSPEC）——两套码系不通用，XDP 无队列/整形能力、tc egress 是 XDP 完全够不到的半边天。**→ 详见第 9 章

**tc cls_bpf（SCHED_CLS/SCHED_ACT）**——tc 流量控制里的 BPF classifier：2013 年以 cBPF 形态出生（cls_bpf.c="BPF 的第一个生产级家"）、2015 年加 eBPF；挂载点 ingress 在 __netif_receive_skb_core（SKB 已存在、早于 IP 层）、egress 在 __dev_queue_xmit；天然可改包、带隧道元数据 helper、与 qdisc 体系配合——"有 SKB 的全功能层"。→ 详见第 9 章

**direct-action（da 模式）**——cls_bpf 的执行模式：classifier 直接返回 verdict 省掉完整 tc action 引擎（传统模式要配 act_pedit 等）；`tc filter add ... bpf da obj prog.o` 是标准挂载姿势；tc 最佳实践="只挂一个 classifier 干完所有匹配+改包"。→ 详见第 9 章

**tcx / netkit**——新一代 tc 挂载：tcx 是 tc 挂载的 link 化重建（kernel/bpf/tcx.c，libbpf `tcx/ingress` section，旧 `SEC("tc")` 已标 deprecated）；netkit（6.7+）是 L2 veth 替代品，pair 经 BPF_NETKIT_PRIMARY 在 ndo_start_xmit() 挂 BPF，Calico 实测吞吐/尾延迟优于 TC/TCX（bpfAttachType 三选：Netkit/TCX/TC）。→ 详见第 9 章

**XDP_REDIRECT**——重定向动作（2018 年以 map-based 形态落地）：设计核心=用 map 而非 helper 参数做目标选择——`bpf_redirect` 单核仅 7.5 Mpps，`bpf_redirect_map` 达 13.0 Mpps（把 RX bulking 藏进 XDP core，NAPI poll 末尾统一 flush 批量≤64 摊销 NIC tail pointer 写）。→ 详见第 9 章

**DEVMAP / DEVMAP_HASH**——ifindex→网卡引用的 map（4.14/5.4）：`bpf_redirect_map` 把包从另一网卡发出，driver 只需实现 ndo_xdp_xmit 即支持；新增 redirect 目标类型零 driver 改动。→ 详见第 4、9 章

**CPUMAP**——CPU id→远端 CPU 的 map（4.15）：把 raw XDP frame 直送目标核、到那边才建 SKB 进协议栈（MPSC+ptr_ring+钉核 kthread）；两大用途=隔离 XDP 层与协议栈（DDoS 时协议栈再慢也拖不垮丢包）、修硬件 RSS 对隧道流量的 CPU 分布失明。→ 详见第 4、9 章

**XSKMAP**——redirect 进 AF_XDP 用户态 socket 的 map（4.18）：XDP 程序按 rx_queue_index 查表重定向；官方明文"必须加载 XDP 程序且 XSKMAP 至少放一个 socket，XSK 才可能收到流量"；copy 模式下它不是跨队列交换机——只能把 queue X 的流量给绑在 queue X 的 socket。→ 详见第 4、9、10 章

**headroom / bpf_xdp_adjust_head**——page 里 data 之前预留的空间叫 headroom：要加包头（VLAN/隧道 encap）必须先把 data 指针前挪——helper bpf_xdp_adjust_head 负值 push（腾头部空间）正值 pull（剥头）；struct xdp_frame 的排队元数据也放 headroom 里，排队转发零额外分配。→ 详见第 9 章

**multi-buffer（XDP_USE_SG / xdp.frags）**——多缓冲/scatter-gather：XDP 初期单帧模型一个包必须整个落在一个 page（jumbo frames 处理不了）；解法=XDP_USE_SG bind flag + XDP_PKT_CONTD 标志（故意与常见 NIC 的 EOP 反向，兼容老应用）链式传递；copy 模式上限 CONFIG_MAX_SKB_FRAGS+1、可移植代码限 18 帧；XDP 程序须用 `xdp.frags` section 声明。→ 详见第 9、10 章

**xdpdrv / xdpgeneric / xdpoffload**——XDP 的三种加载执行位置：xdpdrv=驱动原生执行；xdpgeneric=SKB 层通用路径；xdpoffload=卸载到 SmartNIC 硬件执行（Netronome 双模 demo：同一份 .o 用 xdpdrv 或 xdpoffload 加载，l4lb offload 实测 33 Mpps/38 Gbps）——硬件卸载的三份一致性契约=verifier 按 HW 能力收紧+驱动二次校验、map 跨内核/固件两个内存域、原子与并发语义差异（NFP 对硬件 map/原子/尾调用只有受限支持）。→ 详见第 14 章

**kernel bypass（DPDK/VPP/PF_RING/Snabb）**——eBPF 之前的第三条路线：把包处理搬去用户态换取速度，代价=用户态自带驱动、重造内核网络栈、丢失内核安全层与 OS 集成、程序成沙盒孤岛——eBPF 定位为第四条路（在内核里运行经验证的安全程序）的对立面。三路线选型：全旁路 DPDK/f-stack（独占网卡+完整 FreeBSD 栈）、半旁路 AF_XDP（复用内核驱动与安全模型）、翻译层 passt（零 capability rootless）。→ 详见第 1、10 章

**AF_XDP / XSK（XDP socket）**——4.18 进主线的"高速原始以太网帧直达 Linux 用户态"通道：XDP 是内核内快速岔路口、AF_XDP 是岔路口通向用户态的匝道；设计四支柱=true zero-copy、lock-less、消除 syscall、仍遵守 Linux 隔离与安全规则；Intel 2018 微基准最高 40x vs 旧 AF_PACKET（tcpdump 场景 20x）。史料勘误：2017 年 AF_PACKET v4 论文不可参考（"几乎所有东西都改了"），正确文献是 LPC 2018 论文。执行模式三档：XDP_SKB（generic，任意网卡，1 次拷贝）/XDP_DRV（驱动原生，仍 1 次拷贝）/zero-copy（XDP_ZEROCOPY bind flag 且驱动支持，NIC DMA 直写 UMEM 零拷贝；内核 bind 先试 zero-copy 失败回退 copy，应用应以 XDP_OPTIONS getsockopt 查实际模式）。→ 详见第 10 章

**UMEM**——用户态分配的虚拟连续内存切成等大 chunk（XDP_UMEM_REG 注册；chunk_size 当前只支持 2K/4K）：内核态与用户态共用一个"保税堆场"，传递的只是描述符（提单）不搬数据；RX 与 TX 可共享同一 UMEM——转发只换描述符；aligned 模式下 FILL 环 addr 低 log2(chunk_size) 位被掩掉。→ 详见第 10 章

**四个环（FILL/COMPLETION/RX/TX）**——AF_XDP 的所有权转移模型，全部为 SPSC head/tail 环（size 2 的幂）：FILL（用户态→内核，"空缓冲区交给你收包"）/COMPLETION（内核→用户态，归还所有权——只归还不保证发送成功，含被拒非法描述符）/RX（内核→用户态，xdp_desc{addr,len}）/TX（用户态→内核，需 sendmsg 触发）。两条红线：收包的上游是 FILL 不是 RX；同一缓冲区绝不能同时出现在两个环里（否则包损坏）。→ 详见第 10 章

**XDP_SHARED_UMEM / need_wakeup**——多队列共享与 syscall 省法：SHARED_UMEM 让 UMEM 跨 socket/queue/netdev 共享（同 netdev+queue 多 socket 共用一对 FILL/COMPLETION 由 XSKMAP 分发；跨 queue/netdev 每元组自建一对环、靠 NIC RSS 导流，不需专门 XDP 程序）；XDP_USE_NEED_WAKEUP 在 FILL/TX 环（用户态是生产者的两个环）上置标志才需要 syscall 唤醒——官方建议总是开启。→ 详见第 10 章

**bpfilter**——"iptables 二进制一字不动、规则翻译成 eBPF 程序挂 XDP/tc"的野心项目（2018 Borkmann RFC）：最大胆设计是 bpfilter.ko——跑在用户态的 ELF"新形态内核模块"（UMH 机制，崩不了内核）；一条 `iptables -A INPUT -d 10.0.0.4/32 -j DROP` 译成 26 条 eBPF 指令；历史后验=UMH ELF 模块形态最终未进主线，2020 年后转向 userspace+BPF daemon 形态（引用须注明是历史方案）。→ 详见第 9 章

---

## 五、可观测类（Tracing 与监控）

**eBPF tracing 三性质**——追踪具备的生产级性质："不重编译、不重启、低开销"——事件发生时执行什么交给内核内受限 VM（只能经 map 与用户态交互、保证停机）；前史：DTrace 因 CDDL 与 GPL 不兼容错过 Linux 十年，SystemTap 编译成内核模块内核一升级就碎。可观测性是 eBPF"出圈"的主舞台（Gregg 2016 Facebook Performance@Scale）。→ 详见第 11 章

**trace_pipe / bpf_trace_printk**——第一代输出通道：写 /sys/kernel/debug/tracing/trace_pipe 这个全局共享管道，"is slow, and should only be used for debugging purposes"；三个硬限制=格式串必须是预定义常量、只支持有限转换符、附加参数最多 3 个 u64；多程序并发写互相踩。选型直觉："要分布不要样本→map 直方图；要逐事件明细→ringbuf；要看两眼→printk"。多参数打印用 bpf_trace_vprintk（5.16+），格式化用 bpf_snprintf（5.13+）。→ 详见第 6、11 章

**内核态聚合直方图（log2 hist）**——第四条隐性输出通道（最省）：直方图/计数器留在内核 map 里算完（ARRAY+log2 分桶+原子自增的十行范式），用户态周期性批量读、事件不出内核——biolatency"summarization is all done in kernel context, for efficiency"；bcc 的 print_log2_hist() 一键打印。→ 详见第 1、4、11 章

**enter/exit 双探针延迟范式**——测耗时的标准结构：入口探针 `@start[tid] = nsecs`，出口探针 `/@start[tid]/` 过滤后算差值再 delete——键必须用 tid（同进程多线程并发会互相覆盖）；不带过滤则半程捕获的调用会算出 `nsecs - 0` 的天文数字（新手 bpftrace 延迟脚本第一大坑）；算完必须 delete 防泄漏。同一范式（双程序+map 传参+缓冲区出口）是 L7 协议观测的通用骨架。→ 详见第 11 章

**bpf_get_stackid / STACK_TRACE map**——采样类探针拿调用栈的标准姿势：遍历内核/用户栈（BPF_F_USER_STACK）把 IP 数组存进 STACK_TRACE map（4.6）返回栈 ID，直方图以 {pid, kernel_stack_id, user_stack_id} 为键计数；触发器用 PERF_COUNT_SW_CPU_CLOCK 按核各开 fd，sample_period 建议取质数避免共振——手写 profiler 的三 map 分工（直方图+栈表+符号信息）。→ 详见第 4、11 章

**栈回溯三路线**——栈从哪来：①帧指针展开（最快，要求二进制保留 rbp，strip/无帧指针构建失效；Gregg 2024《The Return of the Frame Pointers》代表发行版正把帧指针请回来）；②DWARF 展栈（读调试信息按 CFI 规则回溯，parca-agent 招牌，覆盖 .NET/Java/Node.js/Python 等十余运行时）；③运行时 VM 结构读取（解释型语言直接读 VM 内部数据结构，rbperf 读 CRuby VM 配版本偏移表是教材）。→ 详见第 11 章

**连续 profiling（continuous profiling）**——always-on 采样 profiler 形态：parca-agent 用 eBPF 捕获用户态+内核态栈 19 次/秒产 pprof（要求 5.3+ with BTF）；其 CPU profiler 核心已切换为 OTel ebpf-profiler（Grafana Pyroscope 捐赠系）的自有 fork——连续 profiling 生态与 OpenTelemetry 汇流的直接证据。想吃透机制可手写最小版（perf_event 程序+双栈 ID+HASH 直方图）。→ 详见第 11 章

**SSL/TLS 明文观测**——uprobe 挂加密边界：uprobe/SSL_write 拿客户端加密前出站明文、uprobe+uretprobe/SSL_read 拿服务端解密后明文——独立于应用、动态挂载免重启、不需要证书（不解密，只是站在加密前/解密后的位置）；实测额外延迟 ~0.2µs/请求；工程化天花板在库与版本矩阵管理（kyanos 为 OpenSSL 1.0.2→3.5.0 维护十余个逐版本 .bpf.c）；限制=只对同节点加解密流量有效。→ 详见第 11 章

**kyanos**——替代"tcpdump→scp→Wireshark"三步流的单命令抓包分析：HTTP/Redis/MySQL/Kafka 等协议过滤+聚合+招牌的内核级延迟拆解（网卡到 socket buffer 每个内核阶段耗时可视化）；采集点=syscall tracepoint 全家+kprobe __ip_queue_xmit+XDP+uprobe 矩阵；内核要求低至 3.10.0-957+（自维护 legacy 变体）。→ 详见第 11 章

**rstat 反例（"何时不该用 eBPF"）**——全语料最珍贵的批判样本：v1 在 sched_switch 挂常驻 probe，刷新比 procfs 快两个数量级，但代价没有消失而是转移——handler 成本×每秒上下文切换数（人为切换风暴 240 万/s 时吃掉 1.8 个 CPU 核），"always-on probe 在机器最忙时收费最贵——恰恰是监控最该便宜的时候"；v2 改回 /proc+/sys+ PSI 五模块全开 ~1.5% 单核。结论：eBPF 仍是内核计数器回答不了的问题（per-task 延迟归因）的正确工具，但应只在调查期间运行。→ 详见第 11 章

**bcc 12 站巡检清单**——无头绪时的巡检路线（Gregg）：execsnoop（短命进程）→opensnoop→ext4slower→biolatency/biosnoop→cachestat→tcpconnect/tcpaccept/tcpretrans→gethostlatency→runqlat→profile -F 49；工具分单用途（一工具一事）与多用途（trace/argdist/funccount/funclatency/stackcount），每个配源码+示例输出+man page 三件套。→ 详见第 11 章

---

## 六、安全类（防御、LSM、攻防）

**eBPF 权限模型（CAP_BPF）**——加载 eBPF 需 root 或 CAP_BPF（追踪另需 CAP_PERFMON）——攻防叙事的前提：eBPF 攻击不是无门槛远程漏洞，而是"已有 root/BPF 权限的攻击者能把它用得多隐蔽"；非特权例外=4.4 起可加载受限 SOCKET_FILTER（helper 白名单 4 个），总开关 `sysctl kernel.unprivileged_bpf_disabled=1`（生产机建议关闭）。→ 详见第 12 章

**verifier 安全边界**——官方明言："verifier 是安全工具（safety tool），不是安全审计工具（security tool）"——它保证程序不会崩溃/越界/死循环，不保证程序不恶意（拿到权限的攻击者可用 eBPF 做 rootkit：凭据窃取/流量嗅探/容器逃逸）；verifier 自身 bug=内核提权漏洞（CVE-2017-16995 曾绕过验证直接读写内核内存）——把 eBPF 当防御武器的同时必须把它当攻击面管理（如限制 bpf() syscall 本身）。→ 详见第 1、3、12 章

**eBPF 安全三代演进**——判定时机不断前移的防御史：第一代事后检测（Falco/Sysmon for Linux——事件先穿越内核边界、规则引擎在用户态判定、只能告警）；第二代内核态策略执行（Tracee/Tetragon——detect→enforce，命中即内核里杀死进程）；第三代强制访问控制（BPF LSM 一线——挂 LSM 钩子在不可回头点之前、返回 -EPERM 事情根本不发生）。勘误式提醒：三代是叙事工具不是严格时间线，选型看"判定位置+判定时机"是否匹配威胁模型。第一代的价值是把遥测成本论证做完：Red Canary 实测 execve 追踪场景 eBPF 探针比 auditd 满配高约 19% 吞吐（14254 vs 11989 execl/s），且 AuditD 在容器场景返回子进程 namespace PID 致进程谱系断裂、eBPF 可读 task_struct 拿 root namespace PID——注意是 2022-01 四核 VM 单场景数字，非普适结论。→ 详见第 12 章

**detect→enforce（Tetragon TracingPolicy）**——第二代的核心范式：Tetragon 把策略做成 K8s CRD（TracingPolicy 声明 kprobe/tracepoint/uprobe+selectors+actions），传感器默认开 process_exec/process_exit，事件自动富化 namespace/pod/容器身份；enforce 硬证据=KPROBE_ACTION_SIGKILL=3/OVERRIDE=5/SIGNAL=10/NOTIFYENFORCER=13（改 action 即从观察转强制）；误杀风险：策略写错的代价是生产事故而非漏报。→ 详见第 12 章

**BPF LSM**——第三代机制内核（Kernel Runtime Security Instrumentation，Google 贡献，5.7）：BPF 程序成为又一个 LSM，挂 lsm_hook_defs.h 任意钩子返回非 0 即否决；经典战例=fileless 阻断——正确挂点是 binfmt 匹配后、执行 point of no return 前的 `lsm/bprm_creds_from_file`，判据"被执行文件 inode 链接数为 0 即匿名文件"（memfd: 前缀可伪造、inode nlink 不可），Sysmon/Tracee/Falco 只能在这里"检测"、BPF LSM 能"阻断"。→ 详见第 5、12 章

**bpflock**——BPF LSM 主机加固锁（六类小锁：filelesslock/kimglock/bpfrestrict/kmodlock 等）：bpfrestrict 挂 lsm/bpf 限制 bpf() syscall 自身（防御程序也是 eBPF，攻击者可先卸载防御探针）；声明式三档 profile（allow/baseline/restricted），合理路径=先 allow 档全量日志再逐条收紧；自认边界："does not protect against evil root"；experimental 且 2022-02 后停滞 4 年（选型看活项目 owLSM/Bombini/BPFJailer）。→ 详见第 12 章

**攻击原语三件套**——eBPF 攻击面的 helper 层：①写用户态内存（bpf_probe_write_user——篡改 sudo 读到的 /etc/sudoers 等；UAPI 明文警告 "should not be used to implement any kind of security mechanism because of TOC-TOU attacks"，只用于半协作进程调试/干预；TripleCross 源码注释自认 "not reliable enough"：随机返回 EFAULT、相邻缓冲联动污染、bash 路径必败——攻击工具自己承认原语不可靠）；②读一切+hook 一切（bpf_probe_read 系×tracepoint/kprobe——凭据窃取/流量嗅探/行为画像）；③信号与返回值改写（bpf_send_signal 反调试 DoS、bpf_override_return 改 syscall 返回值——2021 年即被同行确认局限，LSM 程序是替代路径）。本质：检测原语和攻击原语是同一批（能力对称性）。→ 详见第 12 章

**bad-bpf**——教学级攻击标本（DEF CON 29 "Warping Reality" 配套）：六个程序各演示一种原语滥用——bpfdos（反调试）、exechijack（篡改 execve 参数）、pidhide（hook getdents64 令 ps 失明）、sudoadd（只对 sudo 进程覆写 sudoers——精准单进程提权）、writeblocker（rsyslogd 静默丢 auth.log）、textreplace（read 路径文本替换）；textreplace2 展示 map 配置+bpffs pin 持驻（loader 退出程序仍在，无进程存留的常驻形态）。→ 详见第 12 章

**ebpfkit / ebpfkit-monitor**——工程级 rootkit（BlackHat USA 2021）：混淆（对 bpf syscall 隐藏自身）/容器逃逸/C2（HTTP User-Agent 字段伪装）/eBPF 层主动 ARP+SYN 端口扫描/fs_watch 窃文件；配套检测工具 ebpfkit-monitor 给出"以 eBPF 之道还治 eBPF 之身"两模——静态分析 BPF ELF 按特征查询（列出所有用 bpf_probe_write_user 的程序）+运行时 bpf syscall 白名单监控。→ 详见第 12 章

**TripleCross**——集大成攻击标本（UC3M 学士论文）：GOT 劫持库注入五阶段（从栈上回溯定位 PLT 返回地址→动态生成 shellcode 绕 ASLR/PIE→覆写 GOT）；C2 触发器复刻国家级植入物（pattern-based 仿 NSA Bvp47、multi-packet 仿 CIA Hive——payload 藏进 TCP seq number）；phantom shell 用 XDP/TC 改写既有包 payload 承载 C2（绕开"eBPF 不能自发包"限制）。→ 详见第 12 章

**eBPF 遥测成本论证**——Red Canary 实测：execve 追踪场景 eBPF 探针比 auditd 满配高约 19% 吞吐（14254 vs 11989 execl/s）且 AuditD 在容器场景返回子进程 namespace PID 致进程谱系断裂、eBPF 可读 task_struct 拿 root namespace PID——第一代检测的价值就是把成本论证做完；注意是 2022-01 四核 VM 单场景数字，非普适结论。→ 详见第 12 章

---

## 七、生态类（治理、社区、项目谱系）

**IO Visor**——第一代治理（2015-2016，Linux Foundation 伞组织）：定位"通过可编程数据平面推进内核内 IO 虚拟化"；层级钉版=IO Visor 是组织伞、eBPF 是内核技术、BCC/XDP 是其上的工具层（三者常被混为一谈）；衰落证据=官网 2016 年后更新缓慢、旗舰史料仓 bpf-docs 2019-07 冻结，"项目代管"模式化石，职能被 ebpf.io（门户）+CNCF（项目治理）+各公司瓜分。→ 详见第 1、16 章

**eBPF Foundation / ebpf.io**——第二代治理（2021 至今）：基金会重心在规范（RFC 9669）与安全可靠性倡议，FAQ 明言**不收编第三方项目**（与 CNCF 互补：CNCF 管项目孵化毕业，基金会管内核接口跨厂商中立性）；ebpf.io 门户自称 "Maintained by the eBPF community"，内容 CC BY 4.0、11 种语言本地化。→ 详见第 16 章

**ebpf.io 应用全景（Major/Emerging）**——社区承认的正式生态地图（2026-11 快照 56 项目=10 Major+46 Emerging）：Major 10 席含 bcc/bpftrace/Calico/Cilium/Falco/Katran/Parca/Pixie/Tetragon/OTel eBPF Profiler；Emerging 门槛=开源+eBPF 为核心技术+活跃+开放治理+成立>6 个月且 star>50（Major 再加 >50 contributors+生产规模使用），按 star 季度排序——收录规则本身就是治理机制；可观测类占 Emerging 的 43%，是 eBPF 最大产业化出口。→ 详见第 16 章

**netdev / bpf / xdp-newbies（邮件列表三件套）**——内核开发主战场（纯文本邮件拍板，GitHub 只是镜像）：netdev（订阅 1085，网络子系统总战场，累计 1,248,768 封、2026-09 单月 15,937 封历史峰值）；bpf（502，BPF 子系统专题）；xdp-newbies（305，专为准新手设、避开高流量）。订阅走 subspace.kernel.org（majordomo 已废弃）；查历史优先 lore.kernel.org（权威+Patchwork 集成）；工作流标配=git send-email 或 b4。→ 详见第 16 章

**bpf-next / net-next**——内核开发树：BPF patch 走 bpf-next（Starovoitov/Borkmann 维护），定期批量 merge 进 net-next 再入 mainline——BPF patch 的上游路径天然穿过网络子系统官僚体系（"eBPF 社区"与"netdev 社区"高度重叠的制度原因）；patch 礼仪写在内核树 Documentation/bpf/bpf_devel_QA.rst（Subject 前缀 [PATCH bpf]/[PATCH bpf-next]/[PATCH net-next]、selftests 先行）。→ 详见第 16 章

**GPL 授权边界（争议史）**——2014 年最初 patch 的 license 参数比内核模块更严（非 GPL 拒载）当场引发 reviewer 质疑，Starovoitov 承诺按 module 式分级——兑现为今天的规则：GPL 兼容性取决于 program type 与所用 helper（tracing 须 GPL、网络可专有、GPL-only helper 当场拒载）；生产项目用多许可证分层切片（bpfman 的 Apache/BSD/GPL 三重）；绕开 GPL 的合法出口=用户态 VM（uBPF Apache-2.0）；前车之鉴=DTrace 因 CDDL 错过 Linux 十年。→ 详见第 1、6、16 章

**Cilium**——CNCF 毕业项目、eBPF 网络数据面旗舰（2016 Thomas Graf 首秀）：三种数据面全占（bpf_lxc.c TC clsact 主力+bpf_xdp.c XDP 早丢弃+socket/cgroup 层），bpf/lib/ 60+ 头文件库；系内四仓全活（cilium/tetragon/ebpf/hubble）。对照位 Calico：eBPF 是其五种数据面之一（3.33 时代 GA），tc/tcx/netkit 三种挂载可选（bpfAttachType，tech preview）、Pod veth/netkit 接口走 tc 系双向策略——现代系统常常两者并用（XDP ingress 极速 + tc 系 Pod 双向策略互补而非替代）。→ 详见第 9、16 章

**Katran**——Meta 的 L4 负载均衡器（2018-05 开源，XDP+Maglev 哈希，处理数据中心每个入站包）：CoNEXT'18 移植基准 5.2 Mpps/CPU vs 内核 IPVS 1.2 Mpps（4.3 倍增益），随核数线性扩展；至今仍是 ebpf.io Major——XDP 生产化的活标本。→ 详见第 1、9、16 章

**scx 调度器生态（scheds/rust/）**——sched_ext 之上 14 个 Rust 用户态调度器：scx_layered（多层分类，Meta 生产主力）、scx_rusty（多域 BPF+用户态负载均衡）、scx_lavd（延迟临界度感知，为游戏/交互而生）、scx_bpfland（EEVDF-like 桌面，需 6.16+）、scx_eevdf（内核 EEVDF 的 sched_ext 移植、规则可开关的对照实验台）；混合架构范式=BPF 决策面+用户态策略面经 maps/ringbuf 通信；选型看每个 README 的 "Production Ready?" 直答字段（混有 scx_horoscope 占星娱乐件）。K8s 桥接代表 Gthulhu："DRA chooses what and where; Gthulhu controls how it actually runs"——四层架构（调度可观测/分布式意图/sched_ext 执行/TID 级节点策略，按 comm 匹配 LLM engine/decode worker 与 NCCL/RDMA progress 线程）；硬边界=不是 GPU 调度器（sched_ext 只调 Linux CPU 任务，只能在资源 envelope 内优化）。→ 详见第 13 章

**eBPF for Windows**——微软官方移植（2026-11 仍周更级活跃）：工业级证明"验证器、执行引擎、宿主环境三者可解耦"——验证器=PREVAIL、执行引擎=uBPF、API 兼容层=ebpfapi.dll 暴露 Libbpf API；三种执行模式被安全模型筛选：Native/bpf2c（过检字节码逐条翻译成 C 语句编成签名 .sys——HVCI 生产系统唯一可用）、JIT（HVCI 开启时不可用）、解释器（仅 debug build）；目标是源码级兼容而非二进制兼容。→ 详见第 14 章

**硬件与学术卸载标本（hBPF / Delilah / TP4091 / OpenCSD）**——"通用 eBPF SmartNIC"品类 2016-2018 兴起后消亡（Netronome 被 Corigine 收购基本停更，但 kernel/bpf/offload.c 框架仍在主线——"厂商绑定的生态会随厂商死，进主线的框架不会"）；hBPF=纯 Python 写的 eBPF CPU 上 FPGA（多指令 1 cycle、div/mod 68 cycles 的孤本周期表，但无栈/R1 普通参数属方言）；NVMe TP4091 把 eBPF 列为 downloadable function 执行环境；Delilah=首个真硬件计算存储 eBPF 卸载系统（uBPF on ARM A53；教训=嵌入式 offload 隐形大头是 cache 一致性不是执行）。结论：离开 Linux 内核跑 eBPF 整体是活的，但重心从硬件搬进了软件。→ 详见第 14 章

**agent 支线（AgentSight / ActPlane，2026）**——eBPF×AI agent 的最新生态拼图：AgentSight（eunomia，arXiv:2508.02736）给 Claude Code/Codex 等 CLI 做 top/strace 式观测（零 SDK 零代理，TLS 追踪让闭源 CLI 可观测）；ActPlane（arXiv:2606.25189）把 IFC 信息流控制策略编译成 eBPF 内核态强制——"prompt 约束与模型 guardrail 是概率性的，ActPlane 是确定性的"；反向的"生态自身 agent 化"亦已显形（82 仓中至少 8 个带 CLAUDE.md/AGENTS.md）。→ 详见第 16 章

---

> **维护说明**：本表词条与定义全部取自 docs/01-16 章原文口径；章节中标注"待核实"的特性（如 ARENA 引入版本、tcx 机制细节、bpftool gen min_core_btf）未收录或仅按原文表述。核对勘误见 [../ERRATA.md](../ERRATA.md)；各词条的语料锚点（[id=N]）回到对应章节查证。
