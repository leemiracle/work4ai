# 06 评测：DreamGenBench VLM 裁判与 ZeroMQ 推理服务

## 一、角色定位

这组文件是管线出口两件套。`dreamgenbench/` 三脚本实现 DreamGen 论文的自动评测协议：世界模型生成的机器人视频不能用像素指标衡量，DreamGenBench 用 **VLM 当裁判**——`eval_sr_qwen_whole.py`/`eval_sr_gpt4o_whole.py` 判指令遵循（IF，成功率 SR），`eval_qwen_pa.py` 判物理对齐（PA）。`gr00t/eval/` 是策略上线基础设施：`service.py` 为 ZeroMQ REQ/REP 微型 RPC，`robot.py` 叠"远程模型本地化"，`wrappers/` 三个 gym wrapper 把单步环境适配成模型期望的时序形态并录视频。前者管"生成得像不像真的"，后者管"策略怎么接环境"，且经 `VideoRecordingWrapper` 闭环：录出的 mp4 正是 DreamGenBench 的输入。

## 二、内部结构

**IF 评测·Qwen 版**：`evaluate()` 遍历 `**/*.mp4`（eval_sr_qwen_whole.py:15），按目录命名约定反解 prompt——cogvideo/hunyuan/wan 三套 split 规则各自硬编码（:19-34），与评测产物目录强耦合。判词两套：zeroshot 版带"见人手立即判 0"硬规则（:42-50），常规版只问指令是否完成（:52-56）。视觉输入 `sample_video_frames(num_frames=49, scale_factor=0.3)`（:59）——该行注释还写着 "Sample 16 frames"，代码已改 49 帧缩 30%，注释是化石。49 帧全作独立 image 塞进单条 message（:62-88），`max_new_tokens=4`、首字符 '1' 即判 1（:92, :105-107），CSV 汇总打 1 率（:112-124）。

**IF 评测·GPT-4o 版**：本地模型换 API。帧转 base64 PNG data URI（eval_sr_gpt4o_whole.py:17-25），只采 8 帧、scale 0.5（:69）——两版视觉信息量差异巨大，跨版本比较 SR 须记入变量。请求 `seed`+`temperature=0.0`+`max_tokens=4`（:79-85），配指数退避重试（:76-93）。zeroshot 判词比 Qwen 版多四宫格 multiview 条款（:56, :58）。

**PA 评测**：判词与 prompt 无关（"是否展现良好物理动力学、违反物理即 0"，eval_qwen_pa.py:67-71），prompt 仅作记录列（:65）。输入用 Qwen 原生 `{"type":"video"}` 通道走 `process_vision_info`（:76, :86）而非帧展开。`set_seed/load_model` 在文件内复刻（:13-52），与 utils.py 逐字重复。

**推理服务**：`BaseInferenceServer`（gr00t/eval/service.py:44）起 REP socket，注册表 `{name: EndpointHandler}`（:73-82），内置 ping/kill（:58-59）。`run()` 循环收 bytes→`TorchSerializer.from_bytes`（torch.load，`weights_only=False`，:34）→分发→回传；异常只打印并回 `b"ERROR"`（:103-108）。client 侧 `ping` 失败自动重建 socket（REQ 卡死状态机的标准自救，:124-130），收到 `b"ERROR"` 抛 RuntimeError（:155-156）。`robot.py` 的 `RobotInferenceServer` 只注册 `get_action` 与 `get_modality_config` 两端点（robot.py:30-33）；`RobotInferenceClient(BaseInferenceClient, BasePolicy)` **双继承**（:41）——客户端同时是一个 Policy，一行转发（:46-47），吃 BasePolicy 的代码零改动即远程化。

**三个 wrapper**：`MultiStepWrapper`（multistep_wrapper.py:80）一次 `step(action)` 内循环执行 `n_action_steps` 子步（:207-227），维护 obs deque 按 delta_indices 回看拼 horizon（`_get_obs` :243-278，`delta_indices-1` 的 0 索引修正 :254-262）；断言组要求索引全非正、末位 0、等差递增（:171-185）。`ObsIndexSelectionWrapper`（obs_index_selection_wrapper.py:20）是无状态轻量版——环境自吐完整序列时按 `(L-1)+delta` 切片（:57-66）。`VideoRecordingWrapper`（video_recording_wrapper.py:175）用 PyAV 录 h264 crf 18（:91-110），`reset` 时按 `info["success"]` 改名 `_success{0/1}`（:210-215, :232）——文件名即标签。

## 三、外部连接与数据流

三脚本共享底座 `dreamgenbench/utils.py`：`load_model` 固定拉 `Qwen/Qwen2.5-VL-7B-Instruct`（:35-40），`sample_video_frames` 用 decord 均匀采样、不足帧数复制末帧补齐（:75-80, :89-91）。服务侧消费链：`scripts/inference_service.py` 起 server 并 client 自测（:82, :91）；`scripts/eval_policy.py` 把 `RobotInferenceClient` 直接当 `BasePolicy`（:99）；so100 真机示例再包一层 `ExternalRobotInferenceClient`（eval_gr00t_so100.py:36, :185）。评测闭环：wrapper 录视频带 success 标签 → DreamGenBench 批量裁判 → CSV 汇总。

## 四、甄别：四个源码级坑

1. **argparse `type=bool` 陷阱（两版都有）**：`--zeroshot false` 执行 `bool("false")==True`（eval_sr_qwen_whole.py:139 / eval_sr_gpt4o_whole.py:117）。正确关法是不传该参数，传任何非空字符串都是开。
2. **qwen 版 zeroshot 是双重死代码**：更深一层——`main` 里 `evaluate(args.video_dir, args.output_csv, args.device)`（:144）**根本没传 `args.zeroshot`**，形参永远默认 False，:42-50 那套人手硬规则判词不可达；gpt4o 版 :122 则正确传了。**两版同名参数行为不一致**，复现 zeroshot 数字必须用 gpt4o 版或先修 qwen 版。
3. **gpt4o 版 :28 `openai.api_key = api_key` 是死代码**：下一行 `client = OpenAI(api_key=api_key)`（:29）才是真消费方（:78 走 client），旧式全局赋值无读者，纯迁移残留。
4. **两版容错语义不同**：qwen 版视频不存在 `continue` 跳过（:37-39），gpt4o 版只 print 不跳（:48-49）；且 gpt4o 版重试耗尽后 `pred=0` 记失败而非剔除（:94）——分母口径与 qwen 版不同。

## 五、设计决策

1. **VLM 整段裁判而非逐帧打分**：一次看全轨迹判 0/1，与人类成功判据对齐；代价是判词措辞、帧数、分辨率全是敏感超参（两版已各不相同），可复现性锚定在脚本而非协议文档。
2. **零依赖评测**：qwen 版 7B 本地可跑，gpt4o 版留 API 口；PA 用原生 video 通道保留帧间运动信息——恰是 PA 关心的信号。
3. **ZMQ+torch 序列化而非 HTTP/JSON**：观测是含 numpy/tensor 的嵌套 dict，`torch.save` 全类型通吃（service.py:26-29），代价是反序列化信任边界=局域网。
4. **RobotInferenceClient 双继承**是本组最优雅一笔：RPC 传输与 Policy 接口拼接，评测/真机代码零改动远程化。
5. **双时序 wrapper 并存**：MultiStep 为实时环境缓存历史，ObsIndex 为已吐序列环境切片，同一 delta_indices 契约两种环境形态各有适配层。

## 六、新人提示

- 跑评测先确认目录名含 `cogvideo/hunyuan/wan/cosmos` 之一，否则 prompt 解析 fallback 到 wan 分支（:31-34）不报错——CSV 里 prompt 与指令不符是首查项。
- 想开 zeroshot：qwen 版先修 :144 补传参；两版都别写 `--zeroshot true/false` 布尔串。
- gpt4o 版 multiview 四宫格条款只在 zeroshot 判词里（:56），评 multiview 产物务必核对所用模式。
- 服务端单线程串行，REQ/REP 下客户端并发排队；`timeout_ms=15000`（service.py:112）是本地超时，长 horizon 批量推理注意别撞。
- `MultiStepWrapper` 的 delta_indices 须过断言组；`[0]` 或 `[-3,-2,-1,0]` 合法，正数或非等差直接 assert 崩。
- `VideoRecordingWrapper.reset` 改名依赖 `info["success"]` 键（:232），仿真环境 info 无此键会 KeyError——录自定义环境先补键。
