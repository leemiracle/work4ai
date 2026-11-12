# Handoff report template

Skeleton for the `oncall-handoff` skill. Copy the headings, follow the one-line guidance
under each, then delete the guidance and any section that would be empty. The team's own process
may override this template: where the team's playbook, runbook, imported custom-instructions
doc, oncall memory, or a person in the channel defines a different one, use theirs.

Five sections, and fewer on a quiet window. If the report does not fit on two phone screens,
something in it is not carrying its weight.

---

**Oncall handoff: `<rotation>` — `<start>` to `<end>` `<tz>`** *(partial, as of HH:MM TZ —
only if the window isn't over)*
Outgoing: `<name>`
Incoming: `<name>`

**Start here:** the single most important item for the incoming oncall — one line with its next
step and the thread link. One item, never a list; everything else waits for the sections below.

## TL;DR
Two short sentences a reader with no context can follow: is anything degraded right
now, what is most likely to page them next, and the one open item they must not drop. No jokes here.

## Open items
One line per item, most urgent first. Carried-forward items are marked *(carried, still open)* or
*(carried, dormant — unchanged since `<date>`)*; with no previous report, the SKILL's Inputs rule
applies — omit the markers, no meta lines. A workaround holding the system together is an open
item: say what removes it and when. The link is the Slack thread where the item was handled, plus
the incident channel when one exists.
- `<item>` — `<next step, imperative>` — `<who, plain-text name/team>` — `<thread link>`

## Incidents
Qualified by a high-urgency page or a formal declaration, nothing else. One block each, newest
first. Four lines; if a fifth is needed, the incident deserves a postmortem, not a longer block.

**`<date>` `<short title>`** (`<SEV>`, `<start>`–`<mitigated>` `<tz>`) — `<thread link>` ·
`<incident channel link, if one exists>`
- What happened: one plain-words sentence — what the service does and what actually happened —
  before any metric or monitor name.
- Impact: `<number>` `<unit>` over `<window>` (`<% of what>`); who noticed first.
- Cause and fix: `<confirmed cause + evidence link>`, fixed by `<what changed>` `<link>` — say if the
  fix is temporary. Or "undiagnosed, contained by `<action>`".
- Watch for: the metric or query that would show it returning, with the link.

If the explanation involves more than two systems, post a simple mechanism flow diagram (boxes and
arrows: what broke, what it hit, what the user saw, what recovered it) as its own message with a
one-line caption.

## Alerts and pages
`<N>` pages (`<H>` high-urgency), `<M>` distinct monitors, vs `<N'>` / `<M'>` previous window.
`<B>` in business hours, `<F>` off-hours (nights and weekends, the team's workday in channel-local
time). Intake: `<R>` of `<N>` alerts got any human response (an ack, a reply, an action); the rest
fired into silence.

| Alert | Count | Actionable? | Verdict |
|---|---|---|---|
| `<monitor name>` | `<n>` | yes / no / once | `<what it meant, or a tuning proposal>` `<thread link>` |

Every row links the Slack thread where that alert was handled (in the verdict column, or a
dedicated link), plus the incident channel when one exists.

List the monitors that account for most of the fires (usually a handful), then one aggregate line for
the remainder: "`<k>` other monitors, `<n>` fires". "Actionable" means a human did something other
than acknowledge. A monitor that fired repeatedly with nothing actionable gets its proposal in the
verdict column — tune to what, re-route, convert to a ticket, or delete — rather than a section of
its own. Name each proposal's kind: **coverage** (a human noticed something no rule watched),
**late** (the rule fired long after onset), or **noise** (fired repeatedly, ignored) — the same
taxonomy the postmortem skill uses for detection gaps. The further hygiene rows — a pending
promotion, and a playbook entry whose misses have accumulated to rival its hits — are one line
each, when they apply; the rules live in the SKILL's step 4.

## Notes for next oncall
Dated, concrete, short. Planned maintenance, a flaky dependency to distrust, a customer mid-
migration, a runbook step that turned out wrong (with the correction). One line for requests the
outgoing oncall fielded, if there were enough to be a pattern: "access requests ×4, all for the same
dashboard `<link>`".

---

## Compact variant — weekly digest

For a broad audience; fits in one screen. Group by service, not by category.

**Oncall week `<start>`–`<end>` `<tz>`** — `<N>` pages (`<H>` high), `<I>` incidents, `<O>` items open.
- **checkout-api** — 1 incident (SEV2, 42 min, ~2.7k failed checkouts, fixed by rollback
  `<link>`). 6 pages, 2 actionable. Open: retry budget change `<link>`.
- **payments-worker** — 0 incidents. 9 pages, 0 actionable, so proposing a threshold change `<link>`.
- **search-svc** — quiet.
Carried forward: `<n>` items, `<r>` resolved this week. Full report: `<link>`.

---

## Writing rules

Every section is written to the SKILL's "How to write it — simple, for a reader with no context"
section — plain short sentences, users before metrics, glossed metrics, expanded acronyms,
diagrams and charts as their own captioned messages. The rules below are the format checks on top:

- Quantify: replace qualitative words with the figure and its window, linked to where it came from.
- Links on everything a reader might want to open: incidents, threads, monitors, changes, tickets.
  Every incident block, open item, and alerts-table row links the Slack thread where it was
  handled, plus the incident channel when one exists.
- Link to restricted incident channels rather than quoting them; no customer or individual names
  in the weekly digest.
- One home per item. If an alert belongs to an incident, it's counted there, not again in the table.
- Drop empty sections; never write "None" or "N/A".
- Absolute times with timezone. Names as plain text, no @-mentions.
- The system and the customer are the subjects of sentences; the oncall engineer is not.
- One dry aside is allowed where the numbers have already earned it — the full rule lives in the
  SKILL's step 4.
