# 10 · Generator 教程三线：transfer / action / audiovisual

## ① 角色定位

`cookbooks/cosmos3/generator/` 三条教程线覆盖生成器全部能力面，每条是"任务语义 × 推理后端"的矩阵：

- **transfer（视频迁移）**：空间控制信号（edge/blur/depth/seg/WSM）+ caption → 服从控制布局的写实视频。五本 notebook（cosmos_framework/diffusers/sglang/trt_llm/vllm_omni，sglang 是文档孤儿，见 09 篇⑥）。
- **action（动作模态）**：fd（起始图+动作轨迹→未来观测）/id（视频→自车/末端轨迹）/policy（起始图+指令+状态→观测与动作块）三任务 × 四后端 + sglang 孤儿三本。
- **audiovisual（视听生成）**：t2v/i2v（含声音开关）跨 Nano/Super/Edge/四步蒸馏学生 × 五后端。

三线共同点：环境安装上提共享 `cookbooks/cosmos3/README.md`；生成必须走 Guardrail（gated `nvidia/Cosmos-1.0-Guardrail`，各后端关闭开关名不同）；资产全部仓内。

## ② 内部结构

**transfer 线**——六类控制（README:9-14）：edge(Canny)/blur/depth/seg/WSM(世界场景图)/multi-control。README:16-19 能力矩阵是选后端依据：多控制 Framework+TRT-LLM+vLLM-Omni 支持，**逐控制加权只有 Framework**，Diffusers 收多控制但无权重。`specs/edge.json`（README:371-392 全文）代表字段：`model_mode: video2video`、`resolution+aspect_ratio`（720+16,9→1280×720）、`fps` 既是条件信号又是播放率、hint 块内 `control_path`；控制视频的帧数/几何决定输出（README:36）；WSM 独用 100 帧@10FPS，其余 121 帧@30FPS（README:40-47）。

四后端取数约定各异（README:27-38）：Framework 吃本地 spec 的 `control_path`/`vision_path`；Diffusers 只走 modular pipeline 的 `control_videos={hint: frames}`（README:145-183）；TRT-LLM 把预计算控制 **base64 进 `extra_params.hint.control`**（README:228-230），原始源走 multipart `video_reference`，只有 edge/blur 可服务端现算（README:267-269）；vLLM-Omni 传**服务端可读的仓内相对 `control_path`**（README:307-316，Docker 须从仓根启动）。TRT-LLM 有 MP4 魔数校验（README:259-263）。API 钉版：`/v1/videos/generations` 是废弃别名，规范路由是阻塞式 `/v1/videos/sync`（README:276-277）。

**preview_helpers.py**（174 行，transfer 线唯一 .py）：`TRANSFER_CONTROLS` :13 五元组校验；`_ffmpeg_exe()` :16-29 三级回退；`_transfer_root()` :32-43 环境变量→文件位置→向上找；`make_preview()` :71-95 转 CRF 28 轻量预览且 **mtime 新于预览才重转**（:73）；`preview_transfer()` :98-131 成对展示 control 输入 vs generated 输出，路径约定 `<output_root>/<model>/transfer_<control>/vision.mp4`（:110）。

**action 线**——README:27-49 动作表示：动作是"相邻视觉状态转移"的 token 模态，统一 9D 位姿增量（3D 平移+6D 连续旋转）；embodiment 表：AV 9D（60 帧@10FPS）、DROID/UMI 末端 9D+夹爪=10D、人手 57D。四后端接口：Framework 用 spec JSON；Diffusers 用 `CosmosActionCondition(mode/chunk_size/domain_name/resolution_tier/raw_actions/image)`（README:112-130），**帧数由 chunk_size+1 推导**、height/width/num_frames 不设，id 换 `video=` 返回 `result.action`，policy 联合预测；TRT-LLM 用 multipart `image_reference`+`extra_params.action_mode/action`，响应是 **safetensors 张量**（README:188-199），显式 mp4/avi 被拒绝而非丢轨迹（README:222-224）；vLLM-Omni 用 multipart `input_reference`+异步 `POST /v1/videos`，动作在顶层 `action` 元数据（README:262-292）。TRT-LLM 的 action 契约**钉在源码 revision `bca6761a`** 验证（README:179-181）。

**audiovisual 线**——五后端 notebook + `run_distilled_with_trt_llm.ipynb`（四步蒸馏学生专用，README:409）。README:6-8 钉死 NIM 边界：Generator NIM **只暴露 T2V/I2V**，无 t2i/v2v/声音/动作/transfer。Edge 约束：无音频模块、只支持 256p/480p（README:80-84）。

## ③ 外部连接

- **共享环境层**：`../../README.md` 八节安装；transfer 线钉了 NATTEN 排查（README:422-427：容器 Torch/NATTEN 与 `~/.local` 混装必炸，`PYTHONNOUSERSITE=1` 防遮挡）。
- **HF 资产**：`nvidia/Cosmos3-{Nano,Super,Edge}`+gated Guardrail；action 线 LeRobot 读取器来自 cosmos-framework（README:166-169），DROID 读取器**按目录名识别 feature 布局**故 `COSMOS3_DROID_ROOT` 须指向以 release 命名的目录。
- **训练线接口**：action README:329-341"Post-Train"把推理 cookbook 与 `finetune/` SFT 挂钩（见 11 篇）；audiovisual README:98-104 有 distill 链接。
- **评测线接口**：transfer specs 与 paibench_c specs 同构（08 篇③），教程练手可直接迁移到正式跑分。
- **Action Viewer**：HF Space `nvidia/Cosmos3-Action-Viewer` 零安装预览入口（README:11-12）。

## ④ 数据流

transfer 单次往返（vLLM-Omni）：`assets/depth/prompt.json`+`negative_prompt.json` 读出→`json.dumps` 成字符串→multipart form：顶层 prompt/size/num_frames/fps/seed + `extra_params`（hint 块带**服务端可见 control_path**、resolution 720、帧块参数）→`POST /v1/videos/sync`→MP4 字节落盘→`preview_helpers.preview_transfer("depth")` 内嵌展示。action 的 Diffusers 路线：`assets/actions/av_traj_forward.json`（60×9 数组）读成 tensor→`CosmosActionCondition` 连同 `assets/images/av_0.jpg`→pipeline 推 chunk_size+1 帧→`export_to_video(macro_block_size=1)`（防 ffmpeg 缩放非 16 对齐分辨率）。id/policy 输出侧多一步：`result.action` 画成轨迹。

## ⑤ 设计决策

1. **控制信号预计算且仓内 checked-in**：演示控制视频直接进 git；"从原始视频现算控制"作为进阶路径单独存在（Framework `vision_path`、TRT-LLM `video_reference`、vLLM-Omni `input_reference`）。
2. **同一套 specs 双模型复用**：specs 不含模型名，Nano/Super 只由 `--checkpoint-path` 决定（README:51-52）——配置与模型正交。
3. **响应格式按任务语义选择**：action 是张量语义（轨迹无视频编码可无损承载），TRT-LLM 拒绝 mp4 强制 safetensors——宁可显式失败不做有损降级。
4. **preview_helpers 是唯一共享 .py**：三线其余全是 notebook+JSON——"notebook 内联优先、跨本复用才抽 .py"的克制。
5. **embodiment 参数表前置**：action README 把 9D/10D/57D 表示、单位、后处理、时长列表再讲代码——动作 token 语义是理解三任务的前提。

## ⑥ 新人提示（坑与勘误）

1. **transfer 线 README 后端清单只有四个**：`run_video_transfer_with_sglang.ipynb` 存在但零文档引用（09 篇孤儿清单之一）；根 README:35 演示卡链的是 vllm_omni 版。
2. **guardrail 开关名各后端不同**：`guardrails`（vLLM-Omni）vs `use_guardrails`（TRT-LLM）vs `enable_safety_checker=False`（Diffusers）vs `--no-guardrails`（Framework）vs NIM 双环境变量——抄错字段名不会报错而是静默走默认。
3. **blur 示例分辨率是特例**：4:3 原生桶 1104×832，其余 1280×720（README:272-275）；不传 size 时 TRT-LLM 从源/首控制视频宽高比挑最近支持桶。
4. **action 的 id 模式输入是视频不是图**：Diffusers 侧 `video=`、无 raw_actions；把 fd 调用复制改 mode 会参数错误。fd 的 raw_actions 形状须匹配 chunk_size×dim（AV 为 60×9）。
5. **audiovisual 的 prompt 是结构化 JSON 字符串**：`json.dumps(ensure_ascii=True, separators=(",",":"))` 压缩后进 payload（README:35-45）——直接传纯文本与传结构化 JSON 生成质量不同。
6. **Edge 档跑 t2v 记得改三处**：`resolution:"480"`、`num_frames:121`、`enable_sound:false`（README:80-84）——缺一会在框架校验或生成阶段炸。
