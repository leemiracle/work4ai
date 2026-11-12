# OlmoEarth Tutorial — ICLR ML4RS Workshop

Getting started with [OlmoEarth](https://github.com/allenai/olmoearth_pretrain): from embeddings to fine-tuning for land use / land cover classification, using an African Wildlife Foundation (AWF) dataset in southern Kenya near Amboseli National Park.

## Contents

- `OlmoEarthTutorial.ipynb` — follow-along notebook with code cells to run (recommended).
- `OlmoEarthTutorialCompleted.ipynb` — fully executed notebook with outputs, for reference.
- `OlmoEarthTutorial.pdf` — static PDF of the executed notebook.

## Running the tutorial

The tutorial is designed for **Google Colab with a GPU runtime** (T4 is sufficient). It also runs locally on a machine with a CUDA GPU or Apple Silicon (MPS).

### Option 1: Google Colab (recommended)

1. Open [colab.research.google.com](https://colab.research.google.com).
2. **File → Upload notebook** and select `OlmoEarthTutorial.ipynb` from this repo.
3. **Runtime → Change runtime type → GPU**.
4. Run the cells top to bottom. The first cell installs dependencies; the dataset (~1.8 GB) is downloaded from HuggingFace inside the notebook.

### Option 2: Local (Jupyter)

```bash
git clone https://github.com/allenai/olmoearth_ml4rs_tutorial.git
cd olmoearth_ml4rs_tutorial

python -m venv .venv && source .venv/bin/activate
pip install olmoearth_pretrain olmoearth_pretrain_minimal rslearn wandb \
            scikit-learn matplotlib einops huggingface_hub \
            'jsonargparse[signatures]>=4.27.7' jupyter rasterio scipy

jupyter notebook OlmoEarthTutorial.ipynb
```

## Time & resources

| Approach                   | Time        | GPU memory |
|----------------------------|-------------|------------|
| Embeddings + kNN / linear probe | minutes     | ~2–3 GB    |
| Fine-tune (4 epochs)       | ~15–20 min  | ~4–6 GB    |
| Fine-tune (30 epochs)      | ~2–3 hours  | ~4–6 GB    |

Default settings complete in roughly 30–45 minutes end-to-end.
