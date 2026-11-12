<!-- source: DeepWiki mcp.deepwiki.com · repo openai/NavierStokesAndEuler · extra page Action Words, Path Products, and Amplitudes · fetched 2026-10-26 -->

# Action Words, Path Products, and Amplitudes

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Euler/CylinderActionWords.lean](Euler/CylinderActionWords.lean)
- [Euler/CylinderConstantMapBounds.lean](Euler/CylinderConstantMapBounds.lean)
- [Euler/CylinderPathBilinear.lean](Euler/CylinderPathBilinear.lean)
- [Euler/CylinderPathBilinearBounds.lean](Euler/CylinderPathBilinearBounds.lean)
- [Euler/CylinderPathProduct.lean](Euler/CylinderPathProduct.lean)
- [Euler/CylinderTerminalAmplitude.lean](Euler/CylinderTerminalAmplitude.lean)
- [Euler/CylinderTimePrecomposition.lean](Euler/CylinderTimePrecomposition.lean)
- [Euler/ElapsedTimePathGluing.lean](Euler/ElapsedTimePathGluing.lean)
- [Euler/ElapsedTimePathNaturality.lean](Euler/ElapsedTimePathNaturality.lean)
- [Euler/IntervalPathConcatenation.lean](Euler/IntervalPathConcatenation.lean)
- [Euler/PacketInitialAmplitude.lean](Euler/PacketInitialAmplitude.lean)
- [Euler/TransversePacketAmplitude.lean](Euler/TransversePacketAmplitude.lean)
- [Euler/TransversePacketForwardNorms.lean](Euler/TransversePacketForwardNorms.lean)
- [Euler/TransversePacketJoinedBounds.lean](Euler/TransversePacketJoinedBounds.lean)
- [Euler/TransversePacketJoinedUnitBounds.lean](Euler/TransversePacketJoinedUnitBounds.lean)
- [Euler/TransversePacketPairAmplitude.lean](Euler/TransversePacketPairAmplitude.lean)
- [Euler/TransversePacketPrimaryBounds.lean](Euler/TransversePacketPrimaryBounds.lean)
- [Euler/TransversePacketPrimaryUnitBounds.lean](Euler/TransversePacketPrimaryUnitBounds.lean)

</details>



This page details the construction and properties of "action words" on the cylinder, which are fundamental for describing how quantities transform under spatial translations. It also covers bilinear and product structures for continuous paths of cylinder fields, the mechanism for gluing and concatenating paths over elapsed time, and the amplitude bounds for initial and terminal data. These concepts are crucial for managing the regularity and magnitude of fields throughout the Euler and Navier-Stokes equation proofs.

## Cylinder Action Words

Cylinder action words refer to the way spatial translations (`translate P a`) act on various function spaces defined on the cylinder. These actions are isometric, meaning they preserve norms, which is a critical property for maintaining bounds in Sobolev and Gevrey spaces. The `pathTranslate` function [Euler/CylinderActionWords.lean:22-23]() extends this translation to continuous paths of cylinder fields.

The core idea is that the "block" of a function's orbit under translation is constant. A "block" (`block directions q f n a`) represents a Gevrey-Sobolev norm-like quantity that measures the regularity of a function `f` with respect to its translation orbit. The `block_orbit_constant` theorem [Euler/CylinderActionWords.lean:43-46]() states that for an isometric action, this block value is independent of the translation parameter `a`. This is formalized for continuous paths (`C(K, CylinderL2 P V)`) in `path_block_constant` [Euler/CylinderActionWords.lean:39-46]() and for `TimeLp` spaces in `time_block_constant` [Euler/CylinderActionWords.lean:73-83]().

### Bridging Natural Language to Code: Action Words

```mermaid
graph TD
    subgraph "Natural Language Space"
        NL_ActionWord["Action Word"]
        NL_SpatialTranslation["Spatial Translation"]
        NL_IsometricAction["Isometric Action"]
        NL_BlockConstant["Block Constant under Translation"]
    end

    subgraph "Code Entity Space"
        CE_Translate["`translate P a` (Euler/LpCylinderOrbit.lean)"]
        CE_PathTranslate["`pathTranslate P a` (Euler/CylinderActionWords.lean)"]
        CE_TimeTranslateIsometry["`timeTranslateIsometry P T a` (Euler/CylinderActionWords.lean)"]
        CE_Block["`block directions q f n a` (Euler/ParameterWordGevrey.lean)"]
        CE_BlockOrbitConstant["`EulerIsometricAction.block_orbit_constant` (Euler/IsometricActionWords.lean)"]
        CE_PathBlockConstant["`path_block_constant` (Euler/CylinderActionWords.lean:39-46)"]
        CE_TimeBlockConstant["`time_block_constant` (Euler/CylinderActionWords.lean:73-83)"]
    end

    NL_ActionWord --> NL_SpatialTranslation
    NL_SpatialTranslation --> CE_Translate
    NL_SpatialTranslation --> CE_PathTranslate
    NL_SpatialTranslation --> CE_TimeTranslateIsometry
    CE_Translate -- "Applies to" --> CE_PathTranslate
    CE_Translate -- "Lifts to" --> CE_TimeTranslateIsometry
    NL_IsometricAction --> CE_Translate
    NL_IsometricAction --> CE_PathTranslateIsometry["`pathTranslateIsometry` (Euler/CylinderActionWords.lean:35-37)"]
    NL_IsometricAction --> CE_TimeTranslateIsometry
    NL_BlockConstant --> CE_Block
    CE_BlockOrbitConstant -- "Generalizes" --> CE_PathBlockConstant
    CE_BlockOrbitConstant -- "Generalizes" --> CE_TimeBlockConstant
    CE_PathBlockConstant -- "Uses" --> CE_PathTranslate
    CE_TimeBlockConstant -- "Uses" --> CE_TimeTranslateIsometry
```
Sources:
- [Euler/CylinderActionWords.lean:22-23]()
- [Euler/CylinderActionWords.lean:35-37]()
- [Euler/CylinderActionWords.lean:39-46]()
- [Euler/CylinderActionWords.lean:73-83]()
- [Euler/LpCylinderOrbit.lean]()
- [Euler/ParameterWordGevrey.lean]()
- [Euler/IsometricActionWords.lean]()

## Path Bilinear and Product Structures

The codebase defines bilinear and product structures for continuous paths of cylinder fields. These are essential for handling nonlinear terms in the PDE.

### Bilinear Maps on Paths

A bounded bilinear map `B : E →L[ℝ] F →L[ℝ] G` acting on individual elements can be lifted to act pointwise on continuous paths `C(K,E)`, `C(K,F)`, and `C(K,G)`. This is achieved by `pathBilinear` [Euler/CylinderPathProduct.lean:41-42]().

```lean
def pathBilinear (B : E →L[ℝ] F →L[ℝ] G) : C(K,E) →L[ℝ] C(K,F) →L[ℝ] C(K,G) :=
  coefficientMap.comp (B.compLeftContinuous ℝ K)
```
The `pathBilinear_apply` theorem [Euler/CylinderPathProduct.lean:43-44]() confirms that this operation is indeed pointwise. The norm of `pathBilinear` is bounded by the norm of the original bilinear map `B` [Euler/CylinderPathProduct.lean:48-52](). Crucially, if the input paths are `ContDiff`, their `pathBilinear` product is also `ContDiff` [Euler/CylinderPathProduct.lean:54-59]().

### Scalar Product Path

The `scalarProductPath` [Euler/CylinderPathProduct.lean:68-71]() defines a scalar product for paths of `LiftL2 P` fields. This product leverages the `productHqBilinear` from the `H6` algebra (a Sobolev space on the cylinder) and the `valueOperator` to project the result back to `LiftL2 P`.

```lean
def scalarProductPath : C(K,LiftL2 P) :=
  (valueOperator P 6).compLeftContinuous ℝ K
    (pathBilinear (productHqBilinear P (by norm_num : 6 ≤ 6) L hL)
      (sobolevPath P 6 p hp) (sobolevPath P 6 q hq))
```
The `scalarProductPath_orbit` theorem [Euler/CylinderPathProduct.lean:94-105]() proves that the translation orbit of this scalar product path is `ContDiff`, which is vital for Gevrey regularity analysis. The `scalarProductPath_ae` [Euler/CylinderPathProduct.lean:106-113]() and `pointField_scalarProductPath` [Euler/CylinderPathProduct.lean:115-125]() theorems establish that this constructed path accurately represents the pointwise scalar product almost everywhere and for the smooth representative, respectively.

### Bilinear Product Path

A more general `bilinearProductPath` [Euler/CylinderPathBilinear.lean:49]() is constructed for arbitrary fixed bilinear vector operations. This is done by decomposing the operation into components using `component` [Euler/CylinderPathBilinear.lean:16-17]() and `basisVector` [Euler/CylinderPathBilinear.lean:23](), applying the `scalarProductPath` to each component, and then summing the results.

```lean
def bilinearProductPath : C(K,LiftL2 P) := ∑ i : Fin 3, bilinearTerm P B p q hp hq i
```
The `bilinearProductPath_orbit` [Euler/CylinderPathBilinear.lean:51-54]() ensures the `ContDiff` property of its translation orbit. Similar to the scalar product, `bilinearProductPath_ae` [Euler/CylinderPathBilinear.lean:65-78]() and `pointField_bilinearProductPath` [Euler/CylinderPathBilinear.lean:80-91]() confirm its pointwise behavior.

Sources:
- [Euler/CylinderPathProduct.lean:41-42]()
- [Euler/CylinderPathProduct.lean:43-44]()
- [Euler/CylinderPathProduct.lean:48-52]()
- [Euler/CylinderPathProduct.lean:54-59]()
- [Euler/CylinderPathProduct.lean:68-71]()
- [Euler/CylinderPathProduct.lean:94-105]()
- [Euler/CylinderPathProduct.lean:106-113]()
- [Euler/CylinderPathProduct.lean:115-125]()
- [Euler/CylinderPathBilinear.lean:16-17]()
- [Euler/CylinderPathBilinear.lean:23]()
- [Euler/CylinderPathBilinear.lean:49]()
- [Euler/CylinderPathBilinear.lean:51-54]()
- [Euler/CylinderPathBilinear.lean:65-78]()
- [Euler/CylinderPathBilinear.lean:80-91]()

## Elapsed-Time Gluing and Concatenation

The `EulerElapsedTimePathGluing` namespace provides tools for joining two continuous paths, `u` and `v`, defined over different time intervals `[0, τ]` and `[0, S-τ]` respectively, into a single path over `[0, S]`. This is crucial for constructing solutions over extended time domains.

The `join` function [Euler/ElapsedTimePathGluing.lean:32]() performs this concatenation, requiring that the paths match at the junction point (`hmatch`). The `join_eq_projection` theorem [Euler/ElapsedTimePathGluing.lean:34-40]() relates `join` to a projection operation. The `join_left` [Euler/ElapsedTimePathGluing.lean:58-63]() and `join_right` [Euler/ElapsedTimePathGluing.lean:65-74]() theorems confirm that the joined path correctly reproduces the original paths in their respective domains.

A key property is that differentiation holds across the junction point, as shown by `join_hasDerivWithinAt` [Euler/ElapsedTimePathGluing.lean:76-110](). This ensures that the joined path maintains the necessary regularity.

For paths that depend on a parameter `x`, `join_contDiff` [Euler/ElapsedTimePathGluing.lean:119-124]() proves that if the original paths are `ContDiff` with respect to `x`, the joined path also is.

The `join_map` theorem [Euler/ElapsedTimePathNaturality.lean:22-33]() states that a continuous linear map `L` commutes with the `join` operation. This property is extended to spatial translations in `join_translation` [Euler/ElapsedTimePathNaturality.lean:47-50](), which is then used to prove that the translation orbit of a joined path is `ContDiff` (`join_orbit_contDiff` [Euler/ElapsedTimePathNaturality.lean:55-64]()).

Finally, `join_orbit_block` [Euler/ElapsedTimePathNaturality.lean:66-77]() provides a crucial bound: the Sobolev block of the joined path's translation orbit is bounded by the sum of the blocks of the individual paths. This means that gluing paths does not introduce new regularity costs beyond what is present in the constituent parts.

Sources:
- [Euler/ElapsedTimePathGluing.lean:32]()
- [Euler/ElapsedTimePathGluing.lean:34-40]()
- [Euler/ElapsedTimePathGluing.lean:58-63]()
- [Euler/ElapsedTimePathGluing.lean:65-74]()
- [Euler/ElapsedTimePathGluing.lean:76-110]()
- [Euler/ElapsedTimePathGluing.lean:119-124]()
- [Euler/ElapsedTimePathNaturality.lean:22-33]()
- [Euler/ElapsedTimePathNaturality.lean:47-50]()
- [Euler/ElapsedTimePathNaturality.lean:55-64]()
- [Euler/ElapsedTimePathNaturality.lean:66-77]()

## Initial and Terminal Amplitude Bounds

The amplitude bounds ensure that the magnitude of solutions and their derivatives can be controlled based on the amplitude of the initial data and forcing terms. These bounds are critical for proving well-posedness and breakdown criteria.

### Amplitude Bound for Forcing

The `amplitude_bound` theorem [Euler/TransversePacketAmplitude.lean:22-85]() in `EulerTransversePacketProvider` establishes that if an operator `S` is homogeneous with respect to the forcing term `G` (i.e., `S (a • G) = a • S G`), then a unit-amplitude bound for `S G` can be scaled to any non-negative amplitude `A`.

```lean
theorem amplitude_bound
    (S : ∀ {r : VectorField}, Forcing P D r → C(Icc (0 : ℝ) D.T,LiftL2 P))
    (hs : ∀ {r} (G : Forcing P D r), ContDiff ℝ ∞ (fun a => pathTranslate P a (S G)))
    (hm : ∀ {r r'} (G : Forcing P D r) (H : Forcing P D r') (a : ℝ),
      H.path = a • G.path → S H = a • S G)
    (g : C(Icc (0 : ℝ) D.T,ℝ)) (hg : ∀ t, 0 < g t)
    (directions : ι → LiftTangent) (q : ℕ) (R C : ℝ) (d e : ℕ)
    (hunit : ∀ {r} (G : Forcing P D r),
      (∀ n, block directions q (fun a => pathTranslate P a
        (normalize g hg (HistoryData.forcingPath G))) n 0 ≤ majorant R d n) →
      ∀ n, block directions q (fun a => pathTranslate P a (normalize g hg (S G))) n 0 ≤ C*majorant R e n)
    {r : VectorField} (G : Forcing P D r) (A : ℝ) (hA : 0 ≤ A)
    (hb : ∀ n, block directions q (fun a => pathTranslate P a
      (normalize g hg (HistoryData.forcingPath G))) n 0 ≤ A*majorant R d n)
    (n : ℕ) :
    block directions q (fun a => pathTranslate P a (normalize g hg (S G))) n 0 ≤
      (C*A)*majorant R e n := by
  -- ... proof details ...
```
This theorem is applied to various quantities:
- `velocity_bound` [Euler/TransversePacketForwardNorms.lean:29-41]() and `derivative_bound` [Euler/TransversePacketForwardNorms.lean:43-55]() for the full velocity and derivative paths of the forward solution.
- `velocity_common_bound` [Euler/TransversePacketForwardNorms.lean:57-62]() and `derivative_common_bound` [Euler/TransversePacketForwardNorms.lean:64-69]() provide common bounds for these quantities.

### Amplitude Bound for Initial Data

Similarly, `initial_amplitude_bound` [Euler/PacketInitialAmplitude.lean:20-73]() applies to operators `S` that are homogeneous with respect to initial data `Y`.

```lean
theorem initial_amplitude_bound
    (S : InitialData P D → C(Icc (0 : ℝ) D.T,CylinderL2 P V))
    (hs : ∀ Y, ContDiff ℝ ∞ (fun a => pathTranslate P a (S Y)))
    (hm : ∀ Y Z (a : ℝ), Z.value = a • Y.value → S Z = a • S Y)
    (g : C(Icc (0 : ℝ) D.T,ℝ)) (hg : ∀ t, 0 < g t)
    (directions : ι → LiftTangent) (q : ℕ) (R C : ℝ) (d e : ℕ)
    (hunit : ∀ Y : InitialData P D,
      (∀ n, block directions q (fun a => translate P a (Y.value : CylinderL2 P U)) n 0 ≤ majorant R d n) →
      ∀ n, block directions q (fun a => pathTranslate P a (normalize g hg (S Y))) n 0 ≤ C*majorant R e n)
    (Y : InitialData P D) (A : ℝ) (hA : 0 ≤ A)
    (hb : ∀ n, block directions q (fun a => translate P a (Y.value : CylinderL2 P U)) n 0 ≤ A*majorant R d n)
    (n : ℕ) :
    block directions q (fun a => pathTranslate P a (normalize g hg (S Y))) n 0 ≤
      (C*A)*majorant R e n := by
  -- ... proof details ...
```

### Terminal Amplitude Bounds

The `EulerTransversePacketPrimary.Budget` namespace contains theorems for bounding the terminal data of the primary packet. These include:
- `terminal_bound` [Euler/TransversePacketPrimaryUnitBounds.lean:32-41]() for the endpoint coordinate.
- `past_velocity_bound` [Euler/TransversePacketPrimaryUnitBounds.lean:43-45]() and `past_derivative_bound` [Euler/TransversePacketPrimaryUnitBounds.lean:47-49]() for the past velocity and derivative.
- `future_velocity_bound` [Euler/TransversePacketPrimaryUnitBounds.lean:51-75]() and `future_derivative_bound` [Euler/TransversePacketPrimaryUnitBounds.lean:77-98]() for the future velocity and derivative.
- `velocity_unit_bound` [Euler/TransversePacketPrimaryUnitBounds.lean:100-115]() and `derivative_unit_bound` [Euler/TransversePacketPrimaryUnitBounds.lean:117-128]() for the full velocity and derivative paths.

Similarly, `EulerTransversePacketJoin.Budget` provides bounds for the joined transverse inverse:
- `history_forcing_bound` [Euler/TransversePacketJoinedUnitBounds.lean:34-45]() and `forward_forcing_bound` [Euler/TransversePacketJoinedUnitBounds.lean:47-58]() for the history and forward forcing.
- `terminal_bound` [Euler/TransversePacketJoinedUnitBounds.lean:64-74]() for the terminal data.
- `past_velocity_bound` [Euler/TransversePacketJoinedUnitBounds.lean:76-85]() and `past_derivative_bound` [Euler/TransversePacketJoinedUnitBounds.lean:87-96]() for the past velocity and derivative.
- `future_velocity_bound` [Euler/TransversePacketJoinedUnitBounds.lean:98-118]() and `future_derivative_bound` [Euler/TransversePacketJoinedUnitBounds.lean:120-140]() for the future velocity and derivative.

These bounds are crucial for controlling the growth of solutions and ensuring their regularity within the specified Sobolev and Gevrey norms.

### Bridging Natural Language to Code: Amplitude Bounds

```mermaid
graph TD
    subgraph "Natural Language Space"
        NL_AmplitudeBounds["Amplitude Bounds"]
        NL_Homogeneity["Homogeneity Property"]
        NL_UnitBoundScaling["Scaling Unit Bounds"]
        NL_InitialData["Initial Data"]
        NL_ForcingTerm["Forcing Term"]
        NL_TerminalData["Terminal Data"]
    end

    subgraph "Code Entity Space"
        CE_AmplitudeBound["`amplitude_bound` (Euler/TransversePacketAmplitude.lean:22-85)"]
        CE_InitialAmplitudeBound["`initial_amplitude_bound` (Euler/PacketInitialAmplitude.lean:20-73)"]
        CE_PairAmplitudeBound["`pair_amplitude_bound` (Euler/TransversePacketPairAmplitude.lean:20-103)"]
        CE_HomogeneityTheorem["`hm` parameter in amplitude bounds"]
        CE_VelocityBound["`velocity_bound` (Euler/TransversePacketForwardNorms.lean:29-41)"]
        CE_DerivativeBound["`derivative_bound` (Euler/TransversePacketForwardNorms.lean:43-55)"]
        CE_TerminalBoundPrimary["`terminal_bound` (Euler/TransversePacketPrimaryUnitBounds.lean:32-41)"]
        CE_PastVelocityBoundPrimary["`past_velocity_bound` (Euler/TransversePacketPrimaryUnitBounds.lean:43-45)"]
        CE_FutureVelocityBoundPrimary["`future_velocity_bound` (Euler/TransversePacketPrimaryUnitBounds.lean:51-75)"]
        CE_TerminalBoundJoined["`terminal_bound` (Euler/TransversePacketJoinedUnitBounds.lean:64-74)"]
        CE_PastVelocityBoundJoined["`past_velocity_bound` (Euler/TransversePacketJoinedUnitBounds.lean:76-85)"]
        CE_FutureVelocityBoundJoined["`future_velocity_bound` (Euler/TransversePacketJoinedUnitBounds.lean:98-118)"]
    end

    NL_AmplitudeBounds --> NL_Homogeneity
    NL_Homogeneity --> CE_HomogeneityTheorem
    NL_UnitBoundScaling --> CE_AmplitudeBound
    NL_UnitBoundScaling --> CE_InitialAmplitudeBound
    NL_UnitBoundScaling --> CE_PairAmplitudeBound

    NL_InitialData --> CE_InitialAmplitudeBound
    NL_ForcingTerm --> CE_AmplitudeBound
    NL_ForcingTerm --> CE_PairAmplitudeBound

    CE_AmplitudeBound -- "Applied to" --> CE_VelocityBound
    CE_AmplitudeBound -- "Applied to" --> CE_DerivativeBound

    NL_TerminalData --> CE_TerminalBoundPrimary
    NL_TerminalData --> CE_PastVelocityBoundPrimary
    NL_TerminalData --> CE_FutureVelocityBoundPrimary
    NL_TerminalData --> CE_TerminalBoundJoined
    NL_TerminalData --> CE_PastVelocityBoundJoined
    NL_TerminalData --> CE_FutureVelocityBoundJoined
```
Sources:
- [Euler/TransversePacketAmplitude.lean:22-85]()
- [Euler/PacketInitialAmplitude.lean:20-73]()
- [Euler/TransversePacketPairAmplitude.lean:20-103]()
- [Euler/TransversePacketForwardNorms.lean:29-41]()
- [Euler/TransversePacketForwardNorms.lean:43-55]()
- [Euler/TransversePacketForwardNorms.lean:57-62]()
- [Euler/TransversePacketForwardNorms.lean:64-69]()
- [Euler/TransversePacketPrimaryUnitBounds.lean:32-41]()
- [Euler/TransversePacketPrimaryUnitBounds.lean:43-45]()
- [Euler/TransversePacketPrimaryUnitBounds.lean:47-49]()
- [Euler/TransversePacketPrimaryUnitBounds.lean:51-75]()
- [Euler/TransversePacketPrimaryUnitBounds.lean:77-98]()
- [Euler/TransversePacketPrimaryUnitBounds.lean:100-115]()
- [Euler/TransversePacketPrimaryUnitBounds.lean:117-128]()
- [Euler/TransversePacketJoinedUnitBounds.lean:34-45]()
- [Euler/TransversePacketJoinedUnitBounds.lean:47-58]()
- [Euler/TransversePacketJoinedUnitBounds.lean:64-74]()
- [Euler/TransversePacketJoinedUnitBounds.lean:76-85]()
- [Euler/TransversePacketJoinedUnitBounds.lean:87-96]()
- [Euler/TransversePacketJoinedUnitBounds.lean:98-118]()
- [Euler/TransversePacketJoinedUnitBounds.lean:120-140]()

---

