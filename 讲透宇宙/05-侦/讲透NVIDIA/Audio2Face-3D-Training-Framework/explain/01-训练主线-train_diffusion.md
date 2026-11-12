# 01 训练主线：train_diffusion.Trainer 与 gaussian_diffusion 的分工

## 角色定位

`audio2face/train_diffusion.py`（562 行）是扩散线的训练总控：`Trainer` 类（L43）从配置装载、数据集组装、网络构建到逐 epoch 优化与产物导出一手包办。数学本体不在本文件——前向加噪、去噪采样、扩散损失全部委托给 vendored 的 `audio2face/deps/motion_diffusion_model/diffusion/gaussian_diffusion.py`。两者关系是"编排器 vs 数学引擎"：Trainer 决定喂什么数据、配什么超参、损失怎么组合；GaussianDiffusion 决定噪声怎么加、模型预测目标是什么、损失怎么算。

## 内部结构

`setup()`（L410）是一条单向装配流水线：生成带时间戳的 run 名（`gen_run_name_full` L54）→ 校验三份配置修饰器（L421-423，未知键直接 ValueError）→ `module_to_easy_dict` 合成最终配置（L424-426）→ 装配 Provider 与 `AnimationSegmentDataset`（L432-440）→ `compose_network_info` 组装网络参数（L447-450）→ `create_network`（L454）→ 可选加载预训练权重（L462-466）→ **`create_gaussian_diffusion` 构造扩散引擎**（L457-464 之后于 L468-475）→ uniform schedule sampler（L478）→ Adam + 余弦退火（L480-491）。

关键点有三处。其一，`create_gaussian_diffusion` 固定 `predict_xstart=True`——直接预测 x0（干净动画）而非噪声 ε，这是面部动画任务对稳定性的取舍。其二，`train_step`（L334）里 `schedule_sampler.sample(1, ...)` 每步只采 1 个时间步，扩散损失 `self.diffusion.training_losses(...)`（L355-364）的返回被拆成 `diffusion_loss` 与 `model_output` 两个出口——后者是模型在采样时间步的预测输出，专供 `compute_additional_losses`（L282）在**顶点空间**追加物理损失。其三，梯度按 `GRADIENT_ACCUMULATION_STEPS` 累积（L386-388）。

`compute_additional_losses`（L282）是本仓对扩散损失的关键增广：用 `scale/offset` 反归一化回顶点空间（L292-306），把预测投影回 PCA 基再重建（L309-311），然后在重建顶点上算三项——`lip_dist_loss` 唇距匹配（L315-322）、`motion_loss` 速度损失（L323-327）、`expression_smooth_reg` 上半脸表情平滑正则（L328-332）。总损失在 L382-385 按 α 权重叠加。

## 外部连接

上游：`dataset.py` 的 `AnimationSegmentDataset`（L969）供给 batch；`networks/diffusion_rnn.py` 的 `Network` 经 `networks/base.py:34` 的 `NetworkBaseDiffusion` 提供前向；扩散引擎经 `script_utils.py:27` 的 `create_gaussian_diffusion` 工厂构造。下游：`run()`（L512）结束后无条件调 `export_onnx`（L271-276，函数体内延迟 `from audio2face import convert_onnx` 防循环导入——Converter 的祖父类正是本文件 Trainer）；`infer_diffusion.InferenceEngine`（L32）继承本类复用装配逻辑；run 模块入口 `run()`（L553）四行串联 setup→preload→run。

## 数据流

batch（audio/vertices/emotion_vec/actor_vec，L335-338）→ 可选随机子段裁剪（L341-348）→ 采样时间步 t → training_losses 内部 `q_sample` 加噪 → 网络 forward 输出 x0 预测 → 扩散 MSE + 部位加权（tongue_weight/jaw_weight，见 `gaussian_diffusion.py:1253` 签名——本仓对上游 MDM 的定制参数）→ 顶点空间附加损失 → backward。注意 L368-369 显式断言 batch size 只能为 1（`compute_additional_losses` 的 actor 级 PCA 参数无法按 batch 混算）。

## 设计决策

- **双出口损失设计**：扩散损失在系数空间、附加损失在顶点空间，靠 `model_output` 这个非标准返回字段桥接——上游 MDM 的 training_losses 并不返回它，这是 vendored 代码被定制的实证。
- **KeyboardInterrupt 优雅收尾**（L519-520）：训练中断不丢产物，仍导出 ONNX。
- **partial exposure 双闸**（L531、L401）：`is_partial_exposure()` 为真时不保存 `weights.pth`、不写部分 TensorBoard 标量——开源版硬编码 False（`audio2face/utils.py:361`）。
- **EMA 归网络管**：EMA 副本在 `NetworkBaseDiffusion`（`networks/base.py:35`）而非 Trainer，训练器只管优化器。

## 新人提示

读代码从 `run()`（L512）倒着进；`setup()` 里 L429-431 会拒绝占位值 `XXXXXX_XXXXXX` 的 `PREPROC_RUN_NAME_FULL`——训练前必须回填预处理产物目录名。调损失先看 `losses.py`（L20-L231 共 12 个损失函数），权重 α 全在 `config_train_diffusion_base.py` 以 `LOSS_*` 前缀暴露。想要复现论文训练，`configs/example-diffusion/` 是全量超参样例（NUM_EPOCHS=400）。
