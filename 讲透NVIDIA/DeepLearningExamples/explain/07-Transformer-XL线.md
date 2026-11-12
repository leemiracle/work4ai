# 07 · Transformer-XL 训练评估线：train/eval/mem_transformer

## 角色定位

Transformer-XL 目录（`PyTorch/LanguageModeling/Transformer-XL/`）是本仓语言建模线的"活化石级"范例：它同时展示了 NVIDIA 如何把一个学术开源模型（kimiyoung/transformer-xl，Apache-2.0）工程化成可复现的基准训练管线——分段循环记忆机制、相对位置编码、自适应 softmax 这些论文组件原样保留，外面套上 apex/原生 AMP 双模、L2 持久化、GPU 亲和性、DLLogger 合规报告四层 NVIDIA 定制。仓内 NOTICE 文件明确声明代码汇聚自四个上游（transformer-xl、awd-lstm-lm、cybertronai/transformer-xl、cybertronai/pytorch-lamb）。三个核心文件分工：`mem_transformer.py` 是 Eager 版模型本体（854 行），`train.py` 是训练主控（1151 行），`eval.py` 是推理评估与 TorchScript 导出入口（524 行）；另有 `inference/mem_transformer_jit.py` 平行实现一套 TorchScript 兼容组件供 `--type torchscript` 路径使用。

## 内部结构

`mem_transformer.py` 的组件栈自底向上：`PositionalEmbedding`（mem_transformer.py:29，sinusoidal 编码）→ `PositionwiseFF`（:48，两层 1x1 卷积等价 MLP）→ `MultiHeadAttn`（:84，标准注意力基类）→ `RelMultiHeadAttn`（:159，实现 `_rel_shift` 对角平移把相对位置分数对齐到正确 query-key 偏移）→ `RelPartialLearnableMultiHeadAttn`（:229，拼接 mems 记忆段、融合内容-内容/内容-位置/位置-内容/全局偏置四项分数，是记忆跨段注意力的落点）与 `RelLearnableMultiHeadAttn`（:308）两个变体。解码层三个类全部**直接继承 nn.Module 而非相互继承**：`DecoderLayer`（:395，抽象占位基类）、`RelLearnableDecoderLayer`（:412）、`RelPartialLearnableDecoderLayer`（:432，默认层类型）——图谱 languageNotes 钉版：这个"变体不继承基类"的写法在 jit 版同样存在，目的是降低 TorchScript 追踪复杂度。`AdaptiveEmbedding`（:453）按词频 cutoffs 把词表切簇、低频簇共享小嵌入再投影升维；`MemTransformerLM`（:516）主体中 `init_mems`（:643）与 `_update_mems`（:652）维护跨段记忆环形缓冲，`forward`（:779）返回 (loss, new_mems) 二元组。

NVIDIA 定制点有三处值得点名。其一，模块级 `add_and_scale`（mem_transformer.py:25）把"加法+缩放"压成单函数调用，在两处 attn_score 计算处（:274、:361）复用，是相对原版的显式化微优化。其二，文件尾部 `if __name__ == '__main__':` 自检块（mem_transformer.py:803）：用 argparse 造一组迷你超参，构造 B=4、tgt_len=mem_len=36 的随机数据，`for div_val in [1, 2]` × `d_embed in [200, 100]` 四组合各跑一次前向并打印参数量——模型文件自带单元自检，不依赖任何测试框架。其三，`train.py` 顶部的 apex 回退（train.py:34-37）：`try: from apex import amp / except ModuleNotFoundError: warnings.warn('APEX AMP is unavailable')`——apex 缺席不致命，后续按 `args.amp in ('apex','pytorch')` 分流（:114 定义 choices）。

## 外部连接

模型依赖四个 utils 模块：`utils/data_parallel.py` 的 `BalancedDataParallel`（:54，继承 DataParallel）实现 gpu0_bsz 不均分批——GPU0 因承担额外同步开销而少拿 batch；`utils/gpu_affinity.py` 经 pynvml 读拓扑把进程钉到 NUMA socket（socket/single/single_unique/socket_unique 四模式）；`utils/distributed.py` 的 `init_distributed`（distributed.py:21）按 WORLD_SIZE 环境变量判定是否分布式；`utils/exp_utils.py` 提供 AverageMeter/TimeoutHandler/benchmark 等 15 个训练辅助（:30 起）。`lamb.py` 提供 LAMB 大批量优化器的 Python 版与 `torch.jit.script` 加速版 JITLamb 双实现，train.py 以 `--optim lamb/jitlamb` 选择。数据侧接 `data_utils.py` 的 `get_lm_corpus` 工厂与三种迭代器（LMOrderedIterator 定长滚动切批供 wt103；LMShuffledIterator 句级乱序供 enwik8/text8；LMMultiFileIterator 供 1B-words）。eval.py 与 train.py 对 MemTransformerLM 的导入方式不同：eval.py 是 main() 内按 `args.type` 分支的**延迟导入**（图谱钉版：静态 import 扫描会漏这两条边），pytorch 版与 jit 版运行时才决定加载哪个。

## 数据流

训练流：`main()`（train.py:706）先设 GPU 亲和性与 `torch.cuda.set_device`，随即调 `l2_promote()`（train.py:719），再 `init_distributed`；`world_size = get_world_size()` 后全局 batch 重算为 `local_batch_size * world_size`（:754-757）。模型包装三态（:910-923）：分布式用 `DistributedDataParallel`；单机且 `--gpu0_bsz >= 0` 时换 `BalancedDataParallel(args.gpu0_bsz // args.batch_chunk, ...)`；否则裸 `nn.DataParallel(model, dim=1)`。步进核心 `train_iteration`（:475）：数据 contiguous 后可选 `--swap_mem` 把 mems 在 CPU/GPU 间换入换出（:481-483、:490-492），`torch.cuda.amp.autocast` 仅当 `args.fp16 and args.amp == 'pytorch'` 时启用（:484-487），反传按 amp 实现三分支——pytorch 原生走 `scaler.scale(loss).backward()`，apex 走 `amp.scale_loss(loss, optimizer, delay_unscale=...)` 上下文（:493-499）。梯度裁剪同样分流：apex 路径须对 `amp.master_params(optimizer)` 裁剪（:553-554）。`batch_chunk > 1` 时对 DDP 用 `no_sync()` 攒梯度（:535-536）。checkpoint 保存三态 amp state（:303-308：scaler.state_dict / amp.state_dict / None），重启恢复时对称回读（:991-996），RNG 状态经 `get_default_rng_states/set_default_rng_states` 全设备保存保证续训随机序列一致。评估流：eval.py main()（:274）同样调 `l2_promote()`（eval.py:291），evaluate（:171）跨段传 mems 跑完测试集，末尾可 `torch.jit.script` 导出 TorchScript。

## 设计决策

四条决策线值得咀嚼。①**AMP 双轨制**是 2020 年前后 apex → 原生 torch.cuda.amp 过渡期的典型工程形态：import 级 try/except 让 apex 成为可选依赖，运行级 choices 让用户按容器内 apex 可用性切换，代价是每个精度敏感点（autocast、backward、clip_grad、state_dict）都要写两遍——今天迁移到纯原生 AMP 可删掉约半数分支。②**l2_promote 的实现**（exp_utils.py:221-227）绕过 PyTorch 直接 `ctypes.CDLL('libcudart.so')` 调 `cudaDeviceSetLimit(0x05, 128)`——0x05 是 cudaLimitMaxL2FetchGranularity，把 L2 取粒度设到 128 字节，并用 `cudaDeviceGetLimit` 回读 assert 确认生效；这是 PyTorch 没有暴露的 CUDA 运行时旋钮，纯 NVIDIA 硬件栈优化钩子，train/eval 都在设备初始化后立刻调用。③**DecoderLayer 变体平行继承**牺牲了代码复用（三个类各自的 forward 组装逻辑高度相似）换取 TorchScript 兼容与继承链扁平，与 jit 版的设计动机一致。④**自检块进生产文件**（mem_transformer.py:803）是上游学术仓库风格的残留，NVIDIA 未清除反而保留——好处是 `python mem_transformer.py --cuda` 十秒内冒烟验证模型可跑。

## 新人提示

入手顺序建议：先跑 `python mem_transformer.py`（不加 --cuda 也可）看自检块四组合前向通过，再读 train.py 的 main() 骨架，最后精读 `RelPartialLearnableMultiHeadAttn._forward` 理解 mems 拼接与四项分数。三个易踩的坑：① apex 回退只是 warn 不报错，若容器没装 apex 而你默认 `--amp apex`，会在初始化处才爆 AttributeError——先看启动日志有没有 'APEX AMP is unavailable'；② `--gpu0_bsz` 仅单机 BalancedDataParallel 路径生效，分布式下该参数被忽略，误调它调不动吞吐；③ eval.py 的延迟导入意味着 grep 静态依赖时会低估 pytorch/jit 两版的耦合，改动模型接口需同步检查 `inference/mem_transformer_jit.py` 这个平行宇宙。性能复现时别忘了 l2_promote 的 assert——在不支持该 limit 的平台上它会直接断言失败，这是"仅支持 NVIDIA 平台"的字面执行。
