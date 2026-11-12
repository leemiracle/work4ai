# شارك نموذجك مع العالم

أظهرت آخر درسين تعليميين كيفية ضبط نموذج بدقة باستخدام PyTorch و Keras و 🤗 Accelerate لعمليات التهيئة الموزعة. والخطوة التالية هي مشاركة نموذجك مع المجتمع! في Hugging Face، نؤمن بالمشاركة المفتوحة للمعرفة والموارد لتمكين الجميع من الاستفادة من الذكاء الاصطناعي. ونشجعك على مشاركة نموذجك مع المجتمع لمساعدة الآخرين على توفير الوقت والموارد.

في هذا الدرس، ستتعلم طريقتين لمشاركة نموذجك المدرب أو مضبوط على منصة [Model Hub](https://huggingface.co/models):

- رفع ملفاتك إلى منصة Hub مباشرة باستخدام الكود البرمجي.

- قم بسحب وإفلات ملفاتك إلى Hub باستخدام الواجهة web.

<iframe width="560" height="315" src="https://www.youtube.com/embed/XvSGPZFEjDY" title="مشغل فيديو YouTube"
frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope;
picture-in-picture" allowfullscreen></iframe>

<Tip>

لمشاركة نموذج مع المجتمع، تحتاج إلى حساب على [huggingface.co](https://huggingface.co/join). يمكنك أيضًا الانضمام إلى منظمة موجودة أو إنشاء منظمة جديدة.

</Tip>

## ميزات المستودع

يعمل كل مستودع على Model Hub مثل مستودع GitHub النتقليدي. تقدم مستودعاتنا التحكم في الإصدارات وسجل التغييرات، وقدرة على رؤية الاختلافات بين الإصدارات.

تعتمد آلية التحكم في الإصدارات على منصة Model Hub على نظامي git و [git-lfs](https://git-lfs.github.com). وبعبارة أخرى، يمكنك التعامل مع  كل نموذج كأنه مستودع مستقل، مما يمكّن من زيادة التحكم في الوصول والقابلية للتطوير. يسمح التحكم في الإصدار بإجراء تعديلات وتثبيت إصدار محدد من النموذج باستخدام رمز التغيير (commit hash) أو وسم (tag) أو فرع (branch).

بفضل هذه الميزة، يمكنك تحميل إصدار محدد من النموذج باستخدام معلمة الإصدار "revision":

```py
>>> model = AutoModel.from_pretrained(
...     "julien-c/EsperBERTo-small", revision="4c77982"  # اسم العلامة، أو اسم الفرع، أو تجزئة الالتزام
... )
```

من السهل أيضًا تعديل الملفات  الموجودة داخل مستودع، ويمكنك عرض سجل التغييرات التي طرأت على هذه الملفات ومعاينة الاختلافات بين الإصدارات المختلفة:

![vis_diff](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/vis_diff.png)

## الإعداد

قبل مشاركة نموذج على Hub، ستحتاج إلى بيانات اعتماد حساب Hugging Face الخاصة بك.  إذا كنت تستخدم منصة الأوامر، فقم بتشغيل الأمر التالي في بيئة افتراضية حيث تم تثبيت 🤗 Transformers. سيقوم هذا الأمر بتخزين رمز الدخول الخاص بك في مجلد تخزين المؤقت لـ Hugging Face (`~/.cache/` بشكل افتراضي):

```bash
hf auth login
```

إذا كنت تستخدم دفتر ملاحظات مثل Jupyter أو Colaboratory، فتأكد من تثبيت مكتبة [`huggingface_hub`](https://huggingface.co/docs/hub/adding-a-library). تسمح لك هذه المكتبة بالتفاعل برمجيًا مع Hub.

```bash
pip install huggingface_hub
```

ثم استخدم `notebook_login` لتسجيل الدخول إلى Hub، واتبع الرابط [هنا](https://huggingface.co/settings/token) لإنشاء رمز للتسجيل:

```py
>>> from huggingface_hub import notebook_login

>>> notebook_login()
```


## تحويل النموذج ليتوافق مع جميع الأطر العمل

لضمان إمكانية استخدام نموذجك من قبل شخص يعمل بإطار عمل مختلف، نوصي بتحويل نموذجك ورفعه مع نقاط التحقق من PyTorch و TensorFlow. في حين أن المستخدمين لا يزال بإمكانهم تحميل نموذجك من إطار عمل مختلف إذا تخطيت هذه الخطوة، إلا أنه سيكون أبطأ لأن 🤗 Transformers ستحتاج إلى تحويل نقطة التحقق أثناء التشغيل.

تحويل نقطة التحقق لإطار عمل آخر أمر سهل. تأكد من تثبيت PyTorch و TensorFlow (راجع [هنا](installation) لتعليمات التثبيت)، ثم ابحث عن النموذج الملائم لمهمتك في الإطار الآخر.

حدد `from_tf=True` لتحويل نقطة تحقق من TensorFlow إلى PyTorch:

```py
>>> pt_model = DistilBertForSequenceClassification.from_pretrained("path/to/awesome-name-you-picked", from_tf=True)
>>> pt_model.save_pretrained("path/to/awesome-name-you-picked")
```

## دفع نموذج أثناء التدريب

<Youtube id="Z1-XMy-GNLQ"/>

مشاركة نموذجك على Hub مر بسيط للغاية كل ما عليك هو إضافة معلمة أو استدعاء رد إضافي. كما تذكر من درس [التدريب الدقيق](training)، فإن فئة [`TrainingArguments`] هي المكان الذي تحدد فيه المعلمات الفائقة وخيارات التدريب الإضافية. تشمل إحدى خيارات التدريب هذه القدرة على دفع النموذج مباشرة إلى المنصة Hub. قم بتعيين `push_to_hub=True` في [`TrainingArguments`]:

```py
>>> training_args = TrainingArguments(output_dir="my-awesome-model", push_to_hub=True)
```

مرر معامﻻت التدريب كالمعتاد إلى [`Trainer`]:

```py
>>> trainer = Trainer(
...     model=model,
...     args=training_args,
...     train_dataset=small_train_dataset,
...     eval_dataset=small_eval_dataset,
...     compute_metrics=compute_metrics,
... )
```

بعد ضبط نموذجك بدقة، يمكنك استخدام دالة [`~transformers.Trainer.push_to_hub`] المتاحة في [`Trainer`] لدفع النموذج المدرب إلى المنصة Hub. سوف تضيف 🤗 Transformers تلقائيًا المعلمات الفائقة المستخدمة في التدريب ونتائج التدريب وإصدارات الإطار إلى بطاقة معلومات النموذج الخاصة بك!

```py
>>> trainer.push_to_hub()
```

## استخدام دالة `push_to_hub`

يمكنك أيضًا استدعاء `push_to_hub` مباشرة على نموذجك لتحميله إلى Hub.

حدد اسم نموذجك في `push_to_hub`:

```py
>>> pt_model.push_to_hub("my-awesome-model")
```

ينشئ هذا مستودعًا تحت اسم المستخدم الخاص بك باسم نموذج `my-awesome-model`. يمكن للمستخدمين الآن تحميل نموذجك باستخدام دالة `from_pretrained`:

```py
>>> from transformers import AutoModel

>>> model = AutoModel.from_pretrained("your_username/my-awesome-model")
```
```py
>>> from transformers import AutoModel

>>> model = AutoModel.from_pretrained("your_username/my-awesome-model")
```

إذا كنت تنتمي إلى منظمة وتريد دفع نموذجك تحت اسم المنظمة بدلاً من ذلك، فما عليك سوى إضافته إلى `repo_id`:

```py
>>> pt_model.push_to_hub("my-awesome-org/my-awesome-model")
```

يمكن أيضًا استخدام دالة `push_to_hub` لإضافة ملفات أخرى إلى مستودع النماذج. على سبيل المثال، أضف رموزًا إلى مستودع نموذج:

```py
>>> tokenizer.push_to_hub("my-awesome-model")
```

أو ربما تريد إضافة إصدار TensorFlow من نموذج PyTorch المضبوط:

```py
>>> tf_model.push_to_hub("my-awesome-model")
```

الآن عند الانتقال إلى ملفك الشخصي على Hugging Face، يجب أن ترى مستودع النماذج الذي أنشأته حديثًا. سيؤدي النقر فوق علامة التبويب **Files** إلى عرض جميع الملفات التي قمت بتحميلها في المستودع.

للحصول على مزيد من التفاصيل حول كيفية إنشاء الملفات وتحميلها إلى مستودع، راجع وثائق Hub [هنا](https://huggingface.co/docs/hub/how-to-upstream).

## التحميل باستخدام الواجهة web

يمكن للمستخدمين الذين يفضلون نهج عدم الترميز تحميل نموذج من خلال واجهة Hub web. قم بزيارة [huggingface.co/new](https://huggingface.co/new) لإنشاء مستودع جديد:

![new_model_repo](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/new_model_repo.png)

من هنا، أضف بعض المعلومات حول نموذجك:

- حدد **مالك** المستودع. يمكن أن يكون هذا أنت أو أي من المنظمات التي تنتمي إليها.
- اختر اسمًا لنموذجك، والذي سيكون أيضًا اسم المستودع.
- اختر ما إذا كان نموذجك عامًا أم خاصًا.
- حدد ترخيص الاستخدام لنموذجك.

الآن انقر فوق علامة التبويب **Files** ثم انقر فوق الزر **Add file** لإضافة ملف جديد إلى مستودعك. ثم اسحب وأسقط ملفًا لتحميله وأضف رسالة الالتزام.

![upload_file](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/upload_file.png)

## إضافة بطاقة نموذج

للتأكد من فهم المستخدمين لقدرات نموذجك وقيوده وتحيزاته المحتملة واعتباراته الأخلاقية، يرجى إضافة بطاقة نموذج إلى مستودعك. يتم تعريف بطاقة النموذج في ملف `README.md`. يمكنك إضافة بطاقة نموذج عن طريق:

* قم بإنشاء ملف `README.md` وتحميله يدويًا.
* انقر فوق الزر **Edit model card** في مستودع نموذجك.

الق نظرة على بطاقة [DistilBert](https://huggingface.co/distilbert/distilbert-base-uncased) للحصول على مثال جيد على نوع المعلومات التي يجب أن تتضمنها بطاقة النموذج. للحصول على مزيد من التفاصيل حول الخيارات الأخرى التي يمكنك التحكم فيها في ملف `README.md` مثل البصمة الكربونية للنموذج أو أمثلة الأداة، راجع الوثائق [هنا](https://huggingface.co/docs/hub/models-cards).
