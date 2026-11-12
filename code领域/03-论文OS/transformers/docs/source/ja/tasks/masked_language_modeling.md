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

# Masked language modeling

[[open-in-colab]]

<Youtube id="mqElG5QJWUg"/>

マスクされた言語モデリングはシーケンス内のマスクされたトークンを予測し、モデルはトークンを双方向に処理できます。これ
これは、モデルが左右のトークンに完全にアクセスできることを意味します。マスクされた言語モデリングは、次のようなタスクに最適です。
シーケンス全体の文脈をよく理解する必要があります。 BERT はマスクされた言語モデルの一例です。

このガイドでは、次の方法を説明します。

1. [ELI5](https://huggingface.co/distilbert/distilroberta-base) の [r/askscience](https://www.reddit.com/r/askscience) サブセットで [DistilRoBERTa](https://huggingface.co/distilbert/distilroberta-base) を微調整します。 ://huggingface.co/datasets/eli5) データセット。
2. 微調整したモデルを推論に使用します。

<Tip>

このタスクと互換性のあるすべてのアーキテクチャとチェックポイントを確認するには、[タスクページ](https://huggingface.co/tasks/fill-mask) を確認することをお勧めします。

</Tip>

始める前に、必要なライブラリがすべてインストールされていることを確認してください。

```bash
pip install transformers datasets evaluate
```

モデルをアップロードしてコミュニティと共有できるように、Hugging Face アカウントにログインすることをお勧めします。プロンプトが表示されたら、トークンを入力してログインします。

```py
>>> from huggingface_hub import notebook_login

>>> notebook_login()
```

## Load ELI5 dataset

まず、ELI5 データセットの r/askscience サブセットの小さいサブセットを 🤗 データセット ライブラリからロードします。これで
データセット全体のトレーニングにさらに時間を費やす前に、実験してすべてが機能することを確認する機会が与えられます。

```py
>>> from datasets import load_dataset

>>> eli5 = load_dataset("eli5", split="train_asks[:5000]")
```

[`~datasets.Dataset.train_test_split`] メソッドを使用して、データセットの `train_asks` をトレイン セットとテスト セットに分割します。

```py
>>> eli5 = eli5.train_test_split(test_size=0.2)
```

次に、例を見てみましょう。

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

これは多くのことのように見えるかもしれませんが、実際に関心があるのは`text`フィールドだけです。言語モデリング タスクの優れた点は、次の単語がラベル * であるため、ラベル (教師なしタスクとも呼ばれます) が必要ないことです。

## Preprocess

<Youtube id="8PmhEIXhBvI"/>

マスクされた言語モデリングの場合、次のステップは、`text`サブフィールドを処理するために DistilRoBERTa トークナイザーをロードすることです。

```py
>>> from transformers import AutoTokenizer

>>> tokenizer = AutoTokenizer.from_pretrained("distilbert/distilroberta-base")
```

上の例からわかるように、`text`フィールドは実際には`answers`内にネストされています。これは、次のことを行う必要があることを意味します
[` flatten`](https://huggingface.co/docs/datasets/process.html#flatten) メソッドを使用して、ネストされた構造から `text` サブフィールドを抽出します。

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

`answers`接頭辞で示されるように、各サブフィールドは個別の列になり、`text`フィールドはリストになりました。その代わり
各文を個別にトークン化する場合は、リストを文字列に変換して、それらをまとめてトークン化できるようにします。

以下は、各例の文字列のリストを結合し、結果をトークン化する最初の前処理関数です。

```py
>>> def preprocess_function(examples):
...     return tokenizer([" ".join(x) for x in examples["answers.text"]])
```

この前処理関数をデータセット全体に適用するには、🤗 Datasets [`~datasets.Dataset.map`] メソッドを使用します。 `map` 関数を高速化するには、`batched=True` を設定してデータセットの複数の要素を一度に処理し、`num_proc` でプロセスの数を増やします。不要な列を削除します。

```py
>>> tokenized_eli5 = eli5.map(
...     preprocess_function,
...     batched=True,
...     num_proc=4,
...     remove_columns=eli5["train"].column_names,
... )
```

このデータセットにはトークン シーケンスが含まれていますが、その一部はモデルの最大入力長よりも長くなります。

2 番目の前処理関数を使用して、
- すべてのシーケンスを連結します
- 連結されたシーケンスを`block_size`で定義された短いチャンクに分割します。これは、最大入力長より短く、GPU RAM に十分な長さである必要があります。

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
...     return result
```

データセット全体に`group_texts`関数を適用します。

```py
>>> lm_dataset = tokenized_eli5.map(group_texts, batched=True, num_proc=4)
```

次に、[`DataCollat​​orForLanguageModeling`] を使用してサンプルのバッチを作成します。データセット全体を最大長までパディングするのではなく、照合中にバッチ内の最長の長さまで文を *動的にパディング* する方が効率的です。


シーケンス終了トークンをパディング トークンとして使用し、データを反復するたびにランダムにトークンをマスクするために `mlm_probability` を指定します。

```py
>>> from transformers import DataCollatorForLanguageModeling

>>> tokenizer.pad_token = tokenizer.eos_token
>>> data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm_probability=0.15)
```

## Train

<Tip>

[`Trainer`] を使用したモデルの微調整に慣れていない場合は、[ここ](../training#train-with-pytorch-trainer) の基本的なチュートリアルをご覧ください。

</Tip>

これでモデルのトレーニングを開始する準備が整いました。 [`AutoModelForMaskedLM`] を使用して DistilRoBERTa をロードします。

```py
>>> from transformers import AutoModelForMaskedLM

>>> model = AutoModelForMaskedLM.from_pretrained("distilbert/distilroberta-base")
```

この時点で残っている手順は次の 3 つだけです。

1. [`TrainingArguments`] でトレーニング ハイパーパラメータを定義します。唯一の必須パラメータは、モデルの保存場所を指定する `output_dir` です。 `push_to_hub=True`を設定して、このモデルをハブにプッシュします (モデルをアップロードするには、Hugging Face にサインインする必要があります)。
2. トレーニング引数をモデル、データセット、データ照合器とともに [`Trainer`] に渡します。
3. [`~Trainer.train`] を呼び出してモデルを微調整します。

```py
>>> training_args = TrainingArguments(
...     output_dir="my_awesome_eli5_mlm_model",
...     eval_strategy="epoch",
...     learning_rate=2e-5,
...     num_train_epochs=3,
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

トレーニングが完了したら、 [`~transformers.Trainer.evaluate`] メソッドを使用してモデルを評価し、その複雑さを取得します。


```py
>>> import math

>>> eval_results = trainer.evaluate()
>>> print(f"Perplexity: {math.exp(eval_results['eval_loss']):.2f}")
Perplexity: 8.76
```

次に、 [`~transformers.Trainer.push_to_hub`] メソッドを使用してモデルをハブに共有し、誰もがモデルを使用できるようにします。

```py
>>> trainer.push_to_hub()
```


<Tip>

マスクされた言語モデリング用にモデルを微調整する方法のより詳細な例については、対応するドキュメントを参照してください。
[PyTorch ノートブック](https://colab.research.google.com/github/huggingface/notebooks/blob/main/examples/language_modeling.ipynb)
または [TensorFlow ノートブック](https://colab.research.google.com/github/huggingface/notebooks/blob/main/examples/language_modeling-tf.ipynb)。

</Tip>

## Inference

モデルを微調整したので、それを推論に使用できるようになりました。

モデルに空白を埋めるテキストを考え出し、特別な `<mask>` トークンを使用して空白を示します。

```py
>>> text = "The Milky Way is a <mask> galaxy."
```

推論用に微調整されたモデルを試す最も簡単な方法は、それを [`pipeline`] で使用することです。モデルを使用してフィルマスクの`pipeline`をインスタンス化し、テキストをそれに渡します。必要に応じて、`top_k`パラメータを使用して、返す予測の数を指定できます。

```py
>>> from transformers import pipeline

>>> mask_filler = pipeline("fill-mask", "stevhliu/my_awesome_eli5_mlm_model")
>>> mask_filler(text, top_k=3)
[{'score': 0.5150994658470154,
  'token': 21300,
  'token_str': ' spiral',
  'sequence': 'The Milky Way is a spiral galaxy.'},
 {'score': 0.07087188959121704,
  'token': 2232,
  'token_str': ' massive',
  'sequence': 'The Milky Way is a massive galaxy.'},
 {'score': 0.06434620916843414,
  'token': 650,
  'token_str': ' small',
  'sequence': 'The Milky Way is a small galaxy.'}]
```


テキストをトークン化し、`input_ids`を PyTorch テンソルとして返します。 `<mask>` トークンの位置も指定する必要があります。

```py
>>> from transformers import AutoTokenizer

>>> tokenizer = AutoTokenizer.from_pretrained("stevhliu/my_awesome_eli5_mlm_model")
>>> inputs = tokenizer(text, return_tensors="pt")
>>> mask_token_index = torch.where(inputs["input_ids"] == tokenizer.mask_token_id)[1]
```

入力をモデルに渡し、マスクされたトークンの`logits`を返します。

```py
>>> from transformers import AutoModelForMaskedLM

>>> model = AutoModelForMaskedLM.from_pretrained("stevhliu/my_awesome_eli5_mlm_model")
>>> logits = model(**inputs).logits
>>> mask_token_logits = logits[0, mask_token_index, :]
```

次に、マスクされた 3 つのトークンを最も高い確率で返し、出力します。

```py
>>> top_3_tokens = torch.topk(mask_token_logits, 3, dim=1).indices[0].tolist()

>>> for token in top_3_tokens:
...     print(text.replace(tokenizer.mask_token, tokenizer.decode([token])))
The Milky Way is a spiral galaxy.
The Milky Way is a massive galaxy.
The Milky Way is a small galaxy.
```

