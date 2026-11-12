# 01 · 桥扩散数学：diffusion.py 与 MultiDiffusion 滑窗融合

## 角色定位

diffusion.py 是全仓数学内核，169 行实现 Schrödinger Bridge 的完整采样理论：beta 调度、前向桥采样、反向后验、长序列 MultiDiffusion 融合。训练侧只有 `Diffusion.q_sample` 被用到；推理侧 `get_multidiffusion_vf` 与 `p_posterior` 承担全部采样。文件头（diffusion.py:9-15）声明血统：改编自 NVlabs/I2SB 的 diffusion.py——图像桥扩散到音频桥扩散，数学原样搬运，只换了数据域。

## 内部结构

四个层次自底向上：

**高斯乘积原语**（diffusion.py:90-98）。`compute_gaussian_product_coef(sigma1, sigma2)` 返回两高斯乘积分布的合并系数：coef₁=σ₂²/(σ₁²+σ₂²)、coef₂=σ₁²/(σ₁²+σ₂²)、var=σ₁²σ₂²/(σ₁²+σ₂²)。桥扩散的一切"合并两个信息源"的操作——前向把 x₀/x₁ 揉成 x_t、反向把 pred_x0/x_t 揉成 x_{t_prev}——都是这一个函数。对比 DDPM：DDPM 的 q(x_t|x₀) 是单源加噪，桥是双源加权，权重由两侧方差竞争决定。

**对称二次 beta 调度**（diffusion.py:107-123）。β(t) 在 t≤0.5 取 t²·β_max、t>0.5 取 (1−t)²·β_max（diffusion.py:109-112），峰值居中、两端归零。妙处是积分闭式：∫₀ᵗβ = β_max·t³/3（t≤0.5）与 full_integral−β_max(1−t)³/3（t>0.5），full_integral=2β_max(0.5)³/3（diffusion.py:118-122）。于是 `get_std_fwd(t)=√∫₀ᵗβ`（diffusion.py:125-126）、`get_std_rev(t)=√∫ₜ¹β`（:128-129）都是解析量——无需 DDPM 式的预计算 betas 数组，任意连续 t 直接求值，这也是后面 T-finetuning 能任意切 t 区间的前提。注意构造默认 beta_max=0.3（diffusion.py:101）与配置实测 1.0（configs/pretrain.yaml:78）不一致，读码以配置为准。

**桥采样核 Diffusion 类**（diffusion.py:100-168）。`q_sample`（:137-151，docstring 自注"eq 11"）实现论文前向：x_t = coef₁x₀ + coef₂x₁ + √var·ε。语义上 t=0 纯净数据、t=1 损坏后验（diffusion.py:103 注释），中间是两端的随机插值——训练时只需一次前向就得任意 t 的样本，没有马尔可夫链。`ot_ode=True` 分支去掉噪声项（:149-150）退化为概率流 ODE 确定性路径。反向 `p_posterior`（:153-163）：x_{t_prev} = mu_x0·x₀ + mu_xt·x_t（+噪声，若 SDE 且 t_prev>0），系数来自 (std_{t_prev}, std_delta) 的高斯乘积（:157-158），std_delta=√(std_t²−std_{t_prev}²) 保证方差账目平衡。`get_pred_x0`（:165-168）由网络输出反推：pred_x0 = x_t − σ_fwd(t)·net_out。

**MultiDiffusion 滑窗**（diffusion.py:27-87）。三个函数一组：`get_multidiffusion_vf`（:27-64）是核心——用 `torch.nn.Unfold`（:37-38）把 B×C×H×W 谱图按 win_length 窗口、hop_length 步长切成 (b·l) 个窗口批，分块过 vf_model（:44-51），再用 counts 张量对重叠区域**累加后按覆盖次数平均**（:33, :57, :64）。注意 docstring 限定（:29-31）：所有窗口必须同一时间步 t——不支持异构采样调度。`multidiffusion_pad_inputs`（:67-83）把宽度补齐到 `ceil((W−win)/hop)·hop+win`，填充取输入自身尾段复制（padding_constant 可选覆盖，fast_inpaint 用 0）；`multidiffusion_unpad_outputs`（:86-87）裁回原宽。这里融合的是**速度场而非最终输出**——每个反向步都先融合出全局一致的 vf，再走 p_posterior，保证窗口边界的过渡平滑。

## 外部连接

上游消费者两个：`STFTBridgeModel.training_step` 用 q_sample 造训练样本、目标 = (x_t−x₀)/σ_fwd(t)（A2SB_lightning_module.py:381-386）；`TimePartitionedPretrainedSTFTBridgeModel.ddpm_sample` 在每个反向步调 get_multidiffusion_vf 并做两次掩码混合（A2SB_lightning_module.py:129-144）。compute_gaussian_product_coef 还被 STFTBridgeModel 的两个 i2sb 对照采样变体直接引用（A2SB_lightning_module.py:305, :341）。

## 数据流（一次 50 步反向采样）

predict_step 构造 t_steps=linspace(1,0.05,50)（A2SB_lightning_module.py:192）→ pad 输入与掩码 → 循环 50 次：{t_emb=SinusoidalTemporalEmbedding(t) → 路由时间分区专家 get_vf_model(t)（:128）→ get_multidiffusion_vf 融合窗口速度场 → get_pred_x0 反推干净谱 → 掩区替换 pred_x0、已知区回填加噪 x_t（:133-144）→ p_posterior 步进} → unpad 取最后一步 pred_x0 去 vocode。

## 设计决策与批判

**(1) 为什么桥而不是 DDPM**：音频恢复的起点是"具体损坏输入"而非白噪声，桥直接建模 x₁→x₀ 转移，推理末期（t→1）始终锚定损坏后验，避免了生成先验与恢复任务的错位。**(2) 均值融合是 MultiDiffusion 的弱形式**：窗口重叠区取算术平均（counts 归一化），相比论文里高斯乘积式的方差加权融合（get_multidiffusion_vf 并未用 compute_gaussian_product_coef）更简单也更保守——各窗口被等权对待，不按置信度加权。**(3) β 调度形状**：t=0.5 处 β 峰值意味着中间时刻最"吵"，两端确定性增强——与 q_sample 在 t=0/1 退化为纯 x₀/x₁ 的边界条件自洽。**(4) 解析积分的代价**：换 beta 形状（如余弦调度）要重推闭式，灵活性低于数值积分方案——这是"少一张预计算表"换来的耦合。

## 新人提示

读这个文件按 90→100→27 的顺序（原语→类→滑窗）比按行号顺序快。训练目标里的 σ_fwd(t) 归一化（A2SB_lightning_module.py:386）容易漏看——它决定网络输出量纲，改动 beta 调度时这一项必须联动。MultiDiffusion 的 win/hop 两参数在推理配置里是 predict_win_length=256/predict_hop_length=128（A2SB_lightning_module.py:43-44 默认值），hop<win 才触发融合；hop=win 时退化为不重叠分块。t 终点取 0.05 而非 0（:192），因为 β(t→0)→0、步进无意义还放大数值噪声。
