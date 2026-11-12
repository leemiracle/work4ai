# 03 · NCCL 传输与权重切分

## 1. 角色定位

这一层兑现 README"GPU 直连权重流、无磁盘/序列化"的承诺：`transport/tensor` 是星型拓扑 NCCL 点对点原语；`transport/model` 在其上实现三种整模型搬运策略（`--transfer-mode` 的 fused/unfused/grouped）；`sharding/` 的 PolymorphicMesh 支持同批 GPU 换轴名重排；`models/` 把 JSON 映射编译成 proto，承担 vLLM↔JAX 双向变换与 checkpoint 装载。

## 2. 内部结构（行号锚）

- **NcclTransport ABC**（nccl_base.py:73）：send/gather/scatter/recv/wait 五原语；nccl_type（:36-70）映射 dtype 到 NCCL 枚举；unique id 经 A85 编码走 gRPC、decode 返回 bytes 兼容新版 CuPy（:76-87）。
- **NcclStarTransport**（nccl_star.py:38）：`configure`（:46-66）按 trainer_ranks>=rollout_ranks 选 fan-in/fan-out（:54）、生成 min(两侧) 个 unique_id（:55-58）。fan-in：k=TRAINER//ROLLOUT、world_size=k+1（:86-87），设备按 k 分批（:89）、rank=dev.id%k+1、0 号留星心（:93-95）；fan-out 则 JAX 每 GPU 都是 rank 0 星心（:107-115）；vLLM 侧 create_rollout_transport（:120-141）互为镜像；收发面 send/gather/scatter 及 *_grouped 见 :150-358。
- **三种 model transport**：fused 每参数一个 buffer_callback、全模型一次 jit（nccl_fused.py:121-167）；grouped 全部张量拼 tuple、单 shard_map+单次 group 发送（nccl_grouped.py:178-184、:110-130），fan-out 也支持（:286）；unfused 逐参数 reshard+逐 shard send（nccl_unfused.py:50-62）。
- **PolymorphicMesh**（mesh.py:26-33）：构造时把每维拆成质数因子轴（:31）；`view()`（:133-157）按质数库存（:139-141）合成新轴名。
- **models/mapping_util.py**：load_mapping_from_json（:197-299）展开 {layer} 模板（:257-273）；add_sharding_specs（:302-349）调 vLLM `collective_rpc("get_tp_sharding_specs")`（:303）、断言各 TP rank specs 一致（:312-319）、回填 tp_sharding 与 replication_count（:343-347）。

## 3. 外部连接（图谱边佐证）

param_mapping.proto schema 节点 fanIn=8/fanOut=10：被 mapping_util、三个 model transport、extension.py、checkpoint.py 引用。nccl_star.py hub fanIn=6/fanOut=3——vLLM 侧 extension.py 经 transport/tensor/__init__.py:22-29 的 get_transport_class 注册表拿到同一实现，两端通信子参数天然一致；VLLMTransferEngine→三 transport 组合边（vllm_transfer_engine.py:76-104）是 L13"模型切分会话"层骨干。

## 4. 数据流

发送侧（grouped fan-in）：mapping_specs 带出变换与 tp_sharding；_fused_transfer 逐参数 slice→replicate→transpose→reshape（nccl_grouped.py:142-150）、with_sharding_constraint 重排到 (dst,src) 耦合 mesh（:153-166）、shard_map+buffer_callback 在每 GPU 回调 Python 单组 ncclSend 发 peer 0（:110-130）。接收侧（extension.py）：update_weights_grouped 按 mapping 算 shard 形状（:219-241）、gather_grouped/recv_grouped 一把收完（:245/:271）、commit_staged_weights 走 load_weights（:284-291）。反向流 load_checkpoint_to_jax 扫 safetensors（checkpoint.py:121）、按 vllm_param.transform 逆变换（:154-156）。布局翻译靠映射 JSON：8B 版 mesh_axes=["fsdp","tp"]（llama3_8b_param_mapping.json:2）、num_layers=32（:3）、q_proj transpose [1,2,0]+reshape [-1,4096]（:87-92）、k_proj replication_axis:2（:105-110）；1B 仅 16 层（llama3_1b_param_mapping.json:3）。

## 5. 设计决策

- **星型而非全互联**：JAX TP 与 vLLM TP 不必相等，min(两侧) 个 communicator、每个 k+1 进程（nccl_star.py:54）。
- **变换顺序钉死 slice→replicate→transpose→reshape**（nccl_grouped.py:142 注释），replication 在 transpose 前、沿原始 JAX 轴（param_mapping.proto:76-77）——KV head 复制正确性的关键。
- **grouped 是默认**（vllm_transfer_engine.py:47、:63）：单 jit+单 NCCL group 摊平小张量开销；unfused 是逐参数基线；fused 是早期实现，只认 parallelism==ROLLOUT_RANKS 或 0/1（nccl_fused.py:140-149）、fan-out 未实现（:169-172），GQA K/V 复制场景必 RuntimeError。
- **vLLM 侧强制 V1 loader**：is_sharded_weight=True（extension.py:73-75）把收到的张量当"已切分"；为此把 UnquantizedLinearMethod 移出 WEIGHT_LOADER_V2_SUPPORTED（:61-63）。

## 6. 新人提示（坑/勘误）

- **WeightTransferGateway Protocol 三副本**：nccl_fused.py:36-40、nccl_grouped.py:36-40、nccl_unfused.py:36-40 同文重复，改协议要同步三处。
- **integrations/simple/__init__.py:19 broken import**：import 自不存在的 standalone 包，import 即 ImportError，Llama3 不可用。
- **vllm/llm.py:63 torch NameError**：gemma 修复分支用 torch.tensor 但从未 import torch，gemma + vLLM<=0.9.1 必炸（门槛 :59）。
- dtype 缺省静默按 bfloat16 收（extension.py:189）：精度不匹配不报错而是读出乱码。
- add_sharding_specs 以 sentinel 999999 表示无切分（mapping_util.py:339）；VocabParallelEmbedding 刻意跳过 sharding spec（extension.py:95-101，整块广播+loader 裁剪），故 embed_tokens 无 transform 也能工作。

---
本文 3489 字符（去空白），26 个行号锚。
