# 讲透 NVIDIA/Ising

NVIDIA Ising 量子计算工具族的**中央导航仓**：仓库本体仅 LICENSE、README.md（106 行）、SECURITY.md（24 行）三文件，零代码——README 即产品（README.md:9 "central landing page"），正文全是外链索引。

## 家族地图（README.md 实证）

- **Models 6 个**（README.md:30-37）：Calibration 系 VLM 三个（1.5-31B-BF16 / NVFP4 / 1-35B-A3B，理解量子校准图）+ Decoder 系 AI 预解码器三个（ColorCode-1-Fast 2.94M / SurfaceCode-1-Accurate 1.79M / SurfaceCode-1-Fast 0.91M）；全集入口 HF nvidia-ising collection（README.md:39）。
- **NIM 2 个**（README.md:44-47）+ **托管 API 1 个**（README.md:55）+ **cookbook 2 篇**（README.md:80-85，predecoder 训练/推理/量化教程等）。
- **代码仓 3 个**（README.md:68-72）：Ising-Decoding（解码训练样本）、Quantum-Calibration-Agent-Blueprint（校准 VLM agentic 蓝图）、QCalEval（评测基准）——代码不在本仓，读源码去这三处。
- **治理**：全家族 issue 汇聚本仓（README.md:90-94）；安全漏洞走 SECURITY.md 的 PSIRT 私有披露，禁公开 issue。

## understand 适用性说明

图谱仅 **2 节/1 边/2 层/2 步**（`document:README.md`+`document:SECURITY.md`，fingerprints 2 @ 8d1bd74a）：纯导航仓无源码可供 file/function/class 层分析，onboarding/explain **无适用对象**，属流水线正常裁剪。知识层看 **DeepWiki**：`deepwiki/` 15 页 TRUE_100，收录 HF 模型卡与 Ising-Decoding 训练框架等外部资产的结构性叙述，为了解 Ising 族首选入口。

## 小勘误（3 条 @ 8d1bd74a）

1. README.md:71 "**Comptuer**" 拼写错误（Computer 拼反）。
2. README.md:47 NIM 描述写 "Ising-Calibration-**1**"，实际对应 1-35B-A3B 容器，与 1.5 系列口径混用。
3. 链接大小写不一：README.md:70 `Ising-Decoding` vs :80 `ising-decoding`。

| 产物 | 状态 |
|---|---|
| DeepWiki | ✅ 15 页 TRUE_100（`deepwiki/`） |
| understand 图谱 | ✅ 2n/1e/2 层/2 步（文档层，适用性见上） |
| onboarding/explain | ➖ 不适用（纯导航仓） |
