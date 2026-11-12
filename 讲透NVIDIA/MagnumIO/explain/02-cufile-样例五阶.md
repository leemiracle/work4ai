# 02 · cuFile 样例五阶：教学阶梯与公共库复用

## 一、角色定位

`gds/samples/` 是 MagnumIO 体量最大的目录：五阶 33 个样例+include/common 公共库+bindings/python。双重角色：开发者视角是 cuFile 官方教学阶梯，从"注册文件→读一块显存"爬到批量与虚拟内存映射；集成者视角是可运行的数据完整性测试——README 要求"数据文件 ≥128 MiB 且在 GDS 使能挂载点；清理用 goto，RAII 版看 bindings"（`gds/samples/README.md:7`）。五阶即五条 API 轴：Basics 同步读写、Multithreaded 注册组合矩阵、Batch 批量、Async 流式异步、MemMap 虚拟地址+预注册。

## 二、内部结构

公共库 `gds/samples/include/cufile_sample_utils.hpp`（32/33 样例 include）四组设施：① 错误宏——check_cudadrivercall 打印文件:行号+错误名后 std::exit（:27-42）；多线程版不退出而 promise.set_value(-1) 后 return（:44-56）。② 单位家族 KiB/MiB/GiB constexpr 模板（:86-113）。③ 双 overload cuFileGetErrorString（:140-153）——cuFile 错误码可能是专用码或 POSIX errno：integral 版 IS_CUFILE_ERR 分诊再 strerror，结构体版追加 driver 串。④ 工具三函数 GetFileSize/parseInt/createTestFile（:170-185），实现在 `gds/samples/common/cufile_sample_utils.cc`。

三件套实现：GetFileSize 一次 fstat 失败返 0（`gds/samples/common/cufile_sample_utils.cc:24-28`）；parseInt 清 errno 后查 ERANGE/边界/尾字符（:30-47）；createTestFile 用 Prng 造随机字节填满再 fsync（:49-83）——随机数据让 SHA256 抓住错位读写。

五阶骨架：阶 1 various_mem_rw.cc 内存类型三选一（`gds/samples/1_cuFile_Basics/various_mem_rw.cc:62-78`），头注释点明 Managed 内存免注册、内部池经 cuMemcpyPeer 拷入（:13-16）；阶 2 many_buffers_set_bar.cc 双线程×64 buffer 演示 pin 池调参（`gds/samples/2_cuFile_Multithreaded/many_buffers_set_bar.cc:45-48`）；阶 3 batch_read.cc 走批量全生命周期 SetUp→Submit→GetStatus→Destroy（`gds/samples/3_cuFile_Batch/batch_read.cc:206-231`）；阶 4 async_rw_default.cc 默认流 cuFileReadAsync/WriteAsync（`gds/samples/4_cuFile_Async/async_rw_default.cc:161,177`）；阶 5 memmap_preregister.cc 对 cuMemMap 化指针直接 cuFileBufRegister（`gds/samples/5_cuFile_MemMap/memmap_preregister.cc:254,264`），VMM 编排抽到 `gds/samples/common/cufile_sample_memmap.cc:174,231`。Makefile wildcard 收全量（`gds/samples/Makefile:79-82`），模式规则产动/静双版本（:100-102），vectorAdd.cu 六档 gencode 预编译（:95-97）。

## 三、外部连接

公共头是 samples 子图 fanIn 之首（grep 实证 32/33 引用）。companion：`gds/samples/common/cufile_sample_shasum.cc` dlopen 运行时加载 libcrypto（:75），头文件里 SHA256_* 与 EVP_MD_CTX 两套函数指针（`gds/samples/include/cufile_sample_shasum.hpp:35-41`）是 OpenSSL 双代兼容证据；cufile_sample_memmap.cc 导出 fullCleanup 与 VMM 助手（`gds/samples/include/cufile_sample_memmap.hpp:128`）供阶 5 共享；bindings/python 包装为 Python 测试（见 03 篇）。上游依赖：CUDA、cufile.h（CUFILE_PATH 定位）、OpenSSL。图谱佐证：各样例 .cc 几乎全连公共头与 cufile.h；公共库三 .cc 进所有链接线。

## 四、数据流

以 many_buffers_set_bar.cc 走全程：① parseInt 解析 gpuid（:163）；② SetMaxPinnedMemSize 限 pin 池（:173）并 GetProperties 读回（:178）；③ 每线程独立 open(O_RDONLY|O_DIRECT)（:187）——O_DIRECT 是 GDS 硬前提（no_odirect_write.cc 演示缺它的退化）；④ 线程体（:58-148）：各自 cuFileHandleRegister（:75），GetFileSize 算 nr_ios（:105-108），64 buffer 逐个 cudaMalloc+cuFileBufRegister（:87-89），64 轮流式 cuFileRead（:114）；⑤ goto 跳清理标签逆序 Deregister+cudaFree（:127-139）；⑥ 读数经 promise/future 汇总（:141-147）。整链 Prng、错误宏、错误翻译全来自公共库——33 个样例的 main 几乎都是此模板的参数化变体。

## 五、设计决策

公共库抽在"恰好不挡教学"的粒度：只抽与 cuFile 无关的杂务，每样例的 cuFile 调用序列完整裸露。goto 清理而非 RAII 是刻意选择（README 原话），C 背景读者顺标签读懂释放顺序，RAII 版指给 bindings。错误宏双版本：单线程快速失败、多线程经 promise 上抛，避免 worker exit 杀全进程。SHA256 走 dlopen：libcrypto 版本不可控，探测双代符号最稳。Makefile 双产物：排除 so 版本漂移的 A/B 零成本；模式规则让新增样例零 Makefile 改动——与 gds-diag 注册表同构：加文件即注册。

## 六、新人提示

① KiB 口径陷阱（本目录最著名）：`gds/samples/2_cuFile_Multithreaded/many_buffers_set_bar.cc:47` 定义 MAX_PINNED_MEM_SIZE=KiB(128) 即 131072，:172 注释称"128 KiB"，:183 打印该值标注"bytes"。但按 cuFile API 文档，参数与属性口径均为 KiB：实际配置 128 MiB（注释错），打印值语义也是 KiB（标签错）——KiB() 与 API 口径叠加成双重换算，读输出先校单位。② 数据文件需 ≥128 MiB 且在 GDS 挂载点；tmpfs 类（gds-diag _PSEUDO_FS 黑名单）会走误导性降级。③ GetFileSize 失败返 0，nr_ios=0 静默"成功"读 0 字节——排查零 IO 先查 fd。④ createTestFile 填 char 截断随机字节，非密码学随机。⑤ 多线程样例先抄 devPtrs.fill(nullptr)（:62）这类防御初始化。⑥ batch 条目上限 128（`gds/samples/3_cuFile_Batch/batch_read.cc:18`）。⑦ memmap_thrust.cu 是唯一走 nvcc 显式规则的样例（`gds/samples/Makefile:106-108`），不依赖 vectorAdd.o。⑧ main 分支向后兼容老 cuFile，遇不存在的 API 先核对 README:13-16 的 tag 表。

---
自报：本文 3480 字（不计空格），完整路径行号锚 12 个。
