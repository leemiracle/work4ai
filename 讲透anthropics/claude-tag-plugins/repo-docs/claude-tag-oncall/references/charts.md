# The oncall charts

The fixed shapes for the three figures oncall work keeps needing — a time chart (where the
wall-clock of one thing with an id went, with a stalled / slowed-down / just-long verdict), a
volume graph (one metric over time as a rate, incident window and threshold marked), and an
ingress/egress graph (traffic in vs out per boundary, with a source→destination breakdown of the
change). Chart shapes only; the data comes from whatever this session can read.

A chart in an incident thread is evidence, not decoration. This file fixes the shape of three
pictures so every incident gets the same readable ones; the built-in `dataviz` skill still
governs form and colour for ordinary charts (for the three shapes here, this file wins where the
two differ), and the loading skill's rules — `incident-investigate`'s "Only what's important"
test, figures in their own messages, "How to actually make one" — still decide whether, where
and how a figure posts.

Render everything yourself: fetch the data with whatever tools this session holds, draw with a
plotting library such as matplotlib, save a PNG, and upload the file — several images in a
single file-upload call, never one call per image, and never pasted chart source (Slack renders
none of it).

## Rules for every chart

- Save at 200 dpi or more; the common 100 dpi default is blurry in Slack.
- Label series at their line ends, not in a legend; an on-chart legend appears only where a spec
  below says so.
- A one-line caption whose **first part is the takeaway**, then the time window and source.
  Every number in a caption also appears in the message text — text and charts never disagree.
- Titles in plain words naming the finding, never the metric id; the date in the title; absolute
  times on the axis; one timezone throughout, named.
- Grey for normal; colour only on problems, one distinct hue per problem kind (never shades of
  one hue), at most three.
- Open the saved PNG and look at it before posting: nothing clipped, no overlapping labels, the
  takeaway visible at Slack preview size.
- Save the data tables and the render script beside the PNG (a scratch directory is fine), so
  "re-render to now" later in the incident is cheap.

## Time chart — where the wall-clock of one thing went

For one subject with an id and a timeline — a job, a build, a deploy, a stuck pipeline, a
single slow request. The answer is a verdict plus three kinds of chart.

**Lanes first.** Split the subject into the layer roles it actually has, outermost first:
caller · scheduler or control plane · worker · child tasks · deliberate waits and retries ·
external dependencies. Name each lane in the subject's own vocabulary and drop roles it does not
have — never draw an empty lane. Build one timeline per lane from that layer's own primary
source, say which sources you used, and cross-check adjacent lanes: an outer interval must
bracket the inner work it caused.

**Verdict, null hypothesis first.** Before any chart, say whether anything is actually stuck,
and as of when. Then put every interval of the window into exactly one bucket: working · waiting
on its own child tasks · start-up (submission until the first visible work — always state this
number) · deliberate waits (sleeps, backoff) · waiting on infra · blocked on a person (an
approval gate, requested input — state it even at zero) · stuck or retrying without progress ·
unaccounted. "Stuck" needs a stated threshold: no progress
in the layer's own source for far longer than its typical step. For the largest bucket and every
problem, name the mechanism in that layer's own units (requests/s or ms per request for service
time, bytes for a download or clone, attempts × timeout for a retry loop), and say whether an
infra-attributed problem is specific to this subject or fleet-wide, with at least one comparison
sample.

**Chart 1 — overview.** One swimlane per lane in the order above, shared absolute-time x-axis,
an "as of" marker at the right edge, an on-chart legend. The caption names the lanes and what
each colour means.

**Charts 2..N — zooms.** At least the start-up and the single longest interval, at most four,
one per problem otherwise. Each zoom is one PNG with two panels on a shared x-axis: the lanes
cropped to the range on top, and beneath them a **waterfall of the steps inside the range** — the
form an APM trace viewer or a browser network panel uses. One row per step (a request, a
query, a queue wait, a retry attempt), sorted by start time, each a bar from start to end named in
the layer's own vocabulary with its duration, indented under the outer interval that brackets it.
Measure gaps along the main chain only — from a step's end to the start of the next step under
the same parent; parallel steps are drawn as rows but never produce a gap. Label a gap when it is
the largest in the range or at least 5% of it. Retry attempts are separate rows so a retry loop
reads as a staircase, up to ~20; past that, collapse the run into one row labelled
"N attempts × T s". A problem gap is a hatched span in the problem hue, never a solid bar, so a
wait never looks like work. Each caption states the zoomed range and names the largest gap on
the main chain together with what the subject was waiting on during it.

**Last chart — where the time went.** The buckets as one bar that partitions the window (sums to
~100%; draw *unaccounted* rather than hiding it), every segment labelled with its percentage,
0% buckets named in the caption instead of drawn. Parallel work (fan-out child jobs) is a
separate bar underneath, never added into the main one. The caption lists every bucket's share,
and the verdict must be entailed by this breakdown.

## Volume graph — did the volume move, and when

For "how big is the incident", "did the fix help", "is traffic back to normal": the one metric
the incident moved, over time.

- Plot it as a **rate** (events/sec, or per-bin with the bin-to-day conversion stated once in
  the caption), never a raw cumulative count; y-axis from 0 for counts.
- Mark the incident window: labelled vertical lines at onset and at each mitigation or deploy.
- Give it a comparator: the same weekday of a pre-incident reference week as a dashed grey
  overlay, or a counterfactual band ("what it would have been") where one can be computed. A
  band that cannot be measured gets a conservative floor and an "at least" label — never a point
  estimate dressed as a measurement.
- Draw the threshold as a labelled line in the metric's own unit — the monitor's threshold, or
  the target the team holds the signal to.
- Attribute every percentage to its denominator in the same sentence ("−12% *of what*"), and
  quote absolutes with their load context — most metrics breathe with the daily cycle, so an
  absolute delta at midnight and at peak are different claims.

## Ingress/egress graph — what flows in and out

For a traffic, bandwidth, saturation or cost question at a boundary — a region pair, a cluster
edge, a load balancer, a third-party API.

- **In and out on one panel, same units** (bytes/s or requests/s), so asymmetry is visible; one
  panel per boundary when there are several.
- **Break the change down by source→destination pair**: stacked areas over the window, or ranked
  bars for the spike window, sorted so the pair carrying the change leads. Rank pairs by growth
  against a pre-spike baseline, not by absolute size — the biggest steady flow is otherwise
  always first and says nothing.
- Mark the spike window, and draw the quota or capacity limit as a labelled line where one
  exists — headroom is usually the question being asked.
- The queries come from the responder's own tools (the cloud provider's quota and flow metrics,
  the proxy's byte counters, the balancer's logs); this spec fixes only the picture.

## Before posting — adversarial re-derivation

Re-derive, from the raw rows and not from the chart, before anything uploads: every headline
number; that every coloured interval or gap maps to a stated problem and every stated problem to
a coloured interval or gap; that the breakdown sums; that one timezone runs throughout; and that
the caption's takeaway is entailed by what the picture shows. State that the pass ran in the
message where the skill's format has room for it — never on the chart itself.
