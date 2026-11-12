# 05 vendored MDM：扩散数学引擎与两处深度定制

## 角色定位

`audio2face/deps/motion_diffusion_model/` 是 vendored 的扩散数学库，血统三层：文件头自述 based on OpenAI guided-diffusion → Guy Tevet 的 motion-diffusion-model（2022）→ NVIDIA 2025 改造（`gaussian_diffusion.py:17-23` 版权链）。与 charsiu 整树搬运不同，本仓**只移植了 diffusion/ 子目录 + utils/misc.py**，MDM 上游的训练脚本、数据管线、Transformer 主干全部没搬——它在这里只当"扩散引擎"用，网络主干（diffusion_rnn）是本仓自研的。

## 内部结构

核心 `gaussian_diffusion.py`（1697 行）：三枚举决定模型预测目标与损失形态——`ModelMeanType`（L91，PREVIOUS_X/START_X/EPSILON）、`ModelVarType`（L101，含 LEARNED_RANGE 插值方差）、`LossType`（L115，MSE/KL 及 rescaled 变体）；`q_sample`（L240）闭式前向加噪 x_t=√ᾱ_t·x_0+√(1-ᾱ_t)·ε；`p_mean_variance`（L281）单步去噪统计量，`_predict_xstart_from_eps`（L402）做 ε→x_0 换算；`p_sample_loop`（L591）反向采样主循环。配套件：`respace.py:31` 的 `space_timesteps` 时间步压缩、`resample.py:30` 的时间步采样器工厂、`nn.py:109` 的 `mean_flat`、`losses.py:34/63` 的 KL 与离散高斯对数似然（VB 损失用）。

## 外部连接

全仓仅三个消费点：`train_diffusion.py:37-38` 与 `infer_diffusion.py:25` 各 import `create_gaussian_diffusion`（工厂在 `script_utils.py:27`），训练侧多 import 一个 `create_named_schedule_sampler`。`utils/misc.py` 唯一活代码是 `wrapped_getattr`（L41）——被 `respace.py:28` 的 `_WrappedModel` 用做属性透传；**fp16_util.py（244 行）与 logger.py（502 行）互相引用但全仓零外部消费，是死代码对**；plms 采样族、`resample.py:92` 的 LossAwareSampler、`gaussian_diffusion.py:1424/1496/1551` 三个 MDM 运动学损失同样零调用。

## 数据流

训练：`train_diffusion.py:458-466` 造扩散对象（`DIFFUSION_STEPS=1000`、cosine schedule、`predict_xstart=True`→START_X 直预测 x_0，`config_train_diffusion_base.py:146-148`），uniform 采样器抽时间步（L467），`train_step` 调 `training_losses` 并传 `tongue_weight/jaw_weight`（`train_diffusion.py:350-357`）。推理：`infer_diffusion.py:126-135` 换用 `cfg_inference.TIMESTEP_RESPACING`（样例配置 `configs/example-diffusion/config_inference.py:20` 为 "2"——`space_timesteps(1000,"2")` 得 {0,999} 两步，`SpacedDiffusion` 再由 ᾱ 重算两步 beta 表 L100-105），`USE_DDIM=False` 走 `p_sample_loop`（`config_inference_diffusion_base.py:51,53`）。

## 设计决策

- **定制一：分段加权损失**（`gaussian_diffusion.py:1405-1415`）——按 skin_dim/tongue_dim/jaw_dim 通道布局构造权重张量，舌头 0.1、下颌 1.0（`config_train_diffusion_base.py:197-198`），补偿低维通道在 MSE 里的劣势。
- **定制二：流式状态穿透**（L660-708）——`p_sample_loop` 尾部按 `model.inference_mode` 分叉：streaming_stateless 返回 (sample, h_gru_all) 把 GRU 隐状态带出扩散循环供下窗接力；output_delta 模式采样后按 actor_vec 逐区（皮肤/舌/颌/眼）反归一化。上游 MDM 完全没有这些概念。
- **L1267-1279、L1332-1403 大段被注释的 MDM 运动学损失代码原地保留**——"注释式剪枝"，改删为注，方便对照上游。
- 训练 1000 步、推理 2 步：靠 respacing 的重参数化 beta 表而非 DDIM（DDIM 是备选项）。

## 新人提示

读这份代码先看三枚举再进循环体；改采样步数只动修饰器里 `TIMESTEP_RESPACING`（训练侧空串=满 1000 步）；ONNX 导出的 `num_diffusion_steps=2` 来自 `NUM_DIFFUSION_STEPS`（`train_diffusion.py:111`），与 respacing 字符串是两个独立来源，改其一不改其二会出现 PT 与 ONNX 行为不一致。
