# 讲透 pix2pixHD（NVIDIA 官方高分辨率图像翻译实现）

pix2pixHD 是 CVPR 2018 论文 *High-Resolution Image Synthesis and Semantic Manipulation with Conditional GANs* 的官方实现：语义标签图到 2048×1024 照片级图像的条件 GAN 框架，核心贡献为粗到细生成器（全局生成器+局部增强器）、多尺度判别器与三路损失（GAN+特征匹配+VGG），附实例特征编码与交互式 UI 编辑两个扩展子系统。源码基线 commit 14b3b3c（2024-09-30，代码本体为 2018 年产物，Python2/3 过渡期风格）。

## 全链状态表

| 环节 | 状态 | 说明 |
|---|---|---|
| DeepWiki | 完成 | 17/17 页真一百分（2026-10-26 MCP 抓取，deepwiki/INDEX.md） |
| understand 图谱 | 完成 | 101 节点 / 200 边 / 7 层 / 11 步 tour，fingerprints 43 文件 @14b3b3c7 |
| ONBOARDING | 完成 | onboarding/ONBOARDING.md（约 8100 不计空格字符，102 锚） |
| explain 精讲 | 完成 | 3 篇（见下索引），锚全部源码核实 |
| 本 README | 完成 | 2026-11-10 |

## 产物索引

- `onboarding/ONBOARDING.md` —— 8 节上手指南（架构地图/核心深读/数据流/设计决策/坑/上手路线）
- `explain/01-networks-生成器与判别器族.md` —— networks 工厂：GlobalGenerator/LocalEnhancer/MultiscaleDiscriminator/GANLoss/VGGLoss
- `explain/02-训练主体与损失体系.md` —— Pix2PixHDModel 编排：五元损失闭包过滤、ImagePool、BaseModel 三级加载兜底、UIModel 平行分支
- `explain/03-数据管线与特征预计算.md` —— AlignedDataset 双 transform 约定、延迟 import 破循环、特征两段管线、TRT 推理轴
- `deepwiki/` —— 17 页 wiki 快照（1-overview 至 9-running-the-system）

## 勘误清单（源码实证 vs README/DeepWiki/直觉认知）

1. **TRT 推理路径在源码层面不可运行**：run_engine.py 存在三处未定义名——`range(iter)`（run_engine.py:115）、`max_batch_size`/`max_workspace_size`（run_engine.py:157-158）、run_onnx 末行把建好的 `trt_engine` 误写成 `engine`（run_engine.py:171-173）；且 `trt.infer.ConsoleLogger`（run_engine.py:33）与 `tensorrt.parsers.onnxparser`（run_engine.py:24）是 TensorRT 3.x API，TRT 5+ 已全部移除。对照：DeepWiki 5.2 页把 TRT 描述为可用的部署加速路径（"alternative inference engine for deployment"），未提示源码在现代环境下必然 NameError——TRT 轴应视为历史实验，主线推理以 test.py:59 的 model.inference 为准。
2. **DeepWiki 把聚类过滤条件误称"置信度"**：DeepWiki 4.2 页称 "Only features with confidence > 0.5 are used"；源码 encode_features.py:47 过滤的最后一列实为**实例面积占比**——models/pix2pixHD_model.py:258 写入 `num/(h*w//32)`（block_num=32 的尺寸归一化），是大小度量而非置信度。
3. **聚类文件名带零填充**：DeepWiki 4.2 写作 `features_clustered_[n_clusters].npy`；源码是 `features_clustered_%03d.npy`（encode_features.py:52），options/test_options.py:12 的默认 `--cluster_path` 为 `features_clustered_010.npy`。按 DeepWiki 字面拼出 `features_clustered_10.npy` 会让 sample_features（models/pix2pixHD_model.py:221）找不到文件。
4. **`raise('字符串')` 双现**：models/base_model.py:58 与 models/networks.py:38 在 Python3 下抛 TypeError 而非预期错误消息（Python2 遗留写法），排障时看到的异常类型会出乎意料。
5. **BaseModel.update_learning_rate 定义缺 self**（models/base_model.py:90）：基类方法实为死代码，全靠子类正确覆写（models/pix2pixHD_model.py:288）掩盖；若有新模型只继承不覆写，学习率衰减将静默失效。
6. **fractions.gcd 在 Python 3.9 已移除**：train.py:9 的 lcm 自实现引用 `fractions.gcd`，新解释器下 import 后首次调用即 AttributeError，需换 `math.gcd`。
7. **torchvision 0.2 时代 API**：data/base_dataset.py:37 的 `transforms.Scale` 在新版 torchvision 已改名 Resize，直接跑会 AttributeError。
8. **volatile 与 no_grad 新旧混用**：precompute_feature_maps.py:29 与 models/pix2pixHD_model.py:241 用 PyTorch 0.3 的 `volatile=True`（0.4+ 被忽略并告警），而同文件 inference 已写 0.4 的 `torch.no_grad()` 分支（models/pix2pixHD_model.py:212-214）——移植时只改一半会漏免梯度保护。

## 新人路线

先读 onboarding 第一、二节建立地图 → 按精讲一→二→三的顺序走网络工厂、训练编排、数据面 → 勘误清单当避坑表用（尤其第 1、6、7 条决定可运行性）。深入交互编辑再读 models/ui_model.py 的 style_forward（models/ui_model.py:225）与 get_crop_region（models/ui_model.py:293）。

> 锚格式 `文件:行`，相对仓根 /usr-data/data2/repos/agent-repos/NVIDIA/pix2pixHD/；全部行号经源码逐条核实（2026-11-10）。
