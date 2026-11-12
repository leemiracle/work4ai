# 05 · dataset.py + distributed.py —— 数据管道与梯度同步

> 锚均从源码核实（commit 9487a8db）。distributed.py 整体改编自 NVIDIA/waveglow（版权头 BSD-3，对应 incl_licenses/LICENSE_1）；dataset.py 为本仓自写。

## 角色定位

这两个文件是训练线的两根支柱：dataset.py 决定"模型看到什么"（DNS-2020 干净/带噪对的文件系统布局假设），distributed.py 决定"多卡如何一起看"（DDP 普及前的手写数据并行梯度同步与多进程启动器）。

## 内部结构

**dataset.py**（119 行）：
- CleanNoisyPairDataset（dataset.py:24-85）：构造按 subset 分支——training 用 `training_set/clean/fileid_{i}.wav` 与 noisy 同名配对（L41-43，数量对齐断言 L37-39）；testing 面向 DNS `datasets/test_set/synthetic/no_reverb` 目录（L47），sortkey 提取文件名尾部两段排序保证 clean/noisy 同序（L46/52-57），强制 crop=0（L60）。
- __getitem__（dataset.py:65-82）：torchaudio.load 读对（L67-68）→ 等长断言（L70）→ 训练分支随机裁剪（L76-79）→ unsqueeze 回 (1,L)。
- load_CleanNoisyPairDataset（dataset.py:88-101）：DataLoader 工厂，num_workers=4（L93），多卡 DistributedSampler、单卡 shuffle（L95-99）。

**distributed.py**（189 行）五函数：
- reduce_tensor（distributed.py:42-46）：all_reduce 求和除卡数。
- init_distributed（distributed.py:48-58）：init_process_group + set_device 绑卡。
- _flatten/_unflatten_dense_tensors（distributed.py:60-93）：梯度摊平/还原（docstring 移植自 PyTorch 源码）。
- apply_gradient_allreduce（distributed.py:95-147）：广播 state_dict 对齐参数（L105-108）→ 每参数注册梯度 hook（L136-140）→ 反向时梯度按 dtype 分桶摊平 all_reduce 写回（L110-134）；gloo 遇半精度一次性警告（L120-125）。
- main（distributed.py:150-176）：多卡启动器，见"数据流"。

## 外部连接

dataset.py 零项目内 import（仅 torch/torchaudio/scipy 等），被 train.py:48 与 denoise.py:49 消费。distributed.py 零项目内 import，被 train.py:46 消费三函数；其 main() 反向 spawn train.py 子进程（distributed.py:172）——主仓中唯一"代码调用代码入口"的边。README.md:65 的标准训练命令 `python3 distributed.py -c configs/*.json` 直接落到 `__main__`（distributed.py:179-189）。

## 数据流

**数据管道**：磁盘 fileid_N.wav 对 → torchaudio.load → 10 秒随机裁剪（configs/DNS-large-*.json 的 crop_length_sec=10、sample_rate=16000）→ DataLoader（4 worker）→ train.py:146 的 for 循环。多卡时 DistributedSampler 切分数据互不重叠。

**进程流**：distributed.py main() 组装 `['train.py', ..., '--config=X', '--num_gpus=N', '--group_name=G']`（L154-159）→ 每卡循环把 `args_list[-2]`（--num_gpus 占位）**原位替换**为 `--rank={i}`（L168）→ Popen spawn（L172，rank 0 stdout 直通、其余重定向 GPU_{i}.log，L169-170）→ p.wait 收割（L175-176）。

**梯度流**（每步 backward 后）：hook 触发 queue_callback（L138）→ 分桶摊平 → all_reduce → 写回参数 .grad。

## 设计决策

1. **文件名即契约**：dataset.py:42-43 假定 clean/noisy 同 fileid 严格配对，README.md:31-36 因此专门给了一段给 DNS-Challenge 生成脚本改文件名的 sed 式命令——数据准备错误会在 L37-39/L57 的断言处爆炸而非默默错配。
2. **sortkey 特化**（dataset.py:46）：`'_'.join(name.split('_')[-2:])` 专为 DNS 测试集 `noisy_fileid_XX_clnsp.wav` 类命名设计，换数据集必须改（README.md:59 明言"lines 49-50 of dataset.py need to be carefully changed"）。
3. **--num_gpus 占位符**（distributed.py:158+168）：先 append 再原位覆盖，是 waveglow 移植时的残留写法——**不是 bug**（最终命令行不含该参数，train.py argparse 也未定义），但阅读时极易误判。
4. **手写梯度同步而非 DDP**：torch 1.7 时代 NCCL DDP 尚不完善，waveglow 的 hook+分桶方案是当时最优解；现代复刻直接用 DDP。
5. **死 import**：dataset.py:7 的 scipy wavread 与 L20 的 torchvision 全文件未使用（真实读 wav 用 torchaudio，L67-68）；L31 `super(CleanNoisyPairDataset).__init__()` 是未绑定实例的经典笔误（恰好无害）。

## 新人提示

换自己的数据集：改 dataset.py:41-60 两个分支的路径与命名逻辑即可，接口 (clean, noisy, fileid) 三元组不变。单卡调试直接跑 train.py 跳过 distributed.py；多卡出问题先看 GPU_{i}.log（distributed.py:169-170）——rank 0 输出混在终端里。__getitem__ 的随机裁剪用 np.random（dataset.py:77），num_workers=4 下 worker 种子不严格可复现，别指望逐位对齐论文曲线。

（不计空格约 2200 字符，锚 45+）
