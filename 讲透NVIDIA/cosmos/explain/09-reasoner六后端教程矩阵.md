# 09 · Reasoner 六后端教程矩阵与孤儿 SGLang notebook

## ① 角色定位

`cookbooks/cosmos3/reasoner/` 是 Cosmos3-Reasoner（图像/视频视觉语言推理）的教程面：**同一模型、同一批示例任务，六本 notebook 分别演示六种推理栈**——Cosmos Framework、vLLM、SGLang、TensorRT-LLM、Transformers、NIM。六本的示例目录几乎一致（Image/Video Caption → Temporal Localization → Embodied Reasoning → Common Sense → 2D Grounding → Describe Anything → Action CoT → Physical Plausibility → Situation Understanding），差异只在模型怎么被服务起来。配套 `reasoner_prompt_guide.md`（675 行）是提示词手册，`finetune/` 是 SFT 配方（第 11 篇）。

README 开篇给硬数据：Cosmos3 是**统一 omni checkpoint**（Reasoner+生成器一体），Cosmos Framework 后端即使只做文本推理也加载全套权重（video VAE、audio tokenizer、diffusion expert），Cosmos3-Nano 单卡约 **34 GB**；vLLM/TRT-LLM/Transformers/NIM 只加载 Reasoner 塔，约 **16-17 GB**，差近一半。

## ② 内部结构

**六本 notebook 矩阵**（cell 数实测）：

| notebook | cells | 服务方式 | 模型档位 | 关键特征 |
|---|---|---|---|---|
| run_with_vllm.ipynb | 53 | vLLM server，宿主 8001 | Edge/Super（默认 Super） | 视频示例全在此本；`file://` URI 直传本地媒体 |
| run_with_sglang.ipynb | 53 | Docker `lmsysorg/sglang:dev` | Edge(tp1)/Super(tp4) | **全仓 README 零收录**（见⑥） |
| run_with_tensorrt_llm.ipynb | 52 | TRT-LLM server，宿主 8001 | Nano/Super | 预构建容器或源码安装两条路 |
| run_with_transformers.ipynb | 20 | 进程内，无 server | Nano/Super/Edge | 独立 venv（Transformers main，Python 3.13 kernel） |
| run_with_nim.ipynb | 46 | `nvcr.io/nim/nvidia/cosmos3-reasoner` 容器 | nano/super | 本地资产转 base64 data URI；`media_io_kwargs` 控帧采样 |
| run_with_cosmos_framework.ipynb | 53 | `cosmos_framework.scripts.inference` | Nano/Super/Edge | 全 omni 权重；当前 reasoner 路径只吃 `vision_path` 图像 |

公共骨架：Setup（仓根定位+资产断言）→ Launch server（多档位任选一 cell）→ Wait for readiness → Query examples（渲染 prompt+媒体+输出+框/轨迹）→ Shutdown。

**SGLang notebook 细节**（孤儿但实现完整）：cell 8 Edge 启动——`docker run --runtime nvidia --gpus '"device=0"' -p 8001:8000 lmsysorg/sglang:dev sglang serve --model-type llm --model-path nvidia/Cosmos3-Edge --tp-size 1 --enable-multimodal`；cell 10 Super 版（`--gpus all --tp-size 4`）；HF 缓存挂独立目录并 chmod 777（容器内用户可写）；cell 12 就绪等待最多 1800×2 秒，`docker logs -f` 流式跟踪、容器早退即报错；收尾 cell 52 `docker rm -f cosmos3-reasoner-sglang`。查询侧与 vLLM 同构：`openai.OpenAI(api_key="EMPTY", base_url="http://localhost:8001/v1")` + `MODEL = client.models.list().data[0].id` 动态解析。

**reasoner_prompt_guide.md 推理设置节**：:8-24 两套采样参数——无推理 `top_p=0.8/presence_penalty=1.5/temperature=0.7`，带推理 `top_p=0.95/temperature=0.6/presence_penalty=0.0`；:41-57 **推理开关在用户 prompt 里**——要 `<think>...</think>` 就追加格式指令，不要就省略，无独立参数；:59-75 payload 里**媒体永远在文本前**；:77 起 2D 框/点/轨迹用 **0-1000 归一化坐标**、原点左上；:101 起 13 大类任务逐例 prompt 全文，与六本 notebook 示例对应。

## ③ 外部连接

- **环境安装中枢**：`cookbooks/cosmos3/README.md`（共享指南）设八节——Cosmos Framework/Diffusers/TensorRT-LLM Generator/TensorRT-LLM Reasoner/Transformers/vLLM/vLLM-Omni/NIM；reasoner README 每节链接回对应小节，不在本目录重复安装步骤。
- **模型资产**：HF gated repo（`nvidia/Cosmos3-{Nano,Super,Edge}`），NIM 路线换 NGC 容器（`nvcr.io/nim/nvidia/cosmos3-reasoner`，NGC_API_KEY 鉴权）；`build.nvidia.com/nvidia/cosmos3-nano-reasoner` 是零安装浏览器入口。
- **评测闭环**：教程的输出约定（2D grounding 的 0-1000 坐标、SOT 轨迹）与 vlmevalkit 里 VANTAGE_2DGrounding/VANTAGE_SOT 基准 schema 对应——教程与评测共用同一套输出约定（见 07 篇 `models/cosmos.json` 的 SOT json_schema）。
- **根 README 导流**：L84"10 分钟路径"直链 `run_with_vllm.ipynb`；L167 后端清单明写含 SGLang。

## ④ 数据流

以最完整的 vLLM 路线为例：setup cell 用 `git rev-parse --show-toplevel` 定位仓根并断言 `reasoner/assets` 存在 → 按共享指南启动 server（Super 默认 8001，`--allowed-local-media-path` 必须覆盖 `cookbooks/cosmos3` 才能 `file://` 直读本地媒体）→ 每个 example cell 组 `messages`（system="You are a helpful assistant." + 媒体块 + 任务文本）→ `chat.completions.create(model=动态解析, max_tokens=4096, seed=0)` → 2D grounding/轨迹类再把输出 JSON 框/轨迹画回媒体。NIM 路线把 `file://` 换 base64 data URI（容器看不见宿主文件系统）、帧采样换 `extra_body.media_io_kwargs`；Transformers 路线无 server，`apply_chat_template(tokenize=True)` 直出 tensor 进 `model.generate`。六条路线 prompt 层完全复用 prompt_guide 约定——"换后端只改启动 cell"的根据。

## ⑤ 设计决策

1. **示例矩阵而非单本通吃**：13 类任务 × 6 后端全组合不可维护；实际是每本独立完整但示例目录对齐，按后端挑一本即获全部任务模式。
2. **模型名动态解析**（`client.models.list().data[0].id`）：server 型 notebook 不硬编码 served-model-id，换档位只改启动命令——消掉"模型名漂移"这类最常见新手故障。
3. **就绪等待内建**：SGLang/TRT-LLM notebook 都带 health 轮询（含容器早退检测）——大模型 server 启动常超 10 分钟，裸跑下一 cell 必然连接失败。
4. **显存分层文档化**：34GB vs 16-17GB 对比表把"选后端"变成显存预算问题。
5. **Docker 隔离用于最脆后端**：SGLang 用预构建镜像，避免其对 CUDA/driver 版本的敏感性进入用户环境——与评测线"评测器独立 venv"（08 篇）同一哲学。

## ⑥ 新人提示（坑与勘误）

1. **"孤儿 SGLang notebook"勘误的准确口径**：受托核对的说法实际是**六本**孤儿，不止 reasoner 一本——全仓 README 的 ipynb 引用统计显示 SGLang 系（reasoner/run_with_sglang、audiovisual/run_with_sglang、transfer/run_video_transfer_with_sglang、action/run_{fd,id,policy}_with_sglang 共 6 本）**零引用**；共享环境指南无 SGLang 小节；reasoner README 后端章节只有 5 节；但根 README:167 又宣称"Cosmos 3 runs on ... SGLang ..."。结论：notebook 是完整可跑的正式教程（53 cell 含启停/就绪/全示例），不是草稿；缺的只是文档入口，走 SGLang 只能直接打开这六个文件。
2. **`enable_sound: false` 不是可选项**：Cosmos Framework 的 reasoner 输入 spec 里该字段必须显式 false——框架严格校验会拒绝而非忽略音频请求。
3. **视频示例别在 Cosmos Framework notebook 里找**：当前 Framework reasoner 路径只吃图像（`vision_path`），视频示例全在 vLLM notebook——README 明说这是实现限制非设计偏好。
4. **Transformers 的 Edge 是不同类**：Nano/Super 用 `Cosmos3OmniForConditionalGeneration`，Edge 用 `AutoModelForImageTextToText`，且需 Transformers main 分支——pip 稳定版会 import 失败。
5. **端口约定易混**：vLLM 默认 Super 8001、TRT-LLM 固定 8001、SGLang 容器内 8000 映射宿主 8001。同机混跑两后端必撞端口，换端口要同时改启动 cell 和 client `base_url`。
6. **prompt_guide 的 reasoning 开关是纯文本约定**：不追加 `<think>` 格式指令就按直答走；两套采样参数（presence_penalty 1.5 vs 0.0）须随开关切换，只改 prompt 不改参数会次优。
