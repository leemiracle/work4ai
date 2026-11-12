# 02 — download_models.py：HF 模型下载引擎（编目/校验/共享感知清理）

> 仓根 1244 行 · 全仓唯一重量级 CLI（勘误：任务书曾记 tools/ 下，tools/ 实际只有 mp4_to_gif.py）

## 1. 角色定位

两个安装器共用的引擎层：install.sh:255/593 与 install.bat:387/887 只是把 `--comfyui/--modules/--clean` 透传给它。职责三件事——为 11 个模块键编目模型、带校验的断点感知下载、共享感知清理。依赖极简：标准库 + huggingface_hub（`:38-43` 硬守卫，缺包 exit 1）。

## 2. 内部结构

- **数据模型**：`ModelSpec`（`:50-66`）9 字段——filename 可含仓库子目录、dest_subdir 相对 ComfyUI 根、rename_to 落盘改名、full_repo 整仓、revision 钉 commit、requires_agreement 门控 URL；`ModuleSpec`（`:69-76`）带 skip 预留位。
- **共享常量**（`:83-163`）：QWEN_EDIT_DIFFUSION 等 10 个跨模块条目（Qwen Edit 2511 栈被 03/04/bonus-a/b 复用）。
- **编目**：`build_module_catalogue()`（`:170-610`，441 行），键 "01"…"08"/bonus-a/b；仅 Module 06 Pusa LoRA（`:392`）与 Module 07 Lightning LoRA（`:505`）钉 revision。
- **下载**：`hf_download_file()`（`:627-665`）3 次重试+5s×n 退避，下载后把 HF 仓库目录结构拍平（`:650-654`）；`download_model()`（`:719-809`）三级存在性检查——<1KB 判残缺重下（`:36`）、与 HF 元数据大小不符重下（`:617`）、一致则 skip；`:768-774` 识别未改名 pre-rename 文件；`:790-807` rename 时 rglob 兜底。
- **清理**：`clean_modules()`（`:816-928`）以落盘位置建 `model_key` 集合，属其他模块的键标 SHARED 保留；preview 后要求输入 yes。
- **辅助**：`_detect_ollama()`（`:935-970`）PATH 失败退回 Windows LOCALAPPDATA 路径；`run_module()`（`:977-1060`）模块内按 (repo,filename) 去重、失败即 break（`:1024`）、Ollama notes 先探测是否已满足。

## 3. 外部连接

上游被两个安装器四处调用；下游靠 huggingface_hub（hf_hub_download/snapshot_download/get_token/get_hf_file_metadata）；subprocess 调 ollama 探测 gemma3。落盘子目录与文件名就是各 workflow JSON loader widget 的取值——catalogue、JSON、models.md 三处必须一致；rename_to 把 HF 长名改成 JSON 短名（LotusVAE.safetensors `:146`）。

## 4. 数据流

`--clean`+all 拒绝（`:1161-1165`，防一键全删）→ `parse_modules`（`:1070-1088`，单数字 zfill 补零）→ 逐模块逐模型：agreement 门（`:724-738`，等用户点完 Agree 按 Y）→ 三级检查 → 下载/拍平/改名 → 汇总四桶 downloaded/skipped/failed/manual；任一 failed 则 exit 1。

## 5. 设计决策

- **大小校验用 HF 元数据而非本地 hash**："断点"语义 = 已存在且大小对则跳过，不对则删掉重下（配合 hf_hub_download 内建 resume）。
- **model_key 按落盘位置而非 repo URL 去重**（`:824-831` 注释明说）：Module 02 文本编码器取自 HunyuanVideo_1.5_repackaged（`:220/:227`）而 Module 01 取自 Qwen-Image_ComfyUI（`:93`），同文件名不同 repo，清理不互删。
- **勘误①（任务书指定口径矛盾）**：Module 01 models.md 头部 "Total storage: ~29 GB"，但 `:186-203` 编目加总≈59.3 GB、加 gemma3 ~5 GB≈64 GB——与模块 README、install 菜单（均 ~65 GB）一致，29 GB 是孤立错数；同文件 VRAM "12–16 GB" 也与 README "Win 24/Linux 32 GB" 打架。
- **勘误②**：Module 04 models.md 称 Object Remover "reused from Module 03"，但 `:270-276` 显示它是 04 专属条目，Module 03（`:250-259`）没有该 LoRA。
- **skip 是死字段**：`:74` 的 skip 全 catalogue 从未置 True；`:985` 注释举例 "Module 01 / Ollama" 不会发生（Module 01 照常下载）。
- **fail-fast 只到模块级**：单模块失败 break，后续模块照跑（`:1198-1200`）。

## 6. 新人提示

新增模型三处同步：catalogue 条目、JSON loader 值、models.md（PR 模板 Checklist 要求）。改 rename_to 会破坏老用户 --clean 精确性（model_key 以改名后文件名计算）。full_repo 条目不做存在性检查，重跑靠 snapshot_download 内部增量。agreement 门无人值守时会因 input() 抛 EOFError 走 skip（`:734-735`），CI 化需预登录+预接受协议。
