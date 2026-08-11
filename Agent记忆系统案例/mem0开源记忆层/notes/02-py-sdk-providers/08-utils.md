# 08 — utils（entity_extraction + scoring + lemmatization + factory）

> `mem0/utils/` 是跨模块工具集。本篇重点 3 个核心：entity 抽取（NER）、BM25 评分、lemmatize。

---

## 1. utils/ 全清单

```
mem0/utils/
├── factory.py             # ⭐ 4 个 Factory 类（详见 07-factory.md）
├── entity_extraction.py   # ⭐ spaCy NER 抽实体
├── scoring.py             # ⭐ BM25 + entity boost + 融合
├── lemmatization.py       # ⭐ spaCy lemmatize for BM25
├── spacy_models.py        # spaCy model 单例缓存
├── http.py                # HTTP client 工具
├── gcp_auth.py            # GCP 认证 helper
└── (memory/utils.py 在 mem0/memory/,不是这里)
```

---

## 2. ⭐ `entity_extraction.py`

### 设计目标

抽 3 种 entity：

```python
"""
Extracts three types of entities from a spaCy-processed document:
- **Proper nouns**: Capitalized multi-word sequences (person names, places, brands)
- **Quoted text**: Text in single or double quotes (titles, specific terms)
- **Noun compounds**: Multi-word noun phrases with specific modifiers (e.g., "machine learning")

Returns:
    List of ``(entity_type, entity_text)`` tuples where entity_type is one of
    PROPER, QUOTED, TOPIC, or IDENTIFIER.
"""
```

### 4 种 entity type

| type | 来源 | 例子 |
|------|------|------|
| `PROPER` | spaCy NER（PERSON/ORG/GPE/...） | "Apple", "John Smith", "San Francisco" |
| `QUOTED` | 引号文本 | `"Inception"`, `'The Nightingale'` |
| `TOPIC` | 名词 compound | "machine learning", "neural network" |
| `IDENTIFIER` | 特定模式 | "model X", "version Y" |

### 过滤 generic heads

```python
_GENERIC_HEADS = {
    "thing", "stuff", "way", "time", "experience", "situation",
    "case", "fact", "matter", "issue", "idea", "thought", "feeling",
    "place", "area", "part", "kind", "type", "sort", "lot", "bit",
    "day", "year", "week", "month", "moment", "instance", "example",
    "technique", "method", "approach", "process", "step", "tool",
    "result", "outcome", "goal", "task", "item", "topic", "scale",
    "size", "level", "degree", "amount", "number", "style", "look",
    "color", "colour", "shape", "form", "piece", "section", "side",
    "end", "edge", "surface", "point",
}
```

> 太 generic 的词（如 "the best thing"）不抽——它们的"实体性"很弱。

### 公共 API

```python
def extract_entities(text: str) -> List[Tuple[str, str]]:
    """单 text 抽 entity, owns spaCy model loading."""

def extract_entities_batch(texts: List[str]) -> List[List[Tuple[str, str]]]:
    """批量,用 nlp.pipe 加速。"""
```

> `nlp.pipe` 是 spaCy 的批量处理 API,比循环 `nlp(text)` 快 5-10 倍。

### NER label 白名单

```python
_ACCEPTED_NER_LABELS = {
    "PERSON", "ORG", "GPE",          # 人/组织/地点
    "LOC", "FAC", "PRODUCT",         # 地理位置/设施/产品
    "EVENT", "WORK_OF_ART",          # 事件/作品
    "LAW", "LANGUAGE",               # 法律/语言
    "NORP",                          # 民族/宗教/政治团体
    # 不含 CARDINAL/ORDINAL/QUANTITY/MONEY/PERCENT/DATE/TIME
    # 这些不是"实体",是数值/时间
}
```

---

## 3. ⭐ `scoring.py`（fusion 公式核心）

### BM25 参数选择（query 长度自适应）

```python
def get_bm25_params(query: str, *, lemmatized: Optional[str] = None) -> tuple:
    """Get BM25 sigmoid parameters based on query length.

    Longer queries tend to have higher raw BM25 scores, so we adjust
    the sigmoid midpoint and steepness accordingly.

    Returns:
        (midpoint, steepness) for sigmoid normalization.
    """
    if lemmatized is None:
        lemmatized = lemmatize_for_bm25(query)
    num_terms = len(lemmatized.split()) if lemmatized else 1

    if num_terms <= 3:
        return 5.0, 0.7
    elif num_terms <= 6:
        return 7.0, 0.6
    elif num_terms <= 9:
        return 9.0, 0.5
    elif num_terms <= 15:
        return 10.0, 0.5
    else:
        return 12.0, 0.5
```

> **直觉**：query 越长,BM25 raw score 越高（更多词命中）。sigmoid midpoint 提高,让 normalized score 不至于全是 1.0。

### BM25 归一化（sigmoid）

```python
def normalize_bm25(raw_score: float, midpoint: float, steepness: float) -> float:
    """Sigmoid normalize to [0, 1]."""
    return 1.0 / (1.0 + math.exp(-steepness * (raw_score - midpoint)))
```

### BM25 参数表

| query 长度 | midpoint | steepness | raw=5 时输出 | raw=10 时输出 |
|----------|---------|----------|------------|-------------|
| ≤3 词 | 5.0 | 0.7 | 0.5 | ~0.97 |
| 4-6 词 | 7.0 | 0.6 | 0.23 | 0.73 |
| 7-9 词 | 9.0 | 0.5 | 0.13 | 0.62 |
| 10-15 词 | 10.0 | 0.5 | 0.077 | 0.5 |
| >15 词 | 12.0 | 0.5 | 0.028 | 0.27 |

### ⭐ `ENTITY_BOOST_WEIGHT`

```python
ENTITY_BOOST_WEIGHT = 0.5
```

> 全局常量,entity boost 的最大权重。0.5 意味着 entity 信号最多贡献 final score 的 ~30%（融合时除以 max_possible）。

### ⭐ `score_and_rank`（fusion 主函数）

```python
def score_and_rank(
    semantic_results: List[Dict[str, Any]],
    bm25_scores: Dict[str, float],
    entity_boosts: Dict[str, float],
    threshold: float,
    top_k: int,
    explain: bool = False,
) -> List[Dict[str, Any]]:
    """Score candidates additively and return top-k results.

    For each candidate:
        semantic_score is taken from the result's score field.
        combined = (semantic + bm25 + entity_boost) / max_possible

    Threshold gates the semantic score BEFORE combining -- candidates
    below the threshold are excluded even if BM25/entity would boost them.

    The divisor adapts based on which signals are active:
        - Semantic only: max_possible = 1.0
        - Semantic + BM25: max_possible = 2.0
        - Semantic + BM25 + entity: max_possible = 2.5
        - Semantic + entity (no BM25): max_possible = 1.5
    """
    has_bm25 = bool(bm25_scores)
    has_entity = bool(entity_boosts)

    max_possible = 1.0
    if has_bm25:
        max_possible += 1.0
    if has_entity:
        max_possible += ENTITY_BOOST_WEIGHT   # 0.5

    scored = []
    for result in semantic_results:
        mem_id = result.get("id")
        if mem_id is None:
            continue

        semantic_score = result.get("score") or 0.0
        # ⭐ threshold 门槛（仅对 semantic score）
        if semantic_score < threshold:
            continue

        mem_id_str = str(mem_id)
        bm25_score = bm25_scores.get(mem_id_str, 0.0)
        entity_boost = entity_boosts.get(mem_id_str, 0.0)

        raw_combined = semantic_score + bm25_score + entity_boost
        combined = min(raw_combined / max_possible, 1.0)
        # ... 加 score_details 等
```

### 关键设计

| 设计 | 为什么 |
|------|-------|
| `max_possible` 自适应 | 防止"3 信号都激活"时分数膨胀到 >1.0 |
| threshold 门槛仅对 semantic | 防 BM25/entity 把无语义关联的推上来 |
| 加性融合 | 简单可解释,各信号权重一目了然 |
| `combined = min(..., 1.0)` | clamp 防 >1.0 |

### 融合公式总结

```
final_score = min((semantic + bm25 + entity_boost) / max_possible, 1.0)

其中:
- semantic ∈ [0, 1]（vector store 返回）
- bm25 ∈ [0, 1]（normalize_bm25 后）
- entity_boost ∈ [0, 0.5]（ENTITY_BOOST_WEIGHT × similarity × memory_count_weight）
- max_possible ∈ {1.0, 1.5, 2.0, 2.5}（看哪些信号激活）
```

---

## 4. ⭐ `lemmatization.py`

```python
def lemmatize_for_bm25(text: str) -> str:
    """Lemmatize text for BM25 matching.

    Returns space-joined lemmas for full-text search. Falls back to
    the original text if spaCy is unavailable.
    """
    from mem0.utils.spacy_models import get_nlp_lemma

    nlp = get_nlp_lemma()
    if nlp is None:
        return text   # spaCy 没装,fallback

    doc = nlp(text.lower())
    tokens = []

    for token in doc:
        # 去标点和停用词
        if token.is_punct or token.is_stop:
            continue

        lemma = token.lemma_
        if lemma.isalnum():
            tokens.append(lemma)

        # ⭐ 保留 -ing 形式（处理 noun/verb 歧义）
        if token.text.endswith("ing") and token.text != lemma and token.text.isalnum():
            tokens.append(token.text)

    return " ".join(tokens)
```

### 处理 -ing 歧义

spaCy 的 lemmatize 依赖上下文：
- `"I am meeting John"` → meeting (verb) → meet
- `"The meeting was long"` → meeting (noun) → meeting

不一致会导致 BM25 索引/查询时同一个词被 lemmatize 成不同结果。

**Mem0 的解决**：**同时保留** lemma 和 -ing 原形：

```python
tokens.append(lemma)              # "meet"
if token.text.endswith("ing"):
    tokens.append(token.text)     # "meeting"
```

> 索引和查询都这样处理,BM25 命中率提高。

---

## 5. ⭐ `spacy_models.py`

懒加载 + 缓存 spaCy model：

```python
# 推断（基于使用模式）
_nlp_lemma_cache = None
_nlp_ner_cache = None

def get_nlp_lemma():
    """返回 lemmatize 用的 spaCy model（小 model en_core_web_sm）"""
    global _nlp_lemma_cache
    if _nlp_lemma_cache is None:
        try:
            import spacy
            _nlp_lemma_cache = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model en_core_web_sm not installed. Run: python -m spacy download en_core_web_sm")
            _nlp_lemma_cache = False
    return _nlp_lemma_cache if _nlp_lemma_cache is not False else None

def get_nlp_ner():
    """返回 NER 用的 spaCy model（中 model en_core_web_md）"""
    # 类似
```

> 不装 spaCy 时这些函数返回 None,上层 fallback 到原 text（无 lemmatize,无 entity）。Mem0 SDK 在没 spaCy 时**仍能工作**,只是质量降低。

---

## 6. 性能 profile

| 操作 | 1k 文本耗时 |
|------|----------|
| lemmatize_for_bm25（spaCy small） | ~3s |
| extract_entities（spaCy small + NER） | ~5s |
| extract_entities_batch（spaCy pipe） | ~1s（5x 加速） |
| embed（OpenAI） | ~10s |
| embed_batch（OpenAI） | ~1s |

> spaCy 操作 CPU 密集,但 batch 能显著加速。Mem0 的 add() Phase 7 用 `extract_entities_batch` 而非循环 `extract_entities`。

---

## 7. 装 spaCy 启用 BM25 / Entity

```bash
pip install mem0ai[nlp]
python -m spacy download en_core_web_sm
```

不装 spaCy 时：
- `lemmatize_for_bm25` 返回原 text（BM25 quality 略降,但仍能用）
- `extract_entities` 返回 `[]`（**entity linking 完全失效**,但 search 仍工作）

---

## 8. 接下来

| 想看 | 去哪 |
|------|------|
| add() Phase 7（用 entity） | [`../01-py-sdk-core/06-add-pipeline.md`](../01-py-sdk-core/06-add-pipeline.md) §Phase 7 |
| search() Step 5-6（用 scoring） | [`../01-py-sdk-core/07-search-pipeline.md`](../01-py-sdk-core/07-search-pipeline.md) §Step 5-6 |
| Factory 工厂模式 | [`07-factory.md`](./07-factory.md) |

---

📌 **下一步** → [`../03-py-sdk-client/`](../03-py-sdk-client/) Hosted Platform Client。
