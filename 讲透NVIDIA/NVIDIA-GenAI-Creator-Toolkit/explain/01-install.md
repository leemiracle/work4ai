# 01 — install.sh / install.bat：双平台安装器（编排层入口）

> 锚定 commit 29ee60d9 · install.sh 644 行 / install.bat 996 行

## 1. 角色定位

本仓核心资产是 ComfyUI 教学 workflow JSON（GTC 2026 DLI 课程配套）；两个安装器是全仓唯一可执行逻辑主体，把静态 JSON 变成可运行环境：探测环境 → 选模块 → 克隆 custom node 并就地修上游 → 拷贝 workflow → 编排模型下载。`install.sh:27` 以 `set -euo pipefail` 立规矩；`install.bat:19` 首要约束是必须从 cmd.exe 运行，`:42` 先 `chcp 65001` 保证 UTF-8 输出。

## 2. 内部结构

**install.sh**：参数解析 `:33-39` → 只选 Module 08 时早退 `:63-81`（Trellis2 CUDA 扩展 Windows-only）→ venv/conda 四级探测 `:84-110` → Python/ComfyUI 检查 `:113-132` → CUDA torch 缺失则重装 cu128 `:144-153`。核心 `install_node()` `:155-184`：目录已存在则 skip（幂等），clone --depth 1 后装 requirements，失败只 WARN（fail-soft）。交互菜单 `:196-218`（01 ~65 GB / 07 ~143 GB）；模块→包映射 `:278-401`；`--clean` 分支 `:241-275` 转交 download_models.py。

**install.bat**：参数解析 `:58-89` 专门处理 cmd 把逗号当参数分隔符的陷阱（`:76-86` 把碎 token 拼回 MODULES）→ 三形态探测 `:131-252`：Desktop App（`.venv` `:132-145`）、Portable（python_embeded 同层 `:175` 或父层 `:190`）、Manual（main.py `:199`）；`:147-172` catch 误传 `resource\ComfyUI` 源码目录。Module 08 分支 `:484-584` 是 Windows 大工程：torch 2.9+ 降级 2.8.0+cu128（`:504-528`，C++ ABI）、Trellis2 wheel 目录探测 `:539-552`、DINOv3 transformers 补丁 `:578`、flash_attn sdpa 回退 `:583`。`:install_node` 子程序 `:961-995` 与 shell 函数对等。

## 3. 外部连接

编排 hub 扇出：调 `download_models.py`（install.sh:255/593、install.bat:387/887）；仅 install.bat 调 `normalize_paths_win.py` `:771`（JSON 里 qwen//flux//lotus/ 前缀改双反斜杠）与 `patch_flash_attn.py` `:583`；拷贝 `custom_node/__init__.py` `:446` 生成零节点占位包供模板浏览器识别。

## 4. 数据流

CLI 参数（路径+`--modules`+`--clean`）→ 环境探测 → 模块选择 → 克隆并手术上游 → 拷贝 workflow JSON/样例输入/模板扩展 → 写 `Comfy.TutorialCompleted=False`（install.sh:477）→ Module 01 交互装 Ollama+gemma3（install.sh:497）→ HF 登录 → download_models.py 下载，非零退出触发重试指引（install.sh:595）。

## 5. 设计决策

- **上游依赖就地手术**：sed 删 comfyui-sam2 的 numpy<2 pin（install.sh:342）、Impact-Pack 的 `git+…/sam2` 换 PyPI 免源码编译（`:351`）、Marigold `.tostring()`→`.tobytes()`（`:318`）、triton 钉版；平台连包名都不同：Linux `triton==3.2.0`（`:362`）vs Windows `triton-windows==3.2.0.post21`（install.bat:618）。
- **勘误①（gated 口径自相矛盾）**：install.bat:849 正确列 gated 为 "Module 05 Flux.1-dev, Module 08 DINOv3"，但同文件 `:871/:878` 写 "(Module 07, 08)"；install.sh `:543` 说 05、`:561` 说 07。download_models.py 的 `requires_agreement` 仅 Flux VAE 与 DINOv3 两处，"07" 系复制粘贴笔误。
- **勘误②**：install.bat:296 注释把 Luminance-Stack-Processor 标 "(module 07)"，实际在 Module 05 分支（install.bat:474）。
- **勘误③**：两脚本 `:17` 自称旧仓名 `comfyui-generative-ai-workflows`。
- **Module 08 双向不对称**：Linux 三处硬编码跳过（早退 `:63-81`、workflow 拷贝 `:410`、下载排除 `:578-581`），Windows 反而是最重分支——Trellis2 wheel 只对 Windows+特定 torch 存在。

## 6. 新人提示

改包清单须同步 nodes.md/models.md（PR 模板 Checklist 要求，Module 01 已栽过，见 03 篇）。新增 Windows-only 模块要复刻 Module 08 的三处 Linux 跳过。批处理变量全全局：NODES_DIR 在 Desktop 分支 `:357` 被重写。fail-soft 意味着"安装完成"≠"requirements 全成功"；sed/patch 匹配失败会静默跳过，升级上游要重验补丁。
