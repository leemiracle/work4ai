# 讲透 NVIDIA/enroot

[NVIDIA/enroot](https://github.com/NVIDIA/enroot) v4.2.0——用户态容器运行时与镜像打包系统（无特权沙箱、无守护进程、HPC 场景 3-5 倍速 Docker 导入、makeself .run 离线分发、内建 GPU hook）。本目录为 understand 全链知识库产物。

## 全链状态表

| 阶段 | 状态 | 产物 |
|---|---|---|
| deepwiki | ✅ 100% | [deepwiki/](deepwiki/INDEX.md) |
| understand 图谱 | ✅ 226n/329e · 5 层 7 步 tour · validator 0 issues · fingerprints 88 文件 @ead3a25e | 仓内 `.understand-anything/knowledge-graph.json` |
| onboarding | ✅ 8 节 ≥3000 字 | [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md) |
| explain | ✅ 3 篇（微仓一体通道口径） | [explain/](explain) |

产物索引：ONBOARDING（五工具链/bundle↔runtime 互引/glibc 兼容盲域/hooks/dogfooding 自举）· explain 01 五工具链（bin/ C 二进制族+libbsd）· 02 bundle-runtime 互引与 glibc 兼容 · 03 hooks 体系与自举打包。批阶段甄别笔记 19 条见仓内 `.understand-anything/NOTES-DIGEST.md`。

## 源码级勘误与图谱盲区清单（读码/引用前必读）

1. **`#ifdef __GLIBC__` 全盲域**：`bin/compat.h:30` 起整个条件编译块 tree-sitter 零提取（手写 getmntent_r/lastlog 兼容层），图谱该域函数节点（compat_getmntent_r `:75`、struct compat_lastlog `:116`）全部为批阶段源码手补——引用行号前建议 sed 复核。enroot 以 musl 静态编译，**运行时实际永远走手写分支**，glibc 宏直通（`:31-32`）是为 FORCE_GLIBC 构建保留的死常态路径。
2. **bsd overlay 角括号 include 边界**：`bin/enroot-nsenter.c:51-52`、`bin/enroot-switchroot.c:44-47`、`bin/enroot-mount.c:35` 的 `#include <bsd/xxx.h>` 角括号形式指向 overlay 目录（`deps/Makefile:47` -isystem libbsd/include/bsd 注入），与外部系统头同形——scanner 对「仓内文件用角括号引用」的解析有盲区，这部分依赖边为手补。
3. **include_next 自环弃置**：`deps/libbsd/include/bsd/inttypes.h:28`、`unistd.h:31`、`sys/cdefs.h:47` 等 overlay 头用 include_next 链系统同名头，图谱中该边指向不存在的系统节点、按自环/悬空弃置——libbsd overlay 与系统头的真实依赖关系不在图内。
4. **`.in` 模板后缀盲**：`enroot.in`（858 行、fanIn=18 全仓最高）与 `conf/enroot.conf.in` 构建期才 sed 生成（`Makefile:124-126`），提取器对 .in 后缀全盲，enroot.in 的 21 个函数节点（config::export `:27`、config::load `:31`、config::init `:50` 等）为源码手补。
5. **tree-sitter static struct/函数误判**：`deps/libbsd/src/fparseln.c:71` fparseln（static 修饰+BSD 风格签名）未提取，源码手补；compat.h 的 static inline 函数族同理——「static 全家桶」是本工具链稳定盲区。
6. **enroot-makeself 非自研**：`src/runtime.sh:709` 调用的 `enroot-makeself` 是上游 makeself/makeself.sh 的改名安装（`deps/Makefile:35`），不要在仓内找 makeself 实现。
7. **图谱 L02「hooks 层」fileCount=0**：分层产物怪象——conf/hooks/ 的 8+4 个 hook 文件节点实际散落在 L01/L05 代表集中，L02 是空壳层名；检索 hook 直接按 conf/hooks/ 路径走。
8. **权限模型易误读**：enroot「无特权」指无 setuid-root 无守护进程，但两个辅助二进制带 file capabilities（`Makefile:173-175`：mksquashovlfs=cap_sys_admin、aufs2ovlfs=cap_sys_admin,cap_mknod），deb/rpm 的 postinst/prerm 对称 setcap/回收——说「完全无特权运行」时要带上这个注脚。

## 快速上手

源码在 `/usr-data/data2/repos/agent-repos/NVIDIA/enroot`。主线一条：`docker://URI → docker::import（src/docker.sh:453）→ .sqsh → create（落盘）/load（FUSE 内存）→ start 三阶段装配 → nsenter → switchroot`；旁路 export 反压 .sqsh、bundle 打 .run 离线出走。详见 ONBOARDING §8。
