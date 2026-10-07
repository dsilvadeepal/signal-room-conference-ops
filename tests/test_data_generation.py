import pandas as pd

from signal_room.data_generation import (
    REQUIRED_SIGNAL_COLUMNS,
    generate_attendee_journeys,
    generate_conference_signals,
)


def test_signal_generator_has_expected_grain_and_schema():
    signals = generate_conference_signals(seed=42)

    assert len(signals) == 288
    assert signals["timestamp"].nunique() == 36
    assert signals.groupby("timestamp")["entity_name"].nunique().eq(8).all()
    assert REQUIRED_SIGNAL_COLUMNS.issubset(signals.columns)


def test_journey_generator_has_complete_ordered_attendee_paths():
    journeys = generate_attendee_journeys(seed=42)

    assert journeys["attendee_id"].nunique() == 600
    grouped = journeys.sort_values("timestamp").groupby("attendee_id")
    assert grouped.size().between(4, 6).all()
    assert grouped["journey_stage"].first().eq("arrival").all()
    assert grouped["journey_stage"].last().eq("exit").all()


def test_generators_are_seed_deterministic():
    pd.testing.assert_frame_equal(
        generate_conference_signals(seed=42), generate_conference_signals(seed=42)
    )
    pd.testing.assert_frame_equal(
        generate_attendee_journeys(seed=42), generate_attendee_journeys(seed=42)
    )
