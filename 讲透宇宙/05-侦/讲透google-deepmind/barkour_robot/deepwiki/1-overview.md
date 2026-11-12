<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/barkour_robot · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

The Barkour Robot is an agile quadruped robot platform developed by Google DeepMind to support various research projects. This wiki provides comprehensive documentation of the robot's design, assembly, software, and usage. This overview page introduces the Barkour Robot project at a high level, describing its purpose, main components, and the structure of the repository.

For specific guidance on using the robot, see [Getting Started](#1.1). For information about different robot configurations, see [Versions and Variants](#1.2).

Sources: [README.md:3-8]()

## System Architecture

The Barkour Robot system consists of three primary components: hardware design, embedded software, and simulation environments. These components work together to provide a complete platform for robotics research.

```mermaid
graph TD
    subgraph "Barkour Robot System"
        Hardware["Hardware Design"] --- Software["Embedded Software"]
        Hardware --- Simulation["Simulation"]
        Software --- Simulation
    end
    
    subgraph "Hardware Design"
        CAD["CAD Models"]
        PCBA["PCBA Designs"]
        Assembly["Assembly Instructions"]
        Cables["Cable Drawings"]
    end
    
    subgraph "Embedded Software"
        Firmware["Actuator Firmware"]
        EtherCAT["EtherCAT Configuration"]
        MotorControl["Motor Control"]
    end
    
    subgraph "Simulation"
        MuJoCo["MuJoCo Model"]
        MJX["MJX Training"]
    end
    
    Hardware --> CAD
    Hardware --> PCBA
    Hardware --> Assembly
    Hardware --> Cables
    
    Software --> Firmware
    Software --> EtherCAT
    Software --> MotorControl
    
    Simulation --> MuJoCo
    Simulation --> MJX
```

The system architecture illustrates how the hardware design, embedded software, and simulation environments interact. The hardware design includes CAD models, PCB designs, assembly instructions, and cable drawings. The embedded software includes actuator firmware, EtherCAT configuration, and motor control code. The simulation environments include MuJoCo models and MJX training capabilities.

Sources: [README.md:12-42](), [README.md:101-108]()

## Hardware Components

The Barkour Robot features a modular design with custom motor drivers, actuators, and mechanical components. The robot is available in two variants: one with a fixed head and one with an actuated head that includes a gripper.

```mermaid
graph TD
    subgraph "Barkour Hardware"
        MainBoard["Holberton Main Board"]
        ChildBoard["Holberton Child Board"]
        Actuators["Actuators"]
        Chassis["Chassis Components"]
        Head["Robot Head"]
    end
    
    MainBoard -->|"Mezzanine Connector"| ChildBoard
    MainBoard -->|"EtherCAT"| Host["Host Computer"]
    ChildBoard -->|"Motor Control"| Actuators
    Actuators -->|"Mechanical Power"| Chassis
    
    subgraph "Main Board Components"
        Processor["STM32H755 Dual-Core"]
        EtherCAT_HW["EtherCAT Interface"]
        Power["Power System"]
        IMU["Accelerometer/IMU"]
        Mezzanine["Mezzanine Connector"]
    end
    
    subgraph "Child Board Components"
        MotorDriver["Motor Driver"]
        HBridge["H-Bridge"]
        Feedback["Feedback Circuit"]
        STO["Safe Torque Off"]
    end
    
    MainBoard --> Processor
    MainBoard --> EtherCAT_HW
    MainBoard --> Power
    MainBoard --> IMU
    MainBoard --> Mezzanine
    
    ChildBoard --> MotorDriver
    ChildBoard --> HBridge
    ChildBoard --> Feedback
    ChildBoard --> STO
    
    Head -->|"Two variants: Fixed or Actuated"| Chassis
```

The hardware components diagram shows the relationship between the main hardware elements of the Barkour Robot. The system is built around a main board (Holberton) that connects to child boards for motor control. These boards drive the actuators, which provide mechanical power to the robot chassis. The robot head can be either fixed or actuated depending on the variant.

Sources: [README.md:70-80](), [README.md:45-50]()

## Embedded Software Architecture

The Barkour Robot's embedded software centers around the firmware for the motor drivers, which communicates with a host computer via EtherCAT for real-time control.

```mermaid
graph TD
    subgraph "Firmware Architecture"
        M7["M7 Core @ 480MHz<br>Experimental Use"] --- M4["M4 Core @ 240MHz<br>Motor Control"]
        SRAM4["SRAM4 - Shared Memory"]
        M7 <--> SRAM4
        M4 <--> SRAM4
    end
    
    subgraph "Motor Control System"
        EtherCAT_FW["actuator/firmware/ethercat/*"]
        MotorDrive["actuator/firmware/motor/*"]
        Calibration["actuator/firmware/calibration/*"]
        SafetyFeatures["actuator/firmware/sto/*"]
    end
    
    subgraph "Host Communication"
        HostPC["Host Computer"]
        EtherCATMaster["SOEM EtherCAT Master"]
        ControlSoftware["Motor Control Example"]
    end
    
    M4 --> EtherCAT_FW
    M4 --> MotorDrive
    M4 --> Calibration
    M4 --> SafetyFeatures
    
    HostPC --> EtherCATMaster
    EtherCATMaster -->|"EtherCAT Protocol"| EtherCAT_FW
    HostPC --> ControlSoftware
    ControlSoftware -->|"Motor Control Commands"| EtherCATMaster
```

The firmware architecture diagram illustrates the motor driver's firmware based on the STM32H755 microcontroller with dual-core design. The M4 core handles the motor control processes, including EtherCAT communication, motor drive, calibration, and safety features. The host computer communicates with the motor drivers using the EtherCAT protocol.

Sources: [README.md:103-108]()

## Simulation Environment

The Barkour Robot includes simulation models for the MuJoCo physics engine, supporting both research development and fast training through MJX.

```mermaid
graph LR
    subgraph "Simulation Environment"
        MuJoCoModel["MuJoCo Barkour Model<br>mujoco_menagerie/google_barkour_vb"]
        SimInterface["MuJoCo Interface"]
        MJX["MJX for GPU/TPU Training"]
    end
    
    subgraph "Control Development"
        PolicyDev["Policy Development"]
        ControlTesting["Control Algorithm Testing"]
    end
    
    subgraph "Hardware Interface"
        RealRobot["Physical Barkour Robot"]
        ControlSoftware["Motor Control Software"]
    end
    
    MuJoCoModel --> SimInterface
    SimInterface --> MJX
    
    PolicyDev --> SimInterface
    ControlTesting --> SimInterface
    
    SimInterface -.->|"Transfer Learning"| ControlSoftware
    ControlSoftware --> RealRobot
```

The simulation environment diagram shows how the MuJoCo simulation model interfaces with both control development and the hardware interface. The simulation allows for policy development and control algorithm testing before deployment to the physical robot. MJX provides acceleration for training on GPUs and TPUs.

Sources: [README.md:57-67]()

## Repository Structure

The Barkour Robot repository is organized into several key directories:

| Directory              | Description                                                          |
|------------------------|----------------------------------------------------------------------|
| `docs/`                | Documentation including getting started guides and assembly instructions |
| `actuator/firmware/`   | Embedded firmware for the motor drivers                              |
| `hardware/electronics/` | PCB design files for the custom electronics                         |
| `hardware/cable_drawings/` | Drawings of all custom cable assemblies                           |

Additionally, the repository links to external resources:
- CAD models hosted on Onshape
- MuJoCo simulation models in the MuJoCo Menagerie repository
- MJX tutorial for accelerated training

Sources: [README.md:12-42]()

## Robot Capabilities

The Barkour Robot platform demonstrates impressive capabilities, including:

- Dynamic movements (jumping, running, dancing)
- Environmental interaction and manipulation (with the actuated head variant)
- Robust locomotion on various terrains
- Balance and stability during external disturbances
- Climbing over obstacles
- Following language-based commands

These capabilities make the Barkour Robot a versatile platform for research in areas such as agile locomotion, manipulation, and learning-based control.

Sources: [README.md:110-141]()

## Versions

This repository contains the "vB" version of the Barkour Robot. An older "v0" version was used in earlier work, with assets available through separate links. For more information about the different versions and variants, see [Versions and Variants](#1.2).

Sources: [README.md:131-141]()

---

