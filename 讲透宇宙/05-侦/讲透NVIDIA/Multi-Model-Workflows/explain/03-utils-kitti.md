# 03 · utils/kitti_util.py + utils/config_util.py — 检测语读写器与摆设配置器

## 1. 角色定位

kitti_util.py（87 行）是全仓"检测通用语"的读写器：把 Grounding DINO 的开集检测结果以 KITTI 15 列标注为中间格式读回 Python（read_kitti），用 shapely 把 OCR 多边形空间关联进检测框（object_text 字段），并提供叠加可视化（overlay_labels_on_images）。KITTI 是三个模块间的契约格式：cv_nim/gdino_nim.py:163-179 写、kitti_util 读、overlay 再读。config_util.py（7 行）是 YAML 加载器，表面上的配置统一入口，实际是零活消费的摆设（见勘误）。两者同居图谱 L02 全局常量与工具层。

## 2. 内部结构

**kitti_util.py**：
- :8-20 _polygon_intersection——遍历 polygon_dict 的键，`"x" in key` 命中时以 `key.replace("x","y")` 取配对 y 值，攒点成 shapely Polygon，与 `box(*bbox)` 判 intersects。**:14-15 两行缩进落在 for 层而非 if 层**（勘误见第 5 节）。
- :22-50 read_kitti——:24-25 文件不存在抛 FileNotFoundError；:28 csv.reader 按空格分列；:30 assert 每行≥15 列；:31 取 row[-15:] 为 KITTI 固定尾段；:32 bbox=metadata[3:7]（xmin/ymin/xmax/ymax，ast.literal_eval 兼容字符串数字）；:35 class_name=" ".join(row[:-15])——**类名=前缀全部拼回**；:37 confidence=metadata[-1]；:42-48 传了 ocd_data 时逐 OCR 多边形求交，命中把 label 拼进 object_str，:48 恒写入 object_text 键（零命中是空串不是缺键）。
- :52-86 overlay_labels_on_images——:58 sorted(listdir) 定帧序；:67-72 有 detection_dir 时重读 KITTI 画 2px 绿框；:76-79 读 labels_dir 同名 .txt 文本；:82 cv2.putText 在 (200,200) 用 SIMPLEX 5 号红字绘文本；:84-86 写出叠加帧。

**config_util.py**：
- :3-6 load_config——默认参数是相对路径 'config/config.yaml'，yaml.safe_load 返回 dict，全文仅此一函数。

## 3. 外部连接

- kitti_util 被 app/app_image.py:21（:114-116 调用）与 app/app_video.py:21（:117-118 读、:133 叠加）消费；read_kitti 在 overlay 内部被复用（kitti_util.py:69）。
- kitti_util 依赖 shapely（Polygon/box）+ cv2 + 标准库（csv/ast/os/pathlib）——shapely 是全仓唯一几何判断点。
- config_util 的唯一 import 方是 llm_nim/openai_runner.py:10，而那条 import 本身断链（config/ 下无 config_util.py，真身在 utils/）→ **load_config 实际不可达**。真正在用的配置线是 hydra：schema/default_config.py + config/config.yaml 经 @hydra_runner（app_image.py:141-145）装载。

## 4. 数据流

检测主线：gdino 的 parse_output 写 labels.txt（KITTI 行）→ read_kitti(labels.txt, ocd_data) → list[{class_name,bbox,confidence,object_text}] → json.dumps 进 InstructionalNIM 提示词（app_image.py:68-70）→ Executor 执行 postprocessor 得答案。

OCR 关联线：ocd 的 parse_output 产出 {"metadata":[{label, polygon:{x1..x4,y1..y4}}]}（质心排序，ocd_nim.py:124-140）→ read_kitti :45-47 对每个检测框×每条 OCR 求交 → 命中词拼接进 object_text。检测框从此携带"框内文字"，供代码生成 LLM 用（提示词明言 object_text 字段，openai_nim.py:68）。

可视化线（仅视频模式）：frames_dir + analytics 文本 + 检测 labels → 绿框红字叠加 → ffmpeg 重编码。

## 5. 设计决策（含勘误）

- **勘误·:14-15 缩进错位——对"恒单点静默失效"论断的再勘误**：point=(x,y)/append 两行确系缩进错位（在 for 层、if 外），对不含 "x" 的键（y 键）会拿陈旧 (x,y) 重复追加，是真缺陷。但"polygon_points 恒单点→关联静默失效"过强：用 shapely 2.1.2 独立实验（x/y 交错键序与 x 键在前两种真实键序），连续重复顶点会被 LinearRing 构造折叠，四点多边形的 area/validity/intersects 与正确缩进版**逐项一致**——即对 ocdrnet 的四点 polygon，该 bug 被几何掩蔽，关联结果碰巧正确。真正会炸的边界：首键不含 "x"（如 y 键在前）→ :14 引用未赋值的 x 直接 NameError；polygon 仅一个 (x,y) 对 → Polygon 构造抛 ValueError（linearring 至少 4 坐标）——但后者正确缩进同样炸，属输入非法而非缩进所致。结论：该修（把两行缩进进 if 块），但"现网恒单点失效"不成立。
- **勘误·两套凭据体系，config.yaml 的 nim 段是摆设**：schema/default_config.py:30-33 定义 NIMConfig(url/api_key)、config/config.yaml:8-9 也有 nim 段，但 app 层实际用的是 utils/constants.py:4-6 的 NVCF_API/URL 硬编码（app_image.py:20）——cfg.nim 全程零消费。改 config.yaml 的 api_key 无效，必须动 constants.py 或改代码读 cfg.nim。
- **勘误·schema 同名类遮蔽**：default_config.py:20-26 先定义 GradioApp（server_name/server_port/debug/max_file_size），:38-48 **再次定义同名 GradioApp**（model/app/nim 三字段）——后者遮蔽前者成为 app_image.py:19 导入的生效版；其 :47 默认值 `GradioApp()` 在类体执行时解析到**第一版**类（第二版此时尚未绑定），cfg.app.server_port 可用全靠这次遮蔽的运气。另 NIMConfig 默认 api_key 缺右尖括号（:33 `"<API_KEY"`，typo）。
- **勘误·load_config 双重死因**：相对默认路径 'config/config.yaml' 只有 cwd=仓库根才解析得到（对照 hydra 线 config_root 相对 __file__ 定位的正确姿势，app_image.py:32）；而唯一潜在消费者 openai_runner.py:10 的 import 路径本身写错——两层叠加使它不可达。
- read_kitti 的"末 15 列定界"是全仓最聪明的一手：KITTI 格式类名本不许含空格，而 Grounding DINO 的 phrase 可以（"pile of pallets"）；用"尾 15 列是固定字段、其余全部归并类名"的逆解析，写入端（gdino_nim.py:172/:176 phrase 原样写行首）、读取端（:31/:35）、旧复制（openai_runner.py:41-45）三处对齐成契约。
- overlay 的 cv2.putText（:82）硬编码位置与 Hershey 字体：非 ASCII 文本（中文答案）绘成问号方块，长文本溢出画面无换行——可视化只对短英文答案有效。

## 6. 新人提示

- 动 KITTI 列结构要同步三处镜像（写 gdino_nim.py:163-179、读 :30-37、遗留 openai_runner.py:42-47）加 :30 的 assert 阈值。
- 修 :14-15 时直接把两行缩进进 if 块；顺手把 `"x" in key` 改成 key.startswith("x")，与 ocd_nim.py:117-118 的 _calculate_centroid 口径对齐（子串匹配对 "max_x" 类键会误命中，现网 x1..x4/y1..y4 键下两者恰好等价）。
- object_text 零命中是空串不是缺键（:48）——下游判空用 `not d["object_text"]`，别用 `in`。
- 改 API key 记住只有 utils/constants.py 一处真管用（见勘误）；config.yaml 的 nim 段改了也白改。
- config_util 若要复活：import 改 utils.config_util + 路径绝对化（模仿 config_root 相对 __file__）；否则建议删除文件以免误导新人。
- overlay_labels_on_images 对没有同名 label 文本的帧会 FileNotFoundError（:78 直接 open 无存在性检查）——目录里混入非帧图或 analytics 缺帧都会断链。
