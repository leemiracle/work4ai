<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/ai2thor · page 8 Content Creation and Management · fetched 2026-10-30 -->

# Content Creation and Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [scripts/objaverse_expand.py](scripts/objaverse_expand.py)
- [unity/Assets/Editor/ExpRoomEditor.cs](unity/Assets/Editor/ExpRoomEditor.cs)
- [unity/Assets/Editor/ExpRoomEditor.cs.meta](unity/Assets/Editor/ExpRoomEditor.cs.meta)
- [unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/FurnMove/MATVStand.prefab](unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/FurnMove/MATVStand.prefab)
- [unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/FurnMove/MATVStand.prefab.meta](unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/FurnMove/MATVStand.prefab.meta)
- [unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/ExpSceneScreens/screen_1.prefab](unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/ExpSceneScreens/screen_1.prefab)
- [unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/ExpSceneScreens/screen_2.prefab](unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/ExpSceneScreens/screen_2.prefab)
- [unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/ExpSceneScreens/screen_2.prefab.meta](unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/ExpSceneScreens/screen_2.prefab.meta)
- [unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/ExpSceneTable.meta](unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/ExpSceneTable.meta)
- [unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/ExpSceneTable/ExpRoomTable.prefab](unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/ExpSceneTable/ExpRoomTable.prefab)
- [unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/ExpSceneTable/ExpRoomTable.prefab.meta](unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/ExpSceneTable/ExpRoomTable.prefab.meta)
- [unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/Screen/Screen_Adjust_Script.cs](unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/Screen/Screen_Adjust_Script.cs)
- [unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/Screen/screen_grp.fbx](unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/Screen/screen_grp.fbx)
- [unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/Screen/screen_pair.prefab](unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/Screen/screen_pair.prefab)
- [unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/Screen/screen_pair.prefab.meta](unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/Hide And Seek Objects/ExperimentScene/Screen/screen_pair.prefab.meta)
- [unity/Assets/Scenes/FloorPlan_ExpRoom.unity](unity/Assets/Scenes/FloorPlan_ExpRoom.unity)
- [unity/Assets/Scripts/CollisionListenerChild.cs](unity/Assets/Scripts/CollisionListenerChild.cs)
- [unity/Assets/Scripts/ColorChanger.cs](unity/Assets/Scripts/ColorChanger.cs)
- [unity/Assets/Scripts/DraggablePoint.cs](unity/Assets/Scripts/DraggablePoint.cs)
- [unity/Assets/Scripts/ExpRoom.meta](unity/Assets/Scripts/ExpRoom.meta)
- [unity/Assets/Scripts/ExpRoom/PhysicsRemoteFPSAgentController_partial_ExpRoom.cs.meta](unity/Assets/Scripts/ExpRoom/PhysicsRemoteFPSAgentController_partial_ExpRoom.cs.meta)
- [unity/Assets/Scripts/ProceduralAssetDatabase.cs](unity/Assets/Scripts/ProceduralAssetDatabase.cs)
- [unity/Assets/Scripts/ProceduralAssetEditor.cs](unity/Assets/Scripts/ProceduralAssetEditor.cs)
- [unity/Assets/Scripts/ProceduralAssetEditor.cs.meta](unity/Assets/Scripts/ProceduralAssetEditor.cs.meta)
- [unity/Assets/Scripts/RuntimePrefab.cs](unity/Assets/Scripts/RuntimePrefab.cs)
- [unity/Assets/Scripts/SerializeMesh.cs](unity/Assets/Scripts/SerializeMesh.cs)
- [unity/Assets/Scripts/SimUtil.cs](unity/Assets/Scripts/SimUtil.cs)

</details>



## Purpose and Scope

This document covers AI2-THOR's content creation and management systems, including procedural asset generation, material randomization, asset database management, and content creation tools. These systems enable dynamic scene construction, asset importing from external sources like Objaverse, and visual customization for experimental scenarios.

For information about scene generation and procedural environments, see [Procedural Generation](#6.2). For object physics and interactions, see [Object Interaction System](#7).

## System Architecture

The content creation and management system consists of several interconnected components that handle asset lifecycle from import to runtime usage.

### Overall Content Management Architecture

```mermaid
graph TB
    subgraph "External Sources"
        OBJAVERSE["Objaverse Models"]
        FBX["FBX/Asset Files"] 
        TEXTURES["Texture Assets"]
    end
    
    subgraph "Import Pipeline"
        PAE["ProceduralAssetEditor"]
        PYTHON["Python Pipeline"]
        CONVERTER["Asset Converter"]
    end
    
    subgraph "Asset Processing"
        SERIALIZE["SerializeMesh"]
        RUNTIME["RuntimePrefab"]
        MESH_OBJ["OBJ Export"]
    end
    
    subgraph "Asset Management"
        PAD["ProceduralAssetDatabase"]
        LRU["LRU Cache"]
        PREFABS["Unity Prefabs"]
    end
    
    subgraph "Visual Customization"
        COLORCHANGER["ColorChanger"]
        MATERIALS["Material Database"]
        RANDOMIZER["Material Randomizer"]
    end
    
    subgraph "Runtime Systems"
        SIMOBJ["SimObjPhysics"]
        SCENES["Scene Objects"]
        AGENTS["Agent Controllers"]
    end
    
    OBJAVERSE --> PAE
    FBX --> PAE
    TEXTURES --> PAE
    
    PAE --> PYTHON
    PYTHON --> CONVERTER
    CONVERTER --> SERIALIZE
    
    SERIALIZE --> RUNTIME
    RUNTIME --> PAD
    PAE --> PAD
    
    PAD --> LRU
    LRU --> PREFABS
    
    COLORCHANGER --> MATERIALS
    MATERIALS --> RANDOMIZER
    
    PAD --> SIMOBJ
    PREFABS --> SCENES
    RANDOMIZER --> SCENES
    SCENES --> AGENTS
```

Sources: [unity/Assets/Scripts/ProceduralAssetEditor.cs:1-666](), [unity/Assets/Scripts/ProceduralAssetDatabase.cs:1-222](), [unity/Assets/Scripts/ColorChanger.cs:1-289]()

## Asset Import Pipeline

The asset import system handles conversion of external 3D models into AI2-THOR compatible assets through a multi-stage pipeline.

### Objaverse Integration Workflow

```mermaid
graph TD
    subgraph "User Interface"
        LOAD_BTN["LoadObject Button"]
        OBJECT_ID["objectId Field"]
        SETTINGS["ObjaversePipelineSettings"]
    end
    
    subgraph "Asset Processing Pipeline"
        CHECK_EXISTS["File Exists Check"]
        START_PIPELINE["runAssetPipelineAsync"]
        PYTHON_PROC["runPythonCommand"]
        WAIT_PROCESS["waitForProcess"]
        IMPORT_ASSET["importAsset"]
    end
    
    subgraph "Asset Creation"
        PROCEDURAL_TOOLS["ProceduralTools.CreateAsset"]
        SAVE_TEXTURES["SaveTextures"]
        SAVE_MESHES["SaveMeshesAsObjAndReplaceReferences"]
        CREATE_PREFAB["PrefabUtility.SaveAsPrefabAssetAndConnect"]
    end
    
    subgraph "File System"
        OBJAVERSE_DIR["objaverse directory"]
        JSON_FILE["asset.json"]
        TEXTURE_FILES["Texture Files"]
        OBJ_FILES["OBJ Mesh Files"]
        PREFAB_FILES["Unity Prefab Files"]
    end
    
    LOAD_BTN --> OBJECT_ID
    OBJECT_ID --> CHECK_EXISTS
    CHECK_EXISTS -->|Missing| START_PIPELINE
    CHECK_EXISTS -->|Exists| IMPORT_ASSET
    
    START_PIPELINE --> PYTHON_PROC
    PYTHON_PROC --> WAIT_PROCESS
    WAIT_PROCESS --> IMPORT_ASSET
    
    IMPORT_ASSET --> PROCEDURAL_TOOLS
    PROCEDURAL_TOOLS --> SAVE_TEXTURES
    SAVE_TEXTURES --> SAVE_MESHES
    SAVE_MESHES --> CREATE_PREFAB
    
    PYTHON_PROC --> OBJAVERSE_DIR
    OBJAVERSE_DIR --> JSON_FILE
    SAVE_TEXTURES --> TEXTURE_FILES
    SAVE_MESHES --> OBJ_FILES
    CREATE_PREFAB --> PREFAB_FILES
```

Sources: [unity/Assets/Scripts/ProceduralAssetEditor.cs:285-330](), [unity/Assets/Scripts/ProceduralAssetEditor.cs:596-645](), [unity/Assets/Scripts/SerializeMesh.cs:109-188]()

### Asset Database and Caching

The `ProceduralAssetDatabase` provides centralized asset management with LRU caching for memory efficiency.

```mermaid
graph TB
    subgraph "ProceduralAssetDatabase"
        INSTANCE["Static Instance"]
        ASSET_MAP["ProceduralLRUCacheAssetMap"]
        PREFAB_LIST["List<GameObject> prefabs"]
        MATERIALS["List<Material> materials"]
    end
    
    subgraph "LRU Cache Management"
        PRIORITY_QUEUE["SimplePriorityQueue"]
        MIN_VALUE["priorityMinValue"]
        MAX_VALUE["priorityMaxValue"]
        TOUCH["touch() method"]
        REMOVE_LRU["removeLRU() method"]
    end
    
    subgraph "Asset Operations"
        ADD_ASSET["addAsset()"]
        GET_ASSET["getAsset()"]
        CONTAINS["ContainsAssetKey()"]
        ADVANCE_EXP["advanceExpiration()"]
    end
    
    subgraph "Memory Management"
        UNLOAD_ASSETS["Resources.UnloadUnusedAssets()"]
        GC_COLLECT["GC.Collect()"]
        DESTROY_GO["GameObject.Destroy()"]
    end
    
    INSTANCE --> ASSET_MAP
    ASSET_MAP --> PRIORITY_QUEUE
    ASSET_MAP --> PREFAB_LIST
    ASSET_MAP --> MATERIALS
    
    ADD_ASSET --> PRIORITY_QUEUE
    TOUCH --> ADVANCE_EXP
    ADVANCE_EXP --> PRIORITY_QUEUE
    REMOVE_LRU --> DESTROY_GO
    DESTROY_GO --> UNLOAD_ASSETS
    UNLOAD_ASSETS --> GC_COLLECT
    
    GET_ASSET --> ASSET_MAP
    CONTAINS --> ASSET_MAP
```

Sources: [unity/Assets/Scripts/ProceduralAssetDatabase.cs:8-71](), [unity/Assets/Scripts/ProceduralAssetDatabase.cs:72-221]()

## Visual Customization System

The material and color customization system enables randomization and visual variation for experiments and training scenarios.

### Material Randomization Architecture

```mermaid
graph LR
    subgraph "Material Categories"
        OBJECT_MATS["Object-Specific Materials"]
        ROOM_MATS["Room-Type Materials"] 
        SPLIT_MATS["Train/Val/Test Materials"]
    end
    
    subgraph "ColorChanger Core"
        CACHE_MATS["cacheMaterials()"]
        RESOURCE_MGR["ResourceAssetManager"]
        MATERIAL_GROUPS["materialGroupPaths"]
        ORIG_MATS["origMaterials backup"]
    end
    
    subgraph "Randomization Operations"
        RANDOMIZE["RandomizeMaterials()"]
        SHUFFLE["shuffleMaterials()"]
        SWAP["swapMaterial()"]
        RESET["ResetMaterials()"]
    end
    
    subgraph "Scene Application"
        FIND_RENDERERS["FindObjectsOfType<Renderer>"]
        ACTIVE_NAMES["activeMaterialNames"]
        APPLY_CHANGES["Material Property Updates"]
    end
    
    CACHE_MATS --> RESOURCE_MGR
    RESOURCE_MGR --> OBJECT_MATS
    RESOURCE_MGR --> ROOM_MATS
    RESOURCE_MGR --> SPLIT_MATS
    
    CACHE_MATS --> MATERIAL_GROUPS
    RANDOMIZE --> FIND_RENDERERS
    FIND_RENDERERS --> ACTIVE_NAMES
    RANDOMIZE --> SHUFFLE
    SHUFFLE --> SWAP
    SWAP --> ORIG_MATS
    
    RESET --> ORIG_MATS
    SWAP --> APPLY_CHANGES
```

Sources: [unity/Assets/Scripts/ColorChanger.cs:14-102](), [unity/Assets/Scripts/ColorChanger.cs:146-231](), [unity/Assets/Scripts/ColorChanger.cs:233-267]()

## Content Creation Tools

### Experimental Scene Editor

The system includes specialized tools for experimental content creation, particularly for the ExpRoom scene.

| Tool Component | Purpose | Key Methods |
|----------------|---------|-------------|
| `ExpRoomEditor` | Interactive prefab management | `AddPickupableToAvailableObjects()`, `AddPickupableReceptaclesToAvailableContainers()` |
| `ProceduralAssetEditor` | Asset import and conversion | `LoadObject()`, `SaveObjectPrefabAndTextures()`, `FixPrefabs()` |
| `SerializeMesh` | Mesh serialization | `SaveMeshesAsObjAndReplaceReferences()`, `MeshToObj()` |
| `RuntimePrefab` | Runtime texture loading | `RealoadTextures()`, texture path management |

Sources: [unity/Assets/Editor/ExpRoomEditor.cs:9-418](), [unity/Assets/Scripts/ProceduralAssetEditor.cs:285-475]()

### Mesh and Asset Serialization

The mesh serialization system converts Unity meshes to portable formats and manages asset references.

```mermaid
graph TD
    subgraph "Mesh Processing"
        UNITY_MESH["Unity Mesh"]
        SERIALIZE_MESH["SerializeMesh.Serialize()"]
        MESH_TO_OBJ["MeshToObj()"]
        SERIALIZABLE_MESH["SerializableMesh"]
    end
    
    subgraph "File Export"
        OBJ_EXPORT["SaveAsObj()"]
        ASSET_DATABASE["AssetDatabase.Refresh()"]
        MODEL_IMPORTER["ModelImporter settings"]
        REPLACE_REFS["Replace mesh references"]
    end
    
    subgraph "Collider Handling"
        MESH_COLLIDERS["MeshCollider components"]
        COLLIDER_MESHES["Separate collider meshes"]
        TRIGGER_COLLIDERS["TriggerColliders"]
    end
    
    subgraph "Runtime Loading"
        REBUILD["Rebuild() method"]
        DESERIALIZE["deSerializeMesh()"]
        RECALC_BOUNDS["RecalculateBounds()"]
    end
    
    UNITY_MESH --> SERIALIZE_MESH
    SERIALIZE_MESH --> SERIALIZABLE_MESH
    SERIALIZE_MESH --> MESH_TO_OBJ
    MESH_TO_OBJ --> OBJ_EXPORT
    
    OBJ_EXPORT --> ASSET_DATABASE
    ASSET_DATABASE --> MODEL_IMPORTER
    MODEL_IMPORTER --> REPLACE_REFS
    
    SERIALIZE_MESH --> MESH_COLLIDERS
    MESH_COLLIDERS --> COLLIDER_MESHES
    COLLIDER_MESHES --> TRIGGER_COLLIDERS
    
    SERIALIZABLE_MESH --> REBUILD
    REBUILD --> DESERIALIZE
    DESERIALIZE --> RECALC_BOUNDS
```

Sources: [unity/Assets/Scripts/SerializeMesh.cs:49-78](), [unity/Assets/Scripts/SerializeMesh.cs:109-188](), [unity/Assets/Scripts/SerializeMesh.cs:226-306]()

### Runtime Asset Management

Runtime prefabs handle dynamic texture loading and material configuration for procedurally generated content.

```mermaid
graph LR
    subgraph "RuntimePrefab Component"
        TEXTURE_PATHS["Texture Path Properties"]
        SHARED_MAT["sharedMaterial cache"]
        RELOAD_METHOD["RealoadTextures()"]
    end
    
    subgraph "Texture Types"
        ALBEDO["albedoTexturePath"]
        METALLIC["metallicSmoothnessTexturePath"] 
        NORMAL["normalTexturePath"]
        EMISSION["emissionTexturePath"]
    end
    
    subgraph "Loading Process"
        READ_BYTES["File.ReadAllBytes()"]
        LOAD_IMAGE["Texture2D.LoadImage()"]
        CHANNEL_SWAP["SwapChannelsRGBAtoRRRB()"]
        SET_MATERIAL["Material property assignment"]
    end
    
    subgraph "Material Configuration"
        ENABLE_KEYWORDS["EnableKeyword()"]
        SET_TEXTURES["SetTexture()"]
        SET_COLORS["SetColor()"]
        GI_FLAGS["globalIlluminationFlags"]
    end
    
    TEXTURE_PATHS --> ALBEDO
    TEXTURE_PATHS --> METALLIC
    TEXTURE_PATHS --> NORMAL
    TEXTURE_PATHS --> EMISSION
    
    RELOAD_METHOD --> READ_BYTES
    READ_BYTES --> LOAD_IMAGE
    LOAD_IMAGE --> CHANNEL_SWAP
    CHANNEL_SWAP --> SET_MATERIAL
    
    SET_MATERIAL --> ENABLE_KEYWORDS
    ENABLE_KEYWORDS --> SET_TEXTURES
    SET_TEXTURES --> SET_COLORS
    SET_COLORS --> GI_FLAGS
```

Sources: [unity/Assets/Scripts/RuntimePrefab.cs:14-99](), [unity/Assets/Scripts/RuntimePrefab.cs:45-86]()

---

