# EXPLAIN-05 · modelopt/torch/export + _deploy：量化模型到 TensorRT/TRT-LLM 的导出线

## 一、角色定位

量化做完只完成一半——伪量化模型的权重仍是高精度张量、amax 挂在 quantizer 属性上，引擎不认识。`modelopt/torch/export/` 的职责是**把量化语义翻译成推理引擎可直接消费的 checkpoint**：权重打包、scale 挂成独立张量、量化配置写成 JSON，是 ModelOpt 与部署世界的契约层。

**关键事实（勘误任务书口径）**：本仓 HEAD（e3c903c，"Deprecate TensorRT-LLM model_type in favor of Hugging Face model_type #2569"）正处导出线**世代交替期**。旧 `export/trtllm/`（13 文件含 `__init__.py`，扣除后 12 模块即任务书"12 文件"口径）是 TRT-LLM 专有 checkpoint 导出器，**0.48.0 起废弃、0.49.0 删除**——`_DEPRECATION_MSG` 指向替代品 `export_hf_checkpoint`："a unified Hugging Face checkpoint deployable on TensorRT-LLM, vLLM and SGLang"（`model_config_export.py:90-94`）。新主线即 `unified_export_hf.py`/`unified_export_megatron.py` 的统一 HF checkpoint 导出：一份产物喂三家引擎，量化元数据以 `config.json` 的 `quantization_config`（compressed-tensors 格式）表达。旁支 `_deploy/` 是编译型部署（ONNX→TRT 引擎的 `compile()`），`modelopt/deploy/llm/` 是 TRT-LLM API 的 profiling 包装。

## 二、内部结构

### 公共词汇层

`quant_format.py` 是全后端共享命名表：`QUANTIZATION_FP8` 到六个 GGML IQ 格式共 20+ 常量（`:24-45`），KV cache 量化另表（`:69-73`）。`IQ_FORMATS` 直接从量化后端 registry 派生（`:55`）——"注册即声明可导出"，dispatch 与 export 永不分歧；`FUSION_FREE_FORMATS`（`:61-67`）标记哪些格式的 scale 不参与 q/k/v 与 gate/up 共享输入 amax 的融合。`registry.py` 实现导出侧注册-分发：注册表有序 first-match-wins，支持 MRO 类/类名字符串（对付 trust_remote_code 动态类）/结构 predicate 三模匹配+`prepend` 抢占（`:66-83`），示例即 `@ExportModuleRegistry.register("Llama4TextExperts","GptOssExperts")`（`:107-111`），两个实例见 `:145-148`。`quant_utils.py` 的 `get_quantization_format`（`:475`）沿模块树反推格式串；IQ 格式遇启用中的 input quantizer 直接抛错——"GGML block payload carries no activation scale...would be silently lost"（拒绝静默丢信息是本线反复出现的原则）。

### 统一 HF 导出主线

`export_hf_checkpoint`（`unified_export_hf.py:1834`）自动分流 transformers/diffusers，处理 FSDP2（全 rank gather、rank 0 写盘）与 accelerate offload（流式 writer，一次物化一层，`:1866-1930`）；未加载的权重（MTP head 等）从源 checkpoint 搬运保证完整性（`:1869-1884`）。核心打包 `_export_quantized_weight`（`:607`）：IQ 走 `IQ_FORMAT_REGISTRY[fmt].quantize`（`:640-647`）；NVFP4 已压缩权重（QTensorWrapper）不能从 packed nibble 重算 per-block scale，改用压缩时捕获的 scale（`:652-676`）。`_write_hf_export_config`（`:1559-1586`）写 `hf_quant_config.json` + 转成 compressed-tensors 格式嵌进 `config.json`（`:1570-1574`）；`convert_hf_config.py` 即该转换器（`:17`、`:150`）。`_postprocess_safetensors`（`:175-198`）面向 ComfyUI 类单文件运行时：merge 基座、NVFP4 按 16 对齐 pad、scale swizzle 成 cuBLAS tiled 布局。`quant_aware_conversion.py` 解决 transformers `conversion_mapping` 的原生 revert 在 0-d scale 上会炸的问题：Rename/Split/Merge 三原语（`:38-51`）把 scale 兄弟张量随权重搬运（`:85-90`），拆分时 per-tensor 标量 scale 复制（`:93-95`），量化过的 Merge 抛 `QuantConversionUnsupportedError` 回退（`:98-99`）。Megatron 侧镜像：`export_mcore_gpt_to_hf`（`unified_export_megatron.py:2153`）/`import_mcore_gpt_from_hf`（`:2192`）；`plugins/` 放模型特化（vllm_fakequant 与七份 mcore_* 文件）。

### 旧线 trtllm/（deprecated）

"torch 模型→结构化 config 树→两文件"：`model_config.py` 定义 `ModelConfig`/`DecoderLayerConfig`/`MOEConfig` 等 dataclass 树，HF/megatron/modelopt-quantized 三种来源都可转入、"we will build tensorrt_llm engine from the context saved"（`:16-19`）；线性层 column/row/group 三种并行布局（`:48-50`）。主入口 `torch_to_tensorrt_llm_checkpoint`（`model_config_export.py:100`）/`export_tensorrt_llm_checkpoint`（`:497`）落盘：每 rank 一份 `.safetensors` + 一份映射 TRT-LLM `PretrainedConfig` 的 `.json`（`:533-537`）。`decoder_type.py` 把模型类名映射到 TRT-LLM 自己的 decoder 名（`:15-19` 明言是 TRT-LLM 的模型名而非 HF model_type）：约 40 条子串规则（`:26-68`），顺序敏感——"DiffusionGemma must come before Gemma"（`:43-44`）。`hf_config_map.py` 是 HF 字段别名归一表：光注意力头数就有五种写法（`:22-25`），各家私货字段全覆盖（`:21-84`）。`tensorrt_llm_type.py` 从 TRT-LLM 拷贝三个 IntEnum 以解除对 TRT-LLM 包的依赖（`:21-22`）；`tensorrt_llm_utils.py:80` 生成 build API config；`distribute.py` 处理校准/推理 TP/PP 不一致时的合并重切分。包顶层 `export/__init__.py:43-51` 保留旧路径 re-export 并告警，0.49.0 删除。

### 引擎出口 _deploy/deploy

`compile(model, dummy_input, deployment, ...)`（`compilation.py:28-33`）把 torch 模型编译成 `DeviceModel`（torch→ONNX→目标运行时）。运行时经 `RuntimeRegistry` 分发（`_runtime/registry.py:22`），内置 `register("ORT")`（`ort_client.py:32`）与 `register("TRT")`（`trt_client.py:34`），均在 `_runtime/__init__.py:20-29` 用 `import_plugin` 门控。`modelopt/deploy/llm/generate.py` 的 `class LLM(TRTLLM)` 包装 TRT-LLM llmapi 做 profiling（`:17-41`），藏实战坑：`enable_kv_cache_reuse` 与 context logits 请求互斥——prefix 复用下共享前缀请求只返回重算后缀的 logits，破坏逐 token logprob（`:64-68`）。

## 三、外部连接

上游：`mtq.ptq/qat` 产出的伪量化模型；`quantization/qtensor` 的 `NVFP4QTensor`（真实化权重容器）；`modelopt.torch.models` 模型 spec（`ExportContext.model_type=None` 时"fail loudly instead of guessing"，`registry.py:56-60`）。下游：TRT-LLM（旧 checkpoint 走 build API、新走 HF loader）、vLLM/SGLang、ORT/TRT（`_deploy` 线）、ComfyUI。`modelopt.onnx.export` 是另一条独立出口（见 EXPLAIN-06）。

## 四、数据流

统一 HF 导出（NVFP4 LLM）：①格式判定——遍历模块树收集每层格式→`process_layer_quant_config`（`quant_utils.py:688`）聚合 `hf_quant_config`；②预处理——MoE gate/up amax 同步、共享输入模块融合（`:296-367`）、QKV 融合层重平滑再量化（`:512`）；③打包——逐权重转 packed 格式，scale 提升为模块张量（`weight_scale` 块级 FP8+`weight_scale_2` 全局，`:1183`）；④名称还原——量化感知逆映射回 hub 名（`:1604-1624`）；⑤落盘 safetensors 分片+两份 JSON，引擎读 `quantization_config` 选量化 kernel。

## 五、设计决策

- **开放格式优先**：0.39.0 文档预警→0.48.0 运行时告警→0.49.0 删除（`model_config_export.py:90-93` 交代迁移期策略）；教训是专有 checkpoint 与引擎版本强耦合。
- **注册表替代 if/elif**：三模匹配+`prepend` 让外部包覆盖内置行为而不改主干。
- **拒绝静默错误**：IQ 带激活量化抛错、量化 Merge 抛错回退、model_type 未知即大声失败——宁可失败不产出坏 checkpoint。
- **依赖解耦**：TRT-LLM 枚举拷贝不 import；`_deploy` 运行时全门控——导出 checkpoint 不需要装 TRT-LLM。

## 六、新人提示

1. **新代码一律 `export_hf_checkpoint`**：`export/trtllm/` 是待拆除 legacy，0.49.0 后旧路径直接消失（`export/__init__.py:46-51`）。
2. **读 trtllm/ 先建"三套名词"意识**：decoder_type 的值（TRT-LLM 模型名）、HF `model_type`、hf_config_map 的内部名——混读是最大迷路点。
3. **排查"导出后精度崩"先查 scale 张量**：正确 state_dict 应有 `weight_scale`+`weight_scale_2`；压缩分支缺 `_double_scale` 会触发重算路径，packed nibble 上重算必错（`unified_export_hf.py:652-676`）。
4. **TP/PP 变更显式声明**：校准 TP4 导出想跑 TP2 必须传 `inference_tensor_parallel`，默认 0 沿用校准切分。
5. **`_deploy/compile` 与 LLM 导出是平行线**：前者 ONNX 编译（CV profiling），后者 checkpoint 导出（LLM）；下划线开头即内部 API。
