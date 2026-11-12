# 07 gst-nvdsosd：屏显绘制与 cuOSD 双层渲染

## 一、角色定位

`nvdsosd` 是 DeepStream 管线的"最后一公里"可视化插件：推理、跟踪、分析全部产出结构化元数据后，由它把边界框、分割掩码、文本标签、时钟、线段/箭头/圆圈、隐私模糊等元素"渲染回画面"，供显示或编码存储。它位于 `src/gst-plugins/gst-nvdsosd/gstnvdsosd.c`（1139 行），本体是一个极薄的 GStreamer BaseTransform 适配层——真正的绘制能力来自下层 `src/utils/nvll_osd/` 的 nvll_osd 库与更底层的 cuOSD（cuosd.cpp 967 行 + cuda/cuosd_kernel.cu 1159 行）。三层分工：**插件层读元数据→nvll_osd 层组织帧级参数→cuOSD 层命令式 GPU 渲染**。与 nvinfer"生产元数据"相对，nvdsosd 是元数据的最大消费端之一；由于纯画像素不产生新信息，它也是性能调优时第一个被砍掉的元件（fakesink 场景直接删掉即可）。

## 二、内部结构

插件层（gstnvdsosd.c）核心部件：属性表 PROP_SHOW_CLOCK..PROP_BLUR_BBOX（第 50-62 行）暴露 show-clock/display-text/process-mode/gpu-id/display-box/display-mask/blur-gie-class-ids 等 12 个属性；pad 模板 sink/src 均为 `memory:NVMM` 的 NV12/RGBA（第 79-93 行）；默认 process-mode=GPU（`GST_NV_OSD_DEFAULT_PROCESS_MODE MODE_GPU`，第 98 行），Tegra 平台额外注册 MODE_NONE 枚举但注释明言"Invalid mode. Falls back to GPU"（第 120-122 行）。状态机三函数：`gst_nvds_osd_start` 创建 nvll_osd 上下文（第 275 行），`set_caps` 时调 `nvll_osd_set_params` 分配宽度高度相关缓冲（第 249 行），`transform_ip` 是每帧主循环（第 333 行起）。固定数组 `rect_params/blur_rect_params/mask_params/text_params` 各预分配 MAX_OSD_ELEMS=1024 槽位（第 37 行）。

nvll_osd 层（includes/nvll_osd_api.h，347 行）定义七种 `NvOSD_Frame*Params` 帧级容器（Text/Rect/SegmentMask/Line/Arrow/Circle），每个都带 mode + NvBufSurface 指针 + 参数列表——注意 `buf_ptr` 字段已废弃、注释统一指向 `surf`（如第 70-73 行）。实现分 `nvll_osd_put_text_cpu`（nvll_osd_int.cpp:897）与 `nvll_osd_put_text_gpu`（nvll_osd_int.cpp:1087）两条路径。

cuOSD 层（cuosd.h 165 行）是纯 C++ 命令式 API：`cuosd_draw_text/line/arrow/point/circle/rectangle/boxblur/rotationbox/segmentmask/polyline/rgba_source/nv12_source/clock` 共 13 个 push 型函数 + `cuosd_apply`/`cuosd_launch` 提交 + `cuosd_clear`。文本后端枚举 PangoCairo/StbTrueType（第 39-43 行），实现只在 `textbackend/` 目录提供 pango-cairo.cpp（331 行）；`create_stb_backend` 被 `#ifdef ENABLE_TEXT_BACKEND_STB` 包裹（backend.cpp:47-51）且 stb.hpp 不在本仓——StbTrueType 是预留槽位，本仓库实际可用后端只有 PangoCairo。旁支 nvll_obb.h（182 行）提供 `nvobb_dump_frame`/`nvobb_rotate_gpu`：从表面裁出 AABB 像素再旋转摆正成 OBB 立方图，服务于车牌识别（LPR）等需要"正立小图"的下游模型。

## 三、外部连接

上游通常是 tracker 或 nvdsanalytics（元数据已齐），下游是编码器/显示 sink。横向依赖：nvdsmeta 的 NvDsBatchMeta/NvDsObjectMeta/NvDsDisplayMeta 结构（遍历基础）；nvbufsurface 提供表面描述；GPU 路径依赖 CUDA surface object（BlockLinear NV12）或裸指针（PitchLinear/RGBA）。文本后端外部依赖 pango/cairo/jpeg 开发包（nvll_osd/README Prerequisites）。动态控制方面监听自定义事件 `GST_NVEVENT_OSD_PROCESS_MODE_UPDATE`（gstnvdsosd.c:148-169），可在运行中切换 CPU/GPU 模式。消费 nvll_obb 的调用方在 nvll_osd_int.cpp 与 tao_apps 的 LPR 链路（3D/旋转框场景）。nvinfer 产出的 segmentation mask 经 `mask_params` 传入 `nvll_osd_draw_segment_masks` 完成掩码上色。

## 四、数据流

每帧到达 `transform_ip`（gstnvdsosd.c:333）：①map 缓冲取 NvBufSurface 指针（第 368 行）→ ②遍历 GstMeta 找到 NVDS_BATCH_GST_META 拿 batch_meta（第 377-385 行，用 quark 比对）→ ③**直接遍历 `batch_meta->obj_meta_pool->full_list`**（第 388-390 行）——这是绕过逐帧 frame_meta 的池级遍历：对象池的 full_list 就是全批在用对象，一次扫完；draw_bbox 则收集 rect_params，blur_bbox 则按 gie_id+class_id 过滤收集模糊区（第 415-424 行），draw_mask 收集掩码，text_params 有 display_text 的收文本→ ④display_meta_pool->full_list 同法收集用户自绘的 rect/label/line/arrow/circle（第 493 行起）→ ⑤任一类计数触达 1024 即提前 flush 一次对应 nvll_osd 调用（分块防溢出），循环结束后对剩余计数收尾 flush。GPU 路径最终落到 cuOSD：所有 push 调用只往 host 侧 vector 塞命令并更新 bounding box（如 cuosd.cpp:296-331），`cuosd_apply` 把异类型命令按各自 sizeof 逐个 memcpy 进连续 GPU 命令缓冲 + 偏移表（cuosd.cpp:899-907），文本命令先由 CPU 侧 PangoCairo 栅格化进 glyph 位图图集（cuosd.cpp:728-731），最后单个 `render_elements_kernel`（cuosd_kernel.cu:781）按模板参数 ImageFormat（RGBA/BlockLinearNV12/PitchLinearNV12，对应 BlendingPixel 特化第 609-749 行）分发绘制所有元素，boxblur 走独立 kernel（cuosd.h:124-126 注释明示独立于其他绘制函数）。

## 五、设计决策

①**命令延迟合并 + 单 kernel 提交**：cuOSD 不为每类图形单独起 kernel，而是 host 攒命令、算联合包围盒、一次 `render_elements_kernel` 画完——1000 个框也是一次启动，这是 GPU OSD 对抗小 kernel 启动开销的核心手段；代价是必须维护异类型命令的紧凑序列化（memcpy by type + offset 表）。②**文本栅格化留在 CPU**：GPU 画字形不划算，PangoCairo 在 host 生成位图图集，kernel 只做纹理采样混合，CPU/GPU 各干擅长的事。③**CPU 模式强制 RGBA**：`transform_caps` 里 MODE_CPU 时直接与 RGBA caps 求交（gstnvdsosd.c:193）——NV12 的 YUV 混色 CPU 端太贵，干脆在协商期把格式钉死。④**池级遍历而非逐帧遍历**：obj_meta_pool->full_list 一次拿全批对象，省去双层循环；这也解释了为何插件不关心 frame_meta 的流内归属（画框只需坐标+表面）。⑤**隐私模糊是一等公民**：blur-gie-class-ids 允许"只糊某 GIE 组件某类别"（如只糊人脸不糊车身），Blur_Mask 模式优先掩码、无掩码回退 bbox（第 70-75 行枚举注释）。⑥**dGPU 上 MODE_NONE 拒绝服务**：cudaDevAttrIntegrated 探测（sink_event 第 162 行、start 第 284 行）非集成 GPU 且模式>GPU 直接回退并告警，防止把 dGPU 流水线配成 Jetson 专属直通模式。

## 六、新人提示

改绘制行为先分清层次：调颜色/线宽/字体在 nvdsmeta 的 rect_params/text_params（上游 probe 填），插件只管"画不画"（display-box/display-mask/blur-bbox 开关）；要新增图形种类才动 cuOSD。两个易踩坑：(1) 字号语义——cuosd.h:68 注释说"font_size is scaled by 3 and clamped to 10 - 500"，但源码 MAX_FONT_SIZE 定义为 **200**（textbackend/backend.hpp:27），实际 clamp 是 10–200，注释与代码不一致，按 500 预期写配置会静默变小；(2) CPU 模式只支持 RGBA，若上游给 NV12 会在 caps 协商直接失败而非运行时转换。性能排查记住"OSD 在 Nsight 里只有一两个 kernel"是正常的——命令合并后看不到每图元 kernel；若 `cuosd_launch` 打印 "Please check if there is anything to draw"（cuosd.cpp:940），说明元数据没到（多半上游没接 tracker 或 display_meta 没填）。甄别说明：本篇依据源码逐行核实；任务书所述"drawOBB"实为 nvll_obb 的 dump/rotate API 族（本仓无名为 drawOBB 的函数），"pango 文本后端"经核实为**唯一**在仓实现的后端（StbTrueType 仅有枚举与编译开关，无实现文件）。
