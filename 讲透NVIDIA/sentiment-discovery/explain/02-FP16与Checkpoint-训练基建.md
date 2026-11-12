# 精讲二：FP16_Optimizer 与梯度检查点——2018 年的训练基建

## 角色定位

fp16/ 与 model/checkpoint.py 是"让 4096 维 mLSTM 在 DGX-1V 上四小时吃完 40GB 语料"的工程底座。FP16_Optimizer（fp16/fp16.py:58）是 NVIDIA apex 开源前的家版本——README:218 致谢直言这些工具"最新版本在 APEx github"；仓内自足，pretrain.py:14 直接 `from fp16 import FP16_Module, FP16_Optimizer`，并不依赖外部 apex（对比：main.py:17 与 generate.py:16 才 import apex）。FP16_Module（fp16.py:44）把模型 half() 并在输入输出做 fp16↔fp32 转换（:50）。

## 内部结构

数过 FP16_Optimizer 恰好 23 个方法（含 9 个私有/property 存取器，:151-559）。构造函数拆参数（:166-186）：逐 param_group 把 fp16 参数分出来，为每个克隆 fp32 主副本 `detach().clone().float()`（:181-182），再把优化器的 param_groups 整组替换成 fp32 引用（:186）——优化器全程只见 fp32。loss scale 双策略在 :194-202：静态 LossScaler（fp16/loss_scaler.py 头部，has_overflow 恒 False）或动态 DynamicLossScaler（初始 2^32、scale_window=1000 步连稳翻倍，loss_scaler.py:37-39）。梯度搬运在 fp16/fp16util.py：model_grads_to_master_grads（:93）与 master_params_to_model_params（:115）。

## 外部连接

调用侧在 pretrain.py 训练循环：`optim.backward(loss, update_master_grads=False)`（pretrain.py:202-205）替代 loss.backward()——backward 内部先 `loss_scaler.backward(loss.float())` 放大再反传（fp16.py:491-493）；梯度裁剪走 clip_master_grads（fp16.py:258，对 fp32 主梯度做 clip_grad_norm，溢出时返回 -1）；update_master_grads（:495-506）动态模式下先查 inf/nan（_check_overflow :228），随后拷贝并除回 scale（_downscale_master :251）；step（:345）溢出则打印 "OVERFLOW! Skipping step"（:390-393）跳过本步并降 scale 重来——pretrain.py:233-238 据此同步跳过 LR 步进。多卡梯度归约由 model/distributed.py 的 DDP 扁平化 all_reduce（:39-44）。

## 数据流

一轮迭代：fp16 前向 → fp32 CrossEntropyLoss（pretrain.py:108 reduce=False 逐元素）→ loss×scale 反传 → fp16 .grad 拷贝到 fp32 主参数 → 除以 scale → 裁剪 → 优化器 step 更新主权重 → 主权重拷回 fp16 模型（step 尾 :400）。状态保存 state_dict（:282）连 fp32 主副本一起存（'fp32_from_fp16' :300），load_state_dict（:303）优先整组 copy_ 回灌（:341-343）避免精度损失。

## 设计决策

其一，"fp16 存储 + fp32 数学/主权重"模式的所有权边界清晰：用户只许碰主梯度（inspect_master_grad_data——讽刺的是它 raise NotImplementedError，fp16.py:524，其下 8 行是死代码）。其二，loss scale 与学习率解耦（docstring :117-121 明言"downscaled before applied"）。其三，model/checkpoint.py 的 CheckpointFunction（:36）是从 pytorch torch/utils/checkpoint 改造的自动检查点（license 头 :6-9），加了 CUDA RNG 状态保存/恢复（forward 存 :42、backward 换回重算 :55-59）保证 dropout 可复现——但全仓零 import，是孤儿模块；transformer.py:19 实际用 torch.utils.checkpoint 做 sqrt 分块（:300-306）。

## 新人提示

读 fp16.py 按"构造→backward→step"三角走，docstring 是全仓最好的混合精度教材（含 closure 限制 :383-385：闭包模式与动态 scale 不兼容）。两个易错：FP16_Optimizer 装的是"替换后的 param_groups"，直接拿原 optimizer 用会静默更新错副本（构造注释 :91-99 警告过）；动态 scale 下 .grad 不可信，调试请看主梯度。--chkpt-grad 只在 Transformer 臂生效，RNNModel.forward 收了参数不用（model/model.py:37-44），别指望它省 mLSTM 的显存。
