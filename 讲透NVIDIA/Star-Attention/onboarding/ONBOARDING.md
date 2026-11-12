# Star-Attention 新人上手指南（ONBOARDING）

> 仓库：NVIDIA/Star-Attention（commit dadb4be9，本地 /usr-data/data2/repos/agent-repos/NVIDIA/Star-Attention）
> 配套论文：Star Attention: Efficient LLM Inference over Long Sequences（arXiv 2411.17116，ICML 2025，README.md:294-300 引用）
> 图谱规模：141 节点 / 230 边 / 6 层 / 8 步 tour，fingerprints=51 文件@dadb4be9

## 一、项目定位与解决的问题

Star-Attention 是 NVIDIA 开源的**长序列 LLM 推理加速**参考实现：把"整段上下文一次性全注意力"拆成两阶段——Phase 1 各主机只对本地 chunk 做局部注意力（无需跨机通信），Phase 2 把 query 复制到所有主机、各自对本地 KV 算注意力后，用 log-sum-exp（LSE）在线合并出全局注意力（README.md:232-289 给出完整数学表述）。论文口径的收益是：RULER 16K-128K 上保持 Ring Attention 97-100% 精度的同时，推理加速 1.2x-4.7x（README.md:81 Table 1）。

它**不是训练库**：核心 kernel `StarFlashAttnFunc` 只定义了 forward（star_flash_attn/star_flash_attn.py:55-93），没有 backward，整个仓库也没有训练入口；两套 kernel 都直接 import flash-attn 的私有 API `_flash_attn_forward`（star_flash_attn.py:18、ring_flash_attn/ring_flash_attn.py:18），版本钉死在 flash-attn==2.6.3 + transformers==4.44.0 + torch==2.3.1（requirements.txt:2/5/6）。看懂这份代码的正确姿势是"分布式推理系统工程"，而非可微算法库。

## 二、总体架构与分层

图谱 6 层自顶向下（onboard-input.json layers）：

- **L01 项目入口与启动**（7 文件）：README.md（310 行）、launch.sh、requirements.txt、scripts/download_hf_model.py（snapshot_download 下载 HF 模型，scripts/download_hf_model.py:34/40 支持 --token）。
- **L02 星注意力核心实现**（11 文件）：`star_attention/` 包——modeling_llama.py（718 行，HF Llama 改造）+ modeling_flash_attention_utils.py（分发层）+ star_flash_attn/（星核：定长/varlen + LSE 工具）+ ring_flash_attn/（环形 KV 对照组）。
- **L03 推理基线与主入口**（4 文件）：model.py（395 行三基线）、run_star_attn_inference.py（233 行主入口）、run_ruler.py / run_babilong.py（两基准作业生成器）。
- **L04 RULER 数据生成**（17 文件）：ruler/data/prepare.py 总装 + synthetic/ 五类生成器（niah/qa/variable_tracking/common_words/freq_words）+ tokenizer.py。
- **L05 RULER 评测与配置**（5 文件）：eval/evaluate.py（238 行）+ synthetic_task_config.yaml（13 任务）+ gather_results_ruler.py。
- **L06 BabyLong 评测套件**（7 文件）：babilong/prompts.py（455 行模板库）、metrics.py、gather_results_babilong.py（热图）。

依赖方向很干净：L03-06 只消费 `star_attention/` 的一个出口——`from star_attention import LlamaForCausalLM`（model.py:33，star_attention/__init__.py:16 re-export），kernel 与 HF 之间的缝合全部封在 L02 内部。

## 三、核心子系统深讲

### 3.1 三基线编排（model.py）

`DistributedInferenceBaseModel`（model.py:24）统一装模型：`LlamaForCausalLM.from_pretrained` + bfloat16 + `attn_implementation='flash_attention_2'`（model.py:41-47），并按 rank 切分 GPU（每 rank 分到 `cuda数量/local_world_size` 张卡，model.py:67-72）。三个子类：

- **StarAttentionModel**（model.py:174）：block_size 缺省=上下文长度/世界数（model.py:183-184），上下文补零到 block_size 整数倍（model.py:187-189）；Phase 1 里从第二个块起把第一块的前 anchor_block_size 个 token 拼在块前（model.py:209-213，缺省 anchor=整个第一块，model.py:199-200），跑模型时传 `num_ring_steps=0, enable_star_attn=False`（model.py:220-221）即"零步环形注意力=纯局部"，算完把 anchor 段 KV 丢弃（model.py:225-228）、块内 KV 沿序列维拼接（model.py:230-236）。
- **RingAttentionModel**（model.py:269）：pad 到世界数整数倍（model.py:281-283），每 rank 恰一块（断言 model.py:293），`num_ring_steps=-1` 表示启用完整环形（model.py:302）；Phase 2 直接复用 Star 的生成循环。
- **DenseAttentionModel**（model.py:337）：**不继承**基类，走 transformers 原生 `AutoModelForCausalLM`（model.py:343），context+query 拼成整条 prompt（model.py:389）。

Phase 2 生成循环在基类 `_generate_output`（model.py:118）：每步 greedy argmax（model.py:145-147），模型调用带 `enable_star_attn=True`（model.py:137），且只有最后一个 rank 更新 KV cache（model.py:141-142）——最后一 rank 就是论文里的"query host"。

### 3.2 HF 注入层（modeling_llama.py）

`StarLlamaFlashAttention2` 继承 HF 的 `LlamaFlashAttention2`（modeling_llama.py:74），只改三处：① forward 签名加 `num_ring_steps/enable_star_attn` 两个穿透参数（modeling_llama.py:91-92）；② 星注意力不变式校验——启用时非最后 rank 不得带非空 KV cache（modeling_llama.py:100-105）；③ KV cache 写入策略分叉：`enable_star_attn` 且非最后 rank 时直接**用旧 cache 替换当前 key/value**（不追加，modeling_llama.py:136-137），否则正常 update（modeling_llama.py:141-143）。注意力计算则整体委托给分发层 `_flash_attention_forward`（modeling_llama.py:179-192）。注意模块级 `RANK/WORLD_SIZE` 在 import 时就要求 dist 已初始化（modeling_llama.py:67-71）——这是"必须 torchrun"的根因（见 README 勘误）。`LLAMA_ATTENTION_CLASSES` 把 `flash_attention_2` 槽位换成星注意力头（modeling_llama.py:203-207），DecoderLayer/Model/ForCausalLM 逐层把两个参数穿下去（modeling_llama.py:272-273、419-420、611-612）。

### 3.3 两套 kernel 与分发层

分发层 `_flash_attention_forward`（modeling_flash_attention_utils.py:40）按 `enable_star_attn` 选星核、否则一律落 ring 核（modeling_flash_attention_utils.py:110/137/155）——**局部注意力=环形注意力取 0 步**是本仓库最妙的一处复用；`num_ring_steps` 只在非星模式下传入（modeling_flash_attention_utils.py:98-99）。星核 `_star_flash_attn_forward`（star_flash_attn.py:23）：本地 flash-attn（star_flash_attn.py:26）→ `dist.all_gather` 收全 rank 的 out 与 LSE（star_flash_attn.py:41-42）→ 逐 rank 在线 softmax 合并（star_flash_attn.py:47-48）。环核 `_ring_flash_attn_forward`（ring_flash_attn.py:22）：P2P 环形传 KV 共 world_size-1 步（ring_flash_attn.py:37-38），通信与计算重叠（先 send_recv+commit 再算再 wait，ring_flash_attn.py:49-51/69-75），causal 时只算 step≤rank 的块（ring_flash_attn.py:53）。LSE 合并数学在 utils：`_update_out_and_lse` 的 log 空间公式（star_flash_attn/utils.py:33-34，@torch.jit.script 加持 utils.py:23-24），与 README.md:268-289 的 sum-of-exponents 表述等价（log 空间防溢出版）。

## 四、关键数据流（一条样本的端到端旅程）

以 RULER 一次 star 推理为例：

1. **作业生成**：run_ruler.py 按任务×序列长度×attn_type 拼 `torchrun --nnodes --nproc_per_node` 命令（run_ruler.py:147），先跑数据生成（run_ruler.py:166-176）再跑推理（run_ruler.py:180-192），最后 evaluate（run_ruler.py:195-197）；命令落盘成 .sh 由 `os.system` 执行（run_ruler.py:94-101）。
2. **数据侧**：prepare.py 从 synthetic_task_config.yaml 读任务定义（ruler/data/prepare.py:72-77，13 任务=8 种 NIAH + vt + cwe + fwe + qa_1/qa_2，yaml:16-119）；niah 生成器按针型（数字/单词/UUID）造样本（ruler/data/synthetic/niah.py:110-125、136、218）；token 计数用 tokenizer 封装（ruler/data/tokenizer.py:19/26）。
3. **推理**：torchrun 拉起 N 进程 → init_distributed 仅在有 RANK 环境变量时 `dist.init_process_group('nccl')`（run_star_attn_inference.py:36-48）→ 按 attn_type 装模型（run_star_attn_inference.py:64-105，star 要求 block_size>0 断言 :93）→ 逐行读 jsonl、断点续跑按 index 去重（run_star_attn_inference.py:51-61、145-148）→ rank0 写结果、每样本 barrier 同步（run_star_attn_inference.py:165-186）。
4. **评测聚合**：evaluate.py 做预测后处理（ruler/eval/evaluate.py:70）并调 YAML 配的 metric_fn（evaluate.py:120），匹配函数是 string_match_part/all（ruler/eval/synthetic/constants.py:25/29）；gather_results_ruler.py 按序列长度汇总（ruler/gather_results_ruler.py:52）。BabyLong 线对称：prompts.py:20 get_formatted_input 套模板、metrics.py:40/51 预处理+比对、gather_results_babilong.py:38/52 画热图。

## 五、构建、运行与入口

- **依赖安装**：`pip install -r requirements.txt`（torch 2.3.1/transformers 4.44.0/flash-attn 2.6.3 三个硬钉）+ `nltk.download('punkt_tab')`（README.md:116-125）。
- **一键评测**：launch.sh 是权威配置样例——BENCHMARK 变量切 ruler/babilong（launch.sh:19-37），dense 跑 16-64K、ring 跑 128K（launch.sh:45-46），star 四档 bs=4096/8192/16384/16384 对应 16K/32K/64K/128K（launch.sh:49-52）。
- **自定义数据**：输入 jsonl 需 input_context/input_query/output 字段（README.md:203-211），跑 run_star_attn_inference.py（README.md:215-223）——但注意勘误③：star/ring 必须在 torchrun 下跑。
- **多机/多进程**：-np=每节点并行进程数（每进程分到 8/np 张卡），-nn=节点数，总数 nn*np（README.md:172-186）。

## 六、设计决策与已核实勘误

**决策要点**：① 局部注意力复用环核的 0 步特例，避免第三套 kernel；② 星核在**输出端**合并（all_gather out+LSE，一次同步），环核在**输入端**循环 KV（world_size-1 步 P2P）——这是 star 快 1.2-4.7x 的全部秘密；③ 只改注意力头不动权重，任何 HF Llama checkpoint 免训练即用；④ eager/sdpa 槽位保持 HF 原类（modeling_llama.py:203-207），退化路径完整。

**勘误**（详见上级 README.md 勘误清单）：① attn_type 文档串写 `['dense','star','starkv']`，实现是 dense/ring/star（run_star_attn_inference.py:124 vs 72/81/90）；② `num_ring_steps` docstring 称默认 -1，签名默认 0（modeling_flash_attention_utils.py:82-83 vs 53）；③ README 自定义数据示例裸 python 起 star 会因 dist 未初始化崩溃（run_star_attn_inference.py:39-40、model.py:80、modeling_llama.py:67-71）；④ Dense 不继承分布式基类（model.py:337）；⑤ launch.sh:52 的 128K 用 bs=16384=1/8 上下文，与 README.md:91"统一 1/4"表述不一致；⑥ README:289"每 token 只通信一个标量+一个向量"与实现的 all_gather 全量 out+LSE（star_flash_attn.py:41-42）口径不同。

## 七、新人上手路线

1. **第 1 小时**：README.md:230-289 啃两阶段数学 → star_flash_attn.py 全文（164 行）→ star_flash_attn/utils.py:23-58（LSE 合并）。三者构成算法最小闭环。
2. **第 2 小时**：model.py 走 StarAttentionModel.__call__（model.py:240-266）一条线，对照 Phase1/Phase2；再看 modeling_flash_attention_utils.py:98-158 弄懂三分支路由（padding varlen / position_ids varlen / 定长）。
3. **第 3 小时**：对照读 star_attention/ring_flash_attn/ring_flash_attn.py:22-79 + ring utils 的 RingComm（star_attention/ring_flash_attn/utils.py:103-135）与 get_default_args 反射调用（star_attention/ring_flash_attn/utils.py:29），理解"输入端循环 vs 输出端合并"。
4. **动手验证**：launch.sh 改 BENCHMARK 跑通小模型（建议先 -a dense 单进程冒烟，再 torchrun 起星注意力）；用 scripts/time_inference.py 对比三模式吞吐。
5. **避坑**：flash-attn 私有 API 锁 2.6.3（升级 transformers/flash-attn 大概率 import 断裂）；RingFlashAttnFunc 不支持 alibi（ring_flash_attn.py:102 assert）；`prepare_inputs_for_generation` 里 num_ring_steps 缺省 -1（modeling_llama.py:715）只影响 model.generate() 路径，本仓库手写循环不走它。

（完 · 锚点 45 个，全部经源码行号核实 @dadb4be9）
