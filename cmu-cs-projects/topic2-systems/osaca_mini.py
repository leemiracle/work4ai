"""
OSACA 核心算法 mini 复现：throughput + Critical Path + LCD
==========================================================
配套文档：../../top-cs-projects/OSACA_INTEGRATION.md
姊妹代码：osaca_data.py（指令数据库）

本模块复现 OSACA（github.com/RRZE-HPC/OSACA）的三大核心算法，纯 Python：
  1. analyze_throughput  —— 端口压力分析（找瓶颈端口）
  2. find_critical_path  —— 关键路径（DAG 最长依赖链）
  3. find_lcd            —— Loop-Carried Dependency（跨迭代依赖）

对应 OSACA 的分析流水线（osaca/osaca.py::inspect）：
    parse → add_semantics → assign_optimal_throughput → KernelDG → Frontend

为教学化做了简化：
  - 不做完整汇编解析（用简化的 Instr dataclass 直接表示）
  - 不做 LP 最优端口分配（OSACA 用线性规划，这里用贪心）
  - 不考虑 μop fusion / store-to-load forwarding

但算法骨架与 OSACA 完全一致，能让你看清"OSACA 怎么算出 port pressure 和 CP"。

用法：
    python3 osaca_mini.py              # 跑 daxpy kernel 示例分析
    python3 osaca_mini.py --kernel triad   # 跑 triad kernel
    from osaca_mini import analyze_kernel, KERNELS

参考：OSACA 论文 https://arxiv.org/abs/1910.00214（PMBS19）
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple, Optional
import sys
import os

# 导入本地化的指令数据库
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from osaca_data import query, MICROARCH_PARAMS, InstructionEntry

SEP = "=" * 78
SUBSEP = "-" * 78


# ============================================================================
# 1. 简化的指令模型（对应 OSACA parser/InstructionForm）
# ============================================================================

@dataclass
class Instr:
    """简化指令（对应 OSACA 的 InstructionForm）。

    OSACA 真实流程是：汇编文本 → Parser → InstructionForm（含 operand 详情）
    → ArchSemantics.add_semantics 贴 throughput/latency/port_pressure。
    这里跳过 parser，直接手工构造。
    """
    line: int                    # 行号
    source: str                  # 原始汇编文本
    mnemonic: str                # 助记符（规范化后）
    reads: List[str]             # 读寄存器/内存位置
    writes: List[str]            # 写寄存器/内存位置
    latency: float = 0.0
    throughput: float = 0.0
    port_pressure: List[List] = field(default_factory=list)  # [[cyc, ports], ...]
    is_load: bool = False        # 是否含内存读
    is_store: bool = False       # 是否含内存写
    is_branch: bool = False

    def port_pressure_str(self) -> str:
        parts = []
        for cyc, ports in self.port_pressure:
            ps = ports if isinstance(ports, str) else ",".join(ports)
            parts.append(f"{cyc}×p{ps}")
        return " + ".join(parts) if parts else "-"


# ============================================================================
# 2. 预置 kernel（对应 OSACA examples/）
# ============================================================================

def _attach_semantics(instr: Instr, arch: str):
    """模拟 OSACA ArchSemantics.add_semantics：从数据库贴 latency/throughput/port_pressure。"""
    entry = query(instr.mnemonic, arch)
    if entry:
        instr.latency = entry.latency
        instr.throughput = entry.throughput
        instr.port_pressure = entry.port_pressure


def _build_kernel_daxpy(arch: str) -> List[Instr]:
    """daxpy: y = a*x + y（OSACA examples/daxpy/daxpy.s.csx.gcc.s 风格简化）。"""
    k = [
        Instr(1, "vmovupd (%rsi), %ymm0",      "VMOVUPD", reads=["mem"],   writes=["ymm0"], is_load=True),
        Instr(2, "vmulpd  %ymm1, %ymm0, %ymm0","VMULPD",  reads=["ymm0","ymm1"], writes=["ymm0"]),
        Instr(3, "vaddpd  %ymm0, (%rdx), %ymm0","VADDPD", reads=["ymm0","mem"], writes=["ymm0"], is_load=True),
        Instr(4, "vmovupd %ymm0, (%rdx)",      "VMOVUPD", reads=["ymm0"], writes=["mem"],   is_store=True),
        Instr(5, "addq    $32, %rsi",          "ADD",     reads=["rsi"],   writes=["rsi"]),
        Instr(6, "addq    $32, %rdx",          "ADD",     reads=["rdx"],   writes=["rdx"]),
        Instr(7, "cmpq    %rcx, %rsi",         "CMP",     reads=["rcx","rsi"], writes=[]),
        Instr(8, "jb      .L1",                "JCC",     reads=[],        writes=[], is_branch=True),
    ]
    for ins in k:
        _attach_semantics(ins, arch)
        # VMOVUPD 根据是 load 还是 store 贴不同语义
        if ins.mnemonic == "VMOVUPD" and ins.latency == 0:
            entry = query("VMOVUPD", arch, "ymm,mem" if ins.is_load else "mem,ymm")
            if entry:
                ins.latency = entry.latency
                ins.throughput = entry.throughput
                ins.port_pressure = entry.port_pressure
    return k


def _build_kernel_triad(arch: str) -> List[Instr]:
    """STREAM triad: a[i] = b[i] + c[i]*d[i]（OSACA examples/triad）。"""
    k = [
        Instr(1, "vmovupd (%rbx), %ymm0",       "VMOVUPD", reads=["mem"], writes=["ymm0"], is_load=True),  # b
        Instr(2, "vmovupd (%rcx), %ymm1",       "VMOVUPD", reads=["mem"], writes=["ymm1"], is_load=True),  # c
        Instr(3, "vmulpd  %ymm1, %ymm2, %ymm1", "VMULPD",  reads=["ymm1","ymm2"], writes=["ymm1"]),  # c*d
        Instr(4, "vaddpd  %ymm1, %ymm0, %ymm0", "VADDPD",  reads=["ymm0","ymm1"], writes=["ymm0"]),  # b+c*d
        Instr(5, "vmovupd %ymm0, (%rax)",       "VMOVUPD", reads=["ymm0"], writes=["mem"], is_store=True),  # a
        Instr(6, "addq    $32, %rax",           "ADD",     reads=["rax"], writes=["rax"]),
        Instr(7, "addq    $32, %rbx",           "ADD",     reads=["rbx"], writes=["rbx"]),
        Instr(8, "addq    $32, %rcx",           "ADD",     reads=["rcx"], writes=["rcx"]),
        Instr(9, "cmpq    %rdx, %rax",          "CMP",     reads=["rdx","rax"], writes=[]),
        Instr(10,"jb      .L1",                 "JCC",     reads=[], writes=[], is_branch=True),
    ]
    for ins in k:
        _attach_semantics(ins, arch)
        if ins.mnemonic == "VMOVUPD" and ins.latency == 0:
            entry = query("VMOVUPD", arch, "ymm,mem" if ins.is_load else "mem,ymm")
            if entry:
                ins.latency = entry.latency
                ins.throughput = entry.throughput
                ins.port_pressure = entry.port_pressure
    return k


KERNELS = {
    "daxpy": _build_kernel_daxpy,
    "triad": _build_kernel_triad,
}


# ============================================================================
# 3. 算法 1：Throughput 端口压力分析（对应 OSACA assign_optimal_throughput）
# ============================================================================

def analyze_throughput(kernel: List[Instr], arch: str) -> Dict:
    """计算 kernel 各端口的总压力，识别瓶颈端口。

    OSACA 用线性规划做最优分配；这里用贪心：每条指令的 port_pressure 假设均匀分摊。
    返回 {port: total_cycles, '_bottleneck': (port, cycles), '_total_throughput': cyc}
    """
    info = MICROARCH_PARAMS.get(arch)
    if not info:
        raise ValueError(f"未知架构：{arch}")

    # 初始化所有端口
    port_total: Dict[str, float] = {p: 0.0 for p in info.ports}

    for ins in kernel:
        for cyc, ports in ins.port_pressure:
            # ports 可能是 str（如 '01'）或 list（如 ['2D','3D']）
            port_list = list(ports) if isinstance(ports, str) else ports
            # 均匀分摊到可用端口（贪心；OSACA 用 LP 最优分配）
            if port_list:
                share = cyc / len(port_list)
                for p in port_list:
                    if p in port_total:
                        port_total[p] += share

    # 找瓶颈
    bottleneck_port = max(port_total, key=port_total.get) if port_total else None
    bottleneck_cyc = port_total.get(bottleneck_port, 0) if bottleneck_port else 0
    total_throughput = max(port_total.values()) if port_total else 0

    return {
        "port_total": port_total,
        "bottleneck_port": bottleneck_port,
        "bottleneck_cyc": bottleneck_cyc,
        "total_throughput_cyc": total_throughput,
        "arch": arch,
    }


# ============================================================================
# 4. 算法 2：Critical Path（对应 OSACA KernelDG 的 CP 检测）
# ============================================================================

def find_critical_path(kernel: List[Instr]) -> Dict:
    """关键路径：基于寄存器 RAW 依赖构建 DAG，找最长延迟路径。

    OSACA 用 KernelDG 类（依赖 networkx）构建有向图 + 拓扑排序 + 最长路径。
    这里实现 Kahn 算法变种：按行号顺序，对每条指令，CP = max(前驱 CP) + 自身 latency。
    """
    # 构建 RAW（Read-After-Write）依赖：A 写 R，B 读 R → A → B
    # 简化：只考虑寄存器依赖（不考虑内存别名、不考虑 store-load forwarding）
    last_writer: Dict[str, int] = {}  # reg -> line of last writer

    # 入边：line -> [(pred_line, reg)]
    edges: Dict[int, List[Tuple[int, str]]] = {ins.line: [] for ins in kernel}

    for ins in kernel:
        # 读依赖：每个 read reg 的最近 writer 是前驱
        for r in ins.reads:
            if r in last_writer and last_writer[r] != ins.line:
                edges[ins.line].append((last_writer[r], r))
        # 写更新
        for w in ins.writes:
            last_writer[w] = ins.line

    # DP 求最长路径：cp[line] = max(cp[pred] + pred.latency)
    cp: Dict[int, float] = {}
    cp_source: Dict[int, Optional[int]] = {ins.line: None for ins in kernel}

    for ins in kernel:  # 按行号顺序（假设拓扑序）
        max_pred_cp = 0.0
        best_pred = None
        for pred_line, _reg in edges[ins.line]:
            if cp.get(pred_line, 0) + kernel[pred_line-1].latency > max_pred_cp:
                max_pred_cp = cp.get(pred_line, 0) + kernel[pred_line-1].latency
                best_pred = pred_line
        cp[ins.line] = max_pred_cp
        cp_source[ins.line] = best_pred

    # 找全局最长 CP
    end_line = max(cp, key=cp.get) if cp else None
    cp_length = cp.get(end_line, 0) + (kernel[end_line-1].latency if end_line else 0)

    # 回溯路径
    path = []
    cur = end_line
    while cur is not None:
        path.append(cur)
        cur = cp_source.get(cur)
    path.reverse()

    return {
        "cp_length": cp_length,
        "cp_path": path,
        "cp_edges": edges,
        "end_line": end_line,
    }


# ============================================================================
# 5. 算法 3：Loop-Carried Dependency（对应 OSACA KernelDG 的 LCD）
# ============================================================================

def find_lcd(kernel: List[Instr]) -> List[List[int]]:
    """检测 Loop-Carried Dependency：跨迭代依赖。

    LCD 定义：指令 A 在迭代 N 写寄存器 R，指令 B 在迭代 N+1 读 R。
    在静态汇编中，等价于：A 在循环体内写 R，且 A 的写没有被同迭代内的其他指令覆盖，
    然后 B 在循环末尾或下一迭代开头读 R。

    简化检测：找所有"在循环内被写、且在循环内被读"的寄存器。
    每个 LCD = (写指令行, 读指令行, 寄存器) 链。
    """
    # 找所有"跨迭代可能传递"的寄存器：在循环内既被写又被读
    writes_in_loop: Dict[str, List[int]] = {}  # reg -> [writer lines]
    reads_in_loop: Dict[str, List[int]] = {}

    for ins in kernel:
        if ins.is_branch:
            continue
        for w in ins.writes:
            writes_in_loop.setdefault(w, []).append(ins.line)
        for r in ins.reads:
            if r != "mem":  # 不考虑内存别名
                reads_in_loop.setdefault(r, []).append(ins.line)

    # LCD 候选：寄存器同时在 writes 和 reads 里
    lcd_regs = set(writes_in_loop.keys()) & set(reads_in_loop.keys()) - {"mem"}

    lcds = []
    for reg in lcd_regs:
        writers = writes_in_loop[reg]
        readers = reads_in_loop[reg]
        # 每个 reader 至少有一个 writer 前驱（同迭代或跨迭代）
        # 跨迭代 LCD：writer 行号 > reader 行号（即 writer 在 reader 之后，下一迭代才读到）
        for r_line in readers:
            for w_line in writers:
                if w_line > r_line:  # 跨迭代依赖
                    lcds.append([w_line, r_line, reg])

    return lcds


# ============================================================================
# 6. Frontend：OSACA 风格报告（对应 OSACA frontend.py::full_analysis）
# ============================================================================

def full_analysis(kernel: List[Instr], arch: str, name: str = "kernel") -> str:
    """生成 OSACA 风格的完整分析报告。"""
    info = MICROARCH_PARAMS.get(arch)
    thr = analyze_throughput(kernel, arch)
    cp = find_critical_path(kernel)
    lcds = find_lcd(kernel)

    lines = []
    lines.append(SEP)
    lines.append(f"OSACA-mini Analysis Report")
    lines.append(f"  Kernel:    {name}")
    lines.append(f"  Arch:      {info.name if info else arch} ({arch})")
    lines.append(f"  Ports:     {','.join(info.ports[:12])}{'...' if len(info.ports)>12 else ''}")
    lines.append(SEP)

    # Port pressure 表（OSACA 招牌输出）
    lines.append("")
    lines.append("▶ Port pressure (per iteration):")
    lines.append(f"  {SUBSEP}")
    header = f"  {'line':>4}  {'instruction':<40} {'CP':>5} {'port_pressure':<30}"
    lines.append(header)
    lines.append(f"  {SUBSEP}")
    for ins in kernel:
        in_cp = "★" if ins.line in cp["cp_path"] else " "
        lines.append(f"  {ins.line:>4}{in_cp} {ins.source:<40} {ins.latency:>4.0f}c {ins.port_pressure_str():<30}")

    # Throughput 总结
    lines.append("")
    lines.append(f"  {SUBSEP}")
    lines.append(f"  Total throughput: {thr['total_throughput_cyc']:.2f} cyc/iter")
    lines.append(f"  Bottleneck port:  port {thr['bottleneck_port']} ({thr['bottleneck_cyc']:.2f} cyc)")
    port_summary = ", ".join(f"p{p}={v:.2f}" for p, v in sorted(thr['port_total'].items()) if v > 0.01)
    lines.append(f"  Port pressure:    {port_summary}")

    # Critical Path
    lines.append("")
    lines.append("▶ Critical Path (longest dependency chain):")
    lines.append(f"  {SUBSEP}")
    lines.append(f"  CP length: {cp['cp_length']:.0f} cyc")
    lines.append(f"  CP path:   {' → '.join(f'L{l}' for l in cp['cp_path'])}")
    if cp["cp_path"]:
        path_instrs = [kernel[l-1].source for l in cp["cp_path"]]
        lines.append(f"  CP instructions:")
        for ins_src in path_instrs:
            lines.append(f"    {ins_src}")

    # LCD
    lines.append("")
    lines.append("▶ Loop-Carried Dependencies:")
    lines.append(f"  {SUBSEP}")
    if lcds:
        for w_line, r_line, reg in lcds:
            w_ins = kernel[w_line-1].source.strip()
            r_ins = kernel[r_line-1].source.strip()
            w_lat = kernel[w_line-1].latency
            lines.append(f"  L{w_line} → L{r_line}  via %{reg}   ({w_lat:.0f}cyc)")
            lines.append(f"     write: {w_ins}")
            lines.append(f"     read:  {r_ins}")
    else:
        lines.append("  (none)")

    # 性能诊断（OSACA 招牌洞察）
    lines.append("")
    lines.append("▶ Performance Verdict:")
    lines.append(f"  {SUBSEP}")
    cp_bound = cp["cp_length"]
    thr_bound = thr["total_throughput_cyc"]
    bound = max(cp_bound, thr_bound)
    if cp_bound > thr_bound * 1.2:
        lines.append(f"  ⚠️  CP-bound ({cp_bound:.0f} > thr {thr_bound:.0f}): 依赖链太长，用多 accumulator 打破（参 Agner 原则 3）")
    elif thr_bound > cp_bound * 1.2:
        lines.append(f"  ⚠️  Throughput-bound ({thr_bound:.0f} > CP {cp_bound:.0f}): 端口饱和，换指令（如 div→mul）或向量化")
    else:
        lines.append(f"  ✅ 平衡 (CP {cp_bound:.0f} ≈ thr {thr_bound:.0f})")
    if lcds:
        lines.append(f"  ⚠️  {len(lcds)} LCD(s) 限制 ILP，考虑循环展开/流水线化")

    lines.append("")
    lines.append(f"  估算 kernel 周期/迭代 ≈ {bound:.0f} cyc（max of CP 和 throughput）")

    return "\n".join(lines)


# ============================================================================
# 主入口
# ============================================================================

def main():
    print("╔" + "═" * 76 + "╗")
    print("║" + " OSACA-mini · 核心算法复现（throughput + CP + LCD）".center(76) + "║")
    print("║" + " 来源：github.com/RRZE-HPC/OSACA + 论文 arxiv:1910.00214 ".center(76) + "║")
    print("╚" + "═" * 76 + "╝")

    args = sys.argv[1:]
    kernel_name = "daxpy"
    arch = "skx"

    # 简单参数解析
    for i, a in enumerate(args):
        if a == "--kernel" and i+1 < len(args):
            kernel_name = args[i+1]
        elif a == "--arch" and i+1 < len(args):
            arch = args[i+1]

    if kernel_name not in KERNELS:
        print(f"[!] 未知 kernel：{kernel_name}（可选：{', '.join(KERNELS.keys())}）")
        return

    print(f"\n▶ 分析 kernel={kernel_name}, arch={arch}\n")

    kernel = KERNELS[kernel_name](arch)
    print(full_analysis(kernel, arch, name=kernel_name))

    # 跨架构对比（同一 kernel）
    print(f"\n{SEP}")
    print(f"▶ 同一 kernel ({kernel_name}) 跨架构瓶颈对比")
    print(SEP)
    print(f"  {'架构':<8} {'CP length':>10} {'Throughput':>12} {'瓶颈端口':>10} {'bound':>8} {'诊断':<30}")
    print(f"  {SUBSEP}")
    for a in ["skx", "zen3", "v2", "m1"]:
        try:
            k = KERNELS[kernel_name](a)
            t = analyze_throughput(k, a)
            c = find_critical_path(k)
            bound = max(c["cp_length"], t["total_throughput_cyc"])
            if c["cp_length"] > t["total_throughput_cyc"] * 1.2:
                diag = "CP-bound（依赖链）"
            elif t["total_throughput_cyc"] > c["cp_length"] * 1.2:
                diag = f"thr-bound（port {t['bottleneck_port']}）"
            else:
                diag = "平衡"
            print(f"  {a:<8} {c['cp_length']:>8.0f}cyc {t['total_throughput_cyc']:>10.2f}cyc {t['bottleneck_port']:>10} {bound:>6.0f}cyc {diag:<30}")
        except Exception as e:
            print(f"  {a:<8} [!] {e}")

    print(f"\n💡 关键洞察：")
    print(f"   • OSACA 用 max(CP, throughput) 预测 kernel 周期数——这是它的核心模型")
    print(f"   • CP-bound 时优化依赖链；throughput-bound 时换指令或向量化")
    print(f"   • 同一 kernel 在不同架构的瓶颈可能完全不同（v2 端口多，skx ROB 大）")
    print(f"\n📚 完整 OSACA：pip install osaca 或 godbolt.org（选 Analysis + OSACA）")
    print(f"📖 内部模型：top-cs-projects/OSACA_INTEGRATION.md")


if __name__ == "__main__":
    main()
