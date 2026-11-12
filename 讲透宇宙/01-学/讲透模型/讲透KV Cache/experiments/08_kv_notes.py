#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
08 · KV Cache 不是一次性的：可编辑、可组合的"笔记" —— 实验脚本
================================================================
配套章节：../08-KV Cache不是一次性的：可编辑可组合的笔记.md
模型：Qwen2.5-0.5B-Instruct（CPU, float32）
适配 transformers 5.10 dev：cache.layers[i].keys / .values，形状 [1, kv_heads, seq, head_dim]

三组证据：
  E1 复用（摘抄）：前缀 KV 复用 vs 全量重算 → logits 一致 + 时间节省
  E2 组合（拼接）：增量组装 / 独立编码+RoPE 重旋转拼接 / 天真拼接 vs 全量重算
  E3 编辑（批注）：原地替换"密码"字段的 K/V（天真编辑） vs 追加勘误（erratum）
     —— 对应 arXiv:2606.17107 的核心发现：字段自身 KV 对决策贡献 <1%，结论已写入下游笔记

运行：python3 08_kv_notes.py   （模型路径可用环境变量 QWEN_PATH 覆盖）
"""
import copy
import os
import time

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers.cache_utils import DynamicCache

torch.set_num_threads(4)  # 实测多线程无收益，4 核够
MODEL_PATH = os.environ.get(
    "QWEN_PATH",
    os.path.expanduser("~/ai/models/Qwen2.5-0.5B-Instruct"),
)

# ---------------------------------------------------------------- 基础工具


def prefill_with_logits(model, ids):
    """完整 prefill，返回 (DynamicCache, 最后位置 logits)。"""
    cache = DynamicCache()
    with torch.no_grad():
        out = model(ids, past_key_values=cache, use_cache=True)
    return cache, out.logits[0, -1, :].float()


def prefill(model, ids):
    return prefill_with_logits(model, ids)[0]


def next_token_logits(model, ids, cache):
    """基于给定 cache 续算 ids，返回最后位置 logits（cache 会被扩展）。"""
    with torch.no_grad():
        out = model(ids, past_key_values=cache, use_cache=True)
    return out.logits[0, -1, :].float()


def greedy_continue(model, tok, last_logits, cache, n_new=12):
    """从"下一 token 分布"出发贪心生成（cache 需已包含全部前文）。"""
    token_ids = []
    logits = last_logits
    for _ in range(n_new):
        nxt = int(torch.argmax(logits))
        if nxt == tok.eos_token_id:
            break
        token_ids.append(nxt)
        with torch.no_grad():
            out = model(torch.tensor([[nxt]]), past_key_values=cache, use_cache=True)
        logits = out.logits[0, -1, :].float()
    return tok.decode(token_ids).strip()


# ---------------------------------------------------------------- RoPE 重旋转


def rope_inv_freq(head_dim: int, theta_base: float, device, dtype=torch.float32):
    """RoPE 逆频率：θ_j = base^(-2j/d)（Qwen2 的 half 配对约定）。"""
    return 1.0 / (theta_base ** (torch.arange(0, head_dim, 2, device=device, dtype=dtype) / head_dim))


def rotate_keys_by_delta(keys: torch.Tensor, delta: int, theta_base: float):
    """把已编码的 K（位置 p 已烘焙进旋转）额外旋转 delta 步 → 等价位置 p+delta。

    数学依据：RoPE 是逐 2D 子空间的旋转 R，R(p+Δ) = R(Δ)·R(p)，同子空间旋转可交换。
    keys: [1, kv_heads, seq, head_dim]
    """
    d = keys.shape[-1]
    ang = rope_inv_freq(d, theta_base, keys.device, keys.dtype) * float(delta)  # [d/2]
    cos, sin = ang.cos(), ang.sin()
    x1, x2 = keys[..., : d // 2], keys[..., d // 2:]
    return torch.cat([x1 * cos - x2 * sin, x1 * sin + x2 * cos], dim=-1)


def splice_caches(cache_a, cache_b, theta_base, re_rotate=True):
    """把 cache_b 拼到 cache_a 之后（A 前 B 后），返回新 cache。

    re_rotate=True ：B 的 K 平移 lenA 个位置——"可组合笔记"的正解（arXiv:2606.17107 的 splice）
    re_rotate=False：天真拼接，B 的 K 仍带着 0 起步位置——反面对照
    V 不带位置信息（RoPE 只作用于 Q/K）→ 无需旋转，这也正是 V 空间可自由编辑的原因。
    """
    new = copy.deepcopy(cache_a)
    for ln, lb in zip(new.layers, cache_b.layers):
        kb = rotate_keys_by_delta(lb.keys, new.layers[0].keys.shape[2], theta_base) if re_rotate else lb.keys
        ln.keys = torch.cat([ln.keys, kb], dim=2)
        ln.values = torch.cat([ln.values, lb.values], dim=2)
    return new


# ---------------------------------------------------------------- 主流程


def main():
    print(f"[模型] {MODEL_PATH}")
    tok = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, dtype=torch.float32)
    model.eval()

    # transformers 5.10：rope 参数在 config.rope_parameters；rotary_emb 挂在 model.model 上
    theta_base = float(model.config.rope_parameters.get("rope_theta", 1_000_000.0))
    print(f"[配置] layers={len(model.model.layers)} kv_heads={model.config.num_key_value_heads} "
          f"head_dim={model.config.hidden_size // model.config.num_attention_heads} "
          f"rope_base={theta_base:.3g}")

    # ================= E1 复用 =================
    print("\n" + "=" * 62)
    print("E1 复用（摘抄）：同一前缀服务多个问题")
    print("=" * 62)

    prefix = (
        "你是仓库管理助手。以下是仓库的规章制度，请严格遵守：\n"
        "1. 贵重物品必须存放在三号保险柜，钥匙由值班主管单独保管。\n"
        "2. 每天早上八点进行例行盘点，盘点表需要双人签字确认。\n"
        "3. 外来车辆不得进入装卸区东侧，装卸作业必须两人以上同时在岗。\n"
        "4. 冷链货物的温度记录每四小时填写一次，异常情况立即上报值班室。\n"
        "5. 消防通道在任何情况下都不得堆放货物，违者按安全条例处罚。\n"
        "6. 加班需要提前一天在系统里申请，未经审批的加班不计入工时。\n"
        "7. 每月末进行一次全库巡检，巡检路线为：入库区、存储区、打包区、发货区。\n"
        "8. 所有出入库单据必须当天录入系统，纸质单据保存三年备查。\n"
    )
    questions = [
        "问题：盘点表需要几个人签字？答案：",
        "问题：消防通道可以临时堆放货物吗？答案：",
        "问题：冷链温度记录多久填一次？答案：",
    ]
    p_ids = tok(prefix, return_tensors="pt")["input_ids"]
    n_prefix = p_ids.shape[1]

    t0 = time.perf_counter()
    cache_prefix = prefill(model, p_ids)
    t_prefix = time.perf_counter() - t0

    t_full = t_reuse = 0.0
    max_diff = 0.0
    ans0 = ""
    for qi, q in enumerate(questions):
        q_ids = tok(q, return_tensors="pt")["input_ids"]
        t0 = time.perf_counter()
        cache_full, lg_full = prefill_with_logits(model, torch.cat([p_ids, q_ids], dim=1))
        t_full += time.perf_counter() - t0
        t0 = time.perf_counter()
        c = copy.deepcopy(cache_prefix)
        lg_reuse = next_token_logits(model, q_ids, c)
        t_reuse += time.perf_counter() - t0
        max_diff = max(max_diff, (lg_full - lg_reuse).abs().max().item())
        if qi == 0:
            ans0 = greedy_continue(model, tok, lg_full, cache_full, 10)

    print(f"前缀 {n_prefix} tokens，prefill 一次 {t_prefix*1000:.0f} ms")
    print(f"3 问全量重算 {t_full*1000:.0f} ms vs 复用前缀 {t_reuse*1000:.0f} ms"
          f"（省 {100*(1 - t_reuse/t_full):.0f}%，不含一次性 prefill）")
    print(f"logits 最大绝对差（复用 vs 重算）= {max_diff:.2e}")
    print(f"问题[0] 生成答案: {ans0!r}")

    # ================= E2 组合 =================
    print("\n" + "=" * 62)
    print("E2 组合（拼接）：两段独立编码的 KV 拼在一起")
    print("=" * 62)

    doc_a = (
        "阿波罗十一号飞船在一九六九年七月二十日登陆月球，第一位踏上月面的宇航员是阿姆斯特朗。"
        "他在月面停留了约两个半小时，说出了那句著名的话：这是我个人的一小步，却是人类的一大步。"
        "登舱段随后与指令舱对接，三名宇航员全部安全返回地球。"
        "这次任务是美国阿波罗计划的第五次载人任务，也是人类历史上第一次成功的载人登月。"
    )
    doc_b = (
        "这次任务共带回了约二十一公斤的月球岩石样本，其中一部分后来赠送给了其他国家。"
        "科学家通过对这些样本的分析，确认了月海区域主要由玄武岩构成。"
        "样本中还含有一种后来被命名为阿姆石的新矿物，它是人类在月球上发现的第一种新矿物。"
        "这些岩石样本至今仍在被研究，为理解月球的形成历史提供了关键证据。"
    )
    questions2 = {
        "问A(信息在A段)": "问题：谁第一个踏上月面？答案：",
        "问B(信息在B段)": "问题：任务带回了大约多少公斤的月球岩石？答案：",
    }

    for qname, question in questions2.items():
        full_text = doc_a + doc_b + question
        enc = tok(full_text, return_offsets_mapping=True, return_tensors="pt")
        offs = enc["offset_mapping"][0].tolist()
        cut_a = next(i for i, (s, _) in enumerate(offs) if s >= len(doc_a))
        cut_b = next(i for i, (s, _) in enumerate(offs) if s >= len(doc_a) + len(doc_b))
        ids_full = enc["input_ids"]
        ids_a, ids_b, ids_q = ids_full[:, :cut_a], ids_full[:, cut_a:cut_b], ids_full[:, cut_b:]
        assert torch.equal(torch.cat([ids_a, ids_b, ids_q], dim=1), ids_full)
        if qname.startswith("问A"):
            print(f"段长 A={ids_a.shape[1]} B={ids_b.shape[1]}（offsets 切分，拼回逐 token 一致）")

        cache_ref, lg_ref = prefill_with_logits(model, ids_full)
        ans_ref = greedy_continue(model, tok, lg_ref, cache_ref, 8)

        cache_inc = prefill(model, ids_a)
        lg_inc = next_token_logits(model, torch.cat([ids_b, ids_q], dim=1), cache_inc)
        ans_inc = greedy_continue(model, tok, lg_inc, cache_inc, 8)

        cache_a = prefill(model, ids_a)
        cache_b = prefill(model, ids_b)
        cache_splice = splice_caches(cache_a, cache_b, theta_base, re_rotate=True)
        lg_sp = next_token_logits(model, ids_q, cache_splice)
        ans_sp = greedy_continue(model, tok, lg_sp, cache_splice, 8)

        cache_naive = splice_caches(cache_a, cache_b, theta_base, re_rotate=False)
        lg_nv = next_token_logits(model, ids_q, cache_naive)
        ans_nv = greedy_continue(model, tok, lg_nv, cache_naive, 8)

        def cos(a, b):
            return torch.nn.functional.cosine_similarity(a, b, dim=0).item()

        print(f"\n--- {qname} ---")
        print(f"  全量重算  : {ans_ref!r}")
        print(f"  增量组装  : {ans_inc!r}  (cos={cos(lg_inc, lg_ref):.6f}，位置连续→逐位等价)")
        print(f"  重旋转拼接: {ans_sp!r}  (cos={cos(lg_sp, lg_ref):.4f}，缺跨块注意力→接近但不等)")
        print(f"  天真拼接  : {ans_nv!r}  (cos={cos(lg_nv, lg_ref):.4f}，位置错乱→不可控劣化)")

    # ================= E3 编辑 =================
    print("\n" + "=" * 62)
    print("E3 编辑（批注）：改「门禁密码」字段——下游笔记厚度对照")
    print("=" * 62)

    q3 = "\n问题：仓库的门禁密码是多少？答案："

    # 薄上下文：字段之后几乎没有"笔记"，结论无处下沉
    ctx_thin = "系统设定：仓库的门禁密码是 8848。"
    # 厚上下文：字段之后有多句围绕密码展开的内容，给"结论写入下游笔记"留足空间
    ctx_thick = (
        "系统设定：仓库的门禁密码是 8848。这个密码会打印在新员工入职手册的扉页，"
        "新员工第一次进入仓库时需要用它开通自己的门禁卡。"
        "安全主管每周五会核对密码的登记记录，任何人对密码的疑问都直接找安全主管确认。"
        "手册扉页的密码字体是特殊的防复印字体，复印件上会显示为乱码。"
        "门禁系统每天零点自动重置一次，但密码本身保持不变。"
    )

    td = lambda s: tok(s, add_special_tokens=False)["input_ids"][0]

    def digit_prob(lg):
        """答案位上 '8' 与 '1' 开头（8848 vs 1795）的概率对比。"""
        p = torch.softmax(lg, dim=0)
        return p[td("8")].item(), p[td("1")].item()

    for cname, ctx in [("薄上下文", ctx_thin), ("厚上下文", ctx_thick)]:
        ctx_v2 = ctx.replace("8848", "1795")
        f0 = ctx.index("8848")
        enc_c = tok(ctx, return_offsets_mapping=True, return_tensors="pt")
        n_ctx_tok = enc_c["input_ids"].shape[1]
        field_pos = [i for i, (s, e) in enumerate(enc_c["offset_mapping"][0].tolist())
                     if s >= f0 and e <= f0 + len("8848")]
        ids_q3 = tok(q3, return_tensors="pt")["input_ids"]
        print(f"\n--- {cname}（{n_ctx_tok} tokens） ---")

        cache_base, _ = prefill_with_logits(model, enc_c["input_ids"])
        lg_base = next_token_logits(model, ids_q3, copy.deepcopy(cache_base))
        p8, p1 = digit_prob(lg_base)
        ans = greedy_continue(model, tok, lg_base, copy.deepcopy(cache_base), 6)
        print(f"  基线(8848)     答案 {ans!r}   P(8*)={p8:.3f} P(1*)={p1:.3f}")

        # 天真字段编辑：把 1795 版在同位置的 K/V 拷进来
        cache_v2 = prefill(model, tok(ctx_v2, return_tensors="pt")["input_ids"])
        cache_edit = copy.deepcopy(cache_base)
        for ln, lv in zip(cache_edit.layers, cache_v2.layers):
            for t in field_pos:
                ln.keys[:, :, t, :] = lv.keys[:, :, t, :]
                ln.values[:, :, t, :] = lv.values[:, :, t, :]
        lg_e = next_token_logits(model, ids_q3, cache_edit)
        p8, p1 = digit_prob(lg_e)
        ans = greedy_continue(model, tok, lg_e, cache_edit, 6)
        print(f"  天真字段编辑   答案 {ans!r}   P(8*)={p8:.3f} P(1*)={p1:.3f}")

        # 追加勘误：不动旧笔记，只在上下文末尾追加一条权威更正
        ctx_err = ctx + "\n[状态更新] 门禁密码已改为 1795，本条覆盖之前的一切说法。"
        cache_err, _ = prefill_with_logits(model, tok(ctx_err, return_tensors="pt")["input_ids"])
        lg_r = next_token_logits(model, ids_q3, cache_err)
        p8, p1 = digit_prob(lg_r)
        ans = greedy_continue(model, tok, lg_r, cache_err, 6)
        print(f"  追加勘误       答案 {ans!r}   P(8*)={p8:.3f} P(1*)={p1:.3f}")

    print(
        "\n[解读] 薄上下文：字段 KV 仍是决策的主要来源，天真编辑即可翻转；"
        "\n       厚上下文：结论在 prefill 时已写入下游笔记，原地改字段的效力被稀释"
        "\n       （arXiv:2606.17107 在 8B 级模型系统测得字段自身 KV 贡献 <1%）。"
        "\n       0.5B 小模型指令遵循弱，「勘误」不一定生效——编辑可靠性是规模与"
        "\n       上下文结构的函数，不是免费的午餐。"
    )


if __name__ == "__main__":
    main()
