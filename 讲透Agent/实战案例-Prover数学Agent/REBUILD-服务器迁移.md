# aiz-work 恢复作战文档（重装后按此复活）

> 生成：2026-08-25 · 服务器重装前抢救打包 · 配套本地仓：work4ai 讲透Agent/实战案例-Prover数学Agent/
>
> **⚡ 2026-08-26 状态更新**：本包已整体迁移至 **13 节点 `/mnt/200/lwz/aiz-work/`**（沐曦 MACA 环境，操作规约见 [`remote/README.md`](../../../remote/README.md)）。下文"复活 8 步"针对 18 节点 DCU/rocm 镜像——**13 节点 MACA 环境不再加载该镜像**（改用 vllm-metax）；但包内 `csmath/models`（31G 模型）与 `lean-4.21.0-linux` 仍是活资产（只读挂载进新容器）。`sitepkgs_custom.tar.gz` 为 DCU 定制 torch，MACA 容器**勿装**。

## 一、资产清单（/root/aiz-work/）

| 路径 | 大小 | 内容 | 必要性 |
|---|---|---|---|
| `csmath/` | 43G | 原 /root/csmath bind mount 全量：models(31G, 含 DeepSeek-Prover-V2-7B) + lean-4.21.0-linux(1.8G,x86) + distill 流水线 + prover-smoke | 🔴 核心 |
| `kylin_vllm_hip_v0.23.0-0805.tar` | 28.5G | docker save 的基础镜像（含 vllm0.23.1 rocm633 / flash_attn dtk2604 / transformers 5.12 / DTK 栈全套） | 🔴 核心 |
| `sitepkgs_custom.tar.gz` | 960M | 容器层定制包：torch 2.9.0a0+git1fa9f34 / torchvision / triton 3.5.1 / **numpy 1.26.4**（torch 定制版 wheel 已失传，此处为唯一副本） | 🔴 核心 |
| `wheels/vllm-0.23.1rc1...rocm633...whl` | 46M | vllm 定制 wheel（镜像已自带同版，此处为保险） | 🟡 保险 |
| `wheels/pip_freeze.txt` | 185 行 | 完整 pip 清单 | 🟡 参考 |
| `csmath_inspect_final.json` / `csmath_inspect_backup.json` | - | 容器完整配置（设备映射/挂载/ENV） | 🟡 参考 |
| `csmath_dtk.env` / e12b/e13/mnist 等 | 小 | 历史实验产物 | 🟢 存档 |

## 二、重装后复活 8 步

```bash
# 1. 装 docker（KLAS 自带或 yum install docker-ce）
# 2. 载入镜像（约 3-5 分钟）
docker load -i /root/aiz-work/kylin_vllm_hip_v0.23.0-0805.tar

# 3. 启动容器（设备映射从 inspect_final 提炼：kfd/mkfd/dri + bind mount）
docker run -d --name csmath \
  --device /dev/kfd --device /dev/mkfd --device /dev/dri \
  -v /root/aiz-work/csmath:/work \
  --network host \
  kylin_vllm_hip:v0.23.0-0805 bash -c "sleep infinity"
# 注意：网络模式以 csmath_inspect_final.json 的 NetworkMode 为准（先 jq 查看）

# 4. 恢复容器层定制包（torch 2.9.0a0 + numpy 1.26.4，解压即用）
docker cp /root/aiz-work/sitepkgs_custom.tar.gz csmath:/tmp/
docker exec csmath bash -c "tar xzf /tmp/sitepkgs_custom.tar.gz -C /usr/local/lib/python3.11/"
docker exec csmath python3 -c "import torch,numpy; print(torch.__version__, numpy.__version__, torch.cuda.device_count())"
# 预期：2.9.0a0+git1fa9f34 1.26.4 1

# 5. 验证 Lean（x86 二进制）
docker exec csmath /work/lean-4.21.0-linux/bin/lean --version

# 6. 启动 vLLM（卡1！DCU 用 ROC_VISIBLE_DEVICES，不是 HIP_VISIBLE_DEVICES）
docker exec -d csmath bash -lc "ROC_VISIBLE_DEVICES=1 nohup vllm serve /work/models/DeepSeek-Prover-V2-7B --served-model-name prover --max-model-len 8192 --port 8177 > /work/prover-smoke/vllm_server_gpu1.log 2>&1 &"
# 等待 ~2 分钟后：curl -s http://127.0.0.1:8177/v1/models

# 7. 断点续跑蒸馏流水线（progress.json 记忆进度）
docker exec -d csmath bash -lc "cd /work/distill && nohup python3 distill_pipeline.py --problems problems_core.jsonl --out /work/distill/out > run_full.log 2>&1 &"

# 8. 语法约束解码实验（Needle 2 借法）
docker exec -d csmath bash -lc "cd /work/distill && nohup python3 prover_grammar_decoding.py --out /work/distill/grammar_exp > grammar_exp.log 2>&1 &"
```

## 三、五坑清单（血泪教训，勿重蹈）

1. **选卡**：`HIP_VISIBLE_DEVICES=1` → hipErrorNoDevice；DCU 正统是 **`ROC_VISIBLE_DEVICES=1`**
2. **numpy ABI**：绝不允许 numpy≥2.x（DCU torch 1.x ABI，vLLM 死于 buffer_utils.py:49）。环境被并行改动后先查 `ls -ld .../site-packages/numpy` 时间戳
3. **Lean 架构**：用 `/work/lean-4.21.0-linux/`（x86）；`/work/lean4`（aarch64）不可用
4. **pkill 自杀**：`pkill -9 -f vllm` 会杀自身 shell → 用 `pkill -9 -f "[v]llm serve"`
5. **网络间歇中断**：所有长任务必须 `nohup` + `docker exec -d` 保活；流水线自带 api 断连重试（绝不落死标记）

## 四、遗留状态（2026-08-25 14:10 中断时）

- 蒸馏流水线：24 题完成 6（e2-e6 done，e1 failed@decompose）；第 7 题起因服务器断电/容器 bind mount 迁移中断
- vLLM server：DOWN（容器 bind mount 源 /root/csmath 已 mv 至 aiz-work，重启后容器需按 §二 重建）
- 待跑：core 18 题剩余 → holdout 12 题 → finetune_lora SFT → eval_holdout 三方对照 → grammar 实验
