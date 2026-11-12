# 05 · CosmosReason 双后端：api/cosmos_reason.py 与 vlm/cosmos_reason_hf.py

## 一、角色定位

Cosmos-Reason 是 NVIDIA 的物理世界推理模型线，本 fork 为它准备了两套接入：`vlmeval/api/cosmos_reason.py`（774 行，OpenAI 兼容 HTTP 端点版，vLLM 服务化，fork 改动最重文件）与 `vlmeval/vlm/cosmos_reason_hf.py`（481 行，进程内 transformers 版），另有精简版 `vlm/cosmos.py`。血统演化出两代（Reason1 基于 Qwen2.5-VL、Reason2 基于 Qwen3-VL）与 Think 变体共 6 类。API 版是生产主力——api_models 组的 qwen3_30b_a3b 等 4 个名字全部经由它指向 Lepton 端点（config.py:149-178）；HF 版是"无 API key 本地跑"的镜像，共享视频语义但实现独立。

## 二、内部结构

**API 版 CosmosReason(BaseAPI)**（api/cosmos_reason.py:234）：

- *视频预处理三件套*：`tensor_video_to_base64`（api/cosmos_reason.py:63-127）把 (T,C,H,W) 张量经 **ffmpeg 子进程管道**编码 H.264 fragmented MP4 再 base64——crf 默认 0（近无损），注释实证压缩伪影改变判分：tailgating f1 从 0.74 掉到 0.7（api/cosmos_reason.py:66）。`process_video_info_to_video_url`（api/cosmos_reason.py:130-194）用 qwen_vl_utils 抽帧后编码，带磁盘缓存（utils/video_cache.py:312），并做 vLLM 兼容归一化——fps 标量化、剔除 do_resize（api/cosmos_reason.py:183-189）。`_process_video_with_timeout`（api/cosmos_reason.py:197-231）daemon 线程+join 硬超时——decord 在 NFS 上读非 faststart MP4 无限阻塞且 SIGALRM 救不了（api/cosmos_reason.py:204-208）。
- *构造器*（api/cosmos_reason.py:249-322）：key 取 `COSMOS_API_KEY`（api/cosmos_reason.py:280）；吸收 use_nim/response_format/extra_body/image_patch_size 扩展参数（api/cosmos_reason.py:295-301）；建完即做端点健康检查（api/cosmos_reason.py:319）与**模型名自动解析**（GET `/v1/models`，api/cosmos_reason.py:324-365）。
- *prompt 策略*（api/cosmos_reason.py:383-412）：`use_custom_prompt` 对 MCQ 返回 False——自家"只答字母"指令**抑制推理链致 MMMU 掉分**，退回标准 prompt（api/cosmos_reason.py:387-391）；IFBench 同理（api/cosmos_reason.py:407-411）。`build_prompt` 输出**图在前文在后**（api/cosmos_reason.py:450-452）。
- *generate_inner*（api/cosmos_reason.py:536-665）：视频失败返回哨兵 `'VIDEO_LOAD_FAILED'` 而非 fail_msg，**故意绕开 BaseAPI 重试**（api/cosmos_reason.py:540-543）；NIM 部署走 nvext 分支（api/cosmos_reason.py:590-595）；401/429/500 逐码日志（api/cosmos_reason.py:619-637）；`finish_reason != 'stop'` 标记 truncated 但保留内容（api/cosmos_reason.py:648-660）。generate 覆写按 `INFERENCE_STATS_FILE` 记 JSONL outcome（api/cosmos_reason.py:667-686）。
- *代际家族*：CosmosReason1（patch=14，`<think>/<answer>` 双标签解析，api/cosmos_reason.py:689-701）/CosmosReason1Think（system prompt 注入输出协议，api/cosmos_reason.py:703-725）/CosmosReason2（patch=16，只剥 think 段，api/cosmos_reason.py:727-739）/CosmosReason2Think（user 消息追加 think 指令，api/cosmos_reason.py:742-764）/Qwen3VLThink（首 `<think>` token 被模板嵌入不现于回复，api/cosmos_reason.py:766-774）。

**HF 版 CosmosReasonHF(BaseModel)**（vlm/cosmos_reason_hf.py:15）：默认参数抄自 cosmos-reason1 官方 video_critic 示例（vlm/cosmos_reason_hf.py:50-51）——fps=16、total_pixels=8192×28×28、patch_size=14。构造器双路（vlm/cosmos_reason_hf.py:103-153）：vLLM `enforce_eager=True`+seed=1；transformers `AutoModelForImageTextToText`+bf16（vlm/cosmos_reason_hf.py:142-147）。`generate_inner`（vlm/cosmos_reason_hf.py:193-347）：消息解析（system/video/image/text 分离，vlm/cosmos_reason_hf.py:220-229）→ apply_chat_template → process_vision_info（显式传 patch size，vlm/cosmos_reason_hf.py:279-283）→ 双后端分岔（vLLM L285-305 / transformers L307-345，后者手剥输入 token 段再 decode）。

**精简版 Cosmos(BaseModel)**（vlm/cosmos.py:8）：vLLM 硬加载（图视频各 10 上限，vlm/cosmos.py:15-18），system prompt 固定注入 `<think>/<answer>` 输出协议（vlm/cosmos.py:46-52），无解析后处理。

## 三、外部连接

API 版继承 BaseAPI 重试/探活模板；被 api_models 组四条 partial 引用（config.py:149-178，Lepton 端点）；依赖 qwen_vl_utils 与 ffmpeg。HF 版被 video_models 组注册（config.py:24-30）；vlm/cosmos.py 被 cosmos_series 注册（config.py:2425-2427）。

## 四、数据流

API 版一条视频样本：数据集 build_prompt 给出 `[{type:'video',value:mp4}]` → BaseAPI.generate 归一 → prepare_itlist 断言 patch size 已设（api/cosmos_reason.py:496）→ 超时包裹→缓存查询→抽帧→ffmpeg 编码 base64 data URL（命中缓存跳过重活）→ POST → finish_reason=stop 则 parse_answer → 回写管线。HF 版同源输入进程内走 processor+model，无网络与 base64 开销，但视频张量常驻内存（60 秒 1fps 约 1-2GB，api/cosmos_reason.py:174-175 点明 API 版坚持缓存+子进程的原因。

## 五、设计决策

1. **视频语义在客户端复刻**：端点收 base64 MP4 而非帧列表（api/cosmos_reason.py:181），fps/分辨率经 `mm_processor_kwargs` 随 payload 下发（api/cosmos_reason.py:583-585），保证服务端与本地实验 token 数一致。
2. **三种失败三种语义**：视频坏→哨兵跳过不重试；网络错→退避重试；截断→保留内容但记 truncated——把"重试是否有意义"编码进返回值。
3. **模型名端点自描述**（api/cosmos_reason.py:324-365）：配置与部署漂移是常态，自动 remap 比硬编码健壮。
4. **prompt 让位于公平性**（api/cosmos_reason.py:387-391）：作者承认自家指令在 MCQ 上有害并回退标准 prompt——benchmark 工程少见的诚实注释。
5. **双后端并存而非抽象统一**：接受行为漂移（采样参数 0.6/0.95 vs 0），换取独立演进。

## 六、新人提示（坑/勘误）

- **`'Cosmos-Reason1-7B'` 名字被注册两次**：video_models 组注册为 `vlm.CosmosReasonHF`（config.py:24-26），cosmos_series 组又注册为 `vlm.Cosmos, use_vllm=True`（config.py:2425-2427）。model_groups 顺序中后者靠后，`supported_VLM.update` 后写覆盖先写（config.py:2662-2663）——**最终生效的是 vlm/cosmos.py 精简版**，HF 版注册形同虚设（须 `--config` 显式 `class: CosmosReasonHF` 才用得上）。cosmos_series 传的 `use_vllm=True` 落进 `**kwargs` 被静默忽略（vlm/cosmos.py:12 签名无此参数）。该精简版还不做 think 剥离——system prompt 要求 `<answer>` 格式但原样返回（vlm/cosmos.py:76-77），判分器不认 `<think>` 前缀会系统性低估。
- **APIBASES 是空字典**（api/cosmos_reason.py:51-53）：'OFFICIAL' 被注释掉，`api_base` 必须显式传，直接 `CosmosReason()` 在健康检查处失败。
- **ffmpeg 是硬依赖且要求 stdout 可流式**：fragmented MP4 的 `frag_keyframe+empty_moov`（api/cosmos_reason.py:108）防 moov-at-end 卡死管道；容器无 ffmpeg 时错误晚到视频阶段才爆。缓存键含全部采样参数（api/cosmos_reason.py:150-151）。
- **CosmosReason2 与 2Think 解析正则不同**（api/cosmos_reason.py:733-738 vs 748-755）：切换变体不要复用旧解析。
