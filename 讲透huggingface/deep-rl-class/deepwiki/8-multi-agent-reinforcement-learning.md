<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/deep-rl-class · page 8 Multi-Agent Reinforcement Learning · fetched 2026-10-26 -->

# Multi-Agent Reinforcement Learning

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [units/en/unit7/additional-readings.mdx](units/en/unit7/additional-readings.mdx)
- [units/en/unit7/conclusion.mdx](units/en/unit7/conclusion.mdx)
- [units/en/unit7/hands-on.mdx](units/en/unit7/hands-on.mdx)
- [units/en/unit7/introduction-to-marl.mdx](units/en/unit7/introduction-to-marl.mdx)
- [units/en/unit7/introduction.mdx](units/en/unit7/introduction.mdx)
- [units/en/unit7/multi-agent-setting.mdx](units/en/unit7/multi-agent-setting.mdx)
- [units/en/unit7/self-play.mdx](units/en/unit7/self-play.mdx)

</details>



This page covers the concepts and implementation of Multi-Agent Reinforcement Learning (MARL) in the Deep RL Course. It explains the fundamentals of training multiple agents that interact in a shared environment, focusing on both cooperative and competitive scenarios. For information about the specific implementation of Proximal Policy Optimization (PPO) in multi-agent settings, see [Proximal Policy Optimization](#9).

## Introduction to MARL

Multi-Agent Reinforcement Learning extends traditional reinforcement learning to settings where multiple agents operate simultaneously in a shared environment. Unlike single-agent systems covered in previous units, MARL introduces new dynamics where agents must consider not only their interactions with the environment but also with other agents.

```mermaid
graph LR
    subgraph "Single-Agent RL"
        A1["Agent"] --> ACT1["Actions"]
        ENV1["Environment"] --> OBS1["Observations"]
        ENV1 --> REW1["Rewards"]
        ACT1 --> ENV1
        OBS1 --> A1
        REW1 --> A1
    end

    subgraph "Multi-Agent RL"
        A2["Agent A"] --> ACT2A["Actions A"]
        A3["Agent B"] --> ACT2B["Actions B"]
        ENV2["Shared Environment"] --> OBS2A["Observations A"]
        ENV2 --> OBS2B["Observations B"]
        ENV2 --> REW2A["Rewards A"]
        ENV2 --> REW2B["Rewards B"]
        ACT2A --> ENV2
        ACT2B --> ENV2
        OBS2A --> A2
        OBS2B --> A3
        REW2A --> A2
        REW2B --> A3
    end
```

Sources: units/en/unit7/introduction-to-marl.mdx, units/en/unit7/introduction.mdx

MARL is crucial for many real-world applications where multiple intelligent entities must interact:
- Warehouse automation with multiple robots
- Autonomous vehicle coordination
- Team-based competitive games

In this unit, we focus on training agents in the SoccerTwos environment, a 2vs2 soccer game where teams compete against each other.

## Types of Multi-Agent Environments

Multi-agent environments are categorized based on the interaction dynamics between agents:

```mermaid
graph TD
    MARL["Multi-Agent RL Environments"] --> COOP["Cooperative"]
    MARL --> COMP["Competitive/Adversarial"]
    MARL --> MIX["Mixed"]
    
    COOP --> COOPEX["Example: Warehouse robots<br>coordinating to move packages"]
    COMP --> COMPEX["Example: Tennis match<br>players competing"]
    MIX --> MIXEX["Example: SoccerTwos<br>Team cooperation + opposing team competition"]
    
    COOPEX --> COOPR["Shared team reward"]
    COMPEX --> COMPR["Zero-sum rewards"]
    MIXEX --> MIXR["Team reward + opposing team penalty"]
```

Sources: units/en/unit7/introduction-to-marl.mdx

### Cooperative Environments
Agents work together to maximize a common benefit. For example, robots in a warehouse collaborating to efficiently load and unload packages.

### Competitive/Adversarial Environments
Agents aim to maximize their own benefits by minimizing their opponents' success. For example, a game of tennis where each agent wants to win against the other.

### Mixed Environments
Environments with both cooperative and competitive elements. In SoccerTwos, agents must cooperate with their teammates while competing against the opposing team.

## Designing Multi-Agent Systems

There are two primary approaches to designing multi-agent reinforcement learning systems:

```mermaid
graph TD
    subgraph "Decentralized Approach"
        DA1["Agent 1"] --> DP1["Policy 1"]
        DA2["Agent 2"] --> DP2["Policy 2"] 
        DA3["Agent 3"] --> DP3["Policy 3"]
        
        DP1 --> DENV["Environment"]
        DP2 --> DENV
        DP3 --> DENV
        
        DENV --> DOBS1["Observations 1"]
        DENV --> DOBS2["Observations 2"]
        DENV --> DOBS3["Observations 3"]
        
        DOBS1 --> DA1
        DOBS2 --> DA2
        DOBS3 --> DA3
    end
    
    subgraph "Centralized Approach"
        CA1["Agent 1"] --> CBUF["Experience Buffer"]
        CA2["Agent 2"] --> CBUF
        CA3["Agent 3"] --> CBUF
        
        CBUF --> CSP["Shared Policy"]
        
        CSP --> CENV["Environment"]
        
        CENV --> COBS1["Observations 1"]
        CENV --> COBS2["Observations 2"]
        CENV --> COBS3["Observations 3"]
        
        COBS1 --> CA1
        COBS2 --> CA2
        COBS3 --> CA3
    end
```

Sources: units/en/unit7/multi-agent-setting.mdx

### Decentralized Approach
Each agent is trained independently, treating other agents as part of the environment dynamics. This approach:
- Simplifies implementation (agents are trained like single agents)
- Makes the environment non-stationary (as other agents learn and change)
- Creates challenges for convergence in learning algorithms

### Centralized Approach
A single policy is learned for all agents, or agents share information during training:
- Creates a stationary environment
- Enables more coordinated behaviors
- Uses collective experience to train a policy that benefits the whole system

## Self-Play for Training Competitive Agents

Self-play is a technique for training agents in competitive settings without requiring pre-trained opponents.

```mermaid
flowchart TD
    START["Initial Policy"] --> TRAINA["Train Agent"]
    TRAINA --> SAVEA["Save Policy Copy"]
    SAVEA --> TRAINB["Train Agent"]
    TRAINB --> SAVEB["Save Policy Copy"]
    SAVEB --> TRAINC["Train Agent"]
    
    SAVEA -.-> OPPOOL["Opponent Pool"]
    SAVEB -.-> OPPOOL
    OPPOOL -.-> TRAINB
    OPPOOL -.-> TRAINC
```

Sources: units/en/unit7/self-play.mdx

### How Self-Play Works
1. The agent starts with an initial policy
2. It plays against a copy of itself (same policy)
3. As the agent improves, copies of its policy are saved
4. The agent trains against these saved versions, gradually facing stronger opponents

Self-play addresses a key challenge in training competitive agents - finding opponents of appropriate difficulty. If opponents are too strong, the agent won't learn effectively; if too weak, the agent develops strategies that fail against better opponents.

### Key Self-Play Hyperparameters in Unity ML-Agents
- `save_steps`: How often to save a new policy version for the opponent pool
- `team_change`: How often to swap between teams
- `swap_steps`: How frequently to change opponents
- `window`: Number of past policies to keep in the opponent pool
- `play_against_latest_model_ratio`: Probability of playing against the most recent policy

## MA-POCA: Training Cooperative Agents

For training cooperative agents within teams, Unity ML-Agents developed MA-POCA (Multi-Agent POsthumous Credit Assignment).

```mermaid
graph TD
    subgraph "Team of Agents"
        AG1["Agent 1"] --> ACT1["Actions 1"]
        AG2["Agent 2"] --> ACT2["Actions 2"]
        
        OBS1["Observations 1"] --> AG1
        OBS2["Observations 2"] --> AG2
    end
    
    subgraph "Training Process"
        CC["Centralized Critic"]
        ACT1 --> ENV["Environment"]
        ACT2 --> ENV
        
        ENV --> OBS1
        ENV --> OBS2
        ENV --> TR["Team Reward"]
        
        OBS1 --> CC
        OBS2 --> CC
        ACT1 --> CC
        ACT2 --> CC
        TR --> CC
        
        CC --> V1["Value Estimate 1"]
        CC --> V2["Value Estimate 2"]
        
        V1 --> AG1
        V2 --> AG2
    end
```

Sources: units/en/unit7/hands-on.mdx

MA-POCA uses centralized learning with decentralized execution:
- Each agent makes decisions based only on local observations
- A centralized critic processes states of all team agents to evaluate individual contributions
- This helps determine how well each agent is doing within the context of the team
- Allows agents to learn cooperative behaviors despite receiving only team-level rewards

This solves a common issue in team environments where every agent on the team receives the same reward regardless of their individual contributions.

## The ELO Rating System for Evaluation

In adversarial games, tracking cumulative reward is not sufficient since it depends heavily on opponent skill. The ELO rating system provides a better measure of relative skill level.

```mermaid
flowchart TD
    MATCH["Match: Agent A vs Agent B"] --> CALC["Calculate Expected Outcomes"]
    CALC --> RESULT["Match Result"]
    RESULT --> UPDATE["Update ELO Ratings"]
    
    subgraph "Expected Outcome Calculation"
        EA["E_A = 1/(1+10^((R_B-R_A)/400))"]
        EB["E_B = 1/(1+10^((R_A-R_B)/400))"]
    end
    
    subgraph "Rating Update"
        RA["R_A_new = R_A + K*(S_A - E_A)"]
        RB["R_B_new = R_B + K*(S_B - E_B)"]
    end
    
    CALC --> EA
    CALC --> EB
    RESULT --> RA
    RESULT --> RB
    RA --> UPDATE
    RB --> UPDATE
```

Sources: units/en/unit7/self-play.mdx

### How ELO Works
- Each agent starts with an initial rating (typically 1200)
- After a match, points transfer from loser to winner
- Transfer amount depends on expected outcome based on current ratings:
  - If a higher-rated agent wins against a lower-rated one, few points transfer
  - If a lower-rated agent wins against a higher-rated one, many points transfer

ELO provides a balanced evaluation system that:
- Always keeps total points in the system constant
- Self-corrects when agents face opponents of varying skill levels
- Works for team games by calculating team average ratings

## SoccerTwos Environment

The SoccerTwos environment from Unity ML-Agents is a 2vs2 soccer game where teams compete to score goals.

```mermaid
graph TD
    subgraph "SoccerTwos Environment"
        FIELD["Soccer Field"]
        BG["Blue Goal"]
        PG["Purple Goal"]
        BALL["Ball"]
        
        BA1["Blue Agent 1"]
        BA2["Blue Agent 2"]
        PA1["Purple Agent 1"]
        PA2["Purple Agent 2"]
        
        BA1 --- BT["Blue Team"]
        BA2 --- BT
        PA1 --- PT["Purple Team"]
        PA2 --- PT
        
        BT --- FIELD
        PT --- FIELD
        BALL --- FIELD
        BG --- FIELD
        PG --- FIELD
    end
    
    subgraph "Agent Observation and Action"
        RC["Raycasts (336 dimensions)"]
        AB["3 Action Branches"]
        NNP["Neural Network Policy"]
        
        RC --> NNP
        NNP --> AB
    end
```

Sources: units/en/unit7/hands-on.mdx

### Environment Details
- **Observation Space**: Vector of size 336
  - 11 ray-casts forward over 120 degrees (264 dimensions)
  - 3 ray-casts backward over 90 degrees (72 dimensions)
  - Ray-casts detect: Ball, Goals, Walls, and Agents
- **Action Space**: Three discrete branches controlling movement and rotation
- **Reward Function**: +1 when team scores, -1 when opponent scores

## Training Agents in SoccerTwos

Training effective agents in SoccerTwos requires combining Self-Play (for competitive improvement) with MA-POCA (for team cooperation).

The configuration file defines training parameters:

```yaml
behaviors:
  SoccerTwos:
    trainer_type: poca
    hyperparameters:
      batch_size: 2048
      buffer_size: 20480
      learning_rate: 0.0003
      beta: 0.005
      epsilon: 0.2
      lambd: 0.95
      num_epoch: 3
      learning_rate_schedule: constant
    network_settings:
      normalize: false
      hidden_units: 512
      num_layers: 2
      vis_encode_type: simple
    reward_signals:
      extrinsic:
        gamma: 0.99
        strength: 1.0
    keep_checkpoints: 5
    max_steps: 5000000
    time_horizon: 1000
    summary_freq: 10000
    self_play:
      save_steps: 50000
      team_change: 200000
      swap_steps: 2000
      window: 10
      play_against_latest_model_ratio: 0.5
      initial_elo: 1200.0
```

```mermaid
flowchart TD
    CONFIG["config/poca/SoccerTwos.yaml"] --> TRAIN["mlagents-learn Training Process"]
    TRAIN --> MODEL["Trained Agent Model"]
    MODEL --> HF["Push to Hugging Face Hub"]
    HF --> AIAI["AI vs. AI Challenge"]
    
    subgraph "Training Components"
        POCA["MA-POCA for Team Cooperation"]
        SP["Self-Play for Competition"]
        ST["SoccerTwos Environment"]
    end
    
    TRAIN --> POCA
    TRAIN --> SP
    TRAIN --> ST
```

Sources: units/en/unit7/hands-on.mdx

### Training Process
1. Configure the hyperparameters in the YAML file
2. Run training using ML-Agents:
   ```bash
   mlagents-learn ./config/poca/SoccerTwos.yaml --env=./training-envs-executables/SoccerTwos --run-id="SoccerTwos" --no-graphics
   ```
3. Training typically takes 5-8 hours for 5M timesteps
4. The output is an ONNX model that can be pushed to the Hugging Face Hub

## AI vs. AI Challenge

The course includes an AI vs. AI challenge framework that allows trained agents to compete against each other.

```mermaid
flowchart TD
    MODELS["Model Repository on HF Hub"] --> MATCH["Matchmaking Algorithm"]
    MATCH --> QUEUE["Match Queue"]
    QUEUE --> SIM["Unity Headless Simulation"]
    SIM --> RESULTS["Match Results Dataset"]
    RESULTS --> ELO["ELO Rating Update"]
    ELO --> LEADERBOARD["SoccerTwos Leaderboard"]
    
    MODELS --> DEMO["Interactive Demo Space"]
    LEADERBOARD --> DEMO
```

Sources: units/en/unit7/hands-on.mdx

### How the Challenge Works
1. Every four hours, available models tagged with `ML-Agents-SoccerTwos` are fetched
2. A queue of matches is created using a matchmaking algorithm
3. Matches are simulated and results are recorded (win, loss, or draw)
4. ELO ratings are updated based on match outcomes
5. The leaderboard displays current rankings

Users can visualize matches between different models using an interactive demo space, which provides a way to observe agent behaviors and strategies.

The AI vs. AI framework provides a robust evaluation method by testing agents against a diverse set of opponents, giving a better measure of policy quality than testing against a fixed opponent.

Sources: units/en/unit7/hands-on.mdx

---

