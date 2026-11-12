# 批次 05：BPF 内部机制与 BTF（11 条）

> 资源消化产物 · 清单 manifest/disp/05-BPF内部机制与BTF.txt · 生成于 2026-11-06

**本批总评**：这批资源由两条时间线构成——前 8 条（id 50-57）是 2016-2017 年 eBPF 在 tc/cls_bpf 数据面崛起期的"一手史料"（Daniel Borkmann 在 FOSDEM/netdev 的演讲与论文、Jamal Hadi Salim 的 tc workshop 议程、Thomas Graf 的 Linux 网络栈全景图），后 3 条（id 83-85）是 BTF（BPF Type Format）从内核官方规范到 Facebook 工程博客再到现代科普的完整阶梯。质量分布明显两极：54/55（cls_bpf 可编程化论文）、56（FOSDEM 2016 slides）、57（Linux Networking Explained）、83（kernel 文档）、84（BTF 设计动机）是实料干货；50/51/53 只是会议议程页元数据（slides 链接未本地化），52 是 4 页速览卡片。对学习者的最大价值在于：54/55 讲透了 tc 与 eBPF 的前世今生（从 u32/ematch 的局限推导出为什么必须 eBPF），56 是单文件讲清 tc+eBPF 全貌的最佳 slide，83 是 BTF 二进制格式唯一权威参考；对 AI agent 而言，83 可 grep 出 BTF kind 常量/section 布局等硬规格，54/55/56 可 grep 出 cls_bpf 指令集与 verdict 语义。

---

## [50] eBPF and XDP walkthrough and recent updates

- **是什么**：FOSDEM 2017（Brussels，2017-02-04）SDN and NFV devroom 讲座的会议页元数据，讲者 Daniel Borkmann，30 分钟场次。本地 md 只有议程页（track/room/时间/讲者），不含正文。
- **核心内容**（据页面摘要）：概览 Linux 内核 eBPF 子系统及其与 tc（traffic control）、XDP（eXpress Data Path）的集成，即高性能内核可编程网络数据面；并盘点自上届 FOSDEM 以来进入内核的最重要 eBPF 新特性与编程示例。
- **亮点或坑**：坑——slides PDF（2017_fosdem.pdf）与视频（webm/mp4）链接在 fosdem.org 域名下，未本地化，本条实质是"目录卡"。2017 年初这一时间点正好是 XDP 刚进入内核主线（4.8）后的第一个完整年度总结。
- **对人类学习者的价值**：低（单独看）；高（配合外链 slides 时）——作为 eBPF/XDP 编年史的 2017 锚点。
- **对 AI agent 的用法**：`web/md/50.md`，可 grep "eXpress Data Path" 定位摘要段；外链视频 `video.fosdem.org/2017/UA2.114/ebpf_xdp*` 是唯一内容来源。

## [51] Advanced programmability and recent updates with tc's cls_bpf

- **是什么**：netdev 1.2（东京）Daniel Borkmann talk 的 session 页元数据，是 netdev 1.1 上"On getting tc classifier fully programmable with cls_bpf"（即本批 id 54/55）的续集。
- **核心内容**（据页面描述）：cls_bpf 的高级特性与示例——隧道封装协议（vxlan/geneve/gre）的 tunneling helpers、新的 event output helper（bpf_perf_event_output）、cgroup v2 支持，以及当时可预见要解决的挑战。
- **亮点或坑**：坑——slides/video/paper 三链接均未本地化；与 id 52 的 4 页 slides 摘要卡可互相印证（52 正是同期 tc workshop 材料并列出的同类更新点）。
- **对人类学习者的价值**：中——给出 2016 下半年 cls_bpf 特性演进清单的"名词表"，逐项展开需要看外链 slides。
- **对 AI agent 的用法**：`web/md/51.md`，grep "tunneling helpers" / "cgroup v2" 可拿特性名；与 52.txt 交叉验证同一批更新。

## [52] cls_bpf/eBPF updates since netdev 1.1（slides 文本）

- **是什么**：netdev 1.2 tc workshop（东京，2016-10-05）Daniel Borkmann（时属 Noiro Networks/Cisco Systems）的 4 页速览 slides 全文，盘点 netdev 1.1 到 1.2 之间的 eBPF/cls_bpf 更新。
- **核心内容**：三条线——①cls_bpf 程序能力：tunnel key/options metadata 收集（vxlan/geneve/gre/ipip/ipip6/ip6ip6）、direct packet access（读/写/helpers）、event output helper、cgroup v2、更多 helper（l3/l4/csum_complete 校验和 fixup、NAT64 头重写辅助、skb metadata mangling）、Netronome SmartNIC 硬件 offload；②eBPF core：hash map 预分配、verifier 新参数类型（未初始化 stack buffer、NULL 参数）、verifier 搜索剪枝改进、RCU/refcounting 修复；③JIT（arch/）：当时已有 x86_64/arm64/ppc64/s390，通用 constant blinding 基础设施，ppc64 首个 JIT+tail call，arm64 加 tail call 与 JSET（还缺 BPF_XADD），s390 修 skb→data/hlen recache。
- **亮点或坑**：信息密度极高的"时代切片"：一页看完 2016 年 eBPF 的 arch 支持矩阵与 verifier 演进；注意 BPF_XADD 在 arm64 当年缺失、JIT 只有 4 架构，可作历史对照。
- **对人类学习者的价值**：中高——适合做"eBPF 2016 时间线"的记忆锚；tunnel metadata collect + direct packet access 是 cls_bpf 区别于 XDP 的能力差异点（XDP 当时不覆盖）。
- **对 AI agent 的用法**：`web/pdf-txt/52.txt`，grep "constant blinding" / "tail call" / "XADD" 取 JIT 演进事实；grep "Netronome" 取硬件 offload 起点证据。

## [53] this tc workshop（TC extended workshop 议程）

- **是什么**：netdev 1.2 的 tc 扩展 workshop 议程页（讲者 Jamal Hadi Salim），是 id 52 slides 的"母会议"目录。
- **核心内容**：五项议程——tc 回归测试（Lucas/Roman）、tc eBPF state of union（Daniel，即 id 52）、qdisc 锁讨论（John）、match 工具/cls_u32 links+maps（John）、35 分钟硬件 offload 专题（Intel/Chelsio/Mellanox CX/Spectrum 四家 NIC 厂商各讲一摊）。
- **亮点或坑**：价值在"索引性"——页面列出 5 份 slides PDF 链接（qdisc+match_tool、Chelsio/mlxsw/mlx5 offload 三份 NIC 材料）+YouTube 视频，均未本地化；可看出 2016 年硬件 offload 是 tc 社区的中心议题（议程 35 分钟占比最大）。
- **对人类学习者的价值**：低（纯议程）；中（作为检索硬件 offload 早期材料的入口）。
- **对 AI agent 的用法**：`web/md/53.md`，grep "Offload" 取厂商清单（Intel/Chelsio/Mellanox 两线）；外链 slides URL 模式 `slides/oct5/07_tcws_*` 可供后续补抓。

## [54] On getting tc classifier fully programmable with cls_bpf（netdev 1.1 slides 版）

- **是什么**：Daniel Borkmann 在 netdev 1.1（Seville，2016-02-12）的 23 页 slides 全文——cls_bpf + eBPF 的"定音之作"讲稿，标题即立场：让 tc classifier 完全可编程。
- **核心内容**：完整教学线——①BPF 起源（tcpdump→libpcap→编译器→bytecode→内核解释器，AF_PACKET 收包路径早丢弃点）；②cBPF 速览（32 位、A/X/M[0-15] 寄存器、64 位指令编码 u16:code/u8:jt/u8:jf/u32:k、仅前向跳转、4096 条上限、33 指令+11 寻址模式+16 个 Linux 扩展）；③eBPF 架构（64 位 R0-R10、新指令 dw ld/st/mov/alu64/signed shift/endian/call/xadd、稳定 ABI、bpf(2) syscall+fd 管理、内核内 cBPF→eBPF 迁移——cBPF 解释器已不存在）；④cls_bpf 两种模式（走完整 tc action 引擎 tcf_exts_exec() vs direct-action (da) 快路径直接返回 verdict）；⑤verdict 码：ok/shot/stolen/redirect/unspec；⑥挂载点：ingress（__netif_receive_skb_core→sch_handle_ingress）与 clsact egress（__dev_queue_xmit→sch_handle_egress）；⑦helper 调用约定（R0 返回/R1-R5 参数/R6-R9 callee-saved/R10 只读帧指针，struct bpf_func_proto 给 verifier 做类型检查）；⑧tail call 实现（program array + long jump 复用栈帧、失败则 fall-through）；⑨object pinning（bpf fs，解决 fd 生命周期问题）；⑩安全（verifier 检查环形控制流/未初始化内存/死代码/类型；CONFIG_DEBUG_SET_MODULE_RONX 锁 RO+随机化起始地址；constant blinding 防 JIT spraying 当时标注"near future"）；⑪LLVM 工作流 `clang -O2 -target bpf`（LLVM 3.7 起），C→LLVM→ELF→tc→kernel(verification/JIT)→cls_bpf(exec)。
- **亮点或坑**：一页 slide 的完整 tc 命令示例（clsact qdisc + ingress/egress bpf da 挂载 + 删除）可直接照抄跑；时代局限标注——当时 JIT 仅 x86_64/s390/arm64，512 字节栈、无动态循环这些约束延续至今。
- **对人类学习者的价值**：极高——单份材料把 cBPF→eBPF 的演进逻辑、cls_bpf 的 da 模式语义、helper/map/tail call/pinning 四大机制、verifier 与安全模型全部串起来，是理解"tc 数据面为什么长这样"的最短路径。
- **对 AI agent 的用法**：`web/pdf-txt/54.txt`，grep "bpf_func_proto" 取 helper 签名规格、grep "direct-action" / "TC_ACT" 取 verdict 语义、grep "R10" 取调用约定；slides 页码标记（N / 23）可做引用锚。

## [55] On getting tc classifier fully programmable with cls_bpf（netdev 1.1 论文版）

- **是什么**：同一标题的正式 proceedings 论文（netdev 1.1 论文集，424 行全文），slides 版（id 54）的扩写版，含 28 条带 commit hash 的参考文献——每项关键特性都能定位到具体 Linux kernel/iproute2 commit。
- **核心内容**：与 54 同骨架但细节更深的增量——①eBPF ISA 定位为"cBPF+x86_64+arm64+risc 的混合体"，指令编码专为 JIT 而设计（寄存器映射贴合硬件调用约定，helper 调用 JIT 后只需发一条 call）；②tail call 约束补充：仅同类型程序可互相 tail call、JIT 与解释不能混用、跨程序传状态只能靠 per-CPU map 或 skb->cb 区；③cls_bpf 历史考据：2013 年以 cBPF 分类器诞生（commit 7d1d65cb84e1），2015 年加 eBPF 支持（e2e9b6541dd4），act_bpf 区别仅在返回码（classid vs action opcode）；④非 da 模式的性能税：cBPF 时代 skb 不可改需追加 act_pedit 走 action 管线；⑤redirect 两种实现（clone skb vs da 模式免 clone 的 TC_ACT_REDIRECT + per-CPU scratch buffer + skb_do_redirect()）；⑥tc 前端 ELF 加载全流程（挂 bpf fs 到 /sys/fs/bpf、maps 保留 section、三种 pinning 作用域 globals/<obj-sha>/custom、重定位注入 map fd、tail call section 加载与 grafting 运行时替换）；⑦编程约束（512 字节栈、无全局变量——用单条目 array map 模拟、仅允许 map 相关重定位——loader 与 clang 的"契约"、编译期常量循环可展开否则 verifier 拒绝）；⑧future work：NIC offload 与 CRIU 容器迁移的 eBPF 支持。
- **亮点或坑**：参考文献表本身就是"eBPF 上游化编年史"（Starovoitov 2014 四连 commit：syscall/verifier/program load/x86 JIT），做考古或写综述时是现成的 citation 清单；object pinning 一节记录了被否掉的 fuse 代理方案及理由（额外 daemon 依赖）。
- **对人类学习者的价值**：极高——比 54 更适合精读；"loader 与 clang 的契约"和"全局变量用 map 模拟"两段解释了很多初学者撞到的真实困惑。
- **对 AI agent 的用法**：`web/pdf-txt/55.txt`，grep "commit" 取特性-commit 映射表、grep "512" / "unrolled" 取编程约束、grep "obj-sha" 取 pinning 作用域规格；与 54 互为长短版可交叉校验。

## [56] Linux tc and eBPF（FOSDEM 2016 slides）

- **是什么**：Daniel Borkmann 在 FOSDEM 2016（2016-01-31）的 16 页 slides 全文——比 netdev 1.1（id 54/55，两周后）更早的姊妹篇，主线相同（cBPF→eBPF→cls_bpf→tc 工作流），是 54 的"公开会议精简版"。
- **核心内容**：与 54 重叠约七成，独有增量有三块——①**seccomp BPF 完整 bpf_asm 实例**（Chrome sandbox 用的 syscall 白名单：读 seccomp_data.arch 校验 AUDIT_ARCH_X86_64、逐个 jeq __NR_* 白名单、ret SECCOMP_RET_KILL/ALLOW）——展示 BPF 早在 2012 就"不只是网络"了；②**BPF 在内核的使用全景清单**（Networking：socket filter/AF_PACKET fanout/SO_REUSEPORT/cls_bpf+act_bpf/team driver load balancing/netfilter xt_bpf/PTP classifier/PPP/ISDN；Tracing：kprobes 扩展；Sandboxing：seccomp）——这是 2016 年的 eBPF 应用版图快照；③tc frontend 补充"map fd 也可经 UDS 传给 agent"。
- **亮点或坑**：Take-aways 页金句："tc 的开发并没有深度冬眠"（回应当年"tc 已死"论）+ "eBPF 实现细节复杂，但写 eBPF 程序真的容易（也许在 tc 里最容易）"。seccomp 例子中 `jeq #0, good /* __NR_read */` 这类系统调用号直接可见，是理解 BPF 作通用 VM 的最佳直觉材料。
- **对人类学习者的价值**：高——16 页比 54 的 23 页更快过完主线，seccomp 实例和"内核 BPF 使用全景"两页是 54 没有的；适合作为第一份入门材料。
- **对 AI agent 的用法**：`web/pdf-txt/56.txt`，grep "seccomp" 取 syscall 过滤实例、grep "xt_bpf" / "SO_REUSEPORT" / "team driver" 取 eBPF 2016 应用版图；与 54/55 三份对照可区分"哪些点被反复强调"（da 模式、verdict 码、tc 命令流程）。

## [57] Linux Networking Explained（slideshare）

- **是什么**：Slideshare 上 Thomas Graf 的著名 slide deck "Linux Networking Explained"（65287988）的抓取残片——本地 md 仅 12 行，内容是 slideshare 的 "Client Challenge" 反爬拦截页（"JavaScript is disabled / A required part of this site couldn't load"），**无任何正文**。
- **核心内容**：本地不可得。据公开常识（未在本地验证）：该 deck 逐层讲解 Linux 收发包完整路径（NIC driver→NAPI→netif_receive_skb→IP/TCP→socket），配 eBPF 观测点，是"看懂 tc/eBPF 挂载点前的网络栈必修图解"。此条按抓取失败处理。
- **亮点或坑**：坑——slideshare 需要 JS 渲染，纯静态抓取必失败；上游 slides 地址 https://www.slideshare.net/slideshow/linux-networking-explained/65287988。内容同源的可替代材料：本批 id 54/56 中的 "cls bpf, Invocation points" 页（ingress/egress 挂载图）或 Graf 在 netdev 的同名 talk。
- **对人类学习者的价值**：本地为零；需联网看原 slides 才有价值。
- **对 AI agent 的用法**：`web/md/57.md` 可判定为空资源，无需 grep；如需该图解内容应改抓 graf_chaos 的个人站或 netdev proceedings 同名论文。

## [84] Enhancing the Linux kernel with BTF type information（BTF dedup 算法）

- **是什么**：Andrii Nakryiko 2018-11-14 发在 Facebook BPF blog 的经典文章，讲 BTF deduplication 算法——BTF 能塞进内核镜像的关键一步。文首注明已有更新版（nakryiko.com/posts/btf-dedup/），此版相当于存档。
- **核心内容**：①动机链：BPF 开发体验/可复用性（compile once, run everywhere 的远期愿景）需要类型元数据→DWARF 太通用冗长（内核 .debug_info 121.31MB + .debug_str 2.68MB）→BTF 借鉴 Sun CTF（Solaris 9 起的内核调试格式），极简紧凑；②BTF 模型：每个类型一个带 kind 的描述符（BTF_KIND_INT/ENUM/STRUCT/UNION/ARRAY/FWD/PTR/CONST/VOLATILE/RESTRICT/TYPEDEF），类型间用 type ID 引用（ID=在描述符数组中的位置，ID 0 恒为 void），存于 .BTF ELF section（描述符区 + \0 分隔字符串区）；③问题：DWARF 按 compilation unit 独立生成→pahole 1:1 转换后仍有 315 万个描述符（101.7MB），且同一类型在不同 CU 完整度不同（前向声明 FWD vs 完整定义）——BPF 用途需要"每个唯一类型一份且完整"；④算法五个 pass：字符串去重（比较降为 offset 比较）→非引用类型去重（INT/ENUM/STRUCT/UNION，用 canonical type + canonical index 签名哈希加速，struct 等价判定=DFS 遍历整个连通类型图+假设映射处理环与矛盾）→引用类型去重（PTR/CONST/VOLATILE/RESTRICT/TYPEDEF/ARRAY，等价性归结为被引用类型的 canonical ID）→类型压缩→type ID 修正；FWD→STRUCT 解析让"跨 CU 类型重建"一步等价映射即全局生效；⑤结果：Linux 4.11 上 124MB DWARF → 1.5MB BTF（描述符 101.7MB→0.97MB 压缩 104x，描述符数 314.8 万→2.29 万压缩 137x，耗时 2.6s）；消融实验证明不做类型合并只做去重只能到 12.71MB（9.5x）——**类型重建/合并才是紧凑性的大头**。
- **亮点或坑**：坑——文中 kind 清单是 2018 年快照（FUNC/FUNC_PROTO/BTF_KIND_VAR/DATASECT 等后来才加，见 id 83）；canonical index 哈希碰撞时候选列表会变长属预期；struct 等价判定方向性（candidate 图内类型必须映射到不同 canonical 类型，反向不要求）是正确性核心。
- **对人类学习者的价值**：极高——这是理解"BTF 为什么小、为什么可信"的一手材料，五 pass 流水线 + 双向矛盾检测的 DFS 是可独立学习的算法设计范本（处理带环图等价判定的教科书案例）。
- **对 AI agent 的用法**：`web/md/84.md`，grep "BTF_KIND" 取 kind 语义、grep "Pass #" 取五阶段结构、grep "104x" / "137x" 取压缩数据；图示文件在原站（btf-dedup-*.png）本地无图。

## [85] What is BTF (BPF Type Format)（cloudchirp 科普）

- **是什么**：Teodor J. Podobnik 2024-09-04 在 eBPFChirp/cloudchirp substack 的入门科普——面向生产级 eBPF 开发者的 BTF 三问：BTF 怎么支撑 CO-RE、内核没 BTF 怎么办、BTF-enabled tracepoint 怎么写。
- **核心内容**：①问题：eBPF 程序跨内核版本不可移植（5.3 编译可能 5.4 跑不起来），根因是内核头文件 struct 布局/字段名/offset 漂移；②CO-RE 三要素分工：BTF（描述内核与 eBPF 程序的类型信息）+ Clang（按 BTF 生成 CO-RE relocation 信息——记字段名/类型/所属 struct 而非硬编码 offset，即 field offset relocation）+ BPF Loader 如 libbpf（程序 BTF/CO-RE 信息与目标内核 BTF 匹配、解析类型、更新 offset）；③内核无 BTF 的两条出路：重编内核 CONFIG_DEBUG_INFO_BTF=y（生产机不现实）或随程序分发该内核的 BTF（BTFhub 项目）；④BTF 日常用例：bpftool 能把 map 内容 pretty-print 成变量名（hello.bss 的 counter）、能在程序 dump 里交叠源码行——没有 BTF 就只剩裸字节；⑤BTF-enabled tracepoint 实操：手写复制 /sys/kernel/tracing/events/.../format 的 struct（绑死编译时内核）→ 改用 `bpftool btf dump file /sys/kernel/btf/vmlinux format c > vmlinux.h` 生成运行内核全量类型头，直接用 `trace_event_raw_sched_process_exec` 这类真实类型；vmlinux.h 顶部的 `#define BPF_PSEUDO_MAP_...`/`__attribute__((preserve_access_index))` 行让 Clang 把 CO-RE 重定位嵌入 ELF；编译必须带 `-g`（`clang -O2 -g -target bpf`）。
- **亮点或坑**：坑——正文的技术展示全是 substack 图片（heic 格式截图，本地 md 只有图片占位符无代码文本），关键命令和 struct 定义都看不全，实质是"图载文章"；文章对 84 的引用（BTF 源自 Sun CTF 一段）一字不差搬了过去。
- **对人类学习者的价值**：中——作为 84（原理）与 83（规范）之间的"为什么我在乎"桥梁很称职：vmlinux.h 从哪来、-g 为何必需、bpftool pretty-print 依赖什么，一篇串起开发者最常碰的三个 BTF 触点；但代码细节需联网看原文配图。
- **对 AI agent 的用法**：`web/md/85.md`，grep "BTFhub" / "vmlinux.h" / "CONFIG_DEBUG_INFO_BTF" 取操作要点；代码内容不可 grep（在图里），需引用代码时以 83 的规范为准。

## [83] BPF Type Format (BTF)（kernel.org 官方规范）

- **是什么**：kernel.org 官方 BTF 规范文档（本快照版本号 7.4.0-rc1，Sphinx 渲染全文 1521 行），BTF 二进制格式/内核 API/ELF 接口的唯一权威参考，规范分两半：BTF kernel API（用户态与内核的契约，内核用前先校验）与 BTF ELF file format（ELF 与 libbpf 之间的用户态契约）。
- **核心内容**：①**编码基础**：数据 blob 以 `struct btf_header` 开头（magic=`0xeB9F`，大小端编码不同可用于端序探测；hdr_len 支持扩展）；字符串区首条必须是 null 串；type id 0 保留给 void，类型顺序编号自 1 起；公共头 `struct btf_type` = name_off + info（bit0-23 vlen / bit24-30 kind / bit31 kind_flag）+ size/type 共用体。②**22 种 kind**（1-19：INT/PTR/ARRAY/STRUCT/UNION/ENUM/FWD/TYPEDEF/VOLATILE/CONST/RESTRICT/FUNC/FUNC_PROTO/VAR/DATASEC/FLOAT/DECL_TAG/TYPE_TAG/ENUM64；**20-22 是最新增的 LOC_PARAM/LOC_PROTO/LOCSEC**——inline 站点参数位置描述，flags 组合表达 CONST/ADDR/REG/OFFSET/DEREF/SIGNED，为函数参数提供 DWARF 式 location description）；BTF 编的是 debug info 而非纯类型（FUNC 是 subprogram 不是类型）。③**内核 API**：五个 syscall 命令（BPF_BTF_LOAD 载 blob 得 btf_fd→BPF_MAP_CREATE 带 key/value type_id→BPF_PROG_LOAD 带 func_info/line_info→BPF_BTF_GET_FD_BY_ID/BPF_OBJ_GET_INFO_BY_FD 供 introspection），func_info[0].insn_off 必须为 0 且严格递增，line_info line_col 编码 = 行号<<10 | 列号。④**ELF 四个 section**：.BTF（同 blob 格式）、.BTF.ext（func_info/line_info/core_relo 三子区，**insn_off 在 kernel API 单位是 bpf_insn 条数、在 ELF API 是 section 内字节偏移**——经典坑）、.BTF_ids（BTF_ID_LIST/BTF_SET 宏，编译期 .zero 4 占位由 resolve_btfids 链接期解析）、.BTF.base（split BTF 韧性机制：模块 BTF 只编模块特有类型+蒸馏出最小基类型描述，模块加载时按新 base BTF 重定位，需 pahole v1.28+ 的 distilled_base）。⑤**使用与生成**：bpftool map pretty print（含 bitfield 精确解码）/prog dump 源码交叠/verifier log 行号定位三大用例；生成走 pahole（DWARF→BTF 转换器）或 LLVM 8.0+（bpf target 加 -g 直接出 .BTF/.BTF.ext），文档附完整 clang -S 汇编可逐字段对照。测试入口 tools/testing/selftests/bpf/prog_tests/btf.c。
- **亮点或坑**：与 84（2018 年 11 种 kind）对照即见 BTF 六年演进线：FUNC/VAR/DATASEC（BTF 全局变量与 map 定义）、FLOAT、DECL_TAG/TYPE_TAG（btf_decl_tag/btf_type_tag）、ENUM64、直到 LOC 系列；.BTF.base 一节是较新的模块 split BTF 重定位机制，多数二手教程尚未覆盖。
- **对人类学习者的价值**：极高——写 BTF 解析器、libbpf 工具或做 CO-RE 深度调试时这是规格源头；每个 kind 的 encoding requirement 罗列式写法可直接当 checklist 用。
- **对 AI agent 的用法**：`web/md/83.md`，grep "BTF_KIND" 取 22 种 kind 全表、grep "insn_off" 取双单位语义坑、grep "distilled_base" / ".BTF.base" 取 split BTF 重定位规格、grep "0xeb9f" 取魔数；结构体定义（btf_header/btf_type/btf_member/btf_array/btf_enum64/btf_loc 等）可直接引用为实现依据。
