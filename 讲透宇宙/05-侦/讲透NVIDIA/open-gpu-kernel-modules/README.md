# 讲透 open-gpu-kernel-modules（ogkm）

> NVIDIA GPU 开源内核驱动（GPL 侧），实测版本 **615.71.09**。本目录=understand 全链知识基座（**历史第一大图谱**+onboarding+explain 12 篇）。

## 全链状态表

| 阶段 | 状态 | 产出 |
|---|---|---|
| understand 图谱 | ✅ 2026-11-07 | 仓内 `.understand-anything/knowledge-graph.json`：**16795n/35744e/16 层/16 步 tour，validator 0/0，fingerprints 4000@61dcc937**（超 vLLM 14454n，understand 系列历史第一大图谱） |
| onboarding | ✅ 2026-11-07 | `onboarding/ONBOARDING.md`（8 节 12227 字不计空格，45 锚+8 处抽验全中） |
| explain 12 篇 | ✅ 2026-11-07 | `explain/01-12` 合计 **66733 字符不计空格**，全量抽验 **91 锚 0 真坏**（1 basename 短名歧义归位命中） |

## 战况（181 批，四会话接力）

b1-18 前任遗产（3687n）→ a2f-sdk 段 b53-60（免费增量）→ 本会话 19-52/61-181（约 129 批四 worker 滚动）。两次 1308 团灭+多次 1302，全部死前落盘+SendMessage 复活零重做。全量终验：443 件 json.load 全合法/16793 ID 零重复/4000 文件全覆盖零缺失；merge 仅 2 悬空边（跨批 inherits/calls，手术补建 2 节点回补）。

## 甄别精选（源码级实证，worker 纠错实录）

1. **nvidia.ko 主入口走 rm_\* 家族而非 nvGpuOps\***（nv.c:1667 vs nv_gpu_ops.h:54）——w3 记忆错误被 onboard 代理按源码双向钉版
2. **本版本无 nvidia.c/nv-frontend.c**——前端已合并为 nv.c+nv-pci.c（explain 组1 纠任务书）
3. **NVOC 薄壳实测 149/209**（批分析初判 123/200 被 explain 精化）——123/200 是 133-140 段口径
4. **五个无扩展名 shader 微码=裸二进制经 xz+objcopy 嵌入**（modeset Makefile:202-215）
5. **GspRmBoot_GB202 36555 行 C 数组=全仓最大单文件**；kernel_mig_manager.c 10280 行=最大源文件；kmigmgrCreateComputeInstances_VF 单函数 5675 行
6. **g_allclasses.h=RM 类 ID→头文件唯一映射点（barrel）**；g_rpc-structures.h 12367 行=GSP-RM RPC 契约三巨头之一
7. **NDA 域头 4 个被引用但仓内不存在，全部带宏守卫**（kernel_sec2.c:39 等）
8. **NVSwitch 驱动编入 nvidia.ko**（组2 深挖发现）
9. C 仓 scanner 盲区极端实证：149-164 两段 scanner include 边=0，全手扫 5446 条（四 worker 累计）；NVOC RTTI 伪类（CLASS_DEF/CASTINFO/EXPORT_INFO）过滤钉版
10. **混合模块模式钉版（组2 跨篇甄别）**：开源构建的 nvidia.ko 主体在闭源 `nv-kernel.o_binary`（nvidia-modeset.ko 同理）——**本仓 83k 行开源源码是参考实现而非装机实体**；NVSwitch 主体同在闭源核（开源 83k 行=参考实现）
11. DisplayPort 库 45900 行 C++：EventSink 44 方法 43 纯虚（"33 类"口径无对应按实测表述）；ConnectorImpl 四重继承枢纽（dp_connectorimpl.h:94）
12. swref 实测 **11 个 GPU 代际**目录 429 头（"六代际"按实测修正）；hypervisor 四家适配在 virtualization/hypervisor/ 子树（CPUID 签名识别）

## 分层架构速览（16 层）

构建 37 · 第三方 115 · libspdm 126 · RM 支撑库 139 · **NVOC 生成层 481** · swref 429 · class 307 · ctrl+SDK 268 · **RM 内核核心 402** · 显存 MMU 228 · 引擎子系统 324 · GSP+虚拟化 190 · 显示通道 342 · nvidia.ko 181 · UVM 222 · NVSwitch-NVLink 209

## 与 CUDA-Stack-RE 战役的关联

ogkm 是 CUDA 栈逆向战役（work4ai/讲透CUDA-Stack-RE/）的内核侧开源对照物：GPL 内核壳+闭源 GSP 固件 blob 的双许可证架构=逆向侧"libcuda 巨石"的内核镜像；UVM/modeset/NVSwitch 线与用户态栈（libcuda/NCCL）在 API 面互为表里。

*2026-11-07 凌晨 · cuda-stack-第七轮会话（舰队 ogkm-61-181 段属主）*
