# 02 推理与导出链：InferenceEngine 与 Converter 的继承复用

## 角色定位

`infer_diffusion.py`（509 行）与 `convert_onnx.py`（189 行）构成训练之后的消费链。两者都不是从零实现：`InferenceEngine`（`infer_diffusion.py:32`，`class InferenceEngine(Trainer)`）继承训练器，`Converter`（`convert_onnx.py:26`，`class Converter(InferenceEngine)`）再继承推理引擎——三级链 Trainer←InferenceEngine←Converter 是本仓最关键的复用设计（NOTES-DIGEST 两个批次独立实证）。含义直白：**推理与导出都以训练器为底座**，网络如何构建、配置如何装载、network_info 怎么组装，全部只需实现一次。

## 内部结构

`InferenceEngine.setup()`（L89）与 Trainer.setup 的差异是"装配 vs 回放"：同样装载三份配置（L90-92）与 Provider/Dataset（L105-115），但不初始化优化器，而是定位训练产物目录（L98-101）、`compose_network_info` 复算网络参数（L117-120）、从 `weights.pth` strict 加载权重（L122-124）、切 eval 模式（L126-128），最后按推理配置的 `TIMESTEP_RESPACING` 重建扩散引擎（L130-137）并选择采样函数——非 DDIM 用 `p_sample_loop`，DDIM 用 `ddim_sample_loop`（L139-142）。

`run()`（L137）按 `INFERENCE_MODE` 分两大家族，实际共 10 个枚举值（L180-208）：offline 家族（offline/offline_onnx）整轨一次去噪；streaming 家族（streaming、streaming_stateless、streaming_stateless_output_delta 及各自 _onnx/_trt 变体）滑窗逐段推理——音频先按 STREAMING_CFG 左右补零（L296-306），窗长 `window_size`、步长折半（L308），每窗独立扩散采样。条件装配在 run() 前半段：音频重采样 16kHz 并过 HubertProcessor 标准化（L145-152，可 `NO_STANDARDIZE_AUDIO` 跳过）、actor one-hot（L154-160）、情感 one-hot（neutral 全零约定，L167-170）。

`Converter` 只加两层东西：`setup()`（L39）末尾构造 `WrapModel`（L44-48）并从 STREAMING_CFG 推出导出形状；`convert_model()`（L58）以随机张量当示例输入调 `torch.onnx.export`（L108-115，opset 14，batch 与 latent 维动态）。

## 外部连接

上游三个 runner 把参数送进来：`runners/run_inference.py`（L26 训练 run 名 + 三个 JSON 修饰器；L46-47 对回归网络显式抛 `NotImplementedError`——**推理只支持扩散线**）；`runners/run_deploy.py` 调 `deploy.run`（deploy.py:110）打包最终部署目录（从训练 deploy/ 拷贝 + 汇集预处理产物，L146-159）。下游消费方：Maya-ACE 插件与 A2F SDK 读 deploy 产物（network.onnx + network_info.json + 情感库）。`WrapModel`（convert_onnx.py:117）依赖 diffusion_rnn.Network 的 `set_mode("streaming_stateless")`（L133-137）把 RNN 隐状态改为经 forward 传入/传出——这是能导 ONNX 的前提（自回归隐状态不能留在 Python 侧）。

## 数据流

推理线：音频文件 → 16kHz + 标准化 → 条件向量三元组（window/actor_vec/emotion_vec，`_get_model_kwargs` L45-65 按模式补 h_gru_all）→ `sample_fn`（`_get_sample_params` L67-88 组参）逐窗去噪 → 预测系数 → `geometry/maya_cache.py:301` 的 `export_animation` 导出 .xml/.mc 动画缓存。导出线：Converter.setup 复用推理装配 → WrapModel 把 N 步去噪循环收进单次 forward → onnx.export 落 `deploy/network.onnx`。

## 设计决策

- **继承而非组合**：三份 setup 高度重叠，作者选择继承复用；代价是 `run()` L138 的 TODO 自认——"ONNX Converter depends on InferenceEngine.setup(), should be disentangled"，连 mkdir 顺序都要为 Converter 让路。
- **多后端推理矩阵**：streaming 分支内嵌 onnxruntime 与 TensorRT 双后端（L216-269，TRT 分支硬编码 steps=2 并手工分配输入输出 buffer）——同一份代码同时充当基准真值（PyTorch）与后端验收器。
- **确定性噪声**：`DETERMINISTIC_NOISE_PATH`（L189-191/L311-313）允许外置噪声张量，服务可复现评测。
- **ONNX 导出的兼容妥协**：`do_constant_folding=False` 附注释 "true causes gpu/cpu device mismatch error"（L111）。

## 新人提示

先跑 offline 模式看整轨效果再切 streaming；推理配置里 `INFERENCE_MODE`/`TIMESTEP_RESPACING`/`NUM_DIFFUSION_STEPS`（config_inference_diffusion_base.py:51-54）是三个最影响行为的键。导出的 ONNX 输入名固定为 window/identity/emotion/input_latents/noise（L112），对齐 SDK 文档时按此核对。若要验证导出模型，用 `streaming_stateless_onnx` 模式加载 `simplified.onnx` 对照（L216-226）。
