# MMLU-Pro-Max 新人导览（ONBOARDING）

> 仓：/usr-data/data2/repos/agent-repos/NVIDIA/MMLU-Pro-Max（commit dd20018b）
> 图谱：21 节点 / 41 边 / 6 层 / 12 步 tour，校验 0 issues；行号锚均经源码核实（2026-11-08）

## 1. 项目定位与核心价值

MMLU-Pro-Max 是 NVIDIA 对 MMLU-Pro 的**多层鲁棒性改造**：传统 MCQ 评测对输入扰动高度敏感——换措辞、挪选项位置、抽掉正确答案，分数就可能大变。本仓把这种敏感性从"缺陷"翻转为"测量对象"：用 7 种转换器变体对原基准施加三类扰动（**格式 / 措辞 / 选项结构**），生成多份 manifest（JSONL），配推理透传配置、LLM 裁判 prompt 和答案抽取器，构成一套"测抗扰动能力"的完整造题工具链。仓的边界刻意收窄：**只负责造题与后处理，不含评测执行**（README:18-23 明言），推理推荐外接 NeMo-Skills（README:55）。

## 2. 总体架构

极简三层，全部依赖只有 datasets==3.2.0 与 numpy==1.26.0（requirements.txt 两行）：

- **转换层** `MMLUProMax.py`：抽象基类 MMLUProMaxConverterABC 定义 load→_process_data→_add_prompt→保存的模板流程（MMLUProMax.py:49-53），6 个子类各实现一种扰动。
- **编排层** `convert_and_save.py`：模块级实例化 7 个变体（NoCorrectAnswer 出两种模式，convert_and_save.py:33-41），`--save_dir` 一个参数跑全量。
- **后处理层** `postprocessors.py`：三个 Postprocessor 子类从推理输出的 generation 字段抽最终答案。

配置与数据侧：`data/prompts.json` 集中 5 类 prompt 模板（default/binary/dropped/multiprompt×10/generative）；`data/mmlu_pro_generative_ids.json` 是 4755 个 question_id 的单行数组，圈定可脱离选项作答的开放题子集（MMLUProMax.py:311）；`config/empty_prompt.yaml` 的 user 模板只有 `{input}` 一个占位符（透传）；`config/judge.yaml` 改编自 openai/simple-evals（judge.yaml:1）做生成式答案等价判定。

## 3. 核心模块地图

| 模块 | 职责 | 关键锚 |
|---|---|---|
| MMLUProMax.py | 6 扰动子类+模板方法基类 | 基类:34-65；NoCorrect:68；Drop:133；MultiPrompt:163；ChoiceOrder:203；Binary:261；Generative:305 |
| convert_and_save.py | CLI 一键全量 | ALL_TASKS:33-41；save_MMLUPro_MAX:44-47 |
| postprocessors.py | 三路答案抽取 | 基类:1-17；Binary:20；MCQ:40；Gen:69 |

七个变体对应七个分析问题（README:31-51）：MultiPrompt 问"措辞影响多大"（10 条变体，MMLUProMax.py:163）；ChoiceOrder 问"位置偏置"（正确答案遍历所有位置，MMLUProMax.py:203）；NoCorrectAnswer 两种模式（原位替换 MMLUProMax.py:68 vs 随机插入）与 DropCorrectAnswer（MMLUProMax.py:133）一起问"模型敢不敢承认没有正确答案"；Binary 把选择题拆成判断题（MMLUProMax.py:261）；Generative 问"MCQ 能力能否迁移到开放作答"（MMLUProMax.py:305）。

## 4. 数据流 / 控制流

**造题链**：TIGER-Lab/MMLU-Pro test split（MMLUProMax.py:39）→ 子类 _process_data 扰动（HF datasets 的 .map()，批处理子类 batched=True）→ _add_prompt 用模板填 category/question/options 生成 input 字段 → JSONL 落盘，文件名=类名去 Converter+时间戳（MMLUProMax.py:57-59）。

控制流要害在**笛卡尔展开**：MultiPrompt 每题×10 模板（MMLUProMax.py:177-183 双层循环+deepcopy）；ChoiceOrder 每题×每选项位置（MMLUProMax.py:219-241，正确答案与每个位置逐一交换，新列 always_same_option/original_answer_index 记元数据 :216-217）；Binary 每题×每选项（MMLUProMax.py:276-288，binary_answer 列标 correct/incorrect）。原基准 12032 题在这三个变体下各膨胀约 10 倍，manifest 体积与推理成本先算后跑。

**评测链**（外部）：manifest → NeMo-Skills `ns generate` 推理（空模板透传，README:74-87）→ 输出 JSONL（generation 字段装模型原文）→ Postprocessor 抽 extracted_answer → 生成式路线再用 judge.yaml 让裁判模型（推荐 Qwen2.5-72B）判预测/期望等价性。

## 5. 环境与运行方式

```bash
pip install -r requirements.txt          # 仅 datasets+numpy
python convert_and_save.py --save_dir=SAVE_DIR   # 必须在仓根运行（见 §7 相对路径坑）
# 推理（外部）：ns generate ... ++prompt_config=config/empty_prompt.yaml ++prompt_template=<模型chat模板>
# 后处理：在你自己的脚本里 import postprocessors 并 .process(df)
```

后处理入口约定：输入 DataFrame 必含 generation 列（README:21），输出追加 extracted_answer 列（postprocessors.py:10）。裁判推理用 `ns generate --generation_type=math_judge ++prompt_config=config/judge.yaml`（README 尾示）。

## 6. 设计决策与权衡

- **模板方法而非函数式管线**：基类钉死流程骨架（MMLUProMax.py:49-53），子类只填扰动与题面两步——加新扰动只需继承实现两个方法，编排层零改动。
- **题面前置而非推理时拼装**：完整题面在造题期写进 input 字段，推理侧空模板纯透传——prompt 工程与推理框架解耦，换后端零改模板。
- **裁决外包**：生成式答案的等价性判定交给 LLM 裁判 prompt（judge.yaml:5-10 明确单位缺失算等价、舍入误差算等价），复用 simple-evals 成熟措辞而非自研判分。
- **防覆盖断言**：三个后处理子类都在抽取前检查 extracted_answer 列已存在则抛 ValueError（postprocessors.py:33-34/:62-63/:77-78）——幂等性靠显式失败而非静默重算。
- **manifest 带时间戳**（MMLUProMax.py:58）：同名不覆盖，代价是目录积累多代 manifest 需自行清理。

## 7. 已知问题与勘误

- **【重磅·开箱即崩】data/prompts.json 是非法 JSON**：第 17 行 generative_prompt 键值结尾有**尾逗号**（实测 4562 字节处 `...{question}",` 后接 `}`），Python json 严格模式必抛 JSONDecodeError——而基类构造函数 MMLUProMax.py:36 `json.load(open("./data/prompts.json"))` 在任何转换器实例化时即执行，**当前 HEAD 下 convert_and_save.py 一次也跑不起来**。修法：删该尾逗号。（本轮源码核验新发现。）
- **相对路径硬编码**：MMLUProMax.py:36 与 :311 都用 `./data/...`，convert_and_save.py:24 又是平铺 import——必须从仓根启动。
- **README:70 路径笔误**：示例写 `EMPTY_PROMPT_PATH="data/empty_prompt.yaml"`，实际文件在 `config/empty_prompt.yaml`（README:57 自己写的正确路径可证）。
- **抽象性不强制**：MMLUProMaxConverterABC 只 `from abc import abstractmethod`（MMLUProMax.py:22）却未继承 abc.ABC（:34）——@abstractmethod 失去强制力，忘实现钩子的子类运行到 `pass` 才炸（MMLUProMax.py:41-47 只是文档性约定）。
- **MCQ 抽取的静默全文回退**：三个分割串都不命中时返回整个 generation 文本（postprocessors.py:60），没有 Binary 那样的 "unparsed" 哨兵（postprocessors.py:28-29）——脏数据混进结果列，统计前须自滤。GenPostprocessor 无 boxed 时同样回退全文（postprocessors.py:72）。
- generative_ids 是单行 4755 元素数组（diff 不友好但非缺陷）；binary_prompt 原文有 "it's answer" 语法瑕疵，不影响功能。

## 8. 新人上手路线

1. 读 README 全文（约 120 行）钉死仓边界：造题+后处理在仓内，推理与评分在外部。
2. 修 prompts.json 尾逗号（§7 第一条），否则第 3 步无法进行。
3. 跑 `python convert_and_save.py --save_dir=/tmp/mm`，观察 7 份 manifest 的命名与列结构（input/answer/answer_index，及 ChoiceOrder/Binary/MultiPrompt 各自的元数据列）。
4. 对照读 MMLUProMax.py 的 NoCorrectAnswerConverter（MMLUProMax.py:68-130，最完整子类——双模式+convert_and_save 覆写），再横向扫其余五个子类的 _process_data。
5. 读 postprocessors.py 全文（81 行）理解三路抽取规则，注意 §7 的全文回退坑。
6. 进阶：用任一 MCQ manifest 接 NeMo-Skills 跑小模型，MCQPostprocessor 抽答案后复算准确率——ChoiceOrder manifest 按 always_same_option 分组统计就是现成的位置偏置实验。

——本导览由 understand-anything 图谱流水线生成，图谱在仓内 `.understand-anything/knowledge-graph.json`。
