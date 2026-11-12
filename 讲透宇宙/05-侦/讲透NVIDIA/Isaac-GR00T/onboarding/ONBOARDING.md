# Isaac GR00T N1.7 Onboarding（新人上手指南）

> 仓库：`/usr-data/data2/repos/agent-repos/NVIDIA/Isaac-GR00T`（commit `51d4c89f` "Add support for Jetpack 7.2 on Orin and Thor"）
> 知识图谱：仓内 `.understand-anything/knowledge-graph.json`（1018 节点 / 1771 边 / 14 层 / 16 步 tour，validator 0 issues，fingerprints 323 文件）
> 本文锚格式 `路径:行号`，全部从源码核实；配套 8 篇 explain 见 `../explain/`。

## 1. 项目定位与全景

Isaac GR00T N1.7 是 NVIDIA 开源的**视觉-语言-动作（VLA）机器人基础模型**的训练/微调/评测/部署框架（`README.md:60` 起 GA 发布说明）。模型本体 = **VLM 骨干（Cosmos-Reason2-2B / Qwen3-VL）+ 流匹配（flow matching）DiT 动作头**（`gr00t/model/gr00t_n1d7/gr00t_n1d7.py:38` `Gr00tN1d7ActionHead`）。设计哲学是"一个模型服务多种机器人本体（embodiment）"：通过 `EmbodimentTag` 枚举（`gr00t/data/embodiment_tags.py:29`）+ 每本体一份 modality 配置（`gr00t/configs/data/embodiment_configs.py:26` `MODALITY_CONFIGS` 注册表），同一套骨干+动作头在不同机器人的状态/动作空间之间切换，`CategorySpecificMLP`（`gr00t/model/modules/embodiment_conditioned_mlp.py:143`）按本体 id 查表各自的编码/解码 MLP。

四条主线：**数据线**（LeRobot v2 → `LeRobotEpisodeLoader` → sharded 样本流 → processor 归一化）；**模型线**（`Qwen3Backbone`（`gr00t/model/modules/qwen3_backbone.py:135`）出 VL 特征 → 动作头去噪出 action chunk）；**训练线**（`FinetuneConfig`（`gr00t/configs/finetune_config.py:22`）→ `run()`（`gr00t/experiment/experiment.py:192`）→ `Gr00tTrainer`（`gr00t/experiment/trainer.py:152`））；**部署线**（ONNX（`scripts/deployment/export_onnx_n1d7.py`）→ TensorRT（`build_tensorrt_engine.py`）→ Jetson/Spark）。

FAQ（`FAQ.md`）钉版了几个关键取舍：数据加载器是 CPU 实现（GB200/H100/4090 验证非瓶颈）；微调默认只调 projector+扩散头不调 LLM/视觉塔；"保留 16 层 LLM"是经验性结论。

## 2. 目录结构与代码地图

```
gr00t/                     核心 Python 包（setuptools include gr00t*，pyproject.toml）
├── configs/               三层配置：base_config.py(Config 总装:82)/finetune_config.py/训练与模型配置
│   └── data/              data_config.py(DataConfig:53 多数据集混训)/embodiment_configs.py(注册表)
├── data/                  embodiment_tags.py + state_action/(action_chunking/pose/droid_frame)
│   ├── dataset/           lerobot_episode_loader.py:80 / factory.py:28 / sharded_mixture:149 / single_step:82
│   └── collator/          BasicDataCollator（聚合转 tensor）
├── model/
│   ├── base/              model_pipeline.py:30 ModelPipeline/:68 BasicPipeline（模型+数据集+processor 总装）
│   ├── modules/           qwen3_backbone.py:135 / dit.py:222 DiT/:339 AlternateVLDiT / embodiment_conditioned_mlp
│   └── gr00t_n1d7/        gr00t_n1d7.py:500 主模型 / processing_gr00t_n1d7.py:214 Processor / setup.py(HF 注册)
├── policy/                gr00t_policy.py:70 Gr00tPolicy / server_client.py(ZMQ 客户端)
├── experiment/            experiment.py:192 run / trainer.py:152 Gr00tTrainer / launch_finetune.py 入口
├── eval/                  run_gr00t_server.py:54/:91 / open_loop_eval.py / rollout_policy.py / sim/(四仿真环境)
├── deployment/            modes.py:63 起五个 StrEnum（Export/Verify/Benchmark/Inference/BuildEngine 模式）
└── utils/                 determinism.py(seed_everything)/dist_utils.py(run_or_wait_on_rank0)
demo_data/                 6 个 LeRobot v2.1 样例集（meta/info.json+modality.json+stats.json+parquet）
examples/                  11 个本体/场景示例（SO100/DROID/rebot/LIBERO/SimplerEnv/robocasa/WBC…）
scripts/                   数据下载转换 + deployment/(TRT/onnx 导出构建) + lerobot_conversion/
getting_started/           6 篇上手文档（data_config/data_preparation/finetune/policy/硬件/真机部署）
tests/                     分层测试（gr00t/**, scripts/**, getting_started/, examples/）+ test_support/
tools/                     check_manifest_alignment.py:328（HF 配置对齐审计）
```

注意两个"名不符实"：`gr00t/__init__.py`（388 行）**不是包 barrel，而是测试期对 HF transformers 的 monkey patch 集合**（b2 批分析实证，零业务导出）；`examples/DROID/main_gr00t.py:43` 附近的旋转矩阵是 `gr00t/data/state_action/droid_frame.py` 的**有意镜像**（源码 audit 注释钉版要求同步维护，因为该示例跑在无 gr00t 包的精简 DROID 环境）。

## 3. 数据体系：GR00T 风味 LeRobot v2

数据格式完全兼容上游 LeRobot v2（`getting_started/data_preparation.md:9`），增量是 `meta/modality.json`——把 state/action 向量按语义键切成 `{"single_arm": {"start": 0, "end": 6}}` 式区间。meta 目录四件套：`info.json`（元信息/路径模板）、`modality.json`（切片契约）、`stats.json`（归一化统计）、`relative_stats.json`（相对位姿统计，部分集有）。frames 存 parquet 列存，视频走 mp4。

消费侧三层：
1. **Python 侧 DataConfig**（`gr00t/configs/data/data_config.py:53`）：`video/state/action/language` 四模态各一份 `ModalityConfig`（定义在 `gr00t/data/types.py:85`），带 `delta_indices` 时间采样（如 SO100 的 `list(range(0,16))` 预测 16 步）与逐键 `ActionConfig`（`types.py:77`：RELATIVE delta vs ABSOLUTE、EEF vs 关节空间）；
2. **注册表**：`register_modality_config()`（`embodiment_configs.py:355`）把用户配置挂到 `EmbodimentTag`（预训练 8 标签如 `OXE_DROID_RELATIVE_EEF_RELATIVE_JOINT`、posttrain 预注册如 `LIBERO_PANDA`、自定义 `NEW_EMBODIMENT`，分层见 `embodiment_tags.py:33-52` 的 docstring）；
3. **加载器**：`LeRobotEpisodeLoader`（`lerobot_episode_loader.py:80`）解析 episode 元数据，`ShardedSingleStepDataset`（`sharded_single_step_dataset.py:82`）把轨迹切成单步训练样本，`ShardedMixtureDataset`（`sharded_mixture_dataset.py:149`，IterableDataset）按 `mix_ratio` 混采多数据集，`DatasetFactory`（`factory.py:28`）统一分发。

新本体微调的完整 walkthrough 见 `getting_started/finetune_new_embodiment.md`（以 SO-100 为例，配置样例 `examples/SO100/so100_config.py:26` 起的 so100_config dict——注意 single_arm 用 RELATIVE、gripper 用 ABSOLUTE 的注释级经验）。

## 4. 模型架构：骨干 + 动作头

**骨干** `Qwen3Backbone`（`qwen3_backbone.py:135`）封装 `Qwen3VLForConditionalGeneration`（try/except 可选导入，`qwen3_backbone.py:23`）：gated repo 报错沿异常链遍历识别（`_is_gated_repo_error:47`）并给出 HF_TOKEN 提示；RoPE inv_freq 在 meta device 加载场景需按真实设备重算（`recompute_vision_rotary_inv_freq:79`）；vision patch embed 支持 channels_last 3d 布局优化（`_apply_vision_patch_embed_channels_last:213`）。`set_trainable_parameters:249`（tune_llm/tune_visual/tune_top_llm_layers）承接"只调部分层"策略。

**动作头** `Gr00tN1d7ActionHead`（`gr00t_n1d7.py:38`）= DiT 或 AlternateVLDiT 二选一 + 状态/动作的按本体查表 MLP。训练用 flow matching：Beta 分布采噪声时间（`gr00t_n1d7.py:117` 起长注释解释为何把 Beta 钉在 CPU/fp32——meta device 下构造会炸），损失 = 速度场 MSE × action_mask（`gr00t_n1d7.py:272` 附近）。推理 `get_action_with_features:326` 从纯噪声迭代去噪；**RTC（实时控制）模式**用上一 chunk 尾部动作做 inpainting、冻结头部若干步（延迟补偿）并对中间步用指数 ramp 恢复去噪强度（`gr00t_n1d7.py:360-390`，注释极详）。

**DiT 模块**（`dit.py:222`）是 diffusers ModelMixin；`AlternateVLDiT`（`dit.py:339`）支持 `attend_text_every_n_blocks` 稀疏文本交叉注意力省算力；`_should_force_math_sdpa:37` 是 DGX Spark（sm121）上强制 SDPA 数学后端的平台补丁。总装在 `Gr00tN1d7`（`gr00t_n1d7.py:500`，PreTrainedModel）与 `BasicPipeline`（`model_pipeline.py:68`），后者把模型/数据集/collator/processor 四件套装到一起。

**Processor**（`processing_gr00t_n1d7.py:214` `Gr00tN1d7Processor`）是数据↔模型的翻译官：`set_statistics:345` 注入归一化统计、`decode_action:382`/`unapply:406` 做逆变换回原始动作空间、`process_observation:445`→`_apply_vlm_processing:546` 把图像+指令交给 Qwen3VLProcessor，配套 `Gr00tN1d7DataCollator:159`。

## 5. 训练与微调链路

入口 `gr00t/experiment/launch_finetune.py`：tyro 解析 `FinetuneConfig`（`finetune_config.py:22`，211 行全字段：base_model_path/dataset_path/embodiment_tag/modality_config_path、tune_* 四开关默认只开 projector+diffusion、state_dropout_prob=0.2 的 state dropout 抗过拟合、随机旋转/色彩抖动/掩码增强等数据增强、global_batch_size=64/lr=1e-4、wandb、DeepSpeed alpha）；`load_modality_config()`（`launch_finetune.py:22`）用 importlib **动态加载用户的 .py 配置文件**完成注册（这就是 modality config 必须是可 import 副作用文件的原因）。

`run()`（`experiment.py:192`）组装 `Config`（`base_config.py:82`）→ `BasicPipeline` → `Gr00tTrainer`（`trainer.py:152`，继承 HF Trainer：`_PrefetchIterator:77` 预取数据隐藏 CPU 加载延迟、`_batch_accuracy:118` 训练期动作准确率监控、`ProfCallback:43` torch profiler）。DeepSpeed zero2/zero3 配置由 `get_deepspeed_config`（`base_config.py:155`）按 stage 分流加载 `gr00t/configs/deepspeed/*.json`（消费点实证在 base_config，不是 finetune 脚本）。命令行习惯用法沉淀在 `examples/finetune.sh`。甄别（b1 批）：Gr00tTrainer 的 resume 采用"重播种 rank 对称"策略而非跳数据；`merge_statistics` 用二阶矩公式合并方差。

## 6. 推理、服务化与策略 API

**Gr00tPolicy**（`gr00t/policy/gr00t_policy.py:70`，750 行）是推理统一门面：`__init__` 加载 checkpoint+processor（内部 `import gr00t.model` 是注册副作用导入，`gr00t_policy.py:101`）；`get_action` 走 `_get_action:380`；观测校验 `check_observation:217`、`check_action:434`；`Gr00tSimPolicyWrapper:494` 适配 gymnasium 仿真环境（含严格/宽松两档校验）。上手文档 `getting_started/policy.md`。

**服务化**：`gr00t/eval/run_gr00t_server.py`（`ServerConfig:54`/`main:91`）起 ZMQ+msgpack 的 policy server——把推理搬到大算力集群、机器人本体只跑轻客户端（FAQ 钉版动机）。客户端协议库 `gr00t/policy/server_client.py`（与 `examples/DROID/server_client.py` 的 `PolicyClient:275`/`BasePolicy:175`/`MsgSerializer:144` 是一对双胞胎，后者服务无 gr00t 依赖的精简环境）。开环评测 `open_loop_eval.py:136` `evaluate_single_trajectory` 在验证集上回放打分。

**仿真 rollout**：`gr00t/eval/rollout_policy.py` 统一四套环境（LIBERO/SimplerEnv/robocasa/robocasa365），`env_utils.get_embodiment_tag_from_env_name` 做环境名→本体标签映射，`MultiStepWrapper`（`wrapper/multistep_wrapper.py`）处理宏步/环境步换算（注意 b5 批甄别：episode_lengths 口径=内层 env-step 非宏步数），`seed_everything`（`utils/determinism.py`）保证可复现。环境安装是每环境独立 venv 的 setup_*.sh 孤岛（依赖矩阵互斥，如 `setup_RoboCasa.sh` 是 robocasa/robocasa365 双变体统一安装器）。

## 7. 部署加速与硬件矩阵

部署枚举中枢 `gr00t/deployment/modes.py`：`ExportMode:63`/`VerifyMode:72`/`BenchmarkMode:81`/`InferenceMode:89`/`BuildEngineMode:101` 五个 StrEnum + `PipelineComponent:114`。TRT 线五件套：`export_onnx_n1d7.py`（1580 行，导骨干/动作头 ONNX）、`build_tensorrt_engine.py`（637 行建引擎）、`trt_model_forward.py`（1000 行，**三个前向分工**：tensorrt_forward=TRT ViT+PyTorch LLM、llm_trt_forward=PyTorch ViT+TRT LLM、full_trt_forward=双 TRT——b5 批甄别，名字极易混）、`trt_torch.py`/`verify_n1d7_trt.py` 验证等价、`_trt_contract.py` 契约测试。注意 scripts/deployment **不是 Python 包**，内部靠 `sys.path` 前插裸名互导（`from _trt_contract import ...`），测试也用同样姿势（b2/b28 批实证）。

硬件矩阵三层：x86/GB200 走仓根 `pyproject.toml`（torch 2.9，cu12/cu13 按平台 marker 分叉）；Jetson（JetPack 7.2）与 DGX Spark 各有专属 pyproject+install_deps.sh+Dockerfile（`scripts/deployment/{jetson,spark}/`，CUDA 13.2/13.0）；裸机激活脚本 `scripts/activate_*.sh` 补 TRITON_PTXAS_PATH/LD_LIBRARY_PATH。主 Dockerfile（`docker/Dockerfile`）单文件双架构，aarch64 先 bootstrap torchcodec wheel 再 uv sync，配 EGL/Vulkan headless 渲染。**避坑**：`docker/build.sh` 的 thor/orin profile 指向 `scripts/deployment/{thor,orin}/Dockerfile`——仓内不存在，是死分支；`tools/check_manifest_alignment.py:328` 引用的 `{orin,thor}/pyproject.toml` 磁盘存在但未被图谱收录（scanner 缺口）。

## 8. 新人上手路径与避坑

**推荐阅读序**（对应图谱 tour 16 步）：① `README.md`+`getting_started/` 六篇 → ② 跑通 `getting_started/GR00T_inference.ipynb` → ③ 读懂 modality.json+`so100_config.py` → ④ `LeRobotEpisodeLoader`→`ShardedMixtureDataset` 数据流 → ⑤ `gr00t_n1d7.py` 前向 → ⑥ `finetune_new_embodiment.md` 微调一轮 → ⑦ `gr00t_policy.py`+`run_gr00t_server.py` 推理 → ⑧ 按需进 TRT/评测线。explain 系列（`../explain/` 8 篇）按此序展开。

**避坑清单**（源码级实证）：
- 环境必须是 Python 3.12 + uv（`AGENTS.md`/`pyproject.toml:9`）；测试跑法 `python -m pytest tests/ -m "not gpu"`；
- HF 骨干 `nvidia/Cosmos-Reason2-2B` 是 gated repo，没 `hf auth login` 会拿到精心包装的报错（`qwen3_backbone.py:31` `_GATED_BACKBONE_HINT`）；
- `tests/test_support/` 是**顶层包**（tests/ 在 sys.path，`tests/conftest.py:70` 有函数体延迟 import），测试间共享 subprocess/runtime 助手；
- `gr00t/__init__.py` 是 monkey patch 集不是导出层——别把它当 API 入口；
- activate_orin.sh/activate_thor.sh 头注释仍写着 activate_jetpack72.sh（复制未改名，代码正确注释错）；
- SimplerEnv 目录唯一用 py3.10 孤岛 venv（其余 sim 环境均 3.12，b26 批甄别）；
- DROID 全量集 358GB/95k episodes（`examples/DROID/README.md`），先用 `scripts/download_droid_sample.py` 抽样；
- 数据增强的掩码版数据集（`demo_data/cube_to_bowl_5_with_mask/masks/*.npz`）配套 `examples/mask-guided-background-suppression/`，FinetuneConfig 的 extra_augmentation_config 字段（`finetune_config.py:104`）消费它。

> 事实口径：行号锚全部 grep 核实于 commit 51d4c89f；批分析七组子代理另产出 70+ 条甄别（各批 notes/languageNotes 原文可考）。
