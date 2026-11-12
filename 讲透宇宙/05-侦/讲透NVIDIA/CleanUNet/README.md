# 讲透 CleanUNet（NVIDIA 官方语音去噪实现·微仓精读）

> 源仓：`/usr-data/data2/repos/agent-repos/NVIDIA/CleanUNet`（commit 9487a8db，20 文件微仓）
> 论文：《Speech Denoising in the Waveform Domain with Self-Attention》（arXiv:2202.07790，**ICASSP 2022**）
> 产物生成：2026-11-06，understand-anything 全链路 + 人工精读，全部行号锚从源码核实

## 全链状态表

| 环节 | 状态 | 产物位置 |
|---|---|---|
| deepwiki | 📎 16 页（协调者侧持有，本目录未拷贝） | — |
| understand 图谱 | ✅ 58 节点 / 125 边 / 8 层 / 14 步导览 / 0 issues / fingerprints 20@9487a8db | 仓内 `.understand-anything/knowledge-graph.json` |
| onboarding | ✅ 8 节 ≥3000 字（不计空格 7393 字符，锚 87 处去重） | `onboarding/ONBOARDING.md` |
| explain | ✅ 6 篇（每篇六节结构，行号锚全源码核实，抽验 10/10 命中） | `explain/01…06`（索引见下） |

## explain 索引

| 篇 | 主题 | 覆盖文件 |
|---|---|---|
| 01 | CleanUNet 主网络：编码解码 + Transformer 瓶颈 + weight_scaling_init | network.py |
| 02 | 多分辨率 STFT 损失家族（band=full/high 变体开关） | stft_loss.py |
| 03 | 训练主线与多卡协同（global config 注入/断点续训） | train.py |
| 04 | 推理与客观评测（含 subset 契约错位陷阱） | denoise.py + python_eval.py |
| 05 | 数据管道与梯度同步（文件名契约/占位符非 bug） | dataset.py + distributed.py |
| 06 | 配置变体 / 容器 / 资产层（两 config 唯一差异=band） | configs + Dockerfile + exp 权重 |

## 勘误与甄别清单（源码实证，读仓前必看）

1. **论文会议勘误**：网上与任务描述常称 NeurIPS 2021——README.md:106-114 的 bibtex 实证为 **ICASSP 2022**（kong2022speech, pages 7867-7871），arXiv:2202.07790。引用以 README 为准。
2. **subset 契约错位**：denoise.py:133-134 的 argparse choices 允许 'validation'，但 dataset.py:33 断言只放行 training/testing——传 `-subset validation` 必在数据集构造处 AssertionError 崩溃。
3. **`--num_gpus` 占位符非 bug**：distributed.py:158 append 的 `--num_gpus` 在每卡循环 distributed.py:168 被 `args_list[-2]='--rank=i'` **原位覆盖**，最终命令行不含该参数（train.py:201-208 的 argparse 也未定义它）。初读极易误判为 bug。
4. **tsfm_n_layers 双默认**：network.py:232 代码默认 3，两个 configs JSON 均为 5（DNS-large-full.json L9）——复现论文规格以配置为准，模型容量比代码签名看起来大。
5. **pretrained.pkl 是 git-lfs 指针**：盘上仅 3 行文本（version/oid/size），实体 184336765 字节 ≈176MB，须 `git lfs pull` 后 denoise.py:91 的 torch.load 才能工作；两个权重 oid 不同（full:145c101e…/high:513d9e4f…）但 size 相同。
6. **train/denoise 共用 `__main__` 全局 config 隐式耦合**：train()（train.py:70/81/88）与 denoise()（denoise.py:67/71/81）直接读取 `__main__` 块以 `global` 注入的 dist_config/network_config/trainset_config（train.py:214-220、denoise.py:141-147）——单独 import 函数调用必 NameError；train.py:210 注释自认"Globals nicer in this case"。
7. **五 LICENSE 精确对应五上游血统**：LICENSE_1 BSD-3(waveglow→train/denoise/distributed) / LICENSE_2 MIT(ParallelWaveGAN→stft_loss) / LICENSE_3 MIT(jadore attention→network Transformer) / LICENSE_4 MIT(OpenNMT→注意力间接上游) / LICENSE_5 MIT(vq-vae-2→util 调度器)，与 README.md:99 References 一一对应。
8. **README.md:89 "1 GPU is used for evaluation" 不成立**：python_eval.py 全文件零 torch import（只 pesq/pystoi/scipy/numpy），评测全程 CPU，无 GPU 参与。

## 次级发现（钉在各 explain 篇内）

- dataset.py:7 scipy wavread 与 :20 torchvision 均为死 import；:31 `super(CleanNoisyPairDataset).__init__()` 未绑定实例笔误（无害）。
- network.py:122-144 PositionalEncoding 全仓未启用（n_position=0 走 lambda 恒等，:172-175）；:114-119 get_subsequent_mask 逻辑已被 forward 内联（:340）取代。
- util.py:188 docstring 内 LaTeX `\ell_p` 触发 SyntaxWarning: invalid escape sequence（无功能影响）。
- train.py:118 裸 except 吞 checkpoint 错误静默从头训练；:165 clip_grad_norm(1e9) 形同虚设；:166-167 scheduler.step 先于 optimizer.step（对 Adam 无碍）。
- python_eval.py:23 硬编码 range(300)；:30-31 文件缺失静默 continue。
- 两个 configs 唯一字段差异 stft_config.band（full/high），对应 stft_loss.py:117-120 的高频带上半分支——本仓对 ParallelWaveGAN 上游的本地化改造点。
- Dockerfile 无 COPY，纯环境镜像（NGC pytorch:20.12-py3 + torchaudio 0.8.0 等 7 个固定版本依赖）；torchaudio 0.8.0 ↔ stft_loss.py:13 的 is_pytorch_17plus 探测同属 PyTorch 1.7 世代互锁。

## 快速上手

读序建议：本 README → onboarding/ONBOARDING.md（8 节全景）→ explain 01（模型）→ 02（损失）→ 03-05（训练/推理/数据分布式）→ 06（配置资产）。图谱导览（仓内 knowledge-graph.json 的 14 步 tour）与 explain 顺序互补。
