# 讲透 NVIDIA/harmonizer

> NVIDIA Harmonizer（CVPR 2026，arXiv 2602.24096）：基于 Cosmos-Predict2-0.6B 的单步扩散增强器，修 NeRF/3DGS（NuRec）渲染伪影并保时序一致性，服务自动驾驶/机器人仿真。
> 仓库：github.com/NVIDIA/harmonizer @ 32f3eca · 图谱 192 节点 / 417 边 / 9 层 / 13 步 tour

## 全链状态表

| 阶段 | 产物 | 状态 |
|---|---|---|
| 知识图谱 | 仓内 `.understand-anything/knowledge-graph.json`（192 节点 / 417 边 / 9 层 / 13 步 tour，validator 0 issues） | ✅ fingerprints 58 文件基线 @32f3eca8 |
| 深度导览 | [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md)（8 节，45+ 行号锚） | ✅ 2026-11-08 |
| 文件精讲 | [explain/](explain/) 3 篇（模型核心与 Cosmos 改造 / 训练双变体与光流损失 / 推理导出与 patch-in-image） | ✅ 2026-11-08 |
| 勘误甄别 | 见下方（8 条，全部源码锚实证） | ✅ 2026-11-08 |

## 速览

- **一句话**：把多步扩散蒸馏成单步、时序条件的增强器，跑在在线仿真器单 GPU 回路里（`README.md:19`）；瞄准 appearance harmonization / artifact correction / lighting realism 三失败模式。
- **结构三合一**：研究仓（src/ 训练+推理+评测）+ 部署仓（onnx_export 八件套 ONNX→TRT）+ agent skill 仓（skills/harmonizer，SKILL.md 401 行+六分册）。
- **最独特工程点**：patch-in-image 容器（`Dockerfile.cosmos:69-70` 双 patch 直改 dist-packages 基库）+ 评测链文档自曝两断点（`skills/harmonizer/references/evaluation.md:3-18`）。

## 勘误与甄别（8 条，均经源码核实）

1. **非球谐算子——是 CVPR2026 扩散增强器**。"Harmonizer" 在图形学语境与 spherical harmonics（3DGS 的 SH 表出）、音频 pitch harmonizer 撞名，NVIDIA 生态里做球谐的是 torch-harmonics 仓。本仓 `README.md:9,19` 定义明确：在线生成式图像增强框架，处理的是渲染伪影修复与外观调和，全仓零球谐计算。按字面检索会把人带进 3DGS 着色器代码。
2. **评测链两断点，且是文档自曝而非社区发现**。`skills/harmonizer/references/evaluation.md:3-18` 开篇即言 "This workflow does not currently run as shipped"：① `src/evaluate_test_dataset.py:109` 调 `load_and_compile_model` 缺签名要求的 `image_size` 参数；② 评测加载 fast-tokenizer 管线而其 config 指向 `/work/models/base/model_fast_tokenizer.pt`（`evaluation.md:51-54`），与 `download_checkpoints.sh:7-8` 落盘路径不匹配。skill 明确告诫 agent 勿向用户承诺评测可完成——引用本仓"可评测"结论前必须带上这条。
3. **NVTXRangeDecorator 是三态条件赋值变量，不是 def**。`src/utils/profiling.py:53-58` 按环境变量 `ENABLE_NVTX_DECORATOR`（`:51`）在 `torch.cuda.nvtx.range` / `NullContextDecoratorCompat`（<2.9 无 graph break 类版，`:23`）/ `nullcontext_decorator`（>=2.9 contextmanager 版，`:18`）三态间切换。静态分析/扫描器找不到函数定义属预期，不是符号缺失。
4. **tokenizer.patch 删装饰器而非改函数体**。patch 的两个 hunk（`@@ -705,7`、`@@ -718,7`）只是在基库 tokenizer 的 `encode`/`decode` 头上各删一行 `@torch.no_grad()`，打开 VAE 梯度回传；配合 `src/model/__init__.py:55/71` 手写 `my_vae_encoder_fwd/my_vae_decoder_fwd` 构成双保险。称其为"重写 tokenizer"不准确。
5. **skill 出身 NVIDIA/nurec-skills，前身名 nurec-fixer**。`skills/harmonizer/NOTICE:10` 明记迁移来源；SKILL.md frontmatter（`:2-8`）自述"public successor to the older Fixer recipes"，联系邮箱仍是 nurec-skills@nvidia.com（`SKILL.md:31`）。引用 skill 结构时别当成本仓原创设计。
6. **三层许可文件语义各异，混读会答错再分发义务**。根 `LICENSE`=Apache-2.0（本项目代码）；`THIRD_PARTY_LICENSE.txt` 首行 "LICENSE INFORMATION FOR PIP PACKAGES"，实为 pip 依赖许可聚合，非本项目许可证；`skills/harmonizer/` 另走双许可——文档 CC-BY-4.0（`LICENSE-CC-BY-4.0`）+ 脚本 Apache-2.0（`LICENSE-Apache-2.0.txt`）。skill 文本再分发受 CC-BY 署名约束，与其余代码不同。
7. **ONNX 导出有双前置，非任意时刻可导**。`src/onnx_export/exportable_modules.py:229-245` 强校验模型 `inference_only_mode=True` 且 `compute_caching` 已执行，违者直接 raise；导出 shape（batch/height/width/timestep）固定（`export_onnx.py`）。把导出当通用模型转换入口会碰壁。
8. **推理入口不通用：AOT 变体不能关键字传参**。`src/pix2pix_turbo_nocond_cosmos_base_faster_tokenizer.py:421` 注释明示 `z_denoised = self.unet(z)` 不能写成关键字形式——AOTModule（`:186`，`aoti_load_package:193`）对签名匹配严格；且该变体的 `ImageEncoder/ImageDecoder` 用 lambda 做 4D→5D 适配（`:199-216`），直接换 tokenizer 实现会破坏形状契约。

## 延伸阅读

- 三篇精讲：[01 模型核心与 Cosmos 基座改造](explain/01-模型核心与Cosmos基座改造.md) · [02 训练双变体与光流损失](explain/02-训练双变体与光流损失.md) · [03 推理导出与 patch-in-image](explain/03-推理导出与patch-in-image.md)
- 生态位：基座 nvidia/Cosmos-Predict2-0.6B-Text2Image；权重 nvidia/Harmonizer（`download_checkpoints.sh:25-29`）；退化数据策略源自 nv-tlabs/Difix3D+（`README.md:112`）；skill 前身 NVIDIA/nurec-skills；同 org 球谐库是 torch-harmonics（非本仓）。
