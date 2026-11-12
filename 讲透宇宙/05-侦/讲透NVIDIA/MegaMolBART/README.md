# MegaMolBART 知识库（understand 全链）

> NVIDIA/MegaMolBART@b8f29f8（2022-08-30）——基于 NeMo-Megatron 的 SMILES 分子生成模型：ZINC-15 约 1.45B 分子 span 掩码重建预训练 + gRPC 推断服务。commit 固化基线。

| 阶段 | 状态 | 产物 |
|---|---|---|
| deepwiki（L0） | ✅ | `deepwiki/` |
| understand 批分析 | ✅ 12/12 批全终验 PASS（b12 主会话手工产出：worker 死于 1308 且提取全空） | 仓内 `.understand-anything/` |
| merge | ✅ 168n/309e（11 条前缀错位悬空边手工回补→0 悬空） | `intermediate/`（已清理，scan-result 保留） |
| layers/tour | ✅ 10 层 / 14 步，83/83 file 节点精确覆盖零重复 | knowledge-graph.json |
| finalize | ✅ validator 0 issues/0 warnings；fingerprints 71 文件@b8f29f80 | `.understand-anything/knowledge-graph.json` |
| onboarding | ✅ 4814 字 8 节，25 锚全界内 | `onboarding/ONBOARDING.md` |
| explain | ✅ 4 篇 1886-2404 字/篇，27+ 锚零坏 | `explain/01-04` |
| 甄别清单 | ✅ 16 条（下） | 本文件 |

## explain 索引

1. `01-megamolbart-model.md` — MegaMolBARTModel：薄子类哲学、双准确率口径、sample_molecules 生成钩子
2. `02-tokenizer与词表.md` — 字符级正则分词、523 行词表三分段、导入期读盘副作用
3. `03-augment-span掩码.md` — BART 自监督的化学形态：Bernoulli×Poisson span、死代码甄别
4. `04-grpc推断服务全链.md` — proto→生成桩→服务端/客户端、张量打平传输瓶颈

## 源码级甄别（16 条钉版）

1. **tests/pre_train_model_test.py 260 行全部注释=整体停用测试**（L57 起每个 `# def test_*`）——模型层 CI 覆盖实为零；
2. **models/vocab/megamolbart.model 是单行 SMILES 分词正则非模型权重**（wc -l=0 无换行）；.vocab 才是 523 行词表（0-5 特殊+6-271 属性描述符/UNUSED+272-522 化学 token）；
3. **csv_to_binary.py:87-93 .idx 防覆盖检查误 glob '\*.bin'**——复制粘贴 bug，防覆盖检查形同虚设；
4. tokenizer.py:48 模块导入期 open 读盘副作用（路径 `nemo_chem.__path__[0]/../models/vocab`）；tokenizer.py:222 `def vocab_size` 被 L519 同名 @property 覆盖成死方法；
5. augment.py:222-227 mask_scheme 分支整段注释——span 硬编码；`_mask_replace`(L234)/`_mask_token`(L266) 死代码且引用从未定义的 show_mask_token_prob/chem_token_idxs/decode_vocab（自标 FIXME not working）；
6. NGC model.md 架构数字（8 层/4 头/256 维）与仓内任一 yaml 不完全一致（base=3L/768/12H、xsmall=2L/256/4H、large=8L/1024/16H）——发布权重实况非 yaml 误差；训练超参五项（micro_batch32/fused_adam/Noam/warmup8000/dropout0.1）与 base 匹配；
7. 三个 `*_span_aug.yaml` 变体不含增强开关字段——span 掩码固定在 base 的 model.data 节（mask_scheme:span/mask_prob:0.1/span_lambda:3.0），命名只指继承的数据增强线；
8. config_model.sh 非"抽取配置"，实为 PACKAGE=1 时 `mv /tmp/models/ /models/` 目录搬移；
9. launch.sh usage 帮助列出 pull/root 但 case 只实现 build/push/dev/run/attach/jupyter——文档实现双向漂移；
10. blossom-ci.yml:37 白名单硬编码 `ravitestgit,`（外部贡献者评论不触发 CI），漏洞扫描 job 的 blackduck 步骤全注释=空壳；
11. 容器 ENTRYPOINT（entrypoint.sh）与 startup.sh 各拉一个 JupyterLab——8888 端口双实例冗余；
12. setup.py:24 判断 `os.path.exists('README.rmd')`（不存在的 .rmd）却读 README.md——条件写错文件名，恰好落 else 用 homepage 当 long_description；
13. MoleculeBinaryDataset 多继承 super() 沿 MRO 兜底到 MoleculeBinaryABCDataset.__init__（NeMo Dataset 无自定义 init，脆弱但能跑）；`__exit__` 引用未赋值 self.map_data 且无 __enter__=半成品上下文协议；
14. data/utils.py:102 TODO：metadata_file 当前未被真正读取；csv_dataset 的 apex get_rank_info try-import 为死代码；
15. infer.py 与包 `__init__` 受控循环导入（依赖部分初始化命名空间）；默认配置硬编码容器绝对路径 /workspace/nemo_chem/...；eval 重建判定裸字符串相等 vs canonical SMILES 相等两种口径并存；
16. preprocess 的 split 先于采样——test/val 是 per-shard 1% 而非全局 1%；503 重试=全量重投靠幂等跳过；MAX_LENGTH=150 字符过滤。

## 复跑入口

- 批终验：`python3 /tmp/ua2/verify_batch.py <repo> <N>`；finalize：`python3 /data/usershare/ai/pipeline-bin/understand/finalize_graph.py <repo>`
- 台账：仓内 `.understand-anything/PROGRESS.md`；派发模板：`DISPATCH-TEMPLATE.md`
