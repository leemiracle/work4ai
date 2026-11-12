# 04 · quantization 三件套：残差向量量化（RVQ）——音频 token 的来源

> 锚点基线：`moshi/moshi/quantization/base.py`（171 行）、`core_vq.py`（385 行）、`vq.py`（362 行）。core_vq 移植自 lucidrains/vector-quantize-pytorch（经 Kyutai/Meta audiocraft 双重转手），vq.py 是面向 Mimi 的门面层。

## ① 角色定位

RVQ 回答一个问题：**连续的 512 维 latent 帧如何变成语言模型能吃的离散 token**。做法是串行多次"最近邻查表"：第一级码本粗量化，残差交给第二级，逐级细化。Personaplex 的 Mimi 共 32 级码本、每级 2048 个码字（loaders.py:68-74），推理时只激活前 8 级——最终每 80ms 音频帧产出 8 个 [0,2048) 整数，即 Moshi LM 的 8 个音频码本输入。`SplitResidualVectorQuantizer` 还把第一级单独拆出（语义码本，与 WavLM 蒸馏对齐），其余归声学支路——这就是 Mimi 论文"语义/声学分治"的代码形态。

## ② 内部结构

### base.py：接口与哑实现

- `QuantizedResult` 数据类（base.py:22-28）：量化输出 x、codes、bandwidth（kb/s）、可选 penalty 与 metrics。
- `BaseQuantizer`（base.py:31-97）：`forward/encode/decode/cardinality/total_codebooks/num_codebooks/set_num_codebooks` 抽象接口；`semantic_quantizer`/`acoustic_quantizer` 属性默认返回 self（base.py:70-84），等子类覆写。
- `DummyQuantizer`（base.py:100-170）：不量化的假量化器（训练对照用），bandwidth 公式 `q.numel()*32*frame_rate/1000`（base.py:132）按 32 位浮点直存估算。

### core_vq.py：量化内核

- `EuclideanCodebook`（core_vq.py:73-219）：码本不直接存权重，存两个 buffer——`cluster_usage`（初始全 1，core_vq.py:121）与 `embedding_sum`（初始全 0，core_vq.py:109/122），码字按需计算 `embedding = embedding_sum / cluster_usage.clamp(min=epsilon)`（core_vq.py:142-150 的 property，惰性缓存到 `_embedding`）。`_load_from_state_dict` 做旧名迁移：`inited→_initialized`、`cluster_size→cluster_usage`、`embed_avg/embed_sum→embedding_sum`（core_vq.py:126-140）——兼容 Kyutai/Meta 旧 checkpoint 命名。`_quantize` 是 `torch.cdist(x, embedding, p=2).argmin(-1)`（core_vq.py:183-184）；`decode` 是 `F.embedding(codes, self.embedding)` 查表（core_vq.py:205）。
- `VectorQuantization`（core_vq.py:222-308）：单级 VQ。可选 `codebook_dim != dim` 时的 Linear 投影（core_vq.py:255-261）；布局变换 `b d n → b n d`（core_vq.py:277-283）。
- `ResidualVectorQuantization`（core_vq.py:311-384）：RVQ 主循环。`forward`（core_vq.py:324-363）：`residual = residual - quantized.detach()`、`quantized_out += quantized`（core_vq.py:348-350），metrics 键按 `f"_{i + codebook_offset}"` 逐级打标（core_vq.py:360）。`encode`（core_vq.py:365-376）与 `decode`（core_vq.py:378-384）是推理真正走的两条路。

### vq.py：门面层

- `ResidualVectorQuantizer`（vq.py:41-189）：构造里先建 input/output 1×1 卷积投影（512↔256 维，vq.py:101-112），再委托 core 的 `ResidualVectorQuantization`（vq.py:113-121）。`forward` 算带宽 `bw_per_q = log2(bins)*frame_rate/1000`（vq.py:141）——2048 码本 12.5fps 时每级 11×12.5/1000 = 0.1375 kb/s，8 级共 1.1 kb/s。`encode` 对空输入直接返回空张量（vq.py:158-159），流式边界友好。`set_num_codebooks` 带 `n <= max_n_q` 断言（vq.py:183-185）。
- `SplitResidualVectorQuantizer`（vq.py:192-361）：**Mimi 实际用的量化器**。`n_q_semantic=1`（vq.py:210）：`rvq_first` 管 1 级语义码本，`rvq_rest` 管 31 级声学码本且 `codebook_offset=1`（vq.py:231-240，metric 编号不从 0 重复）；两支都 `force_projection=True`（各自带独立的 512→256 投影，vq.py:232/237）。`no_quantization_mode="same"` 时给两支固定 `generator_seed=1234` 保证随机决策同步（vq.py:227-228）。`forward`（vq.py:262-306）两支并行跑同一输入，嵌入相加（vq.py:281）、codes 沿码本维拼接（vq.py:282-284）、带宽相加（vq.py:288）、penalty 经 `_renorm_and_add` 按实际级数加权合并（vq.py:245-260）。`decode` 前 `n_q_semantic` 列走 first、其余走 rest（vq.py:320-326）。`set_num_codebooks` 断言 `n >= n_q_semantic`（vq.py:354-356）且只调节 rest 支。

## ③ 外部连接

- 唯一装配点：loaders.py:140-142 以 `dimension=256, n_q=32, bins=2048, input/output_dimension=512` 建 Split 量化器；loaders.py:162 随即 `set_num_codebooks(8)` 收敛到 8 级。
- MimiModel 持它为 `self.quantizer`（compression.py:153），`encode` 走 `quantizer.encode`（compression.py:379），`decode_latent` 走 `quantizer.decode`（compression.py:421-423）；训练态的 forward 冻结逻辑按 isinstance 分派 Split/普通两种（compression.py:302-313）。
- LM 侧的 `card` 直接取 `bins`（loaders.py:98 `_lm_kwargs["card"] = _quantizer_kwargs["bins"]` = 2048）——**量化器码本大小就是语言模型音频词表大小**，两套组件由此锁死。

## ④ 数据流

编码（每帧）：512 维 latent（12.5Hz，已过 resample）→ `rvq_first.input_proj` 512→256 → 第一级 cdist 最近邻 → codes[:, 0]（语义 token）→ 同一原始 latent 也进 `rvq_rest`：投影后逐级"量化-减残差"31 层，但 `n_q=7` 时只算 7 级 → codes[:, 1:8]（声学 token）→ 拼成 [B, 8, T]。解码（反向）：codes 切两段分别查表、输出投影回 512 维、两支相加（vq.py:320-326 + vq.py:167-173）→ 还原 latent 交给 SEANetDecoder。注意两支的"残差"互不共享——first 支只量化一级就是完整语义码流，rest 支的残差链从原始输入重新起算，两支嵌入**相加**而非级联。

## ⑤ 设计决策

- **usage/sum 表示法而非直接存码字**：EMA 训练时只动统计量不动码字，推理时 property 一次除法得到码本。这让 `_load_from_state_dict` 的旧名迁移（core_vq.py:126-140）只需搬 buffer，也使"死码替换"这类训练期操作退化为统计量改写。
- **语义/声学分叉而非纯串行 RVQ**：第一级独立投影、独立残差链，保证语义码流不被声学残差污染（第一级拟合的是与 WavLM 对齐的语义目标）；代价是两支嵌入相加的重建略逊于纯串行，但换来 LM 只依赖首码本即可理解语义的解耦。
- **bandwidth 显式建模**：`log2(bins)*frame_rate` 把"码本大小×帧率"折成比特率，`set_num_codebooks` 即质量-带宽旋钮——同一模型 1/8 级可从 0.1375 kb/s 拉到 1.1 kb/s。
- **codebook_offset 平铺 metrics 命名空间**：两支 RVQ 各自的逐级指标合并到一个 dict 时靠 offset 避免撞键（core_vq.py:360）——小设计，省掉嵌套结构。

## ⑥ 新人提示（坑与勘误）

1. **EMA/死码替换在本仓是死代码（实测勘误）**：`_ema_inplace`（core_vq.py:33-34）、`_replace_expired_codes`（core_vq.py:157-169）、`_broadcast_buffers`（core_vq.py:152-155）**定义后全文件零调用**；`EuclideanCodebook.forward`（core_vq.py:208-219）只做量化，不更新统计量。同理 `VectorQuantization.forward` 的 loss 恒为 `zero_scalar`（core_vq.py:303）——commitment loss 为零。图谱早期摘要描述的"EMA 更新+死码替换"是 lucidrains 原版能力，本推理发行版里码本完全冻结，读代码别在 forward 里找训练逻辑。
2. **`initialize` 形参是摆设**：core_vq.py:209/299 保留形参但函数体不使用（原版用于首帧随机初始化码本）。
3. **语义支的"第一级"不等于时序第一帧**：`n_q_semantic` 切的是码本维度（codes[:, :1]），与时间无关。
4. **两套维度别混**：SEANet/Transformer 侧 512，码本内部 256——所有跨接都经 vq.py 的 1×1 卷积投影；调试打印形状时 256 属于码本空间、512 属于latent 空间。
5. **空帧是合法输入**：vq.py:158-159 的空张量短路是流式边界（重采样层偶发 0 帧输出）的兜底，删掉会在会话首帧崩溃。
6. 复现实验想改码本数：只能改 `set_num_codebooks`（≤32），且 LM 的 delays/embedding 形状按 16+1 流预训练（loaders.py:96-97、121）——服务链路里实际消费 8 级（server.py:231 `tokens[:, 1:9]`），其余 8 级由 LM 预测但解码侧丢弃。
