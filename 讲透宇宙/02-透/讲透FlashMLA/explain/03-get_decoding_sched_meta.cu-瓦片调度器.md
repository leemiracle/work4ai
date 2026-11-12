# csrc/smxx/decode/get_decoding_sched_meta/get_decoding_sched_meta.cu 精讲

> 原文件：`csrc/smxx/decode/get_decoding_sched_meta/get_decoding_sched_meta.cu`（116 行）

## ① 角色定位

**瓦片调度器**——解码"两阶段 splitKV"的第一阶段。各序列 KV 长度差异巨大，按序列分配 SM 会严重倾斜；这个 116 行小内核把全部工作切成 `num_sm_parts` 份**负载均等的 SE（schedule enumeration）线索引**，让每个 SM 分到的 KV block 数近似相同。跨 sm90/sm100 共享（故在 `smxx` 目录）。

## ② 内部结构

单个 `get_mla_metadata_kernel`，`<<<1, 32>>>`——**一个 block、一个 warp**（`__launch_bounds__(32,1,1)`），动态 shared memory 开 `sizeof(int)*(b*5+1)`（110 行），手工切五个数组：`num_blocks[b]`、`num_splits[b+1]`、`seqlens_k[b]`、`first/last_block_idx[b]`（21-26 行）。输出 `DecodingSchedMeta`（定义在 `params.h`：`begin/end_req_idx`、`begin/end_block_idx`、`begin_split_idx`、`is_first/last_req_splitted`）。

## ③ 外部连接

输入 `GetDecodeSchedMetaParams` 由 api 层组装，携带 `b/s_q/block_size_topk/fixed_overhead_num_blocks/topk/extra_topk/topk_length` 等。输出两件：`tile_scheduler_metadata_ptr`（每 SM 一条 SE 线）与 `num_splits_ptr`（前缀和，长 b+1）。主解码内核按 blockIdx 索引自己的 SE 线；combine 用 `num_splits[batch]..[batch+1]` 找回该序列所有 split。

## ④ 数据流

① 32 线程条带扫描序列：dense（`topk==-1`）读真实 `seqlens_k[i]`；sparse 用 `topk_length[i]` 或常数 topk，`cur_s_k==0` 钳到 1 保主循环非空，有 extra KV 则先 ceil 到 block 对齐再加 `extra_topk_length`。② 每序列算 `num_blocks = last-first+1`，累加 `num_blocks + fixed_overhead_num_blocks` 到 total（fixed_overhead 补偿每序列固定启动开销）。③ warp shuffle 归约 total。④ **thread 0 串行装箱**（61-99 行）：`payload = ceil_div(total, num_sm_parts) + fixed_overhead`，顺序遍历序列——装得下就整段吃掉推进 `now_req_idx`；装不下则切 `remain_payload - fixed_overhead` 个 block，`now_n_split_idx++`，本条 SE 线结束。每条线写一个 `DecodingSchedMeta`，标注起止序列/块/split 序号及首尾序列是否被劈开。⑤ 100 行 `FLASH_DEVICE_ASSERT` 装箱完备性兜底。⑥ warp 把 num_splits 前缀和写回 global。

## ⑤ 设计决策

- **单 warp 就够**：工作量正比于 batch 与 num_sm_parts（几十到几百），GPU 侧算可留在 stream 里、避免同步回宿主；thread 0 串行段规模完全可接受。
- **贪心等额切分**：以 block 为单位、payload 取上整，允许一个 fixed_overhead 的误差，换来线性复杂度；`is_first/last_req_splitted` 让主内核正确处理边界序列被两个 SM 各算一半的 LSE 归并。
- **dense/sparse 统一**：只在"有效长度从哪来"分叉，装箱逻辑共享。
- **空序列防御**：`seqlens_k==0` 会产生 1 个 block 留待后续修正，空序列也有合法元数据。

## ⑥ 新人提示

1. 配套读 `params.h` 的 `DecodingSchedMeta` 注释，闭开区间约定是理解主内核寻址的钥匙。
2. 改 `num_sm_parts` 公式时保持不变量：payload ≥ 任意单序列 blocks + fixed_overhead。
3. 该 kernel 每个新形状只跑一次，调试可打印 num_splits 前缀和验证装箱。
