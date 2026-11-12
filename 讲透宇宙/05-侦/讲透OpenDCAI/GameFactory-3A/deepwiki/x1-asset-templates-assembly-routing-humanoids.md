<!-- source: DeepWiki mcp.deepwiki.com · repo OpenDCAI/GameFactory-3A · extra page Asset Templates: Assembly, Routing, Humanoids · fetched 2026-11-02 -->

# Asset Templates: Assembly, Routing, Humanoids

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent_skills/asset_qa/3d_object/SKILL.md](agent_skills/asset_qa/3d_object/SKILL.md)
- [agent_skills/asset_qa/3d_object/composition_examples.md](agent_skills/asset_qa/3d_object/composition_examples.md)
- [models/common/glb_utils.py](models/common/glb_utils.py)
- [models/common/glb_writer.py](models/common/glb_writer.py)
- [operators/gen_3d_object/funcs/code_asset.py](operators/gen_3d_object/funcs/code_asset.py)
- [operators/gen_3d_object/funcs/code_asset_templates/__init__.py](operators/gen_3d_object/funcs/code_asset_templates/__init__.py)
- [operators/gen_3d_object/funcs/code_asset_templates/assembly.py](operators/gen_3d_object/funcs/code_asset_templates/assembly.py)
- [operators/gen_3d_object/funcs/code_asset_templates/compose.py](operators/gen_3d_object/funcs/code_asset_templates/compose.py)
- [operators/gen_3d_object/funcs/code_asset_templates/human_template/__init__.py](operators/gen_3d_object/funcs/code_asset_templates/human_template/__init__.py)
- [operators/gen_3d_object/funcs/code_asset_templates/human_template/armour_fit.py](operators/gen_3d_object/funcs/code_asset_templates/human_template/armour_fit.py)
- [operators/gen_3d_object/funcs/code_asset_templates/human_template/figure_fit.py](operators/gen_3d_object/funcs/code_asset_templates/human_template/figure_fit.py)
- [operators/gen_3d_object/funcs/code_asset_templates/human_template/humanoid.py](operators/gen_3d_object/funcs/code_asset_templates/human_template/humanoid.py)
- [operators/gen_3d_object/funcs/code_asset_templates/human_template/plate_armour.py](operators/gen_3d_object/funcs/code_asset_templates/human_template/plate_armour.py)
- [operators/gen_3d_object/funcs/code_asset_templates/rigid_template/__init__.py](operators/gen_3d_object/funcs/code_asset_templates/rigid_template/__init__.py)
- [operators/gen_3d_object/funcs/code_asset_templates/routing.py](operators/gen_3d_object/funcs/code_asset_templates/routing.py)
- [test/test_3d_object_spec.py](test/test_3d_object_spec.py)

</details>



## Purpose and Scope

The `operators/gen_3d_object/funcs/code_asset_templates/` package provides the domain logic, routing heuristics, assembly primitives, and anatomical fitting routines for declarative 3D asset generation (the spec route). Rather than relying entirely on image-to-3D neural networks for rigid or semi-rigid structures, this package classifies subject topologies, builds assembly hierarchies using relative attachments (`attach`) instead of absolute coordinates, and maps parametric or measured meshes for mechanical assemblies and humanoid armours.

Sources: `[operators/gen_3d_object/funcs/code_asset_templates/__init__.py:1-44]()`

---

## 1. Routing Strategies & Topology Classification

The router determines how a subject is constructed by analyzing its **assembly topology** rather than surface adjectives [operators/gen_3d_object/funcs/code_asset_templates/routing.py:1-7]. 

### Topologies and Route Mapping
The classification is defined across three fundamental topologies:
* `COMPOSED`: Parts sit beside each other and are joined by adjacency. Fully describable via code specs (`code` route) [operators/gen_3d_object/funcs/code_asset_templates/routing.py:9-13].
* `NESTED`: Layers sit on a host that must exist and be measured first (e.g., armour on a body). The host is generated and layers are stated (hybrid route) [operators/gen_3d_object/funcs/code_asset_templates/routing.py:14-19].
* `SURFACE`: Inseparable surfaces with no assembly hierarchy (faces, trees). Routed to `generate` [operators/gen_3d_object/funcs/code_asset_templates/routing.py:20-23].

These map directly to pipeline execution flags via `ROUTE_FOR_TOPOLOGY`:
```python
ROUTE_FOR_TOPOLOGY: dict[str, tuple[bool, str]] = {
    COMPOSED: (True, "code"),
    NESTED: (False, "generate"),
    SURFACE: (False, "generate"),
}
```
Sources: `[operators/gen_3d_object/funcs/code_asset_templates/routing.py:45-70]()`

### Claims and Evidence Tiers
Strategies return a `Claim` dataclass containing the evaluated topology, strength, reasoning, and evidence tokens [operators/gen_3d_object/funcs/code_asset_templates/routing.py:82-101]. Claims operate across two evidence tiers:
* `EVIDENCE` (0): Counted keyword matches (e.g., matching nouns and material words) [operators/gen_3d_object/funcs/code_asset_templates/routing.py:78].
* `STRUCTURAL` (1): Structural observations about assembly dependencies (e.g., host-wearer phrasing) that outrank simple word counts [operators/gen_3d_object/funcs/code_asset_templates/routing.py:78-80].

Strategies are registered dynamically via `register()` and queried through `claims()` [operators/gen_3d_object/funcs/code_asset_templates/routing.py:123-171].

### Diagram: Natural Language Routing Space to Code Entities
```mermaid
flowchart TD
    Prompt[""User Input: 'female knight in plate armour'""] --> Router[""routing.claims(subject)""]
    Router --> RigidStrat[""rigid_template.claim()""]
    Router --> HumanStrat[""human_template.claim()""]
    HumanStrat --> NestCheck[""Head-noun & wearing prepositions validation""]
    NestCheck --> StructTier[""Claim(topology='nested', tier=STRUCTURAL)""]
    RigidStrat --> EvidenceTier[""Claim(topology='composed', tier=EVIDENCE)""]
    StructTier --> Resolution[""ROUTE_FOR_TOPOLOGY['nested'] -> generate host""]
    EvidenceTier --> ResolutionCode[""ROUTE_FOR_TOPOLOGY['composed'] -> code spec""]
```
Sources: `[operators/gen_3d_object/funcs/code_asset_templates/routing.py:1-171](), [operators/gen_3d_object/funcs/code_asset_templates/human_template/__init__.py:115-161]()`

---

## 2. Assembly Helpers: Chain, Group, and Mirrored

The `assembly` module handles spatial relationships for `COMPOSED` assets using relational attachments (`attach`) instead of hardcoded absolute coordinates `at` [operators/gen_3d_object/funcs/code_asset_templates/assembly.py:1-20].

### Key Functions
* `chain()`: Attaches each part sequentially to its predecessor from front to back along a designated axis (`x`, `y`, or `z`). Preserves existing explicit `attach` or `parent` definitions to support branching hierarchies [operators/gen_3d_object/funcs/code_asset_templates/assembly.py:40-106].
* `group()`: Attaches an iterable of parts to a single central hub identifier (`to`), preventing cascading positioning dependencies (e.g., four wheels mounted to a chassis) [operators/gen_3d_object/funcs/code_asset_templates/assembly.py:109-144].
* `mirrored()`: Generates symmetric assemblies (e.g., twin barrels, left/right landing skids) from a single description. Automatically updates `suffix` IDs and rewrites internal `attach.to` references to prevent left-side components from improperly parenting to right-side counterparts [operators/gen_3d_object/funcs/code_asset_templates/assembly.py:147-176].

Sources: `[operators/gen_3d_object/funcs/code_asset_templates/assembly.py:1-176]()`

---

## 3. Rigid Templates & Hard-Surface Vocabulary

The `rigid_template` package implements the strategy and vocabulary for manufactured hard-surface objects (`crates`, `rifles`, `vehicles`, `weapons`) [operators/gen_3d_object/funcs/code_asset_templates/rigid_template/__init__.py:1-41].

### Vocabulary Structure
Subject identification relies on three lexical tuples:
* `THINGS`: Core nouns representing rigid assemblies (e.g., `"crate"`, `"rifle"`, `"wheel"`, `"turret"`) [operators/gen_3d_object/funcs/code_asset_templates/rigid_template/__init__.py:28-41].
* `MATERIALS`: Material words that tip borderline classifications (e.g., `"steel"`, `"bronze"`, `"concrete"`) [operators/gen_3d_object/funcs/code_asset_templates/rigid_template/__init__.py:47-50].
* `SHAPES`: Manufacturing descriptors (e.g., `"chamfered"`, `"modular"`, `"riveted"`) [operators/gen_3d_object/funcs/code_asset_templates/rigid_template/__init__.py:54-57].

The `claim()` function extracts whole words from the subject string, counts matches, and returns a `COMPOSED` claim targeting the rigid template builder [operators/gen_3d_object/funcs/code_asset_templates/rigid_template/__init__.py:60-91].

Sources: `[operators/gen_3d_object/funcs/code_asset_templates/rigid_template/__init__.py:1-94]()`

---

## 4. Human Templates, Figures, and Armour Fitting

The `human_template` package manages humanoid bodies and wearable gear under the `NESTED` topology [operators/gen_3d_object/funcs/code_asset_templates/human_template/__init__.py:1-16].

### Modules and Subsystems
* `humanoid`: Generates a parametric biped body from nominal proportions without network calls [operators/gen_3d_object/funcs/code_asset_templates/human_template/__init__.py:21-23].
* `figure_fit`: Measures landmark coordinates off generated T-pose meshes (`tpose.glb`) to account for model-specific proportions [operators/gen_3d_object/funcs/code_asset_templates/human_template/__init__.py:24-30].
* `plate_armour`: Defines modular armaments and plate sets structured around slot names [operators/gen_3d_object/funcs/code_asset_templates/human_template/__init__.py:31-33].
* `armour_fit`: Computes scaling factors and placement matrices to fit armour meshes onto measured body landmarks [operators/gen_3d_object/funcs/code_asset_templates/human_template/__init__.py:34-37].

### Armour Fitting and Slot Resolution
The `SLOTS` dictionary defines spatial placement rules mapping slot names (such as `shin`, `torso`, or `pauldron`) to landmark equations governing lateral splay, height intervals, and depth profiles [operators/gen_3d_object/funcs/code_asset_templates/human_template/armour_fit.py:93-119]. 

To wrap limb cross-sections accurately without intersecting underlying geometry, `span_to_wrap()` reads mesh bounds via `load_mesh_asset()` and scales uniform bounding boxes against target limb girths [operators/gen_3d_object/funcs/code_asset_templates/human_template/armour_fit.py:29-67].

### Diagram: Human Anatomy & Armour Fitting Space to Code Entities
```mermaid
flowchart TD
    Mesh[""Generated Mesh: parts/tpose.glb""] --> FigFit[""figure_fit.landmarks_for()""]
    FigFit --> Landmarks[""Landmark Dict (chest_y, knee_y, ankle_y)""]
    Landmarks --> ArmourFit[""armour_fit.fit_armour(landmarks, pieces)""]
    ArmourFit --> SlotLookup[""SLOTS Table lookup (e.g. SLOTS['shin'])""]
    SlotLookup --> WrapCalc[""armour_fit.span_to_wrap(source, girth)""]
    WrapCalc --> MeshLoader[""glb_writer.load_mesh_asset()""]
    MeshLoader --> FinalSpec[""Composed Spec Output (Nested Host & Plates)""]
```
Sources: `[operators/gen_3d_object/funcs/code_asset_templates/human_template/__init__.py:1-77](), [operators/gen_3d_object/funcs/code_asset_templates/human_template/armour_fit.py:29-119]()`

---

