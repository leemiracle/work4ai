> 来源: [https://deepwiki.com/kscalelabs/ksim/4-example-implementations](https://deepwiki.com/kscalelabs/ksim/4-example-implementations)
> DeepWiki kscalelabs/ksim | Last indexed: 18 May 2025 (9d2640

# Example Implementations

  Relevant source files 
 - [README.md](https://github.com/kscalelabs/ksim/blob/9d26400d/README.md?plain=1)
 - [examples/standing.py](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/standing.py)
 - [examples/walking.py](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking.py)
 - [examples/walking_amp.py](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking_amp.py)
 - [examples/walking_reference_motion.py](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking_reference_motion.py)
 - [examples/walking_rnn.py](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking_rnn.py)
 
  This document provides an overview of the example implementations provided with KSIM. These examples demonstrate how to create practical reinforcement learning tasks using the framework and serve as templates for creating your own custom tasks. For information about the core reinforcement learning framework that underpins these examples, see [Core RL Framework](https://deepwiki.com/kscalelabs/ksim/2-core-rl-framework).

 
## Overview of Example Implementations

 KSIM includes several example implementations that showcase different approaches to controlling a humanoid character:

 
 - **Basic Walking Task** - A foundation implementation using feedforward neural networks
 - **RNN-based Walking Task** - An extension using recurrent neural networks to maintain state
 - **AMP-based Walking Task** - An implementation incorporating Adversarial Motion Priors
 - **Reference Motion Walking Task** - A task that demonstrates motion tracking from reference data
 - **Standing Task** - A simplified task derived from the walking task
 
 
```

```

 **Example Task Hierarchy**

 Sources:

 
 - [examples/walking.py225-490](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking.py#L225-L490)
 - [examples/walking_rnn.py211-383](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking_rnn.py#L211-L383)
 - [examples/walking_amp.py388-732](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking_amp.py#L388-L732)
 - [examples/walking_reference_motion.py143-207](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking_reference_motion.py#L143-L207)
 - [examples/standing.py20-26](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/standing.py#L20-L26)
 
 
## Basic Walking Task

 The `HumanoidWalkingTask` serves as the foundation for most example implementations. It demonstrates how to create a complete reinforcement learning task for training a humanoid to walk using the KSIM framework.

 
### Task Structure

 
```

```

 **Walking Task Structure**

 Sources:

 
 - [examples/walking.py225-366](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking.py#L225-L366)
 - [examples/walking.py47-100](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking.py#L47-L100)
 - [examples/walking.py103-128](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking.py#L103-L128)
 
 
### Model Architecture

 The basic walking task uses a feedforward neural network architecture with a mixture of Gaussians action distribution. This provides a flexible policy that can model multi-modal action distributions.

 
```

```

 **Actor Model Architecture**

 Sources:

 
 - [examples/walking.py48-100](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking.py#L48-L100)
 - [examples/walking.py379-419](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking.py#L379-L419)
 
 
### Key Components

 The basic walking task implementation defines:

 
 - **Physics Model**: Uses a MuJoCo model specified in `scene.mjcf`
 - **Actuators**: Position-based actuators to control the humanoid's joints
 - **Observations**: Extensive set of observations including joint positions, velocities, IMU data, etc.
 - **Commands**: Joystick commands for directional control
 - **Rewards**: Stay alive reward and joystick reward for directional movement
 - **Terminations**: Conditions such as falling, leaving the area, or excessive speeds
 - **Curriculum**: Episode length curriculum that gradually increases difficulty
 
 The task provides a complete setup for training a humanoid to walk in any direction based on joystick commands.

 **Code Structure:**

 
 - `get_mujoco_model()`: Loads the MuJoCo model
 - `get_actuators()`: Defines position actuators for joint control
 - `get_observations()`: Sets up a comprehensive observation space
 - `get_commands()`: Creates a joystick command system
 - `get_rewards()`: Configures task rewards
 - `get_terminations()`: Defines episode termination conditions
 - `get_curriculum()`: Establishes a curriculum learning strategy
 - `get_model()`: Creates the policy network architecture
 - `run_actor()` & `run_critic()`: Process observations into actions and value estimates
 - `sample_action()`: Samples actions from the policy during rollouts
 
 Sources:

 
 - [examples/walking.py225-508](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking.py#L225-L508)
 
 
## RNN-based Walking Task

 The `HumanoidWalkingRNNTask` extends the basic walking task to use recurrent neural networks. This allows the policy to maintain internal state and better handle sequential decision-making.

 
### Key Differences

 The main differences from the basic walking task are:

 
 - **Model Architecture**: Uses GRU cells instead of a simple MLP
 - **State Management**: Maintains and updates hidden state across time steps
 - **Action Sampling**: Preserves hidden state between steps during rollouts
 
 
```

```

 **RNN Actor Architecture**

 Sources:

 
 - [examples/walking_rnn.py25-109](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking_rnn.py#L25-L109)
 - [examples/walking_rnn.py224-266](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking_rnn.py#L224-L266)
 
 
### Implementation Details

 The RNN implementation adds:

 
 - `get_initial_model_carry()`: Initializes the hidden state for the RNN
 - Updated `run_actor()` and `run_critic()`: Handle the hidden state input and output
 - Modified `sample_action()`: Preserves the hidden state between steps
 - Enhanced `get_ppo_variables()`: Processes the hidden state through time
 
 This task demonstrates how to incorporate recurrent models into the KSIM framework, enabling policies with memory.

 Sources:

 
 - [examples/walking_rnn.py310-353](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking_rnn.py#L310-L353)
 - [examples/walking_rnn.py360-383](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking_rnn.py#L360-L383)
 
 
## AMP-based Walking Task

 The `HumanoidWalkingAMPTask` implements Adversarial Motion Priors (AMP), a technique that uses a discriminator to encourage realistic motion based on reference data.

 
### Architecture Overview

 
```

```

 **AMP Architecture**

 Sources:

 
 - [examples/walking_amp.py42-120](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking_amp.py#L42-L120)
 - [examples/walking_amp.py214-265](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking_amp.py#L214-L265)
 - [examples/walking_amp.py388-567](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking_amp.py#L388-L567)
 
 
### Key Components

 The AMP implementation adds:

 
 - **Discriminator Model**: A convolutional network that distinguishes between real and generated motions
 - **Reference Motion**: Motion capture data loaded from file
 - **AMP Reward**: Reward based on the discriminator's ability to distinguish the policy's motion
 - **Motion Conversion**: Functions to convert between trajectory and motion representations
 
 This task demonstrates:

 
 - How to incorporate reference motion data
 - How to implement adversarial training within KSIM
 - How to build a motion discriminator
 
 Sources:

 
 - [examples/walking_amp.py566-583](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking_amp.py#L566-L583)
 - [examples/walking_amp.py502-508](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking_amp.py#L502-L508)
 - [examples/walking_amp.py532-574](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking_amp.py#L532-L574)
 
 
## Reference Motion Walking Task

 The `HumanoidWalkingReferenceMotionTask` demonstrates how to track specific reference motion data, such as from BVH files, without using adversarial training.

 
### Key Features

 This implementation focuses on:

 
 - **Loading and Processing BVH files**: Converting motion capture data to a format usable in MuJoCo
 - **Reference Motion Reward**: Direct reward based on matching joint positions to reference
 - **Visualization Tools**: Utilities to visualize reference points and motions
 
 
```

```

 **Reference Motion Pipeline**

 Sources:

 
 - [examples/walking_reference_motion.py123-140](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking_reference_motion.py#L123-L140)
 - [examples/walking_reference_motion.py143-207](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking_reference_motion.py#L143-L207)
 
 
### Implementation Details

 The reference motion task includes:

 
 - `QposReferenceMotionReward`: A reward function that measures similarity to reference poses
 - `generate_reference_motion()`: Utility to convert BVH data to reference motion
 - Visualization functions for debugging and analysis
 
 This example is useful for tasks where precise motion matching is required, such as animation and character control.

 Sources:

 
 - [examples/walking_reference_motion.py123-140](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking_reference_motion.py#L123-L140)
 - [examples/walking_reference_motion.py170-189](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking_reference_motion.py#L170-L189)
 
 
## Other Example Tasks

 
### Standing Task

 The `HumanoidStandingTask` provides a simplified example that focuses on maintaining a standing posture rather than walking.

 The key difference is in the reward function, which rewards maintaining the humanoid's height within a specific range:

 
```

```

 This demonstrates how to easily create new tasks by extending existing ones and customizing specific components.

 Sources:

 
 - [examples/standing.py20-26](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/standing.py#L20-L26)
 
 
## Running the Examples

 All example implementations include a standardized way to launch them:

 
```

```

 This pattern makes it easy to either train policies or visualize their behavior. The examples also support command-line configuration overrides to customize parameters without modifying the code.

 
### Example Run Commands

 
| Task | Training Command | Visualization Command |
|---|---|---|
| Basic Walking | python -m examples.walking | python -m examples.walking run_mode=view |
| RNN Walking | python -m examples.walking_rnn | python -m examples.walking_rnn run_mode=view |
| AMP Walking | python -m examples.walking_amp | python -m examples.walking_amp run_mode=view |
| Reference Motion | python -m examples.walking_reference_motion | python -m examples.walking_reference_motion run_mode=view |
| Standing | python -m examples.standing | python -m examples.standing run_mode=view |

 For systems with limited memory, most examples provide specific instructions for reducing resource usage:

 
```

```

 Sources:

 
 - [examples/walking.py510-540](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking.py#L510-L540)
 - [examples/walking_rnn.py386-406](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking_rnn.py#L386-L406)
 - [examples/walking_amp.py735-770](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking_amp.py#L735-L770)
 - [examples/walking_reference_motion.py210-246](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking_reference_motion.py#L210-L246)
 - [examples/standing.py28-47](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/standing.py#L28-L47)
 
 
## Common Patterns and Customization

 
### Task Configuration

 All examples follow a consistent pattern for configuration using dataclasses:

 
```

```

 **Configuration Hierarchy**

 Sources:

 
 - [examples/walking.py159-206](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking.py#L159-L206)
 - [examples/walking_rnn.py203-204](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking_rnn.py#L203-L204)
 - [examples/walking_amp.py268-365](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking_amp.py#L268-L365)
 - [examples/walking_reference_motion.py42-74](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking_reference_motion.py#L42-L74)
 
 
### Customization Points

 The examples demonstrate several key customization points:

 
 - **Reward Functions**: Define task objectives
 - **Model Architectures**: Determine policy structure and capabilities
 - **Observations and Commands**: Control agent inputs
 - **Termination Conditions**: Define episode endings
 - **Physics Parameters**: Control simulation properties
 - **Curriculum Learning**: Manage task difficulty progression
 
 These customization points allow researchers and developers to adapt the examples to new scenarios while leveraging the structured KSIM framework.

 Sources:

 
 - [examples/walking.py342-366](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking.py#L342-L366)
 - [examples/walking_rnn.py212-222](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking_rnn.py#L212-L222)
 - [examples/walking_amp.py502-516](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/walking_amp.py#L502-L516)
 - [examples/standing.py21-25](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/standing.py#L21-L25)
 
 
## Conclusion

 The example implementations provided with KSIM demonstrate a range of approaches to reinforcement learning for robotic control, from basic walking to advanced motion matching. These examples serve as both educational resources and starting points for custom implementations.

 By studying these examples, users can understand how to:

 
 - Structure reinforcement learning tasks in KSIM
 - Implement different model architectures
 - Define custom rewards and termination conditions
 - Incorporate reference motion data
 - Leverage curriculum learning and domain randomization
 
 For more advanced applications, users can combine elements from different examples or extend them with new components to address specific research or application needs.
