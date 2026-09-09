# Unsloth Quantization Techniques
unsloth一般使用bitsandbytes做quantization，quantization的具体实现主要分为两种方式：standard quantization和dynamic quantization
## Standard Quantization
TODO
## Dynamic Quantization
- background：quantizing a model down to lower bits sometimes breaks the model entirely
- object：通过quantize model不同的部分， by analyzing activation quantization error and weight quantization error, 保证quantized model的performance和非quantize model的performance最接近的情况下，使得quantized model的size最小
- 每个model的dynamic quantization的具体实现目前unsloth称是机密，无法直接透露每个model的quantization的部分是什么
- 但是unlsoth称vllm已经有支持，猜测是load出来model之后通过参数名字reverse engineer知道要quantize哪些layer （待查证）