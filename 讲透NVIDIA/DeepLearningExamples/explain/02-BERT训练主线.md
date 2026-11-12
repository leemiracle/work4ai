# 02 BERT 训练主线

## 角色定位

`PyTorch/LanguageModeling/BERT/` 的训练主线由三个文件撑起：`run_pretraining.py` 是预训练入口（LDDL 数据流 + LAMB 大 batch），`modeling.py` 是 NVIDIA 自维护的 BERT 模型库（9 个任务头 + 蒸馏扩展），`optimization.py` 名义上是"优化器模块"、实际是微调线（run_glue/run_squad/run_swag）的 BertAdam 供应者。图谱第 2 层"BERT 模型与训练核心"和第 3 层"BERT 性能秘方：LAMB 与混合精度"（tour step-02/03）覆盖的正是这三个文件加 `lamb_amp_opt/` 包。这一组文件是全仓"训练代码"的代表作：它演示了 2019-2021 年 NVIDIA 如何用 apex 扩展 + LAMB 信任比 + 无同步统计把 BERT 预训练推到当时的世界纪录节奏。

## 内部结构

**run_pretraining.py**：L41-43 三个关键 import——`import modeling`、`from schedulers import PolyWarmUpScheduler`、`from lamb_amp_opt.fused_lamb import FusedLAMBAMP`；L52 `import lddl.torch` 引入数据层。L75 `BertPretrainingCriterion` 把 MLM 与 NSP 两个 CrossEntropyLoss（ignore_index=-1）相加，L86 起的 `sequence_output_is_dense` 分支适配 LDDL 稠密标签。L98 `SyncFreeStats` 是性能秘方之一：统计量（optimizer_step/learning_rate/skip_optimizer_step，L587-594 注册）常驻 device、`pin_memory` 主机镜像，训练循环不做 device→host 同步即可落日志。L386 构建 `modeling.BertForPreTraining`，L429 `optimizer = FusedLAMBAMP(...)`，L431 PolyWarmUpScheduler、L436 GradScaler 相继装配，L557 走 `lddl.torch.get_bert_pretrain_data_loader` 流式读 HDF5 分片。

**modeling.py**：L168 BertConfig、L263 BertEmbeddings、L304 BertSelfAttention、L437 BertLayer、L464 BertEncoder、L598 BertPreTrainedModel、L788 BertModel、L890 BertForPreTraining 及其 L887 `make_teacher` 方法（蒸馏教师钩子），其后 961/1022/1083/1158/1227/1301 一字排开 MaskedLM/NSP/序列分类/多选/词元分类/问答六个头，L1373 `Project` 是蒸馏用的维度投影层。L61 `load_tf_weights_in_bert` 保留 TF 权重转换能力。

**optimization.py**：L64 BertAdam（warmup 内建、无 bias correction 的定制 Adam——这是 Google 原版 BERT 的训练口径），L36-51 四个 warmup schedule 函数。最扎眼的是 L27 `import amp_C` 与 L30-33 的模块级绑定：`multi_tensor_l2norm`/`multi_tensor_lamb_stage1_cuda`/`multi_tensor_lamb_stage2_cuda`/`multi_tensor_scale` 四个 apex C 内核被绑到模块属性上。

## 外部连接

三条关键甄别（图谱 languageNotes 钉版 + 源码复核）：

1. **optimization.py 的 amp_C 绑定是"半死"状态**。文件内唯一的类 BertAdam 是纯 Python 实现，不消费这四个绑定；全仓也没有人 `from optimization import multi_tensor_l2norm`。真正用 amp_C l2norm 的是微调脚本自己动手：run_glue.py:117、run_squad.py:712 各自绑定并经 multi_tensor_applier 做梯度范数裁剪。但注意 L27 的 `import amp_C` 是顶层执行——**只要 import optimization 就要求 amp_C 存在**，这是微调线对 NGC 容器的隐性硬依赖。
2. **lamb_amp_opt/fused_lamb 不是"纯 PyTorch 可跑"**。图谱 summary 称其为"不依赖 C 扩展的参考实现"，但源码相反：fused_lamb.py:8 顶层 `import fused_lamb_CUDA`，L30-33 在 multi_tensor_applier 可用时绑 amp_C.multi_tensor_l2norm 与 amp_C.multi_tensor_lamb，不可用则 L37 直接 raise。`fused_lamb_CUDA` 由 lamb_amp_opt/setup.py:15 的 `csrc/multi_tensor_l2norm_kernel.cu` 编译。"参考实现"的准确含义是"随仓可供阅读源码的 LAMB 实现"（lamb_amp_opt/main.py 是它的 20 epoch AMP 冒烟测试），跑起来仍要 CUDA 扩展。
3. **BART 侧的对照组**：`PyTorch/LanguageModeling/BART/bart/lamb.py`（cybertronai MIT 授权，Lamb/JITLamb 双实现共享 lamb_kernel）全仓零 import——真正接线的是 `apex.optimizers.FusedMixedPrecisionLamb`（BART/training_base.py:37 导入、:149 构造）。同一仓里 LAMB 有三种存在形态：amp_C 内核路径（BERT 预训练）、随仓源码包（BERT lamb_amp_opt）、纯参考孤儿（BART lamb.py）——读优化器代码时必须先甄别"哪条是真接线"。

另：`PyTorch/LanguageModeling/BART/bart/modeling/bert_attn.py` 是 BertSelfAttention 的孤儿片段——L18-25 现代 nn.MultiheadAttention 式签名的空 `__init__` 与 L26 起旧式实现连续定义两个 `__init__`（后者覆盖前者生效），且引用 nn/torch/math/F 而全无 import 语句，全仓零引用不可独立运行。它是"参考片段"堆放进仓的化石，不是可复用组件。

## 数据流

预训练：LDDL 产出的 HDF5 分片 → `run_pretraining.py:557` 的 dataloader（内建预取）→ BertForPreTraining 前向 → BertPretrainingCriterion（L75）→ grad_scaler（L440 `torch.cuda.amp.GradScaler`）→ FusedLAMBAMP step → PolyWarmUpScheduler 调度（L431）→ SyncFreeStats 设备端记账 → checkpoint_step 存档。两阶段课程（phase1 短序列 7038 步 + phase2 长序列 1563 步、全局批 8192/4096）由 scripts/configs/pretrain_config.sh 的 4 个入口函数提供超参——该文件 tree-sitter 对含连字符函数名零提取，函数清单系手工补齐。

微调：run_glue.py:40/run_squad.py:42/run_swag.py:35 `from optimization import BertAdam, warmup_linear`，squad 在 L986 构造 BertAdam——与预训练线的优化器完全分家。

## 设计决策

1. **优化器按 batch 规模分层**：微调（小 batch）用 BertAdam 纯 Python 足矣；预训练（8192 全局批）必须 LAMB——信任比 η·||w||/||g|| 让每层学习率自适应权重范数，大 batch 下无需逐层调 warmup。
2. **`_step_supports_amp_scaling = True`**（fused_lamb.py:40）：优化器自己消费 GradScaler 的 found_inf/scale，把动态 loss scaling 的除法与 unscale 融进 step 内核，配合 `lr`/`step` 常驻 GPU（L23-24 的 `torch.tensor(lr, device=...)`）实现整步无 host 同步。
3. **SyncFreeStats 的取舍**：日志精度让位于吞吐——统计量在 device 累积、只在 checkpoint 时拷回。
4. **单文件 modeling.py 兼收并蓄**：训练头、蒸馏扩展（make_teacher/Project）、TF 权重转换同处一文件，是"示例仓优先可读性"的典型；代价是 1400+ 行的它同时被预训练/微调/蒸馏/Triton 四条线 import，牵一发动全身。

## 新人提示

- 想跑通 run_pretraining 必须先装 lddl（数据）、apex+amp_C（优化器内核）、编译 lamb_amp_opt（setup.py），三者都在 NGC 容器里预置——离开容器逐个踩坑是常态。
- optimization.py 的 L30-33 绑定不等于"被使用"：判断接线要看构造点（谁 new 了优化器），不要看谁 import 了模块。
- `sequence_output_is_dense` 分支（run_pretraining.py:86）对应 LDDL 的标签存储格式，读旧教程时容易和稀疏 -1 掩码口径混淆。
- 读 distillation/ 时注意 make_teacher 在 BertForPreTraining 上（modeling.py:887），而 run_squad 的答案后处理链被 Triton 线复用（见第 04 篇）——训练主线不是孤岛。
