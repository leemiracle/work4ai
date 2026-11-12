# examples: Amazon SageMaker

SageMaker inference examples for the `terraform-aws-nim` module.

| Example                                      | Description                                                                                           |
| -------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| [nim/](nim/)                                 | NGC NIM endpoint — supply `source_image_uri` from `nvcr.io/nim/...`                                   |
| [open-weight/](open-weight/)                 | Open-weight endpoint via vLLM — supply `model_id` from HuggingFace or NGC                            |
| [additional-scripts/](additional-scripts/)   | NIM + open-weight with `additional_scripts` — run local or S3 scripts before container startup        |
