# LLM 训练数据栈的最细节：从 Common Crawl 到 Tokenizer 到 Loss Spike

> 本文是《world-ai4sci-math》第 05 卷「模型工程」的深处补章。前 70 万字聊了模型架构（Attention/MoE/Normalization）与训练算法（AdamW/DPO/RLHF），但**训练数据栈本身——也就是工程师每天 70% 时间所在——一直被论文略过**。论文只告诉你「我们用了 15T tokens 的高质量数据」，至于这 15T 怎么从 PB 级网页噪声里淘出来的、tokenizer 的 vocab size 怎么定的、loss spike 怎么救回来的，几乎不写。本文把这一层完全揭开。
>
> 所有 arXiv ID 均经 arXiv API（`export.arxiv.org/api/query`）一手核实。本文在核实过程中发现并纠正了若干流传甚广的错误 ID（例如 DataComp 常被误引为 `2304.08274`，实为 `2304.14108`；BPE 常被误引为 `1610.03054`，实为 `1508.07909`），见文末「核实勘误记录」。
>
> 全文大量可运行代码（HuggingFace `tokenizers` / `datasets`、CCNet pipeline、`datasketch` / `text-dedup`、PyTorch 分布式监控）。建议把每段代码贴进 Jupyter 跑一遍，比读十遍都管用。

---

## 为什么数据栈是 LLM 的「暗物质」

打开任何一篇旗舰模型的 tech report，你会发现一个诡异的对称性：架构章节动辄 20 页，把每一个 Normalization、每一个 RoPE 频率都讲透；而数据章节通常只有一页半，措辞模糊得像法律免责声明——「我们收集了大量公开网页，经过严格的清洗与去重，混合了代码、数学、多语言数据」。为什么？两个原因。

第一，**数据是真正的护城河**。架构可以逆向工程（看开源权重 + 看 tech report 就能复现 Llama），但一个 15T tokens 的清洗 pipeline 没人会开源——这背后是几百人年的脏活累活，是几十条踩坑总结出来的 heuristic，是真正决定模型上限的部分。OpenAI 的论文干脆不写数据，Anthropic 的 Constitutional AI 论文写了对齐数据但几乎不写预训练数据，Meta 的 Llama 3 报告是少数公开讨论数据清洗的大厂，但即便如此也只讲了「最后一公里」。

第二，**数据工程不「学术」**。学术圈奖励的是新颖算法，不是「我把 MinHash 的 band 数从 16 调到 20 之后召回率提升了 3%」这种工程经验。于是数据栈的知识以「部落口述」的形式散落在 HuggingFace Slack、EleutherAI Discord、各种 blog 和 GitHub issue 里，从未被系统化。本文做的就是把这片暗物质写成可读的地图。

> **核心判断**：在 Chinchilla 之后（[arXiv:2203.15556](https://arxiv.org/abs/2203.15556)，Hoffmann et al. 2022，发现模型参数与训练 token 应等比缩放，70B 模型应配 1.4T tokens 而非 GPT-3 的 300B），**数据成了 scaling 的第一瓶颈**。DCLM 团队（[arXiv:2406.11794](https://arxiv.org/abs/2406.11794)）的实验直接证明：用更好的数据过滤，一个 7B 模型用 2.6T tokens 就能在 MMLU 上拿到 64%，逼近 Llama 3 8B（66%）和 Mistral-7B-v0.3（63%），而计算量只有 Llama 3 8B 的 1/6.6。**数据质量是免费的算力。**

---

## 一、数据获取：从 PB 级网页噪声里舀水

### 1.1 Common Crawl 全栈

Common Crawl（CC）是几乎所有大型预训练数据集的母体——C4、RefinedWeb、RedPajama-V2、Dolma、DCLM，它们的网页部分都来自 CC。CC 是一个非营利项目，自 2008 年起每月发布一次互联网爬取快照，存储在 AWS S3 的公开桶 `s3://commoncrawl/` 上，任何人都能免费拉取。一次完整月度爬取的原始数据量在 2024 年已经达到数 PB（含图片等），其中纯文本 WARC 文件约 100+ TB。

**WARC 格式**是这一切的原子单位。WARC（Web ARChive，ISO 28500 标准）把每一次 HTTP 请求/响应封装成一条记录，包含响应头、HTML 内容、元数据（URL、抓取时间、IP）。解析 WARC 的标准工具是 Python 的 `warcio`：

```python
from warcio import ArchiveIterator
import boto3, gzip

# 从 S3 流式读取 CC 的一个 WARC 分片（每个约 1GB gzipped）
s3 = boto3.client('s3')
key = 'common-crawl/crawl-data/CC-MAIN-2024-10/segments/.../warc/...warc.gz'
obj = s3.get_object(Bucket='commoncrawl', Key=key)
for record in ArchiveIterator(obj['Body']):
    if record.rec_type == 'response':
        url = record.rec_headers.get_header('WARC-Target-URI')
        html = record.content_stream().read().decode('utf-8', errors='ignore')
        # 接下来：HTML → 纯文本（trafilatura / resiliparse）
```

**从 HTML 提取正文**是第一个真正的工程难点。直接用 BeautifulSoup 拿 `text` 会把导航栏、广告、JS 残留全部混进来，质量灾难级。业界的两个主力工具：

- **trafilatura**（Adrien Barbaresi 开发）：专门为 NLP 数据集设计，能精准抽取主文区域、剥离 boilerplate，是 RedPajama / DCLM 等数据集的默认选择。
- **resiliparse**（柏林洪堡大学 Web Science 组）：C++ 实现，比 trafilatura 快 5-10x，CCNet 的早期 pipeline 用过。

```python
import trafilatura
text = trafilatura.extract(
    html,
    include_comments=False,        # 不要评论区（噪声源 #1）
    include_tables=False,          # 表格通常无意义
    favor_recall=True,             # 宁可多抽也不要漏
    url=url,                       # 帮助识别主域名
)
```

**CCNet pipeline**（Meta，[arXiv:1911.00359](https://arxiv.org/abs/1911.00359)，Wenzek et al. 2019）是第一个工业级、可复现的 CC 处理管线，至今仍是事实标准。它的核心三步：

1. **语言识别**：用 fastText 的 `lid.176.bin` 模型对每个文档分类，按语言分流；
2. **去重**：文档级 exact dedup + 段落级 line-level dedup；
3. **质量过滤**：用一个在 Wikipedia 上训练的 KenLM 语言模型计算每个文档的 perplexity，按语言把文档分成 *head（高质量）/ *middle / *tail 三档。这是「perplexity filtering」的起源。

CCNet 的开源实现（`cc_net`）用 Meta 的分布式调度跑全量 CC，每小时能处理数十 TB。它输出的 CC-100、CCNet-shards 被后来的 XLM-R、mBART、Llama 系列直接使用。

> **论文**：CCNet: Extracting High Quality Monolingual Datasets from Web Crawl Data [arXiv:1911.00359](https://arxiv.org/abs/1911.00359)（Wenzek et al., 2019）。

### 1.2 Wikipedia dump

Wikipedia 是「优质数据」的金标准——CCNet 用它训练 LM 来给网页打分，所有质量分类器都拿 Wikipedia 当正样本。它的好处是结构化、覆盖广、多语言、相对干净。获取方式：

- **官方 dump**：`https://dumps.wikimedia.org/`，每周全量 dump，提供多种格式。最常用的是 `zhwiki-latest-pages-articles.xml.bz2`（条目 XML，压缩后约几百 MB ~ 数 GB）。
- **HuggingFace datasets**：`datasets.load_dataset("wikipedia", "20220301.en")` 一行加载（注意版本号对应 dump 日期）。
- **Wikipedia Enterprise API**：官方付费 API，提供结构化 JSON，含图片与多媒体引用。

解析 XML dump 的标准工具是 `WikiExtractor`（GIUSSEPPE ATTARDI 的开源项目）：

```bash
python -m wikiextractor.WikiExtractor zhwiki-latest-pages-articles.xml.bz2 \
    --json --filter_disambig --no-templates -o extracted/
```

需要注意的工程坑：①Wikipedia 含大量模板（`{{Infobox}}`、`{{cite}}`），不清理会污染数据；②跨语言链接、重定向页要剔除；③历史/传记条目里人名、日期密集，对模型很有价值，不要因为「看起来像表格」就删。

### 1.3 GitHub 代码数据

代码是现代 LLM（尤其推理模型）的关键燃料。Llama 3、Qwen、DeepSeek 都在预训练里掺了大量代码。获取途径有三：

1. **GitHub Archive + BigQuery**：Google 维护的 `bigquery-public-data.github_repos` 数据集，包含 GitHub 全量 commit、文件、仓库元数据。可以按语言、license、star 数 SQL 过滤。
2. **Software Heritage**：非营利的软件遗产项目，提供完整的代码快照和 API。
3. **直接 clone 高 star 仓库**（小规模实验用）。

**License 过滤**是代码数据的核心法律问题。业界共识（基于 BigCode 项目的研究）：①MIT / Apache-2.0 / BSD 是「安全」的，可自由用于训练；②GPL / AGPL 有传染性，商业模型通常剔除；③CC-BY / CC0 的文档类数据可用；④无 license 文件的仓库默认「All rights reserved」，理论上不能用，实务上多数数据集会保留但占比压低。

**代码清洗**的几条 heuristic（来自 StarCoder / The Stack 的工作）：

```python
def filter_code(content: str, path: str) -> bool:
    lines = content.split('\n')
    avg_line_len = sum(len(l) for l in lines) / max(len(lines), 1)
    if avg_line_len > 200: return False        # 多是 minified JS / 压缩文件
    if content.count('{') > 0 and avg_line_len < 10: return False  # 同上
    if 'auto-generated' in content[:200].lower(): return False       # 自动生成
    if len(lines) < 5: return False                                  # 过短无意义
    # 按扩展名筛语言
    if not path.endswith(('.py', '.js', '.ts', '.java', '.c', '.cpp', '.go', '.rs')):
        return False
    return True
```

`auto-generated` 这一条经常被忽略——很多仓库里的 `package-lock.json`、`.min.js`、protobuf 生成代码会拉低数据质量。

### 1.4 ArXiv / PubMed / Stack Exchange 等垂直源

这些「高质量小源」体积不大但密度极高，是数学、科学、医学能力的关键。

- **ArXiv**：所有论文的 LaTeX 源码可从 `arxiv.org/e-print/<id>` 批量下载。The Pile（[arXiv:2101.00027](https://arxiv.org/abs/2101.00027)，Gao et al. 2020，825 GiB 多样化语料）的 Books3、ArXiv 子集就来自这里。处理 LaTeX 要小心：去掉宏定义、把 `\frac{a}{b}` 转成 `a/b`、保留公式环境。
- **PubMed Central**（PMC）：生物医学论文全文，NLM 官方提供 OA 子集的 XML，免费用。
- **Stack Exchange**：所有子站（Stack Overflow、Math、CS 等）每月在 `archive.org` 上发布完整 dump（CC-BY-SA license）。这是「问答对」结构的金矿，特别适合做指令数据。

```python
import xml.etree.ElementTree as ET
# Stack Exchange 的 Posts.xml 是一个大 XML，每条 <row> 是一个问题或回答
for event, elem in ET.iterparse('Posts.xml', events=('end',)):
    if elem.tag == 'row' and elem.get('PostTypeId') == '1':  # 问题
        title, body = elem.get('Title'), elem.get('Body')
        # 清理 HTML、保留高赞回答（Score > 阈值）
```

### 1.5 私有数据的合法获取

Reddit、Twitter（X）、知乎、微信公众号——这些是「对话」「观点」「时效」的高质量源，但绝大多数受 ToS 限制。

**Reddit 的法律路径**：Reddit 的 Pushshift 历史镜像曾被研究者广泛使用，2023 年 Reddit API 收费后这条路变窄。当前合法方式：①申请 Reddit Data API 的学术/商业 access；②购买 Pushshift 历史快照（已被 Reddit 官方接管）。OpenAI、Anthropic 都被披露与 Reddit 有数据授权协议。

**Twitter/X**：API 严格，学术研究包也只能取少量。GPT-3 的训练数据里包含大量历史推文（通过早期更宽松的 API 取得），现在这条路基本关闭。

**知乎/微信公众号**：中文模型的关键，但 ToS 禁止爬取。实务上：知乎有官方 API（需申请），微信公众号内容只能通过搜狗微信等间接渠道，绝大多数中文数据集对这部分语焉不详。

> **判断**：私有数据的获取成本和合规风险都极高。中小团队的现实策略是：①把 CC 清洗做到极致（RefinedWeb 证明纯网页能打过混合数据，[arXiv:2306.01116](https://arxiv.org/abs/2306.01116)）；②用合成数据补足（见第八章）；③对私有数据保持敬畏，宁缺毋滥。

### 1.6 多语言与长尾语言

中文、阿拉伯语、东南亚语言、非洲语言——这些「长尾」在以英文为中心的 CC 里占比极低，且质量参差。处理多语言有三个层次：

1. **Tokenizer 层**：英文 BPE 对中文极度不友好，一个汉字常常被切成 3-4 个 byte token（fragmentation），既浪费 context 又损害语义。Qwen、ChatGLM、DeepSeek 都为中文专门训了 tokenizer（见第二章）。
2. **数据层**：CC 的中文部分噪声极高（SEO 农场、机器翻译、垃圾采集站），需要更强的质量过滤。CCNet 的 KenLM 方法对低资源语言会失效（Wikipedia 太小训不出好 LM），需要改用 fastText 分类器或多语言 sentence encoder。
3. **混合层**：英文数据天然碾压，多语言不加干预会被淹没。Llama 3（[arXiv:2407.21783](https://arxiv.org/abs/2407.21783)）明确说 8% 的预训练 token 是非英文，并在后训练阶段专门做了多语言对齐。

**阿拉伯语/希伯来语**还要处理 RTL（从右到左）书写、字母变体（letter shaping）、diacritics——这些是 tokenizer 与 normalization 的高发 bug 区。

---

## 二、Tokenizer 训练：vocab size 是一个全局优化问题

Tokenizer 看起来是个小模块（几千行代码），但它的每一个决策都会传遍整个训练——embedding 矩阵大小、context 长度能装多少内容、推理速度、下游生成质量。它是 LLM 里「牵一发动全身」最严重的部件。

### 2.1 四种主流子词算法对比

| 算法 | 提出者/年份 | 训练方式 | 代表模型 |
|------|------------|---------|---------|
| **BPE** | Sennrich et al. 2016（[arXiv:1508.07909](https://arxiv.org/abs/1508.07909)） | 自底向上合并最高频字符对 | GPT-2/3/4、Llama 3（tiktoken） |
| **WordPiece** | Schuster & Nakajima 2012 | 类似 BPE，但合并准则是似然增益 | BERT、DistilBERT |
| **Unigram LM** | Kudo 2018（[arXiv:1804.10959](https://arxiv.org/abs/1804.10959)） | 自顶向下，从大词表中基于 EM 删除使似然损失最小的子词 | T5、ALBERT、mBART |
| **SentencePiece** | Kudo & Richardson 2018（[arXiv:1808.06226](https://arxiv.org/abs/1808.06226)） | 框架，BPE 或 Unigram 都可；不依赖预分词 | Llama 1/2、T5、多语言模型 |

**BPE（Byte Pair Encoding）**的核心是贪心合并：从字符级别开始，每轮统计相邻 token 的共现频次，把最高频的那对合并成新 token，直到词表达到目标大小。它简单、稳定、可复现，是事实标准。GPT-2 的关键改进是把 BPE 作用在 **byte** 而非 unicode 字符上（byte-level BPE，BBPE），这样任何字符（包括 emoji、罕见汉字）都能表示，彻底消灭 OOV（out-of-vocabulary）问题。

```python
# GPT-2 风格的 byte-level BPE 训练（HuggingFace tokenizers）
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import ByteLevel

tokenizer = Tokenizer(BPE(unk_token="<unk>"))
tokenizer.pre_tokenizer = ByteLevel(add_prefix_space=True)
trainer = BpeTrainer(
    vocab_size=50257,
    special_tokens=["<|endoftext|>", "<|im_start|>", "<|im_end|>"],
    initial_alphabet=ByteLevel.alphabet(),  # 256 个字节
)
tokenizer.train_from_iterator(text_iter, trainer=trainer)
```

**WordPiece** 与 BPE 的差别只在合并准则：BPE 看频次，WordPiece 看合并后似然 / 两词单独似然乘积的比值。实际效果差异不大，BERT 系用它是历史原因。

**Unigram LM**（Kudo 2018）走相反方向：先假设一个超大词表，然后用 EM 算法估计每个子词在语料上的概率，删除使总似然损失最小的子词，迭代直到达到目标大小。它的优势是**概率性**——同一个词可以有多种切分，训练时按概率采样（这就是「Subword Regularization」），对低资源语言的鲁棒性更好。但训练比 BPE 慢得多。

**SentencePiece** 是一个工程框架（Google 开源），关键贡献是**不依赖空格预分词**——它把原始字节流直接喂给 BPE 或 Unigram。这对中文、日文、泰文这些「词与词之间没有空格」的语言是革命性的。Llama 1/2 用的就是 SentencePiece + BPE，vocab=32000。

### 2.2 训练自己的 tokenizer：实操

下面是一个完整、可运行的训练流程，目标是为「中文 + 代码 + 英文」混合语料训一个 64K vocab 的 tokenizer：

```python
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import Sequence, Punctuation, Digits, ByteLevel, Metaspace
from tokenizers.normalizers import NFD, Lowercase, StripAccents, Sequence as NormSeq
from tokenizers.decoders import ByteLevel as ByteLevelDecoder
import glob

# 1. 模型与解码器（byte-level，彻底解决 OOV）
tokenizer = Tokenizer(BPE(unk_token="<unk>", byte_fallback=True))  # byte_fallback 关键

# 2. Normalizer：中文一般不做 lowercase，避免「我」与「我」分裂
tokenizer.normalizer = NormSeq([NFD(), StripAccents()])

# 3. Pre-tokenizer：对代码与中英混合至关重要
#    - Metaspace：把空格转成特殊符号 ▁，让「连续中文」能被聚成一个 token
#    - Punctuation：标点单独成 token（代码语法需要）
#    - Digits：长数字单独切（避免 123456789 被切成奇怪 token）
tokenizer.pre_tokenizer = Sequence([
    Metaspace(replacement='▁', add_prefix_space=True),
    Digits(individual_digits=False),
    Punctuation(),
])

# 4. Decoder：与 pre-tokenizer 对应
tokenizer.decoder = tokenizers.decoders.Metaspace(replacement='▁', add_prefix_space=True)

# 5. Trainer：注意 special_tokens 的顺序，前 256 个 byte 必须在
trainer = BpeTrainer(
    vocab_size=64000,
    min_frequency=200,            # 出现少于 200 次的对不合并，降噪
    show_progress=True,
    special_tokens=[
        "<pad>", "<unk>", "<s>", "</s>",       # 基础 4 个
        "<|im_start|>", "<|im_end|>",          # ChatGPT 风格对话分隔符
        "<|endoftext|>",
        "[INST]", "[/INST]",                    # Llama 风格
        "```", "```python", "```json",          # 代码 fenced block（高频）
        *[f"<0x{i:02X}>" for i in range(256)], # 256 bytes（byte_fallback 必需）
    ],
)

# 6. 训练：用文件迭代器，不要全装内存
files = glob.glob("/data/corpus/**/*.txt", recursive=True)
tokenizer.train(files, trainer)

# 7. 保存为 HF 格式，后续 transformers 直接 load
tokenizer.save("my_tokenizer.json")
```

**实测经验**：①`min_frequency` 是最被低估的旋钮——设太低会把拼写错误、垃圾 token 固化进词表，设太高会丢失长尾词；②训练语料必须与最终预训练语料同分布，用纯英文语料训的 tokenizer 套中文数据会出现灾难性 fragmentation；③`byte_fallback=True` 是「保险丝」——遇到训练时没见过的字节，回退到单字节 token 而非 `<unk>`。

### 2.3 Vocabulary size 的取舍

vocab size 不是越大越好，它是一个三方的拉锯：**embedding 矩阵显存** vs **序列压缩率** vs **softmax 计算成本**。

- **embedding 矩阵**：模型最大的参数块之一。一个 7B 模型，hidden_size=4096，vocab=32000 时 embedding 占 4096×32000×2 bytes（BF16）≈ 262 MB；vocab=128000 时占 1 GB+。vocab 越大，embedding 越挤压「真正算力」的预算。
- **序列压缩率**：vocab 越大，每个 token 承载的信息越多，同样长度 context 能装下越多「人读字数」。这对长上下文任务（代码、长文档）是直接红利。
- **softmax 成本**：最终 LM head 是对全词表做 softmax，vocab=128K 比 32K 的最终投影慢 4 倍，且梯度更稀疏。

业界的演化轨迹很说明问题：

| 模型 | 年份 | vocab | 算法 | 备注 |
|------|------|-------|------|------|
| GPT-2 | 2019 | 50,257 | BPE | byte-level，奠基 |
| BERT | 2018 | 30,522 | WordPiece | 小而美 |
| Llama 1/2 | 2023 | 32,000 | SentencePiece+BPE | 偏小，中文 fragmentation 严重 |
| Llama 3 | 2024 | 128,000 | tiktoken (BPE) | 大幅扩词表，128K context 配套 |
| GPT-4o (cl100k) | 2023 | ~100,000 | BPE | tiktoken |
| Qwen2 | 2024 | 151,646 | tiktoken-like | 中文优化，词表大 |
| DeepSeek-V2 | 2024 | 100,000 | BPE | 平衡选择 |

**给小团队的建议**：如果主要做英文，32K-64K 足够；如果要做中文/多语言/代码，64K-128K 是甜点区；超过 128K 收益递减且训练成本陡增。务必在选定后做一次「fragmentation 检查」（见下）。

### 2.4 多语言 tokenizer 与 fragmentation

中文 fragmentation 是初学者的第一道大坑。用 Llama 2 的 32K tokenizer 编码「人工智能」四个字，你会得到类似 `['人', '工', '智', '<0xE6>', '<0x8A>', '<0x80>', '术']` 这样的输出——「能」「术」等字被切碎成 byte，4 个汉字变 7 个 token，等于浪费了 75% 的 context。

```python
from transformers import AutoTokenizer
# 对比不同 tokenizer 在中文上的压缩率
for name in ["meta-llama/Llama-2-7b-hf", "meta-llama/Meta-Llama-3-8B",
             "Qwen/Qwen2-7B", "THUDM/chatglm3-6b"]:
    tok = AutoTokenizer.from_pretrained(name)
    text = "人工智能是研究、开发用于模拟、延伸和扩展人的智能的理论、方法、技术及应用系统的一门新的技术科学。"
    n = len(tok.encode(text))
    print(f"{name:40s} → {n:3d} tokens  (压缩率 {len(text)/n:.2f} 字/token)")
```

典型结果：Llama 2 约 60+ tokens，Llama 3 约 30，Qwen2 约 15。**压缩率差 4 倍意味着同样的 GPU 时长，Qwen2 能见 4 倍的中文数据**——这就是为什么中文模型几乎都自训 tokenizer。

避免 fragmentation 的设计点：①在中文语料上重训词表，让高频字/词成为单 token；②使用 Metaspace 或 ByteLevel 时确保中文不被拆到 byte；③定期检查「单字 fragmentation rate」（被切成 3+ token 的字占比）作为质量指标。

### 2.5 代码 tokenizer：保留缩进与特殊 token

代码有几条特殊要求：①**缩进必须保留**（Python 靠缩进决定语法，把 4 个空格合并成 1 个 token 会让模型完全无法学 Python）；②**常见关键字、操作符应为单 token**（`def`、`return`、`=>`、`::`）；③**fenced code block**（```` ```python ````）应能被识别。

HuggingFace `tokenizers` 处理缩进的标准做法是在 pre-tokenizer 里把连续空格与 tab 视为普通字符，不合并：

```python
# 代码友好的 pre-tokenizer 配置
from tokenizers.pre_tokenizers import Whitespace, Digits, Punctuation, Sequence
# 注意：不要用 WhitespaceSplit()，它会把缩进空格当分隔符吃掉
# 用 Metaspace + Punctuation + Digits 即可保留所有空格
```

` ```python`、` ```json` 这类高频标记应在 special_tokens 中预定义，否则它们会被切成 6-8 个普通 token，浪费且影响模型对「代码开始/结束」的感知。

### 2.6 添加特殊 token

后训练（SFT/对齐）阶段，你需要一套「控制 token」来标记对话结构。ChatGPT 系采用 `<|im_start|>system\n...<|im_end|>`，Llama 系采用 `[INST]...[/INST]`。这些 token 必须在 tokenizer 训练时就加入词表，**不能事后追加**（否则 embedding 矩阵要 pad 新行，重新初始化的训练成本高）。

```python
# 训练时预留（见 2.2 节 special_tokens）
# 如果事后必须加（比如微调已有模型），用 add_tokens + resize_token_embeddings：
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained("...")
n_added = tokenizer.add_special_tokens({
    "additional_special_tokens": ["<|new_role|>", "<|tool_call|>"]
})
model.resize_token_embeddings(len(tokenizer))
# 新 token 的 embedding 是随机初始化的，需要少量微调让模型「认识」它们
```

### 2.7 Tokenizer 的连锁影响

总结一下 tokenizer 决策会怎样传导到训练全链路：

- **embedding 显存**：vocab × hidden_size，是显存大头之一；
- **有效 context 长度**：同样 4K context，压缩率 1.5 字/token 的 tokenizer 能读 6K 字的原文，压缩率 0.5 的只能读 2K；
- **训练速度**：序列越短，单步 forward 越快；
- **生成质量**：fragmentation 严重的 tokenizer 会让模型在边界处生成不可读字符；
- **多语言公平性**：中文 fragmentation 等于变相降低中文数据的有效权重。

> **直觉**：把 tokenizer 想成「数据与模型之间的压缩协议」。压缩率每提升 10%，等于免费多看 10% 的数据。这就是为什么大厂都为自家语言/代码分布定制 tokenizer。

---

## 三、数据清洗：训练 70% 时间所在的战场

这是整章最长、也最重要的一节。网页数据天然是噪声：SEO 文本、机器翻译、重复采集、占位符、乱码、有害内容、个人隐私——如果原样喂进模型，模型会学成垃圾。清洗 pipeline 的目标只有一个：**从 PB 级噪声里，把那 10-20% 的「值得学」的文本捞出来**。

### 3.1 去重：MinHash、LSH 与 exact dedup

去重是清洗的第一性原理。Lee et al.（[arXiv:2107.06499](https://arxiv.org/abs/2107.06499)，ACL 2022）的实验令人震惊：他们在 C4 里发现一个 61 词的英文句子被重复了 **60,000 次**。直接后果是模型 1% 以上的非提示输出是从训练集逐字背诵（verbatim memorization）。去重后，背诵率下降 10 倍，且模型用更少步数达到更好精度。

> **论文**：Deduplicating Training Data Makes Language Models Better [arXiv:2107.06499](https://arxiv.org/abs/2107.06499)（Lee et al., ACL 2022）。代码：`github.com/google-research/deduplicate-text-datasets`。

**三层去重**：

1. **Exact dedup（精确去重）**：用 hash（MD5/SHA1）对整篇文档去重。O(n) 时间，能去掉完全一样的拷贝（采集站、镜像）。这是最便宜也最有效的第一道。
2. **Document-level MinHash LSH（近似文档去重）**：捕捉「几乎一样但有细微差别」的文档（同一篇文章被不同采集站加了广告条、改了标点）。这是去重的真正主力。
3. **Substring / n-gram dedup**：捕捉「长片段重复」（同一份法律声明、同一份 cookie policy 在百万网页里出现）。Lee et al. 用 suffix array 做这个，能精确到 50-token 级别。

**MinHash + LSH（Locality Sensitive Hashing）** 的原理用三句话讲清：①把文档表示成 n-gram（通常是 word-level 3-gram 或 5-gram）的集合；②MinHash 是用 k 个不同的哈希函数，对每个函数取集合里 hash 值最小的那个 n-gram，得到 k 维签名——两个文档的签名重合度近似等于它们的 Jaccard 相似度；③LSH 把签名分组成多个 band，只要两个文档在任一 band 上完全一致就被判为候选重复对，再精确计算 Jaccard 确认。这样把 O(n²) 的两两比较降到近似 O(n)。

工业实现首推 **datasketch**（Eduardo Munnells 的库）和 **text-dedup**（EPFL BIGAI 组的库）。text-dedup 把 MinHash/LSH/SimHash/精确去重全部封装成命令行工具，对超大数据集用内存映射与分片，是目前最易用的：

```bash
# text-dedup：对 jsonl 文件做 MinHash 去重
pip install text-dedup
text-dedup minhash \
    --path "dolma/cc-2024-*.jsonl" \
    --local true \
    --num_perm 256 \            # MinHash 签名维度，256 是精度/速度的甜点
    --threshold 0.7 \           # Jaccard > 0.7 判为重复
    --output cleaned.jsonl
```

`num_perm`（签名维度）和 `threshold`（相似度阈值）是两个核心旋钮。业界经验：num_perm=128-256，threshold=0.7-0.8。threshold 太低会误删相似但不同的文章（如同一新闻的不同版本），太高会漏掉改写过的重复。

**datasketch 的 Python 版**适合中小规模实验：

```python
from datasketch import MinHash, MinHashLSH

def make_minhash(text, num_perm=128):
    m = MinHash(num_perm=num_perm)
    words = text.lower().split()
    for ng in [tuple(words[i:i+3]) for i in range(len(words)-2)]:  # 3-gram
        m.update(' '.join(ng).encode('utf-8'))
    return m

lsh = MinHashLSH(threshold=0.7, num_perm=128)
for i, doc in enumerate(documents):
    mh = make_minhash(doc)
    if lsh.query(mh):   # 已有近似重复，丢弃
        continue
    lsh.insert(i, mh)   # 保留
```

**重要发现**：去重的边际收益是递增的——Muennighoff et al.（[arXiv:2305.16264](https://arxiv.org/abs/2305.16264)，Scaling Data-Constrained LMs）系统研究了数据重复的scaling law，发现重复训练同一份数据，**前 4 个 epoch 几乎没有损失**（loss 与唯一数据相当），但超过 4 epoch 后收益迅速衰减到零。这意味着去重不只是「清理垃圾」，更是「把重复预算花在更有价值的数据上」。

> **论文**：Scaling Data-Constrained Language Models [arXiv:2305.16264](https://arxiv.org/abs/2305.16264)（Muennighoff et al., 2023）。

### 3.2 质量过滤：perplexity 与 classifier-based

去重解决「重复」问题，质量过滤解决「垃圾」问题。两条主线：

**Perplexity filtering（CCNet 方法）**：用一个在 Wikipedia 上训练的小型 n-gram 语言模型（KenLM）给每个网页文档打 perplexity 分。逻辑是「与 Wikipedia 风格相近的文档 perplexity 低，质量高」。CCNet 按语言把文档按 perplexity 分位分成 head/middle/tail 三档，下游模型通常只用 head + middle。

```python
import kenlm
# KenLM 模型（在 Wikipedia 上训的 5-gram）
model = kenlm.Model('wiki_en_5gram.arpa.bin')
def perplexity(text):
    return model.perplexity(text)   # 越低越像 Wikipedia
```

kenlm 是 C++ 实现，单线程每秒能打几十万 token 的分，工业级可用。它的局限是：①只捕捉表面 n-gram 统计，无法理解语义；②对 Wikipedia 风格之外的高质量文本（如小说、对话）会误判；③对低资源语言失效（没有足够 Wikipedia 训 LM）。

**Classifier-based filtering（DCLM / DFN 方法）**：训一个二分类器，正样本是人工标注或代理质量集（如 OpenWebText、Wikipedia），负样本是随机网页。这个分类器给候选文档打分，阈值之上保留。这是 2023 年后的主流方法，效果显著好于 perplexity。

DCLM（[arXiv:2406.11794](https://arxiv.org/abs/2406.11794)）的核心发现就是：**model-based filtering 是组装高质量训练集的关键**。他们用 fastText 训了一个二分类器（正样本 = OpenWebText + Reddit outbound links 这类「人工精选优质网页」，负样本 = 随机 CC），对 240T tokens 的 CC 池打分，最终筛出的 DCLM-Baseline 让 7B 模型在 MMLU 上拿到 64%，比当时所有公开数据集都强。

> **论文**：DataComp-LM: In search of the next generation of training sets for language models [arXiv:2406.11794](https://arxiv.org/abs/2406.11794)（Li et al., 2024）。240T 池子，7B/2.6T tokens → MMLU 64%。

**Data Filtering Networks（DFN）**（[arXiv:2309.17425](https://arxiv.org/abs/2309.17425)，Fang et al. 2023）把这件事再往前推：他们发现「用于过滤的网络，其质量与它在下游任务上的表现是两回事」——一个 ImageNet 准确率低的 CLIP，如果用少量高质量数据训练，反而能筛出比高准确率 CLIP 更好的训练集。这个反直觉的结论说明：过滤器的目标是「区分信号与噪声」，不是「做对下游任务」。DFN-5B 数据集让 ViT-H 在 ImageNet 上达到 84.4% zero-shot。

> **论文**：Data Filtering Networks [arXiv:2309.17425](https://arxiv.org/abs/2309.17425)（Fang et al., 2023）。

**Heuristic rules（C4 / Gopher rules）**：最早的、也最便宜的质量过滤，是一组手工规则。C4（T5 训练集）的规则包括：①必须以标点结尾；②长度 <3 句的丢弃；③含「脏词列表」的丢弃；④必须有完整句子。Gopher（DeepMind）规则更细：限制 `lines_with_no_ending_punctuation` 比例、单词平均长度、符号占比等。这些规则便宜但粗糙，现代 pipeline 把它们作为「第一道粗筛」，再用 LM/classifier 精筛。

```python
def c4_heuristic(text: str) -> bool:
    if len(text) < 200: return False                         # 太短
    if not any(text.rstrip().endswith(p) for p in '.!?":'):  # 无结尾标点
        return False
    lines = text.split('\n')
    n_bad_end = sum(1 for l in lines if l and not l[-1] in '.!?"\')]: ')
    if n_bad_end / max(len(lines), 1) > 0.3:                 # 行尾标点率过低
        return False
    if 'lorem ipsum' in text.lower():                        # 占位符
        return False
    return True
```

### 3.3 PII（个人身份信息）移除

CC 里塞满了邮箱、电话、社保号、IP 地址——这些如果不清理，模型会逐字记住并可能泄露。OpenAI 早期就因此在 GPT-2 发布时只放小模型，担心「deceptive capability」。

主流 PII 检测方法：

- **正则匹配**（CommonRegex / 自写）：邮箱、电话、信用卡号（Luhn 校验）、SSN 都有标准模式。便宜、快、覆盖大头。
- **Microsoft Presidio**：开源 PII 检测与脱敏框架，内置 NER 模型 + 规则引擎，支持几十种 PII 类型，可定制。

```python
# Presidio 用法
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()
results = analyzer.analyze(text=text, language='en',
                           entities=['EMAIL_ADDRESS', 'PHONE_NUMBER', 'IP_ADDRESS', 'US_SSN'])
clean = anonymizer.anonymize(text=text, analyzer_results=results).text
# "Contact john@example.com or 555-1234" → "Contact <EMAIL_ADDRESS> or <PHONE_NUMBER>"
```

注意：PII 检测会误伤合法内容（如教程里的示例邮箱），脱敏后要抽样人工复核。

### 3.4 有害内容过滤

有害内容（toxicity、仇恨、暴力、成人）过滤是对齐安全的预处理层。预训练阶段剔除，能降低模型学到有害模式的概率；后训练阶段再用 RLHF/DPO 进一步对齐。

- **Perspective API**（Jigsaw / Google）：商业 API，对文本打 toxicity/severe_toxicity/identity_attack 等 6 维分数。很多大模型早期用它，缺点是免费配额有限、要联网。
- **Detoxify**（开源自托管模型）：基于 BERT 的 toxicity 分类器，效果接近 Perspective API，可本地部署。
- **规则 + 词表**：脏词列表（如 LDNOOBW）做粗筛，便宜但易绕过（拼写变体）。

注意平衡：过滤太狠会丢掉「讨论有害话题」的合法内容（新闻、医学、文学），让模型对相关话题一无所知，反而损害对齐。

### 3.5 语言识别：fastText 与 CLD3

CCNet pipeline 的第一步就是语言识别，把文档按语言分流。两个主力工具：

- **fastText `lid.176.bin`**（Meta，[arXiv:1612.03651](https://arxiv.org/abs/1612.03651) 的 fastText.zip）：176 种语言，单文件 126MB，CPU 每秒数万文档，精度极高。是工业首选。
- **CLD3**（Google Compact Language Detector v3）：基于神经网络，Chrome 浏览器内置。精度与 fastText 接近，但对混合语言（一段中文一段英文）的处理略好。

```python
import fasttext
model = fasttext.load_model('lid.176.bin')
lang, prob = model.predict("这是一个中文句子", k=1)   # (['__label__zh'], 0.98)
# 实务：保留 prob > 0.7 的，低于的丢弃（噪声语言/混码）
```

低资源语言是难点：fastText 对非洲小语种、方言的精度会下降。实务上对低资源语言设更低阈值（prob > 0.5），并接受较高的噪声。

### 3.6 代码过滤：编译失败与 autogenerated

代码数据除了 1.3 节的源过滤，还有两道深度过滤：

- **编译失败过滤**：对样本代码尝试解析（Python 用 `ast.parse`，JS 用 `acorn`），解析失败的剔除。这能去掉大量残缺、截断的代码片段。
- **autogenerated 过滤**：识别 `package-lock.json`、`yarn.lock`、`.min.js`、protobuf 生成代码、IDE 模板等。这些是「机械产物」，对模型学编程无价值且占空间。

```python
import ast
def is_valid_python(code: str) -> bool:
    try:
        ast.parse(code); return True
    except SyntaxError:
        return False
# 用 multiprocessing.Pool 并行跑，CCNet 风格
```

### 3.7 CCNet pipeline 完整图

把上面几节串起来，一个工业级 CC 处理 pipeline 的全貌（以 CCNet 为蓝本，Dolma/RefinedWeb 都在此基础上扩展）：

```
CC WARC 原始文件
   │
   ├─[trafilatura/resiliparse]→ 纯文本
   │
   ├─[fastText langid lid.176]→ 按语言分片
   │
   ├─[exact dedup + line dedup]→ 去重
   │
   ├─[KenLM (Wikipedia-trained)]→ perplexity → head/middle/tail 分档
   │
   ├─[C4/Gopher heuristic rules]→ 粗筛
   │
   ├─[fastText quality classifier]→ 精筛（DCLM 风格）
   │
   ├─[PII 移除（Presidio）+ toxicity（Detoxify）]→ 安全过滤
   │
   └→ 清洗后分片（jsonl/zstd 压缩，按语言/质量分层）
```

Dolma（AI2，[arXiv:2402.00159](https://arxiv.org/abs/2402.00159)，ACL 2024）开源了完整的 `dolma` 工具包（Python），把上述每一步写成可插拔的 tagger，是当前最透明的复现范本。它产出 3T tokens 的英文语料，被 OLMo 系列模型使用。

> **论文**：Dolma: an Open Corpus of Three Trillion Tokens for Language Model Pretraining Research [arXiv:2402.00159](https://arxiv.org/abs/2402.00159)（Soldaini et al., ACL 2024）。代码：`github.com/allenai/dolma`。

RefinedWeb（TII，Falcon 的训练数据，[arXiv:2306.01116](https://arxiv.org/abs/2306.01116)）证明了一个反直觉结论：**经过严格过滤与去重的纯网页数据，就能训出超过「网页 + 精选混合」的模型**。他们从 CC 拿到 5T tokens，开源 600B，Falcon-7B 在多数基准上超过同尺寸的 Llama。这条结论大幅降低了中小团队的门槛——不必费力搞混合，把网页清洗做好就够。

> **论文**：The RefinedWeb Dataset for Falcon LLM [arXiv:2306.01116](https://arxiv.org/abs/2306.01116)（Penedo et al., 2023）。

RedPajama-V2（Together / CS-LMB，[arXiv:2411.12372](https://arxiv.org/abs/2411.12372)，NeurIPS 2024 D&B）走另一条路：不做最终过滤，而是把 100T+ tokens 的网页文本连同 40+ 个 quality signal（perplexity、词频、符号比等）全部发布，让下游自己组合过滤策略。这是「数据作为平台」的思路，被 Snowflake Arctic、Salesforce XGen、AI2 OLMo 实际使用。

> **论文**：RedPajama: an Open Dataset for Training Large Language Models [arXiv:2411.12372](https://arxiv.org/abs/2411.12372)（Weber et al., NeurIPS 2024）。

### 3.8 OpenAI pipeline 推测

OpenAI / Anthropic 的清洗 pipeline 从未公开，但可以从 GPT-3 论文（[arXiv:2005.14165](https://arxiv.org/abs/2005.14165)）、泄漏信息、专利和招聘 JD 里拼出大致轮廓：

- **训练数据「质量分层」**：用 GPT-2/3 自己当打分器（类似 DFN 的思路）给候选文档打分，保留高分。这是 OpenAI 招聘「Data Scientist, Pretraining」JD 反复强调的「learning-based filtering」。
- **fuzzy dedup + adversarial filtering**：除了 MinHash，还会主动剔除「与测试集相似」的文档，减少 benchmark 污染（OpenAI 的 eval 团队与数据团队紧密配合）。
- **多轮 classifier stacking**：用一系列 fastText / 小 Transformer 分类器（质量、毒性、语言、机器翻译检测）层层过滤。
- **后训练用 Constitutional AI 风格的数据合成**（Anthropic，[arXiv:2212.08073](https://arxiv.org/abs/2212.08073)）：让模型自己 critique + revise，生成对齐数据，减少人工标注。

> **重要提醒**：以上 OpenAI/Anthropic 部分是「基于公开信息的合理推测」，非一手确认。他们的真实 pipeline 几乎可以肯定比这复杂得多。

---

## 四、数据混合：把不同领域按什么比例配在一起

清洗后你有了一堆「干净但分类」的数据：网页、代码、书籍、论文、对话、多语言。把它们按什么比例混在一起，是「Data Mixing」要回答的问题。这个比例对最终模型能力的影响，往往比模型架构的微调更大。

### 4.1 领域配比的经验值

Llama 3（[arXiv:2407.21783](https://arxiv.org/abs/2407.21783)）是少数公开讨论配比的大厂报告。Llama 3 405B 的预训练数据约 15T tokens，公开的粗略配比（按重要度）：

- **网页（CC 清洗后）**：占比最大（50%+），是知识与语言的主体；
- **代码**：显著占比（~15-20%），对推理能力贡献巨大；
- **数学**：专门的数学语料（~5-10%），来源包括数学网页、教材、arXiv；
- **多语言**：约 8%，覆盖几十种语言；
- **书籍/论文/对话**：其余，用于深度知识与对话能力。

注意：Llama 3 报告没有给精确百分比，以上是基于公开章节的合理估计。**不同模型配比差异极大**—— phi 系列（见第八章）几乎全是合成「textbook」数据，纯网页占比极低，照样训出强模型。

### 4.2 DoReMi：用 robust optimization 自动找配比

手动调配比是黑魔法。DoReMi（[arXiv:2305.10429](https://arxiv.org/abs/2305.10429)，Xie et al., NeurIPS 2023）把这件事变成优化问题：先用一个小 proxy 模型（如 280M）跑 **Group Distributionally Robust Optimization（Group DRO）**，自动找一组领域权重，使得「最差的那个领域」的 loss 最小（maximin）。然后用这组权重重采样数据，训一个 30 倍大的正式模型（8B）。

> **论文**：DoReMi: Optimizing Data Mixtures Speeds Up Language Model Pretraining [arXiv:2305.10429](https://arxiv.org/abs/2305.10429)（Xie et al., NeurIPS 2023）。

效果惊人：在 The Pile 上，DoReMi 在所有领域都改善了 perplexity（甚至当它主动降权某个领域时，那个领域的 perplexity 也变好了），下游 few-shot 平均提升 6.5 个百分点，且用 2.6 倍更少的步数达到 baseline 精度。关键洞察是：**Group DRO 自动发现了「这个领域被低估」的信号**，而人工拍脑袋往往会过分配给「看起来重要」的领域。

DoReMi 的局限：①需要一个有代表性的「域划分」；②proxy 模型太小可能误导；③不直接建模「域间转移」（学代码会不会帮助数学？）。但它是把数据混合从「艺术」推向「科学」的关键一步。

### 4.3 Data Mixing Laws：把配比变成可外推的函数

Data Mixing Laws（[arXiv:2403.16952](https://arxiv.org/abs/2403.16952)，Ye et al., ICLR 2025）走得更远：他们发现**模型 loss 与混合比例之间存在可拟合的函数关系**——用几组小规模实验（不同配比 × 小模型）拟合这个函数，就能外推预测大模型在不同配比下的表现，**不必真的去训大模型**。

> **论文**：Data Mixing Laws: Optimizing Data Mixtures by Predicting Language Modeling Performance [arXiv:2403.16952](https://arxiv.org/abs/2403.16952)（Ye et al., ICLR 2025）。

他们的方法：在 RedPajama 上用 1B 模型跑 100B tokens 的实验，拟合 mixing law，找到的最优配比训出的 1B 模型，性能相当于在默认配比上多训 48% 步数。进一步，他们把 mixing law 与 scaling law（步数、模型大小）嵌套使用，用小规模实验就能预测大模型 + 大数据的表现。BiMix（[arXiv:2405.14908](https://arxiv.org/abs/2405.14908)）把这件事再推广，建模「域比例」与「数据量」的联合缩放，loss 外推的相对误差 < 0.2%。

这一脉工作说明：**数据混合正在变成一个可计算、可外推的优化问题**，不再是「老法师凭感觉」。对资源有限的研究者，这是最值得跟进的方向之一。

### 4.4 Curriculum Learning

Curriculum learning 是「由易到难」的数据排序思路。在 NMT（机器翻译）和图像分类上有用，但在 LLM 预训练上**效果不稳定甚至负面**——因为大模型容量足够，不需要 curriculum；且大规模分布式训练下，curriculum 的实现复杂度极高。现代 LLM 几乎都不用传统 curriculum。

但有两个变体被广泛使用：

- **域内 curriculum**：预训练后期加入更多高质量数据（如数学、代码），类似 fine-tuning 的扩展。Llama 3 在预训练最后阶段增加高质量源。
- **退火学习率与数据切换同步**：在 LR decay 阶段切换到更高质量的数据，让模型「收尾时」学到好东西。

---

## 五、训练监控：Loss spike、梯度异常与 dead neuron

数据准备好的瞬间，70% 的工程活才刚开始——训练本身。一个 7B 模型训 2T tokens，要跑几周，几百张 GPU 协同，任何一个环节出错都可能毁掉全部。监控是这个阶段的生命线。

### 5.1 Loss spike：预训练的头号杀手

Loss spike 是预训练中最令人胆寒的现象：训练 loss 一直平稳下降，突然某一步飙升 2-10 倍，之后要么自行恢复，要么永久发散（NaN）。Llama 2 论文里明确提到他们遇到大量 loss spike，需要回滚 checkpoint。GPT-3、PaLM 都报告过。

成因很复杂：①**数据 batch 异常**——某个 batch 全是垃圾/重复/超长样本；②**学习率过大**——大模型在某些 saddle point 附近 LR 过大跳出去；③**数值精度**——BF16/FP16 的动态范围有限，某些梯度溢出；④**优化器状态污染**——Adam 的二阶矩估计被异常梯度污染，后续多步受影响。

应对策略（按从轻到重）：

1. **跳过坏 batch**：检测到 loss 异常升高时，跳过当前 batch 不更新，下一个 batch 继续。简单有效。
2. **梯度裁剪**：`torch.nn.utils.clip_grad_norm_(params, max_norm=1.0)`，把梯度范数限制在阈值内。几乎所有大模型训练的标准配置。
3. **学习率回退**：spike 后把 LR 临时降低，等 loss 恢复再回升。
4. **回滚 checkpoint**：spike 后 loss 不恢复，回滚到上一个健康 checkpoint，跳过问题 batch 重新训。
5. **数值格式升级**：从 FP16 换到 BF16（动态范围更大，不易溢出），关键层用 FP32。

```python
# 一个生产级的「loss spike 自动处理」训练循环骨架
from torch.nn.utils import clip_grad_norm_

for step, batch in enumerate(loader):
    loss = model(batch).loss
    if torch.isnan(loss) or torch.isinf(loss):
        print(f"[step {step}] NaN/Inf loss, skipping batch")
        optimizer.zero_grad()
        continue
    if step > 0 and loss.item() > rolling_mean * 3:   # spike 检测：超过滚动均值 3 倍
        print(f"[step {step}] Loss spike: {loss.item():.3f} > {rolling_mean:.3f}*3, rolling back LR")
        # 跳过本步 + 降 LR
        optimizer.zero_grad()
        for g in optimizer.param_groups:
            g['lr'] *= 0.5
        continue
    loss.backward()
    clip_grad_norm_(model.parameters(), max_norm=1.0)
    if any(torch.isnan(p.grad).any() for p in model.parameters() if p.grad is not None):
        print(f"[step {step}] NaN gradient, skipping update")
        optimizer.zero_grad()
        continue
    optimizer.step()
    update_rolling_mean(loss.item())
```

### 5.2 梯度异常：NaN 与爆炸

NaN 梯度通常是上游数值问题的下游表现。常见源头：①softmax 溢出（logit 过大）；②除零（如 LayerNorm 方差为 0）；③BF16 下溢出。调试法：①在每一步 backward 后扫一遍 `param.grad` 的 NaN；②开启 PyTorch anomaly detection（`torch.autograd.set_detect_anomaly(True)`），它会回溯到第一个产生 NaN 的算子，代价是慢 2-3 倍。

梯度爆炸（gradient explosion）表现为 grad norm 飙升，clip_grad_norm 是标配防御。配合 warmup（前几千步 LR 线性升）能进一步稳定。

### 5.3 激活异常：dead neuron 与 activation collapse

更隐蔽的是「激活级」异常。**Dead neuron**（死亡神经元）：某个 ReLU/GELU 神经元的输入恒为负，输出恒为 0，梯度为 0，永久失活。在深层网络里，这会让有效容量悄悄下降。检测法：统计每个 neuron 在一个 epoch 内的激活率，长期为 0 的标记为 dead。

**Activation collapse**（激活坍缩）：某些层的激活值范围越来越小，最终趋近常数，失去表达能力。常见于 LayerNorm 配置不当或初始化不佳。检测：监控每层激活的 std，持续下降是危险信号。

```python
# 激活统计 hook（每 N 步采样一次）
activation_stats = {}
def make_hook(name):
    def hook(module, inp, out):
        if not hasattr(make_hook, '_counter'): make_hook._counter = 0
        make_hook._counter += 1
        if make_hook._counter % 100 == 0:   # 每 100 步采一次，省开销
            activation_stats[name] = {
                'mean': out.float().mean().item(),
                'std':  out.float().std().item(),
                'dead_ratio': (out == 0).float().mean().item(),  # ReLU 失活率
            }
    return hook
for name, module in model.named_modules():
    if isinstance(module, torch.nn.Linear):
        module.register_forward_hook(make_hook(name))
```

### 5.4 梯度噪声分析

梯度信噪比（gradient signal-to-noise ratio）是判断训练是否健康的高阶指标。SNR 持续下降意味着模型在学噪声而非信号，应该考虑降 LR 或换数据。在分布式训练里，跨 rank 的梯度方差（gradient disagreement）也是关键——方差过大说明各 rank 看到的数据分布不一致，可能是 sampler bug。

### 5.5 Weight 统计：norm 与 spectral

监控权重的 Frobenius norm（每层）、spectral norm（最大奇异值，用于谱归一化诊断）、weight movement（每步权重变化幅度）。权重的 spectral norm 过大往往预示训练不稳定。Transformer 里，attention 的 Q/K/V 权重 norm 异常增长是 over-smoothing 的信号。

### 5.6 监控工具栈

- **Weights & Biases（wandb）**：事实标准，UI 最好，免费配额够小团队用。一行 `wandb.init()` 集成。
- **TensorBoard**：开源、本地、轻量，适合单机实验。
- **MLflow**：偏 MLOps 全流程（实验追踪 + 模型 registry + 部署），企业偏好。
- **自建 Prometheus + Grafana**：超大规模训练（千卡级）必备，因为 wandb 的 API 有速率限制，自建能扛住高频指标。

实务建议：基础 loss / LR / grad_norm 用 wandb 可视化；GPU 利用率、NCCL 流量、显存用 Prometheus + Grafana 监控基础设施层；关键 checkpoint 元数据写 MLflow。

---

## 六、故障恢复：千卡训练不是「能跑」就「能跑完」

训练一个 70B 模型，用 1024 张 H100 跑两周，期间几乎必然遇到：GPU 死、网络断、NCCL 卡死、OOM、坏 batch。如果每次故障都从头重来，整个训练永远跑不完。故障恢复体系是这个规模下能交付的前提。

### 6.1 Checkpoint 频率与策略

Checkpoint 是故障恢复的基础。频率的权衡：太频繁（每 100 步）浪费训练时间（一个 70B checkpoint 写盘几十 GB，几分钟）；太稀疏（每 10000 步）故障时损失大。实务：

- **频率**：每 1-2 小时存一次（约每 1000-5000 步，取决于 batch）。
- **内容**：模型权重 + optimizer state（Adam 的 momentum + variance，体积是权重的 2 倍）+ LR scheduler state + RNG state + 当前数据游标。**少存任何一项都会导致恢复后训出来的模型不一致**。
- **存储**：写本地 SSD（快）+ 异步上传对象存储（S3/OSS，慢但持久）。两份才安全。
- **保留策略**：保留最近 2-3 个 checkpoint，老的删除（磁盘吃不消）。

```python
# 一个完整的 checkpoint 保存（含所有恢复必需的状态）
def save_checkpoint(model, optimizer, scheduler, step, epoch, rng_states, path):
    torch.save({
        'model': model.state_dict(),                           # get_model_state_dict（FSDP 要 sharded save）
        'optimizer': optimizer.state_dict(),
        'scheduler': scheduler.state_dict(),
        'step': step,
        'epoch': epoch,
        'rng_states': {
            'python': rng_states['python'],
            'torch': rng_states['torch'],
            'cuda': rng_states['cuda'],
            'numpy': rng_states['numpy'],
        },
        'data_sampler_state': data_sampler.get_state(),
    }, path)

# FSDP 模式下用 sharded checkpoint 更省内存：
# from torch.distributed.checkpoint import save, FileSystemReader
```

### 6.2 NCCL crash：分布式训练的隐形杀手

NCCL（NVIDIA Collective Communications Library）是 PyTorch 分布式的底层。千卡训练里，NCCL 相关故障占大头。常见症状：训练卡住（不报错但不前进）、`NCCL error: unhandled system error`、某 rank 掉队。

调试与防御：

- **`NCCL_DEBUG=INFO`**：打开详细日志，能看到每步 allreduce 的耗时与异常。
- **`NCCL_SOCKET_IFNAME=eth0`**：明确指定网络接口（多网卡机器默认选错会导致走慢网）。
- **`NCCL_IB_DISABLE=1`** 或 `NCCL_IB_HCA=mlx5_0`：InfiniBand 配置，调错会卡死。
- **`NCCL_TIMEOUT`**：调大（默认 30 分钟，千卡训练偶尔有长 allreduce）。
- **`NCCL_ASYNC_ERROR_HANDLING=1`**：让 NCCL 错误异步上报，避免永久卡死。

```bash
# 启动训练时的标准 NCCL 环境变量
export NCCL_DEBUG=WARN
export NCCL_SOCKET_IFNAME=eth0
export NCCL_IB_HCA=mlx5_0:1
export NCCL_ASYNC_ERROR_HANDLING=1
export NCCL_TIMEOUT=1800           # 30 分钟
export TORCH_DISTRIBUTED_DEBUG=DETAIL   # PyTorch 侧详细日志
```

最让人崩溃的是「静默挂起」——所有 rank 都在等 allreduce，没有任何错误。这时只能靠 watchdog：每个 rank 周期性心跳，发现某 rank 心跳停止就主动 abort + 重启。

### 6.3 OOM 恢复

OOM（Out Of Memory）常见于：①batch size 过大；②激活 checkpointing 没开；③optimizer state 在 FP32 下太大；④长序列样本（如 32K context）。防御：

- **激活 checkpointing**（gradient checkpointing）：用计算换显存，只存部分层激活，反向时重算。代价：慢约 30%，但显存省 60%+。大模型标配。
- **ZeRO / FSDP**：把 optimizer state / 梯度 / 参数分片到各 rank，DeepSpeed ZeRO-3 或 PyTorch FSDP 是标准。
- **动态 batch size**：遇到超长样本时自动降 batch，避免单卡 OOM。

OOM 后的处理：捕获 `RuntimeError: CUDA out of memory`，降 batch size 重启当前 step，或跳过该 batch。

### 6.4 硬件故障：GPU 死、网络断

数据中心级故障：①单卡硬件故障（ECC error、掉卡）；②网络交换机故障；③供电波动。这些无法在软件层完全避免，只能靠「快速检测 + 自动重启」：

- **节点健康检查**：训练前每节点跑 GPU burn 测试，剔除不稳定卡。
- **冗余节点**：预留 5-10% 节点，某节点挂了自动顶上（Slurm / K8s 支持）。
- **elastic training**：PyTorch 的 `torchrun --elastic` 支持节点动态加入/退出，故障时自动缩容继续训。

```bash
# torchrun elastic：节点数可变，故障自动重组
torchrun --nnodes=8:16 --nproc_per_node=8 \
    --rdzv_backend=c10d --rdzv_endpoint=host:29500 \
    train.py --checkpoint_dir=/shared/ckpt
# --nnodes=8:16 表示最少 8 最多 16 节点，故障降到 8 仍能继续
```

### 6.5 跳过坏样本

数据层面的故障——某个 batch 含 NaN 样本、超长序列、编码错误——会导致整步崩溃。防御：在 DataLoader 的 collate 层加「样本清洗 + 异常跳过」：

```python
def safe_collate(batch):
    cleaned = []
    for sample in batch:
        ids = sample['input_ids']
        if len(ids) == 0: continue
        if len(ids) > MAX_LEN:
            ids = ids[:MAX_LEN]                    # 截断超长
        if ids.float().std() == 0: continue        # 全相同（脏数据）
        cleaned.append(sample)
    if len(cleaned) < len(batch) * 0.5:
        raise SkipBatch                             # 一半以上坏了，整 batch 跳过
    return default_collate(cleaned)
```

### 6.6 PyTorch Distributed 的容错

PyTorch 2.x 的弹性训练栈：`torch.distributed.run`（torchrun）+ `torch.distributed.elastic` + `torch.distributed.checkpoint`。这套组合允许节点动态伸缩、故障自动恢复、checkpoint 分片保存。Megatron-LM、DeepSpeed 都构建在此之上。

关键工程经验：①永远不要假设「训练会顺利跑完」，所有训练脚本都要能从任意 checkpoint 续训；②checkpoint 写两份（本地 + 远程）；③写一个「健康检查」脚本，定期 load checkpoint 验证完整性；④预演故障恢复——人为 kill 进程，看能否自动恢复，否则真正故障时一定手忙脚乱。

---

## 七、可复现性：为什么「同样的代码训出不同的模型」

ML 最让人沮丧的经历之一：同一份代码、同一份数据，跑两次得到不同的模型，benchmark 分数差几个点。在科研上这破坏可复现性，在工程上这让 A/B 测试失效。可复现性是「科学性」的底线。

### 7.1 随机种子

最基础也最容易被忽略。所有随机源都要固定：Python `random`、`numpy.random`、`torch`（CPU）、`torch.cuda`。少一个都不可复现。

```python
import os, random, numpy as np, torch
def set_seed(seed: int):
    os.environ['PYTHONHASHSEED'] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    # DataLoader 的 worker 也要固定
    def worker_init(worker_id):
        np.random.seed(seed + worker_id)
        random.seed(seed + worker_id)
    # sampler 也要固定
    torch.use_deterministic_algorithms(True, warn_only=True)
```

### 7.2 cuDNN deterministic

cuDNN 默认用非确定算法（为了快）。开启确定性要付出性能代价：

```python
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False       # 关闭自动选 kernel（非确定）
torch.use_deterministic_algorithms(True)
os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'   # CUDA 11+ 确定性的硬性要求
```

**实务权衡**：调试 / 科研时开 deterministic，大规模生产训练关掉（损失 5-10% 速度，换可复现得不偿失）。但要把 seed 固定，保证「同 seed 同结果」。

### 7.3 环境锁

`pip freeze > requirements.txt` 是最低要求。严肃项目用 `conda env export --no-builds` 或 `pip-compile` 锁定完整依赖树。Docker 镜像固定 tag（不要用 `latest`）。CUDA / cuDNN / NCCL 版本写进 README——这些底层库版本不一致会导致数值结果漂移。

### 7.4 数据版本：DVC

数据会变（清洗 pipeline 改进、新增源、修 bug），「v3 数据」训的模型与「v4 数据」不可比。DVC（Data Version Control）把大文件/目录纳入 git 版本管理（实际存储在 S3/OSS，git 只存指针），让 `dvc checkout` 能切回任意版本数据。

```bash
git add train.py && git commit -m "improve filter"
dvc add data/corpus_v4/        # 数据进 DVC，指针进 git
dvc push                       # 数据推到远程存储
# 后续：dvc checkout 可切到任意历史数据版本
```

### 7.5 训练 config 版本：Hydra

训练超参（LR、batch、warmup、数据配比、模型结构）如果散落在命令行参数里，很快会失控。Hydra（Meta 开源）用结构化 YAML 管理 config，支持组合、覆盖、自动记录每次运行的完整 config 到输出目录。这是把「实验配置」当代码管理的事实标准。

```python
# config.yaml
model:
  hidden_size: 4096
  num_layers: 32
training:
  lr: 3e-4
  batch_size: 256
  warmup_steps: 2000
data:
  mixing:
    web: 0.5
    code: 0.2
    math: 0.1
# 命令行覆盖：python train.py training.lr=1e-4 data.mixing.code=0.3
```

每次运行 Hydra 自动把最终生效的 config 存到 `outputs/<date>/<time>/.hydra/`，事后能精确复现。

---

## 八、合成数据：用模型生成数据来训模型

当真实数据不够好、不够多、不够多样时，用强模型（GPT-4、Claude）生成数据来训小模型，已经成为 2023 年后的事实标准。这一节是「数据栈」里增长最快的部分。

### 8.1 Self-Instruct：自举指令数据

Self-Instruct（[arXiv:2212.10560](https://arxiv.org/abs/2212.10560)，Wang et al., ACL 2023）是奠基工作。思路极简：给 LLM 一组 175 个种子指令，让它自己生成更多指令 + 输入 + 输出，过滤掉重复与无效的，再用这些数据微调自己。结果：vanilla GPT-3 在 Super-NaturalInstructions 上提升 33 个绝对百分点，逼近 InstructGPT-001。

> **论文**：Self-Instruct: Aligning Language Models with Self-Generated Instructions [arXiv:2212.10560](https://arxiv.org/abs/2212.10560)（Wang et al., ACL 2023）。代码：`github.com/yizhongw/self-instruct`。

Self-Instruct 的核心贡献是证明了「指令数据可以从模型自身廉价地大规模生成」，打破了「对齐需要海量人工标注」的假设。后续的 Alpaca、Vicuna、WizardLM 都是这个范式。

### 8.2 Evol-Instruct：让指令越来越难

WizardLM 的 Evol-Instruct（[arXiv:2304.12244](https://arxiv.org/abs/2304.12244)，Xu et al., ICLR 2024）针对 Self-Instruct 的弱点——生成的指令复杂度不够——做了改进：从一组种子指令出发，用 LLM 逐步把它们「进化」成更复杂的版本（加约束、加深推理、变场景），生成不同难度梯度的指令。Evol-Instruct 生成的指令在人工评估中胜过人工写的指令，WizardLM 在 17/29 项技能上达到 ChatGPT 90% 的能力。

> **论文**：WizardLM: Empowering large pre-trained language models to follow complex instructions [arXiv:2304.12244](https://arxiv.org/abs/2304.12244)（Xu et al., ICLR 2024）。

Evol-Instruct 的思路被推广到代码（WizardCoder, [arXiv:2306.08568](https://arxiv.org/abs/2306.08568)）和数学（WizardMath, [arXiv:2308.09583](https://arxiv.org/abs/2308.09583)），都取得了显著提升。它的启示是：**合成数据的关键不只是「多」，更是「有难度梯度」**——让模型见到从易到难的全谱。

### 8.3 Magpie：从对齐模型「免费」抽取对齐数据

Magpie（[arXiv:2406.08464](https://arxiv.org/abs/2406.08464)，Xu et al., 2024）发现了一个巧妙的性质：对齐过的 LLM（如 Llama-3-Instruct）的「左半边模板」（system + assistant 起始 token）是空的，自回归特性会让模型自己生成一个合理的 user query。于是他们只喂左半边模板，让 Llama-3-Instruct 自己生成 400 万条指令 + 回复，筛出 30 万高质量数据微调 Llama-3-8B-Base，结果在某些任务上接近官方 Llama-3-8B-Instruct——而后者用了 1000 万数据 + SFT + 反馈学习。

> **论文**：Magpie: Alignment Data Synthesis from Scratch by Prompting Aligned LLMs with Nothing [arXiv:2406.08464](https://arxiv.org/abs/2406.08464)（Xu et al., 2024）。

Magpie 的意义：对齐数据可以「从空气中变出来」，无需种子指令、无需人工。这极大降低了高质量对齐数据的获取门槛。

### 8.4 Phi 系列：textbook 质量的合成数据

微软 Phi 系列是「合成数据 + 小模型」路线的旗手。phi-1（[arXiv:2306.11644](https://arxiv.org/abs/2306.11644)，Gunasekar et al., 2023，「Textbooks Are All You Need」）只用 6B 「textbook quality」网页 token + 1B GPT-3.5 合成的教材与练习，1.3B 参数，8 张 A100 训 4 天，HumanEval pass@1 达到 50.6%——远超同尺寸甚至更大的模型。

> **论文**：Textbooks Are All You Need [arXiv:2306.11644](https://arxiv.org/abs/2306.11644)（Gunasekar et al., 2023）。

phi-1.5（[arXiv:2309.05463](https://arxiv.org/abs/2309.05463)）扩展到自然语言推理，phi-3（[arXiv:2404.14219](https://arxiv.org/abs/2404.14219)）把 phi-3-mini（3.8B，3.3T tokens）训到 MMLU 69%，逼近 Mixtral 8x7B 和 GPT-3.5。phi 系列的核心论点是：**数据质量远比数据量重要**——精心合成的「教材级」数据，能让小模型达到大模型的水平。这与 Chinchilla 的「等比 scaling」形成有趣对照：phi 走的是「质量超越数量」的捷径。

> **论文**：Phi-3 Technical Report [arXiv:2404.14219](https://arxiv.org/abs/2404.14219)（Microsoft, 2024）。phi-3-mini 3.8B / 3.3T tokens → MMLU 69%。

值得追溯的更早工作还有 **TinyStories**（[arXiv:2305.07759](https://arxiv.org/abs/2305.07759)，Eldan & Li 2023）——用 GPT-3.5/4 合成儿童故事，训出不到 1000 万参数的模型能生成连贯英文，颠覆了「连贯语言需要大模型」的常识，是 phi 系列思想的源头。

### 8.5 Orca 与 reasoning trace 蒸馏

Orca（[arXiv:2306.02707](https://arxiv.org/abs/2306.02707)，Mukherjee et al., 2023）证明：从小模型蒸馏时，不要只蒸馏「最终答案」，要蒸馏 GPT-4 的**完整推理轨迹**（explanation traces、step-by-step thought）。13B 的 Orca 在 BBH 上达到与 ChatGPT 相当，超过 Vicuna-13B 100%。

> **论文**：Orca: Progressive Learning from Complex Explanation Traces of GPT-4 [arXiv:2306.02707](https://arxiv.org/abs/2306.02707)（Mukherjee et al., 2023）。

### 8.6 Persona Hub：十亿角色驱动数据合成

Persona Hub（[arXiv:2406.20094](https://arxiv.org/abs/2406.20094)，Ge et al., 2024）把合成数据推向极致：从网页数据自动提炼出 10 亿个「角色画像」（persona，约世界人口 13%），每个角色作为 LLM 的视角，能生成截然不同的合成数据。论文展示了用它合成数学题、指令、知识文本、游戏 NPC、工具函数的用例。

> **论文**：Scaling Synthetic Data Creation with 1,000,000,000 Personas [arXiv:2406.20094](https://arxiv.org/abs/2406.20094)（Ge et al., 2024）。

### 8.7 偏好数据与过程监督

合成数据不止用于 SFT，也用于偏好对齐。**PRM800K**（[arXiv:2305.20050](https://arxiv.org/abs/2305.20050)，Lightman et al., 2023，「Let's Verify Step by Step」）发布 80 万条 step-level 人工标注的数学推理反馈，证明**过程监督**（每步打分）显著优于结果监督（只看最终答案），在 MATH 子集上达到 78%。这是 o1 / o3 系列推理模型的 data 基石。

> **论文**：Let's Verify Step by Step [arXiv:2305.20050](https://arxiv.org/abs/2305.20050)（Lightman et al., 2023）。PRM800K 数据集。

**Constitutional AI**（[arXiv:2212.08073](https://arxiv.org/abs/2212.08073)，Bai et al., 2022）用一套「宪法」（规则列表）让模型自己 critique + revise 自己的输出，生成偏好数据（RLAIF），减少人工标注。这是 Anthropic Claude 系列的对齐核心。

> **论文**：Constitutional AI: Harmlessness from AI Feedback [arXiv:2212.08073](https://arxiv.org/abs/2212.08073)（Bai et al., 2022）。

### 8.8 合成数据的风险

合成数据不是万能药，有真实风险：

- **模型坍缩（model collapse）**：用模型生成的数据再训模型，多代之后分布退化（长尾丢失、多样性下降）。Shumailov et al. 2024 的研究警告这会让模型「自我中毒」。
- **同质化**：所有用 GPT-4 蒸馏的小模型，都继承了 GPT-4 的偏见与盲点，失去多样性。
- **质量天花板**：合成数据质量受限于「教师模型」，教师模型的错误会被放大。
- **可验证性**：数学/代码合成数据可以靠形式化验证（编译、单元测试、Lean 证明）筛真伪，但开放域文本无法验证，噪声难控。

实务建议：合成数据用作「补充」而非「替代」真实数据；数学/代码类优先用合成（可验证）；定期用全新真实数据「刷新」，避免模型坍缩。

---

## 九、关键论文清单（按重要性排序）

以下是理解 LLM 训练数据栈必读的论文，全部 arXiv ID 已核实：

| 主题 | 论文 | arXiv |
|------|------|-------|
| **CC 清洗管线（奠基）** | CCNet: Extracting High Quality Monolingual Datasets from Web Crawl Data | [1911.00359](https://arxiv.org/abs/1911.00359) |
| **去重（必读）** | Deduplicating Training Data Makes Language Models Better | [2107.06499](https://arxiv.org/abs/2107.06499) |
| **数据受限 scaling** | Scaling Data-Constrained Language Models | [2305.16264](https://arxiv.org/abs/2305.16264) |
| **数据 benchmark** | DataComp-LM (DCLM) | [2406.11794](https://arxiv.org/abs/2406.11794) |
| **数据 benchmark（多模态）** | DataComp | [2304.14108](https://arxiv.org/abs/2304.14108) |
| **质量过滤网络** | Data Filtering Networks (DFN) | [2309.17425](https://arxiv.org/abs/2309.17425) |
| **数据混合优化** | DoReMi | [2305.10429](https://arxiv.org/abs/2305.10429) |
| **混合律** | Data Mixing Laws | [2403.16952](https://arxiv.org/abs/2403.16952) |
| **合成数据-指令** | Self-Instruct | [2212.10560](https://arxiv.org/abs/2212.10560) |
| **合成数据-进化** | WizardLM (Evol-Instruct) | [2304.12244](https://arxiv.org/abs/2304.12244) |
| **合成数据-对齐** | Magpie | [2406.08464](https://arxiv.org/abs/2406.08464) |
| **合成数据-textbook** | Textbooks Are All You Need (phi-1) | [2306.11644](https://arxiv.org/abs/2306.11644) |
| **小模型大能力** | TinyStories | [2305.07759](https://arxiv.org/abs/2305.07759) |
| **推理蒸馏** | Orca | [2306.02707](https://arxiv.org/abs/2306.02707) |
| **过程监督** | Let's Verify Step by Step (PRM800K) | [2305.20050](https://arxiv.org/abs/2305.20050) |
| **宪法 AI** | Constitutional AI | [2212.08073](https://arxiv.org/abs/2212.08073) |
| **数据集（网页为主）** | RefinedWeb (Falcon) | [2306.01116](https://arxiv.org/abs/2306.01116) |
| **数据集（开放透明）** | Dolma | [2402.00159](https://arxiv.org/abs/2402.00159) |
| **数据集（信号平台）** | RedPajama | [2411.12372](https://arxiv.org/abs/2411.12372) |
| **数据集（多源混合）** | The Pile | [2101.00027](https://arxiv.org/abs/2101.00027) |
| **scaling 律（数据）** | Training Compute-Optimal LLMs (Chinchilla) | [2203.15556](https://arxiv.org/abs/2203.15556) |
| **Tokenizer（BPE）** | Neural MT of Rare Words with Subword Units | [1508.07909](https://arxiv.org/abs/1508.07909) |
| **Tokenizer（Unigram）** | Subword Regularization | [1804.10959](https://arxiv.org/abs/1804.10959) |
| **Tokenizer（框架）** | SentencePiece | [1808.06226](https://arxiv.org/abs/1808.06226) |
| **大模型报告（数据章节）** | The Llama 3 Herd of Models | [2407.21783](https://arxiv.org/abs/2407.21783) |
| **开放模型（含数据）** | OLMo | [2402.00838](https://arxiv.org/abs/2402.00838) |
| **GPT-3（奠基）** | Language Models are Few-Shot Learners | [2005.14165](https://arxiv.org/abs/2005.14165) |

---

## 十、给「应用数学研究型工程师」的落地建议

回到你的目标：你是工程基础扎实、数学从零补、想做「应用数学研究型工程师」的人。训练数据栈对你来说，是把工程能力转化为研究能力的最佳入口——因为这一层「工程即研究」「研究即工程」的边界最模糊。三个递进的动手项目：

### 项目一：跑通 CCNet pipeline（1-2 周）

不要一开始就跑全量 CC（PB 级，你跑不动）。下载 CC 的**一个月**的 WARC 分片（约 100 个文件，几十 GB），按 CCNet 论文（[arXiv:1911.00359](https://arxiv.org/abs/1911.00359)）的步骤跑一遍：

1. `warcio` 解析 WARC → HTML；
2. `trafilatura` 抽取正文；
3. `fasttext lid.176.bin` 语言识别；
4. `text-dedup` MinHash 去重；
5. 在中文 Wikipedia 上用 `kenlm` 训一个 5-gram LM，给文档打 perplexity；
6. 按 perplexity 分档，统计各档质量。

**交付物**：一份 markdown 报告，记录每一步的输入/输出规模、过滤掉的比例、几个抽样样本的对比。这个项目让你理解「数据是工程」的全部细节，且每个工具都是工业级，简历加分。

### 项目二：训练自己的 tokenizer（3-5 天）

收集 1-5 GB 的中文 + 代码 + 英文混合文本（Wikipedia dump + GitHub clone + CC 抽样），用 HuggingFace `tokenizers` 训三个 vocab size（32K / 64K / 128K）的 tokenizer，对比：

- 同一段文本的 token 数（压缩率）；
- 中文 fragmentation rate；
- 训练 tokenizer 的时间与内存；
- 把三个 tokenizer 各自接一个 10M 参数的小模型，训 1 epoch，对比 loss。

**交付物**：一个能讲清楚的「tokenizer 设计权衡」实验。这是 tokenizer 这一章的实证版，会让你对「vocab size 是全局优化」有切肤理解。

### 项目三：用 LoRA 微调做数据质量实验（1-2 周）

这是连接「数据」与「研究」的关键项目。选一个开源基座（Qwen2-0.5B 或 Llama-3-8B），准备三组不同质量的 SFT 数据：①高质量（人工精选 / Magpie 抽样）；②中质量（随机 Alpaca）；③低质量（机器翻译 + 噪声）。用 LoRA 在三组数据上各微调一次，在统一 benchmark 上评测。

**交付物**：一份「数据质量 → 模型能力」的定量关系图。这把你从「调参工程师」推向「数据研究者」——你会亲眼看到「数据质量每提升一档，benchmark 涨几个点」，这就是 DCLM / DFN 那一脉研究的微观版本。

### 长期方向：数据作为可计算的优化问题

从研究视角，训练数据栈最大的开放问题是：**数据混合 / 数据质量能否成为一个可计算、可外推的优化目标**？Data Mixing Laws（[arXiv:2403.16952](https://arxiv.org/abs/2403.16952)）和 BiMix（[arXiv:2405.14908](https://arxiv.org/abs/2405.14908)）开了头，但还远未解决。这需要：①scaling law 的数学建模（你的数学补齐方向正好用上）；②大规模实验基础设施（你的工程基础正好用上）；③对「什么是数据质量」的形式化定义（这是开放问题）。

这是一个工程与数学深度交叉的领域，正适合「应用数学研究型工程师」的定位。比起追架构创新（红海），数据栈的研究空间大得多，且工业界急需。

---

## 📌 进一步阅读

**数据集与 benchmark**
- DataComp / DCLM 官网：`datacomp.ai` —— 唯一可以「玩数据」的 benchmark，强烈建议注册参赛。
- Dolma 工具包：`github.com/allenai/dolma` —— 最透明的清洗 pipeline 实现。
- RedPajama-V2：`together.ai/blog/redpajama-data-v2` —— 100T tokens + 40+ quality signal 的「数据平台」。

**工具栈**
- `trafilatura`：HTML 正文抽取首选。
- `text-dedup`：去重瑞士军刀。
- `datasketch`：MinHash/LSH Python 库。
- `kenlm`：n-gram 语言模型（perplexity filtering）。
- `tokenizers`（HuggingFace）：Rust 实现的高速 tokenizer 训练库。
- `sentencepiece`：Google 的多语言 tokenizer。
- `tiktoken`：OpenAI 的 BPE（用于 GPT-4o 等的在线分词）。
- `Presidio`：PII 检测与脱敏。
- `Detoxify`：自托管 toxicity 分类。
- `Hydra`：训练 config 管理。
- `DVC`：数据版本控制。
- `wandb` / `MLflow`：实验追踪。

**博客与社区**
- HuggingFace Blog（`huggingface.co/blog`）：数据相关文章质量高，尤其 BigCode / SmolLM / Cosmopedia 系列。
- EleutherAI Discord：数据工程讨论密集。
- `lifearchitect.ai`（Alan Thompson）：跟踪前沿模型的数据规模。

**经典论文（本节未展开但重要）**
- The Pile（[arXiv:2101.00027](https://arxiv.org/abs/2101.00027)）：22 个高质量子集的混合，是「混合数据」思路的奠基。
- OLMo（[arXiv:2402.00838](https://arxiv.org/abs/2402.00838)）：AI2 的全开放模型（数据 + 代码 + 权重），研究 LLM 的最佳样本。
- GPT-3（[arXiv:2005.14165](https://arxiv.org/abs/2005.14165)）：附录有早期数据清洗的描述，虽简略但历史价值高。

---

## ✍️ 思考题

1. **fragmentation 代价量化**：用一个 32K tokenizer 把 1GB 中文文本编码，计算平均每字消耗的 token 数；再训一个 64K 中文优化 tokenizer 重算。如果把模型 context 设为 4K，两种 tokenizer 下你能读到的「人读字数」差多少？把这个换算成「等效训练算力损失」。

2. **去重阈值选择**：MinHash 的 threshold 设 0.5 vs 0.8，对最终模型的影响是「精度」问题还是「召回」问题？设计一个小实验（用 1GB 数据训 50M 模型）定量回答。提示：Lee et al.（[arXiv:2107.06499](https://arxiv.org/abs/2107.06499)）的去重工具能直接测 verbatim memorization 率。

3. **DoReMi vs Data Mixing Laws**：两者都用小模型预测大数据的配比，但方法不同（Group DRO vs 函数拟合）。从「应用数学」视角，哪种更接近一个「定理」，哪种更接近一个「算法」？它们各自的理论假设是什么，什么情况下会失效？

4. **合成数据的「天花板」**：phi 系列用合成 textbook 数据训出强模型，但所有合成数据都来自 GPT-3.5/4。这是否意味着 phi 的能力上限被 GPT-3.5/4 锁死？设计一个思想实验：如果教师模型在某个数学子领域有系统性错误，phi 系列在这个子领域的表现会如何？如何用形式化验证（Lean / 单元测试）缓解？

5. **模型坍缩的数学建模**：Shumailov et al. 证明用模型生成数据再训模型会导致分布退化。从信息论角度，这是「信息丢失」还是「信息增强」？如果把训练数据建模为对一个未知分布的采样，合成数据是「对采样的再采样」，它引入的「方差」与「偏差」分别是什么？这是否能用 KL 散度或 Wasserstein 距离量化？——这个问题直接连接你的「信息论」研究方向。

---

## 附：核实勘误记录（2026-07-20）

本文所有 arXiv ID 均经 `export.arxiv.org/api/query` 一手核实。核实中发现并拒绝引用的常见错误 ID：

- ❌ **DataComp 误引为 `2304.08274`**：该 ID 实为「An asymptotically exact first-order shear deformation theory for functionally graded plates」（板块力学，cond-mat.soft）。正确为 **`2304.14108`**（Gadre et al., NeurIPS 2023）。语言模型版本 DCLM 为 `2406.11794`。
- ❌ **BPE 误引为 `1610.03054`**：该 ID 实为「Delayed charge recovery discrimination of passivated surface alpha events in P-type point-contact detectors」（核探测器物理）。正确为 **`1508.07909`**（Sennrich et al., ACL 2016）。
- ❌ **WizardLM/Evol-Instruct 误引为 `2305.14108` 或 `2402.09168`**：前者实为「Topological nature of the proper spin current」（凝聚态物理），后者实为「Stabilizing Consensus is Impossible in Lossy Iterated Immediate Snapshot Models」（分布式计算）。正确为 **`2304.12244`**（Xu et al., ICLR 2024）。
- 提醒：本文大纲原始版本的若干 ID（2304.08274、2305.14108、2402.09168、2212.10561、2306.02920）经核实全部不对应预期论文，已逐一查实正确 ID 后引用。**任何 LLM 给出的 arXiv ID 都必须二次核实，铁律不可破。**

<!-- delegate 直接写入，2026-07-20 -->
