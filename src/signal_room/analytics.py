"""Deterministic calculations and bounded recommendations for Signal Room."""

from __future__ import annotations

import pandas as pd

from signal_room.data_generation import REQUIRED_SIGNAL_COLUMNS

HUMAN_BOUNDARY = "Verify and dispatch; not automated."


def validate_signal_data(signals: pd.DataFrame) -> None:
    missing = sorted(REQUIRED_SIGNAL_COLUMNS.difference(signals.columns))
    if missing:
        raise ValueError(f"Missing required signal columns: {', '.join(missing)}")


def add_derived_metrics(signals: pd.DataFrame) -> pd.DataFrame:
    validate_signal_data(signals)
    derived = signals.copy()
    derived["occupancy_rate"] = derived["attendance"] / derived["capacity"] * 100
    derived["operations_pressure_per_100"] = (
        derived["support_case_count"] / derived["attendance"].replace(0, pd.NA) * 100
    )
    derived["plot_eligible"] = derived["attendance"].gt(0).astype(object)
    return derived


def evaluate_rules(signals: pd.DataFrame) -> pd.DataFrame:
    evaluated = add_derived_metrics(signals)
    evaluated["timestamp"] = pd.to_datetime(evaluated["timestamp"])
    evaluated = evaluated.sort_values(["entity_name", "timestamp"], ignore_index=True)
    qualifying = evaluated["occupancy_rate"].ge(90) & evaluated["avg_queue_minutes"].ge(12)
    consecutive = qualifying.groupby(evaluated["entity_name"]).transform(
        lambda values: values.rolling(3, min_periods=3).sum().eq(3)
    )
    app_support = evaluated["app_error_rate_pct"].ge(5) & evaluated["support_case_count"].ge(4)
    evaluated["status"] = "monitor"
    evaluated.loc[consecutive | app_support, "status"] = "attention"
    evaluated["rule_id"] = ""
    evaluated.loc[consecutive, "rule_id"] = "capacity_queue"
    evaluated.loc[app_support, "rule_id"] = evaluated.loc[app_support, "rule_id"].map(
        lambda current: "capacity_queue+app_support" if current else "app_support"
    )
    evaluated["next_best_action"] = "Continue monitoring."
    evaluated.loc[consecutive, "next_best_action"] = "Prepare overflow viewing and share a routing update."
    evaluated.loc[app_support, "next_best_action"] = "Verify app support coverage and brief the concierge team."
    evaluated.loc[consecutive & app_support, "next_best_action"] = "Prepare overflow viewing, verify app support coverage, and brief the concierge team."
    evaluated["owner"] = "Event Operations Lead"
    evaluated["timing"] = evaluated["status"].map({"attention": "Within 15 minutes", "monitor": "Monitor"})
    evaluated["confidence"] = evaluated["status"].map({"attention": "High", "monitor": "Low"})
    evaluated["limitation"] = "Synthetic replay data; verify conditions before dispatching."
    return evaluated


def investigation_evidence(
    evaluated: pd.DataFrame, entity_name: str, timestamp: pd.Timestamp
) -> dict[str, object]:
    snapshot_time = pd.Timestamp(timestamp)
    history = evaluated[evaluated["entity_name"].eq(entity_name)].sort_values("timestamp")
    selected = history[history["timestamp"].eq(snapshot_time)]
    if selected.empty:
        raise ValueError("No matching entity snapshot found.")
    row = selected.iloc[0]
    qualifying = history[
        history["occupancy_rate"].ge(90) & history["avg_queue_minutes"].ge(12)
        & history["timestamp"].le(snapshot_time)
    ].tail(3)
    return {
        "entity_name": entity_name,
        "timestamp": snapshot_time,
        "raw_values": row[["attendance", "capacity", "avg_queue_minutes", "attendee_pulse_score", "app_error_rate_pct", "support_case_count"]].to_dict(),
        "triggering_timestamps": [value.strftime("%-I:%M %p") for value in qualifying["timestamp"]],
        "rule_id": row["rule_id"], "next_best_action": row["next_best_action"],
        "owner": row["owner"], "timing": row["timing"], "confidence": row["confidence"],
        "limitation": row["limitation"], "human_decision_boundary": HUMAN_BOUNDARY,
    }
