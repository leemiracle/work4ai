> 来源: [https://deepwiki.com/deepseek-ai/DeepSeek-VL2/6-conversation-templates](https://deepwiki.com/deepseek-ai/DeepSeek-VL2/6-conversation-templates)
> DeepWiki deepseek-ai/DeepSeek-VL2

# Conversation Templates

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/README.md?plain=1)
 - [deepseek_vl2/models/conversation.py](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/deepseek_vl2/models/conversation.py)
 
  
## Purpose and Scope

 This document explains how conversation templates work in the DeepSeek-VL2 system. Conversation templates provide structured formats for interactions between users and the model, handling both text and image inputs. They standardize prompt formatting and manage conversation history while supporting special tokens for features like visual grounding.

 For information about model inference and execution, see [Inference Guide](https://deepwiki.com/deepseek-ai/DeepSeek-VL2/4-inference-guide).

 
## Conversation Template System Overview

 Conversation templates in DeepSeek-VL2 manage the formatting of multi-turn conversations, ensuring consistency and proper handling of special tokens. The system is built around the `Conversation` class that defines the structure and behavior of different template styles.

 
```

```

 *Diagram: Conversation template flow in DeepSeek-VL2*

 Sources: [deepseek_vl2/models/conversation.py](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/deepseek_vl2/models/conversation.py) [README.md115-138](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/README.md?plain=1#L115-L138)

 
## Template Structure

 The `Conversation` class is the core component for managing conversation templates. Each template defines how messages should be formatted, including separators between messages, role names, and stop tokens.

 
```

```

 *Diagram: Conversation class structure*

 Sources: [deepseek_vl2/models/conversation.py19-122](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/deepseek_vl2/models/conversation.py#L19-L122)

 
### Key Components

 
 - **Name**: Unique identifier for the template (e.g., "deepseek", "deepseekv2")
 - **System Message**: Optional instructional message that precedes the conversation
 - **Roles**: Names for conversation participants (typically user and assistant)
 - **Messages**: The conversation history stored as role-message pairs
 - **Separator Style**: Defines how messages are separated and formatted
 - **Separators**: Strings used to separate messages in the prompt
 - **Stop Tokens**: Criteria to determine when generation should stop
 
 
## Separator Styles

 The `SeparatorStyle` enum defines different formatting approaches for conversations:

 
| Style | Purpose | Format Characteristics |
|---|---|---|
| DeepSeek | Standard format for DeepSeek-VL2 | Uses role labels with colons and double newlines between turns |
| DeepSeekV2 | Alternative format with specialized tokens | Uses special tokens like <｜sft▁begin｜> and <｜sft▁end｜> |
| PLAIN | Simple messages without role labels | No explicit role markers, minimal formatting |
| ALIGNMENT | Special format for image inputs | Automatically adds <image> for user turns |

 Sources: [deepseek_vl2/models/conversation.py10-16](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/deepseek_vl2/models/conversation.py#L10-L16) [deepseek_vl2/models/conversation.py44-104](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/deepseek_vl2/models/conversation.py#L44-L104)

 
## Built-in Templates

 DeepSeek-VL2 comes with several pre-registered conversation templates:

 
```

```

 *Diagram: Built-in conversation templates*

 Sources: [deepseek_vl2/models/conversation.py174-287](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/deepseek_vl2/models/conversation.py#L174-L287)

 
### Default Template: "deepseek"

 The standard template used for most interactions with DeepSeek-VL2:

 
```
<|User|>: <image>
<|ref|>The giraffe at the back.<|/ref|>.

<|Assistant|>: <|ref|>The giraffe at the back.<|/ref|><|det|>[[580, 270, 999, 900]]<|/det|><｜end▁of▁sentence｜>
```

 Sources: [README.md123-169](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/README.md?plain=1#L123-L169)

 
## Using Templates for Conversation

 
### Creating Conversations

 To create a conversation:

 
 - Get a template instance: `conv = get_conv_template("deepseek")`
 - Add messages: `conv.append_message(conv.roles[0], "Hello with <image>")`
 - Generate the prompt: `prompt = conv.get_prompt()`
 
 
### Special Tokens

 DeepSeek-VL2 uses special tokens in conversations for specific functions:

 
| Token | Purpose |
|---|---|
| <image> | Indicates image placement in the text |
| <\|ref\|>...<\|/ref\|> | Marks text referring to specific objects in images |
| <\|det\|>[[x1, y1, x2, y2]]<\|/det\|> | Contains bounding box coordinates for detected objects |
| <｜end▁of▁sentence｜> | Marks the end of the assistant's response |
| <｜sft▁begin｜>, <｜sft▁end｜> | Used in the DeepSeekV2 template to mark message boundaries |

 Sources: [README.md124-169](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/README.md?plain=1#L124-L169) [deepseek_vl2/models/conversation.py204-254](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/deepseek_vl2/models/conversation.py#L204-L254)

 
## Integration with DeepSeek-VL2 Processor

 Conversation templates are integrated with the `DeepseekVLV2Processor` to prepare inputs for the model:

 
```

```

 *Diagram: Conversation processing flow*

 Sources: [README.md126-143](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/README.md?plain=1#L126-L143)

 
## Example Usage

 The conversation format used in the DeepSeek-VL2 codebase typically follows this structure:

 
```

```

 This structure is then processed by the `DeepseekVLV2Processor` to create the necessary inputs for the model:

 
```

```

 Sources: [README.md105-143](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/README.md?plain=1#L105-L143) [README.md265-288](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/README.md?plain=1#L265-L288)

 
## Template Registration

 New conversation templates can be registered using the `register_conv_template` function:

 
```

```

 Sources: [deepseek_vl2/models/conversation.py176-187](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/deepseek_vl2/models/conversation.py#L176-L187) [deepseek_vl2/models/conversation.py208-223](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/deepseek_vl2/models/conversation.py#L208-L223)

 
## Memory Considerations

 When using conversation templates with large models like DeepSeek-VL2-small, memory optimization techniques like incremental prefilling may be necessary, especially on GPUs with limited memory (e.g., 40GB).

 Sources: [README.md245-336](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/README.md?plain=1#L245-L336)
