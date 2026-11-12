# 01 · model.py：编码器-解码器 Transformer 骨架

## 角色定位

model.py（352 行）是 Whisper 论文 Figure 1 的逐块实现，也是全图谱的枢纽节点（fanIn 7 / fanOut 24）：`__init__.py` 装配它（whisper/__init__.py:154-156）、decoding.py 驱动它做自回归生成（whisper/decoding.py:155-163）、transcribe.py 经由 decode 方法消费它（whisper/model.py:351）、timing.py 则直接伸手进它的 cross_attn 模块抓注意力权重（whisper/timing.py:187-192）。读懂这个文件，其余模块都是它的"周边"。

一个必须先钉版的勘误：**任务书与图谱摘要中的 "AudioEncoderChunked" 类不存在**。全仓 grep "Chunked" 零命中；编码器类名是 `AudioEncoder`（whisper/model.py:181），仓库也没有任何"分块编码"机制——长音频切 30 秒窗口是 transcribe.py 的编排职责（whisper/transcribe.py:272-286），模型层永远只看一个 30 秒块。

## 内部结构

自底向上五层积木：

1. **ModelDimensions**（whisper/model.py:25-36）：10 个 int 字段的 dataclass，音频侧与文本侧各 5 维（n_mels/n_audio_ctx/n_audio_state/n_audio_head/n_audio_layer + n_vocab/n_text_ctx/...）。它从 checkpoint 的 `dims` 键反序列化而来，**网络形状完全由权重文件决定**，代码里没有一个写死的层数。
2. **三个 dtype 适配子类**（whisper/model.py:39-59）：LayerNorm 强制 float32 计算再 cast 回（whisper/model.py:41）；Linear/Conv1d 把权重 cast 到输入 dtype（whisper/model.py:46-50、57-59）。fp16 推理下数值稳定性全靠这三个小包装。
3. **sinusoids**（whisper/model.py:62-68）：经典正弦位置编码，`max_timescale=10000`，sin/cos 拼接（whisper/model.py:68）。只给编码器用；解码器用的是**可学习**位置嵌入（whisper/model.py:221）——同一文件里两种位置编码并存是有意为之。
4. **MultiHeadAttention**（whisper/model.py:81-146）：自注意力与交叉注意力统一实现。q/k/v/out 四个 Linear（whisper/model.py:87-90，注意 key 无 bias）。kv_cache 命中时交叉注意力直接复用缓存的 K/V 不再投影（whisper/model.py:101-109）。`qkv_attention` 双路径：SDPA 快路径（whisper/model.py:123-135）不返回注意力权重；手写慢路径（whisper/model.py:137-144）返回 detach 的 qk 矩阵——词级时间戳就靠它。
5. **ResidualAttentionBlock**（whisper/model.py:149-178）：pre-LN 结构，自注意力 + 可选交叉注意力 + 4 倍宽 GELU MLP（whisper/model.py:161-164）。编码器块 `cross_attention=False`，解码器块为 True（whisper/model.py:225）。

两大主体：

- **AudioEncoder**（whisper/model.py:181-211）：conv1（kernel 3、padding 1、stride 1）+ conv2（stride 2）两层 GELU 卷积（whisper/model.py:186-187、200-201），把 (80, 3000) 的 mel 谱变成 (1500, d) 的 token 序列——**降采样恰好 2 倍是 0.02s/音频 token 的来源**；加正弦位置编码（whisper/model.py:188、205）后过 n_layer 个自注意力块，ln_post 收尾（whisper/model.py:210）。
- **TextDecoder**（whisper/model.py:214-256）：token 嵌入 + 位置嵌入按 kv_cache 偏移切片（whisper/model.py:241-245，增量解码的关键三行）；上三角 -inf 因果掩码注册为非持久 buffer（whisper/model.py:231-232）；输出层与嵌入**权重绑定** `logits = x @ E^T`（whisper/model.py:252-254）。

顶层 **Whisper**（whisper/model.py:259-352）组装两者，并携带：alignment_heads 稀疏 buffer（默认后半层全部头，whisper/model.py:279-283）、`set_alignment_heads` 从 base85+gzip 字节串解码注入（whisper/model.py:285-292）、`install_kv_cache_hooks` 用 forward hook 缓存 K/V（whisper/model.py:317-348），最后把 detect_language/transcribe/decode 三个函数绑成方法（whisper/model.py:350-352）——这是 Python 里少见的"类定义晚于功能、靠赋值拼装"的风格。

## 外部连接

- 上游：`load_model` 按 checkpoint dims 构造实例并 load_state_dict（whisper/__init__.py:154-156），官方模型额外注入 alignment_heads（whisper/__init__.py:158-159）。
- 下游消费点：decoding.py 的 PyTorchInference 调 `install_kv_cache_hooks`（whisper/decoding.py:157）并按 beam 重排缓存（whisper/decoding.py:172-176 调 whisper/model.py:317 的缓存字典）；timing.py 对 `block.cross_attn` 装 hook 抓 qk（whisper/timing.py:187-192）、用 `disable_sdpa`（whisper/model.py:71-78）强制走返回权重的慢路径、并读 `alignment_heads.indices()`（whisper/timing.py:207）。
- 属性被外部依赖：`is_multilingual`（阈值 n_vocab≥51865，whisper/model.py:311）与 `num_languages`（whisper/model.py:314-315）直接决定 tokenizer 构造参数（whisper/decoding.py:518-523）。

## 数据流

一次 `forward(mel, tokens)`（whisper/model.py:300-303）：

```
mel (b, 80, 3000)
  → conv1/GELU → conv2/GELU         (b, d, 1500)     whisper/model.py:200-201
  → permute + sinusoidal PE          (b, 1500, d)     whisper/model.py:202-205
  → n_layer × 自注意力块 + ln_post    (b, 1500, d)     whisper/model.py:207-210
tokens (b, n)
  → embedding + 位置嵌入(带 offset)   (b, n, d)        whisper/model.py:241-245
  → n_layer × (因果自注意力 + 交叉注意力 + MLP)         whisper/model.py:248-249
  → ln + x @ E^T                     (b, n, 51865)    whisper/model.py:251-254
```

tiny 模型 dims：音频侧 4 层/384 维/6 头，文本侧 4 层/384 维/6 头；large 则 32 层/1280 维。所有形状差异都藏在 checkpoint 里。

## 设计决策

1. **权重绑定**省掉整个输出投影矩阵（51865×d 参数），对小模型是显著节省，也和 GPT 系传统一致。
2. **编码器固定正弦、解码器可学习位置编码**：音频时间轴是绝对连续的，文本位置是离散相对的，两种归纳偏置各取所需。
3. **KV 缓存用 forward hook 而非改造注意力代码**（whisper/model.py:334-345 的 save_to_cache：首 token 或超长时整体保存，否则沿 dim=1 拼接）——注意力实现保持纯净，缓存逻辑可整体装卸。
4. **SDPA 可用性探测 + 运行时开关**：import 探测（whisper/model.py:16-22）+ 类属性 `use_sdpa` + contextmanager（whisper/model.py:71-78），旧版 torch 优雅降级。
5. **beam 与 SDPA 的 batch 失配修复**：K/V batch=1 时 expand 成 stride-0 视图避免拷贝（whisper/model.py:124-130）—— fused kernel 拒绝广播 batch 的工程级补丁。
6. **无 dropout、无训练分支**：纯推理仓库的极简姿态。

## 新人提示

- 想"改模型结构"基本是死路：形状由权重决定，改代码不改权重只会 load_state_dict 失败。真正的扩展点是换 dims 的 checkpoint。
- 调试数值问题时先看三个 dtype 子类（whisper/model.py:39-59），fp16 下的溢出/精度问题九成在这里有伏笔。
- 手动验证前向：`model = whisper.load_model("tiny"); logits = model(mel, tokens)`，mel 用 `whisper/audio.py:110` 的 log_mel_spectrogram 造，tokens 至少含 sot 序列（whisper/tokenizer.py:159）。
- 记住两个魔法数：51865（多语言词表下界，whisper/model.py:311）与 1500（30s 音频 token 数，由 conv stride 2 决定）。

## 勘误

1. 图谱/任务书提到的 "AudioEncoderChunked" 不存在，实为 `AudioEncoder`（whisper/model.py:181）；仓内亦无分块编码概念，分窗在 transcribe 层。
2. 图谱称 sinusoids "fanIn 3"，实际它只被 AudioEncoder 一处调用（whisper/model.py:188），fanIn 统计包含的是文件级聚合。
