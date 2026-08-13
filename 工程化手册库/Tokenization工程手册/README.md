# Tokenization 工程手册

> **是什么**：把文字切成 token——LLM 处理的最小单位。
> **为什么重要**：Tokenizer 决定 LLM 的**多语言能力 / 编程能力 / 推理能力**。一个差的 tokenizer 让 GPT-4 也犯蠢。

---

## 1. 是什么

**Tokenization** = 文字 → token ID 序列。

```
"Hello world" → [15496, 995]  → embedding → transformer
```

**为什么不是字符级**？
- 字符级：序列太长（100K 字 → 100K token）
- 词级：词表太大（英语 100K+ 词）
- **子词（subword）**：折中——常用词完整，罕见词拆分

## 2. 主流算法

### BPE（Byte Pair Encoding）
- 从字符开始，**合并最高频对**
- `the` → `t` + `h` + `e` → `the`（如果高频）
- **GPT 系列 / Llama / Qwen 都用**

### WordPiece
- 类似 BPE，但基于**似然而非频率**
- **BERT 用**

### SentencePiece
- **语言无关**（不依赖空格分词）
- 适合中文/日文/韩文
- **T5 / Llama / Mistral 用**

### Unigram
- 从大词表**逐步删除**低频 token
- SentencePiece 的另一种模式

## 3. 各模型的 tokenizer

| 模型 | 算法 | 词表大小 | 特点 |
|------|------|---------|------|
| **GPT-4** | BPE (tiktoken) | ~100K | 英文优化 |
| **Llama 3** | tiktoken BPE | 128K | 多语言改进 |
| **Qwen 2.5** | BPE | 152K | 中文最优 |
| **Mistral** | SentencePiece | 32K | 精简 |
| **Claude** | BPE | ~100K | 英文优化 |
| **DeepSeek** | BPE | 100K | 中英平衡 |

## 4. 多视角深层

### 📐 数学
- Tokenizer = 学习一个映射 f: text → token_ids
- BPE 优化目标：最大化压缩率（最少 token 表示最多文字）
- **信息论**：好的 tokenizer 最小化平均 bits/character

### 🌐 语言学
- **Token ≠ 词 ≠ 字**——是子词
- 英文：1 word ≈ 1-2 tokens
- 中文：1 字 ≈ 1-2 tokens（取决于 tokenizer）
- **代码**：`def fibonacci(n):` 可能是 5-10 tokens

### 🧠 认知科学
- Token ≈ 人的"**组块**"（chunking）
- 人不逐字读——按"词/短语"读
- Tokenizer 模拟这个过程

### 💾 信息论
- 好的 tokenizer 最小化**信息丢失**
- 但 token 是离散的 → 有损
- **关键**：tokenizer 决定了 LLM 的"感知粒度"

## 5. Tokenizer 的问题

### 问题 1：字符级信息丢失
- GPT 不知道 `abc` 和 `acb` 哪个在前（在 token 内部看不到字符顺序）
- **拼写任务表现差**

### 问题 2：多语言不公平
- 英文：1 word = 1 token → 便宜
- 中文：1 字 = 2-3 token → **贵 2-3 倍**
- **经济不平等**：非英文用户付更多

### 问题 3：代码 token 不规则
- ``` ( ``` 和 ```)``` 可能是不同 token
- 空格处理不一致
- **影响代码生成质量**

### 问题 4：数字处理
- `12345` 可能是 1 个 token 或 3 个（`12` + `345` 或 `1` + `234` + `5`）
- **影响数学能力**
- Llama 3 修正：数字逐位 tokenize

### 问题 5：对抗后缀
- 特殊 token 组合可以越狱（`SYSTEM:` `HUMAN:` 等）
- **安全风险**

## 6. 实战

```python
import tiktoken

enc = tiktoken.encoding_for_model("gpt-4")
tokens = enc.encode("Hello, 世界!")
print(tokens)  # [9906, 11, 364, 10547, 0]
print(len(tokens))  # 5 tokens

# 反编码
print(enc.decode(tokens))  # "Hello, 世界!"

# 中文 token 数
cn = enc.encode("你好世界")
print(len(cn))  # 可能 4-6 tokens（中文 token 效率低）
```

## 7. 反模式 10 条

1. **以为 1 word = 1 token**（中文/代码差很多）
2. **不计算 token 成本**（API 按 token 收费）
3. **tokenizer 不匹配**（训练用 A，推理用 B）
4. **忽略 max_seq_length**（超长被截断）
5. **特殊 token 冲突**（用户输入含 `<|endoftext|>`）
6. **数字 tokenize 不一致**（影响数学）
7. **多语言 tokenizer 选错**（英文 tokenizer 做中文）
8. **不更新 tokenizer**（新词/新 emoji 不认）
9. **vocab 太小**（罕见词被拆碎）
10. **vocab 太大**（embedding 层巨大）

## 8. 趋势

- **Byte-level tokenizer**：直接处理字节，**语言无关**
- **Dynamic tokenizer**：根据上下文动态调整
- **Multimodal tokenizer**：统一文本 + 图片 + 音频
- **Token-free models**：直接从字符/字节学习（Mamba / ByT5）

---

**核心理念**：**Tokenizer 是 LLM 的"感知器官"。好的 tokenizer = 好的感知 = 好的理解。差的 tokenizer 让 GPT-4 也犯蠢。**
