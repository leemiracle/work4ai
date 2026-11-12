# 讲透 RULER

> NVIDIA/RULER —— 长上下文 LLM 合成评测基准：五族任务生成器（NIAH 八变体/VT/CWE/FWE/QA）×4K-131K 长度阶梯×三引擎（vLLM/TRT-LLM/SGLang）五家 Client，实测模型真实有效上下文窗口。
> 本地仓：/usr-data/data2/repos/agent-repos/NVIDIA/RULER（commit c3f5e3b4）

## 状态（2026-11-10 ✅ 全链路完成）

| 步骤 | 状态 | 产物 |
|---|---|---|
| DeepWiki 全量 | ✅ | [deepwiki/](deepwiki/)（25 内容页 100%） |
| understand 中文图谱 | ✅ | 仓内 `.understand-anything/knowledge-graph.json`（**88 节点/166 边/4 层/6 步 tour**，validator 0 issues，fingerprints 29 文件基线@c3f5e3b4） |
| onboarding | ✅ | [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md)（9390 不计空格字符，7 节，98 行号锚全验证通过） |
| explain 系列 | ✅ | [explain/](explain/) 2 篇（3930/4156 字符，六节结构，锚 23+24 全验证） |

## explain 索引（2 篇）

| # | 篇 | 对象 |
|---|---|---|
| 01 | [data-generation.md](explain/01-data-generation.md) | 造数流水线：五任务生成器+importlib 动态加载+tokenizer/template 公平性机制 |
| 02 | [prediction-serving.md](explain/02-prediction-serving.md) | 预测侧：五家 Client 延迟 import+冒号串配置协议+三引擎服务 |

## 本轮沉淀的勘误（对 DeepWiki/图谱摘要/NOTES 的修正，均源码实证）

- **english_words.json 是 Git LFS 指针**：磁盘仅 3 行（oid sha256:affcd6d4.../size 8564991），不 `git lfs pull` 词堆类任务必炸——.gitattributes:1-3 把 *.jsonl/*.jsonls/*.json 全划给 LFS，README 未提醒
- **OpenAIClient/GeminiClient 不继承 Client 基类**（scripts/pred/client_wrappers.py:188/:342 裸类声明）——图谱摘要"五个远程客户端均派生自抽象基类"不成立，继承者只有 TRTLLM/VLLM/SGL 三家（:108/:136/:161）
- **对话模板 11 种非 12 种**（scripts/data/template.py:16-36 实数：base/meta-chat/vicuna-chat/lwm-chat/command-r-chat/chatglm-chat/RWKV/Phi3/meta-llama3/jamba/nemotron5-instruct）
- **"call_api 顶层 import 仅 stdlib"不准**：顶层有 tqdm（scripts/pred/call_api.py:42）与 nemo read_manifest（:45）；真正延迟的是本仓 client_wrappers/model_wrappers 的 7 处函数体内 import（:100-:183）——静态 import 图对这类文件必然不全（图谱已按源码补边）
- **依赖两套并行清单**：requirements.txt 之外 Dockerfile 单独 pin flash-attn 2.6.0.post1/rotary/causal-conv1d 1.4.0/mamba-ssm 2.2.2 四个 Mamba 系硬依赖且 --no-build-isolation 源码编译（docker/Dockerfile:22-25）
- **SGLang 无仓内服务脚本**：由 run.sh 直接 `python -m sglang.launch_server` 外部拉起（scripts/run.sh:75-76），serve_vllm.py/serve_trt.py 才是仓内资产

## 工程信息

- 流水线：DeepWiki MCP 通道 + understand 批分析 + layers/tour + finalize + 写作收官
- 字数口径：不计空格总字符；行号锚口径：仓内唯一 basename 自动展开后逐一验证（98/23/24 全过）
