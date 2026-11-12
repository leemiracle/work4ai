# 03 · 双轨工程与推理链：Lightning 双副本 + ensembled 子进程包装

## 角色定位

本篇讲工程层：A2SB 怎么训练（main.py + LightningCLI）、怎么服务化（_api 双轨）、怎么跑长音频批量推理（T-finetune 时间分区 + inference/ 子进程包装器）。这层的看点不是算法而是**研究代码的组织方式**——文件级复制替代参数化、配置生成器 + shell 子进程两段式、以最少的框架改动换最大的部署灵活性。

## 内部结构

**入口三兄弟**。`main.py`：`InpaintingAudioSBLightningCLI`（main.py:14-30）向 LightningCLI 注册 ModelCheckpoint 与验证 inpainting 回调、预设命名/频率默认值、link checkpoint 目录到 trainer root；模块顶层直接实例化 cli（main.py:32）无 `__main__` 守卫——`python main.py fit --config ...`（README.md:49）直接可用，但 import main 即触发参数解析。`ensembled_inference.py`：同一 CLI 类的复制粘贴版（ensembled_inference.py:14-30），唯一实质差异是绑定 `TimePartitionedPretrainedSTFTBridgeModel` 而非 `STFTBridgeModel`，且多了 `__main__` 守卫（:31-32）——两个入口脚本行为不一致本身就是个坑。`ensembled_inference_api.py`：与 ensembled_inference.py **整文件仅 import 行不同**（ensembled_inference_api.py:9，改从 _api 模块导入）。

**双轨 diff 实证**。`A2SB_lightning_module_api.py` vs `A2SB_lightning_module.py`，`diff` 全量只有 4 处 hunk：(1) 构造参数 `predict_output_dir="output"` 换成 `output_audio_filename="recon.wav"`；(2) 采样循环去 tqdm（原 :122）；(3) predict_step 输出从"目录下 recon.wav/dirty.wav 双文件"（原 :204-205）改为"写指定单文件"；(4) 一行空行。其余三类训练/采样/评估逻辑逐字相同。这就是"CLI 实验版 vs API 服务版"的全部秘密——**没有抽象，只有复制**。好处：两轨独立演进互不拖累（服务版去 tqdm 防日志爆、单文件输出适配调用方路径）；坏处：任何 bug 修复要改两处，图谱统计中 _api 版三个类 fanIn 明显更低（仅被 ensembled_inference_api.py 消费）即是佐证。

**时间分区推理模块**。`TimePartitionedPretrainedSTFTBridgeModel`（A2SB_lightning_module.py:34-205）是长音频主角：构造时按 `t_cutoffs` 列表加载 len(cutoffs)+1 个 checkpoint（断言 :59），`load_t_bounded_checkpoints`（:64-78）从完整 Lightning state_dict 里剥 `vf_model.*` 前缀、deepcopy 骨架逐个灌权重，收进 nn.ModuleList；采样时 `get_vf_model(t)`（:81-86）线性扫 cutoffs 路由到对应专家——前半段桥用专精 t∈[0,0.5] 的模型，后半段换人。`ddpm_sample`（:103-146）在其间做 MultiDiffusion 滑窗采样（详见 01 篇），掩区/已知区的双重混合在 :133-134 与 :139-144。快通道 `fast_inpaint_ddpm_sample`（:149-180）：假设每个洞短于窗口且彼此分离，`find_middle_of_zero_segments`（utils.py:54）找洞心，只对洞邻域跑完整采样——长音频稀疏小洞时省掉整段滑窗的算力。`predict_step`（:183-205）强制 batch=1（断言 :185），t_steps=linspace(1,0.05,predict_n_steps)（:192），最终 pred_x0 经 `vocode_stft`（:89-100，逐样本跑 inv_transforms 逆链）回波形写盘。

**inference/ 子进程包装器三件套**。共同模式"配置生成器"：读 YAML 模板（`load_yaml`）→ Python dict 改写 → `save_yaml` 写**带时间戳+随机数后缀的临时文件**（inference/A2SB_upsample_api.py:37-45，防并发撞名）→ `shell_run_cmd`（Popen(shell=True) 回显输出，:48-53）调 `python ensembled_inference(_api).py predict -c 基础配置 -c 临时配置`（:81-87）→ 删临时文件。三件分工：`A2SB_upsample_api.py`（单文件带宽扩展，README.md:74 主推入口）——`compute_rolloff_freq`（:56-61）用 librosa spectral_rolloff 99% 能量点自动测截止频率，填进 upsample_mask_kwargs 的 min=max=rolloff（:74-78）实现零参数调用；`A2SB_upsample_dataset.py`（数据集批量）——librosa 双重重采样人工合成指定截止频率的退化版，original/degraded/recon 三版本归档；`A2SB_inpaint_dataset.py`——按 `inp_len/inp_every` 参数生成等距时间戳序列（`inpaint_one_sample`，:78-173），argparse 入口（:176-204）。两处硬编码要改源码：manifest 根路径（A2SB_inpaint_dataset.py:187）与 `cd ../` 假定从 inference/ 目录起跑（A2SB_upsample_api.py:81）。

## 外部连接

上游：configs/ensemble_2split_sampling.yaml 绑定时间分区模型与两个 t 区间 checkpoint；T-finetune 产出的 checkpoint 是它的输入。下游：包装器输出的 wav 进 ssr_eval 指标体系（test_step 里 `ssr_eval.metrics.AudioMetrics`，A2SB_lightning_module.py:415）。平级：`LogValidationInpaintingSTFTCallback`（:479-530）在验证期写频谱图/音频样本——但 `num_to_plot = 0`（:493）让整个循环空转，是关掉的可视化开关。

## 数据流（一次数据集级批量推理）

manifest CSV → read_standard_csv（A2SB_inpaint_dataset.py:32-51 本地复刻版）→ 逐文件：{改写 YAML（时间戳/截止频率/输出路径）→ 写临时配置 → shell 起 ensembled_inference.py 子进程 → LightningCLI predict → FullSequencePredictDataset 整段加载 → pad+MultiDiffusion 50 步采样 → vocode 逆变换 → wav 落盘} → 删临时 YAML。每个文件一次完整 Python 进程启动——冷启动开销全部自担，这是批量评估"能跑但慢"的直接原因。

## 设计决策与批判

**(1) 为什么子进程而不 import 函数**：LightningCLI 的配置体系（class_path 动态实例化+多层 YAML 覆盖）已是事实上的"函数签名"，复用它比写 Python API 更省——代价是每文件一个进程、错误隔离靠 shell 回显。研究仓在"复用配置层"与"工程效率"间选了前者。**(2) 时间分区而非单模型全段**：T-finetune 论文思想——单个网络容量有限，把桥按 t 切段各训专家，推理串联；代价是 checkpoint 数量×2、路由逻辑进模块（:81-86）、且 cutoffs 硬编码在配置。**(3) 双轨复制的真实动机**：tqdm 与输出路径都是"最后一公里"差异，任何抽象（参数化 output_mode）都要动 LightningCLI 序列化链——作者权衡后选择复制，留下了 4 组需同步维护的代码。**(4) batch=1 限制**（:185）：MultiDiffusion 的 Unfold 重排假定同形状整批，变长长音频无法拼 batch——吞吐天花板低，服务化场景需外层并行（多进程）补。

## 新人提示

跑通顺序：先 `A2SB_upsample_api.py`（最短路径，只需 checkpoint）再看 dataset 版。读双轨时以 diff 为地图：4 个 hunk 之外的一切以 A2SB_lightning_module.py 为准。想改推理参数（步数/窗口/hop）优先改命令行覆盖（`--model.predict_n_steps=`，A2SB_upsample_api.py:85），别动基础 YAML。调试子进程失败先看 stdout 回显——shell_run_cmd 是同步逐行打印的（:48-53）， LightningCLI 的参数错误会直接暴露在包装器日志里。改 `t_cutoffs` 记得同步 checkpoint 列表长度（断言 :59 会拦），2-split 配置就在 configs/ensemble_2split_sampling.yaml。
