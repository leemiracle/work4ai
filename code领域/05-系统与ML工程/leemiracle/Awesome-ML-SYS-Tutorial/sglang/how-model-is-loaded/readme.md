# How A Model is Loaded in Hugging Face and SGLang

I spend several days to build up the online update weights feature in SGLang for RLHF workflow. Till now, I still couldn't figure out how to load the `[name, weights]` pairs into SGLang Engine. This is quite annoying, so I decide to dig into the code to figure out how it works.

Thus, this note is written to record my findings on how a model is loaded in Hugging Face and SGLang. We will first start with Hugging Face, and then move on to SGLang. All the codes are based on the `meta-llama/Llama-3.2-1B-Instruct` model.

## Hugging Face

Loading a model from Hugging Face is quite simple with its direct API.

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.2-1B-Instruct", torch_dtype="bfloat16").to("cuda")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-1B-Instruct")
print(model)
```
Try to print the model, we get the following output:

```python
LlamaForCausalLM(
  (model): LlamaModel(
    (embed_tokens): Embedding(128256, 2048)
    (layers): ModuleList(
      (0-15): 16 x LlamaDecoderLayer(
        (self_attn): LlamaSdpaAttention(
          (q_proj): Linear(in_features=2048, out_features=2048, bias=False)
          (k_proj): Linear(in_features=2048, out_features=512, bias=False)
          (v_proj): Linear(in_features=2048, out_features=512, bias=False)
          (o_proj): Linear(in_features=2048, out_features=2048, bias=False)
          (rotary_emb): LlamaRotaryEmbedding()
        )
        (mlp): LlamaMLP(
          (gate_proj): Linear(in_features=2048, out_features=8192, bias=False)
          (up_proj): Linear(in_features=2048, out_features=8192, bias=False)
          (down_proj): Linear(in_features=8192, out_features=2048, bias=False)
          (act_fn): SiLU()
        )
        (input_layernorm): LlamaRMSNorm((2048,), eps=1e-05)
        (post_attention_layernorm): LlamaRMSNorm((2048,), eps=1e-05)
      )
    )
    (norm): LlamaRMSNorm((2048,), eps=1e-05)
    (rotary_emb): LlamaRotaryEmbedding()
  )
  (lm_head): Linear(in_features=2048, out_features=128256, bias=False)
)
```
Let's go into the detailed component of the model, i.e., `model.model, model.lm_head`.

### `model.model`

The whole class `LlamaModel` implements the Transformer decoder architecture.

1. **Embedding Layer**

- `embed_tokens: Embedding(128256, 2048)`
- `128256`: Vocabulary size.
- `2048`: Dimensionality of each embedding vector.
- Maps discrete vocabulary indices to continuous embedding vectors.

2. **Decoder Layers**

- `layers: ModuleList (16 x LlamaDecoderLayer)`
- A stack of 16 decoder layers. Each `LlamaDecoderLayer` contains one `self_attn, mlp, input_layernorm, post_attention_layernorm`.

- `self_attn: LlamaSdpaAttention`: Computes self-attention scores and aggregates contextual information.
  - `q_proj`: Projects input features into the query space. Input: `2048`, Output: `2048`.
  - `k_proj`: Projects input features into the key space. Input: `2048`, Output: `512` (dimensionality reduction for efficiency).
  - `v_proj`: Projects input features into the value space. Input: `2048`, Output: `512`.
  - `o_proj`: Projects attention outputs back to the input feature dimensionality. Input: `2048`, Output: `2048`.
  - `rotary_emb`: Rotary positional embeddings to encode sequence position.

- `mlp: LlamaMLP`: Applies non-linear transformations through a multi-layer perceptron.
  - `gate_proj`: Linear layer, Input: `2048`, Output: `8192`.
  - `up_proj`: Linear layer, Input: `2048`, Output: `8192`.
  - `down_proj`: Linear layer, Input: `8192`, Output: `2048`.
  - `act_fn`: Activation function `SiLU` (Swish) introduces non-linearity.

- `input_layernorm`: Applies RMSNorm to the layer input with dimensionality `2048`.
- `post_attention_layernorm`: Applies RMSNorm after the attention mechanism.

3. **Global Normalization**

- `norm: LlamaRMSNorm((2048,), eps=1e-05)`
- Applies RMSNorm to the final decoder output for stable feature scaling.

4. **Rotary Positional Embedding**

- `rotary_emb: LlamaRotaryEmbedding()`
- Encodes positional information using rotary embeddings to enhance sequence modeling.

### `model.lm_head`

- `lm_head: Linear(in_features=2048, out_features=128256, bias=False)`
- A linear layer that maps the decoder's output features (dim: `2048`) to the vocabulary size (`128256`).
- No bias term: Reduces the number of trainable parameters and computation complexity.

### Model State Dict

In Pytorch, `state_dict` is a core mechanism for saving and loading the parameters and optimizer states of a model. Here is its function and principle:

- `state_dict`: A Python dictionary object that maps each layer to its parameter tensor.
- `model.state_dict()`: Returns the state dictionary of the model, containing all the weights and biases.
- `torch.save(model.state_dict(), PATH)`: Saves the state dictionary to a file.
- `model.load_state_dict(torch.load(PATH))`: Loads the state dictionary from a file.

As you see, state dict is a dictionary, and contains the name and weights of each layer.

We first get the state dict of the model, and then get its VRAM usage.

```python
state_dict = model.state_dict()

total_memory = 0
for name, param in state_dict.items():
    param_memory = param.numel() * param.element_size()  # numel() gives the number of elements, element_size() gives the size in bytes
    total_memory += param_memory

total_memory_mb = total_memory / (1024 * 1024)
print(f"Total memory usage of the state_dict: {total_memory_mb:.2f} MB")

# Total memory usage of the state_dict: 2858.13 MB
```

A 1B model in bfloat16 precision takes about 2.8GB VRAM, that's reasonable.


```python

print(state_dict.keys())

# odict_keys(['model.embed_tokens.weight', 'model.layers.0.self_attn.q_proj.weight', 'model.layers.0.self_attn.k_proj.weight', 'model.layers.0.self_attn.v_proj.weight', 'model.layers.0.self_attn.o_proj.weight', 'model.layers.0.mlp.gate_proj.weight', 'model.layers.0.mlp.up_proj.weight', 'model.layers.0.mlp.down_proj.weight', 'model.layers.0.input_layernorm.weight', 'model.layers.0.post_attention_layernorm.weight', 'model.layers.1.self_attn.q_proj.weight', 'model.layers.1.self_attn.k_proj.weight', 'model.layers.1.self_attn.v_proj.weight', 'model.layers.1.self_attn.o_proj.weight', 'model.layers.1.mlp.gate_proj.weight', 'model.layers.1.mlp.up_proj.weight', 'model.layers.1.mlp.down_proj.weight', 'model.layers.1.input_layernorm.weight', 'model.layers.1.post_attention_layernorm.weight', 'model.layers.2.self_attn.q_proj.weight', 'model.layers.2.self_attn.k_proj.weight', 'model.layers.2.self_attn.v_proj.weight', 'model.layers.2.self_attn.o_proj.weight', 'model.layers.2.mlp.gate_proj.weight', 'model.layers.2.mlp.up_proj.weight', 'model.layers.2.mlp.down_proj.weight', 'model.layers.2.input_layernorm.weight', 'model.layers.2.post_attention_layernorm.weight', 'model.layers.3.self_attn.q_proj.weight', 'model.layers.3.self_attn.k_proj.weight', 'model.layers.3.self_attn.v_proj.weight', 'model.layers.3.self_attn.o_proj.weight', 'model.layers.3.mlp.gate_proj.weight', 'model.layers.3.mlp.up_proj.weight', 'model.layers.3.mlp.down_proj.weight', 'model.layers.3.input_layernorm.weight', 'model.layers.3.post_attention_layernorm.weight', 'model.layers.4.self_attn.q_proj.weight', 'model.layers.4.self_attn.k_proj.weight', 'model.layers.4.self_attn.v_proj.weight', 'model.layers.4.self_attn.o_proj.weight', 'model.layers.4.mlp.gate_proj.weight', 'model.layers.4.mlp.up_proj.weight', 'model.layers.4.mlp.down_proj.weight', 'model.layers.4.input_layernorm.weight', 'model.layers.4.post_attention_layernorm.weight', 'model.layers.5.self_attn.q_proj.weight', 'model.layers.5.self_attn.k_proj.weight', 'model.layers.5.self_attn.v_proj.weight', 'model.layers.5.self_attn.o_proj.weight', 'model.layers.5.mlp.gate_proj.weight', 'model.layers.5.mlp.up_proj.weight', 'model.layers.5.mlp.down_proj.weight', 'model.layers.5.input_layernorm.weight', 'model.layers.5.post_attention_layernorm.weight', 'model.layers.6.self_attn.q_proj.weight', 'model.layers.6.self_attn.k_proj.weight', 'model.layers.6.self_attn.v_proj.weight', 'model.layers.6.self_attn.o_proj.weight', 'model.layers.6.mlp.gate_proj.weight', 'model.layers.6.mlp.up_proj.weight', 'model.layers.6.mlp.down_proj.weight', 'model.layers.6.input_layernorm.weight', 'model.layers.6.post_attention_layernorm.weight', 'model.layers.7.self_attn.q_proj.weight', 'model.layers.7.self_attn.k_proj.weight', 'model.layers.7.self_attn.v_proj.weight', 'model.layers.7.self_attn.o_proj.weight', 'model.layers.7.mlp.gate_proj.weight', 'model.layers.7.mlp.up_proj.weight', 'model.layers.7.mlp.down_proj.weight', 'model.layers.7.input_layernorm.weight', 'model.layers.7.post_attention_layernorm.weight', 'model.layers.8.self_attn.q_proj.weight', 'model.layers.8.self_attn.k_proj.weight', 'model.layers.8.self_attn.v_proj.weight', 'model.layers.8.self_attn.o_proj.weight', 'model.layers.8.mlp.gate_proj.weight', 'model.layers.8.mlp.up_proj.weight', 'model.layers.8.mlp.down_proj.weight', 'model.layers.8.input_layernorm.weight', 'model.layers.8.post_attention_layernorm.weight', 'model.layers.9.self_attn.q_proj.weight', 'model.layers.9.self_attn.k_proj.weight', 'model.layers.9.self_attn.v_proj.weight', 'model.layers.9.self_attn.o_proj.weight', 'model.layers.9.mlp.gate_proj.weight', 'model.layers.9.mlp.up_proj.weight', 'model.layers.9.mlp.down_proj.weight', 'model.layers.9.input_layernorm.weight', 'model.layers.9.post_attention_layernorm.weight', 'model.layers.10.self_attn.q_proj.weight', 'model.layers.10.self_attn.k_proj.weight', 'model.layers.10.self_attn.v_proj.weight', 'model.layers.10.self_attn.o_proj.weight', 'model.layers.10.mlp.gate_proj.weight', 'model.layers.10.mlp.up_proj.weight', 'model.layers.10.mlp.down_proj.weight', 'model.layers.10.input_layernorm.weight', 'model.layers.10.post_attention_layernorm.weight', 'model.layers.11.self_attn.q_proj.weight', 'model.layers.11.self_attn.k_proj.weight', 'model.layers.11.self_attn.v_proj.weight', 'model.layers.11.self_attn.o_proj.weight', 'model.layers.11.mlp.gate_proj.weight', 'model.layers.11.mlp.up_proj.weight', 'model.layers.11.mlp.down_proj.weight', 'model.layers.11.input_layernorm.weight', 'model.layers.11.post_attention_layernorm.weight', 'model.layers.12.self_attn.q_proj.weight', 'model.layers.12.self_attn.k_proj.weight', 'model.layers.12.self_attn.v_proj.weight', 'model.layers.12.self_attn.o_proj.weight', 'model.layers.12.mlp.gate_proj.weight', 'model.layers.12.mlp.up_proj.weight', 'model.layers.12.mlp.down_proj.weight', 'model.layers.12.input_layernorm.weight', 'model.layers.12.post_attention_layernorm.weight', 'model.layers.13.self_attn.q_proj.weight', 'model.layers.13.self_attn.k_proj.weight', 'model.layers.13.self_attn.v_proj.weight', 'model.layers.13.self_attn.o_proj.weight', 'model.layers.13.mlp.gate_proj.weight', 'model.layers.13.mlp.up_proj.weight', 'model.layers.13.mlp.down_proj.weight', 'model.layers.13.input_layernorm.weight', 'model.layers.13.post_attention_layernorm.weight', 'model.layers.14.self_attn.q_proj.weight', 'model.layers.14.self_attn.k_proj.weight', 'model.layers.14.self_attn.v_proj.weight', 'model.layers.14.self_attn.o_proj.weight', 'model.layers.14.mlp.gate_proj.weight', 'model.layers.14.mlp.up_proj.weight', 'model.layers.14.mlp.down_proj.weight', 'model.layers.14.input_layernorm.weight', 'model.layers.14.post_attention_layernorm.weight', 'model.layers.15.self_attn.q_proj.weight', 'model.layers.15.self_attn.k_proj.weight', 'model.layers.15.self_attn.v_proj.weight', 'model.layers.15.self_attn.o_proj.weight', 'model.layers.15.mlp.gate_proj.weight', 'model.layers.15.mlp.up_proj.weight', 'model.layers.15.mlp.down_proj.weight', 'model.layers.15.input_layernorm.weight', 'model.layers.15.post_attention_layernorm.weight', 'model.norm.weight', 'lm_head.weight'])
```

Different from the model architecture, the state dict unsqueezes the name and weights of all the components.

Also, `dict(model.named_parameters()).keys()` gives the same result.

