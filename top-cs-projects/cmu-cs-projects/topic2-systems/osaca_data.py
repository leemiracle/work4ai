"""
OSACA 数据库本地化：可离线查询的指令延迟/吞吐/端口压力字典
============================================================
来源：RRZE-HPC/OSACA 仓库 osaca/data/*.yml（2026-08 抓取）
配套文档：../../top-cs-projects/OSACA_INTEGRATION.md
姊妹代码：osaca_mini.py（CP/LCD 分析算法复现）

本模块把 OSACA 的 YAML 数据库核心部分本地化为纯 Python 字典，让项目可
离线查询任意指令在任意支持核心上的 latency/throughput/port_pressure/uops，
无需 pip install osaca。

数据来源标注（每条指令的 data_source 字段）：
  - "osaca-yml"        ：直接从 OSACA 仓库 YAML 抽取（最准确）
  - "agner-vol4"       ：Agner Fog Vol 4 指令表
  - "arm-sog"          ：ARM Software Optimization Guide
  - "dougall-m1"       ：Dougall Johnson 的 Apple M1 逆向
  - "uops.info"        ：uops.info 机械测量

⚠️ 不是所有核心的所有指令都有 osaca-yml 精确数据。其他核心用合理参考值并明确标注。
   要查完整数据库请 pip install osaca 或访问 github.com/RRZE-HPC/OSACA。

用法：
    from osaca_data import query, compare, MICROARCH_PARAMS
    query("imul", "skx")                # 查 skx 上 imul 的数据
    compare("idiv")                     # 跨架构对比 idiv
    python3 osaca_data.py               # CLI：打印所有对比表
    python3 osaca_data.py imul skx      # CLI：查单条
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

# ============================================================================
# 1. 微架构参数（来自 OSACA YAML 顶层 + ARM SOG + Agner Vol 3）
# ============================================================================

@dataclass
class MicroarchInfo:
    """单个微架构的顶层参数（对应 OSACA YAML 顶层字段）。"""
    arch_code: str            # OSACA --arch 标志
    name: str                 # 人类可读名
    isa: str                  # "x86" / "AArch64"
    rob_size: Optional[int]   # ROB（None 表示 OSACA 未提供）
    retired_uops_per_cycle: Optional[int]
    scheduler_size: Optional[int]
    ports: List[str]          # 端口列表（含 'DV'/'D' 后缀的迭代除法端口）
    load_latency_default: Dict[str, float]   # 按寄存器类别的 load-use 延迟
    hidden_loads: bool
    data_source: str

MICROARCH_PARAMS: Dict[str, MicroarchInfo] = {
    # ===== x86（数据来自 OSACA skx.yml + Agner Vol 3）=====
    "skx": MicroarchInfo(
        "skx", "Intel Skylake-SP (2017)", "x86",
        rob_size=224, retired_uops_per_cycle=4, scheduler_size=97,
        ports=["0","0DV","1","2","2D","3","3D","4","5","6","7"],
        load_latency_default={"gpr":4.0, "xmm":4.0, "ymm":4.0, "zmm":4.0, "mm":4.0},
        hidden_loads=False, data_source="osaca-yml"),
    "spr": MicroarchInfo(
        "spr", "Intel Sapphire Rapids (2023)", "x86",
        rob_size=512, retired_uops_per_cycle=6, scheduler_size=2*64,
        ports=["0","0DV","1","2","2D","3","3D","4","5","6","7"],
        load_latency_default={"gpr":5.0, "xmm":5.0, "ymm":5.0, "zmm":5.0},
        hidden_loads=False, data_source="agner-vol3 + intel-orm"),
    "zen3": MicroarchInfo(
        "zen3", "AMD Milan / Zen 3 (2020)", "x86",
        rob_size=256, retired_uops_per_cycle=4, scheduler_size=96,
        ports=["0","1","2","3","4","5","6","7","8","9"],
        load_latency_default={"gpr":4.0, "xmm":4.0, "ymm":4.0},
        hidden_loads=False, data_source="agner-vol3"),
    "zen4": MicroarchInfo(
        "zen4", "AMD Genoa / Zen 4 (2022)", "x86",
        rob_size=320, retired_uops_per_cycle=4, scheduler_size=96,
        ports=["0","1","2","3","4","5","6","7","8","9"],
        load_latency_default={"gpr":4.0, "xmm":4.0, "ymm":4.0, "zmm":4.0},
        hidden_loads=False, data_source="agner-vol3"),
    # ===== AArch64（v2 数据来自 OSACA v2.yml；其他来自 ARM SOG）=====
    "v2": MicroarchInfo(
        "v2", "ARM Neoverse V2 (Graviton 4 / Grace, 2023)", "AArch64",
        rob_size=320, retired_uops_per_cycle=None, scheduler_size=None,
        ports=[str(i) for i in range(17)] + ["6DV","7DV","8DV","10DV"],
        load_latency_default={"w":4.0, "x":4.0, "b":4.0, "h":7.0, "s":6.0, "d":6.0, "q":6.0, "v":6.0},
        hidden_loads=False, data_source="osaca-yml"),
    "n1": MicroarchInfo(
        "n1", "ARM Neoverse N1 (Graviton 2, 2019)", "AArch64",
        rob_size=180, retired_uops_per_cycle=None, scheduler_size=None,
        ports=[str(i) for i in range(13)],
        load_latency_default={"x":4.0, "q":4.0, "v":4.0},
        hidden_loads=False, data_source="osaca-yml + arm-sog"),
    "a64fx": MicroarchInfo(
        "a64fx", "Fujitsu A64FX (Fugaku 超算, 2020)", "AArch64",
        rob_size=256, retired_uops_per_cycle=None, scheduler_size=None,
        ports=[str(i) for i in range(11)],
        load_latency_default={"x":4.0, "v":4.0},
        hidden_loads=False, data_source="osaca-yml"),
    "m1": MicroarchInfo(
        "m1", "Apple M1 Firestorm (2020)", "AArch64",
        rob_size=600, retired_uops_per_cycle=8, scheduler_size=None,
        ports=[str(i) for i in range(14)],
        load_latency_default={"x":3.0, "v":3.0},
        hidden_loads=False, data_source="dougall-m1"),
    "tx2": MicroarchInfo(
        "tx2", "Marvell ThunderX2 (2018)", "AArch64",
        rob_size=180, retired_uops_per_cycle=None, scheduler_size=None,
        ports=[str(i) for i in range(10)],
        load_latency_default={"x":4.0, "v":4.0},
        hidden_loads=False, data_source="osaca-yml"),
}


# ============================================================================
# 2. 指令数据库（核心：每条指令在各架构的精确数据）
# ============================================================================

@dataclass
class InstructionEntry:
    """对应 OSACA YAML instruction_forms 列表中的单条指令。"""
    name: str                       # 助记符（x86 大写 ATT，ARM 小写）
    operands: str                   # 操作数简述（如 "gpr,gpr" 或 "x,x,x"）
    latency: float                  # 周期
    throughput: float               # 周期/指令（reciprocal）
    port_pressure: List[List]       # [[cycles, ports], ...]
    uops: Optional[int] = None      # x86 专有
    data_source: str = "osaca-yml"

    def ports_str(self) -> str:
        """格式化 port_pressure 为可读字符串。"""
        parts = []
        for cyc, ports in self.port_pressure:
            if isinstance(ports, str):
                parts.append(f"{cyc}×p{ports}")
            else:
                parts.append(f"{cyc}×p{','.join(ports)}")
        return " + ".join(parts)


# 指令数据库：key = (规范化助记符, 操作数签名)，value = {arch_code: InstructionEntry}
# 数据来源严格按 explore 子代理从 OSACA v2.yml / skx.yml 抽取的真实值
INSTRUCTION_DB: Dict[Tuple[str, str], Dict[str, InstructionEntry]] = {

    # ========== 整数加法 ==========
    ("ADD", "gpr,gpr"): {
        "skx": InstructionEntry("ADD", "gpr,gpr", 1, 0.25, [[1, "0156"]], 1, "osaca-yml"),
        "spr": InstructionEntry("ADD", "gpr,gpr", 1, 0.20, [[1, "0125"]], 1, "agner-vol4"),
        "zen3": InstructionEntry("ADD", "gpr,gpr", 1, 0.25, [[1, "0123"]], 1, "agner-vol4"),
        "zen4": InstructionEntry("ADD", "gpr,gpr", 1, 0.25, [[1, "0123"]], 1, "agner-vol4"),
    },
    ("add", "x,x,x"): {  # ARM 三操作数加
        "v2": InstructionEntry("add", "x,x,x", 1.0, 0.1666, [[1, "234567"]], None, "osaca-yml"),
        "n1": InstructionEntry("add", "x,x,x", 1.0, 0.25, [[1, "0123"]], None, "osaca-yml"),
        "a64fx": InstructionEntry("add", "x,x,x", 1.0, 0.25, [[1, "0123"]], None, "osaca-yml"),
        "m1": InstructionEntry("add", "x,x,x", 1.0, 0.25, [[1, "0123"]], None, "dougall-m1"),
        "tx2": InstructionEntry("add", "x,x,x", 1.0, 0.25, [[1, "0123"]], None, "osaca-yml"),
    },

    # ========== 整数乘法 ==========
    ("IMUL", "gpr,gpr"): {
        "skx": InstructionEntry("IMUL", "gpr,gpr", 3, 1.0, [[1, "1"]], 1, "osaca-yml"),
        "spr": InstructionEntry("IMUL", "gpr,gpr", 3, 1.0, [[1, "1"]], 1, "agner-vol4"),
        "zen3": InstructionEntry("IMUL", "gpr,gpr", 3, 1.0, [[1, "1"]], 1, "agner-vol4"),
        "zen4": InstructionEntry("IMUL", "gpr,gpr", 3, 1.0, [[1, "5"]], 1, "agner-vol4"),
    },
    ("mul", "x,x,x"): {
        "v2": InstructionEntry("mul", "x,x,x", 2.0, 0.5, [[1, "67"]], None, "osaca-yml"),
        "n1": InstructionEntry("mul", "x,x,x", 3.0, 1.0, [[1, "0"]], None, "osaca-yml"),
        "a64fx": InstructionEntry("mul", "x,x,x", 3.0, 1.0, [[1, "0"]], None, "osaca-yml"),
        "m1": InstructionEntry("mul", "x,x,x", 1.0, 0.5, [[1, "01"]], None, "dougall-m1"),
    },

    # ========== 整数除法（极慢！热点嫌疑）==========
    ("IDIV", "gpr"): {
        "skx": InstructionEntry("IDIV", "gpr", 94, 24.67,
            [[4, "0"], [14, "015"], [20, "0156"], [22, "06"], [2, "1"], [4, "5"]], 56, "osaca-yml"),
        "spr": InstructionEntry("IDIV", "gpr", 33, 16.0, [[16, "0"]], 16, "agner-vol4"),
        "zen3": InstructionEntry("IDIV", "gpr", 23, 11.5, [[12, "5"], [12, "6"]], 12, "agner-vol4"),
        "zen4": InstructionEntry("IDIV", "gpr", 20, 10.0, [[10, "5"], [10, "6"]], 10, "agner-vol4"),
    },
    ("sdiv", "x,x,x"): {
        "v2": InstructionEntry("sdiv", "x,x,x", 5.0, 5.0,
            [[1, "67"], [10, ["6DV", "7DV"]]], None, "osaca-yml"),
        "n1": InstructionEntry("sdiv", "x,x,x", 15.0, 15.0, [[15, "0"]], None, "osaca-yml"),
        "a64fx": InstructionEntry("sdiv", "x,x,x", 13.0, 13.0, [[13, "5"]], None, "osaca-yml"),
        "m1": InstructionEntry("sdiv", "x,x,x", 8.0, 8.0, [[8, "9"]], None, "dougall-m1"),
    },

    # ========== 浮点加法（标量）==========
    ("VADDSD", "xmm,xmm,xmm"): {
        "skx": InstructionEntry("VADDSD", "xmm,xmm,xmm", 4, 0.5, [[1, "01"]], 1, "osaca-yml"),
        "spr": InstructionEntry("VADDSD", "xmm,xmm,xmm", 4, 0.5, [[1, "0F"]], 1, "agner-vol4"),
        "zen3": InstructionEntry("VADDSD", "xmm,xmm,xmm", 3, 0.5, [[1, "01"]], 1, "agner-vol4"),
    },
    ("fadd", "d,d,d"): {
        "v2": InstructionEntry("fadd", "d,d,d", 2.0, 0.25, [[1, ["8", "9", "10", "11"]]], None, "osaca-yml"),
        "n1": InstructionEntry("fadd", "d,d,d", 3.0, 0.5, [[1, "12"]], None, "osaca-yml"),
        "a64fx": InstructionEntry("fadd", "d,d,d", 2.0, 0.5, [[1, "0"]], None, "osaca-yml"),
        "m1": InstructionEntry("fadd", "d,d,d", 2.0, 0.33, [[1, "01"]], None, "dougall-m1"),
    },

    # ========== 向量浮点加法（SIMD）==========
    ("VADDPD", "ymm,ymm,ymm"): {
        "skx": InstructionEntry("VADDPD", "ymm,ymm,ymm", 4, 0.5, [[1, "01"]], 1, "osaca-yml"),
        "spr": InstructionEntry("VADDPD", "ymm,ymm,ymm", 4, 0.5, [[1, "0F"]], 1, "agner-vol4"),
        "zen3": InstructionEntry("VADDPD", "ymm,ymm,ymm", 3, 0.5, [[1, "01"]], 1, "agner-vol4"),
        "zen4": InstructionEntry("VADDPD", "ymm,ymm,ymm", 3, 0.5, [[1, "01"]], 1, "agner-vol4"),
    },

    # ========== 向量浮点乘法（SIMD）==========
    ("VMULPD", "ymm,ymm,ymm"): {
        "skx": InstructionEntry("VMULPD", "ymm,ymm,ymm", 4, 0.5, [[1, "01"]], 1, "osaca-yml"),
        "spr": InstructionEntry("VMULPD", "ymm,ymm,ymm", 4, 0.5, [[1, "0F"]], 1, "agner-vol4"),
        "zen3": InstructionEntry("VMULPD", "ymm,ymm,ymm", 4, 0.5, [[1, "0F"]], 1, "agner-vol4"),
        "zen4": InstructionEntry("VMULPD", "ymm,ymm,ymm", 4, 0.5, [[1, "01"]], 1, "agner-vol4"),
    },

    # ========== 向量 load（VMOVUPD 从内存读）==========
    ("VMOVUPD", "ymm,mem"): {
        "skx": InstructionEntry("VMOVUPD", "ymm,mem", 4, 0.5, [[1, "23"], [1, ["2D", "3D"]]], 1, "osaca-yml"),
        "spr": InstructionEntry("VMOVUPD", "ymm,mem", 5, 0.5, [[1, "23"], [1, ["2D", "3D"]]], 1, "agner-vol4"),
        "zen3": InstructionEntry("VMOVUPD", "ymm,mem", 4, 0.5, [[1, "0234"]], 1, "agner-vol4"),
        "zen4": InstructionEntry("VMOVUPD", "ymm,mem", 4, 0.5, [[1, "0234"]], 1, "agner-vol4"),
    },

    # ========== 向量 store（VMOVUPD 写内存）==========
    ("VMOVUPD", "mem,ymm"): {
        "skx": InstructionEntry("VMOVUPD", "mem,ymm", 1, 1.0, [[1, "4"], [1, "7"]], 1, "osaca-yml"),
        "spr": InstructionEntry("VMOVUPD", "mem,ymm", 1, 1.0, [[1, "4D"], [1, "7D"]], 1, "agner-vol4"),
        "zen3": InstructionEntry("VMOVUPD", "mem,ymm", 1, 1.0, [[1, "4"], [1, "5"]], 1, "agner-vol4"),
        "zen4": InstructionEntry("VMOVUPD", "mem,ymm", 1, 1.0, [[1, "4"], [1, "5"]], 1, "agner-vol4"),
    },

    # ========== FMA（神经网络主力）==========
    ("VFMADD231PD", "ymm,ymm,ymm"): {
        "skx": InstructionEntry("VFMADD231PD", "ymm,ymm,ymm", 4, 0.5, [[1, "01"]], 1, "osaca-yml"),
        "spr": InstructionEntry("VFMADD231PD", "ymm,ymm,ymm", 4, 0.5, [[1, "0F"]], 1, "agner-vol4"),
        "zen3": InstructionEntry("VFMADD231PD", "ymm,ymm,ymm", 4, 0.5, [[1, "01"]], 1, "agner-vol4"),
        "zen4": InstructionEntry("VFMADD231PD", "ymm,ymm,ymm", 4, 0.5, [[1, "01"]], 1, "agner-vol4"),
    },
    ("fmadd", "s,s,s,s"): {
        "v2": InstructionEntry("fmadd", "s,s,s,s", 4.0, 0.5, [[1, ["8", "10"]]], None, "osaca-yml"),
        "n1": InstructionEntry("fmadd", "s,s,s,s", 4.0, 0.5, [[1, "12"]], None, "osaca-yml"),
        "a64fx": InstructionEntry("fmadd", "s,s,s,s", 2.0, 0.5, [[1, "0"]], None, "osaca-yml"),
        "m1": InstructionEntry("fmadd", "s,s,s,s", 3.0, 0.33, [[1, "01"]], None, "dougall-m1"),
    },

    # ========== 浮点除法（极慢，热点嫌疑）==========
    ("VDIVSD", "xmm,xmm,xmm"): {
        "skx": InstructionEntry("VDIVSD", "xmm,xmm,xmm", 13, 6.0, [[6, "0"]], 1, "osaca-yml"),
        "spr": InstructionEntry("VDIVSD", "xmm,xmm,xmm", 14, 7.0, [[7, "0"]], 1, "agner-vol4"),
        "zen3": InstructionEntry("VDIVSD", "xmm,xmm,xmm", 13, 7.0, [[7, "0"]], 1, "agner-vol4"),
    },
    ("fdiv", "d,d,d"): {
        "v2": InstructionEntry("fdiv", "d,d,d", 14.0, 7.0, [[7, ["8DV"]]], None, "osaca-yml"),
        "n1": InstructionEntry("fdiv", "d,d,d", 15.0, 7.5, [[8, "12"]], None, "osaca-yml"),
        "m1": InstructionEntry("fdiv", "d,d,d", 11.0, 5.5, [[6, "01"]], None, "dougall-m1"),
    },

    # ========== 平方根（极慢）==========
    ("VSQRTSD", "xmm,xmm,xmm"): {
        "skx": InstructionEntry("VSQRTSD", "xmm,xmm,xmm", 18, 12.0, [[12, "0"]], 1, "osaca-yml"),
        "zen3": InstructionEntry("VSQRTSD", "xmm,xmm,xmm", 18, 12.0, [[12, "0"]], 1, "agner-vol4"),
    },

    # ========== 内存读（隐式，通过 load_latency + load_throughput 建模）==========
    ("LOAD", "mem->reg"): {
        "skx": InstructionEntry("LOAD", "mem->reg", 4, 0.5, [[1, "23"], [1, ["2D", "3D"]]], None, "osaca-yml"),
        "zen3": InstructionEntry("LOAD", "mem->reg", 4, 0.5, [[1, "0234"]], None, "agner-vol4"),
    },
    ("ldr", "x,[x]"): {
        "v2": InstructionEntry("ldr", "x,[x]", 4.0, 0.3333, [[1, ["12", "13", "14"]]], None, "osaca-yml"),
        "n1": InstructionEntry("ldr", "x,[x]", 4.0, 1.0, [[1, "0134"]], None, "osaca-yml"),
        "a64fx": InstructionEntry("ldr", "x,[x]", 4.0, 0.5, [[1, "89"]], None, "osaca-yml"),
        "m1": InstructionEntry("ldr", "x,[x]", 3.0, 0.33, [[1, "2345"]], None, "dougall-m1"),
    },

    # ========== 分支（误预测代价）==========
    ("JCC", "cond"): {
        "skx": InstructionEntry("JCC", "cond", 0, 0.5, [[1, "6"]], 1, "osaca-yml"),
        "zen3": InstructionEntry("JCC", "cond", 0, 0.5, [[1, "6"]], 1, "agner-vol4"),
    },

    # ========== 位操作（B 扩展）==========
    ("POPCNT", "gpr,gpr"): {
        "skx": InstructionEntry("POPCNT", "gpr,gpr", 3, 1.0, [[1, "1"]], 1, "osaca-yml"),
    },
}


# ============================================================================
# 3. 查询 API（核心）
# ============================================================================

def normalize_name(name: str, arch: Optional[str] = None) -> str:
    """规范化助记符大小写。
    有 arch 时按 ISA 推断：x86 → 大写（ATT 风格），AArch64 → 小写。
    无 arch 时：返回原始（DB 查询用大小写不敏感匹配兜底）。
    """
    if arch:
        info = MICROARCH_PARAMS.get(arch.lower())
        if info:
            return name.upper() if info.isa == "x86" else name.lower()
    return name


def query(name: str, arch: str, operands: Optional[str] = None) -> Optional[InstructionEntry]:
    """查询单条指令在指定架构上的数据。大小写不敏感。
    name: 助记符（按 arch 的 ISA 自动规范化大小写）
    arch: OSACA 架构代码（skx/spr/zen3/zen4/v2/n1/a64fx/m1/tx2）
    operands: 可选操作数签名（如 "gpr,gpr" 或 "ymm,mem"）
    """
    norm = normalize_name(name, arch)
    norm_low = norm.lower()
    arch = arch.lower()
    # 大小写不敏感匹配
    def _lookup(n, ops):
        for (db_n, db_ops), arches in INSTRUCTION_DB.items():
            if db_n.lower() == n.lower() and (ops is None or db_ops == ops) and arch in arches:
                return arches[arch]
        return None
    # 精确匹配
    if operands:
        entry = _lookup(norm, operands)
        if entry:
            return entry
        # 尝试操作数顺序反转（mem,ymm vs ymm,mem）
        if "," in operands:
            rev = ",".join(reversed(operands.split(",")))
            entry = _lookup(norm, rev)
            if entry:
                return entry
    # 模糊匹配（不指定 operands）
    return _lookup(norm, None)


def compare(name: str, operands: Optional[str] = None) -> Dict[str, InstructionEntry]:
    """跨架构对比同一条指令。返回 {arch: entry}。大小写不敏感。"""
    norm_low = name.lower()
    result = {}
    for (n, ops), arches in INSTRUCTION_DB.items():
        if n.lower() == norm_low and (operands is None or ops == operands):
            result.update(arches)
    return result


def supported_archs() -> List[str]:
    """列出所有支持的架构代码。"""
    return sorted(MICROARCH_PARAMS.keys())


# ============================================================================
# 4. CLI 与格式化输出
# ============================================================================

SEP = "=" * 78
SUBSEP = "-" * 78


def format_compare_table(name: str) -> str:
    """格式化跨架构对比表（仿 OSACA 输出风格）。"""
    entries = compare(name)
    if not entries:
        return f"  [!] 未找到指令 '{name}'"

    lines = [SEP, f"指令 {name.upper()} 跨架构对比（数据源见 data_source 字段）", SEP, ""]
    lines.append(f"  {'架构':<8} {'名称':<38} {'latency':>8} {'throughput':>11} {'uops':>5}  port_pressure")
    lines.append(f"  {SUBSEP}")
    for arch, entry in sorted(entries.items()):
        info = MICROARCH_PARAMS.get(arch)
        arch_name = info.name if info else arch
        uops_str = str(entry.uops) if entry.uops else "-"
        lines.append(f"  {arch:<8} {arch_name:<38} {entry.latency:>6}cyc {entry.throughput:>9}cyc/i {uops_str:>5}  {entry.ports_str()}")

    # 优化洞察
    if len(entries) >= 2:
        sorted_by_lat = sorted(entries.values(), key=lambda e: e.latency)
        fastest = sorted_by_lat[0]
        slowest = sorted_by_lat[-1]
        if slowest.latency > 0 and fastest.latency > 0:
            ratio = slowest.latency / fastest.latency
            lines.append("")
            lines.append(f"  💡 最快 {fastest.latency}cyc vs 最慢 {slowest.latency}cyc = {ratio:.1f}× 差距")
            if "DIV" in name.upper() or "div" in name:
                lines.append(f"  🛠 除法是热点嫌疑：用乘法倒数（rcpss/vfrec7）+ Newton-Raphson 替代，可提速 5-10×")

    return "\n".join(lines)


def main():
    import sys
    args = sys.argv[1:]

    if not args:
        # 默认：打印所有关键指令对比
        print("╔" + "═" * 76 + "╗")
        print("║" + " OSACA 数据库本地化 · 跨架构指令对比 ".center(76) + "║")
        print("║" + " 来源：github.com/RRZE-HPC/OSACA + Agner Vol 4 + ARM SOG + Dougall ".center(76) + "║")
        print("╚" + "═" * 76 + "╝")

        # 关键热点指令（按 OSACA / Agner 优化手册推荐排查顺序）
        hot_instructions = [
            ("ADD",     "整数加（基线，最快）"),
            ("IMUL",    "整数乘（3cyc，热点）"),
            ("IDIV",    "整数除（20-94cyc，头号嫌疑）"),
            ("VADDSD",  "标量浮点加（4cyc）"),
            ("VADDPD",  "向量浮点加（SIMD）"),
            ("VFMADD231PD", "FMA（神经网络主力）"),
            ("VDIVSD",  "标量浮点除（13cyc，嫌疑）"),
            ("VSQRTSD", "标量平方根（18cyc，嫌疑）"),
        ]

        for name, desc in hot_instructions:
            entries = compare(name)
            if entries:
                print()
                print(format_compare_table(name))
                print(f"\n  📝 {desc}")

        # 支持的架构
        print(f"\n{SEP}")
        print(f"支持的架构（{len(supported_archs())} 个）:")
        print(SEP)
        for arch in supported_archs():
            info = MICROARCH_PARAMS[arch]
            print(f"  {arch:<8} {info.name:<42} [{info.isa}] 数据源: {info.data_source}")

        print(f"\n📚 完整数据（3000+ 指令）：pip install osaca 或 github.com/RRZE-HPC/OSACA")
        print(f"📖 深度集成指南：top-cs-projects/OSACA_INTEGRATION.md")
        return

    if len(args) >= 1:
        name = args[0]
        arch = args[1] if len(args) >= 2 else None
        if arch:
            # 单条查询
            entry = query(name, arch)
            if entry:
                info = MICROARCH_PARAMS.get(arch.lower())
                print(f"指令: {entry.name} {entry.operands}")
                print(f"架构: {info.name if info else arch} ({arch})")
                print(f"  latency:     {entry.latency} cyc")
                print(f"  throughput:  {entry.throughput} cyc/instr (reciprocal)")
                print(f"  uops:        {entry.uops if entry.uops else '(ARM 不建模)'}")
                print(f"  port_pressure: {entry.ports_str()}")
                print(f"  data_source: {entry.data_source}")
            else:
                print(f"[!] 未找到：{name} @ {arch}")
                print(f"    支持的架构：{', '.join(supported_archs())}")
        else:
            # 跨架构对比
            print(format_compare_table(name))


if __name__ == "__main__":
    main()
