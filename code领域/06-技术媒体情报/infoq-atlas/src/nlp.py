"""技术实体词典 + 通用 NLP 工具（无外部依赖）。

用于 content_intel 的实体抽取、关键短语、自动摘要、聚类。
"""
from __future__ import annotations
import re

# ---- 技术实体词典（分类，便于报表分组）----
TECH_LEXICON: dict[str, list[str]] = {
    "编程语言": ["Java", "Python", "Go", "Golang", "Rust", "JavaScript", "TypeScript",
        "Kotlin", "Swift", "C++", "C#", "Scala", "Ruby", "PHP", "Java", "Dart",
        "Objective-C", "Elixir", "Clojure", "Julia", "Zig", "Lua", "Solidity"],
    "前端框架": ["React", "Vue", "Angular", "Svelte", "Next.js", "Nuxt", "SolidJS",
        "Electron", "React Native", "Flutter", "Webpack", "Vite", "Rollup",
        "Tailwind", "Redux", "Zustand", "Three.js", "Lit"],
    "后端框架": ["Spring", "Spring Boot", "Spring Cloud", "Django", "Flask", "FastAPI",
        "Express", "NestJS", "Gin", "Echo", "Rails", "Laravel", "gRPC", " thrift"],
    "云原生": ["Kubernetes", "K8s", "Docker", "Containerd", "Istio", "Envoy", "helm",
        "ArgoCD", "Flux", "Serverless", "OpenTelemetry", "Prometheus", "Grafana",
        "etcd", "CNCF", "Service Mesh", "Operator"],
    "云平台": ["AWS", "Azure", "GCP", "阿里云", "腾讯云", "华为云", "百度智能云",
        "火山引擎", "Oracle Cloud", "OCI", "Cloudflare", "Vercel"],
    "数据库": ["MySQL", "PostgreSQL", "Redis", "MongoDB", "Elasticsearch", "ClickHouse",
        "TiDB", "OceanBase", "PolarDB", "Doris", "HBase", "Cassandra", "DynamoDB",
        "SQLite", "Neo4j", "Snowflake", "DuckDB", "CockroachDB", "Spanner"],
    "消息/流": ["Kafka", "RocketMQ", "Pulsar", "RabbitMQ", "Flink", "Spark", "Storm",
        "Paimon", "Iceberg", "Hudi", "Beam", "Samza"],
    "大数据": ["Hadoop", "Hive", "Presto", "Trino", "Doris", "dbt", "Airflow",
        "DolphinScheduler", "DataX", "Flink", "Spark", "Ray"],
    "AI/ML框架": ["PyTorch", "TensorFlow", "JAX", "Keras", "Transformers", "Diffusers",
        "LangChain", "LlamaIndex", "vLLM", "SGLang", "ONNX", "TensorRT", "CUDA",
        "PaddlePaddle", "MindSpore", "Scikit-learn", "XGBoost"],
    "大模型": ["GPT", "GPT-4", "ChatGPT", "LLaMA", "Llama", "Claude", "Gemini",
        "文心一言", "通义千问", "Qwen", "GLM", "ChatGLM", "DeepSeek", "Baichuan",
        "GLM-4", "o1", "Sora", "Stable Diffusion", "Midjourney", "Mistral",
        "Mixtral", "MoE", "RAG", "Agent", "Agent 框架", "Function Calling"],
    "架构模式": ["微服务", "中台", "DDD", "领域驱动设计", "SOA", "Serverless",
        "事件驱动", "Event Sourcing", "CQRS", "Saga", "Sidecar", "Service Mesh",
        "云原生", "低代码", "Service Mesh", "Hexagonal"],
    "方法论": ["DevOps", "SRE", "GitOps", "CI/CD", "TDD", "BDD", "敏捷", "Scrum",
        "OKR", "FinOps", "Chaos Engineering", "可观测性", "Observability"],
    "公司/组织": ["字节跳动", "阿里", "阿里巴巴", "腾讯", "美团", "百度", "华为",
        "京东", "小米", "微软", "Google", "Meta", "Netflix", "Uber", "Amazon",
        "Apple", "OpenAI", "Anthropic", "NVIDIA", "Intel", "英伟达", "蚂蚁", "滴滴",
        "B站", "小红书", "拼多多", "快手"],
}

# 扁平化 + 大小写不敏感索引（英文按原样匹配，中文直接）
_FLAT: list[tuple[str, str]] = []
for cat, terms in TECH_LEXICON.items():
    for t in terms:
        _FLAT.append((t, cat))
# 按长度降序，优先长匹配
_FLAT.sort(key=lambda x: -len(x[0]))


def extract_entities(text: str) -> dict[str, dict[str, int]]:
    """返回 {category: {term: count}}。"""
    if not text:
        return {}
    low = text
    out: dict[str, dict[str, int]] = {}
    seen_spans = []
    for term, cat in _FLAT:
        if not term:
            continue
        cnt = low.count(term)
        if cnt > 0:
            out.setdefault(cat, {})[term] = out.setdefault(cat, {}).get(term, 0) + cnt
    return out


# ---- 关键短语（RAKE 风格）----
_PHRASE_BREAK = re.compile(r"[，。！？；,!?;()\[\]{}\"'`<>\n\r\t|/\\=+\-*]{1,}")
_CN_STOP = set("的了和与及在是为对从到等也被将可以我们他们你我他它这那一个一种一些"
               "通过使用实现以及基于如何进行并且但是然而因此所以如果虽然年月日时个发例"
               "外同时其次其中另外此外还有没有不会可能需要比如例如其实来看总之"
               "图图片本文文中作者译者来源更多相关以及或者由于因为")
_EN_STOP = set("the of to in on for and with a an is are as be by at or from how "
               "what which that this these those it its their our your you we they "
               "https http www com org cn images image wechat img pic picture".split())

# URL / 域名 / 邮箱 清洗（用字符类避免回溯，快速）
_URL_RE = re.compile(r"https?://[^\s)\]]*")           # http(s) 链接
_DOM_RE = re.compile(r"[A-Za-z0-9_.-]+\.(?:com|org|cn|net|io|xyz|geekbang|infoq)[^\s)\]]*")
_MAIL_RE = re.compile(r"[A-Za-z0-9_.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_MD_IMG_RE = re.compile(r"!\[[^\]]*\]\([^)]*\)|!\[[^\]]*\]")
_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")


def clean_text(text: str) -> str:
    """清洗：去 markdown 图片/链接/URL/域名，去图片占位行。快速、无回溯。"""
    if not text:
        return ""
    text = _MD_IMG_RE.sub(" ", text)
    text = _MD_LINK_RE.sub(r"\1", text)
    text = _URL_RE.sub(" ", text)
    text = _DOM_RE.sub(" ", text)
    text = _MAIL_RE.sub(" ", text)
    text = re.sub(r"(?m)^\s*图\s*片\s*$", " ", text)
    return text


def _tok_ok(w: str) -> bool:
    if not w:
        return False
    if w.isdigit():
        return False
    if w in _CN_STOP or w.lower() in _EN_STOP:
        return False
    # 中文单字：必须非停用词（上面已判）
    if len(w) == 1 and "\u4e00" <= w <= "\u9fff":
        return w not in _CN_STOP
    # 英文过短（2字母且非已知缩写）丢弃
    if len(w) == 2 and w.isascii() and w.isalpha() and w.lower() not in {
            "ai", "ml", "go", "js", "os", "db", "ui", "ux", "ci", "cd", "dd", "soa"}:
        return False
    return True


def keyphrases(text: str, topk: int = 20) -> list[tuple[str, float]]:
    """RAKE 风格关键短语：候选短语 + 词频度数评分。"""
    text = clean_text(text)
    if not text:
        return []
    word_freq: dict[str, int] = {}
    phrase_scores: dict[str, float] = {}
    for raw in _PHRASE_BREAK.split(text):
        seg = raw.strip(" .·:-—")
        if not seg:
            continue
        # 切词：英文连续字母数字串 / 中文单字
        toks = re.findall(r"[A-Za-z][A-Za-z0-9.+#_-]{1,}|[\u4e00-\u9fff]", seg)
        good = [t for t in toks if _tok_ok(t)]
        if not good:
            continue
        for t in good:
            word_freq[t] = word_freq.get(t, 0) + 1
        # 短语：相邻中文单字连写，其余用空格
        phrase_parts = []
        for i, t in enumerate(good):
            if i > 0:
                prev_cjk = len(good[i - 1]) == 1 and "\u4e00" <= good[i - 1] <= "\u9fff"
                cur_cjk = len(t) == 1 and "\u4e00" <= t <= "\u9fff"
                phrase_parts.append("" if (prev_cjk and cur_cjk) else " ")
            phrase_parts.append(t)
        phrase = "".join(phrase_parts)
        if 1 <= len(good) <= 5:
            phrase_scores[phrase] = phrase_scores.get(phrase, 0) + 1
    # 评分 = 短语频次 * 平均词频
    scored = []
    for ph, pf in phrase_scores.items():
        words = ph.split()
        avg = sum(word_freq.get(w, 0) for w in words) / max(1, len(words))
        scored.append((ph, round(pf * avg, 2)))
    scored.sort(key=lambda x: -x[1])
    # 合并子串 & 过滤退化短语（单字、纯停用词）
    out = []
    seen = []
    for ph, sc in scored:
        ph_strip = ph.replace(" ", "")
        if len(ph_strip) < 2:                 # 单字短语丢弃
            continue
        if ph_strip in _CN_STOP or ph.lower() in _EN_STOP:
            continue
        if any(ph in s or s in ph for s in seen):
            continue
        seen.append(ph)
        out.append((ph, sc))
        if len(out) >= topk:
            break
    return out


# ---- 抽取式摘要 ----
_SENT_SPLIT = re.compile(r"(?<=[。！？!?])\s*|(?<=\n)\s*|(?<=;)\s*")


def summarize(text: str, n: int = 3, max_len: int = 320) -> list[str]:
    text = clean_text(text)
    if not text:
        return []
    sents = [s.strip() for s in _SENT_SPLIT.split(text) if 8 <= len(s.strip()) <= 400]
    if len(sents) <= n:
        return sents
    # 词频
    wf: dict[str, int] = {}
    for s in sents:
        for t in re.findall(r"[A-Za-z][A-Za-z0-9.+#-]{1,}|[\u4e00-\u9fff]+", s):
            if _tok_ok(t) or _tok_ok(t[0] if t else ""):
                wf[t] = wf.get(t, 0) + 1
    # 句子得分 = 词频和 / 长度开方（偏短句）
    scored = []
    for i, s in enumerate(sents):
        words = re.findall(r"[A-Za-z][A-Za-z0-9.+#-]{1,}|[\u4e00-\u9fff]+", s)
        score = sum(wf.get(w, 0) for w in words) / (len(s) ** 0.4 + 5)
        scored.append((score, i, s))
    # 取 top n 但保持原顺序
    top = sorted(scored, key=lambda x: -x[0])[:n]
    top.sort(key=lambda x: x[1])
    return [s[:max_len] for _, _, s in top]
