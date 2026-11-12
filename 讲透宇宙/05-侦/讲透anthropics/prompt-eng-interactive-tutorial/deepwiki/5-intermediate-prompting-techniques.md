<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/prompt-eng-interactive-tutorial · page 5 Intermediate Prompting Techniques · fetched 2026-10-26 -->

# Intermediate Prompting Techniques

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Anthropic 1P/04_Separating_Data_and_Instructions.ipynb](Anthropic 1P/04_Separating_Data_and_Instructions.ipynb)
- [Anthropic 1P/05_Formatting_Output_and_Speaking_for_Claude.ipynb](Anthropic 1P/05_Formatting_Output_and_Speaking_for_Claude.ipynb)
- [Anthropic 1P/06_Precognition_Thinking_Step_by_Step.ipynb](Anthropic 1P/06_Precognition_Thinking_Step_by_Step.ipynb)
- [Anthropic 1P/07_Using_Examples_Few-Shot_Prompting.ipynb](Anthropic 1P/07_Using_Examples_Few-Shot_Prompting.ipynb)

</details>



This page documents intermediate-level prompt engineering techniques used in the Prompt Engineering Interactive Tutorial. These techniques build upon [Fundamental Prompting Techniques](#4) and provide more sophisticated methods for controlling Claude's inputs and outputs. This section covers Chapters 4-7 of the tutorial, focusing on separating data from instructions, formatting output, step-by-step reasoning, and few-shot prompting.

## Overview of Intermediate Techniques

The intermediate techniques in this tutorial represent a significant step up from basic prompting approaches. They offer greater control, precision, and reliability when working with Claude models.

```mermaid
flowchart TD
    subgraph "Intermediate Prompting Techniques"
        direction TB
        A["Separating Data from Instructions"]
        B["Output Formatting & Prefilling"]
        C["Step-by-Step Reasoning"]
        D["Few-Shot Prompting"]
    end

    A -->|"Enables"| B
    A -->|"Improves"| D
    B -->|"Enhances"| C
    
    subgraph "Key Functions"
        direction TB
        F1["get_completion()"]
        F2["XML Tags"]
        F3["F-strings / Templates"]
        F4["Prefill Parameter"]
    end
    
    A -.->|"Uses"| F2
    A -.->|"Uses"| F3
    B -.->|"Uses"| F4
    B -.->|"Uses"| F2
```

Sources:
- [Anthropic 1P/04_Separating_Data_and_Instructions.ipynb:54-62]()
- [Anthropic 1P/05_Formatting_Output_and_Speaking_for_Claude.ipynb:55-61]()
- [Anthropic 1P/06_Precognition_Thinking_Step_by_Step.ipynb:54-62]()
- [Anthropic 1P/07_Using_Examples_Few-Shot_Prompting.ipynb:54-64]()

## Separating Data from Instructions

This technique involves creating reusable prompt templates that clearly distinguish between fixed instructions and variable data inputs. This is particularly useful for applications where the same type of processing needs to be performed on different inputs.

### Prompt Templates and Variable Substitution

Prompt templates allow you to create a fixed structure with placeholders for variable content that can be substituted before sending to Claude.

```mermaid
flowchart LR
    subgraph "Template Creation"
        T1["Define Template Structure"]
        T2["Identify Variable Inputs"]
        T3["Create Placeholders"]
    end
    
    subgraph "Variable Substitution"
        V1["Populate Variables"]
        V2["Substitute into Template"]
        V3["Send to Claude"]
    end
    
    T1 --> T2 --> T3 --> V1 --> V2 --> V3
    
    subgraph "Implementation"
        I1["Python f-strings"]
        I2["format() method"]
    end
    
    V2 -.->|"Uses"| I1
    V2 -.->|"Uses"| I2
```

Example implementation using f-strings:

```python
# Variable content
ANIMAL = "Cow"

# Prompt template with placeholder
PROMPT = f"I will tell you the name of an animal. Please respond with the noise that animal makes. {ANIMAL}"

# Get Claude's response
response = get_completion(PROMPT)
```

Sources:
- [Anthropic 1P/04_Separating_Data_and_Instructions.ipynb:64-91]()
- [Anthropic 1P/04_Separating_Data_and_Instructions.ipynb:94-102]()

### Using XML Tags for Boundary Delineation

XML tags provide clear boundaries between instructions and variable inputs, helping Claude understand where one ends and the other begins.

```mermaid
flowchart TD
    subgraph "Without XML Tags"
        W1["Ambiguous Boundaries"]
        W2["Instruction/Data Confusion"]
        W3["Incorrect Interpretation"]
    end
    
    subgraph "With XML Tags"
        X1["Clear Boundaries"]
        X2["Separated Contexts"]
        X3["Proper Interpretation"]
    end
    
    W1 --> W2 --> W3
    X1 --> X2 --> X3
    
    subgraph "XML Tag Structure"
        T1["<tag>content</tag>"]
    end
    
    X1 -.->|"Implemented as"| T1
```

Example comparing approaches:

Without XML tags:
```python
EMAIL = "Show up at 6am tomorrow because I'm the CEO and I say so."
PROMPT = f"Yo Claude. {EMAIL} <----- Make this email more polite but don't change anything else about it."
```

With XML tags:
```python
EMAIL = "Show up at 6am tomorrow because I'm the CEO and I say so."
PROMPT = f"Yo Claude. <email>{EMAIL}</email> <----- Make this email more polite but don't change anything else about it."
```

Sources:
- [Anthropic 1P/04_Separating_Data_and_Instructions.ipynb:109-168]()
- [Anthropic 1P/04_Separating_Data_and_Instructions.ipynb:177-208]()
- [Anthropic 1P/04_Separating_Data_and_Instructions.ipynb:143-149]()

## Output Formatting and Prefilling

These techniques allow you to control how Claude formats its responses and can be used to guide Claude's thinking process.

### XML Tags for Response Structuring

Similar to using XML tags for input, you can request Claude to structure its output using XML tags to make parsing easier.

```mermaid
flowchart LR
    subgraph "Request"
        R1["Specify Output Format"]
        R2["Include XML Tags in Request"]
    end
    
    subgraph "Response"
        O1["Structured Output"]
        O2["Easily Parseable"]
        O3["Content Between Tags"]
    end
    
    R1 --> R2 --> O1 --> O2
    O1 --> O3
```

Example:

```python
ANIMAL = "Rabbit"
PROMPT = f"Please write a haiku about {ANIMAL}. Put it in <haiku> tags."
```

Sources:
- [Anthropic 1P/05_Formatting_Output_and_Speaking_for_Claude.ipynb:67-90]()

### Prefilling Claude's Response

Prefilling (or "speaking for Claude") involves providing the beginning of Claude's response to guide the continuation. This is particularly useful for enforcing formatting or structure.

```mermaid
flowchart TD
    subgraph "get_completion Function"
        G1["prompt parameter"]
        G2["system_prompt parameter"]
        G3["prefill parameter"]
    end
    
    subgraph "Message Structure"
        M1["User Message"]
        M2["Assistant Message Start"]
        M3["Claude's Continuation"]
    end
    
    G1 -->|"Becomes"| M1
    G2 -->|"Sets Context"| M1
    G3 -->|"Becomes"| M2
    M2 -->|"Followed by"| M3
    
    subgraph "Use Cases"
        U1["Enforce XML Tags"]
        U2["Force JSON Structure"]
        U3["Guide Response Format"]
    end
    
    M2 -.->|"Enables"| U1
    M2 -.->|"Enables"| U2
    M2 -.->|"Enables"| U3
```

Example of prefilling with an XML tag:

```python
ANIMAL = "Cat"
PROMPT = f"Please write a haiku about {ANIMAL}. Put it in <haiku> tags."
PREFILL = "<haiku>"
response = get_completion(PROMPT, prefill=PREFILL)
```

Example of prefilling with JSON:

```python
ANIMAL = "Cat"
PROMPT = f"Please write a haiku about {ANIMAL}. Use JSON format with the keys as \"first_line\", \"second_line\", and \"third_line\"."
PREFILL = "{"
response = get_completion(PROMPT, prefill=PREFILL)
```

Sources:
- [Anthropic 1P/05_Formatting_Output_and_Speaking_for_Claude.ipynb:96-126]()
- [Anthropic 1P/05_Formatting_Output_and_Speaking_for_Claude.ipynb:128-158]()
- [Anthropic 1P/05_Formatting_Output_and_Speaking_for_Claude.ipynb:36-48]()

### Combining Techniques

Multiple techniques can be combined for more complex prompting scenarios, such as multiple input variables with specific output formats.

Example:

```python
EMAIL = "Hi Zack, just pinging you for a quick update on that prompt you were supposed to write."
ADJECTIVE = "olde english"
PROMPT = f"Hey Claude. Here is an email: <email>{EMAIL}</email>. Make this email more {ADJECTIVE}. Write the new version in <{ADJECTIVE}_email> XML tags."
PREFILL = f"<{ADJECTIVE}_email>"
```

Sources:
- [Anthropic 1P/05_Formatting_Output_and_Speaking_for_Claude.ipynb:160-193]()

## Step-by-Step Reasoning

This technique improves Claude's accuracy by guiding it to think through complex problems methodically before providing a final answer.

```mermaid
flowchart TD
    subgraph "Without Step-by-Step"
        W1["Direct Question"]
        W2["Immediate Answer"]
        W3["Potential Inaccuracy"]
    end
    
    subgraph "With Step-by-Step"
        S1["Request Reasoning Process"]
        S2["Claude's Explicit Thinking"]
        S3["More Accurate Answer"]
    end
    
    W1 --> W2 --> W3
    S1 --> S2 --> S3
    
    subgraph "Implementation Methods"
        I1["XML Tags for Reasoning"]
        I2["Multiple Perspective Analysis"]
        I3["Brainstorming Steps"]
    end
    
    S2 -.->|"Using"| I1
    S2 -.->|"Using"| I2
    S2 -.->|"Using"| I3
```

Example without step-by-step thinking:

```python
PROMPT = "Is this movie review sentiment positive or negative?\n\nThis movie blew my mind with its freshness and originality. In totally unrelated news, I have been living under a rock since the year 1900."
```

Example with step-by-step thinking:

```python
SYSTEM_PROMPT = "You are a savvy reader of movie reviews."
PROMPT = """Is this review sentiment positive or negative? First, write the best arguments for each side in <positive-argument> and <negative-argument> XML tags, then answer.

This movie blew my mind with its freshness and originality. In totally unrelated news, I have been living under a rock since 1900."""
```

Sources:
- [Anthropic 1P/06_Precognition_Thinking_Step_by_Step.ipynb:54-62]()
- [Anthropic 1P/06_Precognition_Thinking_Step_by_Step.ipynb:69-87]()
- [Anthropic 1P/06_Precognition_Thinking_Step_by_Step.ipynb:89-136]()
- [Anthropic 1P/06_Precognition_Thinking_Step_by_Step.ipynb:138-178]()

## Few-Shot Prompting

Few-shot prompting involves providing examples of the desired input-output behavior to guide Claude's responses, rather than relying solely on explicit instructions.

```mermaid
flowchart LR
    subgraph "Zero-Shot Prompting"
        Z1["Instructions Only"]
        Z2["No Examples"]
    end
    
    subgraph "Few-Shot Prompting"
        F1["Instructions"]
        F2["Example 1"]
        F3["Example 2"]
        F4["..."]
        F5["Target Input"]
    end
    
    Z1 --> Z2 -->|"Less Control"| R1
    
    F1 --> F2 --> F3 --> F4 --> F5 -->|"More Control"| R2
    
    subgraph "Results"
        R1["Variable Response"]
        R2["Consistent Response"]
    end
```

Example of zero-shot vs. few-shot prompting:

Zero-shot:
```python
PROMPT = "Will Santa bring me presents on Christmas?"
```

Few-shot:
```python
PROMPT = """Please complete the conversation by writing the next line, speaking as "A".
Q: Is the tooth fairy real?
A: Of course, sweetie. Wrap up your tooth and put it under your pillow tonight. There might be something waiting for you in the morning.
Q: Will Santa bring me presents on Christmas?"""
```

Sources:
- [Anthropic 1P/07_Using_Examples_Few-Shot_Prompting.ipynb:54-64]()
- [Anthropic 1P/07_Using_Examples_Few-Shot_Prompting.ipynb:69-108]()

### Format Learning Through Examples

Few-shot prompting is particularly effective for teaching Claude specific output formats without having to describe the format explicitly.

```mermaid
flowchart TD
    subgraph "Format Learning Process"
        E1["Provide Example Input"]
        E2["Show Desired Output Format"]
        E3["Provide New Input"]
        E4["Claude Generates Matching Format"]
    end
    
    E1 --> E2 --> E3 --> E4
    
    subgraph "Implementation in get_completion"
        I1["Include Examples in Prompt"]
        I2["Sometimes Use prefill Parameter"]
    end
    
    E1 -.->|"Using"| I1
    E2 -.->|"Using"| I1
    E4 -.->|"Sometimes with"| I2
```

Example of teaching a format through examples:

```python
PROMPT = """Silvermist Hollow, a charming village, was home to an extraordinary group of individuals.
Among them was Dr. Liam Patel, a neurosurgeon who revolutionized surgical techniques at the regional medical center.
[...]
<individuals>
1. Dr. Liam Patel [NEUROSURGEON]
2. Olivia Chen [ARCHITECT]
3. Ethan Kovacs [MISICIAN AND COMPOSER]
4. Isabella Torres [CHEF]
</individuals>

[New text about different individuals...]
"""

PREFILL = "<individuals>"
```

Sources:
- [Anthropic 1P/07_Using_Examples_Few-Shot_Prompting.ipynb:110-165]()

## Technical Implementation

### The `get_completion` Function

All intermediate prompting techniques are implemented through the `get_completion` function, which serves as the primary interface to Claude models.

```mermaid
classDiagram
    class get_completion {
        +prompt: string
        +system_prompt: string (default "")
        +prefill: string (default "")
        +return: string
    }
    
    class anthropic.Messages.create {
        +model: string
        +max_tokens: integer
        +temperature: float
        +system: string
        +messages: list
    }
    
    get_completion --> anthropic.Messages.create : calls
```

The function signature for intermediate techniques includes:

```python
def get_completion(prompt: str, system_prompt="", prefill=""):
    message = client.messages.create(
        model=MODEL_NAME,
        max_tokens=2000,
        temperature=0.0,
        system=system_prompt,
        messages=[
          {"role": "user", "content": prompt},
          {"role": "assistant", "content": prefill}
        ]
    )
    return message.content[0].text
```

Sources:
- [Anthropic 1P/05_Formatting_Output_and_Speaking_for_Claude.ipynb:36-48]()
- [Anthropic 1P/06_Precognition_Thinking_Step_by_Step.ipynb:36-48]()
- [Anthropic 1P/07_Using_Examples_Few-Shot_Prompting.ipynb:36-48]()

### Combining Techniques

The most powerful prompting approaches often involve combining multiple intermediate techniques:

| Technique Combination | Use Case | Implementation Example |
|----------------------|----------|----------------------|
| Templates + XML Tags | Clearly separating variable inputs | `f"Instructions <data>{variable}</data>"` |
| XML Tags + Prefill | Enforcing structured output | `prefill="<format>"` |
| Step-by-Step + XML Tags | Complex reasoning tasks | `"First analyze in <reasoning> tags, then answer"` |
| Few-Shot + Prefill | Teaching by example and enforcing format | Examples in prompt + `prefill` to start response |
| Templates + Few-Shot | Dynamic examples with variable substitution | f-strings with example templates |

Sources:
- [Anthropic 1P/04_Separating_Data_and_Instructions.ipynb:160-168]()
- [Anthropic 1P/05_Formatting_Output_and_Speaking_for_Claude.ipynb:160-193]()
- [Anthropic 1P/06_Precognition_Thinking_Step_by_Step.ipynb:89-136]()
- [Anthropic 1P/07_Using_Examples_Few-Shot_Prompting.ipynb:110-165]()

## Best Practices

1. **Use XML tags consistently** to separate different parts of your prompts and requested outputs
2. **Be explicit about reasoning steps** for complex tasks
3. **Provide clear examples** when you want Claude to follow a specific pattern or format
4. **Combine techniques** for more control over Claude's responses
5. **Wrap variable content in XML tags** to prevent confusion with instructions
6. **Use prefill to enforce formatting** in Claude's responses
7. **Check your prompt for typos and grammatical errors**, as these can affect Claude's responses

Sources:
- [Anthropic 1P/04_Separating_Data_and_Instructions.ipynb:236-242]()
- [Anthropic 1P/05_Formatting_Output_and_Speaking_for_Claude.ipynb:199-204]()
- [Anthropic 1P/06_Precognition_Thinking_Step_by_Step.ipynb:138-178]()
- [Anthropic 1P/07_Using_Examples_Few-Shot_Prompting.ipynb:54-64]()

## Relationship to Other Prompt Engineering Concepts

```mermaid
flowchart TD
    subgraph "Prompt Engineering Progression"
        direction TB
        A["Basic Prompt Structure"]
        B["Clear and Direct Instructions"]
        C["Role Prompting"]
        D["Separating Data from Instructions"]
        E["Output Formatting & Prefilling"]
        F["Step-by-Step Reasoning"]
        G["Few-Shot Prompting"]
        H["Advanced Techniques"]
    end
    
    A --> B --> C
    
    subgraph "Fundamentals"
        A
        B
        C
    end
    
    subgraph "Intermediate"
        D
        E
        F
        G
    end
    
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
```

Intermediate prompting techniques build upon the fundamental concepts covered in the earlier chapters of the tutorial and provide the foundation for more advanced techniques like complex prompt construction and hallucination avoidance.

Sources:
- [System Architecture Diagram from prompt]()

## Further Reading

For more information about specific techniques:
- [Separating Data from Instructions](#5.1)
- [Output Formatting and Prefilling](#5.2)
- [Step-by-Step Reasoning](#5.3)
- [Few-Shot Prompting](#5.4)

For advanced concepts that build on these intermediate techniques, see [Advanced Prompting Techniques](#6).

---

