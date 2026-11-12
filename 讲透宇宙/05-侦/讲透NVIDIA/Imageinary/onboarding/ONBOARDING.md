# Imageinary ONBOARDING

> NVIDIA/Imageinary @ aa44843 · v1.1.3 · 图谱 6 层/11 步 tour · 锚经源码核实

## ① 项目定位：为什么需要"随机图像数据集"

NVIDIA 2020 年开源（Apache 2.0）的**可复现大规模随机图像数据集生成器**：随机 numpy 数组 → 任意尺寸/数量的 JPEG/PNG/BMP，或再打包 MXNet RecordIO / TFRecord 训练格式，喂 DL benchmark 压测。

痛点在 README.md:6-12：公开数据集数量与分辨率双固定，压测却要各种输入尺寸；本工具一行命令生成 1000 张 4K JPG（README.md:96-105）。

两个关键定性：**不是 GAN/生成模型库**——图像是纯随机噪声（imagine/imagine.py:540），全库 0 个 network/model 类，imagine.py 仅 11 个模块级函数，价值在"尺寸/数量/格式可控+可复现"；**可复现靠 seed**——每图 `numpy.random.seed(seed+n)`（imagine/imagine.py:539），同参数重跑字节级一致。

## ② 技术栈

Python >= 3.7（setup.py:25）；核心运行依赖仅 numpy+Pillow（setup.py:29-32）。TensorFlow 双轨锁文件：requirements.txt:44 `tensorflow==2.7.0` 与 requirements.txt.tf1:32 `tensorflow==1.14.0`。MXNet 1.6.0（requirements.txt:22）供 RecordIO。分发走 nvidia-pyindex 私有 PyPI（README.md:45-52），包名 `nvidia-imageinary`。

## ③ 模块地图（图谱 6 层）

```
L1 元文档   README.md(16节) · CONTRIBUTING.md(DCO) · VERSION(1.1.3)
L2 依赖打包 requirements.txt(TF2) · requirements.txt.tf1(TF1.14) · setup.py
L3 核心库   imagine/__init__.py(4行barrel) → imagine/imagine.py(567行·11函数·唯一实现)
L4 单元测试 tests/unit/test_units.py · TestUnits 白盒
L5 功能测试 tests/functional/ 四格式黑盒（jpg/png/recordio/tfrecord）
L6 CI      .github/workflows/pushtest.yml 双 job
```

L3 是核心：imagine/__init__.py:1-4 四行 barrel 转出全部公开 API 与 `_main`，构成门面。L4 测纯逻辑，L5 测四格式端到端落盘，L6 双 job 是双轨回归保障。

## ④ 数据流：CLI 到落盘

**create-images**：`_main`（imagine/imagine.py:550-566）分发 → `_parse_args`（imagine/imagine.py:46-106）→ `create_images`（imagine/imagine.py:146-222）先 `_try_create_directory` 幂等建目录（imagine/imagine.py:109-122）→ `Pool()` 并行 `starmap`（imagine/imagine.py:209），按 `chunksize`（imagine/imagine.py:155）控内存 → worker `_image_creation`（imagine/imagine.py:507-547）：seed → 随机数组 → `Image.fromarray(...).convert('RGB'|'RGBA')`（imagine/imagine.py:543-545）→ 按序号落盘。可选 `--size` 触发 `_print_image_information`（imagine/imagine.py:430-456）打印首图与目录大小。

**RecordIO**：`create_recordio`（imagine/imagine.py:281-349）查 mxnet 哨兵（imagine/imagine.py:318-320）→ `_check_directory_exists` 校验源目录（imagine/imagine.py:125-143，缺则 RuntimeError）→ listdir 收集、`ceil` 算分片数（imagine/imagine.py:333）→ `_record_slice` 逐段 yield 五元组（imagine/imagine.py:225-278）→ 并行 worker `_recordio_creation`（imagine/imagine.py:459-504）：`MXIndexedRecordIO` 建 .idx/.rec 对逐图写入。

**TFRecord**：`create_tfrecords`（imagine/imagine.py:352-427）查 TF 哨兵（imagine/imagine.py:388-391）→ 单进程逐图读 bytes 组 `tf.train.Example`（imagine/imagine.py:416-419）→ 写满 `img_per_file` 滚动新文件（imagine/imagine.py:408-412）。输出**不带扩展名**（imagine/imagine.py:402）。

## ⑤ 构建与运行

先 `pip install nvidia-pyindex`（README.md:45-52），再选装 `nvidia-imageinary`（最小）/`['tfrecord']`/`['mxnet']`/`['all']`。装完得 `imagine` 命令——setup.py:26-28 以 `console_scripts` 注册 `imagine=imagine:_main`。建议 virtualenv；测试命令见 README.md:197-199。CLI 实际语法是**位置参数**（imagine/imagine.py:73-80/89-94）：

```bash
imagine create-images <保存路径> <前缀> jpg --width 3840 --count 1000 --size
```

## ⑥ 设计决策

1. **软依赖=try-import 置 None 哨兵**（imagine/imagine.py:21-24/28-36）：功能入口 `if not X: raise ImportError` 并提示 extras 安装命令（imagine/imagine.py:318-320/388-391）——不装框架核心功能可用。mxnet 三符号只置 IRHeader 当哨兵。
2. **TF1/TF2 双轨**：setup.py:10 extras 排掉坏版本，锁文件拆两份互斥环境；可行因只用两代共同 API（imagine/imagine.py:29-34）。
3. **extras 三分组**（setup.py:9-14）：`tfrecord`/`mxnet`+`all` 展平。
4. **无类纯函数式**：11 个模块级函数（公开 3+私有 8），工具型负载最直白。
5. **Pool 并行+chunksize 防爆内存**：imagine/imagine.py:206-208 注释明言大数量+小内存会 stall，解法调大 chunksize。
6. **测试白盒/黑盒分层**：unit 直测私有函数守实现细节，functional 只经门面验证落盘守对外契约。
7. **argparse 子命令复用**：record 类两命令共享父解析器（imagine/imagine.py:70-84）。

## ⑦ 已知坑与勘误

1. **不是 GAN 库**（甄别钉版）：图像=纯随机噪声，0 个 network/model 类。
2. **README RecordIO 段复制粘贴错误**：README.md:145-147 在 RecordIO 一节写"creates TFRecords"，主语应为 RecordIO。
3. **README CLI 示例跑不通**：README.md:96-105 用 `--path/--name` 选项式写法，代码是位置参数（imagine/imagine.py:73-80/89-94），照抄报错。
4. **chunksize 未暴露给 CLI**：README.md:114-116 让用户调 `--chunksize`，`_parse_args` 无此选项，仅 Python API 参数（imagine/imagine.py:155）。
5. **ArgumentParser 形参误用**：imagine/imagine.py:67 把文案当 `prog` 传（应为 description），`--help` usage 被污染但 exit 0，CI 冒烟不报。
6. **TFRecord 输出无扩展名**：imagine/imagine.py:402 不拼 `.tfrecord`；测试只断言 `'tmprecord_0'`（tests/functional/test_tfrecord.py:58），图谱摘要不准。
7. **文件名必须含数字**：`_recordio_creation` 用 `regex.findall(image_name)[0]` 提序号（imagine/imagine.py:498），混入无数字文件名直接 IndexError。
8. **"首图"非排序第一**：`_print_image_information` 按 listdir 顺序取首个文件（imagine/imagine.py:446-453）。
9. **NoReturn 注解误用**：`create_images` 等正常返回 None 却标 NoReturn（imagine/imagine.py:146/109），笔误不影响运行。
10. **VERSION 被 setup.py 消费**（setup.py:6-7）——改版本改文件而非 setup.py。
11. **unit 测试是白盒**：tests/unit/test_units.py:19 的 TestUnits 跨过门面直调私有函数（甄别钉版），改名会打断它。
12. **CI 双 job 触发全部 5 个测试文件**：test_tf2（pushtest.yml:6）与 test_tf1（pushtest.yml:44）各装一份锁文件、跑同一 pytest 命令（pushtest.yml:26/64）。另：requirements.txt 曾被误标 docs/txt 已纠正。

## ⑧ 新人上手路径

1. 读 README.md:6-12 理解价值四控（尺寸/数量/格式/可复现）。
2. 装：virtualenv + `pip install nvidia-pyindex` + 最小安装（无需 TF/MXNet）。
3. 跑通 `imagine create-images /tmp/imgs t_ jpg --count 10 --size`（位置参数！），看 `t_0..t_9.jpg`。
4. 顺序读码（567 行一小时）：imagine/__init__.py:1-4 → `_main`(imagine/imagine.py:550) → `_parse_args`(46) → `create_images`(146) → `_image_creation`(507) → `_record_slice`(225) → 两 record 函数(281/352)。
5. 测试：先 `pytest tests/unit`（秒级），再跑 functional 四件套。
6. 进阶：造 100 图 → record 打包，对照 tests/functional/test_recordio.py:57（断言 .rec+.idx 恰 2 文件）与 test_tfrecord.py:57。
7. 首个贡献需 DCO sign-off（CONTRIBUTING.md，`git commit -s`）；练手：修⑦-2/3/4 的 README 勘误，或给 `_print_image_information` 加排序。