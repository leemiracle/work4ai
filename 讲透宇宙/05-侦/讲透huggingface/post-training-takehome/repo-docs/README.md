# Hugging Face's Post-Training Internship Take-Home

This repo contains Hugging Face's take-home challenge for internships in the post-training team. The take-home was designed shortly after the release of OpenAI's o1 in late 2024, but recent models like gpt-5.4, Opus 4.7, and Kimi K2.6 can solve it fairly well when given access to web search and sandboxed GPUs. More recently, we ran our own [ML Intern](https://huggingface.co/spaces/smolagents/ml-intern) on the challenge and it produced pretty convincing [report](https://huggingface.co/blog/cmpatino/ml-intern-takehome)! It's not quite enough to be hired outright, but perhaps your own agents can do better?

## The challenge

Welcome to the Hugging Face internship exercise! In our recent blog post on [_Scaling Test-Time Compute with Open Models_](https://huggingface.co/spaces/HuggingFaceH4/blogpost-scaling-test-time-compute), we explored how search methods and reward models can be used to enhance the performance of LLMs on math problems.

In this exercise, you will be replicating a baseline method from this approach: **Best-of-N sampling with _weighted_ selection**. This approach involves sampling $N$ independent solutions per problem, scoring the solutions with a reward model, and then grouping solutions with the same final answer. The rewards are then summed per group and the final answer with the highest weighted score is chosen as the Best-of-N solution. For more details, refer to the [DeepMind](https://huggingface.co/papers/2408.03314) and [Math-Shepherd](https://huggingface.co/papers/2312.08935) papers.

We will use the following models from the Hugging Face Hub:
- [**Qwen/Qwen2.5-1.5B-Instruct**](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct): A 1.5 billion parameter chat model with decent math capabilities for its size.
- [**Skywork/Skywork-o1-Open-PRM-Qwen-2.5-1.5B**](https://huggingface.co/Skywork/Skywork-o1-Open-PRM-Qwen-2.5-1.5B): a 1.5 billion parameter process reward model (PRM). Unlike conventional reward models, PRMs are trained to provide a _sequence_ of scores, one for each step in the LLM's reasoning process.

💡 These models are small enough to run on a T4 GPU, so make sure you use a small GPU for running the tasks.

Concretely, we would like you to work through the following steps:
1. Create a filtered subset of 20 level 1-3 problems from the [MATH-500 dataset](https://huggingface.co/datasets/HuggingFaceH4/MATH-500) (smol models cannot really solve the harder levels). Using these problems:
  - Generate $N=1$ solutions for each problem using greedy decoding; this will be used as a baseline. We recommend prompting the model with chain-of-thought and instructing it to ensure the final answers are contained in `\boxed{answer}` (this helps with parsing).
  - Compute the accuracy of your solutions compared to the ground truth.
2. Sample $N=16$ solutions per problem and score them using the Skywork reward model. Although this model is a PRM, we will use the **_last step prediction_** as our final reward for the full solution. Refer to Appendix E of the [DeepMind](https://huggingface.co/papers/2408.03314) paper for guidance on using the last step prediction; this involves selecting the final score in the PRM's output sequence.
3. Using the solutions and rewards from Step 2, compute the Best-of-N accuracy with _**weighted**_ selection.
4. Create a dataset of the problems with the greedy and Best-of-N model solutions and push it to the Hugging Face Hub. Then, create a basic [dataset card](https://huggingface.co/docs/hub/datasets-cards) that describes how the dataset was constructed.
5. Create some plots and analysis of the performance of this approach compared to the greedy baseline. For example, which problems was Best-of-N able to solve that greedy decoding couldn't? If time permits, explore how other parameters impact the performance. For example, how accuracy varies with $N$ or temperature.

**Try to spend ~3 hours on the exercise.**

## Tips

* Some steps in the exercise can take ~15 minutes to run on a small GPU. We recommend familiarising yourself with the remaining steps while waiting for the code to run.
* You can use this [simple helper function](https://gist.github.com/lewtun/9c2ce1937b741404090a3dc4c7c022b3) to extract the answers from the `\boxed{answer}` substrings. In practice, we would use SymPy equivalence but that adds extra complexity.
* The Skywork reward model uses custom modelling code and must be loaded with `trust_remote_code=True`. The authors provide a [repo](https://github.com/SkyworkAI/skywork-o1-prm-inference) with some inference code, but it is possible to use the model directly in `transformers` with `AutoModel.from_pretrained(...)`. You may want to refer to the repo for the PRM scoring helper functions. You will also need to normalize the output logits with a sigmoid function!
* You are welcome to use LLMs (GPT-4o, Claude 3.5, DeepSeek V3, etc) to help you solve this exercise! The only thing we ask is that you indicate which parts of the code were co-authored by an LLM, and that you could explain how the code works if asked :)

## Assessment rubric

What we want to see is whether:

- You have hands-on knowledge of Python and a basic familiarity with the Hugging Face ecosystem.
- You have a good understanding of prompting LLMs and how to generate responses from them.
- You know how to use reward models to improve the quality of language model responses.
- Your code and written explanations can be understood by others. In particular, we like to see simple, readable code over complex over-engineered solutions.


We're especially interested in understanding how you approach projects, so it is important that you can explain the steps you take throughout the process. We want to understand what you have tried, so you will be evaluated on your comments just as much as the code itself.

If you feel that you are spending much longer on this exercise than the allotted time, please stop and simply jot down ideas for next steps if you had more time.

Good luck 🤗!
