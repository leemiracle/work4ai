Configs in this folder (and models on Hugging Face and Google Cloud) use a model naming scheme based on this table from the paper:
<img width="1478" height="1342" alt="image" src="https://github.com/user-attachments/assets/ef0e30bc-157f-47a8-bc7c-e8251eb95f48" />

Models are described as `[initialization]_[norm strategy]_[qk norm strategy (if any)]_[number of KV heads]_[pretraining context length]_[d_ff]_[SWA if sliding window]_[fp8 if float8]`. 

For instance, the top model in the table is `A_post_HQK_8kv_8k_13k_SWA_fp8`.
