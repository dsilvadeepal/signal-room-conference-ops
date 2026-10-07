from pathlib import Path

import pandas as pd
import streamlit as st

from signal_room.analytics import evaluate_rules
from signal_room.state import resolve_location_selection, resolve_selected_entity
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
</style>
""", unsafe_allow_html=True)
st.title("Signal Room")
st.caption("Simulated event replay · local CSV data only")

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
    selected_view = st.selectbox("View", options=list(view_options), key="selected_view")
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

if "selected_entity" not in st.session_state:
    st.session_state.selected_entity = None
if "filter_scope" not in st.session_state:
    st.session_state.filter_scope = None

filter_scope = (str(selected_time), selected_view, tuple(sorted(selected_locations)))
scope_changed = st.session_state.filter_scope not in (None, filter_scope)
if scope_changed:
    st.session_state.selected_entity = None
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

chart_col, detail_col = st.columns([2, 1])
with chart_col:
    if snapshot[snapshot["plot_eligible"].astype(bool)].empty:
        st.info("No eligible entities match these filters. Adjust the replay time or entity type.")
    else:
        selection = st.plotly_chart(build_bubble_chart(snapshot), on_select="rerun", selection_mode="points", key="signal_bubbles")
        points = selection.get("selection", {}).get("points", []) if selection else []
        st.session_state.selected_entity = resolve_selected_entity(
            st.session_state.selected_entity, points, scope_changed
        )
with detail_col:
    st.subheader("Signal detail")
    if st.session_state.selected_entity:
        selected = snapshot[snapshot["entity_name"].eq(st.session_state.selected_entity)]
        if selected.empty:
            st.session_state.selected_entity = None
            st.info("Select a bubble to inspect a signal.")
        else:
            row = selected.iloc[0]
            st.markdown(f"**{row['status'].title()} · {row['entity_name']}**")
            st.write(row["next_best_action"])
            st.caption("Verify and dispatch; not automated.")
            if st.button("Clear selection"):
                st.session_state.selected_entity = None
                st.rerun()
    else:
        st.info("Catalyst Theater is highlighted at 2:30 PM. Select a bubble to inspect its signal.")

if st.session_state.selected_entity:
    history = signals[signals["entity_name"].eq(st.session_state.selected_entity)]
    st.plotly_chart(build_trend_chart(history), use_container_width=True)
