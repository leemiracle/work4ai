<!-- Entry template (append each step using append_file):

## Carry-Forward
(cumulative and refined): {ALL knowledge from previous steps to preserve — carry every item forward, refine it, and add this step's; keep it complete and comprehensive}

## Scene Framing
{what the scene is — entity roles and structure guiding your encoding}

## Delta
- Changed: {what this step changed — new entities, position updates, schema updates, render fixes}
- Invalidated: {encodings or interpretations disproven by this step}

## Scene Structure

- Playable / interactive region: {where the actionable scene is}
- Static structure: {walls, corridors, terrain, boundaries}
- Entities: {sprites or objects that appear dynamic}
- Ambiguous regions: {areas/widgets not yet explained}

## Entity Map

| Entity Type | Instances | Positions | Sprite Size | Confidence |
|-------------|-----------|-----------|-------------|------------|

## Object States

| Entity | Observed state | Value | Confidence |
|--------|----------------|-------|------------|

## Event Frames

- Frame coverage: {no event frames, or which event frame labels were shown and whether the sample is decimated}
- Visible changes: {transient pixels/entities/regions visible across the event frames}
- Affected entities: {entities represented in z_encoded.event_objects}
- Interpretation: {what the event visually shows — transient pixels/entities vs the settled grid}

## WM Rendering Review

- Current step render: {pixels wrong}
- Current step render_event: {frames reconstructed; matched or missed}
- Historical regressions: {step K: render N pixels wrong, or render_event missed}
- Actions: {observable.py edits, level_constants updates, z_encoded backfill}

## WM Retrodiction Review

- Value mismatches (simulator predict wrong): {fields and spatial impact}
- Under-encoded (in predict, missing from z_encoded): {fields, schema work follows}
- Catch-up (in z_encoded, missing from predict): {fields awaiting simulator}
- Actions: {Z_SCHEMA updates, z backfill, feedback sent}

## Feedback

#feedback @simulator [SEVERITY] {predict() missing field or output mismatch, with requested correction} (cite step N)


## Encoding Priorities

- {Unmodeled grid regions to encode}
- {Entity types needing sprites in level_constants}
- {Render accuracy gaps to investigate}

-->
