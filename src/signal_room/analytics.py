"""Deterministic calculations and bounded recommendations for Signal Room."""

from __future__ import annotations

import pandas as pd

from signal_room.data_generation import REQUIRED_SIGNAL_COLUMNS

HUMAN_BOUNDARY = "Verify and dispatch; not automated."


def comparison_delta(metric: str, selected: float, baseline: float) -> dict[str, str]:
    """Format a day-average comparison with operationally meaningful color direction."""
    delta = float(selected) - float(baseline)
    if metric == "attendee_pulse_score":
        return {
            "value": f"{selected:.1f} / 5",
            "delta": f"{delta:+.2f} vs day average",
            "delta_color": "normal",
        }
    if metric == "app_error_rate_pct":
        return {
            "value": f"{selected:.1f}%",
            "delta": f"{delta:+.1f} pp vs day average",
            "delta_color": "inverse",
        }
    if metric == "support_case_count":
        return {
            "value": f"{selected:.0f}",
            "delta": f"{delta:+.2f} vs day average",
            "delta_color": "inverse",
        }
    raise ValueError(f"Unsupported comparison metric: {metric}")


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


def build_overall_conference_pulse(signals: pd.DataFrame) -> pd.DataFrame:
    """Aggregate visible locations into an operations-manager trend by interval."""
    if signals.empty:
        return pd.DataFrame(columns=["timestamp", "occupancy_rate", "avg_queue_minutes"])

    def summarize_interval(rows: pd.DataFrame) -> pd.Series:
        total_attendance = rows["attendance"].sum()
        total_capacity = rows["capacity"].sum()
        queue_weights = rows["attendance"]
        queue = (
            (rows["avg_queue_minutes"] * queue_weights).sum() / queue_weights.sum()
            if queue_weights.sum() else rows["avg_queue_minutes"].mean()
        )
        return pd.Series({
            "occupancy_rate": total_attendance / total_capacity * 100 if total_capacity else 0.0,
            "avg_queue_minutes": queue,
        })

    return (
        signals.groupby("timestamp", as_index=False)
        .apply(summarize_interval, include_groups=False)
        .sort_values("timestamp", ignore_index=True)
    )


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
    baseline_fields = ["attendee_pulse_score", "app_error_rate_pct", "support_case_count"]
    baseline_comparison = {
        field: {"selected": float(row[field]), "entity_day_average": round(float(history[field].mean()), 2)}
        for field in baseline_fields
    }
    return {
        "entity_name": entity_name,
        "timestamp": snapshot_time,
        "raw_values": row[["attendance", "capacity", "avg_queue_minutes", "attendee_pulse_score", "app_error_rate_pct", "support_case_count"]].to_dict(),
        "triggering_timestamps": [value.strftime("%-I:%M %p") for value in qualifying["timestamp"]],
        "rule_id": row["rule_id"], "next_best_action": row["next_best_action"],
        "owner": row["owner"], "timing": row["timing"], "confidence": row["confidence"],
        "limitation": row["limitation"], "human_decision_boundary": HUMAN_BOUNDARY,
        "baseline_comparison": baseline_comparison,
        "dispatch_recommended": row["status"] == "attention",
    }
