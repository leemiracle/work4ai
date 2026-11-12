# 07 · modular 转换器范式：单一真源与跨家族继承

## ① 角色定位

transformers 仓 521 个模型家族目录（`src/transformers/models/`），其中 299 个有 `modular_*.py` 文件——这是 2024 年引入、2026 年版已成绝对主流的"单一真源"（single source of truth）范式：每个家族的 modeling/configuration/image_processing 不再手写，而是由 modular 文件声明"我继承谁、覆写什么"，再由构建期转换器展开成独立的生成文件。生成文件头部带着醒目的 AUTO_GENERATED_MESSAGE（`utils/modular_model_converter.py:41-46`）：🚨 此文件自动生成，任何手改都会被覆盖，改请改 modular。CI 由 `.github/workflows/pr-repo-consistency-bot.yml:179,222` 调 `utils/check_modular_conversion.py --fix_and_overwrite` 强制对账。注意一个易错点：**modular 文件不参与运行时**——`src/transformers/models/` 下没有 `modular_transformers.py` 运行时核心库，转换逻辑全部住在仓根 `utils/`（modular_model_converter.py/modular_integrations.py/modular_model_detector.py），类装饰器（auto_docstring/no_inherit_decorator）则上移到 `src/transformers/utils/generic.py:1090`，随包发布但仅作标记。

## ② 内部结构

转换器基于 **libcst**（保留格式的 CST 解析器）而非 ast——因为生成文件要与原文件做格式对齐的 diff。核心流程：importlib 加载 modular 文件真实模块（`modular_model_converter.py:55-60` 的 `_MODULE_SOURCE_CACHE` 缓存源码+CST 树），沿 MRO 收集父类实现，把相对导入（`..llama.modeling_llama`）改写为绝对路径（`AbsoluteImportTransformer/RelativeImportTransformer`，来自 utils/modular_integrations.py:30-34），最后按"顶层变量优先级规则"合并常量——转换器注释明说（L500-503）：匹配特定模式的顶层变量永远用 modular 自己的值，另一组仅在非 None 时覆盖。继承链上的类在生成文件里被"拍平"：`class Qwen2MLP(LlamaMLP)`（`models/qwen2/modular_qwen2.py:37`）生成的是把 LlamaMLP 主体复制进来、再应用覆写的完整类，不是 Python 层面的跨家族 import。

## ③ 外部连接

跨家族继承是 modular 的灵魂，四条谱系按源码核实：

- **phi**：`modular_phi.py:17-18`——`from ..clip.modeling_clip import CLIPMLP` + `from ..llama.modeling_llama import`（LlamaAttention/LlamaModel/LlamaForCausalLM 全链）。NLP 模型借 CV 模型的 MLP，正是范式的威力所在。
- **qwen2**：`modular_qwen2.py` 三源——llama（L18 起，MLP/Attention/DecoderLayer/PreTrainedModel/ForCausalLM）+ gemma2（L17 `Qwen2RotaryEmbedding(Gemma2RotaryEmbedding)`，L45）+ mistral（L30 `Qwen2Model(MistralModel)`，L109）。
- **step3p7**：八家族大杂烩（modular_step3p7.py:39-71）——deepseek_ocr2/deepseek_v4（Experts/MLP）/gemma3（TextModel）/kimi_k25（VisionRotaryEmbedding）/laguna（Attention/DecoderLayer）/minimax_m3_vl（视觉塔五件套）/qwen2_vl/siglip。L66-69 有一段教科书注释：qwen2_vl 的 `apply_rotary_pos_emb_vision` 在本文件"未使用但承重"（load-bearing）——因为 `Step3p7VisionAttention` 继承 MiniMax 的三轴版本会被 converter 拉进生成文件，而本塔是二维的，必须显式 import 二轴版覆盖之。
- **pp_doclayout_v2 ← v3 版本倒挂**：v2 反向复用 v3（`modular_pp_doclayout_v2.py:47-48` import PPDocLayoutV3ImageProcessor 与 PPDocLayoutV3GlobalPointer）。新版先落地、旧版号模型后补，继承方向与版本号无关——图数据库式的引用网取代了线性版本史。

## ④ 数据流

开发者的修改流：改 modular_*.py → 跑 `python utils/modular_model_converter.py --files src/transformers/models/xxx/modular_xxx.py` → converter 沿 dependency_mapping 把继承链上每个被引用的方法/类体拉平进生成文件 → 头部写入 AUTO_GENERATED_MESSAGE → git diff 里生成文件整体更新。`no_inherit_decorator`（utils/generic.py:1090）是反向闸门：标记某个方法不参与继承拍平，在生成文件里保留原样。CI 的 check_modular_conversion 则重放整个转换并比对，任何"手改生成文件"都会红。

## ⑤ 设计决策与勘误

- **为什么拍平而不是运行时多继承**：生成的 modeling_qwen2.py 零跨家族 import（实测 0 个家族的 modeling 直接 import modeling_llama），用户 pip 安装单家族不会被拉进无关依赖；同时 diff 审查时每个家族自足可读。代价是仓库体积膨胀与"改一处、N 处生成文件刷新"的 PR 噪声——CI 强制是唯一防线。
- **勘误一**：网传"modular 会消灭重复代码"只对了一半——消灭的是**编辑期**重复，**磁盘上**的重复反而更多（107 个家族的 modular 引用 llama，意味着 llama 骨架被复制进 107 份生成文件）。
- **勘误二**：继承谱系读 modular 才是真值，读生成文件会得出"qwen2 与 llama 无关"的错误结论；同理 kimi_k25 与 glm4v 的血统只在 modular_kimi_k25.py:45,249,632 可见。
- **版本倒挂**（pp_doclayout_v2←v3）说明 modular 引用网无环约束靠人工保证，转换器不禁止未来的环。

## ⑥ 新人提示

加新模型先决定"纯继承 or modular"：全新架构可手写，但凡与既有家族有 30% 以上同构就写 modular。改 bug 必须定位到继承链的最深公共节点（llama 级的修复会自动流向 qwen2/qwen3/phi 等百余家族，受益面巨大但回归面同样大）。读生成文件时先看头部是否带 AUTO_GENERATED 标记再决定能否手改。审 PR 时警惕"modular 没改、生成文件改了"或反向的单边修改——两者都过不了 CI，但本地不跑 check 容易白干。
