# 01 · MMLUProMax.py —— 模板方法骨架与六种扰动子类

## 角色定位

`MMLUProMax.py`（326 行）是仓的核心转换器模块：把 TIGER-Lab/MMLU-Pro 的 test split（MMLUProMax.py:39）改造为 7 种评测 manifest。

## 内部结构

**基类 MMLUProMaxConverterABC**（MMLUProMax.py:34-65）用模板方法钉死四步：`__init__` 加载 `./data/prompts.json`（MMLUProMax.py:36，相对路径，必须仓根运行）；load_base_dataset 拉基准（MMLUProMax.py:38-39）；`convert()` 按 load→_process_data→_add_prompt 编排（MMLUProMax.py:49-53），后两步是抽象方法（MMLUProMax.py:41-47）；convert_and_save 以"类名去 Converter+时间戳"命名写 JSONL（MMLUProMax.py:57-58）。甄别要点：基类只导入 abstractmethod 却未继承 abc.ABC（MMLUProMax.py:22）——抽象性实际不强制。

**六个子类**按扰动分三族：

- **答案缺失族**（测"敢不敢说没有对的"）：NoCorrectAnswerConverter（MMLUProMax.py:68-130）双模式——replace=True 把正确选项**原位覆盖**为 NO_ANSWER_MESSAGE（MMLUProMax.py:81-83）；默认 replace=False 在随机位置**插入**该话术并修正 answer_index（MMLUProMax.py:93-95）。DropCorrectAnswerConverter（MMLUProMax.py:133-160）更激进：直接 `options.pop(answer_index)`（MMLUProMax.py:143），配 dropped 模板允许回答"选项里没有"。
- **格式与措辞族**：MultiPromptConverter（MMLUProMax.py:163-201）batched map 把每题与 10 条措辞变体笛卡尔展开（MMLUProMax.py:177-183），新增 prompt_id 列（MMLUProMax.py:175）；ChoiceOrderConverter（MMLUProMax.py:203-258）把正确答案与**每个**选项位置逐一交换（MMLUProMax.py:229-233），新增 always_same_option 列（MMLUProMax.py:216-217）。
- **任务形态族**：BinaryConverter（MMLUProMax.py:261-302）每题×每选项展开成判断题，binary_answer 列标 correct/incorrect（MMLUProMax.py:279-283）；GenerativeConverter（MMLUProMax.py:305-326）加载 4755 个 question_id（MMLUProMax.py:311）过滤出开放题子集。

MCQ 系子类的 _add_prompt 结构一致：`f"{label}. {option}"` 格式化选项后 str.format 填模板，题面全文写入 input 字段（如 MMLUProMax.py:104-113）。

## 外部连接

上游 HuggingFace datasets（MMLUProMax.py:26）；下游 convert_and_save.py 的 ALL_TASKS 逐一实例化（convert_and_save.py:33-41）。数据依赖两份：data/prompts.json（5 类模板）与 data/mmlu_pro_generative_ids.json。**坑**：prompts.json 当前 HEAD 第 17 行结尾有尾逗号，json 严格解析必抛 JSONDecodeError——MMLUProMax.py:36 在任何子类实例化时即触发，开箱即崩。

## 数据流

单遍 map 管线：HF Dataset → `.map(扰动函数)` 或 `.map(batched=True)` 笛卡尔展开 → `.map(_add_prompt)` 填 input → 逐行 json.dumps 写 JSONL（MMLUProMax.py:62-64）。随机性只有一处：NoCorrectAnswer 的 np.random.randint（MMLUProMax.py:87），复现需外部固定 numpy 种子。

## 设计决策

- 模板方法而非配置驱动：加新扰动=继承实现两钩子，骨架与落盘复用；代价是 MCQ 子类重复三段近似 _add_prompt（MMLUProMax.py:103-115/:148-160/:246-258）。
- 笛卡尔展开在造题期一次做完：推理侧拿到平铺 manifest，任何框架直接吃。
- answer_index 修正逻辑内联（MMLUProMax.py:93-95）保证插入式扰动后标签与选项同步，是全模块最细的边界条件。

## 新人提示

跑任何东西前先修 prompts.json 尾逗号（json.load 试一下即验）。加新扰动五步：继承基类、定 PROMPT_KEY、实现两钩子、prompts.json 加模板、ALL_TASKS 挂上。读 ChoiceOrder 交换代码（MMLUProMax.py:229-239）时盯住 options[-1] 是"刚 append 的那份拷贝"。

——锚核对于 2026-11-08，commit dd20018b。
