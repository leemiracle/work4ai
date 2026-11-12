# 01 · miniapp/weather_app.cu —— HMM 零拷贝的 1.3TB 重炮实证

## 角色定位

weather_app.cu 是本仓唯一"真应用"：ERA5 40 年逐小时总降水数据的跨年聚合器，也是 CUDA 12.2 HMM（异构内存管理，非隐马尔可夫）主张的极限验证——1.3TB 输入从始至终零 cudaMemcpy，GPU 直接在 CPU 的 mmap 页面上读数。src/ 四 demo 证明"能做"，它证明"规模上成立"。配套：era5_preicp_nc_to_bin.py 预转换、miniapp/README.md 说明、Makefile 构建（miniapp/Makefile:6-8）。

## 内部结构

单文件 296 行，五个部件：

- **CUDA_CHECK 宏**（weather_app.cu:38）：错误即打印行号并退出。
- **`__constant__ month_day_boundary[13]`**（weather_app.cu:44）：闰年月界 {0,31,60,...,366}。
- **get_month_from_day_of_year**（weather_app.cu:46-62）：手写二分查 day-of-year 归属月。
- **construct_yearly_histogram**（weather_app.cu:64-115）：聚合 kernel，366x24x721x1440≈91.2 亿线程，每线程累加一个(日,时,格点)跨年份；`(i*12+month)*aligned_month_file_map_offset` 直算跨年同月文件偏移（weather_app.cu:99）；非闰年 2/29 特判在 weather_app.cu:103。
- **main**（weather_app.cu:117-295）：VA 预留→逐月 MAP_FIXED→launch→cub 归约→写 CSV/bin→收尾。

## 外部连接

上游 era5_preicp_nc_to_bin.py：netCDF4 逐月读入 `ds["tp"]` 后 `tofile` 裸 float 落盘（era5_preicp_nc_to_bin.py:44-46），年份 1981-2020 硬编码（:28-29）。命名两侧严格对齐：python strftime `'e5.accumulated_tp_1h.%Y%m'`（:39）↔ cu 侧 `sprintf "%d%02d.bin"`（weather_app.cu:156）。miniapp/README.md:5 给 CDS 下载入口与 721x1440/480 文件/≈1.3TB 规模，:11 给三参数用法。库依赖仅 cub 的 DeviceReduce（weather_app.cu:27）；与 src/ 零耦合。

## 数据流

main 先算月文件上界 ≈3.09GB 并取整到 2MB 倍数（weather_app.cu:135-137），匿名 `mmap(PROT_NONE)` 预留整段 VA（weather_app.cu:147）；40 年 x12 月循环：open→`mmap(...,MAP_FIXED,fd,0)`（weather_app.cu:174）→assert 落点（:182）→步长推进（:183）。kernel 把 `va_alloc` 强转 `float*` 当输入指针（weather_app.cu:207-209）——GPU 读的就是 CPU 页缓存里的文件内容。输出直方图 ≈34GiB（366x24x721x1440 个 float）走 cudaMalloc（weather_app.cu:191-194）。host 后处理逐月/日/时调 `cub::DeviceReduce::Sum`：先 NULL 探询临时存储字节数（weather_app.cu:239），再 `malloc` 直接喂 cub（:241，行尾注释 `// use HMM B-)`），GPU 把归约结果写回 host 栈数组（:243 同步）。最终落盘 processed_log.csv（weather_app.cu:222）与 yearly_aggregates.bin（:271-272）。

## 设计决策

1. **2MB 对齐三重动机**：MAP_FIXED 要求页对齐；等距布局让 kernel 单乘法寻址任意年月（weather_app.cu:99）；注释 "probably need 2 MB pages for perf"（weather_app.cu:172）——大页降 TLB 压力，HMM 下缺页代价高。
2. **统一闰年 366 布局**：非闰年 2/29 跳过累加（weather_app.cu:103-107），host 侧同值镜像表（weather_app.cu:221）——文件按真实月长存、索引统一 366 布局，两层解耦。
3. **malloc 直供 cub 是全文题眼**：临时存储（malloc）与输出（host 栈数组）都不是显存指针，GPU 靠 HMM 直接读写（weather_app.cu:239-243）——`// use HMM B-)` 就是仓名的落地。
4. **cudaEvent 计时只围 kernel**（weather_app.cu:206-217），cub 后处理不计入，引用时注意口径。

## 新人提示

- 跑前自查：`nvidia-smi -q | grep Addressing` 得 HMM、空闲显存 >34GiB；目录参数必须以 `/` 结尾（weather_app.cu:157 裸拼接）。
- argv 不校验（weather_app.cu:126-128），少参直接段错误。
- cub 的 `num_items=(721/2)*1440`（整数除=360 行，weather_app.cu:235）只覆盖半张网格——复现博客数字必须带此口径。
- unmap 误用 argc 当文件数（weather_app.cu:282），靠 :291 整段 munmap 兜底；:145 多乘 sizeof(float) 预留 4 倍 VA——"能跑但别学"二连。
- 闰年只判 `year%4`（weather_app.cu:104），1981-2020 无伤，数据跨 2100 年要补整百年规则。
