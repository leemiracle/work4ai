# vocap

This page contains the pseudo-captions and human created captions for the
objects in the SAV dataset as used in our
[VoCap paper](https://arxiv.org/abs/2508.21809). More specifically:

* For the SAV validation set we had human annotators provide captions for each
of the annotated objects. Each object was captioned by three different
annotators.
* For the SAV training set, we highlighted the object of interest given the
ground truth, then we fed this to Gemini 1.5 Pro to create object-centric
captions.

More details can be found in [our paper](https://arxiv.org/abs/2508.21809).

## Format

We release two CSV files with headers:

* [sav_caption_val_human.csv](sav_caption_val_human.csv)
* [sav_caption_train_automatic.csv](sav_caption_train_automatic.csv) (14MB)

Each row contains `video_id`, `object_id`, `caption` (comma separated).
For the validation set, most `video_id`, `object_id` pairs are repeated three
times since every object was captioned by three different human annotators.

## Citing this work

```
@inproceedings{uijings25vocap,
      title={{VoCap}: Video Object Captioning and Segmentation from Any Prompt},
      author={Jasper Uijlings and Xingyi Zhou and Xiuye Gu and Arsha Nagrani
         and Anurag Arnab and Alireza Fathi and David Ross and Cordelia Schmid},
      booktitle={ArXiv},
      year={2025},
}
```

## License and disclaimer

Copyright 2025 Google LLC

All software is licensed under the Apache License, Version 2.0 (Apache 2.0);
you may not use this file except in compliance with the Apache 2.0 license.
You may obtain a copy of the Apache 2.0 license at:
https://www.apache.org/licenses/LICENSE-2.0

All other materials are licensed under the Creative Commons Attribution 4.0
International License (CC-BY). You may obtain a copy of the CC-BY license at:
https://creativecommons.org/licenses/by/4.0/legalcode

Unless required by applicable law or agreed to in writing, all software and
materials distributed here under the Apache 2.0 or CC-BY licenses are
distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the licenses for the specific language governing
permissions and limitations under those licenses.

This is not an official Google product.
