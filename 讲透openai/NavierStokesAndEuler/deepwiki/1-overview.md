<!-- source: DeepWiki mcp.deepwiki.com · repo openai/NavierStokesAndEuler · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Euler/CanonicalPacketHorizons.lean](Euler/CanonicalPacketHorizons.lean)
- [Euler/EulerFiniteLifespan.lean](Euler/EulerFiniteLifespan.lean)
- [Euler/EulerProof.lean](Euler/EulerProof.lean)
- [Euler/H3CurlConvergence.lean](Euler/H3CurlConvergence.lean)
- [Euler/OrdinaryEulerCauchy.lean](Euler/OrdinaryEulerCauchy.lean)
- [Euler/OrdinaryEulerContinuation.lean](Euler/OrdinaryEulerContinuation.lean)
- [Euler/OrdinaryEulerEndpoint.lean](Euler/OrdinaryEulerEndpoint.lean)
- [Euler/OrdinaryEulerLocalCauchy.lean](Euler/OrdinaryEulerLocalCauchy.lean)
- [Euler/OrdinaryEulerStability.lean](Euler/OrdinaryEulerStability.lean)
- [Euler/OrdinaryEulerVaryingHorizon.lean](Euler/OrdinaryEulerVaryingHorizon.lean)
- [Euler/OrdinaryGradientLimit.lean](Euler/OrdinaryGradientLimit.lean)
- [Euler/PacketFiniteLifespan.lean](Euler/PacketFiniteLifespan.lean)
- [Euler/PacketStageContradiction.lean](Euler/PacketStageContradiction.lean)
- [Euler/PacketStageLocalExistence.lean](Euler/PacketStageLocalExistence.lean)
- [NavierStokes/ActualParticularPhysicalData.lean](NavierStokes/ActualParticularPhysicalData.lean)
- [NavierStokes/ActualSignedPhysicalData.lean](NavierStokes/ActualSignedPhysicalData.lean)
- [NavierStokes/InitialPhysicalData.lean](NavierStokes/InitialPhysicalData.lean)
- [NavierStokes/PhysicalParticularWave.lean](NavierStokes/PhysicalParticularWave.lean)

</details>



This repository contains Lean 4 formalizations of finite-time breakdown results for the 3D Euler and Navier–Stokes equations. It also includes the Comparator challenge harness, a framework for defining and testing mathematical challenges. The formalizations are organized into two main libraries: `Euler/` and `NavierStokes/`.

The `Euler/` library focuses on proving the finite-time lifespan of smooth solutions to the 3D incompressible Euler equations. This involves a detailed construction of a self-similar packet cascade, which ultimately leads to a contradiction with global regularity.

The `NavierStokes/` library addresses the 3D incompressible Navier–Stokes equations. It explores potential breakdown scenarios, including a candidate for finite-time singularity in $\mathbb{R}^3$, and develops the necessary machinery for viscous corrections and limit arguments.

## Repository Layout and Build

The codebase is structured into several key directories: `Euler/`, `NavierStokes/`, `NavierStokes/R3/`, and `ComparatorChallenges/`. The `Euler/` and `NavierStokes/` directories contain the core formalizations for each equation. `NavierStokes/R3/` specifically houses the analysis for the Navier–Stokes equations in the whole space $\mathbb{R}^3$. The `ComparatorChallenges/` directory contains JSON files that define challenges for the Comparator harness, allowing for automated testing and verification of specific mathematical statements. The project uses `lake` for its build system.

For details on the directory structure, the `lake` build process, and how the Comparator challenge JSONs are executed, see [Repository Layout and Build](#1.1).

Sources:
- [Euler/EulerProof.lean:1-92]()

## Main Theorems and Problem Statements

The primary goal of this repository is to formally prove significant results regarding the finite-time behavior of solutions to the Euler and Navier–Stokes equations.

For the Euler equations, a key result is the existence of compactly supported smooth initial data that leads to a finite-lifespan solution. This is formalized by the `exists_compact_smooth_finite_lifespan` theorem.

For the Navier–Stokes equations, the repository investigates breakdown statements, including a specific option (D) related to potential singularity formation. This includes analysis in periodic domains and the whole space $\mathbb{R}^3$.

For a detailed exposition of these formal statements and their locations within the codebase, see [Main Theorems and Problem Statements](#1.2).

Sources:
- [Euler/EulerProof.lean:97-101]()

## Proof Strategy at a Glance

The formalization employs distinct strategies for the Euler and Navier–Stokes equations, building upon a common foundation of analytical tools.

For the Euler equations, the proof relies on constructing a self-similar packet cascade. This involves defining and analyzing "packets" of fluid motion that interact in a way designed to lead to a finite-time singularity. The construction iteratively refines these packets, ensuring that their properties (such as regularity and energy) are maintained or amplified in a controlled manner until a breakdown criterion is met.

For the Navier–Stokes equations, the approach involves developing machinery for viscous corrections and limit arguments. This allows for the study of solutions as viscosity approaches zero, bridging the gap between Navier–Stokes and Euler. The repository also constructs a candidate solution for the periodic and $\mathbb{R}^3$ cases, which is then analyzed for potential breakdown.

The overall strategy involves a careful composition of these analytical pieces, leveraging Lean's capabilities for formal verification.

For a more in-depth narrative of the proof strategies, including the self-similar packet cascade, viscous correction/limit machinery, and the periodic/R3 candidate for Navier–Stokes, see [Proof Strategy at a Glance](#1.3).

Sources:
- [Euler/EulerProof.lean:97-101]()
- [NavierStokes/ActualSignedPhysicalData.lean:8-13]()
- [NavierStokes/InitialPhysicalData.lean:11-18]()
- [NavierStokes/ActualParticularPhysicalData.lean:9-15]()
- [NavierStokes/PhysicalParticularWave.lean:7-12]()
- [Euler/OrdinaryEulerCauchy.lean:4-5]()
- [Euler/OrdinaryEulerStability.lean:4-5]()
- [Euler/OrdinaryEulerContinuation.lean:4-5]()
- [Euler/OrdinaryEulerEndpoint.lean:4-5]()
- [Euler/PacketStageLocalExistence.lean:4-8]()
- [Euler/OrdinaryEulerVaryingHorizon.lean:4-5]()

---

