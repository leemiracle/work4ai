# The Aesopian Author Game

This project provides a framework for simulating the game "The Aesopian
Author," allowing for experiments with different types of LLM-powered agents in
a game of subtext and survival.

## Game Rules

The game rules are provided below @instructions/v0/game_rules.md

## Player Personas

There are three variants of the game depending on the extra information critic
knows about the author: 1. Shared Context Only: Author and Critic share a common
set of stories that can be useful for veiled communication 2. Literary History
Only: Critic maintains a history of the author's work and can use that to decode
the meaning of the text. 3. Full: Both shared context and literary history are
provided to the critic

The system prompts define the objectives for each player which are:

### For Inquisitor

(Only one type of system prompt, since inquisitor information remains the same
irrespective of the three variants above)
@instructions/v0/inquisitor_prompts/default.md

### For Author

#### Shared Context Only

@instructions/v0/author_prompts/shared_context_only.md

#### Literary History Only

@instructions/v0/author_prompts/literary_history_only.md

#### Full

@instructions/v0/author_prompts/full.md

### For Critic

#### Shared Context Only

@instructions/v0/critic_prompts/shared_context_only.md

#### Literary History Only

@instructions/v0/critic_prompts/literary_history_only.md

#### Full

@instructions/v0/critic_prompts/full.md

