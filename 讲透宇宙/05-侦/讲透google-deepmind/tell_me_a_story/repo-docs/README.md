# Tell Me A Story

This repository includes the **Tell Me A Story** dataset used in our paper: [Agents' Room: Narrative Generation through Multi-step Collaboration](https://arxiv.org/abs/2410.02603).

## Abstract

Writing compelling fiction is a multifaceted process combining elements such as crafting a plot, developing interesting characters, and using evocative language. While large language models (LLMs) show promise for story writing, they currently rely heavily on intricate prompting, which limits their use. We propose **Agents' Room**, a generation framework inspired by narrative theory, that decomposes narrative writing into subtasks tackled by specialized agents. To illustrate our method, we introduce **Tell Me A Story**, a high-quality dataset of complex writing prompts and human-written stories, and a novel evaluation framework designed specifically for assessing long narratives. We show that **Agents' Room** generates stories that are preferred by expert evaluators over those produced by baseline systems by leveraging collaboration and specialization to decompose the complex story writing task into tractable components. We provide extensive analysis with automated and human-based metrics of the generated output.

## Dataset Description

The **Tell Me A Story** dataset is available in JSONL format at: [link](https://console.cloud.google.com/storage/browser/tell-me-a-story). The data can be downloaded via direct download using:

```bash
wget https://storage.googleapis.com/tell-me-a-story/tell-me-a-story-train_encrypted.jsonl
wget https://storage.googleapis.com/tell-me-a-story/tell-me-a-story-validation_encrypted.jsonl
wget https://storage.googleapis.com/tell-me-a-story/tell-me-a-story-test_encrypted.jsonl
```

The dataset files when downloaded will take up approximately 3MB.

### Dataset decryption
The files have been encrypted to prevent the dataset from being scraped by automated scraping tools.

This repository contains both the symmetric key `skey.key` and private key `private_key.pem` required to decrypt the files.
The symmetric key is encrypted and can be un-encrypted using the private key.

The files can be decrypted using the Python package `cryptography`.
If you do not have it, you can install it using the following command:

```
pip install cryptography
```

Then use the following script to decrypt the files:

```python
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.fernet import Fernet
import sys
import os

if len(sys.argv) > 3:
    filename = sys.argv[1]  # Name of the file to decrypt.
    skey_file = sys.argv[2]  # File containing the symmetrical key.
    pkey_file = sys.argv[3]  # File containing the private key.

    # Load the private key.
    with open(pkey_file, 'rb') as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None,
            backend=default_backend()
        )

    # Load the symmetrical key.
    with open(skey_file, 'rb') as f:
      skey = f.read()

    # Load the file to decrypt.
    with open(filename, 'rb') as f:
      data = f.read()

    # Decrypt the symmetrical key.
    unenc_skey = private_key.decrypt(
        skey,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Decrypt the data.
    f = Fernet(unenc_skey)
    decrypted = f.decrypt(data)

    # Write the data to file.
    out_file = filename.replace('_encrypted.jsonl', '.jsonl')
    with open(out_file, 'wb') as f:
        f.write(decrypted)
else:
    print('Usage: ' + os.path.basename(__file__) + ' filename.jsonl skey.key private_key.pem')
```

### Dataset columns
There are three data splits: `train`, `validation`, and `test`. The dataset contains the following columns:

- `example_id` (str):  A unique identifier for each input prompt.
- `inputs` (str): The input writing prompt.
- `targets` (str): The target fiction story corresponding to the writing prompt.


## Citing this work

If you use any of the material here, please cite the following paper:

```latex
@article{huot2024agents,
  title={Agents' Room: Narrative Generation through Multi-step Collaboration},
  author={Huot, Fantine and Amplayo, Reinald Kim and Palomaki, Jennimaria and Jakobovits, Alice Shoshana and Clark, Elizabeth and Lapata, Mirella},
  journal={arXiv preprint arXiv:2410.02603},
  year={2024}
}
```

## License and disclaimer

Copyright 2024 DeepMind Technologies Limited

This dataset is licensed under the Creative Commons Attribution 4.0
International License (CC-BY). You may obtain a copy of the CC-BY license at:
https://creativecommons.org/licenses/by/4.0/legalcode

Unless required by applicable law or agreed to in writing, all
materials distributed here under the CC-BY license are
distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the licenses for the specific language governing
permissions and limitations under those licenses.

This is not an official Google product.
