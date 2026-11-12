# 批次: 12-工具链·用户态与bpftool（21 条）

本批覆盖 eBPF 工具链的用户态全景：编译器侧（LLVM/BPF backend 的诞生史与 apt 分发）、加载器侧（libbpf 及其 GitHub 镜像、libbpf-bootstrap 脚手架）、内核树自带工具（bpftool/bpf_asm/bpf_dbg/bpf_jit_disasm，多为 kernel.org cgit 页面且部分被 Anubis 反爬盾拦截）、以及用户态 eBPF 运行时谱系（uBPF/generic-ebpf/rbpf 解释器与 JIT、VALE-BPF 网络交换机用例、PREVAIL 用户态验证器及其 PLDI'19 论文、wachy 可视化 profiler）。主线叙事是"内核 eBPF 生态把整套验证器/解释器/编译器复刻到用户态"，从 uBPF 的 BSD 许可 JIT 到微软系 PREVAIL 的抽象解释验证器，再到 rbpf 的 Rust 教学实现，构成一幅完整的"eBPF everywhere"工具地图。坑点：本批 6 条 kernel.org cgit 链接中多条仅剩反爬盾壳页或目录列表，真正有料的内容靠 GitHub 镜像仓和论文 PDF 补齐。

## [140] LLVM
- 是什么：LLVM 编译器基础设施官网首页快照（2026-11 时点，最新 23.1.5）。eBPF 生态的编译侧基石——C 源码经 clang -target bpf 编译成 BPF 字节码，LLVM 是唯一主流 BPF 后端。
- 核心内容：LLVM 全景（Clang/Flang/LLDB/libc++/compiler-rt/MLIR/BOLT 等 14 个子项目）、发布节奏（23.1.x 系列 2026-08 起月度 patch）、社区入口（Discourse/Discord/dev meetings）。2012 ACM Software System Award 得主。
- 对人类学习者：本文档本身与 eBPF 关系弱，价值在于锚定"BPF 是 LLVM 一等公民 target"这个事实；学 eBPF 工具链时版本选择（旧内核需旧 clang，如 4.x 内核配 LLVM 3.7+）是常见痛点。
- 对 AI agent：web/md/140.md 可 grep "Release Schedule" 查版本时间线；安装最新 clang 参见 141。
- 本地路径: /usr-data/data2/kylin/network/awesome-ebpf/web/md/140.md

## [141] here（apt.llvm.org）
- 是什么：LLVM 官方 Debian/Ubuntu apt 仓库页面——拿新版 clang（编译 eBPF 程序）最省事的途径。
- 核心内容：自动安装脚本 `bash -c "$(wget -O - https://apt.llvm.org/llvm.sh)"` 或 `sudo ./llvm.sh <版本号>`；支持 Debian bullseye~sid + Ubuntu focal~resolute，当前分支 22（old-stable）/23（stable）/24（snapshot）；提供全家族包（clang/lld/lldb/libc++/mlir/bolt/flang）；已部署 sigstore 签名可验证；每日两次 Jenkins 重建。
- 亮点：月流量 124TB、被 Linux Kernel/TensorFlow 等引用 24k+ 次——是内核 CI 拿新编译器的事实通道。
- 对人类学习者：老 distro 编不了新 BPF 特性（如 BTF、atomics）时的标准解法就是挂 apt.llvm.org 装 clang-1x。
- 对 AI agent：web/md/141.md grep "llvm.sh" 拿安装命令；grep "apt-get install clang-" 拿各版本包名清单。
- 本地路径: /usr-data/data2/kylin/network/awesome-ebpf/web/md/141.md

## [142] this commit（LLVM D6494 BPF backend review）
- 是什么：LLVM Phabricator D6494——Alexei Starovoitov（ast）2014-12-02 提交、2015-01-24 合入（rL227008）的 LLVM BPF backend 原始 review 全录，eBPF 编译器侧的"创世文档"。
- 核心内容：V1 cover letter 是最好的 eBPF ISA 简史——"universal in-kernel VM"，R0 返回值/R1-R5 参数/R6-R9 callee-saved/R10 只读帧指针，双操作数指令，隐式 prologue/epilogue，无浮点无 SIMD；内核侧时间线（3.15 解释器、3.16 x64 JIT、3.18 verifier+bpf syscall）；设计哲学"kernel rejects all programs that it cannot prove safe"。review 过程本身也是 LLVM 社区教材：Chandler/arsenm/tstellar 的代码卫生 nit、Tim Northover 问"谁来维护防止 bit-rot"、ast 用 git grep 计数反驳命名规范争议。
- 亮点：初版 backend 只有 ~2000 行（BPFISelLowering.cpp 642 行为最大文件），且刻意不支持全局变量/任意函数调用/varargs/间接跳转/alloca——这些限制今天大多已被逐步解除，是理解"为什么 BPF C 是受限 C"的第一手出处。
- 对人类学习者：读 cover letter + 时间线即可收获 80% 价值；想深挖 LLVM 后端结构（TableGen .td/ISelLowering/MCTargetDesc）可对照 diff 逐文件读。
- 对 AI agent：web/md/142.md grep "Short summary of instruction set" / "rL227008" / "no floating point"；引用 BPF ISA 设计初衷时此文是一手来源。
- 本地路径: /usr-data/data2/kylin/network/awesome-ebpf/web/md/142.md

## [143] libbpf（kernel.org cgit 页）
- 内容缺失：抓取时被 kernel.org 的 Anubis 反爬盾（Proof-of-Work JS challenge）拦截，本地仅存挑战页壳，无 libbpf 实际内容。
- 补救：libbpf 内容由 [144] GitHub 镜像仓完整覆盖（README+源码树）；kernel.org 原路径 tools/lib/bpf 的文档可走 GitHub torvalds/linux 镜像树替代。
- 对 AI agent：勿引用 143.md 作事实来源；grep 只会命中 "Anubis"。
- 本地路径: /usr-data/data2/kylin/network/awesome-ebpf/web/md/143.md

## [144] mirrored on GitHub（libbpf 官方 GitHub 镜像）
- 是什么：libbpf 官方 GitHub 仓——权威源码在内核树 bpf-next 的 tools/lib/bpf，此仓定期同步，供构建/打包/submodule 使用。最后提交 2026-11-02，极活跃。
- 核心内容：C 库（src/ 约 35 个文件），用户态 BPF 加载器的事实标准：bpf.c（syscall 封装）、libbpf.c（BPF 对象打开/加载/attach 生命周期，万行级）、btf.c+btf_dump.c（BTF 解析与 C 类型重排）、relo_core.c（CO-RE 重定位）、ringbuf.c（BPF ring buffer 消费）、linker.c（轻量 BPF 静态链接器）、gen_loader.c（BTF-gen/light skeleton）、bpf_helpers.h/bpf_tracing.h/bpf_core_read.h（BPF 程序侧头文件）。构建：`cd src && make`（依赖 libelf，pkg-config 可用 NO_PKG_CONFIG=1 关闭）。
- 亮点：CHECKPOINT-COMMIT/SYNC.md 记录与内核树的同步点；文档在 libbpf.readthedocs.io；提交走 bpf@vger.kernel.org 邮件列表，GitHub 不收 PR。
- 对人类学习者：每个 eBPF 应用的用户态侧几乎都从 `libbpf_open_and_load` 起步；学 CO-RE 原型（PT_REGS/___clone/BPF_CORE_READ）直接读三个头文件即可。
- 对 AI agent：repos/libbpf/libbpf/src 可 grep "bpf_map__" / "libbpf_get_error" / "bpf_program__attach" 查 API 语义；bpf_helper_defs.h 是全部 helper 原型的机器可读清单（写 BPF 代码时的权威参考）。
- 本地路径: /usr-data/data2/kylin/network/awesome-ebpf/repos/libbpf/libbpf

## [145] libbpf-bootstrap
- 是什么：libbpf 官方配套脚手架仓（Andrii Nakryiko 维护），"copy/paste 改名即用"的 BPF 应用起点模板集。最后提交 2026-10-22，活跃。
- 核心内容：examples/c 下渐进式样例——minimal（tracepoint+bpf_printk 起步，无 CO-RE 要求）/minimal_ns（容器/WSL2 命名空间环境）/minimal_legacy（更老内核，无全局变量支持）/bootstrap（真实应用骨架：exec/exit tracepoint 协作程序+map 状态+ring buffer 传数据+CO-RE+vmlinux.h 读 task_struct+Ctrl-C 优雅退出）/bootstrap_legacy（ringbuf 换 perf event array 兼容 <5.8 内核），另有 fentry/kprobe/ksyscall/lsm/profile/sockfilter/task_iter/uprobe/cpus/module 等 15+ 场景与 examples/c/rust Rust(Aya) 版。
- 亮点：三种内核兼容梯度（现代/老内核/命名空间）演示得干干净净；vmlinux.h 直接放在仓根；含 Android 构建工作流。
- 对人类学习者：公认的 eBPF 入门第一站——从 minimal 跑通 trace_pipe 输出到 bootstrap 组装完整应用，配套博客 nakryiko.com/posts/libbpf-bootstrap/。
- 对 AI agent：仓内是最适合"抄骨架"的参考实现库——写 kprobe/fentry/lsm/ringbuf 消费代码前先 grep examples/c/ 对应样例；Makefile 展示 clang -target bpf 编译参数标准写法。
- 本地路径: /usr-data/data2/kylin/network/awesome-ebpf/repos/libbpf/libbpf-bootstrap

## [153] bpftool（bpf-next 树 tools/bpf/bpftool）
- 内容缺失：kernel.org cgit 被 Anubis 反爬盾（Proof-of-Work JS challenge）拦截，本地 153.md 仅 26 行挑战页壳。
- 公知定位（非抓取内容）：bpftool 是内核树自带的 BPF 万能管理 CLI——prog/map/link/cgroup/perf/net/struct_ops/iter/btf/gen 子命令体系，骨架生成（bpftool gen skeleton）是 libbpf 工作流的关键一环。
- 补救路径：GitHub 镜像 torvalds/linux 或 libbpf/bpftool 仓（tools/bpf/bpftool）；本仓 [145] libbpf-bootstrap 已内嵌 bpftool 子模块可直接阅读。
- 对 AI agent：153.md 无事实可引。
- 本地路径: /usr-data/data2/kylin/network/awesome-ebpf/web/md/153.md

## [154] linux/tools/net/（v4.14 树）
- 内容缺失：同上 Anubis 盾壳页（26 行）。
- 公知定位（非抓取内容）：awesome-ebpf 原清单在此小节的历史注脚——早期内核中 BPF 工具位于 tools/net/，v4.14 前后 bpf_asm 等还在此处，后才迁至 tools/bpf/。
- 补救路径：GitHub torvalds/linux tag v4.14 的 tools/net 目录。
- 对 AI agent：154.md 无事实可引。
- 本地路径: /usr-data/data2/kylin/network/awesome-ebpf/web/md/154.md

## [155] linux/tools/bpf/（net-next 树）
- 内容缺失：同上 Anubis 盾壳页。
- 公知定位（非抓取内容）：内核 BPF 工具总目录，含 bpftool/、bpf_asm.c、bpf_dbg.c、bpf_jit_disasm.c、bpf_jit_disasm 等；本批 156-159 四条是其具体成员。
- 补救路径：GitHub torvalds/linux 的 tools/bpf 目录（raw 文件可直读）。
- 对 AI agent：155.md 无事实可引。
- 本地路径: /usr-data/data2/kylin/network/awesome-ebpf/web/md/155.md

## [156] `bpftool`（重复条目）
- 内容缺失：与 [153] 同一 URL（bpf-next 树 tools/bpf/bpftool）的重复收录，同为 Anubis 盾壳页。
- 说明：awesome-ebpf 原文中 bpftool 在"bpftool and Other Tools from the Kernel Tree"小节出现两次；实质内容见 [153] 条目的补救路径。
- 对 AI agent：156.md 无事实可引。
- 本地路径: /usr-data/data2/kylin/network/awesome-ebpf/web/md/156.md

## [157] `bpf_asm`
- 内容缺失：Anubis 盾壳页。
- 公知定位（非抓取内容）：内核树 UASM 汇编器——把人类可读 BPF 汇编（ldxh/jeq/stb 等助记符）汇编成 classic BPF 字节码指令序列，配合 bpf_dbg 使用；主要面向 classic BPF（socket filter）而非 eBPF C 工作流，现属遗留工具。
- 补救路径：GitHub torvalds/linux raw tools/bpf/bpf_asm.c。
- 对 AI agent：157.md 无事实可引。
- 本地路径: /usr-data/data2/kylin/network/awesome-ebpf/web/md/157.md

## [158] `bpf_dbg`
- 内容缺失：Anubis 盾壳页。
- 公知定位（非抓取内容）：内核树 BPF 调试器（基于 readline 的交互 shell）——加载 bpf_asm 产出的 classic BPF 程序、喂 pcap 抓包或手工构造的包、单步执行观察 filter 行为，亦可反汇编 bpf_jit_disasm 的输出。
- 补救路径：GitHub torvalds/linux raw tools/bpf/bpf_dbg.c。
- 对 AI agent：158.md 无事实可引。
- 本地路径: /usr-data/data2/kylin/network/awesome-ebpf/web/md/158.md

## [159] `bpf_jit_disasm`
- 内容缺失：Anubis 盾壳页。
- 公知定位（非抓取内容）：内核 BPF JIT 编译产物反汇编器——读取 /proc/sys/net/core/bpf_jit_enable=2 时内核导出的 JIT 镜像地址（bpf_jit_image 导出 kallsyms），用 opcodes 库反汇编 JIT 后的本机机器码；是验证 JIT 正确性/看最终生成的宿主指令的必备工具。
- 补救路径：GitHub torvalds/linux raw tools/bpf/bpf_jit_disasm.c。
- 对 AI agent：159.md 无事实可引。
- 本地路径: /usr-data/data2/kylin/network/awesome-ebpf/web/md/159.md

## [160] uBPF
- 是什么：iovisor 出品的 Apache-2.0 许可用户态 eBPF 虚拟机——因内核 eBPF 是 GPL 无法被闭源项目复用而生，是最老牌的用户态 eBPF 运行时。最后提交 2026-10-16，非常活跃。
- 核心内容：C 库含汇编器/反汇编器/全平台解释器 + x86-64 与 Arm64 JIT（vm/ubpf_vm.c、ubpf_jit_x86_64.c、ubpf_jit_arm64.c）。README 明确引用 RFC 9669（BPF ISA 官方标准化）为规范基准。亮点是新的 **Safe Execution Profile**：显式解释器专用档位，带寄存器来源追踪（register provenance）、集中式检查解引用、类型化 helper 元数据、descriptor 支持的外部内存区域——歧义指针算术直接拒绝而非事后范围扫描恢复，面向"不依赖外部 verifier 也要安全"的嵌入场景（首版 Safe 档不开 JIT）。另有 docs/VerifiedPrograms.md 专门讲与 PREVAIL 验证过的程序配合使用时 context 指针的注意事项。
- 对人类学习者：理解"eBPF 脱离内核也能跑"的第一站；Safe profile 是活教材——把内核 verifier 的指针追踪思想压缩进用户态运行时。
- 对 AI agent：repos/iovisor/ubpf/vm 可 grep "ubpf_register" / "execution_profile" / "ubpf_jit" 查 API；与 [165] PREVAIL、[164] rbpf 构成用户态 eBPF 三角（运行时/验证器/Rust 版）。
- 本地路径: /usr-data/data2/kylin/network/awesome-ebpf/repos/iovisor/ubpf

## [161] A generic implementation（generic-ebpf）
- 是什么：YutaroHayakawa（FreeBSD eBPF 移植主将）的"泛型 eBPF 运行时"学术项目——一套代码同时在 FreeBSD/Linux 内核态与用户态、macOS 用户态运行 eBPF。最后提交 2021-05-28，已停更（作者转投 FreeBSD 主线 eBPF 工作）。
- 核心内容：三组件——ebpf（可移植解释器+JIT+map 子系统库）、ebpf_dev（字符设备加载接口，Linux bpf(2) 的替代品）、libgbpf（跨后端抽象层+BPF ELF 解析器，支持 ebpf_dev 与 Linux 原生 eBPF 双后端）。支持矩阵：ebpf 库全覆盖四环境，ebpf_dev 仅两大 BSD/Linux 内核。构建产物 ebpf.ko/ebpf-dev.ko 内核模块 + libebpf.so/libgbpf.a 用户库。
- 对人类学习者：跨内核 eBPF 移植的先行实验田（FreeBSD eBPF 的前身），学"eBPF 抽象层怎么设计"的参考；但作为工具已过时，读代码价值大于使用价值。
- 对 AI agent：repos/YutaroHayakawa/generic-ebpf 可 grep "ebpf_dev" / "libgbpf" 看跨平台抽象设计；上游应用见 [163] vale-bpf。
- 本地路径: /usr-data/data2/kylin/network/awesome-ebpf/repos/YutaroHayakawa/generic-ebpf

## [162] VALE software switch（vale(4) man page）
- 是什么：FreeBSD vale(4) 手册页——VALE 虚拟本地以太网交换机的官方文档，是 [163] vale-bpf 的宿主系统背景知识。
- 核心内容：vale 是 netmap(4) 模块的特性，纯软件实现的多虚拟交换机，互连 netmap 客户端（流量源/汇、包转发器、用户态防火墙）；性能"现代机器小包 ~20 Mpps/核、1500 字节帧 ~70 Gbit/s"。端口命名 vale[bdg:][port]（总长≤16 字符）；硬限制 4 交换机×16 端口×1024 缓冲；sysctl dev.netmap.bridge 控制每轮处理包数（延迟/吞吐权衡）。示例：pkt-gen 打流 + tcpdump -ni vale-a:1 抓包、qemu -net netmap,ifname=vale-1:a 虚机互联。作者 Luigi Rizzo/Giuseppe Lettieri（比萨大学，2012）。
- 对人类学习者：理解"eBPF 不止 Linux"路线的关键拼图——VALE 这类高性能软件交换机是 FreeBSD eBPF（vale-bpf）最初的应用场景。
- 对 AI agent：web/md/162.md grep "Mpps" / "netmap" / "vale-" 拿性能数字与用法示例。
- 本地路径: /usr-data/data2/kylin/network/awesome-ebpf/web/md/162.md

## [163] BPF extension module（vale-bpf）
- 是什么：给 VALE 软件交换机加 eBPF 可编程能力的内核模块（FreeBSD/Linux），以 [161] generic-ebpf 为运行时后端。最后提交 2019-11-06，README 明言"generic-ebpf 稳定前不再更新"——实质已归档。
- 核心内容：依赖 generic-ebpf + netmap；工作流：vale-ctl 建交换机并挂接口（vale-ctl -n vi0; vale-ctl -a vale0:vi0）→ make load 装模块 → 用 benchmark/vale-bpf/l2_bridge/l2_bridge_loader -v vale0 加载 eBPF 程序（示例为 L2 网桥逻辑）。
- 对人类学习者："eBPF 程序交换机转发面"的早期实证——比 Linux XDP 之外的另一条可编程数据路径，适合研究 eBPF 跨平台史，不适合生产使用。
- 对 AI agent：repos/YutaroHayakawa/vale-bpf grep "l2_bridge" 看 eBPF 交换机程序长什么样；引用时须注明项目停更状态。
- 本地路径: /usr-data/data2/kylin/network/awesome-ebpf/repos/YutaroHayakawa/vale-bpf

## [164] rbpf
- 是什么：Quentin Monnet（Cilium/eBPF 文档界名人）用 Rust 写的用户态 eBPF 虚拟机，基于 uBPF 移植。最后提交 2026-06-03，仍温和维护。crates.io 版 0.4.1。
- 核心内容：解释器 + x86_64 JIT + 反汇编器，跨 Linux/macOS/Windows 编译（JIT 暂不支持 Windows）。API 四步走：建 VM（传 eBPF 字节码）→ 注册 helper → JIT 编译 → 执行。README 教学性极强：解释了 eBPF 程序通过 sk_buff 元数据取包数据指针的经典模型、两种 VM 变体（EbpfVm/可执行体）。已知被用作教学与原型验证。
- 亮点：Rust 生态用户态 eBPF 的元老实现，代码量小、注释密，是"读一个完整 eBPF VM"最低成本的入口；uBPF 的对照阅读材料。
- 对人类学习者：想看懂 eBPF 解释器/JIT 内部机制，rbpf 的 Rust 源码比 C 更易读；docs.rs 有完整 API 文档。
- 对 AI agent：repos/qmonnet/rbpf/src 可 grep "JIT" / "helper" 看实现；写 Rust 原型需跑 eBPF 字节码时直接 crate 依赖。
- 本地路径: /usr-data/data2/kylin/network/awesome-ebpf/repos/qmonnet/rbpf

## [165] PREVAIL（vbpf/ebpf-verifier）
- 是什么：PREVAIL——微软系（VMware Research 起家）的用户态 eBPF 验证器，Polynomial-Runtime EBPF Verifier using an Abstract Interpretation Layer，PLDI'19 论文的工业延续（仓已更名 vbpf/prevail）。最后提交 2026-11-06（本批最新鲜的仓），极活跃。
- 核心内容：C++23（GCC 13+/Clang 17+）构建，跨 Linux/Windows/macOS + Docker；CLI `bin/prevail <elf> <section> <function>` 输出 PASS/FAIL。功能面丰富：CFG 导出 dot、反汇编 --asm（替代 llvm-objdump -S）、--termination 可验证终止性、--stack-size/--max-call-stack-frames/--max-packet-size 等可调验证参数、conformance groups（atomic32/64、base32/64、callx、divmul32/64、packet）包含/排除——对齐 RFC 9669 ISA 一致性分组；--failure-slice 输出"导致错误的最小指令切片"（默认回溯 200 步）。
- 亮点：是 Windows eBPF（eBPF for Windows）与用户态 eBPF 生态（配合 uBPF）的验证器标准件；仓库有 AGENTS.md（AI 协作开发已进入这个项目的工作流）。
- 对人类学习者：学抽象解释工程落地的最佳真实样本；与 [166] 论文对照读（论文讲原理，仓库讲工程化二十年的演进）。
- 对 AI agent：repos/vbpf/ebpf-verifier/src 可 grep "failure_slice" / "termination" / "conformance"；ebpf-samples/ 内置 cilium 等真实测试程序集。
- 本地路径: /usr-data/data2/kylin/network/awesome-ebpf/repos/vbpf/ebpf-verifier

## [166] using an abstract interpretation layer（PLDI'19 论文）
- 是什么：PREVAIL 的原始论文《Simple and Precise Static Analysis of Untrusted Linux Kernel Extensions》（Gershuni et al., PLDI'19, DOI 10.1145/3314221.3314590），Tel Aviv Univ. × VMware Research × Waterloo × SRI 八人作者。本地 pdf-txt 全文 1002 行可读。
- 核心内容：把内核 eBPF verifier 的四大痛点（false positives 多、不扩展、不支持循环、无形式化基础）放进 abstract interpretation 框架重做。关键洞察：eBPF 程序以"有纪律的方式"操纵少量独占内存区域（context/packet/stack），指针表示为 (region, offset) 对——bounded stack 精确建模、packet 等安全访问粗粒度忽略即够。数值域选型实验：Interval 不够精确，Octagon/Polyhedra 代价过高，**Zone domain（约束形如 X − Y ≤ C，理论立方最坏复杂度、实践快）**在真实程序上与贵域同样精确。实现于 Crab 框架（zone-crab 稀疏表示+split 转换器）。
- 关键数字：192 个真实程序（linux 86/OVS 18/suricata 5 等六项目）仅 1 个 false positive；每程序 ≤5.2s、平均 ~1500 指令/秒；首个支持**带循环** eBPF 程序验证的工具（Linux verifier 靠 CFG 无环硬拒循环，路径枚举型在循环上指数爆炸，实测 69 次迭代撞复杂度上限）；验证目标三性质=memory safety + information flow security + termination。
- 对人类学习者：eBPF + 程序分析双背景读者的必读经典——既是 verifier 原理教材（§2 eBPF 内存模型/寄存器 spilling 讲得比内核文档清楚），也是"如何为受限 DSL 选抽象域"的方法论范文。
- 对 AI agent：web/pdf-txt/166.txt grep "Zone" / "Crab" / "false positive" / "termination"；讨论内核 verifier 局限或用户态验证器设计时引用此全文。
- 本地路径: /usr-data/data2/kylin/network/awesome-ebpf/web/pdf-txt/166.txt

## [167] wachy
- 是什么：Rubrik 开源的 eBPF 用户态性能调试器——"A New Approach to Performance Debugging"，用 uprobe 动态插桩任意已编译二进制的任意函数，0 修改、0 改码、运行时加过滤。项目页快照（文档站 rubrikinc.github.io/wachy）。
- 核心内容：卖点四条——低开销动态插桩（未跟踪函数零开销）；深度代码集成（把 eBPF 追踪接回源码行，号称比裸用 eBPF 快/易 10-100 倍）；真实延迟测量（非采样 profiler，含网络/IO/mutex 阻塞时间，支持延迟直方图）；运行时过滤（"只看 A 调用 B 且 A 首参为 0 的延迟"）。适用场景：高频函数平均延迟、嵌套函数迭代式探索（维护被跟踪函数栈）、尾延迟分析（>100ms 才看内部耗时）、生产环境 TUI 调试（只需 SSH）。明确边界：需 Linux ≥4.6；只支持编译型语言（uprope+调试符号，C++ demangle 支持）；每次被跟踪调用 ~3μs 开销，超低延迟函数不适用。
- 对人类学习者：eBPF 用户态应用的优秀产品化样本——比裸写 uprobe+ringbuf 省一个数量级工作量；"什么场景 eBPF 追踪不合适"（3μs 线）的诚实表述也少见。
- 对 AI agent：web/md/167.md grep "μs" / "uprobes" / "4.6" 拿边界条件；作 eBPF 落地案例引用（本批仅存文档站快照，无源码克隆，活跃度未验证）。
- 本地路径: /usr-data/data2/kylin/network/awesome-ebpf/web/md/167.md
