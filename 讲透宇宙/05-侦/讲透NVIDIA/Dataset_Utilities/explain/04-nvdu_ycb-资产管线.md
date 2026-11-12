# 04 · nvdu/tools/nvdu_ycb.py — YCB 模型资产管线

## 角色定位

`nvdu_ycb` 命令的实现体（248 行，setup.py entry_points 注册）：为 FAT（Falling Things）合成数据集准备 YCB 物体模型库。它不做可视化，是一条独立的**资产生成线**——从 ycb-benchmarks S3 下载 21 个 YCB 物体的 google_16k mesh，按配置文件里的固定变换矩阵把"原始模型"逐顶点变换成"对齐模型"。与 nvdu_data.py 的关系是单向的：只消费 DatasetSettings 解析能力来读配置。

## 内部结构

- **常量区（nvdu_ycb.py:19-44）**：`YCB_DATA_URL` 指向 `ycb-benchmarks.s3-website-us-east-1.amazonaws.com/data/`；`YCBModelType` 三档（Original/AlignedOnly/AlignedCm，nvdu_ycb.py:30-33）平行驱动 `YCB_DIR` 与 `YCB_OBJECT_SETTINGS` 两个下标数组——三档目录 × 三份配置的矩阵式布局。`YCB_URL_POST_FIX="_google_16k"` 注释明言**只支持 16k mesh**。
- **路径工具（nvdu_ycb.py:48-99）**：以 `nvdu.__path__[0]` 为根定位包内 `data/`（模型落点）与 `config/`（设置文件）——包内相对路径的标准手法；`get_ycb_model_path` 固定 `google_16k/textured.obj` 子结构。
- **列举与查询（nvdu_ycb.py:101-111）**：`log_all_object_names` 解析 `_ycb_original.json` 打印全部物体名（剥 `_16k` 后缀）。
- **核心变换 `transform_wavefront_file`（nvdu_ycb.py:114-148）**：纯文本逐行改写 wavefront obj——`v` 顶点行乘完整 4x4 变换矩阵；`vn` 法线行**乘去平移矩阵（只留旋转缩放的 matrix33）后归一化**；其余行原样复制。这是图形学教科书规则（法线变换须用逆转置或至少去平移+归一化）的手工实现，全仓最有含金量的 35 行。
- **资产生成三步（nvdu_ycb.py:150-222）**：`extract_ycb_model` 解 tgz；`download_ycb_model` urllib 下载（可自动解压）；`align_ycb_model`（nvdu_ycb.py:181-202）查物体设置拿 `fixed_model_transform`，把 original 目录的 obj 变换写到 AlignedCm 目录，再复制 `textured.mtl` 与 `texture_map.png`（材质贴图不变换只拷贝）；`setup_all_ycb_models` 遍历配置全部物体串起三步。
- **CLI main（nvdu_ycb.py:225-244）**：无参数打印路径总览、`--list` 列物体、`--setup` 全量装配、位置参数查单物体路径。

## 外部连接

- 依赖 `nvdu/__init__.py`（定位包根）与 `nvdu/core/nvdu_data.py`（DatasetSettings.parse_from_file 读配置）。
- 三份配置（`nvdu/config/object_settings/_ycb_{original,aligned_m,aligned_cm}.json`）是它的数据权威：每份 21 个物体的 `class/segmentation_class_id/fixed_model_transform/cuboid_dimensions`（sample 见 `_ycb_original.json` 的 exported_objects）。
- 产物被可视化线消费：nvdu_viz 的 `--model_dir` 默认指向 `get_ycb_root_dir(YCBModelType.Original)`（test_nvdu_visualizer.py:47），Model3dManager 运行时加载 textured.obj。

## 数据流

```
_nvdu_ycb --setup_
  → DatasetSettings.parse_from_file(_ycb_original.json)
  → 逐物体: download_ycb_model(S3 tgz) → extract_ycb_model → align_ycb_model
       └─ transform_wavefront_file(src obj, dst obj, fixed_model_transform)
            v 行: M × [x,y,z,1]；vn 行: normalize(M33 × [x,y,z,0])
       └─ copy textured.mtl + texture_map.png
  → data/ycb/{original,aligned_cm}/<obj>/google_16k/textured.obj
```

## 设计决策与坑

1. **对齐权威在配置不在代码**：`fixed_model_transform` 全部来自 `_ycb_original.json`，代码只执行矩阵——换数据集（非 YCB）只需换配置，这是它作为"工具链"而非"脚本"的关键一步。
2. **勘误（md5 实证）**：`_ycb_aligned_m.json` 与 `_ycb_aligned_cm.json` **字节级相同**（md5 均为 e567bc7d670a7bf71b8b2b9435cb465a）——AlignedOnly 档没有独立维护的参数；且 `align_ycb_model` 只写 AlignedCm 目录（nvdu_ycb.py:190-191），AlignedOnly 档的 aligned_m 目录实际从不产出。三档模型类型里有一档是"语义占位"。
3. **IntEnum 退化**：YCBModelType 注释保留了 `@unique class YCBModelType(IntEnum)`（nvdu_ycb.py:26-29）后改成普通类——三档值当数组下标用，普通类够用，但失去类型约束。
4. **串行下载无重试**：`urllib.request.urlretrieve` 单发（nvdu_ycb.py:174），21 个物体逐个下，断了就重跑整个 setup（无断点续传；已存在的 obj 会被重复下载——download 不检查本地已有）。
5. **类名 `_16k` 后缀剥离散布三处**：get_mesh_file_path（nvdu_data.py:55-56）、log_all_object_names（nvdu_ycb.py:107-109）、setup_all_ycb_models（nvdu_ycb.py:216-218）各自实现一遍 `if endswith('_16k'): name = name[:-4]`——协议性知识没有收敛到一处。

## 新人提示

S3 源站至今仍可用（ycb-benchmarks 公开桶），但要复现需 Python 3.6 环境 + `import future` 依赖在。只想看对齐效果，读 `transform_wavefront_file` 的 35 行就够——它也是理解 `fixed_model_transform` 语义（original→aligned 的刚体+缩放变换）的最短路径。可视化时报"can NOT find 3d model"（viz/mesh.py:54）几乎总是没跑过 `--setup` 或 `--model_dir` 给错档位目录。
