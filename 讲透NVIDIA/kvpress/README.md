# 讲透 NVIDIA/kvpress

KV 缓存压缩策略集合库：47 个 Press 类统一三层基类（BasePress/ScorerPress/DecodingPress），注册为 transformers pipeline 一行换策略；配 EvaluationRunner+HF leaderboard 评测闭环与 kvzap（KVzip 快速近似）训练子项目。论文 arXiv 2510.00636（`CITATION.cff:14`）。

- 本地仓：`/usr-data/data2/repos/agent-repos/NVIDIA/kvpress`（@`327ed6f`，"Keep the Loogle key count when a prediction does not parse (#299)"，v0.5.5）
- 图谱：440 节点 / 922 边 / 14 层 / 16 步导览，validator 0 issues，fingerprints 155 文件基线

## 全链状态

| 环节 | 状态 | 产物 |
|---|---|---|
| deepwiki | ✅ | `deepwiki/`（36 内容页 TRUE_100，含 INDEX/_coverage-check/wiki_full） |
| understand 图谱 | ✅ | 仓内 `.understand-anything/knowledge-graph.json`（440n/922e/14 层/16 步 @327ed6f3，fp=155） |
| onboarding | ✅ | `onboarding/ONBOARDING.md`（7026 字符，8 节，51 锚） |
| explain | ✅ | `explain/` 4 篇（01-三层基类体系 / 02-注意力评分家族 / 03-预算分配与结构窗口 / 04-评估引擎与 leaderboard，各 2.8-3.1k 字符、12-22 path:line 锚） |
| 批注甄别 | ✅ | 仓内 `.understand-anything/NOTES-DIGEST.md`（2 条高价值：attention_patch 超平面、base_press 钩子集成点） |

## 源码级勘误（8 条，全部行号实证）

1. **`kvpress/presses/__init__.py` 是零导出版权头**：全文件仅 SPDX 版权声明，无任何 import——47 个 press 的真正门面在上一层 `kvpress/__init__.py`（46 行 from-import+`__all__` 48 项=47 Press+1 pipeline）。直觉以为的"包门面"并不存在。
2. **`import kvpress` 即全局 monkey-patch transformers**：`kvpress/__init__.py` 末尾调用 `patch_attention_functions()`（`kvpress/attention_patch.py:98`），改写 transformers 的 ALL_ATTENTION_FUNCTIONS 支持 head 级掩码——import 副作用修改第三方库全局状态，对之后加载的所有模型生效（docstring 自述"automatically called when importing kvpress"）。
3. **compression_ratio 语义是"删除比例"非"保留比例"**：保留数= `max(1, int(k_len*(1-ratio)))`（`kvpress/utils.py:137`），ratio=0.2 是删 20% 留 80%；且钳位永远至少留 1 个 token（仅 ratio≥1.0 显式请求才清空），防短上下文静默清缓存。断言域 0≤ratio<1（`kvpress/presses/scorer_press.py:34`）。
4. **SUPPORTED_MODELS 是告警白名单不是门槛**：不在名单（Llama/Mistral/Phi3/Qwen2/Qwen3/Gemma3，`kvpress/presses/base_press.py:27-33`）的模型只打 warning 照常运行（`:188-189`）。
5. **图谱家族归属按"预算视角"而非"实现视角"**：SnapKVPress 归"预算分配系"（虽本质是末窗注意力评分，`kvpress/presses/snapkv_press.py:69`）；StreamingLLMPress/RandomPress 归"结构窗口系"，但实现上都是 ScorerPress 子类（`kvpress/presses/streaming_llm_press.py:14`——score 把 sink 窗外滑窗内打 0 分 `:52`，纯窗口语义零评分成本）。
6. **PyramidKVPress 不是并列家族成员而是 SnapKV 的子类**：`kvpress/presses/pyramidkv_press.py:17` 继承 SnapKVPress，只覆写 get_layer_budget（`:47`）改逐层预算——"同评分、异预算"的最小差异编程。
7. **kvzap 编号与血统**：kvzap=arXiv 2601.07891（`kvzap/README.md:4`、`kvpress/presses/kvzap_press.py:55`），是 KVzip（arXiv 2505.23416，`kvpress/presses/kvzip_press.py:33`）的快速近似；主 README.md:120 提"approximate KVzip+"并要求与 DMSPress 联用（阈值驱动而非 ratio 驱动，`kvpress/presses/dms_press.py:25`）。
8. **leaderboard 数字分两轮不可混比**：`evaluation/leaderboard.sh:10-15` 把"question 是否参与压缩"的 press 分开循环（no_press 基线先行 `:13`）——信息可见性不同的策略数字不直接可比；另 `tests/test_pipeline.py:47-49` 的 FA2 用例带无 GPU/无 flash_attn 双 skipif，CI 上实际不跑。

## 阅读顺序建议

`deepwiki/1.2`（quick start）→ `onboarding/ONBOARDING.md`（三层基类+五家族地图）→ `explain/01`（基类深潜）→ `explain/02/03`（两大家族）→ `explain/04`（评测闭环）→ 按需查 README.md 的 press 清单与 `notebooks/`。
