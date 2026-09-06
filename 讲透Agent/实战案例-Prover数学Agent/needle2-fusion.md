# Needle 2 借法：窄域蒸馏 + 量化训练方案（融合笔记）

> card_id: needle2-distill-fusion
> universe: 讲透Agent/实战案例-Prover数学Agent
> burke: 场景=DCU 服务器逆向蒸馏 Prover 模型；主体=DeepSeek-Prover-V2-7B→LoRA 学生；行动=借 Needle 2 四做法；目的=端侧化/降本；张力=7B 太大 vs 45M 太专；弧线=先窄域 SFT，再 QAT，最终小模型
> status: 草案（2026-08-25，实验进行中）
> refs: arXiv:2607.18363 (SAN), cactus-needle docs, distill_pipeline.py
> updated: 2026-08-25

## 一、Needle 2 的四条核心做法 → 本任务映射

| Needle 2 做法 | 一句话原理 | 蒸馏任务对应物 | 状态 |
|---|---|---|---|
| **窄域专攻**（放弃通用聊天） | 场景足够专一时，激进放弃通用能力是正确工程决策 | 只训 "Lean 4 core 证明" 单域；题库→ZPD 策展（R2） | ✅ pipeline 已跑 |
| **训练期内置量化**（CQ2-bit QAT，部署=训练模型） | PTQ 在 2-bit 崩溃；量化噪声从预训练就进入梯度路径 | LoRA SFT 后接 QAT→INT8（DCU 有 int8 路径）；"部署模型=训练模型" | 🔶 方案见 §三 |
| **KV 有界**（256-token 滑窗 + KV Sinks 钉住工具定义） | 内存恒定不随对话涨 | 证明场景天然短（22-825 tok）；系统提示(核心库限制)≈sink | ✅ 天然满足 |
| **语法约束解码**（schema→grammar，跳过 98% 词表投影） | 只算合法 token；但前提是输出空间封闭 | Lean 是半开放空间——H2：强约束反伤通过率 | 🔶 实验脚本已备（prover_grammar_decoding.py） |

## 二、已验证的对应关系（数据锚点）

- **R8 双模式节奏** = Needle 的"紧凑推理轨迹"：non-CoT 22-45tok（简单题）vs CoT 581-825tok（复杂题）——训练数据里保留 plan 字段可消融
- **Needle `generate-data`**（schema→JSONL）≈ `distill_pipeline.py`（题库+分解→JSONL）：都是"从结构化源合成微调数据"
- **Needle `finetune`**（冻结底座+LoRA r16 α32→合并单文件）≈ `finetune_lora.py`（冻结 Prover-V2-7B + LoRA r16 α32→合并→vLLM 单目录 serve）

## 三、QAT 路线（下一阶段，借鉴 CQ2-bit "训练即量化"）

### 为什么不做 PTQ
GPTQ/AWQ/HQQ 在 ≤2-bit 崩溃是 Needle 文档明示的；4-bit PTQ 在 7B Prover 上精度损失未知。
而 QAT 让量化噪声进入训练梯度路径，模型学会"在量化格点上工作"。

### 务实三步（DCU 栈约束下的妥协）
1. **LoRA SFT**（fp16，先拿到 domain 增益）——进行中
2. **QAT-INT8**：torch.ao.quantization 或 DTK 的 hquant（若容器内有）；LoRA 权重保持 fp16，base 量化——"混合精度 QAT"
3. **评估对照**：eval_holdout 三方比较 base / base+LoRA / base+LoRA+QAT
   - 若 QAT 掉点 >5pp → 退回 PTQ-INT8（vLLM 加载时量化）或保 fp16

### 诚实边界
- DCU 栈对 torch.ao 的支持未知，需冒烟；厂商 hquant 文档稀缺
- Cactus CQ 是自研 2-bit 方案，我们最多复现"QAT 思想"而非 CQ 本身
- 45M 级别压缩（1/150）不现实——我们的终点是 INT8 7B（≈7GB）或后续换 0.5B 底座

## 四、批判性小结（什么不该学）

1. **Needle 的 45M 是"从零设计"的产物**（SAN 架构+8192 词表+115B tokens 预训练），不是压缩大模型得来的——"蒸馏出 45M" 是误解，它走的是窄域从零训练路线。我们的 7B+LoRA 是另一条路：**改造成本最小化**而非**参数极限化**
2. **语法约束的适用边界**：JSON 工具调用（封闭）收益巨大；Lean 证明（半开放）预期收益归零甚至为负——这正是 grammar 实验要量化的
3. **Engram 记忆（检索替代参数）**对证明场景有潜在价值：把 mathlib 引理名做检索注入——但这改变 harness 架构，超出本轮范围

## 五、下一步

- [ ] grammar 实验跑完 → 验证 H1/H2 → 回填本表
- [ ] LoRA SFT → eval 三方对照
- [ ] QAT 冒烟（torch.ao 在 DCU 的可用性）
