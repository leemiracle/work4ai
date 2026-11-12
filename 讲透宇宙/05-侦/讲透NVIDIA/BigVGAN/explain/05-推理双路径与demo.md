# 05 · 推理双路径 + gradio demo

## 角色定位

仓内有三条推理通道：`inference.py`（wav→mel→波形）、`inference_e2e.py`（mel.npy→波形，跳过 mel 计算）、`demo/app.py`（HF Spaces 部署的 gradio 交互演示）。前两者是"同一件事的两种输入约定"，第三者是门面。它们都不训练、共享 bigvgan.py 的 BigVGAN 与 meldataset 的 mel 标准。

## 内部结构

**inference.py（89 行）**：`inference(a, h)`（inference.py:23-55）用 **utils.load_checkpoint**（inference.py:11/26）加载 `--checkpoint_file`，`remove_weight_norm()`（inference.py:34）后逐文件处理：`librosa.load(sr=h.sampling_rate, mono=True)`（inference.py:38-40）→ `get_mel_spectrogram`（inference.py:43，实现在 meldataset.py:123）→ 生成 → `*MAX_WAV_VALUE` 转 int16 写 wav（inference.py:48-54）。config.json 约定与 checkpoint 同目录（inference.py:69）。

**inference_e2e.py（102 行）**：结构孪生但**自带本地 `load_checkpoint`/`scan_checkpoint` 副本**（inference_e2e.py:22-35）而不复用 utils.py——形成第二条平行加载路径；输入是 `--input_mels_dir` 的 .npy（`[1,C,T]` 或 `[C,T]` 自动补维，inference_e2e.py:53-56），输出后缀 `_generated_e2e.wav`（inference_e2e.py:64-66）。

**demo/app.py（441 行）**：`import spaces`（app.py:4）即 HF Spaces 专有依赖；启动即**预载全部 9 个模型**（LIST_MODEL_ID，app.py:225-235；循环 from_pretrained+去 weight_norm+eval，app.py:240-247）；`inference_gradio`（app.py:31-57）做重采样/单声道化/音量归一化×0.95（app.py:38-42）后调 `inference_model`；后者挂 `@spaces.GPU(duration=120)` 装饰器（app.py:60），推理完 `model.to("cpu")` 释放显存（app.py:79）；9 个示例 wav 绑定对应采样率模型（app.py:328-370），模型规格表由 pandas 转 HTML（app.py:373-438）。

## 外部连接

两 CLI 依赖 bigvgan/inference 入口的 `--use_cuda_kernel` 开关（inference.py:65、inference_e2e.py:78）直通 BigVGAN 构造；demo 依赖根目录 sys.path 注入（app.py:12-13）与 demo/requirements.txt 的 gradio+spaces 两行（比根 requirements 恰好多这两项）。scipy.io.wavfile.write 是三处共同的落盘通道。

## 数据流

wav 路径：输入 wav→重采样到模型 sr→mel（fmax 等按 config）→G→int16 wav。e2e 路径：外部预计算好的 mel .npy→G→wav，**责任前移**——STFT 超参必须与 config.json 完全一致（README.md:135 明示）。demo 路径：浏览器音频→int16/32767 归一（app.py:34）→同 wav 路径→(sr, audio) 元组+生成谱图返回（app.py:50-57）。

## 设计决策

① 双 CLI 分离是给 TTS 上游用的：上游模型（如 TTS）自己产 mel 时用 e2e 免二次变换；② e2e 复制而非复用 utils 是"零耦合单文件脚本"取向，代价是双份维护（见勘误 #4）；③ demo 预载 9 模型牺牲启动时间换切换零延迟——Spaces 冷启动慢但交互即时；④ `@spaces.GPU` 显式申请 120s 是 ZeroGPU 配额协议。

## 新人提示

checkpoint 给 `g_*` 步数文件或 `bigvgan_generator.pt`（HF 下载后改名）皆可；加载后必做 `remove_weight_norm()`（inference.py:34、app.py:243）否则速度与权重不匹配。自己算 mel 喂 e2e 时对齐 `n_fft/win_size/fmin/fmax/hop_size` 五参数，mel 是 log 域（meldataset.py:118 spectral_normalize）。demo 本地跑：`pip install -r demo/requirements.txt` 后 `python demo/app.py`。
