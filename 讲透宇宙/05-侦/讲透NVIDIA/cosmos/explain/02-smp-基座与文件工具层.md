# 02 · smp 基座：文件缓存、图像编解码与运行时工具层

## 一、角色定位

`vlmeval/smp/` 是整个评测栈的"标准库垫层"——fork 里仅四个文件（`__init__.py` 共 4 行 star-import，smp/__init__.py:1-4）：`file.py`（540 行，序列化/下载/数据根/复用管理）、`misc.py`（287 行，环境变量、分布式工具、时间戳）、`vlm.py`（201 行，**名字有误导性：与模型加载无关**，是图像 base64 编解码与 API 探活）、`log.py`（123 行，统一 logger）。全仓 `from vlmeval.smp import ...` 的导入点数以百计：run.py 的入口、dataset 的落盘、wrapper 的编码全都走这里。它把"数据放哪（LMUData 根目录）、怎么存（tsv/json/pkl 多格式）、怎么断点续跑（reuse）"三件横切事务收敛成一处，让 190+ 数据集类和 100+ 模型 wrapper 不必各自实现 IO。

## 二、内部结构

**file.py 三大件**：

- *数据根*：`LMUDataRoot()`（file.py:71-77）= 环境变量 `LMUData` 或 `~/LMUData`，是所有数据集 TSV、解码图片、缓存文件的唯一根；`HFCacheRoot()`（file.py:80-91）按 `HF_HUB_CACHE > HUGGINGFACE_HUB_CACHE > HF_HOME > ~/.cache/huggingface/hub` 顺序探测，并处理了"值是否已带 hub 后缀"两种写法（file.py:84-87）。
- *多格式 load/dump*：`load(f)`（file.py:238-275）按扩展名分派 pkl/json/jsonl/xlsx/csv/tsv 六种；**入参是 URL 时自动下载到 `LMUData/files/` 再读**（file.py:263-267）。`dump(data, f)`（file.py:139-173）对偶，带两个防御：`NumpyEncoder`（file.py:119-135）处理 numpy 标量/数组/复数的 JSON 序列化；**写失败静默降级为 pkl**（file.py:168-172），这救了超长单元格，也可能掩盖权限错误。
- *复用管理*：`prepare_reuse_files`（file.py:487-540）是 `--reuse` 的实现核心——不设 reuse 时把历史预测移入 `bak_` 备份目录（file.py:493-505）；设了则倒序遍历历史 `eval_id` 目录找同 `{model}_{dataset}.` 文件拷回（file.py:517-527），并按 `--reuse-aux` 决定辅助判分文件（`*openai*/*csv/*json/*pkl/*gpt*`）是删是留（file.py:529-535）。

另有：`get_pred_file_format()`（file.py:175-181）默认 tsv，注释点名 xlsx 单元格 32767 字符上限会**静默截断**长预测——这是默认值从 xlsx 改 tsv 的原因（PRED_FORMAT 环境变量可改）；`parse_file`（file.py:381-418）把任意字符串归类为本地文件（mime, path）/base64 data URL（落盘为 `md5(b64).png` 再递归）/URL（下载）/纯文本四态，是消息预处理的地基；`ls`（file.py:312-347）带 `!` 前缀排除语法（file.py:333-336）和层级展开。

**misc.py**：`get_cache_path`（misc.py:71-94）是 HF 数据集缓存定位器——用 `huggingface_hub` 内部 API `_scan_cached_repo` 找 `{repo_type}--{org}--{name}` 下指定 branch 的最新 snapshot，ModelScope 分支由 `VLMEVALKIT_USE_MODELSCOPE` 开关（misc.py:14-15）；`load_env`（misc.py:204-228）读仓库根 `.env` 注入 API key（run.py:550 就是它）；`githash`（misc.py:166-182）在 vlmeval 安装目录跑 `git rev-parse`，供 eval_id 使用；`proxy_set/listinstr/timestr/version_cmp/toliststr/extract_json_objects/get_gpu_memory`（misc.py:97-287）是被全仓复用的小工具，`toliststr`（misc.py:253-260）把 tsv 单元格里的 `"['a','b']"` 字符串安全还原成列表。

**vlm.py**：`encode_image_to_base64`（vlm.py:96-136）是编码热点——RGBA/P 调色板先转 RGB（vlm.py:99-100）；`VLMEVAL_MIN_IMAGE_EDGE`（默认 100px）触发的**小图上采样**（vlm.py:112-118）与 `VLMEVAL_MAX_IMAGE_SIZE`（默认 1e9 字符）触发的 0.7 倍缩圈迭代（vlm.py:121-127）都在控制 base64 体积。`concat_images_vlmeval`（vlm.py:23-51）多图横/竖拼接送非交错模型（存 `/tmp/md5.jpg` 去重）；`apiok`（vlm.py:199-201）发一句 "Hello!" 判 `fail_msg` 是否在回复里，是 API wrapper 的标准探活。

**log.py**：`setup_logger`（log.py:9-59）建名为 `vlmeval` 的根 logger（console+file 双 handler，propagate=False），`get_logger`（log.py:62-88）给子模块挂 NullHandler 兜底，`setup_subprocess_logger`（log.py:91-123）给多进程 worker 重定向独立日志文件。

## 三、外部连接

向上：run.py、三条 inference 管线、dataset 全家、vlm/api wrapper 全部 import smp（如 image_base.py:9-10 一口气引 10 个函数）。向侧：`huggingface_hub._cache_manager._scan_cached_repo`（misc.py:10）与 `PIL/sty/validators/tqdm` 等轻依赖；`download_file`（file.py:277-309）失败且 URL 含 huggingface.co 时自动换 **hf-mirror.com** 镜像重试（file.py:298-301），是国内网络适配的显式痕迹。`image_base.prepare_tsv` 的 >1GB 本地化经 `vlmeval.tools.LOCALIZE`（file.py 引用自 image_base.py:124-125）回调，形成 smp↔tools 的反向依赖。

## 四、数据流

以一个数据集首次构建为例：`ImageBaseDataset.__init__` → `prepare_tsv(url, md5)`（image_base.py:92）→ `download_file` 拉远端 TSV（失败走 hf-mirror）→ md5 校验（file.py:362-370 分块读文件或哈希字符串）→ 超过 1GB 触发 LOCALIZE 生成 `_local.tsv`（image_base.py:121-126）→ `load` 解析为 DataFrame。推理时图片列若是 base64，`dump_image` 调 `decode_base64_to_image_file`（vlm.py:160-165）写 `LMUData/images/{dataset}/`；wrapper 侧再按需 `encode_image_file_to_base64` 送模型。预测落盘走 `get_pred_file_path`（file.py:193-204）+ `dump`；判分中间文件名由 `get_intermediate_file_path`（file.py:465-484）按后缀语义选格式（`_tmp/_response/_processed`→pkl、`_rating/_config`→json、`_acc/_fine`→csv）。

## 五、设计决策

1. **LMUData 单根目录**：数据、图片、缓存、URL 下载物全部集中一处（file.py:71-77、264、395），换机器只需迁移一个目录+一个环境变量。
2. **多格式 duck-typing IO**：`load/dump` 按扩展名自分派（file.py:164-167、269-274），上层代码对存储格式零感知；dump 失败降级 pkl（file.py:168-172）是"先保住数据再谈格式"的取舍。
3. **默认 tsv 而非 xlsx**（file.py:178 注释）：32767 字符上限的静默截断对长 CoT 预测是致命伤，fork 已把默认改正，但 `use_env_format=False` 的旧路径仍返回 xlsx（file.py:202-204），历史行为未清除。
4. **图像体积双阈值**（vlm.py:107-127）：下限防过小图信息丢失、上限防 base64 撑爆 payload，且用迭代缩放而非一次到位，保住长宽比。
5. **日志三件套**：进程内根 logger + 子模块命名空间 + 子进程重定向，多进程评测（mp.Pool 16/32 并发）的日志不互相踩踏。

## 六、新人提示（坑/勘误）

- **`vlmeval/smp/vlm.py` 不是"VLM 模型加载器"**：上游同位置文件曾有模型自动加载逻辑，这个 fork 里只剩图像编解码+探活（全文件 201 行无一处理模型）。按图索骥找"模型注册表"请去 `vlmeval/config.py`（supported_VLM 在 config.py:2640-2663 聚合）。
- **dump 降级 pkl 会改变文件名**（file.py:170-171）：下游按 `{name}.csv` 硬编码找文件会扑空，凡写失败要查同目录 `.pkl`。
- **`mp.Pool(32)` 硬编码**（file.py:62，localize_df）：容器 CPU 配额低于 32 时会 oversubscribe，图片解码阶段偶发卡顿先查这里；参数 `nproc=32` 形同虚设（ConcatDataset 传 nproc=16 也不生效，dataset/__init__.py:258）。
- **fork 修改留有中文注释**：file.py:144"处理 DataFrame 对象"、file.py:386/404"添加对webp的支持"（file.py:431-435 的 parquet_to_tsv 同期新增）——中文注释是 NVIDIA 内部改动的指纹，读 diff 时可据此定位 fork 增量。
- **`toliststr` 用 `eval`**（misc.py:255）：仅适合受信任的 tsv 内容，任何人能改数据集文件就等于能执行代码，二次分发评测数据时须意识到这点。
- **reuse 的辅助文件清理是 `os.system('rm -rf ...')`**（file.py:531-535）：通配符拼接路径，模型/数据集名里含特殊字符时有命令注入面（评测场景低危，但写 CI 时别原样照抄）。
