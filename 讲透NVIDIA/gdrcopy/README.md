# 讲透 gdrcopy（NVIDIA/gdrcopy @fcec3ce0）

GDRCopy：GPU 显存映射内核模块 `gdrdrv` + 用户库 `libgdrapi`。仓址 `/usr-data/data2/repos/agent-repos/NVIDIA/gdrcopy`。

## 全链状态表

| 阶段 | 产物 | 状态 |
|---|---|---|
| DeepWiki | `deepwiki/`（上游已收录） | ✅ 前轮完成 |
| understand 图谱 | 仓内 `.understand-anything/knowledge-graph.json`：224 节点/224 边/4 层/5 步 tour，validator 0 issues，fingerprints 81 文件 @fcec3ce0 | ✅ |
| NOTES 收割 | 仓内 `.understand-anything/NOTES-DIGEST.md`（14 条批阶段甄别笔记） | ✅ |
| onboard 输入 | 仓内 `.understand-anything/onboard-input.json`（73KB，4 层/5 步/hubs30） | ✅ 2026-11-07 |
| ONBOARDING | `onboarding/ONBOARDING.md`（8 节，非空白 6368 字符，file:line 锚 72/唯一 70） | ✅ |
| explain | `explain/01-内核驱动gdrdrv.md`（锚 40）/ `02-用户API与pin机制.md`（锚 35）/ `03-测试族与pplat手扫域.md`（锚 37），各 ~3000 非空白字符、六节结构 | ✅ |

字数口径：不计空格总字符（系列钉版口径；汉字数远小于该值属行号锚密度所致，见 DEEPWIKI-PIPELINE 备忘）。

## 源码级勘误与甄别清单（本轮钉版）

1. **`GDRCOPY_TEST` 宏展开的"同名函数"甄别**：`tests/sanity.cpp` 的 36 处 `GDRCOPY_TEST(` + 1 处 `GDRCOPY_EXTENDED_TEST(` 调用点不是函数，而是 `testsuites/testsuite.hpp:26`/`:37` 宏展开的"类定义+静态自注册对象+成员函数"三件套（用例总数 37，其中 1 个 EXTENDED 默认跳过）。tree-sitter 会把宏调用点识别成同名 `GDRCOPY_TEST` 结构——正确处置是不建节点（本图谱如此）。图内实际同名函数节点仅 5 组：`print_usage`×5、`main`×5、`show_help`×4、`run_test`×2、`ex`×2，均为不同二进制的合法同名，不是宏污染。
2. **三处（实为四处）操作表初始化误判类**：`gdrdrv.c:329`（`proc_dir_entry` 静态变量）、`gdrdrv.c:1464`（`gdrdrv_vm_ops`，vm_operations_struct 操作表）、`gdrdrv.c:1777` 与 `gdrdrv.c:1809`（两处 proc 参数 `file_operations`）——tree-sitter 报"类"，实为静态变量/操作表初始化，未建节点。图谱 5 个 class 节点（`gdr_mr`/`gdr_info`/`gdr_cuda_function_table`/`mt_test_info`/`Test`）全部为真实数据结构。
3. **`pplat.cu` 的 .cu 盲区 9 函数手补**：tree-sitter 不支持 CUDA C++，整文件零提取。图谱 9 个节点（4 个 `__global__` kernel `pplat.cu:50`/`:70`/`:107`/`:142` + `gh_mem_alloc`(:261)/`gh_mem_free`(:310)/`print_usage`(:326)/`check_timeout`(:355)/`main`(:378)）为人工源码手扫产物——该域行号锚勿用 scanner 复跑对账。
4. **`-I gdrdrv/` 是跨层 include 的唯一解释**：用户态 `src/gdrapi.c` include 内核共享头 `gdrdrv.h` 的边，scanner 因不解析 `src/Makefile:27` 的 `CPPFLAGS := ... -I gdrdrv/` 而漏报，已人工补边。读图见 gdrapi.c→gdrdrv.h 依赖勿以为是内核态代码。
5. **`include/gdrapi.h` 零函数体不是缺失**：纯声明头（公共 API 原型+typedef），tree-sitter 提取 0 函数属预期，勿当盲区回补。
6. **`config_arch` 是 bash 生成 C 的技巧**：无扩展名文件被 scanner 判 unknown；实际是 heredoc 写 C 源再编译执行探测架构（x86/arm64），产物回填 `GDRAPI_ARCH`（`src/Makefile:24`）。
7. **`cuda_wrapper.c` 函数表条目行号陷阱**：`gdr_cuda_function_table` 的 struct 定义在 `cuda_wrapper.c:45-48`，`cuda_wrapper.c:50` 的同名字段是变量声明——两处同源不同物。
8. **dkms.conf 的占位符**：`packages/dkms.conf` 的 `@FULL_VERSION@` 等在源码态不生效，由 `packages/build-deb-packages.sh` 打包时替换——按源码 grep 版本号会得到假值。
9. **版本语义三分**：内核 ABI 版本 2.6 在 `gdrdrv.h:31-34`（GET_VERSION ioctl 上报，`gdrdrv.c:1346` 赋值）；用户库最低兼容闸 `MINIMUM_GDRDRV_VERSION` 在 `gdrapi.c:132`；packaging 版本另在 changelog/dkms 替换链里。引用"gdrcopy 版本"须先说清是哪一层。

## 快速上手

- 全链走读：`onboarding/ONBOARDING.md`（8 节）
- 深读：`explain/01`（内核驱动）/ `02`（用户 API 与 pin）/ `03`（测试族）
- 图谱：仓内 `python3 -c "import json;kg=json.load(open('.understand-anything/knowledge-graph.json'));print(len(kg['nodes']),len(kg['edges']))"`
