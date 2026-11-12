# 第 11 篇：reason1 VLM 并行线——Qwen2-VL 内嵌移植与 cp_mesh 上下文并行

## 一、角色定位

`cosmos_predict2/_src/reason1/` 是一条与视频世界模型并行的 VLM 训练线：把 HuggingFace 的 Qwen2-VL / Qwen2.5-VL 整模型**内嵌移植**进本仓（`networks/qwen2_vl.py` 2176 行，`networks/qwen2_5_vl.py` 2230 行），再叠加 torchtitan 风格的五维并行（dp/cp/tp/pp/ep）。产出不是聊天模型，而是**给视频生成提供推理语义嵌入的文本编码器**——多处配置出现 `text_encoder_class="reason1p1_7B"`（如 `model_14b_reason_1p1_rectified_flow.py:152`、`experiments_dmd2_predict2p5.py:219`），教师检查点名也带 reason1p1（`distill/configs/defaults/teacher_model_paths.py:55`）：reason1 的推理嵌入替换/补充 T5，是 "reason embeddings" 实验族的动力源。configs/models/parallelisms/tokenizer/utils 五个子包自成一体，DCP 检查点器有 utils 与 parallelisms 两份副本。

## 二、内部结构

**HF 移植层（networks/）**。`qwen2_vl.py` 文件头 docstring 给出上游锚点：`https://github.com/huggingface/transformers/blob/794fde7b1c3d041519fc28ea3e1461b0cfcad4e7/...modeling_qwen2_vl.py`（`qwen2_vl.py:22`）——固定 commit 的 vendored 拷贝，可对 attention forward 动刀而不受 transformers 版本漂移（仓内 transformers==4.51.3 锁定）。魔改集中在**上下文并行**：attention forward 增加 `cp_mesh: Optional[DeviceMesh] = None` 形参（`qwen2_vl.py:681`、`:784`）；SDPA 路径计算前把本 rank 分片 的 K/V 用 `DTensor.from_local(key_states, cp_mesh, [Shard(2)]).full_tensor()` 全量收集（`:841-843`）——"Q 切片、KV 全量"的简化 CP，没有 ring attention。Model 层 `set_cp_mesh` 存 mesh（`:1121-1122`）；forward 按 `_seq_range` 连续块切分 hidden_states/position_embeddings/position_ids/cache_position/causal_mask（`:1202-1211`），要求 seqlen 整除 CP 世界数（`:1270`）、禁与 KV cache 同用（`:1212`）、禁与 output_attentions 同用（`:787`）。CP 开启时跳过 `_update_causal_mask` 改手搓下三角 -inf 掩码（`:1180`、`:1199-1201`）。甄别要点：`Qwen2VLFlashAttention2.forward` 虽带 cp_mesh 形参（`:681`）但函数体不消费——**CP 只有 SDPA 后端真正可用**。`qwen2_5_vl.py` 是同范式 2.5 版（PatchEmbed/PatchMerger/窗口注意力），模块级 import DTensor/DeviceMesh（`qwen2_5_vl.py:21-23`）。

**模型包装层（models/）**。`vlm_base.py` 的 `VLMBaseModel` 定义骨架：build_model/forward/training_step、优化器调度、FSDP2 钩子。最关键的是模块级 `_broadcast_to_cp_or_tp_ranks`（`vlm_base.py:426-497`）：CP/TP 组内各 rank 数据批必须对齐，tokens/attention_mask/token_mask/images/videos 经 `broadcast_with_shape_check` 从组内首 rank 广播；`has_images` 布尔先达成共识——任何 rank 没图就全员删 images，全员有图而本 rank 缺则补零占位（`:456-467`）；字符串键走 `broadcast_object` 的 `all_gather_object` 取 rank0 值（`:500-508`）。`vlm_qwen.py` 的 `build_model` 按 model_type 分派：qwen2_5_vl / qwen2_vl 用内嵌网络，qwen2_5 纯文本走 `AutoConfig.from_pretrained` 且给 `set_cp_mesh` 打 `lambda x: None` 补丁（`vlm_qwen.py:59-76`）；lm_head 独立 `nn.Linear`（`:78`）；mm_projector 即 `visual.merger`（`:92-95`）。`_forward` 有 TP 手术注释："TP for LLM but no TP for vision encoder" 时需把 DTensor 转回普通张量（`:258`）；CP 下 logits 做 `full_tensor` 收集（`:369-370`）。freeze_vision_encoder/freeze_mm_projector/freeze_llm 配 lr_multiplier 乘子（`:115-132`）。`vlm_qwen_omni.py` 是 omni1 变体（自述 "modified from vlm_qwen.py"，`:17`）。

**并行层（parallelisms/）**。`parallel_dims.py` 的 `ParallelDims` 声明 dp_replicate/dp_shard(-1 自动推)/cp/tp/pp，乘积不符自动调 dp_replicate 并告警（`:59-67`）；`build_mesh` 只为 >1 维度建轴，再 flatten 出 dp / dp_shard_cp / dp_cp 子 mesh（`:101-104`）——FSDP 分片域显式含 cp 轴。`parallelize_qwen.py` 是施加顺序的权威：TP → 激活检查点 → compile → FSDP/HSDP → DDP（`:62-111`）。`apply_tp`：embed_tokens RowwiseParallel、root norm SequenceParallel、lm_head Colwise 配 loss_parallel（`:126-142`）；每层 plan 用 **llama→qwen names_mapping 表**翻译（`:210-222`）——torchtitan 的 llama plan 直接复用。选择性 AC 的 `_save_list` 含 flash/efficient SDPA aten 算子（`:248-257`）。`apply_fsdp` 对视觉块、解码层、根模块逐级 `fully_shard`（`:362-371`）。`planner.py` 的 RenameLoadPlanner 支持并行度变更后的权重重映射；`torchtitan_utilts.py`（拼写如此）承接分布式工具。

## 三、外部连接

上游血缘三支：HF transformers（固定 commit 拷贝）、torchtitan（`parallelize_qwen.py:37-38` 保留注释掉的 torchtitan import）、PyTorch 原生（FSDP2/DTensor/DeviceMesh）。下游以 `text_encoder_class="reason1p1_7B"` 遍布 reason_embeddings 实验族、action 条件模型（`exp_2B_action_conditioned_rectify_flow.py:166`）与蒸馏线。`tokenizer/processor.py` 封装 chat template；`utils/load.py` 做 S3 协调下载；`utils/fused_adam.py` 处理 DTensor 本地张量。

## 四、数据流

训练一步：webdataset 批 → `_broadcast_to_cp_or_tp_ranks` 组内对齐 → processor 应用 chat template → 视觉塔全量算 patch 嵌入（无 CP/TP）→ merger 投影与文本 token 拼接 → `Qwen2VLModel.forward`：CP 时按 `_seq_range` 切成每 rank 连续段 → 逐层 SDPA 内 K/V `full_tensor` 收集后做注意力（每 rank 只算自己 Q 段）→ norm + lm_head（TP 列切+loss_parallel）→ CP 下 logits 收齐算 loss → FSDP2 反传。训完的模型在视频侧当文本编码器，输出嵌入作为 text conditioning 喂给 rectified flow 世界模型。

## 五、设计决策

**为什么 vendored 而非 pip 依赖**：CP 需要把 mesh 深度注入 attention forward 与 Model.forward 的切分，外部 API 做不到；固定 commit 拷贝换"魔改自由+版本稳定"，代价是上游 bugfix 手动跟进（docstring 留 commit 链接就是为了 diff 追踪）。**为什么 CP 用"Q 切片+KV 全量收集"而非 ring attention**：`full_tensor()` 一行搞定，代价是 KV 通信量随 CP 线性增长；对 7B 级 VLM 可接受，也解释了 CP 与 past_key_values 互斥（推理态 KV 收集无意义）。**为什么数据组内广播**：CP/TP 组内各 rank 处理同一样本不同切片，而 webdataset 采样按 DP 切——rank 间数据天然不齐，广播是对齐成本最低的补救。**只有 SDPA 支持 CP** 要记住：CP 时若选 flash_attention_2，cp_mesh 会被静默忽略而非报错。**双份 dcp_checkpointer 与 torchtitan_utilts 拼写**暴露快速移植期工作方式——先复制再按需改，未回头清理。

## 六、新人提示

读这条线的最佳顺序：`parallel_dims.py`（mesh 语义）→ `vlm_qwen.py:41-100`（模型组装）→ `qwen2_vl.py` 只精读三段：`:841-843`（KV 收集）、`:1180-1212`（序列切分）、`:1268-1275`（_seq_range），其余与 HF 上游逐行同构可对照官方文档。练习：① 解释 has_images 共识为什么必须"任何 rank 没图就全员删"而不是"没图的 rank 填零"（提示：变长图像 token 与 all_gather_object 的 rank0 截断语义）；② 用 `parallelize_qwen.py:210-222` 的 names_mapping 手推一层 Qwen decoder 的 TP 切分：q/k/v 列切、o 行切、gate/up 列切、down 行切，画出 Shard(1)↔Replicate 转换点。

> 甄别说明：上游 commit 链接、cp_mesh 注入点、`full_tensor` KV 收集、_seq_range 整除断言、SDPA 独占 CP（flash 前向不消费 cp_mesh）均源码逐处核实；"reason1p1_7B 即 reason1 产出的 7B 文本编码器"由配置命名与 teacher 路径交叉印证，未追权重实测；torchtitan 血缘由注释残留与结构同构推断。
