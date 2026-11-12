# 04 微服务交互 app 与压测矩阵：本地部署主力脚本

## 角色定位
`scripts/audio2face_3d_microservices_interaction_app/` 两脚本分工：**a2f_3d.py**（458 行）是本地 A2F-3D NIM 的主力交互脚本——proto 绑定最全（:31-41 九条 import 覆盖 8 个模块族，独有 health），支持 disabled/tls/mtls 三种安全模式（:378-396），是 quick-start compose 起服务后的"第一验证工具"；**nim_performance_test.py**（382 行）是吞吐/延迟压测器，用多进程池模拟并发客户端。

## 内部结构
**a2f_3d.py** 两子命令（create_parser:341-376）：health_check 走 grpc.health.v1 HealthStub.Check 判 SERVING（check_health:320-337）；run_inference 在 main（:398-453）里 create_grpc_channel→async with channel→A2FControllerServiceStub→stream=stub.ProcessAudioStream()（:432）→双 asyncio 任务并发（:437-440）→三级异常捕获 ValueError/AioRpcError/Exception 各自 exit(1)。write_to_stream（:224-317）比 api_client 版多两件事：输入自检（:236-240 硬拒非 16bit/非 mono，先打印采样信息 :231-234）与 EmotionParameters 注入（:268-271，live_transition_time+beginning_emotion 两 config 键）；read_from_stream（:125-221）多 FPS/首包延迟测量（packet_count+time.time，:148-161，--print-fps 触发）与 --skip-print-to-files 开关（:163-179），输出目录由 compute_output_directory_name（:116-122，2 空格缩进的异类）取 output_{N:06d} 递增名。**nim_performance_test.py**：main 硬编码 6 个音频（:350-355：Claire_sadness 16khz/44.1khz × 5/10/20s）→逐音频 simulate_multiple_clients（:320-343，multiprocessing.Pool(max_stream_nb)）→每个"客户端"子进程执行 `python3 a2f_3d.py run_inference <file> config/config_mark.yml -u <url> --skip-print-to-files --print-fps`（run_single_client:140，config 亦硬编码+相对路径）→get_single_client_perf（:152-182）用正则从 stdout 抓 "First packet sent/received" 两个 time.time() 时间戳差算首包延迟→StatsHolder（:185-239）算 min/P1/P5/P10/median/mean/P90/P95/P99/max 九档→落 performance_output_{N}/ 四件套（csv/png/fps.txt/latency.txt，:361-379）。random.seed(45)（:251）令客户端错峰 sleep 可复现。

## 外部连接
对 proto：8 模块族全量绑定（含 health 与 emotion_aggregate）；对配置：config/config_mark.yml（压测固定用 mark）+ ../../example_audio/ 六变体；对服务：--url 指向 deployment_config.yaml:50 的 0.0.0.0:52000 双向流端点；README 给出 openssl 自签 CA/服务端/客户端证书全流程与三安全模式示例命令。

## 数据流
单请求：wav→校验→1 秒分块流写→帧流回→CSV 三份+out.wav。压测：6 音频×request_nb 次×max_stream_nb 并发→stdout 时间戳解析→DataFrame 聚合（compute_results:242-289）→柱状图（plot_metrics:50-122，延迟/FPS 双子图）+摘要 txt（record_fps_latency_summary_files:301-317，"99% of the requests have latency below X ms"）。

## 设计决策
①压测不在进程内复用通道，而是子进程跑完整脚本——隔离 gRPC 状态、贴近真实客户端、代价是每次冷启动；②首包延迟用 epoch 时间戳差而非 RPC 内计时，实现零侵入（性能埋点早在 a2f_3d.py:276-278/:149-151）；③音频矩阵 2 采样率×3 时长恰好探测流式首延迟与稳态 FPS 两个维度；④三处 compute_output_directory_name 复制（本文件:116、migration、fetch app），目录名前缀参数化但逻辑不共享。

## 新人提示
勘误三连：docstring 说输出到 output/（create_parser:127）实际 OUTPUT_FOLDER='performance_output'（:37）；StatsHolder.get_filed_name（:223）是 get_field_name 拼写笔误；休眠 bug 同 02 篇——emotion_key_frames 两键初始化（:135-138）vs a2e_output 写入（:100）。压测必须 cd 到本目录（全部相对路径）；--max-stream-nb 要与服务端 common.stream_number 对齐（README 明示）；换测试音频/配置只能改源码两处（:140、:350-355）。
