<!--Copyright 2023 The HuggingFace Team. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

⚠️ Note that this file is in Markdown but contain specific syntax for our doc-builder (similar to MDX) that may not be
rendered properly in your Markdown viewer.

-->

# 인과 언어 모델링[[causal-language-modeling]]

[[open-in-colab]]

언어 모델링은 인과적 언어 모델링과 마스크드 언어 모델링, 두 가지 유형으로 나뉩니다. 이 가이드에서는 인과적 언어 모델링을 설명합니다.
인과 언어 모델은 텍스트 생성에 자주 사용됩니다. 또 창의적인 방향으로 응용할 수 있습니다.
직접 사용하며 재미있는 탐구를 해보거나, Copilot 또는 CodeParrot와 같은 지능형 코딩 어시스턴트의 기반이 되기도 합니다.

<Youtube id="Vpjb1lu0MDk"/>

인과 언어 모델링은 토큰 시퀀스에서 다음 토큰을 예측하며, 모델은 왼쪽의 토큰에만 접근할 수 있습니다.
이는 모델이 미래의 토큰을 볼 수 없다는 것을 의미합니다. 인과 언어 모델의 예로 GPT-2가 있죠.

이 가이드에서는 다음 작업을 수행하는 방법을 안내합니다:

1. [DistilGPT2](https://huggingface.co/distilbert/distilgpt2) 모델을 [ELI5](https://huggingface.co/datasets/eli5) 데이터 세트의 [r/askscience](https://www.reddit.com/r/askscience) 하위 집합으로 미세 조정
2. 미세 조정된 모델을 추론에 사용

<Tip>

이 작업과 호환되는 모든 아키텍처와 체크포인트를 보려면 [작업 페이지](https://huggingface.co/tasks/text-generation)를 확인하는 것이 좋습니다.

</Tip>

시작하기 전에 필요한 라이브러리가 모두 설치되어 있는지 확인하세요:

```bash
pip install transformers datasets evaluate
```

커뮤니티에 모델을 업로드하고 공유하기 위해 Hugging Face 계정에 로그인하는 것을 권장합니다. 알림이 표시되면 토큰을 입력하여 로그인하세요:

```py
>>> from huggingface_hub import notebook_login

>>> notebook_login()
```

## ELI5 데이터 세트 불러오기[[load-eli5-dataset]]

먼저, 🤗 Datasets 라이브러리에서 r/askscience의 작은 하위 집합인 ELI5 데이터 세트를 불러옵니다.
이를 통해 전체 데이터 세트에서 학습하는 데 더 많은 시간을 투자하기 전에, 실험해봄으로써 모든 것이 작동하는지 확인할 수 있습니다.

```py
>>> from datasets import load_dataset

>>> eli5 = load_dataset("eli5", split="train_asks[:5000]")
```

데이터 세트의 `train_asks` 분할을 [`~datasets.Dataset.train_test_split`] 메소드를 사용하여 학습 및 테스트 세트로 분할합니다:

```py
>>> eli5 = eli5.train_test_split(test_size=0.2)
```

그런 다음 예제를 살펴보세요:

```py
>>> eli5["train"][0]
{'answers': {'a_id': ['c3d1aib', 'c3d4lya'],
  'score': [6, 3],
  'text': ["The velocity needed to remain in orbit is equal to the square root of Newton's constant times the mass of earth divided by the distance from the center of the earth. I don't know the altitude of that specific mission, but they're usually around 300 km. That means he's going 7-8 km/s.\n\nIn space there are no other forces acting on either the shuttle or the guy, so they stay in the same position relative to each other. If he were to become unable to return to the ship, he would presumably run out of oxygen, or slowly fall into the atmosphere and burn up.",
   "Hope you don't mind me asking another question, but why aren't there any stars visible in this photo?"]},
 'answers_urls': {'url': []},
 'document': '',
 'q_id': 'nyxfp',
 'selftext': '_URL_0_\n\nThis was on the front page earlier and I have a few questions about it. Is it possible to calculate how fast the astronaut would be orbiting the earth? Also how does he stay close to the shuttle so that he can return safely, i.e is he orbiting at the same speed and can therefore stay next to it? And finally if his propulsion system failed, would he eventually re-enter the atmosphere and presumably die?',
 'selftext_urls': {'url': ['http://apod.nasa.gov/apod/image/1201/freeflyer_nasa_3000.jpg']},
 'subreddit': 'askscience',
 'title': 'Few questions about this space walk photograph.',
 'title_urls': {'url': []}}
```

많아 보일 수 있지만, 실제로는 `text` 필드만 중요합니다. 언어 모델링 작업의 장점은 레이블이 필요하지 않다는 것입니다. 다음 단어 *자체가* 레이블입니다. (이렇게 레이블을 제공하지 않아도 되는 학습을 비지도 학습이라고 일컫습니다)

## 전처리[[preprocess]]

<Youtube id="ma1TrR7gE7I"/>

다음 단계는 `text` 필드를 전처리하기 위해 DistilGPT2 토크나이저를 불러오는 것입니다.

```py
>>> from transformers import AutoTokenizer

>>> tokenizer = AutoTokenizer.from_pretrained("distilbert/distilgpt2")
```

위의 예제에서 알 수 있듯이, `text` 필드는 `answers` 아래에 중첩되어 있습니다. 따라서 [`flatten`](https://huggingface.co/docs/datasets/process#flatten) 메소드를 사용하여 중첩 구조에서 `text` 하위 필드를 추출해야 합니다.

```py
>>> eli5 = eli5.flatten()
>>> eli5["train"][0]
{'answers.a_id': ['c3d1aib', 'c3d4lya'],
 'answers.score': [6, 3],
 'answers.text': ["The velocity needed to remain in orbit is equal to the square root of Newton's constant times the mass of earth divided by the distance from the center of the earth. I don't know the altitude of that specific mission, but they're usually around 300 km. That means he's going 7-8 km/s.\n\nIn space there are no other forces acting on either the shuttle or the guy, so they stay in the same position relative to each other. If he were to become unable to return to the ship, he would presumably run out of oxygen, or slowly fall into the atmosphere and burn up.",
  "Hope you don't mind me asking another question, but why aren't there any stars visible in this photo?"],
 'answers_urls.url': [],
 'document': '',
 'q_id': 'nyxfp',
 'selftext': '_URL_0_\n\nThis was on the front page earlier and I have a few questions about it. Is it possible to calculate how fast the astronaut would be orbiting the earth? Also how does he stay close to the shuttle so that he can return safely, i.e is he orbiting at the same speed and can therefore stay next to it? And finally if his propulsion system failed, would he eventually re-enter the atmosphere and presumably die?',
 'selftext_urls.url': ['http://apod.nasa.gov/apod/image/1201/freeflyer_nasa_3000.jpg'],
 'subreddit': 'askscience',
 'title': 'Few questions about this space walk photograph.',
 'title_urls.url': []}
```

각 하위 필드는 이제 `answers` 접두사를 가진 별도의 열로 나뉘었으며, `text` 필드는 이제 리스트입니다. 각 문장을 개별적으로 토큰화하는 대신, 먼저 리스트를 문자열로 변환하여 한꺼번에 토큰화할 수 있습니다.

다음은 문자열 리스트를 결합하고 결과를 토큰화하는 첫 번째 전처리 함수입니다:

```py
>>> def preprocess_function(examples):
...     return tokenizer([" ".join(x) for x in examples["answers.text"]])
```

이 전처리 함수를 전체 데이터 세트에 적용하려면 🤗 Datasets [`~datasets.Dataset.map`] 메소드를 사용하세요. `batched=True`로 설정하여 데이터셋의 여러 요소를 한 번에 처리하고, `num_proc`를 증가시켜 프로세스 수를 늘릴 수 있습니다. 필요 없는 열은 제거하세요:

```py
>>> tokenized_eli5 = eli5.map(
...     preprocess_function,
...     batched=True,
...     num_proc=4,
...     remove_columns=eli5["train"].column_names,
... )
```

이제 데이터 세트는 시퀀스가 토큰화됐지만, 일부 시퀀스는 모델의 최대 입력 길이보다 길 수 있습니다.

이제 두 번째 전처리 함수를 사용하여
- 모든 시퀀스를 연결하고,
- `block_size`로 정의된 길이로 연결된 시퀀스를 여러 개의 짧은 묶음으로 나눕니다. 이 값은 최대 입력 길이와 GPU RAM을 고려해 충분히 짧아야 합니다.

```py
>>> block_size = 128


>>> def group_texts(examples):
...     # Concatenate all texts.
...     concatenated_examples = {k: sum(examples[k], []) for k in examples.keys()}
...     total_length = len(concatenated_examples[list(examples.keys())[0]])
...     # We drop the small remainder, we could add padding if the model supported it instead of this drop, you can
...     # customize this part to your needs.
...     if total_length >= block_size:
...         total_length = (total_length // block_size) * block_size
...     # Split by chunks of block_size.
...     result = {
...         k: [t[i : i + block_size] for i in range(0, total_length, block_size)]
...         for k, t in concatenated_examples.items()
...     }
...     result["labels"] = result["input_ids"].copy()
...     return result
```

전체 데이터 세트에 `group_texts` 함수를 적용하세요:

```py
>>> lm_dataset = tokenized_eli5.map(group_texts, batched=True, num_proc=4)
```

그런 다음 [`DataCollatorForLanguageModeling`]을 사용하여 예제의 배치를 만듭니다. 데이터 세트 전체를 최대 길이로 패딩하는 것보다, 취합 단계에서 각 배치의 최대 길이로 문장을 *동적으로 패딩*하는 것이 더 효율적입니다.

패딩 토큰으로 종결 토큰을 사용하고 `mlm=False`로 설정하세요. 이렇게 하면 입력을 오른쪽으로 한 칸씩 시프트한 값을 레이블로 사용합니다:

```py
>>> from transformers import DataCollatorForLanguageModeling

>>> tokenizer.pad_token = tokenizer.eos_token
>>> data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
```



## 훈련[[train]]

<Tip>

[`Trainer`]를 사용하여 모델을 미세 조정하는 방법을 잘 모르신다면 [기본 튜토리얼](../training#train-with-pytorch-trainer)을 확인해보세요!

</Tip>

이제 모델을 훈련하기 준비가 되었습니다! [`AutoModelForCausalLM`]를 사용하여 DistilGPT2를 불러옵니다:

```py
>>> from transformers import AutoModelForCausalLM, TrainingArguments, Trainer

>>> model = AutoModelForCausalLM.from_pretrained("distilbert/distilgpt2")
```

여기까지 진행하면 세 단계만 남았습니다:

1. [`TrainingArguments`]에서 훈련 하이퍼파라미터를 정의하세요. `output_dir`은 유일한 필수 매개변수로, 모델을 저장할 위치를 지정합니다. (먼저 Hugging Face에 로그인 필수) `push_to_hub=True`로 설정하여 이 모델을 허브에 업로드할 수 있습니다.
2. 훈련 인수를 [`Trainer`]에 모델, 데이터 세트 및 데이터 콜레이터와 함께 전달하세요.
3. [`~Trainer.train`]을 호출하여 모델을 미세 조정하세요.

```py
>>> training_args = TrainingArguments(
...     output_dir="my_awesome_eli5_clm-model",
...     eval_strategy="epoch",
...     learning_rate=2e-5,
...     weight_decay=0.01,
...     push_to_hub=True,
... )

>>> trainer = Trainer(
...     model=model,
...     args=training_args,
...     train_dataset=lm_dataset["train"],
...     eval_dataset=lm_dataset["test"],
...     data_collator=data_collator,
... )

>>> trainer.train()
```

훈련이 완료되면 [`~transformers.Trainer.evaluate`] 메소드를 사용하여 모델을 평가하고 퍼플렉서티를 얻을 수 있습니다:

```py
>>> import math

>>> eval_results = trainer.evaluate()
>>> print(f"Perplexity: {math.exp(eval_results['eval_loss']):.2f}")
Perplexity: 49.61
```

그런 다음 [`~transformers.Trainer.push_to_hub`] 메소드를 사용하여 모델을 허브에 공유하세요. 이렇게 하면 누구나 모델을 사용할 수 있습니다:

```py
>>> trainer.push_to_hub()
```

<Tip>

인과 언어 모델링을 위해 모델을 미세 조정하는 더 자세한 예제는 해당하는 [PyTorch 노트북](https://colab.research.google.com/github/huggingface/notebooks/blob/main/examples/language_modeling.ipynb) 또는 [TensorFlow 노트북](https://colab.research.google.com/github/huggingface/notebooks/blob/main/examples/language_modeling-tf.ipynb)을 참조하세요.

</Tip>

## 추론[[inference]]

좋아요, 이제 모델을 미세 조정했으므로 추론에 사용할 수 있습니다!

생성할 텍스트를 위한 프롬프트를 만들어보세요:

```py
>>> prompt = "Somatic hypermutation allows the immune system to"
```

추론을 위해 미세 조정된 모델을 간단히 사용하는 가장 간단한 방법은 [`pipeline`]에서 사용하는 것입니다. 모델과 함께 텍스트 생성을 위한 `pipeline`을 인스턴스화하고 텍스트를 전달하세요:

```py
>>> from transformers import pipeline

>>> generator = pipeline("text-generation", model="my_awesome_eli5_clm-model")
>>> generator(prompt)
[{'generated_text': "Somatic hypermutation allows the immune system to be able to effectively reverse the damage caused by an infection.\n\n\nThe damage caused by an infection is caused by the immune system's ability to perform its own self-correcting tasks."}]
```

텍스트를 토큰화하고 `input_ids`를 PyTorch 텐서로 반환하세요:

```py
>>> from transformers import AutoTokenizer

>>> tokenizer = AutoTokenizer.from_pretrained("my_awesome_eli5_clm-model")
>>> inputs = tokenizer(prompt, return_tensors="pt").input_ids
```

[`~generation.GenerationMixin.generate`] 메소드를 사용하여 텍스트를 생성하세요. 생성을 제어하는 다양한 텍스트 생성 전략과 매개변수에 대한 자세한 내용은 [텍스트 생성 전략](../generation_strategies) 페이지를 확인하세요.

```py
>>> from transformers import AutoModelForCausalLM

>>> model = AutoModelForCausalLM.from_pretrained("my_awesome_eli5_clm-model")
>>> outputs = model.generate(inputs, max_new_tokens=100, do_sample=True, top_k=50, top_p=0.95)
```

생성된 토큰 ID를 다시 텍스트로 디코딩하세요:

```py
>>> tokenizer.batch_decode(outputs, skip_special_tokens=True)
["Somatic hypermutation allows the immune system to react to drugs with the ability to adapt to a different environmental situation. In other words, a system of 'hypermutation' can help the immune system to adapt to a different environmental situation or in some cases even a single life. In contrast, researchers at the University of Massachusetts-Boston have found that 'hypermutation' is much stronger in mice than in humans but can be found in humans, and that it's not completely unknown to the immune system. A study on how the immune system"]
```
