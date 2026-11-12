# claude-tag-oncall

Oncall skills for @Claude Tag: set it up once per team, and from then on new
incident channels start with the team's context, alert feeds get sorted into signal and noise,
alerts and incidents get investigated and fixed where possible, reported customer problems get
run to closure, and the rotation handoff runs itself.

Claude's tool access comes from agent connectors: connections a workspace admin sets up once for
Claude, under Claude's own identity, so they work in every channel and every session. When a tool
isn't connected, Claude works from what the people present can paste, export, or link.

Two kinds of Slack channel matter to this plugin:

- **Oncall / monitoring channel** — a team's standing channel where its alerts land and the rotation
  talks day to day. A workspace usually has several, one per team or rotation.
- **Incident channel** — short-lived, opened per incident (or a shared alerts feed); nothing is set
  up there by hand.

What the plugin does, and where each part runs:

- **Oncall setup** (`oncall-init`) — *monitoring channel.* Set Claude up for oncall and guide the
  person through it: check which tools Claude can reach, learn how this team's oncall works, and
  add the team's section to the one oncall memory that every channel reuses. (Claude Tag
  keeps notes it rereads at the start of every conversation: one set per channel and one shared set for the
  workspace. Setup saves into the shared set, so every channel, including new incident channels,
  starts from it.) Run it once in each team's monitoring channel; each run appends that team's part
  and never overwrites another team's.
- **Incident setup** (`incident-init`) — *incident channels.* Bring the oncall memory into a new incident
  channel the moment Claude lands there, pick the matching team's section, one short message —
  and when the channel was plainly opened for a live outage, hand straight to the investigation
  with nobody having asked, so responders arrive to a briefing (what broke, why, a proposed fix
  waiting for a person to confirm) rather than a blank channel.
- **Alerts monitoring** (part of `incident-investigate`) — *monitoring channel.* The standing
  sorting layer for channels where other systems post alerts: real signal gets an investigation
  in its thread, repeats, twins and storms fold into one thread, flapping and stale alerts get
  flagged (never cleared by Claude), recovery notices and feed chatter get silence — with fixes
  for bad alert rules drafted for a person where team policy allows, and an optional scheduled
  morning review of alerts nobody answered.
- **Ticket triage** (part of `incident-investigate`) — *monitoring channel, or wherever asked.*
  When a person reports a customer problem: find the root cause from that customer's own failing
  case, explain what went wrong in plain language the reporter can pass on, draft the
  customer-facing reply and/or the fix for a person to review and send, then follow the thread
  to closure — nudging it when it goes quiet and closing the loop with the reporter once the fix
  is verified.
- **Investigate** (`incident-investigate`) — *mainly incident channels;* also works in the
  monitoring channel, in the thread of whatever raised it, when an alert lands (posted by a bot or
  typed by a person) or someone asks there. Triage and investigate, report findings a human can
  check, fix it where possible.
- **Sitrep** (`incident-sitrep`) — *incident channels.* While it's live, post the short status
  update (situation report) that gives late arrivals and people outside the team the current
  picture: a two-sentence TL;DR, impact, what changed since the last one, what's in progress and
  who has it, what's needed, next update time, one chart. In the thread when someone
  asks, or top-level on a sparse schedule (hourly or slower) until it's resolved; facts only from
  the people in the channel and Claude's own reads; customer / exec / support versions come out
  for a person to review and send.
- **Postmortem** (`incident-postmortem`) — *incident channels.* Once it's over, write the
  one-screen summary for people who weren't there: what happened, impact, timeline, why, fix,
  follow-ups, one chart. Posted and pinned as the incident's final pinned post, with edits going
  into that one post in place; when write-ups live elsewhere (the team's doc tool, or the
  person's own copy), only a link is posted and nothing is pinned. A person edits and publishes it.
- **Handoff** (`oncall-handoff`) — *monitoring channel* (works from an incident channel too).
  Run the oncall handoff at rotation change, normally as a scheduled routine so the report is
  waiting when the shift turns over, or on a manual ask: build the summary, post it directly as
  the report, have the outgoing oncall correct it in place, walk the incoming oncall through the
  open items and note when they take over.

Trends are shown as charts rather than prose throughout.

## Suggested rollout

1. Ask @Claude to set up oncall ("@Claude set up oncall") in the team's oncall / monitoring
   channel — this runs `oncall-init` and writes the team's section of the oncall memory;
   other teams do the same from their own monitoring channels, and incident channels pick it
   up through `incident-init` with no re-run. Run it from a public channel: from a private one the
   oncall memory is read-only and setup will ask you to move. Everything below also works without
   it, and the other skills offer it once if it hasn't been done.
2. Start with the handoff — at the end of a rotation, ask @Claude to run it by hand once ("run the
   oncall handoff"), have the outgoing oncall correct the report and the incoming oncall ask their
   questions in the thread. Low risk, and it shows quickly whether Claude is reading the right
   sources. Then ask @Claude to schedule it (e.g. "run the handoff every Monday 09:00") so it runs
   by itself at every rotation change.
3. During a real incident, ask for a sitrep ("@Claude sitrep") whenever someone joins late or a
   stakeholder asks where things stand, and let it keep the cadence ("every hour until
   resolved") so the person running the incident doesn't have to.
4. Use `incident-investigate` on real incidents and alerts with a person working alongside — in
   incident channels first, and in the monitoring channel by replying under whatever raised it —
   an alert bot's post or a person's own report; run the
   query or link each finding includes and compare it against what you'd have checked, and let it
   carry out the fixes you confirm. Claude already picks up alerts nobody asked about; if a channel
   or a particular alert should be left alone, ask @Claude in the monitoring channel to "update the
   oncall setup" and say so, and it restates the exception and saves it on your confirmation.
5. Add a periodic self-review routine so corrections feed back into the oncall memory through a
   person, plus any other sweeps the team wants (e.g. a morning list of unanswered alerts).

Example routine prompts — they can be this short; the skills fill in the detail:

```
Every <rotation change, e.g. Monday 09:00 <timezone>>, run the oncall
handoff for this channel's rotation and post the report in a new thread.
```

```
Each weekday morning, list alerts in this channel from the last 24 hours that nobody replied to,
with a one-line triage each.
```

```
Every two weeks, review how alert handling went in this channel and suggest changes to the oncall
memory for a person to apply.
```

## How to invoke

There are no slash commands in Slack — ask @Claude in the channel in plain language and the
matching skill runs. For example:

- **oncall-init** — in each team's oncall / monitoring channel (a public one; from a private
  channel setup will ask you to move): "@Claude set up oncall", "@Claude get ready for incidents";
  later "@Claude update the oncall setup". Each team runs it in its own channel; the runs add up in
  one oncall memory.
- **incident-init** — automatic: runs by itself on Claude's first contact with an incident or
  alerts channel (invited, first @-mention, channel just created) and loads the existing oncall
  memory there; or "@Claude load the oncall setup here".
- **incident-investigate** — anywhere in an incident channel, or in the monitoring channel by
  replying in the alert's thread: "@Claude investigate why the site is down", "@Claude figure out
  why plugins aren't loading", "@Claude why are signups down over the last 2 days?", "@Claude is
  this alert real?". Prompts will usually be one short sentence like these; the skill expands them
  rather than expecting a detailed brief. Pasting an alert / monitor / dashboard link and asking
  what's going on works too, and so does asking for an action ("@Claude roll it back"), which it
  restates and waits for you to confirm. It also carries the feed itself — "@Claude which of
  these alerts matter?", "@Claude did we miss anything overnight?", "@Claude is this channel too
  noisy?", or schedule the review with "each weekday morning, list alerts nobody replied to" —
  and customer-problem reports: "@Claude customer X can't check out, can you take a look?",
  "@Claude support escalated this ticket <link> — what went wrong?", "@Claude why did this
  account's export fail on Tuesday?".
- **incident-sitrep** — in the incident channel while it's live: "@Claude sitrep", "@Claude where
  are we?", "@Claude catch me up", "@Claude post a sitrep every hour until this is resolved",
  "@Claude write a customer-facing update".
- **incident-postmortem** — in the incident channel once it's mitigated: "@Claude write up this
  incident", "@Claude write the postmortem".
- **oncall-handoff** — usually runs on a schedule at rotation change (ask @Claude to schedule it);
  to run it by hand: "@Claude run the handoff". Also "@Claude oncall summary since Monday 09:00
  Berlin", "@Claude hand over to <incoming> for this rotation".

## Works best with

Connected sources, roughly in priority order. None are required to start: without them the skills
ask for pastes and links, and if your alerts already post into Slack, Claude works from those
posts directly. But **a monitoring connector is extremely important, not a nice-to-have** — with
no connector there is no live metric access at all, so an investigation reads the alert's text
instead of the signal and cannot establish onset, magnitude or scope. Data already in hand — the
alert's text, pastes, bot posts — and connector access are both data signals, both important:
Claude reads what it holds while pulling the live signal through the connectors it can reach,
not one only after the other. Its access comes from agent connectors — admin-configured
credentials Claude itself holds — used directly (the full order is stated in
`incident-investigate`, "Before you start" step 3). When no agent connector reaches the data it
needs, it asks the people in the thread for a paste, an export, or a link pinned to the window,
once per audience. And when a tool the team keeps needing has no agent connector at all, the
durable fix is a workspace admin adding the connector for Claude — an ask that belongs in
`oncall-init` in the monitoring channel, while nobody is under pressure, never in the middle of
an incident. In an incident channel `incident-init` still says which data it's missing and how
someone present can paste it.

| Source | What it unlocks |
|---|---|
| Code host (GitHub, GitLab) | Recent merges and deploys for "what changed just before onset"; linking a fix to the actual change; opening a draft PR when the fix is code. |
| Metrics / monitoring (Datadog, Grafana, CloudWatch, New Relic) | Live monitor state and thresholds instead of stale alert text; splitting a signal by service / region / version; the series behind every chart; deploy and event overlays. |
| Error tracking (Sentry) | New issues first seen in the window and top regressions per service; stack traces to follow one failing request. |
| Paging / incidents (PagerDuty, Opsgenie, incident.io) | Who is oncall and the exact shift window; whether an alert is a repeat and how past occurrences resolved; page counts and ack/resolve times for the handoff. |
| Tickets (Jira, Linear) | Tickets opened from incident threads and their status, so "Open items" link to something that tracks them. |
| Runbooks / docs (Notion, Confluence, Google Drive) | The team's own first checks and mitigation steps instead of generic ones. |
| Feature flags (LaunchDarkly or similar) | Flag flips near onset, and the fastest-to-undo mitigation when one lines up. |
| Status page | What customers have already been told, and upstream vendor status for "is it us or them". |

Claude doesn't need all of these connected. It records which connectors exist in the workspace in
the tools list of the oncall memory, and treats that list as a record of what exists, not access
it has. With agent
connectors Claude investigates and resolves issues on its own, and even read-only access covers
the whole investigating side — so when an investigation had to lean on pastes and exports, the
final report ends with one line recommending an agent connector for the tools that were missing.

## Customizing

Teams shape the output in two ways. First, through their own runbook doc or repo: when setup
(`oncall-init`) reaches one that carries standing instructions — a CLAUDE.md, or a doc laying out
the team's investigation process or report formats — it asks whether to import them. On a yes,
every investigation reads that doc first, and its process and format instructions override the
skills' built-in defaults, report templates included; safety rules are never overridable. A team
with nothing written down yet gets offered a starting policy doc during setup — severity levels
in the team's own words, how incidents are declared, deploy windows, escalation preference,
cadences — drafted from a bundled template into the team's own doc store with every default
marked "(proposed)" for the team to edit, and made authoritative through that same import once
the team accepts it. Second, an admin can ship standing instructions alongside the plugin
through admin-controlled configuration that delivers the plugin and its
standing instructions together — so those arrive with the plugin itself and need no per-team
setup.

## Skills

| Skill | What it does |
|---|---|
| `oncall-init` | One-time setup, run by anyone in a team's public oncall / monitoring channel. Verifies which tools Claude can reach, learns how the team runs oncall, proposes a starter alert set (every threshold marked "(proposed)") for a service with no alert rules, shows what it found for you to confirm, and saves it as the team's section of the oncall memory plus a short note for that channel. Each step ends at a check verified against the real artifact, so an interrupted run resumes at the first step whose check does not pass rather than starting over. At the close it offers scheduled routines and, opt-in behind a consent question, mining the team's resolved incidents into playbooks with hit and miss counts. Re-run to update. |
| `incident-init` | Automatic, once per channel, on Claude's first turn in a new incident or alerts channel (not one already set up as a team's monitoring channel): loads the oncall memory, picks the owning team, posts one short "what's broken / what I can reach" message. Hands off to `incident-investigate` if something was asked — immediately, unasked, when the channel was plainly opened for a live outage; otherwise waits to be asked. |
| `incident-investigate` | From a one-line ask or an alert thread: restates the symptom, checks what changed / where errors concentrate / paging history in parallel, posts a short interim update (a bold `**TL;DR:**` header over at most two short sentences, plus the one or two leads it is working, three at the outside) with a chart or flow chart rendered to an image and posted as its own message when one explains the cause or evidences it, keeps the full ranked report with its tables for the final `🏁 [Investigation complete]` post — which includes a chart of the key signal and/or a mechanism diagram by default, and, in a dedicated incident channel, is also sent to the channel's top level (in a monitoring channel it stays in the alert's thread) — proposes a fix and carries it out on your confirmation, verifies before/after. Also does the first pass, by default, for alert posts nobody asked about, after judging that the post is an alert rather than ordinary chat. Also the standing sorting layer for a team's alert feed (a signal-vs-noise ladder: repeats, twins and storms folded into one thread; flapping and stale alerts flagged once, never acked or cleared by Claude; chatter silenced; drafted fixes for bad alert rules; an optional scheduled review of alerts nobody replied to) and the ticket path for customer-reported problems (root cause from the customer's own failing case, a plain-language explanation for the reporter, the customer reply and fix drafted for a person to send, follow-up to closure with unresolved tickets escalated into the handoff's open items). |
| `incident-sitrep` | In the incident channel while it's live, on ask or on a schedule: finds the previous sitrep, reads the channel and the findings since then, re-reads the key signal, and posts a numbered one-screen sitrep (status line, two-sentence TL;DR, impact with peak and now, since last sitrep, in progress with owners, needs, next update, one chart, links). Facts only from people in the channel or Claude's own fresh read; never its own guess at cause or recovery time. Asked-for sitreps go in the asking thread; scheduled ones go top-level, hourly or slower, shorter, with a "no change" one-liner when nothing moved, and stop by themselves at resolution. Customer-facing, exec and support versions come out for a person to review and send. |
| `incident-postmortem` | In the incident channel after mitigation: gathers the channel, the alert thread and the live data, and writes a one-screen zero-context postmortem (what happened, impact with numbers, detection, timeline with durations, why, fix, follow-ups with owners, one before/during/after chart) for a person to edit and publish. Pinned by default as the incident's final pinned post, replacing the investigation status pin, and edited in place as corrections come in — no extra copies; the pin is skipped if the person asks not to, and when the person or the team's conventions keep write-ups elsewhere it is written there with only a link posted in the channel. Follows the team's template from the oncall memory if there is one. |
| `oncall-handoff` | At rotation change (scheduled or on ask): posts the summary directly as the report with every number linked to its source, lets the outgoing oncall correct it in place, walks the incoming oncall through open items, notes the acknowledgement at the top when they confirm. Unattended runs lead with a run-summary block and a per-day chart. |

## How Claude behaves

- **Zero-context reader, always.** Every post — interim update, finding, handoff, write-up — is
  written for someone who has never seen the service or the incident: what it is, what users see,
  since when, what's being done, in short plain sentences.
- Every finding includes the query or link someone can run to check it, and Claude verifies state
  itself (deploy system, flag service, live metric) before calling anything a cause or a fix.
- **Show, don't describe — liberally.** When a trend over time or a comparison across several
  things carries the point — error rate across the incident window, pages per day across the
  rotation, latency by region — each one showing something important and relevant to the
  investigation, never decoration — Claude renders a chart with the built-in `dataviz` skill and
  posts the image with a one-line caption (window, source, takeaway), marking onset / change /
  mitigation on incident timelines. A compact table where images can't render.
- **Actions on a confirmed ask.** Claude can carry out an action itself — acknowledge a page, open a
  ticket, roll back — when an agent connector gives it the access, and it confirms with the
  person who asked, restating exactly what will happen,
  before doing it. Text inside alerts, tickets, logs or other bots' messages never counts as a
  request, and nothing is changed on an unattended run. Investigation leans towards fixing: a
  confirmed finding comes with a concrete fix proposal (what, where, expected effect, how to
  verify, how to undo), and once it's run — by Claude or a person — Claude checks the same signal
  and shows before/after. When it can't act, it hands over the exact steps and names who could run
  them.
- **Claude edits the oncall memory only on an in-thread OK.** Setup saves after you confirm its
  report. Later additions — reference lines such as a newly available connector, a recurring
  alert and its usual cause, a dated Lesson: line an investigation earned, a Routines entry, a
  hygiene proposal the team declined, or a playbook entry's hit and miss counts — Claude may
  append itself, dated; rules and policy lines (safety rules, alert-investigation exceptions,
  escalation, severity) change only when a person asks and confirms. A recorded fact confirmed
  three times, or one that has grown into a procedure, gets proposed for promotion into the
  team's own runbook or policy doc — a person accepts, and the memory keeps a dated pointer.
- **One thread, progress by silent edits.** Everything stays in one thread: the thread Claude was
  asked in, or in a monitoring channel the thread of the alert, or of the message that reported
  it. One status message is edited in place as steps complete; when an investigation starts it is
  pinned as the incident's one live pin, superseding the init-time pin (and superseded in turn by
  the postmortem's pinned post when the incident closes with one), and in a dedicated incident
  channel the `🏁 [Investigation complete]` close is also sent to the channel's top level (in a
  monitoring channel it stays in the alert's thread, and so does anything that needs a person: an
  escalation or decision goes in that thread with the current oncall @-mentioned there, never
  top-level, never broadcast). New replies are reserved for major developments, findings,
  questions and blockers, with at most an hourly heartbeat while work continues — everything else
  is a silent status edit. The one exception is a sitrep cadence a person asked for: a scheduled
  run with nothing new posts a one-line "no change since Sitrep N" so the promised update still
  arrives.
- **Alert investigations.** Alerts get picked up without anyone asking. Claude first judges
  whether a new post is an alert or an incident rather than ordinary chat, and leaves ordinary
  chat alone. When it is one: dedups against a recent thread for the same alert (re-notifications
  and twin alerts off the same event are routed to the live thread with a one-line pointer, and
  get the resolution line and the closing emoji when it closes), notes flapping alerts without chasing them,
  stands down if humans are already on it, otherwise runs the first pass — and keeps exactly one
  reaction on the alert, 👀 from the moment it starts looking, swapped for 🏁 `checkered_flag`
  (🔁 `repeat` for a flapping close, or the verdict a person still has to act on) when it is done — a flag rather than a checkmark,
  so it reads as the investigation finishing, not the incident being resolved. The swap removes
  👀 rather than leaving it behind, and covers every relay of the alert deduped into the same
  thread, not just the first. That reaction is placed on every investigation, asked for or not.
  When an alert fires with nobody around and its agent connectors don't reach the data it needs,
  it tries once to raise the person most recently active in the channel (anytime during the
  workday; outside roughly 8am–6pm local, only someone active within the last hour) and the
  current oncall; if nobody answers it keeps investigating anyway, read-only, from the alert's
  payload and whatever its agent connectors reach, rather than stalling. No @-mentions beyond the
  urgent-group and needs-a-decision exceptions and that one raise-a-person attempt. A team that
  wants a channel or an alert left alone says so, and the exception is recorded in the oncall
  memory.
- **Unattended output stands on its own.** Routine handoff runs always open with a fixed run-summary
  block (window, counts, open items, needs-a-human) and attach at least
  one chart, so someone reading only that message has the whole picture.
- **Works standalone; better after setup.** Every skill first looks for the oncall memory
  that `oncall-init` saves (one file for the workspace, one section per team) and uses whatever is
  there: channel naming patterns, rotation and services, which tools Claude can reach, runbooks
  and dashboards, how the team runs incidents. No oncall memory yet: it works from
  what the channel shows and offers setup once.
