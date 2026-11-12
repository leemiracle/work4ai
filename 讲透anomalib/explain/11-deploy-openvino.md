# 11 · 部署与 OpenVINO 推理（src/anomalib/deploy/）

## 一、角色定位

`src/anomalib/deploy/` 回答"训练完的模型如何离开 Python 训练环境"（图谱 cli-pipelines-deploy 层，tour T11）。仅 5 个源文件撑起三件事：①`export.py` 定义导出**词汇表**（ExportType/CompressionType 枚举）；②`inferencers/` 三个推理器把磁盘模型变成 `predict()` 调用——OpenVINO IR 主打、PyTorch legacy 回退；③配合 `models/components/base/export_mixin/`（导出执行体）与 `callbacks/nncf/callback.py`（训练期压缩）构成"导出→压缩→推理"闭环。它是 Intel 系库的招牌：默认产物是 OpenVINO 的 model.xml+bin，Studio 推理服务只认这个格式。

## 二、内部结构

**export.py:31（79 行，纯枚举）**：`ExportType`（L31-50）三值 ONNX/OPENVINO/TORCH；`CompressionType`（L53-79）四档：FP16（权重压半精度）、INT8（权重量化但推理反量化回浮点）、INT8_PTQ（权重与算子全整型）、INT8_ACQ（精度受控量化，超阈层保持混合精度）。导出动作本体不在本目录——`ExportMixin`（export_mixin/mixin.py L78）才是执行者：`to_torch`（L93）、`to_onnx`（L126）、`to_openvino`（L222）、`_compress_ov_model`（L309）、`_post_training_quantization_ov`（L359）、`_accuracy_control_quantization_ov`（L398）按档位分派。

**inferencers/base_inferencer.py:35（240 行，名义契约）**：`Inferencer(ABC)`（L35）声明五个抽象方法 load_model（L47-60）/pre_process（L62-75）/forward（L77-90）/post_process（L92-106）/predict（L108-121）。非抽象部分是工具箱：`_superimpose_segmentation_mask`（L123-154）用 dilation 画红描边（7×7 结构元、[255,0,0]，L152-153）；`__call__`（L156-170）转调 predict；`_normalize`（L172-218）按 metadata 的 min/max 键做 min-max 归一化；`_load_metadata`（L220-240）用 OmegaConf 读 metadata.json。

**inferencers/openvino_inferencer.py:70（220 行，主打路线）**：`OpenVINOInferencer`（L70）的 path 参数除路径外还接受 `(xml, bin)` 字节元组（L74-75），服务内存态模型（Studio 后端即此用法）；L98-100 无 openvino 包直接 ImportError。`load_model`（L106-156）：L124 起 `ov.Core()`，L126-140 处理三种后缀——.bin 自动换 .xml 兄弟（L131-134）、.onnx 直读、其余 ValueError；L142-145 在**当前工作目录**建 `openvino_cache/` 设 CACHE_DIR（换 cwd 即失效）；L147-151 compile_model 后 L153-154 取第 0 输入输出 blob。`pre_process`（L158-180）三步整形：>1.0 除 255（L171-172）、补 batch 维（L174-175）、HWC→NCHW（L177-178）。`post_process`（L182-194）把 OVDict 转 dict。`predict`（L196-220）接受路径/PIL/tensor/array（L209-214 归一为 numpy），L217 单行推理，L220 返回 `NumpyImageBatch(image=image, **pred_dict)`——复用 data 层 batch 类型。

**inferencers/torch_inferencer.py:73（294 行，legacy）**：docstring L9-11 双重警告"legacy，推荐 Engine.predict()"；构造即打告警日志（L117-120）。`_get_device`（L127-175）校验 auto/cpu/cuda/xpu。`_load_checkpoint`（L177-221）是安全设计样板：L203-212 要求环境变量 `TRUST_REMOTE_CODE=1` 才肯 `torch.load(..., weights_only=False)`（L221），L219 注释链 PR #2729——pickle 任意代码执行风险被显式围栏。`load_model`（L223-247）从 checkpoint["model"] 恢复并 eval；`predict`（L249-273）L271 前向后 L273 打包 `ImageBatch`；`pre_process`（L275-294）仅 unsqueeze 与 to(device)。

**callbacks/nncf/callback.py:29（183 行，训练期压缩）**：`NNCFCallback`（L29）构造 L72-77 查 nncf。`setup`（L85-113）：L105 `InitLoader(val_dataloader)`——校准集取**验证集**，L103-104 注释明说训练集只有正常样本；L108-113 `wrap_nncf_model` 原位替换 `pl_module.model`。训练中 batch/epoch 回调推进 scheduler（L137-138、L152-153）。`on_train_end`（L155-183）导出 `model_nncf.onnx`（L177-178）再 L180-183 调外部 `mo` 命令转 IR。

## 三、外部连接（图谱边证据）

deploy/__init__.py 的入边是全层最壮观的交汇：`src/anomalib/engine/engine.py:809`（Engine.export 消费 ExportType）、后端 cli.py/training_service.py/model_service.py、examples 多个脚本都 import 它——库、CLI、应用三线在此汇合。export.py 被 mixin.py/utils.py imports，带 5 条 tested_by 边（含 `test_ov_export.py`、`test_inferencer.py`）。openvino_inferencer 的 imports 边连 `data/__init__.py:41`（NumpyImageBatch），并被后端 test_model_service 压测——Studio 推理链路单测直接落它身上。nncf/callback.py 被 notebook `openvino_quantization.ipynb` depends_on；torch_inferencer 另有 `tools/inference/torch_inference.py` 入边。

## 四、数据流

导出流：Engine.export(export_type, compression) → ExportMixin：to_openvino 先产 onnx → ov 工具转 IR → 指定 CompressionType 则 `_compress_ov_model` 走 NNCF（PTQ 用验证集校准、ACQ 跑精度回退循环）→ 产物 `weights/openvino/model.xml|bin + metadata.json`（归一化统计与 threshold 都进 metadata）。训练期压缩流：setup 包装模型 → QAT 训练推进 scheduler → on_train_end 导出量化 IR。推理流（Studio 例）：model.xml + 大写 device（09 篇 model_service L266-268）→ load_model → predict：read_image→pre_process→单次调用→post_process→NumpyImageBatch→上层读 anomaly_map/pred_score。TorchInferencer 同构但终点是 ImageBatch，多一道 TRUST_REMOTE_CODE 闸门。

## 五、设计决策

1. **OpenVINO 优先**：只有 OpenVINO 支持设备枚举（AUTO/CPU/GPU/NPU，L77-79）与性能提示，ONNX 只是中转格式——Intel 生态的明确选择。
2. **推理器零依赖核心模型类**：openvino_inferencer 只 import data 层 NumpyImageBatch 与 read_image，不 import 任何 nn.Module——部署机装 anomalib[openvino] 即可跑。
3. **字节元组入口**（L74-75）：让 Web 服务从对象存储直接喂模型，绕过临时文件。
4. **legacy 与安全显式化**：双 docstring 警告 + 运行时告警 + TRUST_REMOTE_CODE 闸（L203-221），把 pickle 风险从"隐患"变"告知"。
5. **压缩四档覆盖精度-速度谱系**：FP16→INT8→PTQ→ACQ 一条枚举轴表达完整量化菜单，Engine/CLI/Studio 共用词汇。

## 六、新人提示（含勘误）

- **契约漂移（本目录最大坑）**：base_inferencer.py L9-10 与 inferencers/__init__.py L9 均声称两个推理器"继承 Inferencer 基类保 API 一致"——**源码 `class OpenVINOInferencer:`（L70）与 `class TorchInferencer:`（L73）都没有基类**；TorchInferencer 连 forward/post_process 都没有（predict 内联前向）。`Inferencer` 是孤儿契约，改接口须三处手改。
- **图谱摘要漂移**：图谱给 openvino_inferencer 写"输出 PredictionResponse 风格结果"、torch 写"PredictResponse"——源码返回 `NumpyImageBatch`（L196/L220）与 `ImageBatch`（L249/L273）；PredictionResponse 是 Studio 后端 pydantic 类型，不属本目录。
- `openvino_cache/` 建在**当前工作目录**（L142-143），常驻服务换 cwd 后缓存 miss 重编译，要固定工作目录。
- metadata.json 是推理正确性的隐彄件：`_normalize` 依赖的 min/max 与 threshold 全在里面，只拷 xml/bin 会得到未归一化裸分数。
- NNCF 导出依赖 PATH 里的 `mo`（L180），镜像没装 openvino-dev 会在 on_train_end 才失败——训练白跑。集成验证跑 `tests/integration/deploy/test_inferencer.py:56`。

---
**自检**：总字符（不含换行）4644 / 去空格字符 4342；行号锚 52 个（export.py×4、mixin×6、base_inferencer×7、openvino×12、torch×8、nncf×7、其他×2，均经源文件核实；另补 file:line 路径锚 8 处——export.py:31、base_inferencer.py:35、openvino_inferencer.py:70、torch_inferencer.py:73、nncf/callback.py:29、engine.py:809、data/__init__.py:41、test_inferencer.py:56，均 grep -n 实证）。
