# 08 · ViT-Swin 视觉族

## 角色定位

FT 视觉分支=2架构×2精度四目录：`models/vit`(+`_int8`) 是 ViT 编码器（全局注意力），`models/swin`(+`_int8`) 是 Swin/SwinV2 层级窗口注意力。`th_op/swin` 侧的 `ISwinTransformerFunc` 纯虚接口（`th_op/swin/SwinOp.h:27`，forward 在 `SwinOp.h:30`）让 fp32/fp16 双实现挂同一 torch op；只存在于 .h class 声明中，图谱须人工补建（C++ scanner 头文件类声明盲区）；INT8 侧有同构接口（`th_op/swin/SwinINT8Op.h:25`）。

## 内部结构

**ViT**：`ViTTransformer<T>` 按 AttentionType 分派 FUSED（仅 half）/UNFUSED attention 与 FfnLayer；seq_len 由 `img²/patch²+cls` 推出（`models/vit/ViT.cc:138`）。INT8 版换 INT8 后缀层栈，buffer 按 int32 分配（`models/vit_int8/ViTINT8.cc:179`）。
**Swin**：四级嵌套 `SwinTransformer → BasicLayer（stage）→ Block → WindowAttention`；depths/num_heads 走 additional_params 传入（`models/swin/Swin.cc:206`），单实例复用全部 stage。INT8 平行类全链 Col32（`models/swin_int8/SwinINT8.cc:201`），注意力换 `layers/attention_layers_int8/WindowAttentionINT8.cu`。

## 外部连接

- kernel：`kernels/vit_kernels`（bias+cls+pos 合一）；`kernels/image_shift_partition_kernels`（LN+shift+partition，INT8 版 `models/swin_int8/SwinBlockINT8.cc:146`）；`kernels/reverse_roll_kernels`（回滚，`layers/attention_layers/WindowAttention.cc:354`）；`kernels/gen_relative_pos_bias`。
- Swin MLP 不走 FfnLayer，Block 内直接两次 cublas Gemm（`models/swin/SwinBlock.cc:222`）。
- th_op：`SwinTransformerClass` 持 `ISwinTransformerFunc*`（`SwinOp.h:261`），按 dtype switch 实例化模板子类（`th_op/swin/SwinOp.cc:56`），forward 虚调用（`SwinOp.cc:134`）。`vit_gemm.cc`/`swin_gemm.cc` 为离线 autotune 生成 cublasLt 配置。

## 数据流

Swin 链：image [B,3,H,W] → patchEmbed 真 conv2d（`models/swin/Swin.cc:127`，kernel=stride=patch、零 pad）+ 可选 patch_norm LN → [B,res,res,C]。stage 循环（末 stage 不 merge）：block 先 LN+shift+partition 融合核，偶块 shift=0（W-MSA）、奇块 shift=window/2（SW-MSA）（`models/swin/SwinBasicLayer.cc:194`）；WindowAttention softmax 叠 rel-pos bias 与 mask，PV 后投影，ReverseRoll 还原；残差+pre-LN→MLP 两 Gemm+GELU→残差。stage 末 patchMerge：LN/重排+Gemm 压 4C→2C（`models/swin/SwinBasicLayer.cc:114`），分辨率减半通道加倍。末尾 norm 后 avg-pool=stridedBatchedGemm 乘全 1 向量（`models/swin/Swin.cc:242`）出 [B,8C]。**勘误**：FT 止于 pooled 特征，linear 分类头在 PyTorch 侧。

## 设计决策

1. **patch embedding 是 conv2d 非 unfold**：cuDNN IMPLICIT_GEMM，出口直接 NHWC（`utils/conv2d.h:80`），输出即[B,res,res,C]免转置；INT8 版仍 fp。
2. **量化范围**：ViT INT8 覆盖 encoder 全部 GEMM：LN 出口产 int8（`models/vit_int8/ViTINT8.cc:329`）、attention/FFN 走 imma、残差融合核带 dequant scale（mode1=Int32Out/mode2=Int8O）。Swin INT8 更激进：窗口注意力、MLP 连 patchMerge 线性层都 int8（`models/swin_int8/SwinBasicLayerINT8.cc:82`），sm≥80 走 COL32_2R_4R4（`SwinINT8Op.h:96`），scale=amax 表随块发。
3. **shift 边界**：cyclic roll 用取模索引完成（`kernels/image_shift_partition_kernels.cu:31`），零拷贝零 pad，wrap 交叉窗靠 attn_mask 抑制；resolution≤window 时窗口放大全图且 shift=0（`models/swin/SwinBlock.cc:123`）。
4. **rel-pos bias 离线生成**：th_op 独立 op：v1 查表、v2 cpb-MLP（`th_op/swin/SwinOp.h:290`），另出pad64/128/256 trt 版，forward 零计算。
5. **接口分发**：一个 CustomClass 按 dtype 构造子类，精度差异封闭在模板内；INT8 另立接口因权重布局不同（每块16/17 vs 14/15，多出scale）。

## 新人提示

- 先读 `SwinBlock.cc` fp 版再对照 INT8 版，同构双布局=最佳 COL32 教材；version_==1/2 分支贯穿全链（pre/post-LN、merge、logit_scale、cpb），先锁定再读。
- `ape_` 被存储但 forward 未用，仓内无绝对位置嵌入。
- `Swin.cc:116` freeBuffer 释放从未分配的 `buf_`，真正分配的 x_patch_embed_ 等反而漏释放（疑似遗留bug）。
- ViT UNFUSED 半精度 pad：fp 版 %8、INT8 版 %32，勿混用。
- 练习：按 `SwinOp.h` 清单手排一遍扁平权重下标。
