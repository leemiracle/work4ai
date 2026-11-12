# 04 · predict 导出五形态：从模型输出到可分发产物

## 角色定位

`instant_nurec/predict/` + `instant_nurec/cli.py`/`ncore_input.py`/`pretrained.py` + `model/system.py` 构成预测面：把一次前馈的 KelvinInstantNuRecPrimitive 变成**五形态产物**——① 3DGS PLY、② 天空侧车 `.sky.npz`/`.sky.png`、③ 动态层 `.dynamic.npz`、④ 预览渲染 `.render.png`、⑤ 视频渲染 `.render.mp4`（run_inference.py:17-27 docstring 钉版）。"预测即导出"是这层的设计纲领：没有独立后处理步骤，predict 循环内一次落盘。

## 内部结构

**入口链**：`run_inference.py`（根目录薄包装）→ `cli.py` make_parser 定义全量推理选项（model profile/输出目录/--merge/--n-gaussians/--render-preview/--render-video）；8 处函数体内延迟 import（cli.py:201/:209/:217-234）——:216 注释钉版动机"Lazy imports keep argparse-only invocations (e.g. --help) cheap"。`resolve_ncore_paths`（ncore_input.py:31）接受单 JSON 或 `.lst` 清单（每行一个序列路径）展开校验。`run_predict`（predict/run.py）种子固定→`InstantNuRecConfig` 构造 `GaussiansInstantNuRecSystem`（model/system.py:48，串联 DataModule+KelvinInferenceModel+导出器+预览渲染）→ Lightning predict。

**权重边界**（pretrained.py + model/__init__.py）：三 profile `pa-front`（默认，:42）/`pa-multiview`/`pq-front`（:60-84）；HF 下载到 hub 缓存（:114），`INSTANT_NUREC_FULL_PT` 环境变量离线短路且须匹配 profile（:123-132）；工厂 `make` 预检相机 ID（model/__init__.py:55-78，配错报可用相机清单）并**拒载旧 traced archive**（:125-130，提示重新下载）。

**分块合并**（primitive_merge.py）：长序列分块推理后，`CameraFrustum`:41（in_frustum/中心距离）+ `compute_frustum_ownership_mask`:130 做跨块视锥归属去重，`merge_primitives_and_batch`:284 合并静态/动态层、天空 cubemap 与仿射矩阵，可选 KL 体素化迭代到目标高斯数区间 [0.9N, N]。体素化语义取每 voxel 置信度最高高斯的类（kelvin_primitive.py:205/:234）。

**五形态落盘**：PLY（export_ply.py）——`PLYExportGaussians.export`:44 写标准 3DGS splat PLY，颜色走 SH（`RGB2SH`:68），**scale/density 是预激活值**：逆激活硬编码 scale=exp/log、density=sigmoid/logit（:47-52）；`export_kelvin_ply`:75 先剔除非有限密度高斯（:80 日志计数）；用途钉版"NuRec SO 的初始化"（:105）。天空（export_sky.py：`sky_sidecar_path`:25/`sky_preview_path`:29/`export_sky`:33）出 npz+png。动态（export_dynamic.py:15 `export_dynamic`）出世界系刚体变换 npz。预览（render_preview.py）：`os.environ.setdefault("BUILD_3DGUT","1")`/`NUM_CHANNELS="3,4"` 保持部署侧构建选择权威（:39-44），`_looks_like_ftheta`:102 探测相机模型分流渲染参数。视频（render_video.py）逐源相机帧渲染，需 `--merge`+render extra+ffmpeg libx264（cli.py:209 require_ffmpeg）。

## 外部连接

- 上游：inference.py:58 的 KelvinInferenceModel 产出图元；static_core 路径（static_core.py:65）同样汇入 PLY 导出器。
- 下游：PLY 是 NuRec/Omniverse 精修与 AlpaSim 闭环仿真的输入（README.md:32-38）；run.sh 做 shell 级校验（非法 `.ncore-path` exit 65、输出目录不可写 exit 73）。

## 数据流

`--ncore-path` → resolve_ncore_paths → NCore 数据批（instantnurec_ncore.py:80）→ KelvinInferenceModel 前馈（含可选动态掩码精化 inference.py:150-193）→ KelvinInstantNuRecPrimitive（kelvin_primitive.py:415）→ [若 --merge] frustum 去重+体素化 → 五形态并行落盘（PLY+sky 相邻文件、dynamic 按需、render png/mp4 按旗标）。

## 设计决策

1. **预激活导出约定**：消费方（NuRec SO）期望预激活 scale/density，导出器负责逆激活（export_ply.py:51-52）——模型内部激活、盘上预激活，两头契约都显式。
2. **惰性 import 集中在 cli**：8 处延迟 import 让帮助文本零依赖加载（cli.py:216）。
3. **合并是可选且收敛的**：去重用视锥归属而非朴素拼接，体素化迭代至 [0.9N,N] 而非硬切 N。
4. **环境变量只 setdefault**：渲染构建开关可被部署侧环境覆盖（render_preview.py:43）。
5. **traced archive 断崖**：旧 TorchScript 包直接拒载并指路重下（model/__init__.py:130），避免静默行为差异。

## 新人提示

跑视频先备齐三件：`--merge`、`uv sync --extra render`（README.md:114）、ffmpeg+libx264；离线机器设 `INSTANT_NUREC_FULL_PT` 注意要与 --model profile 匹配（pretrained.py:123）；调 `--n-gaussians` 记住合并收敛区间是 [0.9N,N]（primitive_merge.py:284）；拿 PLY 去别的高斯渲染器时记得 scale/density 要先过激活函数，不是直接可用值。
