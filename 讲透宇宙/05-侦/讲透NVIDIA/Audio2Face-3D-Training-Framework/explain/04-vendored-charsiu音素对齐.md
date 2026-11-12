# 04 vendored charsiu：音素对齐库与本仓的唯一消费面

## 角色定位

`audio2face/deps/charsiu/` 是整树 vendored 的第三方音素对齐库（上游 researchoffice/charsiu，arXiv 2110.03876，README.md 保留在 deps/charsiu/README.md）。它把 wav2vec2 改造成帧分类器，实现"音频→逐帧音素"的预测对齐。本仓面部动画训练需要音素通道（唇形对齐的强先验），因此把它连根搬进来而非 pip 安装——代价与收益都很明确：可控可改（见下文两处定制），但要自己维护。

## 内部结构

对齐器家族 6 个（`Charsiu.py`）：基类 `charsiu_aligner`（L41）装载语言预处理器与识别器、定义 align/serve 接口与 TextGrid/TSV 输出（L72/L89）；五个子类各占一段——`charsiu_forced_aligner`（L109，CTC 强制对齐带静音合并 L213/L226）、`charsiu_attention_aligner`（L241）、`charsiu_chain_attention_aligner`（L327）、`charsiu_chain_forced_aligner`（L407，链式先 ASR 再对齐）、`charsiu_predictive_aligner`（L485，**纯声学直出**，不需文本）。

预处理器三级链（`processors.py`）：基类 `CharsiuPreprocessor`（L49）定义音素表映射（L59 mapping_phone2id）与音频预处理（L94）；`CharsiuPreprocessor_en`（L130）实现英文 ARPabet 音素化与词对齐（L143/L216/L248）；`CharsiuPreprocessor_zh`（L279）**直接继承 en 而非基类**（NOTES-DIGEST batch-5 实证），构造时换拼音 tokenizer（L281-285）、定义 21 声母表（L293-295）与 j/q/x 的 ü 化变换表（L297-311），音节拆分在 `_separate_syllable`（L452）。模型侧（`models.py`，658 行）：`Wav2Vec2ForFrameClassification`（L405，wav2vec2+帧分类头，predictive 用）、`Wav2Vec2ForAttentionAlignment`（L151，对齐头）、`ForwardSumLoss`（L39）、`Wav2Vec2ForCTCAndPretraining`（L456）等 8 类。后处理（`utils.py`）：`ctc2duration`/`seq2duration`（L35/L71）把逐帧标签折叠为 (start,end,phone) 时长段、`duration2textgrid`/`word2textgrid`（L98/L124）出 TextGrid。

## 外部连接

**本仓唯一消费入口是 `charsiu_predictive_aligner`**（NOTES-DIGEST batch-5 钉版）：`phoneme.py:68` 在 `PhonemeDetector.__init__` 里延迟 import（先 L84 `prepare_for_charsiu_import` 抑制 transformers 警告、重定向 HF 缓存），按 `CHARSIU_LANG_MAP`（phoneme.py:24-27，en→`en_w2v2_fc_10ms`、zh→`zh_xlsr_fc_10ms`）为每种语言建一个实例（L75）。其余 5 个 aligner 是上游功能全集，在本仓**零调用**——读代码时可整体跳过。

## 数据流

调用链：`PhonemeDetector.gen_phonemes`（phoneme.py:100）→ `align_probs(audio_fpath)`（Charsiu.py:527-533）→ `audio_preprocess` 重采样 16kHz → wav2vec2 帧分类 logits → **softmax(logits/temperature)** 返回 [帧, 词表] 概率矩阵（非 argmax 离散音素）→ 包装成 `Phonemes`（phoneme.py:31）以 100fps（CHARSIU_PHONEME_FPS=100，phoneme.py:22）语义持有 → 需要时 `resample`（L53）到网络帧率 → dataset 的 `PhonemeProvider`（dataset.py:117）按帧窗口切片喂网络。静音 token `[SIL]` 的 id 经 tokenizer 反查（phoneme.py:96-98）。

## 设计决策

- **predictive 而非 forced**：训练数据是表演捕捉的音频+动画，没有逐音素文本标注；forced/chain 家族需要转写文本，predictive 只凭声学直出，与无标注数据天然匹配。
- **本仓定制一：align_probs**（Charsiu.py:527）——上游 predictive aligner 只有 `align`（argmax 后折叠时长段）。本仓加了这个返回概率矩阵的方法，保留不确定性供训练端软监督（temperature 可调，phoneme.py:62 传入）。
- **本仓定制二：依赖瘦身**——zh 预处理器注释掉的 `self.g2p = G2pM()`（processors.py:286）与置空的 punctuation（L288）表明本仓砍掉了 nltk/g2p_en/g2pM 文本侧依赖，只留声学侧。
- **vendored 而非 fork**：上游仓库还在演进，本仓固化快照保证可复现，两处定制以最小 diff 形式留在树内。

## 新人提示

调语言支持只需扩 `CHARSIU_LANG_MAP`（phoneme.py:24）并确认 charsiu 有对应 10ms 帧分类模型卡；zh 模型走 XLSR 底座与 en 的 wav2vec2 底座不同，词表大小也不同（`num_phonemes` 按语言记录于 phoneme.py:76-77）。音素通道整体是可选件：dataset/回归网络侧 `num_phonemes=None` 即全链关闭（conv_w2v_autocorr.py:43-44）。排查对齐质量时先看 temperature——它直接控制概率分布的尖锐度。
