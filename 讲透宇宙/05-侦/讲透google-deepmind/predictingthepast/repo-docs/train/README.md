# Aeneas training code

We recommend creating and activating a `conda` environment to ensure a clean
environment where the correct package versions are installed below.

```sh
# Optional but recommended:
conda create -n predictingthepast python==3.11
conda activate predictingthepast
```

Clone this repository and enter its root directory. Install the full
`predictingthepast` dependencies (including training), via:

```sh
git clone https://github.com/google-deepmind/predictingthepast
cd predictingthepast
pip install --editable .[train]
cd train/
```

The `--editable` option links the `predictingthepast` installation to this
repository, so that `import predictingthepast` will reflect any local
modifications to the source code.

Then, ensure you have TensorFlow installed. If you do not, install either the
CPU or GPU version following the
[instructions on TensorFlow's website](https://www.tensorflow.org/install/pip).
While we use [Jax](https://github.com/google/jax) for training, TensorFlow is
still needed for dataset loading.

Next, ensure you have placed the dataset in `data/led.json`, note the wordlist
and region mappings are also in that directory and may need to be replaced if
they change in an updated version of the dataset.

```sh
curl --output data/led.json https://storage.googleapis.com/ithaca-resources/models/led.json
```

or the ancient Greek model via
```sh
curl --output data/iphi.json https://storage.googleapis.com/ithaca-resources/models/iphi.json
```

Finally, to run training, run:

```sh
./launch_local.sh
```

Alternatively, you can manually run:

```sh
python experiment.py --config=config_latin.py --jaxline_mode=train --logtostderr
```
