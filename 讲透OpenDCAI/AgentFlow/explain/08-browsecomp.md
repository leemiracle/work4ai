# 08 · BrowseComp-V³ 加解密线：AES-256-GCM 数据保护与评测三件套

> 所属仓库：OpenDCAI/AgentFlow（图谱 909 节点/1857 边）。本篇覆盖 `projects/BrowseComp-V3/`——一个自带加密数据集的**多模态浏览 agent 基准**项目（300 道手工题，GPT-5.2 仅 36% 准确率），它嵌在 AgentFlow 仓里但自成一体：下载→解密→rollout→LLM judge 评测→汇总，全链自带。

## 一、角色定位

BrowseComp-V³（README.md:1-3，arXiv:2602.12876）评测的是"多模态深度搜索"：题目必须靠网页浏览工具+跨模态多跳推理才能解，且证据全部公开可搜（README.md:3"strictly enforce the public searchability"）。

它与其他线的关系：**独立平行项目**。不依赖 sandbox 服务、不依赖 synthesis 线，只用 OpenAI 兼容 API 直接单打（每题一次 VLM 调用，README.md:131）。AgentFlow 仓把它整个 vendored 进来（projects/ 目录还有一个 DocDancer，见第 06 篇），推测是为了共用 rollout 基建——但代码上它零 import 仓内其他模块，`grep bcv3/BrowseComp` 全仓只命中本目录与两份 README（README.md:1、README_zh.md 的推荐语）。

文件地图：`scripts/encryption_utils.py`（32 行核心加解密）+ `scripts/decryption_script.py`（65 行单文件 CLI）+ `scripts/decrypt_batch.py`（111 行批量 CLI）+ `run_rollout.py`（约 300 行推理）+ `eval_rollout_results.py`（39KB 评测）+ `summarize_eval_scores.py`（120 行汇总）+ `data/`（空，仅 .gitkeep，数据集要从 HuggingFace 下载）。

## 二、内部结构

### 加解密核心：encryption_utils.py（全 32 行）

三个函数一屏读完：

- **`derive_key`**（encryption_utils.py:6-10）：口令短语的 SHA-256 直接当 256 位密钥。没有盐、没有迭代、没有 KDF 函数——对口令强度的所有指望都在口令本身够长。
- **`encrypt_text`**（encryption_utils.py:12-23）：AES-256-GCM 加密。关键在第 17-18 行：`cryptography` 库的 `AESGCM.encrypt()` 返回的是 `密文||tag` 连体字节串，这里**手工切尾 16 字节**——`ct[:-16]` 是密文、`ct[-16:]` 是认证标签，然后三者（iv/ciphertext/tag）分别 base64 存成三字段 dict。
- **`decrypt_text`**（encryption_utils.py:25-32）：逆操作，`ciphertext + tag` 拼回连体串再解。GCM 解密同时做完整性校验，口令错了会抛 `InvalidTag` 异常。

方案本身（AES-256-GCM + SHA-256 派生）是密码学正统选择；README.md:46-48 也如实标注了算法与"IV/tag: 16-byte base64-encoded"（tag 16 字节准确；IV 长度代码未约束，由加密时的调用方决定）。

### 两个解密 CLI：高度重复的双格式探测

**`decryption_script.py`**——全量解密到单个 JSON。核心是格式探测（decryption_script.py:36-48）：一条记录若有 `encrypted_data` 字段则按"归档格式"（question/answer 塞在同一个 dict 里）解；若有 `encrypted_question` 则按"当前格式"（train.jsonl，两个字段各自是 JSON 字符串，还需再 `json.loads` 一次）解；两者都无则告警跳过。解出的明文直接覆盖写入 `question`/`answer` 键（decryption_script.py:50-51），默认删掉全部加密字段外加 `trajectory`（decryption_script.py:53-57）。

**`decrypt_batch.py`**——每样本一个 JSON 文件（decrypt_batch.py:88），rollout 推荐用这个。增量能力有三：口令走文件而非命令行（decrypt_batch.py:45，避免口令进 shell history）；`--limit N` 快速试跑（decrypt_batch.py:59-60）；`--copy-images` 把样本引用的图片从数据集根目录拷进输出目录（decrypt_batch.py:92-106），让 JSON 里的相对路径 `data/images/xxx.jpg` 在 rollout 时可解析。

**重复度实测**：decrypt_batch.py:64-86 与 decryption_script.py:36-57 是**逐字级重复**——格式探测 if/elif、解密两行、`pop` 清理四连，一段 22 行的代码原样出现两次。这是典型的"复制脚本改需求"产物，正确形态应是抽一个 `decrypt_record(obj, key) -> dict` 共享函数。

### rollout 与评测

**`run_rollout.py`**：扫 `--data_dir` 下所有 `*.json`（run_rollout.py:88），每题拼 question+图片的多模态消息（`_build_user_content`，run_rollout.py:102），一次 VLM 调用出最终答案（`run_one`，run_rollout.py:159）。域归类从 metadata JSON 里挖 d1 域名（run_rollout.py:34-41），输出按 `results/<model>/<domain>/<id>.json` 落盘（README.md:145）。`--dry_run` 只编码图片不发请求（README.md:144），调试图片路径时很有用。

**`eval_rollout_results.py`**（39KB，全项目最大文件）：LLM-as-judge 双层打分——**final answer 正确性** + **process score 过程分**。过程分对着数据集自带的 `sub_goals` 逐条判"是否被模型的预测子目标覆盖（ACHIEVED）"（eval_rollout_results.py:384、501 的 judge prompt 原文"covered by at least one..."）。judge 输出靠正则/文本解析抽 verdict（`extract_final_verdict`，eval_rollout_results.py:587），并发用 ThreadPoolExecutor（eval_rollout_results.py:829），支持断点续评（`load_existing_eval`，eval_rollout_results.py:704）。

**`summarize_eval_scores.py`**：纯聚合，按模型×域（d1/d2）×level×难度分桶算 final/process 均分（summarize_eval_scores.py:39-77），输出文本报表。

## 三、外部连接

- **HuggingFace 数据集** `Halcyon-Zhang/BrowseComp-V3`（README.md:8）——唯一数据源，仓内 `data/` 是空的（仅 .gitkeep），跑前必须下载 `train.jsonl`+`data/images/` 放进去（README.md:71）。
- **OpenAI 兼容 API**：rollout 读 `OPENAI_API_KEY`/`OPENAI_API_BASE` 环境变量（run_rollout.py:280-281），eval 同样（README.md:161，支持 .env 文件）。
- **对 AgentFlow 主仓**：零代码耦合，仅 README 互引。若要在 sandbox 里跑 tool-aided 版（OmniSeeker），README.md:147 指回项目主页，本仓未含其代码。
- **依赖**：`cryptography`（AESGCM）、`openai`、`python-dotenv`、`requests`（requirements.txt，README.md:186 特别说明 rollout 不需要 Pillow）。

## 四、数据流

```
HuggingFace 下载 train.jsonl + data/images/
  │  每行: {id, category, sub_category, image, image_paths,
  │         encrypted_question, encrypted_answer, metadata, sub_goals}
  ▼
decrypt_batch.py --key-file key.txt --output-dir decrypted_samples/ --copy-images ROOT
  │  derive_key(口令) → AESGCM.decrypt(iv, ciphertext+tag) → 明文覆写
  │  question/answer；产 <id>.json 一题一文件（含拷贝的图片）
  ▼
run_rollout.py --data_dir decrypted_samples/ --model_name gpt-4o
  │  每题: question+images → VLM → results/<model>/<domain>/<id>.json
  ▼
eval_rollout_results.py --input_dir results/gpt-4o --judge_model gpt-4o
  │  judge 判 final correctness + 逐 sub_goal 判 ACHIEVED
  │  → eval_gpt-4o.jsonl
  ▼
summarize_eval_scores.py eval_gpt-4o.jsonl → 域/层/难度分桶报表
```

密钥流是单向的：口令短语 → SHA-256 → AES key，全程不落盘（batch 版口令在独立 key.txt）。明文只在 decrypt 输出目录和 rollout results 里存在——评测完成后若要清理，删这两个目录即可。

## 五、设计决策（含批判）

**做得好的**：①GCM 自带完整性校验，口令错=解密失败而非静默产出乱码；②三字段分离存储（iv/ciphertext/tag）而不是一锅 base64，结构清晰可审计；③batch CLI 的 `--copy-images` 精准解决"JSON 相对路径 + rollout 工作目录"这个最常见的坑；④eval 的双层打分（结果对错+过程分）呼应了基准"process evaluation mechanism"的卖点（README.md:3）。

**要批判的**：

1. **加密的防护价值≈零**：口令短语明文写在 README.md:55（`A_Visual_Vertical_Verifiable_Benchmark_for_Multimodal_Browsing_Agents`，README.md:78、87、116 还各重复一遍）。任何人 clone 仓库即得口令。这套 AES-256-GCM 的真实作用是**法律/许可层护栏**（README.md:42"protect intellectual property while allowing community review"——你要主动执行解密动作，等于接受了数据集条款），不是对抗性安全。想清楚这一点就明白为什么 KDF 不加盐也无所谓——本来就不是防穷举的场景。
2. **双格式探测是历史包袱**：归档格式 `encrypted_data`（bcv3_encrypted.jsonl 时代）与新格式 `encrypted_question` 并存，两个 CLI 各自实现一遍探测，重复 22 行。更糟的是新格式的两个加密字段是"JSON 字符串里嵌 JSON"（decrypt_batch.py:70-71 要先 `json.loads` 再解密）——序列化器嵌套不一致，纯手工造数据的痕迹。
3. **删除 `trajectory` 字段混在清理逻辑里**（decryption_script.py:57、decrypt_batch.py:86）：`--keep-encrypted` 的语义其实是"保留加密字段"，但 trajectory 既不是加密字段也非敏感信息，默认被顺手删了。用它复现 tool-aided 实验的人会莫名丢数据。
4. **数据格式文档与字段不完全对齐**：README.md:60 说记录含 `image` 与 `image_paths`，代码里两者是或关系（decrypt_batch.py:18 `obj.get("image_paths") or obj.get("image")`）且 image_paths 可能是 JSON 字符串也可能是列表（decrypt_batch.py:19-26 四分支防御）——文档一句话，代码一捧防御，说明上游数据格式漂过。
5. **eval 文件 39KB 单文件**：judge prompt 模板、双套解析逻辑（final+process）混作一团，且 prompt 里中英文混杂（eval_rollout_results.py:737 的 help 是中文）。

## 六、新人提示

- **先跑通的最短路径**：①HF 下载放 `data/`；②`echo "A_Visual_..." > key.txt`；③`decrypt_batch.py --limit 5` 只解 5 条试水（decrypt_batch.py:42 的 `--limit` 就是干这个的）；④`run_rollout.py --dry_run` 验证图片编码；⑤小模型跑 5 题 → `eval` → `summarize`，全程半小时内可验证。
- **解密失败三连查**（README.md:123-125）：口令大小写、字段格式（是不是真 train.jsonl）、base64 是否完整。GCM 的 InvalidTag 几乎总是口令错。
- **别改 encryption_utils 的 16 字节切分**：`ct[:-16]` 是和 `cryptography` 库的返回格式（密文+tag 连体）绑死的，改成别的切分量直接全军覆没。
- **复用这套加密给自家数据集**：encrypt_text 在仓内没有对应 CLI（只有解密端），要用 Python API 手写加密循环（README.md:109-119 给了调用样例，但注意样例只演示了 decrypt）。
- **看懂一条样本**：decrypt 后的 JSON 里 `sub_goals` 是过程分的判分依据、`metadata` 里藏着域/难度分层（`_extract_domain_d1` 就是从这挖的，run_rollout.py:34），报表格子空往往是 metadata 解析失败。
- **与 AgentFlow 主线的互通**：想在 sandbox 里跑它的题，得自己写适配器把 `<id>.json` 转成 rollout 的任务格式——官方 tool-aided 路径（OmniSeeker）不在本仓。
