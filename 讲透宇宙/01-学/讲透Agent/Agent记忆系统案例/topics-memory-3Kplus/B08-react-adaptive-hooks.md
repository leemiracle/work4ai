# B-08 `GoogleChromeLabs/react-adaptive-hooks`（5.2K★）[结构档-未克隆]
> 来源：deepwiki（索引 2025-04-20, baad29）+ GitHub README/tree + **raw 源码（memory/index.js 已核原文）** ｜ JavaScript/React ｜ Apache-2.0
> 一句话定位：按**设备能力自适应加载**的 5 个 React hooks——其中 `useMemoryStatus` 封装 Device Memory API，是"环境感知降级"的最小可行示范

## 1. 定位与形态
- 仓库极小（tree 实证 25 条目）：每 hook 一目录（`network/ save-data/ hardware-concurrency/ memory/ media-capabilities/`，各含 index.js + 测试），根 `index.js` 汇出。
- 五个 hook（deepwiki Available Hooks）：
  1. `useNetworkStatus`：Network Information API 的 effectiveConnectionType（4G/3G/2G...）；
  2. `useSaveData`：浏览器省流模式开关；
  3. `useHardwareConcurrency`：逻辑 CPU 核数；
  4. `useMemoryStatus`：**设备内存（deviceMemory）**；
  5. `useMediaCapabilitiesDecodingInfo`：媒体格式解码能力。

## 2. 架构与核心模块
### 2.1 useMemoryStatus 源码全文已核（raw memory/index.js，45 行，非转述）
```js
let unsupported;
if (typeof navigator !== 'undefined' && 'deviceMemory' in navigator) {
  unsupported = false;                    // 能力探测：模块加载时一次性判定
} else {
  unsupported = true;
}
let memoryStatus;
if (!unsupported) {
  const performanceMemory = 'memory' in performance ? performance.memory : null;
  memoryStatus = {
    unsupported,
    deviceMemory: navigator.deviceMemory,          // 设备近似 RAM
    totalJSHeapSize: performanceMemory ? ... : null, // JS 堆三指标
    usedJSHeapSize: ...,
    jsHeapSizeLimit: ...
  };
} else {
  memoryStatus = { unsupported };         // 显式降级标志
}
const useMemoryStatus = initialMemoryStatus => {
  return unsupported && initialMemoryStatus
    ? { ...memoryStatus, ...initialMemoryStatus }  // 不支持时合并调用方初始值
    : { ...memoryStatus };
};
```
- 数据合成：`navigator.deviceMemory`（设备总量，粗）+ `performance.memory`（JS 堆实际用量，细）合并为单一快照。
- 快照在**模块加载时算一次**，hook 每次渲染只做对象拷贝——环境能力基本不变，无需重复探测。

### 2.2 通用实现模式（deepwiki Hook Implementation Pattern，引 README.md:38-109,162-196）
- 所有 hook 共享三段式：检查 API 支持 → 模块级快照 → 不支持时返回 `unsupported` 并接受调用方初始值兜底。
- SSR 支持：初始值参数 + UMD 构建（`dist/index.umd.js`）；Next.js 建议 next-transpile-modules（README.md:290-305）。
- 浏览器兼容（deepwiki 表，引 README.md:308-320）：deviceMemory 仅 Chrome 63+/Opera 50+/Edge；performance.memory 仅 Chromium；其余 hook 覆盖面更广。

### 2.3 用法模式（deepwiki Adaptive Loading Patterns，引 README.md:200-288）
- 自适应资源加载（低内存设备发小图/低清视频）；
- 自适应代码分包（弱网/低端设备延迟加载重组件）；
- 渐进增强（核心体验全设备可用，强设备再加料）。

## 3. 与 Agent 记忆的可迁移机制
1. **deviceMemory 的阶梯量化**：Device Memory API 只报 0.25/0.5/1/2/4/8 GiB 的**近似阶梯值**（规范为防指纹攻击故意粗化，上限 8）——Agent 记忆预算也应阶梯量化而非精确字节：预算档位（tiny/small/large）驱动策略切换，够用且稳健。
2. **三段式降级契约**：探测 → 显式 `unsupported` → 接受调用方初始值。记忆系统探测后端能力（向量库有无？嵌入维度支持？）失败时返回显式"不支持"而非静默空结果，并接受默认配置——SSR 初始值 = 记忆冷启动默认配置的对应物。
3. **静态快照缓存**：环境画像（上下文窗口大小、可用工具集、设备档位）会话级缓存一次，不逐次探测。
4. **双源合成指标**：总量预算（deviceMemory 型）+ 当前占用（usedJSHeapSize 型）双指标并报——记忆压力感知的最小充分统计。
5. **自适应加载范式**：记忆策略随环境降级（低内存 → 只保摘要不保原文；弱网 → 本地缓存优先；低端 → 跳过重排）。

## 4. 局限
- deviceMemory/performance.memory 均 Chromium 私有且标准化停滞（W3C 提案未过），Firefox/Safari 无；
- 库为实验演示性质（测试极薄，2019 后低维护），生产需 fork 自维；
- 结构档：仅 memory/index.js 逐行核过，其余 hook 依赖 deepwiki/README 描述。
