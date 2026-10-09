# Signal Room

Signal Room is a Streamlit dashboard for exploring operational signals during a fictional technology conference. It helps an event operations lead spot possible attendee friction, inspect the underlying evidence, and decide what to verify next. This was built as a Week 1 Path C vibe-coding project.

The app is a **simulated replay**, not a live event-monitoring system. All data is synthetic; it uses no real attendee data, external API, LLM, agent, or automated dispatch.

## Try the app

Run it locally with [uv](https://docs.astral.sh/uv/) and Python 3.11 or newer:

```bash
uv sync
uv run streamlit run app.py
```

The committed CSV is ready to use; no credentials or data download are needed. To regenerate the same seeded dataset and run the tests:

```bash
uv run python scripts/generate_data.py
uv run pytest -q
```

Open the local URL printed by Streamlit (normally `http://localhost:8501`). Run these commands from the repository root because the app reads `data/conference_signals.csv` relative to it.

## What to explore

1. Start at the default **2:30 p.m.** replay time. Use **Show** and **Locations** to filter the eight conference locations.
2. Review the five snapshot metrics and the **Experience vs. support pressure** bubble chart. Bubble size represents people affected; coral marks **Attention**.
3. Before selecting a bubble, the right-hand chart shows the filter-aware **Overall conference pulse**: combined occupancy and attendance-weighted queue time.
4. Select **Catalyst Theater** (or another bubble) to see that location's day-long trend and its investigation evidence: current occupancy, queue, support cases, trigger times, and comparisons with its day average.
5. Use **Clear location selection** to return to the conference-wide view, or move the replay control to inspect another interval.

The UI shows status and evidence, but does **not** currently display the rule engine's `next_best_action` text as a recommendation card. Any operational response remains a human decision; simulated conditions must be verified before dispatching anyone.

## Data and logic

[`data/conference_signals.csv`](data/conference_signals.csv) has 288 records: eight locations at 36 fifteen-minute intervals from 9:00 a.m. through 5:45 p.m. on a simulated day. The seeded generator lives in [`src/signal_room/data_generation.py`](src/signal_room/data_generation.py); field definitions are in the [data dictionary](docs/data-dictionary.md).

The bubble chart plots attendee pulse (a simulated 1–5 micro-survey average) against support cases per 100 attendees. A zero-attendance location has no per-attendee pressure value and is omitted from the bubbles. Pulse scores with fewer than five responses should be treated as directional, not conclusive.

The deterministic rules mark a location **Attention** when either condition is met:

- Occupancy is at least 90% and the average queue is at least 12 minutes for three consecutive intervals.
- App error rate is at least 5% and there are at least four support cases in the interval.

Otherwise, the location remains **Monitor**. These are demo thresholds, not validated real-world alert criteria. The analytics module also calculates bounded next-best-action text, but the current dashboard does not render that text.

## Repository guide

| Path | Purpose |
| --- | --- |
| [`app.py`](app.py) | Streamlit interface, filters, charts, and investigation view |
| [`src/signal_room/analytics.py`](src/signal_room/analytics.py) | Derived metrics, status rules, conference trend, and investigation evidence |
| [`src/signal_room/visuals.py`](src/signal_room/visuals.py) | Plotly bubble and trend charts |
| [`src/signal_room/state.py`](src/signal_room/state.py) | Selection and filter-state behavior |
| [`scripts/generate_data.py`](scripts/generate_data.py) | Rebuilds the committed synthetic CSV with seed 42 |
| [`tests/`](tests/) | Data-generation, analytics, visualization, and state checks |

## Design and build notes

The project began with a product discussion in Codex. The Superpowers plugin was used to create the [product design / PRD](docs/superpowers/specs/2026-10-07-signal-room-design.md) and a [task-by-task implementation plan](docs/superpowers/plans/2026-10-07-signal-room-implementation.md). Those documents record the intended design and build process; the behavior described above reflects the code currently on `main`.
