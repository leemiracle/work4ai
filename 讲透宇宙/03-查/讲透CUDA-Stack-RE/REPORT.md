# CUDA 软件栈逆向分析报告（三工具线协同）

**日期**：2026-11-03 起，v1.7（11-06 第七轮：devcode 收官+TileIR 开源闭环+国产 GPU 四栈对照——进行中）
**工作区**：`/usr-data/data1/reverse/cuda-stack/`（bin/samples/work/tools + PROGRESS.md 台账）
**工具线**：①NVIDIA 官方 cuobjdump/nvdisasm（CUDA 12.9+13.1 双代对照）②Ghidra 12.2 headless（节点 13 x86_64 + JDK25）③rea 6.5.0（npx + pwntools evidence 线）+ 自研 Python fatbin 解析器
**样本源**：节点 13（10.44.11.13，root 免密）宿主机 CUDA toolkit + NGC 镜像 `nvcr.io/nvidia/ai-dynamo/sglang-runtime:0.7.0`

---

## 0. 要点速览

1. **主战场=节点 13**：x86_64 + CUDA 12.9/13.1 双 toolkit + 驱动 590.48.01 + NGC/5090 系列 NVIDIA 镜像；node14/18 实为国产类 CUDA 栈（corex/maca/dtk，无 libcuda）——"英伟达镜像在三节点"的实际分布勘误。
2. **fatbin 容器格式全破解**（自研 `fatbin_parser.py` 零依赖解析）：16B 文件头 + 64B 小端 entry 链，与 cuobjdump 架构清单 100% 吻合。
3. **PTX 压缩算法勘误**：CUDA 13.1 fatbin 内 PTX = **zstd**（magic `28 B5 2F FD`），社区流传的 LZ4 说法是旧版本；zstd 解压 736B→2438B 得 PTX ISA 9.1。
4. **架构支持矩阵代差**：CUDA 13.1 nvdisasm/nvcc 拒 sm_5x/6x（"deprecated"），12.9 可用；NCCL 2.27.3 仍带 sm_50 cubin（需双代工具协同反汇编）。
5. **NCCL kernel 语料**：libnccl.so.2.27.3（411MB）内嵌 **104 个 cubin / 6475 个 kernel 函数 / 全量 SASS 7.3GB / 3260 万条指令**；SymDev 命名体系=集合操作×协议(LL/LLM/ST×MC)×算法(RS+AG / AG+R)×dtype(含 FP8 双变体) 全展开。
6. **Ghidra 12.2 落地节点 13**（本机 aarch64 无官方 natives——单包仅 x86_64/win）；**Jython 已移除**，脚本必须 Java（`getCurrentProgram()` API 钉版）；cuobjdump 导出 28667 符号。
7. **rea 6.5.0 实证勘误**：源码无任何 CUDA/fatbin 专属解析器（native/ 仅 windows），其 binary 线= pwntools ELF 适配器（需精确版本栈 pwntools 4.15.0+pyelftools 0.33+unicorn 2.1.2）——"rea 直接静态解析 CUDA 目标"实为通过底层工具链组合，非内建能力。
8. **devcode 加密容器全链还原（第七轮 §9.1）**：libcuda 4 使用点=同一 CFB 流密码（SBOX 互逆双表+LCG 密钥流）；**flags2 bit16=载荷加密标志（fatbin entry 级通用机制，公开产物全零=NVIDIA 内部链路）**；解密器 `tools/devcode_decrypt.py` 9 组自测全过。
9. **TileIR 三方闭环（第七轮 §9.2）**：闭源 vtable ↔ 开源 cuda-tile 仓 magic 吻合 ↔ .tilebc 格式源码级全解析（`tools/tilebc_parser.py`）；tileiras 无公开 C API，消费=CLI+libcuda/opencl 双栈 vtable。
10. **国产 GPU 四栈对照定型（第七轮 §9.3/9.4）**：天数=布局克隆派（无 PTX，自研 magic 0x20160329，JIT 吃 NVVM）；沐曦/海光=ClangOffloadBundle 派（沐曦 cu-bridge 733 符号；海光 hyptxas 跨编译器**实测吃下 NVIDIA PTX**）；NVIDIA=私有演进派（TileIR+devcode 双加密扩展）。

## 1. 资产盘点（三节点 + 本地 645 仓）

| 节点 | 访问 | 架构 | 英伟达资产结论 |
|---|---|---|---|
| 13 | `root@10.44.11.13`（lwz 被拒） | x86_64 麒麟 AIOS V10，1TB 内存/128 核 | CUDA 12.9+13.1 toolkit 完整、驱动 libcuda 590.48.01（98MB）、NGC sglang-runtime 43.9GB（CUDA≥12.9）、nvidia_5090/aidp-nv 系镜像 |
| 14 | `ssh node14` | aarch64 | 天数 corex 5.0.0（clang 系自研 toolkit）+ metax；宿主机 cuda-10.2 空壳 |
| 18 | `ssh 10.44.11.18` | amd64 | kylin_dtk 系（国产 GPU），无英伟达本体 |

- 节点 13 的 dnf 损坏（/usr/bin/python3 缺失）→ 所有运行时走便携版部署：`/opt/jdk25`、`/opt/node22`、`/opt/py311`（miniforge+pwntools 栈）、`/opt/ghidra_12.2_PUBLIC`。
- 本地 NVIDIA org 仓 645 个（`/usr-data/data2/repos/agent-repos/NVIDIA`）。逆向对照核心：**cuda-gdb**（GDB fork，`libcudacore/elf.c` + `gdb/cuda/` 74 文件=官方开源 CUDA ELF 解析参考）、cuda-samples、cutlass、cccl、AMGX、cuda-python、go-nvml、gdrcopy。

## 2. fatbin/CUBIN 容器格式实证（第一手解析）

样本：nvcc 13.1 `-arch=all-major` 产出 vectorAdd.fatbin（47968B，sm_75/80/90/100/110/120 + PTX sm_120）。

```
文件头 16B（小端）: magic 0xBA55ED50 | ver=1 | hdr_size=0x10 | fat_size=0xBB50(=filesize-16)
entry 头 64B（小端）: u16 kind(2=ELF/CUBIN,1=PTX) | u16 ver(0x0101) | u32 hdr(0x40)
                     u64 payload_size | u64 pad | u32 flags | u32 arch(sm_十进制) ...
链式: next = entry_off + 0x40 + payload_size
flags 实证: cubin=0x00010008  PTX=0x00090001(bit0=compressed)
```

- 自研解析器 `tools/fatbin_parser.py`：7 entry 全解析，与 cuobjdump `--list-elf/--list-ptx` 清单完全一致；可抽取独立 cubin/PTX blob。
- **PTX 压缩=zstd**（非 LZ4）：`zstd.ZstdDecompressor()` 直接解出 `.version 9.1 / .target sm_120`。
- CUBIN 本体是标准 ELF（abi=7/CUDA，sm 字段+toolkit 版本内嵌）：`cuobjdump -elf` 可见 `.nv.callgraph`、`.nv.rel.action`、`R_CUDA_CONST_FIELD22_37` 重定位类型——与 cuda-gdb `libcudacore/elf.c` 官方解析实现互证。

## 3. SASS 层发现

### 3.1 版本代差矩阵（cuobjdump/nvdisasm 行为实证）

| 操作 | CUDA 12.9 | CUDA 13.1 |
|---|---|---|
| nvdisasm 反汇编 sm_52/50 | ✅ | ❌ "deprecated, use ≤13.0" |
| nvcc 编译 compute_52 | — | ❌ Unsupported（all-major 下限=sm_75） |
| `--dump-elf-header` 选项 | 有 | 已删（用 `-elf`） |
| fatbin PTX 压缩 | （待考） | zstd 实证 |

→ 教训：**CUDA 栈逆向必须双代工具并备**；13.1 拒老架构时 12.9 兜底。

### 3.2 NCCL 2.27.3 kernel 家族（NGC 镜像内 libnccl 411MB）

- **104 个内嵌 cubin**（13 个 fatbin 容器 × sm_50/60/61/70/80/90/100/120 八架构）、**6475 个 kernel 函数**（res-usage 全表 14297 行已存 `work/dumps/nccl.res.txt`）。
- 全量 SASS 反汇编 **7.3GB**（cuobjdump 12.9，13.1 在 sm_50 段 fatal——代差实证④）。
- SymDev 命名体系：`ncclSymDevKernel_{AllReduce|AllGather|…}_{RSxLD(MC)_AGxST(MC) | AGxLL(MC)_R}_sum_{fp32|fp16|bf16|fp8e4m3|fp8e5m2}(ncclSymDevArgs)`
  - 协议轴：LL/LLM/Simple(ST) × MC（NVLS multicast NVLink SHARP）
  - 算法轴：Ring 的 Scatter-Reduce+AllGather vs Tree 的 AllGather+Reduce
  - dtype 轴：含 **FP8 双变体**（e4m3/e5m2）——NVLS 硬件 reduce 精度覆盖面实证
- sm_90 AllReduce(RS+AG, fp32, MC) 单 kernel 画像（6448 行 SASS / 3208 指令）：`IMAD.MOV.U32` 7.9%、`ISETP.*` 分支系 ~10%、`FADD` 162 条主力、**`ULDC UR9 c[0x0][0x224]` uniform datapath**（sm_80+ 特性）开篇、谓词调度（@P0/@!P0）密集。
- 指令级双字编码注释（每条指令后 16 hex=8B 编码）可直接做指令编码语料。
- **全网 mnemonic 分布**（节点 13 python 流式全量统计，`work/dumps/sass.mn3`）：
  - 每架构指令总量：sm_90 626 万 / sm_100 602 万 / sm_120 535 万 / sm_70 284 万 / sm_61 309 万 / sm_60 307 万 / sm_50 301 万 / sm_80 278 万（+sm_100a/120a 家族特化各千条）——Hopper/Blackwell 代 kernel 指令量近 Maxwell/Kepler 代 2 倍。
  - **Blackwell 信号：sm_100/120 的第一大指令是 `R2UR`（register→uniform register，84.1 万/71.6 万条）**，加 `LOP3.LUT`（37.9/34.2 万）与 `IADD.64`（sm_120 29 万）——uniform datapath 依赖度代际跃升是 NCCL kernel 编译目标的硬证据。

### 3.3 vectorAdd 教学样本（编译链自产）

多架构资源画像（REG 10-12、SHARED 1024、CONSTANT[0] 372-380B——参数槽大小随架构增长）；PTX→SASS 对照六架构齐备（`work/dumps/`）。

## 4. Ghidra 线（节点 13 部署）

- **Ghidra 12.2（2026-10-22 发布）单包 570MB 只含 x86_64/win natives** → 本机 aarch64 不可用，部署节点 13；**JDK 要求 25**（InstallationGuide 实证；节点自带 JDK8 不可用，便携版 `/opt/jdk25`）。
- cuobjdump-13.1 冒烟全绿：**28667 符号**（817 Function + 27850 Label；stripped 二进制内部函数无名——LLVM 静态链接体）。
- **libcuda.so.590.48.01（98MB）分析成功**（`_JAVA_OPTIONS=-Xmx180g`）：**384,525 符号**（cuobjdump 的 13 倍——Driver API dynsym 全量导出）。产物 `work/ghidra-libcuda/`（symbols.txt 10.8MB / fatbin_funcs.txt / 反编译样本）。
- **Driver API fatbin 加载路径定位**：`cuModuleLoad@0x40e9c0`、`cuModuleLoadData@0x40ea80`、`cuModuleLoadDataEx@0x40eb40`、**`cuModuleLoadFatBinary@0x40ec00`**、`cuLaunchKernel(ptsz)@0x435b40/0x486d50`、`cuLaunchKernelEx(ptsz)`。
- **反编译首层机制破译**（`cuModuleLoad`）：API 转发壳模式——①`DAT_05f32570==0x321cba00` 魔数哨兵快退（返回 4=CUDA_ERROR_DEINITIALIZED 类状态位）；②真实现经 `PTR_FUN_05f2bbd0` **函数指针表**分发（内部 RM/API 版本化路由层）；③错误码→字符串经 `DAT_05df79e0` **0x18 步长的有序表二分查找**（code+name 指针二元组结构），miss 兜底 `UNRECOGNIZED_ERROR`；④日志格式串 `"Returning %d (%s) from cuModuleLoad"`（驱动侧 API 出错审计路径）。
- **脚本钉版**：Ghidra 12.x 移除 Jython（"Ghidra was not started with PyGhidra"）→ 写 Java 脚本；`currentProgram()` 魔法已死，用 **`getCurrentProgram()`**；headless 的项目目录必须**预 mkdir**。

## 5. rea 线（评估 + 实证）

- **能力勘误**：rea 6.5.0 无内建 CUDA/fatbin/CUBIN 解析器（全源码 grep 零命中；native/ 仅 windows 产物）。它的 AI 逆向编排=CLI/MCP 框架 + provider 适配器体系（pwntools-elf/rizin/gdb/apktool…）。
- 实跑路径：本机 aarch64 被 "pwntools profile supports Linux x64 only" 拒 → 节点 13 部署 node22+rea（npmmirror registry）+ miniforge py311 + **精确版本栈 pwntools 4.15.0/pyelftools 0.33/unicorn 2.1.2**（`REA_PWNTOOLS_PYTHON` 指定，rea 拒绝自装 Python）。
- 产出：`work/rea/rea.cuobjdump.layout.md`（164KB evidence：sha256 溯源 + provider 版本三元组 + ELF 规范化布局 1279 行）——evidence 化输出对审计链有价值。
- **结论**：rea 在本任务的角色=证据链外壳 + x64 ELF 布局；CUDA 语义层解析由官方工具+自研解析器承担（对"AI 驱动逆向工作流"宣传的实证校准）。

## 6. 版本考古与勘误汇总

1. CUDA 13.1：sm_5x/6x 反汇编+编译双弃；`--dump-elf-header` 选项删除。
2. fatbin PTX 压缩：zstd（非 LZ4）。
3. Ghidra 12.2：JDK 25 / 单包无 arm64 / 无 Jython / `getCurrentProgram()`。
4. NCCL 2.27.3 仍支持 sm_50（Blackwell 时代 sm_120 与 Maxwell sm_50 同库共存——生态兼容性跨度 10 年）。
5. 节点 13 双 libcuda：/lib 21MB vs /usr/lib64 98MB（同名 so 不同大小——容器/runtime 双副本，取用需核对路径）。
6. rea 6.5.0 无 CUDA 专属能力（用户预期校准）。
7. node14/18 无英伟达镜像本体（国产栈对照素材）。

## 6.5 cuda-gdb 官方源码对照（线 C，2026-11-03 晚）

对照对象：本地 `cuda-gdb` 仓（git 7690d763，CUDA Toolkit 13.4 release，binutils-gdb 全树 fork）。完整报告 `work/cudagdb-elf-compare.md`（全行号锚）。

1. **fatbin 容器解析在公开领域是空白**：全仓（bfd/include/gdb/libcudacore）`0xBA55ED50` 零命中；fatbin 唯一出现是 `gdb/elfread.c:142` 的告警消音注释（"we get this for the embedded fatbins"，宿主内嵌 fatbin section 不落任何 PT 段）——"不解析、只消音"。容器层拆包在闭源 cudart/libnvfatbin。**→ 自研 fatbin_parser.py 覆盖的是官方开源代码的空白层**（offset2=0x11 等字段无公开对应物可考）。
2. **CUBIN ELF 三元组官方语义钉版**：`EM_CUDA=190` + `ELFOSABI_CUDA=51(0x33)` + `EI_ABIVERSION` 单字节（非 e_flags）。ABI 版本演进表 0-8（gdb/cuda/cuda-trep.h:34-43）：7=`ABI4 "runtime JIT link"`（cudart 动态加载 kernel 后改写 ELF，cuda-modules.c:486-560 `apply_function_load_updates` 是最完整官方样本）。
3. **重定位差集**：cuda-gdb 仅认 R_CUDA_NONE/32/64/G32/G64（cuda-modules.c:44-48）；自研实证的 `R_CUDA_CONST_FIELD22_37` 属 ABI4 runtime JIT link 引入的运行时重定位族，官方 gdb 遇未知类型 trace+skip。
4. **.nv.\* 官方处理面极小**：仅 `.nv.uft→__UFT`（cuda-asm.c:1079）与 `.note.nv.tkinfo/.note.nv.cuver`（cuda-sass-json.c:494-501）；`.nv.callgraph/.nv.info.*` 等零专门处理。
5. 上游 binutils 已收录 CUDA ELF（include/elf/common.h:79/308）→ readelf 可直接复核 cubin 头。


| 资产 | 路径 |
|---|---|
| 工具二进制（12.9/13.1 × cuobjdump/nvdisasm/ptxas） | `cuda-stack/bin/` |
| 样本（fatbin/cubin/libcudart/libnccl 411MB/libcuda 98MB） | `cuda-stack/samples/` + `bin/libcuda.so.1` |
| dump 产物（vectorAdd 四件套 / NCCL res 全表 / sm_90 kernel SASS） | `cuda-stack/work/dumps/` |
| rea evidence | `cuda-stack/work/rea/` |
| 自研 fatbin 解析器 | `cuda-stack/tools/fatbin_parser.py` |
| Ghidra 导出脚本（Java 版） | `cuda-stack/tools/ghidra_export_fatbin.java` |
| 节点 13 便携运行时（jdk25/node22/py311+pwntools/ghidra） | 节点 13 `/opt/` |
| 7.3GB NCCL 全量 SASS + 统计 | 节点 13 `/tmp/cuda-samples/`（tmp 易失，重要切片已拉回） |

## 6.6 第二轮深挖（2026-11-04 晨：A/B 线 + 字节级勘误）

### A 线：libcuda fatbin 加载路径机制链（Ghidra 递归反编译）

`cuModuleLoadFatBinary@0x40ec00` 三层结构完整破译（`work/ghidra-libcuda/fatbin_path_decomp.c`）：
1. **L0 API 壳**：魔数哨兵 `DAT_05f32570==0x321cba00`→return 4；真实现经 `PTR_FUN_05f2bbe8` 分发——与 cuModuleLoad(05f2bbd0)/cuModuleLoadData(05f2bbd8)/LoadFatBinary(05f2bbe8) 构成 **0x8 步长的 API 指针槽位表**；错误码二分翻译 + `"Returning %d (%s) from cuModuleLoadFatBinary"` 审计日志。
2. **L1 API callback 通知层（FUN_00421c00）**：真实现在 `FUN_002d01f0`，前后经 `FUN_005813c0(6, 0x15, …)` 两次调用（进入/退出），携带函数名字符串——**CUPTI/回调订阅层的驱动侧实证**；上下文获取失败时直接 fallback 裸调用。
3. L1 `FUN_011b9b60` = 参数打包日志格式化层。

### B 线：5090 镜像生产 kernel（libtorch_cuda 470MB）

- **架构谱**：3320 cubin = sm_75/80/86/90/100/120 ×449 + 家族特化（sm_100a×59、**sm_103×59 新架构冒头**、sm_120a/121a、sm_90a×4）——`TORCH_CUDA_ARCH_LIST` 生产编译矩阵实证。
- **发行策略发现**：同镜像的 vllm `_C.abi3.so`(269MB)/`_vllm_fa3_C.abi3.so`(602MB) 只编 **sm_80 单目标、零 PTX**——依赖 Blackwell 对 sm_80+ 的跨代 SASS 二进制兼容（CUDA 12.8+）省编译目标。
- torch 132,832 个 kernel 函数 res-usage 全表（47MB）；**SymMem `two_shot_all_reduce_kernel<f,4,4>` sm_120 画像**（76,264 指令）：MOV 9.6%、IMAD 系 ~13%、**IADD.64 5.5%**（symmetric memory 64 位地址算术）、**LDCU/LDCU.64 6.9%**（uniform constant load）、**HFMA2 2026 条**（打包 fp32 成对 FMA=allreduce 求和主力）——与 NCCL sm_90 的标量 FADD 主力形成代际/库间对照。
- **符号层实证**：kernel 符号带 `STO_CUDA_ENTRY STV_DEFAULT`（st_other 的 CUDA 入口标记）、`.text.<mangled>` per-function section、`.align 128` 入口对齐。
- **指令名代差**：sm_120 uniform 加载=`LDCU.64`，sm_90=`ULDC`（代际更替，与全网 R2UR 主导的微观对应）。
- 工具行为发现：`cuobjdump -fun` 在 13.1 对 470MB 生产库全段 not found（SASS 层符号源与 res-usage 不同）；正确路径=`-xelf` 抽独立 cubin + `nvdisasm -c`；**全局 arch 段计数对齐法**（awk 数 res-usage 全局段序=list-elf 全序）可精确定位目标 cubin。

### 字节级勘误（readelf + python 双验证）

- **EI_OSABI=0x41(65) 而非 51**：CUDA 13.1 cubin 实测 65（LLVM/nvcc 系定义）；cuda-gdb/binutils 源码 `ELFOSABI_CUDA=51` 是另一系——**双官方定义并存**。旧 readelf 显示"未知：41"即 65。
- **EI_ABIVERSION 工具链演进**：CUDA 12.9 产物=7（ABI4 runtime JIT link）→ CUDA 13.1 产物=8（STD_ELF）——fatbin 版本考古新维度。

## 7. 可复用资产

| 资产 | 路径 |
|---|---|
| 工具二进制（12.9/13.1 × cuobjdump/nvdisasm/ptxas） | `cuda-stack/bin/` |
| 样本（fatbin/cubin/libcudart/libnccl 411MB/libcuda 98MB） | `cuda-stack/samples/` + `bin/libcuda.so.1` |
| dump 产物（vectorAdd 四件套 / NCCL res+SASS / torch sm_120 cubin+SASS / sass.mn3 统计） | `cuda-stack/work/dumps/` |
| rea evidence | `cuda-stack/work/rea/` |
| Ghidra 导出（cuobjdump 28667 符号 / libcuda 384525 符号 + fatbin 路径反编译） | `cuda-stack/work/ghidra-libcuda/` |
| cuda-gdb 官方对照报告 | `cuda-stack/work/cudagdb-elf-compare.md` |
| 自研 fatbin 解析器 | `cuda-stack/tools/fatbin_parser.py` |
| Ghidra 脚本（导出 Java 版 + 递归反编译 Java 版） | `cuda-stack/tools/ghidra_export_fatbin.java` `ghidra_decompile_fatbin_path.java` |
| 节点 13 便携运行时（jdk25/node22/py311+pwntools/ghidra） | 节点 13 `/opt/` |
| 节点 13 持久产物（NCCL 7.3GB SASS + torch 抽取 cubin） | 节点 13 `/root/cuda-samples` `/root/k5090` |

## 6.7 第三轮深挖（2026-11-04：libnvfatbin 读写路径 + 官方头文件 + sm_103 考据）

### 官方头文件修正 C 线结论

toolkit 自带 `fatbinary_section.h`（版权 2010-2020）——公开的**宿主 wrapper 层**定义：`__fatBinC_Wrapper_t{magic=0x466243B1, version(1/2), data, filename_or_fatbins}`（version2=预链接 fatbin 数组）；section 名 `.nvFatBinSegment`(控制)/`.nv_fatbin`(数据)/`__nv_relfatbin`(预链接)。容器 entry 内部字段仍不公开（C 线"公开空白"精确化为：**wrapper 层公开、entry 层闭源**）。

### libnvfatbin.so.13.1.115（2.4MB）读写路径定位

二进制常量扫描 + Ghidra xref 脚本（`tools/ghidra_xref_magic.java`）定位 **13 个 magic 引用函数**：
- **FATBIN 0xBA55ED50×4**：读校验×3（`cmp dword [rdi],0xba55ed50`）+ 写路径×1（`movabs rax, 50ed55ba_0001_0010`——magic+version+header_size 8 字节内联构造，旁边 `0x3f800000`=1.0f 字段）。
- **zstd magic×5 + lz4 magic×3 并存**：**zstd=写路径**（`mov dword [rdi],0xfd2fb528`+`lea rdx,[rdi+4]` 构造 frame header）、**lz4=旧格式兼容读**——CUDA 压缩格式迁移（lz4→zstd）的二进制铁证。
- `FUN_001c7360` = **压缩帧头嗅探器完整还原**：zstd FHD 纯自实现（未链 libzstd——window exponent `(>>3)+10`、content-size 字段宽、checksum 位、`0x20000` 最小窗口）；lz4 分支 `&0xfffffff0` 接受 **skippable frame 区间**（0x184D2A50-5F）。
- **`FUN_00217160` = 官方 fatbin 提取器**：按 `"__nv_relfatbin"` 优先/`".nv_fatbin"` 兜底找 section（与头文件双证）→ `*__src==-0x45aa12b0`（=0xBA55ED50 有符号读法）校验 → `malloc(fat_size+0x10)` + memcpy 整体拷贝——**自研"16B 文件头+fat_size@offset8"布局获闭源库代码直接三重印证**。
- 压缩 payload 格式判定/entry 遍历在 `FUN_00217300/FUN_002176a0` 子树（产物 `work/nvfatbin/`）。

### 驱动侧 FUN_002d01f0（cuModuleLoadFatBinary 真实现）定性

= **API 管理层**而非字节解析器：参数校验日志（`"fatCubin cannot be NULL"`）、mutex/spin 自适应锁（`+0x28` 字节判锁型）、成功后 `module+0x24 |= 0x40`（fatbin 装载标志位）；核心解析在 `FUN_003dc5d0` 子树（驱动内部 ELF 处理，待续）。

### sm_103 架构考据（来源：NVIDIA 官方博客/NVCC 文档/arnon.dk，2026-11 查证）

- **sm_103 = CC 10.3 = B300/GB300 Blackwell Ultra 数据中心 GPU**；RTX PRO 6000 Blackwell（工作站/服务器）= sm_120（GB202 硅）；GB10 DGX Spark = sm_121。
- 家族后缀体系（CUDA 12.8 引入）：`sm_100a`(B200 tcgen05 特性)/`sm_103a`(B300 特有)/`sm_XXf`(家族内兼容)；基础 `sm_100` 跑全部 10.x。
- 5090 镜像 torch 编 sm_103×59 = 为数据中心 Blackwell Ultra 备料（生产发行矩阵覆盖数据中心+工作站双线）。

## 6.8 第四轮收官（2026-11-04：官方校验函数 + 分发架构 + 代际 diff + 驱动侧定性）

### FUN_00217300 = 官方 fatbin 校验函数（19 行全文还原）——自研布局 100% 字段级确认

```c
// 官方语义（Ghidra 反编译直译）：
bool is_fatbin(void *p, size_t size) {
    if (!p || size < 0x10) return false;                    // 文件头 16B ✓
    u16 hdr = *(u16*)(p+6);                                  // header_size @6 ✓
    if (hdr > 0xf && (u64)hdr + *(u64*)(p+8) <= size)        // fat_size @8 ✓（头后数据长）
        return *(u32*)p == 0xBA55ED50;                       // magic @0 ✓
    return false;
}
```

### FUN_002176a0 = fatbin 分发器（官方遍历架构还原）

三路分发：①`FUN_002175d0` 文件路径分支（默认名 "no file"）；②**宿主 ELF 分支**——8 字节 e_ident 逐字节比较（`\x7fELF\x02\x01\x01\x41` 含 OSABI=65 再证）→ `FUN_00216950("unnamed library")` 加载 → **`FUN_00216b90` section 迭代器**（while 循环多 fatbin section）→ `FUN_00217160` 提取 → `FUN_00217300` 校验 → **消费者回调 `(*param_3)(fatbin, name, ctx)`**（遍历器+回调解耦架构）；③裸 fatbin 分支直接校验回调。
- entry 内部字段（kind/flags/arch/**offset2=0x11**）在消费端回调更深层——**遗留项**：不在解析关键路径（自研遍历不依赖它已 100% 正确），精确官方命名未获（诚实记录）。

### FUN_003dc5d0 = 驱动模块装载管理器（libcuda 侧终局定性）

CU_JIT options 位字段解析（`&4`/`&0x100`）+ JIT 输入类型判定（1/2=cubin/PTX）+ **spin/mutex 两级锁** + `FUN_003b33a0` 装载核心（JIT/签名链，错误路径 `"Module %s is illegal: 1793289"`——驱动有 module 合法性校验）。**架构级结论：libcuda 不做用户态逐字节容器解析；容器解析全在 libnvfatbin（工具链侧）与 cudart（运行时侧），libcuda 只做管理/装载/校验**。产物 `work/libcuda3/fun3dc5d0_decomp.c`（1412 行）。

### sm_120 vs sm_90 全网指令画像 diff（Blackwell 代际特性系统化）

口径：NCCL 2.27.3 全网 3260 万指令、各架构 top30 mnemonic（`work/dumps/sass.mn3`）占比对比。

| 维度 | Hopper sm_90 | Blackwell sm_120 | 结论 |
|---|---|---|---|
| 64 位算术 | `IMAD.X`(14.9万)+`IADD3.X`(9万) 进位链 | **`IADD.64` 原生 28.96 万条** | 64 位地址算术硬件化 |
| 谓词逻辑 | PLOP3 少 | **`PLOP3.LUT` 9.78 万** | 谓词三输入逻辑融合进 top30 |
| 打包 FMA | 标量 FADD 主力 | **`HFMA2` 9.26 万** | 打包化加深 |
| 寄存器搬运 | MOV 1.8% | **MOV 6.7%（3.7×）** | uniform/bank 约束下搬运增多 |
| 逻辑融合 | LOP3.LUT 5.3% | 8.8% | — |
| local 访存 | LDL 3.0%/STL 2.5% | 1.2%/1.4%（减半） | 寄存器资源更宽 |
| 分支同步 | BSYNC 2.7% | 1.7% | 代码更平直 |
| uniform 化 | R2UR 25.5%（第一） | R2UR 18.4%（仍第一） | uniform datapath 两代皆为基线特征 |

## 6.9 第五轮（2026-11-04~05：四车道并行——JIT 机制突破 + 公开源码闭环 + 六代演化）

### 车道2 ✅ libcuda 装载核心 FUN_003b33a0（16,527 行树）——**PTX JIT 机制本轮最大突破**

**PTX JIT = 进程内 "ptxas 命令行" API（非子进程、非内核态）**，证据链全锚定（work/libcuda4/notes.md）：
1. `FUN_005b6f20`：`dlopen("libnvidia-ptxjitcompiler.so.1") + dlsym("__cuda_CallJitEntryPoint")`（失败=CUDA_ERROR_JIT_COMPILER_NOT_FOUND）；JIT 库本体=节点 13 `/usr/lib64/libnvidia-ptxjitcompiler.so.590.48.01`（32MB，导出 nvPTXCompiler* API，内含 sm_100~110f 目标表）；
2. `FUN_0118c150` 拼 argv：`{"ptxas","-arch","sm/compute_XX[a|f]","--input-as-string", CU_JIT 选项分词…,"-ok","0x%llx"}` → `(*entrypoint)(cmd=1, argc, argv, &out_image, 0, 0)`；
3. **16,527 行树零 fork/exec**——libcuda 里成片裸 "ptxas" 字符串就是各调用点的 argv[0] 内联常量；NVVM/LTO 输入旁路 dlsym `nvvmCompileProgram`（libnvidia-nvvm.so）；
4. 架构串构造器 `FUN_005be6d0`：`"compute_NNN"`（JIT 虚拟目标）vs `"sm_NNN"`（cubin）的分岔点，a/f 后缀与 entry flags2 位对应。

配套机制：module 对象=FUN_003dbd30 `calloc(600B)`+全局 id 计数器+kernel 链 stride 0x480，名字 tag 取 fatbin `__nv_module_id` 节否则合成 "cuModuleLoadDataEx"；**架构选择器 FUN_0039fc00**（输入嗅探：0xba55ed50 掩码兼容新代 0x100001ba55ed50/ELF EM_CUDA=0xbe/0x1ee55a01/裸 PTX 四型；kind4 家族回退 bsearch 表 {7,5}→{7,0}；无匹配 cubin 返 0xd1=NO_BINARY_FOR_GPU→JIT，JIT 禁用=0xdd）；**JIT 磁盘缓存**=CUDA compute cache（FNV-1a 0xcbf29ce484222325 完整性校验+CUPTI 事件 0x3e-0x40）。

**offset2=0x11 判定（第四轮遗留清账）**：实为 entry+**0x28** 扩展 flags2——bit0x100000="a" 后缀/bit0x200000="f" 后缀（消费者=FUN_005cc370，与架构串 a/f 一致）/bit0x1000000=0x68 扩展头代际位；实测 13.1 sm_100+=0x1000011、PTX 压缩=0x8011、12.x PTX=0x2011；低 4 位 0x11 无消费者（疑 nvcc 生成器标记，标遗留）。**"Module illegal: 1793289" 定性**：编译期烘焙的内部源码引用 ID（libnvidia-opencl 同款同数字=共享驱动源码），非错误码/版本；对外错误码 200。

**第四轮勘误（三处）**：①cudart 全库零 fatbin magic 引用——"容器解析在 cudart"修正为 **libcuda 内嵌 nvJitLink**（FUN_005cc370，链接上下文 magic 0x1464243bc，C++ 异常以 TLS+setjmp 仿真）；②FUN_002167c0 是 ar 归档成员迭代器（!<thin>/__.LIBDEP，relocatable .a 路径）非 entry 迭代器；③libnvfatbin FATBIN magic 仅 3 处引用（抽取/校验/**写路径 FUN_0022b900 写新代 magic 0x100001ba55ed50**）。

### 车道3 ✅ 公开源码交叉对照（647 仓全群扫描）——"两头公开、中间空白"差集定型

- **注册 ABI 公开决定性证据=cccl parallel.v2 hostjit**：Windows 导入库显式列 `__cudaRegisterFatBinary` 族符号（compiler.cpp:2103-2111）=按名导入非弱符号约定；Linux=.init_array/Windows=.CRT$XCU（loader.cpp:16-18/133）；**注册有 ctor、注销无 dtor 的不对称**=悬挂注册损坏模块表→kernel 静默 no-op（issue #9367）；-rdc 变体=`__cudaRegisterLinkedBinary_<name>`（TensorRT-Edge-LLM deviceLinkStub）。应用源码普遍零手写注册（nvcc/clang 代码生成器发射）。
- **cuda-gdb 对 fatbin wrapper/entry 零知识**：模块经 CUDBG_EVENT_ELF_IMAGE_LOADED 以 module_id+size+整枚 relocated cubin 到达（cuda-events.c:152/cuda-modules.c:86）；额外公开驱动安全注入（/proc fd 写 magic）/CUDBG_INJECTION_PATH/LFL 能力协商/LFL 增量重定位完整消费端（cuda-modules.c:490-809，ABI4 "runtime JIT link" 样本）；cudadebugger.h=闭源契约头（公开仓不可独立构建）。
- **CUDA_MODULE_LOADING 公开面**：env+CUmoduleLoadingMode 枚举+cuModuleGetLoadingMode 可查询；默认 LAZY（CUDA 11.7+，cutlass 注释）；测试/nsys profiling 普遍反打 EAGER（cuopt 生产 putenv 强制）。
- **JIT 生态实践**（285 命中/20+ 仓）：nvrtc 出 cubin 优先 PTX 兜底；CU_JIT_INPUT 全枚举 **1=PTX/2=FATBINARY 与逆向 FUN_003dc5d0 输入类型 1-2 对号**；PTX NUL 终止契约（MDL-SDK 实证）；**nvfatbin 有公开 builder API**（add_ptx/cubin/ltoir/tile_ir+ERROR_COMPRESSION_*，CUDA≥12.4，pip nvidia-nvfatbin 分发；fatbinary_section.h 随 nvcc wheel 分发=pathfinder 实证）。
- **12 行差集表**（work/pubsrc-xref/notes.md §5）：CUBIN ELF 层=唯一全公开对照；入口（注册序列/API 声明/CU_JIT/nvfatbin API）与出口（cuda-gdb/生态 JIT）公开；**16B 文件头/64B entry 链/kind/flags/offset2/zstd 算法在全 647 仓零命中=本战役逆向独有贡献**；libcuda 三层链与库内分发机制零公开。

### 车道4 ✅ 六代 SASS ISA 演化（Maxwell→Blackwell，3242 万指令）

四轮两代 diff 升格六代全景（work/isa-evolution/sixgen-notes.md）：**64 位算术三步硬件化**（IADD+X → IADD3+X 双进位 → sm_120 IADD.64 原生 5.4%）；**uniform datapath 一代封王**（sm_80 ULDC.64 2.2% 发芽 → sm_90 R2UR 18.8% 直接第一 → 两代稳 13-14%）；**乘法三代三形态**（XMAD 分块族 7.0% → IMAD 族 → IMAD.WIDE.U32）；**溢出四代单调降**（Ampere 峰 5.7% → sm_120 最低 1.9%=寄存器扩容指令级证据）；sm_120 独有 top30=HFMA2/PLOP3.LUT/P4 谓词；a 变体（sm_100a/120a）=64-bit uniform 全家桶（MOV.64/SEL.64/UIADD3.64）；Hopper 起语料翻倍（NVLS/SymMem 内核代增）。**全量直方图交叉验证通过**（arch_mn_full.tsv 2117 行，逐架构总量偏差 0.1-0.36%，top30 结论全成立）；top30 外增量发现：**sm_120 独有 RELIABLE/RECONVERGENT 分支控制族**（BRA.CONV/BSSY.BSYNC.RELIABLE/CALL.REL.NOINC=Blackwell 分支语义精化）+ **sm_120 完全弃用 IMAD.MOV.U32**（与 MOV 3.7× 跃升互为因果）；sm_90 独有 HFMA2.MMA 族/ISETP.*.EX。坑钉版：**gawk split() 对正则分隔符不跳前导空白，a[1] 恒空**（tools/arch_mn.sh 三版 0 行输出真凶）。

### 车道1 ✅ cudart 注册链（app→cudart→libcuda 最后一环，38 件反编译+notes.md）

**cudart 注册链零解析零校验**——`__cudaRegisterFatBinary` 仅 `malloc(0x68)` 构造 handle 存 wrapper 指针（**不查 magic 0x466243B1、不遍历 section**），与车道2"驱动侧解析"互证补全分层终态：**容器解析全在驱动侧（libcuda 内嵌 nvfatbin/nvJitLink），cudart 只做记账与转发**。三层记账：handle 0x68B（func 链表 @+0x50 / var 链表 @+0x40）+ 全局 state 3 张 FNV-1a 分离链接哈希表 + per-module kernel 表。**LAZY/EAGER 双层开关**：cudart 侧 `CUDA_ENABLE_MODULE_LAZY_LOADING`（state+0xc8/c9，装载门槛 FUN_129c70 跳过无 managed var 的 fatbin）vs 驱动侧 `CUDA_MODULE_LOADING`（车道3 公开面）——惰性装载是两层各有一个开关。**交接=被动惰性**：首 CUDA 调用→`dlopen("libcuda.so.1",RTLD_NOW)`→`dlsym(cuGetProcAddress_v2)`→批量解析 cuModuleLoadFatBinary 装载族（三通道+stub 簇防护）→LAB_1243d0 把 wrapper 透传驱动，CUmodule 存 handle+0x8。`__cudaRegisterFunction` 以 hostFunc 指针为 key 入全局 FNV 表；launch 经 FUN_1407f0 查表→cuLaunchKernelEx 槽。钉版坑：**Ghidra 对 x86-64 .so 默认基址 0x100000**（v1 脚本全灭根因）；大函数用反汇编 fallback 优于反编译。

**第五轮架构终态（四车道合流）**：`app ctor(.init_array) → __cudaRegisterFatBinary(纯记账) → [LAZY:首调用] dlopen libcuda+cuGetProcAddress_v2 批量解析 → cuModuleLoadFatBinary(wrapper 透传) → libcuda 内嵌 nvfatbin 解析容器(entry+0x28 flags2 择优/家族回退) → 有 cubin 用之/无则 FUN_003afdf0 JIT(进程内 ptxas 命令行 API via libnvidia-ptxjitcompiler) → FUN_003dbd30 calloc(600B) module → kernel 链 0x480 → launch 查 FNV 表`——从 nvcc 产物到 kernel 执行的完整装载链路全线贯通，公开侧"中间空白"全部由逆向补齐。

## 6.10 第六轮（2026-11-05：三车道——JIT 对端协议/链接上下文全景/B300 语料）

### 车道B ✅ nvJitLink 链接上下文与 descriptor 全字段（notes.md 358 行全锚定）

- **ctx 全表**：0x118B/35 槽（magic@0/arch@+8/mode@+0xc/required-bits@+0x10/选中镜像@+0x68-78/`__nv_module_id`@+0x80/ptxas 产物 handle@+0x88/解压缓冲@+0x90/obfuscation id@+0x98/选项历史链@+0xa0/'a''f' 后缀位@+0xb0）；生命周期=FUN_005ba5d0 建（arena 0x118）→FUN_0039fc00 逐候选一建一毁→FUN_005b6db0 终毁；16 处 magic 校验点全表。
- **descriptor（entry）0x0-0x40 全字段**：**kind 枚举定型 {1=PTX, 2=ELF, 8=NVVM, 0x10=INDEX, 0x40=dlink 成员, 0x80=TileIR}**；**flags2 逐位**：0xf000=压缩算法 nibble、0x10000=解压器位、0x100000/0x200000='a'/'f' 家族后缀、0x1000000=0x68 扩展头代际位；+0x30=obfuscation id、+0x38=解压后大小、+0x14=TLV 扩展记录。
- **cmd 协议表 {1,6,7,9,10,0x10,0x12,0x14,0x15}**+NVVM（"-link-lto"/"-lnk"）+**TileIR 全链**（nvTileIR 11 函数 vtable=ctx[0x17..0x22]；**libnvidia-tileiras.so.590 93.9MB** 节点 13 实存——CUDA 13 "Tile IR" 新格式线的库本体）。
- **重磅新发现**：**0x1ee55a01=加密 devcode 容器**（LCG+S-box 流密码+`<exe>.devcode` sidecar——第五轮输入嗅探第四型的定性）；".nv.compat" ELF 节（SHT 0x70000086）=族兼容数据源；arch 注册表（+0x30/0x38 兼容集+虚实互链）。
- 遗留清账：低 4 位 0x11 维持遗留（无消费者），但 **0x8000/0x2000=压缩 nibble 位**（推翻"无消费者"——0x8011/0x2011/0x11 三样本实测吻合）。勘误 4 条录 notes §9。

### 车道C ✅ sm_103 四代对比（B300/Blackwell Ultra 视角，torch 第二语料 1.2 亿指令）

- **语料勘误**：libtorch_cuda.so 实含 **2819** cubin（非二轮记的 3320）；**sm_103f×59 与 sm_100a×59 同 TU 完美配对**（56/56 名集相等）→ **sm_103 不是 100→120 中间态，是 100a 双胞胎**（独立 tcgen05 加速集=CUTLASS 324+guardrail trap ~150 函数，34.3 万指令）；唯一实质 ISA 差=**UTCOMMA 4X→BLOCK16**（B300 tcgen05 编排变化的指令级证据）。
- **六代趋势跨语料复现**（283 精确同 TU 三元组铁证）：IMAD.MOV.U32 4.2→4.1→0、MOV 6.2%、HFMA2 1.67%、RECONVERGENT 常态化；同内核三代 diff（two_shot 无 103 版本→取同内核 360→352→328 条）：IMAD.MOV.U32 20→0、IADD.64 24 条新出、MOV 4→25、.EX 谓词族全灭。
- **对六代表的跨语料修正**（已回写 work/isa-evolution/sixgen-notes.md）：①**R2UR"第一大指令"是 NCCL 负载特有**（torch 主集 0.05%，300× 差；tcgen05 集 uniform 族 19%——uniform 化程度强依赖负载）；②**IADD.64=sm_120 消费级专属**（103/100a/100 全零）。
- 坑钉版：nvdisasm -c 的 .byte 伪行须 `m!~/^\./` 过滤；f 后缀在 -xelf 文件名被剥；符号名集对齐不能按文件序号。

### 车道A ✅ libnvidia-ptxjitcompiler 命令码语义表（notes.md 203 行全锚定+decomp 15k 行）

- **__cuda_CallJitEntryPoint@0x2d8140 全 26 命令码语义表**：1=编译；7/0x14=建链接 context（**0x14=libcuda nvJitLink "in-memory-ELF-image" 专用**——与车道B 调用方协议表对端闭环）；9=五段链接流水；**0x15=.nv.uidx 注入**；0xe/0xf/0x13/0x1a=ELF 校验 getter 族；nvPTXCompiler*/nvLinker* 公开 API **全部映射到命令码**（导出壳拼 argv={"ptxas","--input-as-string",ptx 串}）。
- **input-as-string 零拷贝**进 ctx[4]；全库零 fork/exec 再证（/tmpxft_ 仅建目录）；选项=两段式注册器（150+ 选项→ctx 字段全表）。
- **错误码三层破译**：内部码 7/8/10=异常描述符类（"Unsupported .version"/"Unsupported Function on arch"/Cancellation），与 nvPTXCompiler.h 枚举 **1:1 对应**；libcuda 侧查表 DAT_05ba2fc0 实际落值 `[0,4,4,6,6,6,5,7,8]`（**缺省 4 而非 5——勘误第五轮"缺省 5"**）。
- **arch 三层表**：导出面 13 base arch+45 PTX 版本（活体探测）；内部枚举数组 75 项=sm_20…sm_121+PTX 34（**洞 22/31**=跳过的架构位）；26 项 LTO profile 表；字节级勘误：sm_89 字符串缺失但注册表在。

**第六轮收官要点**：JIT 协议两端闭环（libcuda 调用方 9 码 ↔ ptxjitcompiler 被调方 26 码全表）；fatbin entry kind 枚举定型六种；压缩 nibble/代际位/a-f 后缀逐位语义；devcode 加密容器与 TileIR 库本体（93.9MB）两个新格式线浮出。

## 8. 下一步（第六轮后，可选增量）——**第七轮全部收口（2026-11-06）**

- [x] devcode 加密容器（0x1ee55a01）深挖：LCG+S-box 流密码参数还原+`.devcode` sidecar 格式 → **第七轮车道A 完成**（§9.1）
- [x] libnvidia-tileiras.so 93.9MB：TileIR 格式与 nvTileIR 11 函数 vtable → **第七轮主会话开源实证闭环**（§9.2）
- [x] 26 命令码中未消费的码调用方 → **=libnvidia-opencl**（94.5MB，dlsym `__cuda_CallJitEntryPoint`+nvTileIR\* 11 函数；`GLVLowerKernelSpvToNVVMIR`=SPIR-V→NVVM 路线；NVVM 7.0.1 双库；与第五轮"1793289 共享源码"互证）（§9.2）

## 9. 第七轮（2026-11-06）：devcode 收官 + TileIR 开源闭环 + 国产 GPU 四栈对照

四车道并行（车道A devcode 深挖/车道B 海光 DTK/车道C 天数 corex/车道D 沐曦 MACA）+主会话集成线。集成笔记：`work/cross-vendor/notes.md`。

### 9.1 车道A：devcode 加密容器全链还原（work/devcode/notes.md 20.6KB 13 节全锚定；tools/devcode_decrypt.py）

**统一密码族（本轮最大成果）**：libcuda 内 4 个使用点实为同一个 **CFB 流密码**——加密 `c[i]=c[i-1]^SBOX_B[p[i]^k[i]]`、解密 `p[i]=SBOX_A[c[i-1]^c[i]]^k[i]`；IV=`(~seed)&0xff`；密钥流 k=LCG(0x41c64e6d, 0x3039) LSB-first 每 4 字节步进；SBOX_A（文件偏移 0x5aa2bc0）与 SBOX_B（0x5b66540）互为逆置换（双向程序验证）。

**载荷解密真身=FUN_005bbda0 入口段**（第六轮"解压器"定性升级）：**flags2 bit16=载荷加密标志**；entry+0x30 obfuscation id=CFB 密钥种子；entry+0x10=密文长；解密后按压缩 nibble 解压（0x1000=zstd 系/0x2000=lz4 系/0x4000=murmur3-fmix64 自研状态机）——**fatbin entry 级通用机制**；公开 nvcc 产物 bit16 全零 ⇒ 加密 entry 属 NVIDIA 内部部署链路。

**容器头+0x70 obfuscation 密文**：固定密钥 **0x00349822**（由密钥流首字 0x690b52b3 逆推——恰为 MAC 种子 0x822349 的 hex 循环移位；IV=0xdd）；写侧 FUN_011c8980/读侧 FUN_005cc370，roundtrip ×200+与通用 CFB 交叉对拍 ×200 全过；bit26=obfuscation 标志。

**MAC 定性（勘误第六轮）**：LCG+SBOX_B 循环=源文件名→4B MAC（种子固定 0x822349、累加器 0xb6），非"解载荷"。**环境变量勘误**：真名 `CUDA_DEVCODE_PATH`/`CUDA_DEVCODE_CACHE`（"Fat binaries search path"仅日志串）。

**.devcode 文件层=外部插件 `libfat*Driver.so`**（LD_LIBRARY_PATH glob 扫描→`dlsym("fatBinaryDriver")`→接口 magic **0x2ee55a02**）；节点 13 全盘零实例 ⇒ 磁盘格式 UNVERIFIED（归闭源插件）。FUN_0031cfe0（magic 第三消费者）=装载分派器：devcode 整包直装/0x466243b1 wrapper 展开+PTX JIT 回退。

**验证**：节点 13 无 .devcode 样本，以 tools/devcode_decrypt.py 自造测试向量——**9 组自测全过**（S-box 互逆/密钥自洽/roundtrip/交叉对拍/bit26 语义/随机密钥载荷加解密/'Z' 块 IV/cubin 冒烟/MAC 全链）。

### 9.2 主会话：TileIR/.tilebc 开源实证闭环 + opencl 收网（work/cross-vendor/notes.md）

**TileIR 三方闭环**：闭源侧（第六轮 nvJitLink vtable 11 函数+magic "\x7fTileIR"+kind 0x80）↔ 开源侧（**cuda-tile 仓**，对齐 CUDA 13.1：`BytecodeWriter.cpp:195` 同款 8B magic；README 直接引用 `tileiras --gpu-name sm_100 x.tilebc -o x.cubin` CLI；`cudatilebc-to-mlir`/`mlir-to-cudatilebc` 双向翻译工具）↔ 库本体（93.9MB tileiras：lowering 目标=NVVM（strings "TileIR lowering to NVVM failed"）；TMA 调优开关 TILEIR_PREFER_TMA_FOR_LOAD_STORE/DELAY_TMA_STORE_WAIT/ALWAYS_SWIZZLE；13 个 nvTileIR\* 导出与 vtable 完全吻合）。

**.tilebc 容器格式（源码级）**：`magic[8B]+major u8+minor u8+tag u16LE`（12B 头）+ section 链（id 低 7 位+0x80 对齐位 / length varint / 对齐填充 / data；varint 7bit+continuation，signed=zigzag；SectionID 0x00=End 0x01=String 0x02=Func 0x03=Debug 0x04=Constant 0x05=Type 0x06=Global 0x07=Producer；FunctionFlags bit0=Private bit1=Kernel bit2=HasOptimizationHints）。**两条源码注释勘误**（以代码为准）：①padding 实际=0xCB（kAlignmentByte，Writer/Reader 两处注释 0xCF 均笔误）；②header 版本域=3 个定宽 LE 字段非注释的 version[varint]。解析器 `tools/tilebc_parser.py` 已固化（构造样本正例+NVIDIA fatbin 负例双验证通过）。

**tileiras 消费通道钉版**：无公开 C API 头（CUDA 13.1/12.9 include 全目录实证）——仅 ①CLI（.tilebc→cubin AOT）②运行时 vtable dlsym（libcuda+libnvidia-opencl 双消费者）。

**架构定性**：CUDA 13.1 tile 体系=NVIDIA 首个「IR 层开源（MLIR dialect+bytecode 格式）+编译器本体闭源」双层结构；fatbin 升格为多 IR 载体容器（PTX/ELF/TileIR/NVVM/index 五 kind+devcode 加密第六型）。

### 9.3 国产 GPU 四栈对照总表（work/cross-vendor/notes.md 全锚版；车道C 数据回填待续）

素材节点：海光=节点18（/opt/dtk-26.04.1+hyhal；hyfatbinary/hyptxas **not stripped with debug_info**）·天数=节点14（corex 三代镜像；死前战果=arch 码 ivcore11/20/30/40→cubin 4/6/8/10/JIT 图 3/5/7/9+生产 .so 内嵌同 magic fatbin 坐实）·沐曦=节点14（metax sglang 镜像，amd64 静态分析）。

| 维度 | NVIDIA CUDA 13.1（基线） | 海光 DTK 26.04 | 天数 corex 5.0 | 沐曦 MACA 3.8.2 |
|---|---|---|---|---|
| 编译器驱动 | nvcc（真编译器） | nvcc=**Perl 壳**→dcc（clang-17 fork，-dcccuda12）；**dccobjdump=cuobjdump 对应物（md5 级印证）；dccturing=SASS 反汇编→重编译往返（NVIDIA 无此能力）** | **nvcc=194 字节 bash stub**（只 cat CUDA 10.2 banner 骗 vllm/pip 探测）；真工具链=LLVM/clang-22+自研 `bi` 后端；ixobjdump 8.9MB=cuobjdump 对应物 | nvcc→**cucc**（bash 参数重写器→gomxccbin→mxcc，LLVM 19.1.3 fork） |
| fatbin 容器 | 16B 头 0xBA55ED50+64B entry kind{1,2}+zstd | HIP 双层（"HIPF" 0x48495046 wrapper+__CLANG_OFFLOAD_BUNDLE__+triple 字符串） | **16B 头布局照抄（fat_size@8 同位同义）但自研 magic 0x20160329**；entry=35B tag{02,arch,02} 无 kind；**"PTX"槽装 LLVM bitcode（0x4243C0DE）** | ClangOffloadBundle（公开容器；.mc_fatbin/.mcFatBinSegment 同名构） |
| 成员标识 | arch 数值字段 | triple `hipv4-amdgcn-amd-amdhsa--gfx906` | arch 码（ivcore11/20/30/40→4/6/8/10，JIT 图=−1） | triple `…--xcore1000/1500/1600`；-bc(bitcode)+native 二元性 |
| 设备码 ELF | CUBIN（NVIDIA） | AMDGPU hsaco（gfx926-938=**海光私有 EF_AMDGPU_MACH 0x81-0x84**） | **e_machine=0xf8/OSABI=0x42'B'**（BI=BigIsland 开山代号）；.note=ROCm msgpack 同款；kernel 描述符=AMD .amdgpu_kernel_code_t 换名；宿主嵌入段名 **.nv_fatbin/.nvFatBinSegment 与 NVIDIA 完全同名** | **e_machine=0xfd 私有**+kd 描述符+MessagePack kernel 元数据（HSA 血统） |
| PTX 路线 | ptxas（JIT=进程内 API） | **hyptxas=PTX→AMDGCN 跨编译器**（flex/bison+LLVM，cuda2gcn.bc 翻译桥；NVIDIA PTX 端到端实测成功） | **全栈无 PTX**；JIT=libcuda dlopen **libdynamiccompile.so 80MB**（含 sm_20→sm_121a 全表+2605 nvvm 串=**NVVM→ivcore 翻译层**） | **无 PTX 路线**（LLVM 直行） |
| CUDA 兼容 | —（本体） | 宿主 ABI 同名保留（__cudaRegister\* 族）+容器换 HIP | 941 导出/469 cu 族/cuModuleLoadFatBinary 在；定级≈CUDA 11.x；cudart `__ixRegisterFunction` 与 `__cudaRegisterFunction` **同址双名**；NVRTC 壳走 clang→llc→lld 子进程链，nvrtcGetPTX≡nvrtcGetCUBIN | **cu-bridge**：libsymbol_cu.so 733 CUDA 符号→libmcruntime |
| libcuda 形态 | 98MB 单体 | **拆三段**（220KB cu\* shim 对标 R560→libcudart 243KB→libgalaxyhip 12.4MB hipamd fork"galaxy"→HSA） | libcuda + 80MB libdynamiccompile（JIT 外置） | libmcruntime（cudart+driver 合体）+libmcimage 43MB |
| 架构代系 | sm_75…120 | gfx906+gfx926/928/936/938 扩展 | ivcore10(BI 已弃)/11(MR)/20(QS·QUASAR)/30(CQ·CONQUEROR)/40(BZ·BLAZER)；ivcore20+ 汇编"not disclosed" | xcore1000-2000；芯片 MXC280/290/500/550/588/600 |
| 注册 ABI | __cudaRegister\* 四件套 | 同名保留（.rela.text 实证） | 同名保留+ix 双名 | __mcRegister\* 四件套逐一对应 |

**三大派系定型（终判）**：①**NVIDIA 布局克隆派=天数**（16B 头布局/段名/.kd 机制照抄，magic 与内容自研，"ROCm 内脏+CUDA ABI 外壳+LLVM-22 bi 后端"杂交栈）；②**ClangOffloadBundle 派=沐曦+海光**（LLVM/ROCm 血统，海光加 HIP wrapper）；③**NVIDIA 私有演进派=本尊**（kind 扩到 TileIR 0x80+devcode 加密第六型，IR 层开源（cuda-tile）而容器格式仍闭源）。**兼容策略光谱**：沐曦全栈 cu-bridge 无感替换（733 符号）＞海光宿主 ABI 同名+容器换血＞天数 ABI 双名+布局级克隆。**中间层光谱**：NVIDIA=PTX 三吃（ptxas/TileIR/devcode）·海光=PTX 消费者（hyptxas 跨编译）·天数=无 PTX 但 JIT 吃 NVVM（libdynamiccompile 翻译层）·沐曦=纯 LLVM 直行。

**跨厂商端到端实测（车道B 战果，2026-11-06）**：NVIDIA PTX（语言头降级 8.5，上限≈CUDA 12.4）喂给海光 hyptxas → 成功产出 gfx906 AMDGPU ELF；IR 级铁证 `%ctaid`→`__hyd_sreg_ctaid` 逐指令直译——**PTX 作为事实跨厂商中间层的首次实机验证**。自研 hyfatbin_parser.py 抽取产物与官方 dccobjdump --extract-elf 逐字节同 md5。

**工具链能力差异三则**：①海光 dccturing 具 SASS（GCN）级反汇编→重编译往返能力，NVIDIA 工具链无对应物（nvdisasm 只读）；②海光 CUDA 兼容层年度零漂移（DTK 25.04→26.04 同 libcuda.so.560.35.03 精确对标 NVIDIA R560）；③海光 nvcc 是 Perl 脚本壳、沐曦 cucc 是 bash 参数重写器、天数 nvcc 是 194 字节 banner stub、NVIDIA nvcc 是真编译器——**四态驱动形态**。

### 9.4 天数 corex 全栈画像（work/corex/notes.md 8 节全锚定+samples 19 件 38MB）

**一句话定性**：**ROCm 内脏 + CUDA ABI 外壳 + LLVM-22 自研 bi 后端**的杂交栈；全栈不存在 PTX 格式。

要点：①工具链=LLVM/clang-22+bi 后端（libLLVMIluvatar\*.a 六件套+MLIR IXGPU/IXDL dialect），真前缀=ix（非任务书猜的 cx\*）；②fatbin 16B 头布局照抄（fat_size@8 同位同义）但 magic=**0x20160329**，自研 parser 拒收验证；③cubin e_machine=0xf8/OSABI=**0x42'B'**（BigIsland 开山代号），.note=ROCm msgpack 同款，kernel 描述符=AMD .amdgpu_kernel_code_t 换名（warp64、.kd）；④架构代系 ivcore10(BI 已弃)/11(MR)/20(QS·QUASAR)/30(CQ·CONQUEROR)/40(BZ·BLAZER)，ivcore20+ 汇编文本 "not disclosed"（仅 ivcore11 开放，助记符 30+ 条 sl_/ml_ 双命名空间 AMD GCN 方言）；⑤libcuda 941 导出/469 cu 族，定级≈CUDA 11.x；cudart `__ixRegisterFunction`/`__cudaRegisterFunction` 同址双名；⑥**JIT=libcuda dlopen libdynamiccompile.so 80MB**（含 sm_20→sm_121a 全表+2605 nvvm 串=NVVM→ivcore 翻译层）；⑦NVRTC 壳走 clang→llc→lld 子进程链（/tmp/ixrtc 日志实证），**nvrtcGetPTX≡nvrtcGetCUBIN**（2208B 字节级相同），选项透传 bug 三代皆在（须传 clang 原生 --cuda-gpu-arch）；⑧演进 4.3.6（有 PTXToLLVM）→4.4.0（clang-18 并入 libdynamiccompile）→4.5.0（clang-18→22 大跳删 ixAssembler，x86_64）→5.0.0（aarch64，bin 清单与 4.5.0 逐字相同）；⑨生产实态=libixattnbkd 24/29/29 枚 fatbin 全部 ivcore11 单 entry AOT（零 JIT 图），libcublas/cudnn 为天数自产。

通信层四栈（nccl 2.23/ixccl 2.28.9 天数/mccl 2.16.5 沐曦/rccl 2.22 海光）能力面矩阵见 multivendor-gpu-comms skill（2026-11 真机实证）。
