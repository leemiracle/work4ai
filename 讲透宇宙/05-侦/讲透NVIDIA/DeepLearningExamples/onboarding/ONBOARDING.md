# NVIDIA/DeepLearningExamples 新人上手指南（ONBOARDING）

> 图谱基线 `729963dd`，行号锚均经源码核实。

## 1. 一句话定位与全景

**这是"示例联邦"而非统一工程**：几十个互不相干的深度学习示例并排放在顶层，跨域依赖几乎为零，没有统一构建系统——每个顶层目录就是一个独立小仓，没有总 main。

三个全局事实：

- **顶层 README 支持矩阵是唯一全仓导航**（README.md:16 起）：Models × AMP/Multi-GPU/Multi-Node/TensorRT/ONNX/Triton/DLC/NB 八列四表，选示例先查它。
- **hubconf.py 是联邦粘合层**：hubconf.py:4 起逐条 `from X import nvidia_y` 注册十余个 torch.hub 模型，每条 import 伴 `sys.path.append` 注入子目录路径。
- **FasterTransformer/ 与 JAX/ 是外迁 stub**：前者仅 3 行迁移公告；后者全是指向 Rosetta（JAX-Toolbox）的外链，本仓无代码。

## 2. 仓库布局地图

图谱共 16 层，按域速览（路径相对仓库根，文件数为图谱口径）：

| 域 | 路径 | 文件 | 一句话 |
|---|---|---|---|
| BERT 主线 | `PyTorch/LanguageModeling/BERT` | 53 | 旗舰：九任务头+预训练/GLUE/SQuAD 微调+LAMB 优化器栈 |
| BERT 数据 | `BERT/data/` | 14 | bertPrep.py 五阶段：下载→格式化→NLTK 分片→HDF5 |
| BERT 蒸馏 | `BERT/distillation/` | 21 | 中间态+任务级蒸馏，产出 4L/6L 小模型 |
| BERT Triton | `BERT/triton/` | 117 | 推理服务化样板：toolkit+runner+三尺寸模型仓 |
| BART | `PyTorch/LanguageModeling/BART` | 63 | 生成式对照：span-corruption+Lightning+ROUGE/BLEU |
| Transformer-XL | `Transformer-XL` | 46 | 跨段记忆+相对位置注意力；五优化器、双 AMP |
| FastSpeech | `CUDA-Optimized/FastSpeech` | 115 | 并行 TTS，vendored tacotron2/waveglow+TRT 子树 |
| Kaldi | `Kaldi/SpeechRecognition` | 38 | 唯一 C++ 主场：约 1200 行流式 ASR 后端 |
| MxNet | `MxNet/Classification/RN50v1.5` | 16 | 非 PyTorch 对照：DALI+Horovod |
| TSPP | `Tools/PyTorch/TimeSeriesPredictionPlatform` | ~375 | 时序预测平台，最复杂子系统 |

根骨架（hubconf.py/总 README，11 文件）见第 1 节；其余顶层（TensorFlow/TensorFlow2/PaddlePaddle/DGLPyTorch 等）属图谱 scope-cut 外历史区域。

## 3. 核心链路走读（BERT 训练→数据→推理，tour 步 1-6）

**(1) 模型积木库**：`modeling.py` 从 `BertConfig`（modeling.py:168）垒出全套积木与 MLM/NSP 头，九任务头（GLUE/SQuAD/SWAG）同文件组装。

**(2) 训练入口**：`run_pretraining.py`＝LDDL HDF5 流式预训练+FusedLAMB 大 batch；`run_glue.py`/`run_squad.py` 是判别式微调两形态。

**(3) 性能秘方——自维护优化器栈**：`lamb_amp_opt/fused_lamb/fused_lamb.py:11` 的 `FusedLAMBAMP` 是吃到万级 batch 的关键（配套 `csrc/` 源码编译）；`optimization.py:26-33` 在**模块级**绑定 apex amp_C 内核（import 即需 apex，故示例配 Dockerfile）；`bind_pyt.py` 是 torchrun 前身自研 spawn 器。

**(4) 数据管线**：`data/bertPrep.py` 以 `--action` 驱动五阶段；`data/TextSharding.py` NLTK 分句装箱均衡分片；`create_pretraining_data.py` 生成 NSP+掩码样本。

**(5) 蒸馏压缩**：`general_distill.py` 做预训练多层中间态（hidden/attention/value）蒸馏、师生维度不同自动插投影层；`task_distill.py` 内置 10 个 GLUE processor；产物 4L/6L 三档小模型。

**(6) Triton 部署（训练产物→服务的全仓样板）**：`triton/export_model.py` 经 deployment_toolkit 导出 ONNX/TorchScript；`run_inference_on_triton.py` 同步/异步双路验证（:258 `client.async_infer`）；`runner/` 是基准编排框架；dist4l/dist6l/large 三目录即用部署（TSPP 部署层的直系祖先）。

## 4. TSPP 时序预测平台专题（最复杂子系统）

TSPP 与单脚本示例是两个物种：**配置驱动的研究平台**，占图谱六层。

**(1) 核心引擎**：`launch_training.py:32` 是 Hydra 总入口，按 trainer 类型分派三线——`training/trainer.py` 的 Trainer ABC（:42）+ CTLTrainer（:47）/StatTrainer（:266）/XGBTrainer（:327）；`models/` 12 个模型文件；`data/datasets.py` 四维注册器+十余种数据集变体。

**(2) 配置联邦＝实验即 YAML**：`conf/train_config.yaml:5-10` 的 defaults 组合链是心脏——model: ??? 必填、dataset 默 electricity、evaluator 按 trainer 类型用 if/cmp resolver 三路选择；`_target_` 直指 Python 类（tft.yaml→`models.tft.InterpretableTFT`）；`conf_utils.py` 注册 if/cmp 等自定义 resolver。改实验＝换 override。`overrides/` 按数据集×模型组织 hp_search.yaml 与 best_N.yaml（搜索空间+最优超参沉淀）。

**(3) 四个 vendored Hydra 插件**（免安装即得并行+调参）：optuna_sweeper（多目标搜索，ask/tell 迭代）；joblib/multiprocessing 两 launcher；torchrun 跨节点 launcher——与 `distributed_launcher/` **两代拷贝并存**（勘误 10）。

**(4) 上手入口**：`examples/` 8 个 shell——hp_search 四变体（单机/分布式/多目标/并行）、ensembling、interpretability、seed_sweep 等。

## 5. 推理服务化层

**deployment_toolkit（Bermuda 工具链）**：BERT 与 TSPP 各一份拷贝，`core.py` 定义 Loader/Saver/Runner/Converter/MetricsCalculator 六大 ABC 与 TensorSpec/Precision 等结构，`bermuda/` 按 onnx/pyt/tensorrt 三后端落地（复制族坑见勘误 6）。

**runner 基准编排**（`BERT/triton/runner/`）：`core.py` 的 DataObject 是 config/task/experiment 数据模型公共基类；`stages.py` 定义 Export/Deploy/Correctness/Perf 等 7 个标记类阶段，编排"导出→部署→正确性→性能"闭环。

**Kaldi 流式 ASR**：`triton-kaldi-backend.cc`（1187 行）以 `TRITONBACKEND_*` 钩子接入 Triton，驱动 Kaldi CUDA 批量在线解码；`kaldi_asr_parallel_client.cc` 模拟上千路音频流压测。

**TSPP 推理收尾**：`inference/converter.py` 经 AI Model Navigator 调 model-navigator CLI（converter.py:98）转 TorchScript/ONNX+config.pbtxt；`triton/model.py` 的 ModelWrapper（:27）读 `.hydra/config_merged.yaml`（:54）后 `hydra.utils.instantiate`（:58）还原 TFT——部署侧复用 Hydra 配置的闭环。

## 6. 构建与部署

**Dockerfile 联邦制**：无根级构建，每示例自带 Dockerfile，`ARG FROM_IMAGE_NAME` 参数化基底（CI --build-arg 换版本），全 NGC 且代际跨度大：Transformer-XL `20.06-py3`（Dockerfile:15）、BERT `21.11-py3`（:13）、TSPP `22.12-py3`（:16）。apex 一律源码编译（bf16lamb 分支不在上游 pip 发布）。

**SLURM 多节点**：`BERT/run.sub` 实为 bash+`#SBATCH`（run.sub:2-5），PHASE2 经 `SLURM_JOB_DEPENDENCY` 定位 phase1 检查点 `ckpt_7038.pt`（:97）；Transformer-XL 的 run.sub 再叠 pyxis/enroot 容器化。**CWD 约定普遍**：脚本须从示例根调用（容器 `/workspace/bert` 经 WORKDIR+COPY 锚定回仓内），`dist6l/runner/start_*.sh` 需以 `BERT/` 为 CWD。

## 7. 新人路线图（按 tour 16 步）

**第 1-3 天（骨架+BERT 主线，步 1-6）**：读 README 矩阵+hubconf.py 认清联邦与 stub → 精读 modeling.py 积木层次与 run_pretraining.py 参数 → 看懂 optimization.py 绑 amp_C 与 FusedLAMBAMP 的动机 → 走 bertPrep.py 五阶段+TextSharding 分片 → 认识蒸馏 4L/6L 产物 → 读 triton/ 的 export→deploy→verify 链路，画出训练到服务全图。

**第 4-7 天（对照示例+推理层，步 7-12）**：BART 对照 BERT 看生成式形态 → Transformer-XL 跨段记忆+adaptive softmax → FastSpeech Length Regulator+tacotron2 对齐教师（TRT 引擎分档+自定义 CUDA 插件是深水区）→ Kaldi 生命周期钩子+流式压测 → MxNet 对照分离"框架习惯"与"公共工程学"。

**第 8-30 天（TSPP+纵向贡献，步 13-16）**：launch_training→trainer 三线→datasets.py 注册器，画"配置如何变成对象" → 吃透 defaults 树+resolver，练习 override 换模型/数据集 → 读 optuna ask/tell 与 torchrun launcher，跑 examples/ 8 脚本（先按勘误 7 纠正 README 笔误）→ converter.py Navigator 链+triton/model.py Hydra 还原，此后选一个域做改动贡献。

## 8. 已知坑与勘误精选（均源码实证）

1. **BERT README 引用不存在的 model.py**：README.md:368 的 `model.py` 磁盘不存在（实为 modeling.py）；lddl 三处链接失效；L596 `run_pretraining.sh` 缺 scripts/ 前缀。
2. **TSPP 的 Adam 不是 torch 原生**：`conf/trainer/optimizer/Adam.yaml:2` 是 `apex.optimizers.FusedAdam`；原生须显式 `TorchAdam`（TorchAdam.yaml:2＝torch.optim.Adam）。
3. **run.sub 是 SLURM 非 HTCondor**：.sub 后缀易误判，实为 bash+`#SBATCH`（run.sub:2-5）。
4. **451 行未编译 CUDA 死代码**：`lamb_amp_opt/csrc/multi_tensor_lamb_out.cu`（451 行）不在 setup.py:13-17 sources 里，历史遗留 out-of-place 变体。
5. **tft_pyt 手动拷贝悬空链**：TSPP README:158-160 指示手动拷 `PyTorch/Forecasting/TFT/modeling.py`→`models/tft_pyt/`；dcrnn.py:23/deepar.py:16/mtgnn.py:20/lstm.py:19 全 import 该仓内不存在目录，不拷即 ImportError。
6. **np.narray 笔误+字节级拷贝群**：各域 `deployment_toolkit/dump.py:82` 的 `np.narray(batch)`（应为 np.asarray）五处逐字节相同（DLRM/WideAndDeep/GPUNet/BERT/TFT）；同类还有 dist4l 四份 per-GPU YAML、dist4l/dist6l 的 setup_environment.sh（diff 空）与两份 deployment_toolkit——改其一须评估同步。
7. **TSPP README overrides 顺序笔误**：README:585 写 `overrides=tft/electricity/best_0`，磁盘实为 `overrides/electricity/tft/`，照抄解析到不存在的组；引用 data/dataset.py 实为 datasets.py。
8. **蒸馏管线潜伏 NameError**：`distillation/utils/data_utils.py:93` 引用未定义裸名 `input_files`（应为 config.input_files），对齐分支触发即崩。
9. **TextSharding.py 四连坑**：L63/66/124/125/227/247 `is 0` 字面量比较（SyntaxWarning）；:319 import 即联网下 punkt；:322 `__init` 永不执行；:69 硬编码 serial 使多进程分支成死代码。
10. **torchrun launcher 双拷贝并存**：`distributed_launcher/`（版权 2022）与 `hydra_torchrun_launcher/`（2024）各嵌一份同名插件且 _core.py 已分叉，改前先确认用哪份。
11. **Facebook vendored 插件群残迹**：optuna_sweeper 版权头 Facebook, Inc.；joblib 的 pyproject 指向仓内不存在的 `news/_template.rst`；multiprocessing 的 pyproject package 名未改净（仍 joblib）。
12. **Kaldi 报错文案串位**：triton-kaldi-backend.cc:343-354 四条类型检查的报错文案与实际类型不匹配（查 TYPE_FP32 报 "expected INT32"），误导排障。
13. **FastSpeech 域吞 ImportError+拷贝残迹**：`fastspeech/model/module.py:37-39` except 只构造异常**没 raise**，apex 缺失被吞到首次用符号才 NameError（perf_infer.py 同模式）；requirements.txt:12 可疑条目 `data`；waveglow 的 `common.layers` 仓内无对应目录；denoiser.py 靠 `sys.path.append('tacotron2')` hack；另 perf_analyzer 的 `_faild_with_measruement_inverval` 三处拼写错误+str.find 布尔陷阱（-1 为真、0 为假）。

---

### 附：图谱统计

图谱 2072 节点/4638 边/16 层/16 步 tour（校验 0 issues）；fingerprints 854 文件 @ `729963dd`；2026-11-05 生成。
