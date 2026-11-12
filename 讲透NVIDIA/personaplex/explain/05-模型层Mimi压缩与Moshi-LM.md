# 05 · compression.py + lm.py + loaders.py：Mimi 压缩模型与 Moshi 多流 LM

> 锚点基线：`moshi/moshi/models/compression.py`（475 行）、`lm.py`（1178 行，本仓最大源文件）、`loaders.py`（365 行）。三者构成"音频 tokenizer + 自回归生成引擎 + 权重装配"的模型层全栈。

## ① 角色定位

**Mimi**（compression.py）= 音频 tokenizer：SEANet 编码器把 24kHz 波形压成 12.5Hz latent，RVQ 离散化成 8 码本 token；解码方向反向。**Moshi**（lm.py）= 多流语音语言模型：一个 32 层主 Transformer 同时建模"文本 + 16 路音频"共 17 条 token 流，配一个 6 层 Depformer 逐码本并行生成音频；`LMGen`（lm.py:646）把这套模型包成逐帧步进的自回归引擎，是 server.py/offline.py 唯一对话入口。**loaders.py** = 从官方超参字典复刻网络形状并装载 HF 权重，含 cpu_offload 分支。7B 之名来自 `_lm_kwargs`：dim=4096、32 层、hidden_scale=4.125（loaders.py:92-122）。

## ② 内部结构

### compression.py

- `CompressionModel` 抽象 API（compression.py:40-90）：encode/decode/decode_latent + channels/frame_rate/sample_rate/cardinality 等属性。
- `MimiModel`（compression.py:102-423）：五件套 encoder/decoder/encoder_transformer/decoder_transformer/quantizer。帧率桥：`encoder_frame_rate=25` 与目标 `frame_rate=12.5` 不等时按 `resample_method` 建下/上采样器（compression.py:192-220），且断言"causal 不能配 interpolate"（compression.py:193-195）——插值要看未来帧。`_MimiState`（compression.py:93-99）持有两个 `CUDAGraphed` 包裹的侧 Transformer，`_init_streaming_state` 在 cuda 上启用、否则 disable（compression.py:222-231）。`_to_framerate/_to_encoder_framerate`（compression.py:264-288）双向换帧率；`forward`（compression.py:297-342，训练用）带帧数守恒断言（compression.py:320-325）与输出裁剪（compression.py:337-338）。推理主路 `encode`（compression.py:368-380）= `_encode_to_unquantized_latent`（graphed 与非 graphed 分叉在 compression.py:359-364）+ `quantizer.encode`；`decode`（compression.py:398-419）= `decode_latent` + 上采样 + graphed decoder_transformer + SEANetDecoder。
- `WrapperCompressionModel`（compression.py:426-474）：纯委托包装，兼容层。

### lm.py

- 常量区（lm.py:54-57）：`AUDIO_TOKENS_PER_STREAM=8`、`FRAME_RATE_HZ=12.5`、以及**硬编码的 `SILENCE_TOKENS`/`SINE_TOKENS` 两个 8 维向量**——静音帧与 440Hz 正弦帧直接以 token 序列写死，绕过实时编码。
- 延迟模式工具：`_delay_sequence`（roll + padding 回填，lm.py:70-81）、`_undelay_sequence`（roll 回 + mask，lm.py:84-99）。delays=[0,0,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1]（loaders.py:121）：文本流 k=0 与两条音频首流（k=1 agent、k=9 user）零延迟，其余延迟 1 帧——这就是 Moshi 的"多流错帧并行"骨架。
- `LMModel`（lm.py:218-552）：17 路嵌入表 `emb`（card+1=2049，lm.py:289-291）+ `text_emb`（32001，lm.py:295）逐流求和（`embed_codes`，lm.py:425-439）；主 Transformer `StreamingTransformer`（lm.py:301-309）；Depformer 套件：`depformer_in` 多线性层（16 个 4096→1024，lm.py:324-328）、`depformer_emb` **只有 dep_q-1=15 张**（"最后一个码本永远不做输入"，lm.py:333-336）、`depformer` 本体（lm.py:340-347）且 `set_streaming_propagate(False)`（lm.py:348）、16 个输出头 `linears`（lm.py:351-353）。特殊 token 体系：`initial_token_id=card`、`zero_token_id=-1`、`ungenerated_token_id=-2`（lm.py:355-390），`ScaledEmbedding` 对 -1 输出精确零向量（lm.py:207-215）。训练态 `forward_train`（lm.py:531-552）与流式态 `forward_depformer`（单码本单步，lm.py:457-493）双实现。
- `LMGen`（lm.py:646-1177）：构造默认 temp 0.8/0.7、top_k 250/25（lm.py:652-655），`zero_text_code=3`（lm.py:677），预生成 `_zero_frame`/`_sine_frame`（lm.py:681-684）。`_LMGenState`（lm.py:555-567）持环形 cache/provided（长度 max_delay+3）+ 三个 `CUDAGraphed`（lm.py:720-722）。核心状态机 `prepare_step_input`（lm.py:726-812）：用户 8 路 token 写入 k=9..16（lm.py:754-759）、agent 流写 k=1..8（lm.py:761-774）、文本写 k=0（lm.py:776-779），写入位置 `(offset+delay)%CT`（lm.py:757）；offset=0 时播 initial token 并返回 None（lm.py:791-796）。`step`（lm.py:814-850）经 graphed_main 出文本 logits；`process_transformer_output`（lm.py:875-958）采样文本、`graphed_depth` 跑 Depformer 出 16 路音频、未 provided 的槽位回填采样值（lm.py:903-912）、`offset <= max_delay` 前不产出（lm.py:933-940）、最终按 `(offset - max_delay + delays)%CT` gather 出对齐帧（lm.py:944-950）。`depformer_step`（lm.py:1129-1177）：`assert not depformer.is_streaming` 后 `with depformer.streaming(B)` **每步重建状态**（lm.py:1141-1142），16 码本链式条件生成（每步以上一码本采样值为下一码本输入，lm.py:1143-1164），provided 槽位 teacher-forcing（lm.py:1159-1163）。
- 系统提示词流水线（lm.py:960-1127）：`load_voice_prompt` 读 WAV、LUFS 归一到 -24（lm.py:967）；`load_voice_prompt_embeddings` 读 `.pt` 缓存（lm.py:977-983）；`_step_voice_prompt_core` 是**生成器**——每个 checkpoint `yield` 一次给 async 外壳插 `is_alive` 探活（lm.py:1025-1062），嵌入回放路径最后整块 `cache.copy_`（lm.py:1038）；`step_system_prompts(_async)`（lm.py:1117-1127）按"音色→静音→文本→静音"四段推进。评估钩子 `create_loss_report`（lm.py:570-643）算 forced token 的 rank 与逐流 CE。

### loaders.py

- 超参字典 `_seanet/_quantizer/_transformer/_lm_kwargs`（loaders.py:48-122）；`DEFAULT_REPO='nvidia/personaplex-7b-v1'`、`MIMI_NAME='tokenizer-e351c8d8-checkpoint125.safetensors'`（loaders.py:44-45）。
- `get_mimi`（loaders.py:129-163）：双 ProjectedTransformer（d_model 512/8 层/context 250），末尾 `set_num_codebooks(8)`（loaders.py:162）。
- `get_moshi_lm`（loaders.py:166-260）：**L187 硬改 `dep_q=16`** 覆盖字典里的 8；meta device 免真实初始化（loaders.py:197）；Patch 1 扩展 depformer self_attn 权重（loaders.py:218-229）；Patch 2 缺失键按 `8→16` 复制补齐（gating/linears/depformer_in/depformer_emb 四组，loaders.py:231-251）；`strict=False, assign=True` 装载（loaders.py:258）。
- `_get_moshi_lm_with_offload`（loaders.py:263-364）：accelerate `infer_auto_device_map`（no_split=StreamingTransformerLayer，loaders.py:344-349）+ `dispatch_model`（loaders.py:357-361）。

## ③ 外部连接

- server.py:434-445 与 offline.py:193-206 是仅有的两个装配消费者；`LMGen.step` 被 server.py:125/227、offline.py:103/279 调用。
- `step_system_prompts_async`（server.py:283）与同步版（offline.py:253）分别服务两条产品线。
- 向下依赖：modules 三件套（03 篇）、RVQ（04 篇）、transformer.py 的 `StreamingTransformer/create_norm_fn`（lm.py:47-50）、`utils/sampling.sample_token`（lm.py:44）。
- voice prompt 嵌入缓存的写侧也在本层：`save_voice_prompt_embeddings=True` 时 `torch.save({"embeddings", "cache"}, ...pt)`（lm.py:1052-1061），server.py:164-169 的 `.pt` 分支消费它——首会话编码 WAV、后续会话直接回放嵌入+整块 cache 拷贝，音色切换从数秒降到毫秒级。

## ④ 数据流

一个 80ms 步（`lm_gen.step(input_tokens=user_codes)`）：①prepare：8 路用户码本按各自 delay 写入环形 cache 的 k=9..16；②graphed_main：cache 当前列的 17 路 token → embed_codes 求和 → 主 Transformer → 文本 logits；③采样文本（teacher-forcing 若 provided）；④graphed_depth：文本 token + 主干输出 → 16 次 Depformer 链式单步（每次一个码本头）→ 16 路音频 token；⑤未强制槽位回填 cache；⑥按"产出位置 = offset - max_delay + delay"gather 出 17 维输出（1 文本 + 16 音频）。server.py 只取 `tokens[:, 1:9]` 送 Mimi 解码——**16 路 audio 生成、8 路解码发声**，其余 8 路是模型内部的用户侧回声通道。Mimi 侧一帧的镜像流：1920 样本 → SEANet→25Hz→降 12.5Hz→RVQ codes [1,8,1]。

## ⑤ 设计决策

- **Depformer 每步重建流式状态**（lm.py:1141-1142 + propagate=False lm.py:348）：Depformer 的"序列"是单个时间步内的 16 个码本，与主干的跨时间 KV cache 语义正交——放进主干传播树会互相污染，索性隔离，`with` 语句进出即状态生命周期。
- **环形 cache + delays 的统一读写**：主干的 KV cache 在 Transformer 内部，token 层的错帧对齐全部压到 `cache` 一个张量上，写入与产出共用 `% CT` 取模寻址（lm.py:757/946）——任意 delay 组合零额外存储。
- **静音/正弦帧 token 化**（lm.py:56-57）：提示词间隔帧不跑 Mimi 编码，直接喂预置 token——省一次编码器前向且内容完全确定。
- **dequantized depformer_in 多线性**：16 个码本各配一个 4096→1024 投影（lm.py:324-328），让 Depformer 为每条音频流定制信息瓶颈；Patch 2 的 8→16 权重复制（loaders.py:231-251）说明官方 checkpoint 只训了 8 套、推理扩到 16 套时后 8 套直接克隆——**扩码本不重训**的工程捷径。
- **cpu_offload 用 accelerate 而非自研**（loaders.py:263-364）：流式推理的逐帧小算子天然适合层间搬运，`no_split_module_classes=["StreamingTransformerLayer"]` 保证注意力层不被劈到两块设备。

## ⑥ 新人提示（坑与勘误）

1. **dep_q 双标**：`_lm_kwargs["dep_q"]=8`（loaders.py:97）在 get_moshi_lm 里被硬改为 16（loaders.py:187）。读配置字典会得出"Depformer 8 码本"的错误结论，以 L187 为准；server.py:230 的断言 `dep_q+1=17` 才是运行时真相。
2. **AUDIO_TOKENS_PER_STREAM=8 的三重一致性**：lm.py:54 的常量、loaders.py:162 的 `set_num_codebooks(8)`、server.py:231 的 `tokens[:, 1:9]` 必须同值，改任何一处而不同步会静默错位（码本错配不报形状错，只出杂音）。
3. **`forward_train`/`create_loss_report` 在服务链路零调用**（grep 实证）：训练/评估遗产，读代码可跳过 lm.py:495-652。
4. `encode_from_sphn` 里 `max_batch` 被强制改 1（lm.py:161-162 "TO-DO: Fix the batching bug"）——形参 max_batch 是谎言，批量编码路径有已知 bug 未修。
5. **delays 索引 9 的零延迟**是用户侧首码本（k=9）——用户音频比 agent 音频"早一帧"可见，这是全双工打断响应的延迟设计，不是笔误。
6. `.pt` 音色缓存与源 WAV **必须同版本模型**：cache 张量形状绑死 num_codebooks×(max_delay+3)，升级码本数后旧 `.pt` 会 `copy_` 形状不匹配崩溃；voices.tgz 里的官方 `.pt` 与 `.wav` 是成对的（server.py:164-169 按后缀分流）。
