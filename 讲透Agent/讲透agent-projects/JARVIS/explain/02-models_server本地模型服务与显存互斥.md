# 02 · models_server.py：本地专家模型服务与显存互斥

## 一、角色定位

`hugginggpt/server/models_server.py`（635 行）是 HuggingGPT 的"手"：控制器 awesome_chat 只负责决策，所有模态的本地推理都由这个 Flask 服务承载。它在 8005 端口暴露三个端点——`/running`（存活探针，`models_server.py:350`）、`/status/<path:model_id>`（模型是否已加载，`:354`）、`/models/<path:model_id>`（POST 推理，`:364`）。awesome_chat 启动时就会打 `/running` 验活（`awesome_chat.py:126`），选型时打 `/status`（`awesome_chat.py:693`），执行时打 `/models`（`awesome_chat.py:533`）。它把"数十个 transformers/diffusers 管线塞进一张卡"这个看似矛盾的需求，用最朴素的锁+搬运解决了。

## 二、内部结构

**load_pipes 预加载（`models_server.py:81-341`）**：按 `local_deployment` 三档装配字典 `pipes`——`full` 档（`:85-177`）加载 caption/文生视频/DCCRNet 降噪/espnet TTS/SD 变体/speecht5_vc/maskformer/dpt-midas 等重模型；`standard` 档（`:179-269`）加载 whisper/speecht5_asr/dpt-large/detr 系列/owlvit/vilt/layoutlm 等 `transformers.pipeline` 一行式管线；`minimal` 档起（`:271-339`）必有 ControlNet 全家——7 个 control 权重（canny/depth/hed/mlsd/openpose/scribble/seg）+ 检测器（OpenposeDetector/MLSDdetector/HEDdetector/MidasDetector/CannyDetector）共享一个 `StableDiffusionControlNetPipeline`（`:272-275`）。注意大量被注释掉的模型（如 blip-large、trocr 两种、gpt2）是历史裁剪痕迹；`/status` 里还硬编码了 trocr 双模型禁用名单（`:356`），虽然它们从未被加载——防御性写法。`pipes = load_pipes(...)` 在**模块导入时**执行（`:343`），所以启动此服务即进入分钟级权重加载，打完 `[ ready ] {during}s`（`:348`）才可用。

**推理分支墙（`:384-597`）**：`/models/<id>` 是一条按 model_id 逐个 if 的长通道——text-to-video 先换 DPMSolverMultistep 调度器再 50 步采样 40 帧，用 `os.system` 调 ffmpeg 转 h264（`:386-394`）；sd-controlnet 分支先 `pipe.controlnet.to('cpu')` 换入目标 control 权重再换 UniPC 调度器出图（`:397-406`）；`-control` 结尾的检测器直接产控制图（`:408-418`）；其余 caption/VQA/DQA/深度/分割/TTS/ASR/增强各占一段。产物统一落 `public/images|audios|videos/`，返回 `{"path": "/images/xxxx.png"}` 由 awesome_chat 改写成 `generated image` 字段（`awesome_chat.py:546`）。

## 三、外部连接

上游唯一消费者是 awesome_chat 的 `local_model_inference`（`awesome_chat.py:532`），请求体仅三种形态：`{"img_url"}`、`{"text"}`、`{"audio_url"}`（外加 controlnet 的 `img_url+text`）。权重来自 `hugginggpt/server/models/download.sh:5-38` 预下载到 `models/` 本地目录（`local_fold = "models"`，`models_server.py:76`），不走网络。Docker 形态（`hugginggpt/Dockerfile.jetson:26-28`）把 models 目录设计为 volume 挂载而非打入镜像。config 复用 awesome_chat 同款 YAML（`:46-57` 读 `local_inference_endpoint.port` 与 `device`，`:63` 默认 cuda:0）。

## 四、数据流

一次 POST `/models/lllyasviel/sd-controlnet-canny` 的完整时序：①自旋等锁——`while "using" in pipes[model_id] and pipes[model_id]["using"]: time.sleep(0.1)`（`models_server.py:366-368`）串行化同模型并发；②置 `using=True` 后把管线 `.to(device)` 上卡（`:369-381`，异常时退 `pipe.model.to` 双层兜底）；③走 controlnet 分支换权重推理出图（`:397-406`）；④**用完即弃**——`pipe.to("cpu") + torch.cuda.empty_cache()`（`:604-607`）立刻腾空显存；⑤`using=False` 解锁（`:613`）返回 JSON。同一个 SD 管线被 7 个 controlnet 条目共享（`:304-338`），换 control 权重而非换整管，省下 7 份 SD 主干显存。所有分支包在同一个 try/except 里（`:384`/`:599`），异常统一返回 `{"error": ...}`（`:602`），`result is None` 时兜底 "model not found"（`:615-616`）。

## 五、设计决策

1. **using 自旋锁+CPU 驱逐**：单卡放不下全部模型，就用"上卡推理→驱逐回 CPU"的乒乓策略（NOTES-DIGEST 甄别）：同一时刻每模型仅一份在卡，推理间互不挤占。代价是每次推理多两次 H2D/D2H 拷贝——正确性优先的取舍。
2. **`.to()` 失败的鸭子类型兜底**（`:376-381`/`:604-611`）：不同管线对 `.to` 支持不一，except 分支直接改 `pipe.device` 属性再搬子模型——糙但兼容 espnet/asteroid 等非标准对象。
3. **model_id 大 if 墙**而非策略模式：每模型的前后处理差异大（video 要 ffmpeg、detection 要画框、segmentation 要调色 paste），表驱动抽象成本高于收益；代价是加模型必改此文件。
4. **已知缺陷**：`models_server.py:504` `model_id == "Intel/dpt-hybrid-midas" and model_id == "Intel/dpt-large"` 恒假（一个值不可能等于两个不同字符串），dpt-hybrid-midas 的精细深度图分支永不执行，full 模式下该模型实际只能走 `:497-502` 的 dpt-large pipeline 版；detr-resnet-50-panoptic 分支（`:570-586`）`colors` 列表用 `for i in range` 生成后，`:579` 的 `for segment in segments` 循环里 `:582` 的 `colors[i]` 不再递增——全部分割块染同一颜色。
5. **ffmpeg 用 os.system**（`:393`）而非 subprocess：shell 注入面小（uuid 文件名）但属于历史仓常见粗放写法。

## 六、新人提示

排查"模型不可用"先打 `/status/<id>`：full/standard 档之外的一切 id 都返回 `loaded: False`（`:354-362`），awesome_chat 就会转 HF 远程。想省显存先降档：minimal 只装 ControlNet（README 建议 RAM>12GB），standard 加常用管线（>16GB），full 全量（>42GB，`hugginggpt/README.md:200-202`）。看启动耗时与每个请求的 `[ inference ]`/`[ complete ] {during}s` 日志（`:370/:620`）即可定位瓶颈。改此文件勿忘：分支必须给 `result` 赋值且文件名用 `uuid4()[:4]`（正确写法见 `:392`，对照 `run_gradio_demo.py:59` 的错误写法）。
