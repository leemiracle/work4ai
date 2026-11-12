# Examples

| Example | Description |
|---------|-------------|
| [sagemaker/nim/](sagemaker/nim/) | NGC NIM realtime endpoint on SageMaker — NGC container, automatic GPU profile selection |
| [sagemaker/open-weight/](sagemaker/open-weight/) | Open-weight LLM on SageMaker via vLLM — HuggingFace or NGC weights |
| [sagemaker/additional-scripts/](sagemaker/additional-scripts/) | SageMaker NIM + open-weight with `additional_scripts` — run local or S3 shell scripts before container startup |
| [eks/nim/](eks/nim/) | NGC NIM on EKS Auto Mode — Helm deploy, S3 model profile cache |
| [eks/open-weight/](eks/open-weight/) | Open-weight LLM on EKS via vLLM — S3 weight sync, kubectl deploy |
| [eks/additional-scripts/](eks/additional-scripts/) | EKS NIM + open-weight with `additional_scripts` — run local or S3 shell scripts as init containers before the pod starts |
| [all-inference/](all-inference/) | All four paths in one apply: SageMaker + EKS, NIM + open-weight |
