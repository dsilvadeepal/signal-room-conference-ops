import pandas as pd

from signal_room.data_generation import (
    REQUIRED_SIGNAL_COLUMNS,
    generate_conference_signals,
)


def test_signal_generator_has_expected_grain_and_schema():
    signals = generate_conference_signals(seed=42)

    assert len(signals) == 288
    assert signals["timestamp"].nunique() == 36
    assert signals.groupby("timestamp")["entity_name"].nunique().eq(8).all()
    assert REQUIRED_SIGNAL_COLUMNS.issubset(signals.columns)


def test_generator_is_seed_deterministic():
    pd.testing.assert_frame_equal(
        generate_conference_signals(seed=42), generate_conference_signals(seed=42)
    )
