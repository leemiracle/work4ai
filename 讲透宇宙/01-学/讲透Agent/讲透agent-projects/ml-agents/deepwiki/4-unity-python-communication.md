<!-- source: DeepWiki mcp.deepwiki.com · repo Unity-Technologies/ml-agents · page 4 Unity-Python Communication · fetched 2026-10-30 -->

# Unity-Python Communication

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [com.unity.ml-agents/Runtime/Communicator/GrpcExtensions.cs](com.unity.ml-agents/Runtime/Communicator/GrpcExtensions.cs)
- [com.unity.ml-agents/Runtime/Communicator/ICommunicator.cs](com.unity.ml-agents/Runtime/Communicator/ICommunicator.cs)
- [com.unity.ml-agents/Runtime/Communicator/RpcCommunicator.cs](com.unity.ml-agents/Runtime/Communicator/RpcCommunicator.cs)
- [com.unity.ml-agents/Runtime/DecisionRequester.cs](com.unity.ml-agents/Runtime/DecisionRequester.cs)
- [com.unity.ml-agents/Runtime/Demonstrations/DemonstrationWriter.cs](com.unity.ml-agents/Runtime/Demonstrations/DemonstrationWriter.cs)
- [com.unity.ml-agents/Runtime/Grpc/CommunicatorObjects/Observation.cs](com.unity.ml-agents/Runtime/Grpc/CommunicatorObjects/Observation.cs)
- [ml-agents-envs/mlagents_envs/communicator.py](ml-agents-envs/mlagents_envs/communicator.py)
- [ml-agents-envs/mlagents_envs/communicator_objects/observation_pb2.py](ml-agents-envs/mlagents_envs/communicator_objects/observation_pb2.py)
- [ml-agents-envs/mlagents_envs/communicator_objects/observation_pb2.pyi](ml-agents-envs/mlagents_envs/communicator_objects/observation_pb2.pyi)
- [ml-agents-envs/mlagents_envs/communicator_objects/unity_to_external_pb2.py](ml-agents-envs/mlagents_envs/communicator_objects/unity_to_external_pb2.py)
- [ml-agents-envs/mlagents_envs/communicator_objects/unity_to_external_pb2_grpc.py](ml-agents-envs/mlagents_envs/communicator_objects/unity_to_external_pb2_grpc.py)
- [ml-agents-envs/mlagents_envs/env_utils.py](ml-agents-envs/mlagents_envs/env_utils.py)
- [ml-agents-envs/mlagents_envs/environment.py](ml-agents-envs/mlagents_envs/environment.py)
- [ml-agents-envs/mlagents_envs/exception.py](ml-agents-envs/mlagents_envs/exception.py)
- [ml-agents-envs/mlagents_envs/mock_communicator.py](ml-agents-envs/mlagents_envs/mock_communicator.py)
- [ml-agents-envs/mlagents_envs/rpc_communicator.py](ml-agents-envs/mlagents_envs/rpc_communicator.py)
- [protobuf-definitions/README.md](protobuf-definitions/README.md)
- [protobuf-definitions/make_for_win.bat](protobuf-definitions/make_for_win.bat)
- [protobuf-definitions/proto/mlagents_envs/communicator_objects/observation.proto](protobuf-definitions/proto/mlagents_envs/communicator_objects/observation.proto)

</details>



This document explains the gRPC-based communication system that enables Unity environments to exchange data with Python training processes in the ML-Agents Toolkit. This covers the protocol implementation, message types, and data flow between Unity and Python processes.

For information about the overall system architecture, see [ML-Agents Overview](#1). For details about the Python training system, see [Python Training System](#3).

## Communication Architecture Overview

The ML-Agents communication system uses gRPC to enable bidirectional data exchange between Unity environments and Python training processes. The `RpcCommunicator` serves as the primary Unity-side implementation, while the `ICommunicator` interface defines the contract for external communication.

```mermaid
graph TB
    subgraph "Unity Environment [com.unity.ml-agents/Runtime/]"
        Academy["Academy [Academy.cs]<br/>Orchestrates Communication"]
        Agent["Agent [Agent.cs]<br/>Generates Observations"]
        RpcComm["RpcCommunicator [Communicator/RpcCommunicator.cs]<br/>gRPC Client"]
        GrpcExt["GrpcExtensions [Communicator/GrpcExtensions.cs]<br/>Protobuf Conversion"]
    end
    
    subgraph "Communication Protocol [mlagents_envs/communicator_objects/]"
        gRPC["gRPC Protocol<br/>UnityToExternalProto"]
        Protobuf["Protobuf Messages<br/>UnityRLInput/Output"]
    end
    
    subgraph "Python Training Process [ml-agents-envs/mlagents_envs/]"
        UnityEnv["UnityEnvironment [environment.py]<br/>Python API"]
        RpcCommPy["RpcCommunicator [rpc_communicator.py]<br/>gRPC Server"]
    end
    
    Academy --> RpcComm
    Agent --> GrpcExt
    RpcComm --> gRPC
    GrpcExt --> Protobuf
    
    gRPC --> RpcCommPy
    Protobuf --> RpcCommPy
    RpcCommPy --> UnityEnv
```

**Sources:** [com.unity.ml-agents/Runtime/Communicator/RpcCommunicator.cs:25-54](), [com.unity.ml-agents/Runtime/Communicator/ICommunicator.cs:130-180](), [ml-agents-envs/mlagents_envs/environment.py:55-68](), [ml-agents-envs/mlagents_envs/rpc_communicator.py:34-52]()

## gRPC Protocol Implementation

The `RpcCommunicator` class implements the Unity-side gRPC client that connects to the Python training process. On the Python side, `mlagents_envs.rpc_communicator.RpcCommunicator` acts as the server. This reversal (Unity as client, Python as server) allows for easier environment management in containerized or distributed settings.

For details, see [gRPC and Protobuf Layer](#4.1).

```mermaid
graph TB
    subgraph "RpcCommunicator (C#) [RpcCommunicator.cs]"
        Client["UnityToExternalProtoClient<br/>m_Client"]
        InitC["Initialize()<br/>Handshake"]
        PutObs["PutObservations()<br/>Send State"]
        GetAct["GetActions()<br/>Receive Actions"]
    end
    
    subgraph "RpcCommunicator (Python) [rpc_communicator.py]"
        Server["grpc.server<br/>ThreadPoolExecutor"]
        Servicer["UnityToExternalServicerImplementation<br/>Exchange()"]
        Pipe["multiprocessing.Pipe<br/>Sync with Main Process"]
    end
    
    Client -- "gRPC Call" --> Servicer
    Servicer -- "Data" --> Pipe
```

**Sources:** [com.unity.ml-agents/Runtime/Communicator/RpcCommunicator.cs:51-54](), [com.unity.ml-agents/Runtime/Communicator/RpcCommunicator.cs:106-154](), [ml-agents-envs/mlagents_envs/rpc_communicator.py:21-32](), [ml-agents-envs/mlagents_envs/rpc_communicator.py:53-75]()

## Message Types and Data Conversion

The `GrpcExtensions` class provides conversion utilities between Unity C# objects and protobuf messages. This enables seamless serialization of agent observations, actions, and metadata for transmission over gRPC.

```mermaid
graph LR
    subgraph "Unity Entities"
        AgentInfo["AgentInfo<br/>reward, done, groupId"]
        ActionSpec["ActionSpec<br/>Continuous/Discrete sizes"]
    end
    
    subgraph "Protobuf Mapping [GrpcExtensions.cs]"
        ToInfoProto["ToAgentInfoProto()<br/>line 71"]
        ToPairProto["ToInfoActionPairProto()<br/>line 42"]
        ToProtoSpec["ToActionSpecProto()<br/>line 196"]
    end
    
    subgraph "Generated Protobuf"
        AgentInfoProto["AgentInfoProto"]
        AgentActionProto["AgentActionProto"]
    end
    
    AgentInfo --> ToInfoProto
    ToInfoProto --> AgentInfoProto
    ActionSpec --> ToProtoSpec
```

**Sources:** [com.unity.ml-agents/Runtime/Communicator/GrpcExtensions.cs:42-65](), [com.unity.ml-agents/Runtime/Communicator/GrpcExtensions.cs:71-105](), [com.unity.ml-agents/Runtime/Communicator/GrpcExtensions.cs:196-218]()

## Initialization and Handshake Protocol

The communication system follows a specific initialization sequence. Unity sends a `UnityRLInitializationOutputProto` containing its capabilities and versions. Python responds with a `UnityRLInitializationInputProto` which includes the RNG seed and environment configuration.

```mermaid
sequenceDiagram
    participant Unity as RpcCommunicator (C#)
    participant Python as RpcCommunicator (Python)
    
    Note over Unity, Python: Initialization Handshake
    Unity->>Python: UnityRLInitializationOutput (Version, Capabilities)
    Python->>Unity: UnityRLInitializationInput (Seed, NumAreas)
    
    Note over Unity, Python: Compatibility Check
    Unity->>Unity: CheckCommunicationVersionsAreCompatible()
```

**Sources:** [com.unity.ml-agents/Runtime/Communicator/RpcCommunicator.cs:106-154](), [com.unity.ml-agents/Runtime/Communicator/RpcCommunicator.cs:73-97](), [ml-agents-envs/mlagents_envs/environment.py:120-129]()

## Side Channel Communication

Side channels provide an auxiliary communication mechanism for exchanging non-RL data like environment parameters, engine configuration, and statistics. These are handled outside the standard observation/action loop.

For details, see [Side Channels](#4.2).

```mermaid
graph TB
    subgraph "Unity Side"
        SC_C["SideChannelManager<br/>com.unity.ml-agents"]
    end
    
    subgraph "Python Side"
        SC_P["SideChannelManager<br/>mlagents_envs.side_channel"]
    end
    
    SC_C -- "SideChannelMessageProto" --> SC_P
```

**Sources:** [ml-agents-envs/mlagents_envs/environment.py:12-14](), [com.unity.ml-agents/Runtime/Communicator/RpcCommunicator.cs:17-20]()

## Communication API Versioning

The system maintains compatibility through semantic versioning. Both sides verify the `API_VERSION` during the handshake.

| Version | Key Feature Support |
|---------|---------------------|
| 1.0.0   | Initial version |
| 1.3.0   | Hybrid actions (Continuous + Discrete) |
| 1.5.0   | Variable length observations and Multi-agent groups |

**Sources:** [ml-agents-envs/mlagents_envs/environment.py:55-68](), [com.unity.ml-agents/Runtime/Communicator/RpcCommunicator.cs:73-97]()

## Protobuf Maintenance

When the communication protocol changes, the protobuf definitions must be updated and regenerated for both C# and Python.

*   **Definitions:** Located in `protobuf-definitions/proto/`.
*   **Generation:** Use `make.sh` (Linux/Mac) or `make_for_win.bat` (Windows).
*   **Requirements:** `protoc`, `grpcio-tools`, and `Grpc.Tools`.

For details, see [gRPC and Protobuf Layer](#4.1).

**Sources:** [protobuf-definitions/README.md:1-43](), [protobuf-definitions/make_for_win.bat:1-44]()

---

