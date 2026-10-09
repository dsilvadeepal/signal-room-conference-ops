from pathlib import Path

import pandas as pd
import streamlit as st

from signal_room.analytics import comparison_delta, build_overall_conference_pulse, evaluate_rules, investigation_evidence
from signal_room.state import chart_selection_key, resolve_location_selection, resolve_selected_entity
from signal_room.visuals import build_bubble_chart, build_trend_chart


st.set_page_config(page_title="Signal Room", layout="wide")
st.markdown("""
<style>
    .stApp { background: #0B1020; }
    [data-testid="stMetric"] { background: #141B2D; border: 1px solid #283554; border-radius: 12px; padding: 1rem; }
    [data-testid="stMetricLabel"], [data-testid="stCaptionContainer"] { color: #AAB6CF; }
    [data-testid="stMetricValue"] { color: #F4F7FB; }
    [data-testid="stSelectbox"] > div, [data-testid="stMultiSelect"] > div { background: #1C2540; }
    .stButton > button { border-color: #6EA8FE; color: #F4F7FB; }
    .app-hero { text-align: center; padding: 0.5rem 0 1rem; }
    .app-hero h1 { margin: 0; color: #F4F7FB; }
    .app-hero p { margin: 0.2rem 0 0; color: #AAB6CF; }
</style>
""", unsafe_allow_html=True)
st.markdown("<div class='app-hero'><h1>Conference Operations Signal Room</h1><p>Monitor attendee experience and support pressure during a simulated event replay</p></div>", unsafe_allow_html=True)

DATA_PATH = Path("data/conference_signals.csv")


@st.cache_data
def load_signals() -> pd.DataFrame:
    return evaluate_rules(pd.read_csv(DATA_PATH, parse_dates=["timestamp"]))


signals = load_signals()
times = sorted(signals["timestamp"].unique())
default_time = pd.Timestamp("2026-10-07 14:30")
selected_time = st.select_slider("Replay time", options=times, value=default_time, format_func=lambda value: pd.Timestamp(value).strftime("%-I:%M %p"))
view_options = {"All locations": ["session", "zone"], "Sessions": ["session"], "Shared services": ["zone"]}
view_col, locations_col = st.columns([1, 2])
with view_col:
    selected_view = st.selectbox("Show", options=list(view_options), key="selected_view")
visible_types = view_options[selected_view]
location_options = sorted(signals[signals["entity_type"].isin(visible_types)]["entity_name"].unique())
previous_view = st.session_state.get("previous_view")
view_changed = previous_view not in (None, selected_view)
if "selected_locations" not in st.session_state:
    st.session_state.selected_locations = location_options
else:
    st.session_state.selected_locations = resolve_location_selection(
        st.session_state.selected_locations, location_options, view_changed
    )
st.session_state.previous_view = selected_view
with locations_col:
    selected_locations = st.multiselect("Locations", options=location_options, key="selected_locations")
snapshot = signals[
    signals["timestamp"].eq(selected_time)
    & signals["entity_type"].isin(visible_types)
    & signals["entity_name"].isin(selected_locations)
]
visible_history = signals[
    signals["entity_type"].isin(visible_types)
    & signals["entity_name"].isin(selected_locations)
]

if "selected_entity" not in st.session_state:
    st.session_state.selected_entity = None
if "show_investigation" not in st.session_state:
    st.session_state.show_investigation = False
if "filter_scope" not in st.session_state:
    st.session_state.filter_scope = None
if "bubble_chart_version" not in st.session_state:
    st.session_state.bubble_chart_version = 0

filter_scope = (str(selected_time), selected_view, tuple(sorted(selected_locations)))
scope_changed = st.session_state.filter_scope not in (None, filter_scope)
if scope_changed:
    st.session_state.selected_entity = None
    st.session_state.show_investigation = False
st.session_state.filter_scope = filter_scope

kpis = st.columns(5)
for column, (label, value, help_text) in zip(kpis, [
    ("Occupancy", f"{snapshot['occupancy_rate'].mean():.0f}%", None),
    ("Average queue", f"{snapshot['avg_queue_minutes'].mean():.1f} min", None),
    ("Attendee pulse", f"{snapshot['attendee_pulse_score'].mean():.1f} / 5", "Average 1–5 attendee pulse rating; higher is better."),
    ("App errors", f"{snapshot['app_error_rate_pct'].mean():.1f}%", None),
    ("Support cases", str(int(snapshot['support_case_count'].sum())), None),
]):
    column.metric(label, value, help=help_text)
st.caption("Pulse-score confidence is lower when fewer than five responses are available; treat it as directional feedback.")

bubble_col, location_col = st.columns([1.35, 1])
with bubble_col:
    if snapshot[snapshot["plot_eligible"].astype(bool)].empty:
        st.info("No locations match these filters. Adjust the replay time, Show, or Locations filters.")
    else:
        selection = st.plotly_chart(
            build_bubble_chart(snapshot),
            on_select="rerun",
            selection_mode="points",
            key=chart_selection_key(st.session_state.bubble_chart_version),
        )
        points = selection.get("selection", {}).get("points", []) if selection else []
        st.session_state.selected_entity = resolve_selected_entity(
            st.session_state.selected_entity, points, scope_changed
        )
        st.session_state.show_investigation = bool(st.session_state.selected_entity)

with location_col:
    if st.session_state.selected_entity:
        selected = snapshot[snapshot["entity_name"].eq(st.session_state.selected_entity)]
        if selected.empty:
            st.session_state.selected_entity = None
            st.session_state.show_investigation = False
            st.info("Select a location bubble to see its performance over time.")
        else:
            row = selected.iloc[0]
            st.subheader(f"Selected location: {row['entity_name']}")
            history = signals[signals["entity_name"].eq(st.session_state.selected_entity)]
            st.caption("This location’s trend across the simulated event day.")
            st.plotly_chart(
                build_trend_chart(history, title=f"Location performance over time: {row['entity_name']}"),
                use_container_width=True,
            )
            st.markdown(f"**{row['status'].title()} · {row['entity_name']}**")
            if st.button("Clear location selection"):
                st.session_state.selected_entity = None
                st.session_state.show_investigation = False
                st.session_state.bubble_chart_version += 1
                st.rerun()
    else:
        st.subheader("Overall conference pulse")
        st.caption("Combined occupancy and attendance-weighted average queue time for the locations in the current filters.")
        st.plotly_chart(
            build_trend_chart(visible_history.pipe(build_overall_conference_pulse), title="Overall conference pulse"),
            use_container_width=True,
        )
        st.info("Select a coral Attention bubble, or any location, to review its location-specific trend and insight.")

if st.session_state.selected_entity and st.session_state.show_investigation:
    evidence = investigation_evidence(signals, st.session_state.selected_entity, selected_time)
    st.subheader(f"Investigation: {st.session_state.selected_entity} · {pd.Timestamp(selected_time).strftime('%-I:%M %p')}")
    raw = evidence["raw_values"]
    raw_cols = st.columns(3)
    raw_cols[0].metric("Occupancy", f"{raw['attendance'] / raw['capacity'] * 100:.0f}%")
    raw_cols[1].metric("Queue", f"{raw['avg_queue_minutes']:.1f} min")
    raw_cols[2].metric("Support cases", str(int(raw["support_case_count"])))
    st.markdown("**Trigger evidence:** " + " · ".join(evidence["triggering_timestamps"]))
    st.markdown("**Compared with this location's day average**")
    baseline_cols = st.columns(3)
    comparison_labels = {
        "attendee_pulse_score": "Attendee pulse score",
        "app_error_rate_pct": "App error rate",
        "support_case_count": "Support cases",
    }
    for column, (metric, values) in zip(baseline_cols, evidence["baseline_comparison"].items()):
        comparison = comparison_delta(metric, values["selected"], values["entity_day_average"])
        column.metric(
            comparison_labels[metric],
            comparison["value"],
            comparison["delta"],
            delta_color=comparison["delta_color"],
        )
    st.caption(f"Limitation: {evidence['limitation']}")
