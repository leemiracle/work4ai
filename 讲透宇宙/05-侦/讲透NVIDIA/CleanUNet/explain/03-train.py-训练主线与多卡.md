# 03 · train.py —— 训练主线与多卡协同

> 锚均从源码核实（commit 9487a8db）。骨架改编自 NVIDIA/waveglow（train.py:1，BSD-3，对应 incl_licenses/LICENSE_1）。

## 角色定位

train.py 是单进程训练入口：`train()` 函数（train.py:56-197）完成从日志、数据、模型、优化器、断点恢复到训练循环的全部编排；`__main__` 块（train.py:200-234）解析 -c/-r/-g 三参数并注入全局配置。多卡训练时它**不是**用户直接敲的命令——README.md:65 的标准入口是 `python3 distributed.py -c configs/*.json`，由后者按卡数 spawn 多个 train.py。

## 内部结构

train() 内部按执行顺序：
1. TensorBoard SummaryWriter（train.py:64-66，rank 0 才建）。
2. 分布式初始化：num_gpus>1 时 init_distributed（train.py:69-70）。
3. checkpoint 目录准备（train.py:73-78，makedirs + chmod 0o775）。
4. 数据加载 load_CleanNoisyPairDataset（train.py:81-84，batch_size_per_gpu 来自 config）。
5. 模型 CleanUNet(**network_config).cuda() + print_size（train.py:88-89）。
6. 多卡包 apply_gradient_allreduce（train.py:92-93）。
7. Adam 优化器（train.py:96）。
8. 断点恢复：ckpt_iter='max' 走 find_max_epoch（train.py:100-101）→ torch.load(map_location='cpu')（L108）→ 恢复模型/优化器状态与**累计训练秒数**（L111-115）。
9. 调度器 LinearWarmupCosineDecay（train.py:129-137，divider=25、warmup_proportion=0.05）与 MRSTFT 损失（L139-142，stft_lambda>0 才建）。
10. while 训练循环（train.py:144-191）。

## 外部连接

import 五路（train.py:46-53）：distributed 三函数、dataset 加载器、stft_loss 损失、util 两组（rescale/find_max_epoch/print_size + LinearWarmupCosineDecay/loss_fn）、network 主模型。配置来源是 `__main__` 的 global 注入（train.py:214-220）：dist_config/network_config/trainset_config 以 `global` 声明后，train() 函数体在 L70/81/88 直接引用——**这是全仓最大的隐式耦合**：单独 `from train import train` 调用必 NameError（waveglow 风格，train.py:210 注释自认"Globals nicer in this case"）。上游 spawn 者是 distributed.py:167-173；产物 checkpoint 被 denoise.py:85-92 消费、TensorBoard 日志落在 log.directory/tensorboard。

## 数据流

每个训练步（train.py:146-191）：for clean/noisy/fileid 批 → 上 CUDA（L148-149）→ zero_grad（L157）→ loss_fn 计算双域损失（L159，L1 + MRSTFT）→ 多卡 reduce_tensor 归约出 reduced_loss（L160-163）→ backward（L164）→ clip_grad_norm(1e9)（L165，上限巨大等于几乎不裁）→ scheduler.step **先于** optimizer.step（L166-167，与常见顺序相反但对 Adam 无碍）→ 按 iters_per_valid 写 TensorBoard 四指标（L170-179）→ 按 iters_per_ckpt 存 pkl（L182-189，含 iter/model/optimizer/累计秒数四键）。种子三连固定 random/torch/np=0（train.py:40-43）。

## 设计决策

1. **裸 except 兜底**（train.py:118-120）：checkpoint 损坏时静默从头训练——训练鲁棒性优先，但也会掩盖真实的路径配置错误。
2. **训练秒数随 ckpt 持久化**（train.py:115/187）：断点续训后 TensorBoard 时间轴不跳跃，工程细节见功力。
3. **调度器自研而非 torch 官方**：LinearWarmupCosineDecay（util.py:103-149）直接改写 param_groups['lr']，为支持从中断迭代恢复两阶段进度（L122-127）。
4. **单卡守卫**（train.py:229-230）：num_gpus==1 且 rank>0 直接 raise；多卡无 group_name 时警告并降级单卡（L224-227）。
5. **cudnn 开关**（train.py:232-233）：enabled+benchmark 全开，定长 crop（10s×16kHz）正是 benchmark 友好场景。

## 新人提示

读 train() 先看 `__main__`（train.py:200-234）再回头，否则 L70 的 dist_config 会让你以为是漏写的自由变量。改 batch/lr/迭代数去 configs/DNS-large-*.json（L22-26），别改代码默认。想复现论文原设（1M 迭代 batch 16）注意 README.md:67 声明仓库现配置（250K×64）与其评测差异可忽略。梯度裁剪 1e9 形同虚设，真需要稳定训练要自己调小。iters_per_ckpt=10000 意味着每万步一个 ~176MB 文件，长跑前算好磁盘。

（不计空格约 2100 字符，锚 45+）
