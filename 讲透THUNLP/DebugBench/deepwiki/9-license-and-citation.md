<!-- source: DeepWiki mcp.deepwiki.com · repo thunlp/DebugBench · page 9 License and Citation · fetched 2026-11-02 -->

# License and Citation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [README.md](README.md)

</details>



This page provides licensing information for the DebugBench project and guidance on how to properly cite the work in academic publications. For information about getting started with the benchmark, see [Quick Start Guide](#1.2). For details on accessing the dataset, see [Accessing the Dataset](#3.5).

## License Overview

DebugBench is released under the Apache License 2.0, an open-source permissive license that allows both commercial and non-commercial use, modification, and distribution of the software. The license provides clear terms for use, reproduction, and redistribution while protecting contributors from liability.

### License Type: Apache 2.0

```mermaid
graph TB
    License["Apache License 2.0<br/>Version 2.0, January 2004"]
    
    subgraph Permissions["Permissions Granted"]
        Commercial["Commercial Use<br/>Allowed for business purposes"]
        Modify["Modification<br/>Create derivative works"]
        Distribute["Distribution<br/>Share original or modified"]
        Patent["Patent Use<br/>Express patent grant"]
        Private["Private Use<br/>Use and modify privately"]
    end
    
    subgraph Conditions["Conditions Required"]
        Notice["License Notice<br/>Include copy of license"]
        State["State Changes<br/>Document modifications"]
        Copyright["Copyright Notice<br/>Preserve attributions"]
    end
    
    subgraph Limitations["Limitations"]
        Liability["No Liability<br/>No warranty provided"]
        Trademark["No Trademark<br/>Cannot use marks"]
        Warranty["No Warranty<br/>AS-IS basis"]
    end
    
    License --> Permissions
    License --> Conditions
    License --> Limitations
```

**License Scope Across Components**

Sources: [LICENSE:1-201](), [README.md:1-57]()

### Copyright Information

The copyright holder for DebugBench is **Runchu Tian** (2023). The copyright notice is included in the license file and applies to all components of the repository.

**Copyright Notice:**
```
Copyright [2023] [Runchu Tian]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0
```

Sources: [LICENSE:189-195]()

### Key License Terms

The Apache License 2.0 includes the following key provisions:

| Term | Description | License Section |
|------|-------------|-----------------|
| **Copyright License** | Perpetual, worldwide, non-exclusive, royalty-free license to reproduce, prepare derivative works, display, perform, sublicense, and distribute | Section 2 |
| **Patent License** | Express grant of patent rights for contributions | Section 3 |
| **Redistribution** | May redistribute in any medium with modifications, provided license is included and changes are stated | Section 4 |
| **Contributions** | Contributions submitted are under the same license terms | Section 5 |
| **Disclaimer of Warranty** | Work provided "AS IS" without warranties | Section 7 |
| **Limitation of Liability** | Contributors not liable for damages | Section 8 |

Sources: [LICENSE:66-174]()

## Citation Information

When using DebugBench in academic research, please cite the original paper. The official citation and contact information are provided below.

### BibTeX Entry

```bibtex
@misc{tian2024debugbench,
      title={DebugBench: Evaluating Debugging Capability of Large Language Models}, 
      author={Runchu Tian and Yining Ye and Yujia Qin and Xin Cong and Yankai Lin and Zhiyuan Liu and Maosong Sun},
      year={2024},
      eprint={2401.04621},
      archivePrefix={arXiv},
      primaryClass={cs.SE}
}
```

Sources: [README.md:46-54]()

### Paper Information

| Field | Value |
|-------|-------|
| **Title** | DebugBench: Evaluating Debugging Capability of Large Language Models |
| **Authors** | Runchu Tian, Yining Ye, Yujia Qin, Xin Cong, Yankai Lin, Zhiyuan Liu, Maosong Sun |
| **Year** | 2024 |
| **arXiv ID** | 2401.04621 |
| **Primary Class** | cs.SE (Software Engineering) |

Sources: [README.md:47-53]()

### Attribution Requirements

When using DebugBench components, users should:

```mermaid
flowchart TD
    Use["Using DebugBench"]
    
    Benchmark["Using Benchmark Dataset"]
    Evaluation["Using Evaluation System"]
    Construction["Using Construction Pipeline"]
    
    CiteDataset["Cite Dataset<br/>Reference arXiv paper"]
    CiteCode["Cite Code<br/>Star GitHub repository"]
    License["Include License<br/>Apache 2.0 notice"]
    
    Attribute["Proper Attribution"]
    
    Use --> Benchmark
    Use --> Evaluation
    Use --> Construction
    
    Benchmark --> CiteDataset
    Evaluation --> CiteDataset
    Construction --> CiteDataset
    
    Benchmark --> CiteCode
    Evaluation --> CiteCode
    Construction --> CiteCode
    
    Benchmark --> License
    Evaluation --> License
    Construction --> License
    
    CiteDataset --> Attribute
    CiteCode --> Attribute
    License --> Attribute
```

**Attribution Flow for Different Use Cases**

Sources: [README.md:40-44]()

## Component-Level Licensing

The Apache 2.0 license applies uniformly across all components of the DebugBench repository:

```mermaid
graph TB
    Root["DebugBench Repository<br/>Apache 2.0"]
    
    subgraph DatasetComponents["Dataset Components"]
        Benchmark["benchmark/<br/>51 JSON shards"]
        Construction["dataset_construction/<br/>Bug implantation code"]
        Cases["dataset_construction/cases/<br/>Oracle code collections"]
    end
    
    subgraph EvalComponents["Evaluation Components"]
        EvalCode["evaluation/<br/>Testing framework"]
        LeetCodeEnv["leetcode_env/<br/>Gym environment"]
        Utils["leetcode_env/utils/<br/>Utilities"]
    end
    
    subgraph ResultComponents["Results Components"]
        Results["evalution_result/<br/>Pre-computed outputs"]
    end
    
    subgraph DataComponents["Data Processing"]
        Scraped["scraped_data/<br/>Raw LeetCode data"]
        Validated["validated_solutions/<br/>Tested solutions"]
    end
    
    Root --> DatasetComponents
    Root --> EvalComponents
    Root --> ResultComponents
    Root --> DataComponents
    
    License2["Apache License 2.0<br/>Applies to all components"]
    
    DatasetComponents -.licensed under.-> License2
    EvalComponents -.licensed under.-> License2
    ResultComponents -.licensed under.-> License2
    DataComponents -.licensed under.-> License2
```

**Repository Structure with License Scope**

| Component | Path | License | Notes |
|-----------|------|---------|-------|
| Benchmark Dataset | `benchmark/` | Apache 2.0 | 4,253 buggy code instances |
| Oracle Code | `dataset_construction/cases/` | Apache 2.0 | Source correct solutions |
| Evaluation Framework | `evaluation/` | Apache 2.0 | LeetCode testing system |
| Environment | `leetcode_env/` | Apache 2.0 | Gym-based environment |
| Pre-computed Results | `evalution_result/` | Apache 2.0 | Baseline model outputs |

Sources: [README.md:26-36](), [LICENSE:1-201]()

## External Dependencies and Data Sources

While DebugBench itself is licensed under Apache 2.0, it integrates with external services and uses third-party data sources that have their own terms:

```mermaid
graph TB
    DebugBench["DebugBench<br/>Apache 2.0"]
    
    subgraph External["External Services"]
        LeetCode["LeetCode Platform<br/>Subject to LeetCode TOS"]
        OpenAI["OpenAI API<br/>GPT-4 usage terms"]
        HuggingFace["Hugging Face<br/>Dataset hosting"]
    end
    
    subgraph ThirdParty["Third-Party Libraries"]
        Gym["gym<br/>MIT License"]
        Pydantic["pydantic<br/>MIT License"]
        OpenAILib["openai library<br/>Apache 2.0"]
        Transformers["transformers<br/>Apache 2.0"]
    end
    
    DebugBench -->|Data source| LeetCode
    DebugBench -->|Bug generation| OpenAI
    DebugBench -->|Dataset hosting| HuggingFace
    
    DebugBench -->|Depends on| Gym
    DebugBench -->|Depends on| Pydantic
    DebugBench -->|Depends on| OpenAILib
    DebugBench -->|Depends on| Transformers
    
    Note1["Note: Users must comply with<br/>LeetCode Terms of Service"]
    Note2["Note: API usage subject to<br/>OpenAI usage policies"]
    
    LeetCode -.-> Note1
    OpenAI -.-> Note2
```

**External Dependencies and Their Licenses**

### Data Source Attribution

The benchmark dataset is derived from LeetCode community solutions:
- **Source**: LeetCode platform (https://leetcode.com/)
- **Content**: Code snippets posted after June 2022
- **Terms**: Subject to LeetCode Terms of Service
- **Processing**: Bugs implanted using GPT-4

Users should be aware that while the DebugBench processing and framework are under Apache 2.0, the original LeetCode problem descriptions and test cases remain subject to LeetCode's terms.

Sources: [README.md:15-22]()

## Contact and Support

For questions about licensing, usage, or citations:

| Contact Method | Details |
|----------------|---------|
| **Email** | trc20@mails.tsinghua.edu.cn |
| **GitHub Issues** | Open an issue at the repository |
| **Hugging Face** | https://huggingface.co/datasets/Rtian/DebugBench |

**Recommended Actions:**
- **Star the repository** if you find DebugBench helpful
- **Cite the paper** in your publications
- **Contact via email** for specific questions
- **Open GitHub issues** for bugs or feature requests

Sources: [README.md:44]()

## Usage Guidelines

### For Academic Research

```mermaid
flowchart LR
    Research["Academic Research"]
    
    Use["Use DebugBench"]
    Cite["Cite Paper<br/>Include BibTeX"]
    License["Include License<br/>If redistributing"]
    Attribute["Acknowledge Source<br/>In publication"]
    
    Research --> Use
    Use --> Cite
    Use --> License
    Use --> Attribute
    
    Publication["Research Publication"]
    
    Cite --> Publication
    License --> Publication
    Attribute --> Publication
```

**Academic Usage Flow**

When using DebugBench for academic purposes:

1. **Citation Required**: Include the BibTeX citation in your paper
2. **Attribution**: Acknowledge DebugBench in your methodology section
3. **Dataset Reference**: Cite the Hugging Face dataset when using benchmark data
4. **Modifications**: If you extend or modify the benchmark, state the changes clearly

Sources: [README.md:40-44]()

### For Commercial Use

The Apache 2.0 license explicitly permits commercial use:

| Permission | Description | Requirement |
|------------|-------------|-------------|
| **Commercial Use** | Use in commercial products/services | Must include license notice |
| **Modification** | Create modified versions | Must state changes made |
| **Distribution** | Distribute original or modified | Must include license copy |
| **Private Use** | Use internally without distribution | No special requirements |
| **Patent Rights** | Use any patents in contributions | Granted by license |

**Requirements for Commercial Distribution:**
1. Include a copy of the Apache 2.0 license
2. Preserve copyright notices from the original work
3. State any modifications made to the original files
4. Include a NOTICE file if one exists

Sources: [LICENSE:89-121]()

### For Educational Use

Educational institutions may use DebugBench freely:

- Use in coursework and assignments
- Include in teaching materials
- Modify for educational purposes
- Share with students

**Best Practice**: Encourage students to cite the paper when using DebugBench in projects or research.

Sources: [README.md:40-44](), [LICENSE:1-201]()

## Redistribution Terms

If redistributing DebugBench or derivative works:

```mermaid
flowchart TD
    Redistribute["Redistribute DebugBench"]
    
    Original["Original Code"]
    Modified["Modified Code"]
    
    IncludeLicense["Include License<br/>Apache 2.0 copy"]
    PreserveNotices["Preserve Notices<br/>Copyright, patent, trademark"]
    StateChanges["State Changes<br/>Document modifications"]
    
    SourceForm["Source Form<br/>Editable code"]
    ObjectForm["Object Form<br/>Compiled binaries"]
    
    Redistribute --> Original
    Redistribute --> Modified
    
    Original --> IncludeLicense
    Modified --> IncludeLicense
    Modified --> StateChanges
    
    IncludeLicense --> PreserveNotices
    
    PreserveNotices --> SourceForm
    PreserveNotices --> ObjectForm
    
    Compliant["Apache 2.0 Compliant<br/>Distribution"]
    
    SourceForm --> Compliant
    ObjectForm --> Compliant
```

**Redistribution Compliance Workflow**

### Required Steps for Redistribution

1. **Include License**: Provide a copy of the Apache License 2.0 ([LICENSE:1-201]())
2. **Preserve Notices**: Keep all copyright, patent, trademark notices ([LICENSE:100-104]())
3. **State Changes**: Mark modified files with change notices ([LICENSE:97-98]())
4. **Attribution**: Include attribution notices if present ([LICENSE:106-121]())

Sources: [LICENSE:89-128]()

## Warranty and Liability

The Apache License 2.0 includes important disclaimers:

### Disclaimer of Warranty

```
Unless required by applicable law or agreed to in writing, Licensor 
provides the Work (and each Contributor provides its Contributions) 
on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, 
either express or implied, including, without limitation, any 
warranties or conditions of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, 
or FITNESS FOR A PARTICULAR PURPOSE.
```

### Limitation of Liability

```
In no event and under no legal theory, whether in tort (including 
negligence), contract, or otherwise, unless required by applicable 
law (such as deliberate and grossly negligent acts) or agreed to in 
writing, shall any Contributor be liable to You for damages.
```

**Key Points:**
- No warranty provided for the software
- Software provided "as is"
- Contributors not liable for damages
- User assumes all risks of use

Sources: [LICENSE:143-163]()

## Summary

| Aspect | Details |
|--------|---------|
| **License** | Apache License 2.0 |
| **Copyright** | Runchu Tian (2023) |
| **Permissions** | Commercial use, modification, distribution, patent use, private use |
| **Conditions** | Include license, state changes, preserve copyright notices |
| **Limitations** | No liability, no trademark rights, no warranty |
| **Citation** | arXiv:2401.04621 (tian2024debugbench) |
| **Contact** | trc20@mails.tsinghua.edu.cn |
| **Repository** | https://github.com/thunlp/DebugBench |
| **Dataset** | https://huggingface.co/datasets/Rtian/DebugBench |

Sources: [README.md:1-57](), [LICENSE:1-201]()