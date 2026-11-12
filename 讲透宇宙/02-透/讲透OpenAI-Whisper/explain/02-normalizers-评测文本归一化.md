# 02 · normalizers：评测侧文本归一化

## 角色定位

normalizers 是一个 4 文件的二级包（whisper/normalizers/），职责是把"转写文本"与"参考文本"压到同一规范形式后再算 WER/CER——它是**评测管线的官方预处理**，不是转写管线的一部分。最重要的定位事实：**包内零消费**。全仓 grep 显示 whisper 主链路（audio/model/tokenizer/decoding/transcribe/timing/utils）没有任何一处 import normalizers；唯二消费者是测试 tests/test_normalizer.py 与评测 notebooks（notebooks/LibriSpeech.ipynb、notebooks/Multilingual_ASR.ipynb）。做推理可以完全跳过本包；做评测（复现论文 WER）则必读。

导出面只有两个名字（whisper/normalizers/__init__.py:1-2）：`BasicTextNormalizer` 与 `EnglishTextNormalizer`。

## 内部结构

**basic.py（80 行）——语言无关清洗器**：

- `remove_symbols_and_diacritics`（whisper/normalizers/basic.py:27-47）：NFKD 分解后，附加符号类 Mn 直接删、标记/符号/标点类 MSP 换空格（whisper/normalizers/basic.py:40-42），配一张手工补充表 ADDITIONAL_DIACRITICS 处理 NFKD 拆不开的 œ/ø/æ/ß/đ/ð/þ/ł 等 16 个特殊字母（whisper/normalizers/basic.py:7-24）。
- `remove_symbols`（whisper/normalizers/basic.py:50-57）：同上但**保留**变音符号，供不需要去腔调的语言（如依赖变音符的越南语系外的场景）。
- `BasicTextNormalizer`（whisper/normalizers/basic.py:60-80）：lower → 去方括号/圆括号内容（whisper/normalizers/basic.py:69-70）→ clean → 可选 `split_letters` 用 Unicode 字素 `\X` 逐字切分（whisper/normalizers/basic.py:74，依赖 `regex` 第三方库而非标准 `re`——这是本包隐藏的额外依赖）→ 压空白。构造参数 `remove_diacritics` 默认 False、`split_letters` 默认 False。

**english.py（553 行）——英文全管线**，三个类：

1. `EnglishSpellingNormalizer`（whisper/normalizers/english.py:452-464）：加载同目录 english.json（约 1700 对英式→美式拼写，whisper/normalizers/english.py:460-461），逐词查表替换（colour→color）。
2. `EnglishNumberNormalizer`（whisper/normalizers/english.py:12-449）：**437 行的拼写数字状态机**，本包最重的一块。__init__ 构建词表族：zeros/ones/tens/multipliers（到 decillion，whisper/normalizers/english.py:92-105）及各自的复数/序数变体（如 "sixes"、'twentieth'、"millionth"）；外加货币前后缀词表（pound/dollar→£/$，whisper/normalizers/english.py:124-133）、正负号词（whisper/normalizers/english.py:118-123）、specials {"and","double","triple","point"}（whisper/normalizers/english.py:142）。`process_words`（whisper/normalizers/english.py:165-386）用三词滑窗逐词消费，处理 "twenty three"→23、"one oh one"→101（连续个位数串接，whisper/normalizers/english.py:218-219）、"$20 million"→"20000000 dollars"（whisper/normalizers/english.py:331-337）、"274th" 序数后缀（whisper/normalizers/english.py:243-264）。preprocess 先把 "and a half" 改写成 "point five"（whisper/normalizers/english.py:392-404）、数字字母边界插空格（whisper/normalizers/english.py:409-410）；postprocess 把 "$2 and ¢7" 合成 "$2.07"（whisper/normalizers/english.py:434）。
3. `EnglishTextNormalizer`（whisper/normalizers/english.py:467-552）：总装管线 `__call__` 顺序为 lower → 删方括号/圆括号内容 → 删语气词 hmm/um/mmm（ignore_patterns，whisper/normalizers/english.py:469、533）→ 40 余条缩写俚语正则替换（won't→will not、gonna→going to、mr→mister，whisper/normalizers/english.py:470-524）→ 去数字间逗号 → 符号清洗保留货币符号 → 数字标准化 → 拼写统一 → 货币百分号间距规范化 → 压空白（whisper/normalizers/english.py:528-552）。

## 外部连接

- 输入来源：转写侧 `result["text"]`（whisper/transcribe.py:511）或参考标注文本。
- 消费者：tests/test_normalizer.py 70+ 断言（最大测试文件）；notebooks/LibriSpeech.ipynb 的 WER 计算；data/meanwhile.json 长音频实验的对照。多语言 notebook 用 BasicTextNormalizer 算 CER。
- 依赖：more-itertools 的 windowed（whisper/normalizers/english.py:7）、regex（whisper/normalizers/basic.py:74）、标准库 fractions.Fraction 做精确小数乘法（whisper/normalizers/english.py:4）。

## 数据流

一句 "It's twenty three dollars, uh, colour" 走 EnglishTextNormalizer：

```
"it's twenty three dollars, uh, colour"     lower+删语气词（whisper/normalizers/english.py:529-533）
→ "it is twenty three dollars, colour"       's→ is、uh 删除（whisper/normalizers/english.py:517-518,533）
→ "it is 23 dollars, color"                  数字状态机+拼写表（whisper/normalizers/english.py:543-544）
→ "it is 23 dollars color"                   去数字间逗号/符号清洗（whisper/normalizers/english.py:539-541）
→ "it is 23 dollar color"?                   注意：dollars 不在替换表，见勘误③
```

WER 评测两边的文本都过同一 normalizer 后按词比对——"预测 23"与"参考 twenty-three"才不会被判两错。

## 设计决策

1. **归一化与推理彻底解耦**：不进转写管线，避免"为了 WER 好看而改用户可见输出"。这是学术评测的诚实姿态。
2. **数字处理选状态机而非正则**：英文数字组合是上下文相关的（hundred 后接 and），正则无法可靠覆盖，宁要 437 行状态机。代价是可读性下降，测试文件因此异常庞大。
3. **两档力度**：English 全管线激进（去标点、去腔调、统一数字拼写）；Basic 只做符号清洗且默认保留变音符号——给依赖变音符的语言留活路。
4. **词表全在 __init__ 构建**（EnglishNumberNormalizer 一次性构造 10 余个 dict/set），实例可复用，符合评测批量场景。

## 新人提示

- 评测自己的转写结果时务必两侧同用 `EnglishTextNormalizer()(text)`；只归一化一侧会把数字/缩写差异全算成错误，WER 虚高。
- 想支持新语言评测：直接用 BasicTextNormalizer 算 CER（字符错误率），这是 Multilingual_ASR notebook 的做法；别试图给每语言写 english.py 级别的状态机。
- tests/test_normalizer.py 是本包最好的文档——每个坑案例（"one oh one"、"and a half"、货币组合）都有断言。
- 注意 `split_letters=True` 只在 Basic 里存在且默认关；中文按字算 CER 时才需要开。

## 勘误

1. 图谱摘要称 normalizers 供"WER 评测使用"属实，但需钉版强调：**主转写链路零 import**，`whisper/normalizers/__init__.py:1` 仅 re-export，防止新人误以为转写输出已被归一化。
2. `regex` 是 basic.py 的硬依赖（whisper/normalizers/basic.py:74 的 `\X` 字素匹配标准 re 不支持），却**未列入 pyproject.toml:26-34 依赖**——靠 tiktoken 等包间接带入才未爆雷，属依赖声明缺失。
3. EnglishNumberNormalizer 的 following_prefixers 只有单数形式映射到 "dollars" 输出（whisper/normalizers/english.py:129-133 把 dollars 映为 "$" 前缀，输出 "23 $" 风格由 postprocess 兜底），词形覆盖是枚举式的、并不完备——极端俚语数字读法（"a couple of"）不在其内，评测前先跑一遍测试集抽样。
