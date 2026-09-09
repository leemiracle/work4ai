> 来源: [https://deepwiki.com/rl-tools/rl-tools/4-environments](https://deepwiki.com/rl-tools/rl-tools/4-environments)
> DeepWiki rl-tools/rl-tools | Last indexed: 2 February 2026 (a0aef4

# Environments

  Relevant source files 
 - [include/rl_tools/rl/algorithms/ppo/loop/core/config.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/algorithms/ppo/loop/core/config.h)
 - [include/rl_tools/rl/algorithms/ppo/loop/core/operations_generic.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/algorithms/ppo/loop/core/operations_generic.h)
 - [include/rl_tools/rl/algorithms/ppo/loop/core/state.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/algorithms/ppo/loop/core/state.h)
 - [include/rl_tools/rl/algorithms/ppo/operations_generic.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/algorithms/ppo/operations_generic.h)
 - [include/rl_tools/rl/algorithms/ppo/ppo.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/algorithms/ppo/ppo.h)
 - [include/rl_tools/rl/components/on_policy_runner/on_policy_runner.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/components/on_policy_runner/on_policy_runner.h)
 - [include/rl_tools/rl/components/on_policy_runner/operations_generic.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/components/on_policy_runner/operations_generic.h)
 - [include/rl_tools/rl/components/on_policy_runner/operations_generic_per_env.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/components/on_policy_runner/operations_generic_per_env.h)
 - [include/rl_tools/rl/components/running_normalizer/running_normalizer.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/components/running_normalizer/running_normalizer.h)
 - [include/rl_tools/rl/environments/l2f/multirotor.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/multirotor.h)
 - [include/rl_tools/rl/environments/l2f/operations_cpu.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/operations_cpu.h)
 - [include/rl_tools/rl/environments/l2f/operations_generic.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/operations_generic.h)
 - [include/rl_tools/rl/environments/l2f/operations_generic/10_sample_initial_parameters.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/operations_generic/10_sample_initial_parameters.h)
 - [include/rl_tools/rl/environments/l2f/operations_generic/30_sample_initial_state.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/operations_generic/30_sample_initial_state.h)
 - [include/rl_tools/rl/environments/l2f/operations_generic/70_post_integration.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/operations_generic/70_post_integration.h)
 - [include/rl_tools/rl/environments/l2f/operations_multitask_generic.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/operations_multitask_generic.h)
 - [include/rl_tools/rl/environments/l2f/operations_multitask_generic_forward.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/operations_multitask_generic_forward.h)
 - [include/rl_tools/rl/environments/l2f/parameters/default.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/parameters/default.h)
 - [include/rl_tools/rl/environments/l2f/parameters/trajectories/lissajous.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/parameters/trajectories/lissajous.h)
 - [src/rl/environments/pendulum/ppo/cpu/CMakeLists.txt](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/pendulum/ppo/cpu/CMakeLists.txt)
 - [src/rl/environments/pendulum/ppo/cpu/config.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/pendulum/ppo/cpu/config.h)
 - [src/rl/environments/pendulum/ppo/cpu/training.cpp](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/pendulum/ppo/cpu/training.cpp)
 - [src/rl/environments/pendulum/ppo/cuda/CMakeLists.txt](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/pendulum/ppo/cuda/CMakeLists.txt)
 - [src/rl/environments/pendulum/ppo/cuda/training.cu](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/pendulum/ppo/cuda/training.cu)
 - [src/rl/zoo/l2f/environment.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/l2f/environment.h)
 - [src/rl/zoo/l2f/environment_big.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/l2f/environment_big.h)
 - [src/rl/zoo/l2f/ppo.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/l2f/ppo.h)
 - [src/rl/zoo/l2f/sac_big.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/l2f/sac_big.h)
 
  This page documents the reinforcement learning environments available in RLtools, their interfaces, and how to create custom environments. Environments provide the simulated worlds where RL agents learn to perform tasks through interaction.

 For information about RL algorithms that train on these environments, see [Reinforcement Learning Algorithms](https://deepwiki.com/rl-tools/rl-tools/2-reinforcement-learning-algorithms). For neural network components used in environment observation processing, see [Neural Network Components](https://deepwiki.com/rl-tools/rl-tools/3-neural-network-components).

 
## Available Environments

 RLtools provides several built-in environments for different types of learning tasks:

 
```

```

 Sources: [CMakeLists.txt37](https://github.com/rl-tools/rl-tools/blob/a0aef476/CMakeLists.txt#L37-L37) [include/rl_tools/rl/environments/l2f/multirotor.h449-503](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/multirotor.h#L449-L503) [src/rl/environments/pendulum/td3/cpu/CMakeLists.txt1-76](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/pendulum/td3/cpu/CMakeLists.txt#L1-L76) [src/rl/environments/mujoco/ant/CMakeLists.txt1-36](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/mujoco/ant/CMakeLists.txt#L1-L36)

 
## Environment Interface

 All RLtools environments implement a common interface through template specialization and operation overloading. Environments use a specification pattern where the `SPEC` template parameter defines types and constants.

 
### Core Operations

 The environment interface consists of these fundamental operations defined in [include/rl_tools/rl/environments/l2f/operations_generic.h38-169](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/operations_generic.h#L38-L169):

 
| Operation | Signature | Description |
|---|---|---|
| malloc | malloc(DEVICE&, Multirotor<SPEC>&) | Allocates dynamic memory for environment |
| free | free(DEVICE&, Multirotor<SPEC>&) | Deallocates environment memory |
| init | init(DEVICE&, Multirotor<SPEC>&) | Initializes environment with default parameters |
| sample_initial_parameters | sample_initial_parameters(DEVICE&, Multirotor<SPEC>&, PARAMETERS&, RNG&) | Samples randomized dynamics parameters |
| sample_initial_state | sample_initial_state(DEVICE&, Multirotor<SPEC>&, PARAMETERS&, STATE&, RNG&) | Samples random initial state |
| step | step(DEVICE&, Multirotor<SPEC>&, PARAMETERS&, STATE&, Matrix<ACTION_SPEC>&, STATE&, RNG&) -> T | Advances simulation by one timestep using RK4 integration |
| observe | observe(DEVICE&, Multirotor<SPEC>&, PARAMETERS&, STATE&, OBSERVATION&, Matrix<OBS_SPEC>&, RNG&) | Generates observations from current state |
| reward | reward(DEVICE&, Multirotor<SPEC>&, PARAMETERS&, STATE&, Matrix<ACTION_SPEC>&, STATE&, RNG&) -> T | Computes reward signal |
| terminated | terminated(DEVICE&, Multirotor<SPEC>&, PARAMETERS&, STATE&, RNG&) -> bool | Checks if episode should terminate |

 
### Environment Specification Pattern

 
```

```

 The `step` function uses RK4 integration [include/rl_tools/rl/environments/l2f/operations_generic.h95-130](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/operations_generic.h#L95-L130) with support for multiple substeps. Actions are scaled from normalized range [-1, 1] to the dynamics-specific action limits [include/rl_tools/rl/environments/l2f/operations_generic.h104-110](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/operations_generic.h#L104-L110)

 Sources: [include/rl_tools/rl/environments/l2f/operations_generic.h38-169](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/operations_generic.h#L38-L169) [include/rl_tools/rl/environments/l2f/multirotor.h14-221](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/multirotor.h#L14-L221) </old_str>

 <new_str>

 
## L2F (Learn to Fly) Environment

 The L2F environment (`rl::environments::Multirotor<SPEC>`) provides a sophisticated multirotor drone simulation with complex state representation, configurable dynamics, and advanced features like domain randomization and trajectory tracking. It is defined in [include/rl_tools/rl/environments/l2f/multirotor.h1-850](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/multirotor.h#L1-L850)

 
### State Representation

 The L2F environment uses a composable state system where components are chained using a linked-list pattern through the `NEXT_COMPONENT` template parameter.

 
#### Base State Components

 
```

```

 Each state component implements:

 
 - `initial_state()`: Sets default values [include/rl_tools/rl/environments/l2f/operations_generic/20_initial_state.h1-200](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/operations_generic/20_initial_state.h#L1-L200)
 - `_sample_initial_state()`: Randomizes initial values [include/rl_tools/rl/environments/l2f/operations_generic/30_sample_initial_state.h1-250](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/operations_generic/30_sample_initial_state.h#L1-L250)
 - `post_integration()`: Updates non-integrated components after physics step [include/rl_tools/rl/environments/l2f/operations_generic/70_post_integration.h1-200](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/operations_generic/70_post_integration.h#L1-L200)
 
 The `StateBase` contains the 13-dimensional continuous state integrated via RK4, while other components like `StateLastAction` and `StateRotorsHistory` are updated discretely in `post_integration()`.

 Sources: [include/rl_tools/rl/environments/l2f/multirotor.h624-850](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/multirotor.h#L624-L850) [include/rl_tools/rl/environments/l2f/operations_generic/70_post_integration.h20-149](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/operations_generic/70_post_integration.h#L20-L149)

 
### Observation Composition System

 The observation system uses a linked-list pattern enabling flexible, composable observations. Each observation component defines its `CURRENT_DIM` and chains to a `NEXT_COMPONENT`.

 
#### Available Observation Components

 
| Component | Class | Dimensions | Description |
|---|---|---|---|
| Position | observation::Position<SPEC> | 3 | Drone position (x, y, z) |
| Orientation (Quaternion) | observation::OrientationQuaternion<SPEC> | 4 | Orientation as quaternion |
| Orientation (Rotation Matrix) | observation::OrientationRotationMatrix<SPEC> | 9 | Orientation as 3×3 rotation matrix |
| Linear Velocity | observation::LinearVelocity<SPEC> | 3 | Body-frame linear velocity |
| Angular Velocity | observation::AngularVelocity<SPEC> | 3 | Body-frame angular velocity |
| Angular Velocity (Delayed) | observation::AngularVelocityDelayed<SPEC> | 3 | Delayed angular velocity for sensor lag |
| IMU Accelerometer | observation::IMUAccelerometer<SPEC> | 3 | Simulated IMU acceleration |
| Action History | observation::ActionHistory<SPEC> | 4×HISTORY_LENGTH | Previous actions for Markovification |
| Rotor Speeds | observation::RotorSpeeds<SPEC> | 4 | Current RPM values (privileged) |
| Random Force | observation::RandomForce<SPEC> | 6 | Applied disturbance forces/torques (privileged) |
| Trajectory Tracking Position | observation::TrajectoryTrackingPosition<SPEC> | 3 | Position error from trajectory |
| Trajectory Tracking Velocity | observation::TrajectoryTrackingLinearVelocity<SPEC> | 3 | Velocity error from trajectory |

 
```

```

 The observation is computed recursively in [include/rl_tools/rl/environments/l2f/operations_generic/40_observe.h1-500](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/operations_generic/40_observe.h#L1-L500) Each component calls `_observe()` on itself, then dispatches to the next component.

 **Privileged observations** (for asymmetric actor-critic) include additional information like rotor speeds and disturbance forces that would not be available to a real robot.

 Sources: [include/rl_tools/rl/environments/l2f/multirotor.h236-615](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/multirotor.h#L236-L615) [include/rl_tools/rl/environments/l2f/operations_cpu.h16-135](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/operations_cpu.h#L16-L135) [src/rl/zoo/l2f/environment.h141-151](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/l2f/environment.h#L141-L151)

 
### Dynamics Models and Registry

 The environment supports multiple quadrotor configurations through a dynamics registry in [include/rl_tools/rl/environments/l2f/parameters/dynamics/registry.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/parameters/dynamics/registry.h)

 
#### Dynamics Parameters

 The `parameters::Dynamics<T, TI, N>` structure defines [include/rl_tools/rl/environments/l2f/multirotor.h25-44](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/multirotor.h#L25-L44):

 
```
struct Dynamics {
    T rotor_positions[N][3];              // Rotor positions in body frame
    T rotor_thrust_directions[N][3];      // Thrust direction unit vectors
    T rotor_torque_directions[N][3];      // Torque direction unit vectors  
    T rotor_thrust_coefficients[N][3];    // Quadratic thrust curve coefficients
    T rotor_torque_constants[N];          // Torque coefficient for each rotor
    T rotor_time_constants_rising[N];     // Motor spool-up time constant
    T rotor_time_constants_falling[N];    // Motor spool-down time constant
    T mass;                                // Total mass
    T gravity[3];                          // Gravity vector
    T J[3][3];                            // Inertia tensor
    T J_inv[3][3];                        // Inverse inertia tensor
    T hovering_throttle_relative;         // Hovering throttle [0,1]
    ActionLimit action_limit;             // Min/max action values
}
```

 
#### Pre-defined Models

 The registry provides models accessed via `parameters::dynamics::registry<MODEL, SPEC>`:

 
| Model Enum | Description | Use Case |
|---|---|---|
| REGISTRY::crazyflie | Bitcraze Crazyflie 2.x | Micro quadrotor, research |
| REGISTRY::x500_sim | PX4 X500 (simulation) | Mid-size quadrotor simulation |
| REGISTRY::x500_real | PX4 X500 (real-world) | Real hardware deployment |
| REGISTRY::arpl_vision | ARPL vision-based model | Vision-based control |
| REGISTRY::race | Racing quadrotor | Aggressive flight |
| REGISTRY::soft_rigid | Soft/rigid mixed dynamics | Research configurations |

 Models can be rotated/remapped using `permute_rotors()` [include/rl_tools/rl/environments/l2f/operations_generic.h47-64](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/operations_generic.h#L47-L64) for motor randomization.

 Sources: [include/rl_tools/rl/environments/l2f/multirotor.h25-44](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/multirotor.h#L25-L44) [src/rl/zoo/l2f/environment_big.h23-24](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/l2f/environment_big.h#L23-L24) [include/rl_tools/rl/environments/l2f/operations_generic.h47-64](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/operations_generic.h#L47-L64)

 
### Domain Randomization

 Domain randomization is controlled by `ParametersDomainRandomization<SPEC>` and sampled in `sample_initial_parameters()` [include/rl_tools/rl/environments/l2f/operations_generic/10_sample_initial_parameters.h36-195](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/operations_generic/10_sample_initial_parameters.h#L36-L195)

 
#### Randomization Parameters

 
```

```

 The randomization process [include/rl_tools/rl/environments/l2f/operations_generic/10_sample_initial_parameters.h54-195](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/operations_generic/10_sample_initial_parameters.h#L54-L195):

 
 - **Thrust-to-Weight**: Directly scales thrust coefficients to achieve desired ratio
 - **Mass**: Sampled uniformly in size (∛mass) to avoid bias toward large quadrotors
 - **Torque-to-Inertia**: Controls rotational agility by adjusting inertia tensor
 - **Size Deviation**: Scales rotor positions independently of mass for varied geometries
 - **Motor Dynamics**: Randomizes first-order motor response time constants
 
 Each parameter can be independently enabled/disabled via `DOMAIN_RANDOMIZATION_OPTIONS` compile-time flags.

 Sources: [include/rl_tools/rl/environments/l2f/operations_generic/10_sample_initial_parameters.h36-195](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/operations_generic/10_sample_initial_parameters.h#L36-L195) [include/rl_tools/rl/environments/l2f/multirotor.h106-127](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/multirotor.h#L106-L127)

 
### Trajectory Tracking

 The environment supports reference trajectory tracking through `StateTrajectory<SPEC>` and `ParametersTrajectory<SPEC>`.

 
#### Trajectory Definition

 Trajectories are pre-computed arrays of `Step<T>` waypoints [include/rl_tools/rl/environments/l2f/parameters/trajectories/trajectory.h9-27](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/parameters/trajectories/trajectory.h#L9-L27):

 
```
struct Step {
    T position[3];           // Desired position
    T yaw;                   // Desired yaw angle
    T linear_velocity[3];    // Desired velocity
    T yaw_velocity;          // Desired yaw rate
}

struct Trajectory {
    Step steps[LENGTH];
}
```

 Trajectories are evaluated at the current timestep to provide desired state in `get_desired_state()` [include/rl_tools/rl/environments/l2f/operations_generic/35_get_desired_state.h1-100](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/operations_generic/35_get_desired_state.h#L1-L100)

 
#### Lissajous Curves

 The primary trajectory type is Lissajous curves [include/rl_tools/rl/environments/l2f/parameters/trajectories/lissajous.h12-60](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/parameters/trajectories/lissajous.h#L12-L60):

 
```
struct Parameters {
    T A, B, C;           // Amplitudes in x, y, z
    T a, b, c;           // Frequency ratios
    T interval;          // Total period duration
    T ramp_duration;     // Initial ramp-up time
}
```

 Position: `[A·sin(a·ω·t), B·sin(b·ω·t), C·sin(c·ω·t)]` where `ω = 2π/interval`

 Default parameters generate a figure-8 pattern in the xy-plane:

 
 - A=0.5, B=1.0, C=0.0 (no z motion)
 - a=2.0, b=1.0 (2:1 frequency ratio)
 - interval=6.5 seconds
 
 The trajectory is pre-computed during initialization via `fill(device, params, trajectory, rng)` [include/rl_tools/rl/environments/l2f/parameters/trajectories/lissajous.h62-68](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/parameters/trajectories/lissajous.h#L62-L68)

 **Observation Components for Tracking:**

 
 - `observation::TrajectoryTrackingPosition`: Position error (current - desired)
 - `observation::TrajectoryTrackingLinearVelocity`: Velocity error
 - `observation::TrajectoryTrackingLookahead`: Future waypoints for prediction
 
 Sources: [include/rl_tools/rl/environments/l2f/parameters/trajectories/lissajous.h12-68](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/parameters/trajectories/lissajous.h#L12-L68) [include/rl_tools/rl/environments/l2f/operations_generic/35_get_desired_state.h1-100](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/operations_generic/35_get_desired_state.h#L1-L100) [include/rl_tools/rl/environments/l2f/multirotor.h189-206](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/multirotor.h#L189-L206)

 
### Reward Functions

 Reward functions are implemented as composable functors in [include/rl_tools/rl/environments/l2f/parameters/reward_functions/](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/parameters/reward_functions/)

 
#### Squared Reward Function

 The primary reward function is `reward_functions::Squared<T>` [include/rl_tools/rl/environments/l2f/parameters/reward_functions/squared/operations_generic.h1-150](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/parameters/reward_functions/squared/operations_generic.h#L1-L150):

 
```
struct Squared {
    bool non_negative;
    T scale;
    T constant;
    T termination_penalty;
    T position;                    // Weight for position error²
    T position_clip;               // Clipping threshold
    T orientation;                 // Weight for orientation error²
    T linear_velocity;             // Weight for velocity error²
    T angular_velocity;            // Weight for angular velocity²
    T linear_acceleration;         // Weight for acceleration²
    T angular_acceleration;        // Weight for angular acceleration²
    T action;                      // Weight for action magnitude²
    T d_action;                    // Weight for action change²
    T position_error_integral;     // Weight for integral error
}
```

 The reward is computed as:

 
```
reward = scale * (constant 
    - position_weight * ||pos_error||²
    - orientation_weight * ||orient_error||²
    - linear_velocity_weight * ||vel_error||²
    - ...
    - d_action_weight * ||action_t - action_{t-1}||²
) + termination_penalty (if terminated)
```

 The squared terms naturally provide stronger penalties for larger errors while keeping derivatives smooth for gradient-based learning.

 Sources: [include/rl_tools/rl/environments/l2f/parameters/reward_functions/squared/operations_generic.h1-150](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/parameters/reward_functions/squared/operations_generic.h#L1-L150) [src/rl/zoo/l2f/environment.h26-41](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/l2f/environment.h#L26-L41)

 
### Integration with Training

 The L2F environment integrates with training loops through the `OnPolicyRunner` (for PPO) or `OffPolicyRunner` (for SAC/TD3).

 
```

```

 See [src/rl/zoo/l2f/environment.h18-162](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/l2f/environment.h#L18-L162) for environment factory configuration and [src/rl/zoo/l2f/sac_big.h1-81](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/l2f/sac_big.h#L1-L81) [src/rl/zoo/l2f/ppo.h1-53](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/l2f/ppo.h#L1-L53) for algorithm-specific configurations.

 Sources: [src/rl/zoo/l2f/environment.h18-162](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/l2f/environment.h#L18-L162) [src/rl/zoo/l2f/sac_big.h18-78](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/l2f/sac_big.h#L18-L78) [src/rl/zoo/l2f/ppo.h23-49](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/l2f/ppo.h#L23-L49) [include/rl_tools/rl/components/on_policy_runner/operations_generic_per_env.h8-76](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/components/on_policy_runner/operations_generic_per_env.h#L8-L76)

 
## Pendulum Environment

 The pendulum environment (`rl::environments::Pendulum<SPEC>`) implements the classic inverted pendulum control problem with continuous control. It serves as a simple testbed for RL algorithms.

 
### Environment Properties

 
| Property | Value | Description |
|---|---|---|
| State | {angle, angular_velocity} | 2D continuous state |
| Action | {torque} | 1D continuous control |
| Observation | {cos(angle), sin(angle), angular_velocity} | 3D observation vector |
| Episode Limit | 200 steps | Maximum episode length |

 The environment is integrated with:

 
 - **TD3**: [src/rl/environments/pendulum/td3/cpu/CMakeLists.txt16-26](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/pendulum/td3/cpu/CMakeLists.txt#L16-L26)
 - **SAC**: [src/rl/environments/pendulum/sac/cpu/CMakeLists.txt5-18](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/pendulum/sac/cpu/CMakeLists.txt#L5-L18)
 - **PPO**: [src/rl/environments/pendulum/ppo/cpu/CMakeLists.txt8-10](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/pendulum/ppo/cpu/CMakeLists.txt#L8-L10)
 
 PPO configuration for Pendulum [src/rl/environments/pendulum/ppo/cpu/config.h1-45](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/pendulum/ppo/cpu/config.h#L1-L45):

 
```
LOOP_CORE_PARAMETERS:
    BATCH_SIZE = 256
    ACTOR_HIDDEN_DIM = 64
    CRITIC_HIDDEN_DIM = 64
    ON_POLICY_RUNNER_STEPS_PER_ENV = 1024
    N_ENVIRONMENTS = 4
    EPISODE_STEP_LIMIT = 200
    
PPO_PARAMETERS:
    ACTION_ENTROPY_COEFFICIENT = 0.0
    N_EPOCHS = 2
    GAMMA = 0.9
    INITIAL_ACTION_STD = 2.0
```

 The Pendulum environment also demonstrates:

 
 - Observation scaling wrapper (`rl::environment_wrappers::ScaleObservations`) [src/rl/environments/pendulum/ppo/cpu/config.h8-9](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/pendulum/ppo/cpu/config.h#L8-L9)
 - Static memory allocation for embedded deployment [src/rl/environments/pendulum/ppo/cpu/CMakeLists.txt2-6](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/pendulum/ppo/cpu/CMakeLists.txt#L2-L6)
 - CUDA implementation [src/rl/environments/pendulum/ppo/cuda/training.cu1-114](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/pendulum/ppo/cuda/training.cu#L1-L114)
 
 Sources: [src/rl/environments/pendulum/ppo/cpu/config.h1-45](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/pendulum/ppo/cpu/config.h#L1-L45) [src/rl/environments/pendulum/ppo/cpu/CMakeLists.txt1-17](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/pendulum/ppo/cpu/CMakeLists.txt#L1-L17) [src/rl/environments/pendulum/ppo/cuda/training.cu32-42](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/pendulum/ppo/cuda/training.cu#L32-L42)

 
## L2F (Learn to Fly) Environment

 The L2F environment provides a sophisticated multirotor drone simulation with complex state representation and configurable dynamics:

 
## MuJoCo Integration

 RLtools integrates with the MuJoCo physics engine for complex robotics simulations:

 
```

```

 The MuJoCo integration requires the `RL_TOOLS_RL_ENVIRONMENTS_ENABLE_MUJOCO` CMake option and supports both CPU and CUDA implementations.

 Sources: [CMakeLists.txt186-223](https://github.com/rl-tools/rl-tools/blob/a0aef476/CMakeLists.txt#L186-L223) [src/rl/environments/mujoco/ant/ppo/cpu/CMakeLists.txt1-54](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/mujoco/ant/ppo/cpu/CMakeLists.txt#L1-L54) [src/rl/environments/mujoco/ant/ppo/cuda/CMakeLists.txt1-103](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/mujoco/ant/ppo/cuda/CMakeLists.txt#L1-L103)

 
## Creating Custom Environments

 To create a custom environment, implement the required operations for your environment type:

 
```

```

 The environment must define template specializations for all required operations and provide the necessary type definitions and constants.

 Sources: [include/rl_tools/rl/environments/l2f/operations_generic.h262-287](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/operations_generic.h#L262-L287) [include/rl_tools/rl/environments/l2f/multirotor.h449-503](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/environments/l2f/multirotor.h#L449-L503)
