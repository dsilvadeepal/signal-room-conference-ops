import pandas as pd
import pytest

from signal_room.analytics import (
    add_derived_metrics,
    build_overall_conference_pulse,
    comparison_delta,
    evaluate_rules,
    investigation_evidence,
    validate_signal_data,
)
from signal_room.data_generation import generate_conference_signals


def signal_row(timestamp, **overrides):
    row = {
        "timestamp": pd.Timestamp(timestamp), "entity_type": "session",
        "entity_name": "Catalyst Theater", "session_title": "Build With Confidence",
        "session_track": "Platform", "capacity": 100, "attendance": 80,
        "check_ins": 10, "avg_queue_minutes": 4.0, "attendee_pulse_score": 4.2,
        "pulse_response_count": 12, "app_error_rate_pct": 1.0,
        "support_case_count": 1, "people_affected": 10,
    }
    return row | overrides


def test_derived_operations_pressure_and_zero_attendance_behavior():
    signals = pd.DataFrame([
        signal_row("2026-10-07 09:00", attendance=80, support_case_count=4),
        signal_row("2026-10-07 09:15", attendance=0, support_case_count=0),
    ])

    derived = add_derived_metrics(signals)

    assert derived.loc[0, "operations_pressure_per_100"] == 5.0
    assert pd.isna(derived.loc[1, "operations_pressure_per_100"])
    assert derived.loc[1, "plot_eligible"] is False


def test_overall_conference_pulse_uses_weighted_occupancy_and_queue():
    signals = pd.DataFrame([
        signal_row("2026-10-07 14:30", entity_name="Catalyst Theater", capacity=100, attendance=90, avg_queue_minutes=12),
        signal_row("2026-10-07 14:30", entity_name="Studio Two", capacity=300, attendance=150, avg_queue_minutes=4),
    ])

    pulse = build_overall_conference_pulse(signals)

    assert len(pulse) == 1
    assert pulse.loc[0, "occupancy_rate"] == 60.0
    assert pulse.loc[0, "avg_queue_minutes"] == 7.0


def test_comparison_delta_uses_semantic_colors_for_better_and_worse_changes():
    pulse = comparison_delta("attendee_pulse_score", selected=2.5, baseline=3.88)
    app_errors = comparison_delta("app_error_rate_pct", selected=6.2, baseline=2.0)
    support_cases = comparison_delta("support_case_count", selected=7, baseline=2.06)

    assert pulse == {"value": "2.5 / 5", "delta": "-1.38 vs day average", "delta_color": "normal"}
    assert app_errors == {"value": "6.2%", "delta": "+4.2 pp vs day average", "delta_color": "inverse"}
    assert support_cases == {"value": "7", "delta": "+4.94 vs day average", "delta_color": "inverse"}


def test_capacity_queue_attention_requires_three_consecutive_intervals():
    signals = pd.DataFrame([
        signal_row("2026-10-07 02:00 PM", attendance=92, avg_queue_minutes=12),
        signal_row("2026-10-07 02:15 PM", attendance=94, avg_queue_minutes=13),
        signal_row("2026-10-07 02:30 PM", attendance=96, avg_queue_minutes=14),
    ])

    evaluated = evaluate_rules(signals)

    assert evaluated["status"].tolist() == ["monitor", "monitor", "attention"]
    assert evaluated.loc[2, "rule_id"] == "capacity_queue"


def test_app_and_support_rule_and_evidence_are_bounded():
    signals = pd.DataFrame([
        signal_row("2026-10-07 02:00 PM", attendance=92, avg_queue_minutes=12),
        signal_row("2026-10-07 02:15 PM", attendance=94, avg_queue_minutes=13),
        signal_row("2026-10-07 02:30 PM", attendance=96, avg_queue_minutes=14,
                   app_error_rate_pct=5.5, support_case_count=4),
    ])

    evaluated = evaluate_rules(signals)
    evidence = investigation_evidence(evaluated, "Catalyst Theater", pd.Timestamp("2026-10-07 14:30"))

    assert evaluated.loc[2, "rule_id"] == "capacity_queue+app_support"
    assert evidence["triggering_timestamps"] == ["2:00 PM", "2:15 PM", "2:30 PM"]
    assert evidence["owner"] == "Event Operations Lead"
    assert evidence["human_decision_boundary"] == "Verify and dispatch; not automated."


def test_normal_session_does_not_trigger_attention():
    evaluated = evaluate_rules(pd.DataFrame([signal_row("2026-10-07 11:00")]))

    assert evaluated.loc[0, "status"] != "attention"
    assert evaluated.loc[0, "next_best_action"] == "Continue monitoring."


def test_missing_required_columns_name_the_missing_fields():
    with pytest.raises(ValueError, match="attendance.*capacity"):
        validate_signal_data(pd.DataFrame({"timestamp": ["2026-10-07 09:00"]}))


def test_generated_catalyst_investigation_has_complete_bounded_evidence():
    evaluated = evaluate_rules(generate_conference_signals(seed=42))

    evidence = investigation_evidence(evaluated, "Catalyst Theater", pd.Timestamp("2026-10-07 14:30"))

    assert evidence["rule_id"] == "capacity_queue+app_support"
    assert evidence["triggering_timestamps"] == ["2:00 PM", "2:15 PM", "2:30 PM"]
    assert evidence["owner"] == "Event Operations Lead"
    assert evidence["timing"] == "Within 15 minutes"
    assert evidence["human_decision_boundary"] == "Verify and dispatch; not automated."
    assert set(evidence["baseline_comparison"]) == {"attendee_pulse_score", "app_error_rate_pct", "support_case_count"}


def test_normal_session_evidence_does_not_recommend_dispatch():
    evaluated = evaluate_rules(pd.DataFrame([signal_row("2026-10-07 11:00", entity_name="Studio Two")]))

    evidence = investigation_evidence(evaluated, "Studio Two", pd.Timestamp("2026-10-07 11:00"))

    assert evidence["dispatch_recommended"] is False
    assert evidence["next_best_action"] == "Continue monitoring."
