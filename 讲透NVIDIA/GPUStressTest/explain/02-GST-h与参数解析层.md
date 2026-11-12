# 02 · GST.h 与参数解析层

## 角色定位

这一层回答两个问题："每块 GPU 跑什么"（util/GST.h 的 12 型号测试套件）与"用户/主程序说什么"（CommandLine → parse_args → BlasOpts 的参数管线）。它是纯数据与解析层，不含任何 CUDA 调用，却是 main.cu 一切行为的数据源；头注释（util/GST.h:44-76）本身就是 -h 帮助的镜像文档。

## 内部结构

**GST.h** 三个常量钉死全局形状：`MAX_NUM_GPUS 32`、`NUM_TESTS 5`、`TEST_WAIT_TIME 600`（util/GST.h:82-84）。`stress_test_args` 结构（:95-105）持 test_name/P_arg 串/m/n/k/ta/tb/B 八要素；`test_suite` 枚举 12 型号（:109）。构造函数一个 switch 分派（:111-142）：T4/P100/V100_16 共用 init_t4（:113-117）、H100 复用 init_a100_80（:121-124）、M60 复用 init_generic（:137-140）——复用只发生在这里。init_* 家族 10 个方法填巨型维度，如 init_a100_40（:181-231）五项 INT8 bisb_imma 81218×34263×322437 / FP16 hsh / TF32 sss_fast_tf32 / FP64 ddd / FP32 sss；init_h200（:393-445）骨架是 n=29263/k=52437 按字节宽度分配。默认构造落 init_generic（:150-153）。

**CommandLine**（util/command_line.h:47-102）：argv 切成 `-key=val` 存 `map<string,pair<string,bool>>`（:50），取值即置消费标记（:104-115），`all_flags_checked`（:92-101）对未消费参数报 unknown argument——防拼错参数的防线。

**test_args.cu**：核心是 `IN_OUT_MATH_SCALE_TYPE_MAPPING` 宏表（util/test_args.cu:119-130）+ `parse_in_math_scale_out_type`（:132-175）把 sss/sss_fast_tf32/ccc/hhh/ddd/zzz/hsh/hss/bisb_imma/bii_imma/qqssq/tss/tst 共 13 串映射到七元组；`parse_args`（:281-413）memset 清零后设默认再逐 flag 覆盖（-m/-n/-k/-lda/-ta/-tb/-p/-m_epilogue/-tune…）；`reset_blas_opts`（:415-450）测试间复位、只保留 -T（缺省 10，:447）。

## 外部连接

GST.h 被 main.cu:83 独家消费（GST 构造 + stress_tests 读取 + NUM_TESTS/TEST_WAIT_TIME 常量）；test_args 的 parse_in_math_scale_out_type 与 cudaDataType2computeType 被 main.cu:85-87 extern 引用；BlasOpts（util/common_header.h:84-125，40 字段+*_opt 标记）是解析层与执行层的合同。基础设施三件套被全仓共享：type_convert.h 的 cuGet 模板族（:46-206）/cuMakeNaN（:145-150）负责类型落地；exceptions.h 的 cuda/cublas_exception（:58/:118）与 check_error 守门（:85/:140）；common_header.h 集中 include 并定义 DEFAULT_* 常量（含名不副实的 `DEFAULT_1024=2048`，util/common_header.h:77）。

## 数据流

命令行/套件参数 → CommandLine 键值表 → parse_args 填 BlasOpts → main 循环内 reset_blas_opts 复位 → **main.cu:1206-1302 又用 if-chain 按 P_arg 前缀重写七元组**（与宏表同一映射的第二份拷贝，改精度组合必须两处同步）→ m/n/k/ta/tb 从 stress_tests 覆盖（main.cu:1304-1309）→ test_cublasLt 按 math_type 选模板特化。dump_test_args（util/GST.h:155-177）在每测试前打印参数留痕。

## 设计决策

1. **套件即数据**：矩阵维度硬编码在头文件而非配置文件——验收工具追求零外部依赖、可审计。
2. **倍数策略**：util/GST.h:146-149 注释明言尺寸取 A100 Benchmark Guide 值的数倍，为的是更宽的显存足迹覆盖而非跑分。
3. **型号复用按显存档**：H100 与 A100_80 同表、M60 落 Generic——同档显存可共用同一套铺满策略。
4. **双重防线**：宏表负责 -P 解析，main if-chain 负责套件内建串——容忍手工测试命令与套件两条入口。

## 新人提示

新增 GPU 型号三步：test_suite 枚举加值、写 init_xxx、main.cu:1091 if-chain 加名字分支。注意 init_v100_16（util/GST.h:233-283）是死代码——构造函数把 V100_16 映到了 init_t4，别往里加东西。检查 README 基线表时以 init_* 为准（README 的 H200 FP8 行是旧代残留，代码无此项）。parse_args 里 "B" flag 检查重复了两遍（util/test_args.cu:333-340），无害但说明这段是复制粘贴产物。
