# 06 · attention 层封装族

## 角色定位

layers/attention_layers（含_fp8/_int8子目录）把QKV投影→QK^T→softmax→context→输出投影封装成可替换单元，接口是纯虚forward(TensorMap*, TensorMap*, AttentionWeight<T>*)（layers/attention_layers/BaseAttentionLayer.h:144）。族按阶段×精度×并行度展开（TP前缀版与fp8/int8版正交），是模型层与kernel间的编排层。

## 内部结构

决策树getAttentionType（layers/attention_layers/BaseAttentionLayer.h:46）：half无causal在sm75/80/86、size∈{32,64}给FUSED（swin加seq≤256）；GPT须FMHA_ENABLE=ON且remove_padding（:77）；fp8需sm89/90、seq<512（:85）；int8需mode1/2、sm80/86 seq≤512（:103）。两路线：Fused把QKV bias后整段交TRT fused MHA单kernel（layers/attention_layers/FusedAttentionLayer.cu:181；GPT context走run_causal_masked_fmha，layers/attention_layers/GptContextAttentionLayer.cc:196）；Unfused走stridedBatchedGemm+invokeMaskedSoftmax（layers/attention_layers/UnfusedAttentionLayer.cc:225）+Gemm。勘误："Fused走MMHA"不成立——MMHA是decoding单kernel（layers/attention_layers/DecoderSelfAttentionLayer.cc:144），Fused用3rdparty MHARunner。

层间差异：DecoderCross的K/V仅step==1由encoder输出一次性GEMM进mem cache（layers/attention_layers/DecoderCrossAttentionLayer.cu:914）；WindowAttention服务Swin窗口注意力，窗口平方≤TRT_MAX_LEN且size32才切TRT fmha；fp8子族仅Self/DecoderSelf/GptContext+TP×2，仅Self版继承BaseAttentionFP8Layer，另两个直接继承BaseAttentionLayer<T1>；int8子族仅Unfused/Fused/Window。

## 外部连接

GPT在models/multi_gpu_gpt/ParallelGptDecoder.cc:27与ContextDecoder同构处实例化TP版、int8_mode传进主族；BERT在models/bert/Bert.cc:26按attention_type二选一；fp8走models/gpt_fp8/GptFP8ContextDecoder.cc:27。

## 数据流

context阶段（GptContext，输入压缩[token_num,hidden]）：①融合QKV GEMM（GptContextAttentionLayer.cc:130）；②AddFusedQKVBiasTranspose加bias/rotary转[B,H,L,Dh]（:156）；③Transpose4dBatchMajor写key/value_cache（:179）；④FUSED一步出context（:196），否则QK^T GEMM（:209，mode2强制float缓冲）→MaskedSoftmax（:245）→QK·V（:286）；⑤转回token-major、输出投影（:304）。

decoding阶段（DecoderSelf，单步[batch,d_model]）：①QKV GEMM（:566）；②fusedQKV_masked_attention_dispatch（:581）——MMHA片内完成bias、rotary、K/V追加进cache、按cache_indirection取源beam KV、softmax；③输出投影（:667）。context写cache、decoding读cache即两阶段交接。

## 设计决策

allreduce位置：TP按head切卡、attention按head独立，QKV后无需通信；仅输出投影产生部分和，在forward尾做一次ftNcclAllReduceSum（TensorParallelGptContextAttentionLayer.cc:52）。勘误：全仓无allreduce_fusion，该开关实为do_all_reduce_旗标+custom_all_reduce换缓冲。TP版继承非TP类整段复用单卡forward编排，本身只是allreduce装饰器。beam差异：DecoderSelf输入含可选cache_indirection（DecoderSelfAttentionLayer.cc:471）——KV cache随beam重排需间接寻址；DecoderCross无此参数（DecoderCrossAttentionLayer.cu:870），其K/V来自encoder、全beam共享。fp8/int8覆盖：fp8无Unfused/cross版；没有Fused int8 context且更彻底——GPT的int8走主族int8_mode参数（DecoderSelfAttentionLayer.h:66），mode2下强制is_qk_buf_float、本体仍走unfused GEMM；int8子族是TRT int8 FMHA（layers/attention_layers_int8/FusedAttentionLayerINT8.cu:636）encoder专用。fp8另限decoder不支持rotary（DecoderSelfAttentionFP8Layer.cc:112）。

## 新人提示

- GPT吃fused context须FMHA_ENABLE=ON且remove_padding；FUSED_PADDED在GPT context被FT_CHECK拒绝（layers/attention_layers/GptContextAttentionLayer.cc:68）。
- 层零状态：权重外置，缓冲reMalloc池化，TP版max_batch_size传0合法。
- fp8双模板T1/T2=输入fp8/输出bf16，scale链贯穿每个GEMM；cache形状的x=16/sizeof(T)是16B向量化痕迹。
