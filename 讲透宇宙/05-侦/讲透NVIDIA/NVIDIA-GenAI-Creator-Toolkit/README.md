# 讲透 NVIDIA NVIDIA-GenAI-Creator-Toolkit

> 源码仓：`/usr-data/data2/repos/agent-repos/NVIDIA/NVIDIA-GenAI-Creator-Toolkit` @ commit `29ee60d9`
> 知识图谱：仓内 `.understand-anything/knowledge-graph.json`

## 全链状态表

| 阶段 | 状态 | 产物 |
|---|---|---|
| 批分析（13 批/66 文件） | ✅ 13/13 | 终验 0 issues；docs 型仓（41 md + 11 workflow JSON），无 import 语义，手扫补 40+ 条安装器/工作流运行时依赖边 |
| understand 图谱 | ✅ 完成 | **89 节点 / 171 边 / 8 层 / 14 步导览**，validator **0 issues 0 warnings**，fingerprints 基线 **66 文件 @ 29ee60d9** |
| Onboarding | ✅ 完成 | `onboarding/ONBOARDING.md`（8 节 / 7227 不计空格字符 / 57 锚 / 5 勘误；1308 团灭后两次复活续写） |
| explain 精讲 | ✅ 3/3 | `explain/01-03`，六节结构、111 锚（30+17+抽验全中） |

## explain 索引（3 篇）

| # | 篇目 | 主题 | 字数（不计空格）/锚 |
|---|---|---|---|
| 01 | install | install.sh/install.bat 双平台安装器全解 | 2496 / 49 |
| 02 | download_models | 模型下载器（实际位于**仓根**，非 tools/——任务书路径勘误） | 2494 / 34 |
| 03 | workflow-module | Module 01 ComfyUI 工作流结构 + 三包依赖甄别 | 2499 / 28 |

## 勘误与甄别（源码一手核实）

1. **models.md 容量口径系统性矛盾**：01 头部 "~29 GB" 与自身表格合计（~59 GB）、README/install.sh 口径（~65 GB）三方矛盾（疑早期草稿残留）；bonus-a 宣称 ~29GB vs README ~60GB 同病。
2. **Module 02 模型漂移**：models.md 表列 Lightning-8steps-V2.0 + bf16 编码器，workflow JSON/README 实为 Edit-2511-Lightning-4steps + fp8_scaled；"Total storage ~21.5GB" 与表合计 ~58.8GB 矛盾。
3. **Module 07 Lotus 版本矛盾**：models.md 写 lotus-depth-g-v2-1-disparity-fp16，README 表与 JSON 实际加载 lotus-depth-d-v-1-1-fp16（以 JSON 为准）。
4. **节点包清单各漏一个**：01 的 README 列 Easy-Use+ollama、nodes.md 列 WJNodes+ollama——JSON 实需三包（easy showAnything + RegexExtract + Ollama），install.sh 实装三包；04/05/bonus-b 同病（5 vs 4 包、4 vs 3 包、4 vs 6 包）。
5. **Object Remover 出处错引**：04 的 models.md 称 "reused from Module 03"，03 清单/JSON 均无此 LoRA。
6. **旧编号体系残留**：06 的 nodes.md 引用 09-cutout-animation-to-video*.json（实际已改名 06-*）；TROUBLESHOOTING 旧编号 + Blackwell 无解条目滞后。
7. **tools/mp4_to_gif.py 硬编码作者个人 OneDrive 路径**，DST 指向不存在的 workflows/10-video-to-video/（旧仓遗留，不可运行）。
8. **custom_node/ 是零节点占位包**（仅注册 example_workflows/ 模板目录）。
9. **06 videoprep JSON 内嵌 2509/2511 两代 Qwen Lightning 下载 URL**，loader 实走 2511；06 主工作流硬依赖 videoprep（跳过会 1 秒空跑）。

## 一句话

ComfyUI 生成式 AI 教学工作流集合（01-08 模块 + 2 bonus）：双平台安装器 + HF 模型下载线 + 每模块四件套（JSON/README/models.md/nodes.md）——**文档口径与 workflow JSON 的漂移是本仓最大陷阱，一切以 JSON 为准**。
