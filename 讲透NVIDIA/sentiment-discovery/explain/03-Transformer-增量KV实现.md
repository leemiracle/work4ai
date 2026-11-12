# 精讲三：vendored fairseq Transformer 与增量 KV 解码

## 角色定位

model/transformer.py 与 transformer_utils.py 是论文的"对照臂"：验证情感神经元方法不挑架构。两文件头自述 "Code adapted from fairseq"（transformer.py:9、transformer_utils.py:9），是 2018 年 fairseq Transformer 的精简 vendored 版，并被改造成 decoder-only LM：pretrain.py:31-32 用 TransformerModel(DecoderPreprocessor, TransformerDecoder) 组装，"编码器" DecoderPreprocessor（transformer.py:102）把 src_tokens 原样塞进 encoder_out（:106-110）——直通占位，TransformerEncoder（:113）在 LM 主链上是死代码。

## 内部结构

MultiheadAttention 自实现于 transformer_utils.py:20（3*embed_dim 拼合 in_proj_weight :35），不用 torch.nn 版的动机写在代码能力里：增量解码缓存、static_kv、beam search 重排与 fp16 安全掩码。投影族用权重切片而非独立矩阵：in_proj_q 取 [0:E]、k 取 [E:2E]、v 取 [2E:]（:184-197 的 _in_proj 家族）。位置编码双形态：Learned（:244）与 Sinusoidal（:269，tensor2tensor 式构造 :288-305），容量硬编码 256 位置（transformer.py:125-126）对齐字符级短序列。解码器层用 GeLU（transformer.py:353、:387 的 tanh 近似，transformer_utils.py:332-337），编码器层却是 ReLU（:218）——同仓不对称。DecoderLayer 还构造了 encoder_attn 交叉注意力（:362-365）但 forward 从不调用（:370-393 只做自注意+FFN）——LM 形态下的死参数。

## 外部连接

模型装配：TransformerDecoderModel（model/model.py:195）包 TransformerDecoder，load_state_dict 时把旧 checkpoint 的 decoder.* 键重写成 encoder.*（:243-247）；make_generation_fast_（transformer.py:72-99）卸 weight_norm 并把 train 方法换成 raise（:93-99）防误用。Featurizer 侧 TransformerFeaturizer（model/model.py:279）在每条样本的第 seq_len-1 位置取特征（:290 的 fancy indexing）——RNN 臂取 cell state，Transformer 臂取末 token 表示，两臂特征口径在此分叉。

## 数据流

训练：全序列 B×T×C 进 Decoder.forward（transformer.py:272），位置嵌入（:274-277）+ √d 缩放嵌入（:284）后逐层；--chkpt-grad 时按 ceil(√层数) 分块调 torch.utils.checkpoint（:300-306）。增量解码：incremental_state 非空时只取最后一个 token（:279-281），MHA 里 qkv_same 用 data_ptr() 判定（transformer_utils.py:63-64），读 saved_state 的 prev_key/prev_value、与当步 k/v concat 后写回（:101-108），后续步注意力照常 bmm（:120）即可看到全部历史——O(1) 每 token。位置嵌入同步增量：位置号=padding_idx+当前长度（:257-259）。beam search 换序走 reorder_incremental_state（:220，index_select 批维）。

## 设计决策

其一，缓存字典键 = "类名.实例ID.key"（_get_full_incremental_state_key :366-375，_fairseq_instance_id 自动递增）——多层多实例共享一个外层 dict 而不串号。其二，fp16 安全：padding 掩码先转 float 再 masked_fill -inf 再转回（:131-136），fill_with_neg_inf 同理（:390-392）。其三，未来掩码只在训练期施加（:124-127，增量态下天然无需）。其四，MoS（Mixture of Softmax）分支引用了未定义类（transformer.py:246-251）——编译可过、启用必 NameError，是迁入未完成的残迹。

## 新人提示

对照读增量解码三件：MHA 的 saved_state 读写（transformer_utils.py:71-108）、Decoder 的取尾 token（transformer.py:279-281）、Learned 位置嵌入的增量位置号（transformer_utils.py:257-262）。两个坑：transformer_utils.py:172-182 有一段编辑事故残留——引用未定义 attn 的残缺 buffered_mask 与重复 in_proj* 四连，真正生效的是 :184-218 的重定义，别对着死代码debug；改注意力想保留增量能力就必须维护 prev_key/prev_value 的写回与 reorder，漏掉 reorder_incremental_state 会让 beam search 结果错乱。
