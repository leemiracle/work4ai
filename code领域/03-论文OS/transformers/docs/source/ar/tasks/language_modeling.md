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

# نمذجة اللغة السببية (Causal language modeling)

[[open-in-colab]]

هناك نوعان من نمذجة اللغة، السببية والمقنعة. يوضح هذا الدليل نمذجة اللغة السببية.
تُستخدم نماذج اللغة السببية غالبًا لتوليد النص. يمكنك استخدام هذه النماذج للتطبيقات الإبداعية مثل
اختيار مغامرة النص الخاصة بك أو مساعد ترميز ذكي مثل Copilot أو CodeParrot.

<Youtube id="Vpjb1lu0MDk"/>

تتنبأ نمذجة اللغة السببية بالرمز التالي في تسلسل من الرموز، ولا يمكن للنموذج سوى الاهتمام بالرموز على
اليسار. هذا يعني أن النموذج لا يمكنه رؤية الرموز المستقبلية. GPT-2 هو مثال على نموذج اللغة السببية.

سيوضح لك هذا الدليل كيفية:

1. ضبط دقيق [DistilRoBERTa](https://huggingface.co/distilbert/distilroberta-base) على مجموعة فرعية [r/askscience](https://www.reddit.com/r/askscience) من مجموعة بيانات [ELI5](https://huggingface.co/datasets/eli5).
2.  استخدام النموذج المدرب الخاص بك للاستنتاج.

<Tip>

لرؤية جميع العمارات ونقاط التحقق المتوافقة مع هذه المهمة، نوصي بالتحقق من [task-page](https://huggingface.co/tasks/text-generation)

</Tip>

قبل أن تبدأ، تأكد من تثبيت جميع المكتبات الضرورية:

```bash
pip install transformers datasets evaluate
```

نحن نشجعك على تسجيل الدخول إلى حساب Hugging Face الخاص بك حتى تتمكن من تحميل ومشاركة نموذجك مع المجتمع. عند المطالبة، أدخل رمزك لتسجيل الدخول:

```py
>>> from huggingface_hub import notebook_login

>>> notebook_login()
```

## تحميل مجموعة بيانات ELI5

ابدأ بتحميل أول 5000 مثال من [ELI5-Category](https://huggingface.co/datasets/eli5_category) مجموعة البيانات مع مكتبة 🤗 Datasets. سيعطيك هذا فرصة للتجربة والتأكد من أن كل شيء يعمل قبل قضاء المزيد من الوقت في التدريب على مجموعة البيانات الكاملة.

```py
>>> from datasets import load_dataset

>>> eli5 = load_dataset("eli5_category", split="train[:5000]")
```

قم بتقسيم مجموعة بيانات `train` إلى مجموعتي تدريب واختبار باستخدام الخاصية [`~datasets.Dataset.train_test_split`]:

```py
>>> eli5 = eli5.train_test_split(test_size=0.2)
```

ثم ألق نظرة على مثال:

```py
>>> eli5["train"][0]
{'q_id': '7h191n',
 'title': 'What does the tax bill that was passed today mean? How will it affect Americans in each tax bracket?',
 'selftext': '',
 'category': 'Economics',
 'subreddit': 'explainlikeimfive',
 'answers': {'a_id': ['dqnds8l', 'dqnd1jl', 'dqng3i1', 'dqnku5x'],
  'text': ["The tax bill is 500 pages long and there were a lot of changes still going on right to the end. It's not just an adjustment to the income tax brackets, it's a whole bunch of changes. As such there is no good answer to your question. The big take aways are: - Big reduction in corporate income tax rate will make large companies very happy. - Pass through rate change will make certain styles of business (law firms, hedge funds) extremely happy - Income tax changes are moderate, and are set to expire (though it's the kind of thing that might just always get re-applied without being made permanent) - People in high tax states (California, New York) lose out, and many of them will end up with their taxes raised.",
   'None yet. It has to be reconciled with a vastly different house bill and then passed again.',
   'Also: does this apply to 2017 taxes? Or does it start with 2018 taxes?',
   'This article explains both the House and senate bills, including the proposed changes to your income taxes based on your income level. URL_0'],
  'score': [21, 19, 5, 3],
  'text_urls': [[],
   [],
   [],
   ['https://www.investopedia.com/news/trumps-tax-reform-what-can-be-done/']]},
 'title_urls': ['url'],
 'selftext_urls': ['url']}
```

على الرغم من أن هذا قد يبدو معقدًا، إلا أنك مهتم حقًا بحقل `text`. ما هو رائع حول مهام نمذجة اللغة
أنت لا تحتاج إلى تسميات (تُعرف أيضًا باسم المهمة غير الخاضعة للإشراف) لأن الكلمة التالية تعمل كتسمية.

## معالجة مسبقة (Preprocess)

<Youtube id="ma1TrR7gE7I"/>

الخطوة التالية هي تحميل مجزء النص DistilGPT2 لمعالجة حقل `text` الفرعي:

```py
>>> from transformers import AutoTokenizer

>>> tokenizer = AutoTokenizer.from_pretrained("distilbert/distilgpt2")
```

ستلاحظ من المثال أعلاه، الحقل `text` هو في الواقع متداخل داخل `answers`. هذا يعني أنك ستحتاج إلى
استخراج حقل `text` الفرعي من بنيته المتداخلة باستخدام الدالة [`flatten`](https://huggingface.co/docs/datasets/process#flatten):

```py
>>> eli5 = eli5.flatten()
>>> eli5["train"][0]
{'q_id': '7h191n',
 'title': 'What does the tax bill that was passed today mean? How will it affect Americans in each tax bracket?',
 'selftext': '',
 'category': 'Economics',
 'subreddit': 'explainlikeimfive',
 'answers.a_id': ['dqnds8l', 'dqnd1jl', 'dqng3i1', 'dqnku5x'],
 'answers.text': ["The tax bill is 500 pages long and there were a lot of changes still going on right to the end. It's not just an adjustment to the income tax brackets, it's a whole bunch of changes. As such there is no good answer to your question. The big take aways are: - Big reduction in corporate income tax rate will make large companies very happy. - Pass through rate change will make certain styles of business (law firms, hedge funds) extremely happy - Income tax changes are moderate, and are set to expire (though it's the kind of thing that might just always get re-applied without being made permanent) - People in high tax states (California, New York) lose out, and many of them will end up with their taxes raised.",
  'None yet. It has to be reconciled with a vastly different house bill and then passed again.',
  'Also: does this apply to 2017 taxes? Or does it start with 2018 taxes?',
  'This article explains both the House and senate bills, including the proposed changes to your income taxes based on your income level. URL_0'],
 'answers.score': [21, 19, 5, 3],
 'answers.text_urls': [[],
  [],
  [],
  ['https://www.investopedia.com/news/trumps-tax-reform-what-can-be-done/']],
 'title_urls': ['url'],
 'selftext_urls': ['url']}
```

كل حقل فرعي هو الآن عموداً منفصلاً مسبوقاً بـ `answers`، وحقل `text` هو قائمة الآن. بدلاً من ذلك
من تجزائة نص كل جملة بشكل منفصل، قم بتحويل القائمة إلى سلسلة حتى تتمكن من تجزئة نصها بشكل مجمّع.

هنا أول دالة معالجة مسبقة لدمج قائمة السلاسل لكل مثال ومجزىء النتيجة:

```py
>>> def preprocess_function(examples):
...     return tokenizer([" ".join(x) for x in examples["answers.text"]])
```

لتطبيق دالة المعالجة المسبقة هذه على مجموعة البيانات بأكملها، استخدم الدالة 🤗 Datasets [`~datasets.Dataset.map`]. يمكنك تسريع  هذه العملية `map` عن طريق تعيين `batched=True` لمعالجة عناصر متعددة من مجموعة البيانات في وقت واحد، وزيادة عدد العمليات مع `num_proc`. احذف أي أعمدة لا تحتاجها:

```py
>>> tokenized_eli5 = eli5.map(
...     preprocess_function,
...     batched=True,
...     num_proc=4,
...     remove_columns=eli5["train"].column_names,
... )
```

تحتوي هذه المجموعة من البيانات على تسلسلات الرموز، ولكن بعضها أطول من الطول الأقصى للمدخلات للنموذج.

يمكنك الآن استخدام دالة ما قبل المعالجة ثانية لـ:

- تجميع كل التسلسلات.
- تقسيم التسلسلات المجمّعة إلى أجزاء أقصر محددة، بحجم `block_size`، والتي يجب أن تكون أقصر من الطول الأقصى للمدخلات ومناسبة لذاكرة GPU.

```py
>>> block_size = 128

>>> def group_texts(examples):
...     # ربط جميع النصوص.
...     concatenated_examples = {k: sum(examples[k], []) for k in examples.keys()}
...     total_length = len(concatenated_examples[list(examples.keys())[0]])
...     # نتجاهل الباقي الصغير، يمكننا إضافة الحشو إذا كان النموذج يدعمه بدلاً من هذا الإسقاط، يمكنك
...     # تخصيص هذا الجزء حسب احتياجاتك.
...     if total_length >= block_size:
...         total_length = (total_length // block_size) * block_size
...     # التقسيم إلى أجزاء بحجم block_size.
...     result = {
...         k: [t[i : i + block_size] for i in range(0, total_length, block_size)]
...         for k, t in concatenated_examples.items()
...     }
...     result["labels"] = result["input_ids"].copy()
...     return result
```

طبق دالة `group_texts` على كامل المجموعة من البيانات:

```py
>>> lm_dataset = tokenized_eli5.map(group_texts, batched=True, num_proc=4)
```

الآن قم بإنشاء دفعة من الأمثلة باستخدام [`DataCollatorForLanguageModeling`]. من الأفضل أن تقوم بـ *الحشو الديناميكي* للجمل إلى الطول الأطول في الدفعة أثناء التجميع، بدلاً من حشو كامل المجموعة من البيانات إلى الطول الأقصى.

استخدم رمز نهاية التسلسل كرمز للحشو، وحدد `mlm_probability` لحجب الرموز بشكل عشوائي عند كل تكرار للبيانات:

```py
>>> from transformers import DataCollatorForLanguageModeling

>>> tokenizer.pad_token = tokenizer.eos_token
>>> data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
```


## التدريب (Train)


<Tip>

إذا لم تكن على دراية بتدريب نموذج باستخدام [`Trainer`], اطلع على [البرنامج التعليمي الأساسي](../training#train-with-pytorch-trainer)!

</Tip>

أنت جاهز الآن لبدء تدريب نموذجك! قم بتحميل DistilGPT2 باستخدام [`AutoModelForCausalLM`]:

```py
>>> from transformers import AutoModelForCausalLM, TrainingArguments, Trainer

>>> model = AutoModelForCausalLM.from_pretrained("distilbert/distilgpt2")
```

في هذه المرحلة، تبقى ثلاث خطوات فقط:

1. حدد معلمات التدريب الخاصة بك في [`TrainingArguments`]. المعامل الوحيد المطلوب هو `output_dir` الذي يحدد أين سيتم حفظ نموذجك. ستقوم بدفع هذا النموذج إلى Hub بتحديد `push_to_hub=True` (يجب أن تكون مسجلاً الدخول إلى Hugging Face لتحميل نموذجك).
2. قم بتمرير معاملات التدريب إلى [`Trainer`] إلى جانب النموذج، والمجموعات من البيانات، ومجمّع البيانات.
3. قم باستدعاء [`~Trainer.train`] لتدريب نموذجك.

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
...     tokenizer=tokenizer,
... )

>>> trainer.train()
```

بمجرد اكتمال التدريب، استخدم طريقة [`~transformers.Trainer.evaluate`] لتقييم نموذجك والحصول على احتمالية الارتباك:

```py
>>> import math

>>> eval_results = trainer.evaluate()
>>> print(f"Perplexity: {math.exp(eval_results['eval_loss']):.2f}")
Perplexity: 49.61
```

ثم شارك نموذجك على Hub باستخدام طريقة [`~transformers.Trainer.push_to_hub`] حتى يتمكن الجميع من استخدام نموذجك:

```py
>>> trainer.push_to_hub()
```

<Tip>

للحصول على مثال أكثر تعمقًا حول كيفية تدريب نموذج للنمذجة اللغوية السببية، اطلع على الدفتر المقابل
[دفتر PyTorch](https://colab.research.google.com/github/huggingface/notebooks/blob/main/examples/language_modeling.ipynb)
أو [دفتر TensorFlow](https://colab.research.google.com/github/huggingface/notebooks/blob/main/examples/language_modeling-tf.ipynb).

</Tip>

## الاستدلال (Inference)

رائع، الآن بعد أن قمت بتدريب نموذج، يمكنك استخدامه للاستدلال!

قم بابتكار سؤال تود توليد نص منه:

```py
>>> prompt = "Somatic hypermutation allows the immune system to"
```

أبسط طريقة لتجربة نموذجك المدرب للاستدلال هي استخدامه في [`pipeline`]. قم بتنفيذ `pipeline` لتوليد النص مع نموذجك، ومرر نصك إليه:

```py
>>> from transformers import pipeline

>>> generator = pipeline("text-generation", model="username/my_awesome_eli5_clm-model")
>>> generator(prompt)
[{'generated_text': "Somatic hypermutation allows the immune system to be able to effectively reverse the damage caused by an infection.\n\n\nThe damage caused by an infection is caused by the immune system's ability to perform its own self-correcting tasks."}]
```

قسم النص وإرجع `input_ids` كتنسورات PyTorch:

```py
>>> from transformers import AutoTokenizer

>>> tokenizer = AutoTokenizer.from_pretrained("username/my_awesome_eli5_clm-model")
>>> inputs = tokenizer(prompt, return_tensors="pt").input_ids
```

استخدم طريقة [`~generation.GenerationMixin.generate`] لتوليد النص.
للمزيد من التفاصيل حول استراتيجيات توليد النص المختلفة والبارامترات للتحكم في التوليد، راجع صفحة [استراتيجيات توليد النص](../generation_strategies).

```py
>>> from transformers import AutoModelForCausalLM

>>> model = AutoModelForCausalLM.from_pretrained("username/my_awesome_eli5_clm-model")
>>> outputs = model.generate(inputs, max_new_tokens=100, do_sample=True, top_k=50, top_p=0.95)
```

فك ترميز الرموز المولدة مرة أخرى إلى نص:

```py
>>> tokenizer.batch_decode(outputs, skip_special_tokens=True)
["Somatic hypermutation allows the immune system to react to drugs with the ability to adapt to a different environmental situation. In other words, a system of 'hypermutation' can help the immune system to adapt to a different environmental situation or in some cases even a single life. In contrast, researchers at the University of Massachusetts-Boston have found that 'hypermutation' is much stronger in mice than in humans but can be found in humans, and that it's not completely unknown to the immune system. A study on how the immune system"]
```
