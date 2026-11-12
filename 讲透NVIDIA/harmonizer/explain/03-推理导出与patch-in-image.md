# 03 · 推理三态、导出部署与 patch-in-image

## 角色定位

覆盖模型之外的"用起来"面：三推理入口（时序演示/部署工具箱/AOT 加载）、`src/onnx_export/` 的 ONNX→TRT 管线与 **patch-in-image** 容器——决定 Harmonizer 能否跑进在线仿真器单 GPU（`README.md:19`）。

## 内部结构

推理三态：① `inference_pix2pix_turbo_harmonizer.py`（159 行）时序推理——逐帧自回归，每帧与前序输出（`--history_idx` 负偏移，`:82`）共同条件化，历史不足回退非时序 V=1 前向（`:133`），`--nontemporal`（`:85`）整体关闭；`save_folder2video` 以 30fps 合 mp4（`:41`）。② `inference_pretrained_model.py`（649 行）部署工具箱：JIT trace 导出（`:230/260`，trace `:254/285`）；unet 走 export+dynamo.compile（`:313/314`）；VAE 走 `torch.compile(backend="torch_tensorrt", mode="max-autotune")`（`:318`）。`_TRT_VERSION`（`:26`，缺省 `(999,0)`，`:28`）：`>=2.9` 才以 `aot_inductor` 导出（`:328-330`）。③ `inference_exported_model.py`（116 行）：`aoti_load_package`（`:24`）加载 `.aoti` 包，`load_tokenizer_jit`（`:14`）配 JIT 版 VAE。

部署线 `src/onnx_export/`：`exportable_modules.py`（269 行）四个固定 shape 包装——VAEEncoder（`:21`）/VAEDecoder（`:49`）/Denoiser（`:86`）/FullModel（`:176`），**双前置校验**：模型须 `inference_only_mode=True` 且 `compute_caching` 已调用（`:229-245`，违者 raise）；`export_onnx.py`（410 行）自插 `sys.path` 支持任意 cwd，shape 固定适配 TRT 并数值校验；`convert_trt.py`（341 行）双路径 trtexec（`:39`，精度旗标 `:70-74`）或 Python API；`inference_trt.py`（575 行）混合后端：denoiser 走 TRT/ORT，VAE tokenizer 留 PyTorch（TorchTokenizer）。

## 外部连接

环境由 `Dockerfile.cosmos` 钉死：基础镜像 `nvcr.io/nvidia/pytorch:25.10-py3`（`:19`），构建期 `RUN patch` 两文件（`:69-70`）——tokenizer.patch 删 `@torch.no_grad()`（hunk `@@ -705,7`/`@@ -718,7`）而非改函数体，text2image_dit.patch（25 行）对齐基库。AOTModule（`...faster_tokenizer.py:186`）与 4D↔5D lambda（`:199-216`）衔接 fast 变体；`utils/profiling.py:53-58` 三态 NVTX 贯穿入口。

## 数据流

部署全链：训练产出 `.pkl` → `inference_pretrained_model.py` 按版本分支导出（JIT/`.pt2`/`.aoti`）→ `inference_exported_model.py` 加载验证 → `export_onnx.py` 出四组件 ONNX+校验 → `convert_trt.py` 出引擎 → `inference_trt.py` 端到端（denoiser=TRT/ORT，VAE=PyTorch）。时序演示是另一条轻路：`.pkl` 直接进 `inference_pix2pix_turbo_harmonizer.py` 逐帧自回归。两条链共享 `FastTokenizer/FastDenoiser` 状态语义（`pipeline.py:84/198`）。

## 设计决策

① **patch-in-image 而非 fork**：两行 `RUN patch`（`Dockerfile.cosmos:69-70`）让基库升级=换镜像 tag，代价是镜像外环境行为不一致——patch 必须随镜像走；② **删装饰器而非重写函数**（tokenizer.patch）：最小侵入打开梯度通道，与 `my_vae_*_fwd` monkey-patch（`src/model/__init__.py:55/71`）双保险；③ **导出双前置强校验**（`exportable_modules.py:229-245`）：缓存未算就导出会得到形状错误的图，宁可构建期 raise；④ **混合后端**（`inference_trt.py`）：VAE 的动态 shape/复杂数值算子不适合 TRT，保留 PyTorch 是务实取舍；⑤ **版本三态探测**（缺省 `(999,0)`）：未知版本按最新语义处理。

## 新人提示

跑评测/导出前先读 `skills/harmonizer/references/evaluation.md:3-18` 两 blocker 自曝（缺 `image_size`+路径错位）。导出前以 `inference_only_mode=True` 构建并调 `compute_caching`（`exportable_modules.py:242`）。AOTModule 不能关键字传参（`...faster_tokenizer.py:421`）。容器外 tokenizer.patch 不自动应用——"本地跑不通"的头号原因。
