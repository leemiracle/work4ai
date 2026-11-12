# 讲透 NVIDIA/3DObjectReconstruction

> NVIDIA 3D 物体重建研究仓（立体视频→3D 资产管线：SAM2 分割 → FoundationStereo 深度 → Theseus 位姿优化 → NVBundleSDF TSDF 重建 → USD/USDZ 导出；宣称 30 分钟产照片级网格）。
> 本目录=understand 全链知识库产物（2026-11-06，kylin-fusion-search 会话，NV 舰队 v3.1 全量队列第 6 仓）。

## 全链状态表

| 阶段 | 状态 | 关键数据 |
|---|---|---|
| prepare | ✅ 2026-11-05 | 52 文件（28 代码）/ 8 批 / scanner 32 条 import 边 |
| 批分析 | ✅ 8/8 | 187n/351e；imports AST 全量重扫 31/31 对账零差异；notebook 手扫补 6 条（scanner 全漏）；1308 团灭一次（批 1 死前落盘验收采纳，批 2-8 复活续跑零损失） |
| merge | ✅ | 187n/351e 输入=输出，零丢失零悬空 |
| layers/tour | ✅ | 13 层 53/53 全覆盖零重复；14 步导览零幽灵 id |
| finalize | ✅ | 双 validator 0 issues/0 warnings（内置+ua-inline-validate exit 0）；fingerprints 52 文件@e7aa98dc |
| ONBOARDING | ✅ | 11629 不计空格字符 / 8 节 / 81 锚（主会话独立抽验 8/8 命中） |
| explain | ✅ 6 篇（小仓从简档） | 2779-3990 字符/篇 / 合计 ~19.3K 字符 / 309 锚（worker 抽验 30=27 精确+3 区间起点合法；主会话独立实证甄别 3/3） |

图谱：仓内 `.understand-anything/knowledge-graph.json`（187n/351e/13 层/14 步 tour）。
产物目录：`onboarding/ONBOARDING.md` + `explain/01-06*.md`（六篇：nerf_runner 核心管线/感知组件/几何工具箱/USD 出口/配置字典/Dockerfile 编译栈）。

## 勘误清单（源码级实证，graph/文档 vs 源码以源码为准）

1. **包名漂移**：`src/README.md:14` 与包根 docstring 写 `nvidia.reconstruction3d.object.*`（不存在），实际 `nvidia.objectreconstruction.*`（pyproject packages 实证）。
2. **三版本号并存**：pyproject `0.2.0` / `cli/main.py:261` 硬编码 `0.1.0` / `__init__.py:27` `__version__="1.0.0"`；E2E 测试断言 0.1.0——与 pyproject 不同步。
3. **pdb 残留**：`networks/nerf_runner.py:1357` `use_mask=0` 分支残留 `pdb.set_trace()`，且未 import pdb——走到必 NameError。
4. **导入期 autocast 泄漏**：`sam2infer.py:70` 导入即 `torch.autocast("cuda", dtype=torch.bfloat16).__enter__()` 且无 `__exit__`——import 后全进程 CUDA 算术落在 bf16 autocast 上下文。
5. **TF32 进程级竞争**：`roma.py:216` 初始化 `set_float32_matmul_precision('highest')`（禁 TF32）vs `sam2infer` 全局开——CLI 调用顺序恰好"碰巧"正确，换调用序即翻车。
6. **lambda 键名分裂**：`tool.py:386-388` smooth_mesh 读 cfg 键 `'lambda'`，而 schema 字段名是 `lambda_`（`schema.py:303`）——dataclass 默认值路径永远取不到；且双份默认值不一致（schema 5/0.3 vs tool 内 2/0.5）。
7. **schema 未覆盖的运行期 KeyError**：FoundationStereo 的 `onnx_path/onnx_input_min/onnx_input_max` 三键（`foundationstereo_onnx.py:192,281,285`）不在 schema 树中——漏键运行期才爆。
8. **死代码**：`sam2infer segment_image_with_bbox` 预处理产出从未喂给 predictor（`:281-285`）。
9. **NeRFSmall 无 skip connection**：`skips=[4]`（`nerf_runner.py:1419`）是死变量；`netdepth/netwidth` 从未传入——网络硬编码 2 层 64 宽（`:1421`）。图谱 summary 原写 CUDA autograd Function，`SHEncoder` 实为纯 PyTorch（`:686-769`）——已钉正。
10. **schema 规模**：19 顶层 dataclass（含嵌套 23 个 @dataclass，导出 11 个）——非浅看的 12 类。
11. **双配置/双清单**：`tests/pytest.ini`（带 marker）与 pyproject `[tool.pytest.ini_options]`（更严）并存，pytest.ini 优先；scipy 双清单微差（pyproject 1.15.1 vs requirements 1.15.2）。
12. **`num_iter_outter` 非笔误**：`theseus_optimizer.py:104` 注释明示沿袭 BundleSDF C++ 命名。
13. **`base.yaml:197` `//workspace` 双斜杠笔误**（路径仍可用但脏）。
14. **FoundationStereo 商业版 ONNX 权重只能从 NGC 拉、常失败需手动**（`deploy.sh:315-338` 有空文件检测重试）；`device='cpu'` 时 `foundationstereo_onnx.py:195-196` 仍无条件要求 CUDA。
15. **Dockerfile 链路锚点**：`docker/Dockerfile` 313 行单 stage（nvcr pytorch:25.04-py3）源码编译 BundleSDF(nvbundlesdf 分支 my_cpp——Python 侧 `import my_cpp` 的真实来源)/SAM2/RoMa(钉 commit)/kaolin(七档 CUDA arch)。

## 生成口径

- 13 层层序：治理文档 → GitHub 协作 → 包构建依赖 → 容器部署 → 包骨架/CLI → 配置系统 → 数据加载/前处理 → 感知推理组件(SAM2/FoundationStereo) → 重建核心引擎(NVBundleSDF/NerfRunner/tool) → Theseus 位姿优化 → 资产后处理出口(USD/USDZ) → 交互可视化/演示 → 测试冒烟。
- 字数口径：ONBOARDING/explain 均「不计空格字符」；explain 小仓从简档 6 篇（<30 代码文件仓规格）。
