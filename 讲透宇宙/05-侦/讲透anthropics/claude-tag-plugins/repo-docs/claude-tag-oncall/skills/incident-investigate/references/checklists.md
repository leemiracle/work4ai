# Investigation checklists

Reference for the `incident-investigate` skill. Run through the relevant list whenever a number
surprises you, before you post it as a finding.

## Is it real?

Before treating an alert as an outage, rule out the ways a healthy system produces a scary graph.

- **Data gap vs real drop.** A throughput or success metric that falls to zero may mean the
  service stopped, or that the agent/exporter stopped reporting. Check a second, independently
  collected signal for the same service (load balancer request count, a downstream consumer's
  intake, host-level CPU). If the second signal is flat-normal, suspect the pipeline, not the
  service.
- **Evaluation window vs actual duration.** A monitor with a 15-minute window can still be red ten
  minutes after a two-minute blip ended. Read the raw series at native resolution and state how
  long the condition actually held.
- **Count vs rate.** "500 errors" over an hour at 50k rpm is 0.017%. Always convert to a rate
  against the matching denominator, and say which denominator.
- **Sampling.** Traces and some log indexes are sampled; error paths are often sampled at a higher
  rate than success paths. Don't compute ratios across differently sampled sources.
- **Clock and timezone.** Confirm the dashboard, the alert, the deploy tool, and the chat are all
  being read in the same timezone. A one-hour offset manufactures false "just before" correlations.
- **Default aggregation hiding per-shard.** Dashboards default to avg or sum across hosts/pods.
  Switch to max, or group by host/pod/shard, before saying "the service" is fine or broken. The
  reverse trap: a consumer pinned to one series of a per-instance metric may be reading a dead
  instance's last minutes — aggregate across series in the query, never index into the list.
- **Synthetic vs real traffic.** A synthetic check failing from one probe location is a probe
  problem until a second location or real-user signal agrees.
- **Already over.** Check whether the signal has recovered before you start; say so immediately if
  it has, then decide whether it still needs explaining.
- **New metric vs new behaviour.** A ratio that steps from nothing to the alert level exactly at a
  deploy and then holds flat may be new instrumentation counting failures the old build produced
  silently. Check whether the metric had data before the rollout before calling it a regression.
- **Stale feed vs healthy signal.** The full rule is "Confirm evidence is current before citing
  it" under the SKILL's "Digging deeper": read the newest point's timestamp first, and treat a
  stalled feed as a finding, never as "looks fine".
- **Blame vs still happening.** The full rule is "A blame verdict names what started it, not what
  is happening now" under the SKILL's "Digging deeper": confirm the symptom is still present
  before naming a blamed change as the live cause.
- **Anomaly monitors have their own failure modes.** "Below the band" is not "near zero": compare
  with the same hour on previous same-weekdays. A burst inside the lookback inflates the band so
  normal traffic reads low; a long dip drags it down, so "recovered" may only mean the detector
  adapted.

## Common measurement traps

- **Averages hide tails.** Mean latency barely moves when 2% of requests take 30 s. Look at p99 and
  max, and at the count of requests over an absolute bound (e.g. >5 s).
- **Pick the control that matches the question.** For "is this level unusual?" compare with the
  same hour on previous same-weekdays — traffic has a daily and weekly shape, so 09:00 Monday vs
  08:00 Monday proves nothing. For "when did it start?" the minutes just before onset are the right
  control, because that is where the step shows.
- **Percent of what?** A ratio whose denominator also moved (fewer requests during an outage,
  because clients gave up) can fall while absolute failures rise. Quote the numerator, the
  denominator, and the ratio together.
- **Success-rate monitors that don't see the failure.** Many "availability" ratios count only 5xx.
  Timeouts surfaced as 499/504 at a proxy, 4xx from auth or quota failures, and requests that never
  arrived are invisible to them. Ask what the numerator and denominator literally count.
- **Where in the stack you count changes the number.** A client that retries turns one failed
  user action into several failed calls further in, so inner-layer error counts overstate impact
  (use the outermost layer for that) while accurately describing load on the dependency. The
  reverse distortion appears once a limiter, shedder, or breaker trips: the traffic you observe
  behind it is only what was admitted, so read the rejected/dropped counter or client-side
  attempts to learn what was actually asked for.
- **Deploy markers lie a little.** "Deployed at 14:08" may be when rollout *started*; the last pod
  may have flipped at 14:20. Use per-version traffic share over time, not the marker, to place
  onset against a deploy.
- **Units.** ms vs s, bytes vs bits, per-second vs per-minute, percent vs ratio. State the unit next
  to every number you post.
- **A retry that worked is evidence, not a fix.** When re-running the failed thing made it pass
  and nothing else changed, the cause — a race, a dependency blip — is still there and will be
  back. Report it as unresolved with the retry noted; never close on it.
- **The test that "verified" it may bypass the broken part.** An end-to-end check proves only the
  path it actually enters: one that injects its input downstream of the failing component has
  never exercised that component, however green it runs. Before trusting "verified", ask where
  the check enters the pipeline — and verify a fix through the same door the real traffic uses.
- **Identity through a proxy is the last hop's.** On a permission error that "can't be happening"
  — the caller is plainly granted access — remember the receiver sees the identity of the last
  hop (a proxy, a forwarding service account), not the originator's. Read the receiver's own log
  for the principal that actually arrived before touching any grant.
- **Automation undoes manual fixes.** A hand-applied config change that vanished within hours
  usually means deployment automation re-applied its template over it. The durable fix lands in
  the template; the manual change only buys time until the next apply.

## Thinking about severity

Every org names and cuts its severity levels differently. The team's own levels, what each one
means here, who declares an incident, and how often status updates go out are captured by
`oncall-init` in that team's section of the oncall memory — use those, in their words, and they
take precedence over anything below. This section is only how to reason towards a guess when the
oncall memory is silent or you need to argue for a level.

Ask, roughly in this order:

- **How broad is the user impact?** Everyone, a region or cohort, one customer, internal only,
  nobody yet. Say it as what people experience ("can't check out"), then the share.
- **Is it growing?** A flat 2% is a different problem from 2% and doubling every ten minutes.
  Trend beats level; look at the last few points, not just the current one.
- **Is data, money, or safety at risk?** Data being lost, corrupted or exposed, payments taken or
  missed wrongly, or anything with a safety or legal edge ranks high even when few users notice.
- **Is there a workaround, and is margin left?** Users can retry or take another path, or a
  temporary mitigation is holding, lowers urgency; running on the last replica, zone or provider
  raises it even while nothing is failing yet.

State severity as a guess in the org's own terms, plus the one fact that would move it up or down.
Don't attach a confidence scale or a percentage to it — certainty is expressed with the words in the
skill's finding format (confirmed / probable / possible / unlikely / ruled out), and only about the
cause. Recommending a level or a change is yours; declaring it is a human's, whoever the oncall memory says
does that here.
