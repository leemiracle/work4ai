# 07 · 特征提取器精讲（src/anomalib/models/components/feature_extractors/）

## ① 角色定位

特征提取器是 anomalib 大半模型族的地基：PatchCore/PaDiM/STFPM/Dinomaly 等 **19 个** image 模型（grep 实测）都靠它取预训练 backbone 的中间层特征。目录仅三文件：`timm.py`（364 行，唯一的类 `TimmFeatureExtractor`）、`utils.py`（84 行，干跑探尺寸）、`__init__.py`（35 行；`models/components/__init__.py:41` 再重导出）。核心价值：把 timm 两套 API（CNN 的 `features_only`、ViT 的 `forward_intermediates`）及 torchvision FX 统一成"图像张量进、{层名: 特征图} 出"的稳定接口，上层不关心 backbone 种类。

## ② 内部结构

**timm.py**

- `_disable_pos_embed_antialiasing`（44-66 行）：monkeypatch timm ViT 的 `resample_abs_pos_embed` 强制 `antialias=False`——该算子 ONNX 导出不支持（46-49 注释）；`_anomalib_no_antialias` 标记保证幂等（57、65）。
- `TimmFeatureExtractor.__init__`（161-236 行）是**四分支分派器**：
  1. `output_fmt` 校验只许 NCHW/NLC（174-176）。
  2. nn.Module 分支（190-198）：任意 torch 模型走 torchvision `create_feature_extractor`（按 return_nodes 截取，193-196）；再固定 256×256 干跑探出 `out_dims`（197-198）。
  3. transformer 分支（200-214）：触发条件 `_uses_intermediates = isinstance(backbone,str) and (output_fmt=="NLC" or "vit" in backbone.lower())`（188 行）——名字含 "vit" 即走此路；层名转 block 序号（202）；`timm.create_model(dynamic_img_size=True)` 建全模型（203-208）并打补丁（209）；记录 patch_size 与 prefix/register token 数（210-212）及 `out_dims=[embed_dim]*len(layers)`（214）。
  4. 普通 CNN 字符串分支（216-230）：layers 全 int 直接当 out_indices（217-218），否则 `_map_layer_to_idx`（220）；`create_model(features_only=True, exportable=True, out_indices=...)`（221-228），out_dims/reductions 取自 feature_info（229-230）。
  5. 其余类型 TypeError（232-234）。
- `_block_name_to_idx`（238-255）：`"blocks.2"`→2，int 直通，非法名 ValueError。
- `_map_layer_to_idx`（257-286）：临时建 features_only 模型读 feature_info 的 module 名单（268-276）；**找不到的层只 warning 并从 `self.layers` 移除，不抛错**（280-284）。
- `forward`（288-324）：intermediates 路径转 `_forward_nlc`（313-314）；默认 `requires_grad=False` 时先 `eval()` 再 no_grad（316-321）；timm 返回 list 时 zip 回字典（322-323）。
- `_forward_nlc`（326-353）：`return_class_token=True` 时把 prefix（CLS+register）与 patch tokens 沿序列维 concat（347-350）。
- `_run_intermediates`（355-364）：统一调 `forward_intermediates(indices, norm, return_prefix_tokens, output_fmt, intermediates_only=True)`。

**utils.py**

- `dryrun_find_featuremap_dims`（36-84 行）：`torch.empty(1,3,*input_size)` 干跑（71-75），临时 eval+no_grad 且事后恢复 training（72-77）；返回 `{层名: {num_features: 通道数, resolution: (H,W)}}`（78-84），PaDiM 尺寸推断与 nn.Module 分支都靠它。

## ③ 外部连接

- **消费者（grep 实证 19 文件）**：padim（`padim/torch_model.py:121`）、patchcore（122）、stfpm teacher+student 双实例（94-95）、reverse_distillation（108）、dinomaly（138）及 cflow/dfm/dfkde/glass/csflow/anomaly_dino 等；uflow 继承出 `LayerNormFeatureExtractor`（`uflow/feature_extraction.py:81`）。
- **图谱边**：入边 uflow 的继承边、`f:foundad/components/encoder_loader.py`、`tests/unit/models/test_feature_extractor.py` 与 `tests/unit/deploy/test_onnx_export.py`（anti-alias 补丁正为导出测试服务）；出边 `f:feature_extractors/utils.py`（timm.py:39）。
- **上下游协议**：上游消费 timm/torchvision FX；下游契约是 `dict[str|int, Tensor]`（288 行）；`out_dims/reductions` 供模型构造期做形状校验（如 PaDiM 的 `n_features_original` 求和，`padim/torch_model.py:126`）。

## ④ 数据流

CNN 路径（常见配置）：`(N,3,256,256)` → features_only 骨干（默认先 eval 再 no_grad，316-321）→ list of tensors → `zip(layers, features)` 成字典（322-323）→ 上层按层名取图、对齐、拼接。ViT 路径（DINOv2，layers 形如 blocks.2/blocks.6）：构造期层名换 int idx（202）；前向走 `forward_intermediates`，`norm=True` 时每个中间块过 backbone 最终 norm（`timm.py:106` docstring）；`output_fmt="NLC"` 吐 `(B,N,D)` token 序列、`"NCHW"` reshape 回空间图（334-337），`return_class_token=True` 前置 CLS/register（348-350）。out_dims 三源：nn.Module 干跑（197）、CNN feature_info 免跑（229）、ViT 全层 embed_dim（214）。

## ⑤ 设计决策

1. **一个类吃三种 backbone**：str-CNN / str-ViT / nn.Module 分派（188、190、200、216），timm 两代 API 差异吸收在类内，上层签名不变——anomalib"一行配置换骨干"的根。
2. **ViT 靠名字嗅探**：`"vit" in backbone.lower()` 即走 forward_intermediates（188），因 features_only 处理不了动态尺寸 ViT（186-187 注释）；副作用是名字碰巧含 "vit" 的非 ViT 模型被误路由。
3. **no_grad/eval 内建**：记忆库模型只要特征不要梯度，故默认 requires_grad=False 且 forward 自行 eval+no_grad（316-321）；STFPM 这类要梯度的传 True 走裸前向（317）。
4. **静默降级的层名映射**：不存在的层 warning+移除（280-284），换骨干宽松兼容；代价是拼错层名不报错、模型悄悄少一层——调异常性能先查这条 warning。
5. **导出友好**：anti-alias 补丁（44-66）+ `exportable=True`（226）为 ONNX/OpenVINO 铺路，是 deploy 体系的隐含前提。
6. **默认 `norm=True`/`dynamic_img_size=True`**（169-170）：对齐 AnomalyDINO 近邻搜索尺度（105-106）、允许非默认 img_size。

## ⑥ 新人提示（含勘误）

1. **勘误（任务描述路径过时）**：任务书写的 `components/feature/` 不存在，实际是 `components/feature_extractors/`；图谱节点与磁盘一致。
2. **勘误（`__init__.py` 文档残留）**：`feature_extractors/__init__.py:10-14` docstring 宣称提供 `BackboneParams`，但 29-35 行实际导出只有 `TimmFeatureExtractor` 与 `dryrun_find_featuremap_dims`——docstring 是残留。
3. **图谱少记了消费者**：入边只显式记 uflow/foundad/测试三类，但 grep 实证 19 个模型实例化——多数经 `anomalib.models.components` 重导出 import（`padim/torch_model.py:44`），图谱把这类边归到包节点。
4. **layer 名是 timm 世界的名字**：CNN 用 feature_info 的 module 名（resnet 为 layer1/2/3），ViT 用 `blocks.<int>`；写错不报错只降级（⑤-4）。
5. **out_dims 三种来源分清**：nn.Module=干跑、CNN=feature_info、ViT=全层 embed_dim（197-198/229/214）；ViT 的 out_dims 与层数重复且不含空间信息，做形状断言时注意。
6. **别外层再包 no_grad**：forward 已自带（319-321）；真正要防的是忘了 `requires_grad=True` 的语义差（STFPM 教师也要梯度）。

---

### 自检报告

- 字数：总字符（含空格）5209 / 去空格字符 4789（达标区间 2500-4800）
- 行号锚：60 处（file.py:行号与段内行号引用，去重计），全部打开源文件核实
- 实测验证：19 个消费者由 `grep -rl "TimmFeatureExtractor(" src/anomalib/models/image/ | wc -l` 实测；uflow 继承（feature_extraction.py:81）已核对
