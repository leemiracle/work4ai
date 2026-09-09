# 一些关于quantization的context
- bnb在checkpoint的命名很常见，是bitsandbytes这个库的缩写
- GGUF:  a binary format that is optimized for quick loading and saving of models, making it highly efficient for inference purposes
# quantization method分类方式
1. offline vs online quantization
2. standard vs dynamic quantization

# offline vs online quantization
## 常见 offline quantization methods
Bitsandbytes
## 常见 online quantization methods
AWQ, GPTQ, Bitsandbytes, marlin
