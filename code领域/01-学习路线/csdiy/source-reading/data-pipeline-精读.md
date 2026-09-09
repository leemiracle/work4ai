# Data Pipeline 精读：数据质量 > 模型大小

> 参照：Phi-2/3 (Microsoft) / LLaMA-2 数据管线 / DataComp
>
> csdiy 对应：tinydataset(原) + nanoGPT精读 + AI核心

---

## 一、核心洞察：Data is All You Need

```
Phi-3 mini (3.8B) 在 MMLU 上超越 LLaMA-2 (7B)
→ 模型小 2x 但数据质量高 10x

结论: 数据质量 > 模型大小
"Garbage in, garbage out" — 低质量数据训出低质量模型
```

---

## 二、预训练数据管线（LLM）

```
原始数据 (互联网爬取)
  ↓ ① 去重（Deduplication）
  ↓ ② 质量过滤（Quality Filter）
  ↓ ③ 安全过滤（Safety Filter）
  ↓ ④ 文本提取（HTML→纯文本）
  ↓ ⑤ Tokenization
  ↓ ⑥ 数据混合（Data Mixing）
训练数据
```

---

## 三、去重（最重要的步骤）

### 为什么去重

```
互联网数据大量重复（新闻转载/博客抄袭/模板内容）

不去重:
  → 模型"记住"重复内容 → 泛化能力差
  → 有效数据量虚高
  → 训练效率低

LLaMA-2: 去重后保留 ~30-50% 原始数据
```

### 去重方法

```
① 精确去重: hash(document) → 相同哈希 = 完全重复
② 模糊去重: MinHash + LSH → 相似度高 = 近似重复
③ 段落级去重: 每个 paragraph 独立 hash
④ 跨数据集去重: 训练集 vs 测试集去重（防止数据泄露）
```

### MinHash + LSH（参照 bloom-filter精读）

```
MinHash: 把文档压缩成固定长度的签名
LSH (Locality-Sensitive Hashing): 相似文档映射到相同桶

→ 近似去重 → O(N) 而非 O(N²)
```

---

## 四、质量过滤

### 启发式规则

```
保留:
  ✅ 长度 > 50 词（排除碎片）
  ✅ 字母/数字比例 > 0.5（排除乱码）
  ✅ 平均句长 5-100 词
  ✅ 不含过多重复 n-gram

丢弃:
  ❌ 包含太多特殊字符
  ❌ HTML/XML 标签残留
  ❌ 不自然语言（日志/代码混入）
```

### 模型过滤

```
训练一个质量分类器:
  正例: Wikipedia / 高质量书籍
  负例: 随机互联网文本

用分类器给每篇文档打分 → 只保留高质量文档

代表: CCNet (CommonCrawl 质量过滤)
```

---

## 五、数据混合（Data Mixing）

### 为什么要混合

```
如果只训练互联网爬取的文本:
  → 质量参差不齐 → 模型学不好推理

混合高质量来源:
  Wikipedia: 4%（高质量知识）
  书籍: 5%（长文本 + 推理）
  代码: 5%（逻辑推理能力）
  论文: 2%（学术能力）
  互联网: 67%（广度覆盖）
  对话: 5%（对话能力）
  数学: 2%（数学推理）
```

### 课程学习（Curriculum Learning）

```
从简单到困难逐步训练:

Phase 1: 大量通用文本（学语言能力）
Phase 2: 高质量文本（学推理能力）
Phase 3: 指令数据（学遵循指令）

→ 比"一次性混合训练"效果更好
```

---

## 六、数据增强（Data Augmentation）

### 文本增强

```
① 回译: EN → ZH → EN'（产生多样化表达）
② 同义词替换: "开心" → "快乐"
③ 随机删除/插入/交换
④ 模板生成: 用 LLM 生成指令变体

高质量增强: 用 GPT-4 生成训练数据（Alpaca/Vicuna 式）
```

### 指令数据生成

```
Self-Instruct (Wang 2022):
  ① 用 LLM 生成任务指令
  ② 用 LLM 生成回答
  ③ 过滤低质量样本
  → 自动生成大量训练数据

Evol-Instruct (WizardLM):
  ① 从简单指令开始
  ② 逐步"进化"为更复杂的指令
  → 递增难度的训练数据
```

---

## 七、指令微调数据

### 格式

```json
{
  "instruction": "把以下句子翻译成英文",
  "input": "今天天气很好",
  "output": "The weather is nice today"
}
```

### 质量 > 数量

```
LIMA (Meta 2023):
  1,000 条精心标注的指令数据
  → 微调 LLaMA → 效果接近 GPT-4（在某些任务上）

结论: 1,000 条高质量 > 100,000 条低质量
```

### 数据格式的影响

```
Alpaca 格式: {"instruction", "input", "output"}
ChatML 格式: {"role": "system/user/assistant", "content"}
ShareGPT 格式: 多轮对话

→ 不同格式训练出的模型能力不同
→ 要和生产环境的推理格式一致
```

---

## 八、数据质量评估

### Perplexity 评估

```
用目标模型在高质量文本上的 PPL:
  PPL 低 → 数据和模型匹配
  PPL 高 → 数据噪声多
```

### 数据多样性

```
n-gram 多样性: unique n-grams / total n-grams
主题分布: 用聚类检查是否覆盖足够主题
语言分布: 多语言比例
```

### DataComp 基准

```
固定模型 → 竞争数据管线 → 比拼下游任务性能
→ 数据管线的 "ImageNet"
```

---

## 九、一句话总结

> 去重（MinHash+LSH）→ 质量过滤（分类器）→ 混合（代码+数学+Wikipedia）→ 课程学习。
>
> Phi-3 (3.8B) 超越 LLaMA-2 (7B) → 数据质量 2x > 模型大小 2x。
>
> **LLM 训练的 80% 工作在数据处理，不在模型架构。**

---

*配套：[nanoGPT精读](nanoGPT-读懂最小GPT.md) | [tokenizer-deep精读](tokenizer-deep-精读.md) | [llm-evaluation精读](llm-evaluation-精读.md)*
