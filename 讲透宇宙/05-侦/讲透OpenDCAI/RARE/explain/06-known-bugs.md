# 06 已知 bug 与坑汇总：动手前必读清单

## 角色定位

RARE 是典型"论文随发仓"：核心实验链（process → 蒸馏 → 训练 → 评估）可用，但边角脚本与文档带多处笔误——其中五个会让对应模块完全跑不起来（预实验线三连雷、KTO 启动脚本、幽灵配置），其余是照抄命令即翻车的路径/拼写坑。本篇把全部已核实问题按严重度归档，每条给行号锚与修法，作为动手前的 check list。

## 内部结构（按严重度分级）

**A 级——模块级失效**：

1. **pre_experiment.py 语法错误**：L66-67 的 `token_list = list(set(self.tokenizer.convert_tokens_to_ids(` 括号未闭合——AST 解析实锤 "'(' was never closed" 于第 66 行，整文件无法 import，预实验线不可运行。修法：L67 末尾补右括号。
2. **pre_experiment.py argparse 双杀**：L18 定义 `--model_path_or_name`，L93 却用 `args.model_path`；L22 定义 `--dataset_name`，L113 却用 `args.data_name`——修好语法也会在 L93 AttributeError。修法：调用改回定义名。
3. **customize_model.py:28 未定义 args**：调用写 `customize_model(args.model_name, args.output_dir, args.special_tokens)`，但 argparse 只定义 `--model_name_or_path`（L22）与 `--output_dir`（L24）；函数签名只收 2 参（L4）却传 3 参——双重雷。修法：改 `args.model_name_or_path` 并删第三参。
4. **幽灵配置 accelerate_config_mm.yaml**：readme.md:192 与 demo/qwenvl_mmrait_rare.sh:20 都引用它，仓里只有 `train/accelerate_config.yaml`。修法：自建或改引用现存的。
5. **train_kto.sh 未定义变量双坑**：L19 `--model_name_or_path ${model_path}`，但 L2 定义的是 `model_name_or_path`；L26 `--cutoff_len ${len}` 从未赋值。bash 静默展开空串。修法：L19 改 `${model_name_or_path}`、给 `len` 赋值。

**B 级——照抄即翻车**：

6. **test_mmarit.json 拼写**：demo/qwenvl_mmrait_rare.sh:34 引 `data/test_mmarit.json`（多个 r），真实产物是 process_mmrait.py:9 的 `test_mmrait.json`——多模态 demo 最后一米 FileNotFoundError。
7. **sft.sh:19 缺 .json**：`--train_file_path="data/train_pubmed"` 会在 sft.py:57 的 `open()` 处崩；demo:26 同参数带后缀是对的。
8. **readme.md:129 幽灵路径**：`scripts/vllm_infer_mm.py`——仓内无 scripts/ 目录，实际在 inference/。
9. **数据需自生成**：`data/` 初始只有 dataset_info.json，全部 train_*.json 要先跑 process/；且 covert、bioasq 两个 KTO 数据集（RL_KTO/data/dataset_info.json:19/27、readme.md:324 引用）无构建脚本，只能自备。

**C 级——不一致与坏味道**：

10. finfact_kto 注册指向 `train_finfact.json`（RL_KTO/data/dataset_info.json:44），其余六条都是 `train_*_kto.json`。
11. `extract_option` 四处复制（eval.py:6、select_true.py:8、process_kto.py:5、vllm_infer_text_reject_sampling.py:85），reject_sampling 版多首字符截断（L103-105），行为有分叉。
12. vllm_infer_text.py 函数签名与 argparse 默认值三处不一致（L88-91 vs L222-240），签名默认是死代码。
13. training_args_mm.yaml:19 `saves//mmrait-qwenvl` 双斜杠（无害）。

## 外部连接

这些坑全部源自同一种工程形态：零共享脚本仓 + 文档手工维护 + 论文截稿时间压力。上游 LLaMA-Factory/vllm 的接口本身没问题，问题都在本仓自己的"最后一公里"——变量名、文件名、路径字符串的抄写。

## 数据流

坑的分布与数据流反向：越靠流水线末端（eval、demo、KTO 启动）坑越密，因为末端脚本最少被回归测试；预实验线最重（三连雷），因为论文发表后几乎没人重跑。

## 设计决策（含批判）

研究仓"能跑出论文数字即冻结"是合理策略，但 A 级五坑说明发布前缺一轮最小冒烟测试——`python -m py_compile` 与 `bash -n` 各跑一遍就能抓出大半。给使用者的建议：fork 后先全量编译/语法检查（会把 pre_experiment.py 的语法错误当场揪出），再按 readme 走 demo。

## 新人提示

1. 按本篇 A 级 1-5 逐条修完，预实验与 KTO 线才可用；文本主线（pubmed demo）与多模态线（修一个拼写后）是开箱即用的。
2. 遇到 "dataset not found"、"file not found" 先对照 06-9 的数据自生成清单，再查拼写。
3. 本篇所有行号均经源码核实（AST 验证语法错误、diff 验证双胞胎），与仓当前 HEAD 一致；若上游更新请重新核对。
