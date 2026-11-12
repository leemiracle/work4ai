# Profiling Snapshots

Dated profiling snapshots live in this folder (`YYYY-MM-DD.md`). The index + rules are maintained in
`../baselines.md` under the "Profiling snapshots" section.

This folder can also hold small, deterministic repro notes for known parity gaps. Those snapshots are
not promotion gates. They exist to preserve one-command repros with the exact failure shape and code
pointers needed to debug or regression-test the issue later.

Current snapshots:

- [2026-05-27-promoted-incremental-arrow.md](2026-05-27-promoted-incremental-arrow.md):
  Arrow-only promoted incremental profile on the canonical replay bundle.
- [2026-05-25-promoted-incremental-preflight.md](2026-05-25-promoted-incremental-preflight.md):
  Arrow promoted-incremental tiny preflight and canonical Arrow profiler.
- [2026-03-02.md](2026-03-02.md): gate rerun refresh snapshot.
- [2026-05-23.md](2026-05-23.md): SPECTER/vector clone cleanup priority check.
