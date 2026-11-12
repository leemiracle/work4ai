# MegaMolBART 新人导览（understand 图谱版）

> 仓 NVIDIA/MegaMolBART@b8f29f8（2022-08-30）。图谱 168 节点/309 边/10 层/14 步 tour，fingerprints 71 文件基线。行号锚均经源码核实。

## ① 项目一句话定位与技术栈

MegaMolBART 是基于 **NeMo-Megatron** 的 SMILES 分子生成模型：encoder-decoder BART 在 ZINC-15 约 1.45B 分子上做 span 掩码重建预训练，服务小分子药物发现。代码栈为 Python（nemo_chem 包，29 个 .py）+ Hydra YAML 配置 + protobuf/gRPC 推断服务 + NGC 容器（`setup/Dockerfile`）。与上游 NeMo 的关系：`nemo_chem/models/megamolbart/megamolbart_model.py:22` 直接 import `MegatronLMEncoderDecoderModel`，本仓只做化学域定制（分词器/数据集/掩码），模型并行与训练循环全托 NeMo。

## ② 总体架构：10 层从外到内

按图谱分层（外→内）：**容器构建与环境**（Dockerfile 单 stage 七步 RUN + conda env）→ **容器运行时脚本**（entrypoint/startup/launch.sh）→ **Python 打包与包标记**（setup.py 经 importlib 读 `nemo_chem/package_info.py` 取 0.2.0.dev 版本号）→ **gRPC 契约与生成代码**（proto 三 rpc + pb2 桩）→ **模型与推断核心** → **分词器与词表资产** → **数据管线** → **训练评估入口与配置**（四档 yaml + SLURM）→ **测试与数据夹具** → **文档与 CI**。核心代码集中在三层：数据管线 9 文件、模型推断 4 文件、入口配置 10 文件——**仓的本质是"NeMo 化学插件 + 数据管线 + 部署壳"**，模型本体只有一个文件。

## ③ 核心数据流：预训练一条链 + 推断一条链

**预训练链**：ZINC-downloader.txt（2794 条 tranche URL，`examples/chem/conf/dataset/ZINC-downloader.txt`）→ `preprocess.py` 下载/按 seed 99%/0.5%/0.5% 切分/MAX_LENGTH=150 过滤 → `csv_to_binary.py` 的 `CsvToBinary`（`nemo_chem/data/preprocess/csv_to_binary.py:43`）把 CSV 转 Megatron mmap 二进制（.bin+.idx）→ 训练时 `MoleculeBinaryDataset` mmap 加载 → collate 层 `MoleculeEnumeration`（`nemo_chem/data/augment.py:31`）做 **span 掩码**：`_mask_span`（augment.py:241）按 `mask_prob=0.1` Bernoulli 采起点、`span_lambda=3.0` 的 Poisson 定长（augment.py:253）、整段塌缩为单 mask token（配置在 `examples/chem/conf/megamolbart_pretrain_base.yaml:86-88`）→ `MolEncTokenizer.tokenize(mask=True)`（`nemo_chem/tokenizer/tokenizer.py:307`）字符级正则分词 → MegaMolBARTModel encoder-decoder 重建 → `megamolbart_eval.py` 分子重建评估。

**推断链**：`infer.py:20` 的 `NeMoMegaMolBARTWrapper` 统一门面——`smis_to_hidden/smis_to_embedding/hidden_to_smis`（infer.py:135/150/165）三向互转；`.nemo` 检查点恢复（infer.py:114-116）。gRPC 化后：`setup/megamolbart.proto` 三 rpc → `generated/megamolbart_pb2_grpc.py` 桩 → `nemo_chem/models/megamolbart/grpc/service.py:13` `InferenceService` 服务端（Hydra compose 加载 infer.yaml，service.py:17-19，监听 50051，service.py:53）→ `examples/chem/nbs/infer.py:10` `InferenceWrapper` 客户端。张量跨进程是 flatten().tolist() 打平传输，非零拷贝。

## ④ 关键子系统深潜

**4.1 分词器与词表**：`MolEncTokenizer`（`nemo_chem/tokenizer/tokenizer.py:100`）是 SMILES **字符级正则分词**（非 BPE）——正则模式在模块导入时从 `models/vocab/megamolbart.model` 读入（tokenizer.py:48 的 `open(DEFAULT_MODEL_PATH)` 读盘副作用）。词表 523 行三分段：0-5 特殊 token、6-271 属性描述符/UNUSED 占位、272-522 化学 token——`DEFAULT_CHEM_TOKEN_START=272`（tokenizer.py:35）与配置类 `chem_tokens_start_idx`（tokenizer.py:72）对齐。注意 tokenizer.py:222 的 `def vocab_size` 被 L519 的同名 @property 覆盖成死方法。

**4.2 span 掩码增强**：`MoleculeEnumeration`（augment.py:31）承担训练侧增广——原子重编号（RenumberAtoms）+span 掩码。掩码分支被硬编码走 span（augment.py:222-227 的 if mask_scheme 分支全注释），`_mask_replace`（augment.py:234）与 `_mask_token`（augment.py:266）是引用未定义符号的死代码（自标 FIXME not working）。**BART 自监督信号的真实形状**：10% 位置起跨度、平均长度 3 的连续 token 段塌缩为单个 mask token。

**4.3 gRPC 推断服务**：契约在 `setup/megamolbart.proto`（package nemo_chem.models.megamolbart.grpc，InputSpec/OutputSpec 两消息 + GenerativeSampler 三 rpc）；服务端 `InferenceService` 继承 `GenerativeSamplerServicer`（pb2_grpc 生成类）；容器里 `setup/startup.sh` 后台拉起服务、`setup/entrypoint.sh` 再拉一个 JupyterLab——8888 端口双实例冗余（批 4 甄别）。

## ⑤ 构建与部署工作流

**容器**：`setup/Dockerfile` 单 stage：BASE_IMAGE 默认 `nvcr.io/nvidia/clara/megamolbart_base:nemo_1.11_rc1`（Dockerfile:16）→ conda env 装 rdkit（Dockerfile:43）→ clone pysmilesutils（Dockerfile:46）→ **GITHUB_ACCESS_TOKEN clone 本仓源码**（Dockerfile:49-52，非 COPY 本地）→ Megatron helper 重编译（Dockerfile:61）→ entrypoint 接线（Dockerfile:75）。**宿主入口** `launch.sh`（build/push/dev/run/jupyter 子命令；usage 帮助列了 pull/root 但 case 未实现——文档实现漂移）。**多机训练**：`examples/chem/slurm/megamolbart_pretrain_slurm.sh` 按节点数推导 GLOBAL_BATCH_SIZE，`auto_launcher.sh` 用 `--dependency=afterany` 把扫参作业串成链。

## ⑥ 测试体系与已知坑

- `tests/test_tokenizer.py`：14 个分词器单测，可用；
- `tests/test_inference.py`：推断链路集成测试（Hydra compose 加载 infer 配置）；
- **`tests/pre_train_model_test.py` 260 行全部注释=停用测试**（L57 起每个 `# def test_*`），形状断言（pos_emb/bart forward/encode/decode/char_acc）全部不执行——CI 里的模型层覆盖实为零；
- `.github/blossom-ci.yml:37` 白名单硬编码 `ravitestgit,`，外部贡献者评论不触发 CI；漏洞扫描 job 的 blackduck 步骤全注释=空壳；
- 数据夹具：tests/data 三 split 迷你 CSV（各 200 条/分片）+metadata 清单；`nemo_chem/data/utils.py:102` 标注 TODO：metadata_file 当前未被真正读取。

## ⑦ 常见任务入口

**换一档模型尺寸训练**：从 `conf/megamolbart_pretrain_{base,large,small,xsmall}_span_aug.yaml` 选档（base 3 层/768/12 头、large 8 层/1024/16 头、small 6 层/512/8 头、xsmall 2 层/256/4 头——四档只覆盖架构与 GPU 拓扑，不覆盖增强开关，span 掩码固定在 base 的 data 节）；本地走 `shell/megamolbart_pretrain_quick.sh`，集群走 slurm 线。

**加一个新的数据增强**：动 `nemo_chem/data/augment.py` 的 `MoleculeEnumeration`（唯一入口），collate 在 `prepare_dataset.py`；注意不要试图复活 `_mask_replace` 死分支——其依赖的 show_mask_token_prob 等符号从未定义。

**部署推断服务**：`launch.sh run` 或直接容器 → startup.sh 起 50051 gRPC；客户端引 `examples/chem/nbs/infer.py` 的 InferenceWrapper；改契约要同时重编 `generated/`（protoc）与 proto。

## ⑧ 进一步阅读：14 步 tour 浓缩

步 1-3 文档与容器（README/QUICKSTART/NGC model.md → Dockerfile 七步 → setup.py 包结构）；步 4-5 入口与配置（pretrain.py 双模式 → 四档 yaml 与 SLURM 缩放）；步 6-8 数据三连（ZINC 下载与预处理 → 二进制数据集 → span 掩码——本仓精华）；步 9-11 模型三连（分词器与 523 行词表 → megamolbart_model.py 本体 → infer.py 门面与评估口径）；步 12-14 服务与外围（gRPC 全链 → 测试与停用坑 → NGC 发布与 CI）。完整 14 步含每步代表文件见图谱 tour。
