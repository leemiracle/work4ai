# 04 · vlm 模型 wrapper 层：BaseModel 协议与三大家族实现

## 一、角色定位

`vlmeval/vlm/`（100 个条目）是本地模型接入层：一家一个目录/文件，`vlm/base.py` 定义 75 行的 `BaseModel` 协议，其余全是实现。与 `vlmeval/api/`（远程 API）在 run.py 层面等价互换——推理管线只认 `model.generate(message, dataset)` 鸭子接口。`vlm/__init__.py` 在 import 期就 `torch.set_grad_enabled(False)`+`manual_seed(1234)`（vlmeval/vlm/__init__.py:1-2）。本篇以协议+qwen2_vl+internvl+interns1 四样本讲清 60+ wrapper 公共形态。

## 二、内部结构

**BaseModel 协议（vlm/base.py:9-224）**：类属性开关 `INTERLEAVE=False`（vlm/base.py:11，能否交错处理图文）、`allowed_types=['text','image','video']`（vlm/base.py:12）。双抽象方法：`build_prompt`（vlm/base.py:29-40，仅当 `use_custom_prompt(dataset)`（vlm/base.py:17-27）返回 True 才被调用）与 `generate_inner`（vlm/base.py:48-50，推理入口）。`generate` 是模板方法（vlm/base.py:104-119）：`check_content` 四态判定（vlm/base.py:52-65）→ `preproc_content` 归一为 listdict（vlm/base.py:67-102，liststr 路径用 `parse_file` 自动识别文件/URL/文本，vlm/base.py:84-89）→ 逐条断言 type 合法（vlm/base.py:117-118）→ 调 generate_inner。降级工具：`message_to_promptimg`（vlm/base.py:140-157）给非交错模型"拼全部文本+取第一图"（BLINK 特判横拼 vlm/base.py:153-154）；`message_to_promptvideo` 由 `VIDEO_LLM` 门控（vlm/base.py:159-202）；`message_to_lmdeploy`（vlm/base.py:204-224）。`chat`（vlm/base.py:121-138）失败时**丢弃最早一轮 user 消息重试**（vlm/base.py:129-137）。

**qwen2_vl 目录型（model.py 760 行 + prompt.py 158 行）**：`Qwen2VLChat(Qwen2VLPromptMixin, BaseModel)`（qwen2_vl/model.py:175）——Mixin 给自定义 prompt，BaseModel 给协议；`INTERLEAVE=True/VIDEO_LLM=True`（qwen2_vl/model.py:177-178）。构造器（qwen2_vl/model.py:180-316）三步：按 `config.json` 的 `architectures` 自动选模型类（omni/qwen2_5/默认三档，qwen2_vl/model.py:239-263）→ 按开关起引擎——vLLM（GPU 数 8/4/2/1 自动 tp_size、max_model_len=32768、图上限 24，qwen2_vl/model.py:273-299）/lmdeploy（qwen2_vl/model.py:301-309）/transformers（qwen2_vl/model.py:311-314）。`_prepare_content`（qwen2_vl/model.py:318-369）转 qwen_vl_utils 方言：本地路径补 `file://`（qwen2_vl/model.py:20-26）、OCRBench 特判 min_pixels（qwen2_vl/model.py:326-330）、帧数不足按 FRAME_FACTOR=2 取整（qwen2_vl/model.py:356-359）。三个 `generate_inner_{transformers,lmdeploy,vllm}`（qwen2_vl/model.py:459/525/541）+ 分发器（qwen2_vl/model.py:636-642）；`post_process` 平衡花括号提取最后的 `\boxed{}`（qwen2_vl/model.py:503-519）。prompt.py 的 `Qwen2VLPromptMixin`（qwen2_vl/prompt.py:4）按 DATASET_TYPE 白名单决定自定义 prompt（qwen2_vl/prompt.py:26-42），四模板处理 MMMU（图前置）/MCQ（中英文判别）/YORN/VQA。

**interns1 对齐样本**：`InternS1Chat`（interns1/interns1_chat.py:29）**不继承 BaseModel**，靠类属性四件套（interns1_chat.py:31-34）+ 同名方法（generate_inner:137、use_custom_prompt:185 等）鸭子对齐——管线只 getattr 不 isinstance。

**internvl 巨型单文件（internvl_chat.py 575 行）**：`InternVLChat(BaseModel)`（internvl_chat.py:94）一个类横跨四代版本（generate_inner 按 version 分发 v1_2/v1_5/v2，internvl_chat.py:467-477）。构造器：`cot_prompt_version` 三档（r1→`R1_SYSTEM_PROMPT` 强制 `<think>` 协议，internvl_chat.py:98-216、25-38、126-128）；lmdeploy 引擎按模型名选 Pytorch/Turbomind（internvl3_5 用前者，internvl_chat.py:166）；**Best-of-N+过程奖励模型**（internvl_chat.py:189-207，BoN>1 强制开 CoT 并另载 reward model）。`set_max_num`（internvl_chat.py:316-337）按数据集设动态分辨率 tile 上限（总量 64，分档 12/18/24）。`generate_v2`（internvl_chat.py:380-465）：BoN 采样→PRM 选优（internvl_chat.py:440-447）→MPO/boxed 后处理→GUI bbox 解析（internvl_chat.py:456-463）。多轮 `chat_inner_v2` 做 `Image1↔Image-1` 换名（internvl_chat.py:507-560、149-160）；GUI 模板从 yaml 加载（internvl_chat.py:21-23）。

## 三、外部连接

向上被 config.py 各 series 分组以 `partial(vlm.XXX, model_path=...)` 注册（config.py:24-26、internvl 系列 config.py:1129-1162），汇入 supported_VLM（config.py:2663）。向侧按需 import：qwen2_vl→qwen_vl_utils/vllm/lmdeploy 三选一；internvl→`trust_remote_code=True` 的 AutoModel（模型代码随权重分发）。数据集查询 DATASET_TYPE/MODALITY（internvl_chat.py:12）。

## 四、数据流

管线调 `model.generate(message, dataset)` → base 归一化 → generate_inner：qwen2_vl 路径 `_prepare_content` → `apply_chat_template` → `process_vision_info` 拿图/视频张量 → vLLM `llm.generate`（qwen2_vl/model.py:590-609）或 transformers `model.generate(**inputs)` → batch_decode 剥特殊 token（qwen2_vl/model.py:499-501）→ 可选 boxed 提取。internvl 路径 `load_image` 动态切 tile → 多图 patch `torch.cat`（internvl_chat.py:392-401）→ `self.model.chat(...)` → 后处理链。

## 五、设计决策

1. **协议极简（2 抽象方法）+ 模板方法收口**（vlm/base.py:104-119）：校验全部前置，60+ wrapper 无一重复实现。
2. **Prompt 双轨制**：数据集默认 build_prompt 与模型自定义（qwen2_vl/prompt.py:26-42、internvl_chat.py:218-240 各自白名单）并存，管线三级优先 `force_use_dataset_prompt > model.use_custom_prompt > dataset.build_prompt`（inference.py:158-166）仲裁公平性与特化 prompt 的张力。
3. **多后端塞单类**（qwen2_vl 按引擎轴）与**单类跨代**（internvl 按版本轴）都是"家族聚拢"策略，避免 wrapper 爆炸漂移。
4. **多图位置三种表达**：lmdeploy 用 IMAGE_TOKEN（internvl_chat.py:42-43）、HF 用 `<image>\n`（internvl_chat.py:493）、internvl 用 `Image-{n}` 换名（internvl_chat.py:150-160）——改 prompt 须对准后端。**能力位（INTERLEAVE/VIDEO_LLM）是显式契约**，基类据此自动降级（vlm/base.py:140-157）。

## 六、新人提示（坑/勘误）

- **`skip_special_token` 笔误三处**：llava.py:394、mantis.py:204、granite_vision.py:192 少了 s（正确为 `skip_special_tokens`）。错误 kwarg 被**静默吞掉，特殊 token 不剥除**，输出带 `<|im_end|>` 尾巴伤判分。fork 未修。
- **Quickstart 引用路径已重组**：指引若让你找 `internvl/model.py`，实际是 `vlmeval/vlm/internvl/internvl_chat.py`（目录只有 internvl_chat/utils/gui_template.yaml）；qwen2_vl 才是 model/prompt 双文件。
- **InternS1Chat 不是 BaseModel 子类**：继承图搜不到但接口齐全（interns1_chat.py:29-34）；"遍历子类"的脚本会漏。
- **Qwen2VLChatAguvis**（qwen2_vl/model.py:645）是 GUI agent 变体（六态注入 recipient_text，qwen2_vl/model.py:693-706），别当普通 wrapper 调。vLLM 视频路径转 numpy（qwen2_vl/model.py:571-573），帧数超 24 上限（qwen2_vl/model.py:17）只 warning 不截断（qwen2_vl/model.py:585-586）；qwen-omni 带音频要求 `VLLM_USE_V1=0`（qwen2_vl/model.py:582）。
- **internvl BoN 强设全局 `USE_COT=1`**（internvl_chat.py:203），同进程后续 internvl 实例被传染。
