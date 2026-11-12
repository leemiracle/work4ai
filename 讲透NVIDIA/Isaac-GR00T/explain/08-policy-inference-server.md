# 08 · 策略推理与服务化：Gr00tPolicy 与 ZMQ 推理服务器

> 覆盖：`gr00t/policy/gr00t_policy.py` · `gr00t/eval/run_gr00t_server.py`（辅锚 `policy.py`、`server_client.py`）

## 一、角色定位

训练闭环之后，这两个文件是模型与真实机器人之间的全部软件层。`Gr00tPolicy` 把"checkpoint+观测 dict"变成"物理单位的动作 chunk"，是部署语义权威实现；`Gr00tSimPolicyWrapper` 是给旧 GR00T 仿真环境 flat-key 接口的适配壳；`run_gr00t_server.py` 把任意 policy 包成 ZMQ+msgpack 请求-应答服务，让推理与控制进程解耦。基类 `BasePolicy.get_action`（`policy.py:80-105`）是模板方法：strict 模式先 `check_observation`、算完再 `check_action`（`:100-104`），校验与计算分离。

## 二、内部结构

**Gr00tPolicy（`gr00t_policy.py:70`）**。`__init__`（`:83-175`）五步：`import gr00t.model` 触发注册（`:101`）；字符串标签经 `EmbodimentTag.resolve`（`:104-105`）；`AutoModel.from_pretrained`+`eval()`+整模型 bfloat16（`:109-111`）；processor 定位带回退——训练期存在 `model_dir/processor/` 子目录（07 篇 `experiment.py:256`），根目录缺 `processor_config.json` 时自动落子目录（`:118-123`）；embodiment 校验失败按"本 checkpoint 支持标签清单"渲染报错，posttrain 标签附"需微调 checkpoint"hint（`:129-160/:142-147`）。通过后缓存该本体 modality_configs（过滤 `rl_info` `:161-165`）、collator（`:166`）与 language 首键（`:171-175`）。

观测侧三方法：`_unbatch_observation`（`:177-198`）从第一个 video 键推断 B（`:188`）拆单条；`_to_vla_step_data`（`:200-215`）包成 `VLAStepData`——actions 显式置空（`:212`），text 取 `language[language_key][0]`（`:213`）；`check_observation`（`:217-378`）防御带：video 必须 uint8 五维 `(B,T,H,W,C)`、T 等于 `len(video.delta_indices)`、C==3（`:276-293`），state 必须 float32 三维 `(B,T,D)`（`:320-332`），language 双层 list、每步恰一条字符串（`:359-378`）。

动作侧 `_get_action`（`:380-432`）五步流水：unbatch（`:400`）→ 逐条 processor 编码并收集 states（`:405-409`）→ collate 后 `_rec_to_dtype` 转 bfloat16（`:411-413`）→ `inference_mode` 内 `model.get_action` 取 `action_pred`（`:416-418`）→ `processor.decode_action(pred, tag, batched_states)` 反归一化（`:421-426`），统一 float32（`:429-431`）。`check_action`（`:434-477`）校验每键 float32 `(B,T,D)`、T 等于 `len(action.delta_indices)`（`:465-477`）。`reset` 返回空 dict（`:482-491`）——policy 无状态。

**Gr00tSimPolicyWrapper（`:494`）**。docstring 明示只为兼容现有仿真基础设施、新环境直接用 Gr00tPolicy（`:502-504`）。核心是 flat↔nested 键变换：`video.cam`→`observation["video"]["cam"]`、动作反向加 `action.` 前缀（`:507-510/:694`）；语言键 `task` 在观测含 `annotation.human.coarse_action` 时被 PATCH 替换以兼容 DC 环境（`:614-616`）；语言形状从 `(B,)` tuple 升维 `(B,1)` 双层 list（`:680-684`）。

**run_gr00t_server.py**。`ServerConfig`（`:53-88`）：model_path/embodiment_tag（默认 `new_embodiment` `:61`）/device 三主键，ReplayPolicy 侧 dataset_path/modality_config_path/execution_horizon（`:68-75`），服务侧 host 0.0.0.0/port 5555（`:78-81`，常量 `:31`）。`main`（`:91-175`）三分支：model_path→Gr00tPolicy（`:101-110`）；dataset_path→ReplayPolicy 且 execution_horizon 必须为正（`:112-120`），modality 配置支持 .py（import 副作用 `:125-131`）与 .json（`:34-50`，识别误传数据集 meta/modality.json），未提供则查注册表（`:140-151`）；皆无报错。可选套 Sim wrapper（`:162-165`）后 `PolicyServer` 起服务（`:167-175`）。

**server_client.py 侧**。`PolicyServer.__init__`（`:155-171`）建 `zmq.REP` 并 bind，注册五端点 ping/kill/get_action/reset/get_modality_config（`:173-182`）。`run`（`:241-273`）同步循环：recv→`MsgSerializer.from_bytes`→可选 api_token 校验（`:250-254`）→按 `request["endpoint"]` 分发（缺省 get_action）→回包；异常不崩服务、回 `{"error":...}`（`:268-273`）。`MsgSerializer`（`:33-103`）是安全亮点：直接驱动 msgpack 而非 msgpack_numpy 高层封装——后者把自定义 hook 链在自身编解码之后，object-dtype ndarray 与伪造 `{nd:True, kind:'O'}` 包会在 hook 介入前进 `pickle.loads`（`:36-44`）；编码侧拒 object-dtype 数组（`:65-71`）、解码侧对 truthy `nd` 值拒绝（`:86-102`），把 `allow_pickle=False` 钉死在传输边界。

## 三、外部连接

Gr00tPolicy 上游依赖 05 篇契约（EmbodimentTag 分层、modality_configs、VLAStepData）与训练期产物（processor 目录、statistics.json——`experiment.py:254-256` 注释明说部署期被消费）。下游三类客户端：`PolicyClient`（REQ socket+15s 超时 `:281-294`）、仿真评估器（经 Sim wrapper）、真机控制进程；`register_endpoint` 可扩展端点（`:222-231`）。`run_gr00t_server.py` 同时是 ReplayPolicy 唯一 CLI 入口（回放轨迹做闭环验证）。

## 四、数据流

一次 get_action 全链：机器人侧组装观测（video uint8 `(B,T,H,W,C)`、state float32 `(B,T,D)`、language 双层 list）→ PolicyClient msgpack 序列化（ndarray 走安全信封）→ REP 循环解包 → `BasePolicy.get_action` 模板：check_observation → `_get_action`（unbatch→VLAStepData→processor 编码→collate→bf16→`model.get_action`→decode_action 反归一化出物理单位）→ check_action → 回包 → 控制端拿 `(B,horizon,D)` 动作 chunk，取前 k 步执行、步进后再请求。

## 五、设计决策

1. **校验即接口文档**：`check_observation`/`check_action` 用几十个断言把 dtype/形状契约写成可执行规格（`:276-293` 等），strict=True 每次都跑——控制端接错格式第一帧就得到精确报错。
2. **decode_action 需要当前 state（`:421-426`）**：RELATIVE 动作语义是"相对当前 state 的增量"，反归一化须知道锚点——这解释了 ActionConfig 为何有 state_key 字段（05 篇 `types.py:81`）。
3. **全程 bfloat16**（模型 `:111`、输入 `:413`）吞吐优先；输出转 float32 保证与控制系统的数值接口稳定（`:429-431`）。
4. **processor 子目录回退（`:118-123`）**：对齐训练期保存布局（07 篇），微调产物零手工搬运即可被 server 加载；同时兼容 processor 放根目录的 HF 惯例。
5. **msgpack_numpy 的 pickle 边界（`server_client.py:33-103`）**：自建安全链正面处理"反序列化=代码执行"威胁——机器人网络接口尤其重要。
6. **同步 REP 而非 PUB/SUB**：单策略单请求语义最简，吞吐靠动作 chunk（一次出 16 步）而非服务端并发。

## 六、新人提示

- 观测形状最常踩坑：视频五维 `(B,T,H,W,C)` 且 uint8（别预归一化成 float），state/language 必须带 batch 维；T 维精确等于 `len(delta_indices)`（单帧 T=1）。
- language 是双层 list `[[指令]]`，Sim wrapper 侧是 `(B,)` tuple——两套格式别混（`gr00t_policy.py:233-235` vs `:533-536`）。
- RELATIVE 动作执行前要加当前 state（delta 语义）；ABSOLUTE 直接下发。horizon 尾部预测误差大，常见做法执行一半就重推理。
- 报错即自助文档：embodiment 不匹配列出该 checkpoint 全部支持标签与 hint（`:154-160`）；默认端口 5555（`run_gr00t_server.py:31`），`kill` 端点可远程优雅停服（`server_client.py:175`）。
- 验证部署先用 ReplayPolicy 分支（`--dataset-path`+`--execution-horizon`）回放轨迹，再切真模型。
