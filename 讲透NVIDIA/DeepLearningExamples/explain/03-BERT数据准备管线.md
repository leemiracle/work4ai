# 03 BERT 数据准备管线

## 角色定位

`PyTorch/LanguageModeling/BERT/data/` 是把 BooksCorpus + Wikipedia 原始语料加工成 LDDL/HDF5 预训练特征的全套产线，图谱第 4 层"BERT 预训练数据管线"（tour step-04）。`bertPrep.py`（363 行）是总入口 CLI，`Downloader.py` 是下载门面，各 `*Downloader.py` 分管一类数据源，`*TextFormatting.py` 与 `TextSharding.py` 负责格式归一与分片，最后由仓根的 `create_pretraining_data.py` 完成 NSP/掩码特征化。这条产线是"容器内运行假设"最重的一组代码——多个环节硬编码 `/workspace/...` 容器路径，离开 NGC 容器即断。它也是全仓"assert False 死分支"最密集的地方，读它要带着"哪些路真的通"的地图。

## 内部结构

**bertPrep.py**：L28 `os.environ['BERT_PREP_WORKING_DIR']` 定工作根；L38-46 的 `directory_structure` 字典定义六级产线目录——download（原始下载）→ extracted（wikiextractor 解出）→ formatted（每篇文章一行，所有源在此归一）→ sharded（分片）→ tfrecord/hdf5（特征化产物，目录名内嵌 lower_case/seq_len/max_pred/masked_lm_prob/seed/dupe_factor 六参数，L35-37 拼接）。`--action`（L227）× `--dataset`（L240）二维驱动五阶段。L132-133 构造 NLTKSegmenter 与 Sharding 完成分片；L188 起的 `create_record_worker` 以 `subprocess.Popen` 并发调用**容器内绝对路径** `python /workspace/bert/create_pretraining_data.py`（L189），按 shard_id%n_processes 节流开进程。

**死分支群（源码钉版）**：L92 wikicorpus_zh 入口 `assert False`（中文语料需分词翻译，未支持）；L141 不认识的 dataset 做 sharding 时 `assert False`；L144 `create_tfrecord_files` 整个动作 `assert False, 'TFrecord creation not supported in this PyTorch model example release'`——其后 WikiExtractor 命令构造与 tfrecord 版 worker（L149）全是死代码。加上 NVIDIAPretrainedWeightDownloader.py:27 的 `assert False, 'not implemented yet'`，四处断头。

**Downloader.py**：L22 门面类，L29-50 按 dataset_name 分派 bookscorpus/wikicorpus_en/wikicorpus_zh/google_pretrained_weights/nvidia_pretrained_weights/{mrpc,sst-2}/squad/all 六路。

**TextSharding.py**（327 行，算法最重）：L20 Sharding 类、L61 `segment_articles_into_sentences`、L138 `get_sentences_per_shard`；装箱目标是把句子按中位数均衡分配到 n_training_shards+n_test_shards（L227/L247 的训练/测试双侧装箱循环）。

## 外部连接

- **BooksDownloader**：shell 调容器内 `/workspace/bookcorpus/download_files.py` 按 url_list.jsonl 拉书——仓外依赖。
- **GLUEDownloader**：先 wget 拉取 Google 工程师 **gist 上的 download_glue_data.py**（仓内不存在，运行时第三方脚本），再 sys.path 注入动态 import 调其 main()——典型的运行时依赖注入，也是供应链审计要点。
- **SquadDownloader**：L14 `import bz2` 是死导入（下载物均为 json/py，无解压路径）；URL 直写构造器字典。
- **WikiDownloader**：L17/L19 **重复两次 `import subprocess`**；wget 非零返回抛 RuntimeError，下载后强制 `bzip2 -dk` 解压。
- **GooglePretrainedWeightDownloader**：内置 7 种模型（base/large × uncased/cased/多语/中文）GCS URL 与逐文件 SHA256 表；哈希用 `bytearray(128*1024)+memoryview+readinto` 流式分块避免整文件载入——本目录工程质量最高的一段；但 serialize/deserialize/listLocallyStoredWeights 三个方法是 pass 空壳。
- **create_pretraining_data.py**（仓根）：L24 `import h5py`、L136 `h5py.File(output_file,'w')` 输出；docstring 仍写 TF examples——Google TF 版脚本移植痕迹。
- 消费端：run_pretraining.py:557 的 LDDL dataloader 吃 hdf5 目录；本目录不 import 任何训练侧模块，单向被消费。

## 数据流

以英文预训练为例的完整链路：

1. **download**：BooksDownloader 拉 BookCorpus、WikiDownloader 拉 wikicorpus_en 的 bz2 并解压成 XML；
2. **extracted**：WikiExtractor（bertPrep 死分支内的命令模板遗留了它的调用方式）从 XML 剥出正文；Books 侧 .txt 已是纯文本；
3. **formatted**：BookscorpusTextFormatting.py（utf-8-sig 剥 BOM、空格连行、双换行分书）与 WikicorpusTextFormatting.py（以 `<doc id=/>` 标签为状态机边界、跳过首行标题、正文压成一行）各自产出"一篇文章一行"的归一语料；
4. **sharded**：TextSharding 用 NLTK 分句后按句数装箱，输出 n_train+n_test 个 `.txt` 分片；
5. **hdf5**：bertPrep 的 worker 并发调 create_pretraining_data.py 做词元化、80/10/10 掩码、NSP 句对构造，落 HDF5 分片；
6. 交给 run_pretraining 的 LDDL 管线（见第 02 篇）。

`BERT_PREP_WORKING_DIR` 是贯穿六级的唯一根变量——所有目录都从它推导，迁移机器只需改这一个环境变量（前提是你把容器路径也一并解决）。

## 设计决策

1. **目录即状态机**：六级目录名直接编码了产线进度与关键参数（hdf5 目录名内嵌六个特征化参数），断点续跑与产物辨识靠"看目录名"完成——朴素但有效，也让 tfrecord 与 hdf5 两种历史口径共存时不会串档。
2. **文本归一层（formatted）是解耦关键**：Book/Wiki 两种异构源在"一篇文章一行"处汇合，Sharding 与特征化只认这一种形态——新增语料源只需实现一个 Formatter。
3. **多进程框架写了但没用**：TextSharding.py:69 `use_multiprocessing = 'serial'` 硬编码，L76 的 manager 分支与 L105 的 queue 分支（后者还是空壳 for+pass）为死代码——"TODO: WIP"注释（L68）自曝了未完成状态；串行装箱对 BooksCorpus 级语料是性能瓶颈但可接受。
4. **诚实的 assert False 优于半成品**：中文路径与 tfrecord 明确断死，比静默产出错误格式好；但 `all` 下载链路会撞上 nvidia_pretrained_weights 的断头（Downloader.py:50 的 all 分支终会调到 NVIDIAPretrainedWeightDownloader.py:27），这是门面没对齐子组件的疏漏。

## 新人提示

- **import TextSharding 即联网**：L317-319 在模块中部执行 `import nltk` + `nltk.download('punkt')`——不是函数内延迟下载，是 import 副作用。离线环境 import 就会炸，先 `pip install nltk` 并预置 punkt 数据。
- **NLTKSegmenter 构造器笔误**：L322 写的是 `__init`（少一个下划线），永不作为构造器执行；好在 L325 `segment_string` 直接调 `nltk.tokenize.sent_tokenize`，实例化时走 object 默认构造、功能不受影响——但如果有人给构造器加参数就会踩坑。
- **`is 0` 语法地雷**：L63/66/124/125/227/247 用 `is 0`/`is not 0` 比较小整数，CPython 小整数缓存下碰巧能跑，Py3.8+ 报 SyntaxWarning，未来版本随时升级为错误。
- 重跑产线前检查 `directory_structure` 各级目录是否已有旧产物——Sharding 的 L124/125 断言会在二次调用构造器时报错，这是防重入设计而非 bug。
- 想要 GLUE/SQuAD 数据直接跑 SquadDownloader 更稳；GLUEDownloader 依赖 gist 脚本， gist 失效是真实风险。
