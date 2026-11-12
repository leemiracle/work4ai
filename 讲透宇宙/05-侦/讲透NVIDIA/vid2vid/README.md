# 讲透 vid2vid（NVIDIA 官方视频到视频翻译实现）

vid2vid 是论文 *Video-to-Video Synthesis*（Wang et al., NeurIPS 2018）的官方 PyTorch 实现：以 pix2pixHD 为图像底座，加入光流复用（warp）+ 软掩码融合 + 多时间尺度跳帧判别器三大时序机制，在 street（Cityscapes 语义标签）/ face（关键点边缘图）/ pose（DensePose+OpenPose）三域实现 2048×1024 时序一致的视频翻译。仓库停更于 2019-07（commit 2e6d137），是 2018-2019 年高分辨率视频生成的代表作。

## 全链状态表

| 环节 | 状态 | 明细 |
|---|---|---|
| deepwiki | 完成 | 14 个内容页 + INDEX/_coverage-check/_structure/wiki_full，2026-10-26 抓取 |
| understand 图谱 | 完成 | 283 节点 / 516 边 / 9 层 / 12 步 tour / fingerprints 114 文件 @ 2e6d1375，校验 0 issues |
| onboarding | 完成 | onboarding/ONBOARDING.md，9349 不计空格字符，112 个源码行号锚全验通过 |
| explain | 完成 | 4 篇六节精讲（01 CompositeGenerator / 02 生成判别主体 / 03 数据管线三域 / 04 FlowNet2 vendored 子树） |

## 勘误清单（源码实证 vs README/认知，行号 @ commit 2e6d137）

1. **仓 README 默认值错误**：README 称 `n_scales_temporal` 默认 3，代码实为 2（options/train_options.py:35）。引用参数时以 train_options.py 为准。
2. **vendored FlowNet2 子树在 Python3 下语法死亡**：models/flownet2_pytorch/main.py:264 的 `d.cuda(async=True)` 使用 Python 3.7+ 保留字 async，整文件无法被 Python3 解析；convert.py:1-3 shebang python2.7 且依赖 caffe。它们是上游训练栈遗留，vid2vid 主链不消费——不要试图 import。
3. **上游数据层是死代码**：models/flownet2_pytorch/datasets.py 属 FlowNet2 独立训练数据层，vid2vid 用自己的 data/ 包（data/custom_dataset_data_loader.py:7-18 的四路延迟 import 不含它）。
4. **下载脚本版本分支已被注释**：scripts/download_flownet2.py:5-11 的 torch 0.4.0/0.4.1 双 file_id 选择整段 docstring 化，现行只剩 install.sh 单一下载路径（scripts/download_flownet2.py:18）。网上教程教你按 torch 版本改 file_id，对不上现行代码。
5. **face 域数据增广被有意关闭**：data/face_dataset.py:25-27 的 scale_ratio/scale_shift 随机化代码被注释、改为常量矩阵——`--random_scale_points` 只动关键点不恢复这段随机。
6. **torch 0.3 checkpoint 兼容钩子**：models/base_model.py:50-60 的 resolve_version 手工向 torch._utils 注入 _rebuild_tensor_v2，官方预训练权重是旧版序列化格式，新版 torch 直接 load 会报 AttributeError——这不是 bug 是兼容层。
7. **测试时 dataset_mode 被静默改写**：README 命令行写 `--dataset_mode temporal`，test.py:19-20 实际把它改写为 'test'（走 TestDataset 而非 TemporalDataset），照 temporal 代码路径调试测试行为必然扑空。
8. **脚本矩阵计数（实测修正）**：本组 onboarding 初版写 street 15 / face 10，`ls scripts/{street,pose,face}` 实测 street 14 个文件（11 sh + 3 py）、face 9 个（7 sh + 2 py）、pose 12 个（12 sh）。四轴矩阵（域 × 分辨率 × g1 短程变体 × 训练/测试）的提法成立，数量以本条为准。
9. **download_gdrive.py 三副本 md5 全同**：scripts/、scripts/street/、scripts/face/ 各一份，md5 均 8f23a129e01d8c78cc4ee42b0ffb0e0d——各域下载脚本 `from download_gdrive import *` 就近消费，改一处不会全局生效。

## 产物索引

- deepwiki/：14 内容页（1 总览 / 2 系统架构 + 2.1-2.3 / 3 数据管线 + 3.1-3.3 / 4 训练 + 4.1-4.2 / 5 测试推理 / 6 docker）
- onboarding/ONBOARDING.md：8 节上手指南（架构地图 / CompositeGenerator 深读 / 三域数据流 / 脚本矩阵 / 坑与勘误 / 新人路线）
- explain/：01 CompositeGenerator 掩码融合双分支（网络本体）· 02 生成与判别主体（编排层）· 03 数据管线三域 · 04 FlowNet2 vendored 子树
- 图谱：仓内 /usr-data/data2/repos/agent-repos/NVIDIA/vid2vid/.understand-anything/knowledge-graph.json

## 新人路线

先读论文 §3，再按 explain/01 → onboarding §3.1 → explain/02 的顺序走"网络本体→融合机制→模型编排"；数据侧按需读 explain/03（做数据集）/ 04（换光流模型）。动手跑通优先用 scripts/street/train_512.sh 的现成命令行，对照 options/base_options.py 逐项注解。所有行号锚基于 commit 2e6d137，升级代码后请重新核对。
