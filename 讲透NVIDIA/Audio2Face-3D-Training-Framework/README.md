# 讲透 NVIDIA Audio2Face-3D-Training-Framework

NVIDIA Audio2Face-3D 训练框架（A2F 生态训练侧开源仓，arXiv 2508.16401，v1.0.1，Apache-2.0）：音频驱动高保真面部动画的预处理/训练/推理/部署全链。源码仓 `/usr-data/data2/repos/agent-repos/NVIDIA/Audio2Face-3D-Training-Framework`。

## 全链状态表

| 阶段 | 状态 | 产物 |
|---|---|---|
| DeepWiki | ✅ 2026-10-26 | `deepwiki/` 7 章 19/19 结构页 100%（TRUE_100 终判，含 wiki_full.md） |
| understand 图谱 | ✅ 2026-11-06 | 仓内 `.understand-anything/knowledge-graph.json`：**265 节点 / 524 边 / 14 层 / 15 步 tour**，validator 0 issues 0 warnings，fingerprints 113 文件 @ commit 112c5eb3 |
| ONBOARDING | ✅ | `onboarding/ONBOARDING.md`（~13KB，8 节，行号锚全源码核实） |
| explain | ✅ 6 篇 | `explain/01~06`（训练主线 / 推理导出链 / 网络与损失 / charsiu / MDM 扩散引擎 / 预处理与配置） |
| NOTES-DIGEST | ✅ | 仓内 `.understand-anything/NOTES-DIGEST.md`（16 条批阶段甄别笔记） |

## explain 索引

1. `explain/01-训练主线-train_diffusion.md` —— Trainer 装配/训练循环/收尾导出
2. `explain/02-推理与导出链-infer-convert.md` —— InferenceEngine/Converter 与三级继承
3. `explain/03-神经网络与损失.md` —— diffusion_rnn 主干与回归线对照
4. `explain/04-vendored-charsiu音素对齐.md` —— 音素通道与唯一消费面
5. `explain/05-vendored-MDM扩散引擎.md` —— 扩散数学引擎与两处深度定制
6. `explain/06-预处理与配置.md` —— 预处理三阶段与配置三层体系

## 勘误与甄别清单（源码级实证）

1. **继承主线 Trainer←InferenceEngine←Converter**（`train_diffusion.py:43`/`infer_diffusion.py:32`/`convert_onnx.py:26`）：推理与导出都以训练器为底座；回归线 `train_regression.py:38` 是并列独立 Trainer 不在链上；`infer_diffusion.py:138` TODO 自认"Converter 依赖 InferenceEngine.setup()"耦合债。
2. **双 vendored 定位差异**：charsiu 整树搬入但全仓唯一消费入口是 `charsiu_predictive_aligner`（`phoneme.py:68`），其余 5 个 aligner 零调用；MDM 只搬 `diffusion/` 子目录+`utils/misc.py` 当纯数学引擎（上游训练脚本/Transformer 主干没搬），全仓仅 3 个消费 import（`train_diffusion.py:37-38`、`infer_diffusion.py:25`）。
3. **根 `run_*.py` 是主机侧包装器非真入口**：只做配置装配（importlib 动态加载 `configs/<name>/` Python 模块转 dict）+ subprocess 调 docker 启动器（`run_train.py:20,32-37`、根 `utils.py:54` load_config）；真逻辑入口在容器内 `runners/run_*.py`（`docker/run_train.sh:31-50`）。
4. **双 utils 模块同名不同物**：根 `utils.py`（78 行，主机侧校验/加载/转发）vs `audio2face/utils.py`（401 行，容器内 EasyDict/深合并/校验器）。判别看 import 方向：根包装器 `from utils import ...`，容器内 `from audio2face import utils`。
5. **配置三层动态加载**：基线层 `config_base/` 六模块 → 修饰器层 `configs/<name>/` 四文件按键覆盖（Actor 参数一律 `{actor: value}` 字典）→ 白名单层 `exposed.py:18`；partial exposure 模式下只许白名单键且**训练不保存 weights.pth**（`train_diffusion.py:531-532`）——开源版 `is_partial_exposure` 硬编码 `return False`（`audio2face/utils.py:347-348`），是 NVIDIA 保留的发布变体钩子。
6. **phoneme→Charsiu 函数体内延迟导入**：`phoneme.py:73` 在 `PhonemeDetector.__init__` 内 import charsiu_predictive_aligner（L72 先 `prepare_for_charsiu_import` L84 抑制 transformers 警告/重定向 HF 缓存），控制笨重依赖的加载时机。
7. **两个 deploy 撞名**：`audio2face/deploy.py`（run L110，训练后模型部署器：读 preproc_info/network_info、生成 SDK 侧 model config）≠ `audio2face/preproc/preproc_deploy.py`（预处理第三阶段：汇聚 skin/tongue PCA、算 mean_geometry）。
8. **前任产物四处锚漂移已修正**（本轮逐条复核）：`is_partial_exposure` 实为 `audio2face/utils.py:347`（ONBOARDING 误 L361）；`get_state_info` 实为 L357（误 L372）；`PREPROC_RUN_NAME_FULL` 占位拒绝实为 `train_diffusion.py:426-427`（误 L429-431）；charsiu 延迟导入实为 `phoneme.py:73`（ONBOARDING 与 explain/04 均误 L68）。
9. **MDM 深度定制两处**：分段加权损失——按 skin/tongue/jaw 通道布局乘权重（舌 0.1/颌 1.0，`gaussian_diffusion.py:1405-1415`、`config_train_diffusion_base.py:197-198`）；`p_sample_loop` 尾部流式分叉——streaming_stateless 把 GRU 隐状态 h_gru_all 带出扩散循环、output_delta 模式采样后逐区反归一化（L660-708，上游 MDM 无此概念）。另 `fp16_util.py`+`logger.py` 是互相引用的死代码对，全仓零外部消费。
10. **训练 1000 步 / 推理 2 步**：训练 `DIFFUSION_STEPS=1000`+cosine+`predict_xstart=True`（直预测 x_0）；推理修饰器 `TIMESTEP_RESPACING="2"`（`configs/example-diffusion/config_inference.py:20`）经 `space_timesteps(1000,"2")`={0,999} 两步采样，`SpacedDiffusion` 按 ᾱ 重算 beta 表。注意 ONNX 的 `num_diffusion_steps=2`（`train_diffusion.py:111`）与 respacing 字符串是**两个独立来源**，改其一不改其二会 PT/ONNX 行为不一致。
11. **舌头预处理可跳过**：舌头缓存/中性帧/刚体顶点表任一缺失时写全零占位 PCA、返回 `skipped: True`（`preproc_tongue.py:242-270`）——无舌数据也能全链路跑通，代价是舌头通道学到噪声基底。

## 口径说明

- explain 字数口径 = 不计空格总字符（01-04 为前任 worker 产物，05-06 为 2026-11-06 续写：2420/2498）。
- 全部行号锚从源码 @112c5eb3 逐条核实；勘误第 8 条即本轮复核抓出的前任锚漂移。
