# 10 · `src/torchio/cli.py`：CLI——tyro 驱动的终端工具集

## 一、角色定位

`cli.py` 把库能力暴露给终端：装好包即得 `torchio` 命令（入口 `pyproject.toml:62` 的 `torchio = "torchio.cli:main"`），不写 Python 也能查看、绘制、动画、转换、变换影像。技术选型是 **tyro**（`cli.py:14`）——基于 dataclass 声明的参数解析器，每个子命令是一个带类型注解与 docstring 的 dataclass，`run()` 方法即执行体。这让 268 行的文件同时是 CLI 实现、`--help` 文档与类型化配置三合一。ONBOARDING 第 6 节只列了 Plot/Animate/Info/Convert 四个子命令，**实际有六个**：还有 Transform（`cli.py:134`）与 Cache（:204，内含 Dir/Clean 两个嵌套子命令）——图谱摘要"ls/plot/animate/convert/transform 等"反而更接近事实，这是对 ONBOARDING 的增量勘误。

## 二、内部结构

**六个子命令 dataclass**（每个字段的 docstring 就是 help 文案，`Annotated[Path, tyro.conf.Positional]` 声明位置参数）：

| 命令 | 行号 | 职责 |
|---|---|---|
| `Plot` | `cli.py:25` | 三正交切面绘图：`ScalarImage(path)` 后 `image.plot(...)`（:40-48），支持 channel/indices/output |
| `Animate` | `cli.py:52` | 切层扫描动画：按输出后缀分派 `.gif`/`.mp4`（:78-94），非法后缀 exit 1（:91-94） |
| `Info` | `cli.py:99` | 打印 `repr(image)`（:105-107）——即 02 篇的多行元数据卡片 |
| `Convert` | `cli.py:111` | 格式转换：`.nii.zarr` 走专用分支（:127-128），其余 `image.save(output)`（:130） |
| `Transform` | `cli.py:134` | **任意变换施加**：类名查注册表（:162-163 `_get_transform_class`），`key=value` 尾参解析（:164 `_parse_kwargs`），支持 `--device`（:154） |
| `Cache(Dir|Clean)` | `cli.py:204`（Dir :172、Clean :180） | 缓存管理：打印/清除数据集缓存（`get_torchio_cache_dir`，Clean 可按名清 :186-200） |

**辅助函数**：`_get_transform_class`（:221-230）从 `_TRANSFORM_REGISTRY`（`transforms/transform.py:47`）按名查类，未知名打印全部可用名后退出（:226-229）——注册表（06 篇 `__init_subclass__` 自动登记）在这里兑现价值。`_parse_kwargs`（:233-242）拆 `key=value`，`_parse_value`（:245-250）用 `ast.literal_eval` 推类型（int/float/bool/tuple 都能传，解析失败回落字符串）。

**入口**：`main`（:258-264）先拦截 `--version`（:260-262）再 `tyro.cli(Command)`（:263）——`Command` Union（:213，注释注明 tyro 需要 Union 而非 `|`）驱动子命令树；Cache 的 `tyro.conf.OmitSubcommandPrefixes`（:207）让 `torchio cache dir` 免写 `cache-dir`。

## 三、外部连接

- **上游**：`torchio` 门面（:16，六个命令全用 `tio.ScalarImage`/`tio.__version__`）；`download.get_torchio_cache_dir`（:17，缓存路径）；`_TRANSFORM_REGISTRY`（:223 延迟导入避免环）。
- **下游**：`pyproject.toml:62` 脚本入口；`.github/workflows/tests.yml` 有 CLI 冒烟步骤（图谱 in 边）；`tests/test_cli.py` 单测；`docs/reference/cli.md` 与 `docs/how-to/visualization.md` 文档页。
- **能力借力**：Plot 依赖 `[plot]` extra（matplotlib），Animate 依赖 Pillow/ffmpeg——不在 CLI 层检查，缺依赖时在 visualization 层报 ImportError 并提示 pip extra（`external/imports.py` 的友好报错模式）。

## 四、数据流

`torchio transform brain.nii.gz noisy.nii.gz Noise std=0.1 --device cuda:0` 走读：

1. `tyro.cli(Command)`（:263）按 Union 分派到 `Transform` dataclass，位置参数 input/output/name 各就各位，`args` 收集尾部 `std=0.1`。
2. `run()`（:162）：`_get_transform_class("Noise")`（:221）查注册表得类；`_parse_kwargs(["std=0.1"])`（:233）→ `ast.literal_eval("0.1")` 得 float 0.1（:248）。
3. `transform = transform_cls(std=0.1)`（:165）→ `ScalarImage(input).to(device)`（:166）。
4. `transform(image)`（:167）走 06 篇 forward 主流程（Tensor 输入被 `_wrap_scalar_input` 包成单元素批）。
5. `result.save(output)`（:168）落盘。

Convert 的分叉在 :126-130：后缀 `.nii.zarr` 走 `image.to_nifti_zarr(...)`（:128）——见下节批判。

## 五、设计决策（含批判）

**dataclass-as-command** 是现代 Python CLI 的优雅范式：字段类型即参数语法、docstring 即帮助文本、无手写 argparse 样板。tyro 选型还顺带解决了 nested subcommand（Cache）与 Union 分派的声明式表达。Transform 子命令把注册表当插件总线，任何用户注册的自定义变换类（06 篇 `__init_subclass__`）立即可从命令行调用——CLI 与库天然同构。

批判四点。其一，**`Convert` 转 zarr 是一个实打实的运行时炸弹**：`cli.py:128` 调用 `image.to_nifti_zarr(self.output)`，但 `Image` 类**没有这个方法**（全仓 grep 唯一引用就是该调用点本身；真正的实现是私有 `_save_nii_zarr`，`image.py:744`，且 `Image.save` 在 `image.py:718` 已经对 `.nii.zarr` 后缀自动分派）。也就是说 `torchio convert a.nii.gz b.nii.zarr` 必抛 AttributeError——应为 `image.save(self.output)` 一行即可（save 的后缀分派本就覆盖此场景）。v2 alpha 的典型疏漏，也是新人可认领的修复点。其二，`Transform` 对 `p`/`include` 等 kwargs 与数据参数同名冲突无校验，`Noise p=0.5` 会静默变成概率参数而非报错——恰好语义合理纯属侥幸。其三，六个 dataclass 的 `run()` 都不捕获异常，nibabel/SimpleITK 的底层报错直接砸向终端，对非 Python 用户不友好。其四，`--version` 用 argv 手工拦截（:260-262）而非 tyro 声明，是绕过解析器的实用主义小补丁，升级 tyro 大版本时记得回归。

## 六、新人提示

1. 装完先跑三连建立体感：`torchio info t1.nii.gz`（元数据卡片）、`torchio plot t1.nii.gz --output slice.png`、`torchio cache dir`。
2. Transform 尾参是 Python 字面量语法：tuple 要写 `axes=(0,1,2)`，bool 写 `True/False`（`ast.literal_eval` 口径，:245-250），写 `--axes 0 1 2` 会失败。
3. 查可用变换名最快方式是故意写错：`_get_transform_class` 会打印注册表全名单（:226-229）。
4. 修 `to_nifti_zarr` bug（:128）是理想的第一个 PR：一行改动 + 在 `tests/test_cli.py` 补一个 zarr 转换用例（注意 zarr 是可选 extra，测试需跳过无 zarr 环境）。
5. 二次开发参考：新增子命令 = 写 dataclass + `run()` + 把它加进 `Command` Union（:213）三步，tyro 自动生成 help；`Convert` 的教训是 run() 里调用的 API 必须先 grep 确认存在。
