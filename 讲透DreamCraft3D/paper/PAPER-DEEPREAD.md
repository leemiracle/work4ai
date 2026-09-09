# PAPER-DEEPREAD：DreamCraft3D — Hierarchical 3D Generation with Bootstrapped Diffusion Prior

> 论文：arXiv **2310.16818**（2023-10-25，ICLR 2024 poster，proceedings.iclr.cc 已核实）
> 团队：清华大学（Jingxiang Sun、Ruizhi Shao、Lizhen Wang、Yebin Liu）× DeepSeek AI（Wen Liu、Zhenda Xie；一作在 DeepSeek 实习期间完成部分工作）
> 代码：`deepseek-ai/DreamCraft3D`（本地 `~/ai/explore/deepseek-ai/DreamCraft3D`，基于 threestudio 框架重构）

**ID 核实记录（2026-09-05）**：2310.16818 标题/摘要完全匹配 ✅；venue = ICLR 2024（iclr.cc virtual poster 19148 + 官方 proceedings 双重实证）。

---

## 1. 一句话定位

**用"先 2D 出图 → 雕几何 → 再刷纹理"的三阶段层级流水线生成 3D 资产，核心创新是 Bootstrapped Score Distillation（BSD）：拿正在优化的 3D 场景的多视角渲染图去 DreamBooth 微调一个"场景专属扩散先验"，再用这个不断进化的先验反过来蒸馏 3D 场景——目标分布本身在随优化状态演化**，从而同时拿到照片级纹理与 360° 视角一致性。

它是 image-to-3D 路线（区别于纯 text-to-3D 的 DreamFusion 系）在 2023 年底的 SOTA：CLIP-score 0.896、参考视角 PSNR 31.8、用户研究 92% 偏好率碾压同期五个基线。

## 2. 动机与痛点

- **3D 数据稀缺**：通用 3D 生成没法像 2D 一样直接训练大生成模型 → 只能借 2D 文生图基础模型"蒸馏"出 3D（DreamFusion 开创的 SDS 路线）。
- **SDS 的三宗罪**：需要超大 CFG guidance → 过饱和/过平滑；每视角独立监督 → 全局 3D 不一致，**Janus 问题**（多张脸/多条腿）；固定目标分布只保证单视角合理。
- **3D-aware 先验的先天不足**：Zero-1-to-3 等 view-conditioned 模型在 Objaverse 上训练，视角意识好但纹理质量差——**几何一致性与纹理保真天然打架**。
- 前作应对要么分段（Magic3D coarse-to-fine）要么换损失（ProlificDreamer VSD），但没有一篇把"层级流水线每一阶段配专属先验"这件事做彻底；DreamBooth3D（Raj et al. 2023）已试个性化扩散模型但仍难全局一致。

**核心洞察**：几何阶段牺牲纹理换一致性（用 3D 先验），纹理阶段固定几何、把"一致性"外包给一个从场景自身渲染图学出来的扩散先验，且两边交替上升（bootstrap）。

## 3. 核心方法

### 3.1 预备：SDS 与 VSD 的梯度形式

SDS（DreamFusion）：

$$\nabla_\theta \mathcal{L}_{\text{SDS}}(\phi, g(\theta)) = \mathbb{E}_{t,\epsilon}\Big[\omega(t)(\epsilon_\phi(x_t;y,t)-\epsilon)\frac{\partial x}{\partial\theta}\Big]$$

VSD（ProlificDreamer）：把解视为分布 $q^\mu(x_0|y)$，对齐扩散模型定义的 $p(x_0|y)$（KL），梯度等价于"预训练分数 − LoRA 分数"之差：

$$\nabla_\theta \mathcal{L}_{\text{VSD}} = \mathbb{E}_{t,\epsilon}\Big[\omega(t)(\epsilon_\phi(x_t;y,t)-\epsilon_{\text{lora}}(x_t;y,t,c))\frac{\partial x}{\partial\theta}\Big]$$

两者都从**固定**的 2D 分布蒸馏——这是 BSD 要打破的设定。

### 3.2 阶段一：Geometry Sculpting（几何雕刻）

**损失全家桶**（参考视角 $c^{\wedge}$、渲染 $g(\theta;c)$）：

- 参考视角光度损失（只算前景区）：$\mathcal{L}_{\text{rgb}}=\|\hat{m}\odot(\hat{x}-g(\theta;\hat{c}))\|_2$；mask 损失利稀疏化：$\mathcal{L}_{\text{mask}}=\|\hat{m}-g_m(\theta;\hat{c})\|_2$；
- 深度/法线一致性（Omnidata 单目估计，负 Pearson 相关处理尺度失配）：

$$\mathcal{L}_{\text{depth}}=-\frac{\text{conv}(d,\hat{d})}{\sigma(d)\sigma(\hat{d})},\qquad \mathcal{L}_{\text{normal}}=-\frac{n\cdot\hat{n}}{\|n\|_2\|\hat{n}\|_2}$$

- **混合 SDS（本文 3D 先验核心）**：2D 分支用 DeepFloyd IF（64×64 像素空间，抓粗结构），3D 分支用 Zero-1-to-3 以参考图为条件：

$$\nabla_\theta\mathcal{L}_{\text{hybrid}} = \nabla_\theta\mathcal{L}_{\text{SDS}} + \mu\,\nabla_\theta\mathcal{L}_{\text{3D-SDS}},\qquad \mu=2$$

其中 $\nabla_\theta\mathcal{L}_{\text{3D-SDS}}=\mathbb{E}_{t,\epsilon}[\omega(t)(\epsilon_\phi(x_t;\hat{x},c,y,t)-\epsilon)\frac{\partial x}{\partial\theta}]$。消融显示去掉 Zero-1-to-3 立刻出现 Janus 与畸形几何。

- **Progressive view training**：训练视角从参考视角附近逐步放大到 360°，把已建好的几何"传播"出去（避免单图歧义直接生成多余椅子腿）。
- **Diffusion timestep annealing**：噪声步 $t$ 从 $\mathcal{U}(0.7,0.85)$ 线性退火到 $\mathcal{U}(0.2,0.5)$——先全局结构后细节，与 coarse-to-fine 对齐（承 DreamTime/ProlificDreamer）。
- **表示升级**：NeuS（隐式 SDF，Instant-NGP 64→384，单层 32 隐单元 MLP 同出 RGB/密度/法线，每 10 迭代 octree 剪枝）→ DMTet（128 可变形四面体网格，512 渲染分辨率）——网格表示天然解耦几何与纹理，给阶段二"冻结几何只刷纹理"铺路。

### 3.3 阶段二：Texture Boosting via BSD（本文最大贡献）

**VSD 直接用会翻车**：换 SD 后纹理真实了，但固定 2D 先验不知道"这个物体的背面长什么样"，纹理不一致卷土重来。

**BSD 三步循环**：

1. **渲染**：当前 mesh 出多视角图 $\{x\}=g(\theta,c_r)$；
2. **增强**：加噪到 $t'$ 档：$x_{t'}=\alpha_{t'}x_0+\sigma_{t'}\epsilon$，再由扩散模型去噪还原 $x_r=r_{t'}(x)$——大 $t'$ 放大细节但引入不一致，小 $t'$ 忠实但保守。**随场景变好逐步调小 $t'$**（实现里从 0.5 退火到 0.1）；
3. **DreamBooth + 蒸馏**：用 "A [V] xxx" 稀有标识符 + 类名 + 相机参数条件微调出场景专属 $\epsilon_{\text{DreamBooth}}$；3D 梯度：

$$\nabla_\theta\mathcal{L}_{\text{BSD}}(\phi,g(\theta))=\mathbb{E}_{t,\epsilon,c}\Big[\omega(t)\big(\epsilon_{\text{DreamBooth}}(x_t;y,t,r_{t'}(x),c)-\epsilon_{\text{lora}}(x_t;y,t,x,c)\big)\frac{\partial x}{\partial\theta}\Big]$$

ICLR 版补总损失 $\mathcal{L}_{\text{texture}}=\lambda_{\text{rgb}}\mathcal{L}_{\text{rgb}}+\lambda_{\text{BSD}}\mathcal{L}_{\text{BSD}}$。**交替优化 2 轮即收敛**（配置里 `freq.n_ref: 2`）。

**直觉**：SDS/VSD 是"向着固定靶子射箭"，BSD 是"靶子跟着你的箭移动"——扩散先验从场景自己的渲染图学习，天然带 3D 概念；场景又从这个越来越懂它的先验拿越来越一致的指导。附录 Algorithm 1 给出完整伪代码（外层循环渲染→增强→微调，内层 T 步对 θ 和 φ 双更新）。

**Structure-aware latent regularization（附录 eq 8）**：ControlNet（几何法线条件）引导的 inpainting 模型补全参考视角不可见区域，生成 $x_{\text{reg}}$，以潜变量范数软约束（不做像素级硬监督）：

$$\mathcal{L}_{\text{reg}}(\phi,g(\theta))=\Sigma(\|E(x)\|_2-\|E(x_{\text{reg}})\|_2)^2$$

（开源版默认配置中 controlnet 分支被注释，属可选增强。）

**训练细节补充（附录 A.1）**：相机/光照增强沿 Magic3D 但三点不同——点光角距 $\mathcal{U}(0,\pi/3)$、**冻结材质增强**（否则伤收敛）、NeuS 粗阶段"固定-随机混合内参"策略（一半 GPU 固定内参满足 Zero-1-to-3 的固定内参要求，另一半随机采距离 $\mathcal{U}(3.2,3.5)$ / FOV $\mathcal{U}(10,20)$）。

## 4. 实验与结果

**定量（300 样本基准：真实图 + SD/DeepFloyd 生成图，附 alpha/深度/prompt）**：

| 方法 | CLIP ↑ | Contextual ↓ | PSNR ↑ | LPIPS ↓ |
|---|---|---|---|---|
| Make-it-3D | 0.872 | 1.609 | 18.937 | 0.054 |
| Magic123 | 0.843 | 1.628 | 22.838 | 0.053 |
| **DreamCraft3D** | **0.896** | **1.579** | **31.801** | **0.005** |

PSNR 31.8 vs 22.8/18.9——参考视角保真断崖式领先（LPIPS 0.005 几乎贴脸）。

**用户研究**：32 人 × 15 组 prompt/图 = 480 份选择，**92% 偏好本方法**（对比 DreamFusion/Magic3D/ProlificDreamer/Make-it-3D/Magic123）。

**消融（Figure 6）**：① 去 Zero-1-to-3 → Janus 重现；② 纹理用 SDS → 过饱和过平滑；③ 用 VSD → 纹理真但不一致；④ BSD 1 轮 → 一致性回来；⑤ BSD 2 轮 → 细节再上一档。ICLR 版 Table 2 定量佐证同结论。

## 5. 局限与后续

- **论文自认（附录 A.3）**：深度先验的歧义/误差会把正面几何细节"烙"进纹理（大象鼻子学成错误几何的失败案例）；未做材质-光照分离（relight 留给未来）。
- **成本**：三阶段级联 + 每样本 DreamBooth 两轮，单物体优化以小时计（README 建议 40G A100）——这是 per-instance 优化路线的通病。
- **后续**：**DreamCraft3D++**（arXiv 2410.12928，2024-10）用多平面重建模型换掉最慢环节，质量效率双升级；BSD 的"自我提升先验"思想被后续大量 3D 生成工作继承；层级化（先几何后纹理）成为 image-to-3D 事实标准范式（TRELLIS 等前馈路线崛起前的主流）。
- **社区评价**：开源时是图像到 3D 质量天花板，threestudio 生态里 BSD guidance 实现被当作 VSD 家族教科书写法引用。

## 6. 与代码的对照（本地仓映射）

| 论文概念 | 代码位置 |
|---|---|
| 三阶段流水线 | `configs/dreamcraft3d-{coarse-nerf,coarse-neus,geometry,texture}.yaml`（README Quickstart 四连命令） |
| 系统状态机（stage: nerf/neus/geometry/texture） | `threestudio/systems/dreamcraft3d.py`（`system_type: dreamcraft3d-system`） |
| $\mathcal{L}_{\text{SDS}}$（DeepFloyd 分支） | `threestudio/models/guidance/deep_floyd_guidance.py` |
| $\mathcal{L}_{\text{3D-SDS}}$（Zero-1-to-3） | `zero123_guidance.py` / `stable_zero123_guidance.py`（论文用 `stable-zero123.ckpt`，paper 版 zero123-xl） |
| VSD 基线 | `stable_diffusion_vsd_guidance.py` |
| **BSD 全家桶**（pipe + pipe_lora + DreamBooth 循环 + 相机条件） | `stable_diffusion_bsd_guidance.py`（1133 行：`train_unet_lora`、`guidance_scale_lora=1.0`、`lora_cfg_training` 等） |
| $\mathcal{L}_{\text{reg}}$（ControlNet 正则） | `controlnet_reg_guidance.py` / `controlnet_guidance.py` |
| 深度/法线先验 | `preprocess_image.py`（Omnidata dpt depth/normal + `--recenter` 去背景，模型放 `load/omnidata/`） |
| 纹理阶段冻结几何 | texture.yaml `geometry.fix_geometry: true` + `geometry_type: tetrahedra-sdf-grid`（DMTet 128） |
| timestep 退火 | texture.yaml `max_step_percent: [0, 0.5, 0.2, 5000]`（start_iter/start_val/end_val/end_iter 四元组） |
| BSD 两轮交替 | texture.yaml `freq.n_ref: 2`、`ref_or_guidance: alternate`；损失权重 `lambda_sd 0.01 / lambda_lora 0.1 / lambda_pretrain 0.1`；`only_pretrain_step: 1000` |
| Janus 兜底（可选） | `threestudio/scripts/img_to_mv.py`（Zero123++ 出多视角）+ `train_dreambooth_lora.py`（微调 DeepFloyd-IF LoRA 换 2D guidance，`lora_weights_path` 注入） |
| NeuS 细节（剪枝/密度偏置） | `threestudio/models/geometry.py`（TetrahedraSDFGrid / NeuS ImplicitVolume） |

## 7. 学习路径

1. **前置**：扩散模型基础（score/DDPM/CFG）；NeRF 体渲染与 NeuS 的 SDF 公式；DreamFusion（SDS 推导，2209.14988）与 ProlificDreamer（VSD，2305.16213）——本文在学习路径上正是这两篇的"第三跳"；DreamBooth/LoRA 概念；DMTet 表示。
2. **精读顺序**：§3 预备（两公式）→ §4.1（几何阶段四件套：损失/3D 先验/退火/表示升级）→ §4.2 + 附录 Algorithm 1（BSD 主体，手推一遍与 VSD 的差别只是"固定分数换成 evolving 分数"）→ §5 消融图（对照每个损失的视觉证据）→ 附录 A.1 工程细节。
3. **复现建议**：`preprocess_image.py` → 四阶段 launch.py 全跑（默认 hamburger 示例，40G A100；显存紧张时 NeuS 阶段降到 128×128）；重点把玩 `stable_diffusion_bsd_guidance.py` 的 train_dreambooth 内循环与 `n_ref`/`only_pretrain_step` 超参；消融复刻：把 `guidance_type` 换成 vsd/sd 版本对比纹理一致性。
4. **延伸**：读 DreamCraft3D++（2410.12928）看"多平面重建"如何替代 per-instance SDS；对照 2025 后的前馈 3D 生成（TRELLIS/Hunyuan3D）理解优化式路线的历史位置。
