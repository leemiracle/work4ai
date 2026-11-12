# 01 仓总览：一个"脚本集合仓"如何串起 RARE 研究全流程

## 角色定位

RARE（Retrieval-Augmented Reasoning Modeling）是 OpenDCAI 组织下、随 KDD 2026 论文发布的研究仓（readme.md:1，arXiv 2503.23513）。核心主张是"知识存储与推理建模解耦"：先用强教师（QwQ-32B / Qwen2.5-VL-32B）在带检索上下文的题目上蒸馏思维链，筛掉答错样本，只用"答对且有推理"的数据微调小模型，绕过死记低阶知识来加速推理建模（readme.md:17）。

工程形态与"框架仓"截然不同——它是**脚本集合仓**：21 个 Python 文件分居 9 个目录，脚本之间**零 py→py import**（图谱 102 节点 169 边中，代码依赖边全是标准库与三方库）。每个脚本都是独立工序，衔接全靠**数据文件约定**：上一步写出的 JSON 文件名就是下一步的输入。

## 内部结构

目录即流水线阶段：

- `process/`（7 脚本）：数据构建族，覆盖 medqa/pubmed（医学）、pubhealth（健康声明）、casehold（法律）、finfact（金融）、mmrait（多模态）六领域；`select_true.py` 是蒸馏后筛真器。
- `inference/`（4 脚本）：文本蒸馏、多模态蒸馏、拒绝采样蒸馏、闭源 API 基线。
- `train/`：两条训练线——自研 `sft.py`（trl + FSDP，torchrun 拉起）与 LLaMA-Factory 薄入口 `train.py`（9 行，见 03 篇）。
- `RL_KTO/`：KTO 偏好优化线（见 04 篇）；`eval/`：准确率计算（见 05 篇）；`demo/`：两条端到端演示链。
- `Pre_Experiment/`：预实验线，用 vLLM prompt_logprobs 把答案 token 损失拆成知识损失 L_A 与推理损失 L_B（带语法错误，见 06 篇）。
- `data/dataset_info.json`：LLaMA-Factory 数据集注册表。

`requirements.txt` 仅 8 项：llamafactory==0.9.2、vllm==0.7.3、deepspeed==0.16.4、qdrant_client、qwen_vl_utils、modelscope、flash-attn、wandb——训练栈锁定 LLaMA-Factory 生态。

## 外部连接

对外依赖全是重资产：HuggingFace hub（数据集 `yuhkalhic/rare_share`、`bigbio/pubhealth`、`casehold/casehold`、`amanrangapur/Fin-Fact`、`whalezzz/M2RAG`；模型 Llama-3.1-8B-Instruct 等）、ModelScope（教师模型下载，demo/llama_pubmedqa_rare.sh:9）、Qdrant（内存向量库）、spaCy（实体抽取）。readme.md:354 致谢 LLaMA-Factory 与 s1——s1 的"蒸馏+筛真"（s1K 方法）正是 RARE 数据策略的直系血统。

## 数据流

一条主数据流贯穿全仓，全部以 `data/*.json` 为交换媒介：

```
原始数据集（HF/ModelScope）
  → process/*.py 构建带 <answer>X</answer> 标签的 instruction/output 对
  → inference/vllm_infer_text.py 蒸馏：教师输出写回同文件 predict 字段
  → process/select_true.py 筛真：只留答对样本，产出 *_true.json
  → train/ 微调（sft.py 读 predict / llamafactory 经 dataset_info.json 读文件）
  → inference/ 对 test_*.json 生成 llm_predict_* 字段
  → eval/eval.py 正则抽选项算准确率
```

两个关键约定：其一，蒸馏脚本**原地改写**输入文件（先备份 .bak，vllm_infer_text.py:158-165），同一个 `train_pubmed.json` 流水线前后语义不同；其二，`<answer>A</answer>` 标签格式是全部模板（如 process_medqa.py:19-31）与全部评估逻辑（eval.py:6-22）之间的隐形契约。

## 设计决策（含批判）

**零 import 的脚本仓**是双刃剑。好处：脚本可独立运行与替换，研究迭代快；坏处：`extract_option` 在 eval.py:6、process/select_true.py:8、RL_KTO/process_kto.py:5、inference/vllm_infer_text_reject_sampling.py:85 **四处复制粘贴**（reject_sampling 版还多了首字符截断，L103-105，行为与其余三份微妙不同），模板字符串也各自为政。格式契约一旦变更要同步改十几个文件——典型的"研究代码优先交付"权衡。

**数据文件即接口**意味着仓内大量文件实为运行时产物：`data/` 初始只有注册表，所有 train_*.json 都要先跑 process/ 才生成（见 06 篇）。

## 新人提示

1. 先读 readme.md 的 Main Experiments 节（L84-242），两条 demo 脚本是可执行的流程图。
2. 记住"一个数据集一条链"：medqa/pubmed 用 rare_share 检索包，pubhealth/casehold/finfact 从 HF 直下，mmrait 用 M2RAG 子集——三条入口三套跑法。
3. 别期望 import 关系帮你导航，按目录阶段读：process → inference → train → eval。
4. 仓与 readme 带伤（不存在的配置、拼错的文件名、语法错误的预实验），动线前先看 06 篇坑清单。
