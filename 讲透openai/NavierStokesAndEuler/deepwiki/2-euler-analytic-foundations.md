<!-- source: DeepWiki mcp.deepwiki.com · repo openai/NavierStokesAndEuler · page 2 Euler: Analytic Foundations · fetched 2026-10-26 -->

# Euler: Analytic Foundations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Euler/BoundedCoefficientJets.lean](Euler/BoundedCoefficientJets.lean)
- [Euler/BoundedCoefficientSmooth.lean](Euler/BoundedCoefficientSmooth.lean)
- [Euler/CylinderCompactTranslation.lean](Euler/CylinderCompactTranslation.lean)
- [Euler/LpCompactTranslation.lean](Euler/LpCompactTranslation.lean)
- [Euler/LpSmoothField.lean](Euler/LpSmoothField.lean)
- [Euler/LpSmoothFieldJets.lean](Euler/LpSmoothFieldJets.lean)
- [Euler/MeanCoefficientFrame.lean](Euler/MeanCoefficientFrame.lean)
- [Euler/MeanCoefficientPath.lean](Euler/MeanCoefficientPath.lean)
- [Euler/MeanCoefficientPathJets.lean](Euler/MeanCoefficientPathJets.lean)
- [Euler/MeanCoefficientSpatial.lean](Euler/MeanCoefficientSpatial.lean)
- [Euler/PacketCylinderCoefficientBounds.lean](Euler/PacketCylinderCoefficientBounds.lean)
- [Euler/PacketMatrixCoefficientGevrey.lean](Euler/PacketMatrixCoefficientGevrey.lean)
- [Euler/PacketPressureJet.lean](Euler/PacketPressureJet.lean)
- [Euler/PacketSlicedAssembly.lean](Euler/PacketSlicedAssembly.lean)
- [Euler/PacketSlicedJets.lean](Euler/PacketSlicedJets.lean)
- [Euler/SmoothCoefficientPath.lean](Euler/SmoothCoefficientPath.lean)
- [Euler/SmoothCoefficientTimeRestriction.lean](Euler/SmoothCoefficientTimeRestriction.lean)
- [Euler/SmoothTimeField.lean](Euler/SmoothTimeField.lean)
- [Euler/SmoothTimeFieldAlgebra.lean](Euler/SmoothTimeFieldAlgebra.lean)
- [Euler/SmoothTimeFieldComposition.lean](Euler/SmoothTimeFieldComposition.lean)
- [Euler/SmoothTimeFieldDerivativeBounds.lean](Euler/SmoothTimeFieldDerivativeBounds.lean)
- [Euler/SmoothTimeFieldJoint.lean](Euler/SmoothTimeFieldJoint.lean)
- [Euler/SmoothTimeFieldLinear.lean](Euler/SmoothTimeFieldLinear.lean)
- [Euler/SmoothTimeFieldPrecomp.lean](Euler/SmoothTimeFieldPrecomp.lean)
- [Euler/SmoothTimeFieldRestriction.lean](Euler/SmoothTimeFieldRestriction.lean)
- [Euler/SmoothTimeFieldSecondJoint.lean](Euler/SmoothTimeFieldSecondJoint.lean)
- [Euler/SmoothTimeFieldTimeJets.lean](Euler/SmoothTimeFieldTimeJets.lean)
- [Euler/TransversePacketTimeData.lean](Euler/TransversePacketTimeData.lean)

</details>



This page provides a high-level overview of the foundational analytic structures and concepts used throughout the Euler library. These components form a reusable analysis layer, enabling the rigorous formalization of smooth fields, jet calculus, function spaces, and the specific cylinder geometry relevant to the Euler equations. Detailed explanations and proofs for each topic are provided in their respective child pages.

## Smooth Time Fields and Jet Calculus

The codebase extensively uses `SmoothTimeField` [Euler/SmoothTimeField.lean:13-20]() and `SmoothCoefficientPath` [Euler/SmoothCoefficientPath.lean:35-40]() structures to represent functions that are smooth both spatially and over a compact time interval. These structures encapsulate a field and its spatial jets (iterated Fréchet derivatives), ensuring all-order spatial smoothness.

The `SmoothTimeField` [Euler/SmoothTimeField.lean:13-20]() is defined for a general real normed domain `E` and codomain `V`, parameterized by a compact topological space `K` (often representing time). It stores the field itself as a continuous map `C(K, E →ᵇ V)` and its spatial jets `jet n` as continuous maps `C(K, E →ᵇ (E [×n]→L[ℝ] V))`. The `jet_eq` [Euler/SmoothTimeField.lean:19]() theorem asserts that `jet n t x` is indeed the `n`-th iterated Fréchet derivative of the field at `(t, x)`.

Operations such as `derivative` [Euler/SmoothTimeField.lean:65-78](), `map` [Euler/SmoothTimeFieldLinear.lean:29-39](), and `precompLinear` [Euler/SmoothTimeFieldPrecomp.lean:30-41]() are defined for `SmoothTimeField`s, allowing for the manipulation and transformation of these smooth fields while preserving their jet properties. For instance, `derivative` [Euler/SmoothTimeField.lean:65-78]() computes the spatial derivative of a `SmoothTimeField`, returning a new `SmoothTimeField` whose values are linear maps.

The `SmoothCoefficientPath` [Euler/SmoothCoefficientPath.lean:35-40]() is a specialized version of `SmoothTimeField` where the spatial domain `E` is fixed to `Space` (representing $\mathbb{R}^3$). It also provides operations like `derivative` [Euler/SmoothCoefficientPath.lean:80-93]() and `translation_contDiff` [Euler/SmoothCoefficientPath.lean:127-129](), which establishes all-order smoothness of the translation orbit in the uniform time-path topology.

For details, see [Smooth Time Fields and Jet Calculus](#2.1).

### Smooth Field and Jet Structure
```mermaid
classDiagram
    direction LR
    class "SmoothTimeField<K, E, V>" {
        +field: C(K, E →ᵇ V)
        +smooth: ∀ t, ContDiff ℝ ∞ (field t : E → V)
        +jet: (n : ℕ) → C(K, E →ᵇ (E [×n]→L[ℝ] V))
        +jet_eq: ∀ n t x, jet n t x = iteratedFDeriv ℝ n (field t : E → V) x
        +derivative(): SmoothTimeField<K, E, E →L[ℝ] V>
        +map(L: V →L[ℝ] W): SmoothTimeField<K, E, W>
        +precompLinear(L: F →L[ℝ] E): SmoothTimeField<K, F, V>
    }
    class "SmoothCoefficientPath<K, V>" {
        +field: C(K, Space →ᵇ V)
        +smooth: ∀ t, ContDiff ℝ ∞ (field t : Space → V)
        +jet: (n : ℕ) → C(K, Space →ᵇ (Space [×n]→L[ℝ] V))
        +jet_eq: ∀ n t x, jet n t x = iteratedFDeriv ℝ n (field t : Space → V) x
        +derivative(): SmoothCoefficientPath<K, Space →L[ℝ] V>
        +translation_contDiff(): ContDiff ℝ ∞ (translated field)
    }
    SmoothTimeField <|-- SmoothCoefficientPath : "specializes E to Space"
    SmoothTimeField --> "1" C_K_E_V : field
    SmoothTimeField --> "N" C_K_E_JetV : jet
    SmoothCoefficientPath --> "1" C_K_Space_V : field
    SmoothCoefficientPath --> "N" C_K_Space_JetV : jet
    C_K_E_V["C(K, E →ᵇ V)"]
    C_K_E_JetV["C(K, E →ᵇ (E [×n]→L[ℝ] V))"]
    C_K_Space_V["C(K, Space →ᵇ V)"]
    C_K_Space_JetV["C(K, Space →ᵇ (Space [×n]→L[ℝ] V))"]
```
Sources: [Euler/SmoothTimeField.lean:13-20](), [Euler/SmoothCoefficientPath.lean:35-40](), [Euler/SmoothTimeField.lean:65-78](), [Euler/SmoothTimeFieldLinear.lean:29-39](), [Euler/SmoothTimeFieldPrecomp.lean:30-41](), [Euler/SmoothCoefficientPath.lean:80-93](), [Euler/SmoothCoefficientPath.lean:127-129]()

## Function Spaces: Lp, Sobolev, Gevrey

The library utilizes various function spaces, including $L^p$, Sobolev, and Gevrey spaces, to characterize the regularity of fields.

The `SmoothL2Field` [Euler/LpSmoothField.lean:31-34]() structure represents functions that are smooth and whose spatial derivatives of all orders are in $L^2$. This is crucial for establishing translation regularity, as demonstrated by `translation_contDiff` [Euler/LpSmoothField.lean:85-87](), which proves that the translation orbit of such a field is infinitely differentiable. The `jetLp` [Euler/LpSmoothField.lean:46]() function provides the $L^2$ norm of the iterated Fréchet derivatives.

For fields with compact support, `CompactField` [Euler/CylinderCompactTranslation.lean:28-31]() is used, which ensures that the field and its derivatives are $L^2$-integrable. The `compactField_hasFDerivAt` [Euler/LpCompactTranslation.lean:70-73]() theorem shows that the Fréchet derivative of the translation map for such fields agrees with the $L^2$ translation derivative.

The `BoundedSmoothField` [Euler/BoundedCoefficientSmooth.lean:48-52]() structure describes smooth fields with globally bounded derivatives of every order. Its `translation_contDiff` [Euler/BoundedCoefficientSmooth.lean:96-97]() theorem asserts that spatial translations of such fields are smooth with respect to the translation parameter.

Gevrey regularity classes are implicitly used through concepts like `majorant` [Euler/PacketMatrixCoefficientGevrey.lean:27]() in bounding iterated derivatives, particularly in the context of operator composition and estimates.

For details, see [Function Spaces: Lp, Sobolev, Gevrey](#2.2).

### Function Space Hierarchy
```mermaid
classDiagram
    direction LR
    class "SmoothL2Field<V>" {
        +field: Space → V
        +smooth: ContDiff ℝ ∞ field
        +integrable: ∀ n, MemLp (iteratedFDeriv ℝ n field) 2 volume
        +toLp(): L2Space V
        +jetLp(n: ℕ): L2Space (Space [×n]→L[ℝ] V)
        +translation_contDiff(): ContDiff ℝ ∞ (translation orbit)
    }
    class "CompactField<P, V>" {
        +field: LiftDomain P → V
        +compact: HasCompactSupport field
        +smooth: ∀ x, ContDiff ℝ ∞ (localFieldLift P field x)
        +toLp(): CylinderL2 P V
        +hasFDerivAt_zero(): HasFDerivAt (translation orbit)
    }
    class "BoundedSmoothField<V>" {
        +field: Space →ᵇ V
        +smooth: ContDiff ℝ ∞ (field : Space → V)
        +bounded: ∀ n, ∃ C, ∀ x, ‖iteratedFDeriv ℝ n (field : Space → V) x‖ ≤ C
        +translation_contDiff(): ContDiff ℝ ∞ (translated field)
    }
    SmoothL2Field <|-- CompactField : "specializes to cylinder, adds compact support"
    SmoothL2Field <|-- BoundedSmoothField : "adds global derivative bounds"
```
Sources: [Euler/LpSmoothField.lean:31-34](), [Euler/LpSmoothField.lean:46](), [Euler/LpSmoothField.lean:85-87](), [Euler/CylinderCompactTranslation.lean:28-31](), [Euler/LpCompactTranslation.lean:70-73](), [Euler/BoundedCoefficientSmooth.lean:48-52](), [Euler/BoundedCoefficientSmooth.lean:96-97]()

## Cylinder Geometry and Coefficient Paths

The Euler equations are formalized on a cylinder domain, which introduces specific geometric considerations. This section outlines the structures and concepts related to this domain.

The `SmoothCoefficientPath` [Euler/SmoothCoefficientPath.lean:35-40]() structure, as mentioned above, is central to representing fields on this domain, where `Space` is $\mathbb{R}^3$. The `translation_contDiff` [Euler/SmoothCoefficientPath.lean:127-129]() theorem is particularly important here, as it guarantees that translating a smooth coefficient path along the spatial domain results in a smooth path in the space of coefficient paths.

The `EulerTransversePacketProvider.Data` [Euler/TransversePacketTimeData.lean:16]() structure, for example, uses `SmoothCoefficientPath`s for various components like `FInv.field` and `M.field` to describe the deformation and its inverse on the cylinder. Operations like `inverseDerivative` [Euler/TransversePacketTimeData.lean:30]() and `normalDerivative` [Euler/TransversePacketTimeData.lean:34]() are defined for these paths, and their smoothness under translation is established by `inverseDerivative_orbit` [Euler/TransversePacketTimeData.lean:102-104]() and `normalDerivative_orbit` [Euler/TransversePacketTimeData.lean:106-108]().

The `MatrixCoefficient` [Euler/PacketMatrixCoefficientGevrey.lean:25]() structure, used in packet construction, also relies on `SmoothCoefficientPath`s. It defines operations like `comp_bound` [Euler/PacketMatrixCoefficientGevrey.lean:25-45]() and `spatialDerivative_bound` [Euler/PacketMatrixCoefficientGevrey.lean:75-87]() which provide bounds for compositions and spatial derivatives of these coefficient paths, crucial for Gevrey regularity estimates.

For details, see [Cylinder Geometry and Coefficient Paths](#2.3).
Sources: [Euler/SmoothCoefficientPath.lean:35-40](), [Euler/SmoothCoefficientPath.lean:127-129](), [Euler/TransversePacketTimeData.lean:16](), [Euler/TransversePacketTimeData.lean:30](), [Euler/TransversePacketTimeData.lean:34](), [Euler/TransversePacketTimeData.lean:102-104](), [Euler/TransversePacketTimeData.lean:106-108](), [Euler/PacketMatrixCoefficientGevrey.lean:25](), [Euler/PacketMatrixCoefficientGevrey.lean:25-45](), [Euler/PacketMatrixCoefficientGevrey.lean:75-87]()

---

