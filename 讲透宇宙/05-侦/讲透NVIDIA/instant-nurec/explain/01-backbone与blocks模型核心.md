# 01 · backbone 与 blocks：前馈重建的感知底座

## 角色定位

`instant_nurec/model/blocks/` 与 `instant_nurec/model/backbone/` 构成模型的"感知-预测"两段：blocks 是可复用神经算子库（ViT、DPT、注意力、嵌入），backbone 把算子组装成 Kelvin 领域管线（编码器→解码器）。InstantNuRec 能"单次前馈出 3DGS"（README.md:8），底座就是这一层：一个 Depth-Anything-3 风格的多图 ViT 提特征，一个 DPT 头把特征解码成逐像素高斯参数。

## 内部结构

**ViT 主干** `AlternateAttentionVisionTransformer`（blocks/aa_vit.py:30）：基于 ByteDance Depth-Anything-3 的 DINOv2 ViT，交替使用局部注意力块与全局注意力块。两个关键设计写在头注释与签名里：RoPE 只加在局部逐图注意力层（aa_vit.py:33），全局块保持无位置编码以支持变长多图输入；激活检查点三档 `checkpointing: "all"|"local"|"none"`（aa_vit.py:52）——注释明言"全局块重算计算量大"，所以允许只 checkpoint 局部块。全局 CLS token 是可选参数（`with_default_global_cls_tokens`:70）。

**嵌入件**（blocks/embeds.py）：`PatchEmbed`:25、`PositionalEmbed`:61/`NormalizedPositionalEmbed`:123、时间条件用 `ContinuousTimeEmbed`:186、2D 旋转位置编码 `RotaryPositionEmbed2D`:254 供 aa_vit 局部层消费。

**密集预测头**（blocks/dpt.py）：`DPTReassembleBlock`:31 把 ViT 中间块特征重排到多尺度，`DPTFullHead`:278 逐级融合上采样输出密集预测，支持 zero_init 稳定训练初始化。

**注意力家族**（blocks/attention.py:36-402）：SelfAttention:36、KVProjector:101、CrossAttention:146、CrossAttentionWithKVProjector:233、AttentionBlock:287、ModulatedAttentionBlock:341、CrossAttentionBlock:402。头注释钉版组合层级：AttentionBlock=SelfAttention+FFN/LN，CrossAttentionBlock=CrossAttention+SelfAttention+FFN/LN（attention.py 文件头）。

**backbone 组装**：`KelvinDAv3Encoder`（backbone/encoders.py:69）包装 aa_vit，`encode`:109 接收多相机图像+相机参数，内含 `_RGBNormalize`:45 与 FOV 推导 `_fov_wh_from_pinhole`:100-106（arctan2 出 fov_w/fov_h）；注意 :131 的 TODO——F-Theta 相机当前也用 pinhole fov 近似。`KelvinDPTDecoder`（backbone/decoders.py:89）是核心输出头：`TimeModulatedMotionHead`:94 做时间调制动态头，:296 挂 `GaussianActivations`（activations.py:132），:442 产出 `GaussianParams`（activations.py:87）形状 (B,V,H,W,C)，:462-463 由语义 logits argmax 导出逐高斯语义类。`KelvinPointQueryCADecoder`（decoders.py:530）继承 DPT 解码器做网格 token 查询点解码，对应 pq-front profile。

## 外部连接

- 上游：DAv3 预训练权重经 `blocks/dav3.py` 键名桥加载——(regex, replacement) 元组表驱动（dav3.py:140-144），未匹配键显式报告，训练时由 TrainingSystem 的 `init_weights_paths.dav3` 触发（docs/TRAINING.md:152）。
- 下游：编码器输出 `KelvinMultiscaleFeaturesLatent` 被 kelvin.py:44 的总装、静态核心 static_core.py:65 与推理模型 inference.py:58 消费；backbone/base.py 用 `@dataclass(kw_only=True, slots=True)`+ABC 抽象属性定义 latent 契约。
- 图谱 hubs：decoders.py fanOut=23、encoders.py fanOut=13，是模型层两大扇出点。

## 数据流

多相机 RGB + 相机参数 →（encoder：归一化→FOV 推导→ViT 交替注意力→中间特征抽取）→ 多尺度 latent →（decoder：DPT 重排/融合→逐像素头）→ 每上下文像素一组高斯参数（位置/旋转/scale/density/RGB/语义 logits/运动）→ `GaussianParams` → 下游组装成 KelvinInstantNuRecPrimitive（primitives/kelvin_primitive.py:415）。

## 设计决策

1. **复用 DAv3 而非自训 ViT**：深度先验直接继承，代价是要维护键名迁移表（dav3.py:140）。
2. **每像素一高斯**：dense 解码（decoders.py:89）而非稀疏查询为主路径——point-query 是变体且公开路径拒训（TRAINING.md:15）。
3. **检查点粒度可选**：全局块重算贵，"local"档是计算/显存折中（aa_vit.py:52-64）。
4. **FOV 用 pinhole 近似**： admits TODO（encoders.py:131），真实 F-Theta 精确 FOV 留待上游 ray_gen.py（660 行）处理。

## 新人提示

先读 attention.py 文件头的组合层级注释再读代码；改解码器输出通道时同步核 activations.py:87 的 `GaussianParams` 字段与 export_ply.py:47-52 的预激活约定；跑 pq-front 前记住它无公开训练路径（TRAINING.md:15-16）；ViT 显存爆先试 `checkpointing="local"`。
