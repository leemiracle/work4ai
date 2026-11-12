# 04 · utils/postprocessing.py — OBJ/MTL → USD/USDZ 资产出口

## ① 角色定位

`src/nvidia/objectreconstruction/utils/postprocessing.py`（414 行）是 real2sim 管线的**最后一公里**：把纹理烘焙产出的 textured_mesh.obj + material.mtl 转成 NVIDIA 生态（Isaac Sim/Omniverse）原生的 **USD/USDZ** 资产。特殊之处在**自实现 OBJ/MTL 解析器**——转换需要"逐面角点"的 UV 索引结构（facevarying），trimesh/assimp 等通用加载器不保留该形态。上游是 NVBundleSDF（nvbundlesdf.py:41 导入两个入口），在纹理烘焙后调用；CLI 流程的终点产物就是它写的 .usdz。

## ② 内部结构

四个层次（未注文件名的行号均指 postprocessing.py）：

**贴图路径解析组**：`_resolve_texture_path`（:13-19）MTL 相对路径按 .mtl 目录补全；`_resolve_texture_path_for_usd`（:22-46）三级回落——主路径缺失时按 basename 在 .mtl/.usd 目录各试一次（实证坑：MTL 常写 `0/material_0.png` 而图实际平铺在旁，嵌套引用让 USDZ localization 失败）；`_texture_asset_path`（:49-73）写**相对 USD 层的资产路径**，同目录时永远写 `./basename` 而非 `./0/basename`（:59-61）。

**OBJ/MTL 解析组**：`_obj_index`（:76-85）处理 1-based 与负索引；`_parse_face_corner`（:88-95）解析 `f v/vt/vn` 单角点（vt 可缺省）；`load_obj`（:98-125）**faces 存成 (顶点索引, UV索引) 角点对**——facevarying 的直接数据源；`_parse_map_kd_path`（:128-165）处理 `map_Kd -mm 0 1 file.png` 带修饰符的行——**从右往左找带图片扩展名的 token**（:146-153），避免把 `-mm`/`0` 当路径；`load_mtl`（:168-188）收 Kd/Ka/Ks/map_Kd。

**USD 组装组**：`_build_st_facevarying`（:191-216）按 faceVertexIndices 顺序逐角点产 (u,v)；兜底：面缺 vt 但 texcoords 数==顶点数时**用顶点索引当 UV 索引**（:202,206-207）；flip_v 时 v→1-v（:210）。`_uv_coverage_stats`（:219-231）统计 UV 覆盖。`build_preview_material`（:234-293）搭 **UsdPreviewSurface+UsdUVTexture+UsdPrimvarReader_float2** 三节点网络——UsdPreviewSurface 没有纹理输入口，直挂路径会被忽略（:244-245）；贴图声明 sRGB（:277）；**Kd 全零时不设 scale**（:278-284，MTL 常在 map_Kd 承载全部颜色时把 Kd 写零，照搬会把采样乘成全黑）。

**两个公共入口**：`convert_obj_to_usd`（:296-372）——stage 元数据 Y-up + metersPerUnit=1.0 + 默认 prim /Model（:307-309，Isaac Sim 友好）；blenderName userProperties（:315，Blender 导入兼容）；UV 覆盖 <50% 时 error 日志（:333-338）；faceVarying primvar "st"（:346-348）；**mesh scale=(100,100,100)**（:365）——厘米 OBJ 放大成米。`export_usd_to_usdz`（:376-400）用 `UsdUtils.CreateNewUsdzPackage`（:391-393，USD24+ 仅存 API）——**打包前在 cwd 建临时 `0/` 目录拷贴图**（:387-388），让 USD 里的 `0/xxx.png` 引用可解析，打完删（:396）。

## ③ 外部连接

上游仅 OpenUSD Python（`from pxr import Gf, Sdf, Usd, UsdGeom, UsdShade, Vt, UsdUtils`，:9）。下游：nvbundlesdf.py:41 导入两入口（管线终点调用）；`__main__` 块（:403-415）是对 retail_item 样本的手工冒烟入口。utils/__init__.py 将其 re-export 进公共 API。

## ④ 数据流

进：textured_mesh.obj + material.mtl + 烘焙贴图。变换：OBJ 角点 → facevarying st primvar（逐角点 UV，同顶点可多 UV）；MTL → UsdPreviewSurface 网络（贴图经 UVTexture 采样而非直挂）。出：.usd（平铺贴图、相对路径）→ .usdz（零拷贝 zip，贴图内嵌）。cm→m 的 100 倍缩放发生在 mesh 变换而非改顶点。

## ⑤ 设计决策

1. **自写解析器**：facevarying 需要保留 f 行每个角点的独立 vt 引用，trimesh 的 (V,3)+(F,3) 加载即毁掉该结构——重写 60 行解析比绕道通用库更直。
2. **路径全部"贴 .usd 层"归一**（:59-61,63-66）：USDZ 打包器按层相对路径找文件，嵌套目录引用（`0/...`）是失败高发区——两级回落 + flat 优先是实证坑的防御性编码。
3. **map_Kd 从右往左扫**（:146）：MTTL 规范允许行内修饰符，常见导出器行为是修饰符在前文件名在后——reversed 扫描 + 扩展名过滤双保险。
4. **临时 `0/` 目录 hack**（:387-388）：CreateNewUsdzPackage 只打包层引用能解析到的文件，而烘焙管线的 MTL 写的就是 `0/` 前缀——在 cwd 造出该结构让打包器吃进，是最小侵入的桥接。
5. **Kd 零值防护 + sRGB 声明**（:277-284）：两处都是"照搬 MTL 字面值会产出黑模型"的实证防御。

## ⑥ 新人提示

- `export_usd_to_usdz` 的 `0/` 目录建在**当前工作目录**（:387）——并发跑两个导出会互踩；参数名拼写 `materal_pic_path`（:376）是笔误但已是公共 API，改名要同步 nvbundlesdf.py:41 的调用。
- scale=(100,100,100)（:365）假设 OBJ 是厘米——若上游烘焙改单位，这里会产出 100 倍大的模型。
- `flip_uv_v` 默认 False（:300）：v 翻转与否取决于上游 UV 展开约定（Xatlas 产出通常不翻），渲出来是镜像贴图先查这里。
- UV 覆盖率的 error 日志（:334-338）只是日志不阻断——覆盖率低的模型照样导出，验收要自己看渲染。
- 只支持单材质单贴图（/Model/Material 一条路径，:246）：多材质 OBJ 会静默只用第一个 map_Kd。

---
*甄别：图谱 summary 与源码一致（自实现解析/facevarying/USDZ 打包三要点全对上）；无冲突。*
