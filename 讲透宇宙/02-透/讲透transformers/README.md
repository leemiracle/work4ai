# 讲透 transformers · understand 图谱全链产物

> huggingface/transformers @f339035（2026-09-29 快照，2026 新代：tokenization 双后端重构+新式 lazy barrel+continuous_batching）· 产物 2026-11-11 · 图谱真源在仓内 .understand-anything/knowledge-graph.json

## 状态

| 产物 | 规模 | 状态 |
|---|---|---|
| knowledge-graph.json | **17789 节点 / 55394 边 / 16 层 / 16 步 tour**（20.3MB） | ✅ finalize+ua-inline-validate 双验 0 issues 0 warnings |
| fingerprints 基线 | 3206 文件 @f339035b | ✅ 支持增量 |
| ONBOARDING.md | 5962 非空白字符 / 8 节 / 49 锚 | ✅ 锚全验 |
| explain/ | 12 篇 2960-4715 字符/篇，合计 88 锚 | ✅ 三型判读消歧终验 88/88 真 0 坏 |

## 裁剪口径（.understandignore）

tests/examples/docs/scripts/utils（仓根）/templates/model_cards 全裁 → 3206 文件入图（src/transformers 3043 含 models/ 521 家族 + .github + 根文件）。

## 批分析实录（114 批 / 597 part 文件，跨 2 个 1308 窗口全零损失）

- 手扫补 imports 合计 ~600 条，三大系统性盲区：①`from ... import initialization as init` 裸包别名导入（数十文件，每批手补）②新式模型 barrel 的 TYPE_CHECKING 星式 import+define_import_structure(_file)（旧式 _import_structure 字典已废弃，scanner 全盲，单批补 75-111 条 depends_on）③函数体内延迟 import
- 260 悬空边：208 回补（class 级符号目标→所在 file 节点+前缀错位 Makefile/workflow/README），52 真悬空（仓根 utils/ 被裁，诚实弃）
- 多批独立证实的基类勘误：**ModelOutput 真身 utils/generic.py:415**（modeling_outputs.py 仅 re-export）；**GenerationMixin 真身 generation/utils.py:485** 且直接继承 continuous_batching ContinuousMixin；**PreTrainedTokenizer=tokenization_python.py:1424 的 PythonBackend 别名**，PreTrainedTokenizerFast=TokenizersBackend；旧 tokenization_utils.py/_fast.py 已不存在（拆 _base/_tokenizers/_sentencepiece/_python 四系）
- modular 单一真源范式全景：299/521 家族有 modular_*.py（libcst 转换器在仓根 utils/modular_model_converter.py，不随包发布）；跨家族继承谱系黄金边：phi←llama+clip、qwen2←llama+gemma2+mistral、step3p7 复用八家族（288 专家 MoE）、pp_doclayout_v2←v3 版本倒挂、sam2_video 的 RotaryEmbedding←sam3
- 死代码/勘误精选：convert_imagegpt 引用不存在的 ImageGPTForCausalLM（真名 ForCausalImageModeling，运行必 ImportError）；tokenization_whisper 同签名双定义后者遮蔽前者；hyperclovax 与 granite 的 logits_scaling 同名语义反转（除法 vs 乘法）；bart/tokenization_bart.py 纯 v5 兼容垫片；pb2_new TrainerSpec 比 pb2 多 5 字段（差分隐私三件套）

## 16 层速览

根配置/CI → 包入口 barrel → Auto 注册矩阵 → 配置体系 → modeling 基类 → 分词双后端 → data/collator → processors 多模态 → 生成引擎+continuous_batching → trainer → pipelines → quantizers/exporters → models NLP 家族 → models 多模态/CV → models 语音 → integrations/infra

## 使用

- 新人：onboarding/ONBOARDING.md → tour 16 步 → explain/ 12 篇（barrel→Auto→config→modeling_utils→分词→生成→modular→llama→MoE→trainer→pipelines/量化→exporters/integrations）
- agent：knowledge-graph.json + 本目录
- 增量：代码变更后重跑 prepare（fingerprints 跳过未变）
