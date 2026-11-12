# 04 · train.py——训练主线（610 行单函数的极端单体设计）

## 角色定位

train.py（777 行）是唯一训练入口，组织方式极其"反工程"：`main()` 只做 argparse+spawn（train.py:668-773），**全部训练逻辑塞进一个 610 行的 `train(rank, a, h)` 函数**（train.py:56-665，从 `def train` 到 `def main` 前一行恰好 610 行），连验证循环 `validate` 都是它的**嵌套函数**（train.py:281-428），靠闭包捕获 generator/sw/steps。这是 HiFi-GAN 血统的脚本式组织在工业仓里的活化石——没有任何 Trainer 类抽象。

## 内部结构

train() 内部按序铺开九段：①DDP init（>1 GPU 时，train.py:57-64）②建 G/MPD/MRD（或 MBD/CQTD，train.py:72-91）③mel 损失选择（train.py:94-102）④checkpoint 扫描与断点恢复（train.py:115-138，`scan_checkpoint` 支持改名为 `bigvgan_generator.pt` 的 HF 权重回续训，train.py:117-124）⑤DDP 包装+AdamW+ExponentialLR（train.py:141-164）⑥训练/验证/unseen 验证三套 DataLoader（train.py:176-269）⑦嵌套 validate（train.py:281-428）⑧epoch/batch 双层循环（train.py:456-665）⑨`steps+=1` 后**step 级** LR 衰减（train.py:656-660，v2 改动，v1 是 epoch 级）。

main() 的 argparse 有 20 个参数（train.py:671-743），含 `--freeze_step`（前 N 步只训回归，train.py:704-709）、`--evaluate`（只验证即退出，train.py:719-724）、`--skip_seen`/`--save_audio`/`--eval_subsample`；GPU 数自动探测并均摊 batch（train.py:755-759），多卡 `mp.spawn`（train.py:763-771）。

## 外部连接

汇聚全仓：bigvgan.py 的 BigVGAN（train.py:72）、discriminators 四类（train.py:27-32）、loss 四函数（train.py:33-38）、meldataset 三件（train.py:24）、utils 六件（train.py:40-47）、env 的 AttrDict+build_env（train.py:23）。第三方：tensorboard、pesq、auraloss、tqdm（train.py:48-51）。

## 数据流

单步（train.py:464-656）：`x(mel), y(wav), y_mel(fmax_loss mel)` 上卡 → G 前向 `y_g_hat`（train.py:474）→ **D 步**：MPD/MRD 对 detach 假样本出 logits → LSGAN 损失 → clip_grad_norm（train.py:486-514，阈值 `h.get("clip_grad_norm",1000)`，v2 配置 500）→ **G 步**：mel 损失（λ=45 或 v2 多尺度×15，train.py:526-532）+ 双路对抗 + 双路特征匹配（train.py:535-542）联合 backward（train.py:544-558）→ rank0 记日志/checkpoint/验证（train.py:560-655）。checkpoint 双文件：`g_步数` 只存 G、`do_步数` 存双 D+双优化器+steps/epoch（train.py:576-597）。验证算 mel err/PESQ/MR-STFT，PESQ 重采样 16k（train.py:335-341）、名字含 "nonspeech" 自动跳过 PESQ（train.py:331）。

## 设计决策

① 单体函数换来"从上往下读一遍就是训练全流程"的线性叙事，代价是任何改动都要在 600 行里找位置；② validate 只允许 rank0（train.py:282），seen/unseen 双清单显式防过拟合叙事（train.py:168-171 注释）；③ 断点恢复从 do 文件反推 steps/epoch（train.py:137-138）；④ v2 训练真 batch=32×8 A100（README.md:212），发布 config 写 4 以便单卡微调（README.md:214）。

## 新人提示

**坑 1**：argparse 默认清单路径 `tests/LibriTTS/*.txt`（train.py:678-692）仓内不存在，实际在 `filelists/LibriTTS/`，裸跑必显式传参（README.md:107-118 示例即全覆盖）。**坑 2**：小 batch 从头训 v2 易早期发散，官方建议初期调低 clip_grad_norm=100（README.md:216）。**坑 3**：改训练逻辑先数清闭包依赖——validate 捕获的 steps 是外层变量，checkpoint 后才递增。
