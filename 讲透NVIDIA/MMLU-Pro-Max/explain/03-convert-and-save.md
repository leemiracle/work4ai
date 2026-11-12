# 03 · convert_and_save.py —— 一键全量编排的 CLI 入口

## 角色定位

`convert_and_save.py`（55 行）是 MMLU-Pro-Max 的命令行入口与造题管线总开关：一条命令把 7 个转换器变体全部跑完，将 MMLU-Pro 加工成整套 MMLU-Pro-Max manifest。它刻意保持**零决策设计**——argparse 只有一个必填参数 `--save_dir`（convert_and_save.py:52），没有变体选择、没有随机种子透传；想只跑部分变体，得改 ALL_TASKS 或自己写脚本实例化转换器。仓的哲学在这里很清楚：编排层越薄越好，全部智能在 MMLUProMax.py 的子类里。

## 内部结构

- **import 块**（convert_and_save.py:23-31）：平铺 `from MMLUProMax import ...` 六个转换器类——import 的是模块文件名 MMLUProMax.py 且无包结构，决定脚本必须从仓根运行（同仓 MMLUProMax.py:36/:311 又各自硬编码 `./data/...` 相对路径，两重仓根耦合）。
- **ALL_TASKS 列表**（convert_and_save.py:33-41）：模块级实例化 7 个变体，顺序即产出顺序——DropCorrectAnswer 打头（convert_and_save.py:34），NoCorrectAnswer 两变体（先 `replace=False, random_loc=True` 后 `replace=True`，convert_and_save.py:35-36），再 Binary/MultiPrompt/ChoiceOrder（convert_and_save.py:37-39），Generative 收尾（convert_and_save.py:40）。实例化发生在 import 期，意味着**import 本模块就会加载 prompts.json**（基类构造 MMLUProMax.py:36）——当前 HEAD 的 prompts.json 尾逗号问题会让这一行直接抛 JSONDecodeError，`--help` 都跑不出来。
- **save_MMLUPro_MAX(save_dir, **kwargs)**（convert_and_save.py:44-47）：for 循环逐任务 convert_and_save(save_dir) 并打印完成行——kwargs 透传是本文件唯一的扩展缝（实际各子类 convert 未用自定义参数）。
- **main 块**（convert_and_save.py:50-55）：argparse 单参数 required=True，直接调 save_MMLUPro_MAX（convert_and_save.py:55）。

## 外部连接

对 MMLUProMax.py 是**纯消费**关系：七个实例的构造参数就是全部配置面（NoCorrectAnswer 的 replace/random_loc 在 convert_and_save.py:35-36 写死）。输出物是 7 份 JSONL manifest，命名来自基类与覆写：类名去 "Converter"+可选模式后缀+时间戳（MMLUProMax.py:57-58 与 :120-123）——每次运行都产出全新文件名的一整套 manifest，永不覆盖。README:10-14 的官方用法就是本脚本；后续 NeMo-Skills 推理命令（README:74-87）的 `++input_file=${MANIFEST_PATH}` 逐份指向这里的输出。

## 数据流

一次性批处理：import 期实例化 7 任务（加载数据文件）→ main 解析 --save_dir → 逐任务执行"load MMLU-Pro → 扰动 → 填模板 → 写 JSONL"完整管线（MMLUProMax.py:49-65）→ 每任务一行 stdout 进度。没有断点续跑概念：任务相互独立，某变体失败不影响已落盘的其他 manifest。7 个任务里三个是笛卡尔展开型（各≈10 倍膨胀），首次试跑建议 --save_dir 指 /tmp 评估体积。

## 设计决策

- **模块级实例化 ALL_TASKS**：import 即得任务清单，便于他脚本 `from convert_and_save import ALL_TASKS` 复用单个转换器；代价是 import 副作用（数据文件加载）与"实例化即配置"——NoCorrectAnswer 两模式的参数写死在 convert_and_save.py:35-36，改实验设计必须改源码。
- **单参数 CLI**：把"跑哪些、怎么跑"的决策全推给代码编辑而非命令行——研究代码的典型取舍（配置面小=维护面小）。
- **顺序固定无并行**：七个任务串行，datasets.map 本身多进程——对一次性 ETL 足够，加 multiprocessing 反而放大 HF 数据集的内存拷贝。

## 新人提示

第一次跑之前先修 prompts.json 的尾逗号（MMLUProMax.py:36 加载必炸，详见 MMLU 仓 ONBOARDING §7）。只想要某个变体时别改本文件——REPL 里 `from MMLUProMax import MMLUProMaxBinaryConverter; MMLUProMaxBinaryConverter().convert_and_save("out")` 更干净。产出文件名带时间戳，建议在 save_dir 用子目录区分实验批次，否则多代 manifest 平铺堆积。验证产出健康度最快一招：`head -1` 任一 manifest 看 input 字段题面是否完整（category/question/options 都渲染），再对 ChoiceOrder 产物确认 always_same_option 列存在（MMLUProMax.py:216）——它能直接喂位置偏置分析。

——锚核对于 2026-11-08，commit dd20018b。
