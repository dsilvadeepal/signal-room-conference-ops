"""Seeded synthetic data for the Signal Room demo."""

from __future__ import annotations

from pathlib import Path
import random

import pandas as pd

REQUIRED_SIGNAL_COLUMNS = {
    "timestamp", "entity_type", "entity_name", "session_title", "session_track",
    "capacity", "attendance", "check_ins", "avg_queue_minutes",
    "attendee_pulse_score", "pulse_response_count", "app_error_rate_pct",
    "support_case_count", "people_affected",
}

ENTITIES = (
    ("session", "Momentum Hall", "Opening the Next Era", "Keynote", 700),
    ("session", "Catalyst Theater", "Build With Confidence", "Platform", 420),
    ("session", "Circuit Lab", "Applied AI Patterns", "AI", 260),
    ("session", "Studio Two", "Designing Trusted Products", "Design", 180),
    ("session", "Workshop Loft", "Analytics in Practice", "Data", 150),
    ("zone", "Arrival Hub", "", "Operations", 900),
    ("zone", "Community Commons", "", "Community", 500),
    ("zone", "Support Bar", "", "Support", 160),
)


def _timestamps() -> pd.DatetimeIndex:
    return pd.date_range("2026-10-07 09:00", periods=36, freq="15min")


def generate_conference_signals(seed: int) -> pd.DataFrame:
    """Return 36 replay intervals for eight conference entities."""
    rng = random.Random(seed)
    rows: list[dict[str, object]] = []
    for timestamp in _timestamps():
        minutes = (timestamp.hour - 9) * 60 + timestamp.minute
        for entity_type, name, title, track, capacity in ENTITIES:
            attendance = int(capacity * rng.uniform(0.38, 0.70))
            queue = round(rng.uniform(1.0, 6.0), 1)
            pulse = round(rng.uniform(3.8, 4.6), 1)
            errors = round(rng.uniform(0.1, 1.8), 1)
            cases = rng.randint(0, 2)
            if name == "Arrival Hub" and minutes <= 45:
                attendance, queue, cases = int(capacity * 0.88), round(rng.uniform(13, 18), 1), rng.randint(5, 8)
                pulse, errors = round(rng.uniform(3.0, 3.5), 1), round(rng.uniform(1.0, 2.2), 1)
            if name == "Catalyst Theater" and 300 <= minutes <= 375:
                attendance, queue = int(capacity * rng.uniform(0.91, 0.97)), round(rng.uniform(12.5, 18), 1)
                pulse, errors, cases = round(rng.uniform(2.4, 3.1), 1), round(rng.uniform(5.2, 7.4), 1), rng.randint(4, 7)
            if name == "Catalyst Theater" and minutes >= 420:
                attendance, queue = int(capacity * rng.uniform(0.70, 0.80)), round(rng.uniform(4, 6.5), 1)
                pulse, errors, cases = round(rng.uniform(3.7, 4.1), 1), round(rng.uniform(1.0, 2.3), 1), rng.randint(1, 2)
            rows.append({
                "timestamp": timestamp, "entity_type": entity_type, "entity_name": name,
                "session_title": title, "session_track": track, "capacity": capacity,
                "attendance": attendance, "check_ins": max(0, int(attendance * rng.uniform(0.04, 0.18))),
                "avg_queue_minutes": queue, "attendee_pulse_score": pulse,
                "pulse_response_count": rng.randint(8, 30), "app_error_rate_pct": errors,
                "support_case_count": cases, "people_affected": max(cases * 8, int(attendance * 0.12)),
            })
    return pd.DataFrame(rows, columns=sorted(REQUIRED_SIGNAL_COLUMNS)).sort_values(
        ["timestamp", "entity_name"], ignore_index=True
    )


def generate_attendee_journeys(seed: int) -> pd.DataFrame:
    """Return ordered, non-identifying attendee journeys for the Sankey view."""
    rng = random.Random(seed)
    rows: list[dict[str, object]] = []
    session_names = [entity[1] for entity in ENTITIES if entity[0] == "session"]
    for attendee in range(1, 601):
        identifier = f"ATT-{attendee:03d}"
        start = pd.Timestamp("2026-10-07 09:00") + pd.Timedelta(minutes=rng.randrange(0, 300, 15))
        choices = ["Catalyst Theater", "Catalyst Theater", "Circuit Lab", "Momentum Hall", "Studio Two", "Workshop Loft"]
        session = rng.choice(choices if attendee <= 260 else session_names)
        stages = [("arrival", "Arrival Hub"), ("session", session)]
        if attendee % 5 == 0:
            stages.append(("support", "Support Bar"))
        stages.append(("community", "Community Commons"))
        if attendee % 3 == 0:
            stages.append(("session", rng.choice(session_names)))
        stages.append(("exit", "Exit"))
        for position, (stage, entity) in enumerate(stages):
            rows.append({
                "attendee_id": identifier,
                "timestamp": start + pd.Timedelta(minutes=30 * position),
                "journey_stage": stage,
                "entity_name": entity,
                "session_title": entity if stage == "session" else "",
                "outcome": "completed" if stage == "exit" else "observed",
            })
    return pd.DataFrame(rows).sort_values(["attendee_id", "timestamp"], ignore_index=True)


def write_demo_data(output_dir: Path, seed: int = 42) -> tuple[Path, Path]:
    """Write the deterministic demo CSVs and return their paths."""
    output_dir.mkdir(parents=True, exist_ok=True)
    signals_path = output_dir / "conference_signals.csv"
    journeys_path = output_dir / "attendee_journeys.csv"
    generate_conference_signals(seed).to_csv(signals_path, index=False)
    generate_attendee_journeys(seed).to_csv(journeys_path, index=False)
    return signals_path, journeys_path
