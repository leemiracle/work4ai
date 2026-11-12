# MiniF2F

[![.github/workflows/ci.yml](https://github.com/google-deepmind/miniF2F/actions/workflows/ci.yml/badge.svg)](https://github.com/google-deepmind/miniF2F/actions/workflows/ci.yml)
[![Gitpod Ready-to-Code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/google-deepmind/miniF2F)

This repository is a fork of
[openai/miniF2F](https://github.com/openai/miniF2F), which is described in
[MiniF2F: a cross-system benchmark for formal Olympiad-level mathematics](https://arxiv.org/abs/2109.00110).

It contains Lean 4 translations of the Lean 3 problems in the original,
translated using [mathport](https://github.com/leanprover-community/mathport).

Compared to the original, this:

*   contains natural language docstrings taken from (best estimates of) the
    source of the original problems, to make identification of misformalizations
    easier.

    These descriptions originate from some combination of:

    *   The contest collection question archive on the
        [AoPS forums](https://artofproblemsolving.com/community/c13_contest_collections)
    *   The [MATH dataset](https://github.com/hendrycks/math)

*   has many fewer misformalizations, with all known false statements removed,
    and many statements strengthened to match the strength of the english
    statement.

*   simplifies the `Minif2fImport` strategy, instead importing all of mathlib.

This is the version of the benchmark on which AlphaProof is evaluated.

This is not an official Google product.
