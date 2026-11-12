# NVIDIA-GenAI-Creator-Toolkit 新人入门（ONBOARDING）

> 图谱基线：commit `29ee60d9`，89 节点 / 171 边 / 8 层 / 14 步导览，66 文件全量分析。

## 1. 项目定位

**是什么**：NVIDIA 官方开源的 ComfyUI 创作型生成式 AI 工作流教学合集（Apache-2.0），改编自 GTC 2026 DLI 课程 *Create Generative AI Workflows for Design and Visualization in ComfyUI*（编号 DLIT81948，README.md:10）。核心资产是 **10 个核心模块 + 2 个 Bonus 模块的 workflow JSON 与配套文档**，不是库代码——全仓唯一重量级可执行程序只有一个 `download_models.py`（1244 行）。

**解决什么**：面向设计师与可视化工作者，把「弱提示词→模型级指令」「单图→图层/全景/HDRI/3D 资产」「playblast→风格化视频」等创作链路做成可复制的 ComfyUI 流水线，并用双平台安装器消除环境搭建门槛。

**技术栈**：Bash（install.sh）+ Windows batch（install.bat）+ Python 3.10 标准库风格脚本 + ComfyUI workflow JSON（LiteGraph/UI v0.4 两种格式）。模型家族覆盖 Qwen Image 2511/2512、Wan2.2 I2V/VACE、Flux、TRELLIS(Trellis2)、Lotus、Marigold、Gemma3(Ollama)。

**规模数字**：66 个分析文件；10+2 模块四件套（workflow JSON + README + models.md + nodes.md）；最大 workflow 是 `workflows/bonus-b-texture-to-pbr/bonus-b-texture-to-pbr.json`（18612 行、49 顶层节点、21 个 subgraph）；硬件门槛 RTX 5090 (Windows) / RTX PRO 6000 (Linux)、全装 12 模块磁盘约 450GB（README.md:16-17、README.md:97）。

## 2. 架构总览

图谱 8 层自下而上是「协作基建 → 文档 → 工具 → 安装器 → 模块三链」：

- **L01 平台协作与仓库配置（7 文件）**：GitHub 协作基建。`.gitattributes:5-6` 全仓 LF、唯二 CRLF 例外是 `*.bat/*.cmd`（即两个 Windows 安装脚本）；CODEOWNERS 把审查权交给 @NVIDIA/creative-genai-workflows；bug/feature/task/config 四类 issue 表单。
- **L02 社区治理与合规文档（8 文件）**：CONTRIBUTING/GOVERNANCE/MAINTAINERS/SECURITY/SUPPORT/THIRD-PARTY.txt。THIRD-PARTY.txt 逐条登记安装器自动克隆的外部 custom node 仓及其 Apache/MIT/GPL 混合许可，是商用合规审查入口。
- **L03 入门与排障文档（3 文件）**：README（课程主文档+模块总表）、LINUX_COMFYUI_INSTALLATION（Ubuntu 24.04 九步手工手册）、TROUBLESHOOTING（四节排障，含两处 Blackwell 无解问题）。
- **L04 模型下载与适配工具（4 文件）**：安装器调用的引擎层——`download_models.py`（模型编目/断点检测/gated 门/`--clean`）、`normalize_paths_win.py`（Windows 路径改写）、`patch_flash_attn.py`（Trellis2 补丁）、`tools/mp4_to_gif.py`（旧仓遗留，不可运行）。
- **L05 双平台安装器（3 文件）**：编排层入口 `install.sh` + `install.bat` + `custom_node/__init__.py`（零节点占位包）。
- **L06 图像编辑模块 01-04（16 文件）**：Qwen Image 家族教学主线（提示词增强/图层拆解/定向重绘/全景外扩）。
- **L07 全景与视频模块 05-07（13 文件）**：HDRI 合成（05）与 Wan2.2 视频双模块（06/07）。
- **L08 3D 与材质模块 08+Bonus（12 文件）**：Trellis2 图生 3D（08）+ 纹理提取（Bonus A）+ PBR 材质分解（Bonus B），构成「贴图→材质→3D 资产」收尾链。

## 3. 核心链路

按 14 步导览归并，主数据流是「课程入口 → 治理合规 → 双平台安装 → 模型下载 → 模块链」：

1. **入口与课程脉络**：README 定门槛（RTX 5090/PRO 6000、500GB 磁盘）、给 10+2 模块总表与依赖关系（README.md:16-17、README.md:80），CHANGELOG 交代首版交付范围。
2. **治理与合规**：所有 PR 归 @NVIDIA/creative-genai-workflows 审查、DCO 签核强制；安全漏洞只走 NVIDIA PSIRT；THIRD-PARTY.txt 是外部节点仓许可总账。
3. **Linux 安装链**：九步手册装 ComfyUI 后 `screen` 挂 `main.py --listen`（headless 必须，LINUX_COMFYUI_INSTALLATION.md:63），SSH 隧道转发 8188 端口访问（LINUX_COMFYUI_INSTALLATION.md:72）；`install.sh:27` 起 `set -euo pipefail`，校验 Python≥3.10 与 CUDA PyTorch（不可用则重装 cu128，install.sh:146-150）。
4. **Windows 安装链**：`install.bat:23-29` 注释明示 Desktop App/Portable/Manual 三形态传参约定，`install.bat:131` 起按 `.venv`/`python_embeded`/`main.py` 特征探测定位 Python；Trellis2 wheel 选择、torch 2.8 降级、numpy 2 兼容改写都在此层。
5. **模型下载**：两个安装器殊途同归调 `download_models.py`——`build_module_catalogue()`（download_models.py:170）编目 11 个模块的全部模型，`main()`（download_models.py:1143）分发下载/清理两条路径；`custom_node/__init__.py:16-22` 的空占位包让 ComfyUI 模板浏览器识别本仓。
6. **模块链（教学主线）**：01 Ollama gemma3 提示词增强（workflow JSON:819 的 OllamaGenerateV2 节点、:146 的 gemma3:latest 模型名）→ 02 图层拆解 → 03 掩码定向重绘 → 04 全景外扩 → 05 EV 分档采样合成 32 位 EXR HDRI → 06 VideoPrep 备料后 Wan2.2 I2V 轨迹视频 → 07 Lotus 深度条件 + Wan2.2 VACE 风格化 → 08 Trellis2 图生 3D → Bonus A 纹理提取 → Bonus B PBR 材质分解。
7. **排障收尾**：TROUBLESHOOTING 四节兜底，重点是两处 Blackwell 无解问题（见第 7 节）。

## 4. 关键文件深读

**download_models.py（1244 行，全仓唯一重量级 CLI）**：核心数据结构是 `ModelSpec`（download_models.py:51-67）——repo/文件名/目标子目录/体积，外加 `rename_to` 下载后改名、`full_repo` 整仓下载、`revision` 锁 commit、`requires_agreement` 挂 gated 协议门。`build_module_catalogue()`（download_models.py:170）内建 441 行模块目录，Qwen/Wan2.2/Flux/TRELLIS/Lotus 全家桶以共享常量（如 `LOTUS_VAE`，download_models.py:140-147 已带 `rename_to="LotusVAE.safetensors"`）跨模块复用。`clean_modules()`（download_models.py:816）按 `(dest_subdir, final_filename)` 键做共享感知清理——被其他模块引用的文件自动保留。`main()`（download_models.py:1143）开头就警告单跑此脚本不装节点，并拒绝 `--clean --modules all` 的误操作。

**install.sh（643 行，Linux 编排器）**：`set -euo pipefail` 起手（install.sh:27）；若所选模块全是 Linux 不兼容的 08 则打印原因直接退出（install.sh:74-79）；torch 无 CUDA 时强制重装 cu128 三件套（install.sh:146-150）；组装下载清单时把 08 从 all 中剔除（install.sh:576-579）。

**install.bat（995 行，Windows 编排器）**：三形态探测是它的灵魂——Desktop App 传安装位置（内有 `.venv\`），Portable 传含 `run_nvidia_gpu.bat` 的根，Manual 传含 `main.py` 的 ComfyUI 目录（install.bat:23-29、install.bat:131）。还负责 Trellis2 预编译 wheel 的版本匹配、torch 2.8 降级与 numpy 2 兼容改写。

**patch_flash_attn.py（88 行，Trellis2 上游补丁器）**：上游 `full_attn.py` 在 `BACKEND='flash_attn'` 分支无条件 `import flash_attn`，Windows 无预编译 wheel 必崩。本脚本用精确的 `OLD_BLOCK`→`NEW_BLOCK` 字符串替换（patch_flash_attn.py:18-30）把该分支包进 try/except，缺失时回退 torch sdpa。

**normalize_paths_win.py（82 行）**：把 workflow JSON 里 `"qwen/`、`"flux/`、`"lotus/` 正斜杠前缀改写成 Windows 双反斜杠（`MODEL_PREFIXES` 定义在 normalize_paths_win.py:30，替换逻辑在 :48-49），解决 Linux 生成的相对路径在 Windows ComfyUI 加载不到模型的问题。

## 5. 模块间关系

- **调用链**：install.sh / install.bat（fanOut=14/19 枢纽）统一调 download_models.py（fanOut=30 全仓最大扇出）；模型落盘由 dest_subdir 决定，workflow JSON 写死同名路径引用——**JSON 与编目的一致性是跨模块核心契约**（02/07 勘误源于此）。
- **共享模型**：Qwen 41GB 基座/编码器/VAE 在 01-04/bonus-a 间共享（README.md:97：全装 12 模块共 ~450GB 非逐项之和）；LOTUS_VAE（download_models.py:140-147）以常量复用，`--clean` 据此保护共享文件（download_models.py:816）。
- **产物链**：04 全景是 05 HDRI 前置；06 VideoPrep 为主流程备首末帧/轨迹/遮罩，跳过则 1 秒空跑（workflows/06-image-cut-out-time-to-move/README.md:93）；Bonus A 输出即 Bonus B 输入，与 08 构成「贴图→材质→3D」闭环。
- **对外依赖**：外部 custom node 仓由安装器克隆、许可记于 THIRD-PARTY.txt；gated 模型（05 EV LoRA、08 DINOv3）走 requires_agreement 门。

## 6. 构建与运行

本仓无需构建——「运行」=装进既有 ComfyUI 后在 UI 加载 workflow：

- **Windows**：`install.bat C:\path\to\ComfyUI --modules 02,03`（须 cmd.exe；三形态传参见 install.bat:23-29）。05/08 gated 模型需先在 HF 接受协议并 `hf login`。
- **Linux**：`bash install.sh /path/to/ComfyUI --modules 02,03`（install.sh:21-22）。无头服务器按九步手册：`screen` 挂 `main.py --listen`（LINUX_COMFYUI_INSTALLATION.md:63），SSH 隧道 8188 访问（LINUX_COMFYUI_INSTALLATION.md:72）。
- **补模型/清理**：`python download_models.py <ComfyUI> --modules 04`；`--clean --modules 06` 删独占模型、留共享（README.md:145）。
- **无测试套件**：质量靠文档四件套。Linux 不装 08（install.sh:74-79）；Windows Trellis2 靠 patch_flash_attn.py 打 sdpa 回退补丁（patch_flash_attn.py:18-30）。

## 7. 设计决策与取舍

- **【勘误】01 磁盘口径**：models.md 写 ~29 GB（workflows/01-llm-prompt-enhancer/01-llm-prompt-enhancer-models.md:3），README 表写 ~65 GB（README.md:80），以 download_models.py 实际编目为准。
- **【勘误】02 LoRA 漂移**：models.md 列 8-steps V2.0（workflows/02-image-deconstruction/02-image-deconstruction-models.md:11），JSON 实载 4steps V1.0 bf16（02-image-deconstruction.json:1686），步数版本双漂移，以 JSON 为准。
- **【勘误】07 深度模型 G/D 变体漂移**：models.md 列 lotus-depth-g-v2-1（workflows/07-video-to-video/07-video-to-video-models.md:24），JSON 实载 lotus-depth-d-v-1-1（07-video-to-video.json:659）；另 models.md:25 要求 LotusVAE 手动改名，download_models.py:140-147 已内建 rename_to 自动改——文档滞后于工具。
- **【勘误】bonus-a 容量**：models.md 写 ~29 GB（bonus-a-texture-extraction-models.md:3）vs README ~60 GB；其 models.md:11 同列 8-step LoRA 与 JSON 口径不一。
- **【勘误】TROUBLESHOOTING 旧编号**：Wan2.2 问题写「modules 09–10」（TROUBLESHOOTING.md:39、:50），本仓实为 06/07；tools/mp4_to_gif.py:8 指向不存在的 10-video-to-video 同源（该脚本 :7-8 硬编码作者 OneDrive 路径，旧仓遗留不可运行）。
- **取舍**：①Linux 弃 08 不修 ABI（install.sh:325-329）；②Blackwell 上 08 挂起与 Wan2.2 冻结「无解等上游」（TROUBLESHOOTING.md:47-51）；③零节点占位包换模板浏览器可见性（custom_node/__init__.py:16-22）。

## 8. 新人上路

**先看**：① README 模块总表选组合；② `workflows/<模块>/README.md` 与 `nodes.md`；③ `models.md` 只当参考——**模型以 download_models.py 编目与 JSON 实载为准**（第 7 节五处勘误全在文档侧）。

**再改**：workflow 在 ComfyUI UI 编辑后导出（2 空格缩进、禁提交权重，CONTRIBUTING.md）；改安装器守 install.sh:27 的 set -euo pipefail 约定；提交须 `git commit -s` DCO 签核，PR 归 @NVIDIA/creative-genai-workflows 审查。

**坑**：①跳过 VideoPrep 跑 06 → 1 秒空跑（workflows/06-image-cut-out-time-to-move/README.md:93）；②下拉框空/缺节点弹窗 → 装 custom node 后重启；③gated 模型 403 → 先接受协议再 hf login；④RTX 5090 上 08 挂起、06/07 冻结是已知无解（TROUBLESHOOTING.md:47-51）勿排查；⑤Linux 不支持 08 会被拦（install.sh:74-79）；⑥tools/mp4_to_gif.py 不可运行。
