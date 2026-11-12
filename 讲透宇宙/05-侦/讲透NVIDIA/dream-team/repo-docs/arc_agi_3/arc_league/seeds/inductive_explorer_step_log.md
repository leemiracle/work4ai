<!-- Entry template (append each step using append_file):

## Carry-Forward
(cumulative and refined): {ALL knowledge from previous steps to preserve — carry every item forward, refine it, and add this step's; keep it complete and comprehensive}

## Game Framing
{the high-level interpretation of mechanics, goal, and game type currently guiding action}

## Prediction Check
- Last recommended action: {action} → {what actually happened}
- Prediction accuracy: {matched/diverged} — {what this tells us about the model}

## Sub-Goal Rationale

| Sub-Goal | Why It Matters | Evidence | Status |
|----------|---------------|----------|--------|
| {name} | {why this sub-goal is necessary for level completion} | {observations/data that justify this definition} | [CONFIRMED]/[UNCERTAIN]/[UNTESTED]/[CONTRADICTED] |

Key dependencies: {which sub-goals should be achieved before others, and why}
Ruled out: {sub-goals or policies the recent evidence works against}

## Policy Analysis

- **Best policy**: {policy name or no policy ready}
- **Target sub-goal**: {sub-goal heuristic and why it matters}
- **Why it works**: {state fields and transitions that support it}
- **Validity condition**: {observed state fields that make the policy ready}
- **Rollout evidence**: {which sub-goals advanced and where the policy stalled}
- **Runner-up**: {second-best policy and when its validity condition is better supported}

## Policy Recommendation
Policy: {POLICY policy_name n_steps | no policy ready}
Use when: {state fields or checkpoint that support the policy}
Switch condition: {observation that supports a different sub-goal or policy}

## Strategy Assessment
- Planning mode: {UPDATING SUB-GOALS|SEARCHING POLICY|POLICY READY|NEEDS MODEL EVIDENCE}
- World model readiness: {ready for policy | policy uncertain | diagnostic only}
- Biggest uncertainty: {what could invalidate the policy}
- Open questions: {unknowns worth probing next}
- Next update if divergent: {policy condition, sub-goal detector, or missing state evidence}

-->
