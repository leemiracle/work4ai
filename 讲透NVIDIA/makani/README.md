# 讲透 NVIDIA/makani

Makani（夏威夷语"风"）：AI 天气/气候模型大规模并行训练库——FourCastNet3/SFNO/HENS-SFNO/FourCastNet1 的训练基座（README.md:9）。

## 全链状态表

| 产物 | 状态 | 位置 |
|---|---|---|
| DeepWiki | ✅ 全量 | `deepwiki/` |
| understand 图谱 | ✅ 680n/1606e/14层/16步，validate 0 issues，fingerprints 231@3fdeb7a6 | 仓内 `.understand-anything/knowledge-graph.json` |
| ONBOARDING | ✅ 8 节 | `onboarding/ONBOARDING.md` |
| explain | ✅ 4 篇 | `explain/01~04` |
| 源码 | 本地 `/usr-data/data2/repos/agent-repos/NVIDIA/makani`，HEAD `3fdeb7a6` | — |

explain 索引：01 Driver 与四 Trainer · 02 模型动物园 SFNO 与 Pangu 复现 · 03 mpu 分布式与损失家族 · 04 数据后端与 Preprocessor2D。

## 关键事实速览

- Driver 总控（driver.py:61，1098 行）+ 四 Trainer（Trainer:807 / EnsembleTrainer:788 / StochasticTrainer / AutoencoderTrainer）+ Inferencer（917 行）+ rollout_buffer（1572 行，O_DIRECT/GDS）
- 旗舰 FourCastNet3：Disco 连续编解码 + 神经算子块（fourcastnet3.py:108/:248/:650，1186 行）；SFNO 是 FCN2/HENS 主力（sfnonet.py:438）
- 并行三轴：通道（fin/fout）、空间（h/w）、集成（README.md:48-50）；mpu 自制栈 mappings/halo/layers（544/406/1091 行）
- 损失=评分函数代码化：CRPS 家族 1196 行、能量分数家族 997 行、LossHandler 550 行；test_losses.py 4282 行 31 类锁语义
- 容器级 GDS：Dockerfile:41 HDF5 ENABLE_DIRECT_VFD + :49 H5PY_DIRECT_VFD=1 h5py==3.16.0

## 勘误清单（源码级实证，≥6 条）

1. **本仓非 HPC 网络测试工具（任务书推翻）**：全仓无网络基准/nccl-tests 类代码；实为 ML 天气/气候模型训练库（README.md:1"Massively parallel training of machine-learning based weather and climate models"），"makani=风"指天气。
2. **`parse_dataset_metada.py` 文件名拼写缺 't'**：文件名是 metada，函数名 `parse_dataset_metadata`（:22）正确——五 CLI 入口的 import 都指向这个错名文件（train.py:28 等），改名会破坏所有调用方，属钉版历史遗留。
3. **LossHandler 不在 losses/ 目录**：在 `makani/utils/loss.py:58`（550 行）；`utils/losses/` 放的是各损失家族实现，两处别混。
4. **"Welford CUDA 核"实为 @torch.compile 融合核**：mpu/layer_norm.py:55 `_welford_kernel` 挂 `@torch.compile` 装饰器，非手写 CUDA 源码；说"自制 CUDA kernel"不准确。
5. **"metadata.json regex 回退"需拆成两件真事**：regex 在 ICON 后端文件名时间戳解码表（icon.py:150-153 `_DATE_PATTERNS`）；metadata 坐标缺失时的回退是按 grid_type 重建纬经度（parse_dataset_metada.py:50-62），与 regex 无关——两件事常被并成一句讹传。
6. **四 Trainer 不是并列继承 Driver**：`EnsembleTrainer`（ensemble_trainer.py:62）继承确定性 `Trainer`（deterministic_trainer.py:62，且类名就叫 Trainer，无 DeterministicTrainer 类名）；只有 Stochastic/Autoencoder 直接继承 Driver。
7. **grid_type 从"默认 equiangular"改为强制必填**：parse_dataset_metada.py:37-45 注释钉版旧默认"对每个非 equiangular 数据集都静默出错"，现在缺声明直接 ValueError。
8. **flexible checkpoint 恢复优化器状态仍是实验性**：README.md:199 明言换并行配置恢复目前只稳模型权重，优化器/调度器状态恢复不保证。
9. **FourCastNet3 的 OOM 多为 torch 内存池碎片**：README.md:231 给环境变量缓解法，不是模型显存不够；inductor 编译 DISCO 卷积撞 recompile 上限时 makani 已把 torch 默认 8 提到 32（README.md:243）。

## 相关产物

- `deepwiki/`：DeepWiki 全量页；批阶段甄别笔记见仓内 `.understand-anything/NOTES-DIGEST.md`（GDS 一条：Dockerfile H5PY_DIRECT_VFD=1）
- 图谱 16 步导览与 ONBOARDING 8 节对应；tests/distributed/ 十专题与 CI 四工作流（style/test_serial/tests/test_distributed）的映射见 ONBOARDING §8
