# Century

#### [Century: A Framework and Dataset for Evaluating Historical Contextualisation of Sensitive Images (Akbulut et al. 2025)](https://openreview.net/forum?id=1KLBvrYz3V)
To better understand how multi-modal models describe and provide context on
historical figures and events, we introduce Century – a novel dataset of
1,500 sensitive historical images.

This dataset consists of images from recent history, created through an
automated method combining knowledge graphs and language models with quality
and diversity criteria created from the practices of museums and digital
archives.

_Century_ contains images that depict events and figures that are diverse
across topics and represents all regions of the world.

Instructions on replicating can be found in the [ICLR paper](https://openreview.net/forum?id=1KLBvrYz3V).

## Data files
We release three datasets.

### century_dataset_images_only.csv
This file contains the canonical Century dataset, with links to all images in
_Century_ as Wikipedia links, alongside other metadata attributes. It has six
columns:

* `image_url` indicating the image’s location on Wikimedia Commons
* `wikipedia_url` indicating where the image appears on Wikipedia
* `wit_split ` indicating which split of the Wikipedia Text-Image Dataset the image was sourced from
* `century_method` indicating which method was used to source the search term corresponding to the image
* `is_starter_set` indicating if the image belongs to the “starter set” we recommend as a starting point for developers
* `century_id` which contains a unique ID for each image

### century_dataset_with_image_quality_labels.csv
This file contains the canonical Century dataset, with all image annotations
collected through human and auto-rater methods. It contains all of the columns
listed above, as well as:

* `rating.method` indicating which evaluation method (human or automated) was used to assign quality and diversity ratings to the image
* `rating.src` indicating the specific labeller model used to assign quality and diversity ratings
* `rating.rater_id` indicating anonymous IDs for all human crowd-workers
* `rating.content` indicating the categorical rating given to describe image content type
* `rating.concept` indicating the categorical rating given to describe the thematic category of the image
* `rating.subregion` indicating the categorical rating given to describe the primary subregion of the image contents
* `rating.time_period` indicating the binary rating given to determine whether the image corresponds to the 20th and 21st centuries (1) or not (0)
* `rating.sensitive` indicating the ordinal rating given to the image’s sensitivity from low (1) to high (5)
* `rating.commemorative` indicating the ordinal rating given to the image’s commemorativeness from low (1) to high (5)
* `rating.controversial` indicating the ordinal rating given to the image’s controversiality from low (1) to high (5)

### knowledge_graph_search_terms.csv
This file contains all search terms of historical events and figures collected
through the knowledge graph mining method described in the paper. It contains a
single column (`terms`) of lower-cased strings.

## Citing this work

To cite this work, use:

 <!-- mdlint off(SNIPPET_INVALID_LANGUAGE) -->
```latex
@inproceedings{Akbulut25,
      title={Century: A Framework and Dataset for Evaluating Historical Contextualisation of Sensitive Images},
      author={Canfer Akbulut and Kevin Robinson and Maribeth Rauh and Isabela Albuquerque and Olivia Wiles and Laura Weidinger and Verena Rieser and Yana Hasson and Nahema Marchal and Iason Gabriel and William Isaac and Lisa Anne Hendricks},
      booktitle={The Thirteenth International Conference on Learning Representations},
      year={2025},
}
```

## License and disclaimer

Copyright 2024 DeepMind Technologies Limited

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
