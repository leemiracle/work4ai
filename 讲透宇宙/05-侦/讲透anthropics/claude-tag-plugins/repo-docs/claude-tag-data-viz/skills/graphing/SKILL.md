---
name: graphing
description: Compose polished charts (timeseries, bar, line, area, pie, scatter, or anything else the data calls for) from tabular data using the chartkit primitives, producing PNG, SVG, or self-contained interactive HTML. Use when the user asks to chart, graph, plot, or visualize data and wants something better than raw matplotlib defaults.
---

# Graphing

You write the plotting code. The kit provides the parts that should stay consistent across every chart: typography, color derivation from the background, the title and caption frame, and offline HTML packaging. Everything about the chart itself is your judgement applied to the data in front of you.

## The primitives

Import `chartkit` by putting this skill's `scripts/` directory on `sys.path`. Use its absolute path, not a relative path, since your working directory is the user's project. The examples below write it as `/path/to/graphing/scripts`; substitute the real path.

Relevant primitives:
- `theme(bg, font)`: sets matplotlib rcParams and returns resolved colors. Foreground colors derive from background luminance, so a dark `bg` produces a correct dark chart. Fields: `bg` `dark` `text` `muted` `grid` `spine` `accent` `secondary` `series` `font_css`. 
- `palette(n, base)`: n colors. No base cycles the default series, a hex base builds a ramp from it, a list cycles the list. 
- `finish(ax, title, subtitle, source)`: The typographic frame. Left-aligned bold title, muted subtitle, small provenance caption. 
- `save(fig, stem, formats, dpi)`: Writes `stem.png`, `stem.svg`, or both. Returns the paths. 
- `write_html(out, data, component_js, title, bg, font)`: Self-contained interactive page. Inlines React, ReactDOM, react-is, and Recharts from `third_party/` so the file opens offline. Your component reads `window.__CHART_DATA__` and renders into `#root`. 
- `zero_fill_days(pairs)` `rolling_mean(values, w)` `log_floor(values)`: Small data helpers for the gotchas listed below. Use them only when they fit. 

## Steps

1. **Look at the data and decide what it deserves.** Shape, count, and meaning drive the choice: trends over time want lines or day bars, ranked categories want horizontal bars, parts of a whole with few slices can be a pie, correlation wants a scatter. Nothing limits you to those: stacked areas, dual axes, small multiples, annotated thresholds are all just code you write.

2. **Infer colors from context.** Check your conversation and memory for design indicators: a tailwind config, CSS variables, or brand guidelines, and consider the semantic meaning of the data (red or amber for errors, green for success). Pass the destination background to `theme(bg=...)` and brand colors to `palette(base=...)` or directly. Fall back to the defaults only when nothing is inferable. The font defaults to Inter and only changes when the user names a typeface or the destination has a documented brand font.

3. **Write a short script** in your scratchpad that imports chartkit, builds the figure with plain matplotlib (or a Recharts component for interactive output), calls `finish`, and saves.

4. **Render and look at the result.** Read the PNG back and check it with your own eyes before handing it over: labels legible, nothing overlapping, colors distinguishable, the story of the data actually visible. Fix and re-render until it is right.

## The shape of a chart script

PNG or SVG via matplotlib:

```python
import sys
sys.path.insert(0, "/path/to/graphing/scripts")
import chartkit as ck
import matplotlib.pyplot as plt

c = ck.theme()                       # or theme(bg="#0f1419") for a dark surface
fig, ax = plt.subplots(figsize=(10, 5))
# ...plain matplotlib against the data, using c.accent, c.secondary, ck.palette(...)
ck.finish(ax, title="What the chart shows", subtitle="scope or time range",
          source="source: where the data came from, date")
print(ck.save(fig, "out/report", formats=("png", "svg")))
```

Interactive HTML via Recharts, written as plain `React.createElement` with no JSX and no build step:

```python
component = """
(function () {
  var e = React.createElement
  var R = window.Recharts
  var DATA = window.__CHART_DATA__
  function App() {
    return e(R.ResponsiveContainer, { width: "100%", height: 420 },
      e(R.LineChart, { data: DATA },
        e(R.CartesianGrid, { stroke: "GRID", vertical: false }),
        e(R.XAxis, { dataKey: "x" }), e(R.YAxis, null),
        e(R.Tooltip, null),
        e(R.Line, { dataKey: "y", stroke: "ACCENT", strokeWidth: 2.4,
                    dot: false, isAnimationActive: false })))
  }
  ReactDOM.createRoot(document.getElementById("root")).render(e(App))
})()
"""
ck.write_html("out/report.html", data, component, title="What the chart shows")
```

Substitute real colors from the theme into the component and keep `isAnimationActive: false` so the chart is complete the moment the file opens.

## Judgement, not flags

These are the defaults of good charts. Deviate when the data argues for it.

- Rotate x labels only when they would otherwise collide. Short labels stay horizontal.
- Cap bar width when there are few categories. Two bars should not fill the canvas edge to edge.
- Label bars with their values when there are roughly a dozen or fewer. Axes and gridlines are for reading trends, not exact values.
- Rank categorical bars by value unless the categories have a natural order.
- Long category names read better on a horizontal bar chart.
- A title states what the chart shows. A subtitle carries the time range or scope. The source caption says where the data came from and when. Skip any of them only deliberately.
- Legends only when there is more than one series. A single series is named by the title.
- Annotate the chart with what matters: a deploy line, a threshold, the peak, the anomaly the user asked about. An annotation the reader did not need is clutter.

## Gotchas the helpers exist for

- Calendar gaps: a timeseries with missing days misleads on a continuous axis. `zero_fill_days` fills them with zero. Skip it when zeros would be the lie (sparse sampling rather than absence of events).
- Rolling averages: `rolling_mean` is trailing, early points average what exists so far. Do not center it on data that ends today.
- Log scales: bars whose value equals the axis minimum get zero height. `log_floor` gives a lower bound one decade down.
- Negative values: matplotlib handles them, but check the y limits include them and add a zero line when bars go both ways. Recharts y domains default to starting at zero, so pass an explicit `domain` on the YAxis when data is negative or log scaled.

## Verification

Run a minimal render and look at it.

```bash
python3 -c "
import sys
sys.path.insert(0, '/path/to/graphing/scripts')
import chartkit as ck
import matplotlib.pyplot as plt
c = ck.theme()
fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(['A', 'B', 'C'], [10, 30, 20], color=c.accent, width=0.5)
ck.finish(ax, title='chartkit smoke test')
print(ck.save(fig, '/tmp/ck_smoke'))
"
```

Confirm a non-empty PNG is written, then read it back and check it renders correctly.
