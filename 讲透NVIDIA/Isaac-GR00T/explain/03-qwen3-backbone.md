# 03 · qwen3_backbone.py — Qwen3-VL 感知骨干封装与三处工程修复

> 源码：`gr00t/model/modules/qwen3_backbone.py`（372 行）。N1.7 的"眼睛和语言中枢"：把 transformers 的 `Qwen3VLForConditionalGeneration` 包装成对动作头友好的特征提取器。文件近半篇幅是三处工程修复（gated 报错、RoPE 修复、Conv3d 性能补丁）。

## 一、角色定位

`Qwen3Backbone`（qwen3_backbone.py:135）是普通 `torch.nn.Module`（不是 PreTrainedModel），由 `get_backbone_cls` 按模型名路由实例化（gr00t_n1d7.py:490-497）——Cosmos-Reason2-2B 本身就是 Qwen3-VL 架构，故 nvidia/Cosmos-Reason2 与 Qwen/Qwen3-VL 两个名字共用此类。它只做一件事的 forward：把图像+文本变成带 mask 的 token 级隐状态序列，交给动作头当交叉记忆。它封装 `Qwen3VLForConditionalGeneration`（qwen3_backbone.py:183-187）；但类 docstring 写的"generate n_queries to represent the future action hidden states"（qwen3_backbone.py:151）是从旧 Eagle/N1.5 骨干拷来的陈旧注释——本类不生成任何 query，与实现不符，读码时以 forward（qwen3_backbone.py:357-372）为准。

## 二、内部结构

**构造链**（`__init__`，qwen3_backbone.py:136-211）：①顶部 try/except 导入 `Qwen3VLForConditionalGeneration`（qwen3_backbone.py:26-31），缺失时在 qwen3_backbone.py:157-162 报"需要 transformers>=4.57.0"；②flash_attn 可选——try import 成功则 `attn_implementation="flash_attention_2"`，失败 warning 并降级 sdpa（qwen3_backbone.py:167-178）；③`load_bf16` 时注入 `torch_dtype=bfloat16`（qwen3_backbone.py:179-180）；④`from_pretrained` 外包一层 gated 仓库错误翻译（qwen3_backbone.py:182-191）；⑤按 `select_layer=12`（configs/model/gr00t_n1d7.py:47）**弹出多余 LLM 层**——`while len(layers)>select_layer: pop(-1)`（qwen3_backbone.py:194-195），截断省算力；⑥`set_trainable_parameters`（:198）；⑦bf16+`trainable_params_fp32=True`（config 默认 True）时把可训练参数逐个 cast 回 fp32（:199-204）；⑧最后依次执行 RoPE 修复（:208）与 Conv3d 补丁（:211）。

**三个修复件**：
- **gated 错误链遍历**：`_is_gated_repo_error`（:47-61）沿 `__cause__/__context__` 最多走 10 层（防异常链成环），匹配 `GatedRepoError` 实例或四条消息标记（:44）；命中则把原始异常翻译成 `_GATED_BACKBONE_HINT`（:34-41）——明确告知 Cosmos-Reason2 是 gated 仓、所有 GR00T checkpoint 都要它、去 HF 申请权限+`hf auth login`。
- **RoPE inv_freq 重算**：Qwen3-VL 的 `inv_freq` 是 `persistent=False` buffer，不进 checkpoint，嵌套 `no_init_weights` 加载后可能未初始化（qwen3_backbone.py:285-294 docstring）。修复思路是"让 transformers 自己的类重算"：vision 侧 `type(rotary)(head_dim_half)`（:79-89，head_dim 由 vision_config.hidden_size//num_heads 推出，:325-327），text 侧 `type(rotary)(config=config)`（:92-105），都在 `_real_inference_device` 找到的真实设备上下文里构造（:64-76，防 meta 设备）。布局缺失就 RuntimeError **fail closed**（:304-340 两处），绝不带未初始化 buffer 静默推理。`_assign_inv_freq`（:108-132）幂等写回：值相同返回 False 不重写，测试可据此断言"真修了"；text 侧连动态 RoPE 用的 `original_inv_freq` 普通属性也同步（:347-351）。
- **channels_last_3d 补丁**（:213-247）：torch≥2.9+cuDNN 9.10.x 下 contiguous bf16 的视觉 patch-embed `Conv3d` 在 sm_80 走病态慢 kernel，`channels_last_3d` 选快路径且数值等价；给每个 Conv3d 转内存格式并挂 forward_pre_hook（:237-241），hook 里 `torch.jit.is_tracing()` 时跳过（:229-231）——ONNX 导出不支持 memory_format，此补丁是纯运行时性能提示。

## 三、外部连接

- 上游：transformers 的 Qwen3-VL 全家（模型类 :27、`image_token_id` :364）、flash_attn 可选依赖（:170）；huggingface_hub 的 `GatedRepoError`（:18）。
- 下游：gr00t_n1d7.py 的 `Gr00tN1d7.__init__` 直接构造它并透传 8 个 tune/load 参数（gr00t_n1d7.py:530-541）；forward 产出的三个键 `backbone_features/backbone_attention_mask/image_mask`（qwen3_backbone.py:366-372）正是动作头 `process_backbone_output` 与 AlternateVLDiT 分支的输入（gr00t_n1d7.py:175-180,252）。
- 测试背书：tests/gr00t/model/ 的 test_qwen3_rope.py/test_gated_backbone_error.py/test_variable_image_size.py 分别钉住三处修复，升级 transformers 前先跑。

## 四、数据流

forward（qwen3_backbone.py:357-372）极简：先 `set_frozen_modules_to_eval_mode`（:358，理由同动作头——HF trainer 每步 model.train()）；白名单只取 4 个键 `input_ids/attention_mask/pixel_values/image_grid_thw`（:360-361，多余键直接丢）；`output_hidden_states=True` 调底层模型后取 `hidden_states[-1]`（:362-363）——注意取的是**被截断到 12 层后的最后一层**，不是原模型末层；`image_mask = input_ids == config.image_token_id`（:364）用特殊 token 位置反推哪些隐状态来自图像；`attention_mask == 1` 转布尔（:365）。产出即 01 篇 vlln→vl_self_attention→AlternateVLDiT 的原料；输入侧 token 化在 processing_gr00t_n1d7.py（04 篇）。

## 五、设计决策

1. **延迟导入隔离版本约束**：顶层 try/except（:26-31）+ get_backbone_cls 的函数内导入（gr00t_n1d7.py:492-493）双保险，让不强求 Qwen3-VL 的环境（如部分 CI）能导入 gr00t.model 包其余部分。
2. **fail closed 而非静默兜底**：RoPE 修复找不到布局就中止加载（:307-313），注释原话 "Continuing would leave it uninitialized and silently corrupt inference"——对"看起来能跑但输出全是垃圾"这类最险故障选择快速失败。
3. **修一次而非修每次**：RoPE 修复放在构造期一次性完成（:208），前向零开销；对比某些框架在 forward 里 lazy rebuild 的做法，这里明确注释 "load time only, no per-forward cost"（:292-293）。
4. **权重冻结的精细粒度**：`set_trainable_parameters`（:249-271）三档——tune_llm 全语言塔、tune_visual 视觉塔、`tune_top_llm_layers>0` 只解冻语言塔**顶部 N 层**（:259-262），这是 LoRA 出现前最省显存的 VLM 微调姿势；N1.7 默认三者全 False（config:45-46,48），backbone 整体冻结。
5. 甄别一条版本口径：本文件报错文案说 transformers>=4.57.0（:161），而 processing 侧 build_processor 说 >=4.52.0（processing_gr00t_n1d7.py:127）——同仓两处最低版本不一致，以更高者 4.57 为准。
6. **fp32 可训练岛**：bf16 推理_dtype 与 fp32 梯度更新天然冲突，:199-204 只对 requires_grad=True 的参数做 cast，冻结参数保持 bf16——显存只花在刀刃上。

## 六、新人提示

- 首次拉模型遇 `RuntimeError: Cannot download the VLM backbone...`（:190）不是 bug，按提示去 huggingface.co/nvidia/Cosmos-Reason2-2B 申请权限并 `hf auth login`。
- `select_layer=12` 意味着加载后 `language_model.layers` 只剩 12 层（:194-195），打印模型结构发现"少了"先想起这条，别误判 checkpoint 损坏。
- 想确认 RoPE 修复真的执行过，看 debug 日志 `RoPE inv_freq reset (vision_rewritten=..., text_rewritten=...)`（:298-302）。
- 改 keys_to_use 白名单要同步处理器输出——多传键在 :361 被静默丢弃，少键才报错。
- ONNX/TRT 导出走的 tracing 路径会绕过 channels_last_3d hook（:229），导出后精度对不上时先排除该补丁的数值差异（理论上等价，但验证脚手架在 tests/scripts/deployment/）。
