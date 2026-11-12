# Automotive Object-Level Metrics

Given an object-check `*.objects.results.json`, this library decides — **per object** — whether a world model
(RDS-HQ) object is **present**, **missing** or **misaligned**, whether a traffic light shows the **wrong
color** or **conflicting colors**, and which **hallucinated** objects are ego-relevant. It covers dynamic
objects, traffic lights, and the lane graph (lane lines and road boundaries).

The object check itself is deliberately unopinionated about those words: `checks/objects/single_view/` emits
per-frame correspondence scores and unexplained image regions, and stops there. Turning that into a verdict
about one object is a separate, policy-laden step, and this library is where that policy is defined. Anything
that reports on object quality — evaluation pipelines, KPIs, dashboards, regression tooling — should resolve
its verdicts here rather than re-deriving them from the score matrix, so that two reports of "12% of cars are
missing" mean the same thing.

## The rules

### An object is **missing** when its box was drawn empty

The mean of a track's scored frames is indistinguishable from zero — nothing in the rendered image was
classified as that object's type, anywhere inside its projected box, in any frame.

This is deliberately **not** a score-below-threshold test. An object that scores a mean of 0.08 is *present but
badly rendered*, and calling it missing conflates two different failures: the model that omitted an object and
the model that drew a poor one. Only the first is an existence failure, and a count that mixes them is
unusable as a generation-quality signal.

This is the rule for every box-shaped object: vehicles, VRUs and traffic lights.

### A lane line or road boundary is **missing** when its mean falls below a measured cutoff

A polyline projects to a thin ribbon whose box is mostly road, so its score runs low even when the line is
drawn correctly, and the empty-box test above would call a barely traced line present. The lane graph takes a
cutoff measured for it instead: the mean of the scored frames below **0.1**, or below **0.002** for a lane line
whose predominant paint style is dashed — its periodic gaps leave most of its box unpainted. Both cutoffs were
tuned on paired add-object perturbation trials, a world-model copy of a real line scored against the real line
it was copied from, over ~2000 lane-line and ~2000 road-boundary trials.

The style is read from `tracks[].lane_style`, which the static check records from the line's RDS-HQ
attributes: a style naming a dashed stroke and no solid one, in any case, selects the dashed cutoff. A hybrid
double line (`SOLID_DASHED`, `DASHED_SOLID`) takes the solid cutoff, since its solid stroke paints a continuous
stripe and it scores like a solid line. A lane line whose result records no style takes the solid cutoff. No
misalignment signal is defined for a polyline.

### An object is **misaligned** when it is drawn, but mostly outside its box

The 85th percentile of a track's scored frames is low but non-zero: `0 < p85 < 0.35`.

Both bounds carry weight. The upper bound is what makes it a defect; the lower bound is what keeps it disjoint
from *missing*, which is a different question with a different answer. The percentile rather than the mean,
because a partly-contained object scores near zero on most of its frames — the mean cannot separate that from
"never drawn at all", but the upper tail can.

### An object is **extra** when nothing in the world model explains it

The check emits hallucination tracks: image regions it could not attribute to any world-model object. One
counts when its `relevancy` — the number of frames in which its box overlapped the drivable surface — is at
least 1, which is what makes it an object the ego actually has to contend with rather than scenery.

Relevancy is only meaningful when the tracker was given a road mask. Where it was not, the field is
structurally zero and the gate is not applied, rather than silently discarding every hallucination. The static
check runs without one, so every traffic-light and lane-graph hallucination track counts.

### A traffic light is in the **wrong state** when a color phase was rendered wrong

A light cycles color over a clip, so there is no single expected color for a track: its frames are split
into **episodes** of constant ground-truth color and each is judged alone. An episode trips when its mean
state score falls below `0.5`, or when it has two consecutive frames below it — a brief wrong-color burst
that the mean would otherwise wash out.

Judging per episode is what makes the verdict attributable: a light rendered correctly through its green
phase and wrongly through its red one is wrong, and a per-track average would dilute that to "mostly fine".

The rule **declines** — reports `null`, not `false` — for a light whose frames name no ground-truth color.
That is the one case where the question cannot be asked rather than merely answered "no": with no color to
have been wrong against, every frame would fall into a single nameless episode split only on frame
contiguity, and a light whose scores happen to dip would come back a confident `true`. A result file that
carries per-frame state scores but no `expected_state` is exactly that shape, so the guard is what keeps such
a file reporting "not measured" instead of a fabricated count.

### A traffic light is **conflicting** when it shows two colors at once

The multi-color score is the second-most-prominent color's share of the dominant one, so a high value means
one light is signalling two things. A conflict is typically brief and intermittent, so this reads a **run of
at least two contiguous frames** above `0.5` rather than a per-track mean — the mean drowns a few conflicting
frames in a mostly-clean track, and a single spike is usually mask noise.

Both rules depend on the frame-space normalization described under
[Traffic lights need a dense frame axis](#4-traffic-lights-need-a-dense-frame-axis).

## Contents

| Target | Description |
| --- | --- |
| `result_view` | Reads a result JSON into typed views: parses both matrix formats, resolves positional `track_idx` to stable track ids, applies the importance policy, and resolves hallucination detection indices into real boxes. The only place that knows about frame spaces |
| `taxonomy` | The object-type registry: group membership, hallucination class labels, and which signals each type defines, derived from `checks/utils/object_class_names` rather than restated |
| `rules` | The rules above as objects that evaluate themselves, and the protocols to implement your own |
| `policy` | Which rule applies to which object type, and the canonical set. Self-describing via `as_dict()` for stamping provenance into any output |
| `existence` | The per-object predicates |
| `augment` | Builds the `object_metrics` block for a result JSON and writes it back into the file |
| `tools/object_metrics` | Finds object-result JSON files, adds or replaces their `object_metrics` blocks, writes the augmented results in place or to a separate file, and optionally prints a per-type summary |
| `summary` | Per-object-type tabulation: observed, unscored, present, missing, misaligned, wrong-state, conflicting, hallucinated, and the rates over them |

## Usage

```python
import json
from pathlib import Path

from kpi.automotive.existence import is_misaligned, is_missing, relevant_hallucinations
from kpi.automotive.policy import default_policy
from kpi.automotive.result_view import ImportancePolicy, read_result
from kpi.automotive.summary import signal_summary
from kpi.automotive.taxonomy import Group

result_json = json.loads(Path("<clip>.dynamic.objects.results.json").read_text())
policy = default_policy(ImportancePolicy.EGO_RELEVANT)
view = read_result(result_json, importance=ImportancePolicy.EGO_RELEVANT)

# Per object
for track in view.tracks.values():
    print(track.track_id, track.object_type, is_missing(track, policy), is_misaligned(track, policy))

# Per object type
for object_type, row in signal_summary(view, policy).items():
    print(object_type, row.observed, row.missing, row.rates()["missing_rate"])

# Extra objects the render invented
extra = relevant_hallucinations(view, Group.FOUR_WHEELER, policy)
```

### Traffic lights

Color-state signals come from a light's per-frame rows and are independent of correspondence — a light can be
drawn (so not missing) and drawn the wrong color:

```python
import json
from pathlib import Path

from kpi.automotive.existence import is_conflicting, is_missing, is_wrong_state
from kpi.automotive.policy import default_policy
from kpi.automotive.result_view import ImportancePolicy, read_result

result_json = json.loads(Path("<clip>.static.objects.results.json").read_text())
policy = default_policy(ImportancePolicy.ALL_SCORED)
view = read_result(result_json, importance=ImportancePolicy.ALL_SCORED)

for track in view.tracks.values():
    if track.object_type != "TrafficLight":
        continue
    print(track.track_id,
          "missing:", is_missing(track, policy),
          "wrong color:", is_wrong_state(track, policy),
          "conflicting:", is_conflicting(track, policy),
          f"({len(track.state_frames)} state frames)")
```

A light the checker never sampled for color has no `state_frames`, and both color predicates return `None`
— unmeasured, not correct. `is_wrong_state` also returns `None` when the light's frames name no ground-truth
color, since there is nothing for the render to have been wrong against; `is_conflicting` still answers,
reading only the multi-color score. Every other object type returns `None` for both, since only lights carry
color state.

## Augmenting a result file

`tools/object_metrics` accepts one or more result JSON files or directories. It recursively searches directories
for `*.objects.results.json`, computes the metrics with the required importance policy, and either updates every
input with `--in-place` or writes a single input to `--output`. Unless `--quiet` is set, it also prints a per-type
summary. In-process callers can perform the same augmentation with `kpi.automotive.augment.augment_file`:

```bash
dazel run //kpi/automotive/tools:object_metrics -- \
    --importance ego_relevant --in-place /path/to/results/
```

It adds exactly one top-level key and leaves everything the check wrote byte-identical, so deleting that key
returns the original file. Elisions below are marked `...`; everything else is real output from a front-wide
clip:

```jsonc
{
  // everything the check wrote, untouched
  "track_ids": [...], "tracks": [...], "score_matrix": {...},
  "hallucination_tracks": [...], "hallucination_detections": {...},
  "processed_frame_ids": [...], "mean_score": ..., "metadata": {...},

  // the one added key
  "object_metrics": {
    "git_sha": "41a2f2f09f419be2e2cb873ce48da19e35c3f73d",   // the build these numbers came from

    // the rules these numbers were computed under, one entry per scored object type
    "policy": {
      "name": "default",
      "importance": "ego_relevant",
      "existence":    {"Car": {"rule": "drawn_empty", "atol": 1e-08}, "...": "14 more types and LaneLine:dashed"},
      "misalignment": {"Car": {"rule": "percentile_between", "percentile": 85.0, "lower": 0.0, "upper": 0.35},
                       "...": "four-wheelers only; VRUs are absent, meaning n/a"},
      "hallucination": {"Car": {"rule": "relevancy_gate", "min_relevancy": 1}, "...": "14 more types"},
      // the state maps hold TrafficLight alone, and appear whatever the file contains: the block records the
      // policy, not the subset of it that happened to fire
      "wrong_state":  {"TrafficLight": {"rule": "wrong_color_episode",
                                        "state_score_threshold": 0.5, "min_wrong_frames": 2}},
      "conflicting":  {"TrafficLight": {"rule": "conflicting_colors",
                                        "multi_color_threshold": 0.5, "min_conflicting_frames": 2}}
    },

    // one entry per object, in track_id order (162 of them in this clip)
    "tracks": [
      {"track_id": 1, "object_type": "Car", "scored_frames": 0, "mean_score": null,
       "unscored": true,  "missing": null,  "present": null, "misaligned": null,
       "wrong_state": null, "conflicting": null, "lane_style": null},
      {"track_id": 3, "object_type": "Car", "scored_frames": 7, "mean_score": 0.6928428571428571,
       "unscored": false, "missing": false, "present": true, "misaligned": false,
       "wrong_state": null, "conflicting": null, "lane_style": null}   // no color or style governs a car
    ],

    "by_type": {
      "Car": {"object_type": "Car", "observed": 20, "unscored": 130, "present": 19, "missing": 1,
              "misaligned": 2, "color_observed": 0, "wrong_state": null, "conflicting": null,
              "hallucinated": 0,
              "present_rate": 0.95, "missing_rate": 0.05, "misaligned_rate": 0.1,
              "wrong_state_rate": null, "conflicting_rate": null},
      "Pedestrian": {"object_type": "Pedestrian", "observed": 0, "unscored": 4, "present": 0, "missing": 0,
                     "misaligned": null, "color_observed": 0, "wrong_state": null, "conflicting": null,
                     "hallucinated": 1,
                     "present_rate": null, "missing_rate": null, "misaligned_rate": null,
                     "wrong_state_rate": null, "conflicting_rate": null}
    },

    "extra_objects": [{"id": 69, "class": "Pedestrian", "group": "vru", "relevancy": 3, "detections": 5}],
    "untyped_track_ids": [],
    "unevaluated_object_types": [],           // track types with no rules
    "unevaluated_hallucination_classes": []   // hallucination labels with no rules
  }
}
```

Three things to read off that example. Track 1 was never scored, so every verdict is `null` rather than
`false` — it is a coverage fact, not a quality one. `Pedestrian` has `"misaligned": null` because no
misalignment rule is defined for VRUs, and `null` rates because nothing of that type was observed, which is
different from a rate of zero. And `Pedestrian` carries a hallucination while observing no ground-truth
objects: correspondence counts are keyed by RDS object type, hallucination counts by detector class label,
because a hallucination has no ground-truth object to take a type from.

The block carries the policy that produced it, not just the numbers — two augmented files are only comparable
if they used the same one, and `--importance` has no default for that reason. Re-running replaces the block
rather than merging, so it is idempotent under a fixed policy and switching policies cannot leave two sets of
numbers side by side. Writes are atomic, so an interrupted run over a directory cannot truncate a result file.

Every object type in the file that the library has rules for is scored; the rest are named in
`unevaluated_object_types`, so a file of types the library does not cover yet yields an empty `by_type` that
explains itself rather than an unexplained blank. Nothing is inferred from the filename and there is no mode
to declare — the file's contents decide what can be scored. Feed it a file holding both dynamic and static
objects and you get metrics for the dynamic ones, the static types listed as unevaluated, and a warning naming
them.

`unevaluated_hallucination_classes` is the same idea in the other key space. A track carries an RDS object
type; a hallucination carries whatever label the detector emitted, and a class can appear with no
ground-truth track of a corresponding type anywhere in the file — so one field cannot cover both. Without the
second, a file whose hallucinations were all dropped for want of a rule would be indistinguishable from one
that had none. Note the distinction it draws: a class listed here has **no rule that can apply**, which is not
the same as a class whose rule ran and rejected it (a hallucination gated out by `relevancy` is absent from
`extra_objects` and correctly absent from this list too).

`git_sha` records the build that produced the block. The rules live in code, so the commit is the only
complete statement of what produced a verdict, and it is what makes a stale block identifiable after the rules
change. It is `null` rather than absent when the build was not stamped, so the field's presence does not vary
between environments — and the status script's `unknown` placeholder is normalized to that `null`, so there is
one spelling of "unavailable" rather than two.

Pass `--output` instead of `--in-place` to write elsewhere; it takes a single input file.

### A traffic-light file

Same command, same block — a static result file simply fills in the two color signals that a dynamic one
leaves `null`. Nothing is read off the filename; the file's contents decide what can be scored. The interactive
table reports every signal, with `n/a` where no rule measured one:

```text
  object_type        obs   unsc  present  missing   misal   wrong   confl  extra
  TrafficLight        10      0        8        2     n/a       5       9      0
```

The corresponding parts of the block, again real output — one clip, ten lights:

```jsonc
{
  "object_metrics": {
    "by_type": {
      "TrafficLight": {"object_type": "TrafficLight", "observed": 10, "unscored": 0, "present": 8,
                       "missing": 2, "misaligned": null,
                       "color_observed": 29, "wrong_state": 5, "conflicting": 9,
                       "hallucinated": 0,
                       "present_rate": 0.8, "missing_rate": 0.2, "misaligned_rate": null,
                       "wrong_state_rate": 0.1724137931034483, "conflicting_rate": 0.3103448275862069}
    },

    "tracks": [
      {"track_id": 818, "object_type": "TrafficLight", "scored_frames": 13, "mean_score": 0.7848615384615385,
       "unscored": false, "missing": false, "present": true, "misaligned": null,
       "wrong_state": true,  "conflicting": true, "lane_style": null},
      {"track_id": 829, "object_type": "TrafficLight", "scored_frames": 8, "mean_score": 0.0,
       "unscored": false, "missing": true,  "present": false, "misaligned": null,
       "wrong_state": true,  "conflicting": false, "lane_style": null},
      {"track_id": 861, "object_type": "TrafficLight", "scored_frames": 21, "mean_score": 0.46204761904761904,
       "unscored": false, "missing": false, "present": true, "misaligned": null,
       "wrong_state": false, "conflicting": true, "lane_style": null}
    ],

    "unevaluated_object_types": ["Crosswalk", "TrafficSign", "WaitLine"],
    "unevaluated_hallucination_classes": ["TrafficSign"]
  }
}
```

Note `observed` and `color_observed` differ: 10 against 29. They are denominators for different questions.
`observed` counts the lights the overlap check scored, which is what "missing" can be asked about;
`color_observed` counts the lights the state check measured, which is what "wrong color" can be asked about.
The two stages gate on different criteria — projected area versus edge truncation and segmentation mass — so
neither population contains the other, and sharing one denominator would publish a color rate over a
population the color detector never saw.

Four things to read off that one. `misaligned` is `null` throughout, because no misalignment rule governs a
light — the same "not measured" convention the dynamic example shows for a pedestrian. The counts and the
per-object verdicts are both published because neither derives from the other: `by_type` says five lights
were the wrong color, `tracks` says *which* five.

Track 829 is the interesting row: `missing` and `wrong_state` are both `true`. That is not a contradiction —
correspondence scoring and color classification are separate measurement channels reading separate fields,
and the color rule is deliberately independent of the existence rule, since a light can be drawn and drawn
wrong. A light scoring zero on correspondence while its color classifier still returns a reading is worth
seeing rather than suppressing.

The rest of the static types in the file appear in `unevaluated_object_types` rather than as zero rows: the
library has no rules for them yet, and reporting `0 missing` for a crosswalk it never examined would be a
substitute verdict. Note `TrafficSign` in both lists — it has neither a correspondence rule nor a
hallucination rule today.

Finally, a file whose state rows carry no `expected_state` reports `"wrong_state": null` and
`"wrong_state_rate": null` for every light rather than a count, while `conflicting` still answers — the
conflict rule needs no ground-truth color. Do not read that `null` as zero; see
[wrong state](#a-traffic-light-is-in-the-wrong-state-when-a-color-phase-was-rendered-wrong).

## Defining your own rules

The rules above are defaults, not a fixed set. A rule is any object that evaluates itself, so you can supply
one this library has never heard of, install it for the object types you care about, and have it evaluated and
recorded exactly like a built-in — no registration, no base class, no fork.

Three protocols, in `rules`:

```python
from collections.abc import Sequence
from typing import Any, Protocol

from kpi.automotive.result_view import HallucinationView, ScoredFrame, StateFrame

class TrackRule(Protocol):          # existence and misalignment
    def holds(self, frames: Sequence[ScoredFrame]) -> bool: ...
    def as_dict(self) -> dict[str, Any]: ...

class HallucinationRule(Protocol):  # extra objects
    def holds(self, hallucination: HallucinationView, *, relevancy_meaningful: bool) -> bool: ...
    def as_dict(self) -> dict[str, Any]: ...

class StateRule(Protocol):          # wrong color, conflicting colors
    def holds(self, frames: Sequence[StateFrame]) -> bool | None: ...
    def as_dict(self) -> dict[str, Any]: ...
```

You do not need to import or subclass these — they are shown so you can see the shape your rule must satisfy.
A plain frozen dataclass with those two methods is enough.

### An existence rule

```python
import dataclasses, statistics
from kpi.automotive.policy import default_policy
from kpi.automotive.result_view import ImportancePolicy

@dataclasses.dataclass(frozen=True)
class MedianBelow:
    threshold: float

    def holds(self, frames):
        return statistics.median(f.score for f in frames) < self.threshold

    def as_dict(self):
        return {"rule": "median_below", "threshold": self.threshold}

base = default_policy(ImportancePolicy.EGO_RELEVANT)
policy = dataclasses.replace(
    base,
    name="median-experiment",                                    # so the output says which rules produced it
    existence={**base.existence, "Car": MedianBelow(0.9)},       # cars only; every other type keeps the default
)
```

`is_missing`, `signal_summary` and everything built on them now use your rule for `Car` and the default for
everything else. `policy.as_dict()` reports it with its own parameters:

```json
{"name": "median-experiment",
 "existence": {"Car":   {"rule": "median_below", "threshold": 0.9},
               "Truck": {"rule": "drawn_empty", "atol": 1e-08}}}
```

#### Rules that need to know *when*

`holds` receives `ScoredFrame`s, not bare floats. A rule that only needs the numbers reads `f.score` and
ignores the rest, as above. The reason for the frame is that some questions are not answerable from a
multiset of scores at all:

```python
import dataclasses

from kpi.automotive.policy import default_policy
from kpi.automotive.result_view import ImportancePolicy

@dataclasses.dataclass(frozen=True)
class SustainedDropout:
    """Missing when the render drew nothing for a contiguous stretch, however good the average."""

    min_missing_frames: int
    atol: float = 1e-8

    def holds(self, frames):
        longest = run = 0
        previous = None
        for f in frames:
            if abs(f.score) > self.atol:
                run = 0
            elif previous is not None and f.ordinal == previous + 1:
                run += 1
            else:
                run = 1
            previous, longest = f.ordinal, max(longest, run)
        return longest >= self.min_missing_frames

    def as_dict(self):
        return {"rule": "sustained_dropout", "min_missing_frames": self.min_missing_frames}

base = default_policy(ImportancePolicy.EGO_RELEVANT)
policy = dataclasses.replace(
    base,
    name="dropout",
    existence={**base.existence, "Car": SustainedDropout(min_missing_frames=2)},
)
```

It installs exactly like any other rule — `is_missing`, `signal_summary` and the `object_metrics` tool pick it
up for `Car`, and `as_dict()` stamps `{"rule": "sustained_dropout", "min_missing_frames": 2}` into the output
so a reader can tell which rule produced the count.

`(0.9, 0.0, 0.0, 0.9)` and `(0.0, 0.9, 0.0, 0.9)` hold the same scores and get different verdicts — which is
the whole point, and is why the default `DrawnEmpty` (a mean test) calls both present.

Each frame carries **both** frame spaces, because rules want different ones:

| field | meaning | use it for |
| --- | --- | --- |
| `ordinal` | position among *scored* frames | adjacency — consecutive ordinals are consecutive measurements at any cadence |
| `frame_idx` | the video frame that ordinal names | elapsed time — a fixed sample count is a different duration at 30 FPS than at the 10 FPS annotation cadence |

Test contiguity on `ordinal`, never on `frame_idx`. A slice — one distance band, say — keeps the ordinals it
had in the parent track, so a gap in a band is a real gap rather than an artefact of slicing.

### A hallucination rule

```python
import dataclasses

from kpi.automotive.policy import default_policy
from kpi.automotive.result_view import ImportancePolicy
from kpi.automotive.taxonomy import Group, types_in_group

base = default_policy(ImportancePolicy.EGO_RELEVANT)

@dataclasses.dataclass(frozen=True)
class MinimumDetections:
    min_detections: int

    def holds(self, hallucination, *, relevancy_meaningful):
        return len(hallucination.detections) >= self.min_detections

    def as_dict(self):
        return {"rule": "minimum_detections", "min_detections": self.min_detections}

policy = dataclasses.replace(
    base,
    name="detection-count",
    hallucination={rds_type: MinimumDetections(3) for rds_type in types_in_group(Group.FOUR_WHEELER)},
)
```

`relevancy_meaningful` tells you whether `hallucination.relevancy` was populated at all for that object's
mode. If your rule reads relevancy, honor the flag — where it is `False` the field is structurally zero, and
gating on it would silently discard every hallucination rather than filtering them.

### A color-state rule

```python
import dataclasses
import statistics

from kpi.automotive.policy import default_policy
from kpi.automotive.result_view import ImportancePolicy

@dataclasses.dataclass(frozen=True)
class MedianStateBelow:
    threshold: float

    def holds(self, frames):
        scores = [f.state_score for f in frames if f.state_score == f.state_score]  # drop NaN
        return bool(scores) and statistics.median(scores) < self.threshold

    def as_dict(self):
        return {"rule": "median_state_below", "threshold": self.threshold}

base = default_policy(ImportancePolicy.ALL_SCORED)
policy = dataclasses.replace(
    base,
    name="median-state",
    wrong_state={**base.wrong_state, "TrafficLight": MedianStateBelow(0.4)},
)
```

`frames` arrive ordinal-normalized and may carry NaN scores, which the checker writes for a frame it could not
sample — most often because the ground-truth color was `unknown`. Treat NaN as unmeasured, not as a low
score; the built-in rules do this via the shared predicates.

A state rule may also return `None` to say the frames cannot answer its question at all, which propagates
through as "not measured" rather than `false`. `MedianStateBelow` above never needs to — it reads only the
scores — but a rule that consults `frame.expected_state` should, since a frame naming no ground-truth color
gives it nothing to judge against. That is exactly what the built-in `WrongColorEpisode` does.

### Four things the library guarantees so your rule does not have to

- **`frames` is non-empty and NaN-free.** Unscored tracks resolve to `None` before any rule is consulted, so
  `holds` never has to decide what an absent measurement means — and it returns a plain `bool`, not
  `bool | None`.
- **Frame space is already normalized.** Both axes arrive resolved on every frame, so no rule re-derives the
  mapping from video frames to scored positions. Getting that wrong is silent rather than loud: adjacency
  tested on raw ids at a 10 FPS annotation cadence makes every run length 1, and the signal reads zero
  forever.
- **"Not applicable" is an absent map entry**, not a rule that declines to answer. Leave a type out of a map
  and its verdict is `None`, which reports as `n/a` rather than as a zero.
- **Your rule is stamped, not flattened.** `as_dict()` calls yours, so provenance describes what actually ran.
- **Each rule states its own comparison.** `PercentileBelow` and `PercentileBetween` are separate types rather
  than one rule whose meaning depends on which field it was stored in, so moving a rule between slots cannot
  silently change what it means.

One thing the library does *not* police: `PercentileBetween` takes its lower bound as a parameter, so nothing
stops you choosing bounds that overlap the existence rule installed for the same type — in which case one
object can be reported both missing and misaligned. Keeping the two disjoint is yours to decide, which is why
the bound is explicit rather than a hidden zero.

## Five things to know before using it

### 1. `ImportancePolicy` is required, and the choice is not cosmetic

The object check marks each scored cell with an `importance` flag: whether the object passed its ego-relevance
filters (lane relevance, distance, oncoming) in that frame. Honoring the flag asks "how well is the model doing
on the objects that matter to the ego?"; ignoring it asks "how well is the model doing overall?". Both are
legitimate questions with different answers, and neither is a safe default.

Measured over 997 real dynamic result files (80 782 tracks), **82% of emitted cells carry `importance == 0`**,
so the two readings score very different populations. **23 281 tracks (28.8%)** are scored under `ALL_SCORED`
and never-observed under `EGO_RELEVANT`, while only 115 (0.14%) flip present ↔ missing. The verdict rule
agrees; the denominator does not:

| Object type | Missing rate, `EGO_RELEVANT` | Missing rate, `ALL_SCORED` |
| --- | --- | --- |
| Car | 4.2% | 11.3% |
| Truck | 4.8% | 10.6% |
| Vehicle | 16.3% | 29.2% |
| Pedestrian | 42.3% | 57.6% |
| Cyclist | 54.2% | 74.3% |

`read_result` therefore takes the policy as a required keyword argument and `ResultView.importance_policy`
records it, so a published number can always be traced back to the population it was computed over. Two
reports are only comparable if they used the same policy.

### 2. `None` means "not measured", never zero

Every predicate returns `bool | None`, and every count on `ObjectSignals` that can be ungoverned is
`int | None`. `None` means *this signal was not measured* — which is a different fact from a count of zero.
Misalignment is defined for 4+ wheelers and not for vulnerable road users, so a pedestrian's misalignment is
`n/a`; reporting it as `0` would publish a 0% misalignment rate for something never measured.

There are three ways a signal goes unmeasured, and they are deliberately indistinguishable to a consumer,
because the honest answer to all three is the same: no rule is installed for the type, the track was never
scored, or the rule itself declined because the data cannot answer it. Each rate follows its count, so a
`null` count never yields a `0.0` rate.

Likewise `unscored` is kept out of `observed`. A track the algorithm never evaluated — filtered before scoring,
outside the processed frame range, or never important under the active policy — is a **coverage** fact, not a
generation-quality one, and counting it as missing would make the metric measure the wrong thing. On the same
997 files, 66% of dynamic tracks have no scored cell at all.

### 3. Missing and misaligned are mutually exclusive

An object the existence rule calls missing is never also reported misaligned — it was not drawn, so it cannot
have been drawn badly. The library establishes that itself rather than relying on your two rules' bounds not
to overlap, so the exclusion holds for your rules as well as the built-ins.

### 4. Traffic lights need a dense frame axis

A light's per-frame rows record **video** frame indices, but the color-state rules test adjacency as
`idx == prev + 1` — a gap starts a new color episode, and a conflict must be a contiguous run. A run read at
30 FPS against 10 FPS annotations lands on video frames 0, 3, 6, where every episode is one frame long and
every run has length 1, so neither rule can ever fire.

`read_result` therefore normalizes each row onto its position in `processed_frame_ids`, and `StateFrame.ordinal`
is that position rather than the index the file records. This is not a legacy concern: of 80 real result files
sampled, 26 have a cadence where the mapping is not the identity.

A row naming a frame absent from `processed_frame_ids` is dropped rather than given an invented position,
which would fabricate adjacency the rules would then read as a contiguous episode.

### 5. Rates have no denominator until something is observed

`ObjectSignals.rates()` returns `None` rather than `0.0` when `observed` is zero, for the same reason. A type
that appears only as hallucinations, or only as unscored tracks, has no measured rate — and a table that
prints `0.0%` there invents confidence that was never earned.

## Scope and constraints

**Dynamic object types, traffic lights and the lane graph.** Traffic signs, crosswalks and wait lines are not
scored yet. `kind_of()` returns `None` for an unregistered type and `signal_summary` skips it,
rather than scoring it by a substitute rule, so an unsupported type is reported as unevaluated rather than
silently counted as fine.

**Signals are per type, not universal.** Misalignment is defined for 4+ wheelers only — a VRU's projected box
is too small for partial containment to be distinguishable from noise, and neither a traffic light nor a
polyline has a box-containment signal at all. Color state is defined for traffic lights only. Ask `defines_signal()` rather
than assuming; a signal a type does not define reports `None`, never zero.

**The percentile rules pin `method="linear"` explicitly.** numpy offers nine interpolation methods and these
rules were characterized against that one, so relying on the default would let a numpy upgrade move a verdict.

**Verdicts about one run, not comparisons between runs.** Control rows, confusion matrices and paired
before/after scoring belong to whatever experiment is being run, not here. This library answers "what does this
result file say about each object"; a caller decides what to conclude from two of those answers.

## See also

- `checks/objects/single_view/README.md` — the object check that produces the input, including the score-matrix format
- `checks/objects/results.py` — `save_results_to_json`, which writes the file these views parse
