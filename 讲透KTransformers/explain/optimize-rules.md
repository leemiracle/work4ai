# YAML 规则引擎精讲：optimize/optimize.py

> 文件：archive/ktransformers/optimize/optimize.py（163 行）+ optimize_rules/ 下 40+ YAML（无 rule.py，规则全是数据文件）。经典框架的"组装大脑"：YAML 声明哪层哪子模块换什么算子类、放 CPU 还是 GPU，本文件把声明编译成真实模型。

## 1. 角色定位

13 层架构的 layer:optimize（优化层），是"模型结构层"（models/modeling_*.py 的 HF 原始模型）与"算子层"（operators/）之间的编译器。不含计算逻辑，只做规则匹配、模块替换、权重装载三件事。顶层 ktransformers.py 薄壳、local_chat.py、balance_serve.py 都 import 它（图谱 edges），是 legacy 路径的事实入口。

## 2. 内部结构

四个函数，职责分离：
- gen_optimize_config（L67-118）——规则引擎核心。DFS 遍历 module._modules，每模块按 YAML 顺序扫规则：match 可含 class（动态 import 后 isinstance）与 name（re.search 正则），同时给出须同时满足；命中即写入 out_data[module_name] 并 break（L101）——首条命中即止。已有 "default" 条目可被后续规则升级（L96-98：换 class、merge kwargs）；recursive（L99）控制是否下钻。未命中落 L103 兜底：class="default"，generate_device=prefill_device=default_device。
- inject（L28-54）——执行替换。按前缀命中项 __import__ 动态加载点路径类（L39），先写旁路 gguf_loader.tensor_device_map[key]=kwargs（L37），再构造注入类并 set_module 换树（L46）；class=="default" 只登记 device map 不换类。
- del_meta（L56-65）：装载后删残留 meta 参数。
- optimize_and_load_gguf（L129-163）——总编排：yaml 读规则 → gen_optimize_config → ModelLoaderFactory.create_loader（L150）选 GGUF/SafeTensor loader → with torch.device("meta"): inject（L151）→ 预载 lm_head（L154）→ load_weights（L155）→ del_meta+empty_cache。

## 3. 外部连接

依赖：custom_loader.py（ModelLoaderFactory）、custom_gguf.py（translate_name_to_gguf）、utils.py（set_module/load_weights）。被依赖：local_chat.py、balance_serve.py、ktransformers.py；唯一生产调用点是 local_chat.py:local_chat → optimize_and_load_gguf（L139）。optimize_rules/ 按硬件分族：根目录 30+ 主流 YAML，npu/rocm/xpu 子目录是异构变体——同一引擎、不同数据。

## 4. 数据流：一次 optimize_and_load_gguf 的流转

从 local_chat.py 起步（L84-139）：
1. meta 建模：torch.device("meta") 下按 config.architectures[0] 建模型（L113）——只有结构无权重，规则匹配靠类类型不靠权重。
2. 选规则：default_optimize_rules（L58-64）按架构名映射 YAML（DeepseekV3ForCausalLM → DeepSeek-V3-Chat.yaml），缺省则交互询问。
3. 编译：以该 YAML 为例：mlp 正则 + class DeepseekV3MoE → 换 KDeepseekV3MoE；其下 .mlp.experts → KTransformersExperts，kwargs 的 prefill_op/generate_op/out_device 正是 experts.py EXPERTS_MAP 的键，且带 recursive: False；self_attn → KDeepseekV2Attention（GPU）；非 kv_b_proj 的 Linear（负向前瞻正则）→ KTransformersLinear；embed_tokens → default 放 CPU。
4. 注入：仍在 meta 上下文 inject 换树，kwargs 灌进 tensor_device_map——default 权重之后靠它（load_cur_state_dict 的 get_device，utils.py L286）定落点。
5. 装载与收尾：load_weights（utils.py L335）递归——遇 BaseInjectedModule 调自管 load()（如 KExpertsCPU.load 走 mmap），普通模块反量化到目标设备；lm_head 先单独装；del_meta 清壳。模型从此是"GPU attention + CPU experts"的注入树。

## 5. 设计决策

- meta 两阶段：规则只关心类型与名字，meta 建模让匹配零成本，也避免先装满再换的双倍内存。
- 规则是数据不是代码：设备分配是部署决策而非算法——AMX、marlin、multi-gpu-4/8 版全是平行 YAML，改部署不动 Python。
- 首条命中即 break + default 可升级：允许"宽规则打底、窄规则补刀"的叠写，代价是顺序敏感。
- recursive: False 不可或缺：KTransformersExperts 自己经 EXPERTS_MAP 构造内部执行器，inject 继续下钻会重复替换。
- tensor_device_map 旁路：注入类的设备偏好必须泄漏给不换类的 default 权重，否则 embed_tokens 这类留底模块全挤上 GPU。

## 6. 新人提示

- 切入：拿 DeepSeek-V3-Chat.yaml 对照 gen_optimize_config 手跑前缀匹配，再看 inject 的 set_module，最后跟到 KTransformersExperts.__init__ 收 kwargs——三步把 YAML 每字段落到代码。
- name 是 re.search 非 fullmatch，忘 ^...$ 锚点会误匹配子串；YAML 里 ^model\\.layers\\. 双反斜杠是转义；规则顺序也改变结果：宽 Linear 规则放 MoE 规则前可能吃掉命中。
- class 路径拼错要到 inject 动态 import（L39）才炸，报错点离 YAML 很远。
