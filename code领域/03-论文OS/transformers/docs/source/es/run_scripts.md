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

# Entrenamiento con scripts

Junto con los [notebooks](./notebooks) de 🤗 Transformers, también hay scripts con ejemplos que muestran cómo entrenar un modelo para una tarea en [PyTorch](https://github.com/huggingface/transformers/tree/main/examples/pytorch), [TensorFlow](https://github.com/huggingface/transformers/tree/main/examples/tensorflow), o [JAX/Flax](https://github.com/huggingface/transformers/tree/main/examples/flax).

También encontrarás scripts que hemos usado en nuestros [proyectos de investigación](https://github.com/huggingface/transformers-research-projects) y [ejemplos pasados](https://github.com/huggingface/transformers/tree/main/examples/legacy) que en su mayoría son aportados por la comunidad. Estos scripts no se mantienen activamente y requieren una versión específica de 🤗 Transformers que probablemente sea incompatible con la última versión de la biblioteca.

No se espera que los scripts de ejemplo funcionen de inmediato en todos los problemas, y es posible que debas adaptar el script al problema que estás tratando de resolver. Para ayudarte con esto, la mayoría de los scripts exponen completamente cómo se preprocesan los datos, lo que te permite editarlos según sea necesario para tu caso de uso.

Para cualquier característica que te gustaría implementar en un script de ejemplo, por favor discútelo en el [foro](https://discuss.huggingface.co) o con un [issue](https://github.com/huggingface/transformers/issues) antes de enviar un Pull Request. Si bien agradecemos las correcciones de errores, es poco probable que fusionemos un Pull Request que agregue más funcionalidad a costa de la legibilidad.

Esta guía te mostrará cómo ejecutar un ejemplo de un script de entrenamiento para resumir texto en [PyTorch](https://github.com/huggingface/transformers/tree/main/examples/pytorch/summarization) y [TensorFlow](https://github.com/huggingface/transformers/tree/main/examples/tensorflow/summarization). Se espera que todos los ejemplos funcionen con ambos frameworks a menos que se especifique lo contrario.

## Configuración

Para ejecutar con éxito la última versión de los scripts de ejemplo debes **instalar 🤗 Transformers desde su fuente** en un nuevo entorno virtual:

```bash
git clone https://github.com/huggingface/transformers
cd transformers
pip install .
```

Para versiones anteriores de los scripts de ejemplo, haz clic en alguno de los siguientes links:

<details>
  <summary>Ejemplos de versiones anteriores de 🤗 Transformers</summary>
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

Luego cambia tu clon actual de 🤗 Transformers a una versión específica, por ejemplo v3.5.1:

```bash
git checkout tags/v3.5.1
```

Una vez que hayas configurado la versión correcta de la biblioteca, ve a la carpeta de ejemplo de tu elección e instala los requisitos específicos del ejemplo:

```bash
pip install -r requirements.txt
```

## Ejecutar un script

El script de ejemplo descarga y preprocesa un conjunto de datos de la biblioteca 🤗 [Datasets](https://huggingface.co/docs/datasets). Luego, el script ajusta un conjunto de datos con [Trainer](https://huggingface.co/docs/transformers/main_classes/trainer) en una arquitectura que soporta la tarea de resumen. El siguiente ejemplo muestra cómo ajustar un [T5-small](https://huggingface.co/google-t5/t5-small) en el conjunto de datos [CNN/DailyMail](https://huggingface.co/datasets/cnn_dailymail). El modelo T5 requiere un argumento adicional `source_prefix` debido a cómo fue entrenado. Este aviso le permite a T5 saber que se trata de una tarea de resumir.

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

## Entrenamiento distribuido y de precisión mixta

[Trainer](https://huggingface.co/docs/transformers/main_classes/trainer) admite un entrenamiento distribuido y de precisión mixta, lo que significa que también puedes usarlo en un script. Para habilitar ambas características:

- Agrega el argumento `fp16` para habilitar la precisión mixta.
- Establece la cantidad de GPU que se usará con el argumento `nproc_per_node`.

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

Los scripts de TensorFlow utilizan [`MirroredStrategy`](https://www.tensorflow.org/guide/distributed_training#mirroredstrategy) para el entrenamiento distribuido, y no es necesario agregar argumentos adicionales al script de entrenamiento. El script de TensorFlow utilizará múltiples GPUs de forma predeterminada si están disponibles.

## Ejecutar un script en una TPU

Las Unidades de Procesamiento de Tensor (TPUs) están diseñadas específicamente para acelerar el rendimiento. PyTorch admite TPU con el compilador de aprendizaje profundo [XLA](https://www.tensorflow.org/xla) (consulta [aquí](https://github.com/pytorch/xla/blob/master/README.md) para obtener más detalles). Para usar una TPU, inicia el script `xla_spawn.py` y usa el argumento `num_cores` para establecer la cantidad de núcleos de TPU que deseas usar.

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

## Ejecutar un script con 🤗 Accelerate

🤗 [Accelerate](https://huggingface.co/docs/accelerate) es una biblioteca exclusiva de PyTorch que ofrece un método unificado para entrenar un modelo en varios tipos de configuraciones (solo CPU, GPU múltiples, TPU) mientras mantiene una visibilidad completa en el ciclo de entrenamiento de PyTorch. Asegúrate de tener 🤗 Accelerate instalado si aún no lo tienes:

> Nota: Como Accelerate se está desarrollando rápidamente, debes instalar la versión git de Accelerate para ejecutar los scripts
```bash
pip install git+https://github.com/huggingface/accelerate
```

En lugar del script `run_summarization.py`, debes usar el script `run_summarization_no_trainer.py`. Los scripts compatibles con 🤗 Accelerate tendrán un archivo `task_no_trainer.py` en la carpeta. Comienza ejecutando el siguiente comando para crear y guardar un archivo de configuración:

```bash
accelerate config
```

Prueba tu configuración para asegurarte que está configurada correctamente:

```bash
accelerate test
```

Todo listo para iniciar el entrenamiento:

```bash
accelerate launch run_summarization_no_trainer.py \
    --model_name_or_path google-t5/t5-small \
    --dataset_name cnn_dailymail \
    --dataset_config "3.0.0" \
    --source_prefix "summarize: " \
    --output_dir ~/tmp/tst-summarization
```

## Usar un conjunto de datos personalizado

El script de la tarea resumir admite conjuntos de datos personalizados siempre que sean un archivo CSV o JSON Line. Cuando uses tu propio conjunto de datos, necesitas especificar varios argumentos adicionales:

- `train_file` y `validation_file` especifican la ruta a tus archivos de entrenamiento y validación.
- `text_column` es el texto de entrada para resumir.
- `summary_column` es el texto de destino para la salida.

Un script para resumir que utiliza un conjunto de datos personalizado se vera así:

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

## Prueba un script

A veces, es una buena idea ejecutar tu secuencia de comandos en una cantidad menor de ejemplos para asegurarte de que todo funciona como se espera antes de comprometerte con un conjunto de datos completo, lo que puede demorar horas en completarse. Utiliza los siguientes argumentos para truncar el conjunto de datos a un número máximo de muestras:

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

No todos los scripts de ejemplo admiten el argumento `max_predict_samples`. Puede que desconozcas si la secuencia de comandos admite este argumento, agrega `-h` para verificar:

```bash
examples/pytorch/summarization/run_summarization.py -h
```

## Reanudar el entrenamiento desde el punto de control

Otra opción útil para habilitar es reanudar el entrenamiento desde un punto de control anterior. Esto asegurará que puedas continuar donde lo dejaste sin comenzar de nuevo si tu entrenamiento se interrumpe. Hay dos métodos para reanudar el entrenamiento desde un punto de control.

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

## Comparte tu modelo

Todos los scripts pueden cargar tu modelo final en el [Model Hub](https://huggingface.co/models). Asegúrate de haber iniciado sesión en Hugging Face antes de comenzar:

```bash
hf auth login
```

Luego agrega el argumento `push_to_hub` al script. Este argumento creará un repositorio con tu nombre de usuario Hugging Face y el nombre de la carpeta especificado en `output_dir`.

Para darle a tu repositorio un nombre específico, usa el argumento `push_to_hub_model_id` para añadirlo. El repositorio se incluirá automáticamente en tu namespace.

El siguiente ejemplo muestra cómo cargar un modelo con un nombre de repositorio específico:

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
