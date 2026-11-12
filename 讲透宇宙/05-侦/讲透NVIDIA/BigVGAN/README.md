# 讲透 NVIDIA/BigVGAN —— 全链知识库总索引

> 源仓：`/usr-data/data2/repos/agent-repos/NVIDIA/BigVGAN`（NVIDIA/BigVGAN @`7d2b454`，v2.4 终版，68 分析文件）
> BigVGAN：通用神经声码器（mel→波形），v1 论文 arXiv:2206.04658 + v2 工程续作（CQT 判别器/多尺度 mel 损失/44kHz 512x/fused CUDA kernel）。

## 全链状态表

| 阶段 | 状态 | 产物与规格 |
|---|---|---|
| deepwiki | ✅ 2026-10-26 | `deepwiki/` 15/15 结构页 TRUE_100（MCP 通道，全层级对账终判）+ wiki_full.md |
| understand 图谱 | ✅ 2026-11-06 | 仓内 `.understand-anything/knowledge-graph.json`：**135 节点 / 305 边 / 10 层 / 15 步 tour / validator 0 issues / fingerprints 68 文件@7d2b4545** |
| onboarding | ✅ 2026-11-06 | `onboarding/ONBOARDING.md`——8 节 7101 字符（不计空格），92 个行号锚全源码核实 |
| explain | ✅ 2026-11-06 | `explain/` 6 篇，每篇 2147-2412 字符（不计空格），六节结构（角色定位/内部结构/外部连接/数据流/设计决策/新人提示），合计 193 锚，锚界内终验 0 坏 |
| 勘误清单 | ✅ 见下 | 12 条，全部源码行号实证 |

## explain 索引

1. `explain/01-bigvgan.py-生成器核心.md`——BigVGAN/AMPBlock1·2/snake 激活族/HF Hub 混入
2. `explain/02-alias-free-双实现树.md`——torch 纯净版 vs CUDA JIT 版、use_cuda_kernel 开关、exp/log 换算
3. `explain/03-判别器与损失-对抗训练面.md`——MPD/MRD/MBD/CQT 四族 + 多尺度 mel 损失 + LSGAN
4. `explain/04-train.py-训练主线.md`——train() 610 行单体、嵌套 validate、DDP spawn、断点恢复
5. `explain/05-推理双路径与demo.md`——inference.py(wav) vs inference_e2e.py(mel.npy) 双加载路径 + gradio
6. `explain/06-配置矩阵与工程配套.md`——九配置三族、env/utils/tests、软键默认值体系

## 勘误清单（12 条，源码实证）

以下均为"README/图谱摘要/直觉认知 vs 源码事实"的差集，行号锚可直接复核：

1. **argparse 默认路径失效**：train.py:678/681 默认 `--input_training_file tests/LibriTTS/train-full.txt`，但仓内不存在 `tests/LibriTTS/`（tests/ 只有 3 个 .py），实际清单在 `filelists/LibriTTS/`——裸跑 train.py 不显式传清单参数必失败（README.md:107-118 示例实际全覆盖了这些参数）。
2. **loss.py:208 休眠 bug**：`loss += self.mag_weight * self.loss_fn(x_logmels, y_logmels)` 的 mag 项应作用于**原始 magnitude mel**（descript 原版为 `loss_fn(x_mels, y_mels)`），此处误用 log-mel——与 207 行 log 项完全重复。默认 `mag_weight=0.0`（loss.py:59）不触发；一旦调非零即双重计 log 项而非幅值项。
3. **图谱摘要"MelDataset 缓存 .mel 文件"不实**（HiFi-GAN 旧版行为残留进知识库）：v2.4 的 meldataset.py 无任何 .mel 磁盘缓存，mel 全量实时计算（meldataset.py:305-315），仅 mel 滤波器基/窗函数有进程内缓存（meldataset.py:47-48、86-93）。
4. **inference_e2e.py 的 scan_checkpoint 是死代码**：inference_e2e.py:30-35 自带本地副本（与 utils.py:75-92 形成第二条平行加载路径），但其 `inference()` 直接用 `a.checkpoint_file` 加载（inference_e2e.py:41），scan 从未被调用；且本地版能力弱于 utils 版（无 `renamed_file` 回退）。
5. **CombinedDiscriminator 拼写错误 + 全仓零消费**：属性名拼作 `self.discrimiantor`（discriminators.py:630）；该类与 MultiBandDiscriminator 在九配置中均无启用（`use_mbd_instead_of_mrd` 分支 train.py:79-84 无任何配置置真，train.py 实际直接独立使用 mpd+mrd 两个判别器）——是"存在但未接线"的库存代码。
6. **v2 静默行为差异**：v2 配置 `use_tanh_at_final:false`+`use_bias_at_final:false`，输出边界从 tanh 改为 `clamp(-1,1)`（bigvgan.py:382-385）；v1 配置无此二键，代码默认 True（bigvgan.py:348/359）——同一份代码两世代输出行为不同，9 模型表（demo/app.py:373-421）不显示此差异。
7. **README batch_size 双口径**：README.md:212 明言 v2 预训练用 batch_size=32×8 A100，而 configs 发布值 4（README.md:214 解释为单 A100 可训）——引用配置时勿误读"发布模型=batch 4 训出"。
8. **demo 依赖差集**：demo/requirements.txt = 根 requirements + `gradio>=4.38.1` + `spaces>=0.28.3` 两行；`spaces` 是 HuggingFace Spaces 专有库（demo/app.py:4/60），本地跑 demo 需补装，否则 import 即失败。
9. **train() 610 行单体**：train.py:56-665 单函数承载 DDP init/断点恢复/优化器/三套 DataLoader/嵌套 validate（train.py:281 闭包捕获 steps）/双层训练循环全部逻辑，main() 只做 argparse+spawn（train.py:668-773）——改训练逻辑需通读全函数，无模块边界。
10. **CUDA 路径三重限定**：① `alias_free_activation/cuda/activation1d.py:11` 模块级执行 `load.load()`——import 即 JIT 编译；② `FusedAntiAliasActivation.backward` 直接 NotImplementedError（activation1d.py:31）——推理专用，训练不支持（bigvgan.py:452-461 三行警告）；③ kernel 硬编码 filter=12/replication pad/logscale 假设（activation1d.py:16-18），超参不同结果静默错误。
11. **train-full.txt 是仓内最大文件**：354570 行（filelists 六件合计 355097 行，其余五件 dev/test/val 仅 527 行）——克隆时 90% 体积是这一份清单，图谱把它归 L09 数据清单层。
12. **图谱 tour t09 "env.py+wandb 渲染钩子"不实**：env.py 全文 18 行只有 AttrDict（env.py:8-11）与 build_env（env.py:14-18），全仓无 wandb 依赖（requirements.txt 无），实验追踪仅 TensorBoard（train.py:272）。

## 勘误之外的源码级洞察（速记）

- **判别器吃的不是 mel 而是 CQT 前的 2x 上采样波形**：DiscriminatorCQT 先 `Resample(fs→2fs)`（discriminators.py:506/533）再 CQT——把时频分辨率整体平移一个八度。
- **MAX_WAV_VALUE=32767 而非 32768**（meldataset.py:20）：注释明示防 int16 溢出爆音，数据/推理/演示三侧共用。
- **e2e 推理责任前移**：mel .npy 的 STFT 五参数（n_fft/win_size/fmin/fmax/hop_size）必须与 config.json 一致（README.md:135），仓不校验只文档约定。
- **librosa.load(sr=None)+裁块后重采样**（meldataset.py:243/274-283）：只重采样随机块而非全文件，大训练集省算力的关键设计。

## 复核方式

```bash
cd /usr-data/data2/repos/agent-repos/NVIDIA/BigVGAN
# 图谱校验
node ~/ai/pipeline-bin/understand/ua-inline-validate.cjs .understand-anything/knowledge-graph.json /tmp/vr.json
# 任一勘误锚抽查，例：勘误 #2
sed -n '200,210p' loss.py
```

（产物日期 2026-11-06；deepwiki 步由 2026-10-26 轮完成，本轮接续 understand→onboard→explain→README 全链收官。）
