#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""finetune_lora.py — 蒸馏数据 → LoRA SFT（Needle finetune 流水线对应物）

Needle 2 映射：
  冻结基础模型 + LoRA → 导出合并 → 单一部署文件（.cact）
  本脚本：冻结 DeepSeek-Prover-V2-7B + LoRA(r16 α32) → 合并 → 单一模型目录（vLLM 直接 serve）

数据：distill.jsonl 的 messages（user=官方 non-CoT prompt, assistant=```lean4 证明```）
  ——与推理时形态完全一致（R8：训练教节奏，prompt 不耍花样）
  --with-plan 消融开关：assistant 前置分解计划文本（Prover-V2 冷启动 {计划,证明} 对的形态）

DCU 注意（踩坑实录）：
  · transformers 5.12 apply_chat_template(tokenize=True) 返回 list 而非 tensor
  · generate 用 DynamicCache 在 DTK 崩——训练不用 cache，无此坑
  · 显存：HIP_VISIBLE_DEVICES=1 指定单卡（卡0被 vLLM server 占用）
用法：
  HIP_VISIBLE_DEVICES=1 python3 finetune_lora.py --data distill.jsonl --out /work/distill/lora_out
"""
import argparse
import json
import os
import sys
import time

import torch
from torch.utils.data import Dataset
from transformers import (AutoModelForCausalLM, AutoTokenizer, Trainer,
                          TrainingArguments)

MODEL_PATH = os.environ.get("PROVER_MODEL", "/work/models/DeepSeek-Prover-V2-7B")


class SFTData(Dataset):
    def __init__(self, path, tok, max_len=1024, with_plan=False):
        self.rows = []
        for line in open(path):
            if not line.strip():
                continue
            r = json.loads(line)
            msgs = r["messages"]
            if with_plan and r.get("skeleton"):
                plan = ("Proof plan (have-chain skeleton):\n```lean4\n"
                        + r["skeleton"] + "\n```\n")
                msgs = [msgs[0], {"role": "assistant",
                                  "content": plan + msgs[1]["content"]}]
            prompt = tok.apply_chat_template(
                [msgs[0]], tokenize=True, add_generation_prompt=True)
            if isinstance(prompt, list):
                prompt = torch.tensor(prompt)
            comp = tok.apply_chat_template(
                msgs, tokenize=True, add_generation_prompt=False)
            if isinstance(comp, list):
                comp = torch.tensor(comp)
            ids = torch.cat([prompt, comp[len(prompt):]])
            if len(ids) > max_len:
                continue
            labels = ids.clone()
            labels[:len(prompt)] = -100
            self.rows.append({"input_ids": ids, "labels": labels})

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, i):
        return self.rows[i]


def collate(batch, pad_id):
    mx = max(len(b["input_ids"]) for b in batch)
    ids, labs, att = [], [], []
    for b in batch:
        n = len(b["input_ids"])
        ids.append(torch.cat([b["input_ids"], torch.full((mx - n,), pad_id, dtype=torch.long)]))
        labs.append(torch.cat([b["labels"], torch.full((mx - n,), -100, dtype=torch.long)]))
        att.append(torch.cat([torch.ones(n, dtype=torch.long), torch.zeros(mx - n, dtype=torch.long)]))
    return {"input_ids": torch.stack(ids), "labels": torch.stack(labs),
            "attention_mask": torch.stack(att)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="/work/distill/out/distill.jsonl")
    ap.add_argument("--out", default="/work/distill/lora_out")
    ap.add_argument("--with-plan", action="store_true")
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--rank", type=int, default=16)
    ap.add_argument("--merge-to", default="")     # 合并后模型目录（vLLM serve 用）
    a = ap.parse_args()

    tok = AutoTokenizer.from_pretrained(MODEL_PATH)
    print("[data] loading...", flush=True)
    ds = SFTData(a.data, tok, with_plan=a.with_plan)
    print(f"[data] {len(ds)} rows", flush=True)
    if not len(ds):
        sys.exit("[fatal] 空数据集")

    from peft import LoraConfig, get_peft_model
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH, dtype=torch.bfloat16, attn_implementation="sdpa")
    model.config.use_cache = False
    lcfg = LoraConfig(
        r=a.rank, lora_alpha=2 * a.rank, lora_dropout=0.05,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
        task_type="CAUSAL_LM")
    model = get_peft_model(model, lcfg)
    model.print_trainable_parameters()

    targs = TrainingArguments(
        output_dir=a.out, num_train_epochs=a.epochs, learning_rate=a.lr,
        per_device_train_batch_size=1, gradient_accumulation_steps=8,
        bf16=True, warmup_ratio=0.1, lr_scheduler_type="cosine",
        logging_steps=1, save_strategy="no", report_to=[],
        gradient_checkpointing=True, optim="adamw_torch")
    pad_id = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id
    trainer = Trainer(model=model, args=targs, train_dataset=ds,
                      data_collator=lambda b: collate(b, pad_id))
    t0 = time.time()
    trainer.train()
    print(f"[train] done {time.time()-t0:.0f}s", flush=True)

    adapter_dir = os.path.join(a.out, "adapter")
    model.save_pretrained(adapter_dir)
    print(f"[save] adapter → {adapter_dir}", flush=True)

    if a.merge_to:
        merged = model.merge_and_unload()
        merged.save_pretrained(a.merge_to, safe_serialization=True)
        tok.save_pretrained(a.merge_to)
        print(f"[save] merged model → {a.merge_to}（vLLM 可直接 serve）", flush=True)


if __name__ == "__main__":
    main()
