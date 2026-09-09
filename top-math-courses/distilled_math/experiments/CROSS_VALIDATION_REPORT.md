# CROSS_VALIDATION_REPORT — 第二教师（Qwen2.5-Math-7B-Instruct）交叉验证报告

> 2026-08-27 · B 阶段交付物 · 执行：13 节点 2×MetaX C500（vllm-metax 容器）
> 题集：[cross_claims.jsonl](cross_claims.jsonl)（24 题：18 真题=各卡 ★ 断言抽样 + 6 陷阱=§3 反例改造）
> 脚本：[cross_distill.py](cross_distill.py)（容器内 localhost:8001，SSE 流式，boxed 三层解析）

## 一、结论（14/24 可判定题）

| 指标 | 结果 | 解读 |
|------|------|------|
| **真题一致率** | **12/12 = 100%** | 第二教师与 GLM 教师在全部可判定 ★ 断言上零分歧——双教师独立收敛，交叉验证通过 |
| **陷阱判对** | 2/2（F02 对 + F05 教师认错） | 见下 |
| **教师错误被抓** | **F05：出题者（GLM）expected 标错** | G(n,1/2) 的 p=1/2 远超连通阈值 ln(n)/n，"几乎必然连通"**为真**；qwen 判 true 正确。教师误把"任意 p 都连通"的证伪意图错标到 p=1/2 这个命题为真的具体值上——**交叉蒸馏抓到教师第 3 次真实错误**（前两次：Courant-Fischer 公式方向写反、哑铃图 λ₁ 紧性归属，均为 L1 断言所抓） |
| 未判定 | 10 题（T04/T12/T14/T15/T16/T18/F01/F03/F04/F06） | 基础设施超时（见 §三），非分歧 |

**核心结论：可判定样本内两教师完全一致 + 教师出题错误被第二教师纠正一次——交叉验证的真正价值恰好体现在"抓教师"，而非"确认教师"。**

## 二、方法要点（复现者必读）

1. **qwen-math 的 \boxed{} 天性**：无视 JSON 输出指令，必以 `\boxed{\text{TRUE}}` 收尾——解析器三层设计（FINAL_JSON → boxed 抽取 → 尾部语义）是必须的；max_tokens ≥1024 否则长 CoT 截断丢 boxed。
2. **陷阱题设计是判别力校准**：无陷阱题的"全对"无信息量（可能全真偏好）；陷阱判对才有资格谈真题分歧。
3. **教师错误三连的共性**：三次全是"陈述本身为真/假的判断"类错误（公式方向/紧性归属/命题真值），而非计算类——**模型的判断型输出比计算型输出更需要独立验证**。

## 三、基础设施实录（13 节点 MACA，一手踩坑档案）

本轮 10 次引擎启动尝试，成功 3 次（旧容器内），失败 7 次。教训按价值排序：

1. **MACA 驱动队列泄漏（跨容器持久）**：强杀 vllm（pkill）后 `mxkwCreateQueueBlock ioctl failed`，容器重建（docker rm/run）+ `vllm_metax_init` + `--ipc=host` **均无法恢复**——队列泄漏在宿主内核驱动层。恢复手段待定（设备 reset/驱动重载需管理员，共享机不动）。**教训：MACA 上停 vllm 只用优雅手段，绝不 pkill 正在初始化的实例；init 中的实例被杀=该卡队列池可能永久损伤（直至宿主干预）**。
2. **pkill -f 自杀坑（重蹈 memory 案底）**：`pkill -f "port 8001"` 匹配执行它的 bash -lc 自身 → shell 被杀、后续命令静默不执行（两次"神秘失败"的真凶）。必须 `pkill -f "[p]ort 8001"`。
3. **vllm_metax_init 依赖**：容器重建后必须先跑（serve.sh 内置，手动 vllm serve 时易漏）；但 init 成功≠引擎能起（见 1）。
4. **断连恶性循环**：客户端 timeout 断连后 vllm 后台继续生成占槽 → 重试排队 → 更多超时。根治=SSE 流式接收（cross_distill.py 终版）。
5. **mv 嵌套陷阱**：目标目录已存在时 `mv A B` 会把 A 塞进 B/ 里而非合并——推送模型目录前必须 `rm -rf` 或 `rsync` 直达。
6. **rsync -az 对已压缩权重纯浪费 CPU**（safetensors 不可压）——用 `--whole-file` 裸推（push_model.sh 已固化，8MB/s 通道 15G 约 13 分钟）。
7. **hf-mirror 容器内直连不可靠**（Connection reset）——本仓正道=本机下载 + push_model.sh 推送。

## 四、遗留与恢复

- **剩余 10 题**：待卡资源恢复后一键续跑——`bash remote/exec.sh 'cd /root/luowz/distill_cross && python3 -u cross_distill.py'`（断点续传设计，有效记录自动跳过）。
- **Prover 服务（8000/8100）**：因卡队列池污染暂不可恢复，需宿主机管理员介入（设备重置或驱动重载）；恢复后 `bash remote/serve.sh` 一键拉起。
- **cross_results.jsonl**：14 条有效记录（远端 /root/luowz/distill_cross/ + 本地 /tmp/opencode/cross_final/ 备份）。
