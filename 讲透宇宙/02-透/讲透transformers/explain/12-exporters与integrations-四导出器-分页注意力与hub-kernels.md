# 12 · exporters 与 integrations：Dynamo 底座四导出器、paged 注意力与 hub kernels

## ① 角色定位

这是仓里两扇"对外之门"。`src/transformers/exporters/` 负责把模型编译产物送出 PyTorch 生态；`src/transformers/integrations/`（__init__.py 316 行，27 个懒加载子模块）收纳所有可选第三方依赖的粘合层——量化后端、DeepSpeed/FSDP、注意力变体、Triton kernel 分发。两包 2026 版的共同主题：**注册表开放化**（register_exporter/register_export_config/register_kernel_mapping_transformers）。

## ② 内部结构

**exporters 实为"一底座+三方向"**：`exporter_dynamo.py` 是公共基座（包装 `torch.export.export(strict=False)`，含 forward 签名拍平、SDPA patch、Cache 类型 pytree 注册与动态形状推导）；`OpenVINOExporter(DynamoExporter)`（exporter_openvino.py:88）与 `ExecutorchExporter(DynamoExporter)`（exporter_executorch.py:109）直接继承之，OpenVINO 侧的 `_fix_exported_program`（L143）与 `_convert_to_openvino`（L183）做图后处理，ExecuTorch 侧 `_get_transform_passes`（L161）按 backend 选 pass。配置层同构：configs.py 里 OnnxConfig（L111）、ExecutorchConfig（L153）、OpenVINOConfig（L190）**全部继承 DynamoConfig**（L77）。分派层 auto.py：AutoExportConfig.from_dict（L52）、AutoHfExporter.from_config（L80）、`supports_export_format`（L126，config 与 exporter 必须成对注册否则 actionable warning L156）、第三方钩子 `register_exporter`（L163）与 `register_export_config`（L174）——重名只 warning 并**覆盖**（L166-167），与 quantizers 的 raise 形成对照。

**integrations 的注意力矩阵**：普通后端（eager/sdpa/flash_attention_2/3/4/flex）之外，2026 版新增 paged 维度——modeling_utils.py:5118-5130 的 `_global_mapping` 用复合键注册：`"paged|flash_attention_2/3/4": paged_attention_forward`（integrations/flash_paged.py:10，decode 短序列走 `_paged_decode_forward` L107）、`"paged|sdpa": sdpa_attention_paged_forward`（sdpa_paged.py:21）、`"paged|eager": eager_paged_attention_forward`（eager_paged.py:22，显式掩码+repeat_kv 的正确性兜底）。**hub_kernels.py** 是 kernels-community 的 Triton kernel 分发层：环境开关 `USE_HUB_KERNELS` 默认 YES（L62），版本下限提示 KERNELS_MIN/MAX_VERSION（L31-32,56-58），核心装饰器 use_kernel_forward_from_hub（L105）/use_kernelized_func（L114）在 kernels 库缺失时优雅降级为 no-op 并告警（L107-111），另有 get_kernel_mapping_transformers（L716）与 register_kernel_mapping_transformers（L723）两层映射注册。

## ③ 外部连接

hub kernels 与模型层直接咬合：modeling_llama.py 的 RMSNorm 类挂 `@use_kernel_forward_from_hub("RMSNorm")`（L52）、apply_rotary_pos_emb 挂 `("rotary_pos_emb")`（L137）、LlamaAttention 挂 `@use_kernelized_func(apply_rotary_pos_emb)`（L216）——llama 骨架第 08 篇的三处装饰器正是本篇的分发出口。paged 注意力与 cache_utils 的 PagedAttentionCache（block_table 语义见 flash_paged.py:39 docstring）配套。integrations/__init__.py 用 _LazyModule + _import_structure 字典把 27 个子模块（aqlm/awq/bitnet/bitsandbytes/compressed_tensors/deepspeed/…）按符号级懒导出——import transformers.integrations 不触发任何可选依赖。

## ④ 数据流

导出流：用户给 export_config（dict 或 ExportConfigMixin）→ register_exporter/register_export_config 注册过的一对 (config_cls, exporter_cls) → AutoHfExporter.from_config 实例化 → DynamoExporter 先跑 torch.export 拿 ExportedProgram → 各方向后处理（OpenVINO 转 IR / ExecuTorch 编 edge）→ 落盘。kernel 流：模型初始化时装饰器查 kernel mapping（内置映射表 + register_kernel_mapping_transformers 扩展）→ 命中且 kernels 可用则替换 forward → 未装 kernels 库走 `_MISSING_KERNELS_MESSAGE` 提示 pip 安装。paged 流：config 设 `attn_implementation="paged|sdpa"` → ALL_ATTENTION_FUNCTIONS.get_interface 按 `"|"` 复合键取 sdpa_attention_paged_forward → 与 PagedAttentionCache 的 block_table 协同。

## ⑤ 设计决策与勘误

- **勘误一（本系列任务卡原文即需修正）**："四导出器 ONNX/TorchScript/OpenVINO/TensorRT"——实测仓内**没有** exporter_torchscript.py 与 exporter_tensorrt.py，四导出器是 **ONNX/OpenVINO/ExecuTorch/Dynamo**；且 ONNX 配置继承 DynamoConfig（configs.py:111），严格说 ONNX 也是 Dynamo 路线的产物。TensorRT/older TorchScript 诉求由 optimum 等外部仓承接，transformers 本体 2026 版全面押注 torch.export。
- **勘误二**：AutoHfExporter.from_pretrained（auto.py:94-98）是显式 "Not implemented yet" 占位（"first-class export recipe workflow"）——从 Hub 拉 export recipe 的愿景尚未兑现，别按文档想象调用。
- **paged 是二维矩阵不是第六后端**：`paged|X` 正交于 X，共 6 个组合键（modeling_utils.py:5125-5129），把它当独立后端理解会漏掉 eager 兜底路径。
- 注册语义三态：quantizer 重名抛错 / exporter 重名警告覆盖 / kernel mapping 静默字典更新——风险越高越严格。
- **hub kernels 默认开**（USE_HUB_KERNELS 默认 YES）意味着默认安装下首次前向可能从 Hub 拉 kernel——离线环境记得显式关。

## ⑥ 新人提示

导出排障先看 Dynamo 层：三方向共享基座，OpenVINO 报的错常源于 dynamo 阶段的签名拍平。注意力选型速查：训练用 sdpa/flash，prefill/decode 分离的服务场景试 `"paged|X"`，正确性对拍用 `"paged|eager"`。给自研模型加加速 kernel：写 Triton → 传 kernels-community → register_kernel_mapping_transformers 挂到你的层名，模型代码零改动。读 integrations 子模块先看模块级 is_xxx_available 探测函数——可选依赖的一切分支都从它分岔。
