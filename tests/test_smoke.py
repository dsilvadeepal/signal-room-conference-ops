def test_package_imports():
    import signal_room


def test_bubble_chart_excludes_ineligible_rows_and_exposes_selection_data():
    import pandas as pd

    from signal_room.visuals import build_bubble_chart

    snapshot = pd.DataFrame([
        {"entity_name": "Catalyst Theater", "attendee_pulse_score": 2.8,
         "operations_pressure_per_100": 5.0, "people_affected": 30,
         "status": "attention", "plot_eligible": True},
        {"entity_name": "Empty Room", "attendee_pulse_score": 4.0,
         "operations_pressure_per_100": None, "people_affected": 0,
         "status": "monitor", "plot_eligible": False},
    ])

    figure = build_bubble_chart(snapshot)

    assert sum(len(trace.x) for trace in figure.data) == 1
    assert figure.data[0].customdata[0][0] == "Catalyst Theater"
    assert figure.data[0].name == "Attention"
    assert figure.data[0].marker.color == "#FF6B7A"
    assert figure.layout.paper_bgcolor == "#141B2D"


def test_trend_chart_contains_the_selected_entity_history():
    import pandas as pd

    from signal_room.visuals import build_trend_chart

    history = pd.DataFrame({
        "timestamp": pd.to_datetime(["2026-10-07 14:00", "2026-10-07 14:15"]),
        "occupancy_rate": [91.0, 94.0],
        "avg_queue_minutes": [12.0, 14.0],
    })

    figure = build_trend_chart(history, title="Location performance over time: Catalyst Theater")

    assert len(figure.data) == 2
    assert list(figure.data[0].x) == list(history["timestamp"])


def test_trend_chart_uses_an_ops_manager_title_for_the_conference_default():
    import pandas as pd

    from signal_room.visuals import build_trend_chart

    history = pd.DataFrame({
        "timestamp": pd.to_datetime(["2026-10-07 14:00", "2026-10-07 14:15"]),
        "occupancy_rate": [70.0, 74.0],
        "avg_queue_minutes": [4.0, 5.0],
    })

    figure = build_trend_chart(history, title="Overall conference pulse")

    assert figure.layout.title.text == "Overall conference pulse"


def test_selection_state_clears_on_empty_chart_selection_or_scope_change():
    from signal_room.state import resolve_selected_entity

    selected_point = [{"customdata": ["Catalyst Theater"]}]

    assert resolve_selected_entity(None, selected_point, scope_changed=False) == "Catalyst Theater"
    assert resolve_selected_entity("Catalyst Theater", [], scope_changed=False) is None
    assert resolve_selected_entity("Catalyst Theater", selected_point, scope_changed=True) is None


def test_dependent_location_filter_resets_to_valid_locations_after_view_change():
    from signal_room.state import resolve_location_selection

    all_locations = ["Catalyst Theater", "Arrival Hub", "Support Bar"]
    session_locations = ["Catalyst Theater"]

    assert resolve_location_selection(["Arrival Hub"], session_locations, view_changed=True) == session_locations
    assert resolve_location_selection(["Catalyst Theater", "Arrival Hub"], session_locations, view_changed=False) == ["Catalyst Theater"]
    assert resolve_location_selection([], all_locations, view_changed=False) == []
