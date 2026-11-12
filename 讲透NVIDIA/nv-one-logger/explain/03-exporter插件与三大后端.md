# 03 · exporter 插件体系与 OTel / W&B / JSON 三后端

## 角色定位

exporter 子包是"一次采集、多后端分发"的支点：core 定义七方法 Exporter ABC 与 entry-points 配置发现机制，otel/wandb 两个兄弟包与内置 JSON 系列给出三档参考实现。Lightning 集成（pytorch_lightning.py）虽不实现 Exporter，但同属"接入生态"一翼。

## 内部结构

`Exporter`（exporter.py:19）七抽象方法 initialize/export_start/export_stop/export_event/export_error/export_telemetry_data_error/close（exporter.py:22-101）；`BaseExporter`（exporter.py:104）加三态机 NOT_INITIALIZED→READY→CLOSED（:110-115），误用即 ExportError（:173-177）。发现机制在 `ExporterConfigManager`：`ENTRY_POINT_NAME = "nv_one_logger.exporter_configs"`（export_config_manager.py:32，importlib.metadata :4），三级优先 direct > file > package（export_config_manager.py:18-28；file 完全替换 package 而非合并 :97-98），create_exporters_from_config（:111）按 class_name 动态导入、失败仅告警跳过（:131-136）。

## 外部连接

三个后端各有适配哲学：**OTelExporter**（otel_exporter.py:25）注入任意 OTel SpanExporter（:28-32），span→OTel span、event→"fake_event_span"（:158）适配 OTel 无事件概念；uuid→(span, context) dict 传播父子（:39,75-91）。**W&B**（wandb_exporter.py）面对"没有 span 只有 metric"的后端，用 MetricNamingStrategy（:73）拍平命名——默认 Hierarchical 产 `my_span.my_event.bar`（:103,351-354），另有 Flat（:135）；同步版 WandBExporterSync（:282）与**异步版 WandBExporterAsync**（:335）双实现：duplex Pipe + daemon 子进程（:362-363），wandb init/log 全在子进程（:373-414），双向管道回传错误（:434-456），_initialize_wandb 临时改 WANDB_RUN_ID/WANDB_SERVICE 避免与用户自己的 wandb 互相干扰（:57-61）。**JSON 系**：BaseJsonExporter（base_json_exporter.py:19）RLock+getpid 防 fork 误写（:26-29）、_last_start_span 合并叶子 span 单条记录（:33-37）；FileExporter 紧凑 JSON 行（file_exporter.py:67-70）、LoggerExporter 层级格式化且可反序列化（logger_exporter.py:80）。

## 数据流

DefaultRecorder.start/stop/event → 遍历 exporters 调 export_* → 各后端自决批量/同步策略（OTel 走 BatchSpanProcessor，otel_exporter.py:16；wandb 异步走管道；JSON 即时写）→ exporter 连挂 5 次被熔断（default_recorder.py:26 `_DISABLE_EXPORTER_AFTER_N_FAILURES`，_ExporterState :37-53）。Lightning 侧 TimeEventCallback（pytorch_lightning.py:47）吃标准钩子，hook_trainer_cls（pytorch_lightning.py:189）补丁 __init__ 插 callback（:215-228）与 save_checkpoint 埋点（:236-246）；OneLoggerPTLTrainer（:251）子类化 Trainer，save_checkpoint 以 try/TypeError 兼容新旧签名（:287-292）。

## 设计决策

1. **entry points 而非硬编码注册表**：第三方后端零侵入接入，配置可来自包元数据/文件/直传三层。
2. **异步 wandb 用子进程而非线程**：wandb 的网络栈与用户进程状态隔离，训练主进程零阻塞（:338-339 docstring）。
3. **同步版保留**：小规模作业省一个进程，双实现按规模选型。
4. **Lightning 双路径**：Callback 吃不了存档后钩子（pytorch_lightning.py:50-53），故 hook 补丁与 Trainer 子类并存；hook 只覆盖同步存档（:194-195）。

## 新人提示

自写后端从 BaseJsonExporter 起步最省事；调试 entry points 用 `importlib.metadata.entry_points(group="nv_one_logger.exporter_configs")` 直接看发现了谁；wandb 异步版的错误在 `_check_for_errors`（每个公共方法开头轮询管道，:441-443），子进程崩了会以 exitcode!=0 暴露（:447-450）。
