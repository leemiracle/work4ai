# eBPF 知识库练习册（EXERCISES）

> **定位**：本练习册配合知识库 16 章（`docs/01` ~ `docs/16`）与 [docs/README.md](README.md) 的三条学习路径（快速通道 2 周 / 系统通道 3-4 月 / AI agent 通道）使用。每章 4 题、全册 64 题，按知识库四部分组织：**机制（1-6 章）/ 工程（7-8 章）/ 应用（9-13 章）/ 生态（14-16 章）**。所有题目素材取自各章"原理层/实践层/深水区"，禁止凭空编造；实操题优先复用章节实践层已验证过的本地语料路径与命令。

## 使用说明

### 难度分层（每章三档渐进，四题覆盖三档）

| 档位 | 标记 | 检验什么 | 作答方式 |
|---|---|---|---|
| 概念题 | 〔概念〕 | 原理层理解（"为什么 r10 只读""tail call 与 pseudo call 的本质区别"） | 纸面作答，能向别人讲清因果链即过关 |
| 实操题 | 〔实操〕 | 动手能力，指向本地语料可真实完成（跑通 minimal、bpftrace one-liner、读源码定位） | 在满足环境要求的主机/语料库上完成并记录输出 |
| 深水题 | 〔深水〕 | 排障、设计权衡与批判（verifier 拒绝三因、基准语境、选型反例） | 综合多章要点给出有出处的判断 |

### 题号与答案约定

- 题号 `N.M` = 第 N 章第 M 题；文末〔参考答案〕按 `答 N.M` 对应。
- 每题附**提示**：指向第 N 章具体小节（如"第 3 章 3.4.1 拒绝表"）与一手语料锚点（`grep` 命令或本地路径）——先自己作答，卡住再看提示，最后对答案要点。
- **先做题再看答案是自学闭环的关键**；答案给的是要点骨架，不是唯一表述。

### 环境要求

- **本地语料根路径**：`/usr-data/data2/kylin/network/awesome-ebpf/`。本册所有相对路径（`repos/...`、`web/md/...`、`web/pdf-txt/...`、`digests/...`、`INVENTORY.md`）均相对此根；grep/读文件类实操题**不需要 root、不需要特殊内核**。
- **动手题主机要求**（按题目标注）：
  - 基线：Linux x86_64，内核 ≥ 5.8（ringbuf/全局变量），`clang ≥ 11 -g -target bpf`、libelf/zlib、bpftool、libbpf ≥ 1.x；加载类操作需 root 或 `CAP_BPF`+`CAP_PERFMON`（5.8 前 bump `RLIMIT_MEMLOCK`）。
  - 逐题增量门槛：fentry 题 ≥ 5.5 且内核带 BTF（`/sys/kernel/btf/vmlinux` 存在）；BPF LSM 题 ≥ 5.7（实战 5.13+）且 `CONFIG_BPF_LSM=y`、`CONFIG_LSM="...,bpf"`；sched_ext 题 ≥ 6.12 且 `CONFIG_SCHED_CLASS_EXT=y`（scx 工具链 clang ≥ 18）；AF_XDP 题 ≥ 4.18；老内核兼容题可用 minimal_legacy/bootstrap_legacy 对照。
  - 无 root 环境的用户态题（第 2/14 章）：PREVAIL（GCC 13+/Clang 17+，C++23 构建）、uBPF/rbpf（rbpf 需 Rust）。
- **版本对账**：涉及"特性 X 要内核几"一律先查 `web/md/22.md`（bcc kernel-versions 矩阵，维护至 6.1）与 `web/md/8.md`（docs.ebpf.io 快照）；引用数字前查 [../ERRATA.md](../ERRATA.md)（33 条全局勘误）。

---

## 第一部分　内核机制（第 1-6 章）

### 第 1 章　历史与总论

**1.1〔概念〕** 1993 年 McCanne & Jacobson 论文用哪**两大架构革新**让 BPF 击败 CSPF/NIT？重点解释：为什么"filter in place + 非共享缓冲模型"能使 reject-all 场景的固定开销做到 4.6-5μs/包且**与包长无关**，而 NIT 大包要 450μs？

> 提示：第 1 章 1.2.1；一手数据 `grep -n "reject all\|Incremental Overhead" web/pdf-txt/86.txt`

**1.2〔概念〕** eBPF 转型（2013-2014）时 Starovoitov 尝试过哪两个失败原型？正解"真 CPU 指令的混合物"通过哪些设计同时保住了**解释器取指速度**与 **JIT 后的性能**？寄存器与 amd64 ABI 一对一映射带来什么直接收益？

> 提示：第 1 章 1.2.3 与 1.2.4；`grep -n "Failed approach\|callee saved" web/pdf-txt/36.txt`

**1.3〔实操〕** 在任意 Linux 主机上执行 `sudo tcpdump -d "tcp dst port 80"` 反汇编 cBPF，对照输出回答：(a) 哪条指令是 1993 论文为变长 IP 头 hack 进指令集的 IHL 寻址，它解决什么问题？(b) `jset #0x1fff` 在排除什么、为什么这一步对 TCP 过滤必不可少？(c) `ret #262144` 与 `ret #0` 的返回值语义是什么？

> 提示：第 1 章 1.3"第 0 步"（含完整输出与逐行读法）

**1.4〔深水〕** (a) 市面常见的"BPF 是 Linux 2.5 引入"说法错在哪？给出正确口径、证据链与引用时的规范写法。(b) 为什么 2017-2019 年文章里"eBPF 无循环"这句话今天不能再当代际事实引用？(c) 从这条勘误归纳出引用快照类语料的一般纪律。

> 提示：第 1 章 1.4 坑 1/坑 2；对照 `grep -n "2.1.75" web/pdf-txt/36.txt` 与 `grep -n "v2.5\|Jay Schullist" web/md/24.md`；版本对账查 `web/md/22.md`

### 第 2 章　VM 与指令集

**2.1〔概念〕** (a) 为什么 r10 是只读帧指针——程序写 r10 会破坏什么不变量？(b) "r1-r5 只能存数字或栈指针、永不存任意内存直接指针"这条纪律是加给谁的、服务于什么目的？(c) 说出 r0/r1-r5/r6-r9/r10 四组寄存器的分工与 x86_64 侧映射。

> 提示：第 2 章 2.2.1（含三个硬边界）；rbpf 实现佐证 `repos/qmonnet/rbpf/src/interpreter.rs` 的 `reg: [u64; 11]`

**2.2〔概念〕** tail call 与 BPF-to-BPF pseudo call 都能"跳到另一段代码"，本质区别在哪？从**调用语义（是否返回）、栈、失败行为、上限约束、跨程序传状态手段**五个维度对比，并说明为什么 rbpf 解释器干脆不支持 tail call。

> 提示：第 2 章 2.2.5 与 2.4 坑 9；第 6 章 6.2.6；上限代差 `MAX_TAIL_CALL_CNT` 现代 man 页 33 vs 4.14 时代 32

**2.3〔实操〕** (a) 手工逐字段解码字节流 `15 00 02 00 00 00 00 00`（小端主机）：写出 opcode 的 class/s/code 拆解、off 与 imm 的值、汇编语义，并解释它为什么是"所有 eBPF 程序里出现频率最高的模式之一"。(b) 无 root 环境：克隆 `repos/vbpf/ebpf-verifier` 构建 PREVAIL，对任一测试 ELF 跑 `bin/prevail <elf> <section> <function>`，再用 `--failure-slice` 对一个故意写错的程序取"致错最小指令切片"。

> 提示：第 2 章 2.3.1（0x020015 模式逐字段算位）与 2.3.3；PREVAIL 用法见第 3 章 3.3.3 末段

**2.4〔深水〕** RFC 9669 的 Security Considerations 为什么把**解释器**判为不安全源？内核侧对应哪个编译配置（其双重动机是什么）？把这套风险评估搬到"用户态嵌入 uBPF/rbpf"场景：没有了内核 verifier 兜底，uBPF 的新一代 Safe Execution Profile 用什么手段补位？

> 提示：第 2 章 2.2.8 与 2.4 坑 8；`grep -n "side-channel\|JIT_ALWAYS_ON" web/md/16.md`；uBPF 见 2.2.10

### 第 3 章　Verifier

**3.1〔概念〕** (a) verifier 两阶段各查什么（列出第一遍 CFG/DAG 的四条规则与第二遍指令模拟跟踪的四类状态）？(b) "verifier 同时是改写器"指验证通过前后完成哪几项指令变换？

> 提示：第 3 章 3.2.3/3.2.4/3.2.8；五步流水线 `grep -n "BPF_PSEUDO_MAP_FD\|state pruning" web/md/21.md`

**3.2〔概念〕** 逐字段解读 verifier log 状态行 `R8=inv(id=0,umin_value=28,umax_value=1048,var_off=(0x0; 0x7fc))`：inv/umin/umax/var_off 各是什么？tnum `(0x0; 0x7fc)` 说明了 verifier 对 R8 知道什么、不知道什么？

> 提示：第 3 章 3.2.5 与 3.3.2 四步读法

**3.3〔实操〕** 构造并观察 verifier 拒绝：(a) 以 `repos/xdp-project/xdp-tutorial/packet01-parsing/` 的解析器为底，删掉 `eth + 1 > data_end` 边界检查后编译加载，捕获 `invalid mem access` 拒绝；(b) 按"末行错误句 → PC 指令行 → 状态行 → 源码行"四步读 log，用 `llvm-objdump -S -no-show-raw-insn prog.o` 把 PC 对回 C 源码；(c) 说明 libbpf 应用里 verifier log 是经哪条路径自动打印的。

> 提示：第 3 章 3.3.1/3.3.2/3.3.3（含照抄级边界检查范式）；libbpf 日志路径见 `repos/libbpf/libbpf-bootstrap/examples/c/minimal.c` 的 `libbpf_set_print`

**3.4〔深水〕** (a) 给出新手撞墙频率最高的三类 verifier 拒绝（invalid mem access 'inv' / unbounded pointer math / infinite loop），各配一个触发代码模式与修复手段。(b) 为什么"概率上几乎必然终止"的随机循环照样被拒？这体现了 verifier 的什么哲学？(c) Maguire 说"verifier 报的错通常是真 bug"——少数例外是什么情况、此时该看什么而不是 C 源码？

> 提示：第 3 章 3.4.1 拒绝表（含 `__adddf3` 浮点与 `-fno-jump-tables`）；随机循环反例 `grep -n "bpf_get_prandom_u32" web/md/45.md`

### 第 4 章　Maps

**4.1〔概念〕** ringbuf（5.8）相对 perf event array 的优势逐条说清（至少五条），并解释 perf array 的"启动仪式"（逐核 perf_event_open 塞 fd）为什么是 ringbuf 设计要消灭的第一个痛点。

> 提示：第 4 章 4.2.5；优势清单 `grep -n "BPF_RINGBUF_OUTPUT" web/md/98.md`；libbpf 消费端 API `grep "ring_buffer__" repos/libbpf/libbpf/src/libbpf.h`

**4.2〔概念〕** map 并发三档解法（per-CPU / 原子原语 / bpf_spin_lock）各自"用什么换锁"、代价与硬约束各是什么？为什么 ARRAY 上做大 value 整体 update 有撕裂读风险、HASH 却没有？per-CPU map 的核数为什么必须按 `/sys/devices/system/cpu/possible` 计？

> 提示：第 4 章 4.2.3 与 4.4 坑 3/坑 9；spin_lock 约束清单 `grep -n "bpf_spin_lock" web/md/15.md`

**4.3〔实操〕** 30 分钟练习（知识库第 4 章原题）：把 `repos/libbpf/libbpf-bootstrap/examples/c/` 的 minimal 改成"用一个 ARRAY map 统计每个 PID 的 write 次数，用户态每秒轮询打印 top3"；第二步把上报换成 ringbuf 逐事件（对照 `bootstrap.bpf.c` 的事件结构体与 reserve/submit 配对）。完成后你能说出 BTF 定义 map、skeleton 读 map、ringbuf 消费三件事各自的标准写法位置。

> 提示：第 4 章 4.3"第一个练习"；Makefile 四步与 ringbuf 主循环在第 7 章 7.3.1/7.3.4

**4.4〔深水〕** (a) `BPF_MAP_GET_NEXT_KEY` 的四象限行为中，哪一条使"迭代中删除元素"的常规写法（lookup→处理→delete→get_next）跳元素或死循环？(b) "重启后计数器清零还是延续"为什么不是 bug 而是工具链语义？给出 ip/tc 与 libbpf 的默认差异和复用 pinned map 的正规姿势。(c) 由此归纳：长期运行的服务升级程序时 map 状态管理的检查单。

> 提示：第 4 章 4.4 坑 1/坑 12；`repos/xdp-project/xdp-tutorial/basic04-pinning-maps/README.org` 的 Gotchas 与 reuse_fd 六步

### 第 5 章　程序类型与挂载点

**5.1〔概念〕** "岗位合同三绑定"是哪三件事？内核里由 `struct bpf_verifier_ops` 的哪三个回调实现？"选一个 program type 就是在内核里选一套校验器人格"——网络类与 tracing 类的校验器人格分别住在哪个源码文件？

> 提示：第 5 章 5.1 与 5.2.1；`grep -n "get_func_proto\|is_valid_access\|convert_ctx_access" web/md/39.md`

**5.2〔概念〕** fentry/fexit 与 kprobe 六维对比表（挂载机制/BTF 依赖/参数读取/返回值/开销/稳定性），并回答：为什么 kprobe 挂载点"不是 ABI"是工程债，而 fentry+CO-RE 让签名漂移"在加载期暴露而非运行期崩"？

> 提示：第 5 章 5.2.3；直接解引用反例 `grep -n "inv on R1" web/md/45.md`（章内转写作 "R1 invalid mem access"）；ABI 边界 `grep -n "not.*ABI\|ABI" web/md/11.md`

**5.3〔实操〕** 同一"统计包数"逻辑写三个版本（可参照第 5 章 5.3 代码骨架）：`SEC("xdp")` 返回 XDP_PASS、`SEC("socket")` 返回 `skb->len`、`SEC("fentry/tcp_v4_connect")` 用 `BPF_PROG` 宏强类型读参。完成后回答：三者 context 类型与返回值语义各由什么决定？再用 `bpftool feature probe` 与 `bpftool prog` 分别回答"本机内核支持什么"与"本机已加载什么"。

> 提示：第 5 章 5.3 三步；三绑定出处 `grep -n "program type" web/md/20.md`

**5.4〔深水〕** (a) "generic XDP 不是 XDP"——它挂在收包路径的哪个位置、丢掉了 XDP 的哪项核心收益？生产抗 DDoS 选型前的必查动作是什么？(b) 在 bcc kernel-versions 矩阵（`web/md/22.md`）里查不到 NETFILTER 程序类型，为什么这不代表它不存在？(c) 由此给出"版本表会骗人的两个年代断层"。

> 提示：第 5 章 5.4 坑 2/坑 5；generic 路径见第 9 章 9.2.1

### 第 6 章　Helpers

**6.1〔概念〕** "helper 体系 = eBPF 的系统调用层（方向反过来）"——支撑这个类比的三个机制事实（白名单如何实现、5 参数上限从哪来、为什么零 FFI 开销）分别是什么？

> 提示：第 6 章 6.1 与 6.2.1/6.2.2；`grep -n "five arguments\|foreign-function" web/md/15.md`

**6.2〔概念〕** `bpf_trace_printk` 的三个硬限制 + 一个全局性缺陷是什么？按"聚合统计 / 流式事件 / 复杂格式化"三类需求给出正确的替代通道排序（含版本门槛）。

> 提示：第 6 章 6.4 坑 1；输出通道三代演进坑 11；`bpf_snprintf` 5.13 / `bpf_trace_vprintk` 5.16

**6.3〔实操〕** (a) 用 bpftrace 完成 one-liner 三连：列 syscall tracepoint 探针、打印 `tracepoint:syscalls:sys_enter_open` 的进程名与文件名、对指定 pid 统计 read 返回字节数的 log2 直方图。(b) 跑 `repos/lizrice/ebpf-beginners/` 的 `ebpf.py`（kprobe 挂 clone + BPF_HASH 按 UID 计数），对照 `hello.py` 说出 BCC Python 路线"前端胶水有多薄"。(c) 用"tracepoint format 文件 + 头文件 grep"套路，自己拼出过滤 `madvise(behavior==MADV_DONTNEED)` 的完整命令。

> 提示：第 6 章 6.3.3 与第 11 章 11.3.1（one-liner 全集与 madvise 收官套路）；`cat /sys/kernel/debug/tracing/events/syscalls/sys_enter_madvise/format`

**6.4〔深水〕** (a) 为什么调完 `bpf_skb_store_bytes`/`bpf_xdp_adjust_head` 这类改包 helper 后，先前对 data/data_end 的边界检查全部作废？机制根源是什么（包可能发生什么）？(b) "我的内核有这个 helper"≠"这个挂载点能用"——用两个三重矩阵错配实例说明。(c) GPL 门控如何决定"商业闭源 eBPF 程序几乎只能做网络数据面"？

> 提示：第 6 章 6.4 坑 2/坑 7/坑 8；改包名单 `grep -n "bpf_helper_changes_pkt_data" web/md/15.md`；GPL 规律：读内核内部结构的 helper 几乎全 GPL-only

---

## 第二部分　现代工程（第 7-8 章）

### 第 7 章　加载、生命周期与 libbpf

**7.1〔概念〕** (a) libbpf 把 BPF 应用生命周期划成 open → load → attach 三段，每段各发生什么（open 阶段"尚未发生任何 bpf(2) 调用"意味着什么）？(b) 为什么 `const volatile` 只读全局变量必须在 open 与 load 之间赋值、load 之后就冻结？少写 `const` 或 `volatile` 各自的后果是什么？

> 提示：第 7 章 7.2.2 与 7.2.6；`grep -n "rodata\|const volatile" web/md/100.md`

**7.2〔概念〕** 三代前端（iproute2 裸加载 / bcc 运行时重编译 / libbpf+CO-RE）对比表里，"谁做翻译、目标机依赖什么、跨内核可移植性"三行各是什么？bcc opensnoop 在 strace 下 10000+ 行 syscall vs 纯 C 版 42 行，这个数量级差异的机制根源是什么？

> 提示：第 7 章 7.2.5；BCC rewriter 机制 `grep -n "bpf_pseudo_fd\|DEBUG_PREPROCESSOR" web/md/101.md`

**7.3〔实操〕** 跑通 minimal 并回答四问：(a) `my_pid` 为什么不需要任何 map 声明就能在内核态与用户态之间共享？(b) `skel->bss->my_pid = getpid()` 为什么是"零 syscall"的写？(c) minimal_ns / minimal_legacy / bootstrap_legacy 三个兄弟样例各解决什么兼容问题？(d) 构建流水四步中 `bpftool gen object`（静态链接）与 `bpftool gen skeleton` 各产出什么？

> 提示：第 7 章 7.3.1/7.3.2；本地仓 `repos/libbpf/libbpf-bootstrap/examples/c/`（README 实测输出 + Makefile 注释）

**7.4〔深水〕** (a) "进程死了 BPF 程序还在内核里"有哪三种残留路径？给出标准排查命令序列。(b) 4.x 时代手写加载器撞上的 kern_version EINVAL 陷阱：为什么**不能用 uname 动态计算**这个字段（用 Ubuntu 4.15.0-33 的具体数字说明）？libbpf 为什么能让用户完全忘记这件事？(c) verifier log_buf 的"悖论"是什么、libbpf 的对策是什么？

> 提示：第 7 章 7.4 坑 8/坑 1/坑 3；`grep -n "kern_version\|LINUX_VERSION_CODE" web/md/101.md`

### 第 8 章　CO-RE 与 BTF

**8.1〔概念〕** (a) "程序在 5.3 编译、5.4 跑不起来"的三种具体断裂情形是什么？除内核版本外还有哪两类因素在制造布局漂移？(b) CO-RE 三要素（BTF / Clang / libbpf）各司什么职？"记字段名而非硬编码 offset"落在 ELF 的哪个部位？

> 提示：第 8 章 8.2.1 与 8.2.6；`grep -n "5.3\|5.4" web/md/85.md`；core_relo 子区在 `web/md/83.md` §.BTF.ext

**8.2〔概念〕** BTF dedup 五个 pass 各做什么？消融实验（关掉类型合并只做朴素去重只能压到 12.71MB/9.5x，全量 dedup 达 104x）证明了紧凑性的大头是什么？字符串区的"name_off 引用"设计让"比较字符串相等"退化成了什么操作？

> 提示：第 8 章 8.2.3；`grep -n "104x\|137x\|12.71" web/md/84.md`

**8.3〔实操〕** (a) 生成 vmlinux.h：`bpftool btf dump file /sys/kernel/btf/vmlinux format c > vmlinux.h`（或直接读 `repos/libbpf/libbpf-bootstrap/tools/gen_vmlinux_h.sh`——全文一行）；说明仓内 submodule 预生成版为什么**不必与本机内核版本精确匹配**。(b) 读 `repos/libbpf/libbpf-bootstrap/examples/c/bootstrap.bpf.c`，把 `BPF_CORE_READ(task, real_parent, tgid)` 改写成等价的 `bpf_probe_read_kernel` 逐步版本，体会两者在"offset 写死 vs 现场重定位"上的差别。(c) 在 `repos/libbpf/libbpf/src/bpf_core_read.h` 里 grep 出 `bpf_core_field_exists` 展开到哪个 Clang builtin、`BPF_TYPE_MATCHES` 枚举取值有几个。

> 提示：第 8 章 8.3.2/8.3.4（含 bpf_core_read.h 行号锚 L44/L166-187/L250/L525）

**8.4〔深水〕** (a) "CO-RE 不是万能移植"——它解决什么、不解决什么？跨大版本分发的正确姿势（存在性分支如何与 `const volatile` 配合让 verifier 做死代码剪枝）？(b) vmlinux.h 为什么不能与系统内核头混用？正确 include 三件套是什么？(c) BTF 工具开发者必踩的 `insn_off` 双单位陷阱：kernel API 与 ELF API 的单位各是什么？(d) 防幻觉纪律：在语料里 grep 不到 `may_exist` / `___execute_bpf` 时应如何处置这类名词？

> 提示：第 8 章 8.4 坑 4/坑 2/坑 1/坑 5-7；`grep -n "insn_off" web/md/83.md`

---

## 第三部分　应用域（第 9-13 章）

### 第 9 章　XDP 与 tc

**9.1〔概念〕** (a) 五种 XDP action 的语义各是什么？`XDP_ABORTED` 内核实际怎么处理？(b) `XDP_TX` 与 `XDP_REDIRECT` 的硬边界（同口 vs 跨设备）是什么——跨设备转发要求目标驱动实现什么接口？(c) 2016 年提案期只有几个 action，REDIRECT 何时以什么形态落地？

> 提示：第 9 章 9.2.2 与 9.4 坑 9；action 表 `grep -n "XDP_ABORTED" web/md/62.md`

**9.2〔概念〕** 为什么单核 `bpf_redirect` 只有 7.5Mpps 而 `bpf_redirect_map` 达 13.0Mpps？说清"map 版把 RX bulking 藏进 XDP core"的机制（NAPI poll 末尾统一 flush、批量≤64 摊销了什么昂贵操作），以及这个设计带来的"新增 redirect 目标类型零 driver 改动"红利。CPUMAP 的两大用途是什么？

> 提示：第 9 章 9.2.4；`grep -n "bpf_redirect_map\|ptr_ring\|CPUMAP" web/pdf-txt/75.txt`

**9.3〔实操〕** veth 对十分钟实验（driver 级 XDP 不需要 100G 网卡）：建 veth0/veth1 → 以 `repos/xdp-project/xdp-tutorial/basic01-xdp-pass/xdp_pass_kern.c` 为底改成"只放行 IPv6、其余 XDP_DROP"（边界检查照抄第 3 章 3.3.3 范式）→ `ip link set dev veth1 xdp obj ... sec xdp` 挂载 → `ip link sh veth1` 确认 xdp flag → veth0 侧 tcpreplay/手工灌混合流量，veth1 侧 tcpdump 验证 IPv4 零到达。完成后回答：解析失败为什么应返回 XDP_PASS（fail-open 设计）？

> 提示：第 9 章 9.3.1/9.3.2（完整命令流出自 `web/md/62.md`）；测试环境脚手架 `repos/xdp-project/xdp-tutorial/testenv/testenv.sh`

**9.4〔深水〕** (a) 基准卫生：引用任何 XDP 性能数字前必须核对哪三个语境（用 24M / 10.1M / 9.7M 三组数字各配出处）？两个能毁掉全部基准的现场失误是什么？(b) 为什么说"XDP 不是免费的"——启用即改变 RX ring 内存模型的代价与后续解法？(c) 勘误题：把 Suricata bypass 的 39 Gbps 直接说成"XDP 的成绩"错在哪（先查 `../ERRATA.md`）？

> 提示：第 9 章 9.2.7 与 9.4 坑 2/3/5；勘误见 `web/md/190.md`（NFQ mark 通道口径）与第 10 章 10.3

### 第 10 章　AF_XDP 与用户态网络

**10.1〔概念〕** 用"共享堆场与提单"模型说清 UMEM + 四环：四个环各自的生产者→消费者方向与载荷是什么？"收包的上游是 FILL 不是 RX"——为什么初学者最常把这个因果搞反？两条语义红线（completion 不保证发送成功 / 同一缓冲区不得同时在两个环）各防住什么事故？

> 提示：第 10 章 10.2.1（含所有权时序图）；`grep -n "FILL\|COMPLETION" web/md/79.md`

**10.2〔概念〕** copy（XDP_SKB/XDP_DRV）与 zero-copy 三种模式的触发条件、拷贝次数与可用性各是什么？内核 bind 时默认行为是什么、生产代码为什么必须用 `XDP_OPTIONS` 查询实际模式而不是假设？`XDP_SHARED_UMEM` 的两种形态（同 queue 多 socket vs 跨 queue/netdev）在 FILL/COMPLETION 环的拓扑上有什么区别？

> 提示：第 10 章 10.2.3/10.2.4

**10.3〔实操〕** 读 `web/md/79.md`（kernel.org AF_XDP 官方文档本地快照）完成：(a) 抄写 xdp_sock_prog 骨架（`SEC("xdp_sock")` + `bpf_map_lookup_elem(&xsks_map, &index)`），解释"必须加载 XDP 程序且 XSKMAP 至少放一个 socket 才能收到流量"的机制（内核在重定向时校验什么、槽位空会怎样）；(b) 写出 rxdrop 基准的三步跑法（ntuple 导流到指定 queue → `-N` 驱动原生模式 → 观察统计），并说明 `ethtool -L combined 1` 与 ntuple 两种导流手段各适用什么场景；(c) 排障：`XDP_STATISTICS` 的 `rx_invalid_descs/tx_invalid_descs` 非零说明什么性质的问题？

> 提示：第 10 章 10.2.2 与 10.3；骨架代码 L342-352、FAQ 与统计节见 `grep -n "XSKMAP\|XDP_STATISTICS" web/md/79.md`

**10.4〔深水〕** (a) "绑了 queue 0 却收不到包"的机制根源（NIC 队列与核的关系）与两个官方解法？"同一 UMEM 缓冲区同时喂 FILL 和 TX 环会包损坏"是什么性质的错误、为什么说它"静默且难复现"？(b) 用户态网络三路线选型决策树的**第一问**是什么？什么条件下连"匝道"都不需要（参照 upf-bpf 的全内核路线）？(c) 跨路线直接比较"40x / 25× / 4-50×"这些倍数为什么是选型大忌？

> 提示：第 10 章 10.4 坑 1/2 与 10.2.7；全内核对照 `repos/navarrothiago/upf-bpf/`；三路线深潜 `knowledge/f-stack.md`、`knowledge/passt.md`

### 第 11 章　可观测性

**11.1〔概念〕** (a) 四类探针（kprobe / tracepoint / uprobe / USDT）按"稳定性 × 能拿到什么上下文"排出对比表，fentry/fexit 为什么被称为"BTF 时代的第三条路"？(b) Brendan Gregg 的工程铁律"尽可能用静态 probe"背后的原因是什么？kprobe 除了不稳定外还有哪类硬失效（提示：inline/static）？

> 提示：第 11 章 11.2.1；铁律 `grep -n "5 Things" web/md/47.md`；kprobe 转 tracepoint 实战复盘见 digests/08

**11.2〔概念〕** "enter/exit 双探针 + 时间戳 map"是延迟测量的通用范式，它的三个关键点（键用 tid / 出口带 `/@start[tid]/` 过滤 / 算完 delete）各防住什么 bug？半程捕获为什么会产生天文数字假值？

> 提示：第 11 章 11.2.4；逐字拆解 `grep -n "@start\[tid\]" web/md/58.md`

**11.3〔实操〕** (a) bpftrace one-liner 全套练习：`bpftrace -l 'tracepoint:syscalls:sys_enter_*'` 列探针 → `sys_enter_open` 打印 comm + `str(args->filename)` → `raw_syscalls:sys_enter` 按进程计数 → `sys_exit_read` 对指定 pid 做 `hist(args->retval)` → `profile:hz:99` 采内核栈。(b) SSL 明文观测：说明 uprobe 挂 `SSL_write`（加密前出站明文）与 `uretprobe` 挂 `SSL_read`（解密后明文）为什么"不需要证书也不解密"；读 `repos/hengyoush/kyanos/bpf/` 目录，数一下 OpenSSL 逐版本矩阵有多少个独立 .bpf.c、这说明工程化天花板在哪。(c) 记录实验：uprobe 方案每请求额外延迟约多少 µs？

> 提示：第 11 章 11.3.1/11.3.3；实测数字 `grep -n "0.2µs\|SSL_write" web/md/114.md`

**11.4〔深水〕** rstat 是全语料最珍贵的"何时不该 eBPF"定量反例：(a) 写出 poller 与 probe 两条 CPU/s 成本公式，并用"常规负载 12454 switches/s 花 8ms/s、切换风暴 240 万/s 吃 1.8 核"这组数字解释"always-on probe 在机器最忙时收费最贵"为什么成立。(b) eBPFChirp 两组实测（uprobe 挂 SSL ~0.2µs/0.3% CPU vs syscall tracepoint 挂高频调用 `sys_exit_read` 11.69% CPU，差约 85 倍的量级）给你什么挂点选型纪律？(c) 对照 DeepFlow 宣称 profiling <1% 开销，说明"低开销"这句话的完整表述应该是什么的函数？

> 提示：第 11 章 11.4 ③④；`grep -n "1.8 CPU cores\|Version 1" repos/overyonder/rstat/README.md`；对照 `grep -n "uprobe 289" digests/17-项目·可观测.md`

### 第 12 章　安全

**12.1〔概念〕** (a) 防御三代演进（Falco 事后检测 → Tracee/Tetragon 内核态 enforce → BPF LSM 强制访问控制）各自"判定时机与判定位置"是什么？(b) tracepoint 与 LSM hook 的本质区别（观察点 vs 决策点）如何用 fileless 检测案例说明——为什么传统工具只能"检测 memfd: 前缀"而 BPF LSM 能"阻断"？

> 提示：第 12 章 12.2.4/12.2.5；fileless 对照 `grep -n "bprm_creds_from_file\|point of no return" web/md/255.md`

**12.2〔概念〕** "能力对称性——检测原语与攻击原语是同一批"：bad-bpf 的六个程序各演示哪种原语滥用（bpfdos / exechijack / pidhide / sudoadd / writeblocker / textreplace）？sudoadd 为什么是"精准单进程提权"——cat 与 sudo 看到的 /etc/sudoers 为什么不一样？textreplace2 的 bpffs pin 驻留形态对防御者有什么反向启示？

> 提示：第 12 章 12.2.2/12.2.3；`repos/pathtofile/bad-bpf/README.md`

**12.3〔实操〕** (a) 读 `repos/linux-lock/bpflock/bpf/filelesslock.bpf.c`：判据 `BPF_CORE_READ(file, f_path.dentry, d_inode, __i_nlink)` 为什么"链接数为 0 即匿名文件"？挂点 `lsm/bprm_creds_from_file` 处 ELF header 与 mm_struct 各处于什么状态？(b) 对照第 12 章 12.3 的 docker 复现命令与三行日志证据链（execsnoop → lsm 拒绝 → execve 失败），写出启用 BPF LSM 的三个前置条件。(c) 读 `repos/cilium/tetragon/examples/policylibrary/bpf.yaml`（监控 BPF 自身使用的现成策略）：它用 kprobe 挂哪两个函数、`ignore: callNotFound: true` 在处理什么版本漂移？把哪一段改成 `Sigkill` 即从观察转强制？

> 提示：第 12 章 12.3 防御路径一/二；enforce 枚举 `grep -n "KPROBE_ACTION" repos/cilium/tetragon/api/v1/tetragon/tetragon.proto`

**12.4〔深水〕** (a) `bpf_probe_write_user` 为什么天生不适合当安全地基（UAPI 的 TOC-TOU 警告 + TripleCross 源码注释里的三条不可靠实录）？(b) detect→enforce 的误杀风险：Tetragon `Sigkill` 策略写错的代价是什么？bpflock 的部署纪律（先 allow 档全量观察再收紧）说明什么？(c) "防御程序自己也是 eBPF"的绕过面：攻击者拿到 root 后能对防御探针做什么？防御侧的两项对冲手段（自己的 LSM 程序 pin + 限制 bpf() syscall）分别对应哪个组件？

> 提示：第 12 章 12.4 坑 1/2/3；不可靠实录 `repos/h3xduck/TripleCross/src/ebpf/include/bpf/exec.h` 注释；bpfrestrict 挂 `lsm/bpf`

### 第 13 章　sched_ext 调度器

**13.1〔概念〕** (a) struct_ops 机制如何让 BPF 程序安全接管 sched_class？`struct sched_ext_ops` 与 `sched_class` 是什么关系？(b) 为什么说"struct_ops 没有任何 ABI 要求"恰恰是 sched_ext API 快速演进的自由度来源，代价又是什么？(c) 唯一必须实现的字段是什么？不实现 `.select_cpu()` 时内核如何兜底？

> 提示：第 13 章 13.2.1；SCX_OPS_DEFINE 实例 `repos/sched-ext/scx/scheds/rust/scx_rusty/src/bpf/main.bpf.c` L2008 起

**13.2〔概念〕** 画出/背出四步调度周期（wakeup → select_cpu → enqueue → dispatch → local DSQ → CPU 运行）：(a) DSQ 的"insert/move"术语约定与"CPU 永远只从自己的 local DSQ 取任务"意味着什么？(b) 为什么只用内置 DSQ（全局 FIFO + 每 CPU local）时根本不用实现 `ops.dispatch()`——这是 scx_simple 几十行能跑的原因吗？(c) 内置 DSQ 支持优先级（vtime）语义吗？

> 提示：第 13 章 13.2.2/13.2.3；一手出处 `repos/sched-ext/scx/OVERVIEW.md` "Scheduling cycle" 节

**13.3〔实操〕** 五分钟上手（需 6.12+ 与 `CONFIG_SCHED_CLASS_EXT=y`，本地语料对照 `repos/sched-ext/scx/README.md` Getting Started 会话）：(a) `cat /sys/kernel/sched_ext/state` 前后对照验证"跑 scx_simple 即切换、Ctrl-C 即回退内核默认调度器"；(b) 选型三连：游戏延迟 / K8s-GPU 集群 / 生产分层各选哪个 scx 调度器、依据各 README 的哪个字段判断"生产就绪"？(c) scx_bpfland 的 `--monitor` 与 scxtop 各解决什么观测需求？

> 提示：第 13 章 13.3.2/13.3.3；选型依据 = 各 `scheds/rust/scx_*/README.md` 的 "Production Ready?" 直答字段

**13.4〔深水〕** (a) sched_ext 的三层安全兜底各是什么？官方原话"最坏情况是饿线程直到 watchdog 触发"为什么不包括 panic？(b) scx_bpfland 在 Linux 6.13 上 verifier 直接失败的两个原因是什么——这如何说明"同一框架、不同内核代际能力不同"？(c) "API 无稳定承诺"对 out-of-tree 调度器维护者意味着什么（对照 BREAKING_CHANGES.md 与发行版打包路径）？(d) 挂起（Ctrl-Z）语义陷阱：为什么对 scx_simple 安全的 SIGSTOP 对 layered/rusty/Gthulhu 用户态模式是策略面失速？

> 提示：第 13 章 13.2.4 与 13.4.1/13.4.5/13.4.6；bpfland 失败原因 `repos/sched-ext/scx/scheds/rust/scx_bpfland/README.md` 开头自述

---

## 第四部分　生态与边界（第 14-16 章）

### 第 14 章　硬件卸载与跨平台

**14.1〔概念〕** 硬件卸载要同时维护哪**三份一致性契约**？各举一个语料实例证明契约会被真实打破（NFP 的受限清单 / Suricata hw 模式的开关要求 / 时分复用多线程）。为什么说"能在内核加载"只是卸载的必要条件而非充分条件？XDP 在卸载对象里有什么结构性优势？

> 提示：第 14 章 14.2.1；受限清单 `grep -n "双重校验\|尾调用" digests/11-内核源码入口.md`；`grep -n "xdp-mode" web/md/188.md`

**14.2〔概念〕** eBPF for Windows 如何用工业级体量证明"验证器、执行引擎、宿主环境三者可解耦"（组件四层各是什么）？HVCI 为什么筛掉 JIT 与解释器、只留 bpf2c native 生产路径——这对"任何带强制代码完整性的宿主都会筛掉部分执行模式"有什么一般性启示？

> 提示：第 14 章 14.2.5 与 14.4 坑 4；`grep -n "bpf2c\|HVCI" repos/microsoft/ebpf-for-windows/README.md`

**14.3〔实操〕** 用户态零 root 跑通 eBPF 一条龙（本地仓均在）：(a) PREVAIL 验证：`repos/vbpf/ebpf-verifier` 构建后 `bin/prevail <elf> <section> <function>` 输出 PASS/FAIL，对 `ebpf-samples/` 里的 invalid 反面教材跑一遍并加 `--failure-slice`；(b) uBPF 执行四步 API（ubpf_create → ubpf_register → ubpf_load → ubpf_exec，头文件 `repos/iovisor/ubpf/vm/inc/ubpf.h`），或 Rust 侧直接依赖 rbpf（`repos/qmonnet/rbpf/README.md` 的 API 节）；(c) 写出 uBPF 与内核的 context 约定差异（r2=mem_len 扩展）——配 PREVAIL 验证过的程序喂 uBPF 前应先读哪份文档？

> 提示：第 14 章 14.3 路径一；第 2 章 2.2.10/2.4 坑 11；`repos/iovisor/ubpf/docs/VerifiedPrograms.md`

**14.4〔深水〕** (a) NFP SmartNIC 路线兴衰给出哪两条教训（厂商绑定生态 vs 进主线的框架）？今天的活跃度判定是什么？(b) Delilah 的 ~15ms 延迟地板：主凶是什么、为什么说"offload 的性能瓶颈通常在搬运与一致性而不在执行"？selective cache flushing 与 BAR/DMA 交叉点各给出什么工程结论？(c) 计算存储场景的 verifier 空窗为什么存在（TP4091 数据按摩需要什么、与 Linux verifier 的终止性模型如何错位）？引用"eBPF 进 SSD"叙事时应带上什么限定？

> 提示：第 14 章 14.2.2/14.2.4 与 14.4 坑 5/6；`grep -n "selective cache\|TP4091" web/pdf-txt/96.txt`（注意 `web/md/96.md` 是损坏文件）

### 第 15 章　工具链与工程实践

**15.1〔概念〕** (a) 加载形态三代演进（一次性命令 → 守护进程化 → OCI 分发）各代的代表与死因？"bpfd 撞名考古"：三个 bpfd 各是谁、什么形态、现状如何、继任者是谁？(b) bpfman 的三大能力是什么、"部署 eBPF 应用无需额外特权"靠什么组件实现？

> 提示：第 15 章 15.2.2；`grep -n "bpfman load image" repos/bpfman/bpfman/docs/quick-start.md`

**15.2〔概念〕** 语言库三路线（cilium/ebpf 纯 Go / libbpfgo 薄封装 / aya 纯 Rust）的选型第一性判断是什么？"要不要追新内核特性"与"要不要单二进制分发"分别把决策推向哪条路线？bpf2go + go:embed 标准工作流三步是什么？

> 提示：第 15 章 15.2.3 与 15.3 路径 3；`grep -rn "go:generate.*bpf2go" repos/cilium/ebpf/examples/`

**15.3〔实操〕** 三件事串起"即取即用→自测→单测"：(a) 在 `repos/iovisor/bcc/libbpf-tools/` 找到 biolatency/runqlat/opensnoop 的 CO-RE 版（.bpf.c + .c 三件套），对照 `repos/iovisor/bcc/tools/biolatency_example.txt` 学会读输出——新项目为什么一律选这版而非 `tools/*.py`？(b) `repos/niclashedam/ebpf-kill-example/` 跑 `make deps && make && make test`：test.sh 的端到端自测逻辑是什么（起循环进程→kill -9→验证什么）？(c) `BPF_PROG_RUN` 单测的 `data_in/data_size_in/repeat` 三个字段各干什么——为什么说"单测与压测同一套 API"？

> 提示：第 15 章 15.2.5 与 15.3 路径 0/路径 2；BPF_PROG_RUN 细节 `grep -n "data_size_in\|repeat" web/md/118.md`

**15.4〔深水〕** (a) 四层测试金字塔（selftests / BPF_PROG_RUN / bpfcompat / Bencher）各回答什么问题？"单测保正确、内核矩阵保可加载、持续基准保不劣化"的对应关系是什么？(b) CO-RE 的"虚假安全感"：真失败源有哪四类？bpfcompat 的 quirk-library 记录的是什么性质的坑？(c) 排障四板斧的正确顺序是什么——"程序没加载成功"与"加载了但行为不对"分别先用哪件工具？

> 提示：第 15 章 15.2.5/15.2.6/15.2.7 与 15.4；`grep -n "quirk" repos/Kernel-Guard/bpfcompat/README.md`；四板斧实证 `grep -n "bpftool prog dump jited\|llvm-objdump" repos/fzakaria/eBPF-mpls-encap-decap/README.md`

### 第 16 章　生态与社区

**16.1〔概念〕** (a) 画出六层生态地图（L0-L6）并各举代表项目；可观测线占 Emerging 席位约多少比例、印证了什么？(b) ebpf.io 全景页的收录门槛（Emerging 与 Major 两档）各是什么？这套门槛作为治理机制过滤掉了什么？

> 提示：第 16 章 16.2.1/16.2.2；`grep -n "Requirements\|Major" web/md/4.md`

**16.2〔概念〕** (a) IO Visor 兴衰的三条本地证据链是什么？它的职能被谁瓜分？(b) "eBPF Foundation 不收编项目"与 CNCF 如何互补？(c) netdev 邮件列表的规模数字（订阅数/累计邮件/2026-09 峰值）说明"旧介质承载最高科技含量的协作"——制度根源是什么（patch 工作流与什么深度绑定）？

> 提示：第 16 章 16.2.3/16.2.4 与 16.4.4；订阅数 `grep -n "netdev\|xdp-newbies" web/md/281.md`；流量 `grep -n "15937" web/md/280.md`（原始归档表不带千分位）

**16.3〔实操〕** 入行第一步的三件小事：(a) 用 `grep -n "<仓名>" INVENTORY.md` 查克隆时点提交日，给三个仓做五档分层判定练习——bpflock（什么档、什么含义）、merbridge（哪年归档）、Ingero/Synapse（什么状态）；(b) 按 16.3 第 1 阶给出新手提问的列表优先级与订阅入口（subspace.kernel.org，majordomo 为什么已废弃）；(c) 读 `repos/xdp-project/xdp-project/areas/` 任一子系统笔记与 README.org——这个顶层仓"不是代码仓"是什么、任务管理用什么机制（OWNER 属性认领制）？

> 提示：第 16 章 16.3/16.4.1 与 16.2.4；分层纪律：A 档可直接选型、D 档只当教材、E 档引用必须标注现状

**16.4〔深水〕** (a) "任何 awesome 清单都是快照而非数据库"：化石挂架的三个实例（两个同名 bpfd / Ingero 404 / merbridge 归档）说明清单缺什么机制？引用前的验活动作是什么？(b) 给内核提第一个 patch：Subject 前缀三选一（`[PATCH bpf]` / `[PATCH bpf-next]` / `[PATCH net-next]`）各对应什么场景？测试先行的硬要求是什么？发帖用什么工具链？(c) 批判题：star 季度排序 + ">50 stars" 门槛使官方地图具有哪两种系统性偏向？2026 年"eBPF × AI agent"双向奔赴的三条支线各是什么？

> 提示：第 16 章 16.4.2/16.2.4/16.3 第 3 阶/16.4.5；patch 礼仪 `web/md/280.md` 实时贴 + 内核树 `Documentation/bpf/bpf_devel_QA.rst`；agent 支线 `digests/16-项目·工具.md`（AgentSight/ActPlane）与 `digests/18-项目·安全与调度器.md`（Inner Warden 转型）

---

## 参考答案

> 以下是**要点骨架**而非唯一表述；建议先独立作答再对照，重点检查因果链是否完整、数字是否带出处。编号与题号一一对应。

### 第一部分　内核机制（第 1-6 章）

**答 1.1**　两大革新：①**寄存器式过滤机取代 memory-stack 表达式树**——CSPF 的操作数栈在寄存器 CPU 上被模拟（为虚拟栈指针生成加减指令、栈元素真实访存），而寄存器机让抽象寄存器直接落物理寄存器；②**filter in place + 非共享缓冲模型**——在驱动 DMA 落包处原位判定，拒绝的包零拷贝。reject-all 与包长无关的原因：NIT 要先把每个包从 mbuf 拷进 STREAMS 消息缓冲（两级拷贝）再过滤，拷贝成本随包长线性增长（216ns/byte），即使包最终被丢弃也要付；BPF 在拷贝发生之前就拒绝，只花判定成本（增量 0 ns/byte），大包时 450μs vs 5μs 差近两个数量级。[web/pdf-txt/86.txt]

**答 1.2**　失败原型：①**从零设计一个 VM**——性能太慢，且用户态工具链要全部重造；②**让内核直接验证 x86 指令**——指令组合爆炸，每种 CPU 架构都要重写一个 verifier。正解：取"真 CPU 指令的混合物"（幻灯口径 10% cBPF + 70% x86 + 25% arm64 + 5% risc，加总 110% 属笔误，表意为"以真实 CPU 指令为主体"）——把 `mov rax,rbx` 改名成 `mov r1,r2`、统一调用约定、**定长编码**（解释器单 C switch 取指快）、**复用 cBPF 编码骨架**（经典程序平凡转译）。寄存器与 amd64 ABI 一对一（r0=rax、r1-r5=rdi/rsi/rdx/rcx/r8、r6-r9=rbx/r13-r15、r10=rbp）、call 直映 x86 call——JIT 退化为"改名翻译"，无寄存器分配与指令选择，**零 FFI 开销**，"用户态编译器以为自己在生成简化版 x86"。[web/pdf-txt/36.txt]

**答 1.3**　(a) `(011) ldxb 4*([14]&0xf)`——把 IP 头长度字段（IHL，偏移 14 处的低 4 位）乘 4 写进变址寄存器 X，解决"变长 IP 头导致 TCP 头偏移不固定"；这个寻址模式是 1993 论文专门 hack 进指令集的。(b) `jset #0x1fff` 位测试 IP 偏移 20 的 flag 字段——非零说明是 IP 分片的非首片，**非首片没有 TCP 头**，直接跳到丢弃，否则后续 `ldh [x+16]` 会读到错误位置。(c) cBPF 的 return 值 = **保留字节数**：非 0（262144=256KB snaplen）= 接受并截断到该长度；0 = 丢弃。"过滤器不仅决定收不收，还决定收多少"（Mike Karels 的建议）。[web/md/24.md 的 tcpdump -d 输出；第 1 章 1.3]

**答 1.4**　(a) "v2.5 引入"出自 igalia 博客转述；Starovoitov 本人在 netconf 2015 幻灯写"introduced in linux in 1997 in version 2.1.75"。采信**作者口径 1997 年 2.1.75**（2.1.x 是 2.2 的开发线）；Jay Schullist 的贡献真实，但 2.5 更像后续系列内维护演化的时点。规范写法："1997 年 2.1.75（作者口径）"。(b) "无循环"是 2017-2019 快照：5.3（2019）起 bounded loops 落地，verifier 只要能证明循环出口条件必然为真即放行。(c) 纪律：**数量与能力口径全部是快照**（12 种 prog type/2017 vs 约 30 种/当代；1M 指令上限 5.2 才有）——引用旧文任何"现在时"断言前先对 `web/md/22.md` 版本矩阵校准，性能与版本数字必须带年代与出处。[第 1 章 1.4 坑 1/2/3]

**答 2.1**　(a) r10 指向本程序 512 字节栈的栈顶，是所有栈相对寻址（`*(u64 *)(r10-8)`）的基准；程序写 r10 会让栈帧基址漂移、后续所有栈访问失去意义，verifier 拒绝（运行时在做 BPF-to-BPF 调用时内部调整 r10 分配子栈帧属于运行时行为，不破坏程序视角不变量）。(b) 这条纪律是**刻意加给 verifier 的**：把内存模型简化到"寄存器里只有标量与栈指针"，类型检查才做得正确、做得起。(c) r0=返回值（helper 返回 + 程序退出码）=rax；r1-r5=调用参数（程序入口 r1=context），caller-saved=rdi/rsi/rdx/rcx/r8；r6-r9=callee-saved=rbx/r13/r14/r15；r10=只读帧指针=rbp。三个硬边界补充：不能访问 IP/返回地址/真实栈指针；只能调 helper/kfunc 不能调任意内核函数。[web/md/11.md、26.md、36.txt]

**答 2.2**　①调用语义：tail call 是"复用栈帧的**跳转**而非调用，永不返回"（调用者的栈/寄存器值对新程序不可见）；pseudo call 是正常函数调用、有独立栈帧、EXIT 返回调用方。②栈：tail call 复用同一栈帧；pseudo call 受"调用链合计栈深 ≤512B（大栈架构 2KiB）"约束。③失败行为：tail call 索引无效/超层数时**静默 fall-through 继续执行原程序**（既是默认分支特性也是幽灵 bug 源）；pseudo call 编译期解析不存在编译错。④上限：tail call 受 `MAX_TAIL_CALL_CNT`（现代 man 页 33，4.14 时代 32）层深限制；pseudo call 受调用深度限制（uBPF/rbpf 为 8）。⑤跨程序传状态：只能靠 per-CPU map 或 skb->cb。rbpf 解释器不支持 tail call 是用户态运行时的自主裁量——选型时的硬筛选项。[第 2 章 2.2.5、第 6 章 6.2.6]

**答 2.3**　(a) 拆解：`0x15` = class BPF_JMP(0x05) | code JEQ(0x10) | s=K(0x00)；regs 字节 `0x00` = src=0,dst=0；off=0x0002；imm=0。汇编语义 `if r0 == 0 goto +2`（偏移相对跳转指令的下一条、单位是 64 位指令条数）。把前三字节当小端 24 位数读即教程的 `0x020015`。它是高频模式因为**紧跟在 call 之后的 NULL 检查**：helper（如 map_lookup_elem）返回 NULL 则跳过后续解引用——verifier 铁律的落地形态。(b) PREVAIL 构建（C++23，GCC 13+/Clang 17+）后：`bin/prevail ebpf-samples/... test <func>` 输出 PASS；对非法程序加 `--failure-slice` 得到导致错误的最小指令切片（也可 `--asm` 替代 llvm-objdump 反汇编、`--termination` 看终止性）。[web/md/26.md；repos/vbpf/ebpf-verifier]

**答 2.4**　RFC 9669 §6：解释器代码可被**推测执行侧信道（Spectre 类）当作 gadget**，与机密数据同地址空间时尤甚，规范推荐只用 JIT；内核对应 `CONFIG_BPF_JIT_ALWAYS_ON`——既是 Spectre 缓解，也是某些无 JIT 架构的必选项（双重动机）。用户态嵌入：没有内核级 verifier 兜底，这个风险要自评——uBPF 的 Safe Execution Profile 把内核 verifier 的指针追踪思想压进解释器本身：寄存器来源追踪（provenance）、每个指针带 region 身份/边界/权限、歧义指针算术**直接拒绝**而非事后范围扫描恢复、类型化 helper 元数据（首版故意不开 JIT）。同类事实：JIT 自身还有 constant blinding 防 JIT spraying。[web/md/16.md §6；repos/iovisor/ubpf]

**答 3.1**　(a) 第一遍 CFG/DAG 检查（check_cfg）：≤BPF_MAXINSNS(4096) 条、**无后向边**（禁环）、**无不可达指令**、无越界/畸形跳转——DFS 确认程序是有向无环图。第二遍全路径指令模拟（do_check）：跳转栈穷举条件分支两侧（DFS）；寄存器类型系统（PTR_TO_PACKET+SCALAR→PTR_TO_PACKET，指针+指针非法）；栈槽生消（读未写过的槽=拒）；exit 时 R0 必须持有已初始化合法返回值。(b) 改写三件事：①map fd 伪指令 → 内核 map 指针（resolve_pseudo_ldimmq）；②context 访问改写（`__sk_buff` 抽象字段偏移 → 真实 sk_buff 偏移）；③helper 编号 → 真实函数地址；另可给 alu32 目标寄存器插入显式 zext 指令减轻 JIT 负担。[web/md/21.md、42.md；第 3 章 3.2.3/3.2.4/3.2.8]

**答 3.2**　`R8=inv(...)`：值未知的标量（inv=invalid/unknown scalar，但带着区间信息）；`umin_value=28, umax_value=1048`：无符号下/上界，即 verifier 证明 R8 ∈ [28,1048]；`var_off=(0x0; 0x7fc)`：tnum（tristate number）——第一个数是确定位掩码（全 0，即高位全确定为 0），第二个数是自由位掩码（低 10 位 0x7fc 中某些位不确定）。合起来：verifier 知道 R8 的取值范围与"哪些位自由"，但不知道精确值。这类区间/tnum 推理由 kernel/bpf/tnum.c 实现，是 packet 指针算术安全证明的基础。[第 3 章 3.2.5]

**答 3.3**　(a) 删掉边界检查后直接 `eth->h_proto` 解引用 → verifier 拒绝，典型报错 `invalid mem access 'inv'` / `R2 invalid mem access`，返回 EACCES。(b) 四步：①定位末行错误句（唯一判死刑的行）；②解码出错指令行 `PC: (十六进制 opcode) 反汇编`；③解码上方状态行（寄存器类型 + 栈槽如 `fp-232=map_value`）；④PC 映射回源码：`llvm-objdump -S -no-show-raw-insn prog.o`（编译带 -g）得源码/汇编交错列表对号入座；BTF line_info 还能让 verifier log 直接标 C 源行。(c) libbpf 应用经 `libbpf_set_print()` 注册回调（minimal.c 恒开 debug），`bpf_object__load` 失败自动打印 verifier log；裸 bpf(2) 路径则按 man page 建议：得到 EACCES 后用 log_level=1 重试取日志。[第 3 章 3.3；web/md/13.md]

**答 3.4**　(a) 三大拒绝：①`invalid mem access 'inv'`——解引用值未知标量/未验证指针（tracing 里直接解引用 ctx->rdi、网络里缺 data/data_end 或 map value 边界检查）；修复=tracing 先 `bpf_probe_read_kernel` 拷上栈、网络补边界检查（照抄 `eth + 1 > data_end` 范式）。②`math between pkt pointer and register with unbounded min value`——packet 指针加了无下界标量（可能为负/巨大，指针会移出包头之前）；修复=加数用显式无符号类型（如 `__u16`）、先与常量比较把界先验出来、警惕移位/加法回绕。③`infinite loop detected`/back-edge——5.3 前一切循环禁，5.3 后循环界无法静态证明也不行；修复=常量界循环、变界用 `bpf_loop`、或 tail call 展开范式。(b) 随机循环"概率上几乎必然终止"仍被拒，因为 verifier 要的是**确定性证明**——它模拟所有路径、要求有限步终止的性质成立，不是概率保证；这正是"kernel rejects all programs that it cannot prove safe"哲学。(c) 少数例外是**编译器优化骗过直觉**（如默认 native target 生成 switch jump table 造成不可达指令，需 `-fno-jump-tables`）——此时必须看 llvm-objdump 的指令流而不是 C 源码。[第 3 章 3.4.1/3.4.4；web/md/45.md、12.md]

**答 4.1**　五条优势：①全 CPU 共享一个环形缓冲（内存占用除以核数，免"逐核 perf_event_open 塞 fd"的启动仪式——这正是 perf array 第一痛点：fd 没塞进对应槽位前程序根本发不出事件）；②两套 API——`bpf_ringbuf_output` 一步提交，`reserve/submit/discard` 两段式先在 ring 里预留拿到指针、直接填充、再提交，**省掉一次拷贝**、填一半还能 discard；③不需要 ctx 参数（与程序类型解耦，perf 版必须传程序上下文）；④用户态性能更优（libbpf 共享 ring buffer manager，`ring_buffer__new/add` 可聚合多 map 到一个 epoll fd，poll/consume/epoll_fd 三种消费姿态）；⑤通知自适应（flags=0 adaptive：消费者忙就不再打扰，另有 NO_WAKEUP/FORCE_WAKEUP）。官方结论："Starting in Linux 5.8, this should be the preferred method"。[web/md/98.md、15.md；第 4 章 4.2.5]

**答 4.2**　三档：①**per-CPU（空间换锁）**——每核独立 value 写入互不相见天然无锁，高频计数首选；代价=读侧按核求和（bcc 自动展开）、内存×核数、**核数必须按 `/sys/devices/system/cpu/possible` 计**（VMware vcpu.hotadd 会让 get_nprocs_conf 虚报 128 直接建错 map）。②**原子原语（操作换锁）**——HASH 的 update 是整个 entry 的**原子替换**；ARRAY update 非原子，但 32/64 位计数器字段可用 `__sync_fetch_and_add()`（内核态直方图=ARRAY+log2 分桶+原子自增十行范式）。③**bpf_spin_lock（真互斥）**——保护"同一 entry 其余字段"的多步更新；约束极多：只能 HASH/ARRAY value 顶层、BTF 描述强制、4 字节对齐、一次一把、**持锁期间禁止任何调用**、所有路径显式 unlock、仅 root、tracing 与 socket filter 不可用、syscall 读写跳过锁字段、map-in-map inner 禁用。撕裂读：ARRAY 整体替换非原子（"replaces elements in a nonatomic fashion"），大 value 并发读者看到半新半旧；HASH 是原子替换所以没有。[web/md/13.md、15.md、29.md；第 4 章 4.2.3]

**答 4.3**　要点：BTF 定义（`struct { __uint(type, BPF_MAP_TYPE_ARRAY); __type(key, pid_t); __type(value, u64); __uint(max_entries, N); } cnt SEC(".maps");`）→ 内核侧 `bpf_map_lookup_elem`/`bpf_map_update_elem(&cnt,&pid,&one,BPF_ANY)`（注意 lookup 返回必须判 NULL）→ 用户态 skeleton `skel->maps.cnt` 拿 fd、循环 `bpf_map__fd` + `bpf_map_get_next_key/lookup_elem` 轮询排序打 top3；ringbuf 版：内核侧 `bpf_ringbuf_reserve(&rb, sizeof(*e), 0)` 判空 → 填 event → `bpf_ringbuf_submit(e, 0)`；用户侧 `ring_buffer__new(bpf_map__fd(skel->maps.rb), handle_event, NULL, NULL)` + `ring_buffer__poll(rb, 100)` 主循环（Ctrl-C 走 -EINTR 优雅退出）。标准写法位置：BTF map 定义与 reserve/submit 在 `bootstrap.bpf.c`，消费三件套在 `bootstrap.c`。[第 4 章 4.3；web/md/100.md]

**答 4.4**　(a) 四象限中的第②条：**key 找不到时不报错，next_key 返回第一个元素**（把"查找失败"静默当成"从头开始"）——迭代中删除元素后 get_next 拿到的 key 已不存在，于是每次都从头开始，轻则跳元素、重则死循环。正确姿势：起始 key=NULL 与 ENOENT 终止配对，删除时保存 next_key 再删；或直接用 BATCH 三连。(b) ip/tc 加载器**默认复用**同名 pinned map，libbpf 默认**新建**——"重启后计数器清零"不是 bug 是工具链语义差；复用 pinned map 的正规姿势=open 之后、load 之前 `bpf_map__reuse_fd(map, bpf_obj_get("/sys/fs/bpf/..."))`。(c) 检查单：升级前盘点 unpin 清单是否与新版 map 集对齐（新增/删除 map 会错位）；stats 工具按 map id 检测换代避免抱着旧 fd 看孤儿 map；重载前 unpin 不存在的 map 会失败需容错；显式清理责任在己——pin 出去的 map 不会自杀。[第 4 章 4.4 坑 1/12；basic04 README]

**答 5.1**　三绑定：①传入入口函数的 **context 类型**；②可用的 **helper 子集**；③**返回值语义**。三个回调：`get_func_proto`（该类型允许调哪些 helper——白名单 switch-case，注意 default 链还会委托 base 集）；`is_valid_access`（context 字段读写合法性）；`convert_ctx_access`（对公开 context 的访问改写成内核真实结构偏移）。"校验器人格"：网络类 prog type 的 ops 在 `net/core/filter.c`，tracing 类在 `kernel/trace/bpf_trace.c`；此外 libbpf 侧按 ELF section 名（`section_defs[]`，libbpf.c L10840 起）推断 prog_type/attach_type——你在 C 代码里从不写枚举值。[web/md/20.md、39.md；第 5 章 5.1]

**答 5.2**　六维：挂载机制——kprobe=int3 动态断点绕经 trampoline；fentry=BPF trampoline 把调用点改为直跳（x86 JIT 用 poke descriptor 做 live-patch 式打补丁）。BTF 依赖——kprobe 无；fentry **硬依赖**（按函数名解析 BTF_ID 拿签名）。参数读取——kprobe 拿裸 pt_regs，必须 `bpf_probe_read_kernel` 先拷上栈（直接解引用 ctx->rdi 撞 `R1 invalid mem access`）；fentry 参数即强类型 C 变量（`BPF_PROG` 宏按 BTF 签名展开）直接可读。返回值——kretprobe 单独挂出口读 RAX 同样要 probe_read；fexit 天然拿出口参数+返回值，fmod_ret 能改写。开销——断点陷阱+上下文保存较重 vs 近零开销直跳。稳定性——**两者挂载点都不是 ABI**（函数改名/内联/删除即断），但 fentry+CO-RE 让签名漂移在**加载期**以重定位失败暴露，而不是运行期读到错内存。[第 5 章 5.2.3；web/md/11.md、45.md]

**答 5.3**　XDP 版 context=`struct xdp_md`（只有 data/data_end 等元数据、无 skb），返回 `XDP_PASS` 等 action 枚举；socket 版 context=`struct __sk_buff`，返回**字节数**（0=丢弃、非 0=接受并截断，想全收 return skb->len）；fentry 版用 `BPF_PROG(name, struct sock *sk, struct sockaddr *uaddr)` 按内核签名强类型取参，返回 0。三绑定由 prog type（经 SEC 名推断）决定。`bpftool feature probe`（可加 `unprivileged`）列本机可用 prog/map/helper 全集；`bpftool prog` 列已加载程序（类型/名称/map ids）。[第 5 章 5.3；web/md/15.md]

**答 5.4**　(a) generic XDP 挂在 `net/core/dev.c` 的 SKB 层路径（4.12 起任意网卡可用），**发生在 skb 分配之后**——拿不到"省 sk_buff 分配"这个 driver XDP 的核心收益，性能显著低；生产抗 DDoS 先 `ethtool -i <dev>` 确认驱动在 native 支持清单（veth/tun/virtio_net/mlx5/i40e 等）。(b) bcc kernel-versions 矩阵 Program types 表止于 SYSCALL（5.15），NETFILTER 等 6.x 新类型不在表内但 `web/md/8.md`（docs.ebpf.io）L65 可证其存在。(c) 两个年代断层：①版本表停在 6.x 早期，新类型/新 map 查 docs.ebpf.io 或 UAPI 头；②bpf(2) man page 有意只覆盖基础集（KPROBE/SCHED_CLS 标 "To be documented"）——man 页查不到≠不存在。[第 5 章 5.4 坑 2/5；第 9 章 9.2.1]

**答 6.1**　①**白名单**：每个 prog type 经 `bpf_verifier_ops.get_func_proto` 的 switch-case 决定允许哪些 helper（不在表内即拒载 "unknown func"）；helper×map 兼容再由 `check_map_func_compatibility()` 把关。②**5 参数上限**：源于 R1-R5 只有 5 个传参寄存器（调用约定与内核 C 一致）——这正是 `bpf_trace_printk` 可变参数最多 3 个的原因（fmt 与 fmt_size 占掉 2 个名额）。③**零 FFI**：eBPF 指令集刻意采用与内核 C calling convention 兼容的寄存器约定，verifier 通过后 JIT 把 BPF_CALL 改写成对真实内核 C 函数的直连调用——"internally, eBPF programs call directly into the compiled helper functions without requiring any foreign-function interface"。"反向 syscall"：普通进程用 syscall 请内核替自己干活，eBPF 程序用 helper 在内核现场替观测/网络逻辑干活。[web/md/15.md；第 6 章 6.1/6.2]

**答 6.2**　三硬限制：①格式串必须是预定义常量（verifier 要求，运行时拼串直接拒载）；②只支持有限转换符（%d/%u/%x/%ld/%lld/%p/%s 等，无宽度/精度修饰，遇未知说明符返回 -EINVAL 且什么都不打）；③附加参数最多 3 个 u64。全局缺陷：写全局共享的 trace_pipe，多程序并发写互相踩，读端 `cat /sys/kernel/debug/tracing/trace_pipe` 是轮询模型，且首次调用往内核日志刷告警。替代排序：聚合统计→**map 直方图**（内核内聚合最省）；流式事件→**ringbuf**（5.8+，老内核 perf_event_output）；复杂格式化→`bpf_snprintf`（5.13+，格式串放只读 map、支持完整 data 数组）；多参数打印→`bpf_trace_vprintk`（5.16+）。[web/md/15.md；第 6 章 6.4 坑 1]

**答 6.3**　(a) 列探针：`bpftrace -l 'tracepoint:syscalls:sys_enter_*'`；open 打印：`bpftrace -e 'tracepoint:syscalls:sys_enter_open { printf("%s %s\n", comm, str(args->filename)); }'`；直方图：`bpftrace -e 'tracepoint:syscalls:sys_exit_read /pid == <PID>/ { @bytes = hist(args->retval); }'`（对照组 `kretprobe:vfs_read { @bytes = lhist(retval, 0, 2000, 200); }`）。(b) hello.py 全部约 16 行：BCC Python 前端 + 内核侧一句 bpf_trace_printk + `b.trace_print()`；ebpf.py 加 BPF_HASH 按 UID 计数、Python 侧 `b["map"][key]` 像 dict 读写——"前端胶水其实很薄"：BCC 在内存里跑 clang 用 Rewriter 把源码改写（printk 展开、内核指针解引用改写成 probe_read+offsetof、map 访问换成 bpf_pseudo_fd 占位）。(c) madvise 套路：`bpftrace -l | grep madvise` → `cat /sys/kernel/debug/tracing/events/syscalls/sys_enter_madvise/format` 看字段布局 → `grep MADV_DONTNEED /usr/include` 查常量值 4 → `bpftrace -e 'tracepoint:syscalls:sys_enter_madvise /args->behavior == 4/ { @[comm] = count(); }'`——"format 文件+头文件 grep"是零文档猜探针参数的标准解法。[第 11 章 11.3.1；web/md/58.md]

**答 6.4**　(a) 机制：改包 helper（`bpf_helper_changes_pkt_data()` 名单上的全部：store_bytes/pull_data/change_{proto,tail,head}/adjust_room/xdp_adjust_* 等）可能触发**包 realloc / 数据搬移**——旧 data/data_end 指针不再可信，verifier 先前的边界检查记忆全部作废；铁律=调完重新拉两个指针、重新做边界检查再解引用，否则拒载。隐藏触发器是非线性 skb（数据在 fragments），需 `bpf_skb_pull_data` 拉平（verifier 检测到写访问还会自动在序言插 pull 做 unclone）。(b) 错配实例：`bpf_get_cgroup_classid` 只在 TC **egress** 可用（ingress 不行）；XDP 的 redirect 不接受任何 flag 只能 egress；`bpf_msg_redirect_map` 只吃 SOCKMAP；`bpf_get_socket_uid` 对非 full socket 返回 overflowuid(65534) 而非错误码。(c) GPL 门控：会读内核内部结构的 helper（get_current_task/probe_read_kernel/get_stack/fib_lookup/override_return 等）几乎全标 gpl_only，编在 bpf_func_proto 里；程序 license 字符串不 GPL 兼容就调不了（报 "Cannot call GPL only function..."）——而 tracing 类程序天然依赖这批 helper，故商业闭源程序几乎只能做网络数据面（普通改包 helper 多数不限）。[web/md/15.md；第 6 章 6.4 坑 2/8/7]

### 第二部分　现代工程（第 7-8 章）

**答 7.1**　(a) open：读 ELF、建 bpf_object 内存对象、识别程序与 map——**尚未发生任何 bpf(2) 调用**，因此是"参数化窗口"（改 rodata/bss、改程序类型、设 open_opts）。load：逐 map `BPF_MAP_CREATE`、`BPF_BTF_LOAD` 灌 BTF、CO-RE 重定位 + map fd 指令重写、`BPF_PROG_LOAD` 交 verifier→JIT。attach：凭 SEC 名自动接线或显式 API，产物是 bpf_link；close/destroy 关 fd，未被 pin/无引用者的对象随引用计数归零回收。(b) `const volatile` 的值在 **load 时**进入验证——verifier 已知值可做死代码剪枝；load 后 rodata 冻结为只读（BPF 侧写它被 verifier 拒）。少 `const`：值在验证期未知（无法剪枝）、视图变 data；少 `volatile`：Clang 直接把常量折叠、变量整个优化删除。[web/md/100.md；第 7 章 7.2.2/7.2.6]

**答 7.2**　iproute2 裸加载：iproute2 内置小型 ELF loader 做翻译，目标机只需 ip/tc，跨内核可移植性差（map 需 pin 到 /sys/fs/bpf/tc/ 共享）。bcc：目标机上的 LLVM **每次运行重编译** C→BPF（需 clang + 全套内核头 + /virtual/include 虚拟头），偏移编译时定死、跨内核配置可能读错字段。libbpf+CO-RE：构建机一次编译，加载时重定位，目标机零编译器依赖（BTF 由发行版内核自带）。opensnoop 10000+ 行 vs 42 行的根源：bcc 每次启动要走完整编译管线（Clang/LLVM 链接进来，内存映射虚拟头、编译、加载），纯 C 版只是 open/load/attach 三个 syscall 族调用——这正是"理想 BPF 工具=200KB 自包含二进制"的动机。[第 7 章 7.2.5；web/md/101.md]

**答 7.3**　(a) 全局变量（my_pid）落 `.bss`/`.data`/`.rodata` 段，load 时 libbpf 用**内部 array map** 承载并 mmap 给用户态——"under the hood are still using BPF maps"。(b) `skel->bss->my_pid` 是对内核 mmap 区的普通内存写，零 syscall。(c) minimal_ns：容器/WSL2 的 pid namespace 内 PID 与宿主不同（改用宿主 PID 获取方式）；minimal_legacy：`#define BPF_NO_GLOBAL_DATA` 后用单元素 ARRAY map 模拟全局变量，兼容无全局变量的老内核；bootstrap_legacy：ringbuf 换 PERF_EVENT_ARRAY 兼容 <5.8（RINGBUF map 5.8 引入）。(d) `bpftool gen object` 做 BPF 静态链接（多 .tmp.o 合一 + 剥 DWARF 保 BTF）；`bpftool gen skeleton` 产出把 .o 字节数组整个嵌入、带强类型句柄（maps/progs/links/bss 视图）与 __open/__load/__attach/__destroy 函数族的 app.skel.h。[第 7 章 7.2.6/7.3；web/md/100.md]

**答 7.4**　(a) 三种残留：①老式 XDP/tc 挂载（程序由网卡/qdisc 本身持有，进程死了还在）；②pin 过的 map/link（bpffs 文件持有引用）；③`bpf_link__disconnect()` 显式留下的 link。排查序列：`bpftool prog list` → `bpftool link list` → `ls /sys/fs/bpf/`。(b) 4.x 对 KPROBE 程序强制 `attr->kern_version == LINUX_VERSION_CODE` 否则 EINVAL；不能用 uname 算：发行版 backport 会抬高 sublevel——Ubuntu 4.15.0-33 的 `KERNEL_VERSION(4,15,0)`=265984 ≠ 编译期 `LINUX_VERSION_CODE`=266002。libbpf 自动填对，手写加载器才会踩（Bolin 靠读 kernel/bpf/syscall.c 源码定位，man page 示例没写这行）。(c) log_buf 悖论：log 只在失败后才有内容，而 **buffer 太小本身会导致加载以 -ENOSPC 失败**（成功时也可能因日志过长失败）；libbpf 对策=失败后以递增 buffer 重试。[第 7 章 7.4 坑 8/1/3；web/md/101.md]

**答 8.1**　(a) 三种断裂（5.3→5.4 例）：字段被挪进新的子 struct（布局重组）；字段改名（seq→seque）；字段位置上/下移（offset 变化）。额外两类漂移源：内核 **.config**（CONFIG_* 增删字段/条件编译）与**架构**差异（ARCH_HAS_NON_OVERLAPPING_ADDRESS_SPACE 甚至决定 bcc 隐式访问映射到哪个 helper），还有发行版补丁。(b) 三要素：**BTF** 描述内核与程序双方的类型信息（目标机的"折叠户型图"）；**Clang** 基于 BTF 生成 CO-RE 重定位——访问 `tcphdr->seq` 时记录的是**字段名+类型+所属 struct** 而非硬编码 offset；**libbpf** 加载时把程序 BTF 与目标内核 BTF 匹配、解析类型、改写 offset。落点：ELF 的 `.BTF.ext` section 的 **core_relo 子区**（与 func_info/line_info 并列），vmlinux.h 全量类型带 `preserve_access_index` 让每次字段访问都生成重定位。[web/md/85.md、83.md；第 8 章 8.2.1/8.2.6]

**答 8.2**　五 pass：①字符串去重（字符串比较退化为 **name_off offset 比较**——dedup 第一个关键设计）；②非引用类型去重（INT/ENUM/STRUCT/UNION/FWD；struct 等价判定=DFS 遍历整个连通类型图+维护"假设映射"处理环与矛盾，candidate→canonical 必须单射）；③引用类型去重（PTR/CONST/TYPEDEF 等，等价性归结为被引用类型的 canonical id）；④类型压缩；⑤type id 修正。FWD→STRUCT 等价映射"一次更新、全局生效"，实现跨 CU 类型重建。消融：关掉类型合并/FWD 解析只做朴素去重只能到 12.71MB（9.5x），全量 dedup 后类型描述符 101.7MB→0.97MB（104x）、条数 3,148,394→22,898（137x）——**大头是类型重建/合并，不是去重**（DWARF 按 compilation unit 独立生成、链接后同一类型重复且完整度不一）。[web/md/84.md；第 8 章 8.2.3]

**答 8.3**　(a) 命令一行即 `gen_vmlinux_h.sh` 全文；预生成版可用是因为 CO-RE 在加载时按目标内核 BTF 重定位字段偏移——vmlinux.h 只提供类型名与字段名（语义），不固化布局。(b) 等价链式版本：`struct task_struct *p; u32 ppid; bpf_probe_read_kernel(&t, sizeof(t), &task->real_parent); bpf_probe_read_kernel(&ppid, sizeof(ppid), &t->tgid);`——BPF_PROBE_READ 族 offset 编译期写死（换内核布局可能读错），BPF_CORE_READ 一个宏完成"沿指针链逐跳安全读取+逐跳记录重定位"。(c) `bpf_core_field_exists` 展开 `__builtin_preserve_field_info(___bpf_field_ref(field), BPF_FIELD_EXISTS)`；类型级用 `__builtin_preserve_type_info(type, BPF_TYPE_ID_LOCAL=0 / BPF_TYPE_ID_TARGET=1 / BPF_TYPE_MATCHES=2)` 三值枚举。[repos/libbpf/libbpf/src/bpf_core_read.h L9/L30/L44/L166-187/L525；第 8 章 8.3.4]

**答 8.4**　(a) CO-RE 解决"结构体布局漂移"，**不解决**"目标内核根本没有这个字段/函数/挂载点"。正确姿势：`bpf_core_field_exists`/`bpf_core_type_exists`/`bpf_core_enum_value_exists` 存在性分支（编译期被 libbpf patch 成 0/1 常量）+ `const volatile` 只读变量让 verifier 死代码剪枝——"字段在就读，不在就置默认值"。(b) vmlinux.h 含全量内核类型定义，与系统内核头混用必然类型重定义冲突；三件套=vmlinux.h + libbpf 头（bpf_helpers.h/bpf_tracing.h/bpf_core_read.h）+ 应用自有头。(c) insn_off 双单位：kernel API 里 `bpf_func_info/line_info->insn_off` 单位是 **struct bpf_insn 条数**，ELF API 里是 **section 内字节偏移**——写 BTF 解析器/loader 必做换算；配套约束：func_info[0].insn_off 必须为 0 且严格递增、line_info 首条指向每个函数第一条指令。(d) 防幻觉纪律：对 `may_exist`、`___execute_bpf`、`bpftool gen min_core_btf` 这类在全部语料（含 libbpf 源码）零命中的名词——语义可类比（存在性探针），**名字勿写死**，按"待核实"处理。[第 8 章 8.4 坑 1-7；web/md/83.md]

### 第三部分　应用域（第 9-13 章）

**答 9.1**　(a) `XDP_PASS` 放行进协议栈；`XDP_DROP` 极速丢弃（页面直接回收，最便宜路径）；`XDP_TX` 从**同一接口**弹回（同 CPU 独占 TX queue 免锁）；`XDP_REDIRECT` 经 devmap/cpumap/xskmap 重定向到另一网卡/CPU/用户态；`XDP_ABORTED` 表示程序出错，**实际按丢包处理**。(b) 硬边界：XDP_TX 只能同口弹回；跨设备必须 REDIRECT，且目标驱动要实现 `ndo_xdp_xmit`（+flush）。(c) 2016 提案期只有 PASS/DROP/TX 三个 action；REDIRECT 2018 年才以 **map-based** 形态落地（作者称 "hopefully last XDP action code"）。[web/md/62.md、69/75.txt；第 9 章 9.2.2]

**答 9.2**　机制：helper 版逐包调 `xdp_do_redirect` 直接写 NIC tail pointer/doorbell（昂贵）；map 版把 **RX bulking 藏进 XDP core**——driver 逐包只是登记，攒到 NAPI poll 循环末尾统一 `xdp_do_flush_map`，批量（≤64）摊销 doorbell 写。红利：redirect 目标类型由 map 定义，新增类型（devmap→cpumap→xskmap）**零 driver 改动**。CPUMAP 用途：①隔离 driver XDP 层与协议栈（DDoS 时协议栈再慢也拖不垮 XDP 丢包）——raw XDP frame 直送远端 CPU、到那边才建 SKB；②修复 NIC 硬件 RSS 对 VXLAN/双层 VLAN 等封装协议的 CPU 分布失明。内部=MPSC 模型+per-CPU 快 enqueue（8 包一批）+bulk 入 ptr_ring+钉核 kthread。[web/pdf-txt/75.txt；第 9 章 9.2.4]

**答 9.3**　实验成功标志：`ip link sh veth1` 出现 xdp flag 与 prog/xdp id ... jited；tcpdump 在 veth1 只抓到 IPv6（10 IPv4 全被丢），trace_pipe 可见逐包 ethertype 日志。fail-open 设计：解析不了的包（如过短、非以太类型）返回 XDP_PASS 交给协议栈兜底——**宁可慢不可错杀**，XDP 层只对"明确判定为非 IPv6"的包下 DROP 判决。注意：section 名用 iproute2 加载时 XDP 约定可省略（`ip link set dev veth1 xdp obj x.o`），libbpf 路线则用 `SEC("xdp")`；调试宏 bpf_debug 走 trace_pipe，生产环境必须移除（每包一次 printk 是快路径实打实的开销）。[web/md/62.md；第 9 章 9.3.1/9.3.2]

**答 9.4**　(a) 三语境：**24 Mpps/CPU drop**（CoNEXT'18 论文，Xeon E5-1650v4 + ConnectX-5 100G + net-next-xdp e641995a 内核）；**10.1 Mpps XDP_DROP**（Cloudflare 2018-07，内核 4.14 + KPTI/retpoline，同一阶梯上 iptables raw 1.688M/nftables netdev 1.53M/tc u32 1.8M）；**9.7 Mpps blacklist drop**（Jesper，i7-6700K + ConnectX-4 50G，iptables raw 对照 4.5-4.7M）。两个毁基准失误：①残留的 raw socket（忘了杀的 tcpdump）——先 `ss -A raw,packet_raw -l -p` 检查；②不关 Turbo Boost（标准差 ±1.5% vs 关后 0.25%）。(b) 代价：启用 XDP 即改变 RX ring 内存模型——每包恒 alloc 4K 页（单帧模型），理论上拖慢正常入栈路径（page allocator 瓶颈）并影响 skb->truesize 与 TCP 吞吐；page_pool 项目即为此而生。真转发（跨设备 redirect）页要等远端 TX 完成才归还，无法完全避开与 MM 层交互。(c) 勘误：39 Gbps（58 倍）出自 **NFQ（Netfilter 队列）mark 通道的 bypass**，不是 XDP 本身的成绩——Suricata 的 XDP 版 bypass 是后来的 SEPTun Mark II 线（SKB 构建前直通），引用必须区分通道。[web/md/78.md、190.md；第 9 章 9.2.7/9.4]

**答 10.1**　UMEM=用户态分配的虚拟连续内存切成等大 chunk（2K/4K），是内核与用户态共用的"保税堆场"——数据不搬，只传提单（描述符）。四环：FILL（用户态→内核，载荷=UMEM addr，"这些空缓冲区交给你收包用"）；COMPLETION（内核→用户态，"用完了收回"，含被拒非法 TX 描述符）；RX（内核→用户态，xdp_desc{addr,len}）；TX（用户态→内核，需 sendmsg 触发）。因果搞反的原因：开发者直觉盯着 RX 环收数据，但**FILL 环没交缓冲区上去，RX 环就不可能有描述符出现**——收包上游是 FILL。红线①completion 只归还所有权不保证发送成功（错误只体现在统计里）；红线②同一缓冲区绝不能同时出现在两个环（NIC 可能一边 DMA 写入一边在发送它——静默数据损坏）。[web/md/79.md；第 10 章 10.2.1]

**答 10.2**　XDP_SKB（generic）：驱动不支持或显式选择，SKB+copy，1 次拷贝，任意网卡；XDP_DRV：驱动原生 XDP 点处理+一次到用户态 copy，需驱动支持；zero-copy：bind flag `XDP_ZEROCOPY` 且驱动支持，NIC DMA 直写 UMEM，0 拷贝。默认：bind 先试 zero-copy 失败回退 copy；`XDP_COPY/ZEROCOPY` flag 可强制（不支持则 bind 失败报错）。必须查询：回退是静默的，生产代码用 `XDP_OPTIONS` getsockopt 的 `XDP_OPTIONS_ZEROCOPY` 位确认实际模式——不要假设。SHARED_UMEM 两形态：①同 netdev+queue 多 socket（XDP 程序查 XSKMAP 做 RR 分发）——**全组只有一对 FILL/COMPLETION**；②跨 queue/netdev——每个 unique (netdev, queue_id) 元组**自建一对** FILL/COMPLETION 环，不需要专门分发 XDP 程序（靠 NIC RSS/ntuple 导流到对应 queue）。[web/md/79.md；第 10 章 10.2.3/10.2.4]

**答 10.3**　(a) 机制：用户态把 XSK 插进 XSKMAP，XDP 程序 `bpf_redirect_map(&xsks_map, index, 0)` 分发；内核重定向时**校验该 XSK 确实绑定在当前 netdev+queue 上**，不匹配或槽位为空则丢包——所以"必须加载 XDP 程序且 XSKMAP 至少放一个 socket"是收流量的硬前提（bind 完成前流量也不流动）。(b) 三步：`ethtool -N <dev> rx-flow-hash udp4 fn` + `ethtool -N <dev> flow-type udp4 src-port 4242 dst-port 4242 action 16`（ntuple 把目标流量导到 queue 16）→ `samples/bpf/xdpsock -i <dev> -q 16 -r -N`（-N=XDP_DRV 驱动原生，-S=XDP_SKB）。`ethtool -L combined 1` 适用"想收全部流量/测试场景"（把多队列收成单队列）；ntuple 适用"只关心特定流"（不扰动其他队列）。(c) invalid descs 非零说明**应用在产非法描述符**——是 bug 不是负载问题（ring 满是另一回事）。[web/md/79.md；第 10 章 10.2.2/10.3]

**答 10.4**　(a) 机制：物理 NIC 初始化时通常**每核一对 RX/TX 队列**（8 核机器 queue 0-7），RSS 按哈希散流，流量大概率落在没绑的队列上。两解：`ethtool -L <iface> combined 1` 收成单队列；或 `ethtool -N` ntuple 规则导流。缓冲区双环=数据竞争：NIC 可能一边收包 DMA 写入该 chunk、一边在发送它——**静默出错、难复现**（官方 FAQ "My packets are sometimes corrupted"）。(b) 决策树第一问：**逻辑真的必须回用户态吗？**——解析/查表/改写/转发能 Verifier 化就全内核 XDP（upf-bpf 型：GTP/UDP parse→PDR 检测→FAR 转发全在 XDP tail call 管线，grep 无任何 AF_XDP 引用）；必须回用户态再谈 AF_XDP/f-stack/passt。(c) 大忌原因：三个倍数的**分母各不相同**——40x/20x 是 2018 RFC 期 Intel 微基准对照旧 AF_PACKET；25× 是 f-stack 厂商 README 口径对照调优内核；4-50× 是 passt 对照 slirp 系（且随 MTU 变化）。跨路线直接比倍数=比不同的分母。[web/md/79.md；第 10 章 10.4/10.2.7]

**答 11.1**　(a) 对比：kprobe——内核动态、任意函数、**不稳定**（函数可增删改名；kretprobe 拿 retval）、上下文是裸 pt_regs 需按 ABI 手工映射参数；tracepoint——内核静态（TRACE_EVENT 手埋）、**稳定**且开发者标注了丰富上下文（强类型 `args->xxx`）；uprobe/uretprobe——用户态动态、随二进制符号走（strip 后需 debuginfo）、拿函数入参/返回值；USDT——用户态静态（DTRACE_PROBE 宏）、稳定、**与 DTrace 宏源码级兼容**（老应用零改动可用）；fentry/fexit——"内核静态化动态"，仍挂任意函数但依赖内核 BTF 函数签名做 trampoline 挂载，类型化参数直读、开销近似函数调用、fexit 出口统一触发（不必再挂 kretprobe）。(b) 铁律原因：kprobe 挂的是内部 API，"事件可随版本任意变化"，预写 kprobe 的工具要按内核版本维护挂点清单（biolatency.py 挂 blk_start_request/blk_mq_start_request 双备胎即自认应重写为 tracepoint）；硬失效：内核内层函数大量 **inline/static**，根本不存在可探测符号——容器网络追踪一文第一版 kprobe 失败后收敛到 4 个 tracepoint 是标准复盘。[web/md/58.md、47.md；第 11 章 11.2.1]

**答 11.2**　三个关键点：①键用 **tid 而非 pid**——同进程多线程并发进出同一函数，用 pid 会互相覆盖时间戳；②出口探针带 `/@start[tid]/` 过滤——探针在程序中途才挂上时（半程捕获），map 里没有该 tid 的入口时间，`nsecs - @start[tid]` 算出 `nsecs - 0` 的**天文数字假值**；③算完 `delete(@start[tid])`——防 map 无限增长泄漏。这套"enter/exit 双程序 + map 传参 + 缓冲区出口"就是 L7 协议观测的通用骨架（eBPFChirp 的 Redis 方案把它搬到 syscall tracepoint 上）。[web/md/58.md；第 11 章 11.2.4]

**答 11.3**　(b) 机制：MiTM 要管证书+解密再加密昂贵；应用内埋点要改代码重启；uprobe 方案**站在加密前/解密后的位置**——`uprobe/SSL_write` 拿客户端加密前的出站明文、`uprobe+uretprobe/SSL_read` 拿服务端解密后明文及返回码（HTTP 200 在这里），不解密所以不需要证书。kyanos 的 bpf/ 目录：openssl_1_0_2a / 1_1_0a / 1_1_1{a,b,d,j} / 3_0_0 / 3_1_0 / 3_2_0 / 3_2_3 / 3_3_0 / 3_4_0 / 3_5_0 共十余个逐版本独立 .bpf.c，另加 Go TLS 的 gotls.bpf.c 与 3.10 legacy 变体——工程化天花板=**库×版本矩阵管理**（换 BoringSSL/GnuTLS 要换挂点，OpenSSL 各版本参数与内部结构不同）。(c) 实测：额外延迟约 **~0.2µs/请求**（1000 请求均值），CPU 占用 SSL_write 0.1%、SSL_read 0.007%、uretprobe/SSL_read 0.3%。限制：只对同节点加解密流量有效，不能部署在网络边缘。[web/md/114.md；repos/hengyoush/kyanos/bpf/]

**答 11.4**　(a) 公式：poller CPU/s ≈ 刷新成本 × 刷新频率；probe CPU/s ≈ handler 成本 × **每秒上下文切换数**（+刷新成本）。rstat 实测：常规 12,454 switches/s 时 handler 只花 8ms/s；人为切换风暴 240 万/s 时**吃掉 1.8 个 CPU 核**——probe 的计费与事件频率成正比，而机器越忙切换越多，"监控最该便宜的时候收费最贵"。(b) 纪律：**能用库边界 uprobe（每请求 ~0.2µs、CPU≤0.3%）就别挂高频 syscall tracepoint 全家桶**（Redis 方案平均 ~17µs，sys_exit_read hook CPU 高达 11.69%）——挂点的事件频率与 handler 复杂度共同决定开销，解码重逻辑放 read 退出路径在生产高频场景要慎重。(c) 完整表述："低开销"永远是**特定挂点 × 特定事件频率的函数**，不是 eBPF 的固有属性；结论钉版：eBPF 仍是内核计数器回答不了的问题（per-task 延迟归因）的正确工具，但常驻仪表盘应优先 poller 模型（/proc+PSI），probe 只在调查期运行。[repos/overyonder/rstat/README.md；web/md/114.md、115.md；第 11 章 11.4 ③④]

**答 12.1**　(a) 第一代（Falco/Sysmon）：事件先**穿越内核边界**，规则引擎在用户态判定——只能事后告警；第二代（Tracee/Tetragon）：过滤与判定**下沉内核**，detect→enforce（Tetragon 的 KPROBE_ACTION_SIGKILL=3/OVERRIDE=5 命中即在内核杀进程/改返回值）；第三代（BPF LSM）：挂 LSM 钩子在**动作发生前的不可回头点**，返回 -EPERM 否决——事情根本不发生。(b) fileless 案例：正确挂点是 binfmt 匹配后、进程执行 point of no return 前——此时 ELF header 已可访问且**不可伪造**（控制权尚未移交）、mm_struct 还挂在 linux_binprm 上；传统工具（SysmonForLinux/Tracee/Falco）只能在这个位置"检测" `memfd:` 前缀（且 /proc/pid/comm 可被 prctl 改、exe 可被 PR_SET_MM_EXE_FILE 指向别处、maps 有 TOCTOU），BPF LSM 能"阻断"——观察点 vs 决策点的分野。[web/md/255.md；第 12 章 12.2.4/12.2.5]

**答 12.2**　六程序：bpfdos——`bpf_send_signal` 对调 ptrace 的 strace 直接 SIGKILL（反调试 DoS）；exechijack——篡改 execve 参数改跑 /a，恶意程序再补跑原程序避免察觉；pidhide——hook getdents64 把 PID 从 /proc 列表 unlink（ps 失明）；sudoadd——**只对 sudo 进程的读取**覆写 /etc/sudoers 首行为 `NOPASSWD:ALL #`；writeblocker——对 fd>2 假装写入成功（rsyslogd 静默丢 auth.log）；textreplace——read 路径文本替换（藏 lsmod 模块/伪造 MAC 反沙箱）。sudoadd 精准性：篡改发生在内核向 sudo 进程回传文件内容的路径上，cat/sudoedit 读到的是真实文件——凭据校验被绕过而磁盘证据干净。textreplace2 启示：配置进 eBPF map（运行时可改目标）+ `--detach` 后经 **bpffs pin 持驻内核**（rm -r /sys/fs/bpf/textreplace 才能卸载）——防御者自己的 LSM 程序同样要 pin 且限制 bpf() syscall，防被先卸载。[repos/pathtofile/bad-bpf/README.md；第 12 章 12.2.3]

**答 12.3**　(a) 判据：memfd_create 建的是 RAM 驻留匿名文件，**没有磁盘目录项，inode 链接数（__i_nlink）为 0**——正常文件至少 1。挂点论证：`bprm_creds_from_file` 处于 binfmt 匹配后、执行 point of no return 前——ELF header 已可访问且不可伪造，mm_struct 尚挂在 linux_binprm 上，是唯一既能看到真相又能否决的窗口；返回 -EPERM 即阻断。(b) 三前置：kernel 5.13+、`CONFIG_BPF_LSM=y`、启动参数 `CONFIG_LSM="...,bpf"`（lsm.s sleepable 变体配可睡眠上下文如 bprm_*）。docker 复现三行日志证据链：execsnoop 看到 syscall_execve → `lsm_bprm_creds_from_file filename=memfd:... retval=-1 reason=denied` → execve 返回 operation not permitted。(c) bpf.yaml：kprobe 挂 `bpf_check` 与 `security_bpf_map_alloc`（<6.9）/`security_bpf_map_create`（6.9+）——`ignore: callNotFound: true` 处理两代内核间**探测符号的版本漂移**（挂点不是 ABI 的工程对策）；把 selector 的 action 换成 `Sigkill`（KPROBE_ACTION_SIGKILL=3）即从观察转强制。[repos/linux-lock/bpflock/bpf/filelesslock.bpf.c；repos/cilium/tetragon/examples/policylibrary/bpf.yaml；第 12 章 12.3]

**答 12.4**　(a) UAPI 原文：因 **TOC-TOU** 竞态"禁止用于实现任何安全机制"，只用于半协作进程调试（attach 时内核日志还打警告）；TripleCross 注释的三条不可靠：①随机返回 EFAULT(-14)、某些路径必败；②filename 与 argv[0] 指针相距恰好 196 字节时单次写同时污染两者；③从 bash 终端发起的 execve 常改写失败——攻击工具自己承认原语不可靠。(b) 误杀代价：Sigkill/Override 是**内核态杀生产进程/改返回值**，策略写错的代价是生产事故而非漏报；bpflock 纪律：restricted 档会拒绝所有进程（含特权容器）、baseline 依赖 host namespace 判定——先 allow 档全量日志观察，再逐条收紧。(c) 绕过面：攻击者拿到 root 后可先**卸载/覆盖防御探针**再作案；对冲：自己的 LSM 程序 pin 住（防卸载）+ 限制 bpf() syscall 本身——bpflock 的 bpfrestrict 挂 `lsm/bpf` 正是与 filelesslock 并列的存在理由；配套 Bombini KernelMon 把"BPF 程序与 map 活动"做成常规监控事件（BPF 自身的可观测性），对冲 ebpfkit 式"对 bpf syscall 隐藏自身"的混淆。[web/md/39.md；repos/h3xduck/TripleCross；第 12 章 12.4]

**答 13.1**　(a) sched_ext 是一个新的 sched_class（调度类）但不实现具体策略，通过 **struct_ops 机制**把一组回调导出给 BPF 程序：`struct sched_ext_ops` 概念上等价于 `sched_class` 的 BPF 镜像，内核 sched_ext 层把复杂回调翻译成更人体工学的版本；BPF 侧用 `SCX_OPS_DEFINE(...)` 注册（编译成 struct_ops map + 程序组）。(b) 自由度：struct_ops **没有任何 ABI 要求**（与要导出 UAPI 的程序类型不同），sched_ext API 因此可以快速演进（破坏性变更记录在 BREAKING_CHANGES.md）；代价=out-of-tree 调度器维护成本≈背 out-of-tree 内核 patch。(c) 唯一必须实现 `name`；不实现 `.select_cpu()` 时内核自动在唤醒路径挑 idle CPU（其余回调也全有合理缺省）。verifier 加载时强制 GPL2。[repos/sched-ext/scx/OVERVIEW.md；第 13 章 13.2.1]

**答 13.2**　(a) 约定：任务被 "insert" 进某个 DSQ；非 local DSQ 里的任务被 "move" 到目标 CPU 的 local DSQ；**CPU 永远只从自己的 local DSQ 取任务执行**——这是 BPF 决策与内核执行之间清晰的产权边界。(b) 是：只用内置 DSQ（全局 FIFO `SCX_DSQ_GLOBAL` + 每 CPU local）时，enqueue 直接插全局/local、收尾链自动从全局 DSQ 兜底取任务——根本不用实现 `ops.dispatch()`（它只在 local 与全局都空时触发），scx_simple 几十行全局 vtime 即此。(c) 不支持：**内置 DSQ 只有 FIFO 语义**；优先级（vtime）要用 `scx_bpf_dsq_insert_vtime()` 插自定义 DSQ（且自定义 DSQ 可用 `scx_bpf_create_dsq()` 建任意多个）。[repos/sched-ext/scx/OVERVIEW.md；第 13 章 13.2.2/13.2.3]

**答 13.3**　(a) 会话：初始 `cat /sys/kernel/sched_ext/state` = disabled；跑 `scx_simple` 后 state 变 enabled、`/sys/kernel/sched_ext/*/ops` 显示 simple；Ctrl-C 退出打印 `EXIT: BPF scheduler unregistered`、state 回 disabled（内核默认 fair 调度器=6.12 时代的 EEVDF 接管）。内核态真相以 /sys/kernel/sched_ext 为准。(b) 选型：游戏延迟→**scx_lavd**（LAVD 延迟临界度感知虚拟 deadline，为游戏/交互而生）；K8s-GPU 集群→**Gthulhu**（K8s 分配→sched_ext 执行面桥接，TID 级策略点名 LLM engine/decode 与 NCCL/RDMA 线程）；生产分层→**scx_layered**（Meta 生产主力）。判断依据=各 README 的 **"Production Ready?"** 直答字段（eevdf=实验对照台、beerland/pandemonium/forge/cake=实验性、horoscope=教育娱乐）。(c) `scx_bpfland --monitor 0.5`：用户态统计显式要（scx_stats 改版后默认不打印）；scxtop=top 式 perf+sched_ext 事件聚合。[repos/sched-ext/scx/；第 13 章 13.3]

**答 13.4**　(a) 三层：verifier 加载时静态证明（+GPL2 强制）；内核运行时校验每个回调返回值（非法 CPU 号/非法 flags→报错卸载）；watchdog 检测"任务 runnable 太久没被调度"强制 error-out。净效果（官方原话）：**忽略内核 bug，调度器最坏只能饿线程直到 watchdog 触发**——任务被迁回可信的内核默认调度器，不存在 panic 路径；三种退出：Ctrl-C / sysrq-S / watchdog 超时。(b) 两个原因：EDQ 使用了 6.13 内核 **verifier 不支持的 atomic release stores**，且 CPU 选择路径**超出 verifier 复杂度上限**——"同一框架、不同内核代际能力不同"的标本（bpfland 要 6.16+）。(c) 含义：无 ABI 稳定承诺 → 破坏性变更随 BREAKING_CHANGES.md 进来，out-of-tree 调度器每个内核代际都可能要改代码重编（维护成本≈out-of-tree patch）；现实回避路径=发行版打包（Arch scx-scheds）或跟主线 CI 矩阵（virtme-ng）。(d) 挂起陷阱：scx_simple 调度全在 BPF 侧，Ctrl-Z 只是停了统计打印；但 layered/rusty/Gthulhu 用户态模式里**用户态进程是策略面**（负载均衡/层管理）——SIGSTOP=策略面失速，README 明确 "This doesn't hold for all schedulers"。[repos/sched-ext/scx/；第 13 章 13.2.4/13.4]

### 第四部分　生态与边界（第 14-16 章）

**答 14.1**　三契约：①**verifier 能力集与 NIC 能力集一致**——verifier 需按 offload 设备能力**收紧检查**、驱动侧二次校验（nfp/bpf/jit.c + kernel/bpf/offload.c）；实例：NFP 硬件 JIT 对硬件 map、原子操作、**尾调用只提供受限支持**；Suricata `xdp-mode: hw` 必须关 BUILD_CPUMAP 与 USE_PERCPU_HASH 才能工作。②**map 跨两个内存域一致**——map 在设备独立内存域，内核/固件各维护一份架构保持同步；实例：bpf-samples 的 l4lb 只用一张普通 HASH、map 装载后由脚本重填。③**原子性与并发语义**——同一段单线程字节码被固件透明时分复用到多个微引擎线程，内核按单核语义验证的原子性要由硬件 map+受限原子指令重新兑现。必要性非充分性："能在内核加载"≠"能在设备上跑"——按**最小公共能力集**写程序（普通 HASH/ARRAY、无 tail call、无 percpu、简单 fetch-add）。结构性优势：XDP 位于协议栈最底部、上下文就是裸包 xdp_md，不依赖 sk_buff 等复杂内核结构——最不复杂、可卸载性最好。[digests/11；web/md/92.md、web/md/93.md；第 14 章 14.2.1]

**答 14.2**　四层组件：验证器=**PREVAIL**（独立用户态验证器，PASS/FAIL）；执行引擎=**uBPF**（移植进 Windows 内核执行上下文，另有 bpf2c 把字节码逐条翻译成等价 C 语句再编成签名 .sys）；API 兼容层=**ebpfapi.dll**（暴露 Libbpf API，bpftool/Netsh 都走它——Linux 加载代码源码级复用）；hook 提供者=**netebpfext** 等扩展驱动（XDP/bind/connect 等 hook 映射到 Windows 网络栈）。HVCI 筛选：JIT 编出的原生码**没有 hypervisor 信任的签名密钥**→HVCI 开启时不可用；解释器仅 debug build（RFC 9669 判其为侧信道 gadget 源）；生产只剩 bpf2c native（字节码→C→标准 .sys 走 Windows 签名体系）。一般启示：**宿主平台的信任模型反过来决定执行引擎选型**——任何带强制代码完整性的宿主（签名链/加载限制）都会筛掉部分执行模式，选型先问宿主信任链。[repos/microsoft/ebpf-for-windows/README.md；第 14 章 14.2.5]

**答 14.3**　(a) 构建 PREVAIL（C++23，GCC 13+/Clang 17+）；`bin/prevail ebpf-samples/src/exposeptr.o <section> <func>` 对正常样例输出 PASS；对 invalid/ 反面教材输出 FAIL，`--failure-slice` 给出致错最小指令切片（11 个 invalid 程序+25 个 .asm 手写用例是验证器研究的标准回归集）。(b) uBPF 四步：`ubpf_create()` 建 VM → `ubpf_register(vm, id, name, fn)` 注 helper → `ubpf_load(vm, code, len, &err)`（或 JIT 编译）→ `ubpf_exec(vm, mem, mem_len, &ret)`；Rust 侧 rbpf：建 VM 传字节码 → `register_helper` → `prog_compile()`（可选 JIT）→ `execute_program()`。(c) 差异：uBPF 解释器启动 `reg[1]=mem` 且**额外 `reg[2]=mem_len`**（内核只承诺 r1=ctx）；配 PREVAIL 验证过的程序喂 uBPF 前先读 `repos/iovisor/ubpf/docs/VerifiedPrograms.md` 的 context 指针约定——"ISA 相同"不等于"运行时契约相同"。[第 14 章 14.3；第 2 章 2.2.10]

**答 14.4**　(a) 教训：①**厂商绑定的生态会随厂商死，进主线的框架不会**——Netronome 被 Corigine 收购后 NFP 硬件线停更、bpf-samples 2018-11 停更，但 nfp 驱动与 kernel/bpf/offload.c 通用卸载框架仍在主线（后来者可复用的公共品）；②2017 年 SmartNIC 预测只部分兑现——"跑通用 eBPF 字节码的 NIC"没有成为品类，可编程网卡终局是 P4/PNA 系与固定功能 DPU。活跃度判定：硬件线死/offload 框架活（随主线演进）。(b) 15ms 地板主凶=**全量 cache flush/invalidate**：A-53 没有 DDIO/cache stashing，DMA 一致性只能刷整片 cache，**代价正比 cache 大小而非数据量**；selective cache flushing（host 声明需失效的字节数）后延迟才正比数据量——结论："卸载到弱核嵌入式平台先算一致性成本；offload 性能瓶颈通常在搬运与一致性，不在执行"；传输选型：程序走 BAR（<1KB 快）、数据走 DMA（>10KB 快）。(c) 空窗：TP4091 数据按摩场景需要 **backward jump**（循环密集），而 Linux verifier 的终止性模型为"程序 5μs 内跑完"设计、禁无界循环——终止分析在设备端既难又重要（否则设备可被死循环锁死），Delilah 诚实把验证留作 future work；引用限定：目前只适合**可信 host 卸载给自己的程序**，安全验证未闭合。[web/pdf-txt/96.txt；第 14 章 14.2.2/14.2.4]

**答 15.1**　(a) 三代：一次性命令（2014-2018，ip/tc/iproute2 加载+BCC 目标机现场编译——每台目标机都是编译机）；守护进程化（2019 前后，两个同名 bpfd：**genuinetools/bpfd**——Go 规则框架 Tracers→Rules→Actions，2019-05 死；**joelagnel/bpfd（BPFd）**——Android stdio 协议远程加载、编译/运行分区思想，2019-06 弃用；这代证明了需求但死于 BCC 路线的部署重量）；OCI 分发（2022-，**bpfman**=原名 bpfd 的直系继任者，CNCF Sandbox，2026-11 仍极活跃）。(b) bpfman 三大能力：①System Overview（系统内 eBPF 使用洞察）；②程序加载器——内置 XDP/TC **dispatcher 多程序链式挂载** + 从 OCI 镜像分发字节码；③eBPF 文件系统管理。"无需额外特权部署"靠 **bpfman-ns**（命名空间特权收敛）+ CSI 驱动（K8s 场景）。规律：加载器层创新向 bpfman 收敛，死掉的是中间形态。[第 15 章 15.2.2；repos/bpfman/bpfman/docs/quick-start.md]

**答 15.2**　第一性判断：**宿主语言决定候选集**（Go agent → cilium/ebpf vs libbpfgo；Rust → aya）。追新内核特性 → **libbpfgo**（CGO 直包 C 库 libbpf，上游新特性零延迟，代价=交叉编译痛+绑定 libc）；要单二进制分发 → **cilium/ebpf**（纯 Go 零 CGO、静态单二进制跨平台最顺，代价=syscall 层自己跟、新特性有延迟）。bpf2go 三步：①C 程序放 bpf/ 目录；②加 `//go:generate go run github.com/cilium/ebpf/cmd/bpf2go -type MyEvent myprog ./bpf/xxx.bpf.c -- -I...`；③`go generate` 自动产出 `myprog_bpfel.o` + Go 加载骨架，`go:embed` 嵌进单二进制。运行时三件套 `NewCollectionFromFile` → `link.NewKprobe(...)` → `ringbuf.NewReader(...)`；可移植 agent 关键=`features.HaveProgramType(...)` 先探能力再降级。[第 15 章 15.2.3；repos/cilium/ebpf/examples/]

**答 15.3**　(a) libbpf-tools 是官方 CO-RE 迁移版（124 个 .c，三件套 xxx.bpf.c/xxx.c/xxx.h）：**目标机免 LLVM 免内核头**（编译一次到处加载），tools/*.py 是旧 BCC 动态编译版仅作参考实现库——新项目误用会把 LLVM 装上每台目标机。读输出：biolatency_example.txt 给了分布解读样例（`usecs` 列+count+distribution，按盘分列 -D）。(b) ebpf-kill-example：`make deps`（编 libbpf+bpftool）→ `make`（73 行 kern.c=sys_enter_kill tracepoint+BTF hash map，92 行 user.c=open/load/attach/读 map）→ `make test` 跑 `test/test.sh`：起一个循环进程→`kill -9` 它→验证 tracepoint 程序触发、map 里有记录，输出 `[ OK ]`——"结构即模板"（生成其他 tracepoint 样例的最佳底版）。(c) BPF_PROG_RUN（旧名 BPF_PROG_TEST_RUN）：`data_in/data_size_in` 喂 mock 数据（XDP 场景=手工构造的 IPv4 包，不发包不占网卡）；`repeat` 重复执行次数——顺带就是性能测量（单测与压测同一套 API，支持 15 种程序类型，libbpf 封装 `bpf_prog_test_run_opts`）。[第 15 章 15.2.5/15.3；web/md/118.md]

**答 15.4**　(a) 四层：selftests/bpf=内核树功能百科（每个 progs/*.c 演示一种 verifier 特性/helper 用法）；BPF_PROG_RUN 单测=不经真实事件源从用户态注入上下文执行并取回结果（保正确，底座）；**bpfcompat 真内核矩阵**=对 30+ 内核（Ubuntu 4.15→6.17 全代+RHEL 系）各 boot 一个真发行版 VM 把 .bpf.o 连同 validator 送进去跑真 `bpf()` load/attach（保可加载，中段——CO-RE 只保"原则上可移植"，它给经验答案）；Bencher 持续基准=每 PR 跑基准挂 thresholds 门禁（保不劣化，塔尖——eBPF 改一行寄存器分配就可能掉 20% 吞吐而功能测试全绿）。(b) 虚假安全感四类真失败源：**BTF 缺失、CO-RE 重定位对不上分叉内核、map/attach 类型不支持、内核配置差异**；quirk-library 记录"版本号≠特性支持"的坑内核（ringbuf 5.8 边界、无 BTF 内核、厂商 backport——正是"6.1 内核未必有 6.1 特性"的坑百科）。(c) 四板斧：加载失败先拿 verifier log（`libbpf_print_fn` 回调 / bpftool prog load 手动重放剥离加载器因素）；行为不对按序——①`cat /sys/kernel/debug/tracing/trace_pipe`（看 bpf_printk）→ ②`bpftool prog dump xlated/jited id <ID>`（看翻译后指令/JIT 本机码）→ ③`llvm-objdump -S -g xxx.bpf.o`（指令对回 C 源）→ ④`bpftool map show/dump`（查 map 内容，BTF 化 map 直接显示结构体字段）。[第 15 章 15.2.5-15.2.7；repos/Kernel-Guard/bpfcompat/]

**答 16.1**　(a) 六层：L0 内核与规范（linux 内核 BPF 子系统 bpf-next/net-next、RFC 9669）；L1 基础设施（libbpf/cilium-ebpf/libbpfgo/aya/zbpf/BCC/eunomia）；L2 加载器管理器（bpfman/L3AF/Inspektor Gadget）；L3 数据面（Cilium/Calico/Katran/LoxiLB/Suricata/upf-bpf）；L4 可观测（Pixie/DeepFlow/Hubble/parca/Coroot/kyanos）；L5 安全（Falco/Tetragon/Tracee/Sysmon+攻击线 ebpfkit/Bad BPF/TripleCross）；L6 调度（scx/Gthulhu）+2026 新支线（AgentSight/ActPlane/Inner Warden）。(b) Emerging 门槛：开源许可+eBPF 为核心技术（去掉 eBPF 项目就失去存在意义）+活跃维护+开放治理+**成立>6 个月且 star>50**；Major 再加 **>50 contributors+生产环境规模使用**；排序按 star 季度更新。过滤效应：挡住学术原型与冷启动项目（TripleCross 这类论文仓不在图上）——官方地图≠生态全集（awesome-ebpf 288 条+digests 才是更全样本）；可观测占 Emerging 46 席中的 20 席（约 43%），印证它是 eBPF 最大的产业化出口。[web/md/4.md；第 16 章 16.2.1/16.2.2]

**答 16.2**　(a) 证据链：①iovisor.org 首页"2016 年后更新缓慢，作为当前状态来源不可靠"；②org 内旗舰史料仓 bpf-docs 2019-07-08 冻结；③org 内活的只剩 bcc 与 ubpf（ply 缓慢、kubectl-trace 低频、BPFd/adeb 已死）。职能瓜分：ebpf.io（门户）、CNCF（项目治理）、各公司开源办公室；IO Visor 是"项目代管"模式的化石。(b) 互补：FAQ 原文 "it does not currently host third-party projects"——eBPF Foundation 管标准与布道（RFC 9669 标准化、安全可靠性倡议），不孵化项目；CNCF 负责项目孵化毕业（本库覆盖：毕业 Cilium/Falco，Sandbox Pixie/Tracee/IG/bpfman）——eBPF 项目在 CNCF 跨 networking/observability/security 三个 SIG 域，按技术而非"eBPF"归类。(c) 数字：netdev 订阅 1085（bpf 502、xdp-newbies 305）；累计 1,248,768 封（2006-11 起）；2026-09 单月 15,937 封历史峰值（10 月 14,837，日均约 600）。制度根源：内核治理与 patch 工作流（git send-email/**b4**/Patchwork/lore）深度绑定**纯文本邮件**——GitHub 只是镜像仓库；当天实时贴还能看到 Starovoitov 的 [PATCH bpf] 与 Kicinski 的 GIT PULL 同框。[web/md/4.md、280.md、281.md；第 16 章 16.2.3/16.2.4]

**答 16.3**　(a) 练习判定：**bpflock**=D 档冻结史料（最后提交 2022-02，停滞 4 年——只当教材，选型看同类活项目 owLSM/Bombini）；**merbridge**=C 档已归档（2025-02-19 最后提交，README 自述不再维护——"清单仍列、上游已死"，选 service mesh 加速前必知）；**Ingero/Synapse**=E 档上游已删（GitHub 404）——引用必须标注现状。验活动作：`grep -n "<仓名>" INVENTORY.md` 拿克隆时点 @日期 → 对照 16.4.1 五档（A=2026-09-29 后可直接选型；B/C=读 release notes 判断低频维护还是事实死亡；D=只当教材；E=标注现状）。(b) 提问优先级：**xdp-newbies（305 订阅，专为准新手设）> bpf（502）> netdev（1085，日均约 600 封，别在这里问入门题）**；订阅走 subspace.kernel.org/subscribing.html（vger 已迁移，majordomo 命令废弃）；同步加 ebpf.io Slack 与 r/eBPF。(c) xdp-project/xdp-project 是 **Emacs org-mode 工作区**（README.org 自言 "work-in-progress workspace"，非代码仓）——用 git 可 diff 的方式共享笔记/benchmark/半成品；任务管理用 **OWNER 属性认领制**（org-agenda 的属性过滤替代 GitHub issue assignee）；GitHub 只保留"需多人讨论/明确反馈"的 issues 与 PR 职能，WIP 笔记可直接 commit master；areas/ 按子系统分目录存上游讨论一手档案（core/drivers/cpumap/devmap/...）。[INVENTORY.md；repos/xdp-project/xdp-project/README.org；第 16 章 16.3/16.4.1/16.2.4]

**答 16.4**　(a) 化石挂架说明清单缺"存活审计"机制——三条实例：awesome-ebpf 仍列 2019 年死的两个同名 bpfd（via bpfman 词条）与 IO Visor bpf-docs；Observability 节列已 404 的 Ingero；L3 列 2025 已归档的 merbridge。验活动作：引用前 `grep INVENTORY.md` 拿最后提交日+读仓 README 头部/release；任何 awesome 清单都是快照不是数据库（尾部约 3% 还是结构性噪音：重复条目/贡献者主页/徽章图）。(b) patch 礼仪：Subject 前缀——`[PATCH bpf]`（fix）、`[PATCH bpf-next]`（新特性）、`[PATCH net-next]`（网络子系统）；commit log 按 what/why/how 分段、fix 带 `Fixes:` 标签；**测试先行**：selftests/bpf 用例是硬要求（"未被 test_verifier.c 跟踪的 verifier 行为视为可变"同理）；发帖用 `git send-email` 或 **b4**（B4 Relay 已是列表主流），patch 状态在 Patchwork/lore 可查；入门尺寸=清理类、selftests 补充、驱动 fix。(c) 两种偏向：①star 季度排序=营销竞争（排序按 GitHub star，刷星可影响地图位置）；②">50 stars"门槛把学术原型/冷启动项目挡在官方地图外（地图≠生态全集）。2026 三条 agent 支线：①用 eBPF **观测** agent——AgentSight（eunomia-bpf，arXiv:2508.02736）给 Claude Code/Codex/Gemini CLI 做 top/strace 式零侵入观测；②用 eBPF **强制管控** agent——ActPlane（arXiv:2606.25189）把 IFC 信息流控制编译成内核态强制（"prompt 约束是概率性的，ActPlane 是确定性的"）+ Inner Warden 商业化转型（用户态裁决免费、内核态 Execution Gate 收费）；③生态自身 agent 化——82 仓中至少 8 个带 CLAUDE.md/AGENTS.md 或明示 AI 协作开发（DeepFlow/aya/owLSM 等），Gthulhu 为 LLM 推理线程做 TID 级调度——"eBPF 观测 agent"与"agent 开发 eBPF"双向奔赴。[web/md/280.md、4.md；digests/16/18；第 16 章 16.4.2/16.4.5]

---

## 收尾自查（做完 64 题后）

1. 你能否不看资料画出"ELF .o → bpf(2) → verifier → JIT → attach → maps/helpers"全链路，并说清每步谁负责？
2. 拿到任何 verifier 报错，能否在 3 分钟内定位到 3.4.1 表格里的那一行并给出修复？
3. 引用任何性能/版本数字前，是否形成了"带出处与语境"的肌肉记忆（ERRATA.md 是最后一道闸）？
4. 选型题（XDP vs tc、ringbuf vs perf array、cilium/ebpf vs libbpfgo vs aya、三代安全方案、三路线用户态网络）是否都能给出"第一性判断+备选+代价"三段式回答？
5. 生态题的落点：你是否已经选定一个 A 档活仓（INVENTORY 验活）作为下一步的动手对象？
