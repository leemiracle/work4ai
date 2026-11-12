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

# Train with a script

🤗 Transformersの[notebooks](./notebooks/README)と一緒に、[PyTorch](https://github.com/huggingface/transformers/tree/main/examples/pytorch)、[TensorFlow](https://github.com/huggingface/transformers/tree/main/examples/tensorflow)、または[JAX/Flax](https://github.com/huggingface/transformers/tree/main/examples/flax)を使用してモデルをトレーニングする方法を示すサンプルスクリプトもあります。

また、私たちの[研究プロジェクト](https://github.com/huggingface/transformers-research-projects)や[レガシーの例](https://github.com/huggingface/transformers/tree/main/examples/legacy)で使用したスクリプトも見つかります。これらのスクリプトは現在メンテナンスされておらず、おそらく最新バージョンのライブラリと互換性がない特定の🤗 Transformersのバージョンが必要です。

サンプルスクリプトはすべての問題でそのまま動作することは期待されておらず、解決しようとしている問題にスクリプトを適応させる必要があるかもしれません。この点をサポートするために、ほとんどのスクリプトはデータがどのように前処理されているかを完全に公開し、必要に応じて編集できるようにしています。

サンプルスクリプトで実装したい機能がある場合は、[フォーラム](https://discuss.huggingface.co)か[イシュートラッカー](https://github.com/huggingface/transformers/issues)で議論してからプルリクエストを提出してください。バグ修正は歓迎しますが、読みやすさのコストで機能を追加するプルリクエストはほとんどマージされない可能性が高いです。

このガイドでは、[PyTorch](https://github.com/huggingface/transformers/tree/main/examples/pytorch/summarization)と[TensorFlow](https://github.com/huggingface/transformers/tree/main/examples/tensorflow/summarization)で実行するサマリゼーショントレーニングスクリプトの実行方法を示します。すべての例は、明示的に指定されていない限り、両方のフレームワークともに動作することが期待されています。

## Setup

最新バージョンのサンプルスクリプトを正常に実行するには、新しい仮想環境に🤗 Transformersをソースからインストールする必要があります:


```bash
git clone https://github.com/huggingface/transformers
cd transformers
pip install .
```

以前のスクリプトのバージョンについては、以下のトグルをクリックしてください：

<details>
  <summary>以前の🤗 Transformersのバージョンに関する例</summary>
	<ul>
		<li><a href="https://github.com/huggingface/transformers/tree/v4.5.1/examples">v4.5.1</a></li>
		<li><a href="https://github.com/huggingface/transformers/tree/v4.4.2/examples">v4.4.2</a></li>
		<li><a href="https://github.com/huggingface/transformers/tree/v4.3.3/examples">v4.3.3</a></li>
		<li><a href="https://github.com/huggingface/transformers/tree/v4.2.2/examples">v4.2.2</a></li>
		<li><a href="https://github.com/huggingface/transformers/tree/v4.1.1/examples">v4.1.1</a></li>
		<li><a href="https://github.com/huggingface/transformers/tree/v4.0.1/examples">v4.0.1</a></li>
		<li><a href="https://github.com/huggingface/transformers/tree/v3.5.1/examples">v3.5.1</a></li>
		<li><a href="https://github.com/huggingface/transformers/tree/v3.4.0/examples">v3.4.0</a></li>
		<li><a href="https://github.com/huggingface/transformers/tree/v3.3.1/examples">v3.3.1</a></li>
		<li><a href="https://github.com/huggingface/transformers/tree/v3.2.0/examples">v3.2.0</a></li>
		<li><a href="https://github.com/huggingface/transformers/tree/v3.1.0/examples">v3.1.0</a></li>
		<li><a href="https://github.com/huggingface/transformers/tree/v3.0.2/examples">v3.0.2</a></li>
		<li><a href="https://github.com/huggingface/transformers/tree/v2.11.0/examples">v2.11.0</a></li>
		<li><a href="https://github.com/huggingface/transformers/tree/v2.10.0/examples">v2.10.0</a></li>
		<li><a href="https://github.com/huggingface/transformers/tree/v2.9.1/examples">v2.9.1</a></li>
		<li><a href="https://github.com/huggingface/transformers/tree/v2.8.0/examples">v2.8.0</a></li>
		<li><a href="https://github.com/huggingface/transformers/tree/v2.7.0/examples">v2.7.0</a></li>
		<li><a href="https://github.com/huggingface/transformers/tree/v2.6.0/examples">v2.6.0</a></li>
		<li><a href="https://github.com/huggingface/transformers/tree/v2.5.1/examples">v2.5.1</a></li>
		<li><a href="https://github.com/huggingface/transformers/tree/v2.4.0/examples">v2.4.0</a></li>
		<li><a href="https://github.com/huggingface/transformers/tree/v2.3.0/examples">v2.3.0</a></li>
		<li><a href="https://github.com/huggingface/transformers/tree/v2.2.0/examples">v2.2.0</a></li>
		<li><a href="https://github.com/huggingface/transformers/tree/v2.1.0/examples">v2.1.1</a></li>
		<li><a href="https://github.com/huggingface/transformers/tree/v2.0.0/examples">v2.0.0</a></li>
		<li><a href="https://github.com/huggingface/transformers/tree/v1.2.0/examples">v1.2.0</a></li>
		<li><a href="https://github.com/huggingface/transformers/tree/v1.1.0/examples">v1.1.0</a></li>
		<li><a href="https://github.com/huggingface/transformers/tree/v1.0.0/examples">v1.0.0</a></li>
	</ul>
</details>

次に、現在の🤗 Transformersのクローンを特定のバージョンに切り替えてください。たとえば、v3.5.1などです。


```bash
git checkout tags/v3.5.1
```


適切なライブラリバージョンを設定したら、任意の例のフォルダに移動し、例固有の要件をインストールします：



```bash
pip install -r requirements.txt
```

## Run a script

この例のスクリプトは、🤗 [Datasets](https://huggingface.co/docs/datasets) ライブラリからデータセットをダウンロードし、前処理を行います。次に、[Trainer](https://huggingface.co/docs/transformers/main_classes/trainer) を使用して要約をサポートするアーキテクチャ上でデータセットをファインチューニングします。以下の例では、[CNN/DailyMail](https://huggingface.co/datasets/cnn_dailymail) データセット上で [T5-small](https://huggingface.co/google-t5/t5-small) をファインチューニングする方法が示されています。T5 モデルは、そのトレーニング方法に起因して追加の `source_prefix` 引数が必要です。このプロンプトにより、T5 はこれが要約タスクであることを知ることができます。


```bash
python examples/pytorch/summarization/run_summarization.py \
    --model_name_or_path google-t5/t5-small \
    --do_train \
    --do_eval \
    --dataset_name cnn_dailymail \
    --dataset_config "3.0.0" \
    --source_prefix "summarize: " \
    --output_dir /tmp/tst-summarization \
    --per_device_train_batch_size=4 \
    --per_device_eval_batch_size=4 \
    --predict_with_generate
```


## Distributed training and mixed precision

[Trainer](https://huggingface.co/docs/transformers/main_classes/trainer)は、分散トレーニングと混合精度をサポートしています。つまり、この機能をスクリプトで使用することができます。これらの機能を有効にするには、次の手順を実行します。

- `fp16`引数を追加して混合精度を有効にします。
- `nproc_per_node`引数で使用するGPUの数を設定します。

以下は提供されたBashコードです。このコードの日本語訳をMarkdown形式で記載します。

```bash
torchrun \
    --nproc_per_node 8 pytorch/summarization/run_summarization.py \
    --fp16 \
    --model_name_or_path google-t5/t5-small \
    --do_train \
    --do_eval \
    --dataset_name cnn_dailymail \
    --dataset_config "3.0.0" \
    --source_prefix "summarize: " \
    --output_dir /tmp/tst-summarization \
    --per_device_train_batch_size=4 \
    --per_device_eval_batch_size=4 \
    --predict_with_generate
```


TensorFlowスクリプトは、分散トレーニングに[`MirroredStrategy`](https://www.tensorflow.org/guide/distributed_training#mirroredstrategy)を使用し、トレーニングスクリプトに追加の引数を追加する必要はありません。TensorFlowスクリプトは、デフォルトで複数のGPUが利用可能な場合にそれらを使用します。

## Run a script on a TPU

Tensor Processing Units (TPUs)は、パフォーマンスを加速させるために特別に設計されています。PyTorchは、[XLA](https://www.tensorflow.org/xla)ディープラーニングコンパイラを使用してTPUsをサポートしており、詳細については[こちら](https://github.com/pytorch/xla/blob/master/README.md)をご覧ください。TPUを使用するには、`xla_spawn.py`スクリプトを起動し、`num_cores`引数を使用して使用するTPUコアの数を設定します。
```bash
python xla_spawn.py --num_cores 8 \
    summarization/run_summarization.py \
    --model_name_or_path google-t5/t5-small \
    --do_train \
    --do_eval \
    --dataset_name cnn_dailymail \
    --dataset_config "3.0.0" \
    --source_prefix "summarize: " \
    --output_dir /tmp/tst-summarization \
    --per_device_train_batch_size=4 \
    --per_device_eval_batch_size=4 \
    --predict_with_generate
```

## Run a script with 🤗 Accelerate

🤗 [Accelerate](https://huggingface.co/docs/accelerate)は、PyTorch専用のライブラリで、CPUのみ、複数のGPU、TPUなど、さまざまなセットアップでモデルをトレーニングするための統一された方法を提供します。PyTorchのトレーニングループを完全に可視化しながら実行できます。まだインストールしていない場合は、🤗 Accelerateをインストールしてください：

> 注意：Accelerateは急速に開発が進行しているため、スクリプトを実行するにはaccelerateのgitバージョンをインストールする必要があります
```bash
pip install git+https://github.com/huggingface/accelerate
```

代わりに、`run_summarization_no_trainer.py` スクリプトを使用する必要があります。 🤗 Accelerate がサポートするスクリプトには、フォルダ内に `task_no_trainer.py` ファイルが含まれています。まず、次のコマンドを実行して設定ファイルを作成し、保存します：

```bash
accelerate config
```

テストを行い、設定が正しく構成されているか確認してください：


```bash
accelerate test
```

Now you are ready to launch the training:


```bash
accelerate launch run_summarization_no_trainer.py \
    --model_name_or_path google-t5/t5-small \
    --dataset_name cnn_dailymail \
    --dataset_config "3.0.0" \
    --source_prefix "summarize: " \
    --output_dir ~/tmp/tst-summarization
```

## Use a custom dataset

要約スクリプトは、CSVまたはJSON Lineファイルであれば、カスタムデータセットをサポートしています。独自のデータセットを使用する場合、いくつかの追加の引数を指定する必要があります。

- `train_file`および`validation_file`は、トレーニングとバリデーションのファイルへのパスを指定します。
- `text_column`は要約するための入力テキストです。
- `summary_column`は出力する対象テキストです。

カスタムデータセットを使用した要約スクリプトは、以下のようになります：

```bash
python examples/pytorch/summarization/run_summarization.py \
    --model_name_or_path google-t5/t5-small \
    --do_train \
    --do_eval \
    --train_file path_to_csv_or_jsonlines_file \
    --validation_file path_to_csv_or_jsonlines_file \
    --text_column text_column_name \
    --summary_column summary_column_name \
    --source_prefix "summarize: " \
    --output_dir /tmp/tst-summarization \
    --per_device_train_batch_size=4 \
    --per_device_eval_batch_size=4 \
    --predict_with_generate
```

## Test a script

すべてが予想通りに動作することを確認するために、データセット全体を処理する前に、データセットの一部の例でスクリプトを実行することは良いアイデアです。以下の引数を使用して、データセットを最大サンプル数に切り詰めます：

- `max_train_samples`
- `max_eval_samples`
- `max_predict_samples`

```bash
python examples/pytorch/summarization/run_summarization.py \
    --model_name_or_path google-t5/t5-small \
    --max_train_samples 50 \
    --max_eval_samples 50 \
    --max_predict_samples 50 \
    --do_train \
    --do_eval \
    --dataset_name cnn_dailymail \
    --dataset_config "3.0.0" \
    --source_prefix "summarize: " \
    --output_dir /tmp/tst-summarization \
    --per_device_train_batch_size=4 \
    --per_device_eval_batch_size=4 \
    --predict_with_generate
```

一部の例のスクリプトは、`max_predict_samples`引数をサポートしていないことがあります。この引数がサポートされているかどうかがわからない場合は、`-h`引数を追加して確認してください。

```bash
examples/pytorch/summarization/run_summarization.py -h
```

## Resume training from checkpoint

以前のチェックポイントからトレーニングを再開するための役立つオプションもあります。これにより、トレーニングが中断された場合でも、最初からやり直すことなく、中断したところから再開できます。チェックポイントからトレーニングを再開するための2つの方法があります。

```bash
python examples/pytorch/summarization/run_summarization.py
    --model_name_or_path google-t5/t5-small \
    --do_train \
    --do_eval \
    --dataset_name cnn_dailymail \
    --dataset_config "3.0.0" \
    --source_prefix "summarize: " \
    --output_dir /tmp/tst-summarization \
    --per_device_train_batch_size=4 \
    --per_device_eval_batch_size=4 \
    --resume_from_checkpoint path_to_specific_checkpoint \
    --predict_with_generate
```

## Share your model

すべてのスクリプトは、最終的なモデルを [Model Hub](https://huggingface.co/models) にアップロードできます。開始する前に Hugging Face にログインしていることを確認してください。

```bash
hf auth login
```

次に、スクリプトに `push_to_hub` 引数を追加します。この引数は、Hugging Face のユーザー名と `output_dir` で指定したフォルダ名でリポジトリを作成します。

特定の名前をリポジトリに付けるには、`push_to_hub_model_id` 引数を使用して追加します。このリポジトリは自動的にあなたの名前空間の下にリストされます。

以下の例は、特定のリポジトリ名でモデルをアップロードする方法を示しています:



```bash
python examples/pytorch/summarization/run_summarization.py
    --model_name_or_path google-t5/t5-small \
    --do_train \
    --do_eval \
    --dataset_name cnn_dailymail \
    --dataset_config "3.0.0" \
    --source_prefix "summarize: " \
    --push_to_hub \
    --push_to_hub_model_id finetuned-t5-cnn_dailymail \
    --output_dir /tmp/tst-summarization \
    --per_device_train_batch_size=4 \
    --per_device_eval_batch_size=4 \
    --predict_with_generate
```




