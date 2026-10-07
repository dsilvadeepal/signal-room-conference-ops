# Signal Room

Signal Room is a synthetic conference-operations dashboard for identifying attendee friction, reviewing evidence, and considering a bounded next-best action.

## Local setup

```bash
uv sync
uv run streamlit run app.py
```

All application data will be simulated. The app does not require credentials, external APIs, or live attendee data.

## Demo data

`data/conference_signals.csv` contains 15-minute session and service-zone snapshots. `data/attendee_journeys.csv` contains ordered, non-identifying synthetic attendee events for the journey view. Generate both deterministic files with `uv run python scripts/generate_data.py`.
