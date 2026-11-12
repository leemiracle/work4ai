# 讲透 Ising-Decoding（NVIDIA 量子纠错 AI 预解码器训练配方）

> 仓：NVIDIA/Ising-Decoding @ea7c1bb（2026-10-16）· understand-anything 全链知识库 · 2026-11-08 生成
> 定位：量子纠错（QEC）decoders 的 AI 训练配方——神经网络消费 Stim detector syndromes 时空数据预测修正（预解码），PyMatching（surface code）/Chromobius（color code）做全局解码收尾；两篇论文（Surface 2026-04 / Color 2026-07），预训练模型发布于 HuggingFace（SurfaceCode-1-Fast/Accurate、ColorCode-1-Fast）。单一用户配置 conf/config_public.yaml + 单一 runner 驱动两码族。

## 全链状态表

| 阶段 | 状态 | 指标 |
|---|---|---|
| 批分析（16 批） | ✅ | 1150 节点 / 2414 边（imports 251 = scanner 225 + ast/手扫补 26） |
| 终验+merge | ✅ | assembled 1150n/2395e（55 规范修正 + 2 contains 前缀错位处置 + 5 complex 真值还原） |
| layers/tour | ✅ | 12 层 / 14 步导览，1150/1150 全覆盖零重复 |
| finalize | ✅ | validator 0 issues 0 warnings · fingerprints 210 文件 @ea7c1bb3 |
| onboarding | ✅ | 7959 字（不计空格）/ 8 节 / 52 锚（终验 54/54 好） |
| explain | ✅ | 5 篇 / 17395 字 / 136 锚（终验零真坏，2 短名锚消歧命中） |

图谱在仓内 `.understand-anything/knowledge-graph.json`（1150n/2395e）。字数口径=不计空格字符。另有 deepwiki/（L0 层，先前行产物）。

## 产物索引

- [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md)——新人 8 节入门：QEC 预解码器定位/技术栈（Py3.11+PyTorch+Stim+PyMatching+Chromobius+cuStabilizer、Hydra、cu12/cu13 双轨、Docker/SLURM）/目录地图/核心链路（run.py→三生成器→predecoder→LER）/数据流/6 设计决策/14 步路径/11 条坑
- [explain/01-workflows编排与配置体系.md](explain/01-workflows编排与配置体系.md)——config_public.yaml 双族切换、run.py run_color/run_surface 编排与 11 模块延迟 import、10 个 Hydra conf 关系（3448 字/26 锚）
- [explain/02-QEC核心库两码族.md](explain/02-QEC核心库两码族.md)——surface/color 两族 memory_circuit 双继承链、HE 三版本（1497/1275/3362 行）、dem_sampling cupy+cuStabilizer、augmented-DEM 管线（3496 字/28 锚）
- [explain/03-数据管线与生成器.md](explain/03-数据管线与生成器.md)——datapipe_stim/_color、generator_torch_color、DatapipeFactory 版本分发、superbatch、Stim→DEM→超批数据流（3480 字/30 锚）
- [explain/04-模型训练评测链.md](explain/04-模型训练评测链.md)——Cascade 模型双参数口径钉版、train.py 三生成器、LER 评测族、failure_analysis 1311 行、三胞胎结果模块（3498 字/26 锚）
- [explain/05-导出基准与测试防线.md](explain/05-导出基准与测试防线.md)——safetensors/ONNX/CUDA-Q 导出线、集群脚本 PREDECODER_ 前缀契约、三层测试分层、CI cu12/cu13 矩阵（3473 字/26 锚）

## 甄别精选（流水线实证，均源码核实）

**双码族结构与勘误（explain 写手推翻任务书 4 处，源码为准）**
1. homological_equivalence 三版本：**1497 行在 code/qec/color_code/**（非 surface），surface 版 1275 行，surface 的 _torch 版 3362 行才是全仓最大单文件。
2. "项目内唯一继承链"不成立：**两条 MemoryCircuit→Circuit 继承链**（surface: Circuit L332=20 方法/MemoryCircuit L794=4 方法；color: Circuit L424=23 方法/MemoryCircuit L949=10 方法）。
3. run.py 延迟 import 实为 **14 行 import/11 个模块**（run.py:216/226-228/288/322/363-364/452-453/534-535/726/742），非 9 条。
4. data_mapping.py 在 **code/qec/surface_code/** 非 code/data/；4 处函数体内延迟 import SurfaceCode 在 :197/316/441/532。
5. 语义错位：triangular_color_code_circuit（surface_code/memory_circuit.py:1236）是 color code 电路构建器却物理位于 surface_code/ 目录；color_code/memory_circuit.py:26 注释证其为 legacy。
6. color 版 homological_equivalence.py:116 自署 "Author: AI Assistant (based on surface code HE by Muyan Li)"——AI 辅助移植的内部自白。

**配置与模型口径**
7. 双参数口径钉版：2.94M=论文 Model B（registry.py:67 _MODEL_B_OVERRIDES embed_dim=512/num_blocks=6）；25,397,764=公开发布 d17 accurate 配置（embed_dim=1024/num_blocks=12，契约测试 test_color_accurate_model_contract.py:27 硬读 yaml）——同一 Cascade 类两套配置，非矛盾。
8. fp8 勘误：conf yaml 自述 fp8 仅指导出精度、训练跑 fp32（config_qec_decoder_r9_fp8.yaml:18 原文）。
9. hydra.main 默认 config_name="config" 是占位（conf/ 无 config.yaml），实际由 local_run.sh:56 CONFIG_NAME:-config_public 传入；公共配置 lr 硬编码（color 1e-5/surface 按 model_id 查表）用户不可覆盖。

**工程惯例与陷阱**
10. deferred-import 全仓惯例：benchmark/test 的 repo 内 import 全在函数体内+sys.path.insert(0,'code')，scanner 全盲（b15/b16 实证，测试批 batchImportData 全空是真因）；qec/precompute_dem.py:2189-2191 延迟 import 规避循环依赖（源码注释明示）。
11. stdlib 撞名：code/training/logging.py 的 `import logging` 被 scanner 误报自引用；utils.py dict_to_device L177/L186 重复定义后者覆盖前者。
12. precompute_frames.py 名不副实：legacy 已被 qec.precompute_dem Torch augmented-DEM 管线取代，仅存两个 config loader（docstring L18-21 自述）。
13. 三层测试分层：code/tests/mid/ 无 __init__.py 是机制的一半（short discover 天然收不到 mid，README_TEST_TIERS.md:23）；README_TEST_TIERS L43 的 test_homological_equivalence 实际在 mid/ 而非 tests/。
14. 孤儿测试：test_training_progress.py 的被测脚本 training_progress.py 不在仓内（skipTest 守卫休眠）；test_tensorrt_fallback.py:74 不导入 logical_error_rate.py 仅镜像其 TRT 导入语义做契约断言。
15. evaluation 三胞胎：color_chromobius_timing/color_sdr/color_threshold_results 同构（lock+normalize+merge+append）。
16. 集群线：local_run.sh L79-84 只认 PREDECODER_ 前缀（忽略裸 BASE_OUTPUT_DIR/LOG_BASE_DIR）；offline_smoketest 默认权重 models/*.pt 目录仓内不存在（脚本防御跳过）；train-cu13 是 NCCL 2.28.9 多卡 SIGSEGV 规避路径；ci-gpu.yml:59/89 cu128/cu130 矩阵。
17. measure_d9_ler.py 自述 "Not run by CI"（LER 阈值校准脚本非测试）。

## 图谱分层（12 层）

CI/容器(8 文件) → 文档依赖(13) → Hydra 配置(10) → QEC 共享基座(62) → Surface Code(117) → Color Code(70) → 数据管线(25) → 模型训练(74) → 评测基线(112) → 工作流导出(34) → 基准脚本(96) → 测试 Cookbook(529)
