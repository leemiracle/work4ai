# 第3章 Verifier：加载时验证器

> 本章导读：任何想认真写 eBPF 程序的人（而不是只改示例）都必读——verifier 拒绝是 eBPF 开发第一堵墙，读懂它能让你从"玄学排错"进入"机制排错"。前置：了解 eBPF 寄存器模型（R0-R10）与 bpf(2) 加载路径。读完你能：说出 verifier 两阶段各查什么、逐行读懂 verifier log 的寄存器状态语法、独立排查 invalid mem access / infinite loop / unbounded pointer math 三大类拒绝、并理解 PREVAIL 等形式化验证器与内核 verifier 的理论对照。

## 3.1 直觉层

**为什么需要验证？** 先看风险模型：eBPF 程序经 JIT 编译后与原生内核 C 代码"无法区分"（BPF Design Q&A 原话：JITed BPF programs are indistinguishable from native kernel C code，[id=11]）。这意味着如果没有验证环节，向内核加载一个 BPF 程序约等于加载一个内核模块——任意内核态代码执行权限。而内核模块需要 root、需要编译、有签名分发问题；eBPF 的产品愿景（Netflix/Cloudflare 的数据面、非特权 socket filter）要求**允许不可信来源的代码进内核**。矛盾只能靠一件事解决：**在执行前证明程序安全**。LLVM BPF 后端的创世 review 里 Alexei Starovoitov 把这条设计哲学写得很直白——"kernel rejects all programs that it cannot prove safe"（内核拒绝一切它无法证明安全的程序，[id=142]）。

**verifier 是什么？** David Miller 2017 年在 xdp-newbies 邮件列表的名句是最好的注脚："横在我们程序与毁灭深渊之间的唯一东西，就是 verifier"（The only thing sitting between our eBPF programs and a deep dark chasm of destruction is the eBPF verifier，[id=21]）。它是一个**加载时运行一次的静态分析器**（kernel/bpf/verifier.c，主入口 bpf_check），逐条指令模拟程序所有可能的执行路径，证明三件事：内存访问永不越界、寄存器/栈先初始化再读（否则内核数据会泄漏给用户态）、程序有限步内终止。证明通过才交给 JIT；证明通过之后**运行时零检查开销**——这是 eBPF 与 Java/WASM 沙箱的本质区别：后者靠运行时边界检查/GC，前者把安全成本一次性付在加载期（PREVAIL 论文对这一点的表述：解释器假定字节码已通过 verifier，从而避免昂贵的运行时安全检查，[id=166]）。

**它在整条 eBPF 栈里的位置**——verifier 坐在 bpf(2) 系统调用的 BPF_PROG_LOAD 命令路径上，是用户态与 JIT 之间的唯一关卡：

```mermaid
flowchart LR
    A[restricted C 源码] -->|clang -target bpf| B[ELF .o]
    B -->|libbpf 打开/重定位| C[bpf BPF_PROG_LOAD syscall]
    C --> D[verifier bpf_check]
    D -->|拒绝| E[返回 EACCES/EINVAL<br>+ verifier log]
    D -->|通过+改写| F[JIT 编译为本机码]
    F --> G[attach 到挂载点]
    G --> H[事件触发·零检查开销执行]
    subgraph verifier 内部
        D1[①map fd 重写] --> D2[②CFG/DAG 检查] --> D3[③全路径指令模拟+剪枝] --> D4[④ctx 偏移改写/⑤helper 地址改写]
    end
    D -.- verifier 内部
```

注意一个常被忽略的对称性：verifier **不是**防火墙式的只读审查者，它同时是**改写器**——map fd 换成内核 map 指针、`struct __sk_buff` 抽象字段偏移换成真实 sk_buff 偏移、helper 编号换成真实函数地址（详见 3.2）。所以"验证"和"指令变换"是同一趟完成的（[id=21] 五步流水线）。

## 3.2 原理层

### 3.2.1 验证目标：三条安全性质

PREVAIL 论文（PLDI'19，[id=166]）把 verifier 的职责形式化为三条性质，与内核实现一一对应：

1. **Memory safety**：程序只能访问它获准的内存区域（context / packet / stack / map value），任何偏移解引用前必须证明在界内；
2. **Information flow security**：非特权程序不能读取未初始化的寄存器或栈槽——这是防内核数据泄漏的防线，所以"读未初始化变量"在 eBPF 里不是 UB 而是硬拒绝；
3. **Termination**：所有执行路径有限步终止。

RFC 9669 的 Security Considerations 给了官方口径的同款清单：verifier 保证有限时间终止、安全内存交互、遵守 API 契约、无未定义行为，并评价这种模型"常能提供比一般软件与 OS 代码更强的安全保证"（[id=16]）。

### 3.2.2 第 0 步：map fd 伪指令重写

用户态用一条特殊的 64 位立即数加载指令携带 map fd：`ldimm64 rN, $FD` 且 src_reg 字段置 1（BPF_PSEUDO_MAP_FD——正常 ldimm64 的 src_reg 恒为 0）。verifier 拿 fd 查出内核 map 对象指针，把指令改写成 `ldimm64 rN, map_ptr`；验证通过后再把 src_reg 清零，使指令恢复为合法编码（[id=21] 步骤 1，对应源码 resolve_pseudo_ldimmq，见 digest 11 [id=269]）。这就是"程序里的 map 引用"从用户态句柄变成内核指针的准确机制——loader 与内核之间唯一的重定位通道也只有这一种（tc 时代文档明确"仅允许 map 相关重定位"是 loader 与 clang 的契约，[id=55]）。

### 3.2.3 第一遍：CFG/DAG 检查（check_cfg）

先对指令流建控制流图（跳转边连接基本块），强制四条规则（[id=21] 步骤 2 + [id=42] 转述 verifier.c 注释）：

- 程序不得超过 BPF_MAXINSNS=4096 条指令（这是 unprivileged 程序的对外可见上限，[id=11]）；
- **无后向边**——即禁止循环（有界循环支持是后来才加的，见 3.2.7）；
- **无不可达指令**（程序必须是一个函数，不是森林）；
- 无越界或畸形跳转。

DAG=有向无环图。Alan Maguire 对这段内核注释的转述（[id=42]）：第一遍是深度优先搜索，确认程序是 DAG，拒绝超大/含环/不可达/坏跳转四类。

### 3.2.4 第二遍：全路径指令模拟（do_check）

第二遍是 verifier 的主体：**从第一条指令出发，模拟所有可能的控制流路径**，逐条指令更新每个寄存器与每个栈槽的抽象状态（[id=42] 引 verifier.c 头注："bpf_check() is a static code analyzer that walks eBPF program instruction by instruction and updates register/stack state. All paths of conditional branches are analyzed until 'bpf_exit' insn"）。机制要点：

- **跳转栈穷举**：遇到条件跳转，把另一侧分支压栈，先走一侧；命中 BPF_EXIT 后弹栈走对侧，直到栈空（[id=21] 步骤 3）。本质是对执行路径空间的 DFS。
- **寄存器类型系统**：值进入寄存器即获得类型，类型决定该寄存器上什么操作合法。典型推导：`PTR_TO_PACKET + SCALAR_VALUE → PTR_TO_PACKET`（packet 指针加有界标量仍是 packet 指针）；而**指针+指针**直接非法——两个地址相加没有合法语义（[id=42]）。
- **栈槽生消**：写过的栈槽记录类型，读未写过的槽=拒绝（对应 3.2.1 的信息流性质）；寄存器 spill 到栈再 load 回来，关系必须保得住（PREVAIL 论文用 `*(u64*)(r10-8)=data_end` 的例子说明为什么栈内容必须像寄存器一样被精确跟踪，[id=166]）。
- **出口检查**：到达 exit 时 R0 必须持有已初始化的合法返回值（[id=42]）。
- **按程序类型裁剪**：每类 prog type 在 `struct bpf_verifier_ops` 里挂三个回调——`get_func_proto`（该类型允许哪些 helper，白名单 switch-case）、`is_valid_access`（context 字段能否访问）、`convert_ctx_access`（访问如何改写成真实偏移）（[id=39]，实现在 net/core/filter.c）。helper×map 兼容矩阵则由 verifier.c 的 check_map_func_compatibility 把关（[id=15] KNOWN ISSUES 节自述的真源之一）。

### 3.2.5 寄存器状态与 verifier log 语法

verifier 对每个寄存器维护**类型 + 取值区间**。Miller 的 level-1 dump 示例（[id=21]）：

```
0: R1=ctx R10=fp
1: R1=ctx R3=imm4,min_value=4,max_value=4,min_align=4 R10=fp
```

读法：行首数字=verifier 正在检查的指令序号；`R1=ctx`=非空 context 指针；`R10=fp`=只读帧指针；`R3=imm4,min_value=4,max_value=4` 表示 R3 是常量 4、值域 [4,4]、对齐 4。2019 年 Maguire 贴的真实报错（[id=42]）已经能看到现代语法全貌：

```
from 1545 to 1615: R0=inv0 R6=inv2 R7=ctx(id=0,off=0,imm=0)
  R8=inv(id=0,umin_value=28,umax_value=1048,var_off=(0x0; 0x7fc)) ...
1617: (0f) r1 += r2
math between pkt pointer and register with unbounded min value is not allowed
```

字段解码：`R8=inv(...)`=值未知的标量（inv=invalid/unknown scalar），`umin_value/umax_value`=无符号下/上界，`var_off=(0x0; 0x7fc)`=tnum（tristate number）：确定位全 0，低 10 位不确定——即 verifier 知道 R8 ∈ [28,1048] 且某些位自由。`from 1545 to 1615` 表示这条状态沿哪条边传播而来。这些区间/tnum 推理由 kernel/bpf/tnum.c 实现（digest 11 把 tnum.c 列为 verifier 协作者文件之一，[id=266]）。

### 3.2.6 剪枝与状态等价（state pruning）

路径穷举最贵，所以有剪枝：verifier 记录每个指令位置已见过的寄存器约束状态；当新路径到达某指令时，若**旧状态比新状态更严格**（旧路径已证明"比当前要查的更宽松的条件都安全"），则该路径无需重走（[id=21] 步骤 3 的原话转述 + [id=42] 的 states_equal() 说明）。PREVAIL 论文从理论侧给内核算法画像：路径枚举 + "启发式跳过那些安全性已被先前路径蕴含的后缀"，并指出这正是它不 scale 的根源（[id=166]）。剪枝有顺序敏感性——同样的代码把条件判断位置挪一挪，可验证性会变（cilium 社区被迫"把条件语句下压进控制流图"来通过验证，[id=166]），这是 3.4 坑位之一。

### 3.2.7 复杂度上限与循环简史

**限额演进**（带版本出处的硬数字）：

- 4.14 时代：第二遍分析总长上限 64k 条指令、待分析分支上限 1k（[id=42] 引 verifier.c 注释，Linux 4.14 口径）；
- 5.2 起：路径探索上限提升到 **100 万条指令**（bcc kernel-versions 矩阵标注 "1M insn limit 5.2"，[id=22]）；
- Design Q&A 官方口径：用户态唯一可见上限是 BPF_MAXINSNS=4096（unprivileged 上限）；内部还有"最大探索指令数（当前 100 万——意味着最大的合法程序是 100 万条 NOP）"、连续分支数、bpf-to-bpf 嵌套深度、每指令 verifier 状态数、map 数量等一系列内部限额，"足够复杂的程序都可能撞上"；以及一句务实结论：**判断程序能否被接受的唯一办法就是试着加载它**，且开发流程承诺新内核永远接受旧内核接受过的程序（[id=11]）。

**循环**：第一遍禁后向边=禁一切循环。旧时代的出路是编译期展开（`#pragma clang loop unroll(full)`，对变界循环失效）和 tail call 模拟跳转（[id=42]）。状态改变的时间线：5.3 引入 bounded loop（内核侧，[id=22]）；而学术界更早——PREVAIL 2019 年就是"首个支持带循环 eBPF 程序验证的工具"，靠 join/widening 算子收敛不动点而非枚举路径，实测内核 verifier 在双 strncmp 合成基准上多项式增长至 69 次迭代撞复杂度上限，PREVAIL 则线性扩展（[id=166]）。现代内核另有 bpf_loop helper 提供回调式循环（docs.ebpf.io Concepts 的 Loops 条目，[id=8]）。循环路径爆炸的乘法效应真实伤人：cilium 曾把 IPv6 扩展头解析循环的界人为压到 4（实际界只受包长限制）、又把 IPCACHE4 前缀数组缩小换通过率，付出性能代价（[id=166] 引 cilium commit 06efc2）。

### 3.2.8 验证通过后的改写

模拟通过不代表结束，verifier 还完成三项变换（[id=21] 步骤 4/5，[id=11]）：

- **context 访问改写**：`struct __sk_buff` 是内核 sk_buff 的固定偏移抽象（对 eBPF 的 ABI 永不变，内部结构随便改），verifier 把程序里对 skb->data 这类字段的访问改写成真实偏移；
- **helper 调用改写**：BPF_CALL 立即数里的 helper 编号换成真实函数地址；
- **zext 插入**：alu32 指令场景下，verifier 可给目标寄存器需要零扩展的指令显式插入一条 mov32 变体，让无硬件 zext 的架构的 JIT 后端不必自己清高位（[id=11]）。

### 3.2.9 PREVAIL：抽象解释对照

把内核 verifier 放进形式化方法坐标系，PREVAIL（Polynomial-Runtime EBPF Verifier using an Abstract Interpretation Layer，PLDI'19，[id=166]）是最好的参照系：

- **建模**：eBPF 程序只操纵少量独占内存区域（context/packet/stack + map 共享区），指针表示为 (region, offset) 二元组；stack 区域精确建模，packet 区域只需粗粒度边界（data/data_end 之间的访问忽略内容）。
- **数值域选型实验**：Interval 不够精确（无法表达 `r5+8 <= data_end` 这类二元关系，192 个基准里 64 个验证失败）；Octagon/Polyhedra 代价过高；**Zone domain（约束形如 X−Y≤C 的差界矩阵域）**在真实程序上与贵域同样精确——最终选型 zone-crab（稀疏表示+Split Normal Form，Crab 框架实现）。
- **收敛方式**：抽象解释用 join/widening 合并路径求不动点，天然避开路径枚举的 N^i 爆炸（N=循环体分支数，i=迭代数）；这也让它在 2019 年就支持循环验证（验证安全性，不验证终止性——termination 另有专门检查）。
- **实测数字**（kernel 4.19，i7-3.40GHz/32GB）：192 个真实程序（linux 86/OVS 18/suricata 5/cilium 24/cilium-tests 36/prototype-kernel 23）仅 1 个 false positive；单程序 ≤5.2s、平均 ~1500 指令/秒；有趣反转——更"强"的 poly-elina 反而在 21 个程序上失败而 zone-crab 成功（64 位系数表示不下的约束直接落 top）。
- **对内核 verifier 的批评**（2019 年口径）：四大痛点=误报多、不 scale、不支持循环、无形式化基础（verifier bug=可利用内核漏洞，当时已有 Jann Horn 报的多个此类 bug）；并实测找到 9 处"开发者被迫改代码绕 verifier"的 commit，PREVAIL 全部直接证明安全——其中一些后来以内核 verifier 修复收场。论文还点破内核算法的脆弱性根源：**靠语法模式匹配做特判**（例如当年认得 `data + X > data_end` 模式却认不得语义等价的 `data + X <= data_end`）。注意时代注脚：其中"不支持循环"已被 5.3 bounded loop 解决，读旧材料须校准。

工业延续：论文项目即 vbpf/ebpf-verifier 仓（现更名 prevail，eBPF for Windows 的验证器标准件），CLI `bin/prevail <elf> <section> <function>` 输出 PASS/FAIL，支持 `--termination` 终止性检查、`--failure-slice` 输出导致错误的最小指令切片、conformance groups 对齐 RFC 9669（[id=165]）。uBPF 则走了另一条路：不依赖外部 verifier，在用户态解释器里内置 Safe Execution Profile（寄存器来源追踪+集中式解引用检查），歧义指针算术直接拒绝（[id=160]）。

## 3.3 实践层

### 3.3.1 拿到 verifier log 的四条路

1. **libbpf 默认路径**（现代工作流）：`libbpf_set_print()` 注册回调后，`bpf_object__load` 失败会自动打印 verifier log——libbpf-bootstrap 的所有示例天然带这能力（本地仓 `repos/libbpf/libbpf-bootstrap/examples/c/minimal.c`，[id=145]）。
2. **bpftool 手动加载**：`bpftool prog load foo.o /sys/fs/bpf/foo`（可加 `-mcpu=v3` 等参数），拒绝时吐 log；bpftool 是内核树 tools/bpf/bpftool 的官方 CLI（[id=153]，本地读源走 GitHub 镜像或 libbpf-bootstrap 内嵌子模块）。
3. **bpf(2) 原生**：PROG_LOAD 的 attr 带 log_buf/log_buf_size/log_level 三字段。bpf(2) man page 明确建议：得到 EACCES（verifier 判 unsafe）后**用 log_level=1 重试**看日志（[id=13]）。等级语义：默认只在基本块边界 dump 寄存器状态；log_level=1 每条指令后都 dump；level 2 再加详细度（[id=21]）。
4. **selftests 通道**：内核 tools/testing/selftests/bpf/test_verifier.c 是 verifier 行为的黄金回归集（内核 Devel Q&A 的铁律：verifier 行为变更必须配 selftests 用例——"未被 test_verifier.c 跟踪的 verifier 行为视为可变"，[id=12]）；test_align.c 演示了用 bpf_verify_program() 捕获寄存器状态 dump 的方法（[id=21]）。

### 3.3.2 verifier log 逐行教学

排错时按固定四步读（素材来自 [id=21][id=42]）：

**第一步：定位末行错误句**。错误句是唯一判死刑的行，如 `math between pkt pointer and register with unbounded min value is not allowed`。

**第二步：解码出错指令行**。`1617: (0f) r1 += r2` 格式=`PC: (十六进制 opcode) 反汇编`。0f=ALU64 加法。这条在把 r2 加到 r1 上。

**第三步：解码其上方的状态行**。`from 1545 to 1615: R7=ctx(...) R8=inv(id=0,umin_value=28,umax_value=1048,var_off=(0x0; 0x7fc)) R10=fp0 fp-248=inv fp-232=map_value`：`R7=ctx` 是 context 指针；`R8=inv(...)` 是标量但有下界 28/上界 1048（tnum 部分见 3.2.5）；`fp-232=map_value` 表示栈上 -232 偏移的槽里存的是 map value 指针——栈槽状态也在 log 里。

**第四步：把 PC 映射回源码**。两条路：①`llvm-objdump -S -no-show-raw-insn prog.o`（编译加 -g）得到源码与 BPF 汇编交错列表，按 PC 对号（[id=42]）；②BTF line_info 让 bpftool prog dump / verifier log 直接关联源行（kernel BTF 文档三大用例之一就是"verifier log 行号定位"，[id=83]）。

对照解读上面那个错误：r1 来自 `*(u32 *)(r7+76)`（即 skb->data，packet 指针），r2 来自栈上变量；verifier 说"packet 指针加一个 min value 无下界的寄存器"不合法——若 r2 可能为负/巨大，指针可能移出包头之前。Maguire 的修复建议：确保加到 packet 指针上的值是**显式无符号类型**（如 `__u16`），并警惕移位/加/乘的回绕（[id=42]）。

### 3.3.3 第一个能过的包解析程序（边界检查范式）

Miller 的教学范式（[id=20]，"请直接照抄这套转型写法"）：

```c
SEC("my_program")
int my_main(struct __sk_buff *skb)
{
    void *data_end = (void *)(long)skb->data_end;   // 必须照抄的转型
    void *data     = (void *)(long)skb->data;
    struct ethhdr *eth = (struct ethhdr *)(data);

    if (eth + 1 > data_end)     // 解引用前必须先做范围检查
        return 0;

    if (eth->h_proto == bpf_htons(ETH_P_IP))   // 检查通过后整个 struct 可安全访问
        return 1;
    return 0;
}
```

语义：verifier 看到 eth 是 packet 指针、且你已证明 [eth, eth+1) 在有效范围内，此后通过 eth 访问 struct ethhdr 任意字段都合法。若删掉 if 检查，加载直接被拒——这就是最常见的 "invalid mem access" 拒绝的解药。两个变体注意：①SOCKET_FILTER 的返回值=接受字节数（0=丢包，非 0=截断接受；想全收就 `return skb->len`），同一个解析器换 prog type 要改返回值（[id=20]）；②调用 bpf_skb_pull_data/bpf_skb_store_bytes 等改包 helper 后，data/data_end 指针与既有检查**全部失效**，必须重新拉取重新检查（见 3.4）。

上手路径建议：`repos/libbpf/libbpf-bootstrap/` 跑通 minimal → `repos/lizrice/ebpf-beginners/`（教学仓）手工构造指令数组体会字节码层 → 想离线试 verifier 用 `repos/vbpf/ebpf-verifier`（`bin/prevail foo.o section func`，`--failure-slice` 直接给出致错最小切片，`--asm` 反汇编替代 llvm-objdump，[id=165]）→ 内核真源码走 GitHub 镜像 raw 通道读 kernel/bpf/verifier.c 及其拆分件（states.c/backtrack.c/liveness.c/log.c/tnum.c，[id=266][id=269]）。

## 3.4 深水区与坑

### 3.4.1 常见拒绝原因 top 列表（按新手撞墙频率）

| 报错句（缩略） | 根因 | 解法 |
|---|---|---|
| `invalid mem access 'inv'` / `R1 invalid mem access` | 解引用了值未知的标量或未经验证的指针；tracing 程序直接解引用 ctx->rdi 也会撞（[id=45]） | tracing 场景先 bpf_probe_read 拷到栈再访问；网络场景补 data/data_end 或 map value 边界检查 |
| `math between pkt pointer and register with unbounded min value` | packet 指针加了无下界（可能为负/巨大）的标量（[id=42]） | 加数用显式无符号类型；把该值的界先验出来（如先与常量比较） |
| `unreachable instruction` | 死代码；C 里罕见，常见于手写字节码或编译器生成的跳转表（switch jump table，[id=12][id=42]） | 编译加 `-fno-jump-tables`（bpf Devel Q&A 钦点，默认 target 会生成必败的 jump table） |
| `infinite loop detected` / `back-edge` | 5.3 前一切循环禁；5.3 后循环界无法静态证明也不行。概率上几乎必然终止的随机循环照样被拒——verifier 要**确定性**保证（[id=45]） | 常量界循环；变界用 bpf_loop；或 tail call 展开范式（[id=19]） |
| `invalid read from stack off -X size N`（未初始化读） | 读没写过的栈槽（[id=54][id=166]） | 先写后读；注意这是信息流安全防线不是语法洁癖 |
| `call to built-in function '__adddf3' is not supported` | 浮点运算——BPF 无 FPU，双精度运算链接器直接失败（[id=45]） | 定点化/整数运算，别用 float/double |
| `program too large`（超 BPF_MAXINSNS/复杂度上限） | 超 4096 条或撞 100 万探索上限（复杂程序多分支叠加，[id=11]） | 拆函数/减分支/上 tail call 复用栈绕过单程序限制（[id=13][id=19]） |
| EACCES（无细节） | verifier 判 unsafe 的总返回码 | bpf(2) 手册建议带 log_level=1 重试拿日志（[id=13]） |

经验之谈（Maguire，[id=42]）：verifier 报的错"通常是真 bug"——你花很久排查，最后多数是程序确实可能越界/读未初始化；少数是编译器优化骗过了你的直觉，这时必须看 llvm-objdump 而不是 C 源码。

### 3.4.2 改包 helper 的"验证失效"陷阱

`bpf_skb_store_bytes()`/`bpf_skb_pull_data()`/`bpf_skb_adjust_room()` 等改包 helper 会使 data/data_end 指针及先前所有边界检查**失效**——包可能被 realloc，旧指针不再可信（[id=42]）。内核侧有专门的 `bpf_helper_changes_pkt_data()` 函数列出哪些 helper 有此效果（[id=15]）。铁律：调完改包 helper，重新拉 data/data_end、重新做边界检查。另一个变体：非线性 skb（数据在 fragments 里）——VM 多层封装场景常撞，需 `bpf_skb_pull_data()` 把目标长度拉进线性区（[id=42]）。

### 3.4.3 循环与路径爆炸的乘法效应

N 个分支的循环体迭代 i 次→N^i 条路径。cilium 实录：IPv6 扩展头解析被迫把界压到 4；IPCACHE4 前缀数组被迫缩小、后随代码复杂化再次缩小，性能受损；多个循环顺序执行路径数相乘，开发者只能实验法找安全界（[id=166]）。当代内核有 bounded loop，但复杂度上限仍按探索指令数计——深度嵌套循环照样撞墙（[id=11]）。

### 3.4.4 版本代差与"verifier 行为可变"

- 报错文案与内部限额代际变化大：4.14 的 64k/1k 上限 vs 5.2+ 的 100 万；digest 11 明确警告读旧书会看到 verifier 还没拆分的文件布局（states/fixups/backtrack/liveness/const_fold/loops 现已是独立文件，[id=266]）。
- verifier 在持续"变聪明"：早期只认 pointer+常量，后来支持 pointer+有界寄存器；map lookup 的 key 从"必须指向栈"放宽到"可指向 map value"（[id=11]）。老内核上的拒绝在新内核可能通过——反向也有保证：官方承诺未来内核接受一切旧内核接受过的程序（[id=11]），但**没有**承诺拒绝过的永远拒绝。
- verifier 行为的契约是 selftests 而非文档：未进 test_verifier.c 的行为视为可变（[id=12]）。

### 3.4.5 安全边界上的历史事故与残留风险

- **CVE-2017-16995**：verifier 的 bug 曾允许构造程序绕过验证、直接读写内核内存（[id=45] 引）——印证 PREVAIL 的论点：verifier 无形式化基础时，"验证器接受不安全程序"即成内核提权漏洞（2019 年时已有多个此类 bug，[id=166]）。2025-2026 学界主线仍是 verifier 形式化与强化（Rocq 形式化抓出内核 bug、proof-carrying code、verifier fuzz，见论文清单 digest，[id=23]）。
- **推测执行不在威胁模型内**：RFC 9669 明说解释器字节码可能成为 Spectre 类侧信道 gadget，推荐只用 JIT（CONFIG_BPF_JIT_ALWAYS_ON 的动机）；配套 hardening 还有程序内存只读化与 constant blinding（常量盲化防 JIT spraying，2016 年 slides 里还标 "near future"，后来落地）（[id=16][id=45][id=54]）。
- **非特权面**：Linux 4.4 起非特权用户可加载受限 SOCKET_FILTER（4 个 helper 的白名单），生产机建议 `sysctl kernel.unprivileged_bpf_disabled=1` 关闭（[id=13]）。

### 3.4.6 PREVAIL 自己的盲区

对照读时注意 PREVAIL（2019 版）不支持：map-in-map、packet reallocation（改包后指针失效需全量 invalidate，约 4 个程序用到）、内部函数调用（bpf-to-bpf，只做过程内分析）（[id=166]）；默认假设包上限 64K（与内核 verifier 同款假设）；位运算只做保守过近似（`w &= x` 近似为 `assume(w < x)`）。工程版 vbpf/ebpf-verifier 后续补齐了很多（如 conformance groups、termination），引用旧论文结论前先查当前仓 README（[id=165]）。

## 3.5 与其他章的关系

前驱：本章默认你已读总览章（eBPF 安全卖点"verified 安全执行"的产品级表述，[id=6]）与指令集/程序加载章（R0-R10 寄存器模型、bpf(2) PROG_LOAD、ELF section 体系——本章 3.2.2 的 map fd 重写直接衔接那章的 ldimm64 编码细节）。verifier 的寄存器区间推导（tnum）与 BTF 章的 line_info 行号定位互为表里。后继：map 与 helper 章（本章只讲了 verifier 怎么裁剪它们的可用性，用法细节在后）；XDP/tc/追踪各程序类型章——每类程序撞 verifier 的具体姿势（网络类=packet 边界检查，tracing 类=probe_read 拷贝范式）将在各自章展开；用户态 eBPF 运行时章（uBPF/PREVAIL 的用户态验证/执行组合）承接收官。

## 3.6 语料索引

| id | 名称 | 本地路径 | 用了什么 |
|---|---|---|---|
| 21 | BPF Verifier Overview（Miller, xdp-newbies 2017） | web/md/21.md | 五步流水线/跳转栈/剪枝原理/log level 1 逐指令 dump 示例与语法/test_align.c 捕获法 |
| 20 | Contextually speaking...（Miller 2017） | web/md/20.md | context 三决定/边界检查范式代码/SOCK_FILTER 返回值语义/LD_ABS 历史地位 |
| 19 | bpf.h and you...（Miller 2017） | web/md/19.md | tail call 绕循环限制/PROG_ARRAY/GPL license 门控背景 |
| 42 | BPF Bytecode & Verifier（Maguire 六部曲之五, 2019） | web/md/42.md | 两阶段机制+4.14 限额 64k/1k/真实报错逐字段解码/llvm-objdump -S/改包 helper 失效/非线性 skb/"通常是真 bug" |
| 11 | BPF Design Q&A（kernel 7.4.0-rc1） | web/md/11.md | BPF_MAXINSNS=4096/100 万探索上限/内部限额清单/"唯一办法是试加载"/前向兼容承诺/verifier 变聪明史/zext 插入/栈上限 |
| 166 | PREVAIL 论文（PLDI'19 全文） | web/pdf-txt/166.txt | 三条安全性质/(region,offset) 建模/Zone 选型实验/192 程序实测数字/N^i 路径爆炸与 69 次迭代/cilium 循环界案例/语法模式匹配脆弱性/PREVAIL 盲区 |
| 165 | PREVAIL 仓（vbpf/ebpf-verifier） | repos/vbpf/ebpf-verifier | CLI 用法/--failure-slice/--termination/conformance groups |
| 160 | uBPF | repos/iovisor/ubpf | Safe Execution Profile 用户态替代路线 |
| 15 | bpf-helpers(7) | web/md/15.md | check_map_func_compatibility 真源/bpf_helper_changes_pkt_data 名单 |
| 13 | bpf(2) man page | web/md/13.md | EACCES+log_level=1 重试建议/map 尺寸用于加载期拒绝/unprivileged 面与 sysctl |
| 12 | BPF Devel Q&A | web/md/12.md | test_verifier.c 行为契约/-fno-jump-tables/-mcpu=probe |
| 22 | bcc kernel-versions | web/md/22.md | bounded loop 5.3 / 1M insn limit 5.2 / direct packet access 4.7 版本锚点 |
| 16 | RFC 9669 BPF ISA | web/md/16.md | verifier 安全保证官方表述/解释器侧信道与 JIT_ALWAYS_ON |
| 45 | eBPF from a Programmer's Perspective | web/md/45.md | 三大可复现拒绝案例（解引用/随机循环/浮点）/hardening/CVE-2017-16995 |
| 39 | Maguire 六部曲之二（helpers） | web/md/39.md | bpf_verifier_ops 三回调（get_func_proto/is_valid_access/convert_ctx_access） |
| 83 | BTF 规范 | web/md/83.md | verifier log 行号定位用例（line_info） |
| 8 | docs.ebpf.io | web/md/8.md | Concepts/Loops（bpf_loop）条目 |
| 266/269 | kernel/bpf 目录与 verifier.c（digest 11） | digests/11-内核源码入口.md | 源码入口/新式文件拆分（states/backtrack/liveness/tnum）/raw 通道 |
| 54 | tc classifier fully programmable slides | web/pdf-txt/54.txt | verifier 检查项清单（环形控制流/未初始化/死代码/类型）/constant blinding 时间线 |
| 55 | 同题论文版 | web/pdf-txt/55.txt | loader-clang 契约（仅 map 重定位）/常量界循环编译期展开 |
| 145 | libbpf-bootstrap | repos/libbpf/libbpf-bootstrap | 实践层上手仓 |

## 3.7 AI agent 用法

本章可当 verifier 排错与机制的检索工具，典型配方：

1. **"程序被拒，报错 X 是什么意思"** → 先 grep `docs/03-Verifier.md` 的 3.4.1 拒绝表（`grep -n "invalid mem access\|unbounded\|unreachable\|infinite loop" docs/03-Verifier.md`）→ 命中解法列；再深潜 `web/md/42.md`（grep 报错原文逐字段解码）与 `web/md/45.md`（grep `infinite loop detected`、`__adddf3` 拿可复现案例）。
2. **"verifier log 这行 R8=inv(umin_value=...) 什么意思"** → grep 本章 3.2.5 与 3.3.2 的语法节；一手对照 `web/md/21.md`（grep `min_value`、`R1=ctx` 拿 Miller 的 dump 原例）。
3. **"为什么循环/大程序过不了验证"** → 本章 3.2.7 复杂度节 + `web/pdf-txt/166.txt`（grep `N i paths`、`69 iterations`、`IPv6` 取路径爆炸实证与 cilium 案例）；版本判断 grep `web/md/22.md` 的 `bounded loop`、`5.2`。
4. **"verifier 会不会误杀/漏放"** → 本章 3.4.5/3.2.9 + `web/pdf-txt/166.txt`（grep `false positive`、`syntactic pattern matching`）；形式化验证需求转 `repos/vbpf/ebpf-verifier`（grep `failure_slice`、`termination`）。
5. **"内核 verifier 源码在哪/怎么读"** → digests/11 的路径表（grep `verifier` 拿 kernel/bpf/verifier.c 及拆分文件清单与 raw 通道）；行为契约问题 grep `web/md/12.md` 的 `test_verifier`。

