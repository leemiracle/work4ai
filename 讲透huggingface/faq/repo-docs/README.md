# The Open Source 🤗 FAQ

When chatting with [Tech to the Rescue](https://techtotherescue.org/), we realized that a lot of non "core ML" organisations do not really understand what 🤗 is and how they could/should use open source machine learning solutions! 

So we made this FAQ together, and we hope people will contribute their questions and their answers to it in order to make it an ever evolving doc! 

(If you want to access the table of contents, click on the ⋮≡ symbol on the top right!)

## Hugging Face 🤗

### How to explain Hugging Face to non-technical colleagues in my organization
Hugging Face is where people come to share, learn about and discuss machine learning on the web. It is a combination of:
- The largest online machine learning library, where everyone working on machine learning shares the building blocks of AI that they create, machine learning objects called “artefacts”
- A center for learning and exploration spot, with free classes, tutorials, links to research papers and user gathered collections of ML artefacts
- A community agora, where people can post updates about their work, share their findings through blogs, and engage in discussions with authors of research and artefacts
- A building workshop, with open source libraries to understand and use machine learning to create new artefacts

### What kind of open source solutions can I find via Hugging Face? Are there only open source models or also other tools?
In terms of solutions, Hugging Face hosts all types of machine learning objects (artefacts): 
1) models, trained for specific use cases (such as generating or analysing text and image, video, audio, tabular data, robotics, etc); 
2) data to train or test these models on; 
3) demos and apps (called spaces) to explore and showcase models, data and use cases. 

All these artefacts are released under a range of licenses (document determining terms of use, open source, open science, semi open, closed), depending on what their authors would like to do. We host close to 2M models and 500K datasets!

Hugging Face also provides a range of open source and other kinds of open software to allow people to create their own machine learning applications and artefacts.

### I’m new to AI and open source. Where should I start on Hugging Face?
The first step is to [create an account](https://huggingface.co/join). Then, you can explore [Spaces](https://huggingface.co/spaces), our AI apps directory: there, you’ll find free and easy to use demos and tools, contributed both by the industry and the community. This should give you ideas of cool use cases! 

If you want to interact with models directly with code, you can check our [get started page on inference](https://huggingface.co/inference/get-started), which provides snippets to start any model in a couple of lines of code.

### What makes Hugging Face different from other open source platforms or solutions? What are crucial elements to consider in our choice?
Hugging Face has been built based on key values for positive social impact, such as openness, accountability, transparency, approachability, and kindness. These values underpin everything we do and provide for the community, helping people to create good machine learning in a bunch of different ways.

Because of these values, Hugging Face resources and community offerings are unique within the tech world in providing a lot of clarity: Where different artefacts came from, what they do, what they can be used for, who created them, what community members and Hugging Face employees think of them, how well they work. This transparency is designed to be highly approachable–understandable to diverse audiences (no matter what their background is), and easy to find.

It has the most open-source AI models and datasets 

It has low-code and no-code solutions, like Spaces, that allow non-technical users to engage with ML technologies

### What level of coding or machine learning expertise is required to use Hugging Face tools?
Very little, actually! You can totally start in machine learning by exploring the vast collection of  AI apps and demos (called “Spaces”), which do not require users to code. If you want to dive deeper into machine learning, you can follow any of our free classes to learn more! There are also many tutorials, which are very light in code or provide the code directly for you, to allow you to get started using models and datasets in a couple minutes.

## Choosing the right solution

### How can I navigate through the Hugging Face platform?
Depending on whether you’re looking for a model, a dataset, or a demo, you can explore the related parts of the site using the top bar. If you’re not sure what you’re looking for, you can look for specific keywords in the top search bar, which works across all the different artefacts on the platform.  

### How can I find the solution that best fits my use case? What are important factors to consider when choosing a solution on the platform?
One of the most important things to keep in mind when selecting models and datasets is whether they are useful for your specific use cases. What audiences do you want to reach? In what contexts will the technology be used? 
Based on consideration of the who, what, how, etc. of your use cases, you can use the search bar to find the best-suited solutions.

Once you know what you are looking for (a satellite image dataset, a small text generation model, all solutions related to tabular data, etc), you have several ways to select from existing options.

You can sort artefacts by actual usage, which translates to downloads or “likes” on the platform: this allows you to see which items are the most popular. Some users have also made use case specific rankings to find the best artefact for things like agentic models, or biochemistry generation, or safe text generation, etc. - you can explore these. 

You can make selections based on the technical constraints of the systems you’re working within, for example:
- For datasets, their storage size will inform you on the hardware capacity you’ll need to work with them effectively
- For models, you can choose whether to work with them locally or through a Hugging Face [Inference Provider](https://huggingface.co/docs/hub/en/models-inference). If you want to work with them locally, then you must have the hardware (e.g., GPUs) that can run them. Otherwise, you can automatically select an Inference Provider that provides the appropriate computing power. 

You can also make selections based on legal and ethical considerations.

In general, an artefact’s license constrains how you can use it: can you use it commercially? For research purposes? Something else?
Ethical considerations reflect your organization’s values and priorities. Do you want to train on data that is ethically sourced, or constructed by a non-profit? Do you want to train on data that is scraped from the web without deep consideration of the content, or content that is more carefully curated? Do you want to train on data that is well documented?

As well as academic and use-case considerations, for example:
Do you want fiction and fact mixed all together, or would you prefer scientific resources? Are there specific topics you would like to make sure the dataset provides?

### Where and how should we host open-source AI models or services on a tight nonprofit budget?
There are different costs depending on what you would like to do. Hugging Face offers a generous free tier for many features, including model hosting and inference, especially for smaller projects. It is possible to openly provide model weights for free (and we recommend documenting the model well and providing as much detail as you can in the README.md to help others find it and know if it suits their use cases – also free!). 

If you would like to provide a demo of your model, then you can use our free [ZeroGPU option](https://huggingface.co/docs/hub/en/spaces-zerogpu), or more advanced computing options depending on your budget.

If you would like private storage or dataset analysis, robust security mechanisms, control over user access, etc., then a [Pro subscription](https://huggingface.co/pro) or [a Team/Enterprise subscription](https://huggingface.co/enterprise) is more appropriate.

If applicable, we also offer an [Academic subscription](https://huggingface.co/docs/hub/en/academia-hub) that provides many of our most powerful tools at a lower cost.

### How can we integrate specific context to open source models to fine-tune them to our specific needs?

There are multiple ways to do this! A hands-on solution is to use our [training libraries](https://huggingface.co/docs/transformers/en/training). We have also recently introduced [Jobs](https://huggingface.co/docs/huggingface_hub/en/guides/jobs), which is slightly lower-code for paid customers, which can be used to run fine-tuning jobs directly.

### What are some cost-saving tips for deploying AI with limited resources?
Use task-specific models: ones that have been fine-tuned for the task you want to do, not the general-purpose base models.

Examine [evaluation performance of models](https://huggingface.co/spaces/OpenEvals/find-a-leaderboard) (evaluation scores are also often provided in the model card), and find the smallest model(s) that work well on the evaluation benchmarks most relevant to your use cases.

Test energy consumption and accuracy in parallel, and pick the model that is an optimal combination of both - sometimes the second-best model will use 30 times less energy!

## Publishing open source solutions on Hugging Face

### Is open source the same as publicly available and if not, in what way is it different? 
Open source and publicly available are not the same thing. When something, that can be materials like software or data, is "publicly available", this simply means that anyone can access these materials. However, this does not grant the person accessing these materials any legal rights to use, modify, or redistribute them; the materials remain "closed", meaning the copyright owner(s) reserve all rights.

Open source, by contrast, is a specific way of using copyright to grant broader rights to anyone accessing these materials, notably to use, modify, and redistribute them. These choices and rights granted are expressed through licenses (like MIT or Apache) that need to be respected by the people accessing these materials.

At Hugging Face, we characterize machine learning solutions on a gradient of openness, from fully closed – where you can only interact with the output of a system – to fully open, where you can see everything about the datasets used, the model weights, how the system was trained, etc. It is up to each company how “open” or “closed” to be. The term “open source” refers to one specific flavor of openness, but there are many ways to be somewhat open and somewhat closed.

One mechanism we make available to help solutions be “open” while still controlling for who uses them and how is via **gating**, where users and members of an organization can approve or disapprove access depending on the conditions they set. This is possible to do for [Datasets](https://huggingface.co/docs/hub/en/datasets-gated), [Models](https://huggingface.co/docs/hub/en/models-gated), and [for all the content shared in a collection](https://huggingface.co/docs/hub/en/enterprise-hub-gating-group-collections).

### What are the differences between open source and commercially available solutions?
Open source solutions are typically free to use, and come with openly available source code, allowing anyone to use, modify, and redistribute, as indicated above. This model encourages community-driven development and offers greater transparency and flexibility. 

Commercially available solutions can be proprietary ("closed"), and usually include professional support, regular updates, and service agreements, but users typically cannot view or alter the source code, and solutions are typically paid.

Commercially available systems can be open source! Many open source projects are commercially available, and many open source licenses explicitly allow for commercial use. They tend to foster community-driven development, which can lead to greater transparency and flexibility and can offer different strategies for support, maintenance, and security, paid or for free.

Generally, open releases are a gradient! We invite you to check out Irene Solaiman’s [great work](https://arxiv.org/abs/2302.04844) on the topic.

### What are the most important questions to answer for ourselves when it comes to considering whether or not to build and publish an open source solution?

Making your solution open source benefits both you and the community: the community gets a new solution for free, and you get more users who can actively contribute, by reporting bugs, suggesting and adding their own features through pull requests, and overall building on it. However, it can also increase the burden of maintenance (as you get more feedback to manage).

### Would it be better to open source a more “ready-to-use” interface than raw dumps of the data/code?

This depends entirely on you and what you want to share! Raw models and data dumps allow all users to inspect them and reuse them for their own purposes and projects, while sharing demos (Spaces) allows more beginner users to discover new use cases and to play with your artefacts more easily.  

### How do we ensure the project remains active and sustainable if (for instance) our organization steps back?
If you decide to step back from an open source project that’s worth maintaining, and it had some traction, you can simply ask the community if someone would be interested in taking the project over, directly on your project page and on social media. Once they are interested, you can either transfer the project to them, or to a shared organisation between you and them.

## Security and sustainability

### Can we verify the owner of an open source solution?
Open source solutions on Hugging Face are made available via repositories (pages that host Datasets, Models, and Apps/Spaces). Repositories are stored within a user’s account or an organization/team’s account – their landing page is in the url right before a resource, i.e. https://huggingface.co/{organization_name}/{repository_name}.  Just remove the {repository_name} from the url, and you will see details on the user or on all members of the organization, on the left-hand side. 

Within a repository, you can see the person who created it and all edits to it using the Files and Versions tab. This links through to https://huggingface.co/datasets/{organization_name}/{repository_name}/commits/main – by default the “main” branch of the project – and you can select other branches of the project that people have worked on to examine as well. (If this “main” and “branch” thing sounds confusing, it is based on the `git` system [which you can learn more about here](https://git-scm.com). By default, when you access content in a repository, you are accessing content from the “main” branch.)

The license used for an open source solution can also show who the owner is.

### What processes guard against data-poisoning or malicious edits?

One of the backbones of the Hugging Face Hub is the git protocol, which provides version control: Git allows you to see a detailed list of exactly who made changes to what, and what those changes were. Hugging Face has integrated git (and [the related HfAPI protocol](https://huggingface.co/docs/huggingface_hub/en/concepts/git_vs_http)) throughout the platform, as a fundamental key for openness, transparency, and accountability.

This protocol helps ensure that malicious actors can not secretly make changes, and that you can check that you trust everyone who has made edits – and that the edits are appropriate: Changes can only be made by Hugging Face users when they submit a suggested change as a “pull request”, and then this request must be approved by a maintainer of the repository.

Further, because Hugging Face datasets are shared and edited using the git protocol, each version of the dataset is stored, and [specific revisions of the dataset](https://huggingface.co/docs/datasets/en/loading#hugging-face-hub) can be downloaded – this helps ensure that identical datasets are used between different parties.

Another common approach to confirm that a file is identical to an intended file is to verify the [checksum (hash signatures of the file)](https://security.stackexchange.com/questions/189000/how-to-verify-the-checksum-of-a-downloaded-file-pgp-sha-etc). 

### How to best manage and moderate contributions to an open-source knowledge or code base?
Contributions to an open-source base are made through issues (asking for questions/clarifications) and pull requests (providing new content). 
Best practices are usually to 
- have contribution guidelines in your readme, to make sure that you get contributions aligned with what you are looking for (for example: we welcome all contributions, or please open an issue first to discuss your idea, or we only currently welcome contributions on issues marked as “open-to-contribution”, etc.
- have coding standards (enforced through linters automatically)
- have a maintainer, someone who has the role of a benevolent dictator to make the ultimate decisions as to what should be done on the code base, for the sake of homogeneity and coherence. This person should interact with the community on discussions, check reactions on issues to identify important topics, while steering the boat and keeping the final say.

### Are open source tools and projects long term sustainable? Why (not) and what can we do ourselves to prevent issues?
Open source tools and projects are generally open to the world until they are deleted by a maintainer. If you want to ensure the code you are working from is always available, you can fork it (create a public copy that you own), from which you’ll be able to grab changes and updates while ensuring it fits your needs.

For security purposes, it is best to use actively maintained code. Code that has been forgotten or abandoned may include bugs that won’t be fixed and security issues that have not been patched.

### Is it safe to use models available on Hugging Face with sensitive data such as personal or health data?
Any model that you download to run locally on your machine can be run on personal data, as processing will then stay on your machine and not go through the web (as long as you follow the below safety suggestions and checks). Running models locally yourself is the best way to ensure data privacy in ML!

Our privacy policy is described at [hf.co/privacy](https://huggingface.co/privacy). Hugging Face offers tools for privacy, security, GDPR and SOC 2 Compliance for [Enterprise/Team customers](https://huggingface.co/enterprise).
For more about privacy and security when using Inference Endpoints, [see details here](https://huggingface.co/docs/inference-endpoints/en/security).

Through the Hugging Face platform, we implement several precautions to assist with safety and security:
- **Safetensors**: Look for the safetensors format used to store model weights on the Hub, which ensures no hidden code execution is possible; which was a risk with the older PyTorch pickle format. Thus no malicious code can be hidden in the weights file. You can read more in [the Safetensors blog](https://huggingface.co/blog/safetensors-security-audit).
- **Modeling code**: To run a model, the modeling code also needs to be downloaded along with the weight files. There are three mechanisms in place to improve safety:
1. Files being fully visible on the Hub, allowing for examination.
2. The trust_remote_code option in downloads to execute any code associated with a model or dataset, which is False by default.
A security scanner runs over files on the Hub and flags any malicious code files. If you want to be extra careful, you can pin the model version with the revision setting to make sure you download the version of the modeling code that has been reviewed.

If you have any questions on privacy or security, or requests, you can email privacy@huggingface.co.

### What are the risks and benefits of using open source data sets? How do I know whether it is complete and reliable?
What a “complete” or “reliable” dataset is is not clearly defined – arguably, a “complete” dataset would be everything in the world ever!
To determine whether a dataset is complete for your purposes, we recommend defining specifically what it should have, and then analyzing the dataset for adherence to your specifications. Data analysis mechanisms to assist include:
- **Datasets library**: the load_dataset function downloads and loads datasets from the Hugging Face Hub, allowing access to Dataset objects, which provide their contents, features, data types, and number of rows, and methods for inspecting, filtering, mapping, and processing data within a Python environment. Community members often use Spaces, Jupyter/Colab notebooks, or IDEs for deeper analysis.
- **Dataset Repositories**: For publicly shared datasets or privately shared with a paid subscription, the dataset page features a Dataset Viewer that supports filtering, searching, and provides basic statistics. Datasets on the Hub are also analyzable using DuckDB SQL, providing a quick way to explore and analyze datasets without downloading them.
- **Data processing tools**: We have created [datatrove](https://github.com/huggingface/datatrove) to assist in quickly analyzing large datasets. There are also many third-party resources for data analysis, such as Databricks.
A dataset might be “reliable” inasmuch as it creates a reliable model. Towards that end, it is critical to test the model you create in scenarios that are most similar to the scenarios in which it will be deployed.

## Ethics 
### How is the training data for models hosted on Hugging Face sourced? More specifically, how do we know whether it mostly comes from the Global North or whether it is suitable for Global South/local contexts?
Hugging Face is a platform for the community to use – we generally don’t source training data ourselves, and so community members who provide datasets are encouraged to document these types of questions about their datasets directly. Towards this goal, we provide [guidance on how to document datasets appropriately](https://huggingface.co/docs/datasets/en/dataset_card) and [tools for doing so](https://huggingface.co/docs/dataset-viewer/en/analyze_data).

Users can also query datasets they are interested in using the Dataset Viewer API, which provides tools such as [DuckDB](https://huggingface.co/docs/dataset-viewer/en/duckdb) to quickly process any information provided in the dataset, such as sources.

Some of our researchers have contributed datasets with extensive details for end-to-end reproduction, documentation of biases and skews, sources, and accompanying academic papers. For example, [FineWeb](https://huggingface.co/datasets/HuggingFaceFW/fineweb) and the [BLOOM corpus](https://huggingface.co/bigscience/bloom#training-data).

In general, datasets heavily skew towards the Global North, which somewhat mirrors [the distribution of internet use throughout the world](https://en.wikipedia.org/wiki/Global_Internet_usage). In the absence of information, it is best to search for datasets that explicitly acknowledge Global South sourcing, or local contexts that you are most interested in.

### How does Hugging Face handle issues like bias and localization in their open source models and datasets?

All datasets are “biased” in some way – with respect to the topics they cover, where they come from, who they represent, etc.

We therefore encourage detailed reporting of datasets, including bias explicitly, in our [dataset documentation protocol](https://github.com/huggingface/huggingface_hub/blob/main/src/huggingface_hub/templates/datasetcard_template.md) and continue to experiment with different tools to calculate biases and skews (such as [Disaggregators](https://github.com/huggingface/disaggregators), [Data Measurements Tool](https://huggingface.co/blog/data-measurements-tool), [FineWeb bias measurement](https://github.com/meg-huggingface/bias-testing)) – the more they are acknowledged, ‘starred’, and used, the more we can support them, so we encourage those interested to check it out!

## Community
### What is the purpose of the Hugging Face community and how can we benefit from and contribute to it?

Hugging Face is the hosting platform for all things machine learning, and contains a melting pot of researchers from academia and the industry, engineers, coders, hobbyists, students, and many more ML-interested people! As such, it’s a place to interact, discuss, and share your work with that community, which allows you to exchange feedback and technical insights with other users.

### How can smaller organizations tap into and connect with the Hugging Face community for mutual knowledge-sharing?
There are several ways to connect and interact with the relevant community on Hugging Face. 

When you upload a model, dataset, or demo (or link a paper), it automatically creates a discussion panel, where questions can be asked and discussions started by interested users. It’s usually a nice place to start (example: [community and developers interacting about the Kimi-K2-Instruct model](https://huggingface.co/moonshotai/Kimi-K2-Instruct/discussions)). Hugging Face also has a social feed where people can post about their updates, ask questions, and generally interact.

### What are best practices in the Hugging Face community that could be applied to, for instance, build more local AI-focused communities?
Hugging Face supports [the creation of landing pages for all types of organizations](https://huggingface.co/organizations/new), where groups can collect data, models, and other resources, as well as communicate with one another in the Community tabs.

Folks can request to join your organization, and you can let people know about it on social media, through your email channels, and local contacts, as well as in [Hugging Face posts](huggingface.co/?activityType=post).

### Are there any examples of nonprofit organizations using open source technology from the Hugging Face platform?
Nonprofit AI organizations using Hugging Face include:
- Allen AI (AI2): https://huggingface.co/allenai
- Beijing Academy of Artificial Intelligence (BAAI): https://huggingface.co/BAAI
- Eleuther AI: https://huggingface.co/EleutherAI
- Project Numina: https://huggingface.co/AI-MO
- Barcelona Supercomputing Center: https://huggingface.co/BSC-LT
- Arc Institute: https://huggingface.co/arcinstitute
- AI Singapore: https://huggingface.co/aisingapore
- and multiple public, governmental organizations also use Hugging Face as well as academic research groups!
You can search through all the organizations using Hugging Face [here](https://huggingface.co/organizations)!


## Acknowledgments

Thanks a lot for Tech To The Rescue for contacting us to suggest this collaboration. 

Thanks also to all the Hugging Face members who took a look at the document to make suggestions, notably Meg Mitchell and Bruna Trevellin, who've been tremendously helpful in making the doc as complete as possible, and Vaibhav Srivastav, who gave a hand to make this launch happen.
