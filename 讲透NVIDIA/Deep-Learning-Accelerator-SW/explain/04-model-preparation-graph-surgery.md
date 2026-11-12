# 04 · 模型准备工具链：让 CNN 骨干住进 DLA 的图手术

> 文件：`scripts/prepare_models/common.py` + 五个模型脚本
> 图谱层：L08 | tour 步：T11

## 角色定位

参考模型（MLPerf 的 ResNet-50/RetinaNet/SSD 系列）拿到的原始 ONNX 并不天然 DLA 友好：卷积后面挂着游离的 Scale/Mul/Add、检测头的多分支 Conv 零散、分类头是 GAP+Flatten+MatMul 长链。common.py 是一把"图手术刀"，五个模型脚本按 `scripts/prepare_models/README.md` 的手册各取几刀，最后由 trtexec 编成 DLA loadable。

## 内部结构

七个模块级函数（common.py:22-158）：

- **垂直融合**：`fuse_mul_into_conv`（common.py:22）把逐通道 Mul 的 scale 直接乘进 Conv 权重；`fuse_add_into_conv`（common.py:36）把逐通道 Add 折成 bias；`fuse_into_conv`（common.py:49）是驱动器，按 (node.op, next.op) 模式扫描套用前两者；
- **水平融合**：`fuse_convs_horizontally`（common.py:63）——同名但完全不同的变换：多条**同属性**（stride/kernel 相同）Conv 分支按输出通道拼接权重合成一个大 Conv，输出 tensor 名也随之合并；
- **改写与裁剪**：`extract_subgraph`（common.py:105）按输入输出名裁子图并改 batch 维；`to_resize_with_scales`（common.py:120）把 9-way Upsample 改成带 scales 的 Resize；`simplify_classification_head`（common.py:130）把 GAP/Squeeze/MatMul/Add/SoftMax 链换成 DLA 友好形态。

## 外部连接

五个消费者：resnet50.py（分类头简化特化版 + 融合）、resnet50_noqdq.py（首层 Conv pad 展开 `expand_first_conv_pads`——DLA 首层 pad 受限的规避）、retinanet_resnext50.py、ssd_mobilenetv1.py、ssd_resnet34.py（Upsample→Resize 用户）。依赖只有 onnx/onnx_graphsurgeon/numpy（requirements.txt）。

## 数据流

下载 ONNX → gs.import_onnx → 逐项手术（toposort 保证融合扫描顺序）→ cleanup 清死节点 → 导出。README 手册把后续链路也写全：`trtexec --onnx=... --useDLACore=0 --allowGPUFallback --int8 --layerPrecisions=...`——NMS/Top-K 等 DLA 不支持的尾部节点留给 GPU，正是根 README 精度表里 "Layers always running on GPU: NMS (Last node)" 一列的来源。

## 设计决策

- **水平融合是 DLA 特有的吞吐手段**：GPU 上多分支并行是优势，DLA 上把 4 条 16 输出 Conv 合成 1 条 64 输出 Conv 才能吃满 batch 维算力——这条变换在 GPU 思维里"没必要"；
- **融合要求无 bias 前置条件**（fuse_mul_into_conv 的 assert）：带 bias 的 Conv 再折 Add 会让 bias 语义纠缠，宁可直接拒绝也不静默改错；
- **手术全部在 ONNX 域、部署前一次性完成**：与 op_reconstruction 同一哲学——DLA 编译器入口处图必须已经"干净"。

## 新人提示

resnet50.py 与 common.py 里各有一个 `simplify_classification_head`，前者是按 ResNet-50 具体节点名定位后转调后者的特化壳——读的时候别混。水平融合的 `new_names` 参数会重命名输出 tensor，后续 trtexec 的 layerPrecisions 名单要用新名，漏改会导致 fp16 层指定失效（README 各模型小节有成品命令可对照）。
