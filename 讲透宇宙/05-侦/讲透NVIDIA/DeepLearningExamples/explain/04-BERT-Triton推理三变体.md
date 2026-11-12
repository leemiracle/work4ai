# 04 BERT-Triton 推理三变体

## 角色定位

`PyTorch/LanguageModeling/BERT/triton/` 是 BERT 的推理部署线，图谱第 5 层"BERT Triton 推理部署"（tour step-06）。目录分两半：共享框架 `runner/`（编排引擎，详见第 05 篇）与三个变体目录 `dist4l/`、`dist6l/`、`large/`。三变体 = 三个可独立运行的基准流水线：4 层 288 维蒸馏小模型、6 层蒸馏中模型、BERT-large 24 层原模型，各自把"导出→格式转换→部署→正确性→性能"五步跑通并产出吞吐/延迟报告。这个目录展示了一种少见的工程形态：**三个入口逐字节相同、全部差异下沉到一份声明式配置**——训练线常见的"复制整个目录改三行"式分叉，在这里被压制到了最小面积。

## 内部结构

**三份 `__main__.py` 逐字节相同**（md5 `98dd8dd7b377c2f149d83e7c6ee5d683` 三处一致，diff 实证）。每份 62 行：L17-18 的 PEP-366 自举 `if __name__ == "__main__" and __package__ is None: __package__ = pathlib.Path(__file__).parent.name`，让脚本既能 `python -m` 又能直接执行；L20-25 相对导入共享框架四件（Config/Executor/ExperimentFinalizer/DockerMaintainer）与本目录 `pipeline_impl`；L28-36 `ExperimentRunner(RunnerProxy)` 以四个类属性注入组件（maintainer_cls/executor_cls/preparer_cls/finalizer_cls）；L39-46 `execute()` 读 YAML 构造 runner 启动；L49 起 argparse 解析 `--config-path/--devices`。

**三份 `pipeline_impl.py`**：dist4l 与 dist6l 逐字节相同（diff exit 0），large 与它们的差异只有两处（diff 实证）：

- L45-46：蒸馏版用 `${CHECKPOINT_DIR}/config.json` + `pytorch_model.bin`（HuggingFace 格式 checkpoint，随 NGC zip 下载自带配置），large 用仓内 `bert_configs/large.json` + `${CHECKPOINT_DIR}/bert_large_qa.pt`（NVIDIA 原生 .pt 权重）；
- L49 与 L151：词表来源——蒸馏版用 CHECKPOINT_DIR 内 vocab.txt，large 指向 `google_pretrained_weights/uncased_L-24_H-1024_A-16/vocab.txt`（依赖数据准备线的产物目录，见第 03 篇）。

pipeline_impl.py:21 模块级 `pipeline = Pipeline()` 后链式注册五阶段：L22 `model_export`（r-string shell 模板调 `triton/export_model.py`，onnx-opset 13，trt 格式加 `--fixed-batch-dim`）、L56 `model_conversion`（model-navigator convert）、L103 `model_deploy`、L138 `triton_prepare_performance_profiling_data`、L155 `triton_performance_offline_tests`。纯过程式模块，无函数无类——声明即配置。

**配置 YAML（四卡型 × 三变体 = 12 份）**：md5 揭示两种形态——dist4l 四份全同（`defc1a3a…`）、dist6l 四份全同（`e9a037c…`），即硬件档位对实验清单无影响；large 分裂为**两组**：A30/T4 共用 `9be8fb3f…`，V100-32G/A100-80G 共用 `eb4bbcb2…`——后组多了 batch 16 档与 `accelerator: trt` 的 TensorRT FP16 实验项（diff：A100 组多出 L72-87 的 16 档与 trt 项）。YAML 顶层两类键：`checkpoints`（NGC 下载 URL，如 dist4l 的 `bert_pyt_ckpt_distilled_4l_288d_qa_squad11_amp` 21.11.0 版）与 `configurations`（逐实验的 batch/format/precision/seq_length/capture_cuda_graph/triton_* 参数）。

## 外部连接

- **runner/ 共享框架**：`from ...runner.config import Config` 等（__main__.py:20-24）——三变体寄生其上，框架组件（Preparer 下载 checkpoint、Maintainer 起 Triton 容器、Executor 跑阶段、Finalizer 汇总）见第 05 篇。
- **triton/ 目录内的部署件**：`model.py` 是 Triton 部署约定封装——L23 `update_argparser`、L57 `get_model`；L33-34 把 vocab_size 补齐到 8 的倍数（TensorRT 对齐友好），L36 在函数内定义局部类 `BertForQuestionAnswering_int32_inputs` 继承 modeling.BertForQuestionAnswering 做 int32→long 输入适配（tree-sitter 不提取函数内局部类，图谱 languageNotes 钉版）。`dataloader.py` 复用 run_squad 的特征化函数产出 `input__0/1/2` 命名张量流；`metrics.py` 继承 deployment_toolkit 的 BaseMetricsCalculator，聚合 start/end logits 走 run_squad 的 get_answers 生成预测 json，再子进程调官方 evaluate-v1.1.py 取 F1。
- **deployment_toolkit**：BERT/triton/ 下有自己的复制件（`.version` 为 0.7.2），导出/推理/测速脚本 import 它——十份复制件之一，见第 05 篇。
- Dockerfile（service 节点）deploys run_pretraining.py 与本线脚本，图谱记两条 deploys 边。

## 数据流

单变体一次完整运行：

1. `python runner/__main__.py --config-path config_NVIDIA-A30.yaml` → ExperimentRunner.start()；
2. Preparer 按 YAML `checkpoints.url` 从 NGC 下载解压 checkpoint、采集 GPU/CPU/Memory 系统信息建 Task 档案；
3. 逐 `configuration`（batch×format×precision 展开）：Executor 导出环境变量（Configuration.parameters() 把 14 字段展开为容器 env），起 TritonServerContainer；
4. model_export：容器内执行 export_model.py（读 checkpoint+dataloader 定长 batch）产出 exported_model（onnx/ts-trace/ts-script/trt 按 EXPORT_FORMAT 分支，pipeline_impl.py:24-31 定后缀名）；
5. model_conversion：model-navigator 转 Triton 可部署格式；
6. model_deploy + Correctness/TritonPerfOffline/TritonPerfOnline 阶段（stages.py 的 7 个零方法体标记类以类型身份参与编排）：run_inference_on_fw（框架侧真值）vs run_inference_on_triton 比对正确性，run_performance_on_triton 出吞吐/延迟；
7. Finalizer 汇总各实验 csv/json/yaml 生成 summary。

数据不落仓内固定路径——一切经 `${SHARED_DIR}` 等环境变量占位注入容器（runner/utils.py 的 get_result_path 支持占位符映射）。

## 设计决策

1. **逐字节相同入口 = 分叉面积最小化**。变体差异被压缩到 pipeline_impl 两行数据面配置 + YAML，升级框架时三处同步零成本。对比第 06 篇 BART 的 finetune/run_eval 之间"同源拷贝后各自漂移"，这里是反例典范。
2. **蒸馏版背 HF 格式、large 背 NVIDIA 格式**：小模型发布物面向 HF 生态（config.json+bin+vocab 一体），大模型沿用自家 .pt+外置词表——两代 checkpoint 口径并存是历史演进的自然沉积，消费侧（model.py:31 get_model_from_args）则两种都吃。
3. **实验清单按算力分档只给 large**：大 batch 16 与 TRT 引擎只在 V100/A100 组开启——小模型在任何卡上都触不到算力上限，档位区分无意义；YAML md5 两组是"实验矩阵随硬件伸缩"的直接证据。
4. **shell 模板 + 环境变量占位的可复现哲学**：阶段命令是 r-string 原样脚本，Configuration.parameters() 展开注入——CommandsExporter 会把每阶段导出为可复现 BASH 脚本，性能报告与复现命令同源。

## 新人提示

- 找三变体差异不要读 __main__.py——diff pipeline_impl.py 与三组 config YAML 的 md5 即可，五分钟出全景。
- `${CHECKPOINT_DIR}` 在蒸馏版与 large 版指向**不同格式**的产物树，写自己的变体时先确认 export_model.py 的 --config-file 能否吃你的 checkpoint 格式。
- trt 导出路径要求固定 batch 维（pipeline_impl.py:27-29 的 FLAG 分支），动态 batch 实验只能走 onnx/ts 路线。
- vocab_size 8 倍数对齐（triton/model.py:33-34）会悄悄改模型结构——比对框架侧与 Triton 侧正确性时这是已知的合法差异，不要当 bug 报。
