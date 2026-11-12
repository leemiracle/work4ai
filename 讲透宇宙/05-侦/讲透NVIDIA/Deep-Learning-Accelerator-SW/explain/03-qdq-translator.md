# 03 · QDQ Translator：QAT 图到 DLA 部署图的翻译层

> 文件：`tools/qdq-translator/qdq_translator.py`（732 行）+ `utils.py`
> 图谱层：L09 | tour 步：T12/T13

## 角色定位

量化感知训练（QAT）的产物是带 QuantizeLinear/DequantizeLinear（Q/DQ）节点对的 ONNX——这是训练框架的"显式量化"表达。DLA 部署链要的却是**裸图 + 每张量 int8 scale + fp16 层清单**（老 TensorRT 与 DLA 编译器的接口形态）。`QATModelParser`（qdq_translator.py:99）就是这个翻译官：读 QAT 图、抽 scale、剥 Q/DQ、按需传播补缺，产出三件套（无 QDQ ONNX、scale JSON、TRT calib cache + layerPrecisions 参数）。

## 内部结构

- `get_quantized_tensor`（qdq_translator.py:118）：区分权重量化器（per-channel：x/zero_point 是 Constant、scale 是 Variable）与激活量化器（per-tensor：三者皆 Variable），并内置 TF 导出格式的 Constant 兼容转换；两个 `_fake_quantize_*_err_hint` 类常量给出 PyTorch 官方导出姿势的链接级指引；
- `verify_weight_scales`（qdq_translator.py:204）：按 TensorRT 量化口径（逐输出通道 dyn_range/127，MatMul 权重先转置）反推 scale，`np.isclose(..., atol=WEIGHT_SCALE_TOLERANCE)`（qdq_translator.py:218，容差 1e-3，qdq_translator.py:32）全量断言——QAT 的 scale 和 TRT 实际量化方式对不上时这里会炸；
- `extract_qdq_scales`（qdq_translator.py:286）抽 Q/DQ 对的 scale；`extract_precision_config`（qdq_translator.py:335）定 fp16 层；`infer_mul_scales`（qdq_translator.py:406）/`infer_unchanged_scales`（qdq_translator.py:429）沿数值不变算子（默认集合 MaxPool/Flatten/Relu/Pad/Transpose/Reshape/Squeeze/Sigmoid，qdq_translator.py:33）传播缺失 scale；`parse`（qdq_translator.py:612）总入口。

## 外部连接

上游是两条 QAT 工作流（e2e_workflow/ 的 tensorflow-quantization 与 pytorch-quantization）；下游是 `utils.py` 的 `export_to_trt_calib`（utils.py:28）：scale 经 `float_to_hex`（utils.py:22，IEEE754 小端十六进制）写成 `TRT-{ver}-EntropyCalibration2` 头的 calib cache，fp16 层拼成 `--layerPrecisions` 参数串喂给 trtexec。版本文件 VERSION 与 CHANGELOG.md 记录 v0.1.0→Unreleased 的修复线（输出张量误量化修复、fp16 BN 跳过 fuse_bn 等）。

## 数据流

`--input_onnx_models` 多模型 → parse 遍历 Q/DQ → scale 表 + 精度配置 → 移除 Q/DQ 节点 → 无 QDQ ONNX + int8_tensor_scales JSON → calib cache + layer_arg.txt。`--trt_calib_version` 默认 8600（qdq_translator.py:31），cache 头必须匹配目标 TRT 版本。

## 设计决策

- **校验而非信任 QAT scale**：verify_weight_scales 用 TRT 口径复核，把"部署后精度崩了才发现 scale 错"提前到翻译期；
- **传播是可选开关**：`--infer_mul_scales` 等默认关——传播能减 fp16 层提延迟，但可能掉精度，README 明说这是权衡；
- **`--add_unary_ew_scales_for_dla`**：给 Conv 后无 Q/DQ 的逐元素节点补 unary scale，专治 DLA 混合精度边界的空窗。

## 新人提示

排查顺序：模型跑挂先看 stderr 里的 err_hint（多半是 PyTorch 导出姿势不对）；精度掉先 diff fp16_nodes 清单再查传播开关是否误开；换 TRT 版本记得 `--trt_calib_version` 同步。DLA 用途有硬门槛：DLA SW ≥ 3.13.0（README.md:8 附近的版本表）。
