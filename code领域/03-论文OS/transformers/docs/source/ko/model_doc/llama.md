<!--Copyright 2022 The HuggingFace Team. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

⚠️ Note that this file is in Markdown but contain specific syntax for our doc-builder (similar to MDX) that may not be
rendered properly in your Markdown viewer.

-->

# LLaMA [[llama]]

## 개요 [[overview]]

LLaMA 모델은 Hugo Touvron, Thibaut Lavril, Gautier Izacard, Xavier Martinet, Marie-Anne Lachaux, Timothée Lacroix, Baptiste Rozière, Naman Goyal, Eric Hambro, Faisal Azhar, Aurelien Rodriguez, Armand Joulin, Edouard Grave, Guillaume Lample에 의해 제안된 [LLaMA: Open and Efficient Foundation Language Models](https://huggingface.co/papers/2302.13971)에서 소개되었습니다. 이 모델은 7B에서 65B개의 파라미터까지 다양한 크기의 기초 언어 모델을 모아놓은 것입니다.

논문의 초록은 다음과 같습니다:

*"LLaMA는 7B에서 65B개의 파라미터 수를 가진 기초 언어 모델의 모음입니다. 우리는 수조 개의 토큰으로 모델을 훈련시켰고, 공개적으로 이용 가능한 데이터셋만을 사용하여 최고 수준의 모델을 훈련시킬 수 있음을 보여줍니다. 특히, LLaMA-13B 모델은 대부분의 벤치마크에서 GPT-3 (175B)를 능가하며, LLaMA-65B는 최고 수준의 모델인 Chinchilla-70B와 PaLM-540B에 버금가는 성능을 보입니다. 우리는 모든 모델을 연구 커뮤니티에 공개합니다."*

팁:

- LLaMA 모델의 가중치는 [이 양식](https://docs.google.com/forms/d/e/1FAIpQLSfqNECQnMkycAp2jP4Z9TFX0cGR4uf7b_fBxjY_OjhJILlKGA/viewform?usp=send_form)을 작성하여 얻을 수 있습니다.
- 가중치를 다운로드한 후에는 이를 [변환 스크립트](https://github.com/huggingface/transformers/blob/main/src/transformers/models/llama/convert_llama_weights_to_hf.py)를 사용하여 Hugging Face Transformers 형식으로 변환해야합니다. 변환 스크립트를 실행하려면 아래의 예시 명령어를 참고하세요:

```bash
python src/transformers/models/llama/convert_llama_weights_to_hf.py \
    --input_dir /path/to/downloaded/llama/weights --model_size 7B --output_dir /output/path
```

- 변환을 하였다면 모델과 토크나이저는 다음과 같이 로드할 수 있습니다:

```python
from transformers import LlamaForCausalLM, LlamaTokenizer

tokenizer = LlamaTokenizer.from_pretrained("/output/path")
model = LlamaForCausalLM.from_pretrained("/output/path")
```

스크립트를 실행하기 위해서는 모델을 float16 정밀도로 전부 로드할 수 있을 만큼의 충분한 CPU RAM이 필요합니다. (가장 큰 버전의 모델이 여러 체크포인트로 나뉘어 있더라도, 각 체크포인트는 모델의 각 가중치의 일부를 포함하고 있기 때문에 모든 체크포인트를 RAM에 로드해야 합니다) 65B 모델의 경우, 총 130GB의 RAM이 필요합니다.


- LLaMA 토크나이저는 [sentencepiece](https://github.com/google/sentencepiece)를 기반으로 하는 BPE 모델입니다. sentencepiece의 특징 중 하나는 시퀀스를 디코딩할 때 첫 토큰이 단어의 시작이라면 (예를 들어 "Banana"), 토크나이저는 문자열 앞에 공백을 추가하지 않는다는 것입니다.

이 모델은 [BlackSamorez](https://huggingface.co/BlackSamorez)의 기여와 함께, [zphang](https://huggingface.co/zphang)에 의해 제공되었습니다. Hugging Face에서의 구현 코드는 GPT-NeoX를 기반으로 하며 [여기](https://github.com/EleutherAI/gpt-neox)에서 찾을 수 있고, 저자의 코드 원본은 [여기](https://github.com/facebookresearch/llama)에서 확인할 수 있습니다.


원래 LLaMA 모델을 기반으로 Meta AI에서 몇 가지 후속 작업을 발표했습니다:

- **Llama2**: Llama2는 구조적인 몇 가지 수정(Grouped Query Attention)을 통해 개선된 버전이며, 2조 개의 토큰으로 사전 훈련이 되어 있습니다. Llama2에 대한 자세한 내용은 [이 문서](llama2)를 참고하세요.

## 리소스 [[resources]]

LLaMA를 시작하는 데 도움이 될 Hugging Face 및 커뮤니티(🌎로 표시)의 공식 자료 목록입니다. 여기에 자료를 제출하고 싶다면 Pull Request를 올려주세요! 추가할 자료는 기존의 자료와 중복되지 않고 새로운 내용을 보여주는 것이 좋습니다.

<PipelineTag pipeline="text-classification"/>

- LLaMA 모델을 텍스트 분류 작업에 적용하기 위한 프롬프트 튜닝 방법에 대한 [노트북](https://colab.research.google.com/github/bigscience-workshop/petals/blob/main/examples/prompt-tuning-sst2.ipynb#scrollTo=f04ba4d2) 🌎

<PipelineTag pipeline="question-answering"/>

- [Stack Exchange](https://stackexchange.com)에서 질문에 답하는 LLaMA를 훈련하는 방법을 위한 [StackLLaMA: RLHF로 LLaMA를 훈련하는 실전 가이드](https://huggingface.co/blog/stackllama#stackllama-a-hands-on-guide-to-train-llama-with-rlhf) 🌎

⚗️ 최적화
- 제한된 메모리를 가진 GPU에서 xturing 라이브러리를 사용하여 LLaMA 모델을 미세 조정하는 방법에 대한 [노트북](https://colab.research.google.com/drive/1SQUXq1AMZPSLD4mk3A3swUIc6Y2dclme?usp=sharing) 🌎

⚡️ 추론
- 🤗 PEFT 라이브러리의 PeftModel을 사용하여 LLaMA 모델을 실행하는 방법에 대한 [노트북](https://colab.research.google.com/github/DominguesM/alpaca-lora-ptbr-7b/blob/main/notebooks/02%20-%20Evaluate.ipynb) 🌎
- LangChain을 사용하여 PEFT 어댑터 LLaMA 모델을 로드하는 방법에 대한 [노트북](https://colab.research.google.com/drive/1l2GiSSPbajVyp2Nk3CFT4t3uH6-5TiBe?usp=sharing) 🌎

🚀 배포
- 🤗 PEFT 라이브러리와 사용자 친화적인 UI로 LLaMA 모델을 미세 조정하는 방법에 대한 [노트북](https://colab.research.google.com/github/lxe/simple-llama-finetuner/blob/master/Simple_LLaMA_FineTuner.ipynb#scrollTo=3PM_DilAZD8T) 🌎
- Amazon SageMaker에서 텍스트 생성을 위해 Open-LLaMA 모델을 배포하는 방법에 대한 [노트북](https://github.com/aws/amazon-sagemaker-examples/blob/main/introduction_to_amazon_algorithms/jumpstart-foundation-models/text-generation-open-llama.ipynb) 🌎

## LlamaConfig [[llamaconfig]]

[[autodoc]] LlamaConfig


## LlamaTokenizer [[llamatokenizer]]

[[autodoc]] LlamaTokenizer
    - get_special_tokens_mask
    - save_vocabulary

## LlamaTokenizerFast [[llamatokenizerfast]]

[[autodoc]] LlamaTokenizerFast
    - get_special_tokens_mask
    - update_post_processor
    - save_vocabulary

## LlamaModel [[llamamodel]]

[[autodoc]] LlamaModel
    - forward


## LlamaForCausalLM [[llamaforcausallm]]

[[autodoc]] LlamaForCausalLM
    - forward

## LlamaForSequenceClassification [[llamaforsequenceclassification]]

[[autodoc]] LlamaForSequenceClassification
    - forward
