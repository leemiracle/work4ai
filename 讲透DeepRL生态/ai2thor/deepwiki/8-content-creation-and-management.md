> 来源: [https://deepwiki.com/allenai/ai2thor/8-content-creation-and-management](https://deepwiki.com/allenai/ai2thor/8-content-creation-and-management)
> DeepWiki allenai/ai2thor | Last indexed: 16 September 2025 (24f798

# Content Creation and Management

  Relevant source files 
 - [scripts/objaverse_expand.py](https://github.com/allenai/ai2thor/blob/24f79883/scripts/objaverse_expand.py)
 - [unity/Assets/Editor/ExpRoomEditor.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Editor/ExpRoomEditor.cs)
 - [unity/Assets/Editor/ExpRoomEditor.cs.meta](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Editor/ExpRoomEditor.cs.meta)
 - [unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/FurnMove/MATVStand.prefab](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/FurnMove/MATVStand.prefab)
 - [unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/FurnMove/MATVStand.prefab.meta](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/FurnMove/MATVStand.prefab.meta)
 - [unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/ExpSceneScreens/screen_1.prefab](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/ExpSceneScreens/screen_1.prefab)
 - [unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/ExpSceneScreens/screen_2.prefab](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/ExpSceneScreens/screen_2.prefab)
 - [unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/ExpSceneScreens/screen_2.prefab.meta](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/ExpSceneScreens/screen_2.prefab.meta)
 - [unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/ExpSceneTable.meta](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/ExpSceneTable.meta)
 - [unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/ExpSceneTable/ExpRoomTable.prefab](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/ExpSceneTable/ExpRoomTable.prefab)
 - [unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/ExpSceneTable/ExpRoomTable.prefab.meta](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/ExpSceneTable/ExpRoomTable.prefab.meta)
 - [unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/Screen/Screen_Adjust_Script.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/Screen/Screen_Adjust_Script.cs)
 - [unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/Screen/screen_grp.fbx](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/Screen/screen_grp.fbx)
 - [unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/Screen/screen_pair.prefab](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/Screen/screen_pair.prefab)
 - [unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/Screen/screen_pair.prefab.meta](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/Screen/screen_pair.prefab.meta)
 - [unity/Assets/Scenes/FloorPlan_ExpRoom.unity](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scenes/FloorPlan_ExpRoom.unity)
 - [unity/Assets/Scripts/CollisionListenerChild.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/CollisionListenerChild.cs)
 - [unity/Assets/Scripts/ColorChanger.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/ColorChanger.cs)
 - [unity/Assets/Scripts/DraggablePoint.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/DraggablePoint.cs)
 - [unity/Assets/Scripts/ExpRoom.meta](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/ExpRoom.meta)
 - [unity/Assets/Scripts/ExpRoom/PhysicsRemoteFPSAgentController_partial_ExpRoom.cs.meta](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/ExpRoom/PhysicsRemoteFPSAgentController_partial_ExpRoom.cs.meta)
 - [unity/Assets/Scripts/ProceduralAssetDatabase.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/ProceduralAssetDatabase.cs)
 - [unity/Assets/Scripts/ProceduralAssetEditor.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/ProceduralAssetEditor.cs)
 - [unity/Assets/Scripts/ProceduralAssetEditor.cs.meta](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/ProceduralAssetEditor.cs.meta)
 - [unity/Assets/Scripts/RuntimePrefab.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/RuntimePrefab.cs)
 - [unity/Assets/Scripts/SerializeMesh.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/SerializeMesh.cs)
 - [unity/Assets/Scripts/SimUtil.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/SimUtil.cs)
 
  
## Purpose and Scope

 This document covers AI2-THOR's content creation and management systems, including procedural asset generation, material randomization, asset database management, and content creation tools. These systems enable dynamic scene construction, asset importing from external sources like Objaverse, and visual customization for experimental scenarios.

 For information about scene generation and procedural environments, see [Procedural Generation](https://deepwiki.com/allenai/ai2thor/6.2-procedural-generation). For object physics and interactions, see [Object Interaction System](https://deepwiki.com/allenai/ai2thor/7-object-interaction-system).

 
## System Architecture

 The content creation and management system consists of several interconnected components that handle asset lifecycle from import to runtime usage.

 
### Overall Content Management Architecture

 
```

```

 Sources: [unity/Assets/Scripts/ProceduralAssetEditor.cs1-666](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/ProceduralAssetEditor.cs#L1-L666) [unity/Assets/Scripts/ProceduralAssetDatabase.cs1-222](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/ProceduralAssetDatabase.cs#L1-L222) [unity/Assets/Scripts/ColorChanger.cs1-289](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/ColorChanger.cs#L1-L289)

 
## Asset Import Pipeline

 The asset import system handles conversion of external 3D models into AI2-THOR compatible assets through a multi-stage pipeline.

 
### Objaverse Integration Workflow

 
```

```

 Sources: [unity/Assets/Scripts/ProceduralAssetEditor.cs285-330](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/ProceduralAssetEditor.cs#L285-L330) [unity/Assets/Scripts/ProceduralAssetEditor.cs596-645](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/ProceduralAssetEditor.cs#L596-L645) [unity/Assets/Scripts/SerializeMesh.cs109-188](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/SerializeMesh.cs#L109-L188)

 
### Asset Database and Caching

 The `ProceduralAssetDatabase` provides centralized asset management with LRU caching for memory efficiency.

 
```

```

 Sources: [unity/Assets/Scripts/ProceduralAssetDatabase.cs8-71](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/ProceduralAssetDatabase.cs#L8-L71) [unity/Assets/Scripts/ProceduralAssetDatabase.cs72-221](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/ProceduralAssetDatabase.cs#L72-L221)

 
## Visual Customization System

 The material and color customization system enables randomization and visual variation for experiments and training scenarios.

 
### Material Randomization Architecture

 
```

```

 Sources: [unity/Assets/Scripts/ColorChanger.cs14-102](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/ColorChanger.cs#L14-L102) [unity/Assets/Scripts/ColorChanger.cs146-231](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/ColorChanger.cs#L146-L231) [unity/Assets/Scripts/ColorChanger.cs233-267](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/ColorChanger.cs#L233-L267)

 
## Content Creation Tools

 
### Experimental Scene Editor

 The system includes specialized tools for experimental content creation, particularly for the ExpRoom scene.

 
| Tool Component | Purpose | Key Methods |
|---|---|---|
| ExpRoomEditor | Interactive prefab management | AddPickupableToAvailableObjects(), AddPickupableReceptaclesToAvailableContainers() |
| ProceduralAssetEditor | Asset import and conversion | LoadObject(), SaveObjectPrefabAndTextures(), FixPrefabs() |
| SerializeMesh | Mesh serialization | SaveMeshesAsObjAndReplaceReferences(), MeshToObj() |
| RuntimePrefab | Runtime texture loading | RealoadTextures(), texture path management |

 Sources: [unity/Assets/Editor/ExpRoomEditor.cs9-418](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Editor/ExpRoomEditor.cs#L9-L418) [unity/Assets/Scripts/ProceduralAssetEditor.cs285-475](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/ProceduralAssetEditor.cs#L285-L475)

 
### Mesh and Asset Serialization

 The mesh serialization system converts Unity meshes to portable formats and manages asset references.

 
```

```

 Sources: [unity/Assets/Scripts/SerializeMesh.cs49-78](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/SerializeMesh.cs#L49-L78) [unity/Assets/Scripts/SerializeMesh.cs109-188](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/SerializeMesh.cs#L109-L188) [unity/Assets/Scripts/SerializeMesh.cs226-306](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/SerializeMesh.cs#L226-L306)

 
### Runtime Asset Management

 Runtime prefabs handle dynamic texture loading and material configuration for procedurally generated content.

 
```

```

 Sources: [unity/Assets/Scripts/RuntimePrefab.cs14-99](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/RuntimePrefab.cs#L14-L99) [unity/Assets/Scripts/RuntimePrefab.cs45-86](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/RuntimePrefab.cs#L45-L86)
