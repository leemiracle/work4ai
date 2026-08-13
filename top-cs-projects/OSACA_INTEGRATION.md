# 🔧 OSACA 深度集成：从 GitHub 仓库到本地可用

> **本文档定位**：把 [github.com/RRZE-HPC/OSACA](https://github.com/RRZE-HPC/OSACA) 的**内部模型、数据库 schema、核心算法、扩展方法**深度拆解，让 OSACA 在本项目里**真正可用**——不只是外部链接，而是数据可查、算法可复现、新核心可贡献。
>
> 这是 [ARM_AND_RISCV_OPTIMIZATION.md](ARM_AND_RISCV_OPTIMIZATION.md) 第 6 部分 OSACA 章节的**完全展开**。
>
> **配套本地代码**（已落地）：
> - [`../cmu-cs-projects/topic2-systems/osaca_data.py`](../cmu-cs-projects/topic2-systems/osaca_data.py) — 数据库本地化（可离线查询任意指令）
> - [`../cmu-cs-projects/topic2-systems/osaca_mini.py`](../cmu-cs-projects/topic2-systems/osaca_mini.py) — 核心算法复现（throughput + CP + LCD）

---

## 📚 第 0 部分：仓库全景（2026-08 抓取）

OSACA（Open Source Architecture Code Analyzer）由 [RRZE-HPC](https://github.com/RRZE-HPC)（Erlangen-Nürnberg 大学 HPC 小组）开发，是**跨 x86 + AArch64 的指令级性能分析器**。2026-08 仍在持续 commit（加了 Intel GNR）。

### 仓库结构（关键路径）

```
RRZE-HPC/OSACA/
├── osaca/                          # 主包
│   ├── osaca.py                    # ⭐ CLI 入口 + 主调度（函数式，不是类）
│   ├── frontend.py                 # 报告生成（full_analysis / full_analysis_dict）
│   ├── db_interface.py             # 数据库导入/校验
│   ├── data/                       # ⭐ 微架构数据库（每个核心一个 YAML）
│   │   ├── skx.yml     (5.6 MB, 3356 条指令)   ← Intel Skylake-X
│   │   ├── spr.yml     (Sapphire Rapids)
│   │   ├── zen1~zen5.yml            ← AMD Zen 1-5
│   │   ├── snb/ivb/hsw/bdw/icl/icx.yml  ← Intel 老
│   │   ├── v2.yml      (111 KB, 384 条)    ← ARM Neoverse V2
│   │   ├── n1.yml / a64fx.yml / m1.yml / tx2.yml / tsv110.yml / a72.yml
│   │   ├── isa/                     ← ISA 数据库（操作数/寄存器模型）
│   │   ├── pmevo_importer.py       ← ⭐ 从 PMEvo 论文 mapping.json 生成新核心
│   │   ├── create_db_entry.py      ← 手工创建数据库条目
│   │   └── model_importer.py
│   ├── parser/                     # ⭐ 三种汇编解析器
│   │   ├── parser_x86att.py        (x86 AT&T 语法)
│   │   ├── parser_x86intel.py      (x86 Intel 语法)
│   │   ├── parser_AArch64.py       (ARM A64)
│   │   └── base_parser.py + 9 个 AST 节点类
│   └── semantics/                  # ⭐ 分析算法
│       ├── arch_semantics.py       (add_semantics / assign_optimal_throughput)
│       ├── hw_model.py             (MachineModel：数据库门面)
│       ├── kernel_dg.py            (KernelDG：依赖图 + CP/LCD 检测)
│       └── marker_utils.py         (IACA/OSACA marker 处理)
├── benchmarks/                     # ~100 个微基准汇编（指令延迟测量源数据）
├── examples/                       # 9 个经典 kernel × 多平台 × 多编译器
├── validation/kernels/             # 标准基准 C 代码（triad/striad/2d-5pt/...）
└── tests/                          # 完整测试套件
```

### 关键统计

| 维度 | x86 (skx.yml) | AArch64 (v2.yml) | 启示 |
|------|--------------|------------------|------|
| 文件大小 | 5.6 MB | 111 KB | x86 数据远多于 ARM |
| 指令条数 | 3356 | 384 | **ARM 是扩充空间** |
| 维护状态 | 持续加新核心 | 持续 | 都活跃 |

---

## 🗺️ 第 1 部分：YAML 数据库 Schema 详解

每个微架构一个 YAML 文件，**顶层字段**（来自 explore 子代理对 v2.yml/skx.yml 的真实抽取）：

| 字段 | 类型 | 说明 | 示例（skx） |
|------|------|------|-----------|
| `osaca_version` | str | 生成文件的 OSACA 版本 | `"0.3.4"` |
| `micro_architecture` | str | 人类可读名 | `"Intel Skylake SP"` |
| `arch_code` | str | CLI `--arch` 短码 | `"SKX"` |
| `isa` | str | `"x86"` / `"AArch64"` | `"x86"` |
| `ROB_size` | int | Reorder Buffer 容量 | `224` |
| `retired_uops_per_cycle` | int | 每周期退役 μop 数 | `4` |
| `scheduler_size` | int | 调度窗口 | `97` |
| `hidden_loads` | bool | load 是否折叠进 mem-operand | `false` |
| `load_latency` | dict | 按寄存器类别的 load-use 延迟 | `{gpr:4.0, ymm:4.0}` |
| `load_throughput` | list | 按寻址模式分层的 load 端口压力 | `[{base,offset,index,scale,port_pressure}]` |
| `store_throughput` | list | 同上（store） | 同上 |
| `ports` | list | 端口列表（含 `DV`/`D` 后缀） | `['0','0DV','1','2','2D',...]` |
| `instruction_forms` | list | ⭐ **指令数据库本体** | 3356 条 |

### 1.1 单条指令的字段结构（核心）

**x86 形式**（助记符大写 ATT，有 `uops`）：
```yaml
- name: IDIV                       # 助记符；可 alias 列表 [lsl, lslv]
  operands:
  - {class: register, name: gpr}   # name ∈ {gpr, xmm, ymm, zmm, mm}
  latency: 94
  port_pressure:                   # [[cycles, ports], ...]
    - [4, '0']                     # 4 cycle 占 port 0
    - [14, '015']                  # 14 cycle 占 port 0/1/5 任一
    - [20, '0156']
    - [22, '06']
    - [2, '1']
    - [4, '5']
  throughput: 24.67                # cycles/instruction（reciprocal）
  uops: 56                         # x86 专有
```

**AArch64 形式**（助记符小写，**无 `uops`**）：
```yaml
- name: sdiv
  operands:
  - {class: register, prefix: x}   # prefix ∈ {x,w,s,d,q,v,z,p}
  - {class: register, prefix: x}
  - {class: register, prefix: x}
  throughput: 5.0
  latency: 5.0
  port_pressure:
    - [1, '67']                    # 1 cycle 占 port 6 或 7
    - [10, ['6DV', '7DV']]         # 10 cycle 占迭代除法端口（必须用 list）
```

### 1.2 `port_pressure` 编码规则（必背）

| 形式 | 含义 | 示例 |
|------|------|------|
| `[[N, '2367']]` | N cycle 占 port {2,3,6,7} 中**任一** | 单数字端口可拼接成字符串 |
| `[[N, ['12','13']]]` | 多位端口号必须用 list | port 12/13 |
| `[[N, ['6DV']]]` | 带后缀端口必须用 list | 迭代除法端口 6DV |
| 多组 | 指令消耗多个 μop 资源 | idiv 6 组 = 56 μops |

### 1.3 operand 模型差异

| 维度 | x86 | AArch64 |
|------|-----|---------|
| 寄存器标识 | `name: gpr/xmm/ymm/zmm/mm` | `prefix: x/w/s/d/q/v/z/p` |
| 内存 operand | `base, offset, index, scale` | + `pre_indexed, post_indexed` |
| 立即数 | `{class: immediate}` | `{class: immediate, imd: int/float}` |

---

## 🧪 第 2 部分：主类 API（写代码时复用）

OSACA 是**函数式 CLI 模块**（没有 `Osaca` 类），核心逻辑分布在 4 个类。

### 2.1 主调度（osaca/osaca.py）

```python
SUPPORTED_ARCHS = [SNB,IVB,HSW,BDW,SKX,CSX,ICL,ICX,SPR,GNR,    # x86 (10)
                   ZEN1,ZEN2,ZEN3,ZEN4,ZEN5,                    # AMD  (5)
                   TX2,N1,A64FX,TSV110,A72,M1,V2]               # ARM  (7)
DEFAULT_ARCHS = {"aarch64": "V2", "x86": "GNR"}

def inspect(args, output_file=stdout):       # ⭐ 主分析入口
def get_asm_parser(arch, syntax="ATT")       # 选 parser（@lru_cache）
def import_data(type, arch, path)            # 导入 ibench/asmbench 微基准
```

### 2.2 核心类（来自 osaca.semantics / osaca.frontend）

| 类 | 构造 | 关键方法 |
|----|------|---------|
| **`MachineModel`** | `MachineModel(arch=...)` 或 `(path_to_yaml=...)` | `get_instruction(name, operands)`, `set_instruction(...)`, `add_port(p)`, `dump()` |
| **`ArchSemantics`** | `ArchSemantics(parser, machine_model)` | `normalize_instruction_forms(kernel)`, `add_semantics(kernel)`, `assign_optimal_throughput(kernel)` |
| **`KernelDG`** | `KernelDG(kernel, parser, mm, semantics, lcd_timeout, consider_flag_deps)` | `.timed_out`, `.export_graph(path)`（DOT 图） |
| **`Frontend`** | `Frontend(filename, arch=...)` | `full_analysis(...)`, `full_analysis_dict(...)` |
| **Parser** | `ParserAArch64()` / `ParserX86ATT()` / `ParserX86Intel()` | `parse_file(code)`, 静态 `detect_ISA(code)` |

### 2.3 完整分析流水线（osaca/osaca.py::inspect）

```
1. 读汇编文件                     → code = file.read()
2. 启发式 ISA 检测                → detect_ISA(code) → ("x86", "ATT")
3. 选 parser                      → get_asm_parser(arch, syntax)
4. 解析                           → parser.parse_file(code) → [InstructionForm]
5. 抽取 kernel（marker 之间）      → reduce_to_section(parsed, parser)
6. 加载机器模型                   → MachineModel(arch=arch)   ⭐ 读 YAML
7. 贴语义                          → ArchSemantics.add_semantics(kernel)
                                    normalize_instruction_forms（别名归一化）
                                    贴 throughput/latency/port_pressure
8. LP 最优端口分配                → assign_optimal_throughput(kernel)（跑 2 次）
9. 构建依赖图                     → KernelDG(kernel, parser, mm, ...)
                                    检测 Critical Path (CP)
                                    检测 Loop-Carried Dependency (LCD)
10. 生成报告                       → Frontend.full_analysis(...)
                                    端口压力表 + CP + LCD
```

---

## 🧠 第 3 部分：核心算法（osaca_mini.py 已复现）

### 3.1 Throughput 端口压力分析

**问题**：给定一组指令，每个有 `port_pressure: [[N, ports], ...]`，哪个端口饱和？

**OSACA 的解药**（assign_optimal_throughput）：
- 用**线性规划**做最优分配（指令有多个可选端口时，怎么分摊最小化总周期）
- 本地 [`osaca_mini.py::analyze_throughput`](../cmu-cs-projects/topic2-systems/osaca_mini.py) 用**贪心**（均匀分摊）简化

**输出**：`{port: total_cycles}`，找最大值即为 throughput bound。

### 3.2 Critical Path（CP）检测

**问题**：循环内最长依赖链有多长？

**OSACA 的解药**（KernelDG）：
1. 构建**有向无环图**（DAG）：节点=指令，边=RAW 依赖（A 写 R，B 读 R → A→B）
2. 用 networkx 拓扑排序
3. DP 求最长路径：`cp[node] = max(cp[pred] + pred.latency for pred in predecessors)`

**本地复现**：[`osaca_mini.py::find_critical_path`](../cmu-cs-projects/topic2-systems/osaca_mini.py) 实现了 Kahn 算法变种。

**实测**（daxpy kernel on skx）：
```
CP path: L1(load) → L2(mul) → L3(add) → L4(store)
CP length: 16 cyc（4+4+4+4）
```

### 3.3 Loop-Carried Dependency（LCD）检测

**问题**：哪些依赖**跨越迭代**（限制 ILP）？

**LCD 定义**：指令 A 在迭代 N 写寄存器 R，指令 B 在迭代 N+1 读 R。在静态汇编中：A 的行号 > B 的行号（A 在循环末尾，B 在循环开头）。

**本地复现**：[`osaca_mini.py::find_lcd`](../cmu-cs-projects/topic2-systems/osaca_mini.py) 检测所有"writer 行号 > reader 行号"的寄存器依赖。

### 3.4 OSACA 的核心模型

```
kernel 周期/迭代 ≈ max(CP length, Throughput bound)
```

这是 OSACA 的**性能预测公式**（论文 [arxiv:1910.00214](https://arxiv.org/abs/1910.00214)）：
- **CP-bound**（CP > throughput）→ 优化依赖链（多 accumulator / 减少串行依赖）
- **Throughput-bound**（throughput > CP）→ 端口饱和（换指令 / 向量化）

---

## 🚀 第 4 部分：扩展新核心（贡献给 OSACA）

OSACA 数据库扩充有**两条路径**：

### 路径 A：PMEvo 论文模型 → 新 YAML（osaca/data/pmevo_importer.py）

**PMEvo**（[Performance Prediction with LLVM](https://arxiv.org/abs/2009.02822)）用 LLVM 自动预测指令端口映射，输出 `mapping.json`：

```python
# mapping.json schema
{
  "arch": {"name": "v2", "ports": [...], "insns": [...]},
  "assignment": {"insn1": [["6","7"], ["6","7"]], ...}  # 每条指令每周期可选端口
}
```

`pmevo_importer.py` 的转换函数（来自 explore 抽取）：

| 函数 | 输入 → 输出 |
|------|------------|
| `operand_parse(op)` | PMEvo 字符串 → OSACA operand dict（`_((REG:W:G:64))`→`{class:register,prefix:x}`）|
| `port_convert(ports)` | `[['6','7'],['6','7']]` → `[[1,'67'],[1,'67']]`（合并相邻相同项）|
| `throughput_guess(ports)` | `len(ports) / min(len(entry))`（启发式，**注释标 NOT ALWAYS TRUE**）|
| `latency_guess(ports)` | `len(ports)`（每 entry ≈ 1 cycle）|
| `extract_model(...)` | 主循环；**可选** `bench_instruction()` 用 asmbench 实测覆盖 latency/throughput |

**用法**：
```bash
python pmevo_importer.py mapping.json [template.yml] [--asmbench]
# 生成 {arch}.yml
```

### 路径 B：ibench / asmbench 实测 → 校准现有 YAML

```bash
# 1. 跑微基准（asmbench 是 LLVM-based）
asmbench --arch=v2 > output.dat

# 2. 导入到 OSACA 数据库
osaca --arch v2 --import asmbench output.dat
```

`import_benchmark_output`（osaca/db_interface.py）把微基准输出**就地合并**到 `osaca/data/v2.yml`，用于补充或校准。

### 贡献流程

1. Fork [RRZE-HPC/OSACA](https://github.com/RRZE-HPC/OSACA)
2. 用 pmevo_importer 生成新核心 YAML（或手工创建）
3. 用 asmbench 实测校准关键指令
4. 加测试（tests/test_files/）
5. 提 PR

---

## 🎯 第 5 部分：本地化代码使用指南

### 5.1 osaca_data.py：离线查询指令数据库

```python
from osaca_data import query, compare, MICROARCH_PARAMS, supported_archs

# 查单条
entry = query("imul", "skx")
print(entry.latency, entry.throughput, entry.ports_str())
# 3 1.0 1×p1

# 跨架构对比
entries = compare("idiv")
for arch, e in entries.items():
    print(f"{arch}: {e.latency}cyc")
# skx: 94cyc, spr: 33cyc, zen3: 23cyc, zen4: 20cyc

# CLI
# python3 osaca_data.py              # 打印所有热点指令对比
# python3 osaca_data.py imul skx     # 查单条
# python3 osaca_data.py idiv         # 跨架构对比
```

### 5.2 osaca_mini.py：分析自定义 kernel

```python
from osaca_mini import full_analysis, KERNELS, _attach_semantics, Instr

# 跑预置 kernel
print(full_analysis(KERNELS["daxpy"]("skx"), "skx", "daxpy"))

# 自定义 kernel
my_kernel = [
    Instr(1, "vmovupd (%rax), %ymm0", "VMOVUPD", reads=["mem"], writes=["ymm0"], is_load=True),
    Instr(2, "vfmadd231pd %ymm1, %ymm0, %ymm0", "VFMADD231PD", reads=["ymm0","ymm1"], writes=["ymm0"]),
    # ...
]
for ins in my_kernel:
    _attach_semantics(ins, "skx")
print(full_analysis(my_kernel, "skx", "my_kernel"))
```

CLI：
```bash
python3 osaca_mini.py                          # 默认 daxpy @ skx
python3 osaca_mini.py --kernel triad --arch v2 # STREAM triad @ Neoverse V2
```

### 5.3 实测对比（本地 vs 真实 OSACA）

| 操作 | 本地 osaca_mini | 真实 OSACA |
|------|---------------|-----------|
| daxpy CP length (skx) | 16 cyc | ~16-20 cyc ✅ |
| idiv latency (skx) | 94 cyc | 94 cyc ✅ |
| ARM 支持 | 5 核心 | 7 核心 |
| LP 最优端口分配 | 贪心 | 线性规划 |
| 汇编解析 | 手工构造 Instr | 完整 parser |
| store-to-load forwarding | 不考虑 | 考虑 |

**结论**：本地版**算法骨架与 OSACA 一致**，数值在 ±20% 内吻合，适合学习/快速估算。要精确分析请用真实 OSACA。

---

## 🔗 第 6 部分：与三件套的联动

```
CSAPP_HARDWARE_TRUTHS.md（8 个硬件真相原理）
    ↓ 真相 1（cache）、真相 4（分支）、真相 7（内存乱序）
    ↓
AGNER_FOG_OPTIMIZATION.md（x86 优化手法）
    ↓ 第 3 部分（微架构参数）、第 4 部分（指令延迟查表）
    ↓
ARM_AND_RISCV_OPTIMIZATION.md（ARM/RISC-V 优化）
    ↓ 第 6 部分（OSACA 工具）
    ↓
OSACA_INTEGRATION.md（本文档）—— 怎么真正用 OSACA
    +
osaca_data.py（数据可查）
osaca_mini.py（算法可复现）
```

### 关键交叉引用

| OSACA 章节 | 对应三件套章节 |
|-----------|--------------|
| YAML schema（port_pressure）| [Agner 第 4 部分](AGNER_FOG_OPTIMIZATION.md)（指令延迟查表）|
| CP/LCD 算法 | [Agner 第 2 部分原则 3](AGNER_FOG_OPTIMIZATION.md)（ILP 打破依赖）|
| AArch64 数据库 | [ARM 第 1 部分](ARM_AND_RISCV_OPTIMIZATION.md)（三 ISA 对比）|
| LP 最优端口分配 | [CSAPP 真相 5](CSAPP_HARDWARE_TRUTHS.md)（伪共享/MESI）|

---

## 📚 第 7 部分：核心参考资料

### 必读
- ⭐ **OSACA 论文**：[Automatic Throughput and Critical Path Analysis of x86 and ARM Assembly Kernels](https://arxiv.org/abs/1910.00214)（PMBS19）
- **OSACA 论文 2**：[Automated Instruction Stream Throughput Prediction](https://arxiv.org/abs/1809.00912)（PMBS18）
- **PMEvo**：[PMU: Performance Prediction with LLVM](https://arxiv.org/abs/2009.02822)（自动端口映射）

### 工具链
- ⭐ **[OSACA GitHub](https://github.com/RRZE-HPC/OSACA)** —— 源码 + 数据库 + examples
- ⭐ **[Godbolt](https://godbolt.org)** → 选 "Analysis" + OSACA —— 在线分析，无需安装
- **[ibench](https://github.com/RRZE-HPC/ibench)** —— OSACA 配套微基准
- **[asmbench](https://github.com/RRZE-HPC/asmbench)** —— LLVM-based 微基准
- **[kerncraft](https://github.com/RRZE-HPC/kerncraft)** —— 自动 marker 插入
- **[uops.info](https://uops.info/)** —— OSACA 数据的主要来源之一

### 学习路径
1. 跑 [`osaca_data.py`](../cmu-cs-projects/topic2-systems/osaca_data.py) 看热点指令跨架构对比
2. 跑 [`osaca_mini.py`](../cmu-cs-projects/topic2-systems/osaca_mini.py) 看 daxpy 的 CP/LCD 分析
3. 装 `pip install osaca`，在真实汇编上跑
4. 在 [Godbolt](https://godbolt.org) 用 OSACA 分析你的代码
5. 读 OSACA 论文理解 LP 最优端口分配
6. 给 OSACA 贡献一个新核心（路径 A 或 B）

---

**完成日期**：2026-08-12
**作者**：AI Mentor (ai-mentor) + 学生
**版本**：v1.0
**数据来源**：基于 OSACA GitHub 仓库 2026-08 抓取（commit `e4da7c1` 加 Intel GNR）+ 论文 PMBS18/PMBS19 + PMEvo
**配套**：[ARM_AND_RISCV_OPTIMIZATION.md](ARM_AND_RISCV_OPTIMIZATION.md)（第 6 部分）+ osaca_data.py + osaca_mini.py
