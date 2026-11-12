# NVIDIA/DeepLearningExamples 全链知识库（understand 战役第 2 夜 · DLE 仓收官）

> 本地仓 `/usr-data/data2/repos/agent-repos/NVIDIA/DeepLearningExamples`；战役台账 `agent-repos/deepwiki-batch/understand-nv-a-layer.md`。

## 状态表（2026-11-05 全链 ✅）

| 阶段 | 结果 |
|---|---|
| scope | 2826→854 文件（PyTorch 主线+Tools 374+CUDA-Optimized 114+Kaldi/MxNet/JAX 残部；TF/TF2/Paddle/SpeechSynthesis 等 16 顶层目录全裁） |
| prepare | ✅ 854 文件/96 批（11-04） |
| 批分析 | ✅ 96/96（11-05 11:00–21:0x，4 并发滚动，1302×1 复活零损失，1308×1 死前落盘+复活零损失） |
| merge | ✅ 2072n/4638e（31 悬空边归因：23 前缀错位手工回补 + 8 hubconf→scope-cut 真缺诚实丢弃钉版） |
| layers/tour | ✅ 16 层/16 步/869 file 节点全覆盖零重复 |
| finalize | ✅ 双 validator 0 issues 0 warnings，fingerprints 854@729963dd |
| onboard | ✅ ONBOARDING 7185 字（不计空格）8 节 |
| explain | ✅ 12 篇合计 52994 字符（不计空格口径），251 行号锚，抽验 10/10+22/25 全 PASS |
| 图谱位置 | 仓内 `.understand-anything/knowledge-graph.json`（2.36MB） |

## 产物索引

- `onboarding/ONBOARDING.md` — 8 节上手指南
- `explain/01-联邦骨架与torchhub入口.md` … `explain/12-TSPP-Hydra配置联邦与插件群.md` — 12 篇精讲（每篇六节：角色定位/内部结构/外部连接/数据流/设计决策/新人提示）
- deepwiki 基座见 `讲透NVIDIA/DeepLearningExamples/deepwiki/`（前置轮产物）

## 勘误清单（源码级实证，README/文档 vs 磁盘事实）

**上游文档失真**
1. README:585 示例 `overrides=tft/electricity/best_0` 与磁盘 `conf/overrides/electricity/tft/` 顺序相反（陈旧笔误，两 worker 独立发现）
2. README 描述的 `model.py` 磁盘不存在（实为 `modeling.py`）
3. triton/README 的 `../readme.md` 断链（磁盘为 `BERT/README.md`，大小写不一致）
4. README 未收录 Transformer-XL 于 NLP 表格；`data/dataset.py`→`datasets.py` 单复数漂移；`script_preprocess_data.py`/`script_generate_sine.py` 磁盘不存在
5. getdata.sh L48 回显 "WikiText-103 (WT2)" 上游笔误

**死代码/死配置**
6. `bart/lamb.py` 全仓零 import——未接线参考实现（真实训练走 apex FusedMixedPrecisionLamb，training_base.py:37/149）
7. `bert_attn.py` 孤儿片段：双 `__init__`（L18 空体被 L26 覆盖）+ 零 import 不可独立运行
8. `multi_tensor_lamb_out.cu` 451 行未列入 setup.py 编译源=未编译变体
9. TextSharding `is 0`/`is not 0` 字面量比较（Py3.8+ SyntaxWarning）；NLTKSegmenter 构造器 `__init` 缺尾下划线永不执行
10. bertPrep `create_tfrecord_files`/`wikicorpus_zh` 入口即 `assert False` 存根；`nltk.download('punkt')` 模块导入即联网
11. `linear_space` 导出零调用孤儿函数；config_xsum `student_*` 蒸馏死字段（HF 拷贝残留）
12. `.dockerignore` 七行排除模式全部无匹配（LM-TFM* 为前身仓库名，历史遗留防御性排除）

**潜伏 Bug（上游真实缺陷）**
13. `distillation/utils/data_utils.py:93` 裸名 `input_files`（应为 `config.input_files`）——num_files<world_size 时 NameError
14. `run_e2e_distillation.sh` L143 phase2 命令缺续行符
15. `perf_analyzer` `_faild_with_measruement_inverval`（函数名三处拼错）`str.find` 返回值做 `or` 判断——-1 为真值，第一段检测不可达
16. `dump.py` 调 `np.narray`（不存在，`np.array` 笔误），四复制件同错
17. `compute_wer.sh` L10 引用未定义变量 `$test_set`（展开空串）
18. `ValidateModelConfig` L343-354 数据类型报错文案与实际检查串位（复制粘贴 bug）
19. `module.py:40`/`perf_infer.py:44` `except ImportError` 仅构造异常未 raise，apex 缺失被静默吞
20. `hparam.py` `yaml.load_all` 无 Loader 参数（PyYAML≥6 报错）；`librosa.output.write_wav` 0.8+ 已移除；`distutils.LooseVersion` Py3.12 移除隐患
21. G2ANet 索引越界 + `i_weights` unbound；marl_train attention="iga" 默认值直接 ValueError（合法值仅 igs/g2anet）

**vendored 血统（Facebook/Meta 版权头实证）**
22. hydra_optuna_sweeper（v1.3.0.dev0）、hydra-joblib-launcher、hydra-torch-distributed-launcher（NVIDIA 改造=torchrun API+fork 硬编码）、hydra_multiprocessing_launcher（"Hydra loky Launcher" 命名不一致）——四插件全 vendored
23. tacotron2=上游内嵌拷贝（BSD 头）；TSPP models/tft.py←google-research/tft、ema.py←rwightman（NOTICE 实证）
24. torchrun launcher 仓内双拷贝并存（`hydra_torchrun_launcher/` 完整版 vs `distributed_launcher/` namespace 包版），Dockerfile L70 装的是后者
25. `conf/hydra/` 下无 sweeper 配置——sweeper 本体由 examples/hp_search.sh CLI 侧指定；真正消费 sweeper.params 的是 vendored 包内 `optuna_sweeper.py:11/:42` 而非顶层同名抽象接口

**变体同构（md5/diff 实证）**
26. BERT triton 三变体 `__main__.py` 逐字节相同（数据面变体非代码分叉）；docker 三变体脚本逐字节相同
27. 四份 per-GPU config YAML 两组 md5（A30==T4 / DGX-1==DGX-A100，按显存档非架构代际）；四份 hardware YAML（dist6l）逐字节全同
28. `wt103` train 系列 4 脚本前 52 行 md5 同构（差异仅尾部参数）；N-HiTS 搜索网格跨数据集 md5 等价复用
29. `Adam.yaml`=apex FusedAdam，`TorchAdam.yaml` 才是 torch 原生（参数体逐字镜像）——同名误导
30. `nhits_v2/` 目录=第二轮 HPO 目录非模型组（组选项不存在，模型选择仍走 `model=nhits`）

**Hydra 机理钉版（TSPP 深水区）**
31. `@_global_` 扁平注入不能携带组级 defaults——故 best_* 内联 criterion/quantiles 块=组装配结果逐字固化（上游注释"IDK how to do a proper subtree substitution"自证 workaround）
32. wt103_large.yaml `train_multinode` 双 `<<` merge key=YAML1.2 core schema 重复键错误根源（PyYAML FullLoader 实测正常，第一重冗余无害）
33. `optional model_dataset@_global_: ${model}_${dataset}` 组合不存在时静默跳过（tft_pems_bay_enc24 等 6 组合落空实证）
34. `models/tft_pyt/` 仓内不存在——README L158 指示用户手动拷贝，lstm.py/mtgnn.py 的 TFT import 双双悬空；TFDEmbedding/LazyEmbedding 符号仅存于源头（Forecasting/TFT 被 scope-cut）
35. `hp_search` 的 `graph:true`（布尔）与 pems_bay.yaml `graph:graph.bin`（字符串，datasets.py:732 os.path.join）类型不兼容历史残留
36. 搜索期预算 1e5 样本/15epoch vs best_* 重训 1e6/30 两阶段流程；`+trainer.config.ema_decay`/`cl_update` 均为 `+` 前缀注入新键（基组无此键，最终消费方 trainer.py:134 `config.get` 默认值）

**基础设施/杂项**
37. `run.sub`=SLURM sbatch 脚本（#!/bin/bash+#SBATCH）非 HTCondor .sub
38. `.d` 文件=nvcc -M 依赖清单非 D 语言；`.o/.so`=ELF、`.wav`=RIFF（含 16 个推理输出工件）被 scanner 误标 code 已纠偏
39. `run_pretraining.sh` 的 `preprocess_bert_pretrain`/`balance_dask_output` 为外部 lddl 包入口非仓内文件；`requirements.txt` L12 `data` 可疑依赖条目（PyPI 无主流同名包）
40. `.version`=deployment_toolkit 0.7.11 勿与 model_navigator v0.2.7 混淆；`bert_configs` base vocab=30528 vs large 30522 双口径；pyproject towncrier template 悬空（上游拷贝残迹，joblib/multiprocessing 两插件同款）
41. Kaldi 容器路径 `/workspace/scripts↔仓内 scripts` 映射由两 Dockerfile `COPY scripts` 钉版；`-t CTM` 选项 getopt 仍解析但 Usage 已注释（半禁用）
42. hubconf.py 8 条 torchhub imports 指向 scope-cut 裁出目录（SSD/ConvNets/GPUNet/Tacotron2/waveglow/HiFiGAN×2/TFT）——磁盘存在但图谱口径外，诚实丢弃不改 scope 边界

## 质量口径

- 锚终验口径=不计空格字符；explain 单篇 3264–4775；抽验组1 28 处两轮全 PASS、组2 25 处（22 直过+2 范围锚假阴性+1 真错已修）
- scanner 盲区补偿账：shell/YAML/JSON/bash 连字符函数名/纯声明 C 头/.cuh 五类全手扫（Python AST 重扫 1:1 对账零缺口）；Hydra 七类锚点方法学（_target_ 内联/组选项/装配链/optional 注入总锚/resolver 条件链/sweeper 网格 md5/最强证据搜索空间归属）
- 原仓零污染（全程只读，git status 仅流水线自产物）
