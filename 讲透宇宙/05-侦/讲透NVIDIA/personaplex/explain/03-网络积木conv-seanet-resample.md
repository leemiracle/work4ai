# 03 · conv.py + seanet.py + resample.py：卷积积木与 SEANet 编解码骨架

> 锚点基线：`moshi/moshi/modules/conv.py`（350 行）、`seanet.py`（416 行）、`resample.py`（140 行），三文件皆带 Kyutai + Meta audiacraft 双版权头，是 Mimi 波形 backbone 的全部积木。

## ① 角色定位

Mimi 音频编解码器的"骨骼与肌肉"在这里：conv.py 提供带因果 padding 与流式能力的卷积原语；seanet.py 把原语组装成 SEANetEncoder/SEANetDecoder（多级下/上采样 + 残差块的对称沙漏结构）；resample.py 则做 Mimi 特有的"帧率变换"——把 SEANet 输出的 25Hz latent 压到 12.5Hz 再进量化器。一句话：24kHz 波形 →（本篇）→ 512 维 latent 帧 →（下篇 RVQ）→ 离散 token。

## ② 内部结构

### conv.py

- 归一化入口 `apply_parametrization_norm`（conv.py:61-68）：只认 `none` 与 `weight_norm` 两种（`CONV_NORMALIZATIONS` frozenset，conv.py:45）。
- padding 数学：`get_extra_padding_for_conv1d`（conv.py:71-78）按 `n_frames = (length - kernel_size + padding_total)/stride + 1` 反推理想长度，保证**最后一个卷积窗是满的**；`pad_for_conv1d` 的 docstring（conv.py:84-92）给出经典反例——不加右补的话转置卷积重建会永久丢一个时间步。`pad1d`（conv.py:98-120）处理短输入的 reflect padding（长度 ≤ padding 时先垫零再反射，conv.py:110-115）；`unpad1d`（conv.py:123-129）对称还原。
- `NormConv1d/NormConvTranspose1d`（conv.py:132-177）：把 `RawStreamingConv1d/ConvTranspose1d`（02 篇）包上 weight_norm 的薄壳。**注意 `causal` 形参被接收但完全没用到**（conv.py:140、165）——因果性实际由上层 StreamingConv1d 的 padding 逻辑决定。
- `StreamingConv1d`（conv.py:189-275）：核心属性链 `_effective_kernel_size = (kernel-1)*dilation+1`（conv.py:239-243）、`_padding_total = effective_kernel - stride`（conv.py:246-247）。forward 四分支（conv.py:253-275）：非流式+causal → 左 padding_total、右 extra（conv.py:263）；非流式+非因果 → 左右均分（conv.py:266-269）；流式 → **只在首帧注入 `state.padding_to_add` 的左 padding 然后归零**（conv.py:272-274），此后因果性全靠 RawStreamingConv1d 的 previous 缓存维持。构造时 stride>1 且 dilation>1 会 warn（conv.py:210-214）。
- `StreamingConvTranspose1d`（conv.py:286-350）：`padding_total = kernel - stride`（conv.py:330）；**只在非流式分支裁剪**——causal 时右裁 `ceil(padding_total * trim_right_ratio)`（conv.py:342-344），`trim_right_ratio` 仅 causal 有意义（断言 conv.py:318-321）；流式分支不裁，因为 Raw 层的 partial 机制已经保证输出恰好完备。
- `TransposedLayerNorm`（conv.py:48-58）：[B,C,T] 适配版 LayerNorm——**全仓零消费者（grep 实证）**，audiocraft 遗产死代码。

### seanet.py

- `SEANetResnetBlock`（seanet.py:42-115）：`hidden = dim // compress`（seanet.py:79）压维；主干是 act→conv→act→conv（kernel_sizes 默认 [3,1]，seanet.py:63）；残差汇合不用 `+` 而用 `StreamingAdd`（seanet.py:98、114-115）——两条支路帧数可能差 1，流式加法器负责对齐；`true_skip=True` 走 Identity，否则 1×1 卷积短路（seanet.py:100-111）。
- `SEANetEncoder`（seanet.py:118-262）：构造即组网。`ratios` **先 reverse**（seanet.py:176，编码器按解码器顺序的逆向下采样）；`hop_length = prod(ratios)`（seanet.py:179）——Personaplex 配置 ratios=[8,6,5,4]（loaders.py:65），hop=960，24000/960=25Hz。结构：首卷积 channels→n_filters（seanet.py:191-201）→ 每级 [n_residual 个残差块（seanet.py:208-223）+ act + stride 卷积 kernel=2*ratio 通道翻倍（seanet.py:226-238）+ mult*=2] → 末卷积到 dimension=512（seanet.py:243-256）。`forward` 带 `@torch_compile_lazy`（seanet.py:260-262）。
- `SEANetDecoder`（seanet.py:265-416）：镜像。ratios **不 reverse**（seanet.py:323）；初始 `mult = 2**len(ratios)`（seanet.py:337）从最深层起；每级 [act + ConvTranspose kernel=2*ratio 通道减半（seanet.py:360-372）+ 残差块×n（seanet.py:374-389）+ mult//=2] → 末卷积回 channels + 可选 final_activation（如 tanh，seanet.py:394-410）。
- `mask_fn/mask_position` 形参（seanet.py:169-170、202-203、240-241）是预留的逐层掩码钩子，本仓构造路径未用。

### resample.py

- `ConvDownsample1d`（resample.py:35-86）：kernel 恒为 `2*stride`（resample.py:67）。非 learnt 模式是**固定权重盒式滤波**——权重锁 `requires_grad_(False)` 并填充 `1/(2*stride)`（resample.py:74-77），输入经 einops `rearrange(x, "b c t -> (b c) () t")`（resample.py:82）按"每通道独立"降采样；learnt 模式则全通道联合、可选 channel_wise 分组卷积（resample.py:53-59）。
- `ConvTrUpsample1d`（resample.py:89-140）：非 learnt 权重填 1.0（resample.py:125-128）；forward 里先用 `torch.ones_like(x[:1])` 探一个 normalization 再相除（resample.py:136-138）——转置卷积在序列边缘会欠覆盖，除以"全 1 输入的响应"恰好归一掉边缘衰减。

## ③ 外部连接

- 上游：loaders.py:132-139 用 `_seanet_kwargs`（dimension=512、n_filters=64、n_residual_layers=1、ratios=[8,6,5,4]、causal=True、pad_mode="constant"、norm="none"，loaders.py:48-67）各建一个 Encoder/Decoder。
- 横向：compression.py:205-220 在 MimiModel 构造时按 `resample_method="conv"` 建 `ConvDownsample1d(2, learnt=False)`/`ConvTrUpsample1d(2, channel_wise=upsample_channel_wise_bug)`——25Hz→12.5Hz 的整数倍 2 变换。
- 下游：SEANet 输出的 512 维 latent 直达 SplitResidualVectorQuantizer（input_projection 在量化器内部，vq.py:104-106）。
- 编解码器 forward 都被 `torch_compile_lazy` 包裹（seanet.py:260、413），且 MimiModel 侧默认以 `no_compile()` 罩住（compression.py:290-295），两层共同决定编译行为。

## ④ 数据流

编码方向一帧 1920 样本的旅程：`StreamingConv1d(1→64, k=7)`（pad_mode="constant"，非 reflect）→ 4 级下采样，每级先过 1 个残差块（k=3 膨胀 2 + k=1）再 stride 卷积（k=16/12/10/8，stride 8/6/5/4）通道 64→128→256→512→1024 → 末卷积 1024→512（k=3）。时间轴 1920→240→40→8→2→1：**一帧恰好变一个 latent 帧（25Hz）**，再经 ConvDownsample1d(2) 减半到 12.5Hz 进 RVQ。解码完全镜像：ConvTrUpsample1d(2) 回 25Hz → decoder_transformer（compression.py 里另接）→ 4 级上采样回 1920 样本。流式语义下每一级的"恰好一帧出一帧"由 02 篇的 previous/partial 缓存协议保证。

## ⑤ 设计决策

- **因果 padding 全部左置**：causal=True 时 padding_total 全补左边（conv.py:263、272-274），流式首帧注入后永久归零——听不到未来，是全双工不打断的物理前提。
- **`norm="none"` 的推理特化**：loaders.py:61-63 注释明言"训练用 weight_norm，推理前权重已预处理成普通卷积"——所以服务态里 NormConv 的 weight_norm 分支实际不激活，等价裸卷积，还规避了 weight_norm 与 torch.compile 的不兼容（compression.py:123-126 注释引 pytorch#121902）。
- **`pad_mode` 在 SEANet 配置里是 "constant"**（loaders.py:64）而非默认 "reflect"（conv.py:206）：reflect 在流式短缓存上会泄露边界信息且实现复杂（conv.py:104-115 的补丁正说明这一点），constant 零值与静音天然对齐。
- **非 learnt 盒式滤波做帧率变换**：25→12.5 只是 2 倍降采样，用可学习卷积收益微小还引入新参数；固定 1/(2*stride) 权重无参数、无训练负担、因果稳定，且上采样侧用"全 1 探针归一化"免费拿到正确边界（resample.py:136-138）。
- **`upsample_channel_wise_bug=True` 默认保留**（compression.py:142、219）：参数名自嘲——上游实现里上采样按通道独立是"bug"，但官方权重就是带着这个 bug 训的，推理必须忠实复现，否则latent 重建系统性走样。

## ⑥ 新人提示（坑与勘误）

1. **Encoder 的 ratios 会 reverse 而 Decoder 不会**（seanet.py:176 vs 323）：传同样的 [8,6,5,4]，Encoder 实际按 [4,5,6,8] 逐级下采样。改 hop_length 或对称性相关代码时必看这一步，否则两层 hop 对不上且不报错。
2. **流式下 ConvTranspose 不裁剪、非流式裁剪**（conv.py:334-349）：单测对流式/非流式输出长度对齐时，记得非流式路径多一个 unpad 步骤；`trim_right_ratio` 在流式推理中无效。
3. **残差块里不能把 `StreamingAdd` 换成普通加法**：残差支路（Identity）与主干（有下采样相位滞后）帧数可差 1，普通 `+` 会直接广播错位或崩溃。StreamingAdd 的缓存语义（streaming.py:444-461）是对齐的关键。
4. `NormConv1d` 的 `causal` 参数是摆设（conv.py:140-148），真正决定因果行为的是外层 `StreamingConv1d.causal`——读代码别被双层同名参数迷惑。
5. `resample.py` 的两个类不是 `StreamingModule`，自己不持有流式状态（resample.py:35/89 直接 nn.Module）——流式因果性完全依赖内部 `StreamingConv1d/ConvTranspose1d` 子模块的自动传播（02 篇 `_apply_named_streaming`）。
6. **`n_residual_layers=1`**（loaders.py:53）是 Personaplex/Mimi 的轻量配置，不是 SEANet 论文默认的 3——按论文参数复刻会导致权重形状对不上 checkpoint。
