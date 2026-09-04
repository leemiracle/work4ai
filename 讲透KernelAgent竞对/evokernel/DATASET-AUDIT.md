# EvoKernel 数据集审计报告（DATASET-AUDIT）

> 审计日期：2026-09-03 · 审计方式：全量脚本统计（/tmp/opencode/evk_audit.py 逻辑固化于本报告）· 对应 git commit `af61b2a`

## 1. 总量核对

| 集合 | manifest 声明 | 磁盘目录数 | 一致 |
|---|---|---|---|
| ops-attention-910b | 58 | 58 | ✅ |
| ops-mhc-910b | 15 | 15 | ✅ |
| ops-kernelbench-910b | 165 | 165 | ✅ |
| ops-attention-cuda-ncu | 79 | 79 | ✅ |
| ops-kernelbench-cuda-ncu | 250 | 250 | ✅ |
| **合计** | **567** | **567** | ✅ |

另有 `ops-exports-bundle.zip`（上述五目录的打包归档）。pytorch-references：Attention 79 / MHC 15 / KernelBench L1 100+L2 100+L3 50（与 README 声明一致）。

## 2. 质量画像（manifest summary）

| 集合 | compiled_rate | correctness_rate | faster_than_baseline | 迭代中位(outer×inner) |
|---|---|---|---|---|
| attention-910b | 100% | **100%** | 0 | 18×1 |
| mhc-910b | 66.7% | **66.7%** | **6/15** | 30×1 |
| kernelbench-910b | 100% | **100%** | 0 | 24×1 |
| attention-cuda-ncu | 100% | **97.5%** (77/79) | — | 22×1 |
| kernelbench-cuda-ncu | 100% | **100%** | — | 18×1 |

全体 outer×inner 迭代量级：median 21 / max 39 / min 1（n=567）。

**关键观察**：
1. **导出=存活者偏差**：五集合全是「筛选后导出」（compiled=true 才入集），attention/mhc/kernelbench 910B 与 kernelbench-cuda 达 100% 正确——不能据此推断生成器真实成功率。
2. **MHC 是唯一带价值标签的集合**：result.json 含 `mean_ms/baseline_mean_ms/speedup_vs_baseline/log2_speedup_vs_baseline/relative_change_pct`，且 6/15 超过 baseline——这是「值驱动检索」(value-driven memory) 论文主张的直接证据载体。
3. **faster_than_baseline=0 的三集合**：performance.mean 只是绝对时延（且跨集合口径不一：attention-910b 毫秒级 0.67-30ms，kernelbench-910b 出现 2181ms 级——疑为整模型前向或不同计时单位），无 baseline 对照字段，做跨集合比较前必须逐 result.json 校准口径。
4. **inner_iter 恒为 1**：迭代预算全在 outer 循环（median 18-30 轮），与论文「continual refining」的 refine 预算一致。

## 3. Schema（两种 result.json 变体）

- 通用版：`kernel_project_name / outer_iter / inner_iter / compiled / correctness / performance{mean,std,min,max,num_trials}`
- MHC 版：`... / mean_ms / baseline_mean_ms / speedup_vs_baseline / log2_speedup_vs_baseline / relative_change_pct`

每 kernel 目录布局：
- 910B：`op_host/(实现名).cpp + _tiling.h`（host 侧 tiling 策略）+ `op_kernel/(实现名).cpp`（device 侧）+ `CppExtension/csrc/op.cpp`（PyTorch 桥接）+ `result.json` + 同名 `.json`（导出元数据）
- CUDA：`best_code.py`（NCU 迭代选优最终产物）+ `result.json`

## 4. 复用建议（面向 hpc-agent 的迁移定律实验）

- `ops-kernelbench-cuda-ncu` 的 250 个 best kernel + `pytorch-references/KernelBench` 任务对 = 现成的「源级配置记忆」素材池（对应 TRANSFER-LAWS v1.0 的 L 档做法）。
- MHC 15 例的 speedup 字段结构 = 小样本价值标注参照。
- 910B 集合 = 跨 ISA（CUDA↔Ascend）迁移假设检验的非 NVIDIA 旁证数据（与仓内已知的 15 MHC Ascend kernels 一致）。
- ⚠️ 采集成本警告：全集 567 kernel 若逐个编译评测需真实 NCU/GPU 环境；本审计只做静态统计，未执行任何 kernel。
