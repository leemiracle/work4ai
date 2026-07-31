# 13 Tokenizer：Transformer 的文本前端

> Transformer 不直接读文本, 它读 **token id 序列**。Tokenizer 把文本切成 token, 是大模型的"输入前端"。
> 现代标准: **BPE** (Byte-Pair Encoding), 大词表 (128K), 多语言优化。

---

## 为什么需要 Tokenizer?

Transformer 的输入是整数序列 `input_ids`, 嵌入层把它们查表成向量。所以必须先把文本 → token → id:
```
"hello world"  ──tokenizer──>  ["hello", " world"]  ──vocab──>  [15339, 995]
```

**三个相互冲突的目标**:
1. **词表别太大**: 嵌入层和 lm_head 是 $O(\text{vocab} \times d)$ 参数, 词表翻倍这两层翻倍
2. **别切成单字符**: "hello" 切成 5 个字符 token 太碎, 浪费序列长度
3. **能处理任何文本**: 包括未见过的词、emoji、代码、中文 → 需要 subword (子词)

---

## 主流算法演化

```
Word-level    整词, 词表爆炸, 无法处理新词
  │
  ▼
Char-level    单字符, 序列太长, 丢失词义
  │
  ▼
WordPiece      (BERT 用) 类似 BPE, 基于似然
  │
  ▼
BPE            ★ 现代 GPT/LLaMA 标准 ★  高频对合并
  │
  ▼
SentencePiece  BPE 的实现框架, 支持无空格语言(中日韩), LLaMA/Qwen 用
  │
  ▼
Byte-level BPE 在【字节】上做 BPE, 永不 OOV (GPT-2/4)
```

---

## BPE 算法 (核心, 三层讲透)

### 直觉
从"所有单个字符"开始, 反复找出语料里**出现频率最高的相邻 token 对**, 合并成一个新 token, 加入词表。重复直到词表达到目标大小。

### 算法 (训练)
```
初始词表 = 所有单字符
循环直到词表 = V:
    统计语料中所有相邻 token 对的频率
    合并频率最高的对 (如 "t"+"h" → "th")
    "th" 加入词表
```
例: "the the" → 字符级 ['t','h','e','t','h','e'] → 合并 'th' → ['th','e','th','e'] → 合并 'the' → ['the','the']

### 推理 (编码新文本)
用训练得到的合并规则, **贪心**地对新文本做同样的合并。未见过的词会被切成已知的 subword (如 "tokenization" → "token" + "ization"), **永不产生 OOV** (out-of-vocabulary)。

---

## 现代趋势 (2023-2026)

### 1. 大词表 + 压缩比
LLaMA-3 用 **128K** 词表 (vs GPT-2 的 50K)。更大词表 → 每个 token 覆盖更多字符 → 同样文本 token 数更少 → 序列更短 → 训练/推理更省。Meta 明确说这提升多语言和代码效率。

### 2. 多语言
中文/代码需要专门优化。Qwen/DeepSeek 的 tokenizer 对中文压缩比远好于纯英文训练的 tokenizer。

### 3. 特殊 token
`<|im_start|>` (ChatML)、`<|endoftext|>` 等控制 token, 是对齐格式的基础。

### 4. tie weights
`lm_head.weight = embed_tokens.weight` (权重绑定), 嵌入层和输出层共享, 省一半词表参数。LLaMA 就是这么做的 (11 篇 `_tied_weights_keys`)。

---

## Tokenizer 影响一切

| 指标 | 受 tokenizer 影响 |
|------|------------------|
| 序列长度 | 压缩比差 → 同样文本 token 多 → 更长 → 更贵 |
| 多语言能力 | 中文切得碎 → 模型学中文更难 |
| 代码能力 | 代码 token 化好 → 学代码更高效 |
| 推理成本 | token 数 ∝ FLOPs 和 KV Cache |

> 💡 **这就是为什么 GPT-4o 把词表从 ~100K 扩到 ~200K**——压缩比提升直接降低每 token 成本。

---

## 速查

| Tokenizer | 代表 | 词表 | 特点 |
|-----------|------|------|------|
| BPE | GPT-2/3/4, LLaMA | 32K-128K | 现代 GPT 标配 |
| SentencePiece BPE | LLaMA, Qwen | 32K-152K | 支持无空格语言 |
| WordPiece | BERT | 30K | 历史遗产 |
| Tiktoken | GPT-4o | ~200K | OpenAI 的高效 BPE 实现 |

---

## 代码: 用 transformers 看 tokenizer
```python
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B")
ids = tok("hello world")["input_ids"]      # [15339, 995]
print(tok.convert_ids_to_tokens(ids))      # ['hello', ' world']
print(tok.vocab_size)                        # 128256
```

## 参考文献
- Sennrich et al. 2016, *Neural Machine Translation of Rare Words with Subword Units* (BPE)
- Kudo & Richardson 2018, *SentencePiece* (SentencePiece)
- Ranger et al. 2024, *Tokenization Is More Than Compression* (tokenizer 对能力的影响)
