# 第 12 篇：configs/ 实验矩阵与 launch/eval 脚本群——从 yaml 到 dreamdojo_* 注册

## 一、角色定位

根目录 `configs/` 只有 10 个 yaml——2 个模型尺寸（2b/14b）× 5 个数据域（pretrain/gr1/g1/agibot/yam）——却是 DreamDojo 训练的**唯一用户入口**：`bash launch.sh dreamdojo_2b_480_640_gr1` 里的实验名就是从这里动态注册的。配套 `launch.sh`/`eval.sh` 与 examples 推理脚本构成"训练-评测"双闸门。理解这条链的关键：`configs/*.yaml` 不是 hydra 直接读的配置，而是被 `cosmos_predict2/experiments/base/action.py` 在 import 期**扫描、合并、注册**的覆盖层——yaml 之上还有 python 默认配置兜底，两层合体才是完整实验。

## 二、内部结构

**yaml 矩阵的极简主义**。`2b_480_640_pretrain.yaml` 全文 44 行：job 组、trainer 的 grad_accum_iter 与 reg/ema 回调、context_parallel_size=1、net 段（action_dim 384/temporal_compression_ratio 4/num_action_per_chunk 12/zero_init_action_embedder true）、dataloader_train（batch_size 4、num_frames 13、三条 dataset_path 加 mixing_weights 1/2/10、data_split full）。**14b 与 2b 差异恰好三个参数**（diff 实证）：`job.name`、`grad_accum_iter`（1 vs 2）、`batch_size`（4 vs 2）——14B 靠"减半 batch+双倍累积"维持等效全局批。**数据域变体**另改几处：gr1 关掉 zero_init_action_embedder、数据换本地 `datasets/PhysicalAI-Robotics-GR00T-Teleop-GR1/GR1_robot`、data_split=train；pretrain 混合三条 AMLFS 源权重 1/2/10、data_split=full。

**注册机制（本篇核心）**。`cosmos_predict2/experiments/base/action.py:294` 以 `Path(__file__).parent.parent.parent.parent / "configs"` 定位仓根 configs/；`:298-311` 扫描 yaml：stem 拼出 `dreamdojo_{stem}` 变量名，**14b 字串检测**决定用 `_default_groot_config_14b` 还是 `_default_groot_config` 做底座（`:306-309`），合并结果写入 globals 与 `_experiment_configs`；`:313-317` 以 `ConfigStore.store(group="experiment", name=var_name.lower())` 注册——`experiment=dreamdojo_2b_480_640_gr1` 选择项由此而来。合并逻辑 `load_experiment_config`（`:29-65`）：两侧 `OmegaConf.to_container(resolve=True)` 后递归 dict 合并、override 胜出，包回 `LazyDict`。python 底座（`:71` 起）自带骨架：override model 为 `action_conditioned_video2world_fsdp_rectified_flow`、net 为 `cosmos_v1_2B_action_chunk_conditioned`、data 为 `dreamdojo_13frame_480_640_train/val`、checkpoint 拉 NGC 预训练权重、lr 16e-5、max_iter 100k、net 默认 action_dim 29（GR1 本体动作维）——**yaml 的 action_dim 384 正是对 29 的覆盖**：从本体动作切到 GR00T chunk 嵌入。

**launch.sh**。环境块与 LAM 的 launch 同族：NCCL 监控关闭、`TORCH_NCCL_HEARTBEAT_TIMEOUT_SEC=1800`、`expandable_segments`、EFA/RDMA、`CUDA_MODULE_LOADING=LAZY`、清 LD_PRELOAD；随后四条 AMLFS 硬编码：PYTHONPATH/HF_HOME/IMAGINAIRE_OUTPUT_ROOT/`source .venv/bin/activate` 全指向 `/mnt/amlfs-01/shared/shenyuang/...`。主命令 `torchrun -m scripts.train --config=cosmos_predict2/_src/predict2/action/configs/action_conditioned/config.py -- experiment=$config_name job.wandb_mode=disabled ~dataloader_train.dataloaders`——`~` 前缀是 hydra 的"删除键"语法。

**eval.sh 与 examples/action_conditioned.py**。eval.sh 固定 `--experiment dreamdojo_2b_480_640_gr1`、checkpoints-dir/save-dir 均为 AMLFS 路径、`--data-split test --checkpoint-interval 5000 --infinite`。`docs/EVAL.md:17` 定义 data-split：full=100%、train=每拼接集前 95%、test=后 5%。`examples/action_conditioned.py`：读 `latest_checkpoint.txt` 拿最新迭代（`:64-67`）；infinite 模式按 interval 步进，`iter_*/all_summary.json` 存在则跳过（`:76-81`），`model_ema_bf16.pt` 缺失就 `convert_checkpoint`（`:85-87`）——先 **`sudo chmod -R 777`** 整个迭代目录再跑 `scripts/convert_distcp_to_pt.py`（PEP 723 脚本，`:43-55`）；外层 `except Exception: pass` + `sleep(60)` 轮询（`:89-91`）。

## 三、外部连接

向上：`scripts/train.py` → `cosmos_oss.scripts.train.main`（第 8 篇）→ config 模块 `action_conditioned/config.py:98-104` 的 `import_all_modules_from_package` 三连——注册发生在 make_config 的 import 副作用里。向下：蒸馏三脚本（teacher_gen/warmup/self_forcing）走 `interactive/configs/config_distill.py` 系与另一族实验名（`cosmos_predict2p5_2B_action_gr00t_gr1_warmup_no_s3` 等），用 `$(pwd)` 相对路径与环境变量默认值，**没有 AMLFS 硬编码**——与 launch.sh 对照可见后者是内部集群快照、蒸馏线已外部化。旁支：`scripts/plot_psnr.py` 消费 eval 产出（要求 501 样本齐全）；`shared_meta/` 存 G1/GR1/AgiBot/YAM 四机器人 modality 与 stats json，是 action_dim 与归一化的数据侧锚点。

## 四、数据流

一次完整后训练：`bash launch.sh dreamdojo_2b_480_640_gr1`（**必须带 dreamdojo_ 前缀全名**，注册名是 `dreamdojo_{stem}` 小写，docs/POSTTRAIN.md:8 明示该全名使用 `2b_480_640_gr1.yaml`）→ torchrun 八卡 → import 链触发 yaml 扫描注册 → `experiment=...` 命中 ConfigStore → yaml 覆盖合并进 2B 底座 → freeze → instantiate：模型（加载 NGC 2B 预训练 ckpt）、dataloader（GR1_robot 本地数据，13 帧窗口，LAM 帧对由数据管线产出 lam_video）→ trainer 写 checkpoints。评测侧：eval.sh → examples 轮询新 iter → convert_distcp_to_pt 转 consolidated → `inference()` 批量生成 → metrics json → plot_psnr 汇总。

## 五、设计决策

**"薄 yaml + 厚 python 底座"**而非纯 hydra 配置树：10 个实验的可读差异压到 44 行 yaml，默认值集中在可 lint 的 python 文件，新增数据域只需复制一个 yaml——矩阵扩张成本最低；代价是读配置必须两处对照，yaml 里看不到的（lr、max_iter、checkpoint 源）藏在底座。**14b 只改三参数**体现"尺寸缩放=批策略缩放"纪律：模型差异由底座选择，数据/回调不动。**AMLFS 硬编码双刃剑**：内部一键复现 vs 外部必改——launch.sh、eval.sh、LAM 三脚本共七处 `/mnt/amlfs-*`，是本仓对外可用性的最大摩擦点，install.sh/SETUP.md 未提示。**坑**：① merge_configs 对新键静默写入（`:50-55`），yaml 键打错无 schema 校验；② examples 的 `sudo chmod -R 777`（`action_conditioned.py:44-48`）假设免密 sudo，容器外常失败；③ `except Exception: pass` 吞推理异常，调试时要去掉；④ 根 conflicts 的 cu129 残留（第 8 篇）提醒配置卫生是全局问题。

## 六、新人提示

加新数据域最短路径：复制 `2b_480_640_gr1.yaml` 改 dataset_path/zero_init_action_embedder/data_split 三处，启动用全名 `bash launch.sh dreamdojo_<stem>`。排障先查三处：yaml 键打错会被 merge **静默接受**（`:50-55` 无 schema 校验），用 `--dryrun` 打印合并后配置对照；训练起不来先看哨兵（第 9 篇）与 AMLFS 路径；评测没产物看 examples 的 bare except 是否吞错。练习：① import action 模块后列出全部 `dreamdojo_` 开头的注册实验名；② diff 两个数据域 yaml，找出比"三参数"更多的隐藏差异（如 mixing_weights），解释 [1,2,10] 的采样含义（第三源 10 倍权重主导）。

> 甄别说明：三参数差异、seven 处 AMLFS 路径、注册机制行号、sudo chmod、EVAL.md 95%/5% 语义均源码实测；"launch.sh 为内部集群快照而蒸馏线已外部化"由两组脚本路径写法对照推断；`import_all_modules_from_package` 三连发生在 make_config 的 import 副作用这一因果由 config.py:88-104 与 experiments 注册代码的结构印证，未逐步 trace hydra 内部。
