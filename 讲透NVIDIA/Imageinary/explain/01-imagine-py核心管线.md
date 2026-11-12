# 01 · imagine.py 核心管线

## 角色定位

imagine/imagine.py（567 行）是全库**唯一实现文件**：三个公开 API 与 CLI 入口 `_main`（imagine/imagine.py:550）全在此，`imagine/__init__.py:1-4` 只是转出四行 barrel。无类无状态，11 个模块级函数按"参数解析→目录卫生→并行生成→报告"分层，常量表在 imagine/imagine.py:39-43。

## 内部结构

- **CLI 层**：`_parse_args`（imagine/imagine.py:46-106）构建三子命令：record 类两命令共享父解析器（imagine/imagine.py:70-84），source/dest/name 位置参数+`--img-per-file`（imagine/imagine.py:80）；create-images 独有 path/name/image_format 位置参数（imagine/imagine.py:89-94）加 `--width/--count/--seed/--size` 等选项（imagine/imagine.py:95-105）。
- **目录卫生**：`_try_create_directory`（imagine/imagine.py:109-122）是 `os.makedirs(exist_ok=True)` 幂等包装；`_check_directory_exists`（imagine/imagine.py:125-143）对缺失源目录抛 RuntimeError。
- **生成层**：`create_images`（imagine/imagine.py:146-222）编排、`_image_creation`（imagine/imagine.py:507-547）单图 worker。
- **辅助层**：`_record_slice`（imagine/imagine.py:225-278）切片生成器、`_print_image_information`（imagine/imagine.py:430-456）大小报告。

## 外部连接

上游消费 numpy 随机数组与 PIL 编解码，`Pool`（imagine/imagine.py:203）提供进程并行。`_main` 被 setup.py:26-28 的 `console_scripts` 注册为 `imagine` 命令；`create_images` 是 functional 测试的造图引擎（如 tests/functional/test_recordio.py:38）；三个私有函数被 tests/unit/test_units.py:19 的 TestUnits 白盒直测。

## 数据流

`_main` 分发（imagine/imagine.py:557-566）→ `create_images` 建目录后 `Pool()`+`starmap(_image_creation, ...)`，按 `chunksize`（默认 64，imagine/imagine.py:155）分块派发（imagine/imagine.py:209）→ 进程内 `_image_creation`：`numpy.random.seed(seed+n)`（imagine/imagine.py:539）保证第 n 张图可复现 → `rand(height,width,3)*255`（imagine/imagine.py:540）→ `Image.fromarray` 后 jpg 走 `convert('RGB')`、png/bmp 走 `convert('RGBA')`（imagine/imagine.py:542-545）→ 按 `前缀+序号.扩展名` 落盘。`finally` 里 close/join 收池；`--size` 开启时调 `_print_image_information`（imagine/imagine.py:219），遍历目录累加字节、以首个文件当首图近似均值（imagine/imagine.py:446-453）。`_record_slice` 是 RecordIO 侧前置：按 `images_per_file` 步进逐段 yield (source,dest,name,子列表,序号) 五元组（imagine/imagine.py:272-278）喂并行 worker。

## 设计决策

1. **无类纯函数式**：一次性生成无需状态对象，签名即契约。
2. **seed+n 而非全局 seed 一次**（imagine/imagine.py:539）：每图独立播种，任何一张可单独重放，并行结果与调度无关。
3. **starmap+chunksize**：imagine/imagine.py:206-208 注释明言内存受限系统会 stall，唯一旋钮是 chunksize。
4. **jpg→RGB、其余→RGBA 分叉**（imagine/imagine.py:542-545）：JPEG 无 alpha 通道，强制 RGB 避免保存报错。
5. **参数用位置而非选项**：README.md:96-105 的 `--path` 示例与代码（位置参数，imagine/imagine.py:89-94）不符，照抄报错。
6. **已知笔误**：imagine/imagine.py:67 把文案当 `prog` 传（应为 description），usage 被污染但退出码 0。

## 新人提示

先跑 `imagine create-images /tmp/t t_ jpg --count 3 --size` 看输出，再按 `_main`(imagine/imagine.py:550)→`_parse_args`(46)→`create_images`(146)→`_image_creation`(507) 通读，一小时可读完。三坑：CLI 参数是位置式（README 示例跑不通）；RecordIO/TFRecord 分支见 02 篇；改私有函数名会打断白盒单测（tests/unit/test_units.py 直调）。