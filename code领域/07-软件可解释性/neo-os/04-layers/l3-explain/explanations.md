# Neo-OS L3 · Three-Layer Explanations (prototype)

> Auto-generated from L2.5 formal rules via GLM-4-plus. 
work4ai 三层讲透 methodology (Intuition → Math → Trace).


---

# ElectionSafety

*Anchor: Raft §5.2 / dsyme RE5 · Category: DISTRIBUTED CONSENSUS*

## Intuition
In any election, if two candidates each win more than half the votes, they must be the same person—otherwise, the total votes would exceed the actual number of voters, which is impossible. This rule prevents contradictory "majority" outcomes and ensures election integrity.

## Formal statement (the math)
The theorem states that for any list of voters and a voting function, if two candidates `c1` and `c2` each satisfy the condition that twice their vote count exceeds the total number of voters, then `c1` must equal `c2`. Mathematically, this enforces that no two distinct candidates can simultaneously hold a strict majority (>50%) of votes, as it would violate the pigeonhole principle (since `2 * (n/2 + 1) > n` for any integer `n`).

## Trace evidence (the code)
Consider 3 voters (`voters = [1, 2, 3]`) and a vote map where `vote 1 = Some A`, `vote 2 = Some A`, and `vote 3 = Some B`. Here, `votesFor voters vote A = 2` (so `2 * 2 > 3` holds), but `votesFor voters vote B = 1` (so `2 * 1 > 3` fails). If we incorrectly claimed both `A` and `B` satisfied the majority condition, the theorem would force `A = B`, exposing the contradiction. In a real system, this would prevent split-brain scenarios where two "leaders" are elected simultaneously.


---

# committedMono

*Anchor: Raft §5.4.2 / dsyme hcommitted_mono · Category: DISTRIBUTED CONSENSUS*

## Intuition
The `committedMono` rule ensures that a node's commitment index only moves forward, like a one-way street for progress—this prevents rollbacks and guarantees that once a log entry is committed, it stays committed, which is essential for consistency in distributed systems.

## Formal statement (the math)
The Lean4 invariant `Inv s := s.commitIndex ≥ 0 ∧ s.lastApplied ≤ s.commitIndex` mathematically enforces two constraints: (1) the commit index is always non-negative, and (2) the last applied log entry never exceeds the commit index. The theorem `Inv_preserved_over_trace` proves that if these conditions hold before processing a list of events (`es`), they will also hold afterward in the final state (`final s es`), ensuring monotonicity of the commit index over any trace of events.

## Trace evidence (the code)
Consider a node with `commitIndex = 2` and `lastApplied = 2` (satisfying `Inv`). If it processes an event that advances `commitIndex` to 3 (e.g., a successful AppendEntries RPC quorum), the invariant holds (`lastApplied` remains ≤ `commitIndex`). If instead, a buggy implementation allowed `commitIndex` to drop to 1, the invariant would violate `lastApplied ≤ commitIndex` (since `lastApplied = 2 > 1`), causing the node to reapply already committed entries or lose committed data—an observable bug violating Raft's progress guarantees.


---

# spinlockPreempt

*Anchor: Linux Documentation/locking/spinlocks.rst · Category: OS KERNEL (synchronization)*

## Intuition
Spinlocks are like a strict handshake agreement: once you grab it, you must finish your task without interruption (preemption disabled), or the system could freeze if another thread tries to sleep while holding the lock. This rule ensures the handshake is never broken by tracking that preemption is disabled whenever a lock is held.

## Formal statement (the math)
The invariant `Inv s := s.preemptCount ≥ 0 ∧ (s.lockHeld = true → s.preemptCount ≥ 1)` states two conditions: (1) the preemption counter is never negative, and (2) if a lock is held (`s.lockHeld = true`), then preemption must be disabled (`s.preemptCount ≥ 1`). The theorem `Inv_preserved_over_trace` proves that for any system state `s` and list of events `es`, if the initial state satisfies `Inv s` and the events `es` are valid (`OK s es`), then the final state after executing `es` will also satisfy `Inv`.

## Trace evidence (the code)
Consider a trace where a thread acquires a spinlock (event `lock_acquire`), which decrements `preemptCount` to 0 (disabling preemption), then a scheduler event `sched_preempt` attempts to preempt the thread. The `OK s es` check would fail here because `sched_preempt` is invalid when `preemptCount = 0`, preventing a violation where the thread could sleep while holding the lock. If this check were bypassed, the thread might sleep, causing a deadlock as other threads spin forever waiting for the lock.


---

# logMatchingSingle

*Anchor: Raft §5.4.1 / dsyme LogMatching · Category: DISTRIBUTED CONSENSUS*

## Intuition
Imagine two witnesses reading the same line in a shared ledger—if they both see the same entry number and timestamp, they must be describing the exact same event. This rule ensures that a log entry at a specific position can't have conflicting content, which is fundamental for distributed systems to agree on the truth.

## Formal statement (the math)
The Lean4 theorem `logMatchingSingle` states that for any log (a list of term-entry pairs), if two observations `h1` and `h2` both report the same term `t` and index `i`, then the corresponding entries `e1` and `e2` must be identical. Mathematically, this enforces the invariant that a log's index-term pair uniquely determines its entry, preventing ambiguity in the log's state.

## Trace evidence (the code)
Consider a Raft log `[(1, 10), (2, 20), (2, 30)]` where a leader appends `(2, 30)` but a follower's log has `(2, 25)` at the same index. If the leader tries to commit index 2, `logMatchingSingle` would fail because `h1 = log.get? 2 = some (2, 30)` and `h2 = log.get? 2 = some (2, 25)` imply `30 = 25`, a contradiction. This violation would manifest as a commit failure, forcing log reconciliation to restore consistency.
