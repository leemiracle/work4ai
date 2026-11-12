# 01 · network.py —— CleanUNet 主网络：编码解码 + Transformer 瓶颈

> 锚均从源码核实（commit 9487a8db）。Transformer 组件改编自 jadore801120/attention-is-all-you-need-pytorch（network.py:13-15 注释），主架构为论文原创。

## 角色定位

network.py 是全仓唯一的模型定义文件，384 行承载三层内容：Transformer 五件套（network.py:17-202）、长度补齐工具 padding（network.py:208-223）、主模型 CleanUNet（network.py:226-355）。尾部 `__main__`（network.py:358-384）可加载 config 做前向+反向冒烟测试（L377 构造 [4,1,72000] 输入，L382-383 反向），无需数据集。

## 内部结构

**Transformer 五件套**（教科书式 post-LN 实现）：
- ScaledDotProductAttention（network.py:17-35）：Q/temperature 与 K^T 相乘（L27），mask 为 0 处填 -1e9（L30），softmax+dropout 加权 V（L32-33）。
- MultiHeadAttention（network.py:38-88）：Q/K/V 三组**无偏置**投影（L48-50）→ 分头转置（L68-73）→ 缩放点积 → 拼接投影 + 残差 + LayerNorm（L82-86）。
- PositionwiseFeedForward（network.py:91-111）：两层 FC + ReLU + 残差 + LayerNorm。
- EncoderLayer（network.py:147-159）与 TransformerEncoder（network.py:162-202）：后者持 n_layers 个 EncoderLayer；n_position<=0 时位置编码退化为恒等 lambda（L172-175）。

**CleanUNet 主体**（network.py:226-355）：
- 构造参数默认 encoder_n_layers=8、kernel_size=4、stride=2、channels_H=64、max_H=768、tsfm_n_layers=3（network.py:229-235；configs 覆盖 tsfm_n_layers=5）。
- encoder 每层 = Conv1d(K=4,S=2) + ReLU + Conv1d 1x1 + GLU（network.py:272-277）；通道 H 逐层翻倍、768 封顶（network.py:297-298）。
- decoder 逆序构造：`insert(0,...)` 头插（network.py:288-293），最先插入的末层不带 ReLU（network.py:280-286 注释 "no relu at end"）。
- 瓶颈三件：tsfm_conv1 降维 1024→512、TransformerEncoder（n_position=0、dropout=0.0，network.py:302-311）、tsfm_conv2 升回 512→1024。
- 全部 Conv1d/ConvTranspose1d 经 weight_scaling_init 初始化（network.py:315-317）。

## 外部连接

对 util.py 有两处依赖：顶层 `from util import weight_scaling_init`（network.py:10）与 `__main__` 块内的延迟导入 `from util import print_size`（network.py:374，目标同文件故 scanner 记一条）。下游消费方是 train.py（L53 import、L88 `CleanUNet(**network_config)`）与 denoise.py（L51 import、L81 同款构造）。配置由 configs/DNS-*.json 的 network_config 节驱动（经 train/denoise 的 global 注入）。

## 数据流

forward（network.py:319-355）七步：(B,L)→(B,1,L) 升维（L321-322）→ 按批 std 归一化（L327-328，+1e-3 防零）→ padding 补齐（L329；padding 函数按 D 层 (L-K)/S+1 公式正推再逆推目标长度，network.py:211-219）→ 8 层下采样收集 skip（L332-336）→ 瓶颈：构造下三角因果 mask（L340）→ 512 维注意力（L342-346）→ 逐层上采样 `x += skip[:, :, :x.shape[-1]]`（L349-352）→ 裁剪回原长、乘 std 反归一化（L354）。skip 是**逐元素相加**而非 U-Net 常见的通道拼接。

## 设计决策

1. **因果性靠 forward 内现造 mask**（network.py:340）而非模型属性——注释明言"for non-causal, set attn_mask to None"，一份代码两种用法。
2. **n_position=0 弃用位置编码**：波形下采样 2^8=256 倍后瓶颈序列已短，注意力只需因果偏置不需绝对位置（network.py:310）。
3. **weight_scaling_init**（util.py:162-169，arXiv:1911.13254）：权重与 bias 同除 sqrt(10*std)，waveglow 沿用的早期训练稳定技术（network.py:315-317）。
4. **GLU 门控**（network.py:276）：1x1 conv 把通道扩 2 倍再减半，比纯 ReLU 通道混合更平滑。
5. **padding 保证等长还原**（network.py:208-223）：解码输出严格等于输入长度，免去推理后对齐。

## 新人提示

改模型先跑 `__main__` 冒烟（network.py:358-384）验证形状。注意 tsfm_n_layers 代码默认 3 ≠ 配置 5，对比论文参数表以 configs/DNS-large-full.json L2-13 为准。PositionalEncoding（network.py:122-144）与 get_subsequent_mask（network.py:114-119）是携带而来的死/半死代码——前者全仓未启用，后者逻辑已被 forward 内联（L340）取代。

（不计空格约 2350 字符，锚 60+）
