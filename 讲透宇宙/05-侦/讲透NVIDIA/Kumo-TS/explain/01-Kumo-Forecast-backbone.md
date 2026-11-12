# 01 · Kumo-Forecast/backbone.py — 单文件预训练骨干与合成包注册

## 角色定位

backbone.py 是预测线的模型底座：895 行单文件组装出 T5 编码器时序骨干，覆盖重构/预测/分类/嵌入四任务（backbone.py:50）。README 称之为 vendored backbone——它源自 MOMENT 式"预训练 transformer 学通用时序表征"路线，SDK 与微调示例都从这一个文件取模型。文件头明示双导入形态 `from backbone import BackbonePipeline`（backbone.py:13）。

## 内部结构

自上而下五段：工具段（control_randomness 随机种子控制 backbone.py:94、EarlyStopping 等）→ 组件段（Masking 掩码生成 backbone.py:151、RevIN 实例归一化 backbone.py:208、Patching/PatchEmbedding 词元化 backbone.py:319）→ 模型段 BackboneModel（backbone.py:445）：__init__ 按 config 串联 normalizer→tokenizer→patch_embedding→encoder→head（backbone.py:471），可选挂 CrossChannelAttention（backbone.py:344，逐 patch 位置让 C 个通道互注意，残差+LayerNorm 稳训练）；_get_transformer_backbone 用 T5EncoderModel 取编码器并默认开梯度检查点（backbone.py:551）→ 管线段 BackbonePipeline（backbone.py:718）混入 PyTorchModelHubMixin；forward 按任务名分发到 reconstruction/forecast/classify/embed 四法（backbone.py:700）。尾部还有 MAE/MSE/MAPE/sMAPE/RMSE 指标工具集（backbone.py:814）。

## 外部连接

上游消费者：model.py 的 build_model 经 BackbonePipeline.from_pretrained 按名装配（model.py:37）；sdk/forecasting.py 加载权重做推理；examples/finetune_example.py 微调后回存。下游依赖 transformers 的 T5 系与 huggingface_hub。最特殊的"连接"是 _register_submodules()（backbone.py:829）：用 sys.modules.update（backbone.py:877）把 backbone.utils.utils、backbone.models.layers.embed 等十余个合成模块路径注册进解释器，import 时即执行（backbone.py:895），仓内 `from backbone.utils.utils import control_randomness` 因此解析到本单文件而非任何真实目录。

## 数据流

以 forecast（backbone.py:642）为例：输入 x_enc [B,C,L] 与 input_mask → RevIN 按 mask 统计均值方差归一（backbone.py:580）→ nan_to_num 清洗 → Patching unfold 切 patch → PatchEmbedding 线性投影 d_model 并用 mask_embedding 占位被掩 patch → reshape 成 (B*C, n_patches, d_model) 进 T5 编码器（通道独立）→ 还原 [B,C,P,D] 后过跨通道注意力（backbone.py:597）→ ForecastingHead 展平映射到 horizon → RevIN denorm 还原尺度。embed 路径则对通道维做 mask 加权 mean 池化输出表征（backbone.py:599）。

## 设计决策

一是单文件+合成包注册：牺牲常规包布局换取"拷一个文件即可用"，代价是 IDE 无法跳转、模块边界只存在于命名约定。二是权重向后兼容作为硬约束：use_cross_channel=False 时架构与旧权重严格一致可 strict=True 加载；True 时仅新增 cross_channel_attn.* 键（backbone.py:488），旧检查点 strict=False 也能载入，注释明说这一命名策略（backbone.py:339）。三是通道独立骨干+可选跨通道层的折中：预训练权重保持 channel-independent，跨通道交互作为可摘拔增强层后置。四是 BackbonePipeline.init() 在加载后按 new_task_name 换头（backbone.py:739），同一份预训练权重可切换四种任务头。

## 新人提示

读该文件先看文件头 docstring（backbone.py:4）与 _register_submodules 的模块表（backbone.py:829），再进 BackboneModel。注意 d_model 默认取自 t5_config（backbone.py:512），且 SUPPORTED_HUGGINGFACE_MODELS 只列 google/flan-t5-*（backbone.py:436），与 SDK 默认的 AutonLab/MOMENT-1-large 并不一致（MOMENT 血统残留）。改层结构前先确认权重兼容：任何改动若新增/改名参数键，旧权重加载即失败。排查 import 错误时记住 backbone.utils.* 全是内存合成模块，磁盘上搜不到。
