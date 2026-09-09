> 来源: [https://deepwiki.com/Unity-Technologies/ml-agents/4-unity-python-communication](https://deepwiki.com/Unity-Technologies/ml-agents/4-unity-python-communication)
> DeepWiki Unity-Technologies/ml-agents | Last indexed: 22 May 2026 (d52b00

# Unity-Python Communication

  Relevant source files 
 - [com.unity.ml-agents/Runtime/Communicator/GrpcExtensions.cs](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Communicator/GrpcExtensions.cs)
 - [com.unity.ml-agents/Runtime/Communicator/ICommunicator.cs](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Communicator/ICommunicator.cs)
 - [com.unity.ml-agents/Runtime/Communicator/RpcCommunicator.cs](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Communicator/RpcCommunicator.cs)
 - [com.unity.ml-agents/Runtime/DecisionRequester.cs](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/DecisionRequester.cs)
 - [com.unity.ml-agents/Runtime/Demonstrations/DemonstrationWriter.cs](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Demonstrations/DemonstrationWriter.cs)
 - [com.unity.ml-agents/Runtime/Grpc/CommunicatorObjects/Observation.cs](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Grpc/CommunicatorObjects/Observation.cs)
 - [ml-agents-envs/mlagents_envs/communicator.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents-envs/mlagents_envs/communicator.py)
 - [ml-agents-envs/mlagents_envs/communicator_objects/observation_pb2.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents-envs/mlagents_envs/communicator_objects/observation_pb2.py)
 - [ml-agents-envs/mlagents_envs/communicator_objects/observation_pb2.pyi](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents-envs/mlagents_envs/communicator_objects/observation_pb2.pyi)
 - [ml-agents-envs/mlagents_envs/communicator_objects/unity_to_external_pb2.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents-envs/mlagents_envs/communicator_objects/unity_to_external_pb2.py)
 - [ml-agents-envs/mlagents_envs/communicator_objects/unity_to_external_pb2_grpc.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents-envs/mlagents_envs/communicator_objects/unity_to_external_pb2_grpc.py)
 - [ml-agents-envs/mlagents_envs/env_utils.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents-envs/mlagents_envs/env_utils.py)
 - [ml-agents-envs/mlagents_envs/environment.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents-envs/mlagents_envs/environment.py)
 - [ml-agents-envs/mlagents_envs/exception.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents-envs/mlagents_envs/exception.py)
 - [ml-agents-envs/mlagents_envs/mock_communicator.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents-envs/mlagents_envs/mock_communicator.py)
 - [ml-agents-envs/mlagents_envs/rpc_communicator.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents-envs/mlagents_envs/rpc_communicator.py)
 - [protobuf-definitions/README.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/protobuf-definitions/README.md?plain=1)
 - [protobuf-definitions/make_for_win.bat](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/protobuf-definitions/make_for_win.bat)
 - [protobuf-definitions/proto/mlagents_envs/communicator_objects/observation.proto](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/protobuf-definitions/proto/mlagents_envs/communicator_objects/observation.proto)
 
  This document explains the gRPC-based communication system that enables Unity environments to exchange data with Python training processes in the ML-Agents Toolkit. This covers the protocol implementation, message types, and data flow between Unity and Python processes.

 For information about the overall system architecture, see [ML-Agents Overview](https://deepwiki.com/Unity-Technologies/ml-agents/1-ml-agents-overview). For details about the Python training system, see [Python Training System](https://deepwiki.com/Unity-Technologies/ml-agents/3-python-training-system).

 
## Communication Architecture Overview

 The ML-Agents communication system uses gRPC to enable bidirectional data exchange between Unity environments and Python training processes. The `RpcCommunicator` serves as the primary Unity-side implementation, while the `ICommunicator` interface defines the contract for external communication.

 
```

```

 **Sources:** [com.unity.ml-agents/Runtime/Communicator/RpcCommunicator.cs25-54](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Communicator/RpcCommunicator.cs#L25-L54) [com.unity.ml-agents/Runtime/Communicator/ICommunicator.cs130-180](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Communicator/ICommunicator.cs#L130-L180) [ml-agents-envs/mlagents_envs/environment.py55-68](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents-envs/mlagents_envs/environment.py#L55-L68) [ml-agents-envs/mlagents_envs/rpc_communicator.py34-52](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents-envs/mlagents_envs/rpc_communicator.py#L34-L52)

 
## gRPC Protocol Implementation

 The `RpcCommunicator` class implements the Unity-side gRPC client that connects to the Python training process. On the Python side, `mlagents_envs.rpc_communicator.RpcCommunicator` acts as the server. This reversal (Unity as client, Python as server) allows for easier environment management in containerized or distributed settings.

 For details, see [gRPC and Protobuf Layer](https://deepwiki.com/Unity-Technologies/ml-agents/4.1-grpc-and-protobuf-layer).

 
```

```

 **Sources:** [com.unity.ml-agents/Runtime/Communicator/RpcCommunicator.cs51-54](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Communicator/RpcCommunicator.cs#L51-L54) [com.unity.ml-agents/Runtime/Communicator/RpcCommunicator.cs106-154](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Communicator/RpcCommunicator.cs#L106-L154) [ml-agents-envs/mlagents_envs/rpc_communicator.py21-32](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents-envs/mlagents_envs/rpc_communicator.py#L21-L32) [ml-agents-envs/mlagents_envs/rpc_communicator.py53-75](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents-envs/mlagents_envs/rpc_communicator.py#L53-L75)

 
## Message Types and Data Conversion

 The `GrpcExtensions` class provides conversion utilities between Unity C# objects and protobuf messages. This enables seamless serialization of agent observations, actions, and metadata for transmission over gRPC.

 
```

```

 **Sources:** [com.unity.ml-agents/Runtime/Communicator/GrpcExtensions.cs42-65](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Communicator/GrpcExtensions.cs#L42-L65) [com.unity.ml-agents/Runtime/Communicator/GrpcExtensions.cs71-105](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Communicator/GrpcExtensions.cs#L71-L105) [com.unity.ml-agents/Runtime/Communicator/GrpcExtensions.cs196-218](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Communicator/GrpcExtensions.cs#L196-L218)

 
## Initialization and Handshake Protocol

 The communication system follows a specific initialization sequence. Unity sends a `UnityRLInitializationOutputProto` containing its capabilities and versions. Python responds with a `UnityRLInitializationInputProto` which includes the RNG seed and environment configuration.

 
```

```

 **Sources:** [com.unity.ml-agents/Runtime/Communicator/RpcCommunicator.cs106-154](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Communicator/RpcCommunicator.cs#L106-L154) [com.unity.ml-agents/Runtime/Communicator/RpcCommunicator.cs73-97](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Communicator/RpcCommunicator.cs#L73-L97) [ml-agents-envs/mlagents_envs/environment.py120-129](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents-envs/mlagents_envs/environment.py#L120-L129)

 
## Side Channel Communication

 Side channels provide an auxiliary communication mechanism for exchanging non-RL data like environment parameters, engine configuration, and statistics. These are handled outside the standard observation/action loop.

 For details, see [Side Channels](https://deepwiki.com/Unity-Technologies/ml-agents/4.2-side-channels).

 
```

```

 **Sources:** [ml-agents-envs/mlagents_envs/environment.py12-14](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents-envs/mlagents_envs/environment.py#L12-L14) [com.unity.ml-agents/Runtime/Communicator/RpcCommunicator.cs17-20](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Communicator/RpcCommunicator.cs#L17-L20)

 
## Communication API Versioning

 The system maintains compatibility through semantic versioning. Both sides verify the `API_VERSION` during the handshake.

 
| Version | Key Feature Support |
|---|---|
| 1.0.0 | Initial version |
| 1.3.0 | Hybrid actions (Continuous + Discrete) |
| 1.5.0 | Variable length observations and Multi-agent groups |

 **Sources:** [ml-agents-envs/mlagents_envs/environment.py55-68](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents-envs/mlagents_envs/environment.py#L55-L68) [com.unity.ml-agents/Runtime/Communicator/RpcCommunicator.cs73-97](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Communicator/RpcCommunicator.cs#L73-L97)

 
## Protobuf Maintenance

 When the communication protocol changes, the protobuf definitions must be updated and regenerated for both C# and Python.

 
 - **Definitions:** Located in `protobuf-definitions/proto/`.
 - **Generation:** Use `make.sh` (Linux/Mac) or `make_for_win.bat` (Windows).
 - **Requirements:** `protoc`, `grpcio-tools`, and `Grpc.Tools`.
 
 For details, see [gRPC and Protobuf Layer](https://deepwiki.com/Unity-Technologies/ml-agents/4.1-grpc-and-protobuf-layer).

 **Sources:** [protobuf-definitions/README.md1-43](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/protobuf-definitions/README.md?plain=1#L1-L43) [protobuf-definitions/make_for_win.bat1-44](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/protobuf-definitions/make_for_win.bat#L1-L44)
