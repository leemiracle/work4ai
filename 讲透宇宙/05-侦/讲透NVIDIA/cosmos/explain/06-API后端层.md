# 06 · API 后端层：BaseAPI 重试模板、wrapper 家族与 adapters 注册表

## 一、角色定位

`vlmeval/api/`（41 个 py 文件 + adapters/ 子包）接管所有"不开本地"的模型：公有云（OpenAI/Gemini/Claude/Reka/Together）、国产云（GLM/Hunyuan/Qwen/Doubao/MiniMax 等）、自托管 OpenAI 兼容服务（CosmosReason 的 Lepton 端点、NVIDIA 内部端点 NVGemini/lmdeploy 自部署）。架构三层：`base.py`（335 行）的 `BaseAPI` 提供重试/消息归一/探活模板；各 wrapper 只实现 `generate_inner` 返回 `(ret_code, answer, log)` 三元组；`adapters/` 是按模型名挂载的输入输出微调钩子注册表（6 个适配器，被 lmdeploy.py 消费）。与 vlm/ 层在 run.py 眼里等价——`build_model_from_config` 在两个命名空间一视同仁 getattr（run.py:72-75）。

## 二、内部结构

**BaseAPI 模板（api/base.py:12-335）**：

- *构造*（api/base.py:18-47）：默认 `retry=10, wait=1`；`_fail_reason_local = threading.local()`（api/base.py:42）线程安全记录失败原因；未知 kwargs 收进 `default_kwargs` 透传（api/base.py:44-47）——wrapper 私有参数从这里漏进来。
- *pickle 安全*（api/base.py:49-56）：`__getstate__` 剔除不可序列化的 threading.local——wrapper 随多进程池被 pickle 到 worker 的必经补丁。
- *generate 重试模板*（api/base.py:232-305）：入参归一（listdict 带 role 时先抽 system，api/base.py:241-242、212-230）→ 起跑前随机睡 0-0.5s（api/base.py:274-275，多线程错峰）→ retry 循环里 `ret_code==0 且 answer 非空且不含 fail_msg` 才算成功（api/base.py:281），否则随机 `0~2*wait` 退避（api/base.py:301-302）→ 全败后按 ret_code 写 `_fail_reason_local`（1=可恢复、2=内容审查，api/base.py:304）。两条防御补丁：**allowed_types 丢失自愈**（api/base.py:248-265，多进程 pickle 后类属性偶发丢失强制重置）；**log 兼容 response 对象**（api/base.py:290-295 取 `.text`）。log 为 dict 时返回 `{"prediction":..., "extra_records":...}`（api/base.py:286-288，agent 评测的结构化通道）。
- *chat 多轮*（api/base.py:167-210 + chat_inner 152-165）：与 vlm/base.py:121-138 同款"逐轮丢弃最老 user 轮"的爆上下文自救。
- *探活*（api/base.py:71-93）：`working()` 临时把 timeout 抬到 120s，发 'hello' 试 5 次。
- *降级*（api/base.py:307-329）：非交错模型 `message_to_promptimg` 三分支版——多图保留 `<image>` 占位符（api/base.py:322），比 vlm/base.py:146-156 直接丢图保留更多信息。

**wrapper 家族（api/__init__.py:1-38 的 38 个 import）**：代表性三档——① OpenAI 生态大杂烩 `OpenAIWrapper`（gpt.py:37）：按模型名子串分派七八种环境变量 key（STEPAI/YI/MiniMax/MOONSHOT/XAI/GOOGLE 等，gpt.py:60-107），Gemini preview 直接改写 api_base 到 Google 官方端点（gpt.py:92-98）；`GPT4V`（gpt.py:331）是其视觉子类。② NVIDIA 内部端点 `NVGemini`（nv_gemini.py:38）：api_base 必填（nv_gemini.py:46），带 preflight 预检（nv_gemini.py:129）。③ OpenAI 兼容自部署 `lmdeploy.py`：构造时 `_detect_adapter(model)` 按模型名选适配器并 `build_adapter` 实例化（lmdeploy.py:63-77）。CosmosReason 家族（api/__init__.py:6-7）已在篇 05 详述。

**adapters 注册表（adapters/base.py）**：`_ADAPTER_REGISTRY` 模块级字典（adapters/base.py:1）；`register_adapter(name)` 双用法——装饰器或直接注册 partial 变体（adapters/base.py:4-22）；`build_adapter(name, **kwargs)` 按名实例化，未注册时 KeyError 列出可用项（adapters/base.py:25-30）。`ModelAdapter` 基类（adapters/base.py:38-78）定义**七个可选钩子**：`dump_image / override_model_args（按数据集改生成参数）/ use_custom_prompt / build_prompt（唯一必须实现）/ process_inputs（HTTP 消息前变换）/ process_payload（改请求体）/ postprocess（改回复）`。现有 6 个：InternVL2/InternVL3/InternS1_1 双变体/CogVLM2/Qwen3（adapters/__init__.py:1-13）。

## 三、外部连接

向上：config.py 的 api_models 等组把每个 API 模型注册为 `partial(api.XXX, model=..., api_base=..., retry=..., timeout=...)`（config.py:147 起，Lepton 端点字符串硬编码在源码里）；run.py 的 FWD_API 开关能把全部 API 模型替换成 GPT4V 类做端点兼容自检（run.py:261-268）。向下：requests 直连各端点（BaseAPI 不引入 openai SDK，全部裸 HTTP）；`.env` 经 smp.load_env 注入 key（misc.py:204-228）；is_api=True 的类走 `infer_data_api` 进程池并行而非分布式切分（inference.py:37、136-150）。侧向：adapters 被 lmdeploy.py:6 显式消费；jt_vl_chat 双文件（jt_vl_chat.py:286 / jt_vl_chat_mini.py:281/287）是同一服务的孪生 wrapper。

## 四、数据流

单条样本：管线 `model.generate(message=struct, dataset=...)` → BaseAPI.generate 归一（system 抽取、parse_file 解析本地文件为可传 URL/base64）→ generate_inner 组装 OpenAI 形状 messages（image_url/video_url 结构见 api/cosmos_reason.py:471-514）→ requests.post → 三元组返回 → 模板判定成败/退避重试 → 成功返回字符串（或 agent 场景的 dict）。API 并行度由 run.py 的 `--api-nproc`（默认 4）控制：infer_data_api 在主 rank 用进程池 map（inference.py:37-90），每个 worker pickle 一份 wrapper（触发 api/base.py:49-56）。

## 五、设计决策

1. **重试语义收敛到 fail_msg 字符串匹配**（api/base.py:281）：子类失败时返回含 fail_msg 的 answer 即触发重试，无需异常体系——简单粗暴但让"半成功"（如截断内容）可以被单独放行（api/cosmos_reason.py:648-660 的 truncated 即利用这点）。
2. **三元组契约而非字符串**（api/base.py:58-69）：ret_code/answer/log 分离让"成功但有警告""失败但内容可判分"这类灰度可表达，是 fork 相对上游加厚最多的接口。
3. **随机退避而非指数退避**（api/base.py:180-181、301-302）：0~2*wait 均匀分布 + 起跑随机延迟，面向"几十线程打同一端点"的评测负载——避免整齐划一的重试风暴。
4. **adapter 钩子化**：模型专属 prompt/后处理不再复制整个 wrapper，而是注册为名字→钩子集（adapters/base.py:4-30），lmdeploy 一个 wrapper 挂 6 种模型的行为——扩展点从"继承"降到"注册"。
5. **密钥从环境变量+模型名双路解析**（gpt.py:60-107）：同一 wrapper 服务十几家供应商，key 按模型名子串路由，避免配置文件。

## 六、新人提示（坑/勘误）

- **jt_vl_chat 是孪生重复**：jt_vl_chat.py（289 行）与 jt_vl_chat_mini.py（290 行）95% 相同，仅端点/默认模型名不同（jt_vl_chat_mini.py:16-18）。更糟的是 **jt_vl_chat_mini.py:18-19 硬编码了完整 JWT APP_CODE**，jt_vl_chat.py:18 也有短 key——公开仓泄漏九天平台真实凭据，复用前先脱敏。
- **`retry=10` 与 `wait=1` 是 BaseAPI 默认**（api/base.py:19-20），多数 config.py 注册显式覆盖（Lepton 条目 timeout=300，config.py:149-178）；judge 默认 retry=3（run.py:384）。排查"卡很久"先看三层 retry。
- **`working()` 探活临时改 `self.timeout`**（api/base.py:77-93）：5 次全败时 timeout 不复原（api/base.py:85-88）——探活失败后的对象处于 120s 超时脏状态。
- **HFChatModel 不继承 BaseAPI**（hf_chat_model.py:38，与 InternS1Chat 同款鸭子对齐）——"api 目录都是 BaseAPI 子类"不成立。
- **adapters 与 wrapper 的 use_custom_prompt 叠加**：lmdeploy wrapper 有自己的 prompt 逻辑，adapter 再叠一层（lmdeploy.py:63-77）；调试 prompt 两个 hook 点都要查。
- **`_fail_reason_local` 只在同线程可读**（api/base.py:304 写入）：跨线程状态走 CosmosReason 的 INFERENCE_STATS_FILE JSONL（api/cosmos_reason.py:667-686）。
