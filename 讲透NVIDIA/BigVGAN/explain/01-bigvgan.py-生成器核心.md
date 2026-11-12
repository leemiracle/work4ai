# 01 · bigvgan.py——生成器核心（BigVGAN / AMPBlock / snake 激活族）

## 角色定位

bigvgan.py 是全仓被依赖最多的模型文件（图谱 fanIn=16）：定义抗混叠残差块 AMPBlock1/2 与主生成器 BigVGAN，把 mel 频谱 `[B, num_mels, T]` 上采样 256x/512x 还原为波形 `[B, 1, time]`。它同时混入 `PyTorchModelHubMixin`（bigvgan.py:244-252），使 `BigVGAN.from_pretrained("nvidia/...")` 一行可用——训练脚本、双推理入口、gradio demo、HF 测试全部消费这一个类。血统改编自 HiFi-GAN（bigvgan.py:4），但把 HiFi-GAN 的 ReLU/LeakyReLU 换成了 snake 周期激活。

## 内部结构

三个类逐层组装：

- **AMPBlock1**（bigvgan.py:31-147）：双卷积路。convs1 按 dilation=(1,3,5) 膨胀（bigvgan.py:56-70），convs2 固定 dilation=1（bigvgan.py:73-87）；forward 用 `self.activations[::2]`/`[1::2]` 交错切片，`a1→c1→a2→c2` 后残差（bigvgan.py:133-139）——激活在卷积**之前**，共 6 个 Activation1d。
- **AMPBlock2**（bigvgan.py:150-241）：单卷积路（convs 只有膨胀支），每层 `a→c` 后残差（bigvgan.py:232-237）。九配置全选 `"resblock": "1"`（bigvgan.py:291-298 分派）。
- **BigVGAN**（bigvgan.py:244-493）：conv_pre 把 num_mels 投到 1536 通道（bigvgan.py:286-288）；ups 为 `nn.ModuleList[ModuleList[ConvTranspose1d]]` 双层嵌套（bigvgan.py:301-317，通道按 `1536//2^(i+1)` 逐级减半）；每级挂 3 个 AMPBlock 并联取均值（bigvgan.py:371-376）；尾部 SnakeBeta→conv_post(ch→1)→tanh（bigvgan.py:379-383）。

snake 激活族在 activations.py：`Snake: x + (1/a)·sin²(ax)`（activations.py:60），`SnakeBeta: x + (1/b)·sin²(ax)`（activations.py:124）——beta 独立控制幅值、alpha 控制频率，二者逐通道可学习，`alpha_logscale=True` 时以 log 空间存储（activations.py:42-45/101-106）。

## 外部连接

依赖 activations.py（snake 族）、alias_free_activation.torch/cuda 的 Activation1d（bigvgan.py:19，构造时按 `use_cuda_kernel` 懒加载，bigvgan.py:95/195/273）、utils 的 init_weights/get_padding（bigvgan.py:18）、env 的 AttrDict。被 train.py:72、inference.py:16、inference_e2e.py:15、demo/app.py:16/242 导入。

## 数据流

forward（bigvgan.py:361-387）：mel→conv_pre→[上采样 2x/4x→3×AMPBlock 均值]×6→activation_post→conv_post→tanh 或 clamp（v2 配置 `use_tanh_at_final=false` 时 `clamp(-1,1)`，bigvgan.py:382-385）。训练后可 `remove_weight_norm()`（bigvgan.py:389-401）提速推理；`_from_pretrained` 加载失败自动去 weight_norm 重试（bigvgan.py:484-491），兼容 HF 上已去范数的权重。

## 设计决策

① 激活前置而非后置——snake 先给卷积提供周期基函数，卷积再做线性组合；② 多 resblock 平均（bigvgan.py:376）而非拼接，压参数量并稳频带覆盖；③ `use_bias_at_final`/`use_tanh_at_final` 用 `h.get(..., True)` 兜底（bigvgan.py:348/359）保证 v1 旧配置向后兼容；④ `h["use_cuda_kernel"]=use_cuda_kernel` 写回配置（bigvgan.py:270），让 AMPBlock 无需传参即可读到同一开关。

## 新人提示

读码从 forward 自顶向下；改配置先确认 resblock/activation 两键（错值直接 NotImplementedError，bigvgan.py:296/340）。注意 `_save_pretrained` 会把含 `use_cuda_kernel` 的整个 h dump 进 config.json（bigvgan.py:410-412），自训模型上传后该键会随之扩散。112M 参数量预算打印在 train.py:109。
