# 10 · MxNet ResNet-50 v1.5 训练全家桶：双后端数据工厂与 Horovod+AMP 编排

## 角色定位

`MxNet/Classification/RN50v1.5/` 是本仓 MXNet 线的主力交付（3107 行 Python），也是 NVIDIA "训练全家桶"范式的标准样本：入口 train.py → 参数组装 → 数据工厂分派 → fit.py 训练编排 → models.py Gluon 模型，外围配 benchmark.py 性能矩阵、global_metrics.py 指标聚合、runner 一键驱动。它的看点不在模型（ResNet-50 v1.5 是最普通的分类网），而在**同一套训练皮如何同时伺候四种数据后端与两种分布式栈**：DALI GPU/CPU 解码、MXNet 原生 ImageRecordIter、synthetic 合成数据；KV store 与 Horovod 两套梯度同步路径可切换。Dockerfile 的 ENV `MXNET_CUDNN_AUTOTUNE_DEFAULT=0` 显式关掉 cuDNN 自动调优以保证基准可复现，是 NVIDIA 性能容器的惯例签名。

## 内部结构

入口极薄：`train.py` 共 70 行，`parse_args()`（:48）把四个模块的参数组拼进同一个 parser——models.add_model_args、fit.add_fit_args（约 33 项超参，含 --lr-schedule multistep/cosine、--warmup-epochs、--amp、--mixup）、data.add_data_args（--data_backend 等 15 项）、dali.add_dali_args；main 流程五行：`hvd.init()`（train.py:62，仅当 kv_store 含 'horovod'）→ `models.get_model`（models.py:485）→ `data.get_data_loader`（data.py:137）→ `fit.fit`（fit.py:473）。`models.py` 的亮点是 `Builder` 类（:68）：把 batchnorm/batchnorm_add_relu/conv/dense/transpose 等算子按 dtype+input_layout+conv_layout+bn_layout 参数化，`Transpose`（:183）/`LayoutWrapper`（:212）HybridBlock 支撑 NCHW/NHWC 双布局适配——同一 Builder 既拼 ResNet 也能拼 SeResNext（add_model_args 的架构清单）。`fit.py` 三层：参数注册（:108 --amp、:118 --lr-schedule、:132 --label-smoothing、:134 --mixup）、外围工具（load_model/save_model/evaluate/model_pred 单图推理、:313 label_smoothing 二行实现）、核心 `model_fit()`（:317）epoch 主循环。

## 外部连接

**同名双工厂**是本仓最有趣的代码拓扑：`data.py:178` 与 `dali.py:142` 都定义 `def get_rec_iter(args, kv=None)`。`data.py` 的 `get_data_loader`（:137-146）四路分派把同名冲突变成特性：dali-gpu 返回绑定 `dali.get_rec_iter(dali_cpu=False)` 的 lambda 闭包、dali-cpu 返回 `dali_cpu=True` 版、mxnet 返回本模块自己的 `get_rec_iter`、synthetic 返回 `get_synthetic_rec_iter`，未知后端抛 ValueError（:146）。DALI 侧（dali.py）：`HybridTrainPipe`（:43）的 define_graph（:89）是声明式算子图——`MXNetReader`（:50）读 RecordIO、`ImageDecoderRandomCrop`（:68）随机裁剪解码、`CoinFlip`（:87，probability=0.5）在图执行期决定镜像（避免 host 端随机数同步）、CropMirrorNormalize 归一化，输出 GPU 侧就绪的 batch；`HybridValPipe`（:99）同构但确定性解码无增强；`get_rec_iter`（:142）按 Horovod rank/size 对 shard 分片构建 DALIClassificationIterator。原生 MXNet 侧（data.py:178 起）：`ImageRecordIter` 接 30 余个增强参数（rand_crop/max_random_scale/brightness/pca_noise...），NHWC 布局直接抛 ValueError（:196，原生迭代器不支持），外面包 `DataGPUSplit`（:147）做逐卡切片+pad 对齐。外围还有 benchmark.py 以 `Popen(['timeout', args.timeout, ...])`（:73）子进程驱动 runner 跑 GPU 数×批大小矩阵，从 dllogger JSON 行（:83 `line[5:]` 切前缀）反解吞吐调和平均。

## 数据流

fit.fit（fit.py:473）编排顺序：设种子（:490-496，random/np/mx.random 三连）→ kvstore 或 Horovod 初始化（:498-500，rank/num_workers）→ AMP 环境 → warmup 探测迭代器测吞吐 → load_model 可选恢复 → `hvd.broadcast_parameters(params, root_rank=0)`（:576）参数对齐 → model_fit。model_fit 内：按 kvstore 二选一造 trainer——`hvd.DistributedTrainer`（:325-326）或 `gluon.Trainer(..., update_on_kvstore=False)`（:328）；`args.amp` 时 `amp.init_trainer(trainer)`（:331-332，mxnet.contrib.amp，fit.py:53 导入）。数据变换闭包 transform_data：`--mixup != 0` 时 `np.random.beta(args.mixup, args.mixup)`（:349-350）采混合系数做图像凸组合+标签重加权；label_smoothing（:357、:365 两处消费）按 eta 混均匀分布。步内：autograd 前反向，AMP 路径 `with amp.scale_loss(Ls, trainer)`（:411-412）动态 loss scale。弹性训练是隐藏特性：`PartitionSignalHandler`（:63）注册 SIGUSR1/SIGTERM（:69-70），`sync()`（:73）每 freq 步经 `hvd.allreduce(self.t, average=False)`（:75）同步各 rank 退出意图——收到信号的 rank 置 1 后 allreduce 把意图扩散到全组，保证所有卡在**同一预分区边界**提前收束，不会出现部分 rank 继续训练的错位。验证走 evaluate（reduce_metrics 全归约全局指标），checkpoint 仅 rank 0 落盘（:225）。

## 设计决策

四条决策线。①**lambda 闭包代替子类**：get_data_loader 不定义 Loader 抽象类，直接返回 `(lambda *args, **kwargs: dali.get_rec_iter(*args, **kwargs, dali_cpu=False))`（data.py:139）——用函数式偏应用消解"dali_cpu 是 DALI 独有参数"的接口差，代价是签名对不上要到运行期才炸。②**DALI vs 原生的双轨保留**：DALI 把解码增强搬上 GPU 是性能主路径，但原生 ImageRecordIter 路径留着（兼容无 DALI 环境+CPU 预处理场景），两条路的参数面完全不同（DALI 走 define_graph 声明、原生走 30 个命令行开关）——README 的性能表都基于 DALI，原生路径更多是保底。③**Horovod 优先于 KV store**：KV store 是 MXNet 自带参数服务器，Horovod 是 ring-allreduce；fit.py 里 'horovod' in kvstore 的字符串探测贯穿全文件（:225/:253/:325/:498），把分布式选型折叠进一个字符串值——简单粗暴但让两条路径的所有分歧点都显式可见。④**synthetic 后端的基准哲学**：SyntheticDataIter 一次性 np.random 生成数据缓存复用，消除存储与解码瓶颈专注算力上限——benchmark.py 的吞吐矩阵可先用 synthetic 定位 GPU 侧瓶颈，再换真实数据看管线损耗。

## 新人提示

入手顺序：train.py 70 行先通读（它是全家的目录）→ data.py 的 get_data_loader 四路分派 → dali.py 的 HybridTrainPipe.define_graph（DALI 声明式范式入门最佳样本）→ fit.py 的 model_fit 主循环。三个坑：① 同名 get_rec_iter 有两处（data.py:178 与 dali.py:142），grep 时注意区分——调用方拿到的永远是 data.get_data_loader 返回的闭包/函数，直接 import dali.get_rec_iter 会绕过分派；② 原生 mxnet 后端 + `--input_layout NHWC` 会在运行期 ValueError（data.py:196），NHWC 只在 DALI/部分模型路径可用，报错信息不指明这一点；③ PartitionSignalHandler 的 SIGUSR1 语义是"优雅收束"不是"立即退出"——跑弹性训练时发信号后模型还会继续训到下一个分区边界，观察日志别误判信号失效；benchmark.py 的 --timeout 传 'inf' 时靠外层 timeout 命令兜底，矩阵跑挂一轮看 JSON 里缺哪格即可定位。
