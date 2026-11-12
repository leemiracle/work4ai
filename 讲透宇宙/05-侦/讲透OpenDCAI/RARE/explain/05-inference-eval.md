# 05 inference/ 蒸馏引擎 + eval/select_true 筛真与评估

## 角色定位

`inference/` 四脚本承担"教师蒸馏"与"学生推理"双角色：`vllm_infer_text.py` 文本批量生成、`vllm_infer_mm.py` 多模态版、`vllm_infer_text_reject_sampling.py` 拒绝采样蒸馏（readme.md:134 推荐用它提质）、`api_infer_post.py` 打闭源 API 做 RAG 基线。`process/select_true.py` 与 `eval/eval.py` 是紧随其后的筛真与评分，共享同一套答案抽取正则。

## 内部结构

**`vllm_infer_text.py`（266 行）**：`format_prompt` 按模板名拼 chat 前缀（L21-33），`get_stop_tokens` 给停止符（L36-47）；`vllm_infer` 主流程（L81-188）：读数据集（instruction 多键回退，L111-113）→ SamplingParams → 初始化 vLLM（L137-143）→ 批量 generate → 输出写回 `prediction_key`（默认 predict，L153）→ **原地改写输入文件**，改前做 .bak 备份（L158-165）。函数签名与 argparse 默认值**三处不一致**：max_new_tokens 8192 vs 10240、tensor_parallel 4 vs 8、max_model_len 10240 vs 20480（L88-91/L222-240）——CLI 实际生效 argparse 侧。

**`vllm_infer_mm.py`（358 行）**同构，多出 `prepare_multimodal_inputs`（L86-129）：把 images 注入 user 消息，每图限 224²~1280×28×28 像素（L114-115）；prompt 走 `AutoProcessor.apply_chat_template`（L179-183），图像由 `process_vision_info` 预处理（L186-188）；每 prompt 限 10 图（L224）；结果双写成 assistant 消息+prediction_key（L238-244）。temperature 默认 0.6（L305）。

**`reject_sampling.py`（407 行）**：`extract_option`（L85-105）+ `check_answer`（L108-112）判分；主循环（L176-230）对答错样本反复采样最多 8 次（L127），首轮存 original（L207-209），耗尽的回滚首轮输出（L237-239）；另存 `_resampled` 并顺手产出 `_true` 筛真文件（L264-288）。`clean_up` 兼顾 NPU 与 CUDA（L14-22）。

**`select_true.py`（118 行）**：text 模式比对 `predict` vs `output`（L57/68），mm 模式读 `messages[1].content`（L64）；答对样本进 `*_true.json`（L77），mm 模式按目录判定拷图片（L83-97）。**`eval.py`（69 行）**：`extract_option`（L6-22）四级正则；`calculate_accuracy`（L25-48）比对并统计抽取率。

## 外部连接

教师模型来自 ModelScope 下载；`api_infer_post.py` 是独立的 aiohttp 异步客户端（20 次退避重试、temp/ 分片断点续跑），打通闭源基线。demo 两条链把全部组件串成可复制命令。

## 数据流

文本线（demo/llama_pubmedqa_rare.sh）：process 构建 → QwQ-32B 蒸馏写 predict（L12-15）→ torchrun SFT → 同一脚本换模型对 test 集推理（L47-52）→ eval 评分（L55-57）。多模态线（demo/qwenvl_mmrait_rare.sh）：蒸馏（L11-13）→ `select_true.py --mm`（L16）→ accelerate 训练（L19-20）→ 推理（L26-30）→ eval（L33-35）。

## 设计决策（含批判）

`extract_option` 在 eval.py:6、select_true.py:8、RL_KTO/process_kto.py:5、vllm_infer_text_reject_sampling.py:85 **四处复制**——前两者逐字节同源，reject_sampling 版多出"首字符在 ABCDE 内则截断"（L103-105），行为有分叉：同一段含混输出在不同环节可能判出不同选项。readme.md:125 又规定"select_true 只对 medqa/casehold/finfact 做"（pubmed 例外）。**demo 拼写坑**：qwenvl_mmrait_rare.sh:34 写 `--file data/test_mmarit.json`——多了个 r，真实文件是 `test_mmrait.json`（process_mmrait.py:9），照抄必 FileNotFoundError。readme.md:129 还有 `scripts/vllm_infer_mm.py` 错路径（实际在 inference/）。原地改写输入文件让"重跑"需手动恢复 .bak，多轮蒸馏会叠加污染。

## 新人提示

1. 多模态 demo 到 eval 步把 `test_mmarit.json` 改成 `test_mmrait.json`——全链最后一米的雷。
2. 蒸馏前确认 .bak 不存在（存在则不覆盖，L159），排查旧数据先看备份时间戳。
3. eval 的 prediction_key 必须与推理时写的 key 逐字符一致，常见错误是拿教师的 predict 评学生。
4. 想提质蒸馏数据就换 reject_sampling 版（readme.md:134），用法相同且自带筛真产出。
