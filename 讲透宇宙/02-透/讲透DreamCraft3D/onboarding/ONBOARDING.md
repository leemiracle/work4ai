# DreamCraft3D 新人指南（简版）

> 依据：仓库 knowledge-graph.json（795 节点/1933 边/8 层/10 步导览）+ README.md。生成日期：2026-09-05。

## 一、项目是什么与定位

DreamCraft3D（论文 arXiv:2310.16818）是 DeepSeek 开源的**层次化 3D 内容生成**方法官方实现：给定一张 2D 参考图（通常先由文生图模型产生），通过"文本→图像→3D"三阶段流水线生成高保真、视角一致的 3D 物体。两个核心贡献：① 用**视角相关扩散模型 Zero-123** 做 score distillation 雕刻几何，保证多视角一致性——纯 2D 扩散先验不知道"背面长什么样"，Zero-123 能从单图推理新视角，弥补了这一致性缺口；② 提出 **Bootstrapped Score Distillation（BSD）**——用场景的多视角增强渲染训练 DreamBooth 个性化扩散模型，扩散先验与 3D 场景**交替优化、相互促进**：优化中的 3D 场景帮扩散模型学到该场景的 3D 知识，学到的先验又反过来提供越来越视角一致的引导，如此自举（bootstrap）带来纹理的实质性跃升。代码构建在 threestudio 与 stable-dreamfusion 之上。注意双许可证：代码 Apache，模型权重 CC-BY-NC（商用受限）。后续已有升级版 DreamCraft3D++（arXiv:2410.12928），改用多平面重建模型提效提质。定位一句话：2D 扩散先验驱动的图像到 3D 资产生成研究框架。

## 二、架构分层（按图谱 layers，自顶向下）

1. **应用入口与实验脚本层**：launch.py、四份 configs YAML、gradio_app.py 演示，用户视角的"操作面"。
2. **三阶段系统编排层**：dreamcraft3d.py 的 ThreeStageOptimizer，论文主实现，stage 字段切换三相行为。
3. **扩散先验引导层**：guidance/ 家族（SDS/BDS/VSD/Zero-123/ControlNet），全项目的"监督信号供应商"，按注册表被系统挑选。
4. **3D 表征与渲染层**：geometry/renderers/materials/exporters，从隐式场到 DMTet 网格，构成"表征被渲染成监督信号"的完整链路。
5. **提示处理与数据层**：prompt_processors 文本编码（CLIP/DeepFloyd/SD 三种 tokenizer）+ data/ 随机相机与参考图批次。
6. **Zero-123 扩散内核层**：extern/ 下 vendored 的完整 LDM（ddpm/ddim/UNet/VAE），理解成本高但可抓主干。
7. **通用工具层**：GAN 判别损失、LPIPS 感知一致性、DPT 深度估计、EMA 等 callbacks，三阶段训练的共同地基。
8. **文档、配置与工程资产层**：docker、CI、load/ 预置资产（四面体网格、HDRI 光照、Zero-123 权重下载脚本）。

## 三、核心模块

- **`launch.py` + `configs/`**：唯一训练入口（--config/--train/--gpu 交给 PyTorch Lightning）；四份 YAML 对应阶段——coarse-nerf/coarse-neus 是 Stage-1 两条几何路线，geometry/texture 是 Stage-2/3；全部指向同一 system_type，靠 stage 字段切换行为。
- **`@register` 插件注册机制**（threestudio/__init__.py）：把 guidance/geometry/material 等登记进注册表，配置里 `*_type` 字符串反查实例化——**理解全仓"配置驱动"设计的钥匙**。
- **`systems/dreamcraft3d.py`**：ThreeStageOptimizer 按 stage 组装几何、材质、渲染器与两路引导（guidance + guidance_3d），阶段间做几何转换与权重接续；zero123.py 是单阶段前身，可对照读。
- **`models/guidance/`**：stable_zero123/zero123 提供视角条件 3D 引导（Stage-1/2）；stable_diffusion_bsd_guidance 是 Stage-3 的 BSD 变体；controlnet_reg_guidance 用深度/法线正则防纹理漂移；vsd 是变分分数蒸馏对照。
- **`models/geometry/` + `renderers/`**：Stage-1 用 implicit_sdf/implicit_volume（NeuS/NeRF 式隐式场 + HashGrid 编码），Stage-2 切 tetrahedra_sdf_grid（DMTet：SDF+顶点变形直接优化可导表面）；渲染器随之从 neus_volume_renderer 换成 nvdiff_rasterizer（nvdiffrast 光栅化）；mesh_exporter 导出最终网格。
- **`extern/zero123.py` + `ldm_zero123/`**：Zero-123 官方推理封装，底下压着完整 LDM——抓住"它把单视角图像变成多视角 SDS 监督"这一句即可，细节按需回查。
- **`threestudio/utils/`（base.py/misc.py）与 `exporters/mesh_exporter.py`**：Generator/Configurable 基类与种子、精度、0 步保存等杂项支撑是插件体系的粘合剂；mesh_exporter 按 system.exporter_type 被挑选，默认配置导出 obj+mtl 带纹理网格，是三阶段成果的最终出口。
- **`prompt_processors/` + `data/`**：三种 tokenizer 适配对应引导模型（CLIP/DeepFloyd/SD）；uncond.py 随机相机批次是 SDS 训练主角，image.py 提供参考图条件。
- **`utils/GAN、lpips、dpt`**：对抗监督（配合 GANVolumeRenderer）、感知一致性项、DPT 深度估计给 ControlNet 正则喂数据。

## 四、快速上手（摘自 README）

硬件门槛：NVIDIA 显卡 **≥20GB 显存** + CUDA（默认配置在 40G A100 上跑；显存不足时优先降低渲染分辨率，再考虑换卡）。

```sh
# 环境：Python>=3.8，PyTorch>=1.12（测过 cu113/cu118），推荐先装 ninja 加速 CUDA 扩展编译
pip install -r requirements.txt
# 权重：stable-zero123.ckpt 下载到 load/zero123/（论文用 zero123-xl.ckpt，仓内有 download.sh）
# Omnidata 深度/法线权重 gdown 下载到 load/omnidata/
```

流程四步（注意各阶段用 `system.weights` 或 `system.geometry_convert_from` 接续上一阶段 ckpt，目录默认在 outputs/ 下按 prompt 命名）：

```sh
# 0) 预处理输入图：去背景 + 生成深度/法线图
python preprocess_image.py /path/to/image.png --recenter
# 1) Stage-1：NeRF 起粗 → NeuS 精修（system.weights 接续 ckpt）
python launch.py --config configs/dreamcraft3d-coarse-nerf.yaml --train system.prompt_processor.prompt="$prompt" data.image_path="$image_path"
python launch.py --config configs/dreamcraft3d-coarse-neus.yaml --train ... system.weights="$ckpt"
# 2) Stage-2：几何细化（system.geometry_convert_from 接续）
python launch.py --config configs/dreamcraft3d-geometry.yaml --train ...
# 3) Stage-3：纹理增强（BSD）
python launch.py --config configs/dreamcraft3d-texture.yaml --train ...
# 4) 导出 obj+mtl 网格
python launch.py --export system.exporter_type=mesh-exporter resume=...
```

省显存技巧：`data.height=128 data.width=128`（含 random_camera 同步降）。Stage-1 出现 Janus（多面）问题时，可选按 README 用 Zero123++ 生成多视角数据 + DreamBooth LoRA 训个性化 DeepFloyd 替换引导（`system.guidance.lora_weights_path` 指向 LoRA 目录）。另外注意两套 Zero-123 权重的差异：默认 `stable-zero123.ckpt`，论文实验用 `zero123-xl.ckpt`，复现指标时别拿错。

## 五、学习路径（按 10 步导览串讲）

**全貌段（步 1–3）**：读 README/安装文档/双许可证建立边界感，注意 CUDA 扩展密集、安装是最容易卡住的一环（可先用 Docker 兜底）→ 看 launch.py 与四份 YAML 如何被 `parse_structured` 装配成带类型的 dataclass，四份配置的 system_type 都指向同一个 dreamcraft3d-system、靠 stage 字段切换行为 → 吃透 `@register` 注册机制与 BaseSystem/BaseLossGathererModule 骨架（训练步、损失收集、指导评测），这一步是理解全仓配置驱动的钥匙。
**主线段（步 4–5）**：精读 ThreeStageOptimizer 论文主实现（对照论文方法图，看三相如何分别组装几何、材质、渲染器与两路引导 guidance+guidance_3d，阶段间如何做几何转换与权重接续），zero123.py 单阶段系统作参照 → 通读 guidance 家族，理清"哪个阶段用哪路监督信号"：Stage-1/2 靠 Zero-123 系视角引导，Stage-3 靠 BSD+ControlNet 正则，VSD 作对照。
**内核段（步 6–7）**：extern/ 的 vendored LDM 抓大放小，只记"load_model + 每 step 的 rgb+相机位姿条件采样"主干 → 几何表征两阶段两形态（Stage-1 隐式 SDF/Volume+HashGrid → Stage-2 DMTet：SDF+顶点变形在四面体网格上直接优化可导表面）与渲染器切换（NeuS/NeRF 体渲染 → nvdiffrast 光栅化），材质与背景模块可插拔。
**支撑段（步 8–10）**：prompt/data 管道（负提示与 Perp-Neg 的处理也在这里）→ GAN/LPIPS/DPT 损失工具（Stage-2/3 高保真的另一半功臣：判别损失配合 GANVolumeRenderer、DPT 深度喂 ControlNet 正则）→ scripts（多视角数据生成、ckpt 转换、DreamBooth/LoRA 微调）/load/docker 工程闭环，跑通 gradio_app.py 完成从论文到复现的闭环。

新人建议：先在单卡跑通三阶段命令拿到一个 mesh，再回头按上述四段读代码，论文与代码对照效率最高。扩展阅读：论文 arXiv:2310.16818 的方法图与损失公式是代码的"说明书"；DreamFusion/Magic3D/ProlificDreamer 等相关工作（README 附链接）可补齐 score distillation 一族的知识地图；若只关心更高质量的生成效果而非研究复现，可直看 DreamCraft3D++。
