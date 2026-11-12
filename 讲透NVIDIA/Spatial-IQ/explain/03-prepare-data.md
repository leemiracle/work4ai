# explain 03 · training/prepare_data.py——SFT/GRPO 训练数据组装线

## 角色定位

316 行的训练数据准备脚本，训练闭环（图谱 L08 层）的入口：把 data_generation 的视图+真值转成 NeMo-RL 可吃的 JSONL。支撑两条配方——SFT（CoT 推理格式教学）与 GRPO/RLVR（奖励由真值驱动）；训练 runner 本体在外部 NeMo-RL 仓（README.md:33），本仓只管"数据契约+配置+评估"，此文件就是契约执行者。

## 内部结构

- **提示词表** `TASK_PROMPTS`（training/prepare_data.py:42）：各 task_id 问句模板；
- **CoT 目标模板** `COT_TARGET_TEMPLATE`（:56-70）：本文件灵魂——`<think>` 块内 10 步分解：物体类型（task1）→列数（task3）→层数（task4）→顶层物体数（task2）→簇数（task9）→可见数（task5）→顶层柱内可见（task7）→直接支撑块（task6）→隐藏块上方可见（task8）→隐藏块数，收敛到 `<answer>{task_main}</answer>`；
- **必填键** `COT_REQUIRED_KEYS`（:71）：task1-9 缺一跳过该 view（:157、:203-204）；
- **样本组切分** `split_sample_groups`（:102）：按 sample 切 train/val 防泄漏；主流程 `main()`（:217）带 `--cot`/`--cot-mask-final-answer`（:226、:229）。

## 外部连接

上游吃视图目录（`collect_view_dirs` :75）与 gt.json；下游 `write_jsonl`（:209）落盘后填进 NeMo-RL YAML 的 `train_data_path` 覆盖位（training/configs/grpo_spatialiq.yaml:137、training/configs/sft_spatialiq.yaml:68）。数据契约由 training/schema.py 六个 Pydantic 模型定义（:39 GtAnswers 起）；processor 可用性由 training/verify_cpu.py 冒烟兜底（:184 `test_sft_processor`、:214 `test_grpo_processor`）。

## 数据流

分叉在 `collect_examples`（training/prepare_data.py:128）。**CoT 模式**（:155-180）：一 view 一样例，问题固定 `task_main`（:177），模板填 task1-9 成 10 步链（:162-171），`ground_truth_number` 另存真值；**普通模式**（:181-199）：逐 task 出样例，task10/11 显式跳过——双视角任务进不了单图管线（:184）。`--cot-mask-final-answer` 的精妙处（:136-139、:173）：最终总数在"总数=a+b"行与 `<answer>` 标签**两处**替换为占位符——教格式不泄答案。

## 设计决策

1. **答案掩码**：堵死"背答案"捷径（training/prepare_data.py:136-139），最终答案留给 GRPO 奖励塑造——SFT 教形式、RL 教结论。
2. **10 步链与子任务真值强绑定**：每步对应有真值的子任务（task1-9），推理链是结构化模板而非自由发挥（:56-70）——奖励可分解、错误可归因。
3. **样本组级切分**（:102）：防同场景多视角跨集泄漏虚高。
4. **双视角任务退出训练线**（:184）：诚实降级，与评测线解耦。
5. **配方两档**：标准档 Qwen2.5-VL-7B、8 prompt×8 generation、500 步（training/configs/grpo_spatialiq.yaml:3、:7、:51）；main 档 Gemma-4-31B + DAPO-tight（training/configs/grpo_spatialiq_main.yaml:2、:52）。

## 新人提示

从 training/prepare_data.py:56-70 模板读起，对照 gt.json 字段理解各 {taskN} 槽位；先跑 `python training/verify_cpu.py` 11 个冒烟测试（training/verify_cpu.py:32），再小数据 dry-run 打印一条 CoT 样例查两处占位符。改模板务必同步 COT_REQUIRED_KEYS（:71），漏键静默跳样例只 stderr 告警（:203-204）。系统提示词 training/prompts/spatialiq_cot.txt:1 的 `<answer>` 约定须与模板一致，否则评测抽取失败。
