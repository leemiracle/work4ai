# 05 gst-nvdsanalytics：ROI/方向/越线分析插件

## 一、角色定位

`gst-nvdsanalytics` 是 DeepStream 的"规则引擎"：它不碰像素、不跑模型，只消费上游产出的**检测框 + trackingId**，在纯 CPU 上回答四个业务问题——这个目标**在不在**某个多边形 ROI 里、是不是**朝某个方向**移动、有没**越过**某条线、某个 ROI 里是否**过挤**（over-crowding）。这些答案最终变成字符串状态（`" ROI:ZoneA "`、`" LC:EntryLine "`）挂进元数据，供下游 msgconv 组事件消息、OSD 画框染色。

它是管线里"感知→语义"的最后一跳：nvinfer 说"这有个 128×256 的人"，nvtracker 说"这个人是 ID 37"，nvdsanalytics 说"ID 37 刚刚反向越过了 ExitGate 线"。绝大多数智能视频分析（VMS 集成、人流统计、周界告警）的业务逻辑都终止于此。

结构上它同样分两层：插件层 `src/gst-plugins/gst-nvdsanalytics/`（`gstnvdsanalytics.cpp` 1082 行 + 新旧两代配置解析器 + 公共头 `nvds_analytics.h` 163 行），算法层 `src/utils/nvds_analytics/nvds_analytics.cpp`（1022 行）。全部纯 C++ 几何运算——没有 CUDA、没有 GPU 依赖，是核心链路里唯一"无 AI 无 GPU"的智能插件。

## 二、内部结构

**配置模型**（插件层 `nvds_analytics.h`，per-stream `StreamInfo` L90-98 汇总四类）：

- `ROIInfo`（L46-53）：多边形点表 `roi_pts`、标签、`inverse_roi`（判定"在 ROI 外"）、per-class 过滤。
- `LineCrossingInfo`（L66-77）：线段端点 + 方向向量 `lc_dir` + 三档 `mode`（`eMode` balanced/strict/loose，L31-35）+ 四种 `mode_dir`（`eModeDir` use_dir/pos_to_neg/neg_to_pos，L37-41，含方向无关或只计单向）+ `extended`（延长线判定）。
- `DirectionInfo`（L79-88）：方向向量 + 参考点 `x1y1/x2y2` + 同款三档 mode。
- `OverCrowdingInfo`（L55-63）：ROI 点表 + `time_threshold_in_ms`（持续时长门）+ `object_threshold`（数量门）。

**算法层状态**（`src/utils/nvds_analytics/nvds_analytics.cpp`）：

- `NvDsAnalyticInfo`（L50-97）：**每对象历史**——环形缓冲 `prvX/prvY/prvW/prvH`（默认 `LAST_N_FRAMES=10`，L43）、中心坐标积分 `intgrlCntrX` 与平方积分（供标准差）、ROI 进入/离开时间戳、per-label `lcStatus`（每条线只报一次越线）、`trackingId`。超时清理由 `m_timeOut`（默认 `TIME_OUT_MSEC=8000`，L44）驱动。
- `NvDsAnalyticCtxImpl`（L125-167）：**每源上下文**——源 id、分辨率、对象表 `m_nvanalyticInf`（trackingId → 历史）、越线累计 `m_objLCcnt`、per-class 滑动窗口计数 `m_classPdf`（`ObjTypeHist` L115-122：`cntPdf` 直方图 + `pastCnt` 按时间戳的历史，`getSmoothCnt()` 用它平滑物体数抖动，中值滤波窗 `MED_FILT_MSEC=1000`，L45）。
- 三个纯几何函数（L860-955）：`CheckDirection`（位移向量与配置方向的余弦相似度门 `dir_sim`）、`NvDSAnalytics_CheckObjInROI`（经典射线法：对多边形每条边检查水平射线交点，奇数为内，L877-915）、`CheckLineCrossing`（先过方向门，再把 prev/curr 两点代入直线方程 `lc_info[0]*x + lc_info[1]*y + lc_info[2]`，异号即穿越，L934-955）。`CheckValidClass`（L917-933）统一 class 过滤语义（空表或含 -1 = 全类）。

**插件层**（gstnvdsanalytics.cpp）：

- `gst_nvdsanalytics_transform_ip`（L402-537）单线程同步处理（对比 nvinfer 的三线程，这里无重计算）。
- 热重载：自定义事件 `GST_NVEVENT_ANALYTICS_RELOAD_CONFIG_UPDATE`（L384-393）置 `reload_config`，下一批到达时按扩展名选 YAML 或 key=value 解析器重读并 `stream_analytics_ctx->clear()`（L419-441）——运行中改 ROI/线段不用重启管线。
- `enable=FALSE` 时 passthrough（L450-454）。
- 元数据深拷贝对：`copy_obj_nvdsanalytics_meta`/`release_obj_nvdsanalytics_meta`（L540-561）与 frame 级同构（L591-613）——tee 分支各自 copy，防双引用。

## 三、外部连接

- **上游**：硬依赖 tracker！`processSource` 里 `trackingId == 0xFFFF...FFFF`（未跟踪）直接打" Cant get ... without enabling tracker"并禁用方向/越线（nvds_analytics.cpp L685-690/L756-761）——ROI 可以只靠检测，方向/越线没有 ID 就没有"上一帧位置"。
- **下游**：OSD（读 `NvDsAnalyticsObjInfo` 染色/画线，插件自身的 `osd_mode` 属性控制 full/partial/off，gstnvdsanalytics.h L98-99）；msgconv（第 6 篇——事件消息里的 `lineCrossing`/`ROI` 字段正是 `lcStatus`/`roiStatus` 字符串）。
- **应用侧**：deepstream-app 的 `[analytics]` 配置组、REST 服务（运行中发 reload 事件热更新 ROI）、以及所有读 user meta 的自定义 probe。
- **元数据契约**：输出走 `NvDsUserMeta` 挂 `NvDsAnalyticsObjInfo`（对象级）与 `NvDsAnalyticsFrameMeta`（帧级计数），定义在公共头 `includes/nvds_analytics_meta.h`（共享全 SDK）。

## 四、数据流

`transform_ip`（L402-537）每批一次：

1. **准备**：可选热重载（L419-441）→ map 出 `NvBufSurface` → 取 `NvDsBatchMeta`。
2. **逐帧**：按 `frame_meta->pad_index` 找/建源上下文（惰性创建 L487-498，首次用 surface 实际宽高初始化，`obj_cnt_win_in_ms` 缺省 50ms L489-490）。
3. **第一遍收集**：遍历 `obj_meta_list`，把 `rect_params`/`object_id`/`class_id` 装进 `ObjInf` 列表（L501-512）。
4. **算法执行 `processSource`**（nvds_analytics.cpp L446-858，每对象）：
   - 更新环形缓冲历史；**平滑参考点**：帧龄 < 10 时用最近 2 帧均值，否则最近 4 帧均值（L640-668）——抗检测框抖动。
   - **STOPPED 判定**（L691-695）：帧龄足够且 `stdX<=400 && stdY/mean_h<=0.01`（坐标标准差极小）→ 状态追加 `" STOPPED "`。
   - **方向**：L2 位移平方 > 3000 且帧龄 > 10 才判（L701，源码自带 `FIXME: heuristics!` 自嘲），用脚点（中心 y + 高/2，更稳）做 `CheckDirection`（相似度 0.5）。
   - **越线**：按 mode 调三档参数（L766-778）——balanced：disp²>3000/dir_sim 0.5/帧龄 10；strict：6000/0.8/20；loose：1000/0.1/3，出批判定在 L782。`use_dir` 走完整 `CheckLineCrossing`（方向门+符号翻转），`pos_to_neg`/`neg_to_pos` 只认单侧穿越（配合 loose 判定），`extended` 起用延长线。每条线 per-object 只报一次（`lcStatus[lc.lc_label]` 短路，L749-752）。
   - **ROI**：射线法 + `inverse_roi` 反转语义；配合 `strtTimeRoiDet/stpTimeRoiDet` 做滞留时间。
   - **过挤**：ROI 内 per-class 计数 + `time_threshold_in_ms` 持续门 + `object_threshold` 数量门 → 帧级 `ocStatus`。
5. **第二遍回写**：`attach_metadata_object`（L516-526 有句 `FIXME: Assumes no meta reordering`——依赖两遍遍历 obj 链表顺序一致）把 `roiStatus/lcStatus/ocStatus/dirStatus` 字符串写进对象 user meta；`attach_framemeta_analytics_metadata`（L527-528）写帧级计数（objInROIcnt/objLCCumCnt 等，`NvDsAnalyticProcessParams` L124-140）。
6. 解锁、unmap、下行。

## 五、设计决策

- **状态即字符串**：分析结果全部拼成 `" DIR:North "`、`" ROI:ZoneA "` 这类字符串而非结构化枚举。上游新增分析类型不需要改下游解析（msgconv 只是把它写进消息的 status 字段）；代价是消费方要 parse 字符串——典型的"消息契约松散换演进自由"。
- **三档模式 = 参数打包**：strict/loose 不是不同算法，而是同一组启发式阈值（位移门/相似度/帧龄）的三档预设（L744-756）。工程上让用户不碰内部阈值就能调灵敏度——但想精细调只能改源码（三组数字都是硬编码）。
- **脚点 + 多帧均值抗抖**：方向/越线判定不用检测框中心而用**脚点**（`curr_y + curr_ht/2`，行人遮挡时脚最稳）；参考点取多帧均值而非上一帧。这两个选择直接决定误报率——单帧检测框抖动 10px 就可能伪造一次"越线"。
- **per-line 一次性触发**：`lcStatus` 短路保证每对象每线只报一次——符合"越线告警"的业务语义（持续触发会淹没消息总线），但反向应用（反复计数）得自己写 probe。
- **全部 CPU、单锁串行**：几何运算微秒级，GPU 化收益为零；`analytic_mutex` 一把大锁护住全部源上下文（L478/L530），简单正确优先。
- **热重载走事件 + 下一批生效**：不立即重配（可能与正在处理的批竞争），而是标记后在下一次 transform 入口重读配置并清空上下文——上下文清空意味着**所有对象的滚动历史丢失**，重载后短时间内判定降级（帧龄门不过），这是隐藏成本。
- **两遍遍历 + 顺序假设**：收集与回写都走 `obj_meta_list`，用下标对齐（L515 的 FIXME 承认了脆弱性）——若上游有人在中途改链表就会错位。写自定义上游插件时切忌在此元素前改对象链。

## 六、新人提示

1. **配置 per-stream**：`[analytics-0]`…`[analytics-N]` 组按 pad_index 对应源；漏配某源该源静默无分析。YAML 与 key=value 双格式并存（`nvdsanalytics_property_parser.cpp` 935 行 vs `..._yaml_parser.cpp` 836 行），字段名大体一致但逐个核对。
2. **方向/越线必开 tracker**：不开就是日志里那句 "Cant get direction information without enabling tracker" 且功能被永久禁用（`dir.enable=false` 是写进源上下文的，之后开 tracker 也不会自动恢复，需 reload 配置或重启）。
3. **调灵敏度先换 mode 再动线**：误报多 → strict；漏报多 → loose。还不够再考虑线的方向向量（`extend` 与 `mode-dir` 的组合语义在 `gstnvdsanalytics` 文档的 LC 图里有示意，源码 L757-790 的分支即对应关系）。
4. **坐标体系是推理输入分辨率**：ROI/线段坐标以 `config-width/config-height`（StreamInfo L95-96）声明，算法内部有归一化换算——你的检测框分辨率（推理缩放后）与配置不一致时看 `scale` 逻辑（transform_ip 里创建 ctx 时用 surface 实宽高 L494-495），别拿显示分辨率硬填。
5. **过挤的计数是平滑后的**：`getSmoothCnt` 的滑动窗（默认 1s 中值滤波）会把瞬时抖动抹掉——测试时用手挥一下不会触发，持续滞留才会；想看原始计数看 `objCnt`、消息里的是 `objInROIcnt`。
6. **ID 跳变会伪造越线/方向**：tracker 换 ID = 新对象从零历史开始，帧龄门（10 帧）会保护大部分场景，但快速 ID 切换仍可能产生异常状态串。追踪质量是 analytics 质量的上界。
7. **热重载丢历史**：reload 后 8 秒（TIME_OUT_MSEC）内的判定都在"冷启动"状态；生产上频繁热更新 ROI 要评估这段降级窗口。

> 注：本篇行号基于 DeepStream 9.1 源码（`src/gst-plugins/gst-nvdsanalytics/`、`src/utils/nvds_analytics/`）核实。`nvds_analytics.h` 同时存在于插件目录（配置结构）与 `includes/`（元数据契约），引用路径别混淆。
