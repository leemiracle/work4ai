# Third-Party Notices

This project will download and install additional third-party open source software projects. Review the license terms of these open source projects before use.

## Dependencies

GMM-TS requires a local clone of [MM-TSFlib](https://github.com/AdityaLab/MM-TSFlib) at commit `e789ce78c9bafd8e3ba0d8850f9ad2becbe83548` (set via `MM_TSFLIB_PATH`). MM-TSFlib provides expert forecasting models, neural network layers, and datasets used at runtime.

Installing this project (for example, via `pip install -r requirements.txt` or `pip install -e .`) may fetch and install third-party packages listed in `requirements.txt` and `setup.py`, including but not limited to:

- PyTorch
- Hugging Face Transformers and related libraries
- Scientific Python stack (NumPy, pandas, scikit-learn, SciPy, and others)

Pre-trained model weights may be downloaded at runtime when using LLM-based experts (for example, BERT, GPT-2). Those artifacts are subject to the license terms published by their respective providers.

DTW utilities in `gmm_ts/utils/dtw.py` are adapted from the [Time-Series-Library](https://github.com/thuml/Time-Series-Library) project.

Review each dependency's license before use.
