# 讲透 NVIDIA/tilus

> NVIDIA 开源的 tile 级 GPU kernel 编译型 DSL：Python 类 → Tilus IR（布局自动推断）→ Hidet IR → CUDA C → NVCC。线程块粒度、张量一等公民、1-8bit 任意位宽低精度；Blackwell/Hopper/Ampere 三代支持；ASPLOS'26（arXiv:2504.12984）。
> 分析基线：commit `20474568`（2026-10-23）· 671 文件 · tilus v0.2.x

## 全链状态表

| 阶段 | 状态 | 产物 |
|---|---|---|
| DeepWiki | ✅ 24/24 TRUE_100（2026-10-26 终判） | `deepwiki/`（INDEX + 24 页） |
| understand 图谱 | ✅ 2782 节点 / 7099 边 / 14 层 / 15 步导览 · validator 0 issues · fingerprints 671 文件@20474568 | 仓内 `.understand-anything/knowledge-graph.json` |
| ONBOARDING | ✅ 8+2 节 · ≥5000 字 · 60+ 行号锚（全部源码实证） | `onboarding/ONBOARDING.md` |
| explain | ✅ 5 篇 · 六节结构 · 每篇 12+ 锚 | `explain/01-tilus-script与DSL.md` ～ `05-发射器与tcgen05.md` |
| 勘误 | ✅ 12 条（下节，全部行号实证） | 本文件 |

## 讲透地图（一句话版）

- **01 DSL**：没有 `@tilus_script` 装饰器——是 `class K(tilus.Script)` 类子类化 + `autotune` 装饰器；`Script.__new__` 直接返回 InstantiatedScript（缓存句柄）。
- **02 布局推断**：RegisterLayout = local×spatial×replicated 代数；45 条逐指令规则 + 手工调优的全局优先级表（order.py），贪心逐条应用到不动点，失败响亮抛错。
- **03 IR 与变换**：InstStmt 包指令进语句树；functional 判定是 DCE 里的显式 allowlist；默认 12 pass 中布局推断跑两遍。
- **04 hidet 基座**：fork 内嵌 hidet v0.6.1 全套（IR/30 pass/codegen/NVCC/自带 DSL）；任意位宽低精度在 lower_subbyte_type 等 pass 落地。
- **05 发射器**：(指令, target) 二维注册表 + 资源上下文族；tcgen05 = TMEM 第四存储层级 + 双描述符位域编码（smem/mma inst descriptor）。

## 源码实证勘误（12 条，均行号核对 @20474568）

1. **没有 `@tilus_script` 装饰器**。API 是类子类化 `class MyKernel(tilus.Script)`（`python/tilus/lang/script.py:41`；官方文档 `docs/source/programming-guides/tilus-script.rst:8` 同款定义）；`python/`+`tests/`+`examples/` 全仓零处 `tilus_script`。图谱摘要"tilus.lang 入口导出 tilus_script 装饰器"失实——`python/tilus/lang/__init__.py:15-16` 仅导出 `Class/Attributes/Script`；`autotune` 才是装饰器（`python/tilus/lang/script.py:106`）且从 `python/tilus/__init__.py:102` 导出。
2. **DotInstEmitter 不按架构分派 wgmma/tcgen05**。它只发 warp 级 `mma_sync_v2`（`python/tilus/backends/emitters/cuda/mma_dot.py:99`）；Hopper/Blackwell 是**独立 IR 指令**（`python/tilus/ir/instructions/cuda/wgmma.py:59` WgmmaMmaSSInst、`python/tilus/ir/instructions/cuda/tcgen05.py:143` Tcgen05MmaSSInst）配独立发射器（`python/tilus/backends/emitters/cuda/wgmma.py:115`、`python/tilus/backends/emitters/cuda/tcgen05/mma.py:199`）。图谱"按目标架构分派 mma.sync/wgmma/tcgen05"说法不成立。
3. **布局推断协议没有 forward/backward**。`python/tilus/ir/layout/inference/rule.py` 只有 `LayoutValidationRule.validate`（:37）与 `LayoutInferenceRule.inference`（:56）两个静态方法协议；图谱摘要"forward/backward 双向推断协议"在该版本不存在。
4. **functional 判定的 allowlist 不在 ir/inst.py**。CLAUDE.md 把它写在 Instruction 条目下（CLAUDE.md:35），实际落点是 `python/tilus/transforms/dead_code_elimination.py:76`（`FUNCTIONAL_INST_TYPES`）+ :129（isinstance 判定）；`ir/inst.py` 本体无 is_functional。
5. **let 传播文件名拼错**：`python/tilus/transforms/let_propogation.py`（propogation），函数名却是 `let_propagation_pass`（`python/tilus/transforms/__init__.py:23` 导入行两拼法同框）。
6. **CopyAysnc 类名拼错**：`python/tilus/backends/emitters/cuda/cp_async.py:42,200,206` 三个 `Aysnc`；下游 `python/tilus/backends/emitters/cuda/cp_async_bulk.py:58,237` 还混用 `CopyAysncBaseEmitter` 基类名。
7. **hidet 文件名拼错**：`python/tilus/hidet/transforms/lower_affine_to_recurence.py`（recurence）；函数名 `lower_affine_to_recurrence_pass` 拼写正确（`python/tilus/drivers.py:127` 导入）。
8. **tcgen05 描述符字段名拼错**：`python/tilus/backends/emitters/cuda/tcgen05/mma.py:75,91,109` 的 `maximim_shift_in_ws`，PTX 文档字段为 maximum_shift_in_ws（类 docstring :61 自己引了官方链接，字段名却没对齐）。
9. **布局推断 pass 在默认管线跑两遍**：`python/tilus/transforms/__init__.py:31` get_default_passes 中 lower_load_store 前后各一次——图谱与文档单数口径（"Tilus 管线中自动布局的阶段化入口"）漏了第二遍。
10. **发射器解析顺序敏感**：`resolve_inst_emitter` 沿 REGISTRY 迭代序取第一个匹配父类即 break（`python/tilus/backends/codegen.py:124-131`）——不是完整 mro 精确匹配，注册顺序（barrel import 顺序）参与解析语义，新增指令父类时需留意。
11. **`examples/matmul/index.rst` 是 0 字节空占位**（NOTES-DIGEST 亦钉版）；Ampere matmul 教程真身在 `docs/source/tutorials/` 与 `examples/matmul/matmul_v0~v5.py`。
12. **HIP/CPU 后端是 fork 遗产非可用目标**：`python/tilus/hidet/backend/codegen.py:1045,1115` 的 HIPCodegen/CPUCodegen 与 `emitters/cast.py` 的 AmdgpuCastInstEmitter 均为 hidet v0.6.1 携带/占位，tilus 实际仅面向 CUDA（README 安装说明与 CI 矩阵均只含 NVIDIA GPU）。

## 产物索引

```
讲透NVIDIA/tilus/
├── README.md                 # 本文件（状态表+勘误+地图）
├── deepwiki/                 # 24 页全量（INDEX.md + _coverage-check.md）
├── onboarding/ONBOARDING.md  # 上船指南（10 节，60+ 锚）
└── explain/
    ├── 01-tilus-script与DSL.md
    ├── 02-布局推断族.md
    ├── 03-IR指令与变换.md
    ├── 04-hidet基座与pass.md
    └── 05-发射器与tcgen05.md
```
