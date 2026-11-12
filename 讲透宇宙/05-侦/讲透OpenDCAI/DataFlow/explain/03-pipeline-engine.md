# 03 · pipeline 引擎——编译期 DAG 与两代断点续跑

## 角色定位

`pipeline/Pipeline.py` 是 DataFlow 的编排心脏：`PipelineABC`（`Pipeline.py:19`）把"一串算子"变成"一张带 key 校验的有向图"，编译期就能拦住字段不匹配；`utils/pipeline_runner.py` 与 `utils/pipeline_checkpoint.py` 分别实现旧版游标续跑与新版事务式 checkpoint。图谱中 `Pipeline.py` 仅 5 条入边，但它是 7 个真继承 pipeline 的公共父类。

## 内部结构

`compile()`（`Pipeline.py:44-58`）是 tracing 式编译：扫 `vars(self)` 把每个 `OperatorABC` 属性包成 `AutoOP` 代理（`Pipeline.py:46-48`），真跑一遍 `forward()` 让回调收集 `OPRuntime`，再把 `forward` 替换成 `_compiled_forward`（`Pipeline.py:52`）。随后 `_build_operator_nodes_graph()`（`Pipeline.py:57`）建图：按 `LLM_SERVING_CLASSES` 探测算子里的后端（`Pipeline.py:69`）、从 kwargs 取 storage 并 assert 类型（`Pipeline.py:72-74`）；key 完整性校验——输入 key 不在累计集合就汇总抛 KeyError（`Pipeline.py:104-136`）；插入 DATASET-INPUT/OUTPUT 哨兵节点（`Pipeline.py:146-163`）。基类 `_compiled_forward`（`Pipeline.py:508-542`）逐节点 `run()` 并管 serving 生命周期：切换后端先 cleanup 旧实例（`Pipeline.py:519-523`）、引用计数归零再 cleanup（`Pipeline.py:537-542`）。`BatchedPipelineABC`（`Pipeline.py:545`）把它重载为分流器：有 `checkpoint_dir` 走事务式，否则走 runner（`Pipeline.py:569-580`）；`StreamBatchedPipelineABC` 已是纯兼容别名（`Pipeline.py:583-586`）。

## 外部连接

依赖 `core.operator`/`pipeline.nodes`/`wrapper.auto_op`/`utils.storage`（`Pipeline.py:8-12`）。循环依赖靠函数体内延迟 import 打破：`pipeline_runner.py` 三处（`pipeline_runner.py:17/21/184`），`pipeline_checkpoint.py:90` 延迟 import `BatchedFileStorage/FileStorage`。图谱边：`Pipeline.py` imports checkpoint，`pipeline_runner` depends_on checkpoint。

## 数据流

旧路径 `run_legacy_pipeline`（`pipeline_runner.py:79-165`）：游标文件 `{prefix}_last_success_step.txt` 存 "step,batch"（`pipeline_runner.py:96-107`），每批跑完回写（`pipeline_runner.py:145-159`）。`run_compiled_pipeline`（`pipeline_runner.py:168-192`）先判定能否自动升级（`pipeline_runner.py:23-52`）。事务式核心 `PipelineCheckpoint`（`pipeline_checkpoint.py:86`）构造时算身份指纹（源 sha256+算子类型+kwargs+输出路径，`pipeline_checkpoint.py:155-172`），兼容 legacy 身份并迁移旧 manifest（`pipeline_checkpoint.py:179-213`）；恢复时截断超长输出尾部（`pipeline_checkpoint.py:257-265`）；`commit()` 每批 fsync 输出+原子写 manifest+校验源文件未变（`pipeline_checkpoint.py:267-283`）。执行器（`pipeline_checkpoint.py:292-363`）在文件锁（`pipeline_checkpoint.py:60-83`）下逐批 commit，空输入也物化输出（`pipeline_checkpoint.py:344-352`），finally 清 `_active_batch` 并 cleanup serving（`pipeline_checkpoint.py:356-363`）。

## 设计决策

"跑一遍 forward 再编译"借鉴 torch.compile：作者只写声明式 forward，框架自动记录算子与参数；"key 即 schema"把字段错误从运行期提到编译期；checkpoint 身份指纹宁可拒绝续跑也不静默错跑（`pipeline_checkpoint.py:204-210`）。批判与甄别：任务书说"33 个 pipeline 文件仅 7 个真继承"，实测 statics/pipelines 下 53 个 .py、47 个定义 `*Pipeline` 类、仅 7 个真继承（grep 实证），其余全是裸类（`reasoning_pipeline.py:8`）——自建 storage、直接 `run(storage.step())`，绕过编译与 key 校验；且两套 `_compiled_forward` 逻辑重复，serving 生命周期要两处维护。

## 新人提示

先 `compile()` 才能 `draw_graph()`，否则 RuntimeError（`Pipeline.py:259-261`）。`op_nodes_list[0]` 是 DATASET-INPUT 哨兵，真实步号=索引-1（`pipeline_runner.py:113`）。断点续跑优先 `checkpoint_dir`；改配置即指纹变、必须换 checkpoint 目录，那报错是特性。裸类 pipeline 低成本改造：继承 `BatchedPipelineABC` 补 `forward()`，即白得 key 校验与事务续跑。
