# invisible-playwright 深读卡 —— 引擎级反检测浏览器：C++ 层 Gecko 补丁 + 贝叶斯一致指纹 + 人类化输入

> **定位**：feder-cr 出品的 Python 包装器——**定制补丁的 Firefox 二进制**提供 100% Playwright API 兼容，同时通过高级浏览器指纹/机器人检测（Cloudflare/DataDome 等）。反直觉差异化：不做 JS 层 `Object.defineProperty` 覆写（检测器能识别"谎言"），而是 **Gecko 引擎 C++ 层补丁**——伪造值与原生行为无法区分；每次会话生成**贝叶斯网络驱动的逻辑一致指纹**（GPU/屏幕/字体/音频硬件特征自洽）；点击/悬停走贝塞尔曲线+人类时序。
> **本地**：`repos/invisible-playwright`（feder-cr/invisible_playwright）｜**深读**：deepwiki 33 子页归档 `deepwiki/invisible-playwright/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 引擎层 | 补丁 Firefox | Gecko C++ level patches（GPU/screen/fonts/audio 引擎内伪造） |
| 指纹层 | 会话一致指纹 | Bayesian network profile 生成（docs/pinning.md） |
| 输入层 | 人类化操作 | Bezier 曲线路径 + 人类时序 + trusted events |
| API 层 | Playwright 兼容 | Python wrapper（与 playwright 库 API 全等） |

## 二、核心机制

1. **引擎级 vs JS 级**：检测器的核心手法是验证属性一致性（JS 覆写的值会被一致性测试戳穿）——invisible_playwright 直接在 Gecko C++ 源码层设值，页面内无注入痕迹，"谎言"在引擎层就是真话。
2. **贝叶斯一致指纹**：GPU/屏幕/字体/音频各维度非独立随机，而是按真实硬件相关性（贝叶斯网络）联合采样——避免"4GB 显存+8K 屏幕"这类不可能组合。
3. **人类化输入**：轨迹（贝塞尔）+时序（人类节奏）+事件签名（trusted events）三重拟人。

## 三、与讲透系列的对位

| 概念 | 讲透系列对应概念 |
|---|---|
| 浏览器反检测 | 讲透Agent/02 §浏览器工具（steel 云浏览器/这个本地隐身路线对照） |
| 贝叶斯一致采样 | 讲透概率图模型 §贝叶斯网络（真实工程应用！） |

## 四、关键入口

```
invisible_playwright/     # Python 包（API=playwright）
docs/pinning.md           # 指纹一致性设计文档
```

## 五、深读子页地图（33 页精选 4）

Overview（vs 标准 Playwright 对比表）｜Engine Patches｜Fingerprint/Pinning｜Humanized Input。

## 六、与"我们"的关系（一句话）

浏览器 Agent 工具箱的"隐身件"——与 steel（云托管）、actionbook（手册资产化）合讲"浏览器自动化三路线"；贝叶斯指纹还是概率图模型的罕见工程落地案例。

---
生成：2026-08-21 · deepwiki 33 页全归档
